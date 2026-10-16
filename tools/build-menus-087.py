"""Private modular menu baseline. Never installs or changes accepted HUD inputs."""
import argparse,concurrent.futures,configparser,importlib.util,io,json,re,struct,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('build-ink-hud-v4');patch=load('patch-menu-migration');hotfix=load('build-ink-hud-v4-hotfix');native=load('build-ink-hud-footer-hotfix');atlas=load('validate-inventory-atlas')
E=patch.E;REF=E.parent;OUT=ROOT/'build/menus087-v1-r2';SCRIPTS=ROOT/'build/menus087-v1/scripts';DEPLOY=ROOT/'deploy/menus087-v1';MOD='modInkIronMenus087'
INPUT_CLASSES=['red.game.witcher3.controls.InputFeedbackButton','red.game.witcher3.controls.HintButton','red.game.witcher3.menus.common_menu.ModuleInputFeedback']
def java(folder,label,args):
 p=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),*map(str,args)],capture_output=True,timeout=240);(folder/(label+'.log')).write_bytes(p.stdout+p.stderr)
 if p.returncode:raise ValueError('FFDec '+label+' failed')
def selected_export(data,folder,classes):
 folder.mkdir(parents=True,exist_ok=True);f=folder/'source.gfx';f.write_bytes(m.r.p.movie(data)[1]);java(folder,'export',['-selectclass',','.join(classes),'-export','script',folder,f])
def batch_compile(source,before,folder,transforms):
 folder.mkdir(exist_ok=True);src=folder/'input.gfx';input_data=m.r.p.movie(source)[1]
 if src.exists() and src.read_bytes()!=input_data:raise ValueError('Compiled checkpoint input changed')
 src.write_bytes(input_data);dest=folder/'compiled.gfx';args=['-replace',src,dest];changes=[];reuse=dest.exists()
 for name,fn in transforms.items():
  path=patch.one_file(before/'scripts',name);text=path.read_text(encoding='utf-8-sig');changed=fn(text)
  replacement=folder/(name+'.as')
  if reuse and replacement.read_text(encoding='utf-8')!=changed:raise ValueError('Compiled checkpoint source changed')
  replacement.write_text(changed,encoding='utf-8',newline='\n');namespace=path.relative_to(before/'scripts').with_suffix('').as_posix().replace('/','.')
  args += [namespace,replacement];changes.append(dict(class_name=name,input_sha256=m.b.audit.sha(text.encode()),output_sha256=m.b.audit.sha(changed.encode())))
 if not reuse:java(folder,'compile',args)
 if not dest.exists() or b'Error:' in (folder/'compile.log').read_bytes():raise ValueError('AS compilation failed')
 return m.r.p.replace_movie(source,m.r.p.compose(source,dest.read_bytes())),changes
def glyphs(source,folder):
 symbols=m.b.contracts.symbols(m.b.audit.swf_tags(source)[2]);names=[k for k in symbols if 'ICO_Xbox_' in k]
 if not names:return source,{'placement_count':0}
 # Same direct paths and 0.8 interior letters accepted in RC1/RC2. No pixel tracing.
 m.smooth.paths=hotfix.small_paths
 def preview(name,w,h,font):
  image=m.smooth.preview(name,w,h,font);image.info['symbol']=name;return image
 m.smooth.flat.r.glyph=preview
 m.smooth.flat.shape=lambda cid,image:m.smooth.shape(cid,image.info['symbol'],image.width,image.height,m.FONT)
 # Inventory contains both BC1 and BC3 atlases. The previous HUD-only guard
 # rejected this unchanged upstream contract; validate both observed encodings.
 m.smooth.flat.b.atlas_contract=atlas.validate
 while folder.exists():folder=folder.with_name(folder.name+'-resume')
 return m.smooth.flat.repair(source,source,folder,m.FONT)
