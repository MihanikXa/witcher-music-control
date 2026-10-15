"""Manifest-driven local State/Voice Volume authoring and strict source gates.

No bank generation, binary editing, licence access, installation or game launch.
Source validation restores ONLY declared edits; all other semantics stay exact.
"""
import argparse
import copy
import json
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

from music_region_inventory import entries
from white_orchard_prepare import build_path, digest
from white_orchard_state_volume_author import semantic
from white_orchard_transition_author import volume
from white_orchard_wwise import Waapi

MUSIC = Path('Interactive Music Hierarchy/music.wwu')
PRESERVED_STATES = {'combat', 'combat_monster_hunt', 'focus_combat',
                    'underwater_combat', 'underwater_combat_focus', 'gwent', 'minigames'}
CLASSES = {'generic', 'silent', 'protected', 'mixed', 'unresolved'}
MUTED = {'exploration', 'exploration_night', 'focus_exploration',
         'focus_exploration_night', 'underwater', 'underwater_focus',
         'boat', 'dialog_scene', 'dialog_scene_night'}


def graph(tree):
    # Reference IDs identify their target, not a second object. In particular
    # TransitionObjectRef must never overwrite the real segment in this map.
    objects = {n.get('ID'): n for n in tree.iter() if n.get('ID') and not n.tag.endswith('Ref')}
    parents = {c: p for p in tree.iter() for c in p}
    consumers = {}
    for selector in tree.iter('MusicSwitchContainer'):
        for entry in entries(selector):
            if entry['target']:
                ident = entry['target']['ID']
                if ident not in objects:
                    raise ValueError('Unresolved AudioNode')
                consumers.setdefault(ident, []).append((selector.get('ID'), tuple(p['Name'] for p in entry['path'])))
    return objects, parents, consumers


def ancestors(node, parents):
    yield node
    while node in parents:
        node = parents[node]
        yield node


def state_values(spec, states):
    muted = spec['muted_states']
    if len(states) != 25 or len(set(muted)) != len(muted) or set(muted) - set(states):
        raise ValueError('Unexpected State policy')
    if set(muted) & PRESERVED_STATES:
        raise ValueError('Combat/Gwent attenuation forbidden')
    if set(muted) != MUTED:
        raise ValueError('Fixed nine-State policy required')
    return {name: -200.0 if name in muted else 0.0 for name in states}


