"""Bounded S18-3 follow-up; compare partial send tapers, not global rule changes."""
import argparse
import json
import os
from pathlib import Path

import numpy as np

from cue_edit_render import decode
from cue_freeze_dsp import RATE,render_continuous
from cue_tail_v2 import write_pcm
from cue_s18_correction import page as previous_page,inspect
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]
PLAN=REPO/'research/72-s18-partial-send-plan.json'
TRIAL=REPO/'build/music-material-selection/treatment-trial-v1'
PRIOR=REPO/'build/music-material-selection/s18-correction-v1'


def build(output):
    output=build_path(output)
    if output.exists():raise FileExistsError('Fresh output only')
    plan=json.loads(PLAN.read_text())
    for path,h in plan['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed')
    old=json.loads((TRIAL/'renders.json').read_text());base=next(c for c in old['cues'] if c['settings']['cue']=='S18-3')
    settings=base['settings'];gain=base['proofs']['B']['wet_gain'];sourcepath=(TRIAL/base['original_reference']).resolve()
    if digest(sourcepath)!=base['source_preview_sha256']:raise ValueError('Source changed')
    source=decode(sourcepath);oldpost=json.loads((PRIOR/'renders.json').read_text());ref=oldpost['cues'][0]['renders']['B']
    output.mkdir();(output/'audio').mkdir()
    renders={'A':dict(file=Path(os.path.relpath(PRIOR/ref['file'],output)).as_posix(),label='A — previous correction: reported dip',qa=ref['qa'])};proofs={};measurements={};actual={}
    for name,power in plan['variants'].items():
        s={**settings,'send_policy':'tapered_ending','send_ending_fade_power':power}
        x,p,v=render_continuous(source,s,s['rt60'],wet_gain=gain)
        if name=='B':reference_dry=v['dry'];primary=p;primary_settings=s
        elif not np.array_equal(reference_dry,v['dry']):raise ValueError('Dry edit changed')
        until=round((2+settings['dry_fade'][0]-settings['source_in'])*RATE)
        original=decode(TRIAL/base['renders']['B']['file'])
        if not np.array_equal(np.rint(x[:until]*32767)/32768,original[:until]):raise ValueError('Pre-fade audio differs')
        qa=write_pcm(output/'audio'/f'S18-3-{name}.wav',x)
        renders[name]=dict(file=f'audio/S18-3-{name}.wav',label=f'{name} — partial send taper {power:g} ({"fuller" if name=="B" else "more restrained"})',qa=qa)
        proofs[name]=p;measurements[name]=inspect(x,v['wet'],v['dry']);actual[name]=dict(send_policy='tapered_ending',power=power,gain=gain)
        if p['cleanup_peak_dbfs']>=-100 or p['dry_stop_max_sample_delta']>.02 or p['release_diagnostics']['rebound_review']:raise ValueError('Tail safety review required')
    primary_settings={**primary_settings,'assumption':'New partial send taper; source/dry fade/RT60/gain retained. Previous post-fader correction rejected for dip. Listening pending.'}
    c=dict(settings=primary_settings,proof={**primary,'freeze_relative':16},renders=renders,source_identity=base['source_identity'],excerpt_role=base['excerpt_role'],original_reference=Path(os.path.relpath(sourcepath,output)).as_posix())
    m=dict(schema=1,plan_sha256=digest(PLAN),feedback_sha256=old['feedback_sha256'],source_metadata_sha256=old['source_metadata_sha256'],
        primary_variant='B',lead_silence=2,trail_silence=3,cues=[c],references=[],subjectively_listened=False,real_browser_tested=False,
        changes=actual,measurements=measurements,proofs=proofs)
    text=previous_page(m)
    text=text.replace('late room buildup correction','partial send correction').replace('S18-3 correction','S18-3 partial-send follow-up')
    text=text.replace('B is the new correction; A is your selected trial version with the reported bump. Only the reverb send changes: it now follows the dry fade instead of continuing unfaded excitation. No extra wet fade, retiming, freeze or normalization. Other selected cues are untouched.',
        'A is the rejected full post-fader correction with the dip. B and C taper the room send more gently, between full independent send and full post-fader. Only this cue is rendered. Dry fade, cut, original wet gain, filters and RT60 stay unchanged. Both are conventional reverb, not freeze.')
    text=text.replace('The new tail is substantially quieter. Listen for whether the bump and intrusive room takeover are gone, and whether the ending now feels too dry or short. Technical measurements cannot decide that.',
        'B fills the dip more, but measurements still show a small late rise. C is more restrained and avoids that measured rise. Compare which sounds continuous without a separate room takeover. Neither is claimed musically resolved.')
    text=text.replace('<option value="A">A — original trial B</option><option value="B">B — corrected post-fader send</option>',
        '<option value="A">A — rejected post-fader correction</option><option value="B">B — fuller partial taper</option><option value="C">C — more restrained partial taper</option>')
    text=text.replace('wmc-cue71-','wmc-cue72-').replace('s18-only-send-correction-outcomes','s18-partial-send-outcomes')
    (output/'renders.json').write_text(json.dumps(m,indent=2)+'\n');(output/'index.html').write_text(text,encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f'#EXTINF:{r["qa"]["seconds"]},{r["label"]}\n{r["file"]}\n' for r in renders.values()))
    for path,h in plan['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed')
    for r in renders.values():
        if digest(output/r['file'])!=r['qa']['sha256']:raise ValueError('Payload mismatch')
    proof=dict(passed=True,cue='S18-3',new_renders=2,preserved_input_count=len(plan['immutable_inputs']),
        hashes={k:r['qa']['sha256'] for k,r in renders.items()},index_sha256=digest(output/'index.html'),metadata_sha256=digest(output/'renders.json'),
        identical_dry=True,identical_pre_fade=True,subjectively_listened=False,real_browser_tested=False)
    (output/'verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
