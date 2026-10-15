"""Complete-context static-only batches; no licence access or deployment.

Every manifest remains independently reviewed. The batch gate reverses every
other declared edit before invoking the existing regional semantic gate, then
restores the whole union and requires pristine source semantics.
"""
import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from regional_music import MUSIC, context, graph, plan, validate_source, validate_event_directory
from white_orchard_state_volume_author import semantic
from white_orchard_prepare import build_path, digest, prepare, stage_original


def restore_volume(node, original):
    props = node.find('PropertyList')
    if props is not None:
        for prop in list(props):
            if prop.tag == 'Property' and prop.get('Name') == 'Volume':
                props.remove(prop)
    old = original.find("./PropertyList/Property[@Name='Volume']")
    if old is not None:
        if props is None:
            raise ValueError('Missing original property list')
        props.append(copy.deepcopy(old))
    elif props is not None and not len(props) and original.find('PropertyList') is None:
        node.remove(props)


def set_static_volume(node):
    props=node.find('PropertyList')
    if props is None:
        props=ET.Element('PropertyList')
        # Wwise's XSD requires properties before references/children/positioning.
        node.insert(0,props)
    prop=props.find("Property[@Name='Volume']")
    if prop is None:prop=ET.SubElement(props,'Property',Name='Volume',Type='Real64')
    values=prop.findall('./ValueList/Value')
    if values:
        if len(values)!=1 or values[0].attrib or 'Value' in prop.attrib:
            raise ValueError('Unsupported qualified/duplicate Volume representation')
        values[0].text='-200'
    else:prop.set('Value','-200')


def batch_semantics(original, candidate, specs, states):
    if not specs or len({s['region'] for s in specs}) != len(specs):
        raise ValueError('Empty or duplicate region batch')
    before, _, _ = graph(original)
    owners = {}
    for spec in specs:
        if spec['state_scopes']:
            raise ValueError('Batch supports static-only manifests')
        plan(original, spec, states)
        for ident in spec['static_targets']:
            if ident in owners:
                raise ValueError('Overlapping batch edit')
            owners[ident] = spec['region']
    proofs = {}
    for spec in specs:
        regional = copy.deepcopy(candidate)
        objects, _, _ = graph(regional)
        for ident in spec['static_targets']:
            prop=objects[ident].find("./PropertyList/Property[@Name='Volume']")
            expected_node=copy.deepcopy(before[ident]);set_static_volume(expected_node)
            expected=expected_node.find("./PropertyList/Property[@Name='Volume']")
            if (prop is None or ('Value' in prop.attrib and len(prop))
                    or semantic(prop)!=semantic(expected)):
                raise ValueError('Unexpected batch Volume property layout')
        for ident, owner in owners.items():
            if owner != spec['region']:
                restore_volume(objects[ident], before[ident])
        proofs[spec['region']] = validate_source(original, regional, spec, states, None)
    restored = copy.deepcopy(candidate)
    objects, _, _ = graph(restored)
    for ident in owners:
        restore_volume(objects[ident], before[ident])
    if semantic(restored) != semantic(original):
        raise ValueError('Batch union restoration differs from pristine source')
    return {'passed': True, 'regions': proofs, 'static_targets': len(owners),
            'all_other_music_semantics_exact': True}


def batch_context(source, specs):
    """Read shared XML once, but require every manifest's own exact pins."""
    original,states=context(source,specs[0])
    hashes={MUSIC.as_posix():digest(source/MUSIC)}
    for spec in specs:
        if (spec['facts']['original_music_sha256']!=hashes[MUSIC.as_posix()]
                or spec['game_state_group']!=specs[0]['game_state_group']):
            raise ValueError('Inconsistent batch music/State context')
        for relative,expected in spec['facts'].get('input_hashes',{}).items():
            if relative not in hashes:hashes[relative]=digest(source/relative)
            if hashes[relative]!=expected:raise ValueError('Pinned batch input changed: '+relative)
    return original,states


