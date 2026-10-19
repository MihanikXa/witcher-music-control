"""Compile Gear annotations against verified installed 5.01 merged/provider inputs."""
import argparse,importlib.util,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--source',type=Path,default=ROOT/'src/inventory/inkGearGrid.ws');ap.add_argument('--disabled-assignment',default='qfGearGridActive = on;');a=ap.parse_args();out=a.out.resolve();m.b.font.private_path(out)
 if out.exists():raise ValueError('Fresh compiler destination required')
 parent=ROOT/'build/ink-hud-v3-final/scripts';receipt=json.loads((parent/'receipt.json').read_text())
 for row in receipt['assembly_inputs']+receipt['current_required_inputs']:
  if m.b.fallback.sha(Path(row['path']))!=row['sha256']:raise ValueError('Verified assembly/provider changed '+row['path'])
 out.mkdir()
 for group in ('base','patch'):shutil.copytree(parent/group,out/group)
 # Actual effective merged Inventory source, not a vanilla replacement.
 live=m.v.GAME/'Mods/mod0000_MergedFiles/content/scripts/game/gui/menus/inventorymenu.ws'
 assembled=out/'base/game/gui/menus/inventoryMenu.ws'
 if m.b.fallback.text(live)!=m.b.fallback.text(assembled):raise ValueError('Current merged Inventory differs from assembly')
 hoods=m.v.GAME/'Mods/modHoods/content/scripts/local/customDyeing.ws'
 hashes={m.b.audit.sha(m.b.fallback.text(p).encode()) for group in ('base','patch') for p in (out/group).rglob('*.ws')}
 if m.b.audit.sha(m.b.fallback.text(hoods).encode()) not in hashes:raise ValueError('Actual Hoods dye annotations missing from assembly')
 runtime=ROOT/'build/native-npc-reproduce/runtime'
 if m.b.fallback.sha(runtime/'wcc_lite.exe')!=m.b.font.COMPILER_SHA:raise ValueError('Compiler changed')
 results=[];source=m.b.fallback.text(a.source.resolve());source_hash=m.b.fallback.sha(a.source.resolve())
 for label in ('api-control','candidate'):
  text=source if label=='candidate' else source.replace(a.disabled_assignment,a.disabled_assignment.replace('= on;','= false;'))
  target=out/'patch/local'/a.source.name;target.parent.mkdir(exist_ok=True);target.write_text(text,encoding='utf-8')
  dest=out/label;dest.mkdir();cmd=[str(runtime/'wcc_lite.exe'),'compilescripts',str(out/'base'),'-patch='+str(out/'patch'),'-out='+str(dest)]
  temporary=out/(label+'-temp');temporary.mkdir()
  try:p=subprocess.run(cmd,cwd=runtime,env=dict(os.environ,TEMP=str(temporary),TMP=str(temporary)),capture_output=True,timeout=150)
  except subprocess.TimeoutExpired as error:
   (out/(label+'.stdout.log')).write_bytes((error.stdout or b'')+(error.stderr or b''))
   if (runtime.parent/'wcc.log').exists():shutil.copy2(runtime.parent/'wcc.log',out/(label+'.full.log'))
   m.b.write_json(out/'failure.json',dict(label=label,timeout_seconds=150,source_sha256=source_hash,command=cmd))
   raise ValueError('Script compiler startup/execution timeout '+label) from error
  (out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr);shutil.copy2(runtime.parent/'wcc.log',out/(label+'.full.log'));log=(out/(label+'.full.log')).read_text(errors='replace');blob=dest/'blob.rsblob'
  if p.returncode or '[Error][Script]' in log or '[Error][WCC]' in log or 'Success! Patch scripts blob saved' not in log or not blob.exists():raise ValueError('Script compilation failed '+label)
  row=dict(label=label,exit_code=p.returncode,blob_sha256=m.b.fallback.sha(blob),warnings=dict(m.b.bars.diagnostics.diagnostic_counter(log,'[Warning]')),assertions=dict(m.b.bars.diagnostics.diagnostic_counter(log,'[Error][Assert]')));results.append(row);print('Gear script',label,'passed',flush=True)
 if results[0]['warnings']!=results[1]['warnings'] or results[0]['assertions']!=results[1]['assertions']:raise ValueError('Control diagnostics differ')
 if m.b.fallback.sha(a.source.resolve())!=source_hash:raise ValueError('Source edited during compilation')
 m.b.write_json(out/'receipt.json',dict(results=results,source_sha256=source_hash,merged_inventory_sha256=m.b.fallback.sha(live),hoods_dye_sha256=m.b.fallback.sha(hoods),control='same annotation/API declarations, disabled data-inclusion flag; not a runtime test',opaque_dependencies=receipt.get('opaque_mods_not_recompiled',[])))
if __name__=='__main__':main()
