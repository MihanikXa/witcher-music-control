"""Menus v4 typography-only successor. Never writes deployed mod/settings files."""
import argparse,concurrent.futures,importlib.util,io,json,re,shutil,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
parent=load('build-menu-typography');b=parent.b;f=load('finish-menu-typography')
OUT=ROOT/'build/menus087-v4-final';DEPLOY=ROOT/'deploy/menus087-v4'
TARGETS={stem:{name:(f.crafting if name=='ItemCraftingModule' else (lambda s,n=name:f.finish(s,n))) for name in changes} for stem,changes in parent.TARGETS.items()}
TARGETS['panel_common']={'MenuCommon':f.common}

def retained_common():
 key='gameplay/gui_new/swf/common/panel_common.redswf'
 namespaces=['red.game.witcher3.menus.common_menu.TopBarNew','red.game.witcher3.menus.common_menu.ModuleInputFeedback','red.game.witcher3.controls.InputFeedbackButton']
 b.selected_export((OUT/'prepared-inputs'/key).read_bytes(),OUT/'common-retained-check',namespaces)
 for namespace in namespaces:
  name=namespace.split('.')[-1];old=b.patch.one_file(OUT/'movies/panel_common/before/scripts',name).read_text(encoding='utf-8-sig');new=b.patch.one_file(OUT/'common-retained-check/scripts',name).read_text(encoding='utf-8-sig')
  if old!=new:raise ValueError('Frozen common class changed '+name)

def process(row):
 key=row['resource'];stem=Path(key).stem;source=(parent.OUT/'prepared-inputs'/key).read_bytes();dest=OUT/'prepared-inputs'/key;dest.parent.mkdir(parents=True,exist_ok=True)
 if stem not in TARGETS:
  dest.write_bytes(source);return dict(resource=key,input_sha256=b.m.b.audit.sha(source),output_sha256=b.m.b.audit.sha(source),retained_v3_exact=True)
 folder=OUT/'movies'/stem;folder.mkdir(parents=True,exist_ok=True);before=folder/'before'
 cached=ROOT/'build/menus087-v4/movies'/stem/'before'
 if not before.exists() and (cached/'scripts').exists():
  if (cached/'source.gfx').read_bytes()!=b.m.r.p.movie(source)[1]:raise ValueError('Cached v3 export input changed')
  shutil.copytree(cached,before)
 if not (before/'scripts').exists():
  before.mkdir(exist_ok=True);gfx=before/'source.gfx';gfx.write_bytes(b.m.r.p.movie(source)[1]);b.m.b.export(gfx,before)
 transforms=TARGETS[stem];data,changes=b.batch_compile(source,before,folder/'abc',transforms);after=folder/'after'
 classes=[b.patch.one_file(before/'scripts',n).relative_to(before/'scripts').with_suffix('').as_posix().replace('/','.') for n in transforms]
 b.selected_export(data,after,classes)
 for n in transforms:
  old=b.patch.one_file(before/'scripts',n).read_text(encoding='utf-8-sig');new=b.patch.one_file(after/'scripts',n).read_text(encoding='utf-8-sig')
  for sig in re.findall(r'(?:public|protected) function [^\n]+',old):
   if sig not in new:raise ValueError('Native interface changed '+n+' '+sig)
  if re.findall(r'addEventListener\([^\n]+',old)!=re.findall(r'addEventListener\([^\n]+',new):raise ValueError('Listeners changed '+n)
 tags=b.m.b.audit.swf_tags(source)[2];newtags=b.m.b.audit.swf_tags(data)[2]
 if [(c,p) for c,p in tags if c!=82]!=[(c,p) for c,p in newtags if c!=82]:raise ValueError('Non-code SWF changes '+stem)
 if not all(c['crc_valid'] for c in b.m.b.font.native.chunks(data)):raise ValueError('Native CRC failure')
 dest.write_bytes(data);print('Prepared typography finishing',stem,flush=True)
 return dict(resource=key,input_sha256=b.m.b.audit.sha(source),output_sha256=b.m.b.audit.sha(data),classes=changes,non_code_tags_exact=True)

def prepare():
 OUT.mkdir(exist_ok=True)
 if not (OUT/'installed-v3-check.json').exists():
  subprocess.run([__import__('sys').executable,str(ROOT/'tools/verify-menu-visual-install.py'),'--release',str(parent.OUT/'receipt.json'),'--report',str(OUT/'installed-v3-check.json')],check=True)
 if not (OUT/'frozen.json').exists():b.m.b.write_json(OUT/'frozen.json',b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS))
 rows=json.loads((parent.OUT/'prepared.json').read_text())['resources']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(process,rows))
 b.m.b.write_json(OUT/'prepared.json',dict(keys=sorted(r['resource'] for r in results),resources=results,runtime_tested=False))
 retained_common()

