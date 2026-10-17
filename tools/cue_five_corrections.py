"""Bounded report83 private corrections. Existing accepted audio is read-only."""
import argparse
import copy
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from cue_remainder_batch import (REPO, RATE, read, level, rel, load_source,
    check_pins, technical, page as batch_page, ending_rows)
from cue_freeze_dsp import render_continuous, dry_envelope, envelope_windows
from cue_tail_v2 import write_pcm, svg
from white_orchard_prepare import digest, build_path

OLD=REPO/'build/music-material-selection/remainder-batch-v1'
PLAN=REPO/'research/84-five-cue-correction-plan.json'
IDS=['S04-a','S16-1','S18-2','S14-1','S14-2']


def validate_settings(key,s,prior):
    if key not in IDS or s['cue']!=key:raise ValueError('Unapproved cue')
    if s['comparison_only'] or s['treatment']!='natural_decay':raise ValueError('Current policy/treatment')
    expected={'S04-a':(3.15,34.),'S16-1':(0.,42.3),'S18-2':(61.,100.8),
              'S14-1':(0.,64.5),'S14-2':(64.5,132.)}[key]
    if (s['source_in'],s['source_out'])!=expected:raise ValueError('Unapproved source clock')
    if not s['source_in']<s['dry_fade'][0]<s['dry_fade'][1]==s['source_out']:raise ValueError('Invalid fade')
    if key=='S04-a':
        for k in ('dry_fade','rt60','continuous_wet_db','highpass_hz','lowpass_hz','fade_in'):
            if s[k]!=prior['settings'][k]:raise ValueError('Preferred ending changed')
        if s['send_policy']!='pre_ending_fade':raise ValueError('Preferred C send changed')
    if key=='S18-2' and s['source_out']>=101:raise ValueError('Rejected section included')
    if key=='S16-1' and s['source_out']-s['dry_fade'][0]<6:raise ValueError('Release not extended')
    if key.startswith('S14') and not (80<=s['highpass_hz']<=120 and s['rt60']>=8):
        raise ValueError('Missing low-aware long room')


def pins():
    selected=read(REPO/'research/82-accepted-private-cue-selections.json')
    p={x['file']:x['sha256'] for x in selected['selections']}
    if len(p)!=18:raise ValueError('Expected18 accepted selections')
    p['build/music-material-selection/cue-edits-v1/audio/S05-main-B.wav']='1f267727b6d531200099bf70656218e364de7982e1a2e508031cf9f8f8c90c35'
    for f in ['research/69-treatment-predictions.json','research/81-remainder-batch-plan.json',
              'research/82-user-remainder-cue-decisions.json','research/82-accepted-private-cue-selections.json',
              'research/83-five-cue-targeted-corrections-handoff.md',rel(OLD/'renders.json',REPO)]:p[f]=digest(REPO/f)
    check_pins(p)
    return p


def measured(source,lo,hi):
    # Stereo energy, never a mono sum. Fine windows retained near each problem.
    crop=source[round(lo*RATE):round(hi*RATE)]
    result={'rows':ending_rows({'source':crop},lo,hi,hi-lo-.05),'bands':{}}
    for a,b in [(30,120),(120,250),(250,500),(500,1000),(1000,4000)]:
        x=signal.sosfilt(signal.butter(4,[a,b],btype='bandpass',fs=RATE,output='sos'),crop,axis=0)
        result['bands'][f'{a}-{b}Hz']={'start_source':lo,'window':.05,
            'dbfs':(20*np.log10(np.maximum(envelope_windows(x),1e-12))).tolist()}
    return result


