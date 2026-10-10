"""Prepare one native SWF filter edit; never write CR2W, import, cook or deploy.

JPEXS generates the changed sprite. Only its verified 24-byte shadow record is
accepted; original SWF tag bytes are retained everywhere else. This avoids
unrelated shape serialization changes from whole-movie XML reassembly.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parents[1]
INPUT_SHA = 'f84544e26c27b38e8b1f64ff8f77775743e1e6ecd7a4f1972fce381ed9a9e819'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def records(data, start):
    """Strict standard SWF tag boundaries including End, retaining offsets."""
    pos = start
    result = []
    while pos < len(data):
        if pos + 2 > len(data):
            raise ValueError('Truncated tag header')
        header = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        code, size = header >> 6, header & 63
        if size == 63:
            if pos + 4 > len(data):
                raise ValueError('Truncated long tag header')
            size = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        end = pos + size
        if end > len(data):
            raise ValueError('Truncated tag payload')
        result.append((code, pos, end))
        pos = end
        if code == 0:
            if size or pos != len(data):
                raise ValueError('Unexpected End/trailing bytes')
            return result
    raise ValueError('Missing End tag')


def body(data):
    if data[:3] not in (b'CWS', b'FWS'):
        raise ValueError('Native standard SWF required, not GFx/CR2W')
    result = zlib.decompress(data[8:]) if data[:3] == b'CWS' else data[8:]
    if len(result) + 8 != struct.unpack_from('<I', data, 4)[0]:
        raise ValueError('SWF length mismatch')
    return result


def sprite(data):
    rect_size = (5 + 4 * (data[0] >> 3) + 7) // 8
    matches = [(a, b) for code, a, b in records(data, rect_size + 4)
               if code == 39 and struct.unpack_from('<H', data, a)[0] == 63]
    if len(matches) != 1:
        raise ValueError('Expected one sprite 63')
    return matches[0]


def shadow_record(changed=False):
    # JPEXS SWFOutputStream: RGBA, four FIXED, UFIXED8, packed flags.
    # Include filter id=0. Angle is the observed exact 16.16 value 51471.
    return struct.pack('<B4B4iHB', 0, *( (20, 23, 24, 166) if changed else (0, 0, 0, 255)),
                       (2 if changed else 4) << 16, (2 if changed else 4) << 16,
                       51471, 1 << 16, (1 if changed else 3) << 8, 0x21)


def accept_sprite(original, candidate):
    """Accept only the known target placement and exact filter byte replacement."""
    if len(candidate) != len(original) or original[:4] != candidate[:4]:
        raise ValueError('Sprite layout changed')
    children = records(original, 4)
    matches = []
    for code, a, b in children:
        p = original[a:b]
        if code == 70 and len(p) >= 6 and struct.unpack_from('<HH', p, 2) == (35, 38):
            if b'tfName\0' not in p or p.count(shadow_record()) != 1:
                raise ValueError('Unexpected name/filter in target placement')
            matches.append((a, b))
    if len(matches) != 1:
        raise ValueError('Expected one character38/depth35 placement')
    a, b = matches[0]
    offset = a + original[a:b].index(shadow_record())
    expected = original[:offset] + shadow_record(True) + original[offset + 24:]
    if candidate != expected:
        raise ValueError('Unexpected sprite changes outside approved filter values')
    return offset


def canonical(node):
    return (node.tag, tuple(sorted((k, v) for k, v in node.attrib.items()
                                  if k != 'fileOffset')), (node.text or '').strip(),
            tuple(canonical(c) for c in node))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--native', type=Path, required=True)
    ap.add_argument('--ffdec', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    source = args.native.resolve()
    data = source.read_bytes()
    if sha(data) != INPUT_SHA:
        raise ValueError('Current native baseline pin changed; audit first')
    out = args.out.resolve()
    if ROOT / 'build' not in out.parents or out.exists():
        raise ValueError('Fresh ignored build output required')
    out.mkdir()
    jar = args.ffdec.resolve()

    def run(label, *argv):
        cmd = ['java', '-jar', str(jar), *map(str, argv)]
        p = subprocess.run(cmd, capture_output=True, timeout=60)
        (out / (label + '.log')).write_bytes(p.stdout + p.stderr)
        if p.returncode:
            raise ValueError('JPEXS failed: ' + label)

    xml = out / 'native.xml'
    run('export', '-swf2xml', source, xml)
    root = ET.parse(xml).getroot()
    changed = copy.deepcopy(root)
    sprites = [n for n in changed.iter() if n.get('type') == 'DefineSpriteTag' and n.get('spriteId') == '63']
    if len(sprites) != 1:
        raise ValueError('XML sprite mismatch')
    fields = [n for n in sprites[0].iter() if n.get('name') == 'tfName']
    if len(fields) != 1 or fields[0].get('characterId') != '38' or fields[0].get('depth') != '35':
        raise ValueError('XML target mismatch')
    filters = fields[0].findall('./surfaceFilterList/item')
    if len(filters) != 1 or filters[0].get('type') != 'DROPSHADOWFILTER':
        raise ValueError('XML filter mismatch')
    f = filters[0]
    before = dict(f.attrib, color=dict(f.find('dropShadowColor').attrib))
    for k, v in dict(blurX='2.0', blurY='2.0', strength='1.0', distance='1.0').items():
        f.set(k, v)
    for k, v in dict(red='20', green='23', blue='24', alpha='166').items():
        f.find('dropShadowColor').set(k, v)
    after = dict(f.attrib, color=dict(f.find('dropShadowColor').attrib))
    modified_xml = out / 'shadow.xml'
    ET.ElementTree(changed).write(modified_xml, encoding='utf-8', xml_declaration=True)
    run('unchanged-assemble', '-xml2swf', xml, out / 'unchanged.swf')
    run('changed-assemble', '-xml2swf', modified_xml, out / 'reassembled-shadow.swf')
    original_body = body(data)
    start, end = sprite(original_body)
    original_sprite = original_body[start:end]
    baseline_body = body((out / 'unchanged.swf').read_bytes())
    a, b = sprite(baseline_body)
    if baseline_body[a:b] != original_sprite:
        raise ValueError('Unchanged JPEXS target sprite not byte-identical')
    candidate_body = body((out / 'reassembled-shadow.swf').read_bytes())
    a, b = sprite(candidate_body)
    candidate_sprite = candidate_body[a:b]
    filter_offset = accept_sprite(original_sprite, candidate_sprite)
    final_body = original_body[:start] + candidate_sprite + original_body[end:]
    if final_body[:start + filter_offset] != original_body[:start + filter_offset] or final_body[start + filter_offset + 24:] != original_body[start + filter_offset + 24:]:
        raise ValueError('Movie changed outside filter record')
    inputs = out / 'input'
    inputs.mkdir()
    final = inputs / 'hud_enemyfocus.swf'
    final.write_bytes(data[:8] + (zlib.compress(final_body) if data[:3] == b'CWS' else final_body))
    run('verify-export', '-swf2xml', final, out / 'verified.xml')
    if canonical(ET.parse(out / 'verified.xml').getroot()) != canonical(changed):
        raise ValueError('Final exported XML differs from approved filter-only source')
    if source.read_bytes() != data:
        raise ValueError('Native input changed')
    receipt = dict(input_path=str(source), input_sha256=sha(data), ffdec_sha256=sha(jar.read_bytes()),
                   output_path=str(final), output_sha256=sha(final.read_bytes()), before=before, after=after,
                   decompressed_byte_differences=sum(x != y for x, y in zip(original_body, final_body)),
                   approved_filter_record_offset_in_body=start + filter_offset,
                   movie_bytes_outside_filter_identical=True, unchanged_target_sprite_identical=True,
                   final_xml_matches_filter_only_source=True, editor_imported=False, cooked=False,
                   packaged=False, runtime_tested=False, package_path=None)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
