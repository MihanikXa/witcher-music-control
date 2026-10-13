"""Read-only regional Wwise selector inventory; never infer intent from names.

Reads only the four named WWUs. Writes fresh evidence under ignored build/.
No authoring, licence access, bank generation, deployment or save access.
"""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path, digest
from white_orchard_compare import read_bank

REGIONS = ('music_prologue', 'music_nomansgrad', 'music_skellige',
           'music_kaer_morhen', 'music_toussaint', 'music_wyzima_castle',
           'music_misty_island', 'music_spiral')
NONCOMBAT = {'exploration', 'exploration_night', 'dialog_scene',
             'dialog_scene_night', 'focus_exploration',
             'focus_exploration_night', 'boat', 'underwater', 'underwater_focus'}


def entries(node):
    """Only this selector's entries, never nested children's mappings."""
    rows = []
    for entry in node.findall('./ObjectLists/ObjectList[@Name="Entries"]/Reference/Local/MultiSwitchEntry'):
        target = entry.find('./ReferenceList/Reference[@Name="AudioNode"]/ObjectRef')
        rows.append({'path': [dict(x.attrib) for x in entry.findall(
            './ObjectLists/ObjectList[@Name="EntryPath"]/Reference/ObjectRef')],
                     'target': dict(target.attrib) if target is not None else None})
    return rows


def properties(node):
    return {p.get('Name'): p.get('Value', p.findtext('./ValueList/Value'))
            for p in node.findall('./PropertyList/Property')}


def inventory(music, events, banks, lines=None):
    objects = {n.get('ID'): n for n in music.iter()
               if n.get('ID') and n.tag != 'ObjectRef'}
    consumers = {}
    for selector in music.iter('MusicSwitchContainer'):
        for entry in entries(selector):
            if entry['target'] is None:
                continue  # Native explicit empty choice; never resolve by name.
            target = entry['target']['ID']
            if target not in objects:
                raise ValueError('Unresolved AudioNode: ' + target)
            consumers.setdefault(target, []).append({
                'selector_id': selector.get('ID'), 'selector': selector.get('Name'),
                'path': [x.get('Name') for x in entry['path']]})
    event_rows = []
    for event in events.iter('Event'):
        actions = []
        for action in event.findall('./ChildrenList/Action'):
            actions.append({'properties': properties(action), 'targets': [dict(x.attrib)
                for x in action.findall('./ReferenceList/Reference/ObjectRef')]})
        event_rows.append({'id': event.get('ID'), 'name': event.get('Name'), 'actions': actions})

    def meta(node):
        return {'name': node.get('Name'), 'id': node.get('ID'),
                'short_id': node.get('ShortID'), 'line': (lines or {}).get(node.get('ID'))}

    regions = []
    for name in REGIONS:
        matches = [n for n in music.iter('MusicSwitchContainer') if n.get('Name') == name]
        if len(matches) != 1:
            raise ValueError('Missing/duplicate regional root: ' + name)
        root = matches[0]
        children = root.findall('./ChildrenList/*')
        worlds = [n for n in children if n.get('Name') == 'world_music']
        quests = [n for n in children if n.get('Name') in ('quests_and_cutscenes', 'quests_cutscenes')]
        if len(worlds) != 1 or len(quests) != 1:
            raise ValueError('Unexpected regional branch structure: ' + name)
        world, quest = worlds[0], quests[0]
        selectors = []
        world_ids = {n.get('ID') for n in world.iter()}
        quest_files = {a.text for a in quest.iter('AudioFile')}
        for selector in world.findall('./ChildrenList/MusicSwitchContainer'):
            mappings = entries(selector)
            locations = [e for e in entries(world) if e['target'] and e['target']['ID'] == selector.get('ID')]
            switch_ids = {p['ID'] for e in locations for p in e['path']}
            selecting_events = [e for e in event_rows if any(
                t['ID'] in switch_ids for a in e['actions'] for t in a['targets'])]
            routes = []
            for mapping in mappings:
                if mapping['target'] is None:
                    routes.append({'states': [x.get('Name') for x in mapping['path']],
                                   'target': None, 'audio_files': [], 'properties': {}})
                    continue
                node = objects[mapping['target']['ID']]
                routes.append({'states': [x.get('Name') for x in mapping['path']],
                    'target': meta(node), 'audio_files': sorted({a.text for a in node.iter('AudioFile')}),
                    'properties': properties(node)})
            selectors.append({**meta(selector), 'locations': locations,
                'arguments': [dict(x.attrib) for x in selector.findall(
                    './ObjectLists/ObjectList[@Name="Arguments"]/Reference/ObjectRef')],
                'events': selecting_events, 'routes': routes})
        playlists = []
        for node in world.iter('MusicPlaylistContainer'):
            ident = node.get('ID')
            usage = consumers.get(ident, [])
            outside = [u for u in usage if u['selector_id'] not in world_ids]
            direct = [e['name'] for e in event_rows if any(t['ID'] == ident
                for a in e['actions'] for t in a['targets'])]
            files = {a.text for a in node.iter('AudioFile')}
            playlists.append({**meta(node), 'properties': properties(node), 'consumers': usage,
                'outside_world_consumers': outside, 'direct_events': direct,
                'audio_files': sorted(files), 'quest_branch_shared_files': sorted(files & quest_files)})
        bank = [b for b in banks.iter('SoundBank') if b.get('Name') == name]
        if len(bank) != 1:
            raise ValueError('Missing/duplicate regional bank: ' + name)
        transitions = []
        for node in world.iter('MusicTransition'):
            transitions.append({**meta(node), 'properties': properties(node),
                'fades': [properties(n) for n in node.iter('MusicFade')]})
        regions.append({**meta(root), 'world': meta(world), 'quest': meta(quest),
            'root_arguments': [dict(x.attrib) for x in root.findall('./ObjectLists/ObjectList[@Name="Arguments"]/Reference/ObjectRef')],
            'root_entries': entries(root), 'world_arguments': [dict(x.attrib) for x in world.findall('./ObjectLists/ObjectList[@Name="Arguments"]/Reference/ObjectRef')],
            'world_entries': entries(world), 'world_state_info_present': world.find('StateInfo') is not None,
            'selectors': selectors, 'playlists': playlists, 'transitions': transitions,
            'world_rtpc_count': len(list(world.iter('RTPC'))),
            'bank_inclusions': [dict(x.attrib) for x in bank[0].findall('./ObjectInclusionList/ObjectRef')],
            'quest_playlists': [{**meta(n), 'audio_files': sorted({a.text for a in n.iter('AudioFile')})}
                                for n in quest.iter('MusicPlaylistContainer')]})
    return {'regions': regions, 'events': event_rows,
            'soundbanks': [{'name': b.get('Name'), 'inclusions': [dict(x.attrib)
                for x in b.findall('./ObjectInclusionList/ObjectRef')]} for b in banks.iter('SoundBank')],
            'policy_classification': 'none; human-reviewed decisions required'}


