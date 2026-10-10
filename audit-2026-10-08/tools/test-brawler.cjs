// Execute generated controller/mechanics bodies with narrow deterministic fixtures.
// This tests actual source branches, not engine animation, compiled B&S or save serialization.
const fs=require('fs'),assert=require('assert'),path=require('path');
const [payloadRoot,receiptPath]=process.argv.slice(2);
assert(payloadRoot&&receiptPath,'Usage: node test-brawler.cjs payload-root receipt.json');
const folder=path.join(payloadRoot,'Mods/modBestGsSchoolStances/content/scripts/local');
const controller=fs.readFileSync(path.join(folder,'CompatBrawlerController.ws'),'utf8');
const mechanics=fs.readFileSync(path.join(folder,'CompatBrawlerMechanics.ws'),'utf8');
function body(text,name){
 const start=text.indexOf('function '+name+'(')>=0?text.indexOf('function '+name+'('):text.indexOf('event '+name+'(');
 assert(start>=0,name);const a=text.indexOf('{',start);let depth=1,z=a+1;
 while(depth){if(text[z]==='{')depth++;if(text[z]==='}')depth--;z++;}
 return text.slice(a+1,z-1);
}
function execute(text,name){
 const source=body(text,name).replace(/\bvar (\w+(?:,\s*\w+)*)\s*:\s*\w+\s*;/g,'let $1;')
  .replace(/(\d+)\.f\b/g,'$1').replace(/(\d+\.\d+)f\b/g,'$1')
  .replace(/\((?:CActor|W3Action_Attack|float)\)/g,'');
 return new Function('env',`with(env){${source}}`);
}
const p={compatBrawlerEnabled:false,compatBrawlerPending:false,compatBrawlerDesired:false,
 stateName:'Exploration',currentWeapon:'steel',alive:true,ciri:false,busy:false,dodging:false,isInFinisher:false,
 allowed:true,vehicle:false,swim:false,air:false,boat:false,interaction:false,minigame:false,timers:new Set(),equips:[],
 GetCurrentStateName(){return this.stateName},IsAlive(){return this.alive},IsCiri(){return this.ciri},
 IsUsingVehicle(){return this.vehicle},IsOnBoat(){return this.boat},IsSwimming(){return this.swim},IsInAir(){return this.air},
 IsInsideInteraction(){return this.interaction},IsInFistFightMiniGame(){return this.minigame},IsInCombatAction(){return this.busy},
 IsCurrentlyDodging(){return this.dodging},IsActionAllowed(){return this.allowed},GetCurrentMeleeWeaponType(){return this.currentWeapon},
 AddTimer(n){this.timers.add(n)},RemoveTimer(n){this.timers.delete(n)},OnEquipMeleeWeapon(n){this.currentWeapon=n;this.equips.push(n)},
 BG2_IsFightingWithFists(){return this.currentWeapon==='fists'},BG2_GloveEnhancementCount(){return 2},
 BG2_BrawlerSocketDamageBonus(){return 10}};
const env=p;Object.assign(env,{GetWitcherPlayer:()=>p,PW_Fists:'fists',EIAB_DrawWeapon:1,
 theGame:{IsFading:()=>false,IsBlackscreen:()=>false,IsFocusModeActive:()=>false},MaxF:Math.max,
 BG2_Config:(g,k,fallback)=>fallback});
for(const name of ['CompatBrawlerContextAllowed','CompatBrawlerActive','CompatBrawlerClear','CompatBrawlerToggle','CompatBrawlerTick']){
 const f=execute(controller,name);p[name]=()=>f.call(p,env);
}
assert(!p.CompatBrawlerActive());p.CompatBrawlerToggle();assert(p.CompatBrawlerActive()&&p.currentWeapon==='fists');
p.CompatBrawlerToggle();assert(!p.CompatBrawlerActive()&&!p.timers.size);
assert(p.equips.length===1,'Exit must not force a sword');
p.busy=true;p.CompatBrawlerToggle();assert(p.compatBrawlerPending&&!p.CompatBrawlerActive());
p.CompatBrawlerToggle();p.busy=false;p.CompatBrawlerTick();assert(!p.CompatBrawlerActive());
p.dodging=true;p.CompatBrawlerToggle();assert(!p.CompatBrawlerActive());p.dodging=false;p.CompatBrawlerTick();assert(p.CompatBrawlerActive());
p.stateName='Swimming';p.CompatBrawlerTick();assert(!p.compatBrawlerEnabled&&!p.compatBrawlerPending&&!p.timers.size);
for(const flag of ['ciri','vehicle','boat','swim','air','interaction','minigame']){
 p.stateName='Exploration';p[flag]=true;p.CompatBrawlerToggle();assert(!p.CompatBrawlerActive());p[flag]=false;
}
p.alive=false;p.CompatBrawlerToggle();assert(!p.CompatBrawlerActive());p.alive=true;
p.allowed=false;p.CompatBrawlerToggle();assert(p.compatBrawlerPending&&!p.CompatBrawlerActive());
p.allowed=true;p.CompatBrawlerTick();assert(p.CompatBrawlerActive());
p.CompatBrawlerClear();p.isInFinisher=true;p.CompatBrawlerToggle();assert(p.compatBrawlerPending&&!p.CompatBrawlerActive());
p.isInFinisher=false;p.CompatBrawlerTick();assert(p.CompatBrawlerActive());
let wrappedCalls=0;env.wrappedMethod=()=>{wrappedCalls++};
function action(){return {attacker:p,victim:{},processedDmg:{vitalityDamage:100,essenceDamage:10},
 IsDoTDamage:()=>false,IsActionMelee:()=>true,WasDodged:()=>false,
 MultiplyAllDamageBy(f){this.processedDmg.vitalityDamage*=f;this.processedDmg.essenceDamage*=f}}}
