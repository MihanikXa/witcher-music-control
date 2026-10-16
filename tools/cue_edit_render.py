"""Private source-clock excerpt renders and independently decoded PCM QA.

No Wwise, installation, network, reference executable or soundbank operations.
Regenerate one cue with --only <cue> and a fresh --output under ignored build/.
"""
import argparse
from collections import OrderedDict
from functools import lru_cache
import csv
import html
import json
import os
from pathlib import Path
import re
import subprocess
import wave

import numpy as np

from cue_freeze_dsp import RATE,render_variants
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]
FFMPEG=Path(r'L:\Programs\Shutter Encoder 20.1 Windows 64bits\Library\ffmpeg.exe')
FEEDBACK=REPO/'research/58-user-musical-material-audition-feedback.json'
SOURCES=REPO/'build/music-material-selection/audition-v3'
LABELS={'A':'A · Dry fade','B':'B · Reverb decay + fade','C':'C · Reverb FREEZE + fade (primary trial)'}


def excerpt_role(settings):
    """Read the user's per-excerpt notes without replacing the source role."""
    key=settings['cue']
    if key=='S11-long' or key=='S18-2':return 'Atmospheric development (per excerpt note)'
    if key in ('S07-b','S07-c'):return 'Brief punctuation (per excerpt note)'
    if key.startswith('S16-') or key=='S20-a':return 'Atmospheric development / punctuation (per excerpt note)'
    return settings['source_role']


def decode(path):
    if not FFMPEG.is_file():raise FileNotFoundError('Trusted installed FFmpeg is required; no automatic installation')
    p=subprocess.run([str(FFMPEG),'-hide_banner','-v','error','-nostdin','-i',str(path),
        '-map','0:a:0','-ac','2','-ar',str(RATE),'-f','f32le','pipe:1'],capture_output=True,timeout=120)
    if p.returncode:raise ValueError(p.stderr.decode('utf-8',errors='replace'))
    if len(p.stdout)%8:raise ValueError('Invalid stereo PCM byte count')
    x=np.frombuffer(p.stdout,dtype='<f4').reshape(-1,2).astype(np.float64)
    if not len(x) or not np.isfinite(x).all():raise ValueError('Invalid decoded source')
    return x


def level(x):return float(20*np.log10(max(float(np.sqrt(np.mean(x*x))),1e-12)))


def validate_plan(plan,user):
    if plan['sample_rate']!=RATE or plan['lead_silence']<1 or plan['trail_silence']<2:raise ValueError('Unsupported clocks/context')
    if len({c['cue'] for c in plan['cues']})!=len(plan['cues']):raise ValueError('Duplicate cue')
    for c in plan['cues']:
        u=user[c['source']]
        if u['decision']!='Keep' or (c['source_title'],c['source_role'],c['verbatim_notes'])!=(u['title'],u['role'],u['notes']):
            raise ValueError('Changed or unapproved user selection')
        if c['source']=='S14' and not c['comparison_only']:raise ValueError('Authored reuse lost restriction')
        if not re.fullmatch(r'S\d\d-[a-z0-9-]+',c['cue']):raise ValueError('Unsafe cue filename')
        if c['variants'] not in (['A','B','C'],['C']):raise ValueError('Undeclared variant')
        if not c['assumption'] or not 1<=c['stage']<=3:raise ValueError('Missing edit assumptions')


