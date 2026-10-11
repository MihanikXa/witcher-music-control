"""Separate private interaction-v2/subtitle-v1 archives, fail-closed gates."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import zipfile
import zlib

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
interaction=load('package-field-folio');subtitle=load('verify-subtitle-shadow-asset')
pipeline=interaction.pipeline;audit=pipeline.audit;inventory=load('audit-text-shadows')


def subtitle_gate(work):
    receipt=json.loads((work/'receipt.json').read_text());key=subtitle.KEY
    if receipt['resource_key']!=key or receipt['compiler_sha256']!=pipeline.font.COMPILER_SHA:raise ValueError('Wrong compiler/resource')
    if [c['label'] for c in receipt['commands']]!=['cook','validate','pack','metadata']:raise ValueError('Incomplete official pipeline')
    for c in receipt['commands']:
        if c['exit_code']!=0 or any(not any(s in a for s in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for a in c['assertions']):raise ValueError('Failed official pipeline/new assertion')
    for flag in ('offline_pipeline_verified','sources_unchanged','runner_workspace_restored','exact_reextraction',
                 'chunk_crc_valid','texture_array_empty','font_array_empty','exporter_linkage_consistent'):
        if receipt.get(flag) is not True:raise ValueError('Missing subtitle gate '+flag)
    for path,sha in [(receipt['source_path'],receipt['source_sha256']),(receipt['expected_swf'],receipt['expected_swf_sha256']),
                     (receipt['baseline_path'],receipt['baseline_sha256'])]:
        if audit.sha(Path(path).read_bytes())!=sha:raise ValueError('Validated input changed')
    cooked=(work/'cooked'/key).read_bytes();subtitle.structure(cooked)
    if pipeline.critical(cooked)!=pipeline.critical(Path(receipt['expected_swf']).read_bytes()):raise ValueError('Cooked source contracts differ')
    if audit.sha(cooked)!=receipt['cooked_sha256'] or (work/'reextracted.redswf').read_bytes()!=cooked:raise ValueError('Cooked input changed')
    bundle=work/'packed/blob0.bundle';entries=list(audit.entries(bundle))
    if len(entries)!=1 or entries[0]['resource']!=key or entries[0]['codec']!=1:raise ValueError('Bundle scope differs')
    e=entries[0]
    with bundle.open('rb') as f:f.seek(e['offset']);recovered=zlib.decompress(f.read(e['packed']))
    if recovered!=cooked:raise ValueError('Extraction differs')
    for file,sha in [('blob0.bundle','bundle_sha256'),('metadata.store','metadata_sha256')]:
        if audit.sha((work/'packed'/file).read_bytes())!=receipt[sha]:raise ValueError('Package input changed')
    return receipt,cooked


def check_source(receipt,original):
    if receipt['expected_swf_sha256']!=original['output_sha256']:raise ValueError('Candidate outside approved source transform')
    if audit.sha(Path(original['input_path']).read_bytes())!=original['input_sha256']:raise ValueError('Transformation baseline changed')
    if not all(original.get(x) is True for x in ('unchanged_selected_tags_exact','independently_decoded_delta_exact','other_tags_retained_from_source')):
        raise ValueError('Missing independently validated source delta')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--module',choices=('interactions','subtitles'),required=True)
    ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--control',type=Path,required=True)
    ap.add_argument('--game',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve()
    if ROOT/'deploy' not in out.parents or out.exists():raise ValueError('Fresh private deploy path required')
    for work in (a.control,a.candidate):pipeline.font.private_path(work)
    source=json.loads((ROOT/'research/text-shadow-wave-a-manifest.json').read_text())
    if a.module=='interactions':
        key=pipeline.KEY;gate=interaction.gate;mod='modFieldFolioInteractionsV2';name='Field-and-Folio-Interactions-v2-private-test.zip'
        control,base=gate(a.control);candidate,cooked=gate(a.candidate)
        vanilla_sha=pipeline.field.RUNTIME_SHA;allowed_owner='modFieldFolioInteractions';original=source['interactions']
    else:
        key=subtitle.KEY;gate=subtitle_gate;mod='modQuietEditorialSubtitleShadow';name='QuietEditorial-Subtitle-Shadow-v1-private-test.zip'
        control,base=gate(a.control);candidate,cooked=gate(a.candidate)
        if control.get('control') is not True:raise ValueError('Subtitle unchanged control required')
        vanilla_sha=source['runtime_baselines']['current_hud_subtitles'];allowed_owner=None;original=source['subtitles']
    check_source(candidate,original)
    vanilla=[];owners=[];count=0
    for folder in ('content','Mods','DLC'):
        for bundle in sorted((a.game/folder).rglob('*.bundle')):
            count+=1
            for e in inventory.index(bundle):
                if e['resource']!=key:continue
                e.update(bundle=str(bundle.resolve()),owner='vanilla' if folder=='content' else bundle.relative_to(a.game).parts[1])
                with bundle.open('rb') as f:f.seek(e['offset']);packed=f.read(e['packed'])
                if e['codec']!=1:raise ValueError('Unexpected resource codec')
                raw=zlib.decompress(packed)
                if folder=='content':vanilla.append(raw)
                else:
                    owners.append(dict(owner=e['owner'],bundle=e['bundle'],sha256=audit.sha(raw)))
                    if e['owner']!=allowed_owner:raise ValueError('Unreviewed deployed owner '+e['owner'])
                    if audit.sha(raw)!=source['runtime_baselines']['interactions_v1_deployed']:raise ValueError('Deployed v1 changed')
        if folder!='content' and any((a.game/folder).rglob(key.split('/')[-1])):raise ValueError('Loose resource owner needs review')
    if not vanilla or any(audit.sha(d)!=vanilla_sha for d in vanilla):raise ValueError('Current installed baseline changed')
    if pipeline.critical(base)!=pipeline.critical(vanilla[0]):raise ValueError('Unchanged control differs from current runtime')
    if a.module=='interactions':
        textures=pipeline.compare_textures(vanilla[0],cooked)
        if any(not r['compressed_payload_identical'] for r in textures):raise ValueError('Full atlas bytes differ')
    else:
        textures=[];subtitle.structure(vanilla[0]);subtitle.structure(cooked)
    for file,info in source['accepted_packages'].items():
        if audit.sha((ROOT/file).read_bytes())!=info['sha256']:raise ValueError('Accepted/archive package changed')
    files={'Mods/'+mod+'/content/'+n:(a.candidate/'packed'/n).read_bytes() for n in ('blob0.bundle','metadata.store')}
    if a.module=='interactions':
        for n in ('OFL-Adobe.txt','FONT-NOTICES.txt'):files['Mods/'+mod+'/'+n]=(ROOT/'build/field-folio-source-v2'/n).read_bytes()
        pins=json.loads((ROOT/'research/field-folio-v1-manifest.json').read_text())['members']
        for n in ('OFL-Adobe.txt','FONT-NOTICES.txt'):
            if audit.sha(files['Mods/'+mod+'/'+n])!=pins['Mods/modFieldFolioInteractions/'+n]:raise ValueError('Attribution changed')
    data=interaction.zipper.archive_bytes(files)
    if data!=interaction.zipper.archive_bytes(dict(reversed(list(files.items())))):raise ValueError('Nondeterministic archive')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or set(z.namelist())!=set(files) or any(z.read(k)!=v for k,v in files.items()):raise ValueError('Archive routing/content differs')
    out.mkdir();target=out/name;target.write_bytes(data)
    report=dict(module=a.module,mod_folder=mod,resource_key=key,zip_path=str(target),zip_sha256=audit.sha(data),zip_bytes=len(data),
        members={k:audit.sha(v) for k,v in files.items()},candidate=candidate,control=control,source_transform=original,
        vanilla_sha256=vanilla_sha,textures=textures,current_owners=owners,scanned_bundles=count,
        accepted_packages_unchanged=True,deterministic_zip=True,exact_zip_readback=True,
        offline_validated=True,runtime_tested=False,installed=False,
        instruction='Disable interaction v1 before enabling v2' if a.module=='interactions' else 'Independent subtitle-only mod')
    (out/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
