"""Remove only the v4 speculative footer-fit expression from decompiled GFx AS3.

Input must be the actual ModuleInputFeedback.as exported from the current
private HUD movie, NOT the original retail source. This produces source only,
not a compiled movie or a game-ready mod. Fail closed if FFDec restructured it.
"""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
V4_FIT = re.compile(
    r'(?m)^[ \t]*this\._canvas\.scaleX\s*=\s*this\._canvas\.scaleY\s*=\s*'
    r'this\._cachedWidth\s*>\s*0\s*&&\s*buttonsSize\s*>\s*this\._cachedWidth\s*'
    r'\?\s*this\._cachedWidth\s*/\s*buttonsSize\s*:\s*1\s*;[ \t]*\r?\n'
    r'[ \t]*buttonsSize\s*\*=\s*this\._canvas\.scaleX\s*;[ \t]*\r?\n'
)

def repair(text):
    if not re.search(r'\bclass\s+ModuleInputFeedback\b', text):
        raise ValueError('Source is not ModuleInputFeedback.as')
    patched, count = V4_FIT.subn('', text)
    if count != 1:
        raise ValueError(
            'Expected exactly one v4 footer-fit expression, found %d. '
            'Inspect the actual decompiled repositionButtons method; do not guess.' % count
        )
    return patched

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True,
                    help='FFDec-exported ModuleInputFeedback.as from current HUD root')
    ap.add_argument('--out', type=Path, required=True,
                    help='Fresh path under the ignored build/ folder')
    args = ap.parse_args()
    out = args.out.resolve()
    if out == ROOT / 'build' or (ROOT / 'build') not in out.parents:
        raise ValueError('Output must be under ignored build/')
    if out.exists():
        raise ValueError('Refusing to overwrite an existing patched source')
    source = args.source.read_text(encoding='utf-8-sig')
    patched = repair(source)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(patched, encoding='utf-8', newline='\n')
    print('Prepared single-method footer source correction:', out)
    print('No compiled GFx, ZIP or runtime validation was produced.')

if __name__ == '__main__':
    main()
