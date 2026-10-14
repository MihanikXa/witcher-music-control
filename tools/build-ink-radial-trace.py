"""One instrumented RC1 diagnostic. No forced wheel opening or live deployment."""
import argparse,json,subprocess,shutil,struct,sys,importlib.util,os,zipfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'tools'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('build-ink-hud-v4');i=load('instrument-radial-movies');b=m.b
BASE=ROOT/'build/ink-hud-v4-hotfix-rc1-final';WORK=ROOT/'build/ink-radial-trace-work';SCRIPT_CACHE=ROOT/'build/ink-radial-trace-script-full-control'

def official(runner,out,label,args,commands):
 exe=runner/'bin/x64_RedKit/wcc_lite.exe'
 if b.fallback.sha(exe)!=b.font.COMPILER_SHA:raise ValueError('Native compiler changed')
 temporary=out/('native-temp-'+label);temporary.mkdir(exist_ok=True)
 cmd=[str(exe),*args];env=dict(os.environ,TEMP=str(temporary),TMP=str(temporary))
 try:p=subprocess.run(cmd,cwd=exe.parent,env=env,capture_output=True,timeout=240)
 except subprocess.TimeoutExpired as error:
  (out/(label+'.stdout.log')).write_bytes((error.stdout or b'')+(error.stderr or b''))
  if (runner/'bin/wcc.log').exists():shutil.copy2(runner/'bin/wcc.log',out/(label+'.full.log'))
  raise
 log=(runner/'bin/wcc.log').read_text(errors='replace');(out/(label+'.full.log')).write_text(log);(out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
 assertions=[line for line in log.splitlines() if '[Error][Assert]' in line]
 commands.append(dict(label=label,command=cmd,cwd=str(exe.parent),temporary_directory=str(temporary),exit_code=p.returncode,assertions=assertions));b.write_json(out/'commands.json',commands)
 if p.returncode or any(not any(x in line for x in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for line in assertions):raise ValueError('Native stage failed: '+label)
 print('Native',label,'passed',flush=True);return log

def script_evidence(out):
 evidence={}
 for label in ('control','candidate'):
  log=(SCRIPT_CACHE/(label+'.full.log')).read_text(errors='replace');blob=SCRIPT_CACHE/label/'blob.rsblob'
  if '[Error][Script]' in log or '[Error][WCC]' in log or 'Success! Patch scripts blob saved' not in log or not blob.exists():raise ValueError('Fresh script controls did not pass')
  evidence[label]=dict(blob_sha256=b.fallback.sha(blob),warnings=dict(b.bars.diagnostics.diagnostic_counter(log,'[Warning]')),assertions=dict(b.bars.diagnostics.diagnostic_counter(log,'[Error][Assert]')))
 if evidence['control']['warnings']!=evidence['candidate']['warnings'] or evidence['control']['assertions']!=evidence['candidate']['assertions']:raise ValueError('Diagnostic regressed matched script control')
 if b.fallback.text(SCRIPT_CACHE/'patch/local/inkRadialDiagnostic.ws')!=b.fallback.text(ROOT/'src/hud/inkRadialDiagnostic.ws'):raise ValueError('Compiled diagnostic source changed')

 if not (out/'scripts').exists():shutil.copytree(SCRIPT_CACHE,out/'scripts')
 return evidence

def reconstructed_package(out,deploy,parent,files,manifest):
 # Clone support from the immutable RC1 archive, replacing only the exact
 # bundle/metadata pair and adding our original diagnostic annotation.
 reconstruction=json.loads((out/'bundle-reconstruction.json').read_text())
 if not reconstruction['diagnostic_only'] or not all(c['byte_identical'] for c in reconstruction['controls']) or len(reconstruction['controls'])!=3:raise ValueError('Native reconstruction controls missing')
 with zipfile.ZipFile(parent['zip_path']) as archive:members={n:archive.read(n) for n in archive.namelist()}
 prefix='Mods/modInkIronHUDRefinementV4/content/'
 for name in ('blob0.bundle','metadata.store'):members[prefix+name]=(out/'packed'/name).read_bytes()
 members[prefix+'scripts/local/inkRadialDiagnostic.ws']=(ROOT/'src/hud/inkRadialDiagnostic.ws').read_bytes()
 bundle=out/'packed/blob0.bundle';metadata=members[prefix+'metadata.store']
 native={k:v for k,v in files.items() if k.endswith('.redswf')}
 if {e['resource'] for e in b.audit.entries(bundle)}!=set(native):raise ValueError('Bundle key mismatch')
 for key,data in native.items():
  if b.bars.extract(bundle,key)!=data or key.replace('/','\\').encode() not in metadata:raise ValueError('Extraction/metadata key mismatch')
 def zipped():
  buffer=io.BytesIO()
  with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
   for key,data in sorted(members.items()):
    info=zipfile.ZipInfo(key,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;archive.writestr(info,data)
  return buffer.getvalue()
 data=zipped()
 if data!=zipped():raise ValueError('Nondeterministic diagnostic ZIP')
 deploy.mkdir();archive=deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip';archive.write_bytes(data)
 with zipfile.ZipFile(archive) as z:
  if z.testzip() or {n:z.read(n) for n in z.namelist()}!=members:raise ValueError('ZIP verification failed')
 manifest.update(mod='modInkIronHUDRefinementV4',selected=parent['selected'],package_members={k:b.audit.sha(v) for k,v in members.items()},resource_hashes={k:b.audit.sha(v) for k,v in files.items()},zip_sha256=b.audit.sha(data),zip_bytes=len(data),exact_reextraction=True,metadata_keys_verified=True,bundle_reconstruction=reconstruction,official_cook_validated=False,compiler_sha256=b.font.COMPILER_SHA,ffdec_sha256=b.fallback.sha(ROOT/'build/tools/ffdec/ffdec.jar'),deployed=False)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);ap.add_argument('--finish',action='store_true');ap.add_argument('--resume',action='store_true');ap.add_argument('--diagnostic-reconstruction',action='store_true');ap.add_argument('--runner',type=Path,default=ROOT/'build/ink-hud-v3-native-runner');a=ap.parse_args();out=a.out.resolve();deploy=a.deploy.resolve();b.font.private_path(out)
 if ROOT/'deploy' not in deploy.parents or deploy.exists():raise ValueError('Fresh private deploy destination required')
 if a.diagnostic_reconstruction and not a.finish:raise ValueError('Explicit diagnostic reconstruction is a finish-only fallback')
 if subprocess.check_output(['git','branch','--show-current']).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
 parent=json.loads((BASE/'receipt.json').read_text())
 if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('RC1 archive changed')
 state=json.loads((WORK/'live-before.json').read_text())
 if b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=state:raise ValueError('Live inputs changed')
 runner=a.runner.resolve();b.font.private_path(runner)
 if not a.finish:
  if (out.exists() and not a.resume) or deploy.exists():raise ValueError('Fresh private destinations required')
  out.mkdir(exist_ok=a.resume);b.write_json(out/'live-before.json',state);script=script_evidence(out);files={};contracts={};edits={}
  for key,h in parent['resource_hashes'].items():
   source=(WORK/'inputs'/key).read_bytes()
   if b.audit.sha(source)!=h:raise ValueError('Installed RC1 source mismatch')
   stem=Path(key).stem;data=source;transforms={}
   if a.resume and (out/'prepared-inputs'/key).exists():
    data=(out/'prepared-inputs'/key).read_bytes();files[key]=data
    if data!=source:
     old,new=b.audit.swf_tags(source)[2],b.audit.swf_tags(data)[2]
     if [(c,p) for c,p in old if c!=82]!=[(c,p) for c,p in new if c!=82]:raise ValueError('Resumed art changed')
     contracts[key]=b.class_contracts(WORK/'exports'/stem/'scripts',out/'reexport'/stem/'scripts')
     contracts[key].update(input_sha256=h,output_sha256=b.audit.sha(data),non_abc_definitions_exact=True)
     edits[key]=dict(resumed_source_files=[str(p.relative_to(out)) for p in (out/'abc'/stem).glob('*.as')])
    print('Trace checkpoint verified',stem,flush=True);continue
   if a.resume:
    for folder in ('abc','reexport'):
     p=out/folder/stem
     if p.exists():p.rename(p.with_name(stem+'.attempt1'))

   if stem in ('hud','hud_radialmenu','hud_iteminfo'):
    transforms['InputFeedbackButton']=lambda t,stem=stem:i.prompt(t,'InputFeedbackButton',stem)
    if list((WORK/'exports'/stem).rglob('ModuleInputFeedback.as')):transforms['ModuleInputFeedback']=lambda t,stem=stem:i.prompt(t,'ModuleInputFeedback',stem)
    if stem=='hud':
     transforms['HintButton']=lambda t:i.prompt(t,'HintButton','hud')
     transforms['Hud']=i.root
    else:
     name='HudModuleRadialMenu' if stem=='hud_radialmenu' else 'HudModuleItemInfo'
     transforms[name]=lambda t,name=name,stem=stem:i.component(t,name,stem)
    data,edits[key]=m.r.compile_classes(source,WORK/'exports'/stem,out/'abc'/stem,transforms)
    e=out/'reexport'/stem;e.mkdir(parents=True);g=e/'final.gfx';g.write_bytes(m.r.p.movie(data)[1]);b.export(g,e)
    # Existing function declarations and callbacks retained; extra observers
    # are intentionally listed, not claimed to be byte-identical listener sets.
    before=WORK/'exports'/stem/'scripts';after=e/'scripts'
    contract=b.class_contracts(before,after)
    old,new=b.audit.swf_tags(source)[2],b.audit.swf_tags(data)[2]
    if b.contracts.symbols(old)!=b.contracts.symbols(new):raise ValueError('Symbols changed')
    if [(c,p) for c,p in old if c!=82]!=[(c,p) for c,p in new if c!=82]:raise ValueError('Artwork/fonts/sprites/placements changed')
    if [c['tail'] for c in b.font.native.chunks(source)[1:]]!=[c['tail'] for c in b.font.native.chunks(data)[1:]]:raise ValueError('Texture data changed')
    original=b.public_chain(before,'Hud' if stem=='hud' else name);modified=b.public_chain(after,'Hud' if stem=='hud' else name)
    if any(modified.get(k)!=v for k,v in original.items()):raise ValueError('Original public export signature changed')
    m.v.atlas_contract(data);contract.update(non_abc_definitions_exact=True,all_texture_tails_exact=True,original_public_signatures=original,input_sha256=h,output_sha256=b.audit.sha(data));contracts[key]=contract
    proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-swf2xml',str(g),str(e/'final.xml')],capture_output=True,timeout=90)
    if proc.returncode:raise ValueError('Independent XML parse failed')
   files[key]=data;p=out/'prepared-inputs'/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);print('Trace prepared',stem,flush=True)
  b.write_json(out/'prepared.json',dict(movie_contracts=contracts,source_edits=edits,script_regression=script,unchanged_keys=[k for k,d in files.items() if b.audit.sha(d)==parent['resource_hashes'][k]]))
  commands=[];native={k:d for k,d in files.items() if k.endswith('.redswf')}
  with b.mount(runner,out,native) as workspace:
   official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
   log=official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
   if 'Found 22 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Native validation failed')
  for k,d in native.items():
   if (out/'cooked'/k).read_bytes()!=d:raise ValueError('Cooked candidate changed')
   p=out/'native-pack-input'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
  with b.mount(runner,out,{}) as workspace:
   official(runner,out,'pack',['pack','-dir='+str(out/'native-pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
   try:official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
   except (ValueError,subprocess.TimeoutExpired):pass
  b.write_json(out/'commands.json',commands);return
 files={k:(out/'prepared-inputs'/k).read_bytes() for k in parent['resource_hashes']};commands=[] if a.diagnostic_reconstruction else json.loads((out/'commands.json').read_text());native_meta=any(c['label']=='metadata' and c['exit_code']==0 for c in commands)
 if not native_meta:
  cmd=[sys.executable,str(ROOT/'tools/relocate-hud-metadata.py'),'--out',str(out)];p=subprocess.run(cmd,capture_output=True,timeout=60);(out/'metadata-relocation.log').write_bytes(p.stdout+p.stderr)
  if p.returncode:raise ValueError('Guarded metadata relocation failed')
  commands.append(dict(label='metadata',command=cmd,exit_code=0,assertions=[],method='Native-control verified fallback; native command did not pass'))
 manifest=json.loads((out/'prepared.json').read_text());manifest.update(version='QFR Radial Opening Trace D1',diagnostic=True,root_cause_confirmed=False,native_metadata_passed=native_meta,official_cook_validated=not a.diagnostic_reconstruction,parent_zip_sha256=parent['zip_sha256'],owners=json.loads((WORK/'owners.json').read_text()),runtime_tested=False)
 if not native_meta:manifest['metadata_relocation']=json.loads((out/'metadata-relocation.json').read_text())
 # Copy the accepted support into a private assembly, adding one original
 # annotation source. Never alter an accepted support cache or live mod.
 if a.diagnostic_reconstruction:
  reconstructed_package(out,deploy,parent,files,manifest)
  manifest['native_control_commands']=json.loads((ROOT/'build/ink-radial-trace-d1-final/commands.json').read_text())
  manifest['native_control_scope']='Initial instrumented revision only; guarded final candidate cook/validate/pack did not complete'
 else:
  support=out/'support';shutil.copytree(ROOT/'build/ink-hud-refinement-v2-release-final/support',support)
  shutil.copy2(ROOT/'src/hud/inkRadialDiagnostic.ws',support/'scripts/local/inkRadialDiagnostic.ws')
  original_select=b.selected_scripts
  b.selected_scripts=lambda selected:original_select(selected)+['inkRadialDiagnostic']
  b.MOD='modInkIronHUDRefinementV4';b.HUD=support
  b.package(out,deploy,set(parent['selected']),files,manifest,runner,commands,verified_native_reuse=True)
 # Existing WS, menu XML and all other support members stay exact. Only the
 # bundle/metadata and the diagnostic WS are allowed package changes.
 old=parent['package_members'];new=manifest['package_members']
 for k,h in old.items():
  if k.endswith(('blob0.bundle','metadata.store')) and '/modInkIronHUDRefinementV4/' in k:continue
  if new.get(k)!=h:raise ValueError('Existing package support changed')
 added=set(new)-set(old)
 if added!={'Mods/modInkIronHUDRefinementV4/content/scripts/local/inkRadialDiagnostic.ws'}:raise ValueError('Unexpected new package file')
 if b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=state:raise ValueError('Live inputs changed')
 archive=deploy/'Ink-Iron-HUD-Radial-Trace-D1-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(archive);manifest['zip_path']=str(archive)
 manifest['original_source_hashes']={str(p.relative_to(ROOT)):b.fallback.sha(p) for p in (ROOT/'src/hud/inkRadialDiagnostic.ws',Path(__file__),ROOT/'tools/instrument-radial-movies.py',ROOT/'tools/compile-radial-trace.py',ROOT/'tools/reconstruct-radial-trace-bundle.py')}
 b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest);print('Trace D1 ready',archive,manifest['zip_sha256'])
if __name__=='__main__':main()
