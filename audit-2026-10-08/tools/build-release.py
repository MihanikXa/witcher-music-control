"""Build private compatibility replacements from pinned local inputs; never deploy."""
import argparse,collections,hashlib,json,re,shutil,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'release/witcher-compatibility'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2),encoding='utf-8')
def masked(t):
 # Keep offsets stable while masking strings and comments, including braces in them.
 return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/',lambda m:''.join('\n' if c=='\n' else ' ' for c in m[0]),t,flags=re.S)
def bounds(t,name):
 m=list(re.finditer(r'\bfunction\s+'+re.escape(name)+r'\s*\(',masked(t)));assert len(m)==1,(name,len(m))
 clean=masked(t);start=clean.index('{',m[0].end());depth=1;end=start+1
 while depth:
  if clean[end]=='{':depth+=1
  if clean[end]=='}':depth-=1
  end+=1
 return start+1,end-1
def replace_body(t,name,body):
 a,b=bounds(t,name);return t[:a]+'\n'+body.rstrip()+'\n'+t[b:]
def body(t,name):a,b=bounds(t,name);return t[a:b]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);ap.add_argument('--documents',type=Path,required=True);args=ap.parse_args();game=args.game.resolve();docs=args.documents.resolve()
 assert game not in OUT.resolve().parents and docs not in OUT.resolve().parents
 assert not OUT.is_symlink()
 OUT.mkdir(parents=True,exist_ok=True)
 expected={x['path'].lower():x['sha256'] for n in ['installed-files.json','other-game-files.json','current-gwent-layout.json'] for x in json.loads((ROOT/'evidence'/n).read_text())}
 sources={};changes=[]
 def source(p):
  p=p.resolve();h=digest(p);assert expected.get(str(p).lower())==h,('Source changed or unpinned',str(p));sources[str(p)]=h;return p
 def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source(p),q)
 def edit(p,name,callback):
  before=p.read_text(encoding='utf-8-sig');after=callback(before);assert before!=after,name
  p.write_text(after,encoding='utf-8',newline='\r\n');changes.append(dict(file=str(p.relative_to(OUT)),purpose=name,before_text_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=digest(p)))
 core=OUT/'payloads/core';loc=OUT/'payloads/localization';arrow=OUT/'payloads/arrow';merged=OUT/'payloads/merged';gwent=OUT/'payloads/gwent'
 refresh=json.loads((ROOT/'evidence/steam-update-merges.json').read_text())
 for row in refresh:
  resource=row['resource'];vanilla=game/'content/content0'/resource.removeprefix('content/')
  assert digest(vanilla)==row['current_vanilla_sha256'],'Run refresh-merges against current Steam version'
  sources[str(vanilla)]=digest(vanilla)
  target=merged/'Mods/mod0000_MergedFiles'/resource
  original_merge=source(game/'Mods/mod0000_MergedFiles'/resource)
  if row['merged_text_changed']:
   prepared=ROOT/'private/steam-update-merges/payload/Mods/mod0000_MergedFiles'/resource
   assert digest(prepared)==row['output_sha256'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prepared,target)
   changes.append(dict(file=str(target.relative_to(OUT)),purpose='Preserve current Steam changes in existing merge',after_sha256=digest(target)))
  else:copy(original_merge,target)
 for row in json.loads((ROOT/'evidence/steam-update-overrides.json').read_text()):
  resource=row['resource'];vanilla=game/'content/content0'/resource.removeprefix('content/')
  assert digest(vanilla)==row['current_vanilla_sha256'];sources[str(vanilla)]=digest(vanilla)
  source(game/'Mods'/row['source_mod']/resource)
  prepared=ROOT/'private/steam-update-merges/payload/Mods/mod0000_MergedFiles'/resource
  assert digest(prepared)==row['output_sha256'];target=merged/'Mods/mod0000_MergedFiles'/resource
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prepared,target)
  changes.append(dict(file=str(target.relative_to(OUT)),purpose='Current Steam native API with retained mod features',after_sha256=digest(target)))
 # Replacement packages deliberately keep original mod folder names. Disable the
 # four original Vortex packages first: no duplicate annotated scopes are added.
 mods=['modBestGsSchoolStances','modCombatSpeed','modAutoLoot','modResponsiveMovement']
 for mod in mods:
  for p in (game/'Mods'/mod).rglob('*'):
   if p.is_file() and '__folder_managed_by_vortex' not in p.parts and '__folder_managed_by_vortex' not in p.name and '__pycache__' not in p.parts:
    copy(p,core/'Mods'/mod/p.relative_to(game/'Mods'/mod))
 pc=Path('bin/config/r4game/user_config_matrix/pc')
 for name in ['modBestGsStances.xml','modCombatSpeed.xml','modAutoLoot.xml','modResponsiveMovement.xml','modBloodAndSteel.xml']:
  copy(game/pc/name,core/pc/name)
 copy(game/'bin/config/base/autoloot.ini',core/'bin/config/base/autoloot.ini')
 state=core/'Mods/modBestGsSchoolStances/content/scripts/local/BestGsStanceState.ws'
 original=state.read_text(encoding='utf-8-sig');evade=body(original,'SetIsCurrentlyDodging');a=evade.index('factor = 1.f;');b=evade.index('bg2_evadeSpeedId = SetAnimationSpeedMultiplier');factor=evade[a:b]
 def state_edit(t):
  # Remove only the superseded timing writes, preserving original control flow,
  # wrapper call order, guards, last-evade state and branch-specific cleanup.
  assert t.count(factor)==1
  t=t.replace(factor,'').replace('    var factor : float;\n','')
  for line in t.splitlines(True):
   if 'SetAnimationSpeedMultiplier(' in line or "AddTimer('BG2_AttackFallback'" in line or "AddTimer('BG2_EvadeFallback'" in line:
    t=t.replace(line,'')
  assert 'factor' not in body(t,'SetIsCurrentlyDodging')
  for name,field in [('BG2_ResetAttackSpeed','bg2_attackSpeedId'),('BG2_ResetEvadeSpeed','bg2_evadeSpeedId')]:
   old=body(t,name);removed='    if(bg2_speedInitialized && '+field+' != -1)\n        ResetAnimationSpeedMultiplier('+field+');\n'
   assert old.count(removed)==1
   t=replace_body(t,name,old.replace(removed,''))
  return t+'''\n// Compatibility: one owner applies timing; school factors remain configurable.
@addMethod(CR4Player)
function BG2_CompatibilityEvadeFactor(isRolling : bool) : float
{
    var factor : float;
'''+factor+'''    return factor;
}
'''
 edit(state,'Transfer school timing into one CSM calculation',state_edit)
 calc=core/'Mods/modCombatSpeed/content/scripts/local/combat_speed/CSMCalculation.ws'
 def calculation(t):
  old=body(t,'CalculateSpeedMultiplier');old=old.replace('var mult : float;','var mult : float;\n\tvar p : CR4Player;')
  return replace_body(t,'CalculateSpeedMultiplier',old.replace('return ApplySpeedLimits(mult);','''p = GetWitcherPlayer();
    if(p && !p.IsCiri())
    {
        switch(action)
        {
            case CSMAction_LightAttack: if(p.GetWeaponHolster().IsMeleeWeaponReady()) mult *= p.BG2_AttackFactor(false); break;
            case CSMAction_HeavyAttack: if(p.GetWeaponHolster().IsMeleeWeaponReady()) mult *= p.BG2_AttackFactor(true); break;
            case CSMAction_Dodge: mult *= p.BG2_CompatibilityEvadeFactor(false); break;
            case CSMAction_Roll: mult *= p.BG2_CompatibilityEvadeFactor(true); break;
        }
    }
    return ApplySpeedLimits(mult);'''))
 edit(calc,'Apply school factor before the single final CSM clamp',calculation)
 # Respect the original guard/roll-immunity implementation; only CSM's enabled
 # predicate is narrowed to Geralt. Ciri has no school profile.
 conf=core/'Mods/modCombatSpeed/content/scripts/local/combat_speed/CSMConfiguration.ws'
 def enabled(t):
  old=body(t,'Enabled');return replace_body(t,'Enabled','    if(!thePlayer || thePlayer.IsCiri()) return false;\n'+old)
 edit(conf,'Exclude Ciri from school-combat controller',enabled)
 hooks=core/'Mods/modCombatSpeed/content/scripts/local/combat_speed/CSMPlayerHooks.ws'
 def evade_lifecycle(t):
  old=body(t,'SetIsCurrentlyDodging')
  old=old.replace('var combatSpeed : CombatSpeed;','var combatSpeed : CombatSpeed;\n\tvar wasDodging : bool;')
  old=old.replace('super.SetIsCurrentlyDodging(enable, isRolling);','wasDodging = IsCurrentlyDodging();\n\tsuper.SetIsCurrentlyDodging(enable, isRolling);\n\tif(enable && !wasDodging) ResetCombatSpeedForFinisher();')
  return replace_body(t,'SetIsCurrentlyDodging',old)
 edit(hooks,'Accepted evade clears prior CSM attack channels before applying evade',evade_lifecycle)
 animation=core/'Mods/modCombatSpeed/content/scripts/local/combat_speed/CSMAnimation.ws'
 def exploration_cleanup(t):
  assert t.count('= thePlayer.SetAnimationSpeedMultiplier(')==6
  return re.sub(r'(\t\w+ = thePlayer.SetAnimationSpeedMultiplier\()',r'\tthePlayer.CSM_EndExplorationTiming();\n\1',t)+'''\n@addMethod(CR4Player)
public final function CSM_EndExplorationTiming() : void
{
    if(defaultLocomotionController)
        ResponsiveMovementEndTransitionAnimation(defaultLocomotionController);
}
'''
 edit(animation,'Release the RM transition causer before each CSM timing write',exploration_cleanup)
 med=core/'Mods/modBestGsSchoolStances/content/scripts/local/BestGsStanceMedallion.ws'
 def medallion(t):
  t=replace_body(t,'BG2_UpdateStanceMedallion','    return false;')
  t=replace_body(t,'BG2_RefreshStanceMedallion','    // Native popup/text feedback remains in BestGsStanceHud.ws.')
  return replace_body(t,'UpdateVitality','    wrappedMethod();')
 edit(med,'Retain SAH wolf artwork without missing-resource diagnostics',medallion)
 manager=core/'Mods/modAutoLoot/content/scripts/local/modAutoLootManager.ws'
 edit(manager,'Use existing interval-aware player tick; retire duplicate timer',lambda t:replace_body(t,'StartTimer',"    if(!m_player) m_player = GetWitcherPlayer();\n    if(m_player) m_player.RemoveTimer('AutoLootPulseTimer');"))
 rm=core/'Mods/modResponsiveMovement/content/scripts/local/responsiveMovement.ws'
 def movement(t):
  old=body(t,'ResponsiveMovementSetTransitionAnimation');return replace_body(t,'ResponsiveMovementSetTransitionAnimation','''    if(!controller || !controller.player) return;
    if(controller.player.IsInCombat() || controller.player.IsInCombatAction() || controller.player.IsCurrentlyDodging())
    {
        ResponsiveMovementEndTransitionAnimation(controller);
        return;
    }
'''+old)
 edit(rm,'Keep exploration transition multiplier out of combat',movement)
 menu=core/pc/'modBestGsStances.xml';tree=ET.parse(menu)
 # Keep Medallion defined for initialization/migration compatibility, hide it.
 for v in tree.iter('Var'):
  if v.get('id')=='Medallion':v.set('visibilityCondition','hideAlways')
 tree.write(menu,encoding='utf-8',xml_declaration=True);changes.append(dict(file=str(menu.relative_to(OUT)),purpose='Hide unavailable medallion option; retain stance speed controls',after_sha256=digest(menu)))
 bas=core/pc/'modBloodAndSteel.xml';tree=ET.parse(bas)
 for e in tree.iter('Entry'):
  if e.get('varId') in ['BaS_CustomAttackEnabled','BaS_CustomDodgeEnabled']:e.set('value','false')
 tree.write(bas,encoding='utf-8',xml_declaration=True);changes.append(dict(file=str(bas.relative_to(OUT)),purpose='Default both competing animation selectors off',after_sha256=digest(bas)))
 # Correct all five shared English IDs. Preserve the vanilla letter signature.
 helper=source(game/'Mods/modSeamlessAdaptiveHUD/translations/w3s.py');sys.path.insert(0,str(helper.parent));import w3s
 bia=w3s.read(source(game/'Mods/modbrothersinarms/content/en.w3strings'),0x79321793);grammar=w3s.read(source(game/'Mods/modZ_GrammarOfThePathRemastered/content/en.w3strings'),0x79321793);upr=w3s.read(source(game/'Mods/modunreasonableplotredesigned/content/en.w3strings'),0x79321793)
 strings={i:bia['strings'][i] for i in [1092187,1130095,391138]};strings[558403]=grammar['strings'][558403]
 letter=grammar['strings'][1063514].replace('I must flee this place. I have brought great shame','I must flee this place.<br><br>My head hangs low as I write, for I have brought great shame')
 assert 'My head hangs low as I write' in letter and letter.endswith('H')
 strings[1063514]=letter
 textfile=loc/'Mods/mod0000_CompatibilityText/content/en.w3strings';textfile.parent.mkdir(parents=True,exist_ok=True)
 w3s.write(textfile,0x79321793,upr['key1'],upr['key2'],[(i,None,s) for i,s in sorted(strings.items())],lambda x:0)
 decoded=w3s.read(textfile,0x79321793);assert decoded['strings']==strings and not decoded['keys']
 save(OUT/'localization-preview.json',strings)
 for p in (game/'ArrowParryManual/Mods/modArrowParryManual').rglob('*'):
  if p.is_file() and '__folder_managed_by_vortex' not in p.name:copy(p,arrow/'Mods/modArrowParryManual'/p.relative_to(game/'ArrowParryManual/Mods/modArrowParryManual'))
 copy(game/pc/'modArrowParryManual.xml',arrow/pc/'modArrowParryManual.xml')
 # Keep the author's complete vanilla-Gwent variant, compiled scripts and DLC.
 # Correct layout only; do not include the incompatible Gwent My Way variant.
 gwent_info=json.loads((ROOT/'evidence/gwent-integration.json').read_text(encoding='utf-8'))
 for root,target in [(game/'Gwent Deck Choice - Vanilla Gwent/mods/mod_GwentDeckChoice',gwent/'Mods/mod_GwentDeckChoice'),(game/'DLC/dlcGwentDeckChoice',gwent/'DLC/dlcGwentDeckChoice')]:
  for p in root.rglob('*'):
   if p.is_file() and '__folder_managed_by_vortex' not in p.name:copy(p,target/p.relative_to(root))
 copy(game/pc/'GwentDeckChoice.xml',gwent/pc/'GwentDeckChoice.xml')
 # The settings transformer operates only on user-selected copies and preserves
 # unrelated sections/lines. No settings are baked into game-root archives.
 profile={'BaS_Main':{'BaS_CustomAttackEnabled':'false','BaS_CustomDodgeEnabled':'false','BaS_DamageIncrease':'0','BaS_CloseCamera':'false'},'csmGeneral':{'CSM_On':'1','CSM_HCap':'1','CSM_LCap':'1','CSM_MinSpeed':'50','CSM_MaxSpeed':'200','CSM_ApplyToFinishers':'0'},'csmBaseSpeed':{'CSM_Base':'0'},'csmSkillSpeed':{'CSM_SR':'0'},'csmArmorSpeed':{'CSM_Arm':'0'},'csmAdrenaline':{'CSM_Adren':'0','CSM_RFSR':'0'},'fhudHUD':{k:'false' for k in ['fhudEnableCombatModules','fhudEnableCombatModulesOnUnsheathe','fhudEnableWolfModuleOnVitalityChanged','fhudEnableWitcherSensesModules','fhudEnableMeditationModules','fhudEnableRadialMenuModules']},'fhudMarkers':{'fhud3DMarkersEnabled':'false','fhudCompassMarkersEnabled':'false'}}
 # Validate every setting against installed menu definitions; no invented keys.
 visible={(g.get('id'),v.get('id')) for p in (game/pc).glob('*.xml') for g in ET.parse(p).iter('Group') for v in g.iter('Var')}
 assert all((group,key) in visible for group,items in profile.items() for key in items),[(g,k) for g,x in profile.items() for k in x if (g,k) not in visible]
 save(OUT/'settings-profile.json',profile)
 controls={context:{'IK_F8':'(Action=ToggleArdHood)','IK_F9':'(Action=ShowPotionsHelper)','IK_F10':'(Action=ShowBombsHelper)','IK_F11':'(Action=ShowOilsHelper)'} for context in ['Exploration','Combat','Horse','Boat','BoatPassenger','Swimming','Diving','Scene']}
 save(OUT/'optional-controls.json',controls)
 shutil.copyfile(ROOT/'tools/prepare-settings.py',OUT/'prepare-settings.py')
 # Concrete priority plan: UPR's coherent eight-resource redesign and SAH's
 # complete wolf HUD win. No binary is claimed merged or rewritten.
 order=json.loads((ROOT/'evidence/mods-settings.json').read_text());names=sorted(order,key=lambda n:int(order[n]['priority']))
 names.remove('modunreasonableplotredesigned');names.insert(names.index('modbrothersinarms'),'modunreasonableplotredesigned');names.remove('modSeamlessAdaptiveHUD');names.insert(names.index('modBestGsSchoolStances'),'modSeamlessAdaptiveHUD');names.insert(1,'mod0000_CompatibilityText');names.append('modGeraltOutfitWheel')
 plan={n:dict(priority=i+1,enabled=True) for i,n in enumerate(names)};save(OUT/'load-order.json',plan)
 # GDC author's BIA compatibility relationship; UPR's separate resources stay
 # ahead of BIA too. Install the complete corrected package, not the orphan DLC.
 names.insert(names.index('modbrothersinarms'),'mod_GwentDeckChoice')
 plan={n:dict(priority=i+1,enabled=True) for i,n in enumerate(names)}
 save(OUT/'load-order.json',plan)
 bundle=json.loads((ROOT/'evidence/bundled-collisions.json').read_text());winners={p:('modSeamlessAdaptiveHUD' if p.endswith('.redswf') else 'modunreasonableplotredesigned') for p in bundle if p!='strings.list'}
 effective=[dict(resource=p,winner=n,sha256=next(x['sha256'] for x in bundle[p] if x['mod']==n),bytes=next(x['extracted_size'] for x in bundle[p] if x['mod']==n)) for p,n in winners.items()]
 for p,n in winners.items():
  chosen=next(x for x in bundle[p] if x['mod']==n)
  source(Path(chosen['bundle']))
  extracted=Path(chosen['extracted'])
  assert digest(extracted)==chosen['sha256'] and extracted.stat().st_size==chosen['extracted_size']
  assert plan[n]['priority'] < min(plan[x['mod']]['priority'] for x in bundle[p] if x['mod']!=n)
 for chosen in [x for x in gwent_info['scenes'] if x['mod']=='mod_GwentDeckChoice']:
  source(Path(chosen['bundle']));assert digest(Path(chosen['extracted']))==chosen['sha256']
  assert plan['mod_GwentDeckChoice']['priority'] < plan['modbrothersinarms']['priority']
  effective.append(dict(resource=chosen['resource'],winner=chosen['mod'],sha256=chosen['sha256'],bytes=chosen['extracted_size']))
 save(OUT/'effective-resource-winners.json',effective)
 # Automated release checks.
 checks={'localization_roundtrip':True,'source_hash_guards':True,'archives':[],'script_delimiters':[],'xml':[],'loose_school_timing_single_controller':False,'compilation':'not performed by build-release; see compiler receipts','runtime_test':False}
 for p in list(core.rglob('*.ws'))+list(merged.rglob('*.ws'))+list(arrow.rglob('*.ws'))+list(gwent.rglob('*.ws')):
  t=masked(p.read_text(encoding='utf-8-sig'));stack=[]
  for c in t:
   if c in '{([':stack.append(c)
   elif c in '})]':assert stack and stack.pop()=={'}':'{',')':'(',']':'['}[c],str(p)
  assert not stack,str(p);checks['script_delimiters'].append(str(p.relative_to(OUT/'payloads')))
 for p in list(core.rglob('*.xml'))+list(arrow.rglob('*.xml'))+list(gwent.rglob('*.xml')):ET.parse(p);checks['xml'].append(str(p.relative_to(OUT/'payloads')))
 assert 'SetAnimationSpeedMultiplier(' not in masked(state.read_text())
 assert 'AddTimer' not in masked(body(manager.read_text(),'StartTimer'))
 assert len(re.findall(r'ApplySpeedLimits\s*\(',masked(body(calc.read_text(),'CalculateSpeedMultiplier'))))==1
 checks['loose_school_timing_single_controller']=True
 for number,(name,folder) in enumerate([('core-replacements',core),('localization',loc),('arrow-layout',arrow),('updated-merges',merged),('gwent-deck-choice-layout',gwent)],1):
  files=sorted(p for p in folder.rglob('*') if p.is_file());assert files
  archive=OUT/(str(number).zfill(2)+'-'+name+'.zip')
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
   for p in files:
    rel=p.relative_to(folder).as_posix();assert rel.split('/')[0] in ['Mods','bin','DLC'];assert '__folder_managed_by_vortex' not in rel
    info=zipfile.ZipInfo(rel,date_time=(2026,10,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   assert set(z.namelist())=={p.relative_to(folder).as_posix() for p in files}
   for p in files:assert hashlib.sha256(z.read(p.relative_to(folder).as_posix())).hexdigest()==digest(p)
  checks['archives'].append(dict(name=archive.name,sha256=digest(archive),bytes=archive.stat().st_size,files=[dict(path=p.relative_to(folder).as_posix(),sha256=digest(p),bytes=p.stat().st_size) for p in files],crc_pass=True,payload_hashes_pass=True))
 save(OUT/'source-manifest.json',sources);save(OUT/'changes.json',changes);save(OUT/'validation.json',checks)
 print(json.dumps({'archives':[(x['name'],x['bytes'],len(x['files'])) for x in checks['archives']],'changed_files':len(changes),'localization_ids':list(strings),'compilation':'see compiler receipts'}))
if __name__=='__main__':main()
