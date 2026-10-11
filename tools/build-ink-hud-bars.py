"""Private single-movie I&I/SAHUD proof; official tools, no deployment.

The author movie is intentionally unchanged. The original adapter disables
incompatible secondary drawing/split modes in memory, retaining module policy.
Compiler checks are a source-assembly regression, not a retail multi-blob test.
"""
import argparse
from collections import Counter
import configparser
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
KEY = 'gameplay/gui_new/swf/hud/hud_wolfstatbars.redswf'
MOD = 'modInkIronAdaptiveBarsTest'


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


font = load('verify-font-asset')
fallback = load('check-npc-fallback')
diagnostics = load('compare-npc-wrapper-diagnostics')
audit = font.audit


def same_movie(a, b):
    # Only official exporter metadata may be rewritten by the cooker.
    return font.movie_tags(a) == font.movie_tags(b)


def structure(data):
    chunks = font.native.chunks(data)
    if [c['class_name'] for c in chunks] != ['CSwfResource', 'CSwfTexture']:
        raise ValueError('Unexpected bars resource structure')
    if not all(c['crc_valid'] for c in chunks):
        raise ValueError('Invalid chunk CRC')
    if chunks[0]['properties']['textures']['value'] != '0100000002000000':
        raise ValueError('Expected one embedded atlas')
    _, info, pixels = font.native.texture(data)
    return chunks, info, pixels


def extract(bundle, key):
    entries = [e for e in audit.entries(bundle) if e['resource'] == key]
    if len(entries) != 1 or entries[0]['codec'] != 1:
        raise ValueError('Expected one ZLIB owner for '+key)
    e = entries[0]
    with bundle.open('rb') as stream:
        stream.seek(e['offset'])
        data = zlib.decompress(stream.read(e['packed']))
    if len(data) != e['size']:
        raise ValueError('Decompressed length differs')
    return data


def snapshot(game, settings):
    # Include every deployed source/container; no saves are read or modified.
    paths = [settings]
    for suffix in ('*.ws', '*.bundle', '*.redswf', '*.cache', '*.store', 'info.json'):
        paths.extend((game/'Mods').rglob(suffix))
    return {str(p.resolve()): fallback.sha(p) for p in sorted(set(paths))}


