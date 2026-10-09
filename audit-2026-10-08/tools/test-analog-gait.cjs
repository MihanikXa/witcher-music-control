// Execute the generated mapping fragment with a small numeric engine fixture.
// This checks source math/control flow, not game animation or device dispatch.
const fs=require('fs'),assert=require('assert');
const [sourcePath,receiptPath]=process.argv.slice(2);
assert(sourcePath && receiptPath,'Usage: node test-analog-gait.cjs generated-locomotion.ws receipt.json');
const source=fs.readFileSync(sourcePath,'utf8');
const start=source.indexOf('if (compatibilityUseSelectedGait && speed > 0.f');
const end=source.indexOf('tempInt = (int)( player.playerMoveType );',start);
assert(start>=0 && end>start);
const fragment=source.slice(start,end).replace(/(\d+)\.f\b/g,'$1');
const run=new Function('fixture',`
 let compatibilityUseSelectedGait=fixture.eligible!==false;
 let compatibilityRawMagnitude=fixture.magnitude;
 let compatibilityTargetCap;
 let compatibilityGaitCap=fixture.cap??-1;
 let speed=fixture.nativeSpeed??(fixture.magnitude>0?0.6:0);
 const speedWalkingMax=0.6,speedRunning=1,forceWalkSpeed=fixture.forceWalk===true;
 const PMT_Idle=0,PMT_Walk=1,PMT_Run=2;
 const player={GetIsSprinting:()=>fixture.sprinting===true,GetIsWalkToggled:()=>fixture.walk,playerMoveType:fixture.nativeType??0};
 const theTimer={timeDelta:fixture.dt??1/60};
 const MinF=Math.min,MaxF=Math.max;
 ${fragment}
 return {speed,cap:compatibilityGaitCap,type:player.playerMoveType};
`);
let samples=0;
for(const walk of [true,false])for(let i=0;i<=1000;i++){
 const magnitude=i/1000;const r=run({walk,magnitude});
 assert(Math.abs(r.speed-magnitude*(walk?0.6:1))<1e-10);
 if(i>0)assert.strictEqual(r.type,walk?1:2);
 samples++;
}
for(const walk of [true,false]){
 const a=run({walk,magnitude:0.6999}),b=run({walk,magnitude:0.7001});
 assert(Math.abs(b.speed-a.speed)<0.001,'No threshold jump at native run threshold');
}
let cap=1,prior=1;
for(let i=0;i<12;i++){
 const r=run({walk:true,magnitude:1,cap});assert(r.type===1);
 assert(r.speed<=prior+1e-10&&prior-r.speed<=0.05+1e-10);
 cap=r.cap;prior=r.speed;
}
assert(Math.abs(cap-0.6)<1e-10);
for(let i=0;i<12;i++){
 const r=run({walk:false,magnitude:1,cap});assert(r.type===2);
 assert(r.speed>=prior-1e-10&&r.speed-prior<=0.05+1e-10);
 cap=r.cap;prior=r.speed;
}
assert(Math.abs(cap-1)<1e-10);
for(const cap of [0.6,1]){
 const r=run({walk:false,magnitude:1,cap,sprinting:true,nativeSpeed:1.5,nativeType:3});
 assert(r.speed===1.5&&r.type===3&&r.cap===cap,'Sprint is native; remembered range untouched');
 const release=run({walk:cap===0.6,magnitude:1,cap:r.cap});assert(release.speed===cap);
}
for(const nativeSpeed of [0,0.2,0.6,1]){
 const r=run({walk:true,magnitude:1,cap:0.6,eligible:false,nativeSpeed,nativeType:9});
 assert(r.speed===nativeSpeed&&r.type===9,'Special states preserve native result');
}
assert(run({walk:false,magnitude:1,cap:1,forceWalk:true}).speed<=0.6);
assert(!fragment.includes('LastUsed'),'Selected gait mapping is independent of last input source');
const result={mapping_source_executed:true,proportional_samples:samples,threshold_continuity:true,bounded_mode_transition:true,sprint_range_preserved:true,special_states_untouched:true,mixed_source_math_independent:true,actual_hardware_dispatch_tested:false,actual_animation_tested:false};
fs.writeFileSync(receiptPath,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