def process(job):
 key,row=job;stem=Path(key).stem;folder=OUT/'movies'/stem;folder.mkdir(parents=True,exist_ok=True);source=Path(row['path']).read_bytes();classes=list(INPUT_CLASSES);transforms={}
 special={'panel_common':('MenuCommon',patch.common),'panel_inventory':('SlotPaperdoll',patch.hoods_slot),'panel_worldmap':('HubMap',patch.smooth_map)}
 if stem in special:
  name,fn=special[stem];transforms[name]=fn
  namespace={'panel_common':'red.game.witcher3.menus.common_menu.MenuCommon','panel_inventory':'red.game.witcher3.slots.SlotPaperdoll','panel_worldmap':'red.game.witcher3.menus.worldmap.HubMap'}[stem];classes.append(namespace)
 if stem=='panel_inventory':transforms['ItemDataStub']=patch.hoods_data;classes.append('red.game.witcher3.menus.common.ItemDataStub')
 if stem=='panel_common':transforms['TopBarNew']=patch.topbar;classes.append('red.game.witcher3.menus.common_menu.TopBarNew')
 known=E/'0.8.7-export'/stem;before=known if known.exists() else folder/'before'
 if before!=known:selected_export(source,before,classes)
 adapters={'InputFeedbackButton':patch.menu_button,'HintButton':m.layout.hint,'ModuleInputFeedback':m.layout.footer}
 for namespace in INPUT_CLASSES:
  name=namespace.split('.')[-1];paths=list((before/'scripts').rglob(name+'.as'))
  if paths:
   transforms[name]=adapters[name]
 # Incomplete selected namespaces are rejected, not silently skipped.
 for name in list(transforms):patch.one_file(before/'scripts',name)
 if (folder/'receipt.json').exists():
  old=json.loads((folder/'receipt.json').read_text());target=OUT/'prepared-inputs'/key
  if old['input_sha256']!=m.b.audit.sha(source) or old['output_sha256']!=m.b.fallback.sha(target):raise ValueError('Completed movie checkpoint changed')
  for name,fn in transforms.items():
   expected=fn(patch.one_file(before/'scripts',name).read_text(encoding='utf-8-sig'))
   if (folder/'abc'/(name+'.as')).read_text(encoding='utf-8')!=expected:raise ValueError('Completed source changed')
  return old
 data,edits=batch_compile(source,before,folder/'abc',transforms) if transforms else (source,[])
 data,glyph=glyphs(data,folder/'glyphs')
 after=folder/'after';selected_export(data,after,classes)
 # Every original SymbolClass export and retained class declaration must survive.
 if m.b.contracts.symbols(m.b.audit.swf_tags(source)[2])!=m.b.contracts.symbols(m.b.audit.swf_tags(data)[2]):raise ValueError('Symbol exports changed '+key)
 count=0
 for name in transforms:
  old=patch.one_file(before/'scripts',name).read_text(encoding='utf-8-sig');new=patch.one_file(after/'scripts',name).read_text(encoding='utf-8-sig')
  for signature in re.findall(r'(?:public|protected) function (?:get |set )?\w+\([^\n]*',old):
   # Parameter names may change when accepted RC2 classes replace equivalent upstream classes.
   sig=re.sub(r'\b\w+(?=\s*:)', '', signature).replace(' ','')
   candidates=[re.sub(r'\b\w+(?=\s*:)', '', s).replace(' ','') for s in re.findall(r'(?:public|protected) function (?:get |set )?\w+\([^\n]*',new)]
   if sig not in candidates:raise ValueError('Class interface lost '+name+': '+signature)
   count+=1
 if not all(c['crc_valid'] for c in m.b.font.native.chunks(data)):raise ValueError('CRC failed')
 report=atlas.validate(data)
 target=OUT/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 receipt=dict(resource=key,input_sha256=m.b.audit.sha(source),output_sha256=m.b.audit.sha(data),classes=edits,glyphs=glyph,atlas=report,retained_public_protected_declarations=count)
 m.b.write_json(folder/'receipt.json',receipt);print('Prepared',stem,flush=True);return receipt
def verify_cache_and_dlc(ledger):
 path=REF/'mods/modInkAndIronUI/content/texture.cache';rows=list(m.b.inventory.cache_entries(path));keys={r['resource'] for r in rows};cfg=configparser.ConfigParser();cfg.read_string(m.b.settings_text(m.v.SETTINGS));hits=[];empty=[]
 for folder in (m.v.GAME/'Mods').iterdir():
  if folder.name in cfg and cfg[folder.name].get('Enabled')=='1':
   for p in folder.rglob('texture.cache'):
    if not p.stat().st_size:empty.append(str(p));continue
    overlap=keys & {r['resource'] for r in m.b.inventory.cache_entries(p)}
    if overlap:hits.append({'owner':folder.name,'keys':sorted(overlap)})
 if hits:raise ValueError('New UI texture collision needs an explicit owner decision')
 m.b.write_json(OUT/'texture-cache-check.json',dict(source_sha256=m.b.fallback.sha(path),entries=len(rows),collisions=hits,empty_cache_placeholders=empty))
 keys={k for k,r in ledger['versions']['0.8.7']['resources'].items() if r['module'] in ('UI','Buttons')};dlc=[]
 for bundle in (m.v.GAME/'DLC').rglob('*.bundle'):
  for e in m.b.audit.entries(bundle):
   if e['resource'] in keys:dlc.append(dict(resource=e['resource'],bundle=str(bundle)))
 if dlc:raise ValueError('DLC UI collision needs review')
 m.b.write_json(OUT/'dlc-owner-check.json',dlc)
def prepare():
 OUT.mkdir(exist_ok=True);ledger=json.loads((E/'ledger.json').read_text())
 if m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=ledger['frozen']:raise ValueError('Live inputs changed')
 m.b.write_json(OUT/'frozen.json',ledger['frozen'])
 verify_cache_and_dlc(ledger)
 rows={k:r for k,r in ledger['versions']['0.8.7']['resources'].items() if k.endswith('.redswf') and (r['module']=='UI' and not k.endswith('/panel_overlay.redswf') or r['module']=='Buttons' and '/hud/' not in k)}
 movies=[(k,r) for k,r in rows.items() if k.endswith('.redswf')];results=[]
 # Native/Java processes are isolated; only two independent movies run at once.
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for r in pool.map(process,movies):results.append(r)
 for k,r in rows.items():
  if not k.endswith('.redswf'):
   target=OUT/'prepared-inputs'/k;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(Path(r['path']).read_bytes())
 m.b.write_json(OUT/'prepared.json',dict(resources=results,keys=sorted(rows),source_archive=ledger['archive'],runtime_tested=False,deployed=False))
