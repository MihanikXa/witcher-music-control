"""Seeded synthetic comparisons and an audio-free local trace review."""
import argparse
from collections import Counter
import csv
from dataclasses import asdict
import hashlib
import html
import json
from pathlib import Path
import statistics

from sparse_context_policy import PROFILES,run,suitability
from sparse_context_audit import REPO,sha,read


def initial(**overrides):
    state=dict(region='synthetic_region_A',location='synthetic_generic_A',selector='reviewed_generic',
               daypart='day',weather='clear',activity='foot',game_state='exploration',native_owner='generic',
               threatened=False,scene=False,paused=False,loading=False,outro_clear=True)
    state.update(overrides);return state


def context(t,generation=0,**values):return dict(time=t,kind='context',generation=generation,values=values)
def opportunity(t,id,type='first_discovery',generation=0,**values):
    return dict(time=t,kind='opportunity',type=type,id=id,generation=generation,first=True,local=True,**values)


def traces():
    rows=[]
    def add(id,duration,events):
        rows.append(dict(id=id,duration=duration,provenance='simulated',
            evidence_limit='Synthetic normalized inputs, not captured gameplay. native_owner/reviewed selector/outro_end and playback acceptance are oracle contracts, not verified script getters.',
            events=sorted(events,key=lambda e:e['time'])))
    add('stable_exploration',3600,[context(0,**initial()),opportunity(900,'pin-A'),opportunity(910,'pin-A'),
        context(1500,weather='rain'),opportunity(1500,'weather-A','weather_change'),context(2100,activity='horse'),
        context(2700,activity='foot',daypart='night',game_state='exploration_night')])
    add('optional_not_compulsory',900,[context(0,**initial()),opportunity(1,'pin-B'),
        opportunity(10,'arrival-B','location_arrival')]+[opportunity(t,'pin-B') for t in range(5,80,5)]+
        [context(80,native_owner='authored'),context(130,native_owner='generic'),
         context(200,selector='ambiguous_world'),context(300,selector='reviewed_generic')])
    add('native_priority',1400,[context(0,**initial(daypart='night',game_state='exploration_night')),
        opportunity(130,'pin-C'),context(180,game_state='combat',native_owner='combat'),
        context(205,game_state='exploration',native_owner='generic'),
        dict(time=211,kind='outro_end',generation=0,combat_epoch=1),opportunity(250,'arrival-C','location_arrival'),
        context(450,native_owner='authored'),context(520,native_owner='generic'),
        context(600,game_state='dialog_scene',scene=True),context(630,game_state='exploration',scene=False),
        context(750,game_state='gwent'),context(780,game_state='exploration'),dict(time=900,kind='load'),
        context(920,generation=1,**initial(daypart='night',game_state='exploration_night')),
        context(1150,generation=1,native_owner='unknown'),context(1250,generation=1,native_owner='generic')])
    add('missing_outro_observation',1800,[context(0,**initial()),context(180,game_state='combat',native_owner='combat'),
        # Even an optimistic snapshot cannot clear the outstanding combat gate.
        context(210,game_state='exploration',native_owner='generic',outro_clear=True),opportunity(250,'pin-D')])
    add('duplicates_boundaries_load',1800,[context(0,**initial()),opportunity(10,'arrival-A','location_arrival')]+
        [context(t,location='synthetic_generic_A') for t in range(2,102,2)]+
        [context(t,location='synthetic_generic_'+('A' if t%2 else 'B')) for t in range(150,157)]+
        [opportunity(160,'arrival-A','location_arrival'),context(600,region='synthetic_region_B',location='synthetic_generic_C'),
         context(610,outro_clear=True),context(900,daypart='night',game_state='exploration_night'),
         dict(time=1000,kind='load'),context(1001,**initial()),
         context(1050,generation=1,**initial(daypart='night',game_state='exploration_night')),
         opportunity(1051,'stale-pin'),opportunity(1100,'fresh-pin',generation=1)])
    add('limited_palette',2400,[context(0,**initial(activity='horse')),opportunity(500,'arrival-E','location_arrival'),
                              context(1800,daypart='night',game_state='exploration_night',activity='foot')])
    return rows


