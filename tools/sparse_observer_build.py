"""Isolated native compilation of original log-only annotations. Never deploys.

Compiles pristine scripts first, then identical context plus one original file.
Native inputs are copied; no installed tool, source or runtime config is edited.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess

from white_orchard_prepare import build_path,digest

REPO=Path(__file__).resolve().parents[1]
KIT=Path(r'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit')
SOURCE=REPO/'src/diagnostics/wmcContextObserver.ws'


def prepare(root):
    root=build_path(root)
    if root.exists():raise FileExistsError(root)
    root.mkdir(parents=True);pins=[]
    def copy(p,q):
        q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        pins.append(dict(source=str(p),sha256=digest(p)))
    for p in (KIT/'bin/x64_RedKit').iterdir():
        if p.is_file() and (p.suffix.lower()=='.dll' or p.name=='wcc_lite.exe'):copy(p,root/'runtime'/p.name)
    for folder,dest in [(KIT/'bin/config',root/'config'),(KIT/'r4data/scripts',root/'base'),
                        (KIT/'r4data/gameplay/globals',root/'data/gameplay/globals')]:
        for p in folder.rglob('*'):
            if p.is_file():copy(p,dest/p.relative_to(folder))
    for rel in ['dep.cache','x64.release.redscripts','engine/textures/texturegroups.xml',
                'game/dlctable.csv','soundbanks/Pc/Init.bnk']:
        copy(KIT/'r4data'/rel,root/'data'/rel)
    for p in (KIT/'r4data').glob('staticshader*.cache'):copy(p,root/'data'/p.name)
    copy(KIT/'bin/redscripts.ini',root/'redscripts.ini')
    # Compiler root is parent of its base directory; paths must include
    # that base name (absolute paths are incorrectly prefixed by this toolchain). A private product title avoids targeting the live game settings.
    data=root.name+'/data/'
    scripts=root.name+'/base/'
    (root/'gameconf.cfg').write_text('r4 {\n title "WMC offline scripts"\n data "'+data+'"\n bundle "bundles"\n config "config"\n scripts "'+scripts+'"\n gameClass "CR4Game"\n playerClass "CR4Player"\n telemetryClass "CR4TelemetryScriptProxy"\n cameraDirClassName "CR4CameraDirector"\n}\n',encoding='utf-8')
    (root/'data/gameplay/globals/soundbanks_always_load.csv').write_text('soundbank\nInit.bnk\n',encoding='utf-8')
    (root/'patch/local').mkdir(parents=True)
    (root/'patch/local/wmcCompilerControl.ws').write_text('class WMCCompilerControl extends CObject {}\n',encoding='utf-8')
    (root/'inputs.json').write_text(json.dumps(dict(inputs=pins,compiler_sha256=digest(root/'runtime/wcc_lite.exe'),
        source_context='pristine REDkit; not the complete merged user script assembly'),indent=2)+'\n',encoding='utf-8')
    return root


def diagnostics(text):
    return Counter(re.sub(r'^\[[^]]+\]','',line) for line in text.splitlines()
                   if '[Warning]' in line or '[Error]' in line)


def assertion_control_source():
    # Same fields, wrappers, native queries and signatures; only log payload is
    # constant. This distinguishes annotation/compiler metadata diagnostics from
    # dynamic trace formatting. It is never installed or executed.
    text=SOURCE.read_text(encoding='utf-8')
    text,n=re.subn(r"LogChannel\('WMCContext',.*?;", "LogChannel('WMCContext', \"declaration-control\");", text,flags=re.S)
    if n!=1:raise ValueError('Expected one original log call')
    return 'class WMCCompilerControl extends CObject {}\n'+text


def compile_one(root,label,include_observer=False,assertion_control=False):
    root=build_path(root)
    if Path(label).name!=label:raise ValueError('Simple attempt label')
    out=root/label
    if out.exists():raise FileExistsError(out)
    out.mkdir();patch=root/'patch/local/wmcContextObserver.ws';patch_dir=root/'patch'
    if assertion_control:
        if include_observer:raise ValueError('Separate control and observer')
        patch_dir=root/'matched-control-patch';p=patch_dir/'local/control.ws'
        if p.exists():
            if p.read_text(encoding='utf-8')!=assertion_control_source():raise ValueError('Assertion control drift')
        else:p.parent.mkdir(parents=True);p.write_text(assertion_control_source(),encoding='utf-8')
    elif include_observer:shutil.copyfile(SOURCE,patch)
    elif patch.exists():raise ValueError('Baseline must not include observer')
    cmd=[str(root/'runtime/wcc_lite.exe'),'compilescripts',str(root/'base'),
         '-patch='+str(patch_dir),'-out='+str(out),'-noninteractivecrash']
    p=subprocess.Popen(cmd,cwd=root/'runtime',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    timeout=False
    try:data=p.communicate(timeout=120)[0]
    except subprocess.TimeoutExpired:
        timeout=True;p.kill();data=p.communicate(timeout=15)[0]
    (root/(label+'.stdout.log')).write_bytes(data)
    log=root/'wcc.log';text=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
    (root/(label+'.full.log')).write_text(text,encoding='utf-8')
    blob=out/'blob.rsblob'
    result=dict(exit_code=p.returncode,timeout=timeout,command=cmd,
        compiled=p.returncode==0 and not timeout and blob.exists() and 'Success! Patch scripts blob saved' in text
            and '[Error][Script]' not in text and '[Error][WCC]' not in text,
        blob_sha256=digest(blob) if blob.exists() else None,
        source_sha256=digest(SOURCE) if include_observer else None,diagnostics=dict(diagnostics(text)))
    (root/(label+'.result.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--prepare',action='store_true')
    p.add_argument('--label',default='baseline');p.add_argument('--candidate',action='store_true')
    p.add_argument('--assertion-control',action='store_true');a=p.parse_args()
    if a.prepare:prepare(a.root)
    r=compile_one(a.root,a.label,a.candidate,a.assertion_control)
    print(json.dumps({k:v for k,v in r.items() if k!='diagnostics'},indent=2))
    if not r['compiled']:raise SystemExit(1)
