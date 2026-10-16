"""Build one isolated 0.8.6 Gear-grid prototype; never deploy or rewrite HUD."""
import argparse,configparser,importlib.util,io,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod);return mod
m=load('build-ink-hud-v4');b=m.b;p=load('patch-ink-gear-grid');native_tool=load('build-ink-hud-footer-hotfix');atlas=load('validate-inventory-atlas')
REF=ROOT/'reference/ink-and-iron-0.8.6/inventory-source';KEY='gameplay/gui_new/swf/inventory/panel_inventory.redswf';MOD='modInkIronGearGridPrototype';SCRIPTS=ROOT/'build/ink-gear-grid-v1-scripts-final'
def unique(directory,name):
 paths=list(directory.rglob(name))
 if len(paths)!=1:raise ValueError('Ambiguous '+name)
 return paths[0]
def frozen():
 settings=m.v.SETTINGS;game=m.v.GAME
 files=[settings,game/'Mods/modInkIronHUDRefinementV4/content/blob0.bundle',game/'Mods/modInkIronHUDRefinementV4/content/metadata.store',game/'Mods/mod0000_MergedFiles/content/scripts/game/gui/menus/inventorymenu.ws',game/'Mods/modHoods/content/blob0.bundle']
 return {str(f):b.fallback.sha(f) for f in files}
def run_java(out,label,args):
 cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),*map(str,args)];result=subprocess.run(cmd,capture_output=True,timeout=240);(out/(label+'.log')).write_bytes(result.stdout+result.stderr)
 if result.returncode:raise ValueError('FFDec failed '+label)
