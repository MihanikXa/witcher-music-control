"""Complete source consumer/source-reuse evidence, without intent heuristics."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from regional_music import context,graph,ancestors,plan,validate_events
from white_orchard_prepare import build_path,digest
from music_region_inventory import entries


def review(source,spec):
    tree,states=context(source,spec);objects,parents,consumers=graph(tree)
    plan(tree,spec,states)
    events=ET.parse(source/'Events/music.wwu');validate_events(tree,events,spec)
    quest=objects[spec['facts']['quest']['id']]
    quest_audio={a.text for a in quest.iter('AudioFile')}
    world=objects[spec['facts']['world']['id']]
    rows=[];coverage={}
    for guid,decision in spec['decisions'].items():
        node=objects[guid]
        descendants={x.get('ID') for x in node.iter() if x.get('ID') and not x.tag.endswith('Ref')}
        uses=[{'selector_id':s,'selector_short_id':objects[s].get('ShortID'),'states':list(p)} for s,p in consumers.get(guid,[])]
        count=sum(bool(set(u['states'])&set(spec['muted_states'])) for u in uses)
        coverage[decision['classification']]=coverage.get(decision['classification'],0)+count
        direct=[e.get('ID') for e in events.iter('Event') if any(r.get('ID') in descendants for r in e.iter('ObjectRef'))]
        transition=[r.get('ID') for r in tree.iter('TransitionObjectRef') if r.get('ID') in descendants]
        audio={a.text for a in node.iter('AudioFile')}
        selectors={u['selector_id'] for u in uses}
        location_values={p['ID'] for e in entries(world) if e['target'] and e['target']['ID'] in selectors for p in e['path']}
        location_events=[]
        for event in events.iter('Event'):
            actions=event.findall('./ChildrenList/Action')
            if not any(r.get('ID') in location_values for a in actions for r in a.findall('./ReferenceList/Reference/ObjectRef')):continue
            location_events.append({'event_id':event.get('ID'),'actions':[{'action_type':a.find("./PropertyList/Property[@Name='ActionType']").get('Value') if a.find("./PropertyList/Property[@Name='ActionType']") is not None else 'default',
                'target_ids':[r.get('ID') for r in a.findall('./ReferenceList/Reference/ObjectRef')]} for a in actions]})
        rows.append({'guid':guid,'short_id':decision['short_id'],'classification':decision['classification'],
            'policy':decision['policy'],'original_volume':decision['original_volume'],'selector_consumers':uses,
            'noncombat_rows':count,'audio_files':sorted(audio),'quest_branch_media_reuse':sorted(audio&quest_audio),
            'direct_audio_events':direct,'native_transition_segments':transition,
            'location_value_ids':sorted(location_values),'location_event_actions':location_events,
            'physical_parent_short_id':next(n.get('ShortID') for n in list(ancestors(node,parents))[1:] if n.get('ShortID'))})
    return {'source_sha256':digest(source/'Interactive Music Hierarchy/music.wwu'),
        'policy_is_not_automatic_intent_classification':True,'coverage_noncombat_rows':coverage,
        'total_noncombat_rows':sum(coverage.values()),'targets':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    result=review(a.source,json.loads(a.manifest.read_text(encoding='utf-8')))
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'coverage':result['coverage_noncombat_rows'],'total':result['total_noncombat_rows']}))
