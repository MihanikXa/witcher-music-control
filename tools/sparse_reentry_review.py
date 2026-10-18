"""Measured re-entry metrics; source, profiler, PCM and retail are distinct gates."""
import math
import statistics


def points(case,role):
    return [p for v in case['pipelines'] if v['role']==role for p in v['envelope']]


def audible_times(case,role,after=-math.inf):
    return [t for t,db,started,virtual in points(case,role) if t>=after and db>-90 and started and not virtual]


def combat_metrics(case):
    entries=[e['accepted'] for e in case['events'] if e['kind']=='state' and e['name']=='combat']
    returns=[e['accepted'] for e in case['events'] if e['kind']=='state' and e['name']=='exploration']
    if not entries or not returns:raise ValueError('Missing actual combat/return acknowledgements')
    back=returns[-1];outro=[p for p in points(case,'outro') if p[0]>back-.5]
    if not outro:raise ValueError('No observed native outro')
    lo,hi=min(p[0] for p in outro),max(p[0] for p in outro)
    middle=[p[1] for p in outro if lo+.5<p[0]<hi-.5]
    if not middle:raise ValueError('Incomplete outro envelope')
    cues=audible_times(case,'cue',back)
    new=min(cues,default=None)
    body=audible_times(case,'combat',entries[0]);first=min(body,default=None)
    rtpc=case['rtpcs'].get('18446744073709551614:threat_rating',[])
    all_outros=[]
    cue_times=audible_times(case,'cue')
    for voice in (v for v in case['pipelines'] if v['role']=='outro'):
        env=voice['envelope'];a,b=env[0][0],env[-1][0]
        mid=[p[1] for p in env if a+.5<p[0]<b-.5]
        gain=statistics.median(mid) if mid else None
        all_outros.append(dict(first=a,last=b,span=b-a,middle_db=gain,
                               native_complete=4.4<b-a<5.4 and gain is not None and abs(gain+19)<.1,
                               cue_overlap=any(a<=t<=b for t in cue_times)))
    # Explicitly fail on missing observed finite re-entry or wrong scope RTPCs.
    return dict(combat_accepted=entries[0],exploration_accepted=back,
                entry_latency=None if first is None else first-entries[0],
                outro_first=lo,outro_last=hi,outro_span=hi-lo,
                outro_middle_db=statistics.median(middle),
                cue_after_return=new,cue_delay=None if new is None else new-back,
                cue_outro_overlap=None if new is None else new<hi,
                threat_values=rtpc,
                all_outros=all_outros,
                complete_native_outros=all(v['native_complete'] for v in all_outros),
                no_cue_during_any_outro=not any(v['cue_overlap'] for v in all_outros),
                complete_native_outro=(4.4<hi-lo<5.4 and abs(statistics.median(middle)+19)<.1),
                bounded_quiet_return=(new is not None and hi+.25<new<back+65),
                tested_30s_guard=(new is not None and 25<new-back<40),
                threat_0_35_100=set(rtpc)=={0,35,100})


def return_metrics(case):
    returns=[e for e in case['events'] if e['name'] in ('mus_loc_prologue_village','exploration')]
    if not returns:raise ValueError('No return')
    back=returns[-1]['accepted'];cue=audible_times(case,'cue',back+.2)
    rest=points(case,'rest');initial_rest=min((p[0] for p in rest),default=None)
    rest_after=[v for v in case['pipelines'] if v['role']=='rest' and v['first']>back]
    return dict(return_accepted=back,next_cue=min(cue,default=None),
                delay=None if not cue else min(cue)-back,
                uninterrupted_nominal_boundary=None if initial_rest is None else initial_rest+30,
                new_rest_pipelines=[dict(pipeline=v['pipeline'],first=v['first'],last=v['last']) for v in rest_after])


def redundant_metrics(case,expected_events=3):
    if len(case['events'])!=expected_events:raise ValueError('Missing planned independent-phase redundant updates')
    cues=sorted((v for v in case['pipelines'] if v['role']=='cue'),key=lambda v:v['first'])
    if len(cues)<2:raise ValueError('Missing cue recurrence')
    cadences=[b['first']-a['first'] for a,b in zip(cues,cues[1:])]
    continued=all(abs(cadence-60.85)<.7 for cadence in cadences)
    return dict(first_pipeline=cues[0]['pipeline'],first=cues[0]['first'],last=cues[0]['last'],
                second=cues[1]['first'],cadence=cues[1]['first']-cues[0]['first'],
                normal_cadence_preserved=continued,cadences=cadences,events=case['events'])


def intensity_metrics(case):
    """Use accepted changes on the actual transport, not a nominal wall clock."""
    changes=[e for e in case['events'] if e['kind']=='rtpc' and e['name']=='threat_rating']
    start=next(e['accepted'] for e in case['events'] if e['name']=='combat')
    end=next(e['accepted'] for e in case['events'] if e['name']=='exploration')
    if [e['value'] for e in changes]!=[35,100]:raise ValueError('Missing controlled threat sequence')
    windows=[(0,start+3,changes[0]['accepted']-.5),
             (35,changes[0]['accepted']+1,changes[1]['accepted']-.5),
             (100,changes[1]['accepted']+1,end-.5)]
    levels={}
    for layer in ('layer1','layer2'):
        voices=[v for v in case['pipelines'] if v['path'][0].endswith(layer)]
        levels[layer]={}
        for value,lo,hi in windows:
            selected=[p[1] for v in voices for p in v['envelope'] if lo<p[0]<hi and p[2] and not p[3]]
            levels[layer][str(value)]=statistics.median(selected) if selected else None
    a,b=levels['layer1'],levels['layer2']
    # The threat-zero window can still contain the original entry crossfade.
    passed=(a['0'] is not None and a['0']>-90
            and all(a[k] is not None and abs(a[k]+17)<.1 for k in ('35','100'))
            and b['0'] is not None and b['0']<-200
            and all(b[k] is not None and abs(b[k]+19)<.1 for k in ('35','100'))
            and set(case['rtpcs'].get('18446744073709551614:threat_rating',[]))=={0,35,100})
    return dict(passed=passed,levels=levels,windows=windows)


def master_metrics(case,role='cue',native_db=-19):
    changes=[e for e in case['events'] if e['kind']=='rtpc' and e['name']=='menu_volume_music']
    if [e['value'] for e in changes]!=[50,100]:raise ValueError('Missing Music master controls')
    env=points(case,role)
    windows=[(50,changes[0]['accepted']+2,changes[0]['accepted']+4),
             (100,changes[1]['accepted']+2,changes[1]['accepted']+4)]
    levels={}
    for value,lo,hi in windows:
        selected=[p[1] for p in env if lo<p[0]<hi and p[2] and not p[3]]
        levels[str(value)]=statistics.median(selected) if selected else None
    passed=(levels['50'] is not None and abs(levels['50']-(native_db-6.0206))<.1
            and levels['100'] is not None and abs(levels['100']-native_db)<.1)
    return dict(passed=passed,levels=levels,windows=windows)