def source_gate(source, project, manifests):
    specs = [json.loads(p.read_text(encoding='utf-8')) for p in manifests]
    original, states = batch_context(source, specs)
    for spec in specs:
        validate_event_directory(original, source, spec)
    result = batch_semantics(original, ET.parse(project / MUSIC).getroot(), specs, states)
    inputs = json.loads((project/'input-manifest.json').read_text())
    units = {x['relative_path'].replace('\\', '/'): x['sha256'] for x in inputs['inputs'] if x['relative_path'].endswith('.wwu')}
    actual = {p.relative_to(project).as_posix(): p for p in project.rglob('*.wwu')}
    if len(units) != 1508 or set(units) != set(actual):
        raise ValueError('Incomplete batch authoring context')
    for rel, sha in units.items():
        if digest(source/rel) != sha or (rel != MUSIC.as_posix() and digest(actual[rel]) != sha):
            raise ValueError('Unrelated/installed work unit changed: '+rel)
    objects,_,_=graph(original)
    required = {a.text for spec in specs for a in objects[spec['facts']['root']['id']].iter('AudioFile')}
    pinned = {x['relative_path'].replace('\\', '/'): x for x in inputs['originals']}
    if not {'Originals/SFX/'+a.replace('\\', '/') for a in required} <= set(pinned):
        raise ValueError('Missing required regional audio inputs')
    for rel, item in pinned.items():
        if digest(source/rel) != item['sha256'] or digest(project/rel) != item['sha256']:
            raise ValueError('Original audio changed')
    result.update(complete_work_units=1508, original_audio_unchanged=True,
                  original_nonmusic_units_unchanged=True, global_definitions_unchanged=True,
                  event_work_units_reviewed=len(list((source/'Events').rglob('*.wwu'))),
                  candidate_music_sha256=digest(project/MUSIC),
                  manifest_sha256s={s['region']: digest(p) for s,p in zip(specs, manifests)},
                  audio_inputs=len(pinned), banks_generated=False, deployed=False)
    return result


def prepare_batch(source, project, regions, pool=None):
    if not regions or len(set(regions)) != len(regions):
        raise ValueError('Explicit unique region list required')
    prepare(source, project, True, regions[0], pool)
    inputs=json.loads((project/'input-manifest.json').read_text())
    music=ET.parse(source/MUSIC)
    existing={x['relative_path'].replace('\\','/') for x in inputs['originals']}
    for region in regions[1:]:
        nodes=[n for n in music.iter('MusicSwitchContainer') if n.get('Name')==region]
        if len(nodes)!=1:raise ValueError('Unknown/duplicate regional root')
        for audio in sorted({a.text for a in nodes[0].iter('AudioFile')}):
            rel=Path('Originals/SFX')/audio.replace('\\','/')
            if rel.as_posix() in existing:continue
            sha=stage_original(source,project/rel,rel,pool)
            inputs['originals'].append({'relative_path':str(rel),'sha256':sha,'bytes':(source/rel).stat().st_size})
            existing.add(rel.as_posix())
    inputs['batch_regions']=regions
    (project/'input-manifest.json').write_text(json.dumps(inputs,indent=2)+'\n')
    return {'work_units':1508,'audio_inputs':len(existing),'regions':regions}


def author_static(source, project, manifests, port):
    from white_orchard_wwise import Waapi
    project=build_path(project)
    if digest(project/MUSIC)!=digest(source/MUSIC):raise ValueError('Fresh pristine music source required')
    specs=[json.loads(p.read_text(encoding='utf-8')) for p in manifests]
    original,states=batch_context(source,specs)
    # Validate pristine full context and every policy before writing anything.
    for spec in specs:
        plan(original,spec,states);validate_event_directory(original,source,spec)
        if spec['state_scopes']:raise ValueError('Static-only batch required')
    units={p.relative_to(project).as_posix():digest(p) for p in project.rglob('*.wwu')}
    pristine={p.relative_to(source).as_posix():digest(p) for p in source.rglob('*.wwu')}
    if len(units)!=1508 or units!=pristine:raise ValueError('Complete pristine authoring context required')
    api=Waapi(port)
    if (Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve()!=project/'w3_audio.wproj'
            or api.call('ak.wwise.core.getInfo')['version']['build']!=8928):
        raise ValueError('Wrong isolated authoring project/version')
    for spec in specs:
        for ident in spec['static_targets']:
            api.call('ak.wwise.core.object.setProperty',{'object':ident,'property':'Volume','value':-200})
    api.call('ak.wwise.core.project.save')
    return source_gate(source,project,manifests)


