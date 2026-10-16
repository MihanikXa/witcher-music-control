"""Read-only v150 music-tail inspection, independent of production bank gates.

Format reference: wwiser wparser.py, commit
08e937b649bc7007c234bbd59e34a41d5eef3b38, MusicNode/TransAware/
MusicSwitch/MusicRanSeq functions. No third-party code is imported or executed.
Unknown versions, layouts, out-of-range arrays and trailing data fail closed.
This decodes structure, not runtime audibility or author intent.
"""
import math

from regional_music_bank import Reader, states


def prefix(r):
    """Music-node NodeBase, including non-automated listener routing only."""
    r.read('B')
    count = r.count('B', 6)
    if count:
        r.read('B')
        r.skip(count * 6)
    r.read('B')
    r.skip(r.count('B', 6) * 6)
    bus, parent = r.read('I'), r.read('I')
    r.read('B')
    count = r.count('B', 5)
    ids = [r.read('B') for _ in range(count)]
    values = [r.read('I') for _ in range(count)]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate node property')
    r.skip(r.count('B', 9) * 9)
    position = r.read('B')
    if position & 3 == 3:
        if position & 96:
            raise ValueError('Unsupported positioning automation')
        positioning_3d = r.read('B')
    else:
        positioning_3d = None
    aux = r.read('B')
    if aux & 8:
        r.skip(16)
    reflections = r.read('I')
    r.skip(6)
    state = states(r)
    return dict(bus=bus, parent=parent, properties=dict(zip(ids, values)),
                positioning=[position, positioning_3d], reflections=reflections, state=state)


def rtpcs(r):
    curves = []
    for _ in range(r.count('H', 16)):
        ident, typ, accum = r.read('I'), r.read('B'), r.read('B')
        param, curve, scale = r.var(), r.read('I'), r.read('B')
        points = [r.read('ffI') for _ in range(r.count('H', 12))]
        if any(not math.isfinite(v) for point in points for v in point[:2]):
            raise ValueError('Nonfinite RTPC graph')
        curves.append(dict(id=ident, type=typ, accumulation=accum,
                           parameter=param, curve=curve, scale=scale, points=points))
    return curves


def track(body, version=150):
    """v150 non-switch music tracks; source/plugin payload remains uninterpreted."""
    if version != 150:
        raise ValueError('Only v150 tracks supported')
    r = Reader(body)
    r.read('B')
    sources = []
    for _ in range(r.count('I', 14)):
        plugin, streaming, ident, memory, flags = r.read('IBIIB')
        params = None
        if plugin & 15 == 2:
            count = r.read('I')
            start = r.pos
            r.skip(count)
            params = body[start:r.pos].hex()
        sources.append(dict(plugin=plugin, streaming=streaming, id=ident,
                            memory=memory, flags=flags, plugin_parameters=params))
    clips = []
    count = r.count('I', 44)
    for _ in range(count):
        clips.append(dict(zip(('track', 'source', 'event', 'play_at', 'begin', 'end', 'duration'),
                              r.read('IIIdddd'))))
        if any(not math.isfinite(clips[-1][k]) for k in ('play_at', 'begin', 'end', 'duration')):
            raise ValueError('Nonfinite music clip')
    subtracks = r.read('I') if count else None
    automation = []
    for _ in range(r.count('I', 12)):
        index, typ = r.read('II')
        points = [r.read('ffI') for _ in range(r.count('I', 12))]
        automation.append(dict(clip=index, type=typ, points=points))
    result = prefix(r)
    result.update(sources=sources, clips=clips, subtracks=subtracks,
                  automation=automation, rtpc=rtpcs(r))
    result['track_type'] = r.read('B')
    if result['track_type'] == 3:
        raise ValueError('Switch music tracks not yet inspected')
    result['lookahead'] = r.read('i')
    if r.pos != len(body):
        raise ValueError('Unexplained track tail')
    return result


