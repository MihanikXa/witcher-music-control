"""Read-only Stage 1 v150 comparison; not a bank writer or runtime certificate.

The narrow inline-State layout is cross-checked against Wwise source XML,
generated metadata and the parser author's primary code (report 15). Fail
closed outside the measured world object/layout. Never edit BKHD/HIRC bytes.
"""
import argparse
import json
from pathlib import Path
import struct
import uuid
import xml.etree.ElementTree as ET

from white_orchard_compare import read_bank, difference
from white_orchard_prepare import build_path, digest
from white_orchard_state_volume_author import semantic

WORLD = 1033516231


class Reader:
    def __init__(self, data, offset=0):
        self.data, self.offset = data, offset

    def read(self, fmt):
        value = struct.unpack_from('<' + fmt, self.data, self.offset)
        self.offset += struct.calcsize('<' + fmt)
        return value[0] if len(value) == 1 else value

    def var(self):
        value = 0
        for _ in range(5):
            byte = self.read('B')
            value = (value << 7) | (byte & 127)
            if not byte & 128:
                return value
        raise ValueError('Invalid variable integer')


def state_chunk(body):
    # The complete untouched object/prefix/suffix are verified below. This
    # measured offset must not be generalized to other HIRC objects.
    r = Reader(body, 28)
    props = [dict(zip(('property_id', 'accumulation', 'in_db'),
                     (r.var(), r.read('B'), r.read('B')))) for _ in range(r.var())]
    groups = []
    for _ in range(r.var()):
        group = {'group_id': r.read('I'), 'sync': r.read('B'), 'states': []}
        for _ in range(r.var()):
            state = {'state_id': r.read('I')}
            count = r.read('H')
            ids = [r.read('H') for _ in range(count)]
            if len(set(ids)) != len(ids):
                raise ValueError('Duplicate inline State property ID')
            state['properties'] = dict(zip(ids, (r.read('f') for _ in range(count))))
            group['states'].append(state)
        groups.append(group)
    return {'offset': 28, 'end': r.offset, 'properties': props, 'groups': groups}


def native_groups(payload):
    """Read just the v150 STMG header and complete StateGroup section."""
    r = Reader(payload)
    header = {'filter_behavior': r.read('H'), 'volume_threshold': r.read('f'),
              'max_voices': r.read('H'), 'max_virtual_voices': r.read('H')}
    groups = []
    for _ in range(r.read('I')):
        group = {'id': r.read('I'), 'default_transition_ms': r.read('I')}
        group['transitions'] = [dict(zip(('from', 'to', 'time_ms'), r.read('III')))
                                for _ in range(r.read('I'))]
        groups.append(group)
    return {'header': header, 'groups': groups, 'state_section_end': r.offset}


def header(bank, metadata=None):
    b = bank['payload']['BKHD']
    if len(b) < 40:
        raise ValueError('Truncated v150 bank header')
    words = struct.unpack_from('<6I', b)
    if words[0] != 150:
        raise ValueError('Only the observed v150 layout is supported')
    result = dict(zip(('version', 'bank_id', 'language_id', 'alignment_flags',
                       'project_id', 'bank_type'), words))
    result.update(hash_hex=b[24:40].hex(), padding_hex=b[40:].hex())
    if metadata:
        node = next(x for x in ET.parse(metadata).iter('SoundBank')
                    if int(x.get('Id')) == words[1])
        result['metadata_hash'] = node.get('Hash')
        result['hash_matches_metadata_guid'] = uuid.UUID(node.get('Hash')).bytes_le == b[24:40]
    return result