const damage=execute(mechanics,'ProcessAction'),defense=execute(mechanics,'ReduceDamage');
env.act=action();damage.call(p,env);assert(env.act.processedDmg.vitalityDamage===170);
damage.call(p,env);assert(env.act.processedDmg.vitalityDamage===170&&wrappedCalls===2,'No double bonus');
p.CompatBrawlerClear();env.act=action();damage.call(p,env);assert(env.act.processedDmg.vitalityDamage===100);
p.CompatBrawlerToggle();env.damageData=action();env.damageData.attacker={};env.damageData.victim=p;
defense.call(p,env);assert(env.damageData.processedDmg.vitalityDamage===65);
p.CompatBrawlerClear();env.damageData.processedDmg.vitalityDamage=100;defense.call(p,env);assert(env.damageData.processedDmg.vitalityDamage===100);
p.CompatBrawlerToggle();p.currentWeapon='steel';env.act=action();damage.call(p,env);assert(env.act.processedDmg.vitalityDamage===100,'Brawler does not buff swords');
p.currentWeapon='fists';env.act=action();env.act.IsDoTDamage=()=>true;damage.call(p,env);assert(env.act.processedDmg.vitalityDamage===100);
env.act=action();env.act.IsActionMelee=()=>false;damage.call(p,env);assert(env.act.processedDmg.vitalityDamage===100);
env.damageData=action();env.damageData.victim=p;env.damageData.attacker={};env.damageData.processedDmg.vitalityDamage=0;
defense.call(p,env);assert(env.damageData.processedDmg.vitalityDamage===0,'Native absorbed damage stays zero');
let nativeResult=true;env.wrappedMethod=()=>nativeResult;
env.parryInfo={attacker:{IsHeavyAttack:()=>true,IsSuperHeavyAttack:()=>false},attackActionName:'heavy'};
for(const name of ['PerformParryCheck','PerformCounterCheck'])assert(execute(mechanics,name).call(p,env)===false);
env.parryInfo.attacker.IsHeavyAttack=()=>false;
for(const name of ['PerformParryCheck','PerformCounterCheck'])assert(execute(mechanics,name).call(p,env)===true);
p.CompatBrawlerClear();env.parryInfo.attacker.IsHeavyAttack=()=>true;
for(const name of ['PerformParryCheck','PerformCounterCheck'])assert(execute(mechanics,name).call(p,env)===true,'Normal mode is native passthrough');
p.CompatBrawlerToggle();nativeResult=false;env.target=p;env.attacker={IsWeaponHeld:()=>false};env.bothUsingFists=true;
const fistGuard=execute(mechanics,'FistFightCheck');assert(fistGuard.call(p,env)===true&&env.bothUsingFists===false);
p.CompatBrawlerClear();assert(fistGuard.call(p,env)===false,'Normal mode cannot relax fist guard');
nativeResult=true;assert(fistGuard.call(p,env)===true,'Native positive result retained');
let toggleCount=0;p.CompatBrawlerToggle=()=>{toggleCount++};
env.thePlayer=p;env.theInput={GetContext:()=> 'Combat'};env.IsPressed=a=>a==='press';env.IsReleased=a=>a==='release';
const input=execute(controller,'OnCompatBrawlerToggle');env.compatBrawlerKeyHeld=false;
for(const a of ['press','press','release','press','release']){env.action=a;input.call(p,env)}
assert(toggleCount===2,'One toggle per press; no auto-repeat');
env.isFromLoad=true;env.previousInput=undefined;const registrations=[];
env.theInput.UnregisterListener=(...args)=>registrations.push(['remove',...args.slice(1)]);
env.theInput.RegisterListener=(...args)=>registrations.push(['add',...args.slice(1)]);
p.compatBrawlerEnabled=true;p.compatBrawlerPending=true;p.compatBrawlerKeyHeld=true;
execute(controller,'Initialize').call(p,env);
assert(!p.compatBrawlerEnabled&&!p.compatBrawlerPending&&!p.compatBrawlerKeyHeld);
assert(registrations.length===2&&registrations[1][2]==='CompatBrawlerToggle');
assert(!/SetAnimationSpeedMultiplier|AddAbility|SetStatPointMax|saved var|BG2_(Witcher|Feline|Bear|Griffin|Viper)\b/.test(controller+mechanics));
const result={actual_generated_bodies_executed:true,toggle_and_pending:true,invalid_contexts_and_death:true,
 neutral_damage_passthrough:true,fist_damage_and_defense:true,no_double_bonus:true,sword_bonus_absent:true,
 repeat_suppression:true,heavy_counter_limits:true,light_fist_guard:true,input_reinitialization_neutral:true,
 dot_and_nonmelee_excluded:true,native_zero_preserved:true,
 persistent_stat_or_speed_writes_absent:true,actual_engine_or_save_tested:false,compiled_blood_and_steel_tested:false};
fs.writeFileSync(receiptPath,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
