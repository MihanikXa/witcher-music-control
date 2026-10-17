/* Offline generated-client logic test. No browser, network or audio playback.
 * A tiny fake DOM exercises our own handlers, including storage failure.
 * This explicitly does NOT claim file:// or browser download verification. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const input=process.argv[2];if(!input)throw Error('Provide generated private index.html');
const html=fs.readFileSync(input,'utf8');
const manifest=JSON.parse(html.match(/<script id="manifest" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
const allAudio=[],downloads=[],blobs=new Map();let counter=0;
class Element {
 constructor(){this.value='';this.checked=true;this.handlers={};this.paused=true;this.readyState=1;this.currentTime=0;this.duration=1000;this.textContent=''}
 addEventListener(name,fn){this.handlers[name]=fn}
 pause(){this.paused=true}
 play(){this.paused=false;this.handlers.play?.();return Promise.resolve()}
 load(){this.handlers.loadedmetadata?.()}
 select(){this.selected=true}
 click(){downloads.push({name:this.download,href:this.href})}
}
const cards=manifest.cues.map(c=>{
 const selectors={};for(const s of ['audio','.variant','.play','.ending','.position','.verdict','.preferred','textarea','.seamless','.resolution','.tail','.artifact'])selectors[s]=new Element();
 const primary=manifest.primary_variant||'C';
 selectors.audio.src=c.renders[primary].file;selectors.audio.duration=c.proof.output_seconds;
 selectors['.variant'].value=primary;selectors['.preferred'].value='';selectors['.verdict'].value='Unreviewed';
 allAudio.push(selectors.audio,new Element());return {dataset:{cue:c.settings.cue},querySelector:s=>selectors[s]}
});
const ids={};for(const key of ['#json','#fallback','#status','#stop','#show','#export'])ids[key]=new Element();
const document={querySelectorAll:s=>s==='article'?cards:s==='audio'?allAudio:[],querySelector:s=>ids[s],
 getElementById:id=>id==='manifest'?{textContent:JSON.stringify(manifest)}:null,createElement:()=>new Element()};
const context={document,localStorage:{getItem(){throw Error('storage deliberately disabled')},setItem(){throw Error('storage deliberately disabled')}},
 Blob,URL:{createObjectURL(b){const id='blob:offline-test-'+counter++;blobs.set(id,b);return id},revokeObjectURL(){}},setTimeout(){},Date,console};
vm.createContext(context);vm.runInContext(script,context);
if(manifest.primary_variant==='B'){
 assert.equal((html.match(/<option value="B" selected>/g)||[]).length,manifest.cues.length);
 for(const c of manifest.cues)assert.ok(html.includes('src="'+c.renders.B.file+'"'));
}
const card=cards[0],audio=card.querySelector('audio');card.querySelector('.play').onclick();assert.equal(audio.paused,false);
if(cards.length>1){cards[1].querySelector('.play').onclick();assert.equal(audio.paused,true)}
card.querySelector('.ending').onclick();assert.ok(audio.currentTime>=manifest.lead_silence);
card.querySelector('.verdict').value='Adjust';card.querySelector('textarea').value='Offline test — shorter freeze, keep the source cut.';
if(manifest.kind==='preregistered-treatment-trial'){
 card.querySelector('.seamless').value='No';card.querySelector('.resolution').value='Uncertain';
 card.querySelector('.tail').value='Too intrusive';card.querySelector('.artifact').value='Heard one — see notes';
}
card.querySelector('textarea').oninput();
if(manifest.cues[0].renders.B){card.querySelector('.variant').value='B';card.querySelector('.variant').onchange();assert.equal(audio.src,manifest.cues[0].renders.B.file);assert.equal(card.querySelector('.preferred').value,'');card.querySelector('.preferred').value='B'}
ids['#show'].onclick();const result=JSON.parse(ids['#json'].value);
assert.equal(result.decisions.length,manifest.cues.length);assert.equal(result.decisions[0].verdict,'Adjust');
assert.equal(result.decisions[0].source_in,manifest.cues[0].settings.source_in);
assert.equal(result.decisions[0].source_out,manifest.cues[0].settings.source_out);
assert.equal(result.decisions[0].settings.verbatim_notes,manifest.cues[0].settings.verbatim_notes);
assert.ok(result.decisions[0].notes.includes('Offline test'));assert.equal(ids['#fallback'].open,true);
if(manifest.kind==='preregistered-treatment-trial'){
 assert.equal(result.kind,'preregistered-treatment-trial-outcomes');
 assert.equal(result.prediction_registration.commit,manifest.registration.commit);
 assert.deepEqual(result.decisions[0].frozen_prediction,manifest.cues[0].prediction);
 assert.equal(result.decisions[0].evaluation.seamless,'No');
 assert.equal(result.decisions[0].evaluation.tail,'Too intrusive');
 assert.equal(manifest.cues[0].prediction.confidence,result.decisions[0].frozen_prediction.confidence);
 result.decisions.forEach((d,i)=>assert.deepEqual(d.frozen_prediction,manifest.cues[i].prediction));
}
if(manifest.kind==='remainder-batch-private-audition'){
 assert.equal(result.kind,'remainder-batch-private-outcomes');
 assert.equal(result.ordinary_decisions.length,10);assert.equal(result.restricted_comparisons.length,2);
 assert.equal(result.decisions[0].current_treatment_reasoning,manifest.cues[0].reasoning);
 assert.equal(result.decisions[0].timing_authority,manifest.cues[0].timing_authority);
 assert.ok(!result.decisions.some(d=>d.cue==='S18-3'));
 assert.equal(manifest.cues.filter(c=>c.renders.C).length,3);
 assert.deepEqual(result.restricted_comparisons.map(d=>d.cue),['S14-1','S14-2']);
 const restricted=cards.find(c=>c.dataset.cue==='S14-1');restricted.querySelector('.verdict').value='Keep';
 const again=context.gather();const kept=again.restricted_comparisons.find(d=>d.cue==='S14-1');
 assert.equal(kept.verdict,'Keep');assert.equal(kept.comparison_only,true);
 assert.ok(kept.allowed_use.includes('private comparison only'));
 assert.ok(!again.ordinary_decisions.some(d=>d.cue.startsWith('S14')));
}
ids['#export'].onclick();assert.equal(downloads.length,1);assert.ok(downloads[0].name.startsWith('wmc-cue-edit-decisions-'));
assert.ok(blobs.has(downloads[0].href));ids['#stop'].onclick();assert.ok(allAudio.every(a=>a.paused));
blobs.get(downloads[0].href).text().then(text=>{assert.equal(JSON.parse(text).decisions.length,manifest.cues.length);
 console.log(JSON.stringify({passed:true,cues:cards.length,storage_disabled_tested:true,export_blob_and_fallback_valid:true,
  switching_and_stop_handlers_tested:true,real_browser_tested:false,real_audio_playback_tested:false}))});
