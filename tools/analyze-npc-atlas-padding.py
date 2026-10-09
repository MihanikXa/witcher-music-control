"""Classify atlas differences against subimage sampling footprints, read-only.

Nearest/bilinear clipped sampling is a stated model, not a captured GPU trace.
No reconstructed pixels, proprietary XML or SWF are emitted into Git.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('native', Path(__file__).with_name('compare-native-npc.py'))
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def distance(x, y, rect):
    x1, y1, x2, y2 = rect
    return max(x1 - x, x - (x2 - 1), y1 - y, y - (y2 - 1), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vanilla', type=Path, required=True)
    ap.add_argument('--cooked', type=Path, required=True)
    ap.add_argument('--native-xml', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    if root / 'build' not in a.out.resolve().parents:
        raise ValueError('Write receipts only under ignored build/')
    b, c = a.vanilla.read_bytes(), a.cooked.read_bytes()
    _, bt, bp = native.texture(b)
    _, ct, cp = native.texture(c)
    if (bt['width'], bt['height']) != (ct['width'], ct['height']):
        raise ValueError('Atlas dimensions differ')
    w, h = bt['width'], bt['height']
    rectangles = {r[0]: r[2:] for code, data in native.audit.swf_tags(b)[2]
                  if code == 1008 for r in [struct.unpack('<6H', data)]}
    p, q = native.bc3(bp, w, h), native.bc3(cp, w, h)
    hist = Counter()
    alpha_diffs = 0
    transparent_rgb_diffs = 0
    for i, (old, new) in enumerate(zip(p, q)):
        alpha_diffs += old[3] != new[3]
        transparent_rgb_diffs += old[3] == new[3] == 0 and old[:3] != new[:3]
        if old[3] != new[3] or ((old[3] or new[3]) and old[:3] != new[:3]):
            d = min(distance(i % w, i // w, r) for r in rectangles.values())
            hist[d] += 1
    fills = [dict(bitmap=int(x.get('bitmapId')), type=int(x.get('fillStyleType')))
             for x in ET.parse(a.native_xml).getroot().iter()
             if x.get('bitmapId') and x.get('bitmapId') != '65535']
    receipt = dict(inputs=[dict(path=str(p.resolve()), sha256=native.audit.sha(p.read_bytes()))
                           for p in (a.vanilla, a.cooked, a.native_xml)],
                   mip_count=bt['mip_count'], fill_references=fills,
                   all_real_bitmap_references_use_subimages=all(f['bitmap'] in rectangles for f in fills),
                   all_real_bitmap_fills_are_clipped=all(f['type'] in (65, 67) for f in fills),
                   alpha_pixel_differences=alpha_diffs,
                   transparent_rgb_pixel_differences=transparent_rgb_diffs,
                   visible_pixel_difference_distances=dict(sorted(hist.items())),
                   clipped_nearest_or_bilinear_model_unaffected=not any(d <= 1 for d in hist),
                   renderer_sampler_state_verified=False, runtime_tested=False)
    a.out.write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
