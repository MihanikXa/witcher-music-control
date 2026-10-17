"""Independent private v2 payload, clock, envelope and preservation checks."""
import argparse
import json
from pathlib import Path
import re

import numpy as np

from cue_edit_render import decode
from cue_freeze_dsp import RATE,envelope_windows,release_diagnostics
from cue_tail_v2 import REPO,V1,PLAN
from white_orchard_prepare import build_path,digest


def verify(folder):
    folder=build_path(folder);m=json.loads((folder/'renders.json').read_text())
    plan=json.loads(PLAN.read_text());old=json.loads((V1/'renders.json').read_text())
    if m['plan_sha256']!=digest(PLAN) or digest(V1/'renders.json')!=plan['v1_metadata_sha256']:raise ValueError('Plan/v1 metadata changed')
    for path,h in plan['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Historical input changed')
    v1_count=0
    for c in old['cues']:
        for r in c['renders'].values():
            if digest(V1/r['file'])!=r['qa']['sha256']:raise ValueError('v1 render changed')
            v1_count+=1
    if {c['settings']['cue'] for c in m['cues']}!={c['cue'] for c in plan['cues']}:raise ValueError('Wrong corrective selection')
    results=[]
    for c in m['cues']:
        s=c['settings'];prior=next(v for v in old['cues'] if v['settings']['cue']==s['cue'])
        for field in ['source_in','source_out','dry_fade','verbatim_notes']:
            if s[field]!=prior['settings'][field]:raise ValueError('Source boundary/user instruction changed')
        source=(folder/c['original_reference']).resolve()
        if digest(source)!=c['source_preview_sha256']:raise ValueError('Original changed')
        old_onset=None
        if s.get('onset_mute_seconds'):
            x=decode(source)[round(s['source_in']*RATE):round((s['source_in']+3)*RATE)]
            old_onset=dict(original_first_three_seconds_rms_dbfs=float(20*np.log10(np.sqrt(np.mean(x*x)))),
                original_first_three_seconds_peak=float(np.max(np.abs(x))))
        b_audio=None
        for name,r in c['renders'].items():
            path=(folder/r['file']).resolve()
            if digest(path)!=r['qa']['sha256']:raise ValueError('Payload mismatch')
            x=decode(path)
            if len(x)!=round(r['qa']['seconds']*RATE) or x.shape[1]!=2:raise ValueError('PCM layout/duration')
            if np.any(x[:2*RATE]) or np.any(x[-3*RATE:]):raise ValueError('Silence context')
            if np.max(np.abs(x))>=.97:raise ValueError('Unsafe levels')
            if name.startswith('A'):continue
            p=c['proofs'][name];active=x[2*RATE:-3*RATE]
            measured=envelope_windows(active);expected=np.array(p['windows_50ms']['combined'])
            # Round-to-16bit readback plus 32767/32768 scale; absolute RMS error bound.
            if np.max(np.abs(measured-expected*32767/32768))>1.6e-5:raise ValueError('Envelope metadata differs from PCM')
            if p['cleanup_peak_dbfs']>=-100 or p['dry_stop_max_sample_delta']>.02:raise ValueError('Unsafe handoff/truncation')
            control=p['wet_control_checks']
            if not all(control[k] for k in ['no_late_wet_attack','no_wet_gain_rebound','no_post_stop_hold']) or control['independent_secondary_fade']:raise ValueError('Control-envelope regression')
            post=release_diagnostics(active,p['dry_stop_relative'])
            if post['rebound_review'] or post['plateau_window_starts']:raise ValueError('Audible-range post-stop envelope review required')
            if s.get('onset_mute_seconds') and np.any(active[:round(s['onset_mute_seconds']*RATE)]):raise ValueError('Bleep remains')
            if name=='B':b_audio=x
            if name=='C':
                stop=round((2+p['dry_stop_relative'])*RATE)
                if not np.array_equal(b_audio[:stop],x[:stop]):raise ValueError('B/C pre-stop loudness mismatch')
                if p['settled_energy_relative_range']>1e-10:raise ValueError('Unstable freeze')
            dry=np.array(p['windows_50ms']['dry'])
            # Same geometry detector on dry 50ms energies, expanded as a diagnostic
            # sequence at 48kHz, distinguishes source-driven rises from wet control.
            dry_proxy=np.repeat(dry,round(.05*RATE))
            dry_diag=release_diagnostics(np.repeat(dry_proxy[:,None],2,axis=1),max(0,s['dry_fade'][0]-s['source_in']-1))
            results.append(dict(cue=s['cue'],variant=name,sha256=r['qa']['sha256'],rt60=p['rt60'],
                seconds=r['qa']['seconds'],peak=r['qa']['peak'],wet_gain=p['wet_gain'],
                cleanup_peak_dbfs=p['cleanup_peak_dbfs'],post_stop_first_second_dbfs=p['post_stop_first_second_dbfs'],
                max_post_stop_rebound_db=post['max_sustained_rebound_db'],plateau_windows=0,
                entire_transition_rebound_db=p['entire_transition_geometry']['max_sustained_rebound_db'],
                dry_transition_rebound_db=dry_diag['max_sustained_rebound_db'],
                freeze_energy_drift=p['settled_energy_relative_range'] if name=='C' else None,
                onset_repair_evidence=old_onset,source_clock_preserved=True))
    page=(folder/'index.html').read_text(encoding='utf-8')
    links=re.findall(r'(?:src|href)="([^"]+)"',page)
    if any(not (folder/p).is_file() for p in links):raise ValueError('Broken local audio/chart link')
    if any('://' in p for p in links):raise ValueError('Unexpected external content')
    return dict(passed=True,cues=len(m['cues']),new_renders=len(results),v1_renders_verified_unchanged=v1_count,
        immutable_report_inputs=len(plan['immutable_inputs']),index_sha256=digest(folder/'index.html'),
        metadata_sha256=digest(folder/'renders.json'),local_links=len(links),
        browser_playback_verified=False,subjectively_listened=False,results=results)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    result=verify(a.folder);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='results'}))
