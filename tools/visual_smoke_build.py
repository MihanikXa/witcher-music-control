"""Build a finite UI smoke diagnostic in fresh copied REDkit context, never deploy."""
import argparse
import json
from pathlib import Path
import zipfile

import sparse_observer_build as compiler
from white_orchard_prepare import digest

SOURCE = compiler.REPO / 'src/diagnostics/wmcVisualSmoke.ws'
MEMBER = 'modWMCVisualSmoke/content/scripts/local/wmcVisualSmoke.ws'


def control_source(text):
    target = 'ShowNotification(row, 12.0, false)'
    if text.count(target) != 1:
        raise ValueError('Expected exactly one snapshot presentation')
    # Identical annotations, native queries, timer and UI API; constant payload only.
    return text.replace(target, 'ShowNotification("WMCVIS1 snapshot-control", 12.0, false)')


def build(root):
    root = compiler.prepare(root)
    baseline = compiler.compile_one(root, 'baseline')
    if not baseline['compiled']:
        raise RuntimeError('Baseline compile failed; evidence retained')
    original = compiler.SOURCE
    try:
        control = root / 'visual-control.ws'
        control.write_text(control_source(SOURCE.read_text(encoding='utf-8')), encoding='utf-8')
        compiler.SOURCE = control
        matched = compiler.compile_one(root, 'matched-control', include_observer=True)
        compiler.SOURCE = SOURCE
        candidate = compiler.compile_one(root, 'candidate', include_observer=True)
    finally:
        compiler.SOURCE = original
    proof = dict(schema=1, baseline=baseline, matched_control=matched, candidate=candidate,
                 matched_diagnostics=candidate['diagnostics'] == matched['diagnostics'],
                 installed=False, retail_validated=False, source_sha256=digest(SOURCE))
    # Recheck all original copied compiler/source inputs against their installed inputs.
    pins = json.loads((root/'inputs.json').read_text(encoding='utf-8'))['inputs']
    proof['installed_inputs_unchanged'] = all(digest(Path(p['source'])) == p['sha256'] for p in pins)
    ready = (matched['compiled'] and candidate['compiled'] and proof['matched_diagnostics']
             and proof['installed_inputs_unchanged'])
    proof['ready_for_optional_manual_test'] = ready
    if ready:
        archive = root/'manual/WMC Visual Smoke - Diagnostic.zip'
        archive.parent.mkdir()
        with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(MEMBER, SOURCE.read_bytes())
        with zipfile.ZipFile(archive) as z:
            if z.namelist() != [MEMBER] or z.read(MEMBER) != SOURCE.read_bytes():
                raise ValueError('Archive readback mismatch')
        proof.update(archive_sha256=digest(archive), archive_member=MEMBER)
    (root/'visual-proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    if not ready:
        raise RuntimeError('Compile/control/preservation gate failed; no package')
    return proof


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, type=Path)
    args = p.parse_args()
    result = build(args.root)
    print(json.dumps({k:v for k,v in result.items() if k not in ('baseline','matched_control','candidate')}, indent=2))
