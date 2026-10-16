"""Bounded native-only sparse experiment; no generation/deployment/licence access.

Only fresh complete ignored workspaces. Does not relax production source gates.
"""
import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from regional_music import graph, ancestors, context, plan, canonical_state, expected_state, validate_source
from white_orchard_prepare import build_path, digest
from white_orchard_state_volume_author import semantic
from white_orchard_transition_author import volume
from white_orchard_wwise import Waapi

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO/'src/wwise/experiments/white-orchard-sparse-v1.json'
D_SPEC = REPO/'src/wwise/regions/white-orchard-D.json'
MUSIC = Path('Interactive Music Hierarchy/music.wwu')


def prop(node, name, default=0):
    p = node.find("./PropertyList/Property[@Name='%s']" % name)
    return float(p.get('Value', p.findtext('./ValueList/Value'))) if p is not None else default


def check_playlist(node, spec):
    root = node.find('./ReferenceList/Reference[@Name="PlaylistRoot"]/Custom/MusicPlaylistItem')
    if root is None or root.get('ID') != spec['playlist_root']:
        raise ValueError('Unexpected playlist root identity')
    leaves = root.findall('./ChildrenList/MusicPlaylistItem')
    if [x.get('ID') for x in leaves] != [spec['music_item'], spec['rest_item']]:
        raise ValueError('Only pinned phrase/rest leaves allowed')
    if prop(root, 'LoopCount', 1) != 0 or prop(root, 'PlayMode') != 0:
        raise ValueError('Expected infinite continuous deterministic sequence')
    for child, target, loops in zip(leaves, (spec['phrase'], spec['rest']), (1, spec['rest_loops'])):
        if (prop(child, 'LoopCount', 1) != loops or prop(child, 'PlaylistItemType') != 1
                or child.find('./ReferenceList/Reference[@Name="Segment"]/ObjectRef').get('ID') != target
                or child.find('ChildrenList') is not None):
            raise ValueError('Unreviewed playlist leaf')


def expected_playlist(original_selected, spec):
    ref=copy.deepcopy(original_selected.find('./ReferenceList/Reference[@Name="PlaylistRoot"]'))
    root=ref.find('./Custom/MusicPlaylistItem')
    children=root.find('ChildrenList')
    children.remove(next(n for n in children if n.get('ID')==spec['removed_group']))
    rest=next(n for n in children if n.get('ID')==spec['rest_item'])
    target=rest.find('./ReferenceList/Reference[@Name="Segment"]/ObjectRef')
    original_rest=next((n for n in original_selected.iter('ObjectRef') if n.get('ID')==spec['rest']),None)
    target.attrib.clear()
    target.attrib.update(original_rest.attrib if original_rest is not None else {'ID':spec['rest']})
    for node,value in ((root,0),(rest,spec['rest_loops'])):
        props=node.find('PropertyList')
        if props is None:props=ET.Element('PropertyList');node.insert(0,props)
        field=props.find("Property[@Name='LoopCount']")
        if field is None:field=ET.SubElement(props,'Property',Name='LoopCount',Type='int16')
        field.set('Value',str(value))
    return ref


def restore_volume(new, old):
    props = new.find('PropertyList')
    field = props.find("Property[@Name='Volume']") if props is not None else None
    if field is not None:
        props.remove(field)
    prior = old.find("./PropertyList/Property[@Name='Volume']")
    if prior is not None:
        if props is None:
            props = ET.SubElement(new, 'PropertyList')
        props.append(copy.deepcopy(prior))
    elif props is not None and not len(props) and old.find('PropertyList') is None:
        new.remove(props)


