"""Read-only measured review of one deliberately rejected Stinger hypothesis.

The capture/PCM checks can pass while the protected-request requirement fails.
No evidence is an engine acknowledgment suitable for a gameplay controller.
"""
import json
from pathlib import Path
import wave
import xml.etree.ElementTree as ET
import numpy as np
from scipy import signal

from sparse_approved_cue import REPO, MUSIC, SOURCE, read, verify_accepted
from sparse_request_probe import SOURCE_SHA
from sparse_stinger_probe import validate_source
from sparse_reentry_measure import summarize, verified_pcm
from white_orchard_prepare import digest

ROOT=REPO/'build/sparse-interface-prerequisites-v1'
PROJECT=ROOT/'wwise/candidate/validation'


def source_gate():
    p=PROJECT;manifest=read(p/'input-manifest.json')
    before=ET.parse(p/'stinger-before.xml').getroot();after=ET.parse(p/MUSIC).getroot()
    gate=validate_source(before,after)
    if digest(p/'stinger-before.xml')!=SOURCE_SHA:raise ValueError('Retained rest-first source drift')
    units=[x for x in manifest['inputs'] if x['relative_path'].endswith('.wwu')]
    if len(units)!=1508 or len(list(p.rglob('*.wwu')))!=1508:raise ValueError('Incomplete context')
    for row in units:
        rel=Path(row['relative_path'])
        if digest(SOURCE/rel)!=row['sha256']:raise ValueError('Installed source drift')
        if rel!=MUSIC and digest(p/rel)!=row['sha256']:raise ValueError('Unapproved work-unit change')
    for row in manifest['originals']:
        if digest(p/row['relative_path'])!=row['sha256']:raise ValueError('Original audio drift')
    cue=p/'Originals/SFX/WMC_S04a_approved.wav'
    if digest(cue)!='5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc':raise ValueError('Approved cue drift')
    verify_accepted()
    return dict(**gate,work_units=1508,event_work_units=len(list((p/'Events').rglob('*.wwu'))),
        original_audio=len(manifest['originals']),cue_sha256=digest(cue),approved24_exact=True,
        globals_and_events_on_disk_exact=True,music_sha256=digest(p/MUSIC))


def pcm_identity(path):
    x,info=verified_pcm(path)
    with wave.open(str(PROJECT/'Originals/SFX/WMC_S04a_approved.wav'),'rb') as w:
        if (w.getnchannels(),w.getframerate(),w.getsampwidth())!=(2,48000,2):raise ValueError('Unexpected cue format')
        y=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
    rate=48000;ref=y[4*rate:6*rate,0].astype(float)
    corr=signal.correlate(x[:,0].astype(float),ref,method='fft')
    offset=int(signal.correlation_lags(len(x),len(ref))[np.argmax(corr)])-4*rate
    if offset<0 or offset+len(y)>len(x):raise ValueError('Incomplete requested cue')
    actual=x[offset:offset+len(y),:2].astype(float)
    expected=y.astype(float)*10**(-18.996625900268555/20)
    error=actual-expected;maximum=float(np.max(np.abs(error)))
    if maximum>1.1 or np.any(x[:,2:]):raise ValueError('Cue/tail PCM identity failed')
    if np.any(x[offset+len(y)+rate:]):raise ValueError('Unexpected playback after completed tail')
    return dict(passed=True,source_frames=len(y),source_seconds=len(y)/rate,
        recorder_offset_frames=offset,recorder_offset_seconds=offset/rate,
        expected_native_gain_db=-18.996625900268555,maximum_pcm16_error=maximum,
        rms_pcm16_error=float(np.sqrt(np.mean(error*error))),other_channels_zero=True,
        complete_baked_tail=True,post_tail_rest_exact_zero=True,recorder_sha256=info['sha256'])


def audible_overlap(pipelines, left, right):
    spans=[]
    for a in pipelines:
        for b in pipelines:
            if a['role']!=left or b['role']!=right:continue
            if any(v is None for v in (a['audible_first'],a['audible_last'],b['audible_first'],b['audible_last'])):continue
            lo=max(a['audible_first'],b['audible_first']);hi=min(a['audible_last'],b['audible_last'])
            if hi>lo:spans.append([lo,hi])
    return spans


def review():
    sg=source_gate();source=ET.parse(PROJECT/'authored-music.xml').getroot();cases=[];artifacts={}
    for label in ('stinger-captures','stinger-followup','stinger-expiry'):
        path=PROJECT/label/'results.json';raw=read(path)
        if not raw['complete'] or raw.get('error') or raw['cleanup_errors']:raise ValueError('Incomplete capture')
        receipt=PROJECT/('stinger-lifecycle.json' if label=='stinger-captures' else label+'-lifecycle.json')
        life=read(receipt)
        if life.get('error') or life['cleanup_errors'] or not life['music_source_exact']:raise ValueError('Lifecycle failure')
        artifacts[str(path.relative_to(REPO))]=digest(path)
        artifacts[str(receipt.relative_to(REPO))]=digest(receipt)
        for case in raw['cases']:
            z=summarize(case,source);_,pcm=verified_pcm(PROJECT/label/(case['case']+'.wav'))
            cases.append(dict(case=case['case'],events=case['events'],rtpcs=z['rtpcs'],
                pipelines=[{k:v[k] for k in ('pipeline','role','ids','first','last','peak','audible_first','audible_last')} for v in z['pipelines']],
                pcm=pcm,complete=case['complete']))
    by={c['case']:c for c in cases}
    cue=lambda name:[v for v in by[name]['pipelines'] if v['role']=='cue']
    if cue('no-request') or any(by['no-request']['pcm']['rms50ms']):raise ValueError('Off-policy control not silent')
    if len(cue('valid-request'))!=1 or len(cue('duplicate-request'))!=1:raise ValueError('Request/deduplication result changed')
    # Fail if evidence no longer establishes this specific defect. Never invert
    # this into a passing safety gate or suppress the failed context captures.
    if not cue('combat-request') or not cue('dialogue-request'):raise ValueError('Expected rejected-hypothesis evidence absent')
    if not cue('late-outro-request'):raise ValueError('Expected native outro-overlap counterexample absent')
    overlaps={name:audible_overlap(by[name]['pipelines'],'cue',role) for name,role in
              [('combat-request','combat'),('late-outro-request','outro'),('active-then-combat','combat')]}
    if not all(overlaps.values()):raise ValueError('Unsafe overlap counterexample absent')
    if not any(v['audible_last'] and v['audible_last']>13 for v in cue('cancel-active')):
        raise ValueError('Active cancellation counterexample absent')
    if not any(v['audible_first'] and v['audible_first']>18 for v in cue('cancel-ineligible')):
        raise ValueError('Latent cancellation counterexample absent')
    identity=pcm_identity(PROJECT/'stinger-captures/valid-request.wav')
    return dict(schema=1,source=sg,positive_pcm=identity,cases=cases,artifacts=artifacts,
        unsafe_overlap_intervals=overlaps,
        approach_count=1,protected_request_proven=False,retail_tested=False,new_banks_generated=False,
        finding='Request starts the exact cue but permits combat/outro overlap and stale dialogue requests. Reject as protected gateway.')


if __name__=='__main__':
    out=ROOT/'review.json'
    if out.exists():raise FileExistsError('Preserve earlier evidence')
    result=review();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Positive requested cue PCM proven; protected gateway FAILED; evidence preserved.')