def write_and_check(path,data,expected_dry,envelope,source,settings,proof,lead,trail,variant):
    if path.exists():raise FileExistsError(path)
    if not np.isfinite(data).all() or np.max(np.abs(data))>.960001:raise ValueError('Unsafe output/headroom')
    pcm=np.rint(data*32767).astype('<i2')
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
    independent=decode(path)
    quantized=pcm.astype(np.float64)/32768
    if independent.shape!=data.shape or np.max(np.abs(independent-quantized))>1e-7:raise ValueError('Independent decoder/readback mismatch')
    nlead,ntrail=round(lead*RATE),round(trail*RATE)
    if np.any(independent[:nlead]) or np.any(independent[-ntrail:]):raise ValueError('Context silence not exact PCM zero')
    a,b=proof['source_start_frame'],proof['source_end_frame']
    expected=source[a:b]*envelope[:,None]
    if not np.array_equal(expected,expected_dry):raise ValueError('Source-clock crop/fade mismatch')
    dry_n=len(expected);first_wet=round(proof['freeze_relative']*RATE)
    compare_n=dry_n if variant=='A' else first_wet
    dry_check=np.rint(expected[:compare_n]*proof['headroom_gain']*32767)/32768
    if not np.array_equal(independent[nlead:nlead+compare_n],dry_check):raise ValueError('Unintended pre-tail source alteration')
    active=independent[nlead:-ntrail]
    if level(active)<-75:raise ValueError('Unexpected inaudible/missing excerpt')
    # The quantized boundary samples must actually be zero, not just have a fade label.
    if np.any(active[0]) or np.any(active[-1]):raise ValueError('Nonzero outer edit boundary')
    start_out=independent[nlead:nlead+min(dry_n,RATE)]
    end_rms=level(active[-min(RATE,len(active)):])
    post_dry=active[dry_n:dry_n+min(RATE,len(active)-dry_n)]
    if variant=='C' and level(post_dry)<-72:raise ValueError('Held field exists numerically but private tail is too weak; review settings')
    cutoff=nlead+dry_n
    seam=float(np.max(np.abs(np.diff(independent[max(0,cutoff-128):cutoff+128],axis=0))))
    if seam>.12:raise ValueError('Excessive sample discontinuity at dry-stop seam')
    tail_window=active[max(0,dry_n):]
    correlation=float(np.corrcoef(tail_window.T)[0,1]) if np.std(tail_window)>1e-9 else None
    peak=float(np.max(np.abs(independent)))
    return dict(passed=True,frames=len(independent),channels=2,rate=RATE,seconds=len(independent)/RATE,
        peak=peak,clipped_samples=int(np.count_nonzero(np.abs(pcm)>=32767)),rms_dbfs=level(active),
        post_dry_first_second_rms_dbfs=level(post_dry),last_active_second_rms_dbfs=end_rms,
        dry_stop_seam_max_sample_delta=seam,tail_stereo_correlation=correlation,
        exact_lead_trail_zero_frames=[nlead,ntrail],source_crop_frame_exact=True,
        pre_tail_source_samples_exact=True,decoder_matches_quantized_pcm=True,sha256=digest(path))


def page(manifest):
    e=lambda x:html.escape(str(x),quote=True)
    cards=[]
    for cue in manifest['cues']:
        s,p=cue['settings'],cue['proof'];ident=s['cue'];variants=cue['renders']
        options=''.join(f'<option value="{k}" {"selected" if k=="C" else ""}>{LABELS[k]}</option>' for k in variants)
        preference_options='<option value="">Undecided</option>'+''.join(f'<option value="{k}">{LABELS[k]}</option>' for k in variants)
        primary=variants['C']['file'];restricted='<strong class="warning">COMPARISON ONLY — verified authored-source reuse.</strong>' if s['comparison_only'] else ''
        end=s['source_out'];fade=s['dry_fade']
        cards.append(f'''<article data-cue="{e(ident)}"><h2>{e(ident)} · {e(s['source_title'])}</h2>{restricted}
<p><b>Source clock:</b> {s['source_in']:.3f}–{end:.3f}s · <b>Dry fade:</b> {fade[0]:.3f}–{fade[1]:.3f}s · Entrance ramp {s['fade_in']:.2f}s.</p>
<p><b>Freeze capture:</b> {p['freeze_source_seconds']:.3f}s source clock. Wet hold through dry stop +{s['hold_after_dry']:.2f}s, then fade to dry stop +{s['tail_extra']:.2f}s. Added tail does not change your source cut.</p>
<p class="small">Reported source: {e(cue.get('source_identity',{}).get('origin_label','See original reference'))}. Playback clock has {manifest['lead_silence']}s of leading silence and {manifest['trail_silence']}s after the complete tail. A/B/C have the same total duration ({p['output_seconds']:.3f}s); A is silent earlier. Source-clock endpoints are not player timestamps.</p>
<select class="variant" aria-label="Ending treatment">{options}</select><button class="play">Play from start</button><button class="ending">Hear ending</button>
<label><input class="position" type="checkbox" checked> Keep position when switching A/B/C</label>
<audio controls preload="none" src="{e(primary)}"></audio>
<p><b>Assumption:</b> {e(s['assumption'])}</p><p class="small">Source role: {e(s['source_role'])}. Excerpt function: {e(excerpt_role(s))}. No subjective musical quality judgment by Codex. Different choices are per-cue provisional tuning, not a final universal preset.</p>
<label>Verdict <select class="verdict"><option>Unreviewed</option><option>Keep</option><option>Adjust</option><option>Reject</option></select></label>
<label>Preferred treatment <select class="preferred">{preference_options}</select></label><p><textarea rows="2" placeholder="Cut correction? Freeze too long/metallic/bright? Better with dry or normal reverb?" aria-label="Listening notes"></textarea></p>
<details><summary>Original feedback / full recording / processing and QA</summary><p>{e(s['verbatim_notes'])}</p>
<audio controls preload="none" src="{e(cue['original_reference'])}"></audio>
<p>Field:16 unequal delays, orthonormal feedback. C closes new excitation at capture and holds state energy; B retains RT60 losses and receives the fading dry send until the dry cut. Input band {s['highpass_hz']}–{s['lowpass_hz']}Hz; {s['prime_seconds']}s prime; {s['wet_attack']}s wet entrance; conventional RT60 {s['rt60']}s. B/C initial wet RMS matched. Common dry/variant headroom gain {p['headroom_db']:.3f}dB; no loudness normalization.</p>
<pre>{e(json.dumps(dict(settings=s,qa={k:v['qa'] for k,v in variants.items()}),indent=2))}</pre></details></article>''')
    refs=''.join(f'<p>{e(r["title"])} — full-source reference only (no new cut)</p><audio controls preload="none" src="{e(r["file"])}"></audio>' for r in manifest['references'])
    data=json.dumps(manifest,ensure_ascii=True).replace('<','\\u003c')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC — Private cue edits / freeze comparison</title>
