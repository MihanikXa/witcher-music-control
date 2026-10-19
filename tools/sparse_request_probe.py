"""Negative/feasibility probe: Seek action on already-playing selected playlist.

Never direct Play, never a production gate. A failed safety/acceptance test is a
blocker, not permission to use the request. Only task-owned authoring process.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from sparse_reentry_pilot import CONSOLE, observe_engine
from sparse_reentry_author import SELECTED, GENERAL
from sparse_approved_cue import REPO, MUSIC, SOURCE, verify_accepted, read
from white_orchard_prepare import build_path, digest, prepare
from white_orchard_wwise import Waapi
import white_orchard_sparse_capture as capture

ROOT=REPO/'build/sparse-live-context-pilot-v1/wwise-request'
NAME='WMC_Diagnostic_Request_Seek'
RETAINED=REPO/'build/sparse-reentry-pilot-v1/candidate-b/validation'
SOURCE_SHA='a5c759d7d4ccd2d182ce28398f634d9dc8095a6aba804b1e46f6c96decc7530a'


def prepare_probe(name):
    if Path(name).name!=name or name in ('.','..'):raise ValueError('Fresh simple worker name')
    verify_accepted()
    if digest(RETAINED/MUSIC)!=SOURCE_SHA:raise ValueError('Retained source changed')
    path=ROOT/name/'validation'
    prepare(SOURCE,path,True,immutable_originals=REPO/'build/licensed-white-orchard/baseline')
    for f in (MUSIC,Path('authored-music.xml'),Path('sparse-source-gate.json'),
              Path('approved-cue-source-gate.json'),Path('reentry-source-gate.json'),Path('reentry-input.json')):
        shutil.copyfile(RETAINED/f,path/f)
    shutil.copyfile(REPO/'build/sparse-approved-cue-pilot-v1/media/WMC_S04a_approved.wav',
                    path/'Originals/SFX/WMC_S04a_approved.wav')
    return path/'w3_audio.wproj'


def source_proof(project):
    path=project.parent;manifest=read(path/'input-manifest.json')
    units=[x for x in manifest['inputs'] if x['relative_path'].endswith('.wwu')]
    if len(units)!=1508 or len(list(path.rglob('*.wwu')))!=1508:raise ValueError('Incomplete original context')
    if digest(path/MUSIC)!=SOURCE_SHA:raise ValueError('Wrong rest-first source')
    for x in units:
        rel=Path(x['relative_path'])
        if digest(SOURCE/rel)!=x['sha256']:raise ValueError('Installed source drift')
        expected=SOURCE_SHA if rel==MUSIC else x['sha256']
        if digest(path/rel)!=expected:raise ValueError('Unapproved work-unit change')
    for x in manifest['originals']:
        if digest(path/x['relative_path'])!=x['sha256']:raise ValueError('Original audio changed')
    cue=path/'Originals/SFX/WMC_S04a_approved.wav'
    if digest(cue)!='5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc':raise ValueError('Cue PCM changed')
    return dict(passed=True,original_work_units=1508,event_work_units=len(list((path/'Events').rglob('*.wwu'))),
                original_media=len(manifest['originals']),cue_sha256=digest(cue),music_sha256=SOURCE_SHA,
                globals_and_event_work_units_exact=True,changes_from_retained_rest_first_source=0)


def cases():
    return [dict(name='rest-control',duration=18,actions=[]),
            dict(name='rest-request',duration=18,actions=[(6,'event',NAME,None)]),
            dict(name='duplicate-request',duration=23,actions=[(6,'event',NAME,None),(9,'event',NAME,None)]),
            dict(name='outro-control',duration=50,actions=[(4,'state','combat',None),(10,'rtpc','threat_rating',35),
                (16,'rtpc','threat_rating',100),(24,'state','exploration',None)]),
            dict(name='outro-request',duration=50,actions=[(4,'state','combat',None),(10,'rtpc','threat_rating',35),
                (16,'rtpc','threat_rating',100),(24,'state','exploration',None),(24.3,'event',NAME,None)]),
            dict(name='authored-request',duration=25,actions=[(4,'state','dialog_scene',None),
                (4.1,'event','mus_q001_tavern_conversation',None),(7,'event',NAME,None)]),
            dict(name='wrong-place-request',duration=18,location='mus_loc_prologue_nilfgaard_camp',actions=[(6,'event',NAME,None)])]


def request_spec(target=SELECTED):
    return {'type':'Event','name':NAME,'children':[{'type':'Action','name':'',
        '@ActionType':36,'@Target':target,'@SeekType':1,'@SeekPercent':99.9,'@SeekToMarker':False}]}


def validate_actions(actions,target):
    if len(actions)!=1:raise ValueError('Exactly one action required')
    a=actions[0]
    if (a.get('type')!='Action' or a.get('@ActionType')!=36 or a.get('@Target',{}).get('id')!=target or
            a.get('@SeekType')!=1 or a.get('@SeekPercent')!=99.9 or a.get('@SeekToMarker') is not False):
        raise ValueError('Unapproved request action')


def run(project,port=18294,selected=None,scope="playlist"):
    if scope not in ("playlist","general"):raise ValueError("Unknown scope")
    target=SELECTED if scope=="playlist" else GENERAL
    project=build_path(project)
    if not project.is_relative_to(ROOT) or project.parent.name!='validation':raise ValueError('Exact private root required')
    verify_accepted();before=digest(project.parent/MUSIC)
    if before!=read(project.parent/'reentry-input.json')['music_sha256']:raise ValueError('Source drift')
    receipt={'source_before':before,'production_gate':False,'purpose':'candidate primitive rejection test',
             'retail_tested':False,'new_globals':False,'spec':request_spec(target),'scope':scope}
    receipt['source_proof_before']=source_proof(project)
    result_path=project.parent/('request-'+scope+'-lifecycle.json')
    if result_path.exists():raise FileExistsError(result_path)
    log=(project.parent/('request-'+scope+'-server.log')).open('wb')
    p=subprocess.Popen([str(CONSOLE),'waapi-server',str(project),'--http-port',str(port),
        '--wamp-port',str(port+1000),'--no-source-control'],stdout=log,stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    api=Waapi(port);ready=False;event=None
    try:
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            if p.poll() is not None:raise RuntimeError('Authoring server exited')
            try:
                ready=Path(api.call('ak.wwise.core.getProjectInfo')['path']).resolve()==project
                if ready:break
            except Exception:pass
            time.sleep(.5)
        if not ready:raise TimeoutError('Task-owned project readiness')
        receipt['version']=api.call('ak.wwise.core.getInfo')['version']
        if receipt['version']['build']!=8928:raise ValueError('Wrong version')
        # Create an isolated Event/Seek action only; no new Play or global object.
        response=api.call('ak.wwise.core.object.set',{'objects':[{'object':r'\Events\Default Work Unit',
            'children':[request_spec(target)],'onNameConflict':'fail'}]})
        receipt['creation']=response
        event=api.call('ak.wwise.core.object.get',{'from':{'path':['\\Events\\Default Work Unit\\'+NAME]}},
                       {'return':['id','name','children']})['return'][0]['id']
        actions=api.call('ak.wwise.core.object.get',{'from':{'id':[event]},'transform':[{'select':['children']}]},
            {'return':['id','type','@ActionType','@Target','@SeekType','@SeekPercent','@SeekToMarker']})['return']
        receipt['loaded_actions']=actions
        validate_actions(actions,target)
        capture.cases=cases;capture.supplemental_cases=lambda:[]
        capture.run(project,port,'request-'+scope+'-captures',selected,observer=observe_engine)
    except BaseException as e:
        receipt['error']=type(e).__name__+': '+str(e)
        raise
    finally:
        errors=[]
        if ready:
            for uri,args in [('ak.wwise.core.transport.executeAction',{'action':'stop'}),
                             *([('ak.wwise.core.object.delete',{'object':event})] if event else []),
                             ('ak.wwise.console.project.close',{})]:
                try:api.call(uri,args)
                except Exception as e:errors.append(str(e))
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=10)
        log.close();receipt.update(cleanup_errors=errors,process_exit=p.returncode,
            source_after=digest(project.parent/MUSIC),source_unchanged=digest(project.parent/MUSIC)==before)
        try:receipt['source_proof_after']=source_proof(project)
        except Exception as e:receipt['source_proof_after']={'passed':False,'error':str(e)}
        result_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path);p.add_argument('--prepare');p.add_argument('--cases',nargs='+')
    p.add_argument('--scope',choices=['playlist','general'],default='playlist')
    a=p.parse_args()
    if a.prepare:print(prepare_probe(a.prepare))
    elif a.project:run(a.project,selected=a.cases,scope=a.scope)
    else:p.error('--prepare or --project required')
