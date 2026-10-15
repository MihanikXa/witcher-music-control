"""Read-only regional source/bank preflight with bounded decoded field gates.

The candidate preflight never blesses opaque changed records. New candidates
require full source proof and derived v150 fields; unsupported layouts stop.
No Wwise generation, package writing, licence access or deployment.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from regional_music import context, validate_source, validate_events, validate_event_directory, MUSIC
from white_orchard_compare import read_bank, difference
from white_orchard_prepare import build_path, digest
from white_orchard_state_bank_audit import header
from white_orchard_state_bank_audit import native_groups
from regional_music_bank import record_gate

D_HASH = '925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d'


def source_gate(source, candidate, manifest, template_path):
    spec = json.loads(manifest.read_text(encoding='utf-8'))
    original, states = context(source, spec)
    validate_events(original, ET.parse(source / 'Events/music.wwu'), spec)
    event_count = validate_event_directory(original, source, spec)
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
                  event_work_units_reviewed=event_count,
                  original_nonmusic_units_unchanged=True, candidate_music_sha256=digest(candidate / MUSIC),
                  manifest_sha256=digest(manifest), global_definitions_unchanged=True)
    return result


def bank_preflight(baseline, candidate, spec, decoded=None):
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
    if decoded is not None:
        if (not decoded.get('passed') or decoded.get('baseline_sha256') != before['sha256']
                or decoded.get('candidate_sha256') != after['sha256']):
            failures.append('decoded_field_proof_missing_or_stale')
    elif after['sha256'] != D_HASH:
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


def decoded_preflight(baseline, candidate, spec, baseline_project, native, sync_ids, source_proof):
    """Independent field checks after full source proof. Still no packaging approval."""
    if not source_proof.get('passed'):
        raise ValueError('Full source proof required before decoded bank checks')
    name = spec['region'] + '.bnk'
    before, after = read_bank(baseline / name), read_bank(candidate / name)
    pristine = read_bank(native / name)
    if difference(pristine, before)['added'] or difference(pristine, before)['removed'] or difference(pristine, before)['changed']:
        raise ValueError('Licensed baseline HIRC not native-exact')
    if set(difference(pristine, before)['chunk_changed']) - {'BKHD'}:
        raise ValueError('Licensed baseline nonheader chunks not native-exact')
    hi = read_bank(native / 'Init.bnk')
    groups = {g['id'] for g in native_groups(hi['payload']['STMG'])['groups']}
    records = record_gate(before, after, spec,
        ET.parse(baseline_project / MUSIC), ET.parse(baseline_project / 'States/global_states.wwu'),
        ET.parse(candidate / 'SoundbanksInfo.xml'), groups, sync_ids)
    # Disposable Init output may differ from native, but regional changes must
    # not introduce ANY new generated globals/registrations/transitions.
    ib, ic = read_bank(baseline / 'Init.bnk'), read_bank(candidate / 'Init.bnk')
    if set(ib['payload']) != set(ic['payload']) or any(
            ib['payload'][k] != ic['payload'][k] for k in ib['payload'] if k != 'BKHD'):
        raise ValueError('New generated global dependency/data')
    def media(folder):
        tree = ET.parse(folder / 'SoundbanksInfo.xml')
        bank = next(n for n in tree.iter('SoundBank') if n.findtext('ShortName') == spec['region'])
        rows = {}
        for n in bank.findall('./Media/File'):
            ident = int(n.get('Id'))
            if ident in rows:
                raise ValueError('Duplicate media identity')
            rel = n.findtext('Path')
            path = (folder / rel).resolve()
            if not path.is_relative_to(folder.resolve()) or not path.is_file():
                raise ValueError('Missing/escaping generated media')
            rows[ident] = (dict(n.attrib), [(c.tag,c.text) for c in n], digest(path))
        return rows
    mb, mc = media(baseline), media(candidate)
    if not mb or mb != mc:
        raise ValueError('Media bytes/references/streaming metadata changed')
    return {'passed': True, 'baseline_sha256': before['sha256'], 'candidate_sha256': after['sha256'],
            'records': records, 'global_generated_data_exact': True,
            'paired_generated_media_exact': len(mb), 'native_init_deployed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--candidate-project', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--baseline-banks', type=Path)
    parser.add_argument('--candidate-banks', type=Path)
    parser.add_argument('--baseline-project', type=Path)
    parser.add_argument('--native-banks', type=Path)
    parser.add_argument('--sync-identities', type=Path, help='Read-only WAAPI GUID/ShortID capture for original game_state')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = build_path(args.output)
    if output.exists():
        raise FileExistsError(output)
    result = source_gate(args.source, build_path(args.candidate_project), args.manifest, args.template)
    if args.baseline_banks or args.candidate_banks:
        if not args.baseline_banks or not args.candidate_banks:
            parser.error('Both bank directories required')
        spec = json.loads(args.manifest.read_text())
        decoded = None
        if args.baseline_project or args.native_banks or args.sync_identities:
            if not all((args.baseline_project, args.native_banks, args.sync_identities)):
                parser.error('Decoded checks require baseline project, native banks and sync identities')
            decoded = decoded_preflight(args.baseline_banks, args.candidate_banks, spec,
                build_path(args.baseline_project), args.native_banks,
                json.loads(args.sync_identities.read_text())['guid_short_ids'], result)
            result['decoded_fields'] = decoded
        result['bank_preflight'] = bank_preflight(args.baseline_banks, args.candidate_banks, spec, decoded)
        result['passed'] &= result['bank_preflight']['passed']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    if not result['passed']:
        raise SystemExit(1)
