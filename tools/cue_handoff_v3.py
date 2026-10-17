"""Two unresolved private cues only: measured dry/room-balance comparisons."""
import argparse
import html
import json
import os
from pathlib import Path
import re

import numpy as np

from cue_edit_render import decode,page as legacy_page
from cue_freeze_dsp import RATE,render_continuous,envelope_windows
from cue_tail_v2 import write_pcm
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]
V2=REPO/'build/music-material-selection/cue-edits-v2'
PLAN=REPO/'research/66-handoff-balance-plan.json'


def handoff_metrics(audio,begin,end):
    """Fixed-clock windows across the handoff; no claim of perceived naturalness."""
    rms=envelope_windows(audio[round(begin*RATE):round(end*RATE)],.25)
    db=20*np.log10(np.maximum(rms,1e-12))
    return dict(window_seconds=.25,player_start=begin,player_end=end,rms_dbfs=db.tolist(),
                largest_adjacent_drop_db=float(max(0,-np.min(np.diff(db)))),
                largest_adjacent_rise_db=float(max(0,np.max(np.diff(db)))))


def page(m):
    e=lambda x:html.escape(str(x),quote=True);cards=[]
    for c in m['cues']:
        s=c['settings'];options=''.join(f'<option value="{k}" {"selected" if k=="B" else ""}>{e(v["label"])}</option>' for k,v in c['renders'].items())
        prefs='<option value="">Undecided</option>'+''.join(f'<option value="{k}">{e(v["label"])}</option>' for k,v in c['renders'].items())
        cards.append(f'''<article data-cue="{e(s['cue'])}"><h2>{e(s['source_title'])} · {e(s['cue'])}</h2>
<p>Unchanged source cut {s['source_in']:.3f}–{s['source_out']:.3f}s. Every excerpt has2s leading and3s final silence. <b>{e(c['comparison_note'])}</b></p>
<select class="variant">{options}</select><button class="play">Play from start</button><button class="ending">Hear handoff</button>
<label><input type="checkbox" class="position" checked>Keep player position when switching</label><audio controls preload="none" src="{e(c['renders']['B']['file'])}"></audio>
<p>Verdict <select class="verdict"><option>Unreviewed</option><option>Keep</option><option>Adjust</option><option>Reject</option></select>
Preferred treatment <select class="preferred">{prefs}</select></p><textarea rows="3" placeholder="Does the music still disappear too quickly into a separate tail? Give player time and variant."></textarea>
<details><summary>Original source, exact processing and measurements</summary><p>{e(s['verbatim_notes'])}</p>
<p>The full source below has its original clock and no extra leading context.</p><audio controls preload="none" src="{e(c['original_reference'])}"></audio>
<p>New natural-reverb versions share the same established wet gain and unchanged RT60/filter topology. No new freeze variant: the unresolved report65 defect is before v2 B/C diverge. Stronger wet balance is present throughout the excerpt, not turned up at the cut. No normalization, compensating gain or late output ramp.</p>
<pre>{e(json.dumps(dict(settings=s,variants=c['renders'],metrics=c['metrics']),indent=2))}</pre></details></article>''')
    old=legacy_page(dict(cues=[],references=[],lead_silence=2,trail_silence=3))
    client=old[old.rfind('<script>'):].replace('wmc-cue61-','wmc-cue66-').replace("kind:'private-cue-edit-listening-decisions'","kind:'private-cue-handoff-v3-decisions'")
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC — two unresolved handoffs v3</title>
<style>body{max-width:1000px;margin:24px auto;padding:0 18px;background:#151a1c;color:#e6e5df;font:17px/1.5 system-ui}article{border:1px solid #627371;border-radius:10px;padding:22px;margin:24px 0}audio,textarea{width:100%}button,select{padding:9px;margin:5px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}header{position:sticky;top:0;background:#151a1cf5;padding:10px}#json{height:180px}</style>
<h1>Two unresolved handoffs — v3</h1><p>Compare A (unchanged rejected v2 natural decay) with B (new primary), then C (controlled alternative). <b>Both new B and C use conventional reverb; C is not a freeze version in this comparison.</b> Dry-only is a diagnostic, not a new preferred style. The three report65 accepted versions are untouched. No change is declared musically successful until you listen.</p>
<p>Listen for an overly quick loss of direct music, separate distant tail, excessive room wash or changed harmonic emphasis. If an ending is still wrong, record the variant and <b>player time</b>. Source cuts remain fixed.</p>
<header><button id="stop">Stop all</button><button id="export">Export decisions JSON</button><button id="show">Show/copy JSON</button><span id="status"></span></header>
<details id="fallback"><summary>Copy export fallback</summary><textarea id="json" readonly></textarea></details>'''+''.join(cards)+'<script id="manifest" type="application/json">'+json.dumps(m).replace('<','\\u003c')+'</script>'+client


def build(output):
    output=build_path(output)
    if output.exists():raise FileExistsError('Fresh output required; never overwrite accepted audio')
    plan=json.loads(PLAN.read_text());old=json.loads((V2/'renders.json').read_text())
    for path,h in plan['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Input changed: '+path)
    output.mkdir();(output/'audio').mkdir()
    m=dict(schema=3,plan_sha256=digest(PLAN),feedback_sha256=old['feedback_sha256'],source_metadata_sha256=old['source_metadata_sha256'],
        lead_silence=2,trail_silence=3,primary_variant='B',cues=[],references=[],subjectively_listened=False,browser_playback_verified=False)
    for cfg in plan['cues']:
        prior=next(c for c in old['cues'] if c['settings']['cue']==cfg['cue']);base=dict(prior['settings'])
        srcpath=(V2/prior['original_reference']).resolve()
        if digest(srcpath)!=prior['source_preview_sha256']:raise ValueError('Source changed')
        source=decode(srcpath);renders={};proofs={};metrics={};arrays={}
        # Calibrate once using the original pre-fade clock. Shared exact gain lets
        # the comparisons isolate send policy or dry fade, rather than tail normalization.
        ref_settings={**base,'continuous_wet_db':cfg['wet_db'],'send_policy':'pre_ending_fade'}
        _,cal,_=render_continuous(source,ref_settings,base['natural_rt60'])
        gain=cal['wet_gain']
        for name in ('B','C'):
            spec=cfg['variants'][name];s={**base,'continuous_wet_db':cfg['wet_db'],'send_policy':spec['send_policy'],
                                      'dry_fade':spec['dry_fade']}
            x,p,components=render_continuous(source,s,base['natural_rt60'],wet_gain=gain)
            a,b=round(base['source_in']*RATE),round(base['source_out']*RATE)
            if not np.array_equal(components['dry'][:b-a],source[a:b]*components['source_envelope'][:,None]):raise ValueError('Source clock mismatch')
            qa=write_pcm(output/'audio'/f'{cfg["cue"]}-{name}.wav',x)
            renders[name]=dict(file=f'audio/{cfg["cue"]}-{name}.wav',label=spec['label'],qa=qa,
                               dry_fade=s['dry_fade'],send_policy=s['send_policy'],rt60=p['rt60'],wet_db_target=cfg['wet_db'])
            arrays[name]=x;proofs[name]=p
            metrics[name]=handoff_metrics(x,*cfg['measurement_player_range'])
            if name=='B':
                dry=np.pad(components['dry'],((2*RATE,3*RATE),(0,0)))
                qa=write_pcm(output/'audio'/f'{cfg["cue"]}-Dry.wav',dry)
                dryrender=dict(file=f'audio/{cfg["cue"]}-Dry.wav',label='Dry-only diagnostic — new B dry fade, no added reverb',qa=qa,dry_fade=s['dry_fade'])
        same_until=round(cfg['same_until_player']*RATE)
        if not np.array_equal(arrays['B'][:same_until],arrays['C'][:same_until]):raise ValueError('Uncontrolled pre-comparison audio difference')
        ref=prior['renders']['B'];refpath=V2/ref['file']
        if digest(refpath)!=ref['qa']['sha256']:raise ValueError('Rejected reference changed')
        metrics['A']=handoff_metrics(decode(refpath),*cfg['measurement_player_range'])
        renders={'A':dict(file=Path(os.path.relpath(refpath,output)).as_posix(),label='A — unchanged v2 B, rejected handoff reference',qa=ref['qa']),
                 **renders,'Dry':dryrender}
        primary={**proofs['B'],'freeze_relative':cfg['ending_button_relative']}
        s={**base,'v3_comparison':cfg,'dry_fade':cfg['variants']['B']['dry_fade'],
           'continuous_wet_db':cfg['wet_db'],'send_policy':cfg['variants']['B']['send_policy'],
           'original_v2_dry_fade':base['dry_fade'],'v2_assumption':base['assumption'],
           'assumption':cfg['note']+' Both new treatments are natural decay; no new freeze capture.'}
        c=dict(settings=s,proof=primary,proofs=proofs,renders=renders,metrics=metrics,
            original_reference=Path(os.path.relpath(srcpath,output)).as_posix(),source_identity=prior['source_identity'],
            source_preview_sha256=prior['source_preview_sha256'],excerpt_role=prior['excerpt_role'],comparison_note=cfg['note'])
        m['cues'].append(c)
        print(json.dumps(dict(cue=cfg['cue'],metrics=metrics)),flush=True)
    (output/'renders.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
    (output/'index.html').write_text(page(m),encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f'#EXTINF:{r["qa"]["seconds"]},{c["settings"]["cue"]} {r["label"]}\n{r["file"]}\n' for c in m['cues'] for r in c['renders'].values()),encoding='utf-8')
    for c in m['cues']:
        for r in c['renders'].values():
            if digest(output/r['file'])!=r['qa']['sha256']:raise ValueError('Output hash mismatch')
    links=re.findall(r'(?:src|href)="([^"]+)"',(output/'index.html').read_text(encoding='utf-8'))
    if any(not (output/p).is_file() for p in links):raise ValueError('Broken local reference')
    return m


def verify(folder):
    """Read-back gate over all rendered PCM and all retained v1/v2 fingerprints."""
    folder=build_path(folder);m=json.loads((folder/'renders.json').read_text());plan=json.loads(PLAN.read_text())
    if m['plan_sha256']!=digest(PLAN):raise ValueError('Plan fingerprint changed')
    for name,h in plan['immutable_inputs'].items():
        if digest(REPO/name)!=h:raise ValueError('Preserved input changed: '+name)
    if [c['settings']['cue'] for c in m['cues']]!=['S05-short','S11-short']:raise ValueError('Unexpected cue scope')
    rows=[]
    for c,cfg in zip(m['cues'],plan['cues']):
        ref=next(v for v in json.loads((V2/'renders.json').read_text())['cues'] if v['settings']['cue']==cfg['cue'])
        for key in ['source_in','source_out','verbatim_notes']:
            if c['settings'][key]!=ref['settings'][key]:raise ValueError('User source cut/wording changed')
        if c['source_preview_sha256']!=digest(folder/c['original_reference']):raise ValueError('Source changed')
        arrays={}
        for name,r in c['renders'].items():
            path=folder/r['file']
            if digest(path)!=r['qa']['sha256']:raise ValueError('Render hash mismatch')
            x=decode(path);arrays[name]=x
            if len(x)!=round(r['qa']['seconds']*RATE):raise ValueError('Wrong duration')
            if np.any(x[:2*RATE]) or np.any(x[-3*RATE:]):raise ValueError('Context silence')
            if not np.isfinite(x).all() or np.max(np.abs(x))>=.97:raise ValueError('Unsafe PCM')
            if name in ('B','C'):
                p=c['proofs'][name]
                expected=np.array(p['windows_50ms']['combined'])*32767/32768
                actual=envelope_windows(x[2*RATE:-3*RATE])
                if len(expected)!=len(actual) or np.max(abs(expected-actual))>1.6e-5:raise ValueError('Envelope proof does not match readback')
                if r['dry_fade']!=cfg['variants'][name]['dry_fade'] or r['send_policy']!=cfg['variants'][name]['send_policy']:raise ValueError('Wrong treatment')
                if p['cleanup_peak_dbfs']>=-100 or p['dry_stop_max_sample_delta']>.02:raise ValueError('Premature cleanup/seam')
                if p['release_diagnostics']['rebound_review'] or p['release_diagnostics']['plateau_window_starts']:raise ValueError('Post-source geometry requires review')
                if p['freeze']:raise ValueError('Unrequested freeze variant')
                if p['wet_gain']!=c['proofs']['B']['wet_gain']:raise ValueError('Comparison changes room level')
                if r['rt60']!=ref['settings']['natural_rt60']:raise ValueError('Uncontrolled RT60 change')
            measured=handoff_metrics(x,*cfg['measurement_player_range'])
            if name in c['metrics'] and abs(measured['largest_adjacent_drop_db']-c['metrics'][name]['largest_adjacent_drop_db'])>.1:raise ValueError('Metric readback disagreement')
        n=round(cfg['same_until_player']*RATE)
        if not np.array_equal(arrays['B'][:n],arrays['C'][:n]):raise ValueError('Pre-comparison level mismatch')
        rows.append(dict(cue=cfg['cue'],metrics={k:handoff_metrics(x,*cfg['measurement_player_range']) for k,x in arrays.items()},
                         renders={k:r['qa'] for k,r in c['renders'].items()},
                         original_source_cut=[c['settings']['source_in'],c['settings']['source_out']],
                         primary_dry_fade=c['settings']['dry_fade'],controls_share_fixed_gain=True,
                         dry_stop_seam_max_delta=max(p['dry_stop_max_sample_delta'] for p in c['proofs'].values()),
                         cleanup_peak_max_dbfs=max(p['cleanup_peak_dbfs'] for p in c['proofs'].values())))
    links=re.findall(r'(?:src|href)="([^"]+)"',(folder/'index.html').read_text(encoding='utf-8'))
    if any('://' in p or not (folder/p).is_file() for p in links):raise ValueError('External or missing local link')
    return dict(passed=True,private_only=True,cues=2,new_renders=6,new_wet_renders=4,dry_controls=2,
                preserved_inputs=len(plan['immutable_inputs']),rows=rows,
                index_sha256=digest(folder/'index.html'),metadata_sha256=digest(folder/'renders.json'),
                subjectively_listened=False,real_browser_tested=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    if a.verify:
        print(json.dumps(verify(a.output),indent=2))
    else:build(a.output)
