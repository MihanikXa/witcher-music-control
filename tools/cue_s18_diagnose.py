"""S18-only diagnostic control. No proposed new reverb treatment or acceptance."""
import argparse
import html
import json
import os
from pathlib import Path

import numpy as np

from cue_edit_render import decode
from cue_freeze_dsp import RATE,dry_envelope
from cue_tail_v2 import write_pcm
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]


def build(output):
    output=build_path(output)
    if output.exists():raise FileExistsError('Fresh diagnostic output required')
    ledger=REPO/'research/69-treatment-predictions.json';before=digest(ledger)
    selected=json.loads((REPO/'research/70-selected-private-cue-renders.json').read_text())['selections']
    for r in selected:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Selected file changed')
    root=REPO/'build/music-material-selection/treatment-trial-v1';old=json.loads((root/'renders.json').read_text());c=next(c for c in old['cues'] if c['settings']['cue']=='S18-3');s=c['settings']
    sourcepath=(root/c['original_reference']).resolve()
    if digest(sourcepath)!=c['source_preview_sha256']:raise ValueError('Source changed')
    source=decode(sourcepath);a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
    dry=source[a:b]*dry_envelope(b-a,RATE,s['fade_in'],s['dry_fade'][0]-s['source_in'],s['dry_fade'][1]-s['source_in'])[:,None]
    output.mkdir();(output/'audio').mkdir();qa=write_pcm(output/'audio/S18-3-dry-diagnostic.wav',np.pad(dry,((2*RATE,3*RATE),(0,0))))
    rejected=REPO/'build/music-material-selection/s18-correction-v2/audio/S18-3-C.wav'
    if not rejected.is_file():raise FileNotFoundError(rejected)
    rel=lambda p:Path(os.path.relpath(p,output)).as_posix()
    rows=[]
    for t in [18.3+i*.1 for i in range(9)]:
        j=round((t-2)*RATE);orig=source[a+j:a+j+RATE//10];d=dry[j:j+RATE//10]
        level=lambda x:float(20*np.log10(max(np.sqrt(np.mean(x*x)),1e-12)))
        rows.append(dict(player_seconds=round(float(t),1),unfaded_source_dbfs=level(orig),dry_faded_dbfs=level(d)))
    links={'dry':'audio/S18-3-dry-diagnostic.wav','source':rel(sourcepath),'rejected':rel(rejected)}
    e=lambda x:html.escape(str(x),quote=True)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S18 — diagnostic, not a correction</title><style>body{max-width:900px;margin:30px auto;padding:0 18px;background:#151a1c;color:#e6e5df;font:18px/1.5 system-ui}audio{width:100%}button{padding:10px;margin:8px}</style><h1>S18-3 — isolate the handoff</h1><p>No new reverb treatment. The last two alternatives remain unresolved. Listen to the dry-only control around18–19.2s: does that fade itself have the objectionable dip, or does the problem appear only when reverb is added? The unfaded source has a different clock, shown below.</p>'''
    for key,title,time in [('dry','Dry-only: exact existing dry fade, no added reverb',18),('source','Unfaded original full recording (source clock128.8s)',128.8),('rejected','Last rejected partial taper C (cue clock18s)',18)]:
        page+=f'<h2>{e(title)}</h2><button data-id="{key}" data-time="{time}">Hear relevant section</button><audio id="{key}" controls preload="none" src="{e(links[key])}"></audio>'
    page+='''<p>Dry control: source112.8–130s, fade127.8–130s,2s leading and3s final silence. Dry stop is cue19.2s. The original full source is only linked, never modified. No musical approval or integration is implied.</p><script>const all=[...document.querySelectorAll('audio')];all.forEach(a=>a.onplay=()=>all.forEach(b=>{if(b!==a)b.pause()}));document.querySelectorAll('button').forEach(b=>b.onclick=()=>{const a=document.getElementById(b.dataset.id);const go=()=>{a.currentTime=Number(b.dataset.time);a.play().catch(()=>{})};if(a.readyState)go();else{a.addEventListener('loadedmetadata',go,{once:true});a.load()}});</script></html>'''
    (output/'index.html').write_text(page,encoding='utf-8')
    if digest(ledger)!=before:raise ValueError('Immutable ledger changed')
    for r in selected:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Selected file changed')
    proof=dict(kind='diagnostic_only_not_a_fix',dry_qa=qa,source_sha256=digest(sourcepath),rejected_reference_sha256=digest(rejected),
        source_cut=[s['source_in'],s['source_out']],dry_fade=s['dry_fade'],measurements=rows,
        selected_hashes_preserved=len(selected),ledger_unchanged=True,real_browser_tested=False,subjectively_listened=False,
        verbatim_feedback='There still that dip that 18.8s, then constant volume then fade effect that we tried to correct for a long time')
    (output/'verification.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n');return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);build(p.parse_args().output)
