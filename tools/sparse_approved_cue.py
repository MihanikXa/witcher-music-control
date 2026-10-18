"""Single accepted cue import proof. All writes confined to ignored pilot output."""
import argparse
import copy
import json
from pathlib import Path
import wave
import xml.etree.ElementTree as ET

import numpy as np

from white_orchard_prepare import build_path, digest
from white_orchard_wwise import Waapi
from white_orchard_sparse import SPEC, D_SPEC, MUSIC, prop, measured_template, validate
from regional_music import graph, context
from white_orchard_state_volume_author import semantic
from white_orchard_compare import read_bank

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/'build/sparse-approved-cue-pilot-v1'
SOURCE=Path(r'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio')
APPROVED=REPO/'build/music-material-selection/five-cue-corrections-v1/audio/S04-a-B.wav'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def verify_accepted():
    selections=read(REPO/'research/85-accepted-private-cue-selections.json')['selections']
    if len(selections)!=24:raise ValueError('Expected24 approvals')
    for s in selections:
        if digest(REPO/s['file'])!=s['sha256']:raise ValueError('Accepted audio changed: '+s['cue'])
    return next(s for s in selections if s['cue']=='S04-a')


def strip_wrapper(pcm,lead,trail):
    if pcm.ndim!=2 or pcm.shape[1]!=2 or trail<=0 or not 0<lead<len(pcm)-trail:raise ValueError('Invalid wrapper bounds')
    if np.any(pcm[:lead]) or np.any(pcm[-trail:]):raise ValueError('Nonzero samples in claimed wrapper')
    return pcm[lead:-trail].copy()


