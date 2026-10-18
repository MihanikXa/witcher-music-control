"""Exact approved waveform/tail proof for uninterrupted re-entry controls."""
import argparse
import json
from pathlib import Path
import wave

import numpy as np
from scipy import signal
from sparse_reentry_pilot import PRIOR
from sparse_reentry_measure import verified_pcm
from white_orchard_prepare import build_path,digest


def compare(actual,expected):
    if actual.shape!=expected.shape:raise ValueError('Incomplete phrase/tail PCM')
    error=actual.astype(float)-expected
    return dict(maximum_error_pcm16=float(np.max(np.abs(error))),
                rms_error_pcm16=float(np.sqrt(np.mean(error*error))))


def proof(path,initial_rest):
    if initial_rest not in (0,30):raise ValueError('Only the two declared cycle layouts')
    source=PRIOR/'media/WMC_S04a_approved.wav'
    if digest(source)!='5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc':raise ValueError('Approved PCM changed')
    x,metadata=verified_pcm(path)
    if metadata['rate']!=48000 or metadata['channels']<2:raise ValueError('Unsupported Recorder rate/channels')
    with wave.open(str(source),'rb') as w:
        if w.getparams()[:3]!=(2,2,48000):raise ValueError('Wrong source format')
        y=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
    rate=48000;gain=10**(-18.996625900268555/20)
    def locate(search_lo,search_hi,reference_lo,reference_hi):
        ref=y[round(reference_lo*rate):round(reference_hi*rate),0].astype(float)
        search=x[round(search_lo*rate):round(search_hi*rate),0].astype(float)
        corr=signal.correlate(search,ref,method='fft')
        lag=signal.correlation_lags(len(search),len(ref))[np.argmax(corr)]
        return round(search_lo*rate)+int(lag)-round(reference_lo*rate)
    first=locate(initial_rest,initial_rest+4,0,2)
    second=locate(initial_rest+75,initial_rest+85,20,21)
    first_checks=[]
    for lo,hi in [(4,4.5),(20,25),(30.85,33),(33,40.85)]:
        a,b=round(lo*rate),round(hi*rate)
        first_checks.append(dict(source_from=lo,source_to=hi,**compare(x[first+a:first+b,:2],y[a:b].astype(float)*gain)))
    complete=compare(x[second:second+len(y),:2],y.astype(float)*gain)
    extra_zero=bool(np.all(x[second:second+len(y),2:]==0))
    quiet=x[first+round(41.1*rate):second-round(.25*rate)]
    quiet_pass=len(quiet)>15*rate and bool(np.all(quiet==0))
    initial_zero=bool(np.all(x[:initial_rest*rate]==0))
    first_pass=all(c['maximum_error_pcm16']<2 for c in first_checks)
    passed=first_pass and complete['maximum_error_pcm16']<2 and extra_zero and quiet_pass and initial_zero and metadata['peak']<32767
    return dict(passed=passed,pcm=metadata,first_offset_frames=first,second_offset_frames=second,
                first_offset_seconds=first/rate,second_offset_seconds=second/rate,
                cadence_seconds=(second-first)/rate,expected_gain_db=-18.996625900268555,
                first_checks=first_checks,complete_second_phrase=complete,
                complete_source_frames=len(y),extra_channels_zero=extra_zero,allocated_tail_then_rest_zero=quiet_pass,
                initial_rest_zero=initial_zero,
                timing_note='Recorder clock, not event/action wall clock. Initial rest is intentional native playback, not an audition wrapper.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wav',type=Path,required=True);p.add_argument('--initial-rest',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    result=proof(a.wav,a.initial_rest);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('pcm','first_checks')}))
    if not result['passed']:raise SystemExit(1)