def native_banks(result, directory):
    """Record membership, not inferred runtime ownership or inclusion repairs."""
    paths = {name: directory / (name + '.bnk') for name in (*REGIONS, 'music_shared')}
    before = {name: digest(path) for name, path in paths.items()}
    banks = {name: read_bank(path) for name, path in paths.items()}
    for region in result['regions']:
        name = region['name']
        ids = {int(p['short_id']) for p in region['playlists']}
        bank = banks[name]
        region['native_bank'] = {'sha256': before[name], 'bytes': bank['bytes'],
            'hirc_count': len(bank['records']),
            'world_playlists_absent': [p for p in region['playlists']
                                      if int(p['short_id']) not in bank['records']],
            'world_playlist_ids_present_elsewhere': {other: sorted(ids & set(b['records']))
                for other, b in banks.items() if other != name and ids & set(b['records'])}}
    if before != {name: digest(path) for name, path in paths.items()}:
        raise RuntimeError('Native banks changed during inventory')
    result['native_bank_hashes'] = before


def run(source, output, bank_directory=None):
    output = build_path(output)
    if output.exists():
        raise FileExistsError('Preserve previous evidence; use a fresh output')
    paths = [source / p for p in ('Interactive Music Hierarchy/music.wwu',
             'Events/music.wwu', 'SoundBanks/music.wwu', 'States/global_states.wwu')]
    before = [digest(p) for p in paths]
    text = paths[0].read_text(encoding='utf-8-sig')
    lines = {}
    for i, line in enumerate(text.splitlines(), 1):
        if '<ObjectRef ' not in line:
            match = re.search(r' ID="([^"]+)"', line)
            if match:
                lines[match[1]] = i
    result = inventory(*[ET.parse(p).getroot() for p in paths[:3]], lines)
    result['states'] = [dict(n.attrib) for n in ET.parse(paths[3]).iter('State')]
    result['input_hashes'] = {p.relative_to(source).as_posix(): h for p, h in zip(paths, before)}
    if bank_directory:
        native_banks(result, bank_directory)
    if before != [digest(p) for p in paths]:
        raise RuntimeError('Inputs changed during inventory')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-banks', type=Path)
    args = parser.parse_args()
    result = run(args.source, args.output, args.native_banks)
    print(json.dumps({r['name']: {'selectors': len(r['selectors']),
          'playlists': len(r['playlists']), 'transitions': len(r['transitions'])}
          for r in result['regions']}))
