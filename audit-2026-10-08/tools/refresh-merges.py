"""Reconstruct prior vanilla text from preserved diffs; stage Steam updates."""
import argparse,difflib,hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from inventory import ROOT,sha
from native_change_policy import POLICY
def reverse_diff(new,diff):
 lines=new.splitlines(True);patch=diff.splitlines(True);out=[];cursor=0;i=2
 while i<len(patch):
  m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',patch[i]);assert m,patch[i]
  start=int(m[3])-1;out.extend(lines[cursor:start]);cursor=start;i+=1
  while i<len(patch) and not patch[i].startswith('@@'):
   line=patch[i];i+=1
   if line.startswith((' ','+')):assert lines[cursor]==line[1:];cursor+=1
   if line.startswith((' ','-')):out.append(line[1:])
 out.extend(lines[cursor:]);return ''.join(out)
def native_hunks(source,vanilla,policy):
 # No marker heuristic: source and vanilla must match the reviewed text pair.
 # Change blocks have no surrounding context, so unrelated adjacent native
 # changes cannot be skipped merely because they share a unified-diff hunk.
 assert hashlib.sha256(source.encode()).hexdigest()==policy['source_sha256'],'Unreviewed mod text'
 assert hashlib.sha256(vanilla.encode()).hexdigest()==policy['vanilla_sha256'],'Unreviewed vanilla text'
 a=source.splitlines(True);b=vanilla.splitlines(True);out=[];ledger=[]
 ops=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
 retain=set(policy['retain_opcodes']);seen=set()
 for index,(tag,i1,i2,j1,j2) in enumerate(ops):
  if tag=='equal':
   assert index not in retain
   out.extend(a[i1:i2]);continue
  keep=index in retain
  if keep:seen.add(index)
  out.extend(a[i1:i2] if keep else b[j1:j2])
  ledger.append(dict(opcode=index,source_lines=[i1+1,i2],vanilla_lines=[j1+1,j2],decision='retain_mod' if keep else 'apply_native'))
 assert seen==retain,'Review indices do not match change blocks'
 return ''.join(out),ledger
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);a=ap.parse_args();game=a.game.resolve()
 rows=json.loads((ROOT/'evidence/merge-source-check.json').read_text());unique={x['resource']:x for x in rows};out=ROOT/'private/steam-update-merges';out.mkdir(exist_ok=True)
 results=[]
 for resource,x in unique.items():
  baseline=game/'content/content0'/resource.removeprefix('content/');new=baseline.read_text(encoding='utf-8-sig')
  installed=game/'Mods/mod0000_MergedFiles'/resource;assert sha(installed)==x['current_sha256'];current=installed.read_text(encoding='utf-8-sig')
  old=reverse_diff(current,(ROOT/'private/diffs'/(Path(resource).stem+'-mod0000_MergedFiles.diff')).read_text(encoding='utf-8'))
  raw=[old.encode(),old.replace('\n','\r\n').encode()];raw+=[b'\xef\xbb\xbf'+b for b in raw]
  raw_hash_verified=any(hashlib.sha256(b).hexdigest()==x['baseline_sha256'] for b in raw)
  # Unified diffs preserve normalized text, not mixed original line endings.
  # The installed merge is hash-pinned; every reversed context/addition matches.
  oldfile=out/(Path(resource).stem+'-old.ws');newfile=out/(Path(resource).stem+'-new.ws');mergefile=out/(Path(resource).stem+'-merged.ws')
  for p,t in [(oldfile,old),(newfile,new),(mergefile,current)]:p.write_text(t,encoding='utf-8',newline='\n')
  proc=subprocess.run(['git','merge-file','-p',str(mergefile),str(oldfile),str(newfile)],capture_output=True);assert proc.returncode==0,(resource,proc.returncode)
  proposed=proc.stdout.decode();target=out/'payload/Mods/mod0000_MergedFiles'/resource;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(proposed,encoding='utf-8',newline='\r\n')
  proposedfile=out/'proposed.ws';proposedfile.write_text(proposed,encoding='utf-8',newline='\n')
  reverse=subprocess.run(['git','merge-file','-p',str(proposedfile),str(newfile),str(oldfile)],capture_output=True)
  assert reverse.returncode==0 and reverse.stdout.decode()==current,'Steam update inverse must restore exact normalized installed merge'
  contribution_checks=[]
  for source in [z for z in rows if z['resource']==resource]:
   sourcefile=game/'Mods'/source['mod']/resource;assert sha(sourcefile)==source['source_sha256']
   assert source['already_incorporated'];contribution_checks.append(source['mod'])
  (out/(Path(resource).stem+'-vanilla-update.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True))),encoding='utf-8')
  (out/(Path(resource).stem+'-merge-update.diff')).write_text(''.join(difflib.unified_diff(current.splitlines(True),proposed.splitlines(True))),encoding='utf-8')
  results.append(dict(resource=resource,baseline_text_changed=old!=new,merged_text_changed=current!=proposed,current_vanilla_sha256=sha(baseline),output_sha256=sha(target),conflict_free=True,prior_raw_hash_verified=raw_hash_verified,contributions_preserved=contribution_checks))
 supplemental=[]
 selected=[('modBetterTorchesNextGen','scripts/game/explorations/exploration_movement_system/exploration_substates/explorationStateInteraction.ws'),('modFriendlyHUD','scripts/game/r4Game.ws'),('modFriendlyHUD','scripts/game/components/inventoryComponent.ws'),('modFriendlyHUD','scripts/game/gui/main_menu/ingameMenu.ws'),('modFriendlyHUD','scripts/game/gui/menus/mapMenu.ws'),('modFriendlyHUD','scripts/game/gui/hud/modules/hudModuleRadialMenu.ws'),('modGeraltOutfitWheel','scripts/game/gui/menus/commonMenu.ws')]
 pinned={x['path'].lower():x['sha256'] for x in json.loads((ROOT/'evidence/installed-files.json').read_text())}
 for mod,rel in selected:
  p=game/'Mods'/mod/'content'/rel;assert sha(p)==pinned[str(p).lower()]
  vanilla=game/'content/content0'/rel;current=p.read_text(encoding='utf-8-sig');new=vanilla.read_text(encoding='utf-8-sig')
  if mod=='modBetterTorchesNextGen':
   proposed=new
   for line in [x for x in current.splitlines() if '// modBetterTorchesNextGen' in x]:
    native=line.replace('// modBetterTorchesNextGen','').replace('//','',1).strip()
    assert native and proposed.count(native)==1,native
    proposed=proposed.replace(native,'//'+native+' // modBetterTorchesNextGen')
   hunks=0
  else:
   proposed,ledger=native_hunks(current,new,POLICY[Path(rel).name])
   hunks=sum(x['decision']=='apply_native' for x in ledger)
  target=out/'payload/Mods/mod0000_MergedFiles/content'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(proposed,encoding='utf-8',newline='\r\n')
  residual=''.join(difflib.unified_diff(new.splitlines(True),proposed.splitlines(True)))
  (out/(mod+'-'+Path(rel).stem+'-retained-mod.diff')).write_text(residual,encoding='utf-8')
  supplemental.append(dict(resource='content/'+rel,source_mod=mod,source_sha256=sha(p),current_vanilla_sha256=sha(vanilla),output_sha256=sha(target),native_change_blocks_applied=hunks,change_review=[] if mod=='modBetterTorchesNextGen' else ledger,residual_diff=str(out/(mod+'-'+Path(rel).stem+'-retained-mod.diff'))))
 (ROOT/'evidence/steam-update-merges.json').write_text(json.dumps(results,indent=2),encoding='utf-8');(ROOT/'evidence/steam-update-overrides.json').write_text(json.dumps(supplemental,indent=2),encoding='utf-8');print(json.dumps({'merges':results,'supplemental':supplemental}))
if __name__=='__main__':main()
