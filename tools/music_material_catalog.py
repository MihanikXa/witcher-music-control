"""Read-only native/MP material joins. Metadata only; never runs reference code."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from music_comparison_decode import music,track
from music_material_opus import inspect
from music_region_inventory import REGIONS
from regional_baseline_reference import cache_index
from regional_music import graph,ancestors
from white_orchard_compare import read_bank
from white_orchard_prepare import build_path,digest

REGION_BANK={'Velen, Novigrad & Oxenfurt':'music_nomansgrad','White Orchard':'music_prologue',
 'Skellige':'music_skellige','Toussaint':'music_toussaint','Kaer Morhen':'music_kaer_morhen',
 'Vizima':'music_wyzima_castle','Isle of Mists':'music_misty_island','The Spiral':'music_spiral'}


def native_catalog(source,banks):
    tree=ET.parse(source/'Interactive Music Hierarchy/music.wwu')
    objects,parents,_=graph(tree);by_short={int(n.get('ShortID')):n for n in objects.values() if n.get('ShortID')}
    media=defaultdict(list)
    for node in tree.iter('AudioFileSource'):
        for m in node.findall('./MediaIDList/MediaID'):
            media[int(m.get('ID'))].append(dict(file=node.findtext('AudioFile'),guid=node.get('ID')))
    approved=set()
    for name in ('white-orchard-D','nomansgrad-expanded-v2','skellige-v1','kaer-morhen-v1','toussaint-v1'):
        manifest=json.loads((Path(__file__).resolve().parents[1]/'src/wwise/regions'/f'{name}.json').read_text())
        approved.update(manifest['static_targets'])
    result=[];errors=[]
    for bank in REGIONS:
        b=read_bank(banks/(bank+'.bnk'))
        for ident,(kind,body) in b['records'].items():
            if kind!=10:continue
            segment=music(10,body);tracks=[]
            for tid in segment['children']:
                try:td=track(b['records'][tid][1])
                except (ValueError,KeyError) as e:
                    errors.append(dict(bank=bank,track=tid,error=str(e)));continue
                n=by_short.get(tid)
                chain=[dict(name=a.get('Name'),guid=a.get('ID'),type=a.tag,short_id=a.get('ShortID'))
                       for a in ancestors(n,parents) if a.get('ShortID')] if n is not None else []
                tracks.append(dict(id=tid,name=n.get('Name') if n is not None else None,
                    ancestry=chain,sources=[dict(s,originals=media[s['id']]) for s in td['sources']],
                    clips=td['clips'],rtpc=td['rtpc'],automation=td['automation'],
                    reviewed_generic=any(a['guid'] in approved for a in chain)))
            n=by_short.get(ident)
            result.append(dict(bank=bank,segment=ident,name=n.get('Name') if n is not None else None,
                duration_ms=segment['duration_ms'],markers=segment['markers'],meter=segment['meter'],tracks=tracks))
    return dict(segments=result,decode_errors=errors,music_source_sha256=digest(source/'Interactive Music Hierarchy/music.wwu'))


def mp_catalog(audit):
    index_path=audit/'main/mods/modMusicPlus/editor/index.json'
    index=json.loads(index_path.read_text(encoding='utf-8'));rows={};errors=[]
    for region,bank in REGION_BANK.items():
        b=read_bank(audit/'banks'/(bank+'.bnk'))
        for pi,p in enumerate(index['playlists']):
            if p['region']!=region:continue
            if not p['pools']:errors.append(dict(playlist=pi,error='No representative pool'));continue
            segments=defaultdict(list)
            for pool in p['pools']:
                for item in pool['i']:
                    if not segments[item[0]]:segments[item[0]].append(item[3])
            for ti,t in enumerate(p['tracks']):
                if t['vanilla']:continue
                key='|'.join(sorted(w for group in t['wems'] for w in group))
                row=rows.setdefault(key,dict(name=t['name'],source=t['source'],wems=t['wems'],editor_ms=t['dur'],assignments=[]))
                expected={int(w.removesuffix('.wem')) for g in t['wems'] for w in g}
                actual=set();decoded=[]
                for sid in segments[ti]:
                    kind,body=b['records'][sid]
                    if kind!=10:raise ValueError('Editor segment is not segment')
                    s=music(kind,body);tracks=[]
                    for tid in s['children']:
                        td=track(b['records'][tid][1]);actual.update(x['id'] for x in td['sources'])
                        tracks.append(dict(id=tid,sources=td['sources'],clips=td['clips'],rtpc=td['rtpc']))
                    decoded.append(dict(segment=sid,duration_ms=s['duration_ms'],markers=s['markers'],tracks=tracks))
                if actual!=expected:errors.append(dict(playlist=pi,track=ti,expected=sorted(expected),actual=sorted(actual)))
                row['assignments'].append(dict(playlist_index=pi,track_index=ti,region=region,
                    title=p['title'],folder=p['folder'],bank=bank,representative_segments=decoded))
    # Four extra sources occur only in diegetic playlists. Retain metadata and
    # state the unjoined Sound/Action layout rather than inventing MusicTracks.
    for pi,p in enumerate(index['playlists']):
        if p['region'] in REGION_BANK:continue
        for ti,t in enumerate(p['tracks']):
            if t['vanilla']:continue
            key='|'.join(sorted(w for group in t['wems'] for w in group))
            row=rows.setdefault(key,dict(name=t['name'],source=t['source'],wems=t['wems'],editor_ms=t['dur'],assignments=[]))
            row['assignments'].append(dict(playlist_index=pi,track_index=ti,region=p['region'],
                title=p['title'],folder=p['folder'],representative_segments=[],
                limitation='Diegetic Sound/Action graph not music-segment joined here'))
    cache=audit/'pack/mods/modMusicPlus/content/soundspc.cache'
    headers={}
    with cache.open('rb') as f:
        entries=cache_index(f)
        for name,(offset,size) in entries.items():
            f.seek(offset);data=f.read(size)
            try:info,_=inspect(data);headers[name]=info
            except (ValueError,KeyError) as e:headers[name]={'error':str(e)}
    return dict(tracks=list(rows.values()),headers=headers,join_errors=errors,
        editor_sha256=digest(index_path),pack_sha256=digest(cache),
        note='Representative segment per track/assignment crosschecked against binary; not every scheduler clone traversed')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','banks','audit','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    result=dict(native=native_catalog(a.source,a.banks),music_plus=mp_catalog(a.audit))
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(native_segments=len(result['native']['segments']),native_errors=len(result['native']['decode_errors']),
        mp_tracks=len(result['music_plus']['tracks']),joins_failed=len(result['music_plus']['join_errors']),
        opus_headers=Counter('error' if 'error' in x else 'supported' for x in result['music_plus']['headers'].values()))))
