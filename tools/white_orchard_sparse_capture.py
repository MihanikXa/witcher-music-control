"""Matched sparse/native/Minimal authoring captures with exception-safe cleanup.

No SoundBank generation, game launch, installed writes or licence inspection.
"""
import argparse
import json
from pathlib import Path
import time
import wave
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path, digest
from white_orchard_wwise import Waapi
from white_orchard_state_volume import MUSIC


def cases():
    # Native phrase exit140s/post-exit148s; finite rest ends170s.
    return [
        dict(name='two-cycles', duration=350, actions=[(20,'rtpc','menu_volume_music',50),(35,'rtpc','menu_volume_music',100)]),
        dict(name='combat-music-authored',duration=105,actions=[(6,'state','combat',None),
             (13,'rtpc','threat_rating',35),(19,'rtpc','threat_rating',100),(34,'state','exploration',None),
             (79,'state','dialog_scene',None),(79.1,'event','mus_q001_tavern_conversation',None)]),
        dict(name='combat-rest-early',duration=215,actions=[(151,'state','combat',None),
             (157,'rtpc','threat_rating',35),(163,'rtpc','threat_rating',100),(173,'state','exploration',None)]),
        dict(name='combat-rest-late',duration=230,actions=[(166,'state','combat',None),
             (172,'rtpc','threat_rating',35),(178,'rtpc','threat_rating',100),(188,'state','exploration',None)]),
        dict(name='place-daynight-music',duration=65,actions=[(6,'state','exploration_night',None),
             (12,'state','exploration',None),(20,'event','mus_loc_prologue_nilfgaard_camp',None),
             (32,'event','mus_loc_prologue_village',None),(43,'state','cutscene',None),
             (44,'state','dialog_scene',None),(49,'state','movie',None),(50,'state','music_only',None),
             (54,'state','exploration',None)]),
        dict(name='place-daynight-rest',duration=210,actions=[(151,'state','exploration_night',None),
             (154,'state','exploration',None),(157,'event','mus_loc_prologue_nilfgaard_camp',None),
             (172,'event','mus_loc_prologue_village',None),(186,'state','cutscene',None),
             (187,'state','dialog_scene',None),(191,'state','movie',None),(192,'state','music_only',None),
             (196,'state','exploration',None)]),
        dict(name='authored-master',duration=30,initial_event='mus_q001_tavern_conversation',
             state='dialog_scene',actions=[(8,'rtpc','menu_volume_music',50),(17,'rtpc','menu_volume_music',100)]),
        dict(name='protected-world',duration=30,location='mus_loc_prologue_village_q505',technical_isolation=True,
             actions=[(8,'rtpc','menu_volume_music',50),(17,'rtpc','menu_volume_music',100)]),
        dict(name='gwent',duration=20,state='gwent',actions=[]),
    ]


def supplemental_cases():
    return [dict(name='authored-rest',duration=185,actions=[
        (151,'state','dialog_scene',None),
        (151.1,'event','mus_q001_tavern_conversation',None)])]


def cleanup(api, capture, transports):
    errors=[]
    calls=[('ak.wwise.core.transport.executeAction',{'action':'stop'})]
    if capture:
        calls.append(('ak.wwise.core.profiler.stopCapture',{}))
    for param in ('threat_rating','menu_volume_music'):
        for go in (None,18446744073709551615):
            args={'rtpc':param}
            if go is not None:args['gameObject']=go
            calls.append(('ak.soundengine.resetRTPCValue',args))
    for transport in transports:
        calls.append(('ak.wwise.core.transport.destroy',{'transport':transport}))
    for uri,args in calls:
        try:api.call(uri,args)
        except Exception as exc:errors.append(dict(uri=uri,error=str(exc)))
    return errors


