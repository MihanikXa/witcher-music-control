"""Fail-closed private shadow trial packaging; reads game, writes deploy only."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


native = load('compare-native-npc')
shadow = load('prepare-npc-shadow')
audit = native.audit
KEY = 'gameplay/gui_new/swf/hud/hud_enemyfocus.redswf'
MOD = 'modQuietEditorialNPCShadow'


def contract_delta(original, candidate):
    excluded = {36, 1000, 1008, 1009}
    old, new = [[(c, b) for c, b in audit.swf_tags(d)[2] if c not in excluded]
                for d in (original, candidate)]
    if len(old) != len(new):
        raise ValueError('Non-image tag count changed')
    changes = [(i, a, b) for i, (a, b) in enumerate(zip(old, new)) if a != b]
    if len(changes) != 1:
        raise ValueError('Expected exactly one modified sprite tag')
    index, a, b = changes[0]
    if a[0] != 39 or b[0] != 39 or struct.unpack_from('<H', a[1])[0] != 63:
        raise ValueError('Wrong changed sprite')
    offset = shadow.accept_sprite(a[1], b[1])
    return dict(nonimage_changed_tag_index=index, sprite=63, filter_offset_in_sprite=offset,
                only_approved_filter_changed=True, other_nonimage_tags_identical=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    work, out = a.build.resolve(), a.out.resolve()
    if ROOT / 'build' not in work.parents or ROOT / 'deploy' not in out.parents or out.exists():
        raise ValueError('Private build and fresh deploy output required')
    receipt = json.loads((work / 'receipt.json').read_text())
    if [c['label'] for c in receipt['commands']] != ['cook', 'validate', 'pack', 'metadata'] or any(
            c['exit_code'] or c['resource_assertions'] for c in receipt['commands']):
        raise ValueError('Official build gates failed')
    if not receipt['exact_reextraction'] or not receipt['sources_unchanged'] or not receipt['expected_native']:
        raise ValueError('Source/re-extraction evidence missing')
    for s in receipt['sources'] + [receipt['expected_native']]:
        if audit.sha(Path(s['path']).read_bytes()) != s['sha256']:
            raise ValueError('Validated source changed')
    cooked = (work / 'cooked' / KEY).read_bytes()
    if audit.sha(cooked) != receipt['reextracted_sha256'] or (work / 'reextracted.redswf').read_bytes() != cooked:
        raise ValueError('Cooked/re-extracted candidate changed')
    # Re-read current installed vanilla entry, rather than trusting a stale cache.
    startup = a.game / 'content/content0/bundles/startup.bundle'
    entries = [e for e in audit.entries(startup) if e['resource'] == KEY]
    if len(entries) != 1 or entries[0]['codec'] != 1:
        raise ValueError('Unexpected current vanilla resource entry/codec')
    e = entries[0]
    with startup.open('rb') as f:
        f.seek(e['offset']); vanilla = zlib.decompress(f.read(e['packed']))
    if audit.sha(vanilla) != '8b5c7cf0cb0e61fd005239689e096c9c5da9e3f1aa2182f9f88c71057903a76e':
        raise ValueError('Installed vanilla baseline changed; re-audit first')
    delta = contract_delta(vanilla, cooked)
    source = Path(receipt['expected_native']['path']).read_bytes()
    excluded = {36, 1000, 1008, 1009}
    if [(c, b) for c, b in audit.swf_tags(source)[2] if c not in excluded] != [(c, b) for c, b in audit.swf_tags(cooked)[2] if c not in excluded]:
        raise ValueError('Cooked source contracts differ')
    contracts = json.loads((work / 'contracts.json').read_text())
    padding = json.loads((work / 'padding.json').read_text())
    if contracts['inputs'][2]['sha256'] != audit.sha(cooked) or padding['inputs'][1]['sha256'] != audit.sha(cooked):
        raise ValueError('Stale texture reports')
    if not all(contracts[k] for k in ('frame_rect_rate_count_version_equal', 'atlas_placements_byte_identical', 'cooked_atlas_linkage_matches')):
        raise ValueError('Rendering contracts changed')
    if len(contracts['atlas_pixel_differences']) != 7 or any(x['visible_differences_including_one_pixel_border'] for x in contracts['atlas_pixel_differences']):
        raise ValueError('Used image pixels/borders changed')
    if not padding['clipped_nearest_or_bilinear_model_unaffected']:
        raise ValueError('Padding may affect modeled sampling')
    chunks, texture, _ = native.texture(cooked)
    if not all(c['crc_valid'] for c in chunks) or chunks[1]['properties']['textureGroup']['value'] != 'GUIWithAlpha':
        raise ValueError('Invalid texture metadata/CRC')
    collisions, bundle_count = [], 0
    # Scan all installed owners, including disabled ones: no profile assumptions.
    for folder in ('Mods', 'DLC'):
        for bundle in sorted((a.game / folder).rglob('*.bundle')):
            bundle_count += 1
            collisions += [str(bundle) for e in audit.entries(bundle) if e['resource'] == KEY]
        for loose in (a.game / folder).rglob('hud_enemyfocus.redswf'):
            collisions.append(str(loose))
    if collisions:
        raise ValueError('Installed EnemyFocus resource owners require review: ' + str(collisions))
    v4 = ROOT / 'src/npc/quietEditorialNameColors.ws'
    if audit.sha(v4.read_bytes()) != '1b9d70f775ac1cf4173739fa01325d65ead2bdb9c1aeb363dac548c03f6b82b7':
        raise ValueError('Accepted v4 source changed')
    files = {}
    for name, hash_key in (('blob0.bundle', 'bundle_sha256'), ('metadata.store', 'metadata_sha256')):
        data = (work / 'packed' / name).read_bytes()
        if audit.sha(data) != receipt[hash_key]:
            raise ValueError('Validated bundle/metadata changed')
        files['Mods/' + MOD + '/content/' + name] = data
    out.mkdir()
    archive = out / 'QuietEditorial-NPC-Shadow-v1-private-test.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, (2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() or set(z.namelist()) != set(files) or any(z.read(k) != v for k, v in files.items()):
            raise ValueError('ZIP content/routing mismatch')
    manifest = dict(zip_path=str(archive), zip_sha256=audit.sha(archive.read_bytes()), zip_bytes=archive.stat().st_size,
                    members={k: audit.sha(v) for k, v in files.items()}, resource_key=KEY,
                    cooked_sha256=audit.sha(cooked), vanilla_sha256=audit.sha(vanilla), source=receipt['expected_native'],
                    delta=delta, texture=texture, full_atlas_visible_differences=contracts['full_atlas_visible_pixel_differences'],
                    full_atlas_transparent_rgb_differences=contracts['full_atlas_transparent_rgb_differences'],
                    used_regions_and_border_match=True, scanned_installed_bundles=bundle_count,
                    installed_resource_collisions=collisions, v4_source_unchanged=True,
                    offline_build_verified=True, renderer_sampler_verified=False, runtime_tested=False,
                    metadata_validation=receipt['metadata_validation'], editor_assertion_state='unknown')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
