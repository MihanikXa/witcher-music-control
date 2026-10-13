"""Private v3 vector Xbox repair + red correction, exact deployed accepted v2.
No deployment. Runtime rendering remains an isolated in-game acceptance check.
"""
import argparse,configparser,json,struct,zlib,shutil,subprocess
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('v2',ROOT/'tools/build-ink-hud-refinement.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
r=v.r;b=v.b
vector=v.load('flat-vector-xbox')
V2=ROOT/'build/ink-hud-refinement-v2-release-final'
RED={'health':('#AA7565','#B65348'),'hostile':('#DE9C89','#D87566'),'lag':('#C3A18F','#C98678')}

def reds(text):
    # Exactly the live v2 native type paint and post-v4 synchronization paint.
    old=int('DE9C89',16);new=int('D87566',16)
    if text.count(str(old))!=2:raise ValueError('Hostile paint contract changed')
    text=text.replace(str(old),str(new))
    text=r.p.one(text,'11171173,0);',str(int('B65348',16))+',0);')
    return r.p.one(text,'g.beginFill(12820879,0.85);','g.beginFill(0xC98678,0.85);')

def finish(a):
    """Resume after cook/validate/pack and checked metadata; never invent receipts."""
    out=a.out.resolve();deploy=a.deploy.resolve();b.font.private_path(out)
    if deploy.exists() or ROOT/'deploy' not in deploy.parents:raise ValueError('Fresh private deploy destination required')
    parent=json.loads((V2/'receipt.json').read_text());commands=json.loads((out/'commands.json').read_text())
    if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('Accepted V2 archive changed')
    for key,digest in parent['source_cache_sha256'].items():
        if b.fallback.sha(V2/'source-inputs'/key)!=digest:raise ValueError('Pinned pre-glyph source changed')
    if b.fallback.sha(Path(parent['glyph_font']['path']))!=parent['glyph_font']['sha256']:raise ValueError('Glyph font changed')
    if a.relocate_metadata and not a.prepare_resume and not any(c['label']=='metadata' and c['exit_code']==0 for c in commands):
        cmd=[__import__('sys').executable,str(ROOT/'tools/relocate-hud-metadata.py'),'--out',str(out),'--verify-existing']
        proc=subprocess.run(cmd,capture_output=True,timeout=60)
        (out/'metadata-relocation.stdout.log').write_bytes(proc.stdout+proc.stderr)
        if proc.returncode:raise ValueError('Checked metadata relocation failed')
        commands.append(dict(label='metadata',command=cmd,exit_code=proc.returncode,assertions=[],method='native-control verified table relocation; v3 metadatastore did not pass'))
        b.write_json(out/'commands.json',commands)
    if not all(any(c['label']==label and c['exit_code']==0 for c in commands) for label in (('cook','validate','pack') if a.prepare_resume else ('cook','validate','pack','metadata'))):raise ValueError('Successful native receipts required')
    state=json.loads((out/'live-before.json').read_text())
    if b.bars.snapshot(v.GAME,v.SETTINGS)!=state:raise ValueError('Live inputs changed')
    files={key:(out/'prepared-inputs'/key).read_bytes() for key in parent['resource_hashes']};contracts={};changes={}
    cached=json.loads((out/'resume-contracts.json').read_text()) if (out/'resume-contracts.json').exists() else None
    for key,data in files.items():
        source=(V2/'pack-input'/key).read_bytes();stem=Path(key).stem
        if cached and key in cached['movie_contracts']:
            contract=cached['movie_contracts'][key]
            if b.audit.sha(source)!=contract['input_sha256'] or b.audit.sha(data)!=contract['output_sha256']:raise ValueError('Resume movie hash changed')
            contracts[key]=contract;changes[key]=cached['changes'][key];continue
        if data==source:continue
        if stem=='hud_enemyfocus':
            contracts[key]=v.contract(source,data,out/'exports'/stem,out/'reexport'/stem)
            original=next((out/'exports'/stem/'scripts').rglob('HudModuleEnemyFocus.as')).read_text(encoding='utf-8-sig')
            edited=(out/'abc'/stem/'HudModuleEnemyFocus.as').read_text(encoding='utf-8-sig')
            if reds(original)!=edited:raise ValueError('Enemy source changed beyond four literals')
            changes[key]=dict(source_edits='Four verified red literals only')
        else:
            original=v.retail(key,out)[0] if stem=='hud_iteminfo' else (V2/'source-inputs'/key).read_bytes()
            rebuilt,contract=vector.repair(source,original,out/'repro-vectors'/stem,Path(parent['glyph_font']['path']))
            if rebuilt!=data:raise ValueError('Reproducible vector build differs')
            contracts[key]=contract;changes[key]=dict(vector_repair=contract)
    script=json.loads((out/'scripts/receipt.json').read_text())
    if not all(row['success'] for row in script['results']):raise ValueError('Script compiler controls failed')
    for row in script['results']:
        if b.fallback.sha(out/'scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Compiler control blob changed')
    for entry in script['assembly_inputs']+script['current_required_inputs']:
        if b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Script input changed')
    manifest=dict(version='Ink & Iron HUD Refinement V3 vector repair',diagnostic=False,root_cause_confirmed=False,changes=changes,movie_contracts=contracts,parent_zip_sha256=parent['zip_sha256'],palette={k:dict(before=x,after=y) for k,(x,y) in RED.items()},official_cook_validated=True,unchanged_keys=sorted(k for k,d in files.items() if b.audit.sha(d)==parent['resource_hashes'][k]),script_regression=script['results'],script_compile_reused=True,opaque_mods_not_recompiled=parent['opaque_mods_not_recompiled'],live_inputs_unchanged=True,source_tool_sha256=b.fallback.sha(Path(__file__)),vector_tool_sha256=b.fallback.sha(ROOT/'tools/flat-vector-xbox.py'),reproducible_movie_bytes_verified=True)
    if (out/'metadata-relocation.json').exists():
        manifest['metadata_relocation']=json.loads((out/'metadata-relocation.json').read_text())
        if manifest['metadata_relocation']['output_metadata_sha256']!=b.fallback.sha(out/'packed/metadata.store'):raise ValueError('Relocated metadata changed')
        manifest['native_v3_metadatastore_passed']=False
    validation=(out/'validate.full.log').read_text()
    if 'Found 22 files to validate' not in validation or 'Errors found in 0 resources:' not in validation:raise ValueError('Native validation gate missing')
    for key,data in files.items():
        if key.endswith('.redswf'):
            if (out/'cooked'/key).read_bytes()!=data:raise ValueError('Cook output differs')
            v.atlas_contract(data)
    b.write_json(out/'resume-contracts.json',manifest)
    if a.prepare_resume:
        print('Reproducible prepared V3 contracts verified',flush=True)
        return
    b.MOD='modInkIronHUDRefinementV3';b.HUD=V2/'support';b.HUD_OPTIONS.remove('iiShowQuickSlotKeys')
    b.package(out,deploy,set(parent['selected']),files,manifest,a.runner.resolve(),commands,verified_native_reuse=True)
    archive=deploy/'Ink-Iron-HUD-Refinement-v3-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(archive);manifest['zip_path']=str(archive)
    b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest)
    print('V3 ready',archive,manifest['zip_sha256'],flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--runner',type=Path,default=ROOT/'build/npc-state-expanded');ap.add_argument('--compiled-cache',type=Path);ap.add_argument('--native-cache',type=Path);ap.add_argument('--finish-package',action='store_true');ap.add_argument('--prepare-resume',action='store_true');ap.add_argument('--relocate-metadata',action='store_true');a=ap.parse_args()
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul required')
    if a.finish_package:return finish(a)
    out,deploy=a.out.resolve(),a.deploy.resolve();b.font.private_path(out)
    if ROOT/'deploy' not in deploy.parents or out.exists() or deploy.exists():raise ValueError('Fresh private destinations required')
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul required')
    parent=json.loads((V2/'receipt.json').read_text());
    for key,digest in parent['source_cache_sha256'].items():
        if b.fallback.sha(V2/'source-inputs'/key)!=digest:raise ValueError('Pinned pre-glyph source changed')
    if b.fallback.sha(Path(parent['glyph_font']['path']))!=parent['glyph_font']['sha256']:raise ValueError('Glyph font changed')
    out.mkdir();state=b.bars.snapshot(v.GAME,v.SETTINGS);b.write_json(out/'live-before.json',state)
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
    for key in list(files):
        source=files[key];stem=Path(key).stem
        if stem=='hud_enemyfocus':
            export=out/'exports'/stem;export.mkdir(parents=True);gfx=export/'original.gfx';gfx.write_bytes(r.p.movie(source)[1]);b.export(gfx,export)
            candidate,edits=r.compile_classes(source,export,out/'abc'/stem,{'HudModuleEnemyFocus':reds},a.compiled_cache/'abc'/stem if a.compiled_cache else None)
            reexport=out/'reexport'/stem;final=out/'abc'/stem/'final.gfx';final.write_bytes(r.p.movie(candidate)[1]);b.export(final,reexport)
            contracts[key]=v.contract(source,candidate,export,reexport);changes[key]=dict(source_edits=edits)
        elif key.endswith('.redswf') and any('ICO_Xbox_' in n for n in b.contracts.symbols(b.audit.swf_tags(source)[2])):
            original=v.retail(key,out)[0] if stem=='hud_iteminfo' else (V2/'source-inputs'/key).read_bytes()
            candidate,contract=vector.repair(source,original,out/'vectors'/stem,Path('C:/Windows/Fonts/segoeui.ttf'))
            contracts[key]=contract;changes[key]=dict(vector_repair=contract)
            gfx=out/'vectors'/stem/'final.gfx';gfx.write_bytes(r.p.movie(candidate)[1]);b.export(gfx,out/'vector-export'/stem)
            proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-swf2xml',str(gfx),str(gfx.with_suffix('.xml'))],capture_output=True,timeout=90)
            if proc.returncode:raise ValueError('Independent vector XML parse failed')
        else:continue
        files[key]=candidate
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
    b.write_json(out/'prepared-contracts.json',dict(owners=owners,changes=changes,movie_contracts=contracts,unchanged_keys=sorted(k for k in files if files[k]==before_files[k])))
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
    manifest=dict(version='Ink & Iron HUD Refinement V3 vector repair',diagnostic=False,root_cause_confirmed=False,owners=owners,changes=changes,movie_contracts=contracts,parent_zip_sha256=parent['zip_sha256'],palette={k:dict(before=x,after=y) for k,(x,y) in RED.items()},official_cook_validated=True,unchanged_keys=sorted(k for k in files if files[k]==before_files[k]),script_regression=script['results'],script_compile_reused=True,native_cache=str(a.native_cache) if a.native_cache else None,opaque_mods_not_recompiled=parent['opaque_mods_not_recompiled'],live_inputs_unchanged=True,source_tool_sha256=b.fallback.sha(Path(__file__)),vector_tool_sha256=b.fallback.sha(ROOT/'tools/flat-vector-xbox.py'))
    # V3 ships identical script bytes and filtered options. No merge regeneration.
    b.MOD='modInkIronHUDRefinementV3';b.HUD=V2/'support';b.HUD_OPTIONS.remove('iiShowQuickSlotKeys')
    b.package(out,deploy,set(parent['selected']),files,manifest,runner,commands,verified_native_reuse=bool(a.native_cache))
    archive=deploy/'Ink-Iron-HUD-Refinement-v3-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(archive);manifest['zip_path']=str(archive)
    b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest)
    if b.bars.snapshot(v.GAME,v.SETTINGS)!=state:raise ValueError('Live inputs changed')
    print('V3 ready',archive,manifest['zip_sha256'],flush=True)

if __name__=='__main__':main()
