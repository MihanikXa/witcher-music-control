"""Validate the inner current movie; never write a CR2W wrapper or deploy.

All generated XML/code/media must stay in ignored build/. This is a diagnostic
probe, not an approved mod build pipeline.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INPUT = '8b5c7cf0cb0e61fd005239689e096c9c5da9e3f1aa2182f9f88c71057903a76e'
spec = importlib.util.spec_from_file_location('audit', ROOT / 'tools/audit-ui.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def semantic_xml(path):
    root = ET.parse(path).getroot()
    for node in root.iter():
        # Derived positions shift when preceding shapes shrink by three bytes.
        node.attrib.pop('fileOffset', None)
        # Only observed representation changes for zero-valued fields.
        if node.get('type') == 'MATRIX' and node.get('scaleX') == '0.0' and node.get('scaleY') == '0.0':
            node.attrib.pop('nScaleBits', None)
        if node.get('type') == 'StyleChangeRecord' and node.get('moveDeltaX') == '0' and node.get('moveDeltaY') == '0':
            node.attrib.pop('moveBits', None)
    return ET.tostring(root)

def run(command, work, label):
    result = subprocess.run(command, cwd=work, capture_output=True, timeout=60)
    (work / (label + '.log')).write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{label} failed: {result.returncode}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ffdec', type=Path, required=True)
    ap.add_argument('--resource', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    work = args.out.resolve()
    if ROOT / 'build' not in work.parents:
        raise ValueError('Output must be under workspace build/')
    work.mkdir(parents=True, exist_ok=True)
    source = args.resource.resolve()
    if digest(source) != EXPECTED_INPUT:
        raise ValueError('Current baseline hash changed; audit before updating the pin')
    offset, signature, original = audit.swf_tags(source.read_bytes())
    gfx = work / 'hud_enemyfocus.gfx'
    gfx.write_bytes(source.read_bytes()[offset:])
    jar = args.ffdec.resolve()
    java = ['java', '-jar', str(jar)]
    xml = work / 'original.xml'
    rebuilt = work / 'unchanged.gfx'
    run(java + ['-swf2xml', str(gfx), str(xml)], work, 'export')
    run(java + ['-xml2swf', str(xml), str(rebuilt)], work, 'assemble')
    _, _, assembled = audit.swf_tags(rebuilt.read_bytes())
    run(java + ['-swf2xml', str(rebuilt), str(work / 'reexport.xml')], work, 'reexport')
    # JPEXS's supported container flag chooses standard SWF for GFxExport.
    # This is not a proprietary-resource header transplant.
    root = ET.parse(xml)
    if root.getroot().get('gfx') != 'true':
        raise ValueError('Expected GFx XML')
    root.getroot().set('gfx', 'false')
    standard = work / 'standard.xml'
    root.write(standard, encoding='utf-8', xml_declaration=True)
    inputs = work / 'input'
    inputs.mkdir(exist_ok=True)
    swf = inputs / 'hud_enemyfocus.swf'
    run(java + ['-xml2swf', str(standard), str(swf)], work, 'standard-assemble')
    if len(original) != len(assembled):
        raise ValueError('Tag count changed')
    changes = [dict(index=i, before_code=a[0], after_code=b[0],
                    before_hash=audit.sha(a[1]), after_hash=audit.sha(b[1]))
               for i, (a, b) in enumerate(zip(original, assembled)) if a != b]
    # Require exact bytes for bytecode, exports, imports, text, timelines.
    critical = {12, 59, 82, 56, 76, 57, 71, 37, 39, 26, 70, 4, 5, 28, 43}
    preserved = all(a == b for a, b in zip(original, assembled)
                    if a[0] in critical or b[0] in critical)
    semantic_equal = semantic_xml(xml) == semantic_xml(work / 'reexport.xml')
    receipt = dict(resource=str(source), resource_sha256=digest(source),
                   ffdec_sha256=digest(jar), payload_offset=offset,
                   payload_signature=signature, tag_count=len(original),
                   reassembled_sha256=digest(rebuilt), changed_tags=changes,
                   critical_tags_byte_identical=preserved,
                   normalized_xml_semantically_equal=semantic_equal,
                   cr2w_import_verified=False, cook_verified=False,
                   bundle_verified=False, pipeline_verified=False,
                   zip_path=None, runtime_tested=False)
    (work / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))
    if not preserved or not semantic_equal:
        raise ValueError('Inner movie contract or semantic XML changed')

if __name__ == '__main__':
    main()
