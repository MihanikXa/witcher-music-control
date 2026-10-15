"""Private RC2: remove only the demonstrated shared footer lexical-name fault.
No deployment; clean RC1 support/artwork. Native and reconstructed stages separate.
"""
import argparse,configparser,importlib.util,io,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));module=importlib.util.module_from_spec(s);s.loader.exec_module(module);return module
m=load('build-ink-hud-v4');b=m.b;repair=load('repair-ink-hud-footer');trace=load('instrument-radial-movies');packer=load('reconstruct-radial-trace-bundle')
BASE=ROOT/'build/ink-hud-v4-hotfix-rc1-final';WORK=ROOT/'build/ink-hud-footer-hotfix-work';KEY='gameplay/gui_new/swf/hud/hud.redswf';CLASS='red.game.witcher3.menus.common_menu.ModuleInputFeedback'
def one(directory,name):
 paths=list(directory.rglob(name));
 if len(paths)!=1:raise ValueError('Nonunique '+name)
 return paths[0]
def method(text):
 a,z=trace.body_span(text,'protected function repositionButtons()');return text[a+1:z]
def ffdec(out,label,args):
 cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),*map(str,args)];p=subprocess.run(cmd,capture_output=True,timeout=180);(out/(label+'.log')).write_bytes(p.stdout+p.stderr)
 if p.returncode:raise ValueError('FFDec failed '+label)
def snapshot():
 """Fresh read-only installed D1 extraction, never modifying deployment."""
 WORK.mkdir()
 d1=json.loads((ROOT/'build/ink-radial-trace-d1-release-final/receipt.json').read_text())
 if b.fallback.sha(Path(d1['zip_path']))!=d1['zip_sha256']:raise ValueError('D1 archive changed')
 cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.settings_text(m.v.SETTINGS))
 owners=b.owners(m.v.GAME,cfg,set(d1['resource_hashes']),WORK)
 b.write_json(WORK/'owners.json',owners);b.write_json(WORK/'live-before.json',b.bars.snapshot(m.v.GAME,m.v.SETTINGS))
 for key,expected in d1['resource_hashes'].items():
  winner=sorted([r for r in owners[key] if r.get('enabled')=='1'],key=lambda r:int(r.get('priority') or 9999))[0]
  if winner['sha256']!=expected:raise ValueError('Installed D1 resource differs: '+key)
  if key==KEY:
   container=Path(winner['container']);entry=next(e for e in b.audit.entries(container) if e['resource']==key)
   data=b.read_bundle(container,entry,m.v.GAME,WORK);(WORK/'installed-hud.redswf').write_bytes(data)
   gfx=WORK/'installed-hud.gfx';gfx.write_bytes(m.r.p.movie(data)[1]);b.export(gfx,WORK/'installed-export')
   ffdec(WORK,'installed-pcode',['-selectclass',CLASS,'-format','script:pcode','-export','script',WORK/'installed-pcode',gfx])
