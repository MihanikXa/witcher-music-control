"""Two bounded XML experiments, exact reversible source allowlists; no banks.

A: native last-played/last-exit on narrow world returns, explicit rest entry on
the existing combat-return rule. B: conservative local rest-first sequence.
No transition fades, sync, outro segment, global definition or PCM is changed.
"""
import argparse
import copy
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

from sparse_reentry_pilot import ROOT,PRIOR,prepare_worker
from sparse_approved_cue import read,MUSIC,REPO
from white_orchard_prepare import digest,build_path
from white_orchard_state_volume_author import semantic
from regional_music import graph,ancestors

SELECTED='{4A23933D-BE41-4C79-BED2-337D24C605EA}'
GENERAL='{00F2D643-114B-46E4-B5EB-4B78ED19D3A6}'
WORLD='{1A59CC64-141A-45A6-8374-EB823D3E9D4F}'
REGION='{A9E3330C-5726-4E53-8974-7EB1BB7C19E3}'
RETURN='{A79AC940-BEEA-48E2-81EA-BD307F4771D4}'
CAMP_RETURN='{23D85023-3E0B-42E8-AC78-6B23436B4635}'
REST_ITEM='{42F12789-7847-4193-AF93-64D2FEB84C2C}'
MUSIC_ITEM='{E628DC21-010A-49FB-BA2F-DDB4B588857B}'


def setprop(node,name,typ,value):
    props=node.find('PropertyList')
    if props is None:props=ET.Element('PropertyList');node.insert(0,props)
    prop=props.find('Property[@Name="'+name+'"]')
    if prop is None:prop=ET.SubElement(props,'Property',Name=name,Type=typ)
    prop.set('Value',str(value))


def transitions(node):
    return node.find('./ReferenceList/Reference[@Name="TransitionRoot"]/Custom/MusicTransition/ChildrenList')


def build(before,mode,new_ids=None):
    if mode not in ('history-rest','rest-first'):raise ValueError('Unknown bounded candidate')
    after=copy.deepcopy(before);nodes,_,_=graph(after);generated=[];new_ids=iter(new_ids) if new_ids else None
    if mode=='rest-first':
        selected=nodes[SELECTED]
        root=selected.find('./ReferenceList/Reference[@Name="PlaylistRoot"]/Custom/MusicPlaylistItem/ChildrenList')
        if [n.get('ID') for n in root]!=[MUSIC_ITEM,REST_ITEM]:raise ValueError('Wrong approved sequence')
        root[:]=[root[1],root[0]]
    else:
        for parent in (GENERAL,REGION):
            collection=transitions(nodes[parent])
            # Preserve the applicable native curve as well as fade lengths.
            # Region Any/Any uses a different curve from the specific return.
            template=collection[0] if parent==GENERAL else next(n for n in collection if n.get('ID')==CAMP_RETURN)
            rule=copy.deepcopy(template)
            for n in rule.iter():
                if n.get('ID') and n.tag!='ObjectRef':
                    ident=next(new_ids) if new_ids is not None else '{'+str(uuid.uuid4()).upper()+'}'
                    n.set('ID',ident);generated.append(ident)
            for name,val in [('SourceContextType',0 if parent==GENERAL else 2),('DestinationContextType',2),
                             ('DestinationPlaylistJumpTo',2),('DestinationJumpPositionPreset',4)]:
                setprop(rule,name,'int16',val)
            refs=rule.find('ReferenceList')
            source=None
            if parent==REGION:
                source=refs.find('Reference[@Name="SourceContextObject"]/ObjectRef').get('ID')
                rule.remove(refs)
            elif refs is not None:raise ValueError('Expected pristine Any/Any template')
            refs=ET.Element('ReferenceList');rule.insert(list(rule).index(rule.find('TransitionInfo')),refs)
            for name,ident in ([('SourceContextObject',source)] if source else [])+[('DestinationContextObject',SELECTED)]:
                r=ET.SubElement(refs,'Reference',Name=name)
                ET.SubElement(r,'ObjectRef',Name=nodes[ident].get('Name'),ID=ident,WorkUnitID='{6D1D322A-964C-439B-8DAF-402ABC1F2F90}')
            # The explicit native combat rule keeps priority over general history.
            collection.insert(len(collection)-1 if parent==GENERAL else len(collection),rule)
        returned=nodes[RETURN]
        if returned.find('./TransitionInfo/JumpToPlaylistItemRef') is not None:raise ValueError('Already has jump')
        setprop(returned,'DestinationJumpPositionPreset','int16',0)
        setprop(returned,'DestinationPlaylistJumpTo','int16',1)
        returned.find('TransitionInfo').insert(0,ET.Element('JumpToPlaylistItemRef',Name='',ID=REST_ITEM))
    if new_ids is not None:
        try:next(new_ids);raise ValueError('Unused identity pins')
        except StopIteration:pass
    return after,generated


def validate(before,after,mode,ids):
    expected,generated=build(before,mode,ids)
    if generated!=ids or semantic(expected)!=semantic(after):raise ValueError('Undeclared source change')
    old,_,_=graph(before);new,_,_=graph(after)
    if set(new)-set(old)!=set(ids) or set(old)-set(new):raise ValueError('Unexpected graph additions/removals')
    _,parents,_=graph(after)
    for owner in after.iter('MusicSwitchContainer'):
        collection=transitions(owner)
        if collection is None:continue
        for rule in collection:
            if rule.get('ID') not in set(ids)|{RETURN}:continue
            for ref in rule.findall('./ReferenceList/Reference/ObjectRef'):
                target=new.get(ref.get('ID'))
                if target is None or target is owner or owner not in ancestors(target,parents):
                    raise ValueError('Transition context must be a real descendant, never its owning switch')
    # Existing original PCM segment/track, combat/outro, clock, gains, event and
    # selector definitions must remain exact through the complete reconstruction.
    return dict(passed=True,mode=mode,added_guids=ids,complete_source_reconstruction=True,
                new_source_audio=False,native_fades_sync_outro_unchanged=True)


def author(name,mode):
    project=prepare_worker(name);path=project.parent/MUSIC
    before=ET.parse(path).getroot();after,ids=build(before,mode)
    # Check against all WWU GUIDs, not just the selected regional hierarchy.
    existing=set()
    for p in project.parent.rglob('*.wwu'):
        existing.update(n.get('ID') for n in ET.parse(p).iter() if n.get('ID'))
    if set(ids)&existing or len(set(ids))!=len(ids):raise ValueError('Identity collision')
    proof=validate(before,after,mode,ids)
    ET.ElementTree(after).write(path,encoding='utf-8',xml_declaration=True)
    proof.update(before_sha256=digest(PRIOR/'generation'/MUSIC),after_sha256=digest(path))
    (project.parent/'reentry-source-gate.json').write_text(json.dumps(proof,indent=2)+'\n')
    (project.parent/'authored-music.xml').write_bytes(path.read_bytes())
    meta=read(project.parent/'reentry-input.json');meta.update(music_sha256=digest(path),candidate=mode)
    (project.parent/'reentry-input.json').write_text(json.dumps(meta,indent=2)+'\n')
    return project


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['history-rest','rest-first'],required=True)
    a=p.parse_args();print(author(a.name,a.mode))
