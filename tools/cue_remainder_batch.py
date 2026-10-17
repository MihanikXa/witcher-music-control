"""Private remainder batch: reuse established cue DSP, protect accepted audio."""
import argparse
import html
import json
import os
from functools import lru_cache
from pathlib import Path
import re

import numpy as np
from scipy import signal

from cue_edit_render import decode,page as legacy_page
from cue_freeze_dsp import RATE,dry_envelope,render_continuous,envelope_windows,release_diagnostics
from cue_tail_v2 import write_pcm,svg
from cue_treatment_predict import source_features,EXPLICIT
from cue_treatment_trial import spectral_metrics
from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]
V1=REPO/'build/music-material-selection/cue-edits-v1'
ORDINARY=['S04-a','S11-long','S07-a','S12-3','S12-4','S15-b','S16-1','S16-3','S18-1','S18-2']
RESTRICTED=['S14-1','S14-2']
PLAN=REPO/'research/81-remainder-batch-plan.json'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def level(x):return float(20*np.log10(max(float(np.sqrt(np.mean(x*x))),1e-12)))
def rel(path,root):return Path(os.path.relpath(path,root)).as_posix()


def preserved_inputs():
    snapshot=read(REPO/'research/79-accepted-private-cue-selections.json')
    ledger=read(REPO/'research/69-treatment-predictions.json')
    pins=dict(ledger['immutable_inputs'])
    for r in snapshot['selections']:pins[r['file']]=r['sha256']
    pins['build/music-material-selection/cue-edits-v1/audio/S05-main-B.wav']='1f267727b6d531200099bf70656218e364de7982e1a2e508031cf9f8f8c90c35'
    pins['research/69-treatment-predictions.json']=snapshot['frozen_prediction_sha256']
    for p in ['research/79-accepted-private-cue-selections.json','research/70-selected-private-cue-renders.json',
              'research/80-remaining-cues-batch-audition-handoff.md']:
        pins[p]=digest(REPO/p)
    accepted={r['cue'] for r in snapshot['selections']}|{'S05-main'}
    expected=accepted|set(ORDINARY)|set(RESTRICTED)
    if len(expected)!=24 or expected!={e['cue'] for e in ledger['entries']}:
        raise ValueError('24-excerpt reconciliation failed')
    check_pins(pins)
    return pins


def check_pins(pins):
    for path,h in pins.items():
        if digest(REPO/path)!=h:raise ValueError('Preserved input changed: '+path)


@lru_cache(maxsize=1)
def load_source(path,sha):
    path=Path(path)
    if digest(path)!=sha:raise ValueError('Source hash mismatch')
    return decode(path)


def ending_rows(arrays,source_start,stop,seconds=3.):
    """Centered stereo RMS on exact source clocks, before any player pad."""
    rows=[]
    start=max(source_start+.05,stop-seconds)
    for t in np.arange(start,stop-.049,.025):
        row=dict(source_seconds=float(t),player_seconds=float(2+t-source_start),windows={})
        for ms in (20,25,50,100):
            n=round(ms*RATE/1000);center=round((t-source_start)*RATE);a=center-n//2
            row['windows'][str(ms)]={k:level(v[a:a+n]) for k,v in arrays.items()}
        rows.append(row)
    return rows


