"""Fail-closed English font trial packaging; no deployment or live writes."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load('verify-font-asset')
prep = load('prepare-english-gentium')
audit = verify.audit
KEY = verify.KEY
MOD = 'modQuietFolioEnglish'


def contract_delta(original, candidate):
    old, new = verify.movie_tags(original), verify.movie_tags(candidate)
    if old[:2] != new[:2] or len(old[2]) != len(new[2]):
        raise ValueError('Movie header or tag count changed')
    changed = []
    for a, b in zip(old[2], new[2]):
        if a == b:
            continue
        if a[0] != 75 or b[0] != 75:
            raise ValueError('Non-font movie contract changed')
        before, after = prep.layout(a[1]), prep.layout(b[1])
        for key in ('id', 'flags', 'language', 'name', 'codes', 'glyphs'):
            if before.get(key) != after.get(key):
                raise ValueError('Font binding/coverage changed: '+key)
        if after['glyphs'] != 383:
            raise ValueError('Incomplete English coverage')
        changed.append(after['id'])
    if changed != [1, 3, 5]:
        raise ValueError('Exactly three intended font replacements required')
    return dict(changed_font_ids=changed, nonfont_tags_identical=True,
                movie_header_identical=True, aliases_styles_and_coverage_preserved=True)


def archive_bytes(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return stream.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    work, out = a.build.resolve(), a.out.resolve()
    if ROOT/'build' not in work.parents or ROOT/'deploy' not in out.parents or out.exists():
        raise ValueError('Private build and fresh deploy paths required')
    receipt = json.loads((work/'receipt.json').read_text())
    if [c['label'] for c in receipt['commands']] != ['cook','validate','pack','metadata']:
        raise ValueError('Incomplete official pipeline')
    for command in receipt['commands']:
        if command['exit_code'] != 0 or any(not any(x in s for x in
                ('depotDirectory.cpp:11', 'soundFileLoader.cpp:101')) for s in command['assertions']):
            raise ValueError('New compiler assertion or failed command')
    for key in ('offline_build_verified','exact_reextraction','sources_unchanged',
                'chunk_crc_valid','texture_array_empty','runtime_font_descriptors_identical',
                'exporter_linkage_consistent','runner_workspace_restored'):
        if receipt.get(key) is not True:
            raise ValueError('Missing validation gate: '+key)
    if receipt['compiler_sha256'] != verify.COMPILER_SHA:
        raise ValueError('Unexpected compiler')
    for path, digest in ((receipt['source_path'],receipt['source_sha256']),
                         (receipt['expected_swf'],receipt['expected_swf_sha256'])):
        if audit.sha(Path(path).read_bytes()) != digest:
            raise ValueError('Validated source changed')
    prepared = Path(receipt['expected_swf']).parent.parent
    names = [b for c,b in audit.swf_tags(Path(receipt['expected_swf']).read_bytes())[2] if c == 88]
    if len(names) != 3 or any(b'Quiet Folio Book' not in b for b in names):
        raise ValueError('Missing independently named source derivative')
    source = json.loads((prepared/'receipt.json').read_text())
    if source['candidate_sha256'] != receipt['expected_swf_sha256'] or not source['independent_xml_geometry_metrics_verified']:
        raise ValueError('Missing independently decoded font proof')
    if [(s['font_id'],s['glyphs'],s['visible_nonempty'],s['spacing_glyphs']) for s in source['styles']] != [
            (i,383,381,[32,160]) for i in (1,3,5)]:
        raise ValueError('Glyph completeness proof differs')
    fonts = [b for c,b in audit.swf_tags(Path(receipt['expected_swf']).read_bytes())[2] if c == 75]
    if [audit.sha(b) for b in fonts] != [s['payload_sha256'] for s in source['styles']]:
        raise ValueError('Independent font payload proof differs')
    cooked = (work/'cooked'/KEY).read_bytes()
    if audit.sha(cooked) != receipt['cooked_sha256'] or cooked != (work/'reextracted.redswf').read_bytes():
        raise ValueError('Cooked input changed')
    if verify.movie_tags(cooked) != verify.movie_tags(Path(receipt['expected_swf']).read_bytes()):
        raise ValueError('Cooked movie differs from independent source')
    bundle = a.game/'content/content0/bundles/r4gui.bundle'
    entries = [e for e in audit.entries(bundle) if e['resource'] == KEY]
    if len(entries) != 1 or entries[0]['codec'] != 1:
        raise ValueError('Unexpected installed vanilla resource')
    e = entries[0]
    with bundle.open('rb') as f:
        f.seek(e['offset']); vanilla = zlib.decompress(f.read(e['packed']))
    if audit.sha(vanilla) != verify.BASELINE_SHA:
        raise ValueError('Installed baseline changed')
    delta = contract_delta(vanilla,cooked)
    collisions, count = [], 0
    for folder in ('Mods','DLC'):
        for bundle in sorted((a.game/folder).rglob('*.bundle')):
            count += 1
            collisions += [str(bundle) for e in audit.entries(bundle) if e['resource'] == KEY]
        collisions += [str(p) for p in (a.game/folder).rglob('fonts_en.redswf')]
    if collisions:
        raise ValueError('English font resource collision: '+str(collisions))
    files = {}
    for name, key in (('blob0.bundle','bundle_sha256'),('metadata.store','metadata_sha256')):
        data = (work/'packed'/name).read_bytes()
        if audit.sha(data) != receipt[key]:
            raise ValueError('Validated package component changed')
        files['Mods/'+MOD+'/content/'+name] = data
    packed = work/'packed/blob0.bundle'
    entries = list(audit.entries(packed))
    if len(entries) != 1 or entries[0]['resource'] != KEY or entries[0]['codec'] != 1:
        raise ValueError('Bundle scope differs')
    e = entries[0]
    with packed.open('rb') as f:
        f.seek(e['offset'])
        if zlib.decompress(f.read(e['packed'])) != cooked:
            raise ValueError('Bundle resource differs')
    for name, digest in (
            ('OFL-SIL.txt','dcae5818b104b6cb24334bb4c92f7896d1ac988529ca4654ff21361a7b5b94ee'),
            ('OFL-Noto.txt','0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb'),
            ('FONT-NOTICES.txt',None)):
        data = (prepared/name).read_bytes()
        if digest and audit.sha(data) != digest:
            raise ValueError('License notice differs')
        if name == 'FONT-NOTICES.txt' and b'Quiet Folio Book' not in data:
            raise ValueError('Missing derivative attribution')
        files['Mods/'+MOD+'/'+name] = data
    data = archive_bytes(files)
    if data != archive_bytes(dict(reversed(list(files.items())))):
        raise ValueError('Archive is not deterministic')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() or sorted(archive.namelist()) != sorted(files) or any(archive.read(k) != v for k,v in files.items()):
            raise ValueError('ZIP routing/content mismatch')
    out.mkdir()
    archive = out/'QuietFolio-English-Gentium-Book-v1-private-test.zip'
    archive.write_bytes(data)
    manifest = dict(zip_path=str(archive),zip_sha256=audit.sha(data),zip_bytes=len(data),
                    members={k:audit.sha(v) for k,v in sorted(files.items())},resource_key=KEY,
                    vanilla_sha256=audit.sha(vanilla),cooked_sha256=audit.sha(cooked),
                    source_sha256=receipt['expected_swf_sha256'],delta=delta,
                    official_receipt=str(work/'receipt.json'),styles=[{k:v for k,v in s.items() if k not in ('codes','gpos_features')} for s in source['styles']],
                    scanned_installed_bundles=count,installed_resource_collisions=collisions,
                    deterministic_archive=True,offline_build_verified=True,runtime_tested=False,
                    font_name_tags='Three source attribution tags stripped by official GFx import; external notices included',
                    metadata_validation=receipt['metadata_validation'])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    main()
