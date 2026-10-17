"""Render one S18 dry-only release comparison; never alter wet/accepted audio."""
import argparse
import html
import json
import os
from pathlib import Path
import numpy as np
from cue_edit_render import decode
from cue_freeze_dsp import RATE,dry_db_release,dry_envelope
from cue_tail_v2 import write_pcm
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]


def build(output):
    output=build_path(output)
    if output.exists():raise FileExistsError('Fresh output required')
    ledger=REPO/'research/69-treatment-predictions.json';ledger_hash=digest(ledger)
    selected=json.loads((REPO/'research/70-selected-private-cue-renders.json').read_text())['selections']
    for r in selected:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Selected render changed')
    root=REPO/'build/music-material-selection/treatment-trial-v1'
    cue=next(c for c in json.loads((root/'renders.json').read_text())['cues'] if c['settings']['cue']=='S18-3')
    s=cue['settings'];sourcepath=(root/cue['original_reference']).resolve()
    if digest(sourcepath)!=cue['source_preview_sha256']:raise ValueError('Source changed')
    source=decode(sourcepath);a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
    crop=source[a:b];args=(b-a,RATE,s['fade_in'],s['dry_fade'][0]-s['source_in'],s['dry_fade'][1]-s['source_in'])
    old=crop*dry_envelope(*args)[:,None]
    parameters=dict(depth_db=72.,onset_seconds=.12,cleanup_seconds=.02)
    env=dry_db_release(*args,**parameters);new=crop*env[:,None]
    start=round(args[-2]*RATE)
    if not np.array_equal(old[:start],new[:start]):raise ValueError('Pre-fade samples changed')
    previous=REPO/'build/music-material-selection/s18-handoff-diagnostic/audio/S18-3-dry-diagnostic.wav'
    proof_old=json.loads((previous.parent.parent/'verification.json').read_text())
    if digest(previous)!=proof_old['dry_qa']['sha256']:raise ValueError('Dry control changed')
    output.mkdir();(output/'audio').mkdir()
    qa=write_pcm(output/'audio/S18-3-dry-db-release.wav',np.pad(new,((2*RATE,3*RATE),(0,0))))
    level=lambda x:float(20*np.log10(max(np.sqrt(np.mean(x*x)),1e-12)))
    rows=[]
    for t in np.arange(17.,19.2,.1):
        j=round((t-2)*RATE)
        rows.append(dict(player_seconds=round(float(t),1),old_dbfs=level(old[j:j+RATE//10]),new_dbfs=level(new[j:j+RATE//10])))
    rel=lambda p:html.escape(Path(os.path.relpath(p,output)).as_posix(),quote=True)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S18 dry fade comparison</title><style>body{max-width:850px;margin:30px auto;padding:0 20px;background:#171b1d;color:#eee;font:18px/1.5 system-ui}audio{width:100%}button{padding:10px}</style><h1>S18-3 — dry fade only</h1><p>No added reverb. Both use source112.8–130s, entrance0.8s, ending fade127.8–130s. Player fade17–19.2s;2s lead and3s final silence.</p><p>B spreads attenuation more evenly in decibels:120ms smooth onset,72dB reduction,20ms quiet cleanup to zero. It reduces the music earlier in the same window. This is a listening test, not an accepted correction.</p>'''
    for key,title,url in [('A','A — previous dry fade',rel(previous)),('B','B — even-dB dry release','audio/S18-3-dry-db-release.wav')]:
        page+=f'<h2>{title}</h2><button data-id="{key}">Hear ending from16s</button><audio id="{key}" controls preload="metadata" src="{url}"></audio>'
    page+='''<p>Compare the ending slope first. Wet versions remain untouched. Reply with whether B still has a sudden late drop, and whether its earlier reduction feels too quick.</p><script>const all=[...document.querySelectorAll('audio')];all.forEach(a=>a.onplay=()=>all.forEach(b=>{if(b!==a)b.pause()}));document.querySelectorAll('button').forEach(b=>b.onclick=()=>{const a=document.getElementById(b.dataset.id);const go=()=>{a.currentTime=16;a.play().catch(()=>{})};if(a.readyState)go();else{a.addEventListener('loadedmetadata',go,{once:true});a.load()}});</script></html>'''
    (output/'index.html').write_text(page,encoding='utf-8')
    for r in selected:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Selected render changed')
    if digest(ledger)!=ledger_hash:raise ValueError('Ledger changed')
    proof=dict(kind='dry_release_comparison_not_accepted',verbatim_feedback='It does have a quick dip at the very end',
               source_sha256=digest(sourcepath),source_cut=[s['source_in'],s['source_out']],dry_fade=s['dry_fade'],
               parameters=parameters,new_qa=qa,old_sha256=digest(previous),pre_fade_samples_exact=True,
               selected_hashes_preserved=len(selected),ledger_unchanged=True,measurements=rows,
               real_browser_tested=False,subjectively_listened=False)
    (output/'verification.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n')
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
