"""Read-only regional source/bank preflight with explicit decoder blockers.

The candidate preflight never blesses opaque changed records. Only known D's
exact hash has a pinned regression adapter. New layouts stop with evidence.
No Wwise generation, package writing, licence access or deployment.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from regional_music import context, validate_source, MUSIC
from white_orchard_compare import read_bank, difference
from white_orchard_prepare import build_path, digest
from white_orchard_state_bank_audit import header

D_HASH = '925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d'


def source_gate(source, candidate, manifest, template_path):
    spec = json.loads(manifest.read_text(encoding='utf-8'))
    original, states = context(source, spec)
    if digest(template_path) != spec['facts']['template_source_sha256']:
        raise ValueError('Template fingerprint changed')
    template = next(n for n in ET.parse(template_path).iter('MusicSwitchContainer')
                    if n.get('ShortID') == '1033516231').find('StateInfo')
    result = validate_source(original, ET.parse(candidate / MUSIC).getroot(), spec, states, template)
    manifest_in = json.loads((candidate / 'input-manifest.json').read_text())
    pinned = {x['relative_path'].replace('\\', '/'): x['sha256'] for x in manifest_in['inputs'] if x['relative_path'].endswith('.wwu')}
    copied = {p.relative_to(candidate).as_posix(): p for p in candidate.rglob('*.wwu')}
    if len(pinned) != 1508 or set(copied) != set(pinned):
        raise ValueError('Incomplete authoring context')
    for rel, sha in pinned.items():
        if digest(source / rel) != sha or (rel != MUSIC.as_posix() and digest(copied[rel]) != sha):
            raise ValueError('Unrelated or installed input changed: ' + rel)
    for original in manifest_in['originals']:
        rel = original['relative_path']
        if digest(candidate / rel) != original['sha256'] or digest(source / rel) != original['sha256']:
            raise ValueError('Source audio changed')
    result.update(complete_work_units=1508, original_audio_unchanged=True,
                  original_nonmusic_units_unchanged=True, candidate_music_sha256=digest(candidate / MUSIC),
                  manifest_sha256=digest(manifest), global_definitions_unchanged=True)
    return result


def bank_preflight(baseline, candidate, spec):
    name = spec['region'] + '.bnk'
    before, after = read_bank(baseline / name), read_bank(candidate / name)
    delta = difference(before, after)
    identities = lambda h: {k:v for k,v in h.items() if k not in ('hash_hex','metadata_hash','hash_matches_metadata_guid')}
    hb, hc = header(before, baseline / 'SoundbanksInfo.xml'), header(after, candidate / 'SoundbanksInfo.xml')
    # No whitelist-only success: source facts + records still need a measured
    # field decoder. Do not apply offset28/14 to arbitrary regional records.
    failures = []
    if delta['added'] or delta['removed']:
        failures.append('unexpected_HIRC_addition_or_removal')
    if identities(hb) != identities(hc) or not hc['hash_matches_metadata_guid']:
        failures.append('BKHD_identity_or_metadata')
    for tag in ('DIDX','DATA'):
        if before['payload'].get(tag) != after['payload'].get(tag):
            failures.append('embedded_media_changed:'+tag)
    if set(delta['chunk_changed']) - {'BKHD','HIRC'}:
        failures.append('unexpected_chunk_change')
    if after['sha256'] != D_HASH:
        failures.append('measured_record_decoder_required_for_this_manifest')
    else:
        # Hash establishes exact previously audited record/media identity;
        # caller must also supply the same verified manifest/source proof.
        if spec['purpose'] != 'retained-D-regression':
            failures.append('known_D_hash_with_wrong_manifest')
        if before['sha256'] != '5b28f4ee5f286ec46a80120ea632c1d2ca715c0e2b05fb90ddd411f16e9a953a':
            failures.append('known_D_with_unpinned_baseline')
    return {'passed': not failures, 'failures': failures, 'delta': delta,
            'baseline_sha256': before['sha256'], 'candidate_sha256': after['sha256'],
            'candidate_header': hc, 'packaging_allowed': False,
            'note': 'Preflight only; diagnostics, streamed media and exact native cooker readback remain independent mandatory gates.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--candidate-project', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--baseline-banks', type=Path)
    parser.add_argument('--candidate-banks', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = build_path(args.output)
    if output.exists():
        raise FileExistsError(output)
    result = source_gate(args.source, build_path(args.candidate_project), args.manifest, args.template)
    if args.baseline_banks or args.candidate_banks:
        if not args.baseline_banks or not args.candidate_banks:
            parser.error('Both bank directories required')
        result['bank_preflight'] = bank_preflight(args.baseline_banks, args.candidate_banks, json.loads(args.manifest.read_text()))
        result['passed'] &= result['bank_preflight']['passed']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    if not result['passed']:
        raise SystemExit(1)