def package():
 if DEPLOY.exists():raise ValueError('Fresh release directory required')
 prepared=json.loads((OUT/'prepared.json').read_text());command_path=OUT/'native-commands.json'
 if not command_path.exists():command_path=OUT/'native-final/native-commands.json'
 commands=json.loads(command_path.read_text());native_complete={r['label'] for r in commands if r['passed']}=={'cook','validate','pack','metadata'}
 reconstruction=None
 if not native_complete:
  reconstruction=json.loads((OUT/'reconstruction.json').read_text())
  if len(reconstruction['controls'])!=2 or not all(r['bundle_and_metadata_byte_identical'] for r in reconstruction['controls']) or not reconstruction['independent_changed_metadata_exact'] or not reconstruction['independent_changed_bundle_exact'] or not reconstruction['exact_extraction']:raise ValueError('Unverified reconstruction')
  if b.m.b.fallback.sha(OUT/'packed/blob0.bundle')!=reconstruction['bundle_sha256'] or b.m.b.fallback.sha(OUT/'packed/metadata.store')!=reconstruction['metadata_sha256']:raise ValueError('Reconstructed files changed')
 bundle=OUT/'packed/blob0.bundle';entries=list(b.m.b.audit.entries(bundle))
 if {r['resource'] for r in entries}!=set(prepared['keys']):raise ValueError('Unexpected packed keys')
 for r in entries:
  if b.m.b.bars.extract(bundle,r['resource'])!=(OUT/'prepared-inputs'/r['resource']).read_bytes():raise ValueError('Resource re-extraction failed')
 old=json.loads((parent.OUT/'receipt.json').read_text())
 with zipfile.ZipFile(old['zip_path']) as z:members={n:z.read(n) for n in z.namelist()}
 for name in ('blob0.bundle','metadata.store'):members['Mods/modInkIronMenus087/content/'+name]=(OUT/'packed'/name).read_bytes()
 def makezip():
  stream=io.BytesIO()
  with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
   for name,data in sorted(members.items()):
    info=zipfile.ZipInfo(name,(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
  return stream.getvalue()
 data=makezip()
 if data!=makezip():raise ValueError('ZIP not deterministic')
 if b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS)!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Live files/settings changed')
 DEPLOY.mkdir();path=DEPLOY/'Ink-Iron-0.8.7-Menus-v4-Typography-Finishing-private-test.zip';path.write_bytes(data)
 with zipfile.ZipFile(path) as z:
  if z.testzip():raise ValueError('ZIP CRC failed')
 b.m.b.write_json(OUT/'receipt.json',dict(zip_path=str(path),zip_sha256=b.m.b.audit.sha(data),bytes=len(data),parent_sha256=old['zip_sha256'],resources=prepared['resources'],native=commands,native_candidate_cook_validated=native_complete,native_metadata_reconstructed=not native_complete,reconstruction=reconstruction,members={k:b.m.b.audit.sha(v) for k,v in members.items()},live_unchanged=True,runtime_tested=False,scripts_options_art_unchanged=True))
 print(path,b.m.b.audit.sha(data),flush=True)

def report():
 r=json.loads((OUT/'receipt.json').read_text());log=(OUT/'tests.log').read_text(encoding='utf-8-sig');match=re.search(r'Ran (\d+) tests in ([\d.]+)s',log)
 if not match or not re.search(r'\bOK\s*$',log):raise ValueError('Successful test receipt required')
 r.update(release='Menus v4 — Typography Finishing',date='2026-10-17',tests=dict(count=int(match[1]),seconds=float(match[2]),passed=True,log_sha256=b.m.b.fallback.sha(OUT/'tests.log')),font_and_preview_evidence=json.loads((OUT/'font-model.json').read_text()),installed_parent_check=json.loads((OUT/'installed-v3-check.json').read_text()),modified_movies=9,modified_classes=13,retained_v3_movies_exact=31,native_logs={str(p.relative_to(OUT)):b.m.b.fallback.sha(p) for folder in ('native-final','native-startup-failed') for p in (OUT/folder).glob('*.log')},source_hashes={str(p.relative_to(ROOT)):b.m.b.fallback.sha(p) for p in [Path(__file__),ROOT/'tools/finish-menu-typography.py',ROOT/'tools/preview-menu-finishing.py',ROOT/'tools/reconstruct-menu-finishing.py',ROOT/'tests/test_menu_finishing.py']})
 r['native_resource_validation_outstanding']=not r['native_candidate_cook_validated']
 r['recorded_final_native_attempts']={folder:json.loads((OUT/folder/'native-commands.json').read_text()) for folder in ('native-startup-failed','native-final') if (OUT/folder/'native-commands.json').exists()}
 b.m.b.write_json(ROOT/'research/menus087-v4-typography-finishing-manifest.json',r)

def verify_native():
 work=OUT/'native-verification'
 if work.exists():raise ValueError('Fresh verification directory required; previous evidence retained')
 work.mkdir();shutil.copy2(OUT/'prepared.json',work/'prepared.json');shutil.copytree(OUT/'prepared-inputs',work/'prepared-inputs')
 b.OUT=work;b.native_build()
 for name in ('blob0.bundle','metadata.store'):
  if (work/'packed'/name).read_bytes()!=(OUT/'packed'/name).read_bytes():raise ValueError('Native control differs from reconstructed candidate '+name)
 b.m.b.write_json(work/'verification.json',dict(native_complete=True,bundle_and_metadata_match_release=True))

def main():
 if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Wrong branch')
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','native','package','report','verify-native'));a=ap.parse_args()
 if a.stage=='verify-native':verify_native();return
 if a.stage=='native':b.OUT=OUT;b.native_build()
 else:globals()[a.stage]()
if __name__=='__main__':main()
