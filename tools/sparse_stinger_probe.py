"""One bounded rest-only/local stinger hypothesis. No banks or deployment.

Reuses a source-unreferenced existing Trigger for private authoring only. This
is not permission to reuse its semantics in production or a proven safe gateway.
"""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from sparse_approved_cue import REPO,MUSIC,verify_accepted,read
from sparse_reentry_author import SELECTED,MUSIC_ITEM,REST_ITEM
from sparse_reentry_pilot import CONSOLE,observe_engine
from white_orchard_prepare import digest,build_path
from white_orchard_state_volume_author import semantic
from white_orchard_wwise import Waapi
import sparse_request_probe as prior
import white_orchard_sparse_capture as capture

ROOT=REPO/'build/sparse-interface-prerequisites-v1/wwise'
TRIGGER='{90730515-839D-472E-BE48-C0B95033193D}'
CUE='{22B6E6E1-528D-47DD-98F1-C1B3C1AD800A}'
EVENT='WMC_Private_Request_Stinger'
CANCEL='WMC_Private_Cancel_Stinger'


def rest_only(before):
    after=copy.deepcopy(before)
    selected=next(n for n in after.iter('MusicPlaylistContainer') if n.get('ID')==SELECTED)
    items=selected.find('./ReferenceList/Reference[@Name="PlaylistRoot"]/Custom/MusicPlaylistItem/ChildrenList')
    if [n.get('ID') for n in items]!=[REST_ITEM,MUSIC_ITEM]:raise ValueError('Unexpected retained sequence')
    items.remove(items[1]);return after


def validate_source(before,after):
    if semantic(rest_only(before))!=semantic(after):raise ValueError('Unexpected source modification')
    expected=copy.deepcopy(after)
    old=next(n for n in before.iter('MusicPlaylistContainer') if n.get('ID')==SELECTED)
    new=next(n for n in expected.iter('MusicPlaylistContainer') if n.get('ID')==SELECTED)
    a=old.find('./ReferenceList/Reference[@Name="PlaylistRoot"]/Custom/MusicPlaylistItem/ChildrenList')
    b=new.find('./ReferenceList/Reference[@Name="PlaylistRoot"]/Custom/MusicPlaylistItem/ChildrenList')
    b.append(copy.deepcopy(a[1]))
    if semantic(expected)!=semantic(before):raise ValueError('Source restoration failed')
    return dict(passed=True,only_removed_playlist_reference=MUSIC_ITEM,
        original_segment_and_pcm_retained=True,all_native_transition_and_gain_semantics_exact=True)


def prepare():
    prior.ROOT=ROOT
    project=prior.prepare_probe('candidate');prior.source_proof(project)
    path=project.parent/MUSIC;shutil.copyfile(path,project.parent/'stinger-before.xml')
    before=ET.parse(path).getroot();after=rest_only(before);gate=validate_source(before,after)
    ET.ElementTree(after).write(path,encoding='utf-8',xml_declaration=True)
    shutil.copyfile(path,project.parent/'authored-music.xml')
    gate.update(before_sha256=digest(project.parent/'stinger-before.xml'),after_sha256=digest(path))
    (project.parent/'stinger-source-gate.json').write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
    return project


def stinger_spec():
    return {'type':'MusicStinger','name':'WMC_Private_S04a_Stinger','@Trigger':TRIGGER,'@Segment':CUE,
        '@PlaySegmentAt':0,'@NumSegmentAdvance':0,'@DontPlayAgainTime':45}


def cases():
    return [dict(name='no-request',duration=55,actions=[]),
        dict(name='valid-request',duration=55,actions=[(6,'event',EVENT,None)]),
        dict(name='duplicate-request',duration=55,actions=[(6,'event',EVENT,None),(12,'event',EVENT,None)]),
        dict(name='combat-request',duration=45,actions=[(4,'state','combat',None),(6,'event',EVENT,None),
            (12,'rtpc','threat_rating',35),(18,'rtpc','threat_rating',100),(24,'state','exploration',None)]),
        dict(name='outro-request',duration=55,actions=[(4,'state','combat',None),(12,'rtpc','threat_rating',35),
            (18,'rtpc','threat_rating',100),(24,'state','exploration',None),(25,'event',EVENT,None)]),
        dict(name='authored-request',duration=30,actions=[(4,'state','dialog_scene',None),
            (4.1,'event','mus_q001_tavern_conversation',None),(9,'event',EVENT,None)]),
        dict(name='dialogue-request',duration=35,actions=[(4,'state','dialog_scene',None),
            (9,'event',EVENT,None),(18,'state','exploration',None)]),
        dict(name='wrong-location-return',duration=35,location='mus_loc_prologue_nilfgaard_camp',
            actions=[(6,'event',EVENT,None),(16,'event','mus_loc_prologue_village',None)]),
        dict(name='gwent-request',duration=20,state='gwent',actions=[(6,'event',EVENT,None)]),
        dict(name='cancel-active',duration=25,actions=[(6,'event',EVENT,None),(12,'event',CANCEL,None)]),
        dict(name='active-then-combat',duration=55,actions=[(6,'event',EVENT,None),(12,'state','combat',None),(20,'rtpc','threat_rating',35),(26,'rtpc','threat_rating',100),(32,'state','exploration',None)]),
        dict(name='active-then-authored',duration=35,actions=[(6,'event',EVENT,None),(12,'state','dialog_scene',None),(12.1,'event','mus_q001_tavern_conversation',None)]),
        dict(name='late-outro-request',duration=55,actions=[(4,'state','combat',None),(12,'rtpc','threat_rating',35),(18,'rtpc','threat_rating',100),(24,'state','exploration',None),(28,'event',EVENT,None)]),
        dict(name='cancel-ineligible',duration=35,actions=[(4,'state','dialog_scene',None),(9,'event',EVENT,None),(12,'event',CANCEL,None),(18,'state','exploration',None)]),
        dict(name='request-master',duration=55,actions=[(6,'event',EVENT,None),(15,'rtpc','menu_volume_music',50),(24,'rtpc','menu_volume_music',100)])]


