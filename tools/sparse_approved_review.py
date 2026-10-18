"""Read-only playback evidence for the single approved cue, not retail certification."""
import argparse
import json
import math
from pathlib import Path
import statistics
import wave
import xml.etree.ElementTree as ET

import numpy as np
from scipy import signal

from sparse_approved_cue import ROOT,read,verify_accepted
from white_orchard_prepare import digest
from white_orchard_fade_measure import pcm
from white_orchard_sparse_measure import case_summary,intervals
from white_orchard_sparse_review import matching


def recorder(path):
    data,ch,rate=pcm(path);x=np.frombuffer(data,dtype=np.int16).reshape(-1,ch)
    rows=[]
    for a in range(0,len(x),rate//20):
        v=x[a:a+rate//20].astype(float)/32768
        rows.append(float(np.sqrt(np.mean(v*v))))
    return x,dict(sha256=digest(path),seconds=len(x)/rate,channels=ch,rate=rate,
        peak=int(np.max(np.abs(x.astype(np.int32)))),rms50ms=rows,
        exact_zero_intervals=intervals([i*.05 for i,v in enumerate(rows) if v==0],.051))


def cue_pcm_proof(path):
    x,out=recorder(path)
    with wave.open(str(ROOT/'media/WMC_S04a_approved.wav'),'rb') as w:y=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
    rate=48000
    correlation=signal.correlate(x[:4*rate,0].astype(float),y[:2*rate,0].astype(float),method='fft')
    offset=int(signal.correlation_lags(4*rate,2*rate)[np.argmax(correlation)])
    out['source_offset_frames']=offset;out['source_offset_seconds']=offset/rate
    # Music100, after native entry fade. Quantization is allowed; identity/tail cuts are not.
    checks=[]
    gain=10**(-18.996625900268555/20)
    for lo,hi in [(4,4.5),(20,25),(30.85,33),(33,40.85)]:
        a,b=round(lo*rate),round(hi*rate);actual=x[a+offset:b+offset,:2].astype(float);expected=y[a:b].astype(float)*gain
        error=actual-expected
        checks.append(dict(source_from=lo,source_to=hi,maximum_error_pcm16=float(np.max(np.abs(error))),
            rms_error_pcm16=float(np.sqrt(np.mean(error*error))),stereo_reference_scaled_rms=float(np.sqrt(np.mean(expected*expected))),
            actual_rms_dbfs=float(20*np.log10(max(float(np.sqrt(np.mean(actual*actual)))/32768,1e-12)))))
    out['approved_pcm_comparisons']=checks;out['expected_native_gain_db']=-18.996625900268555
    # First phrase includes intentional Music-master changes. Establish complete
    # waveform identity independently on the second phrase, with steady100 gain.
    ref=y[20*rate:21*rate,0].astype(float);search=x[75*rate:85*rate,0].astype(float)
    corr=signal.correlate(search,ref,method='fft');lag=signal.correlation_lags(len(search),len(ref))[np.argmax(corr)]
    second=75*rate+int(lag)-20*rate
    expected=y.astype(float)*gain;actual=x[second:second+len(y),:2].astype(float)
    if actual.shape!=expected.shape:raise ValueError('Second phrase/tail incomplete')
    out['complete_second_phrase']=dict(offset_frames=second,offset_seconds=second/rate,
        maximum_error_pcm16=float(np.max(np.abs(actual-expected))),
        rms_error_pcm16=float(np.sqrt(np.mean((actual-expected)**2))),
        source_frames=len(y),silent_extra_channels=bool(np.all(x[second:second+len(y),2:]==0)))
    out['timing_caveat']='Recorder sample clock is not action-acceptance wall clock. First phrase source6–7s includes the deliberate master50 transition; full second phrase has steady master100.'
    # All channels must be zero well after the full source tail, before next entry.
    out['complete_tail_then_rest_zero']=bool(np.all(x[round((offset/rate+41)*rate):round((offset/rate+60)*rate)]==0))
    return out


def review(sparse_label='matrix-native-clock'):
    verify_accepted();gate=read(ROOT/'sparse/validation/approved-cue-source-gate.json');cue=gate['segment']['short_id']
    data={};evidence={};checks=[]
    def check(name,value):checks.append(dict(name=name,passed=bool(value)))
    for mode in ['native','minimal','sparse']:
        folders=[ROOT/mode/'validation'/'matrix-v1'] if mode!='sparse' else [ROOT/n/'validation'/sparse_label for n in ['sparse','sparse-b','sparse-c']]
        combined=[];fingerprints=set()
        for folder in folders:
            raw=read(folder/'results.json')
            check(mode+':'+folder.parent.parent.name+':complete-clean',raw['complete'] and not raw['cleanup_errors'] and not raw.get('error'))
            tree=ET.parse(folder.parent/'authored-music.xml');fingerprints.add(digest(folder.parent/'authored-music.xml'))
            summaries=[]
            for rawcase in raw['cases']:
                c=case_summary(rawcase,tree);c['capture_end_time']=rawcase['samples'][-1]['time'];c['capture_folder']=str(folder.relative_to(ROOT))
                _,c['pcm']=recorder(folder/(c['case']+'.wav'));summaries.append(c)
            (folder/'approved-cue-measurements.json').write_text(json.dumps(dict(cases=summaries),allow_nan=False)+'\n')
            combined.extend(summaries)
        from sparse_approved_capture import cases
        check(mode+':exact-case-coverage',len(combined)==len(cases()) and {c['case'] for c in combined}=={c['name'] for c in cases()})
        check(mode+':identical-worker-source',len(fingerprints)==1)
        data[mode]={c['case']:c for c in combined};evidence[mode]=combined
    selected={mode:matching(data[mode]['two-cycles'],cue if mode=='sparse' else 133462974) for mode in data}
    check('native-selected-audible',any(v['peak_db']>-30 for v in selected['native']))
    check('minimal-selected-suppressed',all(v['peak_db']<-200 for v in selected['minimal']))
    check('approved-cue-native-gain',any(abs(v['peak_db']+19)<.1 for v in selected['sparse']))
    voices=selected['sparse'];env=[p for v in voices for p in v['envelope']]
    first=[db for t,db in env if 4<t<7];half=[db for t,db in env if 10<t<14];last=[db for t,db in env if 20<t<25]
    check('master-100-50-100',first and half and last and abs(statistics.median(half)-statistics.median(first)+6.0206)<.1 and abs(statistics.median(last)-statistics.median(first))<.1)
    check('cue-recurrence',len(intervals([t for t,db in env]))>=3)
    quiet=matching(data['sparse']['two-cycles'],4111369)
    check('actual-native-rest-selected',quiet and max(t for v in quiet for t,db in v['envelope'])>115)
    audio=cue_pcm_proof(ROOT/'sparse/validation'/sparse_label/'two-cycles.wav')
    check('approved-PCM-and-tail-retained',all(v['maximum_error_pcm16']<2 for v in audio['approved_pcm_comparisons'])
        and audio['complete_second_phrase']['maximum_error_pcm16']<2 and audio['complete_second_phrase']['silent_extra_channels'])
    check('complete-tail-then-real-rest',audio['complete_tail_then_rest_zero'])
    combat={}
    for name in ['combat-music','combat-rest-early','combat-rest-late']:
        combat[name]={}
        for mode in data:
            c=data[mode][name];start=next(e['accepted'] for e in c['events'] if e['name']=='combat');returned=next(e['accepted'] for e in c['events'] if e['name']=='exploration')
            outro=matching(c,800050000);env=[p for v in outro for p in v['envelope']]
            body=[v for v in c['voices'].values() if '/village_combat/' in '/'.join(v['path'])]
            first=min((t for v in body for t,db in v['envelope']),default=math.inf)
            lo=min((t for t,db in env),default=math.inf);hi=max((t for t,db in env),default=-math.inf)
            middle=[db for t,db in env if lo+.5<t<hi-.5]
            row=dict(entry_latency=first-start,outro_first=lo,outro_last=hi,outro_span=hi-lo,
                outro_middle_db=statistics.median(middle) if middle else None,E_accepted=returned,
                threat_values={k:v for k,v in c['effective_rtpcs'].items() if 'threat_rating' in k})
            combat[name][mode]=row
            if mode!='minimal':
                check(name+':'+mode+':combat-response',0<=first-start<4.1)
                check(name+':'+mode+':complete-outro',4.3<hi-lo<5.5 and hi>returned+3 and hi<c['capture_end_time']-10)
                check(name+':'+mode+':outro-gain',middle and abs(statistics.median(middle)+19)<.1)
            check(name+':'+mode+':effective-threat',any(set(vals)=={0,35,100} for k,vals in row['threat_values'].items() if k.startswith('18446744073709551614:')))
            if mode=='sparse' and 'rest' in name:
                rests=matching(c,4111369)
                check(name+':rest-active-before-combat',any(start-1<t<start and db>-30 for v in rests for t,db in v['envelope']))
                check(name+':no-generic-restart-before-combat',not any(start<t<first and db>-90 for v in matching(c,cue) for t,db in v['envelope']))
    intensity={}
    for mode in data:
        case=data[mode]['combat-music'];intensity[mode]={}
        for layer in ['layer1','layer2']:
            voices=[v for v in case['voices'].values() if v['path'][-1].endswith(layer)]
            levels={}
            for state,lo,hi in [('0',10.5,11.8),('35',14.5,17),('100',21,25)]:
                values=[db for v in voices for t,db in v['envelope'] if lo<t<hi]
                levels[state]=statistics.median(values) if values else None
            intensity[mode][layer]=levels
        check(mode+':combat-intensity',intensity[mode]['layer1']['35'] is not None and abs(intensity[mode]['layer1']['35']+17)<.1
            and intensity[mode]['layer2']['0'] is not None and intensity[mode]['layer2']['0']<-200
            and all(intensity[mode]['layer2'][k] is not None and abs(intensity[mode]['layer2'][k]+19)<.1 for k in ['35','100']))
    for name in ['authored-phrase','authored-rest']:
        for mode in data:
            c=data[mode][name];auth=matching(c,933909186)
            check(name+':'+mode+':authored-audible',auth and max(v['peak_db'] for v in auth)>-30)
        check(name+':authored-native-level',abs(max(v['peak_db'] for v in matching(data['native'][name],933909186))-max(v['peak_db'] for v in matching(data['sparse'][name],933909186)))<.1)
        sparse=data['sparse'][name]
        first_cue=min(t for v in matching(sparse,cue) for t,db in v['envelope'])
        first_authored=min(t for v in matching(sparse,933909186) for t,db in v['envelope'])
        nominal_boundary=first_cue+(60.85 if name=='authored-rest' else 30.85)
        check(name+':authored-preempts-phrase-or-rest-boundary',first_authored<nominal_boundary)
    for name in ['gwent','protected-world']:
        n=max((v['peak_db'] for v in data['native'][name]['voices'].values()),default=-999)
        s=max((v['peak_db'] for v in data['sparse'][name]['voices'].values()),default=-999)
        check(name+':audible-native',n>-40 and abs(n-s)<.1)
    for name in ['place-daynight-music','place-daynight-rest']:
        case=data['sparse'][name];dialog=next(e['accepted'] for e in case['events'] if e['name']=='dialog_scene')
        mute=[db for v in matching(case,cue) for t,db in v['envelope'] if dialog+1.1<t<dialog+4.5]
        check(name+':ordinary-dialogue-suppressed',not mute or max(mute)<-200)
    result=dict(schema=1,passed=all(c['passed'] for c in checks),checks=checks,combat=combat,intensity=intensity,
        cue_pcm=audio,fixtures_only=True,retail_validated=False,bank_validated=False)
    (ROOT/'playback-review.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--label',default='matrix-native-clock');args=p.parse_args()
    from white_orchard_prepare import build_path
    ROOT=build_path(args.root)
    result=review(args.label);print(json.dumps(dict(passed=result['passed'],failed=[c for c in result['checks'] if not c['passed']])));raise SystemExit(0 if result['passed'] else 1)