def inspect_source(source,s):
    a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
    f=source_features(source,s)
    crop=source[a:b]
    rows=ending_rows({'source':crop},s['source_in'],s['source_out'],4)
    start=max(a,b-8*RATE);context=source[start:b]
    bands={}
    for lo,hi in [(30,200),(200,1000),(1000,4000),(4000,10000)]:
        x=signal.sosfiltfilt(signal.butter(4,[lo,hi],btype='bandpass',fs=RATE,output='sos'),context,axis=0)
        bands[f'{lo}-{hi}Hz']=[dict(source_seconds=t,dbfs=level(x[round((t-start/RATE)*RATE)-1200:round((t-start/RATE)*RATE)+1200]))
                              for t in np.arange(max(start/RATE+.05,s['source_out']-2),s['source_out']-.049,.1)]
    final=[r for r in rows if r['source_seconds']>=s['source_out']-1]
    values=[r['windows']['50']['source'] for r in final]
    rebound=max(((values[j]-values[i],i,j) for i in range(len(values)) for j in range(i+1,min(len(values),i+21))),default=(0,0,0))
    f.update(fine_source_rows=rows,source_bands_50ms=bands,
        onset_250ms=[dict(source_seconds=s['source_in']+i/RATE,dbfs=level(crop[i:i+RATE//4])) for i in range(0,min(len(crop),8*RATE),RATE//4)],
        local_recovery=dict(db=max(0.,float(rebound[0])),from_source=final[rebound[1]]['source_seconds'],to_source=final[rebound[2]]['source_seconds']),
        source_kind_caveat='Source/arrangement identity retained from original audition. Signal features do not establish stem completeness, harmonic resolution or musical quality.')
    return f


def survey(output):
    pins=preserved_inputs();ledger=read(REPO/'research/69-treatment-predictions.json');old=read(V1/'renders.json')
    entries=[]
    for key in ORDINARY+RESTRICTED:
        e=next(e for e in ledger['entries'] if e['cue']==key)
        prior=next(c for c in old['cues'] if c['settings']['cue']==key)
        p=(V1/prior['original_reference']).resolve();source=load_source(str(p),prior['source_preview_sha256'])
        features=inspect_source(source,e['source_settings'])
        entries.append(dict(cue=key,comparison_only=key in RESTRICTED,features=features,source_sha256=digest(p),source_identity=prior['source_identity']))
        print(json.dumps(dict(cue=key,last_half=features['last_half_second_dbfs'],change=features['source_ending_change_db'],recovery=features['local_recovery'],onset=features['onset_250ms'][:24])),flush=True)
    check_pins(pins)
    output=build_path(output)
    if output.exists():raise FileExistsError('Preserve earlier survey')
    output.write_text(json.dumps(dict(immutable_inputs=pins,entries=entries),indent=2,allow_nan=False)+'\n')


def validate_plan(plan,ledger):
    ids=[c['cue'] for c in plan['cues']]
    if ids!=ORDINARY+RESTRICTED:raise ValueError('Batch must contain exactly ten ordinary and two restricted cues')
    if sum(bool(c.get('alternative_changes')) for c in plan['cues'])>3:raise ValueError('At most three diagnostic alternatives')
    for c in plan['cues']:
        key=c['cue'];s=c['settings'];e=next(e for e in ledger['entries'] if e['cue']==key)
        if c['comparison_only']!=(key in RESTRICTED) or s['comparison_only']!=c['comparison_only']:
            raise ValueError('Restricted classification changed')
        if s['cue']!=key or [s['source_in'],s['source_out']]!=[e['source_settings']['source_in'],e['source_settings']['source_out']]:
            raise ValueError('Selected source boundary changed')
        if key in EXPLICIT and s['dry_fade']!=e['source_settings']['dry_fade']:
            raise ValueError('Explicit user fade changed')
        if not s['source_in']<=s['dry_fade'][0]<s['dry_fade'][1]==s['source_out']:
            raise ValueError('Invalid ending window')
        if s.get('local_dry_alignment') or s.get('local_send_fade'):
            raise ValueError('No comparable source-backed S18 alignment approved for this batch')
        alt=c.get('alternative_changes')
        if alt and (len(alt)!=1 or set(alt)-{'send_policy','continuous_wet_db'}):
            raise ValueError('Alternative must change one reviewed variable')
        if s['treatment']=='source_release_only':
            if alt or s['send_policy']!='none' or s['rt60'] is not None or s['continuous_wet_db'] is not None:
                raise ValueError('Source-release-only must not add room')
            if not -100<=s['guard_peak_ceiling_dbfs']<=-60:raise ValueError('Unsafe endpoint guard ceiling')
            if abs(s['source_out']-s['dry_fade'][0]-.02)>1/RATE:raise ValueError('Only20ms quiet endpoint guard reviewed')
        elif s['treatment']!='natural_decay' or s['send_policy'] not in ('post_fader','pre_ending_fade'):
            raise ValueError('Unreviewed treatment')


def render_source_release(source,s):
    """Retain existing recorded decay, with the existing tiny quiet-end guard."""
    a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
    fs,fe=[v-s['source_in'] for v in s['dry_fade']]
    if not 0<=a<b<=len(source):raise ValueError('Source clock out of range')
    peak=float(np.max(np.abs(source[a+round(fs*RATE):b])))
    if peak>10**(s['guard_peak_ceiling_dbfs']/20):raise ValueError('Source too loud for quiet endpoint guard')
    env=dry_envelope(b-a,RATE,s['fade_in'],fs,fe);dry=source[a:b]*env[:,None]
    # Same fixed attenuation-only headroom convention as the legacy renderer.
    original_peak=float(np.max(np.abs(dry)));headroom=min(1.,.96/max(original_peak,1e-12))
    dry*=headroom
    audio=np.pad(dry,((2*RATE,3*RATE),(0,0)))
    proof=dict(source_start_frame=a,source_end_frame=b,dry_seconds=(b-a)/RATE,dry_stop_relative=fe,
               output_seconds=len(audio)/RATE,tail_extra=0.,rt60=None,freeze=False,wet_gain=0.,send_policy='none',
               headroom_gain=headroom,original_dry_peak=original_peak,
               guard_original_peak_dbfs=20*np.log10(max(peak,1e-12)),guard_peak_ceiling_dbfs=s['guard_peak_ceiling_dbfs'],
               cleanup_peak_dbfs=None,dry_stop_max_sample_delta=float(np.max(np.abs(np.diff(np.pad(dry[-128:],((0,128),(0,0))),axis=0)))),
               windows_50ms={k:envelope_windows(v).tolist() for k,v in [('dry',dry),('wet',np.zeros_like(dry)),('combined',dry)]},
               wet_control_checks=dict(no_late_wet_attack=True,no_wet_gain_rebound=True,no_post_stop_hold=True,independent_secondary_fade=False),
               release_policy='Original recorded release; no added reverb, no tail boost;20ms quiet endpoint guard')
    return audio,proof,dict(dry=dry,wet=np.zeros_like(dry),source_envelope=env)


def technical(source,s,audio,p,components):
    a,b=p['source_start_frame'],p['source_end_frame'];raw=audio[2*RATE:-3*RATE]
    if not np.array_equal(components['dry'][:b-a],source[a:b]*components['source_envelope'][:,None]*p.get('headroom_gain',1.)):
        raise ValueError('Wrong original source samples/envelope')
    if np.any(components['dry'][b-a:]):raise ValueError('Dry music continues beyond chosen source endpoint')
    # Measurement pads allow centered windows after stop even for native-release-only.
    frames=max(len(raw),b-a+3*RATE);pad=lambda x:np.pad(x,((0,frames-len(x)),(0,0)))
    original=np.zeros((frames,2));original[:b-a]=source[a:b]
    arrays=dict(source=original,dry=pad(components['dry']),wet=pad(components['wet']),combined=pad(raw))
    beginning=max(s['source_in'],min(s['dry_fade'][0]-.5,s['source_out']-3))
    rows=ending_rows(arrays,s['source_in'],s['source_out']+2,s['source_out']+2-beginning)
    before=[r for r in rows if s['source_out']-1<=r['source_seconds']<=s['source_out']-.05]
    max_excess_drop=0.;max_excess_rise=0.;actual_rise=0.
    for left,right in zip(before,before[4:]):
        x,y=left['windows']['50'],right['windows']['50']
        if min(x['combined'],y['combined'])>-70:
            max_excess_drop=max(max_excess_drop,(x['combined']-y['combined'])-(x['source']-y['source']))
            max_excess_rise=max(max_excess_rise,(y['combined']-x['combined'])-(y['source']-x['source']))
            actual_rise=max(actual_rise,y['combined']-x['combined'])
    wet=[r['windows']['50']['wet'] for r in before]
    growth=max((wet[j]-wet[i] for i in range(len(wet)) for j in range(i+1,len(wet)) if min(wet[i],wet[j])>-80),default=0.)
    stop=(b-a)/RATE
    post=release_diagnostics(arrays['combined'],stop)
    spec=spectral_metrics(raw,max(0,s['dry_fade'][0]-s['source_in']),stop)
    warnings=[]
    if max_excess_drop>6:warnings.append('Fast processing-associated handoff drop (>6dB/100ms while output above−70dBFS); listen.')
    if max_excess_rise>3:warnings.append('Local decay slope differs from original source by >3dB/100ms; room may carry a source dip. Listen for a separate handoff; this is not necessarily a literal volume rise.')
    if growth>3:warnings.append('Late wet energy rises >3dB in the final source second; may be room/source modulation, review the handoff.')
    if post['rebound_review'] or post['plateau_window_starts']:warnings.append('Post-source envelope rebound/plateau review flag.')
    if spec['maximum_audible_spectral_distance']>.65:warnings.append('Large spectral evolution; source and room coloration may both contribute.')
    if s['treatment']=='source_release_only':warnings.append('Original recording already decays; no added room. Endpoint guard threshold is engineering evidence, not an audibility verdict.')
    bands={}
    for lo,hi in [(30,200),(200,1000),(1000,4000),(4000,10000)]:
        bands[f'{lo}-{hi}Hz']={}
        # Evaluate the ending interval with preceding4s context, not the full file repeatedly.
        first=max(0,round((beginning-s['source_in']-4)*RATE));last=min(frames,round((stop+2.1)*RATE))
        for name,arr in arrays.items():
            x=signal.sosfiltfilt(signal.butter(4,[lo,hi],btype='bandpass',fs=RATE,output='sos'),arr[first:last],axis=0)
            rms=envelope_windows(x,.05)
            bands[f'{lo}-{hi}Hz'][name]=dict(source_start_seconds=s['source_in']+first/RATE,window_seconds=.05,dbfs=(20*np.log10(np.maximum(rms,1e-12))).tolist())
    return dict(ending_rows=rows,bands_50ms=bands,maximum_processing_excess_drop_100ms_db=max(0.,max_excess_drop),
                maximum_processing_excess_rise_100ms_db=max(0.,max_excess_rise),last_source_second_wet_growth_db=max(0.,growth),
                maximum_combined_rise_100ms_db=max(0.,actual_rise),
                post_source_geometry=post,spectral=spec,warnings=warnings,
                limitation='Measurements review possible processing defects; natural source fluctuations and musical quality require human listening.')


def page(m):
    e=lambda x:html.escape(str(x),quote=True)
    def card(c):
        s=c['settings'];key=s['cue'];r=c['renders'];p=c['proofs']['B']
        opts=''.join(f'<option value="{k}" {"selected" if k=="B" else ""}>{e(v["label"])}</option>' for k,v in r.items())
        prefs='<option value="">Undecided</option>'+''.join(f'<option value="{k}">{e(v["label"])}</option>' for k,v in r.items())
        style='Original recorded release; no added reverb.' if s['treatment']=='source_release_only' else f'Natural room: RT60 {s["rt60"]}s, {s["continuous_wet_db"]}dB target, {s["send_policy"]}.'
        if p.get('headroom_gain',1.)<1:style+=f' Constant headroom attenuation {20*np.log10(p["headroom_gain"]):.2f}dB throughout; no compression.'
        watch=' '.join(c['technical']['B']['warnings']) or 'No threshold review flag. Listening approval remains pending.'
        return f'''<article data-cue="{e(key)}"><h2>{e(key)} · {e(s['source_title'])}</h2><p>{e(c['source_identity'].get('origin_label','Original private audition source'))}</p>
<p>Source {s['source_in']:.3f}–{s['source_out']:.3f}s · Fade {s['dry_fade'][0]:.3f}–{s['dry_fade'][1]:.3f}s. {e(style)}</p><p>{e(c['timing_authority'])}</p>
<select class="variant">{opts}</select><button class="play">Entrance / full cue</button><button class="ending">Hear last8s + tail</button><label><input type="checkbox" class="position" checked>Keep position on switch</label><audio controls preload="none" src="{e(r['B']['file'])}"></audio>
<p>Verdict <select class="verdict"><option>Unreviewed</option><option>Keep</option><option>Adjust</option><option>Reject</option></select> Preferred <select class="preferred">{prefs}</select></p><textarea rows="2" placeholder="Variant and player time; dip, separate tail, too wet/short, onset or other issue?"></textarea>
<details><summary>Why this treatment / technical warnings / original reference</summary><p>{e(c['reasoning'])}</p><p><b>Technical review:</b> {e(watch)}</p><p>{e(s['verbatim_notes'])}</p><p>Original below uses its own source clock; edited player =2s + source time −{s['source_in']:.3f}s. Source stop is player {2+s['source_out']-s['source_in']:.3f}s. {e(c.get('onset_note',''))}</p><audio controls preload="none" src="{e(c['original_reference'])}"></audio><p><a href="envelopes/{e(key)}.svg">50ms envelopes</a> · <a href="analysis/{e(key)}.json">20–100ms and spectral measurements</a></p><pre>{e(json.dumps(dict(settings={k:s[k] for k in ['source_in','source_out','dry_fade','fade_in','send_policy','rt60','continuous_wet_db','treatment','comparison_only']},variants={k:dict(file=v['file'],sha256=v['qa']['sha256']) for k,v in r.items()}),indent=2))}</pre></details></article>'''
    ordinary=''.join(card(c) for c in m['cues'] if not c['comparison_only'])
    restricted=''.join(card(c) for c in m['cues'] if c['comparison_only'])
    data={**m,'cues':[{k:v for k,v in c.items() if k not in ('proofs','technical')} for c in m['cues']]}
    legacy=legacy_page(dict(cues=[],references=[],lead_silence=2,trail_silence=3))
    client=legacy[legacy.rfind('<script>'):].replace('wmc-cue61-','wmc-remainder81-')
    wrapper="""const oldGather=gather;gather=function(){const x=oldGather();x.kind='remainder-batch-private-outcomes';x.scope='Private audition only; S14 Keep is comparison-only, never normal reuse approval';x.decisions.forEach(d=>{const q=cueData(cards.find(c=>c.dataset.cue===d.cue));d.comparison_only=q.comparison_only;d.current_treatment_reasoning=q.reasoning;d.timing_authority=q.timing_authority;d.allowed_use=d.comparison_only?'private comparison only; dedicated-authored reuse restriction':'pending private cue listening decision';});x.ordinary_decisions=x.decisions.filter(d=>!d.comparison_only);x.restricted_comparisons=x.decisions.filter(d=>d.comparison_only);return x;};"""
    client=client.replace('</script>',wrapper+'</script>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC — remainder batch</title><style>body{max-width:1000px;margin:25px auto;padding:0 16px;background:#151a1c;color:#ece8de;font:16px/1.45 system-ui}article{border:1px solid #637571;border-radius:8px;padding:16px;margin:18px 0}audio,textarea{width:100%}button,select{padding:8px;margin:4px}header{position:sticky;top:0;background:#151a1cf5;padding:8px;z-index:1}a{color:#9cddf2}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}.restricted{border:3px solid #bc9358;padding:14px}#json{height:180px}</style>
<h1>Remaining cue auditions</h1><p>Ten ordinary excerpts, each with one primary B. Three optional C comparisons change one variable; A links older defective references on the known-problem cues. All new room treatments are conventional decay; C is a comparison label, not freeze. Everything here is <b>pending your listening</b>. Previously accepted cues, including S18-3 T3, are preserved.</p><p>Suggested order: S04-a → S11-long → S07-a → quiet-end S12-4/S16-3, then the rest. Each edited player has2s leading and3s final silence; use the ending button, then listen through the complete tail. Keep/Adjust/Reject and preferred variant are independent; export once after reviewing.</p>
<header><button id="stop">Stop all</button><button id="export">Export decisions JSON</button><button id="show">Show/copy JSON</button><span id="status"></span></header><details id="fallback"><summary>Copy JSON fallback</summary><textarea id="json" readonly></textarea></details>'''+ordinary+'''<section class="restricted"><h1>S14 — private comparison only</h1><p>These two recordings have verified reuse in dedicated authored music. They are segregated comparisons, not ordinary soundtrack-reuse candidates. Any Keep verdict remains comparison-only. No distribution or game integration is authorized.</p>'''+restricted+'</section><script id="manifest" type="application/json">'+json.dumps(data,allow_nan=False).replace('<','\\u003c')+'</script>'+client


def build(output,resume=False):
    output=build_path(output)
    if output.exists() and not resume:raise FileExistsError('Fresh output required or explicit --resume with identical plan')
    plan=read(PLAN);ledger=read(REPO/'research/69-treatment-predictions.json');validate_plan(plan,ledger)
    if digest(REPO/'research/81-remainder-source-analysis.json')!=plan['source_analysis_sha256']:raise ValueError('Recorded source survey changed')
    check_pins(plan['immutable_inputs']);old=read(V1/'renders.json')
    if resume:
        m=read(output/'renders.json')
        if m['plan_sha256']!=digest(PLAN):raise ValueError('Cannot resume changed plan')
        if [c['settings']['cue'] for c in m['cues']]!=[c['cue'] for c in plan['cues'][:len(m['cues'])]]:raise ValueError('Resume metadata is not an exact completed prefix')
        for c,cfg in zip(m['cues'],plan['cues']):
            if c['settings']!=cfg['settings']:raise ValueError('Completed settings differ')
            for r in c['renders'].values():
                if digest(output/r['file'])!=r['qa']['sha256']:raise ValueError('Completed audio changed')
    else:
        output.mkdir();(output/'audio').mkdir();(output/'analysis').mkdir();(output/'envelopes').mkdir()
        m=dict(schema=1,kind='remainder-batch-private-audition',plan_sha256=digest(PLAN),feedback_sha256=digest(REPO/'research/58-user-musical-material-audition-feedback.json'),source_metadata_sha256=digest(REPO/'build/music-material-selection/audition-v3/auditions.json'),primary_variant='B',lead_silence=2,trail_silence=3,cues=[],references=[],subjectively_listened=False,browser_playback_verified=False)
    for cfg in plan['cues']:
        if any(c['settings']['cue']==cfg['cue'] for c in m['cues']):continue
        key=cfg['cue'];s=dict(cfg['settings']);prior=next(c for c in old['cues'] if c['settings']['cue']==key)
        src=(V1/prior['original_reference']).resolve();source=load_source(str(src),cfg['source_sha256'])
        renders={};proofs={};qa_data={};gain=None
        specs=[('B',s)]+([('C',{**s,**cfg['alternative_changes']})] if cfg.get('alternative_changes') else [])
        for name,settings in specs:
            if settings['treatment']=='source_release_only':x,p,components=render_source_release(source,settings)
            else:
                if name=='C' and 'continuous_wet_db' in cfg['alternative_changes']:
                    gain=proofs['B']['wet_gain']*10**((settings['continuous_wet_db']-s['continuous_wet_db'])/20)
                x,p,components=render_continuous(source,settings,settings['rt60'],wet_gain=gain)
            if name=='B':gain=p['wet_gain']
            qa=write_pcm(output/'audio'/f'{key}-{name}.wav',x)
            t=technical(source,settings,x,p,components)
            label='B — new primary (unreviewed)' if name=='B' else 'C — one-variable diagnostic: '+', '.join(f'{k}={v}' for k,v in cfg['alternative_changes'].items())
            if cfg['comparison_only']:label='Private comparison only · '+label
            renders[name]=dict(file=f'audio/{key}-{name}.wav',label=label,qa=qa)
            proofs[name]=p;qa_data[name]=t
        if key in ('S04-a','S11-long','S07-a'):
            which='B' if key=='S04-a' else 'C';r=prior['renders'][which];path=V1/r['file']
            if digest(path)!=r['qa']['sha256']:raise ValueError('Prior failed reference changed')
            renders['A']=dict(file=rel(path,output),label=f'A — unchanged v1 {which}, known-defect reference',qa=r['qa'])
        c=dict(settings=s,comparison_only=cfg['comparison_only'],reasoning=cfg['reasoning'],timing_authority=cfg['timing_authority'],
               alternative_changes=cfg.get('alternative_changes'),renders=renders,proofs=proofs,technical=qa_data,
               proof=dict(output_seconds=proofs['B']['output_seconds'],freeze_relative=max(0,proofs['B']['dry_seconds']-6)),
               original_reference=rel(src,output),source_preview_sha256=digest(src),source_identity=cfg['source_identity'],excerpt_role=prior['excerpt_role'])
        if key=='S04-a':c['onset_note']='Original near-silence until about source3.25s, then a gradual rise around source5s; nothing trimmed. Player adds2s.'
        m['cues'].append(c)
        (output/'analysis'/f'{key}.json').write_text(json.dumps(qa_data,indent=2,allow_nan=False)+'\n')
        (output/'envelopes'/f'{key}.svg').write_text(svg(f'{key}: x0 = source{s["source_in"]:.3f}s / player2s',proofs),encoding='utf-8')
        (output/'renders.json').write_text(json.dumps(m,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(cue=key,variants=list(renders),primary_warnings=qa_data['B']['warnings'])),flush=True)
    (output/'index.html').write_text(page(m),encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f'#EXTINF:{r["qa"]["seconds"]},{c["settings"]["cue"]} {r["label"]}\n{r["file"]}\n' for c in m['cues'] for r in c['renders'].values()),encoding='utf-8')
    check_pins(plan['immutable_inputs']);return m


def verify(output):
    output=build_path(output);plan=read(PLAN);validate_plan(plan,read(REPO/'research/69-treatment-predictions.json'))
    check_pins(plan['immutable_inputs']);m=read(output/'renders.json');count=0;results=[]
    if m['plan_sha256']!=digest(PLAN) or [c['settings']['cue'] for c in m['cues']]!=ORDINARY+RESTRICTED:raise ValueError('Wrong batch/plan')
    for c,cfg in zip(m['cues'],plan['cues']):
        s=c['settings'];src=(output/c['original_reference']).resolve()
        if digest(src)!=cfg['source_sha256']:raise ValueError('Source changed after rendering')
        source=load_source(str(src),cfg['source_sha256'])
        if s!=cfg['settings'] or c['comparison_only']!=cfg['comparison_only']:raise ValueError('Recorded treatment/classification changed')
        for name,r in c['renders'].items():
            path=output/r['file'];x=decode(path)
            if digest(path)!=r['qa']['sha256'] or len(x)!=round(r['qa']['seconds']*RATE):raise ValueError('Render hash/duration mismatch')
            if x.shape[1]!=2 or not np.isfinite(x).all() or np.any(x[:2*RATE]) or np.any(x[-3*RATE:]) or np.max(np.abs(x))>=.97:raise ValueError('PCM context/clipping')
            if level(x[2*RATE:-3*RATE])<-75:raise ValueError('Missing musical material')
            if name=='A':continue
            if np.any(x[2*RATE]) or np.any(x[-3*RATE-1]):raise ValueError('Outer active boundary is nonzero')
            count+=1;p=c['proofs'][name];settings=s if name=='B' else {**s,**cfg['alternative_changes']}
            a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
            if (a,b)!=(p['source_start_frame'],p['source_end_frame']):raise ValueError('Source clocks shifted')
            env=dry_envelope(b-a,RATE,s['fade_in'],settings['dry_fade'][0]-s['source_in'],settings['dry_fade'][1]-s['source_in'])
            expected=np.zeros((len(x)-5*RATE,2));expected[:b-a]=source[a:b]*env[:,None]*p.get('headroom_gain',1.)
            if np.max(np.abs(envelope_windows(expected)-p['windows_50ms']['dry']))>1e-12:raise ValueError('Independent dry reconstruction failed')
            actual=envelope_windows(x[2*RATE:-3*RATE]);stored=np.array(p['windows_50ms']['combined'])*32767/32768
            if len(actual)!=len(stored) or np.max(np.abs(actual-stored))>1.6e-5:raise ValueError('Stored PCM envelope mismatch')
            if p['dry_stop_max_sample_delta']>.02:raise ValueError('Excessive endpoint discontinuity')
            if settings['treatment']=='natural_decay' and (p['freeze'] or p['cleanup_peak_dbfs']>=-100):raise ValueError('Unsafe natural-tail termination')
            if p['rt60']!=settings['rt60'] or p['send_policy']!=settings['send_policy']:raise ValueError('Recorded treatment differs from plan')
            if name=='C':
                expected_gain=c['proofs']['B']['wet_gain']*10**((settings['continuous_wet_db']-s['continuous_wet_db'])/20)
                if abs(p['wet_gain']-expected_gain)>1e-12:raise ValueError('Uncontrolled alternative wet calibration')
                if 'send_policy' in cfg['alternative_changes']:
                    xb=decode(output/c['renders']['B']['file']);until=round((2+s['dry_fade'][0]-s['source_in'])*RATE)
                    if not np.array_equal(x[:until],xb[:until]):raise ValueError('Send-only alternative changed earlier music/field')
                else:
                    ratio=expected_gain/c['proofs']['B']['wet_gain']
                    if np.max(np.abs(np.array(p['windows_50ms']['wet'])-np.array(c['proofs']['B']['windows_50ms']['wet'])*ratio))>1e-12:
                        raise ValueError('Wet-level alternative changed more than its fixed gain')
            if settings['treatment']=='source_release_only' and p['wet_gain']!=0:raise ValueError('Quiet source revived by added room')
            results.append(dict(cue=s['cue'],variant=name,comparison_only=c['comparison_only'],qa=r['qa'],treatment=settings['treatment'],
                                fade=settings['dry_fade'],rt60=settings['rt60'],wet_gain=p['wet_gain'],send=settings['send_policy'],
                                cleanup_peak_dbfs=p['cleanup_peak_dbfs'],guard_original_peak_dbfs=p.get('guard_original_peak_dbfs'),headroom_gain=p.get('headroom_gain',1.),
                                drop_review_db=c['technical'][name]['maximum_processing_excess_drop_100ms_db'],
                                actual_rise_100ms_db=c['technical'][name]['maximum_combined_rise_100ms_db'],relative_rise_review_db=c['technical'][name]['maximum_processing_excess_rise_100ms_db'],
                                wet_growth_db=c['technical'][name]['last_source_second_wet_growth_db'],warnings=c['technical'][name]['warnings']))
    if count!=15 or len(list((output/'audio').glob('*.wav')))!=15:raise ValueError('Not exactly12 primaries/3 diagnostic alternatives')
    links=re.findall(r'(?:src|href)="([^"]+)"',(output/'index.html').read_text(encoding='utf-8'))
    if any('://' in p or not (output/p).is_file() for p in links):raise ValueError('Missing/external player reference')
    return dict(engineering_safety_passed=True,musical_fit='Pending human listening; no new acceptance',ordinary_primaries=10,restricted_primaries=2,alternatives=3,new_wavs=count,
                accepted11_and_separate_main_preserved=True,immutable_inputs=len(plan['immutable_inputs']),all24_ids_reconciled=True,
                results=results,index_sha256=digest(output/'index.html'),metadata_sha256=digest(output/'renders.json'),
                real_browser_tested=False,subjectively_listened=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--survey',type=Path);p.add_argument('--output',type=Path);p.add_argument('--verify',action='store_true');p.add_argument('--resume',action='store_true')
    a=p.parse_args()
    if a.survey:survey(a.survey)
    elif a.output:
        if not a.verify:build(a.output,resume=a.resume)
        result=verify(a.output);(build_path(a.output)/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result))
    else:p.error('Choose --survey or --output')
