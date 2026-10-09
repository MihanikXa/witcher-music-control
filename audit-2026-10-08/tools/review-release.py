"""Regression checks for the release review; static checks are not compilation."""
import argparse,difflib,hashlib,json,re,sys
from pathlib import Path
from importlib.machinery import SourceFileLoader
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'release/witcher-compatibility'
sys.path.insert(0,str(Path(__file__).parent))
build=SourceFileLoader('review_build',str(Path(__file__).with_name('build-release.py'))).load_module()
refresh=SourceFileLoader('review_refresh',str(Path(__file__).with_name('refresh-merges.py'))).load_module()
def norm(t):return re.sub(r'\s+','',build.masked(t))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);game=ap.parse_args().game.resolve();checks={}
 # Independent native edits on both sides of a mod edit share one diff hunk.
 a='old native\nanchor1\n// modFriendlyHUD\ncustom\nanchor2\nold tail\n'
 b='new native\nanchor1\n// modFriendlyHUD\nstandard\nanchor2\nnew tail\n'
 policy=dict(source_sha256=hashlib.sha256(a.encode()).hexdigest(),vanilla_sha256=hashlib.sha256(b.encode()).hexdigest(),retain_opcodes=[2])
 actual,ledger=refresh.native_hunks(a,b,policy)
 assert actual=='new native\nanchor1\n// modFriendlyHUD\ncustom\nanchor2\nnew tail\n'
 try:refresh.native_hunks(a,b+'unreviewed\n',policy)
 except AssertionError:pass
 else:raise AssertionError('New vanilla must require review')
 checks['mixed_hunk_and_unreviewed_input_regressions']=True
 core=OUT/'payloads/core/Mods';original=(game/'Mods/modBestGsSchoolStances/content/scripts/local/BestGsStanceState.ws').read_text(encoding='utf-8-sig');staged=(core/'modBestGsSchoolStances/content/scripts/local/BestGsStanceState.ws').read_text(encoding='utf-8-sig')
 attack=build.body(original,'OnCombatActionStart')
 expected=''.join(x for x in attack.splitlines(True) if 'SetAnimationSpeedMultiplier(' not in x and "AddTimer('BG2_AttackFallback'" not in x)
 assert norm(build.body(staged,'OnCombatActionStart'))==norm(expected)
 evade=build.body(original,'SetIsCurrentlyDodging');start=evade.index('factor = 1.f;');end=evade.index('bg2_evadeSpeedId = SetAnimationSpeedMultiplier')
 expected=evade[:start]+evade[end:];expected=expected.replace('    var factor : float;\n','')
 expected=''.join(x for x in expected.splitlines(True) if 'SetAnimationSpeedMultiplier(' not in x and "AddTimer('BG2_EvadeFallback'" not in x)
 assert norm(build.body(staged,'SetIsCurrentlyDodging'))==norm(expected)
 for name,field in [('BG2_ResetAttackSpeed','bg2_attackSpeedId'),('BG2_ResetEvadeSpeed','bg2_evadeSpeedId')]:
  expected=build.body(original,name).replace('    if(bg2_speedInitialized && '+field+' != -1)\n        ResetAnimationSpeedMultiplier('+field+');\n','')
  assert norm(build.body(staged,name))==norm(expected)
 assert 'AnimationSpeedMultiplier(' not in build.masked(staged)
 checks['bestg_original_branches_wrapper_order_and_bookkeeping_preserved']=True
 hooks=(core/'modCombatSpeed/content/scripts/local/combat_speed/CSMPlayerHooks.ws').read_text();evade=build.body(hooks,'SetIsCurrentlyDodging')
 assert evade.index('wasDodging = IsCurrentlyDodging();')<evade.index('super.SetIsCurrentlyDodging')<evade.index('ResetCombatSpeedForFinisher();')<evade.index('combatSpeed.RollSpeed(')
 assert 'if(enable && !wasDodging)' in evade
 animation=(core/'modCombatSpeed/content/scripts/local/combat_speed/CSMAnimation.ws').read_text()
 assert len(re.findall(r'CSM_EndExplorationTiming\(\);\s*\w+ = thePlayer.SetAnimationSpeedMultiplier',animation))==6
 assert 'public final function CSM_EndExplorationTiming' in animation
 checks['accepted_evade_and_prewrite_exploration_cleanup']=True
 calc=(core/'modCombatSpeed/content/scripts/local/combat_speed/CSMCalculation.ws').read_text()
 assert calc.count('if(p.GetWeaponHolster().IsMeleeWeaponReady())')==2
 rm=core/'modResponsiveMovement/content/scripts/local/responsiveMovement.ws';old=(game/'Mods/modResponsiveMovement/content/scripts/local/responsiveMovement.ws').read_text(encoding='utf-8-sig')
 assert norm(build.body(rm.read_text(),'ResponsiveMovementSetTransitionAnimation')).endswith(norm(build.body(old,'ResponsiveMovementSetTransitionAnimation')))
 assert norm(build.body(rm.read_text(),'ResponsiveMovementEndTransitionAnimation'))==norm(build.body(old,'ResponsiveMovementEndTransitionAnimation'))
 checks['melee_guard_and_rm_owned_reset_preserved']=True
 reviewed=[]
 for row in json.loads((ROOT/'evidence/steam-update-overrides.json').read_text()):
  if row['source_mod']=='modBetterTorchesNextGen':continue
  a=(game/'Mods'/row['source_mod']/row['resource']).read_text(encoding='utf-8-sig');b=(game/'content/content0'/row['resource'].removeprefix('content/')).read_text(encoding='utf-8-sig')
  generated,ledger=refresh.native_hunks(a,b,refresh.POLICY[Path(row['resource']).name])
  p=OUT/'payloads/merged/Mods/mod0000_MergedFiles'/row['resource']
  assert generated==p.read_text(encoding='utf-8-sig')
  reviewed.append(dict(resource=row['resource'],retained=sum(x['decision']=='retain_mod' for x in ledger),native=sum(x['decision']=='apply_native' for x in ledger)))
 checks['native_change_block_review']=reviewed
 manifest=json.loads((OUT/'validation.json').read_text());checks['archive_payload_count']=sum(len(x['files']) for x in manifest['archives'])
 assert checks['archive_payload_count']==171 and len(manifest['archives'])==5
 checks['compilation']= 'See compiler-review receipts; this script performs no compilation'
 (OUT/'review-validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(json.dumps(checks))
if __name__=='__main__':main()
