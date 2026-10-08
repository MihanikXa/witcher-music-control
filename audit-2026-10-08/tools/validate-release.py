"""Validate private release overlays and unchanged live inputs, without deployment."""
import argparse,collections,importlib.util,json,re,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from inventory import sha,bundles
from importlib.machinery import SourceFileLoader
build=SourceFileLoader('release_builder',str(Path(__file__).with_name('build-release.py'))).load_module()
settings=SourceFileLoader('settings_helper',str(Path(__file__).with_name('prepare-settings.py'))).load_module()
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'release/witcher-compatibility'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def text(p):
 b=p.read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig').replace('\r\n','\n').replace('\r','\n')
def values(t):
 result={};group=None
 for line in t.splitlines():
  m=re.match(r'\s*\[([^]]+)\]',line)
  if m:group=m[1]
  elif group and '=' in line and not line.lstrip().startswith((';','#')):
   key,value=line.split('=',1);result[(group,key.strip())]=value.strip()
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);a=ap.parse_args();game=a.game.resolve()
 checks={};original=read(ROOT/'evidence/installed-files.json')+read(ROOT/'evidence/other-game-files.json')
 unchanged=[x for x in original if Path(x['path']).is_file() and sha(Path(x['path']))==x['sha256']]
 drift=[x['path'] for x in original if x not in unchanged]
 assert not any(x.get('mod') for x in original if x['path'] in drift),'Installed mod changed'
 controls=read(ROOT/'evidence/control-snapshot.json')
 control_drift=[x['live'] for x in controls if sha(Path(x['live']))!=x['sha256']]
 assert all(Path(p).name=='mods.settings' for p in control_drift),control_drift
 import configparser
 order=configparser.ConfigParser();order.read(next(x['live'] for x in controls if Path(x['live']).name=='mods.settings'))
 old_order=read(ROOT/'evidence/mods-settings.json')
 assert set(order.sections())-set(old_order)=={'mod_GwentDeckChoice'} and not set(old_order)-set(order.sections())
 assert all(order[n][key]==old_order[n][key] for n in old_order for key in ['priority','enabled'])
 checks['unchanged_live_files']=len(unchanged)+len(controls)-len(control_drift);checks['external_live_drift']=drift+control_drift;checks['current_priority_relationships_unchanged']=True
 steam=SourceFileLoader('steam_baseline',str(Path(__file__).with_name('steam-baseline.py'))).load_module()
 app=text(game.parents[1]/'appmanifest_292030.acf');checks['steam_build']=re.search(r'"buildid"\s*"(\d+)"',app)[1]
 current_manifest={}
 for depot,gid in re.findall(r'"(\d+)"\s*\{\s*"manifest"\s*"(\d+)"',app):
  p=game.parents[2]/'depotcache'/(depot+'_'+gid+'.manifest');assert p.is_file(),str(p)
  current_manifest.update({x['relative'].lower():x for x in steam.manifest(p)})
 script_baselines=[]
 for key,x in current_manifest.items():
  if key.endswith('.ws'):
   assert steam.sha1(game/x['relative'])==x['sha1'],x['relative'];script_baselines.append(x['relative'])
 checks['current_steam_scripts_verified']=len(script_baselines)
 old_manifest={x['relative'].lower():x for x in read(ROOT/'evidence/steam-manifest-files.json')}
 changed_scripts=[k for k,x in current_manifest.items() if k.endswith('.ws') and old_manifest.get(k,{}).get('sha1')!=x['sha1']]
 overrides=[(x.get('mod'),x.get('relative')) for x in original if x.get('relative') and ('content/content0/'+x['relative'].removeprefix('content/')).lower() in changed_scripts]
 checks['changed_steam_scripts']=changed_scripts;checks['affected_whole_file_overrides']=overrides
 meta=current_manifest.get('content/metadata.store')
 if meta:checks['current_metadata_matches_steam']=steam.sha1(game/meta['relative'])==meta['sha1']
 refresh=read(ROOT/'evidence/steam-update-merges.json')
 for x in refresh:
  assert sha(game/'content/content0'/x['resource'].removeprefix('content/'))==x['current_vanilla_sha256']
 checks['refreshed_merges']=sum(x['merged_text_changed'] for x in refresh);checks['merge_update_inverse_roundtrip']=True
 supplemental=read(ROOT/'evidence/steam-update-overrides.json')
 for x in supplemental:
  assert sha(game/'content/content0'/x['resource'].removeprefix('content/'))==x['current_vanilla_sha256']
  assert sha(OUT/'payloads/merged/Mods/mod0000_MergedFiles'/x['resource'])==x['output_sha256']
 checks['additional_current_steam_overrides']=len(supplemental)
 core=OUT/'payloads/core'
 replacements={p.name for p in (core/'Mods').iterdir()}
 allws={x['path'].lower():Path(x['path']) for x in original if x['path'].lower().endswith('.ws')}
 for x in original:
  if x.get('mod') in replacements and x['path'].lower().endswith('.ws'):allws[x['path'].lower()]=core/'Mods'/x['mod']/x['relative']
 for x in original:
  if x.get('mod')=='mod0000_MergedFiles' and x['path'].lower().endswith('.ws'):allws[x['path'].lower()]=OUT/'payloads/merged/Mods/mod0000_MergedFiles'/x['relative']
 for x in supplemental:
  allws[str(game/'Mods'/x['source_mod']/x['resource']).lower()]=OUT/'payloads/merged/Mods/mod0000_MergedFiles'/x['resource']
 pattern=r'@(wrapMethod|replaceMethod|addMethod|addField)\s*\(\s*(\w+)\s*\)\s*(?:@\w+\([^)]*\)\s*)*(?:\w+\s+)*(function|event|var|autobind)\s+(\w+)'
 annotations=collections.defaultdict(list)
 for original_path,p in allws.items():
  for m in re.finditer(pattern,build.masked(text(p))):annotations[(m[2],m[4],m[1])].append(original_path)
 baseline=collections.Counter()
 utf16=[]
 for x in original:
  if not x['path'].lower().endswith('.ws'):continue
  p=Path(x['path'])
  if p.read_bytes().startswith((b'\xff\xfe',b'\xfe\xff')):utf16.append(str(p))
  for m in re.finditer(pattern,build.masked(text(p))):baseline[(m[2],m[4],m[1])]+=1
 counts=collections.Counter({k:len(v) for k,v in annotations.items()})
 added=counts-baseline;removed=baseline-counts
 assert added=={('CR4Player','BG2_CompatibilityEvadeFactor','addMethod'):1},added
 assert not removed,removed
 checks['annotations_preserved']=sum(baseline.values());checks['unique_helper_added']=True;checks['utf16_scripts_included']=utf16
 # Native dodge body remains an ordered subsequence after CSM's lifecycle block.
 vanilla=build.body(text(game/'content/content0/scripts/game/player/r4Player.ws'),'SetIsCurrentlyDodging')
 patch=build.body(text(core/'Mods/modCombatSpeed/content/scripts/local/combat_speed/CSMPlayerHooks.ws'),'SetIsCurrentlyDodging')
 native=[re.sub(r'\s+','',x) for x in vanilla.splitlines() if x.strip()]
 lines=[re.sub(r'\s+','',x) for x in patch.splitlines() if x.strip()];i=0
 for line in lines:
  if i<len(native) and line==native[i]:i+=1
 assert i==len(native),(i,len(native));checks['native_roll_immunities_preserved']=True
 # All same-path merge inputs are byte-identical, so no generated merge needs regeneration.
 merges=read(ROOT/'evidence/merge-source-check.json')
 for x in merges:
  if x['mod'] in replacements:assert sha(core/'Mods'/x['mod']/x['resource'])==x['source_sha256']
 checks['existing_merge_contributions']=len(merges)
 corebundles=[]
 for p in core.rglob('*.bundle'):corebundles.append({'path':str(p.relative_to(core)),'entries':len(list(bundles(p)))})
 checks['bundle_tables']=corebundles
 merged=OUT/'payloads/merged/Mods/mod0000_MergedFiles/content/scripts/game'
 inv=text(merged/'components/inventoryComponent.ws');menu=text(merged/'gui/main_menu/ingameMenu.ws');mapws=text(merged/'gui/menus/mapMenu.ws');r4=text(merged/'r4Game.ws')
 assert 'optional forceAdd : bool' in inv and inv.count('true, forceAdd')==3
 assert 'insideBounds : bool' in mapws and 'fromSelectionPanel, insideBounds, idToAdd' in mapws
 assert 'GetMarketingProxy' not in r4+menu and 'W3MarketingPopupData' not in menu
 assert 'GetFHUDConfig().UpdateUserSettings()' in menu and 'ChooseMainMenuType' in r4
 radial=text(merged/'gui/hud/modules/hudModuleRadialMenu.ws')
 assert 'm_desaturatedFields.Contains("Slot1")' in radial and 'potionsHelper.Update()' in radial
 common=text(merged/'gui/menus/commonMenu.ws');assert 'module.ForceModuleUpdate()' in common and 'GetOWManager().Cancel()' in common
 torch=text(merged/'explorations/exploration_movement_system/exploration_substates/explorationStateInteraction.ws')
 assert 'enum EBlendMode' in torch and torch.count('// modBetterTorchesNextGen')==3
 checks['native_api_and_retained_features']=True
 loc=SourceFileLoader('loc_index',str(Path(__file__).with_name('localization-audit.py'))).load_module()
 indexed=read(ROOT/'evidence/localization-index.json');arrow_strings=[]
 for p in (OUT/'payloads/arrow').rglob('*.w3strings'):
  row=loc.index(p);language=p.stem.lower()
  for other in [x for x in indexed if x['language']==language]:
   assert not set(row['ids'])&set(other['ids']),('Arrow string ID collision',language,other['mod'])
   assert set(row['keys'])&set(other['keys']) <= {str(0x4d5f8b0c)},('Unexpected Arrow key collision',language,other['mod'])
  arrow_strings.append({'language':language,'strings':row['count']})
 checks['arrow_localization_indexes']=arrow_strings
 stats=[]
 for original_name,delta_name in [('dx12user.settings','settings-profile.json'),('input.settings','optional-controls.json')]:
  snapshot=next(x for x in read(ROOT/'evidence/control-snapshot.json') if Path(x['live']).name==original_name)
  old=text(Path(snapshot['live']));delta=read(OUT/delta_name);new=text(OUT/'prepared-settings'/original_name)
  assert settings.transform(old,delta)==new
  before=values(old);after=values(new);allowed={(g,k) for g,items in delta.items() for k in items}
  assert all(after[k]==v for k,v in before.items() if k not in allowed)
  occupied=[k for k in allowed if k[1].startswith('IK_') and k in before and before[k]!=delta[k[0]][k[1]]]
  assert all(after[k]==before[k] for k in occupied)
  assert all(after[(g,k)]==v for g,items in delta.items() for k,v in items.items() if (g,k) not in occupied)
  stats.append({'file':original_name,'changes':sum(after.get(k)!=before.get(k) for k in allowed),'occupied_keys_skipped':[list(k) for k in occupied]})
 checks['settings']=stats
 # A realistic occupied binding and unrelated control survive the delta.
 sample='[Combat]\nIK_F8=(Action=Existing)\nIK_F3=(Action=OutfitWheel)\n';result=settings.transform(sample,{'Combat':{'IK_F8':'(Action=New)','IK_F9':'(Action=Helper)'}})
 assert values(result)[('Combat','IK_F8')]=='(Action=Existing)' and values(result)[('Combat','IK_F3')]=='(Action=OutfitWheel)'
 try:settings.transform('[Combat]\nIK_F8=a\nIK_F8=b\n',{'Combat':{'IK_F8':'c'}})
 except AssertionError:pass
 else:raise AssertionError('Duplicate keys must be rejected')
 checks['settings_collision_tests']=True
 v=read(OUT/'validation.json')
 for x in v['archives']:
  with zipfile.ZipFile(OUT/x['name']) as z:
   assert z.testzip() is None and len(set(z.namelist()))==len(z.namelist())
   for f in x['files']:
    import hashlib
    assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
  assert sha(OUT/x['name'])==x['sha256']
 checks['archives_checked']=len(v['archives']);checks['compile_pass']=False;checks['runtime_pass']=False
 (OUT/'integration-validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(json.dumps(checks))
if __name__=='__main__':main()