def native_build():
 files={k:(OUT/'prepared-inputs'/k).read_bytes() for k in json.loads((OUT/'prepared.json').read_text())['keys']};commands=[];runner=ROOT/'build/ink-hud-v3-native-runner';work=OUT/'native-final';work.mkdir()
 with m.b.mount(runner,work,files) as workspace:
  ok,_=native.native(runner,work,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(work/'cooked')],commands)
  if not ok:raise ValueError('Native cook failed')
  ok,log=native.native(runner,work,'validate',['validate','-db='+str(work/'cooked/cook.db'),'-outdir='+str(work/'validation')],commands)
  if not ok or 'Errors found in 0 resources:' not in log:
   commands[-1]['passed']=False;m.b.write_json(work/'native-commands.json',commands);raise ValueError('Native resource validation failed')
 for key,value in files.items():
  if (work/'cooked'/key).read_bytes()!=value:raise ValueError('Cooked bytes changed '+key)
 pack_input=work/'pack-input'
 for key,value in files.items():
  p=pack_input/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
 with m.b.mount(runner,work,{}) as workspace:
  for label,args in [('pack',['pack','-dir='+str(pack_input),'-outdir='+str(OUT/'packed'),'-compression=ZLIB']),('metadata',['metadatastore','-path='+str(OUT/'packed')])]:
   ok,_=native.native(runner,work,label,args,commands)
   if not ok:raise ValueError('Native '+label+' failed; no success inferred')
 m.b.write_json(OUT/'native-commands.json',commands)
def package():
 if DEPLOY.exists():raise ValueError('Fresh deploy directory required')
 prepared=json.loads((OUT/'prepared.json').read_text());script=json.loads((SCRIPTS/'receipt.json').read_text());commands=json.loads((OUT/'native-commands.json').read_text())
 if m.b.fallback.sha(Path(script['options_base_path']))!=script['options_base_sha256']:raise ValueError('Current settings page changed')
 if {r['label'] for r in commands if r['passed']}!={'cook','validate','pack','metadata'}:raise ValueError('Incomplete native pipeline')
 bundle=OUT/'packed/blob0.bundle';entries=list(m.b.audit.entries(bundle))
 if {e['resource'] for e in entries}!=set(prepared['keys']):raise ValueError('Unexpected resource')
 for e in entries:
  if m.b.bars.extract(bundle,e['resource'])!=(OUT/'prepared-inputs'/e['resource']).read_bytes():raise ValueError('Extraction failed')
 prefix='Mods/'+MOD+'/content/';members={prefix+n:(OUT/'packed'/n).read_bytes() for n in ('blob0.bundle','metadata.store')}
 members[prefix+'texture.cache']=(REF/'mods/modInkAndIronUI/content/texture.cache').read_bytes()
 if m.b.audit.sha(members[prefix+'texture.cache'])!=json.loads((OUT/'texture-cache-check.json').read_text())['source_sha256']:raise ValueError('Texture cache changed')
 for p in (SCRIPTS/'vendor').glob('*.ws'):members[prefix+'scripts/local/'+p.name]=p.read_bytes()
 # Retain existing HUD options: only add menu vars to its independently named page.
 for p in (SCRIPTS.parent/'options').glob('*'):members['bin/config/r4game/user_config_matrix/pc/'+p.name]=p.read_bytes()
 def zip_bytes():
  stream=io.BytesIO()
  with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
   for name,data in sorted(members.items()):
    i=zipfile.ZipInfo(name,(2026,10,16,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16;z.writestr(i,data)
  return stream.getvalue()
 data=zip_bytes()
 if data!=zip_bytes():raise ValueError('Nondeterministic ZIP')
 if m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Live installation changed')
 DEPLOY.mkdir();archive=DEPLOY/'Ink-Iron-0.8.7-Compatible-Menus-v1-private-test.zip';archive.write_bytes(data)
 with zipfile.ZipFile(archive) as z:
  if z.testzip():raise ValueError('ZIP CRC failed')
 receipt=dict(prepared=prepared,native=commands,scripts=script,zip_path=str(archive),zip_sha256=m.b.audit.sha(data),zip_bytes=len(data),members={k:m.b.audit.sha(v) for k,v in members.items()},frozen_unchanged=True,runtime_tested=False)
 m.b.write_json(OUT/'receipt.json',receipt);print('PRIVATE MENUS READY',archive,receipt['zip_sha256'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','native','package'));a=ap.parse_args()
 if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Wrong branch')
 {'prepare':prepare,'native':native_build,'package':package}[a.stage]()
if __name__=='__main__':main()