def plan(original, spec, states):
    if spec['schema'] != 1 or spec['wwise_build'] != 8928:
        raise ValueError('Unsupported manifest/version')
    if spec['purpose'] not in ('retained-D-regression', 'exception-fixture', 'scoped-pilot'):
        raise ValueError('Unreviewed manifest purpose')
    objects, parents, consumers = graph(original)
    for key in ('root', 'world', 'quest'):
        identity = spec['facts'][key]
        node = objects[identity['id']]
        if node.get('Name') != identity['name'] or node.get('ShortID') != str(identity['short_id']):
            raise ValueError('Identity mismatch: ' + key)
    world = objects[spec['facts']['world']['id']]
    root = objects[spec['facts']['root']['id']]
    quest = objects[spec['facts']['quest']['id']]
    if root not in ancestors(world, parents) or root not in ancestors(quest, parents):
        raise ValueError('Unexpected regional ancestry')
    values = state_values(spec, states)
    scopes, static = spec['state_scopes'], spec['static_targets']
    if set(spec.get('static_consumer_paths', {})) - set(static):
        raise ValueError('Consumer pins declared for nonstatic target')
    if len(set(scopes)) != len(scopes) or len(set(static)) != len(static):
        raise ValueError('Duplicate edit target')
    replay = spec['purpose'] == 'retained-D-regression'
    if replay and (spec['region'] != 'music_prologue' or scopes != [world.get('ID')]
                   or set(static) != set(spec['regression_static_ids'])):
        raise ValueError('Invalid bounded legacy replay')
    for ident in scopes:
        node = objects[ident]
        chain = list(ancestors(node, parents))
        if world not in chain or quest in chain or node.find('StateInfo') is not None:
            raise ValueError('Invalid/nonpristine State scope')
        if any(n.get('ID') in scopes for n in chain[1:]):
            raise ValueError('Overlapping State gains')
    decisions = spec['decisions']
    # Switch entries do not enumerate all consumers. Native transition rules
    # may directly play a segment inside a playlist after game_state changes.
    # Require separate approval for attenuation of such physical ancestry.
    if not replay:
        for ref in original.iter('TransitionObjectRef'):
            target = objects.get(ref.get('ID'))
            if target is None:
                raise ValueError('Unresolved native transition target')
            chain = list(ancestors(target, parents))
            if not {n.get('ID') for n in chain} & (set(scopes) | set(static)):
                continue
            playlist = next((n for n in chain if n.tag == 'MusicPlaylistContainer'), None)
            decision = decisions.get(playlist.get('ID') if playlist is not None else '', {})
            if (decision.get('transition_attenuation_approved') is not True
                    or not decision.get('transition_evidence') or decision.get('policy') != 'approved'
                    or decision.get('classification') != 'generic'):
                raise ValueError('Unreviewed native transition attenuation: ' + ref.get('ID'))
    # Require a declaration for every noncombat choice, not every node name.
    required = {ident for ident, use in consumers.items() if any(
        set(path) & set(spec['muted_states']) and world in ancestors(objects[ident], parents)
        for _, path in use)}
    if required - set(decisions):
        raise ValueError('Undeclared noncombat paths')
    for ident, decision in decisions.items():
        if decision['classification'] not in CLASSES or not decision['evidence']:
            raise ValueError('Unreviewed decision')
        node = objects[ident]
        if node.get('Name') != decision['name'] or node.get('ShortID') != str(decision['short_id']):
            raise ValueError('Decision identity mismatch')
        chain_ids = {n.get('ID') for n in ancestors(node, parents)}
        if 'parent_id' in decision or 'parent_short_id' in decision:
            physical = next(n for n in list(ancestors(node, parents))[1:] if n.get('ShortID'))
            if (decision.get('parent_id') != physical.get('ID')
                    or str(decision.get('parent_short_id')) != physical.get('ShortID')):
                raise ValueError('Reviewed physical parent mismatch')
        attenuated = bool(chain_ids & set(scopes)) or bool(chain_ids & set(static))
        classification = decision['classification']
        if classification in ('generic', 'silent') and attenuated and decision['policy'] != 'approved':
            raise ValueError('Pending policy would receive attenuation')
        if not replay and classification in ('protected', 'unresolved', 'mixed') and attenuated:
            raise ValueError('Protected/unreviewed/mixed ancestry attenuated: ' + node.get('Name'))
        if classification == 'generic' and not attenuated:
            raise ValueError('Generic coverage gap: ' + node.get('Name'))
        if ident in static:
            used = {state for _, path in consumers.get(ident, []) for state in path}
            if classification != 'generic' or decision['policy'] != 'approved' or used & PRESERVED_STATES:
                raise ValueError('Destructive static edit or mixed-use target')
            if volume(node) != decision['original_volume']:
                raise ValueError('Original static property mismatch')
            if any(world not in ancestors(objects[selector], parents)
                   for selector, _ in consumers.get(ident, [])):
                raise ValueError('Static target consumed outside world')
            pinned = spec.get('static_consumer_paths', {}).get(ident)
            if pinned is not None:
                actual = sorted((selector, objects[selector].get('ShortID'), path)
                                for selector, path in consumers.get(ident, []))
                expected = sorted((row['selector_id'], str(row['selector_short_id']), tuple(row['states']))
                                  for row in pinned)
                if not expected or actual != expected:
                    raise ValueError('Static consumer closure differs from reviewed paths')
            elif not replay and any(not any(n.get('ID') in scopes for n in ancestors(objects[selector], parents))
                                    for selector, _ in consumers.get(ident, [])):
                raise ValueError('Static target consumed outside reviewed scopes')
    if set(static) - set(decisions):
        raise ValueError('Undeclared static target')
    return values


def canonical_state(info):
    """Normalize only freshly allocated LOCAL CustomState GUIDs/ShortIDs."""
    info = copy.deepcopy(info)
    for row in info.findall('./CustomStateList/CustomState'):
        local = row.find('CustomState')
        local.set('ID', '{LOCAL}')
        local.set('ShortID', 'LOCAL')
    rows = info.find('CustomStateList')
    rows[:] = sorted(rows, key=lambda n: n.find('StateRef').get('ID'))
    return semantic(info)


