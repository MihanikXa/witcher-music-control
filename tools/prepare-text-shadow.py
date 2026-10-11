"""Field-scoped native SWF edits; JPEXS independently serializes and verifies.

Only approved tag payloads are spliced into original movie bytes. No CR2W
writing, import, deployment, font regeneration or whole-movie replacement.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('npc', ROOT/'tools/prepare-npc-shadow.py')
npc = importlib.util.module_from_spec(spec); spec.loader.exec_module(npc)


def shadow(effect):
    """Keep source compositing/passes; new glow direction follows accepted NPC."""
    if effect.get('type') not in ('GLOWFILTER', 'DROPSHADOWFILTER'):
        raise ValueError('Only scoped glow/drop-shadow conversion supported')
    old_color = effect.find('glowColor' if effect.get('type') == 'GLOWFILTER' else 'dropShadowColor')
    if old_color is None or int(old_color.get('alpha','255')) == 0 or any(int(old_color.get(c)) != 0 for c in ('red', 'green', 'blue')):
        raise ValueError('Refuse semantic/nonblack effect without new explicit audit')
    attrs = dict(type='DROPSHADOWFILTER', id='0', blurX='2.0', blurY='2.0', strength='1.0',
                 distance='1.0', angle=effect.get('angle', str(51471/65536)),
                 innerShadow=effect.get('innerShadow', effect.get('innerGlow')),
                 knockout=effect.get('knockout'), compositeSource=effect.get('compositeSource'),
                 passes=effect.get('passes'))
    if any(v is None for v in attrs.values()): raise ValueError('Incomplete filter contract')
    node = ET.Element('item', attrs)
    ET.SubElement(node, 'dropShadowColor', dict(type='RGBA', red='20', green='23', blue='24', alpha='166'))
    return node


def locations(root):
    """Return XML tag indices corresponding to strict binary tag paths."""
    def walk(nodes, path=()):
        for i, node in enumerate(nodes):
            address = path+(i,)
            yield address, node
            sub = node.find('subTags')
            if sub is not None: yield from walk(sub, address)
    return list(walk(root.find('tags')))


def payloads(body, start, path=()):
    result = {}
    for i, (code, a, b) in enumerate(npc.records(body, start)):
        address = path+(i,); result[address] = (code, body[a:b])
        if code == 39: result.update(payloads(body[a:b], 4, address))
    return result


def splice(body, start, replacements, path=()):
    result = body[:start]; previous = start
    for i, (code, a, b) in enumerate(npc.records(body, start)):
        address = path+(i,); original = body[a:b]
        value = replacements.get(address, original)
        if code == 39: value = splice(original, 4, replacements, address)
        header = body[previous:a]
        if value != original:
            long = len(header) == 6 or len(value) >= 63
            header = struct.pack('<H', (code<<6) | (63 if long else len(value)))
            if long: header += struct.pack('<I', len(value))
        result += header+value; previous = b
    return result


def prepare(source, digest, jar, out, field, name, sprite, height=None):
    data = source.read_bytes()
    if npc.sha(data) != digest: raise ValueError('Input pin changed')
    if ROOT/'build' not in out.resolve().parents or out.exists(): raise ValueError('Fresh private build path required')
    out.mkdir(parents=True)
    def run(label, *args):
        p = subprocess.run(['java', '-jar', str(jar), *map(str,args)], capture_output=True, timeout=60)
        (out/(label+'.log')).write_bytes(p.stdout+p.stderr)
        if p.returncode: raise ValueError('JPEXS failed: '+label)
    run('export', '-swf2xml', source, out/'before.xml')
    root = ET.parse(out/'before.xml').getroot(); changed = copy.deepcopy(root)
    nodes = locations(changed); definitions = [(p,n) for p,n in nodes
        if n.get('type') == 'DefineEditTextTag' and n.get('characterID') == str(field)]
    scopes = {p:n for p,n in nodes if n.get('type') == 'DefineSpriteTag'}
    placements = [(p,n) for p,n in nodes if n.get('type') == 'PlaceObject3Tag'
        and n.get('name') == name and n.get('characterId') == str(field)
        and (int(scopes[p[:-1]].get('spriteId')) if len(p)>1 else 0) == sprite]
    if len(definitions) != 1 or len(placements) != 1: raise ValueError('Nonunique/missing explicit field placement')
    fp, text = definitions[0]; pp, placement = placements[0]
    effects = placement.find('surfaceFilterList')
    if effects is None or len(effects) != 1: raise ValueError('Expected exactly one audited local effect')
    before = npc.canonical(effects[0]); effects[0] = shadow(effects[0]); approved = {pp}
    original_height = text.get('fontHeight')
    if height is not None:
        if not 1 <= height <= 100: raise ValueError('Font size outside trial range')
        text.set('fontHeight', str(height*20)); approved.add(fp)
    ET.ElementTree(changed).write(out/'changed.xml', encoding='utf-8', xml_declaration=True)
    run('unchanged', '-xml2swf', out/'before.xml', out/'unchanged.swf')
    run('changed', '-xml2swf', out/'changed.xml', out/'reassembled.swf')
    original = npc.body(data); start = (5+4*(original[0]>>3)+7)//8+4
    old = payloads(original,start)
    unchanged = payloads(npc.body((out/'unchanged.swf').read_bytes()),start)
    modified = payloads(npc.body((out/'reassembled.swf').read_bytes()),start)
    if any(unchanged.get(p) != old[p] for p in approved): raise ValueError('Unchanged selected tag round-trip differs')
    replacements = {p:modified[p][1] for p in approved}
    if any(modified[p][0] != old[p][0] for p in approved): raise ValueError('Tag type changed')
    final_body = splice(original,start,replacements)
    final = b'CWS'+data[3:4]+struct.pack('<I',len(final_body)+8)+zlib.compress(final_body)
    inputs = out/'input'; inputs.mkdir(); target = inputs/source.name; target.write_bytes(final)
    run('verify', '-swf2xml', target, out/'verified.xml')
    if npc.canonical(ET.parse(out/'verified.xml').getroot()) != npc.canonical(changed):
        raise ValueError('Independent decode disagrees with exact approved XML delta')
    if source.read_bytes() != data: raise ValueError('Source changed')
    report = dict(input_path=str(source.resolve()),input_sha256=digest,output_path=str(target.resolve()),
        output_sha256=npc.sha(final),ffdec_sha256=npc.sha(jar.read_bytes()),field=field,name=name,
        sprite=sprite,depth=int(placement.get('depth')),approved_tag_paths=[list(p) for p in sorted(approved)],
        font_height_before=original_height,font_height_after=text.get('fontHeight'),
        before=before,after=npc.canonical(effects[0]),unchanged_selected_tags_exact=True,
        independently_decoded_delta_exact=True,other_tags_retained_from_source=True,
        editor_imported=False,cooked=False,packaged=False,runtime_tested=False)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n'); return report


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--sha256',required=True); ap.add_argument('--ffdec',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--field',type=int,required=True)
    ap.add_argument('--name',required=True); ap.add_argument('--sprite',type=int,required=True)
    ap.add_argument('--height',type=int); a=ap.parse_args()
    print(json.dumps(prepare(a.source,a.sha256,a.ffdec,a.out,a.field,a.name,a.sprite,a.height),indent=2))


if __name__=='__main__': main()