def run(project,port,label,selected=None):
    project=build_path(project)
    api=Waapi(port)
    if project.parent.name!='validation' or Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve()!=project:
        raise ValueError('Exact isolated validation project required')
    if Path(label).name!=label:raise ValueError('Simple label')
    out=project.parent/label
    out.mkdir(exist_ok=False)
    proof=json.loads((project.parent/'sparse-source-gate.json').read_text())
    if not proof['passed']:raise ValueError('Source gate required')
    plan=cases()+(supplemental_cases() if selected else [])
    if selected:
        if set(selected)-{x['name'] for x in plan}:raise ValueError('Unknown case')
        plan=[x for x in plan if x['name'] in selected]
    result=dict(mode=proof['mode'],source_proof_sha256=digest(project.parent/'sparse-source-gate.json'),
                version=api.call('ak.wwise.core.getInfo')['version'],cases=[],complete=False,
                fixtures_only=True,retail_validated=False)
    transports=[];capturing=False;restore=[];slot=None;anchor=None
    old_channel=api.call('ak.wwise.core.object.get',{'from':{'path':[MUSIC]}},{'return':['@BusChannelConfig']})['return'][0]['@BusChannelConfig']
    try:
        api.call('ak.wwise.core.transport.executeAction',{'action':'stop'})
        api.call('ak.wwise.core.object.setProperty',{'object':MUSIC,'property':'BusChannelConfig','value':6353158})
        api.call('ak.wwise.core.object.set',{'objects':[{'object':MUSIC,'@Effects':[{'type':'EffectSlot','name':'','@Effect':{
            'type':'Effect','name':'WMC_SparseRecorder','classId':8650755,'@DownmixToStereo':False,
            '@ApplyDownstreamVolume':True,'@AuthoringFilename':str(out/'unused.wav')}}],'listMode':'append'}]})
        slot=api.call('ak.wwise.core.object.get',{'from':{'path':[MUSIC]}},{'return':['@Effects']})['return'][0]['@Effects'][-1]['id']
        recorder=api.call('ak.wwise.core.object.get',{'from':{'id':[slot]}},{'return':['@Effect']})['return'][0]['@Effect']['id']
        anchor_file=out/'anchor.wav'
        with wave.open(str(anchor_file),'wb') as wav:
            wav.setparams((6,2,48000,0,'NONE','not compressed'))
            for _ in range(int(max(x['duration'] for x in plan))+5):wav.writeframesraw(bytes(48000*12))
        anchor=r'\Actor-Mixer Hierarchy\Default Work Unit\WMC_SparseAnchor'
        api.call('ak.wwise.core.audio.import',{'importOperation':'useExisting','autoAddToSourceControl':False,
            'autoCheckOutToSourceControl':False,'imports':[{'objectPath':anchor,'objectType':'Sound',
            'audioFile':str(anchor_file),'@OverrideOutput':True,'@OutputBus':MUSIC,
            '@OverrideVirtualVoice':True,'@BelowThresholdBehavior':0}]})
        for obj in (anchor,'play_music_prologue'):
            if obj==anchor:ident=obj
            else:
                tree=ET.parse(project.parent/'Events/music.wwu')
                ident=next(n.get('ID') for n in tree.iter('Event') if n.get('Name')==obj)
            transports.append(api.call('ak.wwise.core.transport.create',{'object':ident})['transport'])
        api.call('ak.wwise.core.profiler.startCapture');capturing=True
        for case in plan:
            api.call('ak.wwise.core.transport.executeAction',{'action':'stop'})
            restore=[]
            if case.get('technical_isolation'):
                # Existing report35 technical exception control, never source policy.
                tree=ET.parse(project.parent/'authored-music.xml')
                for ident in ('{1A59CC64-141A-45A6-8374-EB823D3E9D4F}','{7F25E162-CD2C-4E73-8A67-E3DCB41564BA}'):
                    node=next(n for n in tree.iter() if n.get('ID')==ident and n.tag in ('MusicSwitchContainer','MusicPlaylistContainer'))
                    for row in node.findall('./StateInfo/CustomStateList/CustomState'):
                        local=row.find('CustomState');field=local.find("./PropertyList/Property[@Name='Volume']")
                        value=float(field.get('Value')) if field is not None else 0
                        restore.append((local.get('ID'),value))
                        api.call('ak.wwise.core.object.setProperty',{'object':local.get('ID'),'property':'Volume','value':0})
            for param in ('threat_rating','menu_volume_music'):
                for go in (None,18446744073709551615):
                    args={'rtpc':param}
                    if go is not None:args['gameObject']=go
                    api.call('ak.soundengine.resetRTPCValue',args)
                api.call('ak.soundengine.setRTPCValue',{'rtpc':param,'value':0 if param=='threat_rating' else 100})
            api.call('ak.soundengine.setState',{'stateGroup':'game_state','state':case.get('state','exploration')})
            time.sleep(1.1)
            api.call('ak.wwise.core.object.setProperty',{'object':recorder,'property':'AuthoringFilename','value':str(out/(case['name']+'.wav'))})
            api.call('ak.wwise.core.transport.executeAction',{'transport':transports[0],'action':'play'})
            location=case.get('location','mus_loc_prologue_village')
            api.call('ak.soundengine.postEvent',{'event':location,'gameObject':18446744073709551614})
            time.sleep(.1)
            api.call('ak.wwise.core.transport.executeAction',{'transport':transports[1],'action':'play'})
            if case.get('initial_event'):
                api.call('ak.soundengine.postEvent',{'event':case['initial_event'],'gameObject':18446744073709551614})
            row=dict(mode=proof['mode'],case=case['name'],events=[],samples=[],complete=False,
                     initial_state=case.get('state','exploration'),location=location,
                     technical_isolation=bool(restore),primed_before_play=True)
            result['cases'].append(row)
            started=time.monotonic();pending=list(case['actions']);last_write=0
            while time.monotonic()-started < case['duration']:
                elapsed=time.monotonic()-started
                while pending and elapsed>=pending[0][0]:
                    when,kind,name,value=pending.pop(0)
                    if kind=='state':api.call('ak.soundengine.setState',{'stateGroup':'game_state','state':name})
                    elif kind=='event':api.call('ak.soundengine.postEvent',{'event':name,'gameObject':18446744073709551614})
                    elif kind=='rtpc':api.call('ak.soundengine.setRTPCValue',{'rtpc':name,'value':value})
                    else:raise ValueError('Unknown scheduled action')
                    row['events'].append(dict(scheduled=when,accepted=time.monotonic()-started,kind=kind,name=name,value=value))
                voices=api.call('ak.wwise.core.profiler.getVoices',{'time':'capture'},
                    {'return':['pipelineID','objectGUID','objectName','baseVolume','isVirtual','isStarted']})['return']
                contributions={str(v['pipelineID']):api.call('ak.wwise.core.profiler.getVoiceContributions',
                    {'time':'capture','voicePipelineID':v['pipelineID']}) for v in voices if 'Anchor' not in v['objectName']}
                rtpcs=api.call('ak.wwise.core.profiler.getRTPCs',{'time':'capture'})['return']
                row['samples'].append(dict(time=time.monotonic()-started,voices=voices,contributions=contributions,
                    rtpcs=[x for x in rtpcs if x['name'] in ('threat_rating','menu_volume_music')]))
                if elapsed-last_write>=10:
                    (out/'results.json').write_text(json.dumps(result)+'\n');last_write=elapsed
                time.sleep(.16)
            api.call('ak.wwise.core.transport.executeAction',{'action':'stop'});time.sleep(.3)
            row['complete']=True
            for ident,value in restore:api.call('ak.wwise.core.object.setProperty',{'object':ident,'property':'Volume','value':value})
            restore=[]
            (out/'results.json').write_text(json.dumps(result)+'\n')
            print(json.dumps(dict(mode=proof['mode'],case=case['name'],samples=len(row['samples']))),flush=True)
        result['complete']=True
    except BaseException as exc:
        result['error']=type(exc).__name__+': '+str(exc)
        raise
    finally:
        for ident,value in restore:
            try:api.call('ak.wwise.core.object.setProperty',{'object':ident,'property':'Volume','value':value})
            except Exception as exc:result.setdefault('restore_errors',[]).append(str(exc))
        result['cleanup_errors']=cleanup(api,capturing,transports)
        for uri,args in [('ak.wwise.core.object.delete',{'object':slot})] if slot else []:
            try:api.call(uri,args)
            except Exception as exc:result['cleanup_errors'].append(dict(uri=uri,error=str(exc)))
        if anchor:
            try:api.call('ak.wwise.core.object.delete',{'object':anchor})
            except Exception as exc:result['cleanup_errors'].append(dict(uri='delete-anchor',error=str(exc)))
        try:api.call('ak.wwise.core.object.setProperty',{'object':MUSIC,'property':'BusChannelConfig','value':old_channel})
        except Exception as exc:result['cleanup_errors'].append(dict(uri='restore-channel',error=str(exc)))
        (out/'results.json').write_text(json.dumps(result)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True)
    p.add_argument('--port',type=int,required=True);p.add_argument('--label',required=True);p.add_argument('--cases',nargs='+')
    a=p.parse_args();run(a.project,a.port,a.label,a.cases)
