"""Read-only, version-pinned follow-up to the negative native logger probe.

Never launches/attaches to the game, changes configuration or visits save files.
The command-line policy below is a model of reviewed instructions, not runtime
observation. Executable dumps and actual personal paths remain private.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

from observer_native_log_audit import PE, IMAGE_SHA

REPO=Path(__file__).resolve().parents[1]
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3')
ROOT=REPO/'build/native-logger-activation-v1'
KEYS=('LogDebugScripts','DebugScriptsForceFlush','DebugScriptsLogDir')
ORIGINAL='a9750eeabb62948d661a3ec785c82919eb4075dad9de6e35aaf9a4a1bc9f86b2'
STAGED='ec0f09b06fd74984017ad27acbc3564705d0244c7af388e6415f9267a2ecfa4f'


def literal_offsets(data, needle):
    if not needle:raise ValueError('Nonempty literal required')
    start=0
    while True:
        i=data.find(needle,start)
        if i<0:return
        yield i;start=i+1


def command_gate_model(command_line):
    # Native call at 0x270f26b is the reviewed narrow strstr implementation.
    # This intentionally models substring/case behavior, NOT an argv parser.
    return dict(disabled_field_17c='-debugscripts' not in command_line,
                model_only=True,does_not_inspect_actual_process=True)


def pc_order(xml):
    root=ET.fromstring(xml)
    nodes=root.findall('./Set[@name="pc"]')
    if root.tag!='OverrideOrder' or len(nodes)!=1:raise ValueError('Unknown config descriptor')
    paths=[n.get('name') for n in nodes[0].findall('Path')]
    for name in paths:
        if not name:raise ValueError('Empty layer')
        parts=name.replace('\\','/').split('/')
        if any(p in ('.','..') or ':' in p for p in parts) or name.startswith(('/','\\')):
            raise ValueError('Layer leaves config root')
    return paths


def logger_rows(text):
    # Inventory only: preserve duplicates/line numbers. Do not pretend this is
    # the native parser or manufacture effective runtime precedence.
    group='';rows=[]
    for no,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if s.startswith('[') and s.endswith(']'):group=s[1:-1]
        elif group=='Scripts' and '=' in s:
            key,value=s.split('=',1);key=key.strip()
            if key in KEYS:rows.append(dict(line=no,key=key,value=value.strip()))
    return rows


def native_proof(data):
    if hashlib.sha256(data).hexdigest()!=IMAGE_SHA:raise ValueError('Unreviewed executable')
    p=PE(data)
    if p.bytes(p.off(0x270f1ac),7)!=bytes.fromhex('c6837c01000001'):raise ValueError('Constructor default changed')
    if p.rel(0x270f264,7,3)!=0x3629800:raise ValueError('Flag reference changed')
    if p.bytes(p.off(0x3629800),14)!=b'-debugscripts\0':raise ValueError('Flag literal changed')
    if p.rel(0x270f26b,5,1)!=0x1a90014:raise ValueError('Substring call changed')
    if p.bytes(p.off(0x270f275),6)!=bytes.fromhex('b001eb0232c0'):raise ValueError('Flag polarity changed')
    if p.bytes(p.off(0x270f27b),6)!=bytes.fromhex('88837c010000'):raise ValueError('Flag field write changed')
    if p.bytes(p.off(0x2287e6b),8)!=bytes.fromhex('80b87c010000000f'):raise ValueError('Logger field read changed')
    if p.rel(0x2287e72,6,2)!=0x22880d9:raise ValueError('Early-return branch changed')
    if p.rel(0x1e7407d,5,1)!=0x270f020:raise ValueError('Engine construction changed')
    return dict(image_sha256=IMAGE_SHA,constructor=0x270f020,constructor_default_write=0x270f1ac,
        flag_reference=0x270f264,substring_call=0x270f26b,flag_field_write=0x270f27b,
        initializer_guard=0x2287e6b,skip_target=0x22880d9,actual_command_line_observed=False,
        ini_alone_cannot_clear_constructor_gate=True,meaning='Logging-disabled predicate derived from absence of native -debugscripts substring; not inferred from IsFinalBuild.')


def audit():
    exe=GAME/'bin/x64_dx12/witcher3.exe';proof=native_proof(exe.read_bytes())
    cfg=GAME/'bin/config';descriptor=cfg/'config_description.xml';layers=pc_order(descriptor.read_text(encoding='utf-8-sig'))
    rows=[];files=0
    for layer in layers:
        for f in sorted((cfg/layer.replace('\\','/')).glob('*.ini')):
            files+=1
            for row in logger_rows(f.read_text(encoding='utf-8-sig',errors='replace')):
                rows.append(dict(path=str(f.relative_to(cfg)),**row))
    general=cfg/'base/general.ini';sha=hashlib.sha256(general.read_bytes()).hexdigest()
    result=dict(schema=1,native=proof,config=dict(descriptor_sha256=hashlib.sha256(descriptor.read_bytes()).hexdigest(),
        ordered_pc_layers=layers,ini_files_inspected=files,logger_rows=rows,general_sha256=sha,
        restoration='original' if sha==ORIGINAL else 'staged' if sha==STAGED else 'unrecognized_drift'),
        game_launched=False,installed_files_modified=False,observer_installed=False,
        dx11_expected_exe_present=(GAME/'bin/x64/witcher3.exe').is_file(),actual_test_executable_not_inferred=True)
    buf=ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None,5,None,0,buf)!=0:raise ValueError('Documents resolution failed')
    documents=Path(buf.value)
    # ONE source-guided alternative, not a scan: Documents + current game's
    # known application folder. Exact native app-spec population remains a limit.
    candidates=[REPO/'build/sparse-interface-prerequisites-v1/retail-logs/scriptslog.txt',
                documents/'The Witcher 3/scriptslog.txt']
    result['log_checks']=[]
    for name,f in zip(('configured_probe','documents_application_candidate'),candidates):
        row=dict(candidate=name,exists=f.is_file())
        if f.is_file():
            with f.open('rb') as stream:header=b'Debugging scripts for ' in stream.read(16384)
            row.update(size=f.stat().st_size,modified_epoch=f.stat().st_mtime,native_header_seen=header)
        result['log_checks'].append(row)
    result['user_config']=[]
    for name in ('user.settings','dx12user.settings'):
        f=documents/'The Witcher 3'/name;items=[]
        if f.is_file():
            for row in logger_rows(f.read_text(encoding='utf-8-sig',errors='replace')):
                value=row['value']
                # Never export another user directory or unrelated config text.
                if row['key']=='DebugScriptsLogDir':value='empty' if not value else 'nonempty_private'
                elif value.lower() not in ('true','false','0','1'):value='other_private'
                items.append(dict(key=row['key'],value=value))
        result['user_config'].append(dict(filename=name,exists=f.is_file(),logger_values=items))
    result['limits']=['No real runtime command line, effective CVar values, file-open error or event output observed.',
        'No universal user-settings-versus-native-CVar precedence claim from mere key presence.',
        'Documents app-directory candidate is not proof of the exact runtime default path.',
        'No new test is authorized; confirm existing launch route/arguments first.']
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    output=a.output.resolve()
    if not output.is_relative_to((REPO/'build').resolve()) or output.exists():raise ValueError('Fresh ignored output only')
    result=audit();output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Read-only native proof and bounded config/path inventory complete; no retail activation claimed.')