def music(kind, body, version=150):
    if version != 150 or kind not in (10, 12, 13):
        raise ValueError('Only v150 segment/switch/playlist inspection supported')
    r = Reader(body)
    r.read('B')
    result = prefix(r)
    result['rtpc'] = rtpcs(r)
    result['children'] = [r.read('I') for _ in range(r.count('I', 4))]
    result['meter'] = r.read('ddfBBB')
    result['stingers'] = [r.read('IIIIiI') for _ in range(r.count('I', 24))]
    if kind == 10:
        result['duration_ms'] = r.read('d')
        if not math.isfinite(result['duration_ms']) or result['duration_ms'] < 0:
            raise ValueError('Invalid music duration')
        markers = []
        for _ in range(r.count('I', 13)):
            ident, position = r.read('I'), r.read('d')
            if not math.isfinite(position):
                raise ValueError('Nonfinite marker')
            end = body.find(b'\0', r.pos)
            if end < 0:
                raise ValueError('Unterminated marker')
            name = body[r.pos:end].decode('utf-8', errors='strict')
            r.pos = end + 1
            markers.append(dict(id=ident, position=position, name=name))
        result['markers'] = markers
    else:
        rules = []
        for _ in range(r.count('I', 54)):
            source = [r.read('I') for _ in range(r.count('I', 4))]
            dest = [r.read('I') for _ in range(r.count('I', 4))]
            src = dict(zip(('fade_ms', 'curve', 'offset', 'sync', 'cue', 'post_exit'), r.read('iIiIIB')))
            dst = dict(zip(('fade_ms', 'curve', 'offset', 'cue', 'jump', 'jump_type', 'entry', 'pre_entry', 'match_cue'), r.read('iIiiIHHBB')))
            transition = None
            if r.read('B'):
                transition = dict(id=r.read('I'), fade_in=r.read('iIi'),
                                  fade_out=r.read('iIi'), pre=r.read('B'), post=r.read('B'))
            rules.append(dict(source=source, dest=dest, src=src, dst=dst, transition=transition))
        result['rules'] = rules
        if kind == 12:
            result['continue'] = r.read('B')
            depth = r.read('I')
            if depth > 64 or depth > (len(body) - r.pos) // 5:
                raise ValueError('Impossible argument depth')
            groups = [r.read('I') for _ in range(depth)]
            types = [r.read('B') for _ in range(depth)]
            result['arguments'] = list(zip(groups, types))
            size, mode = r.read('I'), r.read('B')
            if size % 12:
                raise ValueError('Invalid decision-tree size')
            result['mode'] = mode
            nodes = [r.read('IIHH') for _ in range(size // 12)]
            rows, visited = [], set()

            def visit(index, level, path):
                if index >= len(nodes) or index in visited:
                    raise ValueError('Invalid/cyclic decision-tree index')
                visited.add(index)
                key, union, weight, probability = nodes[index]
                if level == depth:
                    rows.append(dict(path=path, target=union, weight=weight, probability=probability))
                else:
                    first, count = union & 65535, union >> 16
                    if first + count > len(nodes):
                        raise ValueError('Invalid decision-tree children')
                    for child in range(first, first + count):
                        visit(child, level + 1, path + [nodes[child][0]])
            if nodes:
                visit(0, 0, [])
            if len(visited) != len(nodes):
                raise ValueError('Unreachable decision-tree bytes')
            result['entries'] = rows
        else:
            count = r.read('I')
            if count > (len(body) - r.pos) // 30:
                raise ValueError('Impossible playlist count')
            # Iterative child closure avoids recursion on untrusted input.
            pending, items = 1, []
            while pending:
                if len(items) >= count:
                    raise ValueError('Playlist child count mismatch')
                offset = r.pos
                values = r.read('IIIIhhhIHBB')
                item = dict(zip(('segment', 'item', 'children', 'type', 'loop', 'loop_min',
                                 'loop_max', 'weight', 'avoid', 'use_weight', 'shuffle'), values))
                item['offset'] = offset
                items.append(item)
                pending += item['children'] - 1
            if len(items) != count:
                raise ValueError('Playlist item count mismatch')
            result['playlist'] = items
    if r.pos != len(body):
        raise ValueError('Unexplained music tail: %d bytes' % (len(body) - r.pos))
    return result