<style>body{max-width:1000px;margin:30px auto;padding:0 20px;background:#151a1c;color:#ece6da;font:17px/1.5 system-ui}article{padding:22px;border:1px solid #526064;border-radius:12px;margin:26px 0}h1,h2{line-height:1.2}button,select{padding:9px;margin:5px}audio,textarea{width:100%}label{display:inline-block;margin:5px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}.small,details{font-size:14px;color:#c2cecb}.warning{color:#ffd18a}a{color:#a3dbed}#json{height:180px}header{position:sticky;top:0;background:#151a1cf5;padding:10px 0;border-bottom:1px solid #526064;z-index:1}</style>
<h1>Private musical gestures — ending comparisons</h1><p>Start with S04, S05 and S11. C is a genuine held reverb field, B an ordinary decaying field, A a dry fade. Only representative excerpts offer all three. Compare musical resolution, not loudness or extra duration. No final soundtrack, rights or integration decision is implied.</p>
<p>Use a comfortable volume. Full original balance is retained; native base-stem auditions remain base stems. The extra tail extends beyond the labeled dry stop. Actual digital silence surrounds the rendered cue, without moving its source-clock cuts. Your verdict is needed: Codex has not listened subjectively.</p>
<header><button id="stop">Stop all audio</button><button id="export">Export decisions JSON</button><button id="show">Show/copy JSON fallback</button><span id="status"></span></header>
<details id="fallback"><summary>Export fallback</summary><p>If your browser blocks a local download, select and copy this complete JSON. This works without local storage or downloads.</p><textarea id="json" readonly aria-label="Exported decisions JSON"></textarea></details>'''+''.join(cards)+f'<h2>Uncut references</h2>{refs}'+'''
<script id="manifest" type="application/json">'''+data+'''</script>
<script>
const manifest=JSON.parse(document.getElementById('manifest').textContent),cards=[...document.querySelectorAll('article')];
const allAudio=[...document.querySelectorAll('audio')];
function stopAll(except){allAudio.forEach(a=>{if(a!==except)a.pause()})}
allAudio.forEach(a=>a.addEventListener('play',()=>stopAll(a)));
function cueData(card){return manifest.cues.find(c=>c.settings.cue===card.dataset.cue)}
function start(a,t){stopAll(a);const go=()=>{a.currentTime=Math.min(t,Math.max(0,(a.duration||1e6)-.05));a.play().catch(e=>document.querySelector('#status').textContent='Press the audio Play control: '+e.message)};if(a.readyState>=1)go();else{a.addEventListener('loadedmetadata',go,{once:true});a.load()}}
for(const card of cards){const cue=cueData(card),a=card.querySelector('audio'),v=card.querySelector('.variant');
card.querySelector('.play').onclick=()=>start(a,0);
card.querySelector('.ending').onclick=()=>start(a,manifest.lead_silence+Math.max(0,cue.proof.freeze_relative-2));
v.onchange=()=>{const t=card.querySelector('.position').checked?a.currentTime:0,playing=!a.paused;a.pause();a.src=cue.renders[v.value].file;a.addEventListener('loadedmetadata',()=>{if(playing)start(a,t);else a.currentTime=Math.min(t,a.duration)},{once:true});a.load()};
const inputs=[card.querySelector('.verdict'),card.querySelector('.preferred'),card.querySelector('textarea')],key='wmc-cue61-'+manifest.plan_sha256.slice(0,12)+'-'+card.dataset.cue;
try{const x=JSON.parse(localStorage.getItem(key)||'null');if(x)inputs.forEach((el,i)=>el.value=x[i])}catch(e){document.querySelector('#status').textContent='Storage unavailable; use Export.'}
inputs.forEach(x=>x.oninput=()=>{try{localStorage.setItem(key,JSON.stringify(inputs.map(x=>x.value)))}catch(e){document.querySelector('#status').textContent='Use Export to retain notes.'}})}
function gather(){return {schema:1,kind:'private-cue-edit-listening-decisions',plan_sha256:manifest.plan_sha256,feedback_sha256:manifest.feedback_sha256,source_metadata_sha256:manifest.source_metadata_sha256,decisions:cards.map(c=>{const x=cueData(c);return {cue:c.dataset.cue,source:x.settings.source,source_identity:x.source_identity,title:x.settings.source_title,source_role:x.settings.source_role,excerpt_role:x.excerpt_role,source_in:x.settings.source_in,source_out:x.settings.source_out,dry_fade:x.settings.dry_fade,verdict:c.querySelector('.verdict').value,preferred:c.querySelector('.preferred').value,notes:c.querySelector('textarea').value,settings:x.settings,render_hashes:Object.fromEntries(Object.entries(x.renders).map(([k,v])=>[k,v.qa.sha256]))}})}}
function showJSON(){const text=JSON.stringify(gather(),null,2);document.querySelector('#json').value=text;document.querySelector('#fallback').open=true;return text}
document.querySelector('#stop').onclick=()=>stopAll();
document.querySelector('#show').onclick=()=>{showJSON();document.querySelector('#json').select()};
document.querySelector('#export').onclick=()=>{const text=showJSON(),url=URL.createObjectURL(new Blob([text],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='wmc-cue-edit-decisions-'+Date.now()+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)};
</script></html>'''


def build(plan_path,output,max_stage=3,only=None):
    output=build_path(output);plan=json.loads(plan_path.read_text(encoding='utf-8'))
    if digest(FEEDBACK)!=plan['feedback_sha256'] or digest(SOURCES/'auditions.json')!=plan['source_metadata_sha256']:
        raise ValueError('Authoritative user feedback/source metadata changed')
    users={r['id']:r for r in json.loads(FEEDBACK.read_text(encoding='utf-8'))};validate_plan(plan,users)
    sources={r['id']:r for r in json.loads((SOURCES/'auditions.json').read_text(encoding='utf-8'))}
    chosen=[c for c in plan['cues'] if c['stage']<=max_stage and (not only or c['cue'] in only)]
    if only and set(only)-{c['cue'] for c in chosen}:raise ValueError('Unknown cue or stage')
    output.mkdir(exist_ok=True);(output/'audio').mkdir(exist_ok=True);(output/'validation').mkdir(exist_ok=True)
    index=output/'renders.json'
    if index.exists():
        manifest=json.loads(index.read_text(encoding='utf-8'))
        if manifest['plan_sha256']!=digest(plan_path):raise ValueError('Use a fresh output for revised settings; preserve earlier renders')
    else:
        if list((output/'audio').iterdir()):raise ValueError('Undocumented files in output')
        manifest=dict(schema=1,plan_sha256=digest(plan_path),feedback_sha256=plan['feedback_sha256'],
            source_metadata_sha256=plan['source_metadata_sha256'],lead_silence=plan['lead_silence'],trail_silence=plan['trail_silence'],
            ffmpeg_sha256=digest(FFMPEG),private_audition_only=True,subjectively_listened=False,cues=[],references=[])
    @lru_cache(maxsize=1)
    def load(ident):
        row=sources[ident];path=(SOURCES/row['preview']).resolve()
        if not path.is_relative_to(SOURCES) or digest(path)!=row['preview_sha256']:raise ValueError('Source preview mismatch')
        return decode(path)
    for original in chosen:
        if any(x['settings']['cue']==original['cue'] for x in manifest['cues']):
            prior=next(x for x in manifest['cues'] if x['settings']['cue']==original['cue'])
            if any(digest(output/r['file'])!=r['qa']['sha256'] for r in prior['renders'].values()):raise ValueError('Previous render changed')
            continue
        settings=dict(original);source=load(settings['source'])
        end=len(source)/RATE if settings['source_out'] is None else settings['source_out'];settings['source_out']=end
        if settings['dry_fade'] is None:settings['dry_fade']=[end-plan['fallback_fades'][settings['cue']],end]
        arrays,proof,dry,envelope=render_variants(source,settings,plan['lead_silence'],plan['trail_silence'])
        renders={}
        for variant,data in arrays.items():
            path=output/'audio'/(settings['cue']+'-'+variant+'.wav')
            qa=write_and_check(path,data,dry,envelope,source,settings,proof,plan['lead_silence'],plan['trail_silence'],variant)
            renders[variant]=dict(label=LABELS[variant],file='audio/'+path.name,qa=qa)
        original_path=(SOURCES/sources[settings['source']]['preview']).resolve()
        if digest(original_path)!=sources[settings['source']]['preview_sha256']:raise ValueError('Source changed during rendering')
        cue=dict(settings=settings,proof=proof,renders=renders,original_reference=Path(os.path.relpath(original_path,output)).as_posix(),
                 source_preview_sha256=sources[settings['source']]['preview_sha256'])
        manifest['cues'].append(cue)
        index.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(cue=settings['cue'],variants=list(renders),seconds=proof['output_seconds'],headroom_db=proof['headroom_db'])),flush=True)
    manifest['references']=[dict(source=i,title=users[i]['title'],file=Path(os.path.relpath(SOURCES/sources[i]['preview'],output)).as_posix()) for i in plan['reference_only']]
    for c in manifest['cues']:
        c['excerpt_role']=excerpt_role(c['settings'])
        original=sources[c['settings']['source']]['identity']
        c['source_identity']={k:original[k] for k in ('media','bank','segment','track','tracks','original') if k in original}
        c['source_identity']['origin_label']=original.get('source','The Witcher 3 native audition source')
    index.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (output/'index.html').write_text(page(manifest),encoding='utf-8')
    with (output/'renders.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['cue','variant','source_in','source_out','dry_fade','extra_tail','duration','file'])
        for c in manifest['cues']:
            for v,r in c['renders'].items():w.writerow([c['settings']['cue'],v,c['settings']['source_in'],c['settings']['source_out'],c['settings']['dry_fade'],c['settings']['tail_extra'],r['qa']['seconds'],r['file']])
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{r['qa']['seconds']},{c['settings']['cue']} {v}\n{r['file']}\n" for c in manifest['cues'] for v,r in c['renders'].items()),encoding='utf-8')
    stagefile=output/'validation'/f'stage{max_stage}-proof.json'
    if not stagefile.exists():stagefile.write_text(json.dumps(dict(cues=len(manifest['cues']),renders=sum(len(c['renders']) for c in manifest['cues']),
        index_sha256=digest(output/'index.html'),metadata_sha256=digest(index),all_render_qa_passed=True),indent=2)+'\n')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-stage',type=int,choices=(1,2,3),default=3);p.add_argument('--only',nargs='+')
    a=p.parse_args();build(a.plan,a.output,a.max_stage,a.only)
