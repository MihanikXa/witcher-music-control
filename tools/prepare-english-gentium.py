"""Prepare licensed glyph source data; never writes SWF/CR2W or packages.

Requires fonttools==4.60.1. Reads the installed font bundle directly. Only
ignored build output is allowed; original game/font tables remain private.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit-ui.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
URL = 'https://software.sil.org/downloads/r/gentium/GentiumBook-7.000.zip'
ZIP_SHA256 = 'fa4e35bcea62dd68befabf4bb7c2765aacd2691f51ec8ae008f5f913ef49f419'
KEY = 'gameplay/gui_new/swf/witcher3/fonts_en.redswf'


def rect_end(data, pos):
    if pos >= len(data):
        raise ValueError('Missing font bounds')
    bits = data[pos] >> 3
    end = pos + (5 + 4 * bits + 7) // 8
    if end > len(data):
        raise ValueError('Truncated font bounds')
    return end


def layout(data):
    info = audit.font_info(75, data)
    count = info['glyphs']
    base = 7 + data[4]
    unit = 4 if info['flags'] & 8 else 2
    fmt = '<I' if unit == 4 else '<H'
    off = struct.unpack_from(fmt, data, base + count * unit)[0]
    if not info['flags'] & 128 or not info['flags'] & 4:
        raise ValueError('Expected DefineFont3 wide codes and layout')
    start = base + off + 2 * count
    ascent, descent, leading = struct.unpack_from('<HHh', data, start)
    advances = list(struct.unpack_from('<' + 'h' * count, data, start + 6))
    pos = start + 6 + 2 * count
    for _ in range(count):
        pos = rect_end(data, pos)
    kern_count = struct.unpack_from('<H', data, pos)[0]
    if pos + 2 + kern_count * 6 != len(data):
        raise ValueError('Unexpected font layout length')
    info.update(ascent=ascent, descent=descent, leading=leading,
                advances=advances, kerning_count=kern_count)
    return info


def main():
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.transformPen import TransformPen
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--archive', type=Path, help='Local independently downloaded SIL release ZIP')
    args = ap.parse_args()
    out = args.out.resolve()
    if ROOT / 'build' not in out.parents or out.exists():
        raise ValueError('Fresh ignored build directory required')
    out.mkdir(parents=True)
    bundle = args.game / 'content/content0/bundles/r4gui.bundle'
    entries = [x for x in audit.entries(bundle) if x['resource'] == KEY]
    if len(entries) != 1:
        raise ValueError('Expected exactly one current EN entry')
    entry = entries[0]
    with bundle.open('rb') as f:
        f.seek(entry['offset']); packed = f.read(entry['packed'])
    if entry['codec'] not in (0, 1):
        raise ValueError('Unsupported bundle codec')
    runtime = zlib.decompress(packed) if entry['codec'] == 1 else packed
    if len(runtime) != entry['size']:
        raise ValueError('Resource length mismatch')
    (out / 'fonts_en.redswf').write_bytes(runtime)
    _, _, tags = audit.swf_tags(runtime)
    fonts = [layout(b) for c, b in tags if c == 75]
    if [(x['id'], x['flags'] & 3) for x in fonts] != [(1, 0), (3, 2), (5, 1)]:
        raise ValueError('Unexpected style bindings')
    if args.archive:
        archive = args.archive.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=45) as response:
            archive = response.read()
    zpath = out / 'GentiumBook-7.000.zip'
    if audit.sha(archive) != ZIP_SHA256:
        raise ValueError('Upstream release differs from independently verified input')
    zpath.write_bytes(archive)
    with zipfile.ZipFile(zpath) as z:
        if z.testzip() is not None:
            raise ValueError('Upstream archive CRC failure')
        for name in ('Regular', 'Bold', 'Italic'):
            file = 'GentiumBook-' + name + '.ttf'
            (out / file).write_bytes(z.read('GentiumBook-7.000/' + file))
        for file in ('OFL.txt', 'FONTLOG.txt', 'README.txt'):
            (out / file).write_bytes(z.read('GentiumBook-7.000/' + file))
    receipt = dict(status='source-preparation-only; no-converted-resource',
                   resource_key=KEY, runtime_sha256=audit.sha(runtime),
                   upstream_url=URL, upstream_zip_sha256=audit.sha(archive),
                   ofl_sha256=audit.sha((out / 'OFL.txt').read_bytes()),
                   styles=[], runtime_tags=[{'code': c, 'sha256': audit.sha(b)} for c, b in tags],
                   package_path=None, cooked=False, runtime_tested=False)
    samples = ['Roach', 'Vesemir', 'Geralt of Rivia', 'Kaer Morhen',
               'Witcher silver sword', '0123456789', 'AV To Wa',
               'Dandelion’s lute — “A tale…”', 'É Ł Œ ß æ']
    for baseline, style in zip(fonts, ('Regular', 'Italic', 'Bold')):
        path = out / ('GentiumBook-' + style + '.ttf')
        font = TTFont(path)
        cmap = font.getBestCmap()
        upem = font['head'].unitsPerEm
        glyphs = font.getGlyphSet()
        codes = baseline['codes']
        missing = sorted(set(codes) - set(cmap))
        outlines = []
        for code in codes:
            if code not in cmap:
                continue
            pen = DecomposingRecordingPen(glyphs)
            glyphs[cmap[code]].draw(TransformPen(pen, (20480/upem, 0, 0, -20480/upem, 0, 0)))
            outlines.append(dict(code=code, glyph=cmap[code],
                                 advance_20480=font['hmtx'][cmap[code]][0]*20480/upem,
                                 pen_commands=pen.value))
        prepared = out / (style.lower() + '-outline-source.json')
        prepared.write_text(json.dumps(outlines), encoding='utf-8')
        runtime_advances = dict(zip(codes, baseline['advances']))
        widths = []
        for text in samples:
            if all(ord(c) in runtime_advances and ord(c) in cmap for c in text):
                old = sum(runtime_advances[ord(c)] for c in text)/20480
                new = sum(font['hmtx'][cmap[ord(c)]][0] for c in text)/upem
                widths.append(dict(text=text, vanilla_em=old, gentium_em=new,
                                   unkerned_ratio=new/old if old else None))
        gpos = font['GPOS'].table if 'GPOS' in font else None
        features = [f.FeatureTag for f in gpos.FeatureList.FeatureRecord] if gpos else []
        receipt['styles'].append(dict(style=style, font_id=baseline['id'],
            binding=baseline['name'], flags=baseline['flags'],
            baseline_glyphs=len(codes), baseline_metrics={k:baseline[k] for k in ('ascent','descent','leading','kerning_count')},
            baseline_font_payload_sha256=baseline['payload_sha256'],
            ttf_sha256=audit.sha(path.read_bytes()), units_per_em=upem,
            source_metrics=dict(ascent=font['hhea'].ascent, descent=font['hhea'].descent,
                                line_gap=font['hhea'].lineGap, x_height=font['OS/2'].sxHeight),
            missing_baseline_codes=[f'U+{c:04X}' for c in missing],
            glyph_sources=len(outlines), outline_source_sha256=audit.sha(prepared.read_bytes()),
            digit_advances=[font['hmtx'][cmap[ord(c)]][0] for c in '0123456789'],
            gpos_features=sorted(set(features)), legacy_kern_present='kern' in font,
            widths=widths))
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt['styles'], indent=2))


if __name__ == '__main__':
    main()
