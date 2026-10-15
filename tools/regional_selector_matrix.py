"""Data-driven paired native-selector captures in isolated validation projects."""
import argparse
import json
from pathlib import Path
from white_orchard_prepare import build_path, digest
from white_orchard_transition_probe import run
from white_orchard_transition_measure import measure
from regional_playback_review import summarize


def validate_groups(groups):
    names = set()
    if not groups:
        raise ValueError('Empty playback matrix')
    for g in groups:
        if (set(g) - {'name', 'location_event', 'cases', 'duration', 'audition_object', 'prime_location', 'crossfade_event'}
                or not {'name', 'location_event', 'cases', 'duration'} <= set(g)
                or not isinstance(g['name'], str) or not g['name']
                or Path(g['name']).name != g['name'] or g['name'] in names
                or not isinstance(g['location_event'], str) or not g['location_event']
                or not isinstance(g['cases'], list) or not g['cases']
                or len(set(g['cases'])) != len(g['cases'])
                or not isinstance(g['duration'], (int, float)) or not 19 <= g['duration'] <= 90):
            raise ValueError('Invalid/duplicate playback group')
        if 'prime_location' in g and not isinstance(g['prime_location'],bool):
            raise ValueError('Explicit boolean location priming required')
        if 'crossfade_event' in g and (not isinstance(g['crossfade_event'],str) or not g['crossfade_event']):
            raise ValueError('Explicit crossfade location event required')
        names.add(g['name'])


def matrix(project, manifest, plan, port, label):
    project = build_path(project)
    if project.parent.name != 'validation' or Path(label).name != label:
        raise ValueError('Isolated validation project/simple label required')
    groups = json.loads(plan.read_text(encoding='utf-8'))
    validate_groups(groups)
    output = project.parent / (label + '-matrix.json')
    if output.exists() or any((project.parent / (label+'-'+g['name'])).exists() for g in groups):
        raise FileExistsError('Preserve previous captures; choose a fresh label')
    proof = {'manifest_sha256': digest(manifest), 'plan_sha256': digest(plan), 'groups': [],
             'fixtures_only': True, 'retail_validated': False}
    for g in groups:
        name = label+'-'+g['name']
        run(project, name, port, ['native-reference', 'manifest'], g['cases'],
            manifest=manifest, location_event=g['location_event'],
            explicit_threat_zero=True, minimum_duration=g['duration'], audition_object=g.get('audition_object'),
            prime_location=g.get('prime_location',False),crossfade_event=g.get('crossfade_event'))
        folder = project.parent / name
        measure(folder)
        proof['groups'].append({'name': name, 'summary': summarize(folder)})
        output.write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    return proof


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--port',type=int,required=True)
    p.add_argument('--label',required=True)
    a=p.parse_args();matrix(a.project,a.manifest,a.plan,a.port,a.label)
