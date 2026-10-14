"""V4 RC1: one radial bytecode isolation, smaller A/B/X/Y interiors only.
Runtime root cause is not claimed: native/GFx validation cannot execute gameplay.
"""
import argparse,json,struct,subprocess,sys,shutil
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
BASE=ROOT/'build/ink-hud-v4-final7';WORK=ROOT/'build/ink-hud-v4-hotfix-work';V3=ROOT/'build/ink-hud-v3-final';GLYPHS=ROOT/'build/ink-hud-v4-final4/prepared-contracts.json'
original_paths=m.smooth.paths

def small_paths(name,w,h,font):
 layers=original_paths(name,w,h,font)
 if name.split('ICO_Xbox_',1)[1].split('.')[0] in ('A','B','X','Y'):
  color,path=layers[2];cx=w/2;cy=h/2
  layers[2]=(color,[(kind,tuple((cx if i%2==0 else cy)+(value-(cx if i%2==0 else cy))*0.8 for i,value in enumerate(points))) for kind,points in path])
 return layers

def restore_radial_code(source,working):
 code=[p for c,p in m.b.audit.swf_tags(working)[2] if c==82];current=[p for c,p in m.b.audit.swf_tags(source)[2] if c==82]
 if len(code)!=len(current):raise ValueError('ABC container count changed')
 replacements=iter(code)
 return m.replace_tags(source,lambda tags:[(c,next(replacements) if c==82 else p) for c,p in tags])

