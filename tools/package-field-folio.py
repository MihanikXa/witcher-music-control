"""Private interaction-only package; validates current vanilla and both builds."""
import argparse
import json
from pathlib import Path
import struct
import zipfile
import io
import zlib
import importlib.util

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


pipeline=load('verify-field-folio-asset');zipper=load('package-english-gentium')
field=pipeline.field;audit=field.audit;KEY=field.KEY;MOD='modFieldFolioInteractions'


def gate(work):
    receipt=json.loads((work/'receipt.json').read_text())
    if [c['label'] for c in receipt['commands']]!=['cook','validate','pack','metadata']:
        raise ValueError('Incomplete official build')
    for c in receipt['commands']:
        if c['exit_code']!=0 or any(not any(x in s for x in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for s in c['assertions']):
            raise ValueError('Official build failed or new assertion')
    for key in ('offline_pipeline_verified','exact_reextraction','sources_unchanged','runner_workspace_restored',
                'font_definitions_identical_to_source','official_font_descriptors_present'):
        if receipt.get(key) is not True:raise ValueError('Missing validation gate: '+key)
    if receipt['resource_key']!=KEY or receipt['compiler_sha256']!=pipeline.font.COMPILER_SHA:
        raise ValueError('Unexpected resource or compiler')
    for path,digest in [(receipt['source_path'],receipt['source_sha256']),
                        (receipt['expected_swf'],receipt['expected_swf_sha256']),
                        (receipt['baseline_path'],receipt['baseline_sha256'])]:
        if audit.sha(Path(path).read_bytes())!=digest:raise ValueError('Validated input changed')
    cooked=(work/'cooked'/KEY).read_bytes()
    if audit.sha(cooked)!=receipt['cooked_sha256'] or cooked!=(work/'reextracted.redswf').read_bytes():
        raise ValueError('Cooked input changed')
    if pipeline.critical(cooked)!=pipeline.critical(Path(receipt['expected_swf']).read_bytes()):
        raise ValueError('Source contracts changed')
    cs,_=pipeline.textures(cooked)
    linkage=cs[0]['properties']['linkageName']['value']
    exporters=[b for c,b in audit.swf_tags(cooked)[2] if c==1000]
    if len(exporters)!=1 or linkage[:-4].encode() not in exporters[0] or not linkage.endswith('.gfx'):
        raise ValueError('Resource/movie linkage differs')
    bundle=work/'packed/blob0.bundle';entries=list(audit.entries(bundle))
    if len(entries)!=1 or entries[0]['resource']!=KEY or entries[0]['codec']!=1:raise ValueError('Bundle scope changed')
    e=entries[0]
    with bundle.open('rb') as f:
        f.seek(e['offset'])
        if zlib.decompress(f.read(e['packed']))!=cooked:raise ValueError('Bundle extraction differs')
    for name,key in [('blob0.bundle','bundle_sha256'),('metadata.store','metadata_sha256')]:
        if audit.sha((work/'packed'/name).read_bytes())!=receipt[key]:raise ValueError('Package component changed')
    return receipt,cooked


def delta(original,candidate):
    old=pipeline.critical(original);new=pipeline.critical(candidate)
    if old[:2]!=new[:2]:raise ValueError('Movie geometry changed')
    added=[(c,b) for c,b in new[2] if c==75 and struct.unpack_from('<H',b)[0] in field.IDS.values()]
    if [audit.font_info(c,b)['id'] for c,b in added]!=[218,219]:raise ValueError('Utility font IDs missing/duplicated')
    expected=[(c,field.field_binding(b,218) if c==37 and struct.unpack_from('<H',b)[0]==field.FIELD else b) for c,b in old[2]]
    filtered=[(c,b) for c,b in new[2] if (c,b) not in added]
    if filtered!=expected:raise ValueError('Changes outside utility fonts and approved selector')
    return dict(field=215,font_id=218,new_font_ids=[218,219],only_action_font_selector_changed=True,
                abc_symbols_timelines_and_unrelated_fields_identical=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--control',type=Path,required=True)
    ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--game',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
    if ROOT/'deploy' not in out.parents or out.exists():raise ValueError('Fresh private deploy output required')
    for work in (a.control.resolve(),a.candidate.resolve()):pipeline.font.private_path(work)
    control,base=gate(a.control);candidate,cooked=gate(a.candidate)
    vanilla=None
    for bundle in (a.game/'content/content0/bundles').glob('*.bundle'):
        found=[e for e in audit.entries(bundle) if e['resource']==KEY]
        if found:
            if vanilla is not None or len(found)!=1 or found[0]['codec']!=1:raise ValueError('Unexpected vanilla owner')
            e=found[0]
            with bundle.open('rb') as f:f.seek(e['offset']);vanilla=zlib.decompress(f.read(e['packed']))
    if vanilla is None or audit.sha(vanilla)!=field.RUNTIME_SHA:raise ValueError('Current installed baseline changed')
    if pipeline.critical(base)!=pipeline.critical(vanilla):raise ValueError('Unchanged control contracts differ from vanilla')
    report=pipeline.compare_textures(vanilla,cooked)
    if any(not r['compressed_payload_identical'] for r in report):raise ValueError('Expected exact full atlas bytes')
    change=delta(vanilla,cooked)
    prepared=Path(candidate['expected_swf']).parent.parent
    source=json.loads((prepared/'receipt.json').read_text())
    selected=next(c for c in source['candidates'] if c['weight']=='Regular')
    if selected['sha256']!=candidate['expected_swf_sha256'] or not source['independent_geometry_and_binding_verified']:
        raise ValueError('Missing independent glyph and binding proof')
    collisions=[];count=0
    for folder in ('Mods','DLC'):
        for bundle in (a.game/folder).rglob('*.bundle'):
            count+=1;collisions += [str(bundle) for e in audit.entries(bundle) if e['resource']==KEY]
        collisions += [str(p) for p in (a.game/folder).rglob('hud_interactions.redswf')]
    if collisions:raise ValueError('Installed resource owners require review: '+str(collisions))
    accepted=json.loads((ROOT/'research/field-folio-phase1-manifest.json').read_text())['accepted_packages']
    for path,entry in accepted.items():
        if audit.sha((ROOT/path).read_bytes())!=entry['sha256']:raise ValueError('Accepted package changed')
    files={'Mods/'+MOD+'/content/'+name:(a.candidate/'packed'/name).read_bytes() for name in ('blob0.bundle','metadata.store')}
    license_data=(prepared/'OFL-Adobe.txt').read_bytes()
    pin=json.loads((ROOT/'src/fonts/source-sans-3-source.json').read_text())['files']['LICENSE.md']['sha256']
    if audit.sha(license_data)!=pin:raise ValueError('Complete OFL notice differs')
    files['Mods/'+MOD+'/OFL-Adobe.txt']=license_data
    files['Mods/'+MOD+'/FONT-NOTICES.txt']=(prepared/'FONT-NOTICES.txt').read_bytes()
    data=zipper.archive_bytes(files)
    if data!=zipper.archive_bytes(dict(reversed(list(files.items())))):raise ValueError('Archive nondeterministic')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or set(z.namelist())!=set(files) or any(z.read(k)!=v for k,v in files.items()):raise ValueError('ZIP routing/content differs')
    out.mkdir();archive=out/'Field-and-Folio-Interactions-v1-private-test.zip';archive.write_bytes(data)
    manifest=dict(zip_path=str(archive),zip_sha256=audit.sha(data),zip_bytes=len(data),resource_key=KEY,
                  members={k:audit.sha(v) for k,v in files.items()},vanilla_sha256=audit.sha(vanilla),
                  cooked_sha256=audit.sha(cooked),source_sha256=candidate['expected_swf_sha256'],delta=change,
                  textures=report,styles=source['styles'],control_receipt=str((a.control/'receipt.json').resolve()),
                  candidate_receipt=str((a.candidate/'receipt.json').resolve()),scanned_installed_bundles=count,
                  installed_resource_collisions=collisions,accepted_packages=accepted,
                  font_library_replaced=False,deterministic_zip=True,offline_pipeline_verified=True,runtime_tested=False,
                  metadata_validation='Official producer, one-entry inventory and exact bundle extraction; independent full store consumer untested',
                  editor_assertion_state='Unknown; Editor log reports Asserts Disabled ON; no suppression performed')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
