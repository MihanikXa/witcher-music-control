"""Controlled official SWF imports in fresh, physically isolated REDkit layouts.

No assertion suppression, live tool invocation, junctions, installation or ZIP.
Minimal and expanded bootstrap are separate cases, not a claim of full depot
equivalence. All official files are copied; receipts record unchanged inputs.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MOVIES = ('hud_enemyfocus', 'hud_crosshair', 'hud_watermark')
KEY_DIR = Path('gameplay/gui_new/swf/hud')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot(folder):
    return {str(p): [p.stat().st_size, p.stat().st_mtime_ns, sha(p)]
            for p in folder.rglob('*') if p.is_file()}


def diagnostics(text):
    lines = text.splitlines()
    assertions = [s for s in lines if '[Error][Assert]' in s]
    return dict(assertion_sites=dict(Counter(s.split('dev\\src\\', 1)[-1].split(']')[0]
                                            for s in assertions)),
                resource_assertions=[s for s in assertions if 'diskFile.cpp:2633' in s],
                depot_assertions=[s for s in assertions if 'depotDirectory.cpp' in s],
                overwrite_cancelled='overwriting is cancelled' in text,
                script_errors=[s for s in lines if '[Error][Script]' in s],
                error_count=sum('[Error]' in s for s in lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--redkit', type=Path, required=True)
    ap.add_argument('--settings-directory', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--bootstrap', choices=('minimal', 'expanded'), required=True)
    ap.add_argument('--attach-depots', action='store_true',
                    help='Use observed current WCC startup selectors with local project/uncook roots')
    ap.add_argument('--resave-control', action='store_true',
                    help='Compare fresh import with official loaded-resource resave, never accept the assertion')
    a = ap.parse_args()
    if a.resave_control and not a.attach_depots:
        ap.error('--resave-control requires explicit --attach-depots')
    kit, work = a.redkit.resolve(), a.out.resolve()
    if ROOT / 'build' not in work.parents or work.exists():
        raise ValueError('Use a fresh directory under ignored build/')
    before = snapshot(a.settings_directory)
    runtime = work / 'bin/x64_RedKit'
    runtime.mkdir(parents=True)
    (work / 'settings-before.json').write_text(json.dumps(before, indent=2))
    ledger = []

    def copy(p, q):
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
        ledger.append(dict(source=str(p), sha256=sha(p), bytes=p.stat().st_size,
                           mtime_ns=p.stat().st_mtime_ns, local=str(q)))

    def tree(source, dest):
        for p in source.rglob('*'):
            if p.is_file():
                copy(p, dest / p.relative_to(source))
        print('Copied', source.name, flush=True)

    for p in (kit / 'bin/x64_RedKit').iterdir():
        if p.suffix.lower() == '.dll' or p.name == 'wcc_lite.exe':
            copy(p, runtime / p.name)
    for rel in ('config', 'tools/GFx4'):
        tree(kit / 'bin' / rel, work / 'bin' / rel)
    for rel in ('gameconf.cfg', 'redscripts.ini'):
        copy(kit / 'bin' / rel, work / 'bin' / rel)
    data = work / 'r4data'
    for p in (kit / 'r4data').glob('staticshader*.cache'):
        copy(p, data / p.name)
    for rel in ('dep.cache', 'game/dlctable.csv', 'engine/textures/texturegroups.xml', 'soundbanks/pc/Init.bnk'):
        copy(kit / 'r4data' / rel, data / rel)
    tree(kit / 'r4data/gameplay/globals', data / 'gameplay/globals')
    if a.bootstrap == 'expanded':
        for rel in ('engine', 'game', 'scripts', 'soundbanks/pc'):
            tree(kit / 'r4data' / rel, data / rel)
        for p in (kit / 'r4data/gameplay/gui_new').rglob('*.xml'):
            copy(p, data / p.relative_to(kit / 'r4data'))
        for rel in ('x64.release.redscripts', 'dep.cache.editor', 'startupexclusives.xml',
                    'LocalEditorStringDataBaseW3_UTF8.db'):
            copy(kit / 'r4data' / rel, data / rel)
    for name in MOVIES:
        copy(kit / 'r4data' / KEY_DIR / (name + '.swf'), work / 'input' / (name + '.swf'))
    temp = work / 'temp'
    temp.mkdir()
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp))
    commands = []
    startup_args = []
    if a.attach_depots:
        for key in (b'-uncookDir\0', b'-workspaceDir\0'):
            if key not in (runtime / 'wcc_lite.exe').read_bytes():
                raise ValueError('Current binary no longer contains the observed startup selectors')
        uncook, project = work / 'uncook', work / 'project'
        uncook.mkdir()
        project.mkdir()
        startup_args = ['-uncookDir', str(uncook) + '\\', '-workspaceDir', str(project) + '\\']

    def run(label, args):
        cmd = [str(runtime / 'wcc_lite.exe')] + args + startup_args
        result = subprocess.run(cmd, cwd=runtime, env=env, capture_output=True, timeout=60)
        (work / (label + '.stdout.log')).write_bytes(result.stdout + result.stderr)
        shutil.copyfile(runtime.parent / 'wcc.log', work / (label + '.full.log'))
        text = (work / (label + '.full.log')).read_text(errors='replace')
        record = dict(label=label, command=cmd, exit_code=result.returncode,
                      log_sha256=sha(work / (label + '.full.log')), diagnostics=diagnostics(text))
        commands.append(record)
        print(json.dumps(record), flush=True)

    run('help', ['help', 'swfimport'])
    run('import', ['swfimport', '-fromAbsPath=' + str(work / 'input'),
                   '-toDepotPath=' + str(KEY_DIR)])
    imported = []
    for name in MOVIES:
        found = list(work.rglob(name + '.redswf'))
        if len(found) != 1:
            raise ValueError(f'Expected exactly one fresh import of {name}: {found}')
        imported.append(found[0])
    workspace = imported[0].parents[4]
    if a.resave_control:
        resaved = work / 'resaved'
        run('resave', ['resave', '-tmpdir=' + str(resaved), '-path=' + str(KEY_DIR),
                       '-ext=redswf', '-ignorefileversion'])
        if len(list(resaved.rglob('*.redswf'))) == len(MOVIES):
            workspace = resaved
    run('cook', ['cook', '-platform=pc', '-mod=' + str(workspace), '-outdir=' + str(work / 'cooked')])
    run('validate', ['validate', '-db=' + str(work / 'cooked/cook.db'), '-outdir=' + str(work / 'validation')])
    inputs_unchanged = all(p['sha256'] == sha(Path(p['source'])) and
                           p['mtime_ns'] == Path(p['source']).stat().st_mtime_ns for p in ledger)
    (work / 'inputs.json').write_text(json.dumps(ledger, indent=2))
    outputs = [dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p))
               for p in imported + list((work / 'cooked').rglob('*.redswf'))]
    receipt = dict(bootstrap=a.bootstrap, official_layout=True, complete_depot=False,
                   explicit_depot_selectors=a.attach_depots,
                   inputs_ledger_sha256=sha(work / 'inputs.json'), commands=commands, outputs=outputs,
                   installed_inputs_unchanged=inputs_unchanged,
                   documents_unchanged=before == snapshot(a.settings_directory),
                   pipeline_verified=False, zip_path=None)
    (work / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    if not inputs_unchanged or not receipt['documents_unchanged']:
        raise RuntimeError('Protected file drift: stop')
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    main()
