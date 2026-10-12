"""Stage an observable regional-only experiment; no installation or generation.

Require the existing structural audit and matching known baseline warnings.
This does not waive the strict native-equivalence gate or certify runtime loading.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from white_orchard_compare import read_bank, difference
from white_orchard_cooker import prepare, execute
from white_orchard_loading_package import verify, NATIVE_INIT, LICENSED_BANK
from white_orchard_prepare import build_path, digest
from white_orchard_state_bank_audit import audit, header


def diagnostics(folder):
    result = json.loads((folder / 'result.json').read_text())
    if result['exit_code'] not in (0, 2) or not result['expected_banks_only']:
        raise ValueError('Failed generation cannot supply a test package')
    rows = [line.split('\t') for line in (folder / 'generation.log').read_text().splitlines()
            if line.startswith('SoundBankGeneration\t')]
    if any(row[1] != 'Warning' for row in rows):
        raise ValueError('Error/fatal or unexpected diagnostic severity')
    return Counter(tuple(row[1:]) for row in rows)


def stage(redkit, baseline, baseline_project, candidate, candidate_project, root):
    root = build_path(root)
    native = redkit / 'r4data/soundbanks/Pc'
    bank = candidate / 'music_prologue.bnk'
    if digest(baseline / 'music_prologue.bnk') != LICENSED_BANK:
        raise ValueError('Not the retained licensed unmodified baseline')
    if diagnostics(baseline) != diagnostics(candidate):
        raise ValueError('New or changed warnings require review before packaging')
    b, c = read_bank(baseline / bank.name), read_bank(bank)
    hb, hc = header(b), header(c)
    if {k: v for k, v in hb.items() if k != 'hash_hex'} != {k: v for k, v in hc.items() if k != 'hash_hex'}:
        raise ValueError('Unexpected BKHD identity/metadata difference')
    if hb['project_id'] != 17637 or set(difference(b, c)['chunk_changed']) - {'BKHD', 'HIRC'}:
        raise ValueError('Unexpected bank identity or non-State chunk change')
    if digest(native / 'Init.bnk') != NATIVE_INIT:
        raise ValueError('Native Init provenance mismatch')
    prepare(redkit, root)  # Requires an absent isolated root, preserves A/B.
    proof = audit(native, baseline, candidate, baseline_project, candidate_project,
                  root / 'structural-audit.json')
    if not all(proof['checks'].values()):
        raise ValueError('Structural checks failed')
    bank_hash = digest(bank)
    inputs, output, split = [root / name for name in ('candidate-input', 'candidate-cooked', 'candidate-split')]
    inputs.mkdir(); output.mkdir()
    shutil.copyfile(bank, inputs / bank.name)
    exe = redkit / 'bin/x64_RedKit/wcc_lite.exe'
    execute(exe, root, 'candidate-cook', ['cooksounds', '-soundbanksdir=' + str(inputs) + '\\',
            '-outdir=' + str(output) + '\\', '-platform=pc_dx12', '-r4remastersounds',
            '-outsplitfile=' + str(output / 'audio-split.list')])
    cooked = verify(output / 'CookedPC/soundspc.cache', bank)
    execute(exe, root, 'candidate-split', ['splitcache', 'sounds', '-platform=pc_dx12',
            '-split=' + str(output / 'audio-split.list'), '-file=' + cooked['path'],
            '-outdir=' + str(split) + '\\'])
    readback = verify(split / 'content0/soundspc.cache', bank)
    package = root / 'packages/candidate/modWMCBankLoadingTest/content/soundspc.cache'
    package.parent.mkdir(parents=True)
    shutil.copyfile(Path(cooked['path']), package)
    if (digest(bank) != bank_hash or digest(package) != cooked['sha256'] or
            digest(native / 'Init.bnk') != NATIVE_INIT or
            any(digest(root / p) != NATIVE_INIT for p in
                ('bin/initialdata/sound/Init.bnk', 'r4data/soundbanks/Pc/Init.bnk'))):
        raise ValueError('Protected input/bootstrap/package changed')
    result = dict(bank_sha256=bank_hash, bank_header=hc, cooked=cooked,
                  native_reader=readback, package=str(package),
                  known_generation_exit_code=json.loads((candidate / 'result.json').read_text())['exit_code'],
                  warning_rows_matched_to_baseline=sum(diagnostics(candidate).values()),
                  init_in_package=False, structural_checks_passed=True,
                  ready_for_authorized_experiment=True, runtime_validated=False,
                  deployed=False, release_certified=False)
    (root / 'candidate-verified.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('redkit', 'baseline', 'baseline-project', 'candidate', 'candidate-project', 'root'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    stage(*(getattr(args, name).resolve() for name in
            ('redkit', 'baseline', 'baseline_project', 'candidate', 'candidate_project', 'root')))