def validate(original, candidate, spec, d, mode, states, template):
    if mode not in ('native','minimal','sparse'):raise ValueError('Unknown control mode')
    before, parents, consumers = graph(original)
    after, _, _ = graph(candidate)
    selected = before[spec['selected']]
    chain = [n for n in ancestors(selected, parents) if n.tag == 'MusicSwitchContainer']
    if (int(selected.get('ShortID')) != spec['selected_short_id'] or chain[0].get('ID') != spec['parent']
            or len(consumers[spec['selected']]) != 7
            or any(set(path) & {'combat', 'gwent', 'minigames'} for _, path in consumers[spec['selected']])):
        raise ValueError('Unreviewed selection/ancestry/consumer change')
    restored = copy.deepcopy(candidate)
    objects, _, _ = graph(restored)
    scopes = [] if mode == 'native' else ([d['facts']['world']['id']] if mode == 'minimal'
        else [spec['selected']] + spec['other_local_state_scopes'])
    actual_scopes = {i for i,n in after.items() if n.tag in ('MusicPlaylistContainer','MusicSwitchContainer') and n.find('StateInfo') is not None}
    expected_original = {i for i,n in before.items() if n.tag in ('MusicPlaylistContainer','MusicSwitchContainer') and n.find('StateInfo') is not None}
    if actual_scopes != expected_original | set(scopes):
        raise ValueError('Unexpected State gain ancestry')
    local_ids=set();local_short_ids=set()
    original_short_ids={n.get('ShortID') for n in original.iter() if n.get('ShortID')}
    for ident in scopes:
        state = after[ident].find('StateInfo')
        rows = state.findall('./CustomStateList/CustomState')
        names = [r.find('StateRef').get('Name') for r in rows]
        if len(rows) != 25 or len(set(names)) != 25:
            raise ValueError('Expected 25 disjoint local States')
        muted = set(d['muted_states']) - ({'exploration'} if mode == 'sparse' and ident == spec['selected'] else set())
        values={name:-200 if name in muted else 0 for name in states}
        expected=expected_state(template,values,states,d['game_state_group'])
        if canonical_state(state)!=canonical_state(expected):
            raise ValueError('Unexpected State property/group/reference/transition serialization')
        for row in rows:
            local=row.find('CustomState');i,s=local.get('ID'),local.get('ShortID')
            if (i in local_ids or i in before or i in states.values() or s in local_short_ids
                    or s in original_short_ids):raise ValueError('Local State identity collision')
            local_ids.add(i);local_short_ids.add(s)
            if prop(row.find('CustomState'), 'Volume') != (-200 if row.find('StateRef').get('Name') in muted else 0):
                raise ValueError('Unexpected local State value')
        objects[ident].remove(objects[ident].find('StateInfo'))
    static = [] if mode == 'native' else [i for i in d['static_targets'] if mode == 'minimal' or i != spec['selected']]
    for ident in static:
        if volume(after[ident]) != -200:
            raise ValueError('Missing static suppression')
        restore_volume(objects[ident], before[ident])
    if mode == 'sparse':
        if volume(after[spec['selected']]) != volume(selected):
            raise ValueError('Selected phrase remains statically muted')
        check_playlist(after[spec['selected']], spec)
        reference=after[spec['selected']].find('./ReferenceList/Reference[@Name="PlaylistRoot"]')
        if semantic(reference)!=semantic(expected_playlist(selected,spec)):
            raise ValueError('Unapproved playlist fields/IDs/references/order')
        refs = objects[spec['selected']].find('ReferenceList')
        changed = refs.find("Reference[@Name='PlaylistRoot']")
        index = list(refs).index(changed)
        refs.remove(changed)
        refs.insert(index, copy.deepcopy(selected.find('./ReferenceList/Reference[@Name="PlaylistRoot"]')))
    if semantic(restored) != semantic(original):
        raise ValueError('Unexpected source/event/transition/media relationship change')
    return dict(passed=True, mode=mode, scopes=scopes, static=static,
                all_other_music_semantics_exact=True, selected_consumers=consumers[spec['selected']])


def measured_template(d):
    path=REPO/'build/white-orchard-transition-fix/candidate'/MUSIC
    if digest(path)!=d['facts']['template_source_sha256']:
        raise ValueError('Retained D State template fingerprint mismatch')
    return next(n for n in ET.parse(path).iter('MusicSwitchContainer')
                if n.get('ID')==d['facts']['world']['id']).find('StateInfo')


def consumer_closure(original, spec, d, event_trees):
    objects,parents,consumers=graph(original)
    scopes=set(spec['other_local_state_scopes']+[spec['selected']])
    targets=scopes|set(d['static_targets'])
    world=objects[d['facts']['world']['id']]
    for ident in targets:
        if world not in ancestors(objects[ident],parents):raise ValueError('Target outside world ancestry')
        for selector,path in consumers.get(ident,[]):
            if (world not in ancestors(objects[selector],parents)
                    or set(path)&{'combat','combat_monster_hunt','gwent','minigames'}):
                raise ValueError('Protected/shared consumer')
    descendants={ident for ident,node in objects.items()
                 if {n.get('ID') for n in ancestors(node,parents)}&targets}
    if any(r.get('ID') in descendants for r in original.iter('TransitionObjectRef')):
        raise ValueError('Native transition inherits attenuation')
    count=0
    for tree in event_trees:
        count+=1
        if any(r.get('ID') in descendants for r in tree.iter('ObjectRef')):
            raise ValueError('Direct event/descendant consumer')
    return dict(event_work_units=count,transition_conflicts=0,direct_event_conflicts=0,
                reviewed_consumers={i:consumers[i] for i in targets})


