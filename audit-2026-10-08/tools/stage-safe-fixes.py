# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Build private review packages; no live installation or Vortex state writes."""
from inventory import *
import shutil,sys,difflib
sys.dont_write_bytecode=True
def main():
 dest=ROOT/'patches';dest.mkdir(exist_ok=True)
 f=json.loads((ROOT/'evidence/installed-files.json').read_text())
 # Preserve the already verified merges; these are references, not new fixes.
 for x in f:
  if x['mod']=='mod0000_MergedFiles':
   p=dest/'verified-existing-merges/Mods'/x['mod']/x['relative'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(x['path'],p)
 # Correct the install archive topology, without copying Vortex markers.
 source=GAME/'ArrowParryManual/Mods/modArrowParryManual'
 for p in source.rglob('*'):
  if p.is_file() and '__folder_managed_by_vortex' not in p.name:
   q=dest/'arrow-deflection-layout/Mods/modArrowParryManual'/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
 xml=GAME/'bin/config/r4game/user_config_matrix/pc/modArrowParryManual.xml'
 q=dest/'arrow-deflection-layout'/xml.relative_to(GAME);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(xml,q)
 # Use the installed author's documented reader/writer, previously inspected.
 sys.path.insert(0,str(GAME/'Mods/modSeamlessAdaptiveHUD/translations'));import w3s
 src=GAME/'Mods/modunreasonableplotredesigned/content/en.w3strings';r=w3s.read(src,0x79321793);sid=1063514;old=r['strings'][sid]
 new=old.replace('I have born it until now, I can bear it no longer.','I have borne it until now, but I can bear it no longer.').replace('Do you  know','Do you know').replace('as a I write','as I write')
 assert old!=new and 'My head hangs low' in new
 target=dest/'localization/Mods/mod0000_AuditCompat/content/en.w3strings';target.parent.mkdir(parents=True,exist_ok=True)
 w3s.write(target,0x79321793,r['key1'],r['key2'],[(sid,None,new)],lambda x:0)
 check=w3s.read(target,0x79321793);assert check['strings']=={sid:new} and not check['keys']
 (dest/'localization/letter-before-after.md').write_text('# Blood Ties letter: ID 1063514\n\nBefore: UPR expanded letter is hidden by Grammar of the Path.\n\nProposed text:\n\n'+new.replace('<br>','\n')+'\n',encoding='utf-8')
 save('localization-patch-validation.json',dict(id=sid,source=str(src),source_sha256=sha(src),patch=str(target),patch_sha256=sha(target),roundtrip=True,retained_expansion='My head hangs low' in new,corrections=['born -> borne','add but to join clauses','remove double space','as a I write -> as I write'],compiler_or_runtime_test=False))
 # Conditional priority proposal: do not deploy until resource-policy review.
 ini=configparser.ConfigParser();ini.optionxform=str;ini.read(DOC/'mods.settings')
 names=sorted(ini.sections(),key=lambda n:int(ini[n]['Priority']))
 names.remove('modunreasonableplotredesigned');names.insert(names.index('modbrothersinarms'),'modunreasonableplotredesigned')
 names.insert(1,'mod0000_AuditCompat');names.append('modGeraltOutfitWheel')
 text='; REVIEW CANDIDATE ONLY: UPR/BIA resource preservation is not independently certified.\n'
 for priority,name in enumerate(names,1):
  old=ini[name] if ini.has_section(name) else {};text+=f'[{name}]\nEnabled={old.get("Enabled","1")}\nPriority={priority}\nVK={old.get("VK",name)}\n'
 order=dest/'load-order';order.mkdir(exist_ok=True);(order/'mods.settings.proposed').write_text(text,encoding='utf-8',newline='\r\n')
 old=(DOC/'mods.settings').read_text();(order/'mods.settings.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='live mods.settings',tofile='review candidate')),encoding='utf-8')
 # Capture small live control files as independent copies for future guarded rollback.
 backup=ROOT/'private/control-snapshot';backup.mkdir(exist_ok=True)
 controls=[DOC/'mods.settings',DOC/'input.settings',DOC/'dx12user.settings',GAME/'WitcherScriptMerger/MergeInventory.xml']
 snapshots=[]
 for i,p in enumerate(controls):
  q=backup/(str(i)+'-'+p.name);shutil.copyfile(p,q);snapshots.append(dict(live=str(p),snapshot=str(q),sha256=sha(q),mtime_ns=p.stat().st_mtime_ns))
 save('control-snapshot.json',snapshots)
 payload=[]
 for p in dest.rglob('*'):
  if p.is_file():payload.append(dict(path=str(p),relative=str(p.relative_to(dest)),size=p.stat().st_size,sha256=sha(p)))
 save('patch-manifest.json',payload)
 print('Review package files:',len(payload),'localization roundtrip passed')
if __name__=='__main__':main()