def audit(native, baseline, candidate, baseline_project, candidate_project, output):
    output = build_path(output)
    a, b, c = [read_bank(p / 'music_prologue.bnk') for p in (native, baseline, candidate)]
    ia, ib, ic = [read_bank(p / 'Init.bnk') for p in (native, baseline, candidate)]
    report = {'regional': {name: {'bytes': bank['bytes'], 'sha256': bank['sha256'],
                                'header': header(bank, folder / 'SoundbanksInfo.xml' if name != 'native' else None)}
                            for name, bank, folder in (('native', a, native), ('baseline', b, baseline), ('candidate', c, candidate))},
              'baseline_vs_native': difference(a, b), 'candidate_vs_baseline': difference(b, c),
              'disposable_init_vs_native': difference(ia, ib),
              'candidate_vs_baseline_init': difference(ib, ic)}
    checks = {}
    checks['baseline_hirc_native_exact'] = a['payload']['HIRC'] == b['payload']['HIRC']
    checks['only_world_hirc_changed'] = report['candidate_vs_baseline']['added'] == [] and report['candidate_vs_baseline']['removed'] == [] and [x['id'] for x in report['candidate_vs_baseline']['changed']] == [WORLD]
    checks['embedded_media_native_exact'] = all(a['payload'][tag] == b['payload'][tag] == c['payload'][tag] for tag in ('DIDX', 'DATA'))
    checks['disposable_init_pair_exact'] = ib['sha256'] == ic['sha256']
    before, after = b['records'][WORLD], c['records'][WORLD]
    checks['world_type_preserved'] = before[0] == after[0] == 12
    old, new = state_chunk(before[1]), state_chunk(after[1])
    report['inline_state_chunk'] = new
    checks['empty_baseline_state_chunk'] = old['properties'] == [] and old['groups'] == []
    checks['world_prefix_and_suffix_exact'] = before[1][:28] == after[1][:28] and before[1][old['end']:] == after[1][new['end']:]
    checks['only_additive_db_volume'] = new['properties'] == [{'property_id': 0, 'accumulation': 2, 'in_db': 1}]
    checks['one_immediate_group'] = len(new['groups']) == 1 and new['groups'][0]['sync'] == 0
    metadata = ET.parse(candidate / 'SoundbanksInfo.xml')
    group = next(x for x in metadata.iter('StateGroup') if x.get('Name') == 'game_state')
    names = {int(x.get('Id')): x.get('Name') for x in group.findall('./States/State')}
    source_audit = json.loads((candidate_project / 'state-volume-clean-authoring.json').read_text())
    expected = {name for name, v in source_audit['state_table'].items() if v['saved_voice_volume_db'] != 0}
    serialized = new['groups'][0]
    for state in serialized['states']:
        state['name'] = names[state['state_id']]
    checks['exact_nine_attenuated_states'] = len(serialized['states']) == len(expected) == 9 and {x['name'] for x in serialized['states']} == expected and all(x['properties'] == {0: -200.0} for x in serialized['states'])
    checks['existing_metadata_group_id'] = serialized['group_id'] == int(group.get('Id'))
    stmg = native_groups(ia['payload']['STMG'])
    native_group = next(x for x in stmg['groups'] if x['id'] == serialized['group_id'])
    report['native_game_state_group'] = native_group
    # State IDs are named game-sync values, not local HIRC object IDs. STMG
    # declares groups and transition overrides, not an exhaustive State enum.
    transition_ids = {t[k] for t in native_group['transitions'] for k in ('from', 'to')}
    report['states_without_native_custom_transition'] = [x['name'] for x in serialized['states'] if x['state_id'] not in transition_ids]
    checks['native_group_exists'] = native_group['id'] == serialized['group_id']
    checks['native_state_source_unchanged'] = (baseline_project / 'States/global_states.wwu').read_bytes() == (candidate_project / 'States/global_states.wwu').read_bytes()
    units_a = {p.relative_to(baseline_project).as_posix(): p for p in baseline_project.rglob('*.wwu')}
    units_b = {p.relative_to(candidate_project).as_posix(): p for p in candidate_project.rglob('*.wwu')}
    checks['all_1508_units_retained'] = units_a.keys() == units_b.keys() and len(units_a) == 1508
    different = [rel for rel in units_a if digest(units_a[rel]) != digest(units_b[rel])]
    checks['only_music_work_unit_differs'] = different == ['Interactive Music Hierarchy/music.wwu']
    trees = [ET.parse(p / 'Interactive Music Hierarchy/music.wwu') for p in (baseline_project, candidate_project)]
    world = next(x for x in trees[1].iter('MusicSwitchContainer') if x.get('ShortID') == str(WORLD))
    world.remove(world.find('StateInfo'))
    checks['source_semantics_only_world_stateinfo'] = semantic(trees[0].getroot()) == semantic(trees[1].getroot())
    # IDs/bodies for every non-world record are exact, which includes all
    # events/actions, quest routing, sources and streaming flags/references.
    checks['all_nonworld_records_native_exact'] = all(a['records'][i] == c['records'][i] for i in a['records'] if i != WORLD)
    converted = []
    for project in (baseline_project, candidate_project):
        converted.append({p.relative_to(project / '.cache').as_posix(): digest(p)
                          for p in (project / '.cache').rglob('*.wem')})
    checks['converted_media_pair_exact'] = bool(converted[0]) and converted[0] == converted[1]
    report['converted_media_files'] = len(converted[0])
    checks['metadata_hashes_crosschecked'] = all(report['regional'][name]['header']['hash_matches_metadata_guid'] for name in ('baseline', 'candidate'))
    report.update(checks=checks, changed_work_units=different,
                  serialized_new_hirc_ids=[], local_custom_state_ids_serialized=False,
                  deployable=False, reason='Structural audit only; generation, global fidelity and runtime acceptance require separate gates.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'checks': checks, 'deployable': False, 'reason': report['reason']}))
    if not all(checks.values()):
        raise RuntimeError('One or more structure checks failed; see evidence')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('native', 'baseline', 'candidate', 'baseline-project', 'candidate-project', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args()
    audit(args.native, args.baseline, args.candidate, args.baseline_project, args.candidate_project, args.output)