def make_plan():
    if PLAN.exists():raise FileExistsError('Preserve recorded plan')
    old=read(OLD/'renders.json');entries=[]
    choices={
      'S04-a':dict(source_in=3.15,send_policy='pre_ending_fade'),
      'S16-1':dict(dry_fade=[35.,42.3],rt60=8.,continuous_wet_db=-14),
      'S18-2':dict(source_out=100.8,dry_fade=[97.5,100.8]),
      'S14-1':dict(highpass_hz=80,rt60=8.5,continuous_wet_db=-13),
      'S14-2':dict(highpass_hz=80,rt60=9.,continuous_wet_db=-14,send_policy='post_fader')}
    reasons={
      'S04-a':'Original remains near−92dBFS through source3.15s. Remove only this prefix, preserve the entire preferred C PCM suffix exactly, including its ending. Standard2s context stays.',
      'S16-1':'Original stays roughly−25dBFS through42.3s. Old2.2s fade causes the disappearance. Begin a7.3s smooth release at35s, with continuously established8s post-fader room; no wet hold.',
      'S18-2':'Source declines from about−15dBFS at98s toward−25dBFS at100s before the new rise after101s. Proposed97.5–100.8s fade ends before the rejected return; no later samples feed dry or room. Cadence remains a listening decision.',
      'S14-1':'Source60–64.5s carries30–120Hz energy around−25.6dBFS, stronger than120–250Hz. Lower send HP250→80Hz and8.5s real decay carry more low-note energy. Fixed−13dB pre-fade wet target; no late gain automation.',
      'S14-2':'Original125–132s low band dominates; recorded release falls rapidly after130.5s. Establish restrained80Hz–3kHz9s room throughout, fed only by the current passage and post-fader source. Preserve original near-silent20ms guard and constant headroom reduction.'}
    for key in IDS:
        prior=next(c for c in old['cues'] if c['settings']['cue']==key)
        s=copy.deepcopy(prior['settings']);s.update(choices[key]);s.update(comparison_only=False,treatment='natural_decay')
        s['assumption']=reasons[key];s['reasoning']=[reasons[key]];s['variants']=['B'];s['compare']=True
        src=(OLD/prior['original_reference']).resolve();source=load_source(str(src),prior['source_preview_sha256'])
        lo,hi={'S04-a':(0,6),'S16-1':(33,42.3),'S18-2':(94,103),'S14-1':(60,64.5),'S14-2':(125,132)}[key]
        validate_settings(key,s,prior)
        entries.append(dict(cue=key,settings=s,headroom_gain=.85 if key.startswith('S14') else 1.,reference_variant='C' if key=='S04-a' else 'B',
            source_file=rel(src,REPO),source_sha256=digest(src),reason=reasons[key],source_measurements=measured(source,lo,hi)))
    plan=dict(schema=1,kind='five-target-correction-plan',immutable_inputs=pins(),cues=entries,
        policy='S14 eligible for future Sparse consideration per user; neither render accepted; authored routing protected; private only.',
        subjective_evaluation=False,alternatives=0)
    PLAN.write_text(json.dumps(plan,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def crop_preferred_pcm(original,target,trim):
    """Drop source prefix only, preserving every remaining preferred PCM frame."""
    with wave.open(str(original),'rb') as r:
        params=r.getparams();frames=r.readframes(r.getnframes())
    if params.nchannels!=2 or params.sampwidth!=2 or params.framerate!=RATE:raise ValueError('Expected stereo PCM16')
    cut=round(trim*RATE)*4;lead=2*RATE*4
    payload=frames[:lead]+frames[lead+cut:]
    with wave.open(str(target),'wb') as w:w.setparams(params);w.writeframes(payload)
    return payload


def page(m):
    text=batch_page(m)
    start=text.index('<h1>Remaining cue auditions</h1>');end=text.index('<header>',start)
    text=text[:start]+'''<h1>Five targeted corrections</h1><p>Compare unchanged A with corrected B. All five new versions are pending listening. No freeze or diagnostic alternatives. Standard2s lead and3s final silence are listening context. Source clocks are shown per card. S14 is eligible for future Sparse consideration; authored routing and rights remain protected.</p><p>S04-a: hear the entrance. S16-1: hear the longer release. S18-2: confirm the earlier musical stop. S14: listen for sustained low-note decay without a separate room swell.</p>'''+text[end:]
    text=re.sub(r'<section class="restricted">.*?</section>','',text,flags=re.S)
    text=text.replace('WMC — remainder batch','WMC — five targeted corrections').replace('wmc-remainder81-','wmc-corrections84-')
    text=text.replace('Hear last8s + tail','Hear problem area + tail')
    text=text.replace("x.kind='remainder-batch-private-outcomes'","x.kind='five-cue-correction-outcomes'")
    text=text.replace("x.scope='Private audition only; S14 Keep is comparison-only, never normal reuse approval'","x.scope='Private listening; S14 eligible for future Sparse consideration, authored routing protected; no distribution or integration approval'")
    text=text.replace("'pending private cue listening decision'","'pending private cue listening decision; S14 future-use policy per report82'")
    # Meaningful comparison time follows absolute source clock across the S04 trim.
    text=text.replace('v.onchange=()=>{const t=card.querySelector',"let previousVariant='B';v.onchange=()=>{const prior=cue.renders[previousVariant],next=cue.renders[v.value];const shift=(prior.source_in??cue.settings.source_in)-(next.source_in??cue.settings.source_in);previousVariant=v.value;const t=card.querySelector")
    text=text.replace("checked?a.currentTime:0,playing", "checked?Math.max(0,a.currentTime+shift):0,playing")
    # Ending button reaches before the actual problem, not only2s before stop.
    text=text.replace('manifest.lead_silence+Math.max(0,cue.proof.freeze_relative-2)',"Math.max(2,cue.problem_source-((cue.renders[v.value].source_in)??cue.settings.source_in)+2-5)")
    return text


def build(output,resume=False,next_only=False):
    output=build_path(output)
    if output.exists() and not resume:raise FileExistsError('Fresh output required')
    plan=read(PLAN);check_pins(plan['immutable_inputs']);old=read(OLD/'renders.json')
    if resume:
        m=read(output/'renders.json')
        if m['plan_sha256']!=digest(PLAN) or [c['settings']['cue'] for c in m['cues']]!=IDS[:len(m['cues'])]:raise ValueError('Resume plan/prefix changed')
        for c,cfg in zip(m['cues'],plan['cues']):
            if c['settings']!=cfg['settings']:raise ValueError('Completed settings changed')
            for r in c['renders'].values():
                if digest(output/r['file'])!=r['qa']['sha256']:raise ValueError('Completed audio changed')
    else:
        output.mkdir();[(output/p).mkdir() for p in ['audio','analysis','envelopes']]
        m=dict(schema=1,kind='five-cue-targeted-corrections',plan_sha256=digest(PLAN),
        feedback_sha256=digest(REPO/'research/82-user-remainder-cue-decisions.json'),
        source_metadata_sha256=digest(OLD/'renders.json'),primary_variant='B',lead_silence=2,trail_silence=3,
        cues=[],references=[],subjectively_listened=False,browser_playback_verified=False)
    for cfg in plan['cues']:
        if any(c['settings']['cue']==cfg['cue'] for c in m['cues']):continue
        key=cfg['cue'];s=cfg['settings'];prior=next(c for c in old['cues'] if c['settings']['cue']==key)
        validate_settings(key,s,prior);source=load_source(str(REPO/cfg['source_file']),cfg['source_sha256'])
        original=OLD/prior['renders'][cfg['reference_variant']]['file'];path=output/'audio'/f'{key}-B.wav'
        old_s=copy.deepcopy(prior['settings'])
        old_stop=(old_s['source_out']-old_s['source_in'])
        old_audio=load_source(str(original),digest(original)).copy()
        # Preserve original decoded output, reconstruct dry and residual wet for diagnostics.
        raw=old_audio[2*RATE:-3*RATE];n=round(old_stop*RATE);env=dry_envelope(n,RATE,old_s['fade_in'],old_s['dry_fade'][0]-old_s['source_in'],old_stop)
        d=np.zeros_like(raw);d[:n]=source[round(old_s['source_in']*RATE):round(old_s['source_out']*RATE)]*env[:,None]*prior['proofs'][cfg['reference_variant']].get('headroom_gain',1.)
        old_components=dict(dry=d,wet=raw-d,source_envelope=env)
        oldp=copy.deepcopy(prior['proofs'][cfg['reference_variant']]);oldp.update(source_start_frame=round(old_s['source_in']*RATE),source_end_frame=round(old_s['source_out']*RATE))
        old_t=technical(source,old_s,old_audio,oldp,old_components)
        if key=='S04-a':
            crop_preferred_pcm(original,path,s['source_in']);audio=load_source(str(path),digest(path)).copy()
            trim=round(s['source_in']*RATE);raw=audio[2*RATE:-3*RATE]
            components=dict(dry=d[trim:],wet=(old_audio[2*RATE:-3*RATE]-d)[trim:],source_envelope=env[trim:])
            p=copy.deepcopy(oldp);p.update(source_start_frame=trim,dry_seconds=s['source_out']-s['source_in'],dry_stop_relative=s['source_out']-s['source_in'],output_seconds=len(audio)/RATE,
                windows_50ms={k:envelope_windows(v).tolist() for k,v in [('dry',components['dry']),('wet',components['wet']),('combined',raw)]},pcm_suffix_exact=True)
            qa=dict(sha256=digest(path),seconds=len(audio)/RATE,channels=2,rate=RATE,peak=float(np.max(np.abs(audio))),clipped_samples=0,decoder_exact=True)
        else:
            headroom=cfg.get('headroom_gain',1.)
            audio,p,components=render_continuous(source if headroom==1 else source*headroom,s,s['rt60'])
            p['headroom_gain']=headroom
            if path.exists():
                # A post-write diagnostic failure may leave a valid, immutable render.
                previous=load_source(str(path),digest(path))
                expected=np.rint(audio*32767).astype('<i2').astype(float)/32768
                if not np.array_equal(previous,expected):raise ValueError('Existing render differs; never overwrite')
                qa=dict(sha256=digest(path),seconds=len(previous)/RATE,channels=2,rate=RATE,
                    peak=float(np.max(np.abs(previous))),clipped_samples=int(np.count_nonzero(np.abs(previous)>=32767/32768)),decoder_exact=True)
            else:qa=write_pcm(path,audio)
        # The established exact-source gate operates before headroom multiplication.
        # Pass the exact scaled input to avoid changing its strict byte/equality rule
        # merely for differing floating-point multiplication order.
        gain=p.get('headroom_gain',1.)
        t=technical(source if gain==1 else source*gain,s,audio,{**p,'headroom_gain':1.},components)
        t['source_measurement_gain']=gain
        # LF release measurements of components and actual sum, with causal filter context.
        bands={}
        start=max(0,round((s['source_out']-s['source_in']-6)*RATE))
        for a,b in [(30,120),(120,250),(250,500)]:
            bands[f'{a}-{b}Hz']={}
            for name,x in [('dry',components['dry']),('wet',components['wet']),('combined',audio[2*RATE:-3*RATE])]:
                y=signal.sosfilt(signal.butter(4,[a,b],btype='bandpass',fs=RATE,output='sos'),x[start:],axis=0)
                bands[f'{a}-{b}Hz'][name]={'source_start':s['source_in']+start/RATE,'window':.05,'dbfs':(20*np.log10(np.maximum(envelope_windows(y),1e-12))).tolist()}
        renders={'B':dict(file=rel(path,output),label='B — corrected, pending listening',qa=qa,source_in=s['source_in']),
                 'A':dict(file=rel(original,output),label='A — unchanged preferred previous render',qa=prior['renders'][cfg['reference_variant']]['qa'],source_in=old_s['source_in'])}
        c=dict(settings=s,comparison_only=False,reasoning=cfg['reason'],timing_authority='Report83 user correction; exact revised engineering settings provisional. Standard2s lead preserved.',
            source_identity=prior['source_identity'],excerpt_role=prior['excerpt_role'],original_reference=rel(REPO/cfg['source_file'],output),
            source_preview_sha256=cfg['source_sha256'],renders=renders,proofs={'B':p},technical={'B':t},
            proof=dict(output_seconds=p['output_seconds'],freeze_relative=p['dry_stop_relative']),
            problem_source={'S04-a':3.25,'S16-1':40.1,'S18-2':100.,'S14-1':63.,'S14-2':130.5}[key],
            onset_note=f"A source start {old_s['source_in']}s; B source start {s['source_in']}s. A/B switches follow source time.")
        analysis=dict(source=cfg['source_measurements'],previous=old_t,corrected=t,low_bands_corrected=bands,
            residual_wet_caveat='Previous wet reconstructed as decoded sum minus exact dry; includes PCM quantization, not a separate measured stem.')
        (output/'analysis'/f'{key}.json').write_text(json.dumps(analysis,allow_nan=False)+'\n',encoding='utf-8')
        (output/'envelopes'/f'{key}.svg').write_text(svg(key,{'B':p}),encoding='utf-8')
        m['cues'].append(c);(output/'renders.json').write_text(json.dumps(m,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
        print(json.dumps(dict(cue=key,seconds=qa['seconds'],post_dbfs=p['post_stop_first_second_dbfs'] if key!='S04-a' else None,warnings=t['warnings'])),flush=True)
        if next_only:break
    if len(m['cues'])<5:
        check_pins(plan['immutable_inputs'])
        return dict(completed=len(m['cues']),status='Exact completed prefix preserved; resume in a fresh process')
    (output/'index.html').write_text(page(m),encoding='utf-8');check_pins(plan['immutable_inputs'])
    return verify(output)


def verify(output):
    output=build_path(output);plan=read(PLAN);check_pins(plan['immutable_inputs']);m=read(output/'renders.json')
    if [c['settings']['cue'] for c in m['cues']]!=IDS or m['plan_sha256']!=digest(PLAN):raise ValueError('Wrong cue/plan')
    results=[]
    for c,cfg in zip(m['cues'],plan['cues']):
        s=c['settings'];r=c['renders']['B'];p=c['proofs']['B']
        if s!=cfg['settings']:raise ValueError('Settings drift')
        if digest(REPO/cfg['source_file'])!=cfg['source_sha256']:raise ValueError('Original source changed')
        if digest(output/c['renders']['A']['file'])!=c['renders']['A']['qa']['sha256']:raise ValueError('Historical reference changed')
        x=load_source(str(output/r['file']),r['qa']['sha256'])
        if x.shape!=(round(r['qa']['seconds']*RATE),2) or not np.isfinite(x).all() or np.max(np.abs(x))>=.97:raise ValueError('PCM integrity')
        if np.any(x[:2*RATE]) or np.any(x[-3*RATE:]):raise ValueError('Context silence')
        if p['source_start_frame']!=round(s['source_in']*RATE) or p['source_end_frame']!=round(s['source_out']*RATE):raise ValueError('Source clocks')
        if s['cue']=='S04-a':
            a=load_source(str(output/c['renders']['A']['file']),c['renders']['A']['qa']['sha256'])
            if not np.array_equal(x[2*RATE:],a[round((2+s['source_in'])*RATE):]):raise ValueError('Preferred C suffix changed')
        else:
            if p['freeze'] or p['cleanup_peak_dbfs']>=-100 or p['send_policy']!='post_fader':raise ValueError('Unexpected tail control')
            if p['dry_stop_max_sample_delta']>.02:raise ValueError('Ending discontinuity')
            if p.get('headroom_gain',1.)!=cfg['headroom_gain']:raise ValueError('Unexpected headroom gain')
            expected=np.array(p['windows_50ms']['combined'])*32767/32768
            if np.max(np.abs(envelope_windows(x[2*RATE:-3*RATE])-expected))>1.6e-5:raise ValueError('PCM envelope drift')
        stop=round((2+s['source_out']-s['source_in'])*RATE)
        post=[level(x[stop+i*RATE:stop+(i+1)*RATE]) for i in range(min(10,int(len(x)/RATE)-int(stop/RATE)-3))]
        results.append(dict(cue=s['cue'],sha256=r['qa']['sha256'],settings=s,post_source_seconds_dbfs=post,warnings=c['technical']['B']['warnings'],cleanup_peak_dbfs=p['cleanup_peak_dbfs']))
    if len(list((output/'audio').glob('*.wav')))!=5:raise ValueError('Expected five new primaries')
    for path in re.findall(r'(?:src|href)="([^"]+)"',(output/'index.html').read_text(encoding='utf-8')):
        if '://' in path or not (output/path).is_file():raise ValueError('Missing/nonlocal link')
    report=dict(technical_integrity_passed=True,accepted18_plus_separate_main_preserved=True,primaries=5,alternatives=0,subjective_success=False,results=results)
    (output/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report


def bounded_batch(output,resume=False):
    """One command/batch, fresh interpreter per cue to bound peak memory."""
    output=build_path(output)
    if output.exists() and not resume:raise FileExistsError('Fresh output required')
    for _ in IDS:
        complete=len(read(output/'renders.json')['cues']) if (output/'renders.json').exists() else 0
        if complete==5:break
        command=[sys.executable,str(Path(__file__).resolve()),'--output',str(output),'--next']
        if output.exists():command.append('--resume')
        subprocess.run(command,check=True)
    return verify(output)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',action='store_true');ap.add_argument('--output',type=Path);ap.add_argument('--verify',action='store_true');ap.add_argument('--resume',action='store_true');ap.add_argument('--next',action='store_true');a=ap.parse_args()
    if a.plan:make_plan()
    elif a.output:
        result=verify(a.output) if a.verify else (build(a.output,resume=a.resume,next_only=True) if a.next else bounded_batch(a.output,resume=a.resume))
        print(json.dumps(result))
    else:ap.error('Choose --plan or --output')
