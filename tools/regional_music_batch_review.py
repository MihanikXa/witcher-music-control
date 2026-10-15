"""Read-only manifest-bound paired playback review; never claims retail proof."""
import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from regional_playback_review import summarize, static_voice_checks, outro_checks
from white_orchard_prepare import build_path, digest


def collect(manifest, matrices):
    captures=[];summaries=[];folders=set()
    for path in matrices:
        matrix=json.loads(path.read_text())
        if matrix['manifest_sha256']!=digest(manifest):raise ValueError('Stale playback manifest')
        for group in matrix['groups']:
            folder=build_path(group['summary']['folder'])
            if folder in folders:raise ValueError('Duplicate capture group')
            folders.add(folder)
            summary=summarize(folder)
            if (summary['raw_sha256']!=group['summary']['raw_sha256']
                    or summary['measurement_sha256']!=group['summary']['measurement_sha256']):
                raise ValueError('Stale matrix raw/PCM measurement proof')
            raw=json.loads((folder/'results.json').read_text())
            counts=Counter((c['mode'],c['case']) for c in raw['cases'])
            names={c['case'] for c in raw['cases']}
            if counts!=Counter((m,n) for m in ('native-reference','manifest') for n in names):
                raise ValueError('Incomplete or duplicate paired capture')
            captures.extend(raw['cases']);summaries.append(summary)
    if not captures:raise ValueError('Empty playback evidence')
    return captures,summaries


def master_curves(captures):
    curves=[]
    for case in captures:
        if case['case'] not in ('music-master','protected-direct'):continue
        values={}
        for sample in case['samples']:
            for contribution in sample['contributions'].values():
                for node in contribution['return']['objects']:
                    if node['name']!='Music':continue
                    for prop in node.get('parameters',[]):
                        if prop.get('reason')=='RTPC' and prop.get('propertyType')=='Volume':
                            values.setdefault(str(prop['driverValue']),set()).add(prop['value'])
        if not values:continue
        if (values.get('100.0')!={0.0} or not values.get('50.0')
                or any(abs(v+6.0206003)>.001 for v in values['50.0'])):
            raise ValueError('Music master curve differs or 100/50 control missing')
        curves.append({'mode':case['mode'],'case':case['case'],'values':{k:sorted(v) for k,v in values.items()}})
    if {r['mode'] for r in curves}!={'native-reference','manifest'}:
        raise ValueError('Paired native/modified Music master evidence missing')
    return curves


def review(manifest, source_music, matrices, return_group, return_playlist, peak, mechanism):
    spec=json.loads(manifest.read_text())
    if digest(source_music)!=spec['facts']['original_music_sha256']:
        raise ValueError('Playback source fingerprint differs from manifest')
    captures,summaries=collect(manifest,matrices)
    static=static_voice_checks(captures,spec,ET.parse(source_music))
    selected=[s for s in summaries if Path(s['folder']).name==return_group]
    if len(selected)!=1:raise ValueError('Exact return control group required')
    returns=outro_checks(selected[0],return_playlist,peak,('combat-sustain','combat-sustain-offset'))
    if mechanism not in ('named-native-outro','native-combat-return-tail'):
        raise ValueError('Explicit measured return mechanism required')
    return {'passed':True,'region':spec['region'],'manifest_sha256':digest(manifest),
            'static_voice_checks':static,'transition_review':{'passed':True,'mechanism':mechanism,
                'named_outro_observed':mechanism=='named-native-outro','checks':returns},
            'music_master_curves':master_curves(captures),'captures':len(captures),
            'groups':summaries,'fixtures_only':True,'retail_validated':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('manifest','source-music','output'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--matrices',type=Path,nargs='+',required=True)
    p.add_argument('--return-group',required=True);p.add_argument('--return-playlist',required=True)
    p.add_argument('--peak',type=float,required=True);p.add_argument('--mechanism',required=True)
    a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    r=review(a.manifest,a.source_music,a.matrices,a.return_group,a.return_playlist,a.peak,a.mechanism)
    out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'passed':r['passed'],'captures':r['captures'],'measured_static_targets':len(r['static_voice_checks']['measured_static_subset'])}))