def author(project, source, mode, port):
    project = build_path(project)
    if project.parent.name != 'validation':
        raise ValueError('Experimental validation workspace only')
    spec, d = json.loads(SPEC.read_text()), json.loads(D_SPEC.read_text())
    original, states = context(source, d)
    plan(original, d, states)  # Existing D identity and consumer preflight.
    closure=consumer_closure(original,spec,d,(ET.parse(p) for p in sorted((source/'Events').rglob('*.wwu'))))
    units = {p.relative_to(project.parent).as_posix():digest(p) for p in project.parent.rglob('*.wwu')}
    originals = {p.relative_to(source).as_posix():digest(p) for p in source.rglob('*.wwu')}
    if len(units) != 1508 or units != originals:
        raise ValueError('Fresh pristine 1508-work-unit context required')
    audit = project.parent/'sparse-source-gate.json'
    if audit.exists():
        raise FileExistsError(audit)
    api = Waapi(port)
    if (Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve() != project
            or api.call('ak.wwise.core.getInfo')['version']['build'] != 8928):
        raise ValueError('Wrong authoring project/version')
    scopes = [] if mode == 'native' else ([d['facts']['world']['id']] if mode == 'minimal'
        else [spec['selected']] + spec['other_local_state_scopes'])
    for ident in scopes:
        api.call('ak.wwise.core.object.setStateProperties', {'object':ident,'stateProperties':['Volume']})
        api.call('ak.wwise.core.object.setStateGroups', {'object':ident,'stateGroups':[d['game_state_group']]})
    api.call('ak.wwise.core.project.save')
    current = ET.parse(project.parent/MUSIC)
    objects,_,_ = graph(current)
    for ident in scopes:
        muted = set(d['muted_states']) - ({'exploration'} if mode == 'sparse' and ident == spec['selected'] else set())
        for row in objects[ident].findall('./StateInfo/CustomStateList/CustomState'):
            api.call('ak.wwise.core.object.setProperty', {'object':row.find('CustomState').get('ID'),
                'property':'Volume','value':-200 if row.find('StateRef').get('Name') in muted else 0})
    if mode != 'native':
        for ident in d['static_targets']:
            if mode == 'minimal' or ident != spec['selected']:
                api.call('ak.wwise.core.object.setProperty',{'object':ident,'property':'Volume','value':-200})
    if mode == 'sparse':
        api.call('ak.wwise.core.object.delete',{'object':spec['removed_group']})
        api.call('ak.wwise.core.object.setProperty',{'object':spec['playlist_root'],'property':'LoopCount','value':0})
        api.call('ak.wwise.core.object.setReference',{'object':spec['rest_item'],'reference':'Segment','value':spec['rest']})
        api.call('ak.wwise.core.object.setProperty',{'object':spec['rest_item'],'property':'LoopCount','value':spec['rest_loops']})
    api.call('ak.wwise.core.project.save')
    result = validate(original, ET.parse(project.parent/MUSIC).getroot(), spec, d, mode,states,measured_template(d))
    changed = [rel for rel,sha in units.items() if digest(project.parent/rel) != sha]
    if set(changed) - {MUSIC.as_posix(),'Control Surface Sessions/Default Work Unit.wwu'}:
        raise ValueError('Unrelated work unit changed')
    inputs=json.loads((project.parent/'input-manifest.json').read_text())
    if any(digest(project.parent/x['relative_path']) != x['sha256'] for x in inputs['originals']):
        raise ValueError('Original media changed')
    result.update(work_units=1508, original_media=len(inputs['originals']), changed_units=changed,
                  source_sha256=digest(project.parent/MUSIC), experimental_only=True,
                  spec_sha256=digest(SPEC), generated_banks=False,consumer_closure=closure)
    audit.write_text(json.dumps(result,indent=2)+'\n')
    (project.parent/'authored-music.xml').write_bytes((project.parent/MUSIC).read_bytes())
    print(json.dumps(result))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--mode',choices=('native','minimal','sparse'),required=True);p.add_argument('--port',type=int,required=True)
    a=p.parse_args();author(a.project,a.source,a.mode,a.port)