def demo_cues(catalog,verify_local=True):
    chosen={'S04-a':'punctuation','S04-b':'punctuation','S16-2':'atmospheric'}
    out=[]
    for cue in catalog['approved_cues']:
        if cue['id'] in chosen:
            if verify_local and sha(REPO/cue['file'])!=cue['sha256']:raise ValueError('Accepted cue hash mismatch')
            out.append(dict(id=cue['id'],family=cue['composition_key'],seconds=cue['model_duration_seconds'],role=chosen[cue['id']],sha256=cue['sha256']))
    if len(out)!=3:raise ValueError('Exact approved illustrative subset missing')
    return out


def metrics(model,trace):
    starts=[r for r in model.records if r['kind']=='start'];counts=Counter(r['kind'] for r in model.records)
    exact=family=unsuitable=0;last_id={};last_family={};previous_end=0;longest=0
    cues={c['id']:c for c in model.cues};intervals=model.intervals
    for s,allocation in zip(starts,intervals):
        if s['time']-last_id.get(s['cue'],-1e9)<model.p.excerpt_gap:exact+=1
        if s['time']-last_family.get(s['family'],-1e9)<model.p.family_gap:family+=1
        last_id[s['cue']]=allocation['end'];last_family[s['family']]=allocation['end']
        unsuitable+=suitability(cues[s['cue']],s['context'])==0
        longest=max(longest,s['time']-previous_end);previous_end=allocation['end']
    longest=max(longest,trace['duration']-previous_end)
    allocated=sum(x['end']-x['start'] for x in intervals)
    reasons=Counter()
    for i in model.exposure:reasons[i['reason']]+=i['end']-i['start']
    return dict(starts=len(starts),completions=counts['complete'],interruptions=counts['interrupt'],
                allocation_seconds=allocated,allocation_fraction=allocated/trace['duration'],
                longest_no_sparse_allocation=longest,eligible_seconds=reasons['eligible'],
                palette_blocked_seconds=reasons['palette_empty_or_recent'],
                exposure_hazard=sum(x['hazard'] for x in model.exposure),
                recent_excerpt_repeats=exact,recent_family_repeats=family,editorial_hypothesis_mismatches=unsuitable,
                expired_opportunities=counts['opportunity_expired'],consumed_opportunities=counts['opportunity_consumed'],
                opened_opportunities=counts['opportunity_open'],cancelled_opportunities=counts['opportunity_cancelled'],
                pending_opportunities=len(model.windows),
                duplicates=counts['duplicate_opportunity'],rejected_opportunities=counts['opportunity_rejected'],
                per_cue=dict(Counter(s['cue'] for s in starts)))


def independent_check(model,trace):
    starts=[r for r in model.records if r['kind']=='start']
    if len(starts)!=len(model.intervals):raise ValueError('Missing committed allocation')
    kinds=Counter(r['kind'] for r in model.records)
    if kinds['opportunity_open']!=kinds['opportunity_expired']+kinds['opportunity_consumed']+kinds['opportunity_cancelled']+len(model.windows):
        raise ValueError('Lost/renewed opportunity accounting')
    previous=-1
    for start,i in zip(starts,model.intervals):
        c=start['context']
        if not(c['native_owner']=='generic' and c['outro_clear'] is True and c['selector']=='reviewed_generic'
               and c['game_state'] in ('exploration','exploration_night') and c['scene'] is False
               and c['threatened'] is False and c['paused'] is False and c['loading'] is False):raise ValueError('Native veto violated')
        if i['start']<previous-1e-8 or i['end']<i['start']:raise ValueError('Overlapping/negative allocation')
        previous=i['end']
        if i['reason']=='natural':
            duration=next(c['seconds'] for c in model.cues if c['id']==i['cue'])
            if abs(i['end']-i['start']-duration)>1e-6:raise ValueError('Natural phrase shortened')
    # Independent external veto edges must terminate any ongoing allocation.
    for e in trace['events']:
        v=e.get('values',{})
        veto=(e['kind']=='load' or v.get('native_owner','generic')!='generic'
              or v.get('game_state','exploration') not in ('exploration','exploration_night')
              or any(v.get(k) is True for k in ('paused','loading','scene','threatened'))
              or v.get('selector','reviewed_generic')!='reviewed_generic')
        if veto and any(i['start']<e['time']-1e-7 and i['end']>e['time']+1e-7 for i in model.intervals):
            raise ValueError('Cue survives external hard veto')
    return True