def compile_bridge(assembly, runtime, work, game, cfg):
    if fallback.sha(runtime/'wcc_lite.exe') != font.COMPILER_SHA:
        raise ValueError('Script compiler changed')
    before = []
    for group in ('base', 'patch'):
        for p in (assembly/group).rglob('*.ws'):
            q = work/group/p.relative_to(assembly/group)
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text(fallback.text(p), encoding='utf-8', newline='\n')
            before.append(dict(path=str(p.resolve()), sha256=fallback.sha(p)))
    hashes = {audit.sha(fallback.text(p).encode()) for p in work.rglob('*.ws')}
    required = []
    # The exact currently deployed merged inputs and affected HUD providers
    # must be represented. Non-winning full replacement files are not inputs.
    for owner, relative in [('mod0000_MergedFiles', ''),
                            ('modSeamlessAdaptiveHUD', 'local/SeamlessAdaptiveHUD'),
                            ('modFriendlyHUD', 'game/gui/hud/modules'),
                            ('modFriendlyHUD', 'fhudscripts')]:
        for p in (game/'Mods'/owner/'content/scripts'/relative).rglob('*.ws'):
            if owner == 'modFriendlyHUD' and p.name == 'hudModuleRadialMenu.ws':
                # The deployed merged winner is checked above.
                continue
            if audit.sha(fallback.text(p).encode()) not in hashes:
                raise ValueError('Source assembly differs from current HUD/merge input: '+str(p))
            required.append(dict(path=str(p.resolve()), sha256=fallback.sha(p)))
    accepted = game/'Mods/modQuietEditorialNPCColorsV4/content/scripts/local/quietEditorialNameColorsV4.ws'
    if accepted.exists() and audit.sha(fallback.text(accepted).encode()) not in hashes:
        q = work/'patch/local/quietEditorialNameColorsV4.ws'
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text(fallback.text(accepted), encoding='utf-8')
        required.append(dict(path=str(accepted.resolve()), sha256=fallback.sha(accepted)))
    extra = work/'patch/local/inkIronBarsBridge.ws'
    extra.parent.mkdir(parents=True, exist_ok=True)
    source = fallback.text(ROOT/'src/hud/inkIronBarsBridge.ws')
    results = []
    cases = [('baseline', None), ('noop', '@wrapMethod(SahSettings)\nfunction Load() { wrappedMethod(); }\n'),
             ('candidate', source)]
    for label, text in cases:
        if text is not None:
            extra.write_text(text, encoding='utf-8', newline='\n')
        output = work/label
        output.mkdir()
        cmd = [str(runtime/'wcc_lite.exe'), 'compilescripts', str(work/'base'),
               '-patch='+str(work/'patch'), '-out='+str(output)]
        p = subprocess.run(cmd, cwd=runtime, capture_output=True, timeout=60)
        log = (runtime.parent/'wcc.log').read_text(errors='replace')
        (work/(label+'.full.log')).write_text(log)
        (work/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
        errors = [s for s in log.splitlines() if '[Error][Script]' in s or '[Error][WCC]' in s]
        blob = output/'blob.rsblob'
        result = dict(label=label, command=cmd, exit_code=p.returncode, errors=errors,
            success=p.returncode == 0 and not errors and blob.exists() and blob.stat().st_size > 0
                    and 'Success! Patch scripts blob saved' in log,
            assertions=dict(diagnostics.diagnostic_counter(log, '[Error][Assert]')),
            warnings=dict(diagnostics.diagnostic_counter(log, '[Warning]')),
            blob_sha256=fallback.sha(blob) if blob.exists() else None)
        results.append(result)
        (work/'commands.json').write_text(json.dumps(results, indent=2))
        print('Script', label, result['success'], flush=True)
        if not result['success']:
            raise ValueError('Script compiler failed: '+label)
    for result in results[1:]:
        result['assertions_added'] = dict(Counter(result['assertions'])-Counter(results[0]['assertions']))
        result['assertions_removed'] = dict(Counter(results[0]['assertions'])-Counter(result['assertions']))
    if results[1]['warnings'] != results[0]['warnings']:
        raise ValueError('No-op warning regression')
    if results[1]['warnings'] != results[2]['warnings'] or results[1]['assertions'] != results[2]['assertions']:
        raise ValueError('Candidate diagnostics differ from declaration-matched no-op')
    if any(fallback.sha(Path(s['path'])) != s['sha256'] for s in before+required):
        raise ValueError('Compiler input changed')
    opaque = [m for m in cfg.sections() if cfg[m].get('Enabled') == '1'
              and (game/'Mods'/m/'content/info.json').exists()
              and json.loads((game/'Mods'/m/'content/info.json').read_text(encoding='utf-8-sig')).get('useLooseScripts') is False]
    receipt = dict(results=results, source_assembly_inputs=before, current_required_inputs=required,
                   opaque_mods_not_recompiled=opaque, scope='source-assembly regression, not retail multi-blob simulation')
    (work/'receipt.json').write_text(json.dumps(receipt, indent=2))
    return receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--settings', type=Path, required=True)
    ap.add_argument('--assembly', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--deploy', type=Path, required=True)
    a = ap.parse_args()
    out, deploy = a.out.resolve(), a.deploy.resolve()
    font.private_path(out)
    if out.exists() or deploy.exists() or ROOT/'deploy' not in deploy.parents:
        raise ValueError('Fresh ignored build/deploy directories required')
    if subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT).decode().strip() != 'ui-overhaul':
        raise ValueError('ui-overhaul branch required')
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read_string(fallback.text(a.settings))
    for owner in ('modSeamlessAdaptiveHUD', 'modFriendlyHUD', 'mod0000_MergedFiles'):
        if cfg[owner].get('Enabled') != '1':
            raise ValueError('Required current provider disabled: '+owner)
    state = snapshot(a.game, a.settings)
    out.mkdir()
    (out/'live-before.json').write_text(json.dumps(state, indent=2))
    source_bundle = ROOT/'reference/ink-and-iron-0.8/mods/modInkAndIronHUD/content/blob0.bundle'
    inputs = json.loads((ROOT/'research/ink-and-iron-0.8-audit/input-files.json').read_text())
    bundle_pin = next(r['sha256'] for r in inputs if r['path'] == 'mods/modInkAndIronHUD/content/blob0.bundle')
    if fallback.sha(source_bundle) != bundle_pin:
        raise ValueError('Canonical author container changed since audit')
    # Canonical author bundle uses codec 5; read previously audited extraction
    # and require its hash to equal the independently recorded inventory row.
    source_path = ROOT/'build/ink-and-iron-0.8-audit/payloads/modInkAndIronHUD'/KEY
    source = source_path.read_bytes()
    import csv
    rows = list(csv.DictReader((ROOT/'research/ink-and-iron-0.8-audit/resources.csv').open()))
    row = next(r for r in rows if r.get('resource') == KEY and r.get('module') == 'modInkAndIronHUD')
    if audit.sha(source) != row['sha256']:
        raise ValueError('Audited I&I source changed')
    structure(source)
    pinned = out/'author-bars.redswf'
    pinned.write_bytes(source)
    owners = []
    for bundle in (a.game/'Mods').rglob('*.bundle'):
        for e in audit.entries(bundle):
            if e['resource'] == KEY:
                owner = bundle.relative_to(a.game/'Mods').parts[0]
                if e['codec'] == 1:
                    raw = extract(bundle, KEY)
                elif e['codec'] == 0:
                    with bundle.open('rb') as stream:
                        stream.seek(e['offset'])
                        raw = stream.read(e['packed'])
                    if len(raw) != e['size']:
                        raise ValueError('Raw owner size differs')
                elif e['codec'] == 5:
                    dest = out/'owners'/owner
                    dest.mkdir(parents=True, exist_ok=True)
                    quick = a.game/'WitcherScriptMerger/Tools/QuickBMS'
                    p = subprocess.run([str(quick/'quickbms.exe'), '-Q', '-o', str(quick/'witcher3.bms'),
                                        str(bundle), str(dest)], capture_output=True, timeout=60)
                    if p.returncode:
                        raise ValueError('Current-owner extraction failed')
                    raw = (dest/KEY).read_bytes()
                    if len(raw) != e['size']:
                        raise ValueError('Owner extraction size differs')
                else:
                    raise ValueError('Unknown deployed codec')
                owners.append(dict(owner=owner, path=str(bundle.resolve()), resource_sha256=audit.sha(raw),
                                   enabled=cfg[owner].get('Enabled'), priority=cfg[owner].get('Priority')))
    loose = []
    for p in (a.game/'Mods').rglob('hud_wolfstatbars.redswf'):
        owner = p.relative_to(a.game/'Mods').parts[0]
        loose.append(dict(owner=owner, path=str(p.resolve()), resource_sha256=fallback.sha(p),
                          enabled=cfg[owner].get('Enabled'), priority=cfg[owner].get('Priority')))
    if any(o['owner'] != 'modSeamlessAdaptiveHUD' and o['enabled'] == '1' for o in owners):
        raise ValueError('Additional enabled bars owner needs review')
    if any(o['owner'] != 'modSeamlessAdaptiveHUD' and o['enabled'] == '1' for o in loose):
        raise ValueError('Additional loose bars owner needs review')
    script = compile_bridge(a.assembly.resolve(), ROOT/'build/native-npc-reproduce/runtime', out/'scripts', a.game, cfg)
    runner = ROOT/'build/npc-state-expanded'
    exe = runner/'bin/x64_RedKit/wcc_lite.exe'
    if fallback.sha(exe) != font.COMPILER_SHA:
        raise ValueError('Compiler changed')
    commands = []
    def run(label, args):
        cmd = [str(exe), *args]
        p = subprocess.run(cmd, cwd=exe.parent, capture_output=True, timeout=60)
        log = (runner/'bin/wcc.log').read_text(errors='replace')
        (out/(label+'.full.log')).write_text(log)
        (out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
        assertions = [s for s in log.splitlines() if '[Error][Assert]' in s]
        commands.append(dict(label=label, command=cmd, exit_code=p.returncode, assertions=assertions))
        (out/'commands.json').write_text(json.dumps(commands, indent=2))
        if p.returncode or any(not any(x in s for x in ('depotDirectory.cpp:11', 'soundFileLoader.cpp:101')) for s in assertions):
            raise ValueError('Official stage failed/new assertion: '+label)
        print('Resource', label, 'passed', flush=True)
        return log
    with font.mounted_input(runner, out, pinned, key=KEY) as workspace:
        run('cook', ['cook', '-platform=pc', '-mod='+str(workspace), '-outdir='+str(out/'cooked')])
        log = run('validate', ['validate', '-db='+str(out/'cooked/cook.db'), '-outdir='+str(out/'validation')])
        if 'Found 1 files to validate' not in log or 'Errors found in 0 resources:' not in log:
            raise ValueError('Single-resource validation failed')
        cooked = (out/'cooked'/KEY).read_bytes()
        _, _, pixels = structure(cooked)
        if not same_movie(source, cooked) or pixels != structure(source)[2]:
            raise ValueError('Movie contracts or atlas changed')
        dest = out/'pack-input'/KEY
        dest.parent.mkdir(parents=True)
        dest.write_bytes(cooked)
        run('pack', ['pack', '-dir='+str(out/'pack-input'), '-outdir='+str(out/'packed'), '-compression=ZLIB'])
        log = run('metadata', ['metadatastore', '-path='+str(out/'packed')])
        if 'Loaded 1 bundles with 1 entries' not in log:
            raise ValueError('Metadata inventory differs')
        if extract(out/'packed/blob0.bundle', KEY) != cooked or len(list(audit.entries(out/'packed/blob0.bundle'))) != 1:
            raise ValueError('Bundle re-extraction/scope differs')
        if KEY.replace('/', '\\').encode() not in (out/'packed/metadata.store').read_bytes():
            raise ValueError('Official metadata key missing')
    if snapshot(a.game, a.settings) != state:
        raise ValueError('Live installation changed; no package issued')
    deploy.mkdir()
    files = {'Mods/'+MOD+'/content/'+n: (out/'packed'/n).read_bytes() for n in ('blob0.bundle', 'metadata.store')}
    adapter = fallback.text(ROOT/'src/hud/inkIronBarsBridge.ws').encode('utf-8')
    files['Mods/'+MOD+'/content/scripts/local/inkIronBarsBridge.ws'] = adapter
    archive = deploy/'Ink-Iron-Adaptive-Bars-v1-private-test.zip'
    def zipper():
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
            for name in sorted(files):
                info = zipfile.ZipInfo(name, (2026, 10, 11, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, files[name])
        return buf.getvalue()
    data = zipper()
    if data != zipper():
        raise ValueError('Nondeterministic ZIP')
    archive.write_bytes(data)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or {n:z.read(n) for n in z.namelist()} != files:
            raise ValueError('ZIP routing/content differs')
    receipt = dict(resource_key=KEY, mod=MOD, author_bundle_sha256=fallback.sha(source_bundle),
        author_resource_sha256=audit.sha(source), cooked_sha256=audit.sha(cooked),
        adapter_sha256=audit.sha(adapter), owners=owners, loose_owners=loose,
        compiler_sha256=font.COMPILER_SHA, commands=commands, script_regression=script['results'],
        opaque_mods_not_recompiled=script['opaque_mods_not_recompiled'],
        bundle_sha256=fallback.sha(out/'packed/blob0.bundle'), metadata_sha256=fallback.sha(out/'packed/metadata.store'),
        zip_path=str(archive), zip_sha256=audit.sha(data), zip_bytes=len(data),
        members={n:audit.sha(b) for n,b in files.items()}, movie_tags_and_atlas_identical=True,
        chunk_crcs_valid=True, exact_reextraction=True, official_pipeline_verified=True,
        live_inputs_unchanged=True, runner_workspace_restored=True, runtime_tested=False, deployed=False,
        constraints={'hudStyle':0, 'hudMinimal':False, 'toxicMode':0})
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2))
    (deploy/'manifest.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('commands', 'script_regression')}, indent=2))


if __name__ == '__main__':
    main()
