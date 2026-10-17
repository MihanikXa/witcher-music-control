"""Render only the preregistered six private cues; never alter predictions/outcomes."""
import argparse
from datetime import datetime,timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess

import numpy as np

from cue_edit_render import decode,page as legacy_page
from cue_freeze_dsp import RATE,render_continuous,envelope_windows,release_diagnostics,dry_envelope,validate_wet_control,ramp
from cue_handoff_v3 import handoff_metrics
from cue_tail_v2 import write_pcm,svg,LEGACY_DSP_KEYS
from cue_treatment_predict import REPO,V1,LEDGER,TRIAL
from white_orchard_prepare import digest,build_path


def registration():
    rel=LEDGER.relative_to(REPO).as_posix()
    commit=subprocess.run(['git','log','-1','--format=%H','--',rel],cwd=REPO,capture_output=True,check=True,text=True).stdout.strip()
    if not re.fullmatch('[a-f0-9]{40}',commit):raise ValueError('Ledger must be committed before trial rendering')
    blob=subprocess.run(['git','show',commit+':'+rel],cwd=REPO,capture_output=True,check=True).stdout
    raw=LEDGER.read_bytes()
    # Git autocrlf stores LF but this checkout uses CRLF. Permit ONLY that byte
    # translation, not JSON reserialization, changed settings, spaces or outcomes.
    if blob!=raw.replace(b'\r\n',b'\n'):raise ValueError('Working ledger differs from preregistered commit; do not backfill predictions')
    return dict(commit=commit,ledger_sha256=digest(LEDGER),git_blob_sha256=hashlib.sha256(blob).hexdigest(),
                comparison='exact bytes after CRLF-to-LF only',render_start_utc=datetime.now(timezone.utc).isoformat())


def verify_pins(ledger):
    for path,h in ledger['immutable_inputs'].items():
        if digest(REPO/path)!=h:raise ValueError('Immutable input changed: '+path)
    original=json.loads((V1/'renders.json').read_text())
    if digest(REPO/'build/music-material-selection/audition-v3/auditions.json')!=original['source_metadata_sha256']:
        raise ValueError('Original source catalog changed')
    if digest(REPO/'research/58-user-musical-material-audition-feedback.json')!=original['feedback_sha256']:
        raise ValueError('Original user feedback changed')


def spectral_metrics(x,fade_start,stop):
    """Coarse 250ms spectral jumps across whole handoff, not a timbre verdict."""
    begin=max(0,fade_start-1);end=min(len(x)/RATE,stop+1)
    n=RATE//4;vectors=[];centroids=[];levels=[]
    freq=np.fft.rfftfreq(n,1/RATE);window=np.hanning(n)
    for a in range(round(begin*RATE),round(end*RATE)-n+1,n):
        block=x[a:a+n];power=np.mean(abs(np.fft.rfft(block*window[:,None],axis=0))**2,axis=1)
        vectors.append(power/max(np.linalg.norm(power),1e-20));levels.append(float(20*np.log10(max(np.sqrt(np.mean(block**2)),1e-12))))
        centroids.append(float(np.sum(freq*power)/max(power.sum(),1e-20)))
    events=[dict(relative_seconds=begin+(i+1)*.25,distance=float(1-np.dot(a,b)))
            for i,(a,b,la,lb) in enumerate(zip(vectors,vectors[1:],levels,levels[1:])) if min(la,lb)>-75]
    jumps=[r['distance'] for r in events]
    return dict(window_seconds=.25,relative_start=begin,centroids_hz=centroids,rms_dbfs=levels,
                maximum_audible_spectral_distance=max(jumps,default=0),audible_spectral_events=events,
                review_only='Spectral change can be musical; no guaranteed timbral continuity from RMS or this proxy.')


