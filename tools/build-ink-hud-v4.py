"""Private v4: exact deployed v3 inputs, smooth paths, measured prompts, I&I quickslots.
Never deploys. Native stages and guarded metadata fallback are recorded separately.
"""
import argparse,json,struct,zlib,subprocess,shutil
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=load('build-ink-hud-v3');r=d.r;b=d.b;v=d.v;smooth=load('smooth-xbox');layout=load('polish-hud-layout')
PARENT=ROOT/'build/ink-hud-v3-final';WORK=ROOT/'build/ink-hud-v4-work';FONT=Path('C:/Windows/Fonts/segoeui.ttf')
def export(gfx,dest):
 dest.mkdir(parents=True,exist_ok=True)
 proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-export','script',str(dest),str(gfx)],capture_output=True,timeout=240)
 (dest/'export.log').write_bytes(proc.stdout+proc.stderr)
 if proc.returncode or not list(dest.rglob('*.as')):raise ValueError('AS export failed')
b.export=export
PALETTE={'health':('#B65348','#B94A40'),'hostile':('#D87566','#D9695A'),'lag':('#C98678','#C77D6E')}
def reds(t):
 for name,(old,new) in PALETTE.items():
  if name=='hostile':
   if t.count(str(int(old[1:],16)))!=2:raise ValueError('Hostile dual paint changed')
   t=t.replace(str(int(old[1:],16)),str(int(new[1:],16)))
  elif name=='health':t=r.p.one(t,str(int(old[1:],16))+',0);',str(int(new[1:],16))+',0);')
  else:t=r.p.one(t,str(int(old[1:],16))+',0.85);',str(int(new[1:],16))+',0.85);')
 return t

def replace_tags(source,fn):
 tags=b.audit.swf_tags(source)[2];output=fn(tags);_,raw,body,_=r.p.movie(source);start=(5+4*(body[0]>>3)+7)//8+4
 stream=body[:start]+b''.join(smooth.f.tag(c,p) for c,p in output)
 return r.p.replace_movie(source,b'CFX'+raw[3:4]+struct.pack('<I',len(stream)+8)+zlib.compress(stream))

def warning(source):
 edits=[]
 def change(tags):
  result=[]
  for c,p in tags:
   if c==83 and struct.unpack_from('<H',p)[0]==29:
    if p.count(b'\xff\0\0\xff')!=1:raise ValueError('Warning stroke guard')
    p=p.replace(b'\xff\0\0\xff',b'\xff\0\0\xb3');edits.append('Shape29 red stroke alpha 255->179')
   if c==39 and struct.unpack_from('<H',p)[0]==63:
    children=[];sprite=bytearray(p)
    for tc,a,e in smooth.flat.parser.records(p,4):
     tp=p[a:e]
     if tc==70 and b'mcDodgeFeedback\0' in tp:
      if tp.count(b'\xff\0\0\xff')!=1:raise ValueError('Warning glow guard')
      sprite[a+tp.index(b'\xff\0\0\xff')+3]=179;edits.append('mcDodgeFeedback red glow alpha 255->179')
     children.append(smooth.f.tag(tc,tp))
    p=bytes(sprite)
   result.append((c,p))
  return result
 candidate=replace_tags(source,change)
 if len(edits)!=2:raise ValueError('Two warning paints required')
 return candidate,edits

