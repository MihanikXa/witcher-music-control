"""S18-3-only private correction: change send routing, preserve all musical clocks."""
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
TRIAL=REPO/'build/music-material-selection/treatment-trial-v1'
PLAN=REPO/'research/71-s18-send-correction-plan.json'


def corrected_settings(original):
    if original['cue']!='S18-3':raise ValueError('Correction authorized for S18-3 only')
    return {**original,'send_policy':'post_fader'}


def inspect(x,wet,dry):
    rows=[]
    for t in np.arange(18.3,19.81,.1):
        a,b=round((t-2)*RATE),round((t-2+.1)*RATE)
        level=lambda v:float(20*np.log10(max(np.sqrt(np.mean(v[a:b]**2)),1e-12)))
        rows.append(dict(player_seconds=round(float(t),1),dry_dbfs=level(dry),wet_dbfs=level(wet),combined_dbfs=level(x[2*RATE:-3*RATE])))
    return rows


def page(m):
    c=m['cues'][0];s=c['settings'];e=lambda x:html.escape(str(x),quote=True)
    old=legacy_page(dict(cues=[],references=[],lead_silence=2,trail_silence=3))
    client=old[old.rfind('<script>'):].replace('wmc-cue61-','wmc-cue71-').replace("kind:'private-cue-edit-listening-decisions'","kind:'s18-only-send-correction-outcomes'")
    options=''.join(f'<option value="{k}" {"selected" if k=="B" else ""}>{e(r["label"])}</option>' for k,r in c['renders'].items())
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC — S18-3 correction</title>
<style>body{max-width:950px;margin:30px auto;padding:0 18px;background:#151a1c;color:#ece6da;font:17px/1.5 system-ui}article{padding:20px;border:1px solid #627371;border-radius:10px}audio,textarea{width:100%}button,select{padding:9px;margin:5px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}a{color:#9bd8ee}#json{height:180px}</style>
<h1>S18-3 — late room buildup correction</h1><p>B is the new correction; A is your selected trial version with the reported bump. Only the reverb send changes: it now follows the dry fade instead of continuing unfaded excitation. No extra wet fade, retiming, freeze or normalization. Other selected cues are untouched.</p>
<p>The new tail is substantially quieter. Listen for whether the bump and intrusive room takeover are gone, and whether the ending now feels too dry or short. Technical measurements cannot decide that.</p>
<header><button id="stop">Stop all</button><button id="export">Export decisions JSON</button><button id="show">Show/copy JSON</button><span id="status"></span></header><details id="fallback"><summary>Copy export fallback</summary><textarea id="json" readonly></textarea></details>'''+f'''
<article data-cue="S18-3"><h2>{e(s['source_title'])} · S18-3</h2>
<p>Source112.8–130s; unchanged dry fade127.8–130s, entrance0.8s. Player has2s leading and3s final silence. Reported player19s corresponds to source129.8s; dry stop is player19.2s.</p>
<select class="variant">{options}</select><button class="play">Play from start</button><button class="ending">Hear around the bump</button><label><input type="checkbox" class="position" checked>Keep position when switching</label><audio controls preload="none" src="{e(c['renders']['B']['file'])}"></audio>
<p>Verdict <select class="verdict"><option>Unreviewed</option><option>Keep</option><option>Adjust</option><option>Reject</option></select> Preferred treatment <select class="preferred"><option value="">Undecided</option><option value="A">A — original trial B</option><option value="B">B — corrected post-fader send</option></select></p><textarea rows="3" placeholder="Bump gone? Tail still intrusive, or now too quiet? Include player time."></textarea>
<details><summary>Exact original reference / processing /100ms measurements</summary><audio controls preload="none" src="{e(c['original_reference'])}"></audio><p>RT60 5.5s and the exact original wet gain are retained. Gain is not recalibrated to make the new tail louder. Pre-fade audio is sample-identical. No subjective listening by Codex.</p><pre>{e(json.dumps(dict(changes=m['changes'],measurements=m['measurements'],settings=s),indent=2))}</pre></details></article>
<script id="manifest" type="application/json">'''+json.dumps(m).replace('<','\\u003c')+'</script>'+client


def build(output):
    output=build_path(output)
    if output.exists():raise FileExistsError('Use a fresh output')
    plan=json.loads(PLAN.read_text())
    for path,h in plan['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed: '+path)
    old=json.loads((TRIAL/'renders.json').read_text());prior=next(c for c in old['cues'] if c['settings']['cue']=='S18-3')
    original=prior['settings'];settings=corrected_settings(original)
    sourcepath=(TRIAL/prior['original_reference']).resolve();source=decode(sourcepath)
    if digest(sourcepath)!=prior['source_preview_sha256']:raise ValueError('Source changed')
    source_gain=prior['proofs']['B']['wet_gain']
    control,cp,cc=render_continuous(source,original,original['rt60'],wet_gain=source_gain)
    audio,p,components=render_continuous(source,settings,settings['rt60'],wet_gain=source_gain)
    originalpath=TRIAL/prior['renders']['B']['file'];original_pcm=decode(originalpath)
    if not np.array_equal(original_pcm,np.rint(control*32767)/32768):raise ValueError('Original reconstruction mismatch')
    if not np.array_equal(cc['dry'],components['dry']):raise ValueError('Unapproved dry edit')
    prefix=round((2+settings['dry_fade'][0]-settings['source_in'])*RATE)
    if not np.array_equal(audio[:prefix],control[:prefix]):raise ValueError('Pre-fade audio changed')
    output.mkdir();(output/'audio').mkdir();qa=write_pcm(output/'audio/S18-3-B.wav',audio)
    primary={**p,'freeze_relative':16} # Existing client subtracts2s: start at player16.
    for key in ('family','confidence','reasoning','risks','measurement_unknowns','explicit_fade_preserved','treatment'):
        settings.pop(key,None)
    settings['assumption']='Only room excitation follows the unchanged dry fade; original source/fade/RT60/wet gain retained. Listening approval pending.'
    c=dict(settings=settings,proof=primary,renders={
        'A':dict(file=Path(os.path.relpath(originalpath,output)).as_posix(),label='A — selected trial B, reported bump',qa=prior['renders']['B']['qa']),
        'B':dict(file='audio/S18-3-B.wav',label='B — corrected post-fader room send',qa=qa)},
        original_reference=Path(os.path.relpath(sourcepath,output)).as_posix(),source_identity=prior['source_identity'],excerpt_role=prior['excerpt_role'])
    m=dict(schema=1,plan_sha256=digest(PLAN),feedback_sha256=old['feedback_sha256'],source_metadata_sha256=old['source_metadata_sha256'],
        primary_variant='B',lead_silence=2,trail_silence=3,cues=[c],references=[],subjectively_listened=False,browser_playback_verified=False,
        changes=dict(send_policy=['pre_ending_fade','post_fader'],wet_gain_unchanged=source_gain,dry_exact=True,pre_fade_exact_until_player_seconds=prefix/RATE),
        measurements=dict(A=inspect(control,cc['wet'],cc['dry']),B=inspect(audio,components['wet'],components['dry'])),
        comparison=dict(A_post_source_first_second_dbfs=cp['post_stop_first_second_dbfs'],B_post_source_first_second_dbfs=p['post_stop_first_second_dbfs']))
    (output/'renders.json').write_text(json.dumps(m,indent=2)+'\n');(output/'index.html').write_text(page(m),encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f'#EXTINF:{r["qa"]["seconds"]},{r["label"]}\n{r["file"]}\n' for r in c['renders'].values()),encoding='utf-8')
    for path,h in plan['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed after render')
    for r in c['renders'].values():
        if digest(output/r['file'])!=r['qa']['sha256']:raise ValueError('Output/reference mismatch')
    links=re.findall(r'(?:src|href)="([^"]+)"',(output/'index.html').read_text(encoding='utf-8'))
    if any('://' in path or not (output/path).is_file() for path in links):raise ValueError('Invalid local resource')
    proof=dict(passed=True,cue='S18-3',new_renders=1,new_sha256=qa['sha256'],immutable_inputs=len(plan['immutable_inputs']),
        identical_original_reconstruction=True,identical_dry_and_pre_fade=True,no_clipping=qa['clipped_samples']==0,
        post_source_geometry=p['release_diagnostics'],cleanup_peak_dbfs=p['cleanup_peak_dbfs'],dry_stop_sample_delta=p['dry_stop_max_sample_delta'],
        index_sha256=digest(output/'index.html'),metadata_sha256=digest(output/'renders.json'),subjectively_listened=False,real_browser_tested=False)
    if p['cleanup_peak_dbfs']>=-100 or p['dry_stop_max_sample_delta']>.02 or p['release_diagnostics']['rebound_review']:raise ValueError('Tail safety review required')
    (output/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