def expected_state(template, values, states, group):
    node = copy.deepcopy(template)
    if node is None:
        raise ValueError('Measured State template required')
    if [p.get('Name') for p in node.findall('./StatePropertyList/Property')] != ['Volume']:
        raise ValueError('Unexpected State properties')
    refs = node.findall('./StateGroupList/StateGroupInfo/StateGroupRef')
    if len(refs) != 1 or refs[0].get('ID') != group:
        raise ValueError('Unexpected State group')
    seen = set()
    for row in node.findall('./CustomStateList/CustomState'):
        ref, local = row.find('StateRef'), row.find('CustomState')
        name = ref.get('Name')
        if name in seen or states.get(name) != ref.get('ID'):
            raise ValueError('Duplicate/wrong State reference')
        seen.add(name)
        props = local.find('PropertyList')
        if props is not None:
            local.remove(props)
        if values[name] != 0:
            props = ET.SubElement(local, 'PropertyList')
            ET.SubElement(props, 'Property', Name='Volume', Type='Real64', Value=str(int(values[name])))
    if seen != set(states):
        raise ValueError('Incomplete State table')
    return node


def validate_source(original, candidate, spec, states, template):
    values = plan(original, spec, states)
    objects, _, _ = graph(candidate)
    before, _, _ = graph(original)
    restored = copy.deepcopy(candidate)
    restore_objects, _, _ = graph(restored)
    expected = canonical_state(expected_state(template, values, states, spec['game_state_group']))
    local_ids, local_short_ids = set(), set()
    original_short_ids = {n.get('ShortID') for n in original.iter() if n.get('ShortID')}
    for ident in spec['state_scopes']:
        info = objects[ident].find('StateInfo')
        if info is None or canonical_state(info) != expected:
            raise ValueError('Unexpected State serialization: ' + ident)
        for row in info.findall('./CustomStateList/CustomState'):
            local = row.find('CustomState')
            local_id, short_id = local.get('ID'), local.get('ShortID')
            if local_id in local_ids or local_id in before or local_id in states.values() or short_id in local_short_ids or short_id in original_short_ids:
                raise ValueError('Local State identity collision')
            local_ids.add(local_id); local_short_ids.add(short_id)
        restore_objects[ident].remove(restore_objects[ident].find('StateInfo'))
    for ident in spec['static_targets']:
        if volume(objects[ident]) != -200:
            raise ValueError('Static volume mismatch')
        props = restore_objects[ident].find('PropertyList')
        props.remove(props.find("Property[@Name='Volume']"))
        old = before[ident].find("./PropertyList/Property[@Name='Volume']")
        if old is not None:
            props.append(copy.deepcopy(old))
        elif len(props) == 0 and before[ident].find('PropertyList') is None:
            restore_objects[ident].remove(props)
    if semantic(restored) != semantic(original):
        raise ValueError('Unexpected routing/transition/source/global/State change')
    return {'passed': True, 'state_scopes': len(spec['state_scopes']),
            'static_targets': len(spec['static_targets']), 'states': len(values),
            'attenuation_mechanism': 'static-only' if not spec['state_scopes'] else 'State-and-static',
            'all_other_music_semantics_exact': True,
            'pending_decisions': sum(d['classification'] in ('mixed', 'unresolved') for d in spec['decisions'].values()),
            'shipping_policy_complete': all(d['classification'] not in ('mixed', 'unresolved') for d in spec['decisions'].values())}


def context(source, spec):
    path = source / MUSIC
    if digest(path) != spec['facts']['original_music_sha256']:
        raise ValueError('Source fingerprint mismatch')
    for relative, expected in spec['facts'].get('input_hashes', {}).items():
        if digest(source / relative) != expected:
            raise ValueError('Pinned reference/global input changed: ' + relative)
    states_tree = ET.parse(source / 'States/global_states.wwu')
    group = next(n for n in states_tree.iter('StateGroup') if n.get('ID') == spec['game_state_group'])
    states = {n.get('Name'): n.get('ID') for n in group.findall('./ChildrenList/State')}
    return ET.parse(path).getroot(), states