def glyphs(source,key,parent,out):
 stem=Path(key).stem
 if stem=='hud_iteminfo':
  smooth.flat.r.glyph=lambda n,w,h,font:smooth.preview(n,w,h,font)
  source,contract=smooth.flat.repair(source,source,out/'initial',FONT)
 else:contract=parent['movie_contracts'][key]
 details=contract['glyphs'];mapping={x['shape_id']:x for x in details if x['shape_id']}
 def change(tags):
  return [(c,smooth.shape(struct.unpack_from('<H',p)[0],mapping[struct.unpack_from('<H',p)[0]]['symbol'],mapping[struct.unpack_from('<H',p)[0]]['width'],mapping[struct.unpack_from('<H',p)[0]]['height'],FONT) if c==32 and struct.unpack_from('<H',p)[0] in mapping else p) for c,p in tags]
 # Also repaint native BitmapData fallback slots using the same supersampled paths.
 smooth.flat.r.glyph=lambda n,w,h,font:smooth.preview(n,w,h,font)
 names={x['bitmap_id']:x['symbol'] for x in details}
 source,blocks=smooth.flat.original_atlas_art(source,names,out,FONT)
 return replace_tags(source,change),dict(glyphs=details,math_curve_shapes=len(mapping),atlas_blocks=blocks,new_external_images=0)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--finish',action='store_true');ap.add_argument('--resume',action='store_true');a=ap.parse_args();out=a.out.resolve();deploy=a.deploy.resolve();runner=ROOT/'build/ink-hud-v3-native-runner'
 if subprocess.check_output(['git','branch','--show-current']).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
 parent=json.loads((PARENT/'receipt.json').read_text());b.font.private_path(out)
 if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('Accepted v3 archive changed')
 state=json.loads(((out if a.finish else WORK)/'live-before.json').read_text())
 if b.bars.snapshot(v.GAME,v.SETTINGS)!=state:raise ValueError('Installed inputs changed')
 if not a.finish:
  out.mkdir(exist_ok=a.resume);b.write_json(out/'live-before.json',state);files={k:(WORK/'inputs'/k).read_bytes() for k in parent['resource_hashes']};changes={};contracts={}
  for key,data in list(files.items()):
   if b.audit.sha(data)!=parent['resource_hashes'][key]:raise ValueError('V3 input mismatch')
   stem=Path(key).stem;original=data
   if a.resume and (out/'prepared-inputs'/key).exists():
    data=(out/'prepared-inputs'/key).read_bytes();files[key]=data
    if stem=='hud_iteminfo':original=(ROOT/'build/ink-hud-batch-private-v1-final/pack-input'/key).read_bytes()
    if data!=original:
     contracts[key]=v.contract(original,data,out/'base-export'/stem,out/'reexport'/stem)
     changes[key]=dict(resumed_exact_hash=b.audit.sha(data),source_patches=[str(p.relative_to(out)) for p in (out/'abc'/stem).glob('*.as')])
    print('V4 verified checkpoint',stem,flush=True);continue
   if a.resume:
    for folder in ('exports','abc','reexport','base-export','glyphs'):
     target=out/folder/stem
     if target.exists():target.rename(target.with_name(stem+'.attempt1'))
   has=key in parent['movie_contracts'] and 'glyphs' in parent['movie_contracts'][key]
   if stem=='hud_iteminfo':data=(ROOT/'build/ink-hud-batch-private-v1-final/pack-input'/key).read_bytes();original=data;has=True
   if has:data,changes[key]=glyphs(data,key,parent,out/'glyphs'/stem)
   transforms={}
   if stem=='hud_enemyfocus':transforms['HudModuleEnemyFocus']=reds
   if has:
    exp=out/'exports'/stem;exp.mkdir(parents=True);gfx=exp/'source.gfx';gfx.write_bytes(r.p.movie(data)[1]);b.export(gfx,exp)
    if list(exp.rglob('InputFeedbackButton.as')):transforms['InputFeedbackButton']=layout.button
    if list(exp.rglob('ModuleInputFeedback.as')):transforms['ModuleInputFeedback']=layout.footer
    if list(exp.rglob('HintButton.as')):transforms['HintButton']=layout.hint
   elif transforms:
    exp=out/'exports'/stem;exp.mkdir(parents=True);gfx=exp/'source.gfx';gfx.write_bytes(r.p.movie(data)[1]);b.export(gfx,exp)
   if transforms:
    data,edits=r.compile_classes(data,exp,out/'abc'/stem,transforms);changes.setdefault(key,{})['source_edits']=edits
   if stem=='hud_enemyfocus':data,changes[key]['warning']=warning(data)
   files[key]=data
   if data!=original:
    exp2=out/'reexport'/stem;exp2.mkdir(parents=True);gfx=exp2/'final.gfx';gfx.write_bytes(r.p.movie(data)[1]);b.export(gfx,exp2)
    # Public AS, listener strings, fonts and exports checked against effective input.
    exp0=out/'base-export'/stem;exp0.mkdir(parents=True);gfx0=exp0/'base.gfx';gfx0.write_bytes(r.p.movie(original)[1]);b.export(gfx0,exp0)
    contracts[key]=v.contract(original,data,exp0,exp2)
    proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-swf2xml',str(gfx),str(exp2/'final.xml')],capture_output=True,timeout=90)
    if proc.returncode:raise ValueError('Independent XML parse')
   target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   print('V4 prepared',stem,flush=True)
  b.write_json(out/'prepared-contracts.json',dict(changes=changes,movie_contracts=contracts,unchanged_keys=[k for k,d in files.items() if b.audit.sha(d)==parent['resource_hashes'][k]]))
  native={k:d for k,d in files.items() if k.endswith('.redswf')};commands=[]
  with b.mount(runner,out,native) as workspace:
   b.official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
   log=b.official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
   if 'Found 22 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Validation gate')
  for k,d in native.items():
   if (out/'cooked'/k).read_bytes()!=d:raise ValueError('Cook bytes differ')
   v.atlas_contract(d)
   p=out/'native-pack-input'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
  with b.mount(runner,out,{}) as workspace:
   b.official(runner,out,'pack',['pack','-dir='+str(out/'native-pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
   try:b.official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
   except (ValueError,subprocess.TimeoutExpired):pass
  b.write_json(out/'commands.json',commands)
  return
 files={k:(out/'prepared-inputs'/k).read_bytes() for k in parent['resource_hashes']};commands=json.loads((out/'commands.json').read_text())
 native_meta=(out/'packed/metadata.store').exists()
 if not native_meta:
  cmd=[__import__('sys').executable,str(ROOT/'tools/relocate-hud-metadata.py'),'--out',str(out)];proc=subprocess.run(cmd,capture_output=True,timeout=60);(out/'metadata-relocation.log').write_bytes(proc.stdout+proc.stderr)
  if proc.returncode:raise ValueError('Metadata relocation failed')
  commands.append(dict(label='metadata',command=cmd,exit_code=0,assertions=[],method='Native-control verified relocation; native metadata timed out'))
 script=json.loads((PARENT/'scripts/receipt.json').read_text())
 for entry in script['assembly_inputs']+script['current_required_inputs']:
  if b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Script input changed')
 for row in script['results']:
  if not row['success'] or b.fallback.sha(PARENT/'scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Compiler control changed')
 # This release changes GFx only; exactly the same WitcherScript bytes/providers.
 manifest=json.loads((out/'prepared-contracts.json').read_text());manifest.update(version='Ink & Iron HUD Refinement V4',palette={k:dict(before=a,after=c) for k,(a,c) in PALETTE.items()},owners=json.loads((WORK/'owners.json').read_text()),parent_zip_sha256=parent['zip_sha256'],script_regression=script['results'],script_compile_reused=True,opaque_mods_not_recompiled=parent['opaque_mods_not_recompiled'],official_cook_validated=True,native_metadata_passed=native_meta,live_inputs_unchanged=True,runtime_tested=False)
 manifest['glyph_font']=dict(path=str(FONT),sha256=b.fallback.sha(FONT),fonttools_version=__import__('fontTools').__version__)
 manifest['tool_sha256']={n:b.fallback.sha(ROOT/'tools'/n) for n in ('build-ink-hud-v4.py','smooth-xbox.py','polish-hud-layout.py','relocate-hud-metadata.py','rebuild-hud-v4-art.py','correct-hud-v4-centering.py','preview-hud-v4.py')}
 manifest['source_patches']={str(p.relative_to(out)):b.fallback.sha(p) for p in (out/'abc').rglob('*.as')}
 manifest['source_inputs']={k:dict(installed_v3_sha256=h,base_sha256=b.fallback.sha((ROOT/'build/ink-hud-batch-private-v1-final/pack-input'/k) if k.endswith('hud_iteminfo.redswf') else WORK/'inputs'/k),base='accepted I&I batch v1 quickslots' if k.endswith('hud_iteminfo.redswf') else 'actual deployed v3') for k,h in parent['resource_hashes'].items()}
 manifest['native_metadata_attempt']=dict(commandlet='metadatastore',timeout_seconds=240,passed=native_meta,log='metadata.full.log')
 if (out/'centering.json').exists():manifest['centering']=json.loads((out/'centering.json').read_text())
 if (out/'art-rebuild.json').exists():manifest['art_rebuild']=json.loads((out/'art-rebuild.json').read_text())
 manifest['glyph_design']=dict(canvas=[64,64],circle_diameter_before=40.96,circle_diameter_after=38,trigger_before=[51.2,32],trigger_after=[40,28],outline=1.25,xbox_prompt_scale=0.6875,label_gap=7,hold_gap=4,command_gap=20,backing_alpha_before=224,backing_alpha_after=128)
 if not native_meta:manifest['metadata_relocation']=json.loads((out/'metadata-relocation.json').read_text())
 b.MOD='modInkIronHUDRefinementV4';b.HUD=ROOT/'build/ink-hud-refinement-v2-release-final/support'
 b.package(out,deploy,set(parent['selected'])|{'iteminfo'},files,manifest,runner,commands,verified_native_reuse=True)
 archive=deploy/'Ink-Iron-HUD-Refinement-v4-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(archive);manifest['zip_path']=str(archive)
 # Prove all WS bytes match the accepted package, including state bridge.
 old={k.split('/content/',1)[1]:h for k,h in parent['package_members'].items() if k.endswith('.ws')};new={k.split('/content/',1)[1]:h for k,h in manifest['package_members'].items() if k.endswith('.ws')}
 if new!=old:raise ValueError('Script package differs: fresh compiler run required')
 if b.bars.snapshot(v.GAME,v.SETTINGS)!=state:raise ValueError('Live changed')
 b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest)
 print('V4 ready',archive,manifest['zip_sha256'],flush=True)
if __name__=='__main__':main()