def prepare(out,parent):
 out.mkdir();state=json.loads((WORK/'live-before.json').read_text())
 if m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=state:raise ValueError('Live snapshot changed')
 m.b.write_json(out/'live-before.json',state);v3=json.loads((V3/'receipt.json').read_text());previous=json.loads(GLYPHS.read_text());files={};changes={}
 m.smooth.paths=small_paths
 for key,h in parent['resource_hashes'].items():
  source=(WORK/'inputs'/key).read_bytes()
  if m.b.audit.sha(source)!=h:raise ValueError('Deployed v4 input differs')
  if not key.endswith('.redswf'):
   files[key]=source;target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source);continue
  data=source;details=previous['changes'].get(key,{}).get('glyphs') or v3['movie_contracts'].get(key,{}).get('glyphs')
  if details:
   selected=[d for d in details if d['symbol'].split('ICO_Xbox_',1)[1].split('.')[0] in ('A','B','X','Y')]
   definitions={d['shape_id']:d for d in selected if d['shape_id']}
   m.smooth.flat.r.glyph=lambda n,w,h,font:m.smooth.preview(n,w,h,font)
   data,blocks=m.smooth.flat.original_atlas_art(source,{d['bitmap_id']:d['symbol'] for d in selected},out,m.FONT)
   data=m.replace_tags(data,lambda tags:[(c,m.smooth.shape(struct.unpack_from('<H',p)[0],definitions[struct.unpack_from('<H',p)[0]]['symbol'],64,64,m.FONT) if c==32 and struct.unpack_from('<H',p)[0] in definitions else p) for c,p in tags])
   changes[key]=dict(interior_scale=0.8,old_height=21,new_height=16.8,outer_layers_unchanged=True,glyphs=selected,atlas_blocks=blocks)
  if key.endswith('hud_radialmenu.redswf'):
   working=(V3/'pack-input'/key).read_bytes()
   if m.b.audit.sha(working)!=v3['resource_hashes'][key]:raise ValueError('Working v3 radial input changed')
   data=restore_radial_code(data,working);changes[key]['radial_abc_restored_from_v3']=True
  # Only A/B/X/Y Shape3 records and radial ABC may differ. All authored
  # sprites, placements, other shapes, font/import/export records stay exact.
  a=m.b.audit.swf_tags(source)[2];z=m.b.audit.swf_tags(data)[2]
  selected_ids={d['shape_id'] for d in (changes.get(key,{}).get('glyphs') or []) if d['shape_id']}
  if len(a)!=len(z):raise ValueError('Tag inventory changed')
  for (ca,pa),(cz,pz) in zip(a,z):
   if ca!=cz:raise ValueError('Tag type changed')
   allowed=(ca==32 and struct.unpack_from('<H',pa)[0] in selected_ids) or (ca==82 and key.endswith('hud_radialmenu.redswf'))
   if not allowed and pa!=pz:raise ValueError('Unrelated GFx definition changed')
  m.v.atlas_contract(data)
  if any(not c['crc_valid'] for c in m.b.font.native.chunks(data)):raise ValueError('CRCs invalid')
  files[key]=data;target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  if key in changes:
   directory=out/'exports'/Path(key).stem;directory.mkdir(parents=True);gfx=directory/'final.gfx';gfx.write_bytes(m.r.p.movie(data)[1])
   proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-swf2xml',str(gfx),str(directory/'final.xml')],capture_output=True,timeout=90)
   if proc.returncode:raise ValueError('Independent XML parse failed')
  print('Hotfix prepared',Path(key).stem,flush=True)
 m.b.write_json(out/'prepared.json',dict(changes=changes,unchanged_keys=[k for k,d in files.items() if m.b.audit.sha(d)==parent['resource_hashes'][k]],radial_abc_source_sha256=m.b.fallback.sha(V3/'pack-input/gameplay/gui_new/swf/hud/hud_radialmenu.redswf'),root_cause_confirmed=False,diagnostic=True))
 return files

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--finish',action='store_true');a=ap.parse_args();out=a.out.resolve();deploy=a.deploy.resolve();m.b.font.private_path(out)
 if subprocess.check_output(['git','branch','--show-current']).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
 parent=json.loads((BASE/'receipt.json').read_text())
 if m.b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('V4 archive changed')
 if m.b.fallback.sha(m.FONT)!=parent['glyph_font']['sha256']:raise ValueError('Pinned glyph font changed')
 runner=ROOT/'build/ink-hud-v3-native-runner'
 if not a.finish:
  if out.exists() or deploy.exists():raise ValueError('Fresh private destinations required')
  files=prepare(out,parent);native={k:d for k,d in files.items() if k.endswith('.redswf')};commands=[]
  with m.b.mount(runner,out,native) as workspace:
   m.b.official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
   log=m.b.official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
   if 'Found 22 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Native validation failed')
  for k,d in native.items():
   if (out/'cooked'/k).read_bytes()!=d:raise ValueError('Cook changed candidate')
   p=out/'native-pack-input'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
  with m.b.mount(runner,out,{}) as workspace:
   m.b.official(runner,out,'pack',['pack','-dir='+str(out/'native-pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
   try:m.b.official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
   except (ValueError,subprocess.TimeoutExpired):pass
  m.b.write_json(out/'commands.json',commands);return
 files={k:(out/'prepared-inputs'/k).read_bytes() for k in parent['resource_hashes']};commands=json.loads((out/'commands.json').read_text());native_meta=any(c['label']=='metadata' and c['exit_code']==0 for c in commands)
 if not native_meta:
  cmd=[sys.executable,str(ROOT/'tools/relocate-hud-metadata.py'),'--out',str(out)];proc=subprocess.run(cmd,capture_output=True,timeout=60);(out/'metadata-relocation.log').write_bytes(proc.stdout+proc.stderr)
  if proc.returncode:raise ValueError('Bounded metadata fallback failed')
  commands.append(dict(label='metadata',command=cmd,exit_code=0,assertions=[],method='Native-control verified relocation; native command did not pass'))
 script=json.loads((V3/'scripts/receipt.json').read_text())
 for entry in script['assembly_inputs']+script['current_required_inputs']:
  if m.b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Compiler input changed')
 for row in script['results']:
  if not row['success'] or m.b.fallback.sha(V3/'scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Compiler controls changed')
 manifest=json.loads((out/'prepared.json').read_text());manifest.update(version='HUD V4 Hotfix RC1 radial-bytecode isolation',parent_zip_sha256=parent['zip_sha256'],owners=json.loads((WORK/'owners.json').read_text()),native_metadata_passed=native_meta,official_cook_validated=True,script_compile_reused=True,script_regression=script['results'],palette_frozen=parent['palette'],runtime_tested=False,source_font=parent['glyph_font'],tool_sha256=m.b.fallback.sha(Path(__file__)))
 if not native_meta:manifest['metadata_relocation']=json.loads((out/'metadata-relocation.json').read_text())
 m.b.MOD='modInkIronHUDRefinementV4';m.b.HUD=ROOT/'build/ink-hud-refinement-v2-release-final/support'
 m.b.package(out,deploy,set(parent['selected']),files,manifest,runner,commands,verified_native_reuse=True)
 old={n.split('/content/',1)[1]:h for n,h in parent['package_members'].items() if n.endswith('.ws')};new={n.split('/content/',1)[1]:h for n,h in manifest['package_members'].items() if n.endswith('.ws')}
 if old!=new:raise ValueError('WitcherScript changed')
 menu='bin/config/r4game/user_config_matrix/pc/modInkIronHUDBatch.xml'
 if parent['package_members'][menu]!=manifest['package_members'][menu]:raise ValueError('Menu registration content changed')
 if m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=json.loads((out/'live-before.json').read_text()):raise ValueError('Live inputs changed')
 archive=deploy/'Ink-Iron-HUD-v4-Hotfix-RC1-radial-isolation-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(archive);manifest['zip_path']=str(archive)
 m.b.write_json(out/'receipt.json',manifest);m.b.write_json(deploy/'manifest.json',manifest);print('RC1 ready',archive,manifest['zip_sha256'])
if __name__=='__main__':main()