def make_page(m):
    e=lambda x:html.escape(str(x),quote=True);cards=[]
    for c in m['cues']:
        s=c['settings'];p=c['prediction'];key=s['cue']
        watch=[];primary=c['technical']['B']
        if primary['handoff']['largest_adjacent_drop_db']>6:watch.append('Measured handoff is still relatively steep; listen for a separate room tail.')
        if primary['spectral']['maximum_audible_spectral_distance']>.65:watch.append('Measured spectral change is high; listen for an unnatural change of timbre or lost musical detail.')
        if c['proofs']['B']['post_stop_first_second_dbfs']<-70:watch.append('Primary post-source tail is very quiet; an alternate with more remaining energy is not automatically musically better.')
        watch_html='<p><b>Post-render technical watch (not an edited prediction):</b> '+e(' '.join(watch))+'</p>' if watch else ''
        options=''.join(f'<option value="{k}" {"selected" if k=="B" else ""}>{e(r["label"])}</option>' for k,r in c['renders'].items())
        prefs='<option value="">Undecided</option>'+''.join(f'<option value="{k}">{e(r["label"])}</option>' for k,r in c['renders'].items())
        questions=''
        for cls,title,choices in [('seamless','Seamless handoff?',['Unreviewed','Yes','No','Uncertain']),('resolution','Musically resolves?',['Unreviewed','Yes','No','Uncertain']),('tail','Tail balance',['Unreviewed','Appropriate','Too intrusive','Too short','Uncertain']),('artifact','Unexpected artifact?',['Unreviewed','None heard','Heard one — see notes','Uncertain'])]:
            questions+=f'<label>{title} <select class="{cls}">'+''.join(f'<option>{v}</option>' for v in choices)+'</select></label>'
        cards.append(f'''<article data-cue="{e(key)}"><h2>{e(key)} · {e(s['source_title'])}</h2>
<p><b>Precommitted prediction:</b> {e(p['family'])}; conventional RT60 {p['rt60']}s, {e(p['send_policy'])}, target {p['continuous_wet_db']}dB wet/dry. Confidence: provisional.</p>
<p>{e(' '.join(p['reasoning']))}</p><p>Source clock {s['source_in']:.3f}–{s['source_out']:.3f}s; predicted dry fade {p['dry_fade'][0]:.3f}–{p['dry_fade'][1]:.3f}s (old fade {p['original_dry_fade'][0]:.3f}–{p['original_dry_fade'][1]:.3f}s). Player includes2s lead and3s final silence.</p>
<p>Evaluation group: {e(c['trial_group'])}. {e(c['arrangement_caveat'])}</p>{watch_html}
<select class="variant">{options}</select><button class="play">Play from start</button><button class="ending">Hear ending</button><label><input type="checkbox" class="position" checked>Keep position on switch</label><audio controls preload="none" src="{e(c['renders']['B']['file'])}"></audio>
<p><b>Human outcome — separate from prediction</b></p><label>Verdict <select class="verdict"><option>Unreviewed</option><option>Keep</option><option>Adjust</option><option>Reject</option></select></label><label>Preferred treatment <select class="preferred">{prefs}</select></label><div>{questions}</div>
<textarea rows="3" placeholder="Variant and player timestamp; what did you hear? No need to judge the prediction itself."></textarea>
<details><summary>Original reference / immutable prediction / actual technical results</summary><p>{e(s['verbatim_notes'])}</p><p>Original recording has its own source clock, without extra lead.</p><audio controls preload="none" src="{e(c['original_reference'])}"></audio><a href="envelopes/{e(key)}.svg">50ms dry/wet/sum envelopes</a><pre>{e(json.dumps(dict(prediction=p,alternative=c['alternative'],technical=c['technical']),indent=2))}</pre></details></article>''')
    old=legacy_page(dict(cues=[],references=[],lead_silence=2,trail_silence=3))
    client=old[old.rfind('<script>'):].replace('wmc-cue61-','wmc-cue69-')
    client=client.replace("card.querySelector('textarea')],key=","card.querySelector('textarea'),...['seamless','resolution','tail','artifact'].map(k=>card.querySelector('.'+k))],key=")
    wrapper='''
const originalGather=gather;
gather=function(){const x=originalGather();x.kind='preregistered-treatment-trial-outcomes';x.prediction_registration=manifest.registration;
x.decisions.forEach(d=>{const c=cards.find(c=>c.dataset.cue===d.cue),p=cueData(c);d.frozen_prediction=p.prediction;d.trial_group=p.trial_group;d.evaluation=Object.fromEntries(['seamless','resolution','tail','artifact'].map(k=>[k,c.querySelector('.'+k).value]));});return x;};
'''
    client=client.replace('</script>',wrapper+'</script>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC — preregistered six-cue treatment trial</title>
<style>body{max-width:1050px;margin:25px auto;padding:0 18px;background:#151a1c;color:#e6e5df;font:17px/1.5 system-ui}article{border:1px solid #627371;border-radius:10px;padding:22px;margin:24px 0}audio,textarea{width:100%}button,select{padding:8px;margin:5px}label{display:inline-block}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}header{position:sticky;top:0;background:#151a1cf5;padding:10px}a{color:#9bd8ee}#json{height:200px}</style>
<h1>Six predicted endings — private listening trial</h1><p>All choices were committed before rendering. <b>B is the predicted primary</b>, not a claimed success. C is a single controlled alternative on only two cues; both are natural reverb. A, where present, is an unchanged earlier defective reference. Listen to B first, then the optional comparison. No new freeze was justified by these measurements.</p>
<p>Two known-problem cases and four unreviewed excerpts test different things. S07/S12 reuse compositions with an accepted different excerpt; they are not independent composition holdouts. Record human outcomes below; exporting does not overwrite the committed prediction ledger. The five accepted renders and S05-main remain untouched.</p>
<header><button id="stop">Stop all</button><button id="export">Export decisions JSON</button><button id="show">Show/copy JSON</button><span id="status"></span></header><details id="fallback"><summary>Copy export fallback</summary><textarea id="json" readonly></textarea></details>'''+''.join(cards)+'<script id="manifest" type="application/json">'+json.dumps(m).replace('<','\\u003c')+'</script>'+client


def build(output):
    reg=registration();ledger=json.loads(LEDGER.read_text());verify_pins(ledger)
    output=build_path(output)
    if output.exists():raise FileExistsError('Fresh output required')
    chosen=[next(e for e in ledger['entries'] if e['cue']==key) for key in TRIAL]
    if any(not e['trial'] or e['status']!='pending' or e['comparison_only'] for e in chosen):raise ValueError('Trial scope mismatch')
    output.mkdir();(output/'audio').mkdir();(output/'envelopes').mkdir()
    (output/'registration.json').write_text(json.dumps(reg,indent=2)+'\n')
    m=dict(schema=1,kind='preregistered-treatment-trial',registration=reg,plan_sha256=digest(LEDGER),
        feedback_sha256=digest(REPO/'research/58-user-musical-material-audition-feedback.json'),
        source_metadata_sha256=digest(REPO/'build/music-material-selection/audition-v3/auditions.json'),
        primary_variant='B',lead_silence=2,trail_silence=3,subjectively_listened=False,browser_playback_verified=False,cues=[],references=[])
    old=json.loads((V1/'renders.json').read_text())
    for entry in chosen:
        key=entry['cue'];prior=next(c for c in old['cues'] if c['settings']['cue']==key)
        sourcepath=(V1/prior['original_reference']).resolve()
        if digest(sourcepath)!=prior['source_preview_sha256']:raise ValueError('Source mismatch')
        source=decode(sourcepath);renders={};proofs={};technical={};gain=None
        begin=max(0,entry['prediction']['dry_fade'][0]-entry['source_settings']['source_in']-1)
        end=entry['prediction']['dry_fade'][1]-entry['source_settings']['source_in']
        for name,p in [('B',entry['prediction'])]+([('C',entry['alternative'])] if entry['alternative'] else []):
            s={**entry['source_settings'],**p}
            x,proof,components=render_continuous(source,s,p['rt60'],wet_gain=gain)
            if name=='B':gain=proof['wet_gain']
            proof['calibration_window_source_seconds']=[max(p['dry_fade'][0]-4,p['source_in']+1),p['dry_fade'][0]] if name=='B' else None
            proof['gain_policy']='calibrated before primary fade' if name=='B' else 'exact primary gain; not independently normalized'
            qa=write_pcm(output/'audio'/f'{key}-{name}.wav',x)
            a,b=proof['source_start_frame'],proof['source_end_frame']
            if not np.array_equal(components['dry'][:b-a],source[a:b]*components['source_envelope'][:,None]):raise ValueError('Dry source mismatch')
            renders[name]=dict(file=f'audio/{key}-{name}.wav',label='B — preregistered primary' if name=='B' else 'C — preregistered single-factor alternative',qa=qa)
            proofs[name]=proof
            dry=components['dry'];wet=components['wet'];combined=x[2*RATE:-3*RATE]
            technical[name]=dict(handoff=handoff_metrics(x,2+begin,2+end+1),spectral=spectral_metrics(combined,begin+1,end),
                dry_stop_sample_delta=proof['dry_stop_max_sample_delta'],cleanup_peak_dbfs=proof['cleanup_peak_dbfs'],
                post_source=proof['release_diagnostics'],dry_and_wet_spectral={k:spectral_metrics(v,begin+1,end) for k,v in [('dry',dry),('wet',wet)]},
                no_late_attack_hold_or_second_fade=proof['wet_control_checks'])
        if entry['trial_group']=='known_problem_note':
            v='C' if key=='S07-c' else 'B';ref=prior['renders'][v];path=V1/ref['file']
            if digest(path)!=ref['qa']['sha256']:raise ValueError('Old reference changed')
            renders['A']=dict(file=Path(os.path.relpath(path,output)).as_posix(),label=f'A — unchanged v1 {v}, known-defect reference',qa=ref['qa'])
            technical['A']=dict(handoff=handoff_metrics(decode(path),2+begin,2+end+1),
                legacy_architecture='Wet output begins near fade/capture, rises, holds, then independently fades; forbidden by new gain-law checks.')
        settings={k:v for k,v in entry['source_settings'].items() if k not in LEGACY_DSP_KEYS}
        settings.update(entry['prediction'])
        settings['v1_source_assumption']=settings['assumption']
        settings['assumption']=' '.join(entry['prediction']['reasoning'])+' Natural decay; no late wet attack/hold or new freeze.'
        primary={**proofs['B'],'freeze_relative':entry['prediction']['dry_fade'][0]-settings['source_in']}
        c=dict(settings=settings,prediction=entry['prediction'],alternative=entry['alternative'],proof=primary,proofs=proofs,renders=renders,technical=technical,
            source_identity=entry['source_identity'],excerpt_role=prior['excerpt_role'],trial_group=entry['trial_group'],arrangement_caveat=entry['source_arrangement_caveat'],
            original_reference=Path(os.path.relpath(sourcepath,output)).as_posix(),source_preview_sha256=digest(sourcepath))
        m['cues'].append(c);(output/'renders.json').write_text(json.dumps(m,indent=2)+'\n')
        (output/'envelopes'/f'{key}.svg').write_text(svg(key,proofs),encoding='utf-8')
        print(json.dumps(dict(cue=key,variants=list(renders),technical_summary={k:{'max_handoff_drop_db':v['handoff']['largest_adjacent_drop_db']} for k,v in technical.items()})),flush=True)
    verify_pins(ledger)
    (output/'index.html').write_text(make_page(m),encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f'#EXTINF:{r["qa"]["seconds"]},{c["settings"]["cue"]} {r["label"]}\n{r["file"]}\n' for c in m['cues'] for r in c['renders'].values()),encoding='utf-8')
    return m


def verify(folder):
    reg=registration();ledger=json.loads(LEDGER.read_text());verify_pins(ledger)
    folder=build_path(folder);m=json.loads((folder/'renders.json').read_text())
    if m['registration']['commit']!=reg['commit'] or m['plan_sha256']!=digest(LEDGER):raise ValueError('Registration mismatch')
    if [c['settings']['cue'] for c in m['cues']]!=TRIAL:raise ValueError('Not exactly preregistered six')
    results=[];flags=[];audition_flags=[];count=0
    for c in m['cues']:
        key=c['settings']['cue'];e=next(e for e in ledger['entries'] if e['cue']==key)
        if c['prediction']!=e['prediction'] or c['alternative']!=e['alternative']:raise ValueError('Predictions changed after rendering')
        if digest(folder/c['original_reference'])!=c['source_preview_sha256']:raise ValueError('Source changed')
        src=decode(folder/c['original_reference']);arrays={}
        for name,r in c['renders'].items():
            path=folder/r['file'];x=decode(path)
            arrays[name]=x
            if digest(path)!=r['qa']['sha256'] or len(x)!=round(r['qa']['seconds']*RATE):raise ValueError('PCM identity/duration')
            if np.any(x[:2*RATE]) or np.any(x[-3*RATE:]) or np.max(abs(x))>=.97:raise ValueError('Context silence/headroom')
            if name=='A':continue
            if np.any(x[2*RATE]) or np.any(x[-3*RATE-1]) or np.sqrt(np.mean(x[2*RATE:-3*RATE]**2))<10**(-75/20):raise ValueError('Missing material or nonzero outer sample')
            count+=1;p=c['proofs'][name];spec=e['prediction'] if name=='B' else e['alternative']
            a,b=e['features']['crop_frames']
            if (p['source_start_frame'],p['source_end_frame'])!=(a,b):raise ValueError('Wrong source crop')
            fs,fe=[v-spec['source_in'] for v in spec['dry_fade']]
            env=dry_envelope(b-a,RATE,spec['fade_in'],fs,fe)
            expected_dry=np.zeros((len(x)-5*RATE,2));expected_dry[:b-a]=src[a:b]*env[:,None]
            if np.max(abs(envelope_windows(expected_dry)-np.array(p['windows_50ms']['dry'])))>1e-12:raise ValueError('Dry fade/crop proof differs from original source')
            if p['rt60']!=spec['rt60'] or p['send_policy']!=spec['send_policy'] or p['freeze']:raise ValueError('Wrong treatment')
            if p['wet_gain']!=c['proofs']['B']['wet_gain']:raise ValueError('Alternative was independently level-normalized')
            measured=envelope_windows(x[2*RATE:-3*RATE]);expected=np.array(p['windows_50ms']['combined'])*32767/32768
            if len(measured)!=len(expected) or np.max(abs(measured-expected))>1.6e-5:raise ValueError('Envelope metadata mismatch')
            if p['cleanup_peak_dbfs']>=-100 or p['dry_stop_max_sample_delta']>.02:raise ValueError('Truncation/seam')
            if not all(p['wet_control_checks'][k] for k in ['no_late_wet_attack','no_wet_gain_rebound','no_post_stop_hold']):raise ValueError('Forbidden control architecture')
            post=release_diagnostics(x[2*RATE:-3*RATE],p['dry_stop_relative'])
            if post['rebound_review'] or post['plateau_window_starts']:flags.append(dict(cue=key,variant=name,kind='post_source_geometry_review',detail=post))
            if c['technical'][name]['handoff']['largest_adjacent_drop_db']>6:
                audition_flags.append(dict(cue=key,variant=name,kind='fast_handoff_review',threshold_db=6,
                    limitation='Conservative diagnostic review threshold, not a preregistered preference rule or a perceptual pass/fail. Prediction remains unchanged.'))
            if c['technical'][name]['spectral']['maximum_audible_spectral_distance']>.65:
                audition_flags.append(dict(cue=key,variant=name,kind='spectral_change_review',threshold=.65,
                    limitation='Change can come from the composition or spectral filtering; listening required. Not a preregistered preference threshold.'))
            results.append(dict(cue=key,variant=name,qa=r['qa'],prediction_family=e['prediction']['family'],
                original_fade=spec['original_dry_fade'],actual_fade=spec['dry_fade'],rt60=p['rt60'],wet_gain=p['wet_gain'],
                cleanup_peak_dbfs=p['cleanup_peak_dbfs'],dry_stop_sample_delta=p['dry_stop_max_sample_delta'],
                handoff_drop_db=c['technical'][name]['handoff']['largest_adjacent_drop_db'],
                spectral_distance=c['technical'][name]['spectral']['maximum_audible_spectral_distance'],
                post_stop_first_second_dbfs=p['post_stop_first_second_dbfs'],post_source_review=post['rebound_review']))
        if 'C' in arrays:
            relative=min(c['prediction']['dry_fade'][0],c['alternative']['dry_fade'][0])-c['settings']['source_in']
            until=round((2+relative)*RATE)
            if not np.array_equal(arrays['B'][:until],arrays['C'][:until]):raise ValueError('Uncontrolled level/field difference before comparison')
        if c['trial_group']=='known_problem_note':
            old=e['source_settings'];length=round((old['source_out']-old['source_in'])*RATE)
            total=length+round(old['tail_extra']*RATE)
            f=round((old.get('freeze_at',old['dry_fade'][0])-old['source_in'])*RATE)
            legacy=np.zeros(total);legacy[f:]=1
            attack=round(old['wet_attack']*RATE);legacy[f:f+attack]*=ramp(attack)
            tail=length+round(old['hold_after_dry']*RATE);legacy[tail:]*=1-ramp(total-tail)
            try:validate_wet_control(legacy,round((old['dry_fade'][1]-old['source_in'])*RATE),False)
            except ValueError as exc:
                if 'Late wet' not in str(exc):raise
            else:raise ValueError('Regression gate failed to reject actual legacy late wet envelope')
    if count!=8:raise ValueError('Wrong trial render count')
    links=re.findall(r'(?:src|href)="([^"]+)"',(folder/'index.html').read_text(encoding='utf-8'))
    if any('://' in p or not (folder/p).is_file() for p in links):raise ValueError('Missing/external resource')
    return dict(passed=not flags,engineering_safety_passed=not flags,technical_review_flags=flags,audition_review_flags=audition_flags,
        musical_fit='pending human evaluation; no prediction was promoted after rendering',registration=m['registration'],new_renders=count,cues=6,
        immutable_inputs_verified=len(ledger['immutable_inputs']),index_sha256=digest(folder/'index.html'),metadata_sha256=digest(folder/'renders.json'),
        source_measurements_not_subjective=True,browser_playback_verified=False,subjectively_listened=False,results=results)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    if a.verify:print(json.dumps(verify(a.output),indent=2))
    else:build(a.output)