def verify_banks(source, project, manifests, job_path, native, sync_ids):
    """One full union source proof, then independent per-bank existing decoders."""
    from regional_music_gate import decoded_preflight, bank_preflight
    from white_orchard_candidate_package import diagnostics
    union=source_gate(source,project,manifests)
    jobs=json.loads(job_path.read_text(encoding='utf-8'))
    specs=[json.loads(p.read_text(encoding='utf-8')) for p in manifests]
    expected={s['region'] for s in specs if s['static_targets']}
    if set(jobs)!=expected:raise ValueError('Bank job set differs from modified manifest set')
    results={}
    for spec in specs:
        region=spec['region']
        if region not in jobs:continue
        job=jobs[region]
        baseline=build_path(job['baseline_banks']);candidate=build_path(job['candidate_banks'])
        native_proof=json.loads(build_path(job['baseline_proof']).read_text())
        from white_orchard_prepare import digest
        if (not native_proof.get('passed') or native_proof.get('region')!=region
                or native_proof.get('generated_sha256')!=digest(baseline/(region+'.bnk'))):
            raise ValueError('Missing/stale independently verified native baseline')
        if diagnostics(baseline)!=diagnostics(candidate):
            raise ValueError('Candidate generation diagnostics differ from reviewed regional baseline')
        proof={k:v for k,v in union.items() if k!='regions'}
        proof['manifest_sha256']=union['manifest_sha256s'][region]
        proof['batch_manifest_sha256s']=union['manifest_sha256s']
        proof['regional_source_proof']=union['regions'][region]
        decoded=decoded_preflight(baseline,candidate,spec,build_path(job['baseline_project']),native,sync_ids,proof)
        bank=bank_preflight(baseline,candidate,spec,decoded)
        if not bank['passed']:raise ValueError('Regional bank preflight failed: '+region)
        proof.update(decoded_fields=decoded,bank_preflight=bank,generation_diagnostics_baseline_exact=True)
        output=build_path(job['output'])
        if output.exists():raise FileExistsError(output)
        output.write_text(json.dumps(proof,indent=2)+'\n')
        results[region]={'passed':True,'proof':str(output),'candidate_sha256':decoded['candidate_sha256']}
    return {'passed':True,'banks':results,'source':union}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--project',type=Path,required=True)
    p.add_argument('--manifests',type=Path,nargs='+');p.add_argument('--prepare-regions',nargs='+')
    p.add_argument('--immutable-originals',type=Path);p.add_argument('--author',action='store_true')
    p.add_argument('--port',type=int,help='Matching isolated WAAPI server required for authoring')
    p.add_argument('--bank-jobs',type=Path);p.add_argument('--native',type=Path);p.add_argument('--sync-identities',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    if a.prepare_regions:result=prepare_batch(a.source,build_path(a.project),a.prepare_regions,a.immutable_originals)
    elif a.bank_jobs:
        if not a.native or not a.sync_identities:p.error('Bank verification requires native banks and sync identities')
        result=verify_banks(a.source,a.project,a.manifests,a.bank_jobs,a.native,json.loads(a.sync_identities.read_text())['guid_short_ids'])
    elif a.author:
        if a.port is None:p.error('Authoring requires the isolated WAAPI port')
        result=author_static(a.source,a.project,a.manifests,a.port)
    else:result=source_gate(a.source,a.project,a.manifests)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
