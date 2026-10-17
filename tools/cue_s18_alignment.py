"""Render three private S18 local send/crossover timing tests from immutable source."""
import argparse,html,json,os
from pathlib import Path
import numpy as np
from scipy import signal
from cue_edit_render import decode
from cue_freeze_dsp import RATE,render_continuous
from cue_tail_v2 import write_pcm
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]
SOURCE=REPO/'build/music-material-selection/audition-v3/audio/S18-Island-alternate-pads-arrangement.opus'
TRIAL=REPO/'build/music-material-selection/treatment-trial-v1'
CENTERS=(129.450,129.575,129.650)
MEASURE_CENTERS=tuple(round(float(t),3) for t in np.arange(129.25,129.925,.025))+(129.95,)
BANDS=((30,200),(200,1000),(1000,4000),(4000,10000))

def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))
def db(x):return float(20*np.log10(max(rms(x),1e-12)))
def window(x,center,seconds):
    n=round(seconds*RATE);c=round(center*RATE);a=c-n//2;b=a+n
    if a<0 or b>len(x):raise ValueError('Measurement window out of bounds')
    return x[a:b]
def band(x,lo,hi):
    return signal.sosfiltfilt(signal.butter(4,[lo,hi],btype='bandpass',fs=RATE,output='sos'),x,axis=0)
def rel(p,base):return Path(os.path.relpath(p,base)).as_posix()

