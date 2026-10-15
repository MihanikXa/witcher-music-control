"""Read-only profiler evidence summary; source/bank/runtime gates stay separate."""
import argparse
import json
import statistics
from pathlib import Path
from white_orchard_prepare import build_path, digest


def static_voice_checks(captures, spec, source_tree):
    """Measured subset only: verify actual gain ancestry and reject generic bleed."""
    from regional_music import graph, ancestors
    objects,parents,_=graph(source_tree)
    prefixes={}
    for ident in spec['static_targets']:
        names=[]
        for node in ancestors(objects[ident],parents):
            if node.tag in ('MusicSwitchContainer','MusicPlaylistContainer','MusicSegment'):
                names.append(node.get('Name'))
            if node.get('ID')==spec['facts']['root']['id']:
                break
        else:
            raise ValueError('Static target outside regional ancestry')
        prefixes[ident]=tuple(reversed(names))
    observed={}
    for case in captures:
        if case['mode']!='manifest':continue
        for sample in case['samples']:
            for contribution in sample['contributions'].values():
                data=contribution['return'];nodes=data['objects'];names=[n['name'] for n in nodes]
                if spec['facts']['root']['name'] not in names:continue
                start=names.index(spec['facts']['root']['name'])
                for ident,prefix in prefixes.items():
                    if tuple(names[start:start+len(prefix)])!=prefix:continue
                    node=nodes[start+len(prefix)-1]
                    values=[p['value'] for p in node.get('parameters',[]) if p.get('reason')=='SoundBankValue' and p.get('propertyType')=='Volume']
                    if values!=[-200.0] or data['volume']>-180:
                        raise ValueError('Measured generic gain missing or exploration bleed')
                    row=observed.setdefault(ident,{'samples':0,'maximum_total_db':float('-inf')})
                    row['samples']+=1;row['maximum_total_db']=max(row['maximum_total_db'],data['volume'])
    if not observed:
        raise ValueError('No measured static playlist voices; silence is not proof')
    return {'passed':True,'measured_static_subset':observed,
            'all_targets_auditioned':len(observed)==len(prefixes)}


def summarize(folder):
    raw = json.loads((folder / 'results.json').read_text(encoding='utf-8'))
    measured = json.loads((folder / 'transition-measurements.json').read_text(encoding='utf-8'))
    if measured['evidence_sha256'] != digest(folder / 'results.json'):
        raise ValueError('Stale playback measurements')
    rows = []
    for case in measured['cases']:
        capture = next(c for c in raw['cases'] if (c['mode'], c['case']) == (case['mode'], case['case']))
        last = capture['samples'][-1]['time']
        voices = {}
        for key, voice in case['voices'].items():
            envelope = voice['envelope']
            if not envelope or not key:
                continue
            windows = {}
            for start, end in [(4.5, 5.8), (8.5, 9.8), (12, 13), (16, 18.5)]:
                values = [v['total_db'] for v in envelope if start <= v['wall_time'] < end]
                windows[f'{start}-{end}'] = statistics.median(values) if values else None
            voices[key] = {'object': voice['object'], 'first': envelope[0]['wall_time'],
                'last': envelope[-1]['wall_time'], 'peak_db': max(v['total_db'] for v in envelope),
                'median_db_windows': windows,
                'ended_before_capture_stop': envelope[-1]['wall_time'] < last - 5}
        rtpcs = {}
        for sample in capture['samples']:
            for value in sample.get('rtpcs', []):
                rtpcs.setdefault(str(value['gameObjectId']) + ':' + value['name'], set()).add(value['value'])
        rows.append({'mode': case['mode'], 'case': case['case'], 'capture_last': last,
                     'events': capture['events'], 'voices': voices,
                     'effective_rtpc_values': {k: sorted(v) for k, v in rtpcs.items()},
                     'recording_present': case['recording_present'],
                     'pcm_sha256': case.get('pcm', {}).get('sha256'),
                     'pcm_seconds': case.get('pcm', {}).get('seconds'),
                     'pcm_rms50ms_peak': max(case['pcm']['rms50ms']) if case.get('pcm') else None})
    return {'folder': str(folder), 'raw_sha256': digest(folder / 'results.json'),
            'measurement_sha256': digest(folder / 'transition-measurements.json'), 'cases': rows,
            'limitation': 'Wall/PCM origins differ; virtual-bus Recorder absence is not measured zero PCM. Native playlist history/random choice is not reset by transport stop.'}


def outro_checks(summary, playlist, expected_peak, case_names=('e-combat', 'e-combat-offset')):
    """Explicit paired cases: audible return cue completes after E, before stop."""
    if not case_names or len(set(case_names))!=len(case_names):
        raise ValueError('Explicit unique outro cases required')
    checks = []
    for case in summary['cases']:
        if case['case'] not in case_names:
            continue
        returned = [e['accepted'] for e in case['events'] if e.get('state') == 'exploration'][-1]
        voices = [v for path, v in case['voices'].items() if '/' + playlist + '/' in path]
        audible = [v for v in voices if abs(v['peak_db'] - expected_peak) < .5]
        passed = bool(audible) and all(v['last'] > returned + 2 and v['ended_before_capture_stop'] for v in audible)
        checks.append({'mode': case['mode'], 'case': case['case'], 'passed': passed,
                       'return_time': returned, 'audible_native_outro_voices': audible})
    expected = {(mode, case) for mode in ('native-reference', 'manifest')
                for case in case_names}
    if len(checks) != len(expected) or {(c['mode'], c['case']) for c in checks} != expected or not all(c['passed'] for c in checks):
        raise ValueError('Missing/attenuated/truncated combat outro evidence')
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folders', nargs='+', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = build_path(args.output)
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps([summarize(build_path(f)) for f in args.folders], indent=2) + '\n', encoding='utf-8')
