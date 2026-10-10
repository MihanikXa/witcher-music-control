"""Original movie-local utility fonts and one exact interaction field edit.

Writes standard authoring SWFs only. No CR2W writer, importer or deployment.
Uses the independently verified v1 glyph serializer without modifying v1.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('convert',ROOT/'tools/build-gentium-swf.py')
convert = importlib.util.module_from_spec(spec); spec.loader.exec_module(convert)
audit = convert.audit
KEY = 'gameplay/gui_new/swf/hud/hud_interactions.redswf'
NATIVE_SHA = '075e0cf4fa94ea293ad50d8528d0dc0778546794f53a07655885a6156dc4f03d'
RUNTIME_SHA = '5e1ce7d3be052cea8a0ea9d1d744a3fe059fd367bc4bd7ed951fa76d599780e9'
FIELD = 215
IDS = {'Regular':218,'Medium':219}
ALIASES = {'Regular':'Quiet Folio Utility','Medium':'Quiet Folio Utility Medium'}
IMAGE_TAGS = {35,36,73,1000,1008,1009}


def field_binding(payload, font_id):
    if struct.unpack_from('<H',payload)[0] != FIELD or not 1 <= font_id <= 65534:
        raise ValueError('Wrong field or invalid font ID')
    pos = convert.prep.rect_end(payload,2)
    flags = bytearray(payload[pos:pos+2])
    if flags != bytes.fromhex('8cb3') or payload[pos+2:pos+14] != b'$NormalFont\0':
        raise ValueError('Unexpected authored field flags/font class')
    # First flag byte HasFont; second byte HasFontClass. Preserve all other bits.
    flags[0] |= 1; flags[1] &= ~128
    return payload[:pos]+bytes(flags)+struct.pack('<H',font_id)+payload[pos+14:]


def font_template(base, font_id, alias):
    """Replace only a template header; offsets are relative to the offset table."""
    name = alias.encode()+b'\0'
    if len(name)>255 or not 1 <= font_id <= 65534:
        raise ValueError('Font name/ID out of range')
    flags = base[2] & ~3  # Both utility weights are upright, not SWF synthetic bold.
    return struct.pack('<HBBB',font_id,flags,base[3],len(name))+name+base[5+base[4]:]


def derive(source, destination, style):
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    font = TTFont(source); gs = font.getGlyphSet(); cmap = font.getBestCmap()
    additions, descriptions = {}, []
    for code,parts in ((0x2103,(0xB0,ord('C'))),(0x2109,(0xB0,ord('F'))),
                       (0x215F,(0xB9,0x2044))):
        if code in cmap:
            continue
        pen = TTGlyphPen(None); x = 0
        for component in parts:
            name = cmap[component]; record = DecomposingRecordingPen(gs)
            gs[name].draw(record); record.replay(TransformPen(pen,(1,0,0,1,x,0)))
            x += font['hmtx'][name][0]
        name = 'quietfolio_'+format(code,'04X'); glyph = pen.glyph()
        order = list(font.getGlyphOrder())
        font['glyf'][name] = glyph; font.setGlyphOrder(order+[name])
        glyph.recalcBounds(font['glyf']); font['hmtx'][name] = (x,glyph.xMin)
        additions[code] = name
        descriptions.append(dict(code=f'U+{code:04X}',components=[f'U+{c:04X}' for c in parts],advance=x))
    if 0x212B not in cmap:
        additions[0x212B] = cmap[0xC5]
        descriptions.append(dict(code='U+212B',canonical_equivalent='U+00C5'))
    for table in font['cmap'].tables:
        if table.isUnicode(): table.cmap.update(additions)
    # Replace identity records on every platform; retain Adobe copyright/OFL.
    for record in font['name'].names:
        if record.nameID in (1,3,4,6,16):
            value = 'QuietFolioUtility-'+style if record.nameID in (3,6) else ALIASES[style]
            font['name'].setName(value,record.nameID,record.platformID,record.platEncID,record.langID)
    font.recalcTimestamp = False; font.save(destination)
    return descriptions


def assemble(native, fonts, weight):
    offset,_,tags = audit.swf_tags(native); raw = native[offset:]
    body = zlib.decompress(raw[8:]) if raw[:1] == b'C' else raw[8:]
    size = (5+4*(body[0]>>3)+7)//8
    result = body[:size+4]; changed = 0
    for code,payload in tags:
        if code == 37 and struct.unpack_from('<H',payload)[0] == FIELD:
            for style in ('Regular','Medium'):
                result += convert.tag(75,fonts[style])
                result += convert.tag(88,struct.pack('<H',IDS[style])+ALIASES[style].encode()+b'\0'+
                                      b'Derived from Adobe Source Sans 3; SIL OFL 1.1.\0')
            payload = field_binding(payload,IDS[weight]); changed += 1
        result += convert.tag(code,payload)
    if changed != 1:
        raise ValueError('Exactly one action text definition required')
    return b'CWS'+raw[3:4]+struct.pack('<I',len(result)+8)+zlib.compress(result)


def verify_delta(native, candidate, fonts, weight):
    def header(data):
        offset= audit.swf_tags(data)[0];raw=data[offset:]
        body=zlib.decompress(raw[8:]) if raw[:1]==b'C' else raw[8:]
        size=(5+4*(body[0]>>3)+7)//8
        return raw[3],body[:size+4]
    if header(native)!=header(candidate):
        raise ValueError('Movie version, bounds, frame rate or frame count changed')
    old = audit.swf_tags(native)[2]; new = audit.swf_tags(candidate)[2]
    additions = [(c,b) for c,b in new if c == 75 and struct.unpack_from('<H',b)[0] in IDS.values()]
    if additions != [(75,fonts[s]) for s in ('Regular','Medium')]:
        raise ValueError('Additional fonts differ')
    stripped = [(c,b) for c,b in new if not(c in (75,88) and struct.unpack_from('<H',b)[0] in IDS.values())]
    expected = [(c,field_binding(b,IDS[weight]) if c==37 and struct.unpack_from('<H',b)[0]==FIELD else b) for c,b in old]
    if stripped != expected:
        raise ValueError('Changes outside font definitions and target binding')
    return dict(only_field_font_binding_changed=True,other_tags_byte_identical=True,
                abc_symbols_timelines_images_filters_preserved=True)


def main():
    import fontTools
    import uharfbuzz
    if fontTools.__version__!='4.60.1' or uharfbuzz.__version__!='0.56.3':
        raise ValueError('Pinned fonttools 4.60.1 and uharfbuzz 0.56.3 required')
    ap = argparse.ArgumentParser()
    ap.add_argument('--game',type=Path,required=True)
    ap.add_argument('--native',type=Path,required=True)
    ap.add_argument('--sources',type=Path,required=True)
    ap.add_argument('--gentium',type=Path,default=ROOT/'build/gentium-font-source-final')
    ap.add_argument('--ffdec',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a = ap.parse_args(); out = a.out.resolve()
    if ROOT/'build' not in out.parents or out.exists():
        raise ValueError('Fresh private output required')
    native = a.native.read_bytes()
    if audit.sha(native) != NATIVE_SHA:
        raise ValueError('Current native authoring source changed')
    vanilla = None
    for bundle in (a.game/'content/content0/bundles').glob('*.bundle'):
        matches = [e for e in audit.entries(bundle) if e['resource']==KEY]
        if matches:
            if vanilla is not None or len(matches)!=1 or matches[0]['codec']!=1:
                raise ValueError('Unexpected installed resource owners')
            e=matches[0]
            with bundle.open('rb') as f:
                f.seek(e['offset']); vanilla = zlib.decompress(f.read(e['packed']))
    if vanilla is None or audit.sha(vanilla)!=RUNTIME_SHA:
        raise ValueError('Installed interaction movie changed')
    if [(c,b) for c,b in audit.swf_tags(native)[2] if c not in IMAGE_TAGS] != [(c,b) for c,b in audit.swf_tags(vanilla)[2] if c not in IMAGE_TAGS]:
        raise ValueError('Native non-image contracts differ from installed runtime')
    definitions = {struct.unpack_from('<H',b)[0] for c,b in audit.swf_tags(native)[2]
                   if c in (2,7,11,14,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90)}
    if set(IDS.values()) & definitions:
        raise ValueError('New IDs collide with existing character definitions')
    pins = json.loads((ROOT/'src/fonts/source-sans-3-source.json').read_text())
    for name,record in pins['files'].items():
        if audit.sha((a.sources/name).read_bytes()) != record['sha256']:
            raise ValueError('Independent source/license hash differs')
    baseline = (a.gentium/'fonts_en.redswf').read_bytes()
    if audit.sha(baseline) != convert.BASELINE_SHA:
        raise ValueError('Pinned 383-point English subset required')
    base = next(b for c,b in audit.swf_tags(baseline)[2] if c==75)
    out.mkdir(); inputs=out/'input'; inputs.mkdir()
    (out/'runtime.redswf').write_bytes(vanilla)
    (inputs/'hud_interactions_ff_unchanged.swf').write_bytes(native)
    expected,fonts,styles = {},{},[]
    for style in ('Regular','Medium'):
        derived=out/('QuietFolioUtility-'+style+'.ttf')
        additions=derive(a.sources/('SourceSans3-'+style+'.ttf'),derived,style)
        payload,stats,records,bounds,advances,pairs=convert.font_payload(font_template(base,IDS[style],ALIASES[style]),derived,IDS[style])
        fonts[style]=payload; expected[IDS[style]]=(stats,records,bounds,advances,pairs)
        stats.update(style=style,alias=ALIASES[style],constructions=additions)
        styles.append({k:v for k,v in stats.items() if k not in ('codes','gpos_features')})
    bindings={IDS[s]:(ALIASES[s]+r'\u0000',False,False) for s in ('Regular','Medium')}
    candidates=[]
    for weight in ('Regular','Medium'):
        candidate=assemble(native,fonts,weight)
        path=inputs/('hud_interactions_ff_'+weight.lower()+'.swf'); path.write_bytes(candidate)
        xml=out/(weight.lower()+'.xml')
        p=subprocess.run(['java','-jar',str(a.ffdec.resolve()),'-swf2xml',str(path),str(xml)],capture_output=True,timeout=60)
        (out/(weight.lower()+'.jpexs.log')).write_bytes(p.stdout+p.stderr)
        if p.returncode: raise ValueError('Independent JPEXS decode failed')
        root=ET.parse(xml).getroot()
        # Validate only the two additions, leaving the original empty font 212 intact.
        for n in list(root.find('tags')):
            if n.get('type')=='DefineFont3Tag' and int(n.get('fontID')) not in expected:
                root.find('tags').remove(n)
        checked=out/(weight.lower()+'.fonts.xml');ET.ElementTree(root).write(checked)
        convert.verify_xml(checked,expected,bindings)
        field=next(n for n in root.iter() if n.get('type')=='DefineEditTextTag' and n.get('characterID')==str(FIELD))
        if field.get('fontId') != str(IDS[weight]) or field.get('hasFont')!='true' or field.get('hasFontClass')!='false' or field.get('useOutlines')!='true' or field.get('fontHeight')!='440':
            raise ValueError('Independent field binding decode failed')
        candidates.append(dict(weight=weight,path=str(path),sha256=audit.sha(candidate),delta=verify_delta(native,candidate,fonts,weight)))
    collisions=[];count=0
    for folder in ('Mods','DLC'):
        for bundle in (a.game/folder).rglob('*.bundle'):
            count+=1;collisions += [str(bundle) for e in audit.entries(bundle) if e['resource']==KEY]
        collisions += [str(p) for p in (a.game/folder).rglob('hud_interactions.redswf')]
    (out/'OFL-Adobe.txt').write_bytes((a.sources/'LICENSE.md').read_bytes())
    (out/'FONT-NOTICES.txt').write_text('Quiet Folio Utility: original derivative of Adobe Source Sans 3 3.052, Regular/Medium.\nCopyright 2010-2024 Adobe. SIL OFL 1.1; see OFL-Adobe.txt. Reserved name Source is not used as derivative family.\nOnly U+2103/U+2109/U+215F licensed component constructions and canonical U+212B mapping added.\n')
    receipt=dict(status='Source validated; unchanged and candidate Editor imports required',resource_key=KEY,
                 native_sha256=NATIVE_SHA,runtime_sha256=RUNTIME_SHA,source_provenance=pins,
                 control_path=str(inputs/'hud_interactions_ff_unchanged.swf'),control_sha256=NATIVE_SHA,
                 candidates=candidates,styles=styles,selected_trial='Regular',
                 linkage='movie-local DefineFont3 IDs 218/219; DefineEditText 215 direct FontID; no new global alias',
                 narrative_font_library_changed=False,original_font_212_preserved=True,
                 original_importassets2_preserved=True,scanned_installed_bundles=count,
                 installed_resource_collisions=collisions,independent_geometry_and_binding_verified=True,
                 official_import_verified=False,official_cook_verified=False,package_path=None,runtime_tested=False)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__': main()