def native(runner,out,label,args,commands):
 exe=runner/'bin/x64_RedKit/wcc_lite.exe'
 if b.fallback.sha(exe)!=b.font.COMPILER_SHA:raise ValueError('Native compiler pin')
 temporary=out/('temp-'+label);temporary.mkdir();cmd=[str(exe),*args]
 try:
  p=subprocess.run(cmd,cwd=exe.parent,env=dict(os.environ,TEMP=str(temporary),TMP=str(temporary)),capture_output=True,timeout=90)
  row=dict(label=label,command=cmd,exit_code=p.returncode,passed=False);output=p.stdout+p.stderr
 except subprocess.TimeoutExpired as error:
  row=dict(label=label,command=cmd,exit_code=None,passed=False,timeout_seconds=90);output=(error.stdout or b'')+(error.stderr or b'')
 log=(runner/'bin/wcc.log').read_text(errors='replace') if (runner/'bin/wcc.log').exists() else ''
 (out/(label+'.full.log')).write_text(log);(out/(label+'.stdout.log')).write_bytes(output)
 assertions=[line for line in log.splitlines() if '[Error][Assert]' in line];row['assertions']=assertions
 row['passed']=row['exit_code']==0 and not any(not any(s in line for s in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for line in assertions)
 commands.append(row);b.write_json(out/'native-commands.json',commands);print('Native',label,'passed' if row['passed'] else 'did not complete successfully',flush=True)
 return row['passed'],log

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--prepared',action='store_true');a=ap.parse_args();out=a.out.resolve();deploy=a.deploy.resolve();b.font.private_path(out)
 if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
 if ROOT/'deploy' not in deploy.parents or deploy.exists():raise ValueError('Fresh private deploy path required')
 if not WORK.exists():snapshot()
 parent=json.loads((BASE/'receipt.json').read_text())
 if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('RC1 archive changed')
 state=json.loads((WORK/'live-before.json').read_text())
 if b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=state:raise ValueError('Deployed inputs changed')
 if a.prepared:
  manifest=json.loads((out/'prepared.json').read_text());files={k:(out/'prepared-inputs'/k).read_bytes() for k in parent['resource_hashes']}
  if {k:b.audit.sha(v) for k,v in files.items()}!=manifest['resource_hashes']:raise ValueError('Prepared bytes changed')
 else:
  out.mkdir();files={k:(ROOT/'build/ink-radial-trace-work/inputs'/k).read_bytes() for k in parent['resource_hashes']}
  if {k:b.audit.sha(v) for k,v in files.items()}!=parent['resource_hashes']:raise ValueError('RC1 inputs changed')
  source=files[KEY];before=out/'before';before.mkdir();gfx=before/'source.gfx';gfx.write_bytes(m.r.p.movie(source)[1]);b.export(gfx,before)
  original=one(before/'scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig');modified=repair.repair(original)
  installed=one(WORK/'installed-export/scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
  if not repair.V4_FIT.search(method(installed)) or 'var buttonsSize' in installed:raise ValueError('Prepared correction not demonstrated in deployed source')
  pcode=one(WORK/'installed-pcode','ModuleInputFeedback.pcode').read_text()
  if pcode.count('getlex Multiname("buttonsSize",')!=3:raise ValueError('Expected actual unresolved lexical instructions')
  working=one(ROOT/'build/ink-hud-v3-final/vector-export/hud/scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
  if method(modified)!=method(working):raise ValueError('Repaired method must equal working v3 exactly')
  candidate,edits=m.r.compile_classes(source,before,out/'abc',{'ModuleInputFeedback':repair.repair});files[KEY]=candidate
  after=out/'after';after.mkdir();final=after/'final.gfx';final.write_bytes(m.r.p.movie(candidate)[1]);b.export(final,after)
  ffdec(out,'final-xml',['-swf2xml',final,after/'final.xml']);ffdec(out,'final-pcode',['-selectclass',CLASS,'-format','script:pcode','-export','script',out/'final-pcode',final])
  if 'buttonsSize' in one(out/'final-pcode','ModuleInputFeedback.pcode').read_text():raise ValueError('Unresolved lexical name remains')
  diff=[]
  for path in (before/'scripts').rglob('*.as'):
   other=after/'scripts'/path.relative_to(before/'scripts')
   if path.read_bytes()!=other.read_bytes():diff.append(path.relative_to(before/'scripts').as_posix())
  if diff!=['red/game/witcher3/menus/common_menu/ModuleInputFeedback.as']:raise ValueError('Unrelated classes changed '+str(diff))
  result=one(after/'scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
  if result!=modified:raise ValueError('Compiled source differs outside exact two-statement repair')
  if [(c,p) for c,p in b.audit.swf_tags(source)[2] if c!=82]!=[(c,p) for c,p in b.audit.swf_tags(candidate)[2] if c!=82]:raise ValueError('Non-ABC artwork changed')
  if [c['tail'] for c in b.font.native.chunks(source)[1:]]!=[c['tail'] for c in b.font.native.chunks(candidate)[1:]]:raise ValueError('Texture data changed')
  m.v.atlas_contract(candidate)
  if any(not c['crc_valid'] for c in b.font.native.chunks(candidate)):raise ValueError('Native CRC invalid')
  contract=b.class_contracts(before/'scripts',after/'scripts')
  if b.public_chain(before/'scripts','Hud')!=b.public_chain(after/'scripts','Hud'):raise ValueError('Root/OW export signatures changed')
  manifest=dict(version='HUD v4 Hotfix RC2 shared footer correction',source_defect_confirmed=True,runtime_tested=False,parent_zip_sha256=parent['zip_sha256'],modified_resource=KEY,source_edits=edits,modified_classes=diff,method_matches_working_v3=True,non_abc_definitions_exact=True,texture_tails_exact=True,contracts=contract,resource_hashes={k:b.audit.sha(v) for k,v in files.items()},unchanged_keys=[k for k,v in files.items() if b.audit.sha(v)==parent['resource_hashes'][k]],installed_owners=json.loads((WORK/'owners.json').read_text()))
  for key,data in files.items():
   dest=out/'prepared-inputs'/key;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  b.write_json(out/'prepared.json',manifest);print('One shared method repaired; all other class sources/artwork exact',flush=True)
 # No new WitcherScript: pin the successful exact-source compiler controls.
 receipt=json.loads((ROOT/'build/ink-hud-v3-final/scripts/receipt.json').read_text())
 for entry in receipt['assembly_inputs']+receipt['current_required_inputs']:
  if b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Script provider changed')
 for row in receipt['results']:
  if not row['success'] or b.fallback.sha(ROOT/'build/ink-hud-v3-final/scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Verified compiler control changed')
 manifest['script_compile_reused']=True;manifest['script_control_blob_hashes']={row['label']:row['blob_sha256'] for row in receipt['results']}
 runner=ROOT/'build/ink-hud-v3-native-runner';commands=[];native_files={k:v for k,v in files.items() if k.endswith('.redswf')}
 with b.mount(runner,out,native_files) as workspace:
  cooked,_=native(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
  if not cooked and commands[-1]['exit_code'] is not None:raise ValueError('Native cook rejected candidate; no reconstruction bypass')
  validated=False
  if cooked:
   validated,log=native(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
   validated=validated and 'Found 22 files to validate' in log and 'Errors found in 0 resources:' in log
   if not validated:raise ValueError('Native validation rejected resource or did not complete')
   for key,data in native_files.items():
    if (out/'cooked'/key).read_bytes()!=data:raise ValueError('Native cook changed bytes')
 packed=False;metadata=False
 if cooked and validated:
  for key,data in native_files.items():
   target=out/'native-pack-input'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  with b.mount(runner,out,{}) as workspace:
   packed,_=native(runner,out,'pack',['pack','-dir='+str(out/'native-pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
   if not packed and commands[-1]['exit_code'] is not None:raise ValueError('Native pack rejected candidate; no reconstruction bypass')
   if packed:metadata,_=native(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
   if packed and not metadata and commands[-1]['exit_code'] is not None:raise ValueError('Native metadata rejected candidate; no reconstruction bypass')
 manifest.update(native_commands=commands,official_cook_validated=cooked and validated,native_pack_passed=packed,native_metadata_passed=metadata)
 if not packed:
  if (out/'packed').exists():raise ValueError('Partial native pack requires inspection')
  controls=[]
  for name in ('ink-hud-refinement-v2-release-final','ink-hud-v3-diagnostic-final','ink-radial-trace-d1-final'):
   bundle=ROOT/'build'/name/'packed/blob0.bundle';control_files={e['resource']:b.bars.extract(bundle,e['resource']) for e in b.audit.entries(bundle)};reproduced=packer.reconstruct(bundle,control_files)
   if reproduced!=bundle.read_bytes():raise ValueError('Native bundle control mismatch')
   controls.append(dict(path=str(bundle),sha256=b.fallback.sha(bundle),byte_identical=True))
  packed_dir=out/'packed';packed_dir.mkdir();(packed_dir/'blob0.bundle').write_bytes(packer.reconstruct(ROOT/'build/ink-radial-trace-d1-final/packed/blob0.bundle',native_files));manifest['bundle_reconstruction_controls']=controls
 if not metadata:
  if (out/'packed/metadata.store').exists():raise ValueError('Partial native metadata requires inspection')
  cmd=[sys.executable,str(ROOT/'tools/relocate-hud-metadata.py'),'--out',str(out)];p=subprocess.run(cmd,capture_output=True,timeout=60);(out/'metadata-relocation.log').write_bytes(p.stdout+p.stderr)
  if p.returncode:raise ValueError('Guarded metadata reconstruction failed')
  manifest['metadata_relocation']=json.loads((out/'metadata-relocation.json').read_text())
 bundle=out/'packed/blob0.bundle';md=(out/'packed/metadata.store').read_bytes()
 if {e['resource'] for e in b.audit.entries(bundle)}!=set(native_files):raise ValueError('Pack contains unrelated keys')
 for key,data in native_files.items():
  if b.bars.extract(bundle,key)!=data or key.replace('/','\\').encode() not in md:raise ValueError('Extraction/metadata key mismatch')
 with zipfile.ZipFile(parent['zip_path']) as z:members={name:z.read(name) for name in z.namelist()}
 for name in ('blob0.bundle','metadata.store'):members['Mods/modInkIronHUDRefinementV4/content/'+name]=(out/'packed'/name).read_bytes()
 if any('inkRadialDiagnostic' in name for name in members):raise ValueError('Diagnostic accidentally included')
 def zipped():
  buffer=io.BytesIO()
  with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
   for name,data in sorted(members.items()):
    info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
  return buffer.getvalue()
 archive_data=zipped()
 if archive_data!=zipped():raise ValueError('Non-deterministic ZIP')
 deploy.mkdir();archive=deploy/'Ink-Iron-HUD-v4-Hotfix-RC2-footer-private-test.zip';archive.write_bytes(archive_data)
 with zipfile.ZipFile(archive) as z:
  if z.testzip() or {name:z.read(name) for name in z.namelist()}!=members:raise ValueError('ZIP failed extraction')
 manifest.update(zip_path=str(archive),zip_sha256=b.audit.sha(archive_data),zip_bytes=len(archive_data),package_members={name:b.audit.sha(data) for name,data in members.items()},exact_reextraction=True,deployed=False,original_tool_hashes={name:b.fallback.sha(ROOT/'tools'/name) for name in ('build-ink-hud-footer-hotfix.py','repair-ink-hud-footer.py','polish-hud-layout.py')})
 if b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=state:raise ValueError('Live inputs changed')
 b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest);print('RC2 READY',archive,manifest['zip_sha256'],flush=True)
if __name__=='__main__':main()
