"""Read-only licensed-baseline/candidate gates. Never generate, license or deploy.

Writes a fresh JSON evidence file under build/ and exits 1 on any unresolved
gate. A pass permits the next offline step only; it is not runtime acceptance.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

from white_orchard_compare import read_bank, difference
from white_orchard_prepare import build_path, digest
from white_orchard_state_bank_audit import audit, header, native_groups

BANKS = ('Init.bnk', 'music_prologue.bnk')
HEADER_FIELDS = ('version', 'bank_id', 'language_id', 'alignment_flags',
                 'project_id', 'bank_type', 'padding_hex')


def plugins(payload):
    """Observed v150 INIT: count, repeated u32 ID + NUL-terminated name."""
    if len(payload) < 4:
        raise ValueError('Truncated INIT registration count')
    count = struct.unpack_from('<I', payload)[0]
    offset, entries = 4, {}
    if count > len(payload) // 5:
        raise ValueError('Impossible INIT registration count')
    for _ in range(count):
        if offset + 4 > len(payload):
            raise ValueError('Truncated INIT registration ID')
        ident = struct.unpack_from('<I', payload, offset)[0]
        offset += 4
        end = payload.find(b'\0', offset)
        if end < 0:
            raise ValueError('Unterminated INIT plugin name')
        name = payload[offset:end].decode('ascii')
        if ident in entries:
            raise ValueError('Duplicate INIT registration ID')
        entries[ident] = name
        offset = end + 1
    if offset != len(payload):
        raise ValueError('Unconsumed INIT registration bytes')
    return entries


def generation(folder):
    result = json.loads((folder / 'result.json').read_text())
    text = (folder / 'generation.log').read_text(encoding='utf-8', errors='replace')
    # Do not copy log text, command arguments or licence contents into reports.
    severities = collections.Counter(re.findall(r'\t(Fatal Error|Error|Warning)\t', text))
    forbidden = {
        'media_limit': bool(re.search(r'maximum number of media items exceeded|trial license:', text, re.I)),
        'licence_error': bool(re.search(r'no licen[cs]e|licen[cs]e.{0,40}(expired|invalid|missing)', text, re.I)),
        'failed_completion': bool(re.search(r'completed with (fatal )?error', text, re.I)),
        'unreviewed_warnings': bool(severities['Warning']),
    }
    matching_tool = bool(re.search(r'Wwise\s*\|\s*v2023\.1\.19\s*\|\s*Build no\.8928', text))
    actual_banks = sorted(p.name for p in folder.rglob('*.bnk'))
    return {'exit_code': result.get('exit_code'), 'banks': result.get('banks'),
            'severity_counts': dict(severities), 'blocking_diagnostics': forbidden,
            'log_sha256': digest(folder / 'generation.log'),
            'matching_tool_banner': matching_tool,
            'actual_bank_files': actual_banks,
            'passed': matching_tool and result.get('exit_code') == 0 and result.get('banks') == actual_banks == sorted(BANKS)
                      and not any(forbidden.values()) and not severities['Error']
                      and not severities['Fatal Error']}


def source_control(project):
    """Baseline must be a complete untouched copy, without inclusion experiments."""
    manifest = json.loads((project / 'input-manifest.json').read_text())
    attrs = ET.parse(project / 'w3_audio.wproj').getroot().attrib
    matching_version = all(manifest['version'].get(k) == v and attrs.get(k) == v
                           for k, v in {'WwiseVersion': 'v2023.1.19', 'WwiseBuild': '8928', 'SchemaVersion': '119'}.items())
    expected = {Path(x['relative_path']).as_posix(): x for x in manifest['inputs']
                if x['relative_path'].endswith('.wwu')}
    actual = {p.relative_to(project).as_posix(): p for p in project.rglob('*.wwu')}
    changed = [rel for rel in expected if rel not in actual or digest(actual[rel]) != expected[rel]['sha256']]
    media = {Path(x['relative_path']).as_posix(): x for x in manifest['originals']}
    bad_media = [rel for rel in media if not (project / rel).is_file() or digest(project / rel) != media[rel]['sha256']]
    return {'work_units': len(actual), 'matching_source_version': matching_version, 'changed_or_missing_units': changed,
            'extra_units': sorted(actual.keys() - expected.keys()), 'changed_originals': bad_media,
            'passed': matching_version and actual.keys() == expected.keys() and len(actual) == 1508
                      and not changed and not bad_media
                      and 'Preserved all work units' in ' '.join(manifest['changes'])
                      and not (project / 'leaf-inclusion-audit.json').exists()}


def compare_pair(native, generated, metadata):
    """No waivers: hashes may differ with corroborating metadata, nothing else."""
    hn, hg = header(native), header(generated, metadata)
    differences = difference(native, generated)
    fields = {k: {'native': hn[k], 'generated': hg[k]} for k in HEADER_FIELDS if hn[k] != hg[k]}
    chunk_diffs = [k for k in differences['chunk_changed'] if k != 'BKHD']
    return {'native_sha256': native['sha256'], 'generated_sha256': generated['sha256'],
            'native_header': hn, 'generated_header': hg, 'header_field_differences': fields,
            'bank_hash_changed': hn['hash_hex'] != hg['hash_hex'],
            'hirc': differences, 'unexplained_chunks': chunk_diffs,
            'passed': not fields and hg['hash_matches_metadata_guid'] and not chunk_diffs
                      and not differences['added'] and not differences['removed'] and not differences['changed']}


def baseline(native, folder, project, game_init):
    n = {name: read_bank(native / name) for name in BANKS}
    b = {name: read_bank(folder / name) for name in BANKS}
    pairs = {name: compare_pair(n[name], b[name], folder / 'SoundbanksInfo.xml') for name in BANKS}
    pn, pb = plugins(n['Init.bnk']['payload']['INIT']), plugins(b['Init.bnk']['payload']['INIT'])
    plugin_diff = {'missing': {i: pn[i] for i in pn.keys() - pb.keys()},
                   'added': {i: pb[i] for i in pb.keys() - pn.keys()},
                   'changed': {i: {'native': pn[i], 'generated': pb[i]} for i in pn.keys() & pb.keys() if pn[i] != pb[i]}}
    stmg_n, stmg_b = n['Init.bnk']['payload']['STMG'], b['Init.bnk']['payload']['STMG']
    stmg = {'native_bytes': len(stmg_n), 'generated_bytes': len(stmg_b),
            'native_sha256': hashlib.sha256(stmg_n).hexdigest(),
            'generated_sha256': hashlib.sha256(stmg_b).hexdigest(),
            'byte_exact': stmg_n == stmg_b,
            'decoded_native_state_groups': native_groups(stmg_n),
            'decoded_generated_state_groups': native_groups(stmg_b),
            'remaining_stmg_bytes_policy': 'Entire chunk must match; StateGroup prefix decoding alone is insufficient.'}
    gen, src = generation(folder), source_control(project)
    checks = {'generation_success': gen['passed'], 'unpruned_untouched_source': src['passed'],
              'shipped_game_init_matches_native_reference': digest(game_init) == n['Init.bnk']['sha256'],
              'native_bank_ids_expected': header(n['Init.bnk'])['bank_id'] == 1355168291 and header(n['music_prologue.bnk'])['bank_id'] == 3228744150,
              'native_project_identity_nonzero': all(header(v)['project_id'] != 0 for v in n.values()),
              'init_native_fidelity': pairs['Init.bnk']['passed'],
              'regional_native_fidelity': pairs['music_prologue.bnk']['passed'],
              'plugin_registrations_exact': pn == pb, 'complete_stmg_exact': stmg['byte_exact']}
    return {'checks': checks, 'generation': gen, 'source': src, 'banks': pairs,
            'plugin_registration_differences': plugin_diff, 'stmg': stmg,
            'native_dependency_policy': 'Native global HIRC/INIT/STMG/ENVS/PLAT and all other chunks must match. No new reference graph is accepted.',
            'passed': all(checks.values())}


def inputs(args):
    """Fingerprint read-only inputs, binding the baseline proof to this invocation."""
    files = set()
    for folder in (args.native, args.baseline, args.candidate):
        if folder:
            files.update(folder / name for name in BANKS)
            if folder != args.native:
                files.update(folder / name for name in ('result.json', 'generation.log', 'SoundbanksInfo.xml'))
    for project in (args.baseline_project, args.candidate_project):
        if project:
            files.update(project.rglob('*.wwu'))
            files.update((project / '.cache').rglob('*.wem'))
            files.update((project / 'Originals').rglob('*'))
            files.update(project / name for name in ('w3_audio.wproj', 'input-manifest.json'))
    files.add(args.game_init)
    if args.candidate_project:
        files.add(args.candidate_project / 'state-volume-clean-authoring.json')
    return {str(p.resolve()): digest(p) for p in sorted(files) if p.is_file()}


def run(args):
    output = build_path(args.output)
    if output.exists():
        raise FileExistsError('Use a fresh verification output; preserve earlier evidence')
    for path in (args.native, args.baseline, args.candidate, args.baseline_project, args.candidate_project):
        if path and output.is_relative_to(path.resolve()):
            raise ValueError('Evidence output must be outside all input directories')
    for path in (args.baseline, args.candidate, args.baseline_project, args.candidate_project):
        if path:
            build_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {'mode': args.mode, 'passed': False, 'deployable': False,
              'verification_schema': 1, 'validator_sha256': digest(Path(__file__)),
              'licence_status': 'Not inspected or changed; clean generation is evidence of effective build coverage only.',
              'runtime_validated': False, 'failures': []}
    try:
        report['active_stage'] = 'input_fingerprint'
        before = inputs(args)
        report['active_stage'] = 'baseline_native_fidelity'
        report['baseline'] = baseline(args.native, args.baseline, args.baseline_project, args.game_init)
        report['failures'] = ['baseline.' + k for k, passed in report['baseline']['checks'].items() if not passed]
        if args.mode == 'candidate' and not report['failures']:
            report['active_stage'] = 'baseline_proof_binding'
            proof = json.loads(args.baseline_report.read_text())
            # Recompute the baseline rather than trusting a hand-edited passed flag.
            base_args = argparse.Namespace(**vars(args))
            base_args.candidate = base_args.candidate_project = None
            proof_matches = proof.get('mode') == 'baseline' and proof.get('passed') is True and proof.get('input_hashes') == inputs(base_args)
            if not proof_matches:
                report['failures'].append('baseline_report_missing_or_stale')
            else:
                report['active_stage'] = 'candidate_state_serialization'
                detail = output.with_name(output.stem + '-state-detail.json')
                if detail.exists():
                    raise FileExistsError('State detail exists; use a fresh output stem')
                try:
                    structural = audit(args.native, args.baseline, args.candidate,
                                       args.baseline_project, args.candidate_project, detail)
                except RuntimeError:
                    structural = json.loads(detail.read_text())
                report['candidate_structural'] = structural
                report['active_stage'] = 'candidate_generation_globals_media'
                gen = generation(args.candidate)
                cn = {name: read_bank(args.candidate / name) for name in BANKS}
                bn = {name: read_bank(args.baseline / name) for name in BANKS}
                # Regional HIRC is allowed to differ only as decoded by the State audit.
                rh = header(cn['music_prologue.bnk'], args.candidate / 'SoundbanksInfo.xml')
                bh = header(bn['music_prologue.bnk'])
                src_audit = json.loads((args.candidate_project / 'state-volume-clean-authoring.json').read_text())
                spec = json.loads((Path(__file__).resolve().parents[1] / 'src/wwise/white-orchard-state-volume.json').read_text())
                required = {name for cat in ('exploration', 'dialogue') for name in spec['active_states'][cat]}
                serialized = structural['inline_state_chunk']['groups'][0]['states']
                candidate_originals = json.loads((args.candidate_project / 'input-manifest.json').read_text())['originals']
                baseline_originals = json.loads((args.baseline_project / 'input-manifest.json').read_text())['originals']
                original_media = all((args.candidate_project / x['relative_path']).is_file() and digest(args.candidate_project / x['relative_path']) == x['sha256'] for x in candidate_originals)
                checks = {'generation_success': gen['passed'],
                          'all_structural_checks': all(structural['checks'].values()),
                          'state_names_match_policy': {s['name'] for s in serialized} == required and len(serialized) == 9,
                          'source_authoring_audit_passed': not src_audit['unrelated_work_units_changed'] and src_audit['all_work_units_preserved'] and src_audit['music_changes_only_world_state_info'],
                          'original_media_unchanged': original_media and candidate_originals == baseline_originals,
                          'no_inclusion_experiment': not (args.candidate_project / 'leaf-inclusion-audit.json').exists(),
                          'regional_header_identity_exact': all(rh[k] == bh[k] for k in HEADER_FIELDS) and rh['hash_matches_metadata_guid'],
                          'no_unexplained_regional_chunks': set(difference(bn['music_prologue.bnk'], cn['music_prologue.bnk'])['chunk_changed']) <= {'BKHD', 'HIRC'},
                          'candidate_init_global_data_exact': compare_pair(bn['Init.bnk'], cn['Init.bnk'], args.candidate / 'SoundbanksInfo.xml')['passed']}
                report['candidate'] = {'checks': checks, 'generation': gen, 'passed': all(checks.values())}
                report['failures'].extend('candidate.' + k for k, passed in checks.items() if not passed)
        report['active_stage'] = 'read_only_input_recheck'
        after = inputs(args)
        report['input_hashes'] = before
        report['read_only_inputs_unchanged'] = before == after
        if before != after:
            report['failures'].append('inputs_changed_during_validation')
        report['passed'] = not report['failures']
    except (OSError, ValueError, KeyError, IndexError, TypeError, StopIteration, struct.error, RuntimeError, ET.ParseError) as exc:
        # Missing/malformed evidence must produce a machine-readable failure.
        report['failures'].append('invalid_or_missing_evidence:' + type(exc).__name__)
        report['error_type'] = type(exc).__name__
        if isinstance(exc, ValueError):
            report['error_detail'] = str(exc)[:200]
        if isinstance(exc, OSError) and exc.filename:
            report['evidence_file'] = str(exc.filename)
    report['next_step'] = ('Validate candidate against this accepted baseline.' if args.mode == 'baseline' else 'Eligible for separate offline cooker packaging; no runtime/deployment approval.') if report['passed'] else 'STOP: resolve listed gates; do not package, rewrite headers or replace native Init.'
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'failures': report['failures'], 'report': str(output), 'deployable': False}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('baseline', 'candidate'))
    for name in ('native', 'baseline', 'baseline-project', 'game-init', 'output'):
        p.add_argument('--' + name, required=True, type=Path)
    for name in ('candidate', 'candidate-project', 'baseline-report'):
        p.add_argument('--' + name, type=Path)
    args = p.parse_args()
    if args.mode == 'baseline' and any((args.candidate, args.candidate_project, args.baseline_report)):
        p.error('baseline mode does not accept candidate or prior-proof arguments')
    if args.mode == 'candidate' and not all((args.candidate, args.candidate_project, args.baseline_report)):
        p.error('candidate requires --candidate, --candidate-project and --baseline-report')
    sys.exit(run(args))
