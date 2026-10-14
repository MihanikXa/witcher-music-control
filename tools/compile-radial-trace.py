"""Compile diagnostic annotations against pinned current source assembly controls."""
import argparse,json,subprocess,shutil,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();m.b.font.private_path(out)
 if out.exists():raise ValueError('Fresh private compiler output required')
 parent=ROOT/'build/ink-hud-v3-final/scripts';receipt=json.loads((parent/'receipt.json').read_text())
 for entry in receipt['assembly_inputs']+receipt['current_required_inputs']:
  if m.b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Pinned current source input changed')
 out.mkdir()
 for group in ('base','patch'):shutil.copytree(parent/group,out/group)
 runtime=ROOT/'build/native-npc-reproduce/runtime'
 if m.b.fallback.sha(runtime/'wcc_lite.exe')!=m.b.font.COMPILER_SHA:raise ValueError('Compiler binary changed')
 results=[]
 for label in ('control','candidate'):
  text=m.b.fallback.text(ROOT/'src/hud/inkRadialDiagnostic.ws')
  if label=='control':text=text.replace('report.InvokeSelfOneArg(FlashArgString(message));','report.InvokeSelfOneArg(FlashArgString("declaration-control"));')
  p=out/'patch/local/inkRadialDiagnostic.ws';p.write_text(text,encoding='utf-8')
  destination=out/label;destination.mkdir();cmd=[str(runtime/'wcc_lite.exe'),'compilescripts',str(out/'base'),'-patch='+str(out/'patch'),'-out='+str(destination)]
  process=subprocess.run(cmd,cwd=runtime,capture_output=True,timeout=150);(out/(label+'.stdout.log')).write_bytes(process.stdout+process.stderr);shutil.copy2(runtime.parent/'wcc.log',out/(label+'.full.log'))
  log=(out/(label+'.full.log')).read_text(errors='replace');blob=destination/'blob.rsblob'
  if process.returncode or '[Error][Script]' in log or '[Error][WCC]' in log or not blob.exists() or 'Success! Patch scripts blob saved' not in log:raise ValueError('Compilation failed '+label)
  results.append(dict(label=label,command=cmd,exit_code=process.returncode,blob_sha256=m.b.fallback.sha(blob),warnings=dict(m.b.bars.diagnostics.diagnostic_counter(log,'[Warning]')),assertions=dict(m.b.bars.diagnostics.diagnostic_counter(log,'[Error][Assert]'))))
  print('Diagnostic script',label,'passed',flush=True)
 if results[0]['warnings']!=results[1]['warnings'] or results[0]['assertions']!=results[1]['assertions']:raise ValueError('Matched API control diagnostics differ')
 m.b.write_json(out/'receipt.json',dict(results=results,control='same declarations/native API calls; constant trace payload',source_sha256=m.b.fallback.sha(ROOT/'src/hud/inkRadialDiagnostic.ws'),current_required_inputs=receipt['current_required_inputs'],assembly_inputs=receipt['assembly_inputs'],opaque_mods_not_recompiled=receipt.get('opaque_mods_not_recompiled',[])))
if __name__=='__main__':main()
