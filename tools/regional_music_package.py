"""Guarded regional-only native cooker/ZIP staging; never installs or launches."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile

from regional_music_cache import verify_bytes
from white_orchard_candidate_package import diagnostics
from white_orchard_cooker import prepare, execute
from white_orchard_loading_package import NATIVE_INIT
from white_orchard_prepare import build_path, digest


def require_proofs(spec, manifest_hash, proof, bank_hash, source_hash, playback):
    decoded = proof.get('decoded_fields', {})
    preflight = proof.get('bank_preflight', {})
    if (not proof.get('passed') or not decoded.get('passed') or not preflight.get('passed')
            or proof.get('manifest_sha256') != manifest_hash
            or proof.get('candidate_music_sha256') != source_hash
            or decoded.get('candidate_sha256') != bank_hash
            or preflight.get('candidate_sha256') != bank_hash
            or not decoded.get('global_generated_data_exact')
            or not decoded.get('paired_generated_media_exact')
            or proof.get('complete_work_units') != 1508
            or not proof.get('original_audio_unchanged')
            or not proof.get('original_nonmusic_units_unchanged')
            or not proof.get('global_definitions_unchanged')):
        raise ValueError('Missing/stale independent full source/decoded/media/global proof')
    # This first package policy is deliberately bounded to the measured NML
    # pilot, rather than granting playback approval to arbitrary future regions.
    approved = {'{48810350-DE09-4F69-B3DA-FCF4667EF177}', '{958962C3-1AC8-4C75-939C-B5EBEC3C75DD}',
                '{E5564ADB-9A93-4E6A-8D72-DE209E1A1A2D}', '{FA35E341-DB95-427A-BC50-EC2DD414DA4C}'}
    if spec['region'] != 'music_nomansgrad' or spec['state_scopes'] or set(spec['static_targets']) != approved or len(spec['static_targets']) != 4:
        raise ValueError('Unreviewed regional packaging policy')
    parents = {'719937819': 193134718, '946096996': 193134718,
               '132074504': 432285193, '568231384': 432285193}
    records = decoded.get('records', {})
    if (set(records) != set(parents) or decoded['paired_generated_media_exact'] != 423
            or any(records[i].get('kind') != 13 or records[i].get('parent') != parent
                   or not records[i].get('immutable_remainder_exact') for i, parent in parents.items())):
        raise ValueError('Missing/wrong measured regional record/media proof')
    for location in ('zone02', 'zone03'):
        checks = playback.get('outro_checks', {}).get(location, [])
        expected = {(m, c) for m in ('native-reference', 'manifest')
                    for c in ('e-combat', 'e-combat-offset')}
        if len(checks) != 4 or {(c['mode'], c['case']) for c in checks} != expected or not all(c['passed'] for c in checks):
            raise ValueError('Missing native/modified complete-outro playback review')


def stage(redkit, baseline, candidate, project, manifest, proof_path, playback_path, root, resume_after_timeout=False):
    spec = json.loads(manifest.read_text(encoding='utf-8'))
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    playback = json.loads(playback_path.read_text(encoding='utf-8'))
    bank = candidate / (spec['region'] + '.bnk')
    bank_hash = digest(bank)
    require_proofs(spec, digest(manifest), proof, bank_hash,
                   digest(project / 'Interactive Music Hierarchy/music.wwu'), playback)
    if digest(baseline / bank.name) != proof['decoded_fields']['baseline_sha256']:
        raise ValueError('Baseline changed since decoded proof')
    warnings = diagnostics(candidate)
    if diagnostics(baseline) != warnings:
        raise ValueError('New/changed generation diagnostics require explicit review')
    if digest(redkit / 'r4data/soundbanks/Pc/Init.bnk') != NATIVE_INIT:
        raise ValueError('Native bootstrap Init provenance changed')
    root = build_path(root)
    if resume_after_timeout:
        prior = json.loads((root / 'regional-cook-result.json').read_text(encoding='utf-8'))
        if not prior.get('timeout') or (root / 'regional-package-verified.json').exists():
            raise ValueError('Resume permitted only for retained first cooker timeout')
        if (root / 'regional-input' / bank.name).read_bytes() != bank.read_bytes():
            raise ValueError('Retained cooker input changed')
    else:
        prepare(redkit, root)
    inputs, cooked, split = [root / n for n in ('regional-input', 'regional-cooked', 'regional-split')]
    if resume_after_timeout:
        cooked = root / 'regional-cooked-retry'
        cooked.mkdir()
    else:
        inputs.mkdir(); cooked.mkdir()
        shutil.copyfile(bank, inputs / bank.name)
    exe = redkit / 'bin/x64_RedKit/wcc_lite.exe'
    execute(exe, root, 'regional-cook-retry' if resume_after_timeout else 'regional-cook', ['cooksounds', '-soundbanksdir=' + str(inputs) + '\\',
        '-outdir=' + str(cooked) + '\\', '-platform=pc_dx12', '-r4remastersounds',
        '-outsplitfile=' + str(cooked / 'audio-split.list')], timeout_seconds=180 if resume_after_timeout else 45)
    cache = cooked / 'CookedPC/soundspc.cache'
    expected = {bank.name: bank.read_bytes()}
    first = verify_bytes(cache.read_bytes(), expected)
    execute(exe, root, 'regional-split', ['splitcache', 'sounds', '-platform=pc_dx12',
        '-split=' + str(cooked / 'audio-split.list'), '-file=' + str(cache), '-outdir=' + str(split) + '\\'])
    second = verify_bytes((split / 'content0/soundspc.cache').read_bytes(), expected)
    entry = 'Mods/modWMCNomansgradPilot/content/soundspc.cache'
    package = root / 'package' / entry
    package.parent.mkdir(parents=True)
    shutil.copyfile(cache, package)
    archives = root / 'archives'; archives.mkdir()
    archive = archives / 'WMC Velen Novigrad — Zone 02-03 Combat Outro Test.zip'
    info = zipfile.ZipInfo(entry, date_time=(2026, 10, 14, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(archive, 'x') as zipped:
        zipped.writestr(info, package.read_bytes())
    with zipfile.ZipFile(archive) as zipped:
        if zipped.namelist() != [entry] or zipped.testzip() or zipped.read(entry) != cache.read_bytes():
            raise ValueError('Archive nesting/content/readback mismatch')
    if digest(bank) != bank_hash or any(digest(root / p) != NATIVE_INIT for p in (
            'bin/initialdata/sound/Init.bnk', 'r4data/soundbanks/Pc/Init.bnk')):
        raise ValueError('Bank/bootstrap changed during packaging')
    result = {'region': spec['region'], 'bank_sha256': bank_hash,
        'manifest_sha256': digest(manifest), 'source_bank_proof_sha256': digest(proof_path),
        'playback_review_sha256': digest(playback_path), 'generation_exit_code': json.loads((candidate / 'result.json').read_text())['exit_code'],
        'reviewed_warning_rows': sum(warnings.values()), 'cooked_cache': first,
        'native_split_readback': second, 'archive': str(archive), 'archive_sha256': digest(archive),
        'archive_bytes': archive.stat().st_size, 'zip_entry': entry,
        'init_in_package': False, 'wem_in_package': False, 'partial_coverage': True,
        'offline_package_verified': True, 'runtime_validated': False, 'deployed': False}
    result['resumed_after_cooker_timeout'] = resume_after_timeout
    (root / 'regional-package-verified.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('redkit', 'baseline', 'candidate', 'project', 'manifest', 'proof', 'playback', 'root'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--resume-after-timeout', action='store_true')
    args = parser.parse_args()
    stage(args.redkit, build_path(args.baseline), build_path(args.candidate), build_path(args.project),
          args.manifest, build_path(args.proof), build_path(args.playback), args.root, args.resume_after_timeout)
