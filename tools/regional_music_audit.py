"""Read-only whole-project consumers and native membership; no intent heuristics."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from regional_music import graph, ancestors, MUTED
from music_region_inventory import inventory, properties
from white_orchard_compare import read_bank
from white_orchard_prepare import build_path, digest


def audit(source, native, regions):
    music=ET.parse(source/'Interactive Music Hierarchy/music.wwu')
    events=ET.parse(source/'Events/music.wwu')
    data=inventory(music.getroot(),events.getroot(),ET.parse(source/'SoundBanks/music.wwu').getroot())
    objects,parents,consumers=graph(music)
    event_index={};event_count=0
    for path in sorted((source/'Events').rglob('*.wwu')):
        event_count+=1
        for event in ET.parse(path).iter('Event'):
            row={'file':path.relative_to(source).as_posix(),'event_id':event.get('ID'),
                 'actions':[{'properties':properties(a),'targets':[r.get('ID') for r in a.iter('ObjectRef')]}
                            for a in event.findall('./ChildrenList/Action')]}
            for ref in event.iter('ObjectRef'):event_index.setdefault(ref.get('ID'),[]).append(row)
    results=[]
    all_audio={}
    for node in music.iter('MusicPlaylistContainer'):
        for audio in {a.text for a in node.iter('AudioFile')}:
            all_audio.setdefault(audio,[]).append(node.get('ID'))
    for region in data['regions']:
        if region['name'] not in regions:continue
        bank=read_bank(native/(region['name']+'.bnk'))
        member={int(k) for k in bank['records']}
        targets=[]
        for item in region['playlists']:
            node=objects[item['id']]
            descendants={n.get('ID') for n in node.iter() if n.get('ID') and not n.tag.endswith('Ref')}
            uses=consumers.get(item['id'],[])
            nrows=sum(bool(set(path)&MUTED) for _,path in uses)
            if not nrows and int(item['short_id']) in member:continue
            physical=next(n for n in list(ancestors(node,parents))[1:] if n.get('ShortID'))
            transitions=[]
            for ref in music.iter('TransitionObjectRef'):
                if ref.get('ID') not in descendants:continue
                rule=next(n for n in ancestors(ref,parents) if n.tag=='MusicTransition')
                transitions.append({'target_id':ref.get('ID'),'rule':ET.tostring(rule,encoding='unicode')})
            targets.append(dict(item,noncombat_rows=nrows,native_present=int(item['short_id']) in member,
                parent_id=physical.get('ID'),parent_short_id=int(physical.get('ShortID')),
                selector_consumers=[{'selector_id':sid,'selector_short_id':objects[sid].get('ShortID'),'states':list(path)} for sid,path in uses],
                all_event_descendant_consumers=[e for ident in descendants for e in event_index.get(ident,[])],
                transition_consumers=transitions,
                reused_media={a:all_audio[a] for a in item['audio_files'] if len(all_audio[a])>1}))
        results.append(dict(region,reviewed_targets=targets,native_sha256=bank['sha256'],native_hirc_count=len(member)))
    if len(results)!=len(set(regions)):raise ValueError('Missing or duplicate requested region')
    return {'source_music_sha256':digest(source/'Interactive Music Hierarchy/music.wwu'),
            'event_work_units':event_count,'regions':results,'intent_not_automatically_classified':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('source','native','output'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--regions',nargs='+',required=True);a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    result=audit(a.source,a.native,a.regions)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({r['name']:len(r['reviewed_targets']) for r in result['regions']}))