def prepare(out):
 resume=out.exists()
 if not resume:out.mkdir();b.write_json(out/'frozen.json',frozen())
 elif not (out/'after/inventory.gfx').exists() or frozen()!=json.loads((out/'frozen.json').read_text()):raise ValueError('Only exact compiled checkpoint may resume')
 pins=json.loads((REF/'source-manifest.json').read_text());source=(REF/'ui'/KEY).read_bytes()
 if b.audit.sha(source)!=pins['ui']['inventory_sha256']:raise ValueError('0.8.6 source changed')
 before=REF/'ui-export';official=unique(REF/'hoods-export/scripts','SlotPaperdoll.as').read_text(encoding='utf-8-sig')
 transforms={'SlotBase':p.slot_base,'ItemDataStub':p.item_data,'SlotPaperdoll':lambda text:p.slot_paperdoll(text,official),'SlotsListBase':p.slot_list,'ModulePaperdoll':p.paperdoll,'TooltipInventory':p.tooltip,'ContextInfoManager':p.context,'MenuInventory':p.menu}
 if resume:
  data=m.r.p.replace_movie(source,(out/'after/inventory.gfx').read_bytes());edits=[]
  for name,transform in transforms.items():
   original=unique(before/'scripts',name+'.as').read_text(encoding='utf-8-sig');patched=unique(out/('abc-prefix' if name in list(transforms)[:4] and (out/'abc-prefix').exists() else 'abc'),name+'.as')
   if patched.read_text(encoding='utf-8-sig')!=transform(original):raise ValueError('Compiled patch source changed '+name)
   edits.append(dict(class_name=name,input_sha256=b.audit.sha(original.encode()),output_sha256=b.fallback.sha(patched),compiled_checkpoint_verified=True))
  after=out/'after'
 else:
  cache=ROOT/'build/ink-gear-grid-v1/abc'
  if cache.exists() and out.name!='ink-gear-grid-v1':
   first=dict(list(transforms.items())[:4]);rest=dict(list(transforms.items())[4:])
   intermediate,early=m.r.compile_classes(source,before,out/'abc-prefix',first,cache=cache)
   data,late=m.r.compile_classes(intermediate,before,out/'abc',rest);edits=early+late
  else:data,edits=m.r.compile_classes(source,before,out/'abc',transforms)
  after=out/'after';after.mkdir();gfx=after/'inventory.gfx';gfx.write_bytes(m.r.p.movie(data)[1]);b.export(gfx,after)
  run_java(out,'xml',['-swf2xml',gfx,after/'inventory.xml'])
 declarations=b.class_contracts(before/'scripts',after/'scripts')
 old=b.public_chain(before/'scripts','MenuInventory');new=b.public_chain(after/'scripts','MenuInventory')
 if any(new.get(key)!=value for key,value in old.items()):raise ValueError('Native menu export changed')
 working=b.public_chain(REF/'installed-hoods-export/scripts','MenuInventory')
 if any(new.get(key)!=value for key,value in working.items()):raise ValueError('Installed 5.01 Hoods menu export changed')
 old_tags=b.audit.swf_tags(source)[2];new_tags=b.audit.swf_tags(data)[2]
 if [(c,v) for c,v in old_tags if c!=82]!=[(c,v) for c,v in new_tags if c!=82]:raise ValueError('Unrelated movie/art/font/export definition changed')
 if [x['tail'] for x in b.font.native.chunks(source)[1:]]!=[x['tail'] for x in b.font.native.chunks(data)[1:]]:raise ValueError('Original 0.8.6 atlas pixels changed')
 if any(not c['crc_valid'] for c in b.font.native.chunks(data)):raise ValueError('Native resource CRC invalid')
 atlas_report=atlas.validate(data)
 changed=[]
 for path in (before/'scripts').rglob('*.as'):
  other=after/'scripts'/path.relative_to(before/'scripts')
  if path.read_bytes()!=other.read_bytes():changed.append(path.name[:-3])
 if set(changed)!=set(transforms):raise ValueError('Unexpected changed class '+str(changed))
 # Prove upstream 0.8.6 step debounce and hide-line option were not rolled back
 # by using the older official Hoods movie wholesale.
 final_menu=unique(after/'scripts','MenuInventory.as').read_text(encoding='utf-8-sig');final_paper=unique(after/'scripts','SlotPaperdoll.as').read_text(encoding='utf-8-sig');a,z=p.trace.body_span(final_paper,'public function canDrop(dragData:IDragTarget) : Boolean');c,d=p.trace.body_span(official,'public function canDrop(dragData:IDragTarget) : Boolean')
 if final_paper[a+1:z]!=official[c+1:d]:raise ValueError('Official Hoods dye method not exact')
 for signature in ('protected function iaiEqStep(', 'public function iaiSetRarityStyle('):
  original=unique(before/'scripts','MenuInventory.as').read_text(encoding='utf-8-sig');a,z=p.trace.body_span(original,signature);c,d=p.trace.body_span(final_menu,signature)
  if original[a+1:z]!=final_menu[c+1:d]:raise ValueError('0.8.6 behavior rolled back')
 dest=out/'prepared-inputs'/KEY;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and dest.read_bytes()!=data:raise ValueError('Prepared candidate would change; fresh output required')
 if not dest.exists():dest.write_bytes(data)
 manifest=dict(version='Ink & Iron 0.8.6 Gear Grid Prototype v1',key=KEY,source_pins=pins,resource_sha256=b.audit.sha(data),source_edits=edits,changed_classes=changed,contracts=declarations,installed_hoods_exports_retained=len(working),atlas=atlas_report,non_abc_and_textures_exact=True,official_hoods_canDrop_exact=True,upstream_dpad_and_hide_line_retained=True,runtime_tested=False,deployed=False)
 b.write_json(out/'prepared.json',manifest);print('Gear GFx prepared; eight bounded classes, artwork exact',flush=True)
