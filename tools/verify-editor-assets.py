"""Cook existing Editor outputs in a fresh official layout; no imports/deployment.

Copies the established expanded CLI layout, mounts inputs at bin/workspace,
validates two controls, packs exactly EnemyFocus and creates official metadata.
Proprietary output remains under build. No CR2W serialization/header edits.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit-ui.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
KEY = 'gameplay/gui_new/swf/hud/hud_enemyfocus.redswf'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--layout', type=Path, required=True)
    ap.add_argument('--workspace', type=Path, required=True)
    ap.add_argument('--control-workspace', type=Path,
                    help='Read unchanged Watermark from a separate baseline project')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    if ROOT / 'build' not in out.parents or out.exists():
        raise ValueError('Fresh private build output required')
    inputs = []
    for name in ('hud_enemyfocus', 'hud_watermark'):
        rel = Path(KEY).with_name(name + '.redswf')
        workspace = args.control_workspace if name == 'hud_watermark' and args.control_workspace else args.workspace
        source = workspace / rel
        if not source.is_file():
            raise ValueError('Saved Editor resource missing; no cooker executed: ' + str(source.resolve()))
        inputs.append((rel, source))
    out.mkdir()
    for rel in ('bin/x64_RedKit', 'bin/config', 'r4data'):
        shutil.copytree(args.layout / rel, out / rel)
    for rel in ('bin/gameconf.cfg', 'bin/redscripts.ini'):
        shutil.copy2(args.layout / rel, out / rel)
    sources = []
    for rel, source in inputs:
        dest = out / 'bin/workspace' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        sources.append(dict(path=str(source.resolve()), sha256=audit.sha(source.read_bytes()),
                            bytes=source.stat().st_size, mtime_ns=source.stat().st_mtime_ns))
    exe = out / 'bin/x64_RedKit/wcc_lite.exe'
    commands = []

    def run(label, argv):
        command = [str(exe)] + argv
        result = subprocess.run(command, cwd=exe.parent, capture_output=True, timeout=60)
        (out / (label + '.stdout.log')).write_bytes(result.stdout + result.stderr)
        text = (out / 'bin/wcc.log').read_text(errors='replace')
        (out / (label + '.full.log')).write_text(text)
        commands.append(dict(label=label, command=command, exit_code=result.returncode,
                             resource_assertions=[s for s in text.splitlines() if 'diskFile.cpp:2633' in s],
                             assertion_count=text.count('[Error][Assert]')))
        if result.returncode or commands[-1]['resource_assertions']:
            raise ValueError('Command failed or emitted resource-state assertion: ' + label)
        return text

    run('cook', ['cook', '-platform=pc', '-mod=' + str(out / 'bin/workspace'),
                 '-outdir=' + str(out / 'cooked')])
    text = run('validate', ['validate', '-db=' + str(out / 'cooked/cook.db'),
                            '-outdir=' + str(out / 'validation')])
    if 'Errors found in 0 resources:' not in text:
        raise ValueError('Resource validation did not pass')
    pack_input = out / 'pack-input' / KEY
    pack_input.parent.mkdir(parents=True)
    shutil.copy2(out / 'cooked' / KEY, pack_input)
    run('pack', ['pack', '-dir=' + str(out / 'pack-input'),
                 '-outdir=' + str(out / 'packed'), '-compression=ZLIB'])
    text = run('metadata', ['metadatastore', '-path=' + str(out / 'packed')])
    if 'Loaded 1 bundles with 1 entries' not in text:
        raise ValueError('Unexpected metadata input inventory')
    bundle = out / 'packed/blob0.bundle'
    entries = list(audit.entries(bundle))
    if len(entries) != 1 or entries[0]['resource'] != KEY or entries[0]['codec'] != 1:
        raise ValueError('Unexpected bundle resource/codec')
    entry = entries[0]
    with bundle.open('rb') as f:
        f.seek(entry['offset']); raw = zlib.decompress(f.read(entry['packed']))
    if raw != pack_input.read_bytes():
        raise ValueError('Re-extracted bytes differ from cooked input')
    (out / 'reextracted.redswf').write_bytes(raw)
    metadata = out / 'packed/metadata.store'
    if not metadata.is_file() or KEY.replace('/', '\\').encode() not in metadata.read_bytes():
        raise ValueError('Official metadata did not contain expected key')
    if any(audit.sha(Path(s['path']).read_bytes()) != s['sha256'] or
           Path(s['path']).stat().st_mtime_ns != s['mtime_ns'] for s in sources):
        raise ValueError('Original Editor workspace changed')
    receipt = dict(commands=commands, sources=sources, sources_unchanged=True,
                   compiler_sha256=audit.sha(exe.read_bytes()), entry=entry,
                   bundle_sha256=audit.sha(bundle.read_bytes()),
                   metadata_sha256=audit.sha(metadata.read_bytes()),
                   reextracted_sha256=audit.sha(raw), exact_reextraction=True,
                   metadata_validation='official generator, one bundle/entry and embedded key; not a full independent store decoder',
                   editor_assertion_state='unknown', runtime_tested=False, package_path=None)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
