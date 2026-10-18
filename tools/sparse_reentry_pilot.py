"""Bounded private re-entry fixture preparation and task-owned Wwise capture.

No SoundBanks, licences, installed writes or script controller. Complete WWUs
and immutable originals are retained; only known experiment music XML is staged.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from white_orchard_prepare import prepare, build_path, digest
from white_orchard_wwise import Waapi
import white_orchard_sparse_capture as capture
from sparse_approved_cue import SOURCE, REPO, MUSIC, verify_accepted, read

ROOT=REPO/'build/sparse-reentry-pilot-v1'
PRIOR=REPO/'build/sparse-approved-cue-pilot-v1'
CONSOLE=Path(r'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe')


def cases(candidate=None):
    out=[]
    for kind in ('event','state'):
        name='mus_loc_prologue_village' if kind=='event' else 'exploration'
        out.append(dict(name='redundant-'+kind,duration=130,actions=[(t,kind,name,None) for t in (6,44,57)]))
    out.append(dict(name='redundant-event-confirmation',duration=75,
                    actions=[(t,'event','mus_loc_prologue_village',None) for t in (6,44,57)]))
    for kind in ('location','daynight'):
        for phase,a,b,duration in [('music',6,12,65),('early',44,48,90),('late',56,60,100)]:
            actions=[(a,'event','mus_loc_prologue_nilfgaard_camp',None),(b,'event','mus_loc_prologue_village',None)] if kind=='location' else [
                (a,'state','exploration_night',None),(b,'state','exploration',None)]
            out.append(dict(name=kind+'-'+phase,duration=duration,actions=actions))
    for phase,start,end,duration in [('music',6,30,100),('early',44,66,120),('late',57,82,135)]:
        out.append(dict(name='combat-'+phase,duration=duration,actions=[(start,'state','combat',None),
            (start+6,'rtpc','threat_rating',35),(start+12,'rtpc','threat_rating',100),(end,'state','exploration',None)]))
    out.extend([
      dict(name='rapid-combat',duration=100,actions=[(6,'state','combat',None),(20,'state','exploration',None),
        (23,'state','combat',None),(29,'rtpc','threat_rating',35),(35,'rtpc','threat_rating',100),(42,'state','exploration',None)]),
      dict(name='cycles-master',duration=140,actions=[(8,'rtpc','menu_volume_music',50),(16,'rtpc','menu_volume_music',100)]),
      dict(name='authored-music',duration=40,actions=[(6,'state','dialog_scene',None),(6.1,'event','mus_q001_tavern_conversation',None)]),
      dict(name='authored-rest',duration=85,actions=[(44,'state','dialog_scene',None),(44.1,'event','mus_q001_tavern_conversation',None)]),
      dict(name='authored-recovery',duration=75,actions=[(6,'state','combat',None),(22,'state','exploration',None),
          (24,'state','dialog_scene',None),(24.1,'event','mus_q001_tavern_conversation',None)]),
      dict(name='dialogue-music',duration=95,actions=[(8,'state','dialog_scene',None),(20,'state','exploration',None)]),
      dict(name='dialogue-scenes',duration=75,actions=[(8,'state','dialog_scene',None),(20,'state','exploration',None),
          (42,'state','cutscene',None),(43,'state','dialog_scene',None),(51,'state','movie',None),
          (52,'state','music_only',None),(60,'state','exploration',None)]),
      dict(name='protected-world',duration=25,location='mus_loc_prologue_village_q505',technical_isolation=True,
           actions=[(8,'rtpc','menu_volume_music',50),(17,'rtpc','menu_volume_music',100)]),
      dict(name='gwent',duration=20,state='gwent',actions=[]),
      dict(name='state-settling',duration=22,actions=[(2,'state','combat',None),(5,'state','exploration',None),
                                                   (8,'state','dialog_scene',None),(11,'state','exploration',None)]),
    ])
    if candidate=='rest-first':
        # Same musical phase coverage after the explicitly declared initial rest.
        for case in out:
            name=case['name']
            if name.startswith('redundant-'):
                case['actions']=[(t,case['actions'][0][1],case['actions'][0][2],None) for t in (6,26,36,74,87)]
                case['duration']=150
            elif name.startswith(('location-','daynight-')):
                phase=name.rsplit('-',1)[1]
                start={'music':36,'early':6,'late':26}[phase]
                gap=6 if phase=='music' else 4
                case['actions']=[(start,*case['actions'][0][1:]),(start+gap,*case['actions'][1][1:])]
                case['duration']=start+gap+65
            elif name.startswith('combat-'):
                phase=name.rsplit('-',1)[1];start={'music':36,'early':6,'late':26}[phase]
                end=start+24
                case['actions']=[(start,'state','combat',None),(start+6,'rtpc','threat_rating',35),
                                 (start+12,'rtpc','threat_rating',100),(end,'state','exploration',None)]
                case['duration']=end+70
            elif name=='cycles-master':
                case['duration']=155
                case['actions']=[(38,'rtpc','menu_volume_music',50),(46,'rtpc','menu_volume_music',100)]
            elif name=='authored-music':
                case['actions']=[(36,'state','dialog_scene',None),(36.1,'event','mus_q001_tavern_conversation',None)];case['duration']=65
            elif name=='dialogue-music':
                case['actions']=[(36,'state','dialog_scene',None),(50,'state','exploration',None)];case['duration']=115
            elif name=='authored-rest':
                case['actions']=[(6,'state','dialog_scene',None),(6.1,'event','mus_q001_tavern_conversation',None)];case['duration']=45
    return out


def prepare_worker(name,mode='sparse'):
    if Path(name).name!=name or name in ('.','..'):raise ValueError('Simple fresh worker name required')
    if mode not in ('sparse','native','minimal'):raise ValueError('Unknown mode')
    verify_accepted()
    path=build_path(ROOT/name/'validation')
    prepare(SOURCE,path,True,immutable_originals=REPO/'build/licensed-white-orchard/baseline')
    source=PRIOR/('generation' if mode=='sparse' else mode+'/validation')
    shutil.copyfile(source/MUSIC,path/MUSIC)
    for filename in ('sparse-source-gate.json','authored-music.xml'):
        old=PRIOR/('sparse' if mode=='sparse' else mode)/'validation'/filename
        shutil.copyfile(old,path/filename)
    if mode=='sparse':
        shutil.copyfile(PRIOR/'sparse/validation/approved-cue-source-gate.json',path/'approved-cue-source-gate.json')
        shutil.copyfile(PRIOR/'media/WMC_S04a_approved.wav',path/'Originals/SFX/WMC_S04a_approved.wav')
    shutil.copyfile(path/MUSIC,path/'authored-music.xml')
    sha=digest(path/MUSIC)
    (path/'reentry-input.json').write_text(json.dumps(dict(mode=mode,music_sha256=sha,source_context='complete1508',licence_copied=False),indent=2)+'\n')
    return path/'w3_audio.wproj'


def observe_engine(api):
    # Official getState schema requests a short sound-engine update delay.
    # Getters require qualified object references; unlike setters, bare names
    # are rejected by this installed API. GUIDs are pinned original definitions.
    time.sleep(.01)
    return dict(game_state=api.call('ak.soundengine.getState',{'stateGroup':'{27711515-3584-4123-9F09-B90831398B80}'}),
                location=api.call('ak.soundengine.getSwitch',{'switchGroup':'{3139B245-58B7-4C39-9BE9-414395307E75}','gameObject':18446744073709551614}),
                music_type=api.call('ak.soundengine.getSwitch',{'switchGroup':'{2076AA35-8BFD-4069-A941-1D9625ADD8F0}','gameObject':18446744073709551614}))


def observe_settling(api):
    started=time.monotonic();out=observe_engine(api)
    samples=[dict(time=time.monotonic()-started,state=out['game_state']['return']['name'])]
    for _ in range(5):
        time.sleep(.05)
        state=api.call('ak.soundengine.getState',{'stateGroup':'{27711515-3584-4123-9F09-B90831398B80}'})
        samples.append(dict(time=time.monotonic()-started,state=state['return']['name']))
    out['state_settling']=samples
    return out


def run(project,port,label,selected,settling=False):
    project=build_path(project);out=project.parent/(label+'-lifecycle.json')
    if out.exists():raise FileExistsError(out)
    expected=read(project.parent/'reentry-input.json')['music_sha256']
    if digest(project.parent/MUSIC)!=expected:raise ValueError('Unverified music source')
    log=(project.parent/(label+'-server.log')).open('wb')
    command=[str(CONSOLE),'waapi-server',str(project),'--http-port',str(port),'--wamp-port',str(port+1000),'--no-source-control']
    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,
                             creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    state=dict(pid=process.pid,port=port,project=str(project.relative_to(REPO)),closed=False,errors=[])
    api=Waapi(port);ready=False
    try:
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('Task-owned server exited during startup')
            try:
                info=api.call('ak.wwise.core.getProjectInfo')
                if Path(info['path']).resolve()==project:ready=True;break
            except Exception:pass
            time.sleep(.5)
        if not ready:raise TimeoutError('Exact project readiness timed out')
        if api.call('ak.wwise.core.getInfo')['version']['build']!=8928:raise ValueError('Wrong Wwise build')
        meta=read(project.parent/'reentry-input.json')
        parents=['{00F2D643-114B-46E4-B5EB-4B78ED19D3A6}',
                 '{1A59CC64-141A-45A6-8374-EB823D3E9D4F}','{A9E3330C-5726-4E53-8974-7EB1BB7C19E3}']
        state['loaded_continue_play']=api.call('ak.wwise.core.object.get',{'from':{'id':parents}},
                                              {'return':['id','@ContinuePlay']})['return']
        if len(state['loaded_continue_play'])!=3 or not all(n['@ContinuePlay'] for n in state['loaded_continue_play']):raise ValueError('Native continuation changed')
        if meta.get('candidate')=='history-rest':
            gate=read(project.parent/'reentry-source-gate.json')
            ids=[gate['added_guids'][0],gate['added_guids'][3],'{A79AC940-BEEA-48E2-81EA-BD307F4771D4}']
            settings=api.call('ak.wwise.core.object.get',{'from':{'id':ids}},
                             {'return':['id','@DestinationPlaylistJumpTo','@DestinationJumpPositionPreset']})['return']
            state['loaded_transition_settings']=settings
            if len(settings)!=3 or {n['id'] for n in settings}!=set(ids):raise ValueError('Missing loaded transitions')
            for n in settings:
                expected_settings=(1,0) if n['id']==ids[-1] else (2,4)
                if (n['@DestinationPlaylistJumpTo'],n['@DestinationJumpPositionPreset'])!=expected_settings:
                    raise ValueError('Authoring loader did not retain candidate transition settings')
        capture.cases=lambda:cases(meta.get('candidate'));capture.supplemental_cases=lambda:[]
        capture.run(project,port,label,selected,observer=observe_settling if settling else observe_engine)
    finally:
        if ready:
            try:
                api.call('ak.wwise.core.transport.executeAction',{'action':'stop'})
                state['remaining_transports']=api.call('ak.wwise.core.transport.getList')
                api.call('ak.wwise.console.project.close')
                state['closed']=True
            except Exception as e:state['errors'].append(str(e))
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        state['process_exit']=process.returncode;log.close()
        state['source_after_sha256']=digest(project.parent/MUSIC)
        state['source_exact']=state['source_after_sha256']==expected
        out.write_text(json.dumps(state,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare');p.add_argument('--mode',default='sparse');p.add_argument('--project',type=Path)
    p.add_argument('--port',type=int);p.add_argument('--label',default='matrix-v1');p.add_argument('--cases',nargs='+')
    p.add_argument('--settling-observer',action='store_true');a=p.parse_args()
    if a.prepare:print(prepare_worker(a.prepare,a.mode))
    else:run(a.project,a.port,a.label,a.cases,a.settling_observer)
