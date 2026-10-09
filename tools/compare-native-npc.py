"""Read-only observed-format comparison, never a CR2W writer or build gate.

Limited to the installed v164 NPC resource's two chunks. Table/export layout
is cross-checked against WolvenKit-7 CR2WExport.cs; that older reader does not
support v164. Do not generalize this inspector to a supported v164 serializer.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import zlib

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit-ui.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def chunks(data):
    if len(data) < 160 or data[:4] != b'CR2W' or struct.unpack_from('<I', data, 4)[0] != 164:
        raise ValueError('Expected observed current CR2W v164')
    tables = [struct.unpack_from('<III', data, 40 + i * 12) for i in range(10)]
    so, ss, _ = tables[0]
    no, ns, _ = tables[1]
    eo, es, _ = tables[4]
    if so + ss > len(data) or no + ns * 8 > len(data) or eo + es * 24 > len(data):
        raise ValueError('Invalid table bounds')
    names = []
    for i in range(ns):
        offset, _ = struct.unpack_from('<II', data, no + i * 8)
        start = so + offset
        names.append(data[start:data.index(0, start, so + ss)].decode())
    result = []
    for i in range(es):
        cls, flags, parent, size, offset, template, crc = struct.unpack_from('<HHIIIII', data, eo + i * 24)
        if offset + size > len(data) or data[offset] != 0:
            raise ValueError('Invalid chunk bounds/preamble')
        pos = offset + 1
        props = {}
        while True:
            name = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            if not name:
                break
            typ, length = struct.unpack_from('<HI', data, pos)
            pos += 6
            if length < 4 or pos + length - 4 > offset + size:
                raise ValueError('Invalid property bounds')
            value = data[pos:pos + length - 4]
            pos += length - 4
            kind = names[typ]
            if kind == 'Uint32':
                value = struct.unpack('<I', value)[0]
            elif kind in ('CName', 'ETextureCompression'):
                value = names[struct.unpack('<H', value)[0]]
            elif kind == 'String':
                # Only the observed short ANSI linkage strings, not a generic
                # REDengine string serializer.
                if not value or value[0] & 0xc0 != 0x80 or len(value) != (value[0] & 0x3f) + 1:
                    raise ValueError('Unsupported linkage string encoding')
                value = value[1:].decode('ascii')
            else:
                value = value.hex()
            props[names[name]] = dict(type=kind, value=value)
        result.append(dict(class_name=names[cls], flags=flags, parent=parent,
                           size=size, offset=offset, properties=props,
                           crc_valid=zlib.crc32(data[offset:offset + size]) == crc,
                           tail=data[pos:offset + size]))
    return result


def texture(data):
    cs = chunks(data)
    if [c['class_name'] for c in cs] != ['CSwfResource', 'CSwfTexture']:
        raise ValueError('Expected exactly resource + embedded texture')
    t = cs[1]
    # Observed current GUIWithAlpha single embedded mip metadata, not a writer.
    fields = struct.unpack_from('<7I', t['tail'])
    resident, count, width, height, pitch, size, alignment = fields
    pixels = t['tail'][28:]
    if count != 1 or resident != 0 or size != len(pixels) or size != ((width + 3) // 4) * ((height + 3) // 4) * 16:
        raise ValueError('Unsupported/incomplete embedded DXT5 mip contract')
    return cs, dict(resident=resident, mip_count=count, width=width, height=height,
                   pitch=pitch, bytes=size, alignment=alignment, sha256=audit.sha(pixels)), pixels


def bc3(data, width, height):
    """Decode BC3 for measured pixel differences; no image files are written."""
    if width <= 0 or height <= 0 or len(data) != ((width + 3) // 4) * ((height + 3) // 4) * 16:
        raise ValueError('Invalid BC3 dimensions/data length')
    out = [[0, 0, 0, 0] for _ in range(width * height)]
    def rgb565(v):
        r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
        return [(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)]
    pos = 0
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            a0, a1 = data[pos:pos + 2]
            alphas = [a0, a1]
            if a0 > a1:
                alphas += [((7 - i) * a0 + i * a1) // 7 for i in range(1, 7)]
            else:
                alphas += [((5 - i) * a0 + i * a1) // 5 for i in range(1, 5)] + [0, 255]
            abits = int.from_bytes(data[pos + 2:pos + 8], 'little')
            c0, c1, bits = struct.unpack_from('<HHI', data, pos + 8)
            colors = [rgb565(c0), rgb565(c1)]
            colors += [[(2 * colors[0][i] + colors[1][i]) // 3 for i in range(3)],
                       [(colors[0][i] + 2 * colors[1][i]) // 3 for i in range(3)]]
            for n in range(16):
                xx, yy = x + n % 4, y + n // 4
                if xx < width and yy < height:
                    out[yy * width + xx] = colors[(bits >> (n * 2)) & 3] + [alphas[(abits >> (n * 3)) & 7]]
            pos += 16
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--native', type=Path, required=True)
    ap.add_argument('--vanilla', type=Path, required=True)
    ap.add_argument('--cooked', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    if root / 'build' not in a.out.resolve().parents:
        raise ValueError('Write receipts only under ignored build/')
    native, vanilla, cooked = [p.read_bytes() for p in (a.native, a.vanilla, a.cooked)]
    tags = [audit.swf_tags(b)[2] for b in (native, vanilla, cooked)]
    excluded = {36, 1000, 1008, 1009}
    critical = [[(c, b) for c, b in group if c not in excluded] for group in tags]
    bitmaps = []
    for c, b in tags[0]:
        if c == 36:
            char, fmt, width, height = struct.unpack_from('<HBHH', b)
            pixels = zlib.decompress(b[7:])
            if fmt != 5 or len(pixels) != width * height * 4:
                raise ValueError('Unexpected native lossless bitmap')
            bitmaps.append(dict(character=char, format=fmt, width=width, height=height,
                                decoded_sha256=audit.sha(pixels)))
    before_chunks, before, bp = texture(vanilla)
    after_chunks, after, cp = texture(cooked)
    bpx, cpx = bc3(bp, before['width'], before['height']), bc3(cp, after['width'], after['height'])
    if (before['width'], before['height']) != (after['width'], after['height']):
        raise ValueError('Atlas dimensions differ')
    visible_different = sum(b[3] != c[3] or ((b[3] or c[3]) and b[:3] != c[:3])
                            for b, c in zip(bpx, cpx))
    transparent_rgb_different = sum(b[3] == c[3] == 0 and b[:3] != c[:3]
                                    for b, c in zip(bpx, cpx))
    rectangles = [struct.unpack('<6H', b) for c, b in tags[1] if c == 1008]
    stats = []
    for char, image, x1, y1, x2, y2 in rectangles:
        differences = []
        for y in range(y1, y2):
            for x in range(x1, x2):
                i = y * before['width'] + x
                # RGB of fully transparent pixels cannot affect this image.
                differences += [abs(bpx[i][3] - cpx[i][3])]
                if bpx[i][3] or cpx[i][3]:
                    differences += [abs(bpx[i][j] - cpx[i][j]) for j in range(3)]
        border_differences = 0
        for y in range(max(0, y1 - 1), min(before['height'], y2 + 1)):
            for x in range(max(0, x1 - 1), min(before['width'], x2 + 1)):
                i = y * before['width'] + x
                b, c = bpx[i], cpx[i]
                border_differences += bool(b[3] != c[3] or ((b[3] or c[3]) and b[:3] != c[:3]))
        stats.append(dict(character=char, rectangle=[x1, y1, x2, y2],
                          visible_differences_including_one_pixel_border=border_differences,
                          max_channel_difference=max(differences),
                          mean_channel_difference=sum(differences) / len(differences)))
    def metadata(cs):
        return [{k: v for k, v in c.items() if k != 'tail'} for c in cs]
    def movie_header(data):
        offset, _, _ = audit.swf_tags(data)
        raw = data[offset:]
        body = zlib.decompress(raw[8:])
        rect_size = (5 + 4 * (body[0] >> 3) + 7) // 8
        return raw[3], body[:rect_size + 4]
    def atlas_linkage_matches(cs, movie_tags):
        images = [b for code, b in movie_tags if code == 1009]
        if len(images) != 1:
            return False
        # Observed external image layout: export-name length at byte 10,
        # then file-name length and bytes. Both names are short ASCII.
        image = images[0]
        name_pos = 11 + image[10]
        length = image[name_pos]
        name = image[name_pos + 1:name_pos + 1 + length].decode('ascii')
        return name == cs[1]['properties']['linkageName']['value']
    receipt = dict(inputs=[dict(path=str(p.resolve()), sha256=audit.sha(b), bytes=len(b))
                           for p, b in zip((a.native, a.vanilla, a.cooked), (native, vanilla, cooked))],
                   native_bitmaps=bitmaps, tag_counts=list(map(len, tags)),
                   frame_rect_rate_count_version_equal=movie_header(native) == movie_header(vanilla) == movie_header(cooked),
                   native_nonimage_tags_byte_identical=critical[0] == critical[1],
                   cooked_nonimage_tags_byte_identical=critical[1] == critical[2],
                   atlas_placements_byte_identical=[b for c, b in tags[1] if c == 1008] == [b for c, b in tags[2] if c == 1008],
                   vanilla_atlas_linkage_matches=atlas_linkage_matches(before_chunks, tags[1]),
                   cooked_atlas_linkage_matches=atlas_linkage_matches(after_chunks, tags[2]),
                   vanilla_chunks=metadata(before_chunks), cooked_chunks=metadata(after_chunks),
                   vanilla_texture=before, cooked_texture=after, atlas_pixel_differences=stats,
                   full_atlas_visible_pixel_differences=visible_different,
                   full_atlas_transparent_rgb_differences=transparent_rgb_different,
                   pipeline_verified=False, runtime_tested=False, zip_path=None)
    a.out.write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('inputs', 'vanilla_chunks', 'cooked_chunks', 'native_bitmaps')}, indent=2))


if __name__ == '__main__':
    main()
