"""Compile copied current scripts and proposed overlays with official wcc; never deploy."""
import argparse,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'release/witcher-compatibility'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p):
 b=p.read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);ap.add_argument('--project',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--scope',choices=['full','full-unified','full-split','full-context','timing'],default='full');args=ap.parse_args()
 game=args.game.resolve();project=args.project.resolve();runtime=args.runtime.resolve()
 assert list(project.glob('*.w3edit')),'Project definition missing'
 work=project/'compatibility-validation'/args.scope;assert game not in work.parents
 base=work/'base';patch=work/'patch';result=work/'output';result.mkdir(parents=True,exist_ok=True)
 assert not base.exists() and not patch.exists(),'Use a fresh isolated scope directory or archive the previous run'
 sources=[]
 for p in (game/'content/content0/scripts').rglob('*.ws'):
  q=base/p.relative_to(game/'content/content0/scripts');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
  sources.append(dict(path=str(p),sha256=sha(p),role='vanilla'))
 plan=json.loads((OUT/'load-order.json').read_text(encoding='utf-8'));origins={}
 for name,row in plan.items():
  if not row['enabled']:continue
  staged=[p/'Mods'/name for p in (OUT/'payloads').iterdir() if (p/'Mods'/name).is_dir()]
  assert len(staged)<=1,name
  folder=staged[0] if staged else game/'Mods'/name
  if folder.is_dir():origins[name]=folder
 if args.scope=='timing':origins={k:v for k,v in origins.items() if k in ['modBestGsSchoolStances','modCombatSpeed','modResponsiveMovement']}
 winners={};opaque=[];annotations=[]
 for name,folder in sorted(origins.items(),key=lambda item:plan[item[0]]['priority']):
  info=folder/'content/info.json'
  if info.exists() and json.loads(info.read_text(encoding='utf-8-sig')).get('useLooseScripts') is False:
   opaque.append(dict(mod=name,source_files=len(list(folder.rglob('*.ws'))),blob_sha256=sha(folder/'content/precompiled.rsblob') if (folder/'content/precompiled.rsblob').exists() else None))
  for p in (folder/'content/scripts').rglob('*.ws'):
   rel=p.relative_to(folder/'content/scripts');key=rel.as_posix().lower()
   if (game/'content/content0/scripts'/rel).exists():
    if key in winners:continue
    winners[key]=name;q=base/rel
   else:q=patch/name/rel;annotations.append(dict(mod=name,relative=rel.as_posix()))
   q.parent.mkdir(parents=True,exist_ok=True);q.write_text(decode(p),encoding='utf-8',newline='\n')
   sources.append(dict(path=str(p),sha256=sha(p),role='override' if key in winners and winners[key]==name else 'overlay'))
 overlay_count=len(list(patch.rglob('*.ws')));assert overlay_count,'No annotation overlay'
 if args.scope in ['full-unified','full-split']:
  # Whole-file overrides reference newly added structs/classes. Compile these
  # in the same definitions update, not a baseline pass followed by a patch.
  for p in list(patch.rglob('*.ws')):
   if args.scope=='full-split' and 'mod_GwentDeckChoice' in p.parts:continue
   q=base/'__overlays'/p.relative_to(patch);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
   if args.scope=='full-split':p.unlink()
 if args.scope=='full-context':
  # Forward types referenced by whole-file overrides must exist in the base.
  # Keep every annotated source in official patch context.
  for p in list(patch.rglob('*.ws')):
   if '@' in p.read_text(encoding='utf-8'):
    # Lift complete top-level type definitions unchanged for forward references.
    import importlib.util
    spec=importlib.util.spec_from_file_location('build',ROOT/'tools/build-release.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    text=p.read_text(encoding='utf-8');clean=helper.masked(text);spans=[]
    for m in re.finditer(r'\b(?:(?:abstract|final|native)\s+)*(?:struct|enum|class)\s+\w+(?:\s+extends\s+\w+)?\s*\{',clean):
     start=clean.index('{',m.start());end=start+1;depth=1
     while depth:
      if clean[end]=='{':depth+=1
      elif clean[end]=='}':depth-=1
      end+=1
     spans.append((m.start(),end))
    if spans:
     q=base/'__value_types'/p.relative_to(patch);q.parent.mkdir(parents=True,exist_ok=True);q.write_text('\n'.join(text[a:b] for a,b in spans),encoding='utf-8')
     for a,b in reversed(spans):text=text[:a]+text[b:]
     p.write_text(text,encoding='utf-8')
    continue
   q=base/'__dependencies'/p.relative_to(patch);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);p.unlink()
 command=[str(runtime/'wcc_lite.exe'),'compilescripts',str(base)]+([] if args.scope=='full-unified' else ['-patch='+str(patch)])+['-out='+str(result)]
 try:
  proc=subprocess.run(command,cwd=runtime,capture_output=True,timeout=55);log=proc.stdout+proc.stderr;exit_code=proc.returncode
 except subprocess.TimeoutExpired as e:log=(e.stdout or b'')+(e.stderr or b'');exit_code=None
 (work/'compiler.log').write_bytes(log);message=log.decode(errors='replace');blob=result/'blob.rsblob'
 passed=exit_code==0 and (('Success! Scripts cooked' in message and any(p.stat().st_size>0 for p in result.glob('*.redscripts'))) if args.scope=='full-unified' else ('Success! Patch scripts blob saved' in message and blob.is_file() and blob.stat().st_size>0))
 diagnostics=dict(warnings=message.count('[Warning]'),assertions=message.count('[Error][Assert]'),script_errors=[line for line in message.splitlines() if '[Error][WCC]' in line]);
 receipt=dict(diagnostics=diagnostics,scope=args.scope,exit_code=exit_code,compile_pass=passed,compiler_sha256=sha(runtime/'wcc_lite.exe'),base_files=len(list(base.rglob('*.ws'))),overlay_files=overlay_count,whole_file_winners=winners,compiled_mods_without_full_source=opaque,sources=sources,outputs=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in result.iterdir() if p.is_file()],runtime_test=False,actual_deployment=False)
 (work/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
 summary={k:receipt[k] for k in ['scope','exit_code','compile_pass','base_files','overlay_files','compiled_mods_without_full_source']}
 (ROOT/'evidence'/('compiler-'+args.scope+'.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(summary));print(message[-2400:])
if __name__=='__main__':main()
