"""Read-only v150 single-cue experiment gate; never relaxes production gates.

Validates declared structure by complete bounded decoding AND byte restoration.
New default-node records are independently serialized from explicit field rules.
No licence/project-file contents are read. All output is private build evidence.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

from white_orchard_compare import read_bank, difference
from white_orchard_prepare import build_path, digest
from white_orchard_candidate_package import diagnostics
from white_orchard_state_bank_audit import header, native_groups
from white_orchard_build_gate import plugins
from regional_music_bank import decode, validate_record
from music_comparison_decode import music, track
from music_material_opus import chunks
from sparse_approved_cue import (REPO, SOURCE, ROOT, MUSIC, SPEC, D_SPEC, read,
                                 verify_accepted, validate_import, measured_template,
                                 validate, context)

SEGMENT, TRACK, MEDIA, SELECTED = 1029261546, 499024852, 383927916, 133462974


def require(condition, message):
    if not condition:
        raise ValueError(message)


def embedded(bank):
    idx, data = bank['payload']['DIDX'], bank['payload']['DATA']
    require(len(idx) % 12 == 0, 'Malformed DIDX')
    result, ranges = {}, []
    for pos in range(0, len(idx), 12):
        ident, offset, size = struct.unpack_from('<III', idx, pos)
        require(ident not in result and size > 0 and offset + size <= len(data), 'DIDX identity/bounds')
        result[ident] = data[offset:offset + size]
        ranges.append((offset, offset + size))
    ranges.sort()
    require(all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:])), 'Overlapping media')
    end = 0
    for start, stop in ranges:
        require(not any(data[end:start]), 'Unexplained nonzero DATA padding')
        end = stop
    require(not any(data[end:]), 'Unexplained trailing DATA bytes')
    return result


def header_gate(a, b, metadata):
    ha, hb = header(a), header(b, metadata)
    require(hb['hash_matches_metadata_guid'] and hb['project_id'] == 17637, 'BKHD metadata mismatch')
    excluded = {'hash_hex', 'padding_hex', 'metadata_hash', 'hash_matches_metadata_guid'}
    require({k:v for k,v in ha.items() if k not in excluded} ==
            {k:v for k,v in hb.items() if k not in excluded}, 'BKHD identity changed')
    # BKHD(8+40+pad), DIDX(8+n), DATA header(8): align DATA start.
    # One additional 12-byte DIDX entry consumes the old 12 zero pad bytes.
    for bank, h in ((a, ha), (b, hb)):
        require(list(bank['payload'])[:3] == ['BKHD','DIDX','DATA'], 'Unexpected memory chunk order')
        padding = (-64 - len(bank['payload']['DIDX'])) % 16
        require(h['alignment_flags'] == 16 and h['padding_hex'] == bytes(padding).hex(),
                'Unexplained/nonzero BKHD alignment padding')
    return hb


def state_bytes(group, ids):
    require(len(ids) < 128, 'Unsupported State count')
    return (bytes([1, 0, 2, 1, 1]) + struct.pack('<IBB', group, 0, len(ids))
            + b''.join(struct.pack('<IHHf', i, 1, 0, -200) for i in sorted(ids)))


def item_bytes(item):
    keys = ('segment', 'item', 'children', 'type', 'loop', 'loop_min', 'loop_max',
            'weight', 'avoid', 'use_weight', 'shuffle')
    return struct.pack('<IIIIhhhIHBB', *(item[k] for k in keys))


def selected_gate(before, after, group, muted):
    require(before[0] == after[0] == 13, 'Wrong selected type')
    a, b = music(*before), music(*after)
    require(not a['rtpc'] and not a['state']['groups'] and not a['state']['properties'],
            'Nonpristine selected prefix')
    require(a['children'] == [4111369, 319905093], 'Unexpected native children')
    # Only add local State Volume, one physical child and the declared sequence.
    sa = a['state']
    child_start = sa['end'] + 2  # verified zero RTPC count
    child_end = child_start + 4 + 4 * len(a['children'])
    playlist_start = a['playlist'][0]['offset'] - 4
    items = copy.deepcopy(a['playlist'][:3])
    items[0].update(children=2, loop=0)
    items[1]['segment'] = SEGMENT
    items[2].update(segment=4111369, loop=3)
    expected = (before[1][:sa['start']] + state_bytes(group, muted)
                + before[1][sa['end']:child_start]
                + struct.pack('<4I', 3, 4111369, 319905093, SEGMENT)
                + before[1][child_end:playlist_start] + struct.pack('<I', 3)
                + b''.join(item_bytes(i) for i in items))
    require(after[1] == expected, 'Unexpected selected flags/routing/State/playlist/tail bytes')
    return dict(parent=b['parent'], children=b['children'], state=b['state'],
                playlist=b['playlist'], immutable_remainder_exact=True)


def default_base(parent):
    # v150 NodeBase: no FX/metadata, inherited bus, no properties/ranges/3D/aux,
    # no reflections; native default advanced flags/max-voices; no States/RTPCs.
    return (bytes(4) + struct.pack('<II', 0, parent) + bytes(5) + bytes(4)
            + bytes([0, 1, 0, 0, 0, 0]) + bytes(4))


def new_records_gate(records, cue_ids, media_size):
    seg = records[SEGMENT]; tr = records[TRACK]
    require(seg[0] == 10 and tr[0] == 11, 'Wrong new record types')
    expected_segment = (b'\0' + default_base(SELECTED) + struct.pack('<II', 1, TRACK)
                        + struct.pack('<ddfBBBI', 16000, 0, 60, 4, 4, 1, 0)
                        + struct.pack('<dI', 40850, 2)
                        + struct.pack('<Id', cue_ids[0], 0) + b'\0'
                        + struct.pack('<Id', cue_ids[1], 30850) + b'\0')
    expected_track = (struct.pack('<B I I B I I B', 0, 1, 262145, 0, MEDIA, media_size, 0)
                      + struct.pack('<IIIIdddd', 1, 0, MEDIA, 0, 0, 0, 0, 40850)
                      + struct.pack('<II', 1, 0) + default_base(SEGMENT)
                      + struct.pack('<Bi', 0, 0))
    require(seg[1] == expected_segment, 'Unexpected new segment fields/flags/tail')
    require(tr[1] == expected_track, 'Unexpected new track fields/flags/source/clip/tail')
    return {'segment': music(*seg), 'track': track(tr[1])}


def metadata_media(folder):
    tree = ET.parse(folder / 'SoundbanksInfo.xml')
    node = next(n for n in tree.iter('SoundBank') if n.findtext('ShortName') == 'music_prologue')
    files = node.findall('./Media/File')
    require(len({n.get('Id') for n in files}) == len(files), 'Duplicate media metadata')
    return {int(n.get('Id')): n for n in files}, tree


def verify(root, banks, baseline):
    project = root / 'generation'
    verify_accepted()
    spec, d = read(SPEC), read(D_SPEC)
    original, states = context(SOURCE, d)
    pre = ET.parse(root / 'sparse/validation/pre-import-music.xml').getroot()
    source = ET.parse(project / MUSIC).getroot()
    validate(original, pre, spec, d, 'sparse', states, measured_template(d))
    source_gate = validate_import(pre, source, {}, read(root / 'media/audio-proof.json'),
                                  project / 'w3_audio.wproj')
    inputs = read(project / 'input-manifest.json')
    require(inputs['version'].get('WwiseVersion') == 'v2023.1.19'
            and inputs['version'].get('WwiseBuild') == '8928'
            and not (project / 'leaf-inclusion-audit.json').exists(), 'Wrong context/version')
    units = {x['relative_path'].replace('\\', '/'): x['sha256'] for x in inputs['inputs']
             if x['relative_path'].endswith('.wwu')}
    actual = {p.relative_to(project).as_posix(): p for p in project.rglob('*.wwu')}
    require(len(units) == 1508 and actual.keys() == units.keys(), 'Incomplete work units')
    for rel, sha in units.items():
        require(digest(SOURCE / rel) == sha, 'Installed source changed: ' + rel)
        if rel != MUSIC.as_posix():
            require(digest(actual[rel]) == sha, 'Unrelated work unit changed: ' + rel)
    for item in inputs['originals']:
        require(digest(project / item['relative_path']) == digest(SOURCE / item['relative_path'])
                == item['sha256'], 'Original audio changed')
    result = read(banks / 'result.json')
    require(result['exit_code'] in (0, 2) and result['expected_banks_only'], 'Generation failed')
    require(re.search(r'Wwise\s*\|\s*v2023\.1\.19\s*\|\s*Build no\.8928',
                      (banks/'generation.log').read_text(encoding='utf-8')), 'Wrong generator version')
    require(sorted(p.name for p in banks.rglob('*.bnk')) == ['Init.bnk', 'music_prologue.bnk'], 'Wrong generation scope')
    require(diagnostics(banks) == diagnostics(baseline), 'Unreviewed diagnostics')
    a, b = [read_bank(p / 'music_prologue.bnk') for p in (baseline, banks)]
    native = read_bank(SOURCE.parent.parent / 'r4data/soundbanks/Pc/music_prologue.bnk')
    nd = difference(native, a)
    require(not (nd['added'] or nd['removed'] or nd['changed'])
            and set(nd['chunk_changed']) <= {'BKHD'}, 'Retained baseline no longer native-exact')
    hb = header_gate(a, b, banks / 'SoundbanksInfo.xml')
    ia, ib = [read_bank(p / 'Init.bnk') for p in (baseline, banks)]
    require(ia['sha256'] == ib['sha256'], 'Generated Init changed')
    native_init = read_bank(SOURCE.parent.parent / 'r4data/soundbanks/Pc/Init.bnk')
    require(plugins(ib['payload']['INIT']) == plugins(native_init['payload']['INIT']), 'Native plugins mismatch')
    require(digest(Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\initialdata\sound\Init.bnk'))
            == native_init['sha256'] == '2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277', 'Native Init changed')
    media_a, media_b = embedded(a), embedded(b)
    require(set(media_b) - set(media_a) == {MEDIA} and set(media_a) <= set(media_b), 'Unexpected embedded membership')
    require(all(media_a[i] == media_b[i] for i in media_a), 'Original embedded media changed')
    ma, ta = metadata_media(baseline); mb, tb = metadata_media(banks)
    require(set(mb) - set(ma) == {MEDIA} and set(ma) <= set(mb), 'Unexpected media metadata membership')
    for ident, node in ma.items():
        require(ET.tostring(node) == ET.tostring(mb[ident]), 'Existing media/stream metadata changed')
        rel = node.findtext('Path')
        require(digest(baseline / rel) == digest(banks / rel), 'Existing external media changed')
    new_media = media_b[MEDIA]
    wem = chunks(new_media)
    fmt = wem[b'fmt ']
    require(len(fmt) == 66 and struct.unpack_from('<HHI', fmt) == (65535, 2, 48000)
            and struct.unpack_from('<I', fmt, 24)[0] == 1960800, 'Encoded format/sample count mismatch')
    cached = list((project / '.cache/Windows/SFX').glob('WMC_S04a_approved_*.wem'))
    require(len(cached) == 1 and cached[0].read_bytes() == new_media, 'Bank media differs from official conversion')
    require(mb[MEDIA].get('Streaming') == 'false' and mb[MEDIA].get('Location') == 'Memory',
            'Unexpected new streaming dependency')
    require(any(s['plugin'] == 262145 for kind, body in a['records'].values() if kind == 11
                for s in track(body)['sources']), 'New codec not present in native baseline')
    groups = [n for n in tb.iter('StateGroup') if n.get('Name') == 'game_state']
    old_groups = [n for n in ta.iter('StateGroup') if n.get('Name') == 'game_state']
    require(groups and old_groups, 'Missing sync metadata')
    def sync(n):
        return int(n.get('Id')), {x.get('Name'):int(x.get('Id')) for x in n.findall('./States/State')}
    group, ids = sync(groups[0])
    require(set(ids) == set(states) and all(sync(n) == (group, ids) for n in groups + old_groups), 'State IDs changed')
    require(group in {g['id'] for g in native_groups(native_init['payload']['STMG'])['groups']}, 'New global StateGroup')
    nodes = {n.get('ID'):n for n in source.iter() if n.get('ShortID')}
    state_targets = {int(nodes[g].get('ShortID')) for g in spec['other_local_state_scopes']}
    static_targets = {int(nodes[g].get('ShortID')) for g in d['static_targets'] if g != spec['selected']}
    delta = difference(a, b)
    require(delta['added'] == [{'id':TRACK,'type':11},{'id':SEGMENT,'type':10}] and not delta['removed'], 'Unexpected HIRC membership')
    require({x['id'] for x in delta['changed']} == state_targets | static_targets | {SELECTED}, 'Unexpected changed records')
    muted = {ids[n] for n in d['muted_states']}
    checks = {}
    for ident in sorted(state_targets | static_targets):
        parent = music(*a['records'][ident])['parent']
        old_volume = struct.unpack('<f', decode(*a['records'][ident])['properties'].get(0, bytes(4)))[0]
        checks[str(ident)] = validate_record(a['records'][ident], b['records'][ident],
             'state' if ident in state_targets else 'static', parent, group, muted, old_volume)
    checks[str(SELECTED)] = selected_gate(a['records'][SELECTED], b['records'][SELECTED], group, muted - {ids['exploration']})
    seg = next(n for n in source.iter('MusicSegment') if int(n.get('ShortID')) == SEGMENT)
    cues = seg.findall('./ObjectLists/ObjectList[@Name="Cues"]//MusicCue')
    # Local Cue ShortIDs are not stored in WWU. Pin observed compiler identities
    # against the exact source GUIDs and independently repeated identical output;
    # do not invent a GUID->ShortID hash algorithm. No native rule names these IDs.
    marker_ids = {'{58205DEA-62A7-4731-8A7E-BDB54D776881}':43573010,
                  '{C75E0F5E-0C6C-4A4E-BDAF-FF3423214A4A}':1539036744}
    require([n.get('ID') for n in cues] == list(marker_ids), 'Unreviewed source cue identities')
    cue_ids = list(marker_ids.values())
    new = new_records_gate(b['records'], cue_ids, len(new_media))
    require(set(delta['chunk_changed']) == {'BKHD','HIRC','DIDX','DATA'}, 'Unexpected bank chunks')
    require(set(a['payload']) == set(b['payload']) and all(a['payload'][k] == b['payload'][k]
            for k in a['payload'] if k not in delta['chunk_changed']), 'Unexpected chunk change')
    preserved = read(root / 'preservation.json')
    for rel, item in preserved['preserved_release_inputs'].items():
        require(digest(REPO / rel) == item['sha256'], 'Preserved release changed')
    return dict(passed=True, source=source_gate, work_units=1508, original_audio=len(inputs['originals']),
                generation_exit=result['exit_code'], warnings=sum(diagnostics(banks).values()),
                baseline_warnings_exact=True, candidate_sha256=b['sha256'], baseline_sha256=a['sha256'],
                candidate_bytes=b['bytes'], hirc_count=len(b['records']), delta=delta, records=checks,
                new_records=new, new_media=dict(id=MEDIA, bytes=len(new_media),
                    sha256=hashlib.sha256(new_media).hexdigest(), format='Wwise Vorbis',
                    frames=1960800, channels=2, rate=48000, embedded=True, official_cache_exact=True,
                    decoded_pcm_verified=False),
                original_embedded_exact=len(media_a), original_metadata_and_external_payloads_exact=len(ma),
                header=hb, generated_init_exact=True, generated_init_sha256=ib['sha256'],
                native_init_sha256=native_init['sha256'], all24_accepted_exact=True,
                retail_verified=False, encoded_media_auditioned=False, release_ready=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--banks', type=Path, required=True)
    p.add_argument('--baseline', type=Path, default=REPO/'build/licensed-white-orchard/baseline-banks')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    output = build_path(args.output)
    require(not output.exists(), 'Preserve previous gate evidence')
    try:
        result = verify(args.root.resolve(), args.banks.resolve(), args.baseline.resolve())
    except Exception as error:
        output.write_text(json.dumps({'passed':False,'error':str(error)}, indent=2)+'\n')
        raise
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','candidate_sha256','hirc_count','generation_exit','warnings')}))
