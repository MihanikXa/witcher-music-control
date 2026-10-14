"""Read-only profiler evidence summary; source/bank/runtime gates stay separate."""
import argparse
import json
import statistics
from pathlib import Path
from white_orchard_prepare import build_path, digest


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


def outro_checks(summary, playlist, expected_peak):
    """Bounded NML/WO proof: audible return cue completes after E, before stop."""
    checks = []
    for case in summary['cases']:
        if case['case'] not in ('e-combat', 'e-combat-offset'):
            continue
        returned = [e['accepted'] for e in case['events'] if e.get('state') == 'exploration'][-1]
        voices = [v for path, v in case['voices'].items() if '/' + playlist + '/' in path]
        audible = [v for v in voices if abs(v['peak_db'] - expected_peak) < .5]
        passed = bool(audible) and all(v['last'] > returned + 2 and v['ended_before_capture_stop'] for v in audible)
        checks.append({'mode': case['mode'], 'case': case['case'], 'passed': passed,
                       'return_time': returned, 'audible_native_outro_voices': audible})
    expected = {(mode, case) for mode in ('native-reference', 'manifest')
                for case in ('e-combat', 'e-combat-offset')}
    if len(checks) != 4 or {(c['mode'], c['case']) for c in checks} != expected or not all(c['passed'] for c in checks):
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
