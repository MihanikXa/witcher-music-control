"""Read-only acceptance review of three completed sparse authoring controls."""
import argparse
import json
from pathlib import Path
import statistics

from white_orchard_prepare import build_path, digest


def matching(case,short_id):
    return [v for v in case['voices'].values() if any(str(n['short_id'])==str(short_id)
        for chain in v.get('source_ancestry',{}).values() for n in chain)]


def values(voices,start,end):
    return [v for voice in voices for t,v in voice['envelope'] if start<=t<end]


def review_authored_rest(folders,output):
    """Separate supplement, deliberately not substituted for the nine-case matrix."""
    output=build_path(output)
    if output.exists():raise FileExistsError(output)
    rows={}
    for role,folder in folders.items():
        folder=build_path(folder)
        m=json.loads((folder/'sparse-measurements.json').read_text())
        if m['mode']!=role or m['raw_sha256']!=digest(folder/'results.json'):
            raise ValueError('Wrong/stale supplemental control')
        if len(m['cases'])!=1 or m['cases'][0]['case']!='authored-rest':
            raise ValueError('Expected authored-rest supplement only')
        c=m['cases'][0]
        if not c['complete']:raise ValueError('Incomplete supplement')
        voices=matching(c,933909186)
        accepted=next(e['accepted'] for e in c['events'] if e['kind']=='event')
        first=min(t for v in voices for t,db in v['envelope'] if db>-90)
        rows[role]=dict(event_accepted=accepted,first_authored_voice=first,
            steady_authored_db=statistics.median(values(voices,165,175)),
            raw_sha256=m['raw_sha256'],measurements_sha256=digest(folder/'sparse-measurements.json'))
        if role=='sparse':
            rows[role]['active_rest_before_event']=bool(values(matching(c,4111369),150,151))
    passed=(rows['sparse']['active_rest_before_event'] and
            abs(rows['sparse']['steady_authored_db']-rows['native']['steady_authored_db'])<.05 and
            all(0<r['first_authored_voice']-r['event_accepted']<6 for r in rows.values()))
    result=dict(passed=passed,controls=rows,fixtures_only=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


def review(native,minimal,sparse,output):
    output=build_path(output)
    if output.exists():raise FileExistsError(output)
    data={};checks=[];details={}
    for role,folder in [('native',native),('minimal',minimal),('sparse',sparse)]:
        folder=build_path(folder);m=json.loads((folder/'sparse-measurements.json').read_text())
        if m['mode']!=role or m['raw_sha256']!=digest(folder/'results.json'):
            raise ValueError('Wrong/stale measured control')
        data[role]={c['case']:c for c in m['cases']}
        if len(data[role])!=9 or any(not c['complete'] for c in m['cases']):raise ValueError('Incomplete matrix')
    def check(name,passed):checks.append(dict(name=name,passed=bool(passed)))
    cycles=data['sparse']['two-cycles'];ncycles=data['native']['two-cycles'];dcycles=data['minimal']['two-cycles']
    music=matching(cycles,133462974);rest=matching(cycles,4111369)
    check('audible-selected-native-gain',abs(statistics.median(values(music,5,15))-
        statistics.median(values(matching(ncycles,133462974),5,15)))<.05)
    check('Minimal-control-suppressed',max(values(matching(dcycles,133462974),5,15))<-180)
    check('native-rest-voice-selected',bool(rest))
    quiet=[span for span in cycles['pcm']['zero_windows'] if span[1]-span[0]>15]
    check('two-measured-environmental-rests',len(quiet)==2 and all(21<x[1]-x[0]<23 for x in quiet))
    check('audible-second-and-third-phrase',min(values(music,180,190))>-90 and min(values(music,343,347))>-90)
    for a,b,label in [(5,15,'100-initial'),(23,30,'50'),(43,48,'100-restored')]:
        check('master-'+label,abs(statistics.median(values(music,a,b))-
            statistics.median(values(matching(ncycles,133462974),a,b)))<.05)
    details['rests_audio_seconds']=quiet
    details['intensity']={}
    for layer in ('layer1','layer2'):
        trajectory={}
        for role in ('native','sparse'):
            c=data[role]['combat-music-authored']
            voices=[v for v in c['voices'].values() if any(
                name.endswith('_'+layer) for name in v['path'])]
            trajectory[role]=[statistics.median(values(voices,a,b))
                              for a,b in ((10,12),(16,18),(23,27))]
        check('intensity-'+layer+':native-response',all(abs(a-b)<.05
            for a,b in zip(trajectory['native'],trajectory['sparse'])))
        details['intensity'][layer]=trajectory
    details['context_limits']={}
    for name in ('place-daynight-music','place-daynight-rest'):
        c=data['sparse'][name]
        others=[v for v in c['voices'].values() if any(
            x in v['path'] for x in ('expl_nml_zone_01_PROLOGUE_NIGHT','expl_nilfgaard_camp'))]
        check(name+':other-generic-selections-suppressed',bool(others) and
              all(v['peak_db']<-190 for v in others))
        dialog=(46,48) if name.endswith('music') else (189,190)
        check(name+':ordinary-dialogue-suppressed',max(values(matching(c,133462974),*dialog))<-190)
        details['context_limits'][name]={
            'selected_intervals':[(v['path'],v['intervals']) for v in matching(c,319905093)],
            'rest_intervals':[(v['path'],v['intervals']) for v in matching(c,4111369)],
            'interpretation':'Native reselection can cancel rest/restart phrase; movie/music_only retain unity policy'}
    details['combat']={}
    for case_name in ('combat-music-authored','combat-rest-early','combat-rest-late'):
        rows={}
        for role in data:
            case=data[role][case_name]
            combat=next(e['accepted'] for e in case['events'] if e['name']=='combat')
            returned=next(e['accepted'] for e in case['events'] if e['name']=='exploration')
            outro=matching(case,800050000)
            if not outro:raise ValueError('Missing actual native outro voice')
            env=[x for v in outro for x in v['envelope']]
            first=min(t for t,v in env);last=max(t for t,v in env)
            middle=[v for t,v in env if first+.5<t<last-.5]
            body=[v for v in case['voices'].values() if '/village_combat/' in '/'.join(v['path'])]
            start=min(t for v in body for t,db in v['envelope'])
            rows[role]=dict(combat_accepted=combat,combat_voice_latency=start-combat,
                E_accepted=returned,outro_first=first,outro_last=last,outro_span=last-first,
                outro_middle_db=statistics.median(middle),outro_peak=max(v for t,v in env))
            if role!='minimal':
                check(case_name+':'+role+':natural-complete-outro',4.3<last-first<5.5 and last<max(
                    t for v in body+outro+matching(case,133462974) for t,db in v['envelope'])-10)
                check(case_name+':'+role+':outro-after-E',first>=returned-.2 and last>returned+3)
                check(case_name+':'+role+':combat-responds',0<=start-combat<4.1)
            actual={value for key,vals in case['effective_rtpcs'].items()
                    if key=='18446744073709551614:threat_rating' for value in vals}
            check(case_name+':'+role+':actual-threat-values',{0,35,100}<=actual)
        check(case_name+':native-outro-gain',abs(rows['native']['outro_middle_db']-rows['sparse']['outro_middle_db'])<.05)
        if case_name!='combat-music-authored':
            c=data['sparse'][case_name];t=rows['sparse']['combat_accepted']
            check(case_name+':interrupts-active-rest',bool(values(matching(c,4111369),t-.5,t)))
            check(case_name+':no-generic-music-prelude',not any(db>-90 for db in values(matching(c,319905093),t,t+1)))
        details['combat'][case_name]=rows
    for case_name,ident in [('authored-master',933909186),('protected-world',589261176),('gwent',None)]:
        c=data['sparse'][case_name];n=data['native'][case_name]
        cv=matching(c,ident) if ident else list(c['voices'].values())
        nv=matching(n,ident) if ident else list(n['voices'].values())
        check(case_name+':audible',bool(cv) and max(values(cv,3,7))>-90)
        check(case_name+':native-gain',abs(statistics.median(values(cv,3,7))-statistics.median(values(nv,3,7)))<.1)
    result=dict(passed=all(x['passed'] for x in checks),checks=checks,details=details,
        fixtures_only=True,bank_generated=False,retail_validated=False,
        protected_world_note='Separately declared report35 technical gain-isolation control, not new shipped policy')
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('native','minimal','sparse','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--authored-rest',action='store_true')
    a=p.parse_args()
    r=(review_authored_rest(dict(native=a.native,minimal=a.minimal,sparse=a.sparse),a.output)
       if a.authored_rest else review(a.native,a.minimal,a.sparse,a.output))
    print(json.dumps(dict(passed=r['passed'],failed=[c['name'] for c in r.get('checks',[]) if not c['passed']])))
    if not r['passed']:raise SystemExit(1)
