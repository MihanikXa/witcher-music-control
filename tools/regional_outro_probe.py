"""Bounded native-selector regression matrix; isolated fixtures only, no banks."""
import argparse
from pathlib import Path
from white_orchard_transition_probe import run
from white_orchard_transition_measure import measure


def matrix(project, manifest, port, label, white_orchard=False):
    modes = ['native-reference', 'manifest']
    locations = [('village', 'mus_loc_prologue_village')] if white_orchard else [
        ('zone02', 'mus_loc_nml_zone_02'), ('zone03', 'mus_loc_nml_zone_03')]
    for location, event in locations:
        batches = [
            ('outro', ['e-combat', 'e-combat-offset'], 35),
            ('contexts', ['e-dialogue', 'e-cutscene-dialogue', 'e-movie-dialogue',
                          'e-music-only-dialogue', 'combat-threat', 'night-combat'], 19),
        ]
        if white_orchard:
            batches.append(('authored', ['authored', 'q001-direct', 'gwent'], 19))
        for batch, cases, duration in batches:
            name = f'{label}-{location}-{batch}'
            run(project, name, port, modes, cases, manifest=manifest,
                location_event=event, explicit_threat_zero=True, minimum_duration=duration)
            measure(project.parent / name)
    if white_orchard:
        name = label + '-q505'
        run(project, name, port, ['D-reference', 'native-reference', 'manifest'],
            ['authored-world'], manifest=manifest,
            location_event='mus_loc_prologue_village_q505', explicit_threat_zero=True)
        measure(project.parent / name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--label', required=True)
    parser.add_argument('--white-orchard', action='store_true')
    args = parser.parse_args()
    matrix(args.project, args.manifest, args.port, args.label, args.white_orchard)