def build(output):
    output=build_path(output)
    if output.exists():raise FileExistsError('Use a fresh ignored output')
    source_hash='97663b268c063e35f0e4f6ac2f1fa3ade10289d93cf4994e46663580576ea8dc'
    if digest(SOURCE)!=source_hash:raise ValueError('Original audition source hash differs')
    preserved=json.loads((REPO/'research/71-s18-send-correction-plan.json').read_text())['immutable_inputs']
    for path,h in preserved.items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed: '+path)
    selected=json.loads((REPO/'research/70-selected-private-cue-renders.json').read_text())['selections']
    for r in selected:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Pinned selected audio changed')
    prior=json.loads((TRIAL/'renders.json').read_text())
    cue=next(c for c in prior['cues'] if c['settings']['cue']=='S18-3');s=cue['settings']
    source=decode(SOURCE)
    if digest(TRIAL/cue['original_reference'])!=source_hash:raise ValueError('Trial source link is not the uploaded/original source')
    gain=cue['proofs']['B']['wet_gain'];original_file=TRIAL/cue['renders']['B']['file']
    # Rebuild the old selected independent-send signal before comparing its components.
    ref,refproof,refcomp=render_continuous(source,s,s['rt60'],wet_gain=gain)
    if not np.array_equal(decode(TRIAL/original_file),np.rint(ref*32767)/32768):raise ValueError('Reference reconstruction mismatch')
    dry_path=REPO/'build/music-material-selection/s18-handoff-diagnostic/audio/S18-3-dry-diagnostic.wav'
    dry_evidence=json.loads((REPO/'research/73-s18-diagnostic-evidence.json').read_text())
    if digest(dry_path)!=dry_evidence['dry_qa']['sha256']:raise ValueError('Dry-only control identity changed')
    dry_expected=np.pad(refcomp['dry'][:round((s['source_out']-s['source_in'])*RATE)],((2*RATE,3*RATE),(0,0)))
    actual_dry=decode(dry_path)
    if not np.array_equal(actual_dry,np.rint(dry_expected*32767)/32768):raise ValueError('Dry-only control reconstruction mismatch')
    source_in=s['source_in'];source_out=s['source_out'];a=round(source_in*RATE);b=round(source_out*RATE)
    # render_continuous returns component arrays before the player-context pad.
    offset=0
    output.mkdir();(output/'audio').mkdir();renders={};measurements={};candidate_components={}
    # Components start at source112.8s (before the2s playback pad).
    def cueclock(x):return x[offset:offset+(b-a)]
    base_original=source[a:b]
    compref={k:cueclock(v) for k,v in refcomp.items() if k in ('dry','wet')}
    compref['combined']=compref['dry']+compref['wet']
    valley_scan=[]
    for ms in (20,25,50,75,100):
        centers=np.arange(129.50,129.651,.0025)
        values=[db(window(source,float(t),ms/1000)) for t in centers]
        best=int(np.argmin(values))
        valley_scan.append(dict(window_ms=ms,source_center_seconds=round(float(centers[best]),4),
                               dbfs=values[best]))
    # Exact direct-signal measurements and band evolution around the disputed window.
    original_rows=[]
    for center in MEASURE_CENTERS:
        row=dict(source_seconds=round(float(center),3),player_seconds=round(float(center-110.8),3),windows={})
        for ms in (20,25,50,100):
            row['windows'][str(ms)]=dict(original_dbfs=db(window(base_original,center-source_in,ms/1000)),
                actual_dry_pcm_dbfs=db(window(actual_dry,center-110.8,ms/1000)))
        original_rows.append(row)
    band_summary=[]
    for lo,hi in BANDS:
        filtered=band(source,lo,hi)
        band_summary.append(dict(hz=[lo,hi],rows=[dict(source_seconds=t,dbfs=db(window(filtered,t,0.05))) for t in (129.45,129.575,129.65,129.75,129.85,129.95)]))
    # Energy-envelope lag is an empirical modulation lag, not an acoustic path delay.
    x=band(base_original,200,1000);y=band(compref['wet'],200,1000)
    hop=round(.01*RATE);win=round(.02*RATE)
    idx=np.arange(round((128.4-source_in)*RATE),round((129.9-source_in)*RATE)-win,hop)
    ex=np.array([rms(x[i:i+win]) for i in idx]);ey=np.array([rms(y[i:i+win]) for i in idx])
    lagrows=[]
    for lagms in range(0,1001,10):
        k=round(lagms/1000/.01)
        if k<len(ex)-3:lagrows.append((lagms,float(np.corrcoef(ex[:-k or None],ey[k:])[0,1])))
    best_lag=max(lagrows,key=lambda z:z[1]) if lagrows else (None,None)
    def rows_for(components):
        arrays={'source':base_original,'dry':cueclock(components['dry']),
                'wet':cueclock(components['wet']),
                'combined':cueclock(components['dry']+components['wet'])}
        out=[]
        for center in MEASURE_CENTERS:
            row=dict(source_seconds=round(float(center),3),player_seconds=round(float(center-110.8),3),windows={})
            for ms in (20,25,50,100):
                row['windows'][str(ms)]={k:db(window(v,center-source_in,ms/1000)) for k,v in arrays.items()}
            out.append(row)
        return out
    for ix,center in enumerate(CENTERS,1):
        settings={**s,
                  'local_dry_alignment':dict(center_source_seconds=center,shift_seconds=.10,width_seconds=.5),
                  'local_send_fade':dict(center_source_seconds=center,width_seconds=.5)}
        audio,proof,components=render_continuous(source,settings,s['rt60'],wet_gain=gain)
        lo=round((center-.25-source_in)*RATE);hi=round((center+.25-source_in)*RATE)
        if not np.array_equal(audio[:2*RATE+lo],ref[:2*RATE+lo]):raise ValueError('Audio before local window changed')
        if not np.array_equal(components['dry'][hi+1:],refcomp['dry'][hi+1:]):raise ValueError('Dry audio after local window changed')
        if np.any(components['send_envelope'][hi+1:]):raise ValueError('New excitation continued after local send stop')
        candidate_components[f'T{ix}']={z:cueclock(components[z]) for z in ('dry','wet')}
        name=f'S18-3-alignment-{ix}.wav';qa=write_pcm(output/'audio'/name,audio)
        label=('Earlier','Natural-dip aligned','Later')[ix-1]
        renders[f'T{ix}']=dict(file='audio/'+name,sha256=qa['sha256'],label=f'{label}: {center:.3f}s source / {center-110.8:.3f}s player',center_source_seconds=center,center_player_seconds=round(center-110.8,3),width_seconds=.5,qa=qa)
        measurements[f'T{ix}']=dict(rows=rows_for(components),proof=dict(send_policy=proof['send_policy'],local_send_fade=proof['local_send_fade'],local_dry_alignment=proof['local_dry_alignment'],wet_gain=proof['wet_gain'],rt60=proof['rt60'],cleanup_peak_dbfs=proof['cleanup_peak_dbfs'],dry_stop_max_sample_delta=proof['dry_stop_max_sample_delta'],post_stop_first_second_dbfs=proof['post_stop_first_second_dbfs'],post_stop_geometry=proof['release_diagnostics'],prefix_exact=True,dry_after_window_exact=True,send_zero_after_window=True))
    measurements['reference']={'rows':rows_for(refcomp),'proof':dict(send_policy=s['send_policy'],wet_gain=gain,rt60=s['rt60'],original_render_sha256=digest(TRIAL/original_file))}
    # Per-band output trajectory for all four aligned candidates at 50ms windows.
    for lo,hi in BANDS:
        k=f'{lo}-{hi}Hz';measurements.setdefault('bands_50ms',{})[k]={}
        labels=[('reference',refcomp)]+[(f'T{i}',candidate_components[f'T{i}']) for i in range(1,4)]
        filtered_source=band(base_original,lo,hi)
        for label,cc in labels:
            arrays={'source':filtered_source,'dry':band(cc['dry'],lo,hi),
                    'wet':band(cc['wet'],lo,hi),'combined':band(cc['dry']+cc['wet'],lo,hi)}
            measurements['bands_50ms'][k][label]=[dict(source_seconds=t,**{z:db(window(v,t-source_in,.05)) for z,v in arrays.items()}) for t in (129.25,129.35,129.45,129.55,129.575,129.65,129.75,129.85,129.95)]
    # A comparison page with unchanged selected trial B as A and three timing candidates.
    refs=[dict(label='A — unchanged selected trial B',file=rel(TRIAL/original_file,output),sha256=digest(TRIAL/original_file),center_source_seconds=None)]
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S18-3 local alignment test</title><style>body{max-width:950px;margin:30px auto;padding:0 18px;background:#151a1c;color:#eee;font:17px/1.5 system-ui}audio{width:100%}button{padding:9px;margin:4px}</style><h1>S18-3 — local dry / reverb alignment</h1><p>All candidates retain source112.8–130.0s and the fixed endpoint. A is the unchanged selected render. T1–T3 align on the listed source center: locally delay dry-fade progress by100ms with a smooth raised-cosine phase warp, while tapering new reverb input with a smooth0.5s cosine window. The earlier2.2s fade window, wet level and RT60 remain fixed. These are timing trials, not approved edits.</p><p>Player time = source time −110.8s. Compare the disputed area using “Hear from17.5s”; each player stops the others. Source reference and component measurements are recorded alongside the files.</p>'''
    for key,obj in [('A',refs[0])]+list(renders.items()):
        url=html.escape(obj['file'],quote=True)
        page+=f'<h2>{html.escape(key+" — "+obj["label"],quote=True)}</h2><button data-id="{key}">Hear from17.5s</button><audio id="{key}" controls preload="metadata" src="{url}"></audio>'
    page+=f'<details><summary>Original source and existing dry-only control</summary><p>Original uses its own source clock. Dry control uses the cue player clock.</p><audio id="source" controls preload="none" src="{html.escape(rel(SOURCE,output),quote=True)}"></audio><audio id="dry" controls preload="none" src="{html.escape(rel(dry_path,output),quote=True)}"></audio></details>'
    page+='''<p>Listen for whether the direct dip remains, whether the room swells or holds, and whether the change feels continuous through the fixed130.0s ending. These are provisional timing trials, not accepted edits. No musical endpoint or original source is changed.</p><script>const all=[...document.querySelectorAll('audio')];all.forEach(a=>a.onplay=()=>all.forEach(b=>{if(a!==b)b.pause()}));document.querySelectorAll('button').forEach(b=>b.onclick=()=>{const a=document.getElementById(b.dataset.id);const go=()=>{a.currentTime=17.5;a.play().catch(()=>{})};if(a.readyState)go();else{a.addEventListener('loadedmetadata',go,{once:true});a.load()}})</script></html>'''
    (output/'index.html').write_text(page,encoding='utf-8')
    (output/'measurements.json').write_text(json.dumps(dict(source_sha256=source_hash,source_clock='player_time + 110.8',window_centers_seconds=[129.45,129.575,129.65],window_size_ms=[20,25,50,100],original_rows=original_rows,valley_scan=valley_scan,bands_original=band_summary,wet_modulation_lag=dict(hop_ms=10,window_ms=20,best_lag_ms=best_lag[0],max_correlation=best_lag[1],meaning='energy-modulation alignment only; not acoustic path delay'),candidates=measurements),indent=2,allow_nan=False)+'\n')
    for r in selected:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Pinned selected audio changed during render')
    for path,h in preserved.items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed after render: '+path)
    proof=dict(source_sha256=source_hash,original_selected_render_sha256=digest(TRIAL/original_file),dry_control_sha256=digest(dry_path),new_renders=renders,source_cut=[112.8,130.0],endpoint_unchanged=True,earlier_fade_window_unchanged=s['dry_fade'],dry_phase_shift_seconds=.10,dry_phase_width_seconds=.5,send_taper_width_seconds=.5,independent_send_gain_unchanged=gain,rt60=s['rt60'],fade_centers=list(CENTERS),pinned_selections_preserved=len(selected),immutable_inputs_preserved=len(preserved),real_browser_tested=False,subjectively_listened=False)
    (output/'verification.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n')
    print(json.dumps(proof,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
