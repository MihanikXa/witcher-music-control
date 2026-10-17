"""Source-only features and transparent, preregisterable private-cue triage.

No trial DSP/audio is rendered here. Five accepted examples are references,
not a fitted dataset; spectral/chroma proxies cannot identify chord resolution.
"""
import argparse
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy import signal

from cue_edit_render import decode
from cue_freeze_dsp import RATE,dry_envelope,envelope_windows
from white_orchard_prepare import digest

REPO=Path(__file__).resolve().parents[1]
V1=REPO/'build/music-material-selection/cue-edits-v1'
LEDGER=REPO/'research/69-treatment-predictions.json'
TRIAL=['S07-c','S12-2','S15-a','S16-2','S18-3','S20-a']
EXPLICIT={'S05-main','S07-a','S07-b','S07-c','S11-short','S11-long','S15-a','S15-b','S20-a'}


def db(x):return float(20*np.log10(max(float(np.sqrt(np.mean(x*x))),1e-12)))


def source_features(source,s):
    a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
    if not 0<=a<b<=len(source):raise ValueError('Invalid source clock')
    x=source[a:b];last=x[-min(len(x),8*RATE):]
    rms=envelope_windows(last,.1);rdb=20*np.log10(np.maximum(rms,1e-12))
    # Source-only, downsampled spectral analysis. No encoding or modified audio.
    mono=signal.resample_poly(last.mean(axis=1),1,4)
    _,t,z=signal.stft(mono,fs=12000,nperseg=2048,noverlap=1024,boundary=None)
    power=np.abs(z)**2;freq=np.fft.rfftfreq(2048,1/12000)
    norms=power/np.maximum(np.linalg.norm(power,axis=0),1e-20)
    flux=1-np.sum(norms[:,1:]*norms[:,:-1],axis=0)
    chroma=np.zeros((12,power.shape[1]));valid=(freq>=100)&(freq<=3000)
    pitch=(np.rint(69+12*np.log2(freq[valid]/440)).astype(int)%12)
    for k in range(12):chroma[k]=power[valid][pitch==k].sum(axis=0)
    c=chroma/np.maximum(np.linalg.norm(chroma,axis=0),1e-20)
    cm=1-np.sum(c[:,1:]*c[:,:-1],axis=0)
    start=power[:,t<max(t[-1]-1,0)].mean(axis=1)
    end=power[:,t>=max(t[-1]-1,0)].mean(axis=1)
    specdist=float(1-np.dot(start,end)/max(np.linalg.norm(start)*np.linalg.norm(end),1e-20))
    fs,fe=[v-s['source_in'] for v in s['dry_fade']]
    env=dry_envelope(len(x),RATE,s['fade_in'],fs,fe)
    # Model the existing dry edit only; its knee is a risk indicator, not a reverb fit.
    dry=x*env[:,None];begin=max(0,fs-1)
    dd=20*np.log10(np.maximum(envelope_windows(dry[round(begin*RATE):],.25),1e-12))
    usable=dd[:-1]>-70
    drops=-np.diff(dd)[usable]
    early=last[:max(1,len(last)//2)]
    return dict(crop_frames=[a,b],duration=len(x)/RATE,analysis_last_seconds=len(last)/RATE,
        ending_100ms_rms_dbfs=rdb.tolist(),last_half_second_dbfs=db(x[-RATE//2:]),
        preceding_two_seconds_dbfs=db(x[max(0,len(x)-3*RATE):max(1,len(x)-RATE)]),
        last_second_dbfs=db(x[-RATE:]),source_ending_change_db=db(x[-RATE:])-db(early),
        last_four_seconds_slope_db_per_second=float(np.polyfit(np.arange(min(40,len(rdb)))*.1,rdb[-40:],1)[0]),
        rms_rise_events_over_3db=int(np.count_nonzero(np.diff(rdb)>3)),
        positive_100ms_rise_p90_db=float(np.percentile(np.maximum(np.diff(rdb),0),90)),
        spectral_flux_p90=float(np.percentile(flux,90)),
        pitch_class_change_p90=float(np.percentile(cm,90)),
        ending_spectral_distance=specdist,
        last_second_highband_fraction=float(end[freq>=3000].sum()/max(end.sum(),1e-20)),
        original_dry_fade_seconds=fe-fs,modeled_dry_250ms_max_drop_db=float(max(0,max(drops,default=0))),
        first_half_second_dbfs=db(x[:RATE//2]),first_three_seconds_dbfs=db(x[:3*RATE]),
        stereo_correlation=float(np.corrcoef(last.T)[0,1]),
        original_room_rt60=None,room_measurement_limitation='Mixed/stem recording, no isolated impulse or known excitation stop; cannot identify room RT60 reliably.',
        harmonic_limitation='Pitch-class/spectral distances conflate instrumentation, transients and harmony; no chord/cadence claim.',
        rhythmic_limitation='RMS rises/flux are activity proxies, not verified percussion, tempo or rhythmic intent.')


def predict(s,f,explicit):
    """Small heuristic tree; thresholds are engineering choices, never fitted accuracy."""
    fade=list(s['dry_fade']);reasons=[]
    quiet=f['last_half_second_dbfs']<-65 and f['source_ending_change_db']<-15
    busy=f['positive_100ms_rise_p90_db']>2 or f['spectral_flux_p90']>.45
    active=f['last_half_second_dbfs']>-50
    short=f['original_dry_fade_seconds']<2
    if quiet:
        family='already_dissipating';wet=-23;rt=4.5;send='post_fader'
        reasons.append('Source is below−65dBFS at endpoint and falls >15dB: do not amplify a quiet ending or freeze earlier harmony.')
    elif short and active:
        family='active_short_fade';wet=-14;rt=5.5;send='pre_ending_fade'
        reasons.append('Active source with <2s existing fade risks rapid direct/room handoff; established room and independent ending send follow the accepted S05 family, not a fitted rule.')
        if not explicit:
            fade[0]=max(s['source_in']+1,fade[1]-2.2)
            reasons.append('Only the earlier Codex-provisional fade is extended to2.2s; source endpoint remains fixed.')
    elif f['original_dry_fade_seconds']>=3.5:
        family='long_explicit_or_provisional_fade';wet=-20 if f['source_ending_change_db']<-10 else -17
        rt=6 if busy else 7;send='post_fader'
        reasons.append('Existing >=3.5s fade provides room for post-fader integration; avoid sustaining an older harmonic field through a long changing phrase.')
    else:
        family='active_moderate_fade';wet=-16 if busy else -17
        rt=6 if busy else (7.5 if f['duration']>45 else 6.5);send='post_fader'
        reasons.append('Moderate fade: start with accepted S11-style continuously active post-fader room; lower mix than−14dB is a conservative untested transfer.')
    if f['pitch_class_change_p90']>.15 or f['ending_spectral_distance']>.5:
        reasons.append('Elevated pitch-class/spectral change proxy: do not automatically freeze; actual harmonic coherence remains unknown.')
    return dict(family=family,treatment='natural_decay',send_policy=send,continuous_wet_db=wet,rt60=rt,
        source_in=s['source_in'],source_out=s['source_out'],dry_fade=fade,original_dry_fade=s['dry_fade'],
        explicit_fade_preserved=not explicit or fade==s['dry_fade'],fade_in=s['fade_in'],
        highpass_hz=s['highpass_hz'],lowpass_hz=s['lowpass_hz'],
        send_stop_guard_seconds=.02,render_extra_seconds=max(10,rt*1.65),lead_silence=2,trail_silence=3,
        reasoning=reasons,confidence='provisional / low for musical fit; deterministic technical selection',
        risks=['Room coloration or wash','Perceived handoff despite smooth RMS','Possible wrong musical resolution','Base-stem balance may not represent full native arrangement'],
        measurement_unknowns=['True room decay','Actual chord progression and cadence','Human tail preference'])


def survey():
    if LEDGER.exists():raise FileExistsError('Preregistered predictions are immutable; version future rules instead')
    old=json.loads((V1/'renders.json').read_text());sources={r['id']:r for r in json.loads((REPO/'build/music-material-selection/audition-v3/auditions.json').read_text())}
    prior={r['cue']:r for r in json.loads((REPO/'research/62-user-cue-edit-decisions.json').read_text())['decisions']}
    accepted=json.loads((REPO/'research/67-accepted-private-cue-selections.json').read_text())['selections'];approved={r['cue']:r for r in accepted}
    pins={str(p.relative_to(REPO)).replace('\\','/'):digest(p) for p in [REPO/'research/58-user-musical-material-audition-feedback.json',REPO/'research/61-private-cue-edit-plan.json',V1/'renders.json',REPO/'research/62-user-cue-edit-decisions.json',REPO/'research/67-accepted-private-cue-selections.json',REPO/'research/68-remainder-treatment-prediction-handoff.md']}
    for r in accepted:
        if digest(REPO/r['file'])!=r['sha256']:raise ValueError('Accepted audio mismatch')
        pins[r['file']]=r['sha256']
    aux=next(c for c in old['cues'] if c['settings']['cue']=='S05-main')['renders']['B']
    pins[str((V1/aux['file']).relative_to(REPO)).replace('\\','/')]=aux['qa']['sha256']
    @lru_cache(maxsize=2)
    def load(ident):
        p=REPO/'build/music-material-selection/audition-v3'/sources[ident]['preview']
        if digest(p)!=sources[ident]['preview_sha256']:raise ValueError('Preview changed')
        pins[str(p.relative_to(REPO)).replace('\\','/')]=digest(p)
        return decode(p)
    entries=[]
    for c in old['cues']:
        s=c['settings'];key=s['cue'];f=source_features(load(s['source']),s);p=predict(s,f,key in EXPLICIT)
        status='accepted' if key in approved else 'auxiliary_accepted' if key=='S05-main' else 'comparison_only_pending' if s['comparison_only'] else 'pending'
        alt=None
        if key=='S07-c':
            alt={**p,'send_policy':'pre_ending_fade','reasoning':['Controlled alternative changes only ending-send routing; long fade may otherwise leave too weak a tail. Exact common wet gain will be shared.']}
        if key=='S12-2':
            alt={**p,'dry_fade':s['dry_fade'],'reasoning':['Controlled alternative retains original short provisional fade with the same room/send/gain; tests the earlier fade extension rather than louder tails.']}
        entries.append(dict(cue=key,source=s['source'],title=s['source_title'],source_identity=c['source_identity'],
            pool=sources[s['source']]['pool'],source_arrangement_caveat=sources[s['source']]['risk'],
            verbatim_notes=s['verbatim_notes'],previous_feedback={k:prior[key][k] for k in ('verdict','preferred','notes')},
            status=status,trial=key in TRIAL,trial_group='known_problem_note' if key in ('S07-c','S12-2') else 'fresh_unreviewed' if key in TRIAL else None,
            shares_source_with_calibrator=s['source'] in {r['cue'].split('-')[0] for r in accepted},
            comparison_only=s['comparison_only'],source_settings=s,features=f,
            prediction=p if status in ('pending','comparison_only_pending') else None,
            alternative=alt if status in ('pending','comparison_only_pending') else None,
            approved_render=approved.get(key)))
        print(key,status,'end',round(f['last_half_second_dbfs'],1),'flux',round(f['spectral_flux_p90'],2),'pitch',round(f['pitch_class_change_p90'],2),'prediction',p['family'],flush=True)
    result=dict(schema=1,kind='preregistered-cue-treatment-predictions',rule_version=1,
        no_trial_rendering_before_registration=True,trial_cues=TRIAL,immutable_inputs=pins,
        constraints='Exactly six trial cues, one primary each, alternatives on S07-c/S12-2 only. Natural default; no freeze causal claim from quiet accepted endpoints. S14 comparison only, never trial.',
        rules=['Endpoint below−65dBFS and >15dB drop: subtle post-fader natural4.5s.',
               'Active endpoint >−50dBFS, fade<2s: established−14dB room/pre-ending send; extend only provisional fade to2.2s.',
               'Fade>=3.5s: post-fader natural6s if high activity, otherwise7s;−20dB if source already drops>10dB, otherwise−17dB.',
               'Other: post-fader−16dB/6s if high activity, else−17dB/6.5s (7.5s for >45s excerpt).',
               'High activity is positive100ms rise p90>2dB OR spectral-flux p90>0.45; thresholds are heuristic, not learned.',
               'No primary freeze: proxies do not verify coherent harmony; accepted quiet freeze endings are causally confounded.'],
        calibration_limit='Five different accepted combinations, plus separate S05-main reference. No fitted weights, probabilities, accuracy or leave-one-out claim.',
        evaluation='Record user outcomes in a new file; do not edit these predictions. Two known defects and four fresh excerpts evaluated separately; S07/S12 share sources with calibrators.',entries=entries)
    LEDGER.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args();survey()