def run(project,chosen,label="stinger-captures"):
    project=build_path(project)
    if not project.is_relative_to(ROOT):raise ValueError('Private fixture only')
    gate=read(project.parent/'stinger-source-gate.json')
    validate_source(ET.parse(project.parent/'stinger-before.xml').getroot(),ET.parse(project.parent/MUSIC).getroot())
    if Path(label).name!=label or label in ('.','..'):raise ValueError('Simple fresh capture label required')
    if (project.parent/label).exists():raise FileExistsError('Retain previous captures')
    verify_accepted();log=(project.parent/(label+'-server.log')).open('xb')
    result=dict(production_gate=False,new_global_definitions=False,trigger_reuse='private authoring hypothesis only')
    receipt=project.parent/(label+'-lifecycle.json')
    if receipt.exists():raise FileExistsError(receipt)
    process=subprocess.Popen([str(CONSOLE),'waapi-server',str(project),'--http-port','18396','--wamp-port','19396',
        '--no-source-control'],stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    api=Waapi(18396);ready=False;stinger=None;event=None;cancel=None
    try:
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('Authoring server exited')
            try:
                ready=Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve()==project
                if ready:break
            except Exception:pass
            time.sleep(.5)
        if not ready:raise TimeoutError('Private project readiness')
        result['version']=api.call('ak.wwise.core.getInfo')['version']
        if result['version']['build']!=8928:raise ValueError('Wrong authoring version')
        api.call('ak.wwise.core.object.set',{'objects':[{'object':SELECTED,'@Stingers':[stinger_spec()],'listMode':'append'}]})
        stinger=api.call('ak.wwise.core.object.get',{'from':{'id':[SELECTED]}},{'return':['@Stingers']})['return'][0]['@Stingers'][-1]['id']
        result['loaded_stinger']=api.call('ak.wwise.core.object.get',{'from':{'id':[stinger]}},
            {'return':['id','type','@Trigger','@Segment','@PlaySegmentAt','@NumSegmentAdvance','@DontPlayAgainTime']})['return']
        api.call('ak.wwise.core.object.set',{'objects':[{'object':r'\Events\Default Work Unit','children':[
            {'type':'Event','name':EVENT,'children':[{'type':'Action','name':'','@ActionType':35,'@Target':TRIGGER}]}],
            'onNameConflict':'fail'}]})
        event=api.call('ak.wwise.core.object.get',{'from':{'path':['\\Events\\Default Work Unit\\'+EVENT]}},{'return':['id']})['return'][0]['id']
        api.call('ak.wwise.core.object.set',{'objects':[{'object':r'\Events\Default Work Unit','children':[{'type':'Event','name':CANCEL,'children':[{'type':'Action','name':'','@ActionType':2,'@Target':CUE}]}],'onNameConflict':'fail'}]})
        cancel=api.call('ak.wwise.core.object.get',{'from':{'path':['\\Events\\Default Work Unit\\'+CANCEL]}},{'return':['id']})['return'][0]['id']
        capture.cases=cases;capture.supplemental_cases=lambda:[]
        capture.run(project,18396,label,chosen,observer=observe_engine)
    except BaseException as e:
        result['error']=type(e).__name__+': '+str(e);raise
    finally:
        errors=[]
        if ready:
            commands=[('ak.wwise.core.transport.executeAction',{'action':'stop'})]
            commands += [('ak.wwise.core.object.delete',{'object':x}) for x in [cancel,event,stinger] if x]
            commands.append(('ak.wwise.console.project.close',{}))
            for uri,args in commands:
                try:api.call(uri,args)
                except Exception as e:errors.append(str(e))
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        log.close();result.update(cleanup_errors=errors,process_exit=process.returncode,
            music_source_exact=digest(project.parent/MUSIC)==gate['after_sha256'])
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--project',type=Path)
    p.add_argument('--label',default='stinger-captures');p.add_argument('--cases',nargs='+');a=p.parse_args()
    if a.prepare:print(prepare())
    else:run(a.project,a.cases,a.label)
