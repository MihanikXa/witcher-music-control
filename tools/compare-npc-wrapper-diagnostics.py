"""Bounded serial compiler controls; copied source assembly, no deployment.

Compares one no-op EnemyFocus event wrapper, one no-op existing HUD wrapper
target, and the original RGB hook against a freshly compiled identical baseline.
"""
import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fallback', ROOT / 'tools/check-npc-fallback.py')
fallback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback)


def diagnostic_counter(log, marker):
    return Counter(line.split(marker, 1)[1].strip() for line in log.splitlines() if marker in line)


def make_probe_noop(source):
    """Retain diagnostic declarations/signatures, replace only known bodies.

    Deliberately bounded to this original probe, not a WitcherScript parser.
    Quoted braces are handled; this supplied source has no braces in comments.
    """
    bodies = {'QEProbeNotice': 'return;', 'QEProbePalette': 'return original;',
              'OnTick': 'var result : bool; result = wrappedMethod(timeDelta); return result;',
              'UpdateName': 'wrappedMethod(enemyName);',
              'qeprobe': 'return;'}
    pattern = re.compile(r'\bfunction\s+(\w+)\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{')
    edits = []
    names = []
    for match in pattern.finditer(source):
        name = match.group(1)
        if name not in bodies:
            raise ValueError('Unexpected probe function')
        depth, pos = 1, match.end()
        quoted = False
        escaped = False
        while depth and pos < len(source):
            char = source[pos]
            if char == '"' and not escaped:
                quoted = not quoted
            if not quoted:
                depth += (char == '{') - (char == '}')
            escaped = char == '\\' and not escaped
            pos += 1
        if depth:
            raise ValueError('Unclosed diagnostic body')
        edits.append((match.end(), pos - 1, '\n    ' + bodies[name] + '\n'))
        names.append(name)
    if sorted(names) != sorted(['QEProbeNotice', 'QEProbePalette', 'OnTick', 'OnTick', 'UpdateName', 'qeprobe']):
        raise ValueError('Exact six-function diagnostic shape required')
    for start, end, replacement in reversed(edits):
        source = source[:start] + replacement + source[end:]
    return source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--assembly', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, help='Original diagnostic source; declaration-matched no-op control')
    a = ap.parse_args()
    work, runtime = a.out.resolve(), a.runtime.resolve()
    if ROOT / 'build' not in work.parents or work.exists() or ROOT / 'build' not in runtime.parents:
        raise ValueError('Fresh build output and isolated runtime required')
    work.mkdir(parents=True)
    sources = []
    for group in ('base', 'patch'):
        for p in (a.assembly / group).rglob('*.ws'):
            q = work / group / p.relative_to(a.assembly / group)
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text(fallback.text(p), encoding='utf-8', newline='\n')
            sources.append({'path': str(p), 'sha256': fallback.sha(p)})
    temp = work / 'temp'
    temp.mkdir()
    extra = work / 'patch/local/quietEditorialDiagnostic.ws'
    extra.parent.mkdir(parents=True, exist_ok=True)
    cases = {
        'baseline': None,
        'npc_noop': '@wrapMethod(CR4HudModuleEnemyFocus)\nfunction OnTick(timeDelta : float) { var nativeResult : bool; nativeResult = wrappedMethod(timeDelta); return nativeResult; }\n',
        'hud_noop': '@wrapMethod(CR4ScriptedHud)\nfunction OnTick(timeDelta : float) { wrappedMethod(timeDelta); }\n',
        'candidate': fallback.text(ROOT / 'src/npc/quietEditorialNameColors.ws'),
    }
    if a.candidate:
        candidate = fallback.text(a.candidate)
        cases = {'baseline': None,
                 'paired_noop': make_probe_noop(candidate),
                 'candidate': candidate}
    results = []
    for label, source in cases.items():
        if source is not None:
            extra.write_text(source, encoding='utf-8', newline='\n')
        output = work / label
        output.mkdir()
        cmd = [str(runtime / 'wcc_lite.exe'), 'compilescripts', str(work / 'base'),
               '-patch=' + str(work / 'patch'), '-out=' + str(output)]
        proc = subprocess.run(cmd, cwd=runtime, env=dict(os.environ, TEMP=str(temp), TMP=str(temp)),
                              capture_output=True, timeout=60)
        (work / (label + '.stdout.log')).write_bytes(proc.stdout + proc.stderr)
        log = (runtime.parent / 'wcc.log').read_text(errors='replace')
        (work / (label + '.full.log')).write_text(log)
        errors = [s for s in log.splitlines() if '[Error][Script]' in s or '[Error][WCC]' in s]
        blob = output / 'blob.rsblob'
        result = dict(label=label, command=cmd, exit_code=proc.returncode, errors=errors,
                      success=proc.returncode == 0 and not errors and blob.exists() and
                      blob.stat().st_size > 0 and 'Success! Patch scripts blob saved' in log,
                      assertions=dict(diagnostic_counter(log, '[Error][Assert]')),
                      warnings=dict(diagnostic_counter(log, '[Warning]')),
                      blob_sha256=fallback.sha(blob) if blob.exists() else None,
                      blob_bytes=blob.stat().st_size if blob.exists() else None,
                      source_sha256=fallback.sha(extra) if source is not None else None)
        results.append(result)
        print(label, result['success'], sum(result['assertions'].values()), flush=True)
    baseline = results[0]
    for r in results[1:]:
        r['assertions_added'] = dict(Counter(r['assertions']) - Counter(baseline['assertions']))
        r['assertions_removed'] = dict(Counter(baseline['assertions']) - Counter(r['assertions']))
        r['warnings_added'] = dict(Counter(r['warnings']) - Counter(baseline['warnings']))
        r['warnings_removed'] = dict(Counter(baseline['warnings']) - Counter(r['warnings']))
    unchanged = all(fallback.sha(Path(s['path'])) == s['sha256'] for s in sources)
    receipt = dict(results=results, compiler_sha256=fallback.sha(runtime / 'wcc_lite.exe'),
                   sources=sources, source_inputs_unchanged=unchanged, deployed=False)
    (work / 'receipt.json').write_text(json.dumps(receipt, indent=2))
    if not unchanged or not all(r['success'] for r in results):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
