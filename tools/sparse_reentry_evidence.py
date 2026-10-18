"""Finalize this bounded experiment from immutable local captures; no playback.

Fail on missing coverage, invalid PCM, source drift, missing real re-entry or
muted/cropped outro. Expected negative A/baseline observations remain evidence,
not passing claims of persistence. No raw audio or third-party XML is exported.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from sparse_reentry_pilot import ROOT,PRIOR,SOURCE
from sparse_reentry_review import (combat_metrics,return_metrics,redundant_metrics,
                                   intensity_metrics,master_metrics,points)
from sparse_approved_cue import read,REPO
from white_orchard_prepare import digest,build_path


def finalize(output):
    checks=[];inputs=[];groups={}
    def check(name,value):checks.append(dict(name=name,passed=bool(value)))
    def load(path):
        inputs.append(dict(path=path.relative_to(REPO).as_posix(),sha256=digest(path)))
        return read(path)
    source=load(ROOT/'source-gate-final-v3.json')
    check('complete-source-and-preservation',source['passed'])
    state_path=SOURCE/'States/global_states.wwu'
    inputs.append(dict(path=str(state_path),sha256=digest(state_path)))
    state_group=next(n for n in ET.parse(state_path).iter('StateGroup') if n.get('Name')=='game_state')
    native_times={(n.find('StartState').get('Name'),n.find('EndState').get('Name')):float(n.findtext('Time'))
                  for n in state_group.findall('./TransitionList/Transition')}
    dialogue_fade=native_times['exploration','dialog_scene']
    check('original-explicit-and-fallback-dialogue-duration',dialogue_fade==native_times['None','dialog_scene']==2)
    paths={
        'baseline': ['baseline-a/validation/diagnosis-v1','baseline-a/validation/event-confirmation-v1',
                     'baseline-b/validation/diagnosis-v2','baseline-c/validation/diagnosis-v2'],
        'history-rest':['candidate-a/validation/discriminators-v3','candidate-a/validation/history-early-v1'],
        'rest-first':['candidate-b/validation/discriminators-v1','candidate-b/validation/regression-v1',
                      'candidate-b/validation/dialogue-v1']}
    case_counts={};observer_coverage=[];state_observations=[]
    for group,folders in paths.items():
        rows={};case_counts[group]=0
        for rel in folders:
            folder=ROOT/rel;data=load(folder/'measurements.json');case_counts[group]+=len(data['cases'])
            raw=load(folder/'results.json')
            check(rel+':complete-clean',raw['complete'] and not raw['cleanup_errors'] and not raw.get('error'))
            check(rel+':source-fingerprint',data['source_sha256']==digest(folder.parent/'authored-music.xml'))
            legacy=rel in ('baseline-a/validation/diagnosis-v1','baseline-b/validation/diagnosis-v2','baseline-c/validation/diagnosis-v2')
            observer_coverage.append(dict(path=rel,cases=len(raw['cases']),
                getter_cases=sum('initial_engine' in c for c in raw['cases']),
                limitation='Baseline precedes getter observer; API acknowledgements/profiler only.' if legacy else None))
            for captured in raw['cases']:
                if legacy:continue
                check(rel+':'+captured['case']+':initial-State',
                      captured['initial_engine']['game_state']['return']['name']==captured['initial_state'])
                previous=captured['initial_state']
                for e in captured['events']:
                    if e['kind']=='state':
                        seen=e['engine_after']['game_state']['return']['name']
                        state_observations.append(dict(path=rel,case=captured['case'],accepted=e['accepted'],
                            requested=e['name'],immediate_getter=seen,previous=previous))
                        check(rel+':'+captured['case']+':known-asynchronous-State',seen in (previous,e['name']))
                        previous=e['name']
                    locations={'mus_loc_prologue_village':'village','mus_loc_prologue_nilfgaard_camp':'nilfgaard_camp'}
                    if e['kind']=='event' and e['name'] in locations:
                        check(rel+':'+captured['case']+':location-ack',e['engine_after']['location']['return']['name']==locations[e['name']])
            for case in data['cases']:
                # The unfinished first event WAV is retained, never approved.
                if group=='baseline' and case['case']=='redundant-event':
                    check('bad-initial-PCM-rejected',not case['pcm']['valid']);continue
                check(rel+':'+case['case']+':finalized-PCM',case['pcm']['valid'] and case['pcm']['peak']<32767)
                check(rel+':'+case['case']+':PCM-identity',digest(folder/(case['case']+'.wav'))==case['pcm']['sha256'])
                name=case['case'];rows[name]=dict(pcm_sha256=case['pcm']['sha256'],pcm_seconds=case['pcm']['seconds'])
                if 'combat' in name:
                    rows[name]['combat']=combat_metrics(case)
                    if name!='rapid-combat':rows[name]['intensity']=intensity_metrics(case)
                if name.startswith(('location-','daynight-')):rows[name]['return']=return_metrics(case)
                if name.startswith('redundant-'):
                    rows[name]['redundant']=redundant_metrics(case,5 if group=='rest-first' else 3)
                if group=='rest-first':
                    if 'combat' in name:
                        m=rows[name]['combat']
                        check(name+':native-outro-and-bounded-return',m['complete_native_outro'] and m['bounded_quiet_return']
                              and m['complete_native_outros'] and m['no_cue_during_any_outro']
                              and not m['cue_outro_overlap'] and m['threat_0_35_100'] and 0<=m['entry_latency']<4.1)
                        if name!='rapid-combat':check(name+':native-intensity',rows[name]['intensity']['passed'])
                    if name.startswith('redundant-'):check(name+':continued-cadence',rows[name]['redundant']['normal_cadence_preserved'])
                    if name.startswith(('location-','daynight-')):
                        delay=rows[name]['return']['delay']
                        check(name+':fresh-bounded-rest',delay is not None and 20<delay<40)
                    if name.startswith('authored-'):
                        auth=[v for v in case['pipelines'] if 933909186 in v['ids']]
                        levels=[p[1] for v in auth for p in v['envelope'] if p[2] and not p[3]]
                        rows[name]['authored_peak_db']=max(levels,default=None)
                        check(name+':authored-native-gain',levels and abs(max(levels)+22)<.1)
                        when=next(e['accepted'] for e in case['events'] if e['name']=='mus_q001_tavern_conversation')
                        late=[p for p in points(case,'cue') if p[0]>when+4 and p[2] and not p[3] and p[1]>-90]
                        check(name+':no-late-generic-cue',not late)
                    if name in ('dialogue-music','dialogue-scenes'):
                        bad=[]
                        for i,e in enumerate(case['events']):
                            if e['kind']!='state' or e['name']!='dialog_scene':continue
                            end=next((q['accepted'] for q in case['events'][i+1:] if q['kind']=='state'),case['last_sample'])
                            # Original global_states.wwu pins exploration→dialogue
                            # and fallback dialogue fades to2s; preserve the fade.
                            bad.extend(p for p in points(case,'cue') if e['accepted']+dialogue_fade+.3<p[0]<end and p[1]>-200 and p[2] and not p[3])
                        check(name+':generic-dialogue-suppressed',not bad)
                    if name=='gwent':
                        vals=[p[1] for p in points(case,'other') if p[2] and not p[3]]
                        rows[name]['peak_db']=max(vals,default=None)
                        check('gwent-native-gain',vals and abs(max(vals)+17)<.1)
                    if name in ('cycles-master','protected-world'):
                        m=master_metrics(case,'cue' if name=='cycles-master' else 'other',-19 if name=='cycles-master' else -17)
                        rows[name]['master']=m;check(name+':Music-master',m['passed'])
        groups[group]=rows
    expected={'redundant-event','location-music','daynight-music','location-early','daynight-late',
              'combat-music','combat-early','combat-late','rapid-combat','cycles-master',
              'authored-music','authored-rest','authored-recovery','dialogue-scenes','dialogue-music','protected-world','gwent'}
    check('rest-first-exact-case-coverage',set(groups['rest-first'])==expected)
    waveform=load(ROOT/'candidate-b-pcm-proof.json');check('complete-approved-waveform-tail-rest',waveform['passed'])
    prior=load(REPO/'research/87-approved-cue-sparse-evidence.json')
    # Reuse preserved native/Minimal evidence, not newly asserted playback.
    comparisons={}
    for mode in ('native','minimal'):
        path=PRIOR/mode/'validation/matrix-v1/approved-cue-measurements.json'
        data=load(path);comparisons[mode]=dict(cases=len(data['cases']),regenerated=False)
    lifecycle=[]
    for rel in paths['rest-first']+['candidate-a/validation/history-early-v1','candidate-b/validation/state-settling-v1']:
        folder=ROOT/rel;record=load(folder.parent/(folder.name+'-lifecycle.json'))
        check(rel+':closed-source-exact',record['closed'] and record['source_exact'] and not record['errors']
              and record['remaining_transports']=={'list':[]})
        lifecycle.append(dict(path=rel,closed=record['closed'],source_exact=record['source_exact']))
    old_a=load(ROOT/'candidate-a/validation/discriminators-v3-lifecycle.json')
    expected_a=next(p['source_sha256'] for p in source['projects'] if p['name']=='candidate-a')
    exception=dict(raw_source_exact=old_a['source_exact'],source_after_sha256=old_a['source_after_sha256'],
                   independently_verified_sha256=expected_a,
                   reason='Expected hash variable was shadowed by a settings tuple; fixed for subsequent capture.')
    check('A-discriminator-independent-source-and-cleanup',old_a['source_after_sha256']==expected_a
          and old_a['closed'] and not old_a['errors'] and old_a['remaining_transports']=={'list':[]})
    settling=load(ROOT/'candidate-b/validation/state-settling-v1/results.json')
    check('settling-probe-complete-clean',settling['complete'] and not settling['cleanup_errors'] and not settling.get('error'))
    settled=[]
    for event in settling['cases'][0]['events']:
        samples=event['engine_after']['state_settling'];matched=[s for s in samples if s['state']==event['name']]
        check('settled-State:'+event['name'],bool(matched) and samples[-1]['state']==event['name'] and samples[-1]['time']<1)
        settled.append(dict(requested=event['name'],samples=samples,first_matching_delay=matched[0]['time'] if matched else None))
    result=dict(schema=1,passed=all(c['passed'] for c in checks),checks=checks,source=source,
                inputs=inputs,capture_case_counts=case_counts,groups=groups,prior_controls=comparisons,
                historical_report87_status=prior['status'],waveform={k:v for k,v in waveform.items() if k!='pcm'},cleanup=lifecycle,
                retained_lifecycle_defect=exception,
                observer_coverage=observer_coverage,
                immediate_State_observations=state_observations,settling_probe=settled,
                native_dialogue_fade_seconds=dialogue_fade,
                generated_banks=False,new_bank_verified=False,retail_verified=False,defaults_approved=False)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    r=finalize(out);print(json.dumps(dict(passed=r['passed'],failed=[x['name'] for x in r['checks'] if not x['passed']])))
    if not r['passed']:raise SystemExit(1)