def native(out):
 data=(out/'prepared-inputs'/KEY).read_bytes();commands=[];runner=ROOT/'build/ink-hud-v3-native-runner'
 with b.mount(runner,out,{KEY:data}) as workspace:
  passed,_=native_tool.native(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
  if not passed:raise ValueError('Native cook did not pass; no success claimed')
  passed,log=native_tool.native(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
  if not passed or 'Found 1 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('One-resource native validation did not pass')
 if (out/'cooked'/KEY).read_bytes()!=data:raise ValueError('Cooked bytes changed')
 with b.mount(runner,out,{}) as workspace:
  passed,_=native_tool.native(runner,out,'pack',['pack','-dir='+str(out/'prepared-inputs'),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
  if not passed:raise ValueError('Native pack did not pass')
  passed,_=native_tool.native(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
  if not passed:raise ValueError('Native metadata did not pass; no reconstructed metadata')
 print('All four native stages passed',flush=True)
def package(out,deploy):
 if deploy.exists():raise ValueError('Fresh private deploy destination required')
 manifest=json.loads((out/'prepared.json').read_text());commands=json.loads((out/'native-commands.json').read_text())
 if not {'cook','validate','pack'} <= {r['label'] for r in commands if r['passed']}:raise ValueError('Native resource gates incomplete')
 official_metadata=any(r['label']=='metadata' and r['passed'] for r in commands)
 reconstruction=None
 if not official_metadata:
  reconstruction=json.loads((out/'metadata-reconstruction.json').read_text())
  if not reconstruction['native_control_byte_identical']:raise ValueError('Metadata control incomplete')
 receipt=json.loads((SCRIPTS/'receipt.json').read_text())
 if b.fallback.sha(ROOT/'src/inventory/inkGearGrid.ws')!=receipt['source_sha256']:raise ValueError('Compiled source changed')
 bundle=out/'packed/blob0.bundle';data=(out/'prepared-inputs'/KEY).read_bytes();entries=list(b.audit.entries(bundle));md=(out/'packed/metadata.store').read_bytes()
 if len(entries)!=1 or entries[0]['resource']!=KEY or b.bars.extract(bundle,KEY)!=data or KEY.replace('/','\\').encode() not in md:raise ValueError('Bundle extraction/metadata mismatch')
 prefix='Mods/'+MOD+'/content/';members={prefix+name:(out/'packed'/name).read_bytes() for name in ('blob0.bundle','metadata.store')};members[prefix+'scripts/local/inkGearGrid.ws']=(ROOT/'src/inventory/inkGearGrid.ws').read_bytes()
 def zipped():
  stream=io.BytesIO()
  with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
   for name,content in sorted(members.items()):
    info=zipfile.ZipInfo(name,(2026,10,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,content)
  return stream.getvalue()
 content=zipped()
 if content!=zipped():raise ValueError('Nondeterministic ZIP')
 deploy.mkdir();archive=deploy/'Ink-Iron-0.8.6-Gear-Grid-v1-private-test.zip';archive.write_bytes(content)
 with zipfile.ZipFile(archive) as z:
  if z.testzip() or {n:z.read(n) for n in z.namelist()}!=members:raise ValueError('ZIP mismatch')
 if frozen()!=json.loads((out/'frozen.json').read_text()):raise ValueError('Protected live inputs changed')
 manifest.update(zip_path=str(archive),zip_sha256=b.audit.sha(content),zip_bytes=len(content),package_members={n:b.audit.sha(v) for n,v in members.items()},native_commands=commands,native_cook_validate_pack_metadata=official_metadata,native_cook_validated=True,native_pack_passed=True,native_metadata_passed=official_metadata,metadata_reconstruction=reconstruction,exact_bundle_extraction=True,compiler=receipt,frozen_inputs=json.loads((out/'frozen.json').read_text()),original_source_hashes={str(path.relative_to(ROOT)):b.fallback.sha(path) for path in list((ROOT/'src/inventory').glob('*'))+[Path(__file__),ROOT/'tools/patch-ink-gear-grid.py',ROOT/'tools/prepare-ink-gear-source.py',ROOT/'tools/compile-ink-gear-grid.py',ROOT/'tools/validate-inventory-atlas.py',ROOT/'tools/relocate-inventory-metadata.py']})
 b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest);print('GEAR PROTOTYPE READY',archive,manifest['zip_sha256'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--stage',choices=('prepare','native','package'),required=True);a=ap.parse_args();out=a.out.resolve();deploy=a.deploy.resolve();b.font.private_path(out)
 if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
 if ROOT/'deploy' not in deploy.parents:raise ValueError('Private deploy path required')
 if a.stage=='prepare':prepare(out)
 else:
  manifest=json.loads((out/'prepared.json').read_text())
  if b.fallback.sha(out/'prepared-inputs'/KEY)!=manifest['resource_sha256'] or frozen()!=json.loads((out/'frozen.json').read_text()):raise ValueError('Prepared/live input changed')
  if a.stage=='native':native(out)
  else:package(out,deploy)
if __name__=='__main__':main()