def prepare_audio():
    selection=verify_accepted()
    if digest(APPROVED)!=selection['sha256']:raise ValueError('Wrong accepted source')
    folder=ROOT/'media';folder.mkdir(parents=True,exist_ok=False)
    with wave.open(str(APPROVED),'rb') as w:
        params=w.getparams();payload=w.readframes(w.getnframes())
    if (params.nchannels,params.sampwidth,params.framerate,params.nframes)!=(2,2,48000,2200800):raise ValueError('Unexpected approved PCM')
    pcm=np.frombuffer(payload,dtype='<i2').reshape(-1,2)
    trimmed=strip_wrapper(pcm,96000,144000)
    path=folder/'WMC_S04a_approved.wav'
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(trimmed.tobytes())
    with wave.open(str(path),'rb') as w:assert w.readframes(w.getnframes())==payload[96000*4:-144000*4]
    nonzero=np.flatnonzero(np.any(trimmed!=0,axis=1))
    rms=[]
    for a in range(0,len(trimmed),2400):
        v=trimmed[a:a+2400].astype(float)/32768
        rms.append(float(20*np.log10(max(float(np.sqrt(np.mean(v*v))),1e-12))))
    proof=dict(schema=1,cue='S04-a',approved_sha256=selection['sha256'],approved_frames=len(pcm),
        removed_lead_frames=96000,removed_trail_frames=144000,retained_frames=len(trimmed),
        authoring_sha256=digest(path),pcm_slice_exact=True,rate=48000,channels=2,bits=16,
        entry_ms=0.,dry_stop_exit_ms=30850.,duration_ms=len(trimmed)/48,
        baked_post_exit_ms=len(trimmed)/48-30850,first_nonzero_seconds=int(nonzero[0])/48000,
        last_nonzero_seconds=int(nonzero[-1])/48000,rms50ms_dbfs=rms,
        peak=float(np.max(np.abs(trimmed.astype(float)))/32768),
        no_dsp=True,wrapper_is_audition_context=True,source_clock_start=3.15,source_clock_dry_stop=34.)
    (folder/'audio-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    return proof


def validate_import(before,after,proof,media,project):
    """Independent add-node check plus exact restoration of the earlier sparse source."""
    prior,_,_=graph(before);current,parents,_=graph(after)
    added=set(current)-set(prior);removed=set(prior)-set(current)
    if removed:raise ValueError('Removed original objects')
    segments=[n for n in after.iter('MusicSegment') if n.get('ID') not in prior]
    if len(segments)!=1:raise ValueError('Exactly one new segment required')
    seg=segments[0];selected=current[read(SPEC)['selected']]
    if parents[seg].tag!='ChildrenList' or parents[parents[seg]] is not selected:raise ValueError('Wrong physical ancestry')
    if seg.get('Name')!='WMC_S04a_approved':raise ValueError('Wrong imported cue')
    tracks=seg.findall('./ChildrenList/MusicTrack');sources=seg.findall('.//AudioFileSource');clips=seg.findall('.//MusicClip')
    if len(tracks)!=1 or len(sources)!=1 or len(clips)!=1:raise ValueError('Expected one complete track/source/clip')
    allowed={n.get('ID') for n in seg.iter() if n.get('ID') and n.tag!='ObjectRef' and n.tag!='AudioSourceRef'}
    if added-allowed:raise ValueError('Unexpected additions outside cue subtree')
    ids=[n.get('ID') for n in seg.iter() if n.get('ID') and n.tag not in ('ObjectRef','AudioSourceRef')]
    if len(ids)!=len(set(ids)) or set(ids)&set(prior):raise ValueError('GUID collision')
    shorts=[n.get('ShortID') for n in seg.iter() if n.get('ShortID')]
    original_shorts={n.get('ShortID') for n in before.iter() if n.get('ShortID')}
    if len(shorts)!=len(set(shorts)) or set(shorts)&original_shorts:raise ValueError('ShortID collision')
    mediaids=[n.get('ID') for n in sources[0].iter('MediaID')]
    original_media={n.get('ID') for n in before.iter('MediaID')}
    if len(mediaids)!=1 or set(mediaids)&original_media:raise ValueError('Media ID collision')
    source_file=project.parent/'Originals/SFX'/sources[0].findtext('AudioFile')
    if digest(source_file)!=media['authoring_sha256']:raise ValueError('Imported PCM differs from derived source')
    cues=seg.findall('./ObjectLists/ObjectList[@Name="Cues"]//MusicCue')
    if len(cues)!=2 or sorted(prop(c,'TimeMs') for c in cues)!=[0,30850]:raise ValueError('Wrong entry/exit markers')
    if prop(seg,'EndPosition')!=media['duration_ms'] or prop(clips[0],'EndTrimOffset')!=media['duration_ms']:
        raise ValueError('Baked tail clipped or stretched')
    if prop(clips[0],'BeginTrimOffset') or prop(clips[0],'PlayAt') or prop(tracks[0],'Volume') or prop(seg,'Volume'):
        raise ValueError('Unexpected timing/gain')
    if clips[0].find('AudioSourceRef').get('ID')!=sources[0].get('ID'):raise ValueError('Wrong clip source')
    check_new_fields(seg,tracks[0],sources[0],clips[0],cues,media)
    restored=copy.deepcopy(after);objects,pp,_=graph(restored)
    new=objects[seg.get('ID')];pp[new].remove(new)
    music_item=next(n for n in restored.iter('MusicPlaylistItem') if n.get('ID')==read(SPEC)['music_item'])
    old_item=next(n for n in before.iter('MusicPlaylistItem') if n.get('ID')==read(SPEC)['music_item'])
    ref=music_item.find('./ReferenceList/Reference[@Name="Segment"]/ObjectRef')
    if ref.get('ID')!=seg.get('ID'):raise ValueError('New cue not selected')
    ref.attrib.clear();ref.attrib.update(old_item.find('./ReferenceList/Reference[@Name="Segment"]/ObjectRef').attrib)
    if semantic(restored)!=semantic(before):raise ValueError('Undeclared original source/transition/event edit')
    return dict(passed=True,segment=dict(id=seg.get('ID'),short_id=int(seg.get('ShortID'))),
        track=dict(id=tracks[0].get('ID'),short_id=int(tracks[0].get('ShortID'))),
        source_id=sources[0].get('ID'),media_id=int(mediaids[0]),added_guids=sorted(added),
        exact_restoration=True,source_sha256=digest(source_file),musical_exit_ms=30850.,duration_ms=media['duration_ms'])


def check_new_fields(seg,track,source,clip,cues,media):
    """Explicit new-node semantics; removing an opaque subtree is not validation."""
    tags={'MusicSegment','MusicTrack','AudioFileSource','MusicTrackSequence','MusicClip','MusicCue','MusicTransition',
        'PropertyList','Property','ReferenceList','Reference','ObjectRef','Custom','ChildrenList','TransitionInfo',
        'ObjectLists','ObjectList','Local','AudioSourceRef','Language','AudioFile','MediaIDList','MediaID'}
    if any(n.tag not in tags for n in seg.iter()):raise ValueError('Unrecognized imported layout')
    if any(n.get('Name') not in {'Cues','Sequences','Clips'} for n in seg.iter('ObjectList')):raise ValueError('Unrecognized cue object list')
    def fields(node,expected):
        def value(p):
            v=p.get('Value',p.findtext('./ValueList/Value'))
            return v=='True' if p.get('Type')=='bool' else float(v)
        actual={p.get('Name'):value(p) for p in node.findall('./PropertyList/Property')}
        if len(actual)!=len(node.findall('./PropertyList/Property')) or actual!=expected:
            raise ValueError('Unapproved imported '+node.tag+' properties')
    fields(seg,{'EndPosition':media['duration_ms'],'OverrideClockSettings':1,'Tempo':60});fields(track,{})
    fields(source,{'LoopBegin':-.001,'LoopEnd':-.001,'TrimBegin':-.001,'TrimEnd':-.001})
    if source.findtext('Language')!='SFX':raise ValueError('Wrong source language')
    fields(clip,{'EndTrimOffset':media['duration_ms'],'FadeInMode':0,'FadeOutMode':0})
    for cue in cues:fields(cue,{'CueType':1,'TimeMs':30850.} if prop(cue,'CueType')==1 else {})
    if any(seg.find('.//'+tag) is not None for tag in ('StateInfo','RTPCList','Effects','EffectSlot')):
        raise ValueError('Unexpected cue processing or dependency')
    conv=seg.find('./ReferenceList/Reference[@Name="Conversion"]/ObjectRef')
    if conv is None or conv.get('ID')!='{CD5FEB1F-5340-419B-B846-9C660D7A1B24}':raise ValueError('New conversion dependency')
    for node in (seg,track):
        output=node.find('./ReferenceList/Reference[@Name="OutputBus"]/ObjectRef')
        if output is None or output.get('ID')!='{1514A4D8-1DA6-412A-A17E-75CA0C2149F3}':raise ValueError('Unexpected bus dependency')
    if len(seg.findall('./ReferenceList/Reference'))!=2 or len(track.findall('./ReferenceList/Reference'))!=2:raise ValueError('Unexpected new references')
    transition=track.find('./ReferenceList/Reference[@Name="TransitionRoot"]/Custom/MusicTransition')
    if transition is None or transition.find('ChildrenList') is not None:raise ValueError('Imported track transition changed')
    fields(transition,{'IsFolder':1})
    if list(transition.find('TransitionInfo')):raise ValueError('Imported track transition processing')


def collision_audit(project,banks):
    project=build_path(project);before=ET.parse(project.parent/'pre-import-music.xml').getroot()
    after=ET.parse(project.parent/MUSIC).getroot();a,_,_=graph(before);b,_,_=graph(after)
    nodes=[n for i,n in b.items() if i not in a]
    guids={n.get('ID') for n in nodes if n.get('ID','').startswith('{')}
    short={int(n.get('ShortID')) for n in nodes if n.get('ShortID')}
    media={int(n.get('ID')) for n in nodes if n.tag=='MediaID'}
    seen=0
    for path in SOURCE.rglob('*.wwu'):
        tree=ET.parse(path);seen+=1
        for n in tree.iter():
            if n.get('ID') in guids or (n.get('ShortID') and int(n.get('ShortID')) in short):raise ValueError('Original project identity collision')
            if n.tag=='MediaID' and int(n.get('ID')) in media:raise ValueError('Original source media collision')
    bankcount=0
    for path in sorted(banks.glob('*.bnk')):
        bank=read_bank(path);bankcount+=1
        if short&set(bank['records']):raise ValueError('Native HIRC collision')
        import struct
        # Negative check also covers native streamed source-ID references whose
        # media are not embedded in DIDX. Source IDs are v150 little-endian u32.
        if any(struct.pack('<I',mid) in body for mid in media for kind,body in bank['records'].values()):
            raise ValueError('Possible native streamed/media reference collision; decode before proceeding')
        idx=bank['payload'].get('DIDX',b'')
        if len(idx)%12:raise ValueError('Invalid native DIDX')
        if media&{struct.unpack_from('<I',idx,i)[0] for i in range(0,len(idx),12)}:raise ValueError('Native media collision')
    if seen!=1508 or bankcount<8:raise ValueError('Incomplete identity scope')
    return dict(passed=True,original_work_units=seen,native_banks=bankcount,new_guids=sorted(guids),new_short_ids=sorted(short),new_media_ids=sorted(media),
        new_media_id_absent_from_all_native_hirc_bodies=True)


def author(project,port):
    project=build_path(project);api=Waapi(port)
    if project.parent.name!='validation' or Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve()!=project:raise ValueError('Wrong isolated project')
    media=read(ROOT/'media/audio-proof.json');verify_accepted()
    if (project.parent/'approved-cue-source-gate.json').exists():raise FileExistsError('Preserve completed import')
    before=ET.parse(project.parent/MUSIC).getroot()
    original,states=context(SOURCE,read(D_SPEC))
    base=validate(original,before,read(SPEC),read(D_SPEC),'sparse',states,measured_template(read(D_SPEC)))
    (project.parent/'pre-import-music.xml').write_bytes((project.parent/MUSIC).read_bytes())
    spec=read(SPEC);selected=api.call('ak.wwise.core.object.get',{'from':{'id':[spec['selected']]}},{'return':['path']})['return'][0]
    objpath=selected['path']+r'\<MusicSegment>WMC_S04a_approved\<MusicTrack>WMC_S04a_approved'
    imported=api.call('ak.wwise.core.audio.import',{'importOperation':'createNew','autoAddToSourceControl':False,'autoCheckOutToSourceControl':False,
        'imports':[{'objectPath':objpath,'audioFile':str(ROOT/'media/WMC_S04a_approved.wav'),'importLanguage':'SFX'}]},
        {'return':['id','name','type','shortId','path']})
    (project.parent/'import-result.json').write_text(json.dumps(imported,indent=2)+'\n')
    api.call('ak.wwise.core.project.save')
    tree=ET.parse(project.parent/MUSIC);segment=next(n for n in tree.iter('MusicSegment') if n.get('Name')=='WMC_S04a_approved')
    api.call('ak.wwise.core.object.setProperty',{'object':segment.get('ID'),'property':'EndPosition','value':media['duration_ms']})
    api.call('ak.wwise.core.object.setProperty',{'object':segment.get('ID'),'property':'OverrideClockSettings','value':True})
    api.call('ak.wwise.core.object.setProperty',{'object':segment.get('ID'),'property':'Tempo','value':60})
    for cue in segment.findall('./ObjectLists/ObjectList[@Name="Cues"]//MusicCue'):
        api.call('ak.wwise.core.object.setProperty',{'object':cue.get('ID'),'property':'TimeMs','value':30850 if prop(cue,'CueType')==1 else 0})
    api.call('ak.wwise.core.object.setReference',{'object':spec['music_item'],'reference':'Segment','value':segment.get('ID')})
    api.call('ak.wwise.core.project.save')
    after=ET.parse(project.parent/MUSIC).getroot();result=validate_import(before,after,{},media,project)
    inputs=read(project.parent/'input-manifest.json')
    for x in inputs['originals']:
        if digest(project.parent/x['relative_path'])!=x['sha256']:raise ValueError('Original audio changed')
    changed=[p.relative_to(project.parent).as_posix() for p in project.parent.rglob('*.wwu')
        if digest(p)!=digest(SOURCE/p.relative_to(project.parent))]
    if len(list(project.parent.rglob('*.wwu')))!=1508 or set(changed)-{MUSIC.as_posix(),'Control Surface Sessions/Default Work Unit.wwu'}:raise ValueError('Unrelated WWU change')
    result.update(original_sparse_gate=base,work_units=1508,original_audio=len(inputs['originals']),changed_work_units=changed,accepted24_preserved=True,
        authored_source_sha256=digest(project.parent/MUSIC),clock=dict(override=True,tempo=60,time_signature=[4,4]))
    (project.parent/'approved-cue-source-gate.json').write_text(json.dumps(result,indent=2)+'\n')
    (project.parent/'authored-music.xml').write_bytes((project.parent/MUSIC).read_bytes())
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audio',action='store_true');p.add_argument('--project',type=Path);p.add_argument('--port',type=int,default=18292);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--collision-banks',type=Path);a=p.parse_args()
    ROOT=build_path(a.root)
    if a.collision_banks:result=collision_audit(a.project,a.collision_banks)
    elif a.audio:result=prepare_audio()
    else:result=author(a.project,a.port)
    print(json.dumps(result))