def validate_events(original, events, spec):
    objects, parents, _ = graph(original)
    static = set(spec['static_targets'])
    for ref in events.iter('ObjectRef'):
        node = objects.get(ref.get('ID'))
        if node is not None and {n.get('ID') for n in ancestors(node, parents)} & static:
            raise ValueError('Direct event targets a permanent attenuation candidate or descendant')


def validate_event_directory(original, source, spec):
    """All event work units, including references outside the regional bank folder."""
    objects, parents, _ = graph(original)
    static = set(spec['static_targets'])
    forbidden = {ident for ident,node in objects.items()
                 if {n.get('ID') for n in ancestors(node, parents)} & static}
    files = sorted((source / 'Events').rglob('*.wwu'))
    if not files:
        raise ValueError('Missing complete event source')
    for path in files:
        if any(ref.get('ID') in forbidden for ref in ET.parse(path).iter('ObjectRef')):
            raise ValueError('Direct event targets a permanent attenuation candidate or descendant: '
                             + path.relative_to(source).as_posix())
    return len(files)


def author(source, project, manifest, template_path, port):
    project = build_path(project)
    spec = json.loads(manifest.read_text(encoding='utf-8'))
    original, states = context(source, spec)
    values = plan(original, spec, states)
    validate_events(original, ET.parse(source / 'Events/music.wwu'), spec)
    event_count = validate_event_directory(original, source, spec)
    workspace = project.parent
    report = workspace / 'regional-source-audit.json'
    if report.exists():
        raise FileExistsError(report)
    units = {p.relative_to(workspace).as_posix(): digest(p) for p in workspace.rglob('*.wwu')}
    original_units = {p.relative_to(source).as_posix(): digest(p) for p in source.rglob('*.wwu')}
    if len(units) != 1508 or units != original_units:
        raise ValueError('Fresh complete pristine context required')
    api = Waapi(port)
    if Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve() != project.resolve() or api.call('ak.wwise.core.getInfo')['version']['build'] != 8928:
        raise ValueError('Wrong project/version')
    for ident in spec['state_scopes']:
        api.call('ak.wwise.core.object.setStateProperties', {'object': ident, 'stateProperties': ['Volume']})
        api.call('ak.wwise.core.object.setStateGroups', {'object': ident, 'stateGroups': [spec['game_state_group']]})
    api.call('ak.wwise.core.project.save')
    current = ET.parse(workspace / MUSIC).getroot()
    objects, _, _ = graph(current)
    for ident in spec['state_scopes']:
        for row in objects[ident].findall('./StateInfo/CustomStateList/CustomState'):
            api.call('ak.wwise.core.object.setProperty', {'object': row.find('CustomState').get('ID'),
                'property': 'Volume', 'value': values[row.find('StateRef').get('Name')]})
    for ident in spec['static_targets']:
        api.call('ak.wwise.core.object.setProperty', {'object': ident, 'property': 'Volume', 'value': -200})
    api.call('ak.wwise.core.project.save')
    template_tree = ET.parse(template_path)
    if digest(template_path) != spec['facts']['template_source_sha256']:
        raise ValueError('Measured template source changed')
    template = next(n for n in template_tree.iter('MusicSwitchContainer') if n.get('ShortID') == '1033516231').find('StateInfo')
    result = validate_source(original, ET.parse(workspace / MUSIC).getroot(), spec, states, template)
    after = {p.relative_to(workspace).as_posix(): digest(p) for p in workspace.rglob('*.wwu')}
    if set(after) != set(units) or any(after[p] != units[p] for p in units if p != MUSIC.as_posix()):
        raise ValueError('Unrelated work unit changed')
    result.update(manifest_sha256=digest(manifest), music_sha256=digest(workspace / MUSIC),
                  complete_work_units=1508, event_work_units_reviewed=event_count,
                  banks_generated=False, deployed=False)
    # Keep pristine authored source before any separate profiler/Recorder fixture
    # changes. This snapshot contains no project/licence material.
    shutil.copyfile(workspace / MUSIC, workspace / 'regional-authored-music.xml')
    report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--port', type=int, default=18093)
    args = parser.parse_args()
    author(args.source, args.project, args.manifest, args.template, args.port)
