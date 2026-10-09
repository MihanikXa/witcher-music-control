"""Compile read-only copies of the enabled profile with an additive NPC hook.

No staging/deployment/merged-script writes. A failing baseline or candidate
prohibits packaging. Source dumps and compiler outputs stay in ignored build.
"""
import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def text(p):
    b = p.read_bytes()
    return b.decode('utf-16' if b.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--settings', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    runtime = args.runtime.resolve()
    if ROOT / 'build' not in runtime.parents or not (runtime / 'wcc_lite.exe').is_file():
        raise ValueError('Use an already isolated runtime under workspace build/')
    work = args.out.resolve()
    if ROOT / 'build' not in work.parents or work.exists():
        raise ValueError('Use a fresh workspace build directory')
    work.mkdir(parents=True)
    settings_hash = sha(args.settings)
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read_string(text(args.settings))
    base = work / 'base'
    patch = work / 'patch'
    patch.mkdir()
    temp = work / 'temp'
    temp.mkdir()
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp))
    sources = []
    winners = {}

    def copy(p, q, owner):
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text(text(p), encoding='utf-8')
        sources.append(dict(path=str(p), sha256=sha(p), owner=owner))

    vanilla = args.game / 'content/content0/scripts'
    for p in vanilla.rglob('*.ws'):
        copy(p, base / p.relative_to(vanilla), 'vanilla')
    opaque = []
    mods = sorted((s for s in cfg.sections() if cfg[s].get('Enabled') == '1'),
                  key=lambda s: int(cfg[s].get('Priority', '999999')))
    for mod in mods:
        content = args.game / 'Mods' / mod / 'content'
        info = content / 'info.json'
        if info.exists() and json.loads(info.read_text(encoding='utf-8-sig')).get('useLooseScripts') is False:
            opaque.append(mod)
        script_root = content / 'scripts'
        for p in script_root.rglob('*.ws'):
            rel = p.relative_to(script_root)
            key = rel.as_posix().lower()
            if (vanilla / rel).exists():
                if key in winners:
                    continue
                winners[key] = mod
                copy(p, base / rel, mod)
            else:
                copy(p, patch / mod / rel, mod)

    results = []
    for label in ['baseline', 'candidate']:
        if label == 'candidate':
            copy(ROOT / 'src/npc/quietEditorialNameColors.ws',
                 patch / 'modQuietEditorialNPCColors/local/quietEditorialNameColors.ws', 'original-candidate')
        output = work / label
        output.mkdir()
        cmd = [str(runtime / 'wcc_lite.exe'), 'compilescripts', str(base),
               '-patch=' + str(patch), '-out=' + str(output)]
        proc = subprocess.run(cmd, cwd=runtime, env=env, capture_output=True, timeout=60)
        (work / (label + '.stdout.log')).write_bytes(proc.stdout + proc.stderr)
        full_log = runtime.parent / 'wcc.log'
        log = full_log.read_text(errors='replace') if full_log.exists() else ''
        (work / (label + '.full.log')).write_text(log)
        errors = [line for line in log.splitlines() if '[Error][Script]' in line or '[Error][WCC]' in line]
        passed = proc.returncode == 0 and 'Success! Patch scripts blob saved' in log and (output / 'blob.rsblob').is_file()
        results.append(dict(label=label, command=cmd, exit_code=proc.returncode,
                            compiler_pass=passed, errors=errors,
                            output_files=[dict(name=p.name, sha256=sha(p)) for p in output.iterdir() if p.is_file()]))
        if sha(args.settings) != settings_hash:
            raise RuntimeError('Settings changed during read-only validation; do not package')
    receipt = dict(settings_sha256=settings_hash, compiler_sha256=sha(runtime / 'wcc_lite.exe'),
                   sources=sources, whole_file_winners=winners, opaque_mods=opaque,
                   results=results, packaging_allowed=all(r['compiler_pass'] for r in results) and not opaque,
                   deployed=False, zip_path=None)
    (work / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(dict(results=results, opaque_mods=opaque, packaging_allowed=receipt['packaging_allowed']), indent=2))
    raise SystemExit(0 if receipt['packaging_allowed'] else 2)

if __name__ == '__main__':
    main()
