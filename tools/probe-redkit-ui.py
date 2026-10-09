"""Reproduce the isolated official importer/cooker diagnostic, with no ZIP.

Uses probe-enemyfocus.py output or the installed native authoring SWF. Copies
official installed tools/data only into ignored build/. A successful subprocess
or cook is NOT a pipeline pass. No package operation is implemented.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KEY = Path('gameplay/gui_new/swf/hud/hud_enemyfocus.redswf')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--redkit', type=Path, required=True)
    ap.add_argument('--probe', type=Path, help='Previous inner-movie probe directory')
    ap.add_argument('--native', action='store_true', help='Import unchanged installed authoring SWF instead')
    ap.add_argument('--resource', type=Path, help='Required runtime baseline when using --native')
    ap.add_argument('--settings-directory', type=Path, required=True,
                    help='Read-only settings/saves directory to fingerprint before and after')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    def snapshot():
        return {str(p): dict(sha256=sha(p), mtime_ns=p.stat().st_mtime_ns)
                for p in args.settings_directory.rglob('*') if p.is_file()}
    settings_before = snapshot()
    kit, work = args.redkit.resolve(), args.out.resolve()
    if args.native:
        if not args.resource:
            ap.error('--native requires --resource')
        original = args.resource.resolve()
    elif args.probe:
        probe = args.probe.resolve()
        original = Path(json.loads((probe / 'receipt.json').read_text())['resource'])
    else:
        ap.error('Provide --native --resource or --probe')
    if ROOT / 'build' not in work.parents or work.exists():
        raise ValueError('Use a fresh directory under workspace build/')
    runtime = work / 'runtime'
    runtime.mkdir(parents=True)
    sources = []

    def copy(p, q):
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
        sources.append(dict(path=str(p), sha256=sha(p), output=str(q)))

    for p in (kit / 'bin/x64_RedKit').iterdir():
        if p.suffix.lower() == '.dll' or p.name == 'wcc_lite.exe':
            copy(p, runtime / p.name)
    for folder, target in [('bin/config', 'config'), ('bin/tools/GFx4', 'tools/GFx4')]:
        for p in (kit / folder).rglob('*'):
            if p.is_file():
                copy(p, work / target / p.relative_to(kit / folder))
    for p in (kit / 'r4data').glob('staticshader*.cache'):
        copy(p, work / 'data' / p.name)
    for p in (kit / 'r4data/gameplay/globals').glob('*.csv'):
        copy(p, work / 'data/gameplay/globals' / p.name)
    for rel in ['soundbanks/pc/Init.bnk', 'game/dlctable.csv', 'dep.cache',
                'engine/textures/texturegroups.xml']:
        copy(kit / 'r4data' / rel, work / 'data' / rel)
    # Config paths are relative to wcc's root (the parent's parent of runtime).
    data = work.name + '/data/'
    (work / 'gameconf.cfg').write_text('r4 {\n title "The Witcher 3"\n'
        f' data "{data}"\n bundle "bundles"\n config "config"\n'
        f' scripts "{data}/scripts"\n splash "splashscreen.bmp"\n'
        ' gameClass "CR4Game"\n playerClass "CR4Player"\n'
        ' telemetryClass "CR4TelemetryScriptProxy"\n'
        ' cameraDirClassName "CR4CameraDirector"\n}\n')
    temp = work / 'temp'
    temp.mkdir()
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp))
    commands = []
    if args.native:
        input_dir = work / 'input'
        copy(kit / 'r4data' / KEY.with_suffix('.swf'), input_dir / 'hud_enemyfocus.swf')
    else:
        input_dir = probe / 'input'

    def wcc(label, argv):
        cmd = [str(runtime / 'wcc_lite.exe')] + argv
        result = subprocess.run(cmd, cwd=runtime, env=env, capture_output=True, timeout=60)
        (work / (label + '.stdout.log')).write_bytes(result.stdout + result.stderr)
        log = work / 'wcc.log'
        if log.exists():
            shutil.copyfile(log, work / (label + '.full.log'))
        log_text = (work / (label + '.full.log')).read_text(errors='replace') if log.exists() else ''
        commands.append(dict(command=cmd, cwd=str(runtime), exit_code=result.returncode,
                             assertions=[line for line in log_text.splitlines() if '[Error][Assert]' in line]))
        return result.returncode

    wcc('help-import', ['help', 'swfimport'])
    wcc('import', ['swfimport', '-fromAbsPath=' + str(input_dir),
                   '-toDepotPath=gameplay/gui_new/swf/hud'])
    imported = work / 'workspace' / KEY
    cooked = work / 'cooked' / KEY
    if imported.is_file():
        wcc('cook', ['cook', '-platform=pc', '-mod=' + str(work / 'workspace'),
                     '-outdir=' + str(work / 'cooked')])
        if cooked.is_file():
            wcc('validate', ['validate', '-db=' + str(work / 'cooked/cook.db'),
                             '-outdir=' + str(work / 'validation')])
    # Conservative observed-contract screen, not a complete CR2W decoder.
    texture_type = b'array:2,0,handle:CSwfTexture'
    before = texture_type in original.read_bytes()
    after = cooked.is_file() and texture_type in cooked.read_bytes()
    receipt = dict(source_route='native-authoring-swf' if args.native else 'runtime-reconstruction',
        inputs=sources, commands=commands,
        original_sha256=sha(original), imported_sha256=sha(imported) if imported.exists() else None,
        cooked_sha256=sha(cooked) if cooked.exists() else None,
        vanilla_texture_array_type_present=before, cooked_texture_array_type_present=after,
        rendering_dependency_gate=bool(before and after), pipeline_verified=False,
        zip_path=None, reason='Full rendering contracts and assertion-free import are not verified; no packaging permitted.')
    receipt['settings_directory_unchanged'] = settings_before == snapshot()
    (work / 'settings-before.json').write_text(json.dumps(settings_before, indent=2))
    (work / 'official-receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k: v for k, v in receipt.items() if k not in ['inputs', 'commands']}, indent=2))
    raise SystemExit(2)  # Deliberately fail closed: this is not a mod builder.

if __name__ == '__main__':
    main()