def write_html(path,representatives,summary):
    palette={'eligible':'#d9ead3','playing':'#84b4ed','palette_empty_or_recent':'#ddd','minimum_quiet':'#eee'}
    parts=['<!doctype html><meta charset="utf-8"><title>WMC contextual policy trial</title>',
           '<style>body{font:16px system-ui;max-width:1150px;margin:30px auto;padding:0 16px}svg{width:100%;height:34px}table{border-collapse:collapse}td,th{padding:5px 12px;border:1px solid #ccc}summary{cursor:pointer}pre{white-space:pre-wrap;font-size:13px}small{color:#555}</style>',
           '<h1>Contextual Sparse policy — simulated traces</h1><p>No audio, captured gameplay or approved pacing defaults. Blue: cue allocation; green: eligible but silent; grey: quiet/anti-repeat; amber: native/context veto; purple: optional opportunity window. Hover for timing, integrated hazard and cue identities. Allocation includes accepted tails and internal silence.</p>',
           '<p>All traces assume an unimplemented native ownership/selector/outro oracle. <a href="results.json">Results and parameters</a> · <a href="traces.json">Synthetic inputs</a> · <a href="summary.csv">Population summary</a></p>',
           '<h2>Population comparisons</h2><table><tr><th>Profile / approach</th><th>Starts/run</th><th>Allocation</th><th>Recent family repeats</th><th>Editorial mismatches</th><th>Expired windows</th></tr>']
    for row in summary:
        parts.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in (row['profile']+' / '+row['approach'],round(row['mean_starts'],2),str(round(row['mean_allocation_fraction']*100,1))+'%',row['recent_family_repeats'],row['editorial_hypothesis_mismatches'],row['expired_opportunities']))+'</tr>')
    parts.append('</table><p>Two explicitly different experimental hazard budgets; counts are descriptive, not equal-rate superiority or musical-quality scores. Randomized control shares every native safety gate.</p><h2>Trace review (published seed7, restrained profile)</h2>')
    for rep in representatives:
        d=rep['duration'];parts.append('<h3>'+html.escape(rep['id']+' / '+rep['approach'])+'</h3><svg viewBox="0 0 1000 44">')
        for r in rep['exposure']:
            x=r['start']/d*1000;width=max(.2,(r['end']-r['start'])/d*1000);color=palette.get(r['reason'],'#f7d69c')
            title=html.escape(f"{r['start']:.2f}–{r['end']:.2f}s {r['reason']}; integrated hazard={r['hazard']:.6f}")
            parts.append(f'<rect x="{x}" width="{width}" height="30" fill="{color}"><title>{title}</title></rect>')
        windows={}
        for event in rep['records']:
            if event['kind']=='opportunity_open':windows[event['event']]=event['time']
            if event['kind'] in ('opportunity_expired','opportunity_consumed','opportunity_cancelled') and event['event'] in windows:
                begin=windows.pop(event['event']);width=(event['time']-begin)/d*1000
                title=html.escape(f"{event['event']}: {begin:.2f}–{event['time']:.2f}s; {event['kind']}")
                parts.append(f'<rect x="{begin/d*1000}" y="34" width="{width}" height="8" fill="#a982c9"><title>{title}</title></rect>')
        for allocation in rep['allocations']:
            x=allocation['start']/d*1000
            title=html.escape(f"{allocation['cue']}: {allocation['start']:.2f}–{allocation['end']:.2f}s; {allocation['reason']}")
            parts.append(f'<text x="{x}" y="20" font-size="11"><title>{title}</title>{html.escape(allocation["cue"])}</text>')
        parts.append('</svg><small>'+html.escape(json.dumps(rep['metrics']))+'</small><details><summary>Decision/context/opportunity log</summary><pre>'+html.escape(json.dumps(rep['records'],indent=2))+'</pre></details>')
    path.write_text('\n'.join(parts),encoding='utf-8')


