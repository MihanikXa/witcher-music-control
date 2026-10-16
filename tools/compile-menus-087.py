"""Private exact-provider compilation plus additive existing-page menu options."""
import argparse,copy,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-menus-087.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b);m=b.m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--finish-existing',action='store_true');a=ap.parse_args()
 out=b.SCRIPTS
 if not a.finish_existing:out.mkdir()
 parent=ROOT/'build/ink-hud-v3-final/scripts';old=json.loads((parent/'receipt.json').read_text())
 for row in old['assembly_inputs']+old['current_required_inputs']:
  if m.b.fallback.sha(Path(row['path']))!=row['sha256']:raise ValueError('Current source changed '+row['path'])
 if not a.finish_existing:
  for group in ('base','patch'):shutil.copytree(parent/group,out/group)
 live=m.v.GAME/'Mods/mod0000_MergedFiles/content/scripts/game/gui/menus/inventorymenu.ws'
 if m.b.fallback.text(live)!=m.b.fallback.text(out/'base/game/gui/menus/inventoryMenu.ws'):raise ValueError('Wrong merged Inventory')
 if list((out/'patch').rglob('inkGearGrid.ws')):raise ValueError('Gear layout must be absent')
 vendor=out/'vendor';vendor.mkdir(exist_ok=a.finish_existing);results=[];runtime=ROOT/'build/native-npc-reproduce/runtime'
 if m.b.fallback.sha(runtime/'wcc_lite.exe')!=m.b.font.COMPILER_SHA:raise ValueError('Compiler pin')
 for label in ('control','candidate'):
  if label=='candidate':
   for p in (b.REF/'mods/modInkAndIronUI/content/scripts/local').glob('*.ws'):
    text=m.b.fallback.text(p);dest=vendor/p.name
    if a.finish_existing:
     if dest.read_text(encoding='utf-8')!=text or (out/'patch/local'/p.name).read_text(encoding='utf-8')!=text:raise ValueError('Compiled candidate source changed')
    else:dest.write_text(text,encoding='utf-8');shutil.copy2(dest,out/'patch/local'/p.name)
  dest=out/label;cmd=[str(runtime/'wcc_lite.exe'),'compilescripts',str(out/'base'),'-patch='+str(out/'patch'),'-out='+str(dest)]
  exit_code=0
  if not a.finish_existing:
   dest.mkdir();p=subprocess.run(cmd,cwd=runtime,capture_output=True,timeout=150);exit_code=p.returncode;(out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr);shutil.copy2(runtime.parent/'wcc.log',out/(label+'.full.log'))
  log=(out/(label+'.full.log')).read_text(errors='replace');blob=dest/'blob.rsblob'
  if exit_code or 'Success! Patch scripts blob saved' not in log or '[Error][Script]' in log or '[Error][WCC]' in log or not blob.exists():raise ValueError('Script compile failed '+label)
  results.append(dict(label=label,exit_code=exit_code,existing_successful_compile_verified=a.finish_existing,blob_sha256=m.b.fallback.sha(blob),warnings=dict(m.b.bars.diagnostics.diagnostic_counter(log,'[Warning]')),assertions=dict(m.b.bars.diagnostics.diagnostic_counter(log,'[Error][Assert]'))));print('Menu scripts',label,'passed',flush=True)
 if results[0]['warnings']!=results[1]['warnings'] or results[0]['assertions']!=results[1]['assertions']:raise ValueError('Diagnostic delta needs review')
 current=m.v.GAME/'bin/config/r4game/user_config_matrix/pc/modInkIronHUDBatch.xml';raw=current.read_bytes();root=ET.fromstring(raw);existing={n.get('id') for n in root.findall('.//Var')}
 upstream=ET.parse(b.REF/'bin/config/r4game/user_config_matrix/pc/modInkAndIron.xml').getroot();menu_names=set()
 for p in vendor.glob('*.ws'):menu_names.update(re.findall(r"GetVarValue\(\s*'InkAndIronOptions'\s*,\s*'(\w+)'",p.read_text()))
 additions=[n for n in upstream.findall('.//Var') if n.get('id') in menu_names and n.get('id') not in existing]
 text=raw.decode('utf-8-sig');marker='</VisibleVars>'
 if text.count(marker)!=1:raise ValueError('Settings page anchor changed')
 combined=text.replace(marker,'\n'+''.join(ET.tostring(n,encoding='unicode') for n in additions)+marker)
 options=out.parent/'options';options.mkdir(exist_ok=a.finish_existing);(options/current.name).write_text(combined,encoding='utf-8')
 check=ET.fromstring(combined)
 for n in root.findall('.//Var'):
  newer=next(x for x in check.findall('.//Var') if x.get('id')==n.get('id'))
  oldnode=copy.deepcopy(n);newnode=copy.deepcopy(newer);oldnode.tail=None;newnode.tail=None
  if ET.tostring(oldnode)!=ET.tostring(newnode):raise ValueError('Existing HUD option changed')
 m.b.write_json(out/'receipt.json',dict(results=results,source_hashes={p.name:m.b.fallback.sha(p) for p in vendor.glob('*.ws')},merged_inventory_sha256=m.b.fallback.sha(live),opaque_dependencies=old.get('opaque_mods_not_recompiled',[]),options_base_path=str(current),options_base_sha256=m.b.fallback.sha(current),added_options=[n.get('id') for n in additions],existing_hud_options_unchanged=True))
if __name__=='__main__':main()
