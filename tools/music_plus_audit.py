"""Read-only local Music Plus comparison; outputs derived evidence under build/.

Never executes reference code, writes banks, installs or invokes Wwise.
Archive extraction is deliberately separate from this inspection command.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

from music_comparison_decode import music, track
from regional_baseline_reference import cache_index
from white_orchard_compare import read_bank, difference
from white_orchard_prepare import build_path
from regional_music_bank import Reader


def fnv(name):
    value = 2166136261
    for byte in name.lower().encode('utf-8'):
        value = ((value * 16777619) & 0xffffffff) ^ byte
    return value


def payloads(path):
    with path.open('rb') as stream:
        result = {}
        for name, (offset, size) in cache_index(stream).items():
            stream.seek(offset)
            data = stream.read(size)
            if len(data) != size:
                raise ValueError('Truncated cache payload')
            result[name] = dict(offset=offset, bytes=size,
                                sha256=hashlib.sha256(data).hexdigest())
        return result


def playback_closure(bank, root):
    """Conservative music playback closure; physical switch children aren't edges.

    Includes zero-weight alternatives and every transition segment, so absence
    here is stronger than absence under the current user settings. Does not
    prove dynamic event reachability, audibility, or runtime rule precedence.
    """
    pending, visited = [root], set()
    while pending:
        ident = pending.pop()
        if ident in visited or ident not in bank['records']:
            continue
        visited.add(ident)
        kind, body = bank['records'][ident]
        if kind not in (10, 12, 13):
            continue
        d = music(kind, body)
        if kind == 12:
            pending.extend(e['target'] for e in d['entries'])
        elif kind == 13:
            pending.extend(e['segment'] for e in d['playlist'])
        else:
            pending.extend(d['children'])
        pending.extend(t['transition']['id'] for t in d.get('rules', []) if t['transition'])
        pending.extend(s[1] for s in d['stingers'])
    return visited


def event_switch(bank, event):
    kind, body = bank['records'][fnv(event)]
    if kind != 4:
        raise ValueError('Not an Event')
    r = Reader(body)
    count = r.count('var', 4)
    if count != 1:
        raise ValueError('Expected one switch action')
    ident = r.read('I')
    if r.pos != len(body):
        raise ValueError('Unexplained Event tail')
    kind, body = bank['records'][ident]
    # Exact observed v150 SetSwitch(global), no property/range bundles.
    if kind != 3 or len(body) != 17 or body[:2] != b'\x01\x19' or body[6:9] != bytes(3):
        raise ValueError('Unsupported switch-action layout')
    group, value = struct.unpack_from('<II', body, 9)
    if struct.unpack_from('<I', body, 2)[0] != value:
        raise ValueError('Inconsistent action target')
    return group, value


def pause_profiles(bank, target):
    kind, body = bank['records'][target]
    if kind != 12:
        raise ValueError('Expected scheduler MusicSwitch')
    d = music(kind, body)
    group, variant = event_switch(bank, 'mod_music_next_v0')
    result = {}
    for chance in range(6):
        cg, cv = event_switch(bank, 'mod_music_pchance_' + str(chance))
        for length in range(4):
            lg, lv = event_switch(bank, 'mod_music_plen_' + str(length))
            if d['arguments'] != [(group, 0), (cg, 0), (lg, 0)]:
                raise ValueError('Unreviewed pause argument routing')
            entries = [e for e in d['entries'] if e['path'] == [variant, cv, lv]]
            if len(entries) != 1:
                raise ValueError('Missing/duplicate pause profile')
            ident = entries[0]['target']
            k, v = bank['records'][ident]
            info = music(k, v)
            segments = {}
            for item in info.get('playlist', []):
                if item['segment']:
                    sk, sv = bank['records'][item['segment']]
                    if sk != 10:
                        raise ValueError('Unsupported playlist leaf')
                    segment = music(sk, sv)
                    segments[str(item['segment'])] = dict(duration=segment['duration_ms'],
                        markers=segment['markers'], children=segment['children'])
            result[f'{chance}/{length}'] = dict(id=ident, kind=k, node=info, segments=segments)
    return result


def audit(main, banks, native, source, output):
    output = build_path(output)
    if output.exists():
        raise ValueError('Use a fresh output; preserve previous evidence')
    cache = payloads(main / 'mods/mod0000_MusicPlusPlaylists/content/soundspc.cache')
    if set(cache) != {p.name for p in banks.glob('*.bnk')} or any(
            Path(name).name != name or not name.endswith('.bnk') for name in cache):
        raise ValueError('Extracted bank set does not match cache')
    tree = ET.parse(source / 'Interactive Music Hierarchy/music.wwu')
    nodes = {int(n.get('ShortID')): n for n in tree.iter()
             if n.get('ShortID') and n.tag != 'ObjectRef'}
    parents = {c: p for p in tree.iter() for c in p}
    names = {i: n.get('Name') for i, n in nodes.items()}
    names.update({fnv(n): n for n in (
        'game_state', 'music_type', 'world', 'quests_cutscenes',
        'exploration', 'exploration_night', 'dialog_scene', 'dialog_scene_night',
        'combat', 'combat_monster_hunt', 'cutscene', 'movie', 'music_only',
        'threat_rating', 'intensity', 'mod_music_variant', 'mod_music_variant_combat',
        'mod_music_pause_chance', 'mod_music_pause_length', 'mod_music_pchance',
        'mod_music_plen', 'mod_music_cmute', 'mod_music_cas', 'mod_music_tp',
        *['mod_music_atten_' + k for k in ('exploration', 'combat', 'gwent', 'bards', 'tavern')],
        *['mod_music_boost_' + k for k in ('exploration', 'combat', 'gwent', 'bards', 'tavern')])})
    result = {'banks': {}, 'format': 'v150; complete bounded music-tail decode',
              'hash_names': {str(i): n for i, n in names.items() if n and n.startswith('mod_music')}}
    for path in sorted(banks.glob('*.bnk')):
        old, new = read_bank(native / path.name), read_bank(path)
        if new['sha256'] != cache[path.name]['sha256']:
            raise ValueError('Extracted bank payload mismatch')
        if struct.unpack_from('<I', new['payload']['BKHD'])[0] != 150:
            raise ValueError('Unsupported bank version')
        decoded, errors = {}, []
        track_curves, plugins, streams = Counter(), Counter(), set()
        track_count = 0
        for ident, (kind, body) in new['records'].items():
            if kind in (10, 12, 13):
                try:
                    decoded[ident] = music(kind, body)
                except ValueError as exc:
                    errors.append(dict(id=ident, type=kind, error=str(exc)))
            elif kind == 11:
                try:
                    info = track(body)
                    track_count += 1
                    track_curves.update(names.get(c['id'], str(c['id'])) for c in info['rtpc'])
                    plugins.update(str(s['plugin']) for s in info['sources'])
                    streams.update(s['id'] for s in info['sources'])
                except ValueError as exc:
                    errors.append(dict(id=ident, type=kind, error=str(exc)))
        diff = difference(old, new)
        row = dict(sha256=new['sha256'], bytes=new['bytes'],
                   bkhd_words=struct.unpack_from('<6I', new['payload']['BKHD']),
                   native_hirc=len(old['records']), hirc=len(new['records']),
                   type_counts=dict(Counter(t for t, _ in new['records'].values())),
                   differences=diff, decode_errors=errors,
                   decoded_types=dict(Counter(new['records'][i][0] for i in decoded)),
                   tracks_decoded=track_count, track_rtpc_counts=dict(track_curves),
                   track_plugins=dict(plugins), media_ids=sorted(streams),
                   embedded_chunks_exact={k: old['payload'].get(k) == new['payload'].get(k)
                                          for k in ('DIDX', 'DATA')})
        root = next((n for n in tree.iter('MusicSwitchContainer') if n.get('Name') == path.stem), None)
        if root is not None:
            quest = next(n for n in root.findall('./ChildrenList/*')
                         if n.get('Name') in ('quests_and_cutscenes', 'quests_cutscenes'))
            ids = {int(n.get('ShortID')) for n in quest.iter() if n.get('ShortID') and n.tag != 'ObjectRef'}
            present = ids & old['records'].keys()
            row['authored_subtree'] = dict(source_ids=len(ids), native_ids=len(present),
                absent_native=sorted(ids - old['records'].keys()),
                missing_modified=sorted(present - new['records'].keys()),
                changed=[dict(id=i, name=names.get(i)) for i in sorted(present & new['records'].keys())
                         if old['records'][i] != new['records'][i]])
            selected = {int(root.get('ShortID')), int(quest.get('ShortID'))}
            selected.update(i for i in decoded if i in nodes and new['records'][i] != old['records'].get(i)
                            and new['records'][i][0] in (12, 13))
            row['changed_native_music_nodes'] = {str(i): dict(name=names.get(i), **decoded[i])
                for i in sorted(selected) if i in decoded}
            row['removed_native_names'] = [dict(id=i, name=names.get(i), type=old['records'][i][0])
                                          for i in sorted(old['records'].keys() - new['records'].keys())]
        row['rtpc_counts'] = dict(Counter(names.get(c['id'], str(c['id']))
            for d in decoded.values() for c in d['rtpc']))
        row['native_events'] = {str(i): dict(exact=new['records'].get(i) == rec)
                               for i, rec in old['records'].items() if rec[0] == 4}
        actions = [i for i, rec in old['records'].items() if rec[0] == 3]
        row['native_actions'] = dict(count=len(actions), changed_or_missing=[i for i in actions
            if old['records'][i] != new['records'].get(i)])
        # Newly added events called by the script: retain exact action bytes as
        # evidence, without guessing action-specific layouts.
        event_names = [*['mod_music_next_' + k + str(v) for k in ('v', 'c') for v in range(8)],
                       'mod_music_next_vr', 'mod_music_next_cr',
                       *['mod_music_' + k + '_' + str(v) for k, count in
                         (('pchance', 6), ('plen', 4), ('cmute', 2), ('cas', 3), ('tp', 3)) for v in range(count)]]
        row['script_events'] = {}
        for event in event_names:
            ident = fnv(event)
            if ident not in new['records']:
                continue
            kind, body = new['records'][ident]
            if kind != 4:
                raise ValueError('Named script event has wrong type')
            r = Reader(body)
            actions = [r.read('I') for _ in range(r.count('var', 4))]
            if r.pos != len(body):
                raise ValueError('Unexplained Event bytes')
            row['script_events'][event] = dict(id=ident, actions={str(i):
                dict(type=new['records'][i][0], body=new['records'][i][1].hex()) for i in actions})
        result['banks'][path.name] = row
    index = json.loads((main / 'mods/modMusicPlus/editor/index.json').read_text())
    result['editor'] = dict(playlists=len(index['playlists']),
        playlist_regions=dict(Counter(p['region'] for p in index['playlists'])),
        selections=sum(len(p['tracks']) for p in index['playlists']),
        unique_tracks=len({(t['name'], t['source']) for p in index['playlists'] for t in p['tracks']}),
        unique_sources=sorted({t['source'] for p in index['playlists'] for t in p['tracks']}))
    result['cache'] = cache
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('main', 'banks', 'native', 'source', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--profile-bank')
    p.add_argument('--profile-target', type=int)
    a = p.parse_args()
    result = audit(a.main, a.banks, a.native, a.source, a.output)
    if a.profile_bank or a.profile_target:
        if not (a.profile_bank and a.profile_target) or Path(a.profile_bank).name != a.profile_bank:
            p.error('Profile bank basename and exact target ID required together')
        profiles = pause_profiles(read_bank(a.banks / a.profile_bank), a.profile_target)
        result['pause_profiles'] = profiles
        a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'banks': len(result['banks']), 'editor': result['editor'],
                      'decode_errors': sum(len(b['decode_errors']) for b in result['banks'].values())}))