def trial(out,seeds=200,verify_local=True):
    if out.exists():raise FileExistsError(out)
    if seeds<1:raise ValueError('Positive seed count required')
    catalog=read(REPO/'research/92-context-signal-catalog.json');cues=demo_cues(catalog,verify_local);inputs=traces()
    for row in catalog['signals']:
        for ref in row['references']:
            for part in ('primary','redkit'):
                if verify_local and part in ref and sha(Path(ref[part]['path']))!=ref[part]['sha256']:raise ValueError('Audited source drift')
    out.mkdir(parents=True);runs=[];representatives=[];summary=[]
    for profile in PROFILES.values():
        for approach in ('randomized','contextual'):
            subset=[]
            for trace in inputs:
                for seed in range(seeds):
                    model=run(trace,cues,profile,seed,approach);independent_check(model,trace)
                    m=metrics(model,trace);row=dict(profile=profile.name,approach=approach,trace=trace['id'],seed=seed,**m)
                    subset.append(row);runs.append(row)
                    if seed==7 and profile.name=='restrained':
                        representatives.append(dict(id=trace['id'],approach=approach,duration=trace['duration'],
                            metrics=m,records=model.records,exposure=model.exposure,allocations=model.intervals))
            summary.append(dict(profile=profile.name,approach=approach,runs=len(subset),
                mean_starts=statistics.mean(r['starts'] for r in subset),
                mean_allocation_fraction=statistics.mean(r['allocation_fraction'] for r in subset),
                zero_start_runs=sum(r['starts']==0 for r in subset),
                recent_family_repeats=sum(r['recent_family_repeats'] for r in subset),
                recent_excerpt_repeats=sum(r['recent_excerpt_repeats'] for r in subset),
                editorial_hypothesis_mismatches=sum(r['editorial_hypothesis_mismatches'] for r in subset),
                expired_opportunities=sum(r['expired_opportunities'] for r in subset),
                interruptions=sum(r['interruptions'] for r in subset)))
    result=dict(schema=1,provenance='simulation only; no playback',profiles={k:asdict(v) for k,v in PROFILES.items()},
        installed_sources_checked_this_run=verify_local,three_private_cues_checked_this_run=verify_local,
        catalog_sha256=sha(REPO/'research/92-context-signal-catalog.json'),illustrative_cues=cues,seeds=[0,seeds-1],
        hazard='Integrated exponential threshold; baseline ramp + max active optional-window boost. No callback-count Bernoulli.',
        comparison_limit='Randomized constant rate differs from contextual hazard budget; shared native hard gates; no aesthetic success claim.',
        summary=summary,runs=runs,representatives=representatives)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (out/'traces.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
    with (out/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    write_html(out/'index.html',representatives,summary)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seeds',type=int,default=200)
    p.add_argument('--metadata-only',action='store_true',help='Portable math replay; explicitly does not reverify installed sources/audio')
    a=p.parse_args()
    root=a.output.resolve()
    if not root.is_relative_to((REPO/'build').resolve()):raise ValueError('Private output must be under ignored build')
    r=trial(root,a.seeds,not a.metadata_only);print(json.dumps(r['summary'],indent=2))
