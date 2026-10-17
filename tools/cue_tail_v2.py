"""Five-cue private corrective comparison. Never rewrites v1 or source recordings."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import wave

import numpy as np

from cue_freeze_dsp import RATE, render_continuous, envelope_windows, release_diagnostics
from cue_edit_render import REPO, SOURCES, decode, page as legacy_page
from white_orchard_prepare import build_path, digest

V1=REPO/'build/music-material-selection/cue-edits-v1'
PLAN=REPO/'research/64-continuous-tail-plan.json'
LEGACY_DSP_KEYS=('tail_extra','wet_db_relative','prime_seconds','hold_after_dry','wet_attack',
                 'rt60','freeze_transition','freeze_at','compare','variants')


def page(m):
    e=lambda x:html.escape(str(x),quote=True)
    cards=[]
    for c in m['cues']:
        s=c['settings'];p=c['proof']
        options=''.join(f'<option value="{v}" {"selected" if v=="B" else ""}>{e(r["label"])}</option>' for v,r in c['renders'].items())
        prefs='<option value="">Undecided</option>'+''.join(f'<option value="{v}">{e(r["label"])}</option>' for v,r in c['renders'].items())
        cards.append(f'''<article data-cue="{e(s['cue'])}"><h2>{e(s['cue'])} · {e(s['source_title'])}</h2>
<p>Original source clock {s['source_in']:.3f}–{s['source_out']:.3f}s; dry fade {s['dry_fade'][0]:.3f}–{s['dry_fade'][1]:.3f}s. {e(s['onset_note'])}</p>
<p>2s leading silence; 3s final silence. B is the primary audition, not an approved musical result. A references the exact v1 file; durations differ. Switching keeps the same source-relative player clock.</p>
<select class="variant">{options}</select><button class="play">Play from start</button><button class="ending">Hear ending</button>
<label><input type="checkbox" class="position" checked>Keep position when switching</label>
<audio controls preload="none" src="{e(c['renders']['B']['file'])}"></audio>
<p>Verdict <select class="verdict"><option>Unreviewed</option><option>Keep</option><option>Adjust</option><option>Reject</option></select>
Preferred treatment <select class="preferred">{prefs}</select></p><textarea rows="3" placeholder="Dip/rebound? Tail too wet/long? Onset or harmonic problem?"></textarea>
<details><summary>Exact processing / original source / measured envelopes</summary>
<p>{e(s['verbatim_notes'])}</p><audio controls preload="none" src="{e(c['original_reference'])}"></audio>
<p>B: continuous post-fader reverb, RT60 {p['rt60']}s; no hold or imposed end fade except a sub−100dBFS safety cleanup. C: same established field, closed input at dry stop, 150ms internal freeze transition and immediate continuous exponential release. No pre-cut harmony hold.</p>
<p>V2 gain is calibrated once on pre-fade music and fixed for B/C; all dry levels unchanged. Longer B is independently calibrated to the same pre-fade wet/dry RMS, not a louder tail target. A stays untouched; perceived tail loudness is intentionally not normalized.</p>
<a href="envelopes/{e(s['cue'])}.svg">50ms dry/wet/sum envelopes</a>
<pre>{e(json.dumps({k:v for k,v in c.items() if k not in ('proof',)},indent=2))}</pre></details></article>''')
    data=json.dumps(m).replace('<','\\u003c')
    # Reuse already tested storage-optional, play-one-at-a-time and JSON client.
    old=legacy_page(dict(cues=[],references=[],lead_silence=2,trail_silence=3))
    client=old[old.rfind('<script>'):].replace('wmc-cue61-','wmc-cue64-').replace("kind:'private-cue-edit-listening-decisions'","kind:'private-cue-tail-v2-decisions'")
    refs=''.join(f'<p>{e(r["title"])}</p><audio controls preload="none" src="{e(r["file"])}"></audio>' for r in m['references'])
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC private tail corrections v2</title>
<style>body{max-width:1000px;margin:25px auto;padding:0 18px;background:#151a1c;color:#e6e5df;font:17px/1.5 system-ui}article{border:1px solid #627371;padding:22px;margin:24px 0;border-radius:10px}audio,textarea{width:100%}select,button{padding:9px;margin:5px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}a{color:#9bd8ee}header{position:sticky;top:0;background:#151a1cf5;padding:10px}#json{height:200px}</style>
<h1>Continuous tails — five corrective auditions</h1><p>Start with S05-short → S11-short → S12-1 → S07-b → S04-b. Compare A (unchanged v1), B (primary natural decay), C (optional freeze). S11 and S07 also offer a longer B. Listen through the whole tail: no late wet entrance, rebound, hold or second obvious fade should emerge. Musical quality requires your ears; numerical checks are not approval.</p>
<header><button id="stop">Stop all</button><button id="export">Export decisions JSON</button><button id="show">Show/copy JSON</button><span id="status"></span></header>
<details id="fallback"><summary>Copy export fallback</summary><textarea id="json" readonly></textarea></details>'''+''.join(cards)+'<h2>Previously accepted comparison</h2>'+refs+'<script id="manifest" type="application/json">'+data+'</script>'+client


def svg(cue,proofs):
    colors={'dry':'#a9b5bd','wet':'#f5b875','combined':'#8ee4bf'}
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650" viewBox="0 0 1100 650"><rect width="1100" height="650" fill="#151a1c"/>']
    for row,(name,p) in enumerate(proofs.items()):
        top=35+row*200;duration=p['output_seconds']-5
        parts.append(f'<text x="45" y="{top}" fill="white">{cue} {name}: gray dry / orange wet / green combined; dBFS RMS, 50ms</text>')
        stop=p['dry_stop_relative'];x=60+stop/duration*1000
        parts.append(f'<path d="M{x},{top+10} v150" stroke="white" stroke-dasharray="4 4"/>')
        for k,values in p['windows_50ms'].items():
            db=20*np.log10(np.maximum(values,1e-6));pts=' '.join(f'{60+i*.05/duration*1000:.1f},{top+15+(-max(-100,min(0,v)))*1.35:.1f}' for i,v in enumerate(db))
            parts.append(f'<polyline points="{pts}" fill="none" stroke="{colors[k]}" stroke-width="1"/>')
    return ''.join(parts)+'</svg>'


def write_pcm(path,x):
    if path.exists():raise FileExistsError(path)
    pcm=np.rint(x*32767).astype('<i2')
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
    read=decode(path)
    if not np.array_equal(read,pcm.astype(float)/32768):raise ValueError('Independent PCM decode mismatch')
    if np.any(read[:2*RATE]) or np.any(read[-3*RATE:]):raise ValueError('Context silence changed')
    if np.max(np.abs(read))>=.97:raise ValueError('Clipping/headroom')
    return dict(sha256=digest(path),seconds=len(read)/RATE,channels=2,rate=RATE,
                peak=float(np.max(np.abs(read))),clipped_samples=int(np.count_nonzero(np.abs(pcm)>=32767)),decoder_exact=True)


def build(output,only=None):
    output=build_path(output)
    if output.exists():raise FileExistsError('Use fresh output; preserve all earlier evidence')
    plan=json.loads(PLAN.read_text());old=json.loads((V1/'renders.json').read_text())
    if digest(V1/'renders.json')!=plan['v1_metadata_sha256']:raise ValueError('v1 changed')
    for name,h in plan['immutable_inputs'].items():
        if digest(REPO/name)!=h:raise ValueError('Authoritative feedback changed')
    output.mkdir();(output/'audio').mkdir();(output/'envelopes').mkdir()
    m=dict(schema=2,plan_sha256=digest(PLAN),feedback_sha256=old['feedback_sha256'],
        source_metadata_sha256=old['source_metadata_sha256'],lead_silence=2,trail_silence=3,
        subjectively_listened=False,browser_playback_verified=False,primary_variant='B',cues=[],references=[])
    for config in plan['cues']:
        key=config['cue']
        if only and key not in only:continue
        prior=next(c for c in old['cues'] if c['settings']['cue']==key)
        settings=dict(prior['settings']);settings.update(config)
        for k in LEGACY_DSP_KEYS:settings.pop(k,None)
        source_path=(V1/prior['original_reference']).resolve()
        if digest(source_path)!=prior['source_preview_sha256']:raise ValueError('Source mismatch')
        source=decode(source_path);renders={};proofs={}
        for name,mode,rt in [('B',False,settings['natural_rt60']),('C',True,settings['natural_rt60'])]+([('B-long',False,settings['longer_rt60'])] if settings.get('longer_rt60') else []):
            x,p,components=render_continuous(source,settings,rt,freeze=mode,
                wet_gain=proofs['B']['wet_gain'] if mode else None)
            # Exact source clock/envelope reconstruction independent of render crop.
            a,b=round(settings['source_in']*RATE),round(settings['source_out']*RATE)
            expected=source[a:b]*components['source_envelope'][:,None]
            if not np.array_equal(expected,components['dry'][:b-a]):raise ValueError('Dry crop changed')
            if np.any(components['dry'][b-a:]):raise ValueError('Unexpected dry continuation')
            if settings.get('onset_mute_seconds') and np.any(x[2*RATE:round((2+settings['onset_mute_seconds'])*RATE)]):raise ValueError('Onset bleep not isolated')
            qa=write_pcm(output/'audio'/f'{key}-{name}.wav',x)
            label={'B':f'B — v2 natural decay (primary), RT60 {rt}s','C':f'C — v2 freeze / immediate release {rt}s','B-long':f'B-long — v2 longer natural decay, RT60 {rt}s'}[name]
            renders[name]=dict(file=f'audio/{key}-{name}.wav',label=label,qa=qa)
            proofs[name]=p
        ref=prior['renders']['C'];refpath=V1/ref['file']
        if digest(refpath)!=ref['qa']['sha256']:raise ValueError('v1 reference changed')
        renders={'A':dict(file=Path(os.path.relpath(refpath,output)).as_posix(),label='A — unchanged v1 freeze reference',qa=ref['qa']),**renders}
        if key=='S07-b':
            r=prior['renders']['B'];path=V1/r['file']
            if digest(path)!=r['qa']['sha256']:raise ValueError('Accepted reference changed')
            renders['A-decay']=dict(file=Path(os.path.relpath(path,output)).as_posix(),label='Accepted v1 conventional B reference',qa=r['qa'])
        # Client ending button uses original fade start minus 2s, all clocks still aligned.
        primary=dict(proofs['B']);primary['freeze_relative']=settings['dry_fade'][0]-settings['source_in']
        c=dict(settings=settings,source_identity=prior['source_identity'],excerpt_role=prior['excerpt_role'],
               original_reference=Path(os.path.relpath(source_path,output)).as_posix(),
               source_preview_sha256=digest(source_path),proof=primary,proofs=proofs,renders=renders)
        m['cues'].append(c)
        (output/'envelopes'/f'{key}.svg').write_text(svg(key,proofs),encoding='utf-8')
        (output/'renders.json').write_text(json.dumps(m,indent=2)+'\n')
        print(json.dumps(dict(cue=key,variants=list(renders),metrics={n:{k:p[k] for k in ['rt60','wet_gain','cleanup_peak_dbfs','post_stop_first_second_dbfs','dry_stop_max_sample_delta']} for n,p in proofs.items()})),flush=True)
    accepted=next(c for c in old['cues'] if c['settings']['cue']=='S05-main')['renders']['B']
    if digest(V1/accepted['file'])!=accepted['qa']['sha256']:raise ValueError('Accepted S05-main changed')
    m['references']=[dict(title='S05-main — previously accepted v1 conventional B, unchanged',file=Path(os.path.relpath(V1/accepted['file'],output)).as_posix(),sha256=accepted['qa']['sha256'])]
    (output/'renders.json').write_text(json.dumps(m,indent=2)+'\n')
    (output/'index.html').write_text(page(m),encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f'#EXTINF:{r["qa"]["seconds"]},{c["settings"]["cue"]} {r["label"]}\n{r["file"]}\n' for c in m['cues'] for r in c['renders'].values()),encoding='utf-8')
    for c in m['cues']:
        for r in c['renders'].values():
            if digest(output/r['file'])!=r['qa']['sha256']:raise ValueError('Final payload mismatch')
    links=re.findall(r'(?:src|href)="([^"]+)"',(output/'index.html').read_text(encoding='utf-8'))
    if any(not (output/p).is_file() for p in links):raise ValueError('Missing local link')
    return m


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--only',nargs='+')
    args=p.parse_args();build(args.output,args.only)
