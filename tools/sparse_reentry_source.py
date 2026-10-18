"""Complete-context and reversible re-entry source proof; no project keys read."""
import argparse
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

from sparse_reentry_pilot import ROOT,PRIOR,SOURCE,REPO,MUSIC
from sparse_reentry_author import validate as reentry_validate
from sparse_approved_cue import verify_accepted,read,validate_import,SPEC,D_SPEC,context,validate,measured_template
from white_orchard_sparse import consumer_closure
from white_orchard_prepare import digest,build_path


def require(ok,message):
    if not ok:raise ValueError(message)


def verify(root):
    verify_accepted();d,spec=read(D_SPEC),read(SPEC)
    original,states=context(SOURCE,d)
    old=ET.parse(PRIOR/'generation'/MUSIC).getroot()
    pre=ET.parse(PRIOR/'sparse/validation/pre-import-music.xml').getroot()
    validate(original,pre,spec,d,'sparse',states,measured_template(d))
    validate_import(pre,old,{},read(PRIOR/'media/audio-proof.json'),PRIOR/'generation/w3_audio.wproj')
    require(digest(PRIOR/'generation'/MUSIC)=='a0beae9fbf32d55054c2cb8ea10a2cc8f0034b699d9c921fef1e1351075b53ff','Prior source changed')
    prior=read(REPO/'research/88-approved-cue-licensed-bank-evidence.json')
    require(digest(PRIOR/'generated-banks-licensed/music_prologue.bnk')==prior['candidate_sha256'],'Preserved experiment bank changed')
    for rel,item in read(PRIOR/'preservation.json')['preserved_release_inputs'].items():
        require(digest(REPO/rel)==item['sha256'],'Preserved release input changed')
    require(digest(Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\initialdata\sound\Init.bnk'))
            ==prior['native_init_sha256'],'Native Init changed')
    closure=consumer_closure(original,spec,d,(ET.parse(p) for p in sorted((SOURCE/'Events').rglob('*.wwu'))))
    projects=[]
    for meta_file in sorted(root.glob('*/validation/reentry-input.json')):
        project=meta_file.parent;meta=read(meta_file);inputs=read(project/'input-manifest.json')
        units={x['relative_path'].replace('\\','/'):x['sha256'] for x in inputs['inputs'] if x['relative_path'].endswith('.wwu')}
        actual={p.relative_to(project).as_posix():p for p in project.rglob('*.wwu')}
        require(len(units)==1508 and units.keys()==actual.keys(),'Incomplete source context')
        changed=[]
        for rel,sha in units.items():
            require(digest(SOURCE/rel)==sha,'Installed original WWU changed')
            if digest(actual[rel])!=sha:changed.append(rel)
        require(changed==[MUSIC.as_posix()],'Unexpected WWU changes')
        candidate=ET.parse(project/MUSIC).getroot()
        if meta.get('candidate'):
            gate=read(project/'reentry-source-gate.json')
            semantic_gate=reentry_validate(old,candidate,meta['candidate'],gate['added_guids'])
        else:
            require(digest(project/MUSIC)==digest(PRIOR/'generation'/MUSIC),'Baseline differs from approved source')
            semantic_gate={'passed':True,'baseline_exact':True}
        require(digest(project/MUSIC)==meta['music_sha256']==digest(project/'authored-music.xml'),'Snapshot mismatch')
        for audio in inputs['originals']:
            rel=audio['relative_path']
            require(digest(project/rel)==digest(SOURCE/rel)==audio['sha256'],'Original source media changed')
            require(os.path.samefile(project/rel,REPO/'build/licensed-white-orchard/baseline'/rel),'Immutable hardlink identity lost')
        require(digest(project/'Originals/SFX/WMC_S04a_approved.wav')=='5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc','Approved source changed')
        projects.append(dict(name=project.parent.name,work_units=len(units),original_audio=len(inputs['originals']),
                             source_sha256=digest(project/MUSIC),source_gate=semantic_gate))
    require(len(projects)==5,'Expected three baseline workers and two bounded candidates')
    return dict(passed=True,projects=projects,closure=closure,approved24_exact=True,
                retained_bank_sha256=prior['candidate_sha256'],native_init_sha256=prior['native_init_sha256'],
                original_events_unchanged=True,generated_banks=False,retail_verified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    output=build_path(a.output)
    if output.exists():raise FileExistsError(output)
    try:r=verify(a.root)
    except Exception as error:
        output.write_text(json.dumps(dict(passed=False,error=str(error)),indent=2)+'\n');raise
    output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,projects=len(r['projects']),events=r['closure']['event_work_units'])))
