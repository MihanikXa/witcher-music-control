"""Private v3 diagnostic + red correction, using exact deployed accepted v2.
No deployment. Deliberately requires runtime feedback before a glyph-fix claim.
"""
import argparse,configparser,json,struct,zlib,shutil,subprocess
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('v2',ROOT/'tools/build-ink-hud-refinement.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
r=v.r;b=v.b
V2=ROOT/'build/ink-hud-refinement-v2-release-final'
RED={'health':('#AA7565','#B65348'),'hostile':('#DE9C89','#D87566'),'lag':('#C3A18F','#C98678')}

def reds(text):
    # Exactly the live v2 native type paint and post-v4 synchronization paint.
    old=int('DE9C89',16);new=int('D87566',16)
    if text.count(str(old))!=2:raise ValueError('Hostile paint contract changed')
    text=text.replace(str(old),str(new))
    text=r.p.one(text,'11171173,0);',str(int('B65348',16))+',0);')
    return r.p.one(text,'g.beginFill(12820879,0.85);','g.beginFill(0xC98678,0.85);')

def button_probe(text):
    if 'import flash.display.Shape;' not in text:
        text=r.p.one(text,'   import flash.display.Sprite;','   import flash.display.Sprite;\n   import flash.display.Shape;')
    needle='            this._gpadIcon.gotoAndStop(this.getPadIconFrameLabel(navCode));'
    probe="""
            // Temporary diagnostic: no event handlers, no new hit area.
            var qfMark:Shape = this._gpadIcon.getChildByName("qfGlyphPathV3") as Shape;
            if (!qfMark) {
               qfMark = new Shape();
               qfMark.name = "qfGlyphPathV3";
               this._gpadIcon.addChild(qfMark);
            }
            qfMark.graphics.clear();
            qfMark.graphics.beginFill(this._gpadIcon == this.mcIconXbox ? 0xFF00FF : (this._gpadIcon == this.mcIconSteam ? 0x00FFFF : 0xFFFF00),1);
            qfMark.graphics.drawRect(-4,-4,8,8);
            qfMark.graphics.endFill();
"""
    return r.p.one(text,needle,needle+probe)

def hint_probe(text):
    # Controlsfeedback uses HintButton, not InputFeedbackButton.
    synthetic='   import flash.display.Sprite;'+chr(10)+'            this._gpadIcon.gotoAndStop(this.getPadIconFrameLabel(navCode));'
    inserted=button_probe(synthetic).split('this._gpadIcon.gotoAndStop(this.getPadIconFrameLabel(navCode));',1)[1].replace('this._gpadIcon','_loc3_')
    if 'import flash.display.Shape;' not in text:
        text=r.p.one(text,'   import flash.display.MovieClip;','   import flash.display.MovieClip;'+chr(10)+'   import flash.display.Shape;')
    return r.p.one(text,'            _loc3_.gotoAndStop(_loc4_);','            _loc3_.gotoAndStop(_loc4_);'+inserted)

def write_texture_mark(source,linkage,rectangle,color):
    """Replace only wholly interior BC3 blocks, never neighboring images."""
    result=bytearray(source);chunks=b.font.native.chunks(source)
    i=next(i for i,c in enumerate(chunks) if c['properties'].get('linkageName',{}).get('value')==linkage)
    c=chunks[i];width=c['properties']['width']['value'];tail=c['offset']+c['size']-len(c['tail']);x1,y1,x2,y2=rectangle
    left=((x1+x2)//2-12+3)//4*4;top=((y1+y2)//2-12+3)//4*4
    if not(x1<=left and left+24<=x2 and y1<=top and top+24<=y2):raise ValueError('Probe blocks exceed image')
    rgb=tuple(int(color[j:j+2],16) for j in (1,3,5))
    # Use a constant RGB565 color and opaque BC3 alpha, no interpolation.
    packed=((rgb[0]*31//255)<<11)|((rgb[1]*63//255)<<5)|(rgb[2]*31//255)
    block=bytes((255,255))+bytes(6)+struct.pack('<HHI',packed,packed,0)
    touched=[]
    for y in range(top,top+24,4):
        for x in range(left,left+24,4):
            pos=tail+28+(y//4*((width+3)//4)+x//4)*16
            result[pos:pos+16]=block;touched.append(pos)
    eo,count,_=struct.unpack_from('<III',result,88)
    struct.pack_into('<I',result,eo+i*24+20,zlib.crc32(result[c['offset']:c['offset']+c['size']]))
    struct.pack_into('<I',result,96,zlib.crc32(result[eo:eo+count*24]))
    struct.pack_into('<I',result,32,r.p.header_crc(result))
    if not all(c['crc_valid'] for c in b.font.native.chunks(result)):raise ValueError('Probe CRC failure')
    return bytes(result),dict(linkage=linkage,rectangle=list(rectangle),marked_rectangle=[left,top,left+24,top+24],color=color,blocks=36)

def atlas_probes(source,original):
    symbols=b.contracts.symbols(b.audit.swf_tags(source)[2]);cid=symbols['ICO_Xbox_A.png']
    edits=[];candidate=source
    for data,color in ((original,'#00FFFF'),(source,'#FF00FF')):
        images={}
        for code,payload in b.audit.swf_tags(data)[2]:
            if code==1009:
                pos=11+payload[10];images[struct.unpack_from('<H',payload)[0]]=payload[pos+1:pos+1+payload[pos]].decode('ascii')
        sub=next(payload for code,payload in b.audit.swf_tags(data)[2] if code==1008 and struct.unpack_from('<H',payload)[0]==cid)
        _,image,*rect=struct.unpack('<6H',sub)
        candidate,change=write_texture_mark(candidate,images[image],rect,color);edits.append(change)
    return candidate,edits

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--runner',type=Path,default=ROOT/'build/npc-state-expanded');ap.add_argument('--compiled-cache',type=Path);ap.add_argument('--native-cache',type=Path);a=ap.parse_args()
    out,deploy=a.out.resolve(),a.deploy.resolve();b.font.private_path(out)
    if ROOT/'deploy' not in deploy.parents or out.exists() or deploy.exists():raise ValueError('Fresh private destinations required')
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul required')
    parent=json.loads((V2/'receipt.json').read_text());out.mkdir();state=b.bars.snapshot(v.GAME,v.SETTINGS);b.write_json(out/'live-before.json',state)
    if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('Accepted V2 archive changed')
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.settings_text(v.SETTINGS));owners=b.owners(v.GAME,cfg,set(parent['resource_hashes']),out)
    files={}
    for key,digest in parent['resource_hashes'].items():
        active=sorted([o for o in owners[key] if o.get('enabled')=='1'],key=lambda o:int(o.get('priority') or 9999))
        if not active or active[0]['sha256']!=digest:raise ValueError('Deployed V2 winner changed: '+key)
        entry=next(e for e in b.audit.entries(Path(active[0]['container'])) if e['resource']==key)
        data=b.read_bundle(Path(active[0]['container']),entry,v.GAME,out)
        if b.audit.sha(data)!=digest:raise ValueError('Deployed input changed')
        files[key]=data
    before_files=dict(files);contracts={};changes={}
    for stem in ('hud_enemyfocus','hud_controlsfeedback','hud_interactions'):
        key=b.PREFIX+stem+'.redswf';source=files[key];export=out/'exports'/stem;export.mkdir(parents=True);gfx=export/'original.gfx';gfx.write_bytes(r.p.movie(source)[1]);b.export(gfx,export)
        transform={'HudModuleEnemyFocus':reds} if stem=='hud_enemyfocus' else ({'HintButton':hint_probe} if stem=='hud_controlsfeedback' else {'InputFeedbackButton':button_probe})
        candidate,edits=r.compile_classes(source,export,out/'abc'/stem,transform,a.compiled_cache/'abc'/stem if a.compiled_cache else None)
        changes[key]=dict(source_edits=edits)
        if stem!='hud_enemyfocus':
            original=(V2/'source-inputs'/key).read_bytes();candidate,marks=atlas_probes(candidate,original);changes[key]['atlas_probes']=marks
        reexport=out/'reexport'/stem;final=out/'abc'/stem/'final.gfx';final.write_bytes(r.p.movie(candidate)[1]);b.export(final,reexport)
        contracts[key]=v.contract(source,candidate,export,reexport);files[key]=candidate
        print('V3 contract',stem,'passed',flush=True)
    for key,data in files.items():
        target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    script=json.loads((V2/'scripts/receipt.json').read_text())
    for entry in script['assembly_inputs']+script['current_required_inputs']:
        if b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Current script input changed')
    if not all(row['success'] for row in script['results']):raise ValueError('Script controls required')
    for row in script['results']:
        if b.fallback.sha(V2/'scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Compiler output changed')
    shutil.copytree(V2/'scripts',out/'scripts')
    commands=[];runner=a.runner.resolve();b.font.private_path(runner);native={k:d for k,d in files.items() if k.endswith('.redswf')}
    if a.native_cache:
        cache=a.native_cache.resolve();b.font.private_path(cache)
        commands=json.loads((cache/'commands.json').read_text())
        if not all(any(c['label']==label and c['exit_code']==0 for c in commands) for label in ('cook','validate','pack')):raise ValueError('Native cache must have successful cook/validate/pack')
        log=(cache/'validate.full.log').read_text()
        if 'Found '+str(len(native))+' files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Cached validation inventory/errors differ')
        for key,data in native.items():
            if (cache/'cooked'/key).read_bytes()!=data:raise ValueError('Cached cooked inputs differ')
            v.atlas_contract(data)
        shutil.copytree(cache/'packed',out/'packed')
        for label in ('cook','validate','pack'):
            for suffix in ('.full.log','.stdout.log'):shutil.copy2(cache/(label+suffix),out/(label+suffix))
        with b.mount(runner,out,{}) as workspace:
            b.official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
    else:
        with b.mount(runner,out,native) as workspace:
            b.official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
            log=b.official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
            if 'Found '+str(len(native))+' files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Native validation gate failed')
            for key,data in native.items():
                if (out/'cooked'/key).read_bytes()!=data:raise ValueError('Cook changed candidate')
                v.atlas_contract(data)
    manifest=dict(version='Ink & Iron HUD Refinement V3 diagnostic and red trial',diagnostic=True,root_cause_confirmed=False,owners=owners,changes=changes,movie_contracts=contracts,parent_zip_sha256=parent['zip_sha256'],palette={k:dict(before=x,after=y) for k,(x,y) in RED.items()},official_cook_validated=True,unchanged_keys=sorted(k for k in files if files[k]==before_files[k]),script_regression=script['results'],script_compile_reused=True,native_cache=str(a.native_cache) if a.native_cache else None,opaque_mods_not_recompiled=parent['opaque_mods_not_recompiled'],live_inputs_unchanged=True,source_tool_sha256=b.fallback.sha(Path(__file__)))
    # V3 ships identical script bytes and filtered options. No merge regeneration.
    b.MOD='modInkIronHUDRefinementV3Diagnostic';b.HUD=V2/'support';b.HUD_OPTIONS.remove('iiShowQuickSlotKeys')
    b.package(out,deploy,set(parent['selected']),files,manifest,runner,commands,verified_native_reuse=bool(a.native_cache))
    archive=deploy/'Ink-Iron-HUD-Refinement-v3-diagnostic-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(archive);manifest['zip_path']=str(archive)
    b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest)
    if b.bars.snapshot(v.GAME,v.SETTINGS)!=state:raise ValueError('Live inputs changed')
    print('V3 diagnostic ready',archive,manifest['zip_sha256'],flush=True)

if __name__=='__main__':main()
