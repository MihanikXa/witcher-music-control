"""Bounds-checked v150 music-node prefix/State decoder; never writes banks.

Layout provenance: pinned wwiser wparser.py (report34), cross-checked against
native-exact NML and retained D. Unsupported spatial layouts fail closed.
Opaque music/RTPC tails are preserved byte-for-byte, not heuristically decoded.
"""
import math
import struct
import xml.etree.ElementTree as ET


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def read(self, fmt):
        size = struct.calcsize('<' + fmt)
        if self.pos + size > len(self.data):
            raise ValueError('Truncated v150 music node')
        values = struct.unpack_from('<' + fmt, self.data, self.pos)
        self.pos += size
        return values[0] if len(values) == 1 else values

    def skip(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise ValueError('Truncated bounded array')
        self.pos += count

    def var(self):
        value = 0
        for index in range(5):
            byte = self.read('B')
            if index == 0 and byte == 128:
                raise ValueError('Noncanonical variable integer')
            value = (value << 7) | (byte & 127)
            if value > 0xffffffff:
                raise ValueError('Variable integer overflow')
            if not byte & 128:
                return value
        raise ValueError('Unterminated variable integer')

    def count(self, fmt, minimum):
        count = self.var() if fmt == 'var' else self.read(fmt)
        if count > (len(self.data) - self.pos) // minimum:
            raise ValueError('Impossible bounded count')
        return count


def states(r):
    start = r.pos
    properties = []
    for _ in range(r.count('var', 3)):
        properties.append((r.var(), r.read('B'), r.read('B')))
    if len({p[0] for p in properties}) != len(properties):
        raise ValueError('Duplicate State property')
    groups = []
    for _ in range(r.count('var', 6)):
        group_id, sync = r.read('I'), r.read('B')
        entries = []
        for _ in range(r.count('var', 6)):
            ident = r.read('I')
            count = r.count('H', 6)
            ids = [r.read('H') for _ in range(count)]
            values = [r.read('f') for _ in range(count)]
            if len(set(ids)) != len(ids) or not all(math.isfinite(x) for x in values):
                raise ValueError('Duplicate/nonfinite inline State properties')
            entries.append({'id': ident, 'properties': dict(zip(ids, values))})
        if len({s['id'] for s in entries}) != len(entries):
            raise ValueError('Duplicate State ID')
        groups.append({'id': group_id, 'sync': sync, 'states': entries})
    if len({g['id'] for g in groups}) != len(groups):
        raise ValueError('Duplicate StateGroup')
    return {'start': start, 'end': r.pos, 'properties': properties, 'groups': groups}


def decode(kind, body, version=150):
    if version != 150 or kind not in (12, 13):
        raise ValueError('Only v150 MusicSwitch/MusicPlaylist nodes supported')
    r = Reader(body)
    r.read('B')  # MusicNode flags before NodeBase
    r.read('B')  # override parent FX
    count = r.count('B', 6)
    if count:
        r.read('B')  # bypass all
        r.skip(count * 6)  # index, effect ID, v150 bit vector
    r.read('B')  # override metadata
    r.skip(r.count('B', 6) * 6)
    bus, parent = r.read('I'), r.read('I')
    r.read('B')  # priority/MIDI bit vector
    prop_start = r.pos
    count = r.count('B', 5)
    ids = [r.read('B') for _ in range(count)]
    raw = [body[r.pos + i*4:r.pos + (i+1)*4] for i in range(count)]
    r.skip(count * 4)
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate node property')
    prop_end = r.pos
    r.skip(r.count('B', 9) * 9)  # ranged properties: ID, min/max raw values
    positioning = r.read('B')
    if positioning & 1 and positioning & 2:
        raise ValueError('Unreviewed listener-relative/spatial layout')
    aux = r.read('B')
    if aux & 8:
        r.skip(16)
    reflections = r.read('I')
    r.skip(6)  # advance flags, virtual queue, max voices, threshold, HDR flags
    state = states(r)
    # RTPC count must still exist after States; rest is immutable comparison tail.
    if r.pos + 2 > len(body):
        raise ValueError('Missing RTPC tail')
    return {'bus': bus, 'parent': parent, 'reflections': reflections,
            'property_start': prop_start, 'property_end': prop_end,
            'properties': dict(zip(ids, raw)), 'state': state}


def validate_record(before, after, edit, parent, group=None, muted_ids=None, original_volume=0):
    kind, old_body = before
    if after[0] != kind:
        raise ValueError('HIRC type changed')
    new_body = after[1]
    a, b = decode(kind, old_body), decode(kind, new_body)
    if a['parent'] != parent or b['parent'] != parent:
        raise ValueError('Source/serialized parent mismatch')
    if edit == 'state':
        sa, sb = a['state'], b['state']
        if sa['properties'] or sa['groups']:
            raise ValueError('Nonpristine baseline State chunk')
        if sb['properties'] != [(0, 2, 1)] or len(sb['groups']) != 1:
            raise ValueError('Only additive dB Volume permitted')
        g = sb['groups'][0]
        if g['id'] != group or g['sync'] != 0 or len(g['states']) != len(muted_ids):
            raise ValueError('Unexpected StateGroup/synchronization/count')
        if {s['id'] for s in g['states']} != set(muted_ids) or any(s['properties'] != {0: -200.0} for s in g['states']):
            raise ValueError('Unexpected State values/references')
        restored = new_body[:sb['start']] + old_body[sa['start']:sa['end']] + new_body[sb['end']:]
    elif edit == 'static':
        pa, pb = a['properties'], b['properties']
        old = struct.unpack('<f', pa.get(0, bytes(4)))[0]
        if old != original_volume or pb.get(0) != struct.pack('<f', -200):
            raise ValueError('Unexpected original/new static Volume')
        if {k:v for k,v in pa.items() if k != 0} != {k:v for k,v in pb.items() if k != 0}:
            raise ValueError('Unapproved node property changed')
        restored = new_body[:b['property_start']] + old_body[a['property_start']:a['property_end']] + new_body[b['property_end']:]
    else:
        raise ValueError('Unapproved edit kind')
    if restored != old_body:
        raise ValueError('Unapproved prefix/tail/routing/RTPC change')
    return {'kind': kind, 'parent': parent, 'baseline_state_offset': a['state']['start'],
            'candidate_state_offset': b['state']['start'], 'immutable_remainder_exact': True}


def record_gate(before, after, spec, music, globals_tree, metadata, native_group_ids, sync_ids):
    """Field allowlist after independent full source verification; no offsets."""
    nodes = {n.get('ID'): n for n in music.iter() if n.get('ShortID')}
    parents = {c:p for p in music.iter() for c in p}
    group = next(n for n in globals_tree.iter('StateGroup') if n.get('ID') == spec['game_state_group'])
    # Source global State WWUs do not store ShortIDs. Require an independently
    # captured WAAPI GUID->ShortID table, never infer them from filenames.
    group_id = sync_ids[group.get('ID')]
    states_by_name = {n.get('Name'): sync_ids[n.get('ID')] for n in group.iter('State')}
    if len(states_by_name) != 25 or group_id not in native_group_ids:
        raise ValueError('Missing native/global State definitions')
    matches = [n for n in metadata.iter('StateGroup') if int(n.get('Id')) == group_id]
    if not matches or any(n.get('Name') != group.get('Name') for n in matches):
        raise ValueError('Metadata/global StateGroup mismatch')
    names = {int(n.get('Id')):n.get('Name') for n in matches[0].findall('./States/State')}
    # Full-context SoundbanksInfo repeats sync definitions for each bank.
    # Every occurrence must agree; duplicate IDs inside one enum fail.
    for match in matches:
        entries = match.findall('./States/State')
        observed = {int(n.get('Id')):n.get('Name') for n in entries}
        if len(observed) != len(entries) or observed != names:
            raise ValueError('Inconsistent repeated metadata State definitions')
    if names != {i:name for name,i in states_by_name.items()}:
        raise ValueError('Metadata/global State mismatch')
    wanted = {int(nodes[i].get('ShortID')): (i, 'state') for i in spec['state_scopes']}
    for i in spec['static_targets']:
        ident = int(nodes[i].get('ShortID'))
        if ident in wanted:
            raise ValueError('Overlapping field edits')
        wanted[ident] = (i, 'static')
    if set(before['records']) != set(after['records']):
        raise ValueError('Unexpected HIRC addition/removal')
    changed = {i for i in before['records'] if before['records'][i] != after['records'][i]}
    if changed != set(wanted):
        raise ValueError('Unexpected changed/unchanged HIRC object set')
    result = {}
    for ident, (guid, edit) in wanted.items():
        node = nodes[guid]
        parent = parents[node]
        while parent.get('ShortID') is None:
            parent = parents[parent]
        result[str(ident)] = validate_record(before['records'][ident], after['records'][ident],
            edit, int(parent.get('ShortID')), group_id,
            {states_by_name[name] for name in spec['muted_states']},
            spec['decisions'].get(guid, {}).get('original_volume', 0))
    return result
