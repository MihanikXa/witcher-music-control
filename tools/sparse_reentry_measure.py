"""Read-only per-pipeline re-entry timelines and 50ms private PCM evidence."""
import argparse
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

from regional_music import graph,ancestors
from sparse_approved_review import recorder
from sparse_approved_cue import read
from white_orchard_prepare import build_path,digest
from music_material_opus import chunks
import struct


def verified_pcm(path):
    parts=chunks(path.read_bytes())
    fmt=parts[b'fmt ']
    if len(fmt)<16:raise ValueError('Incomplete PCM format')
    codec,channels,rate,byte_rate,block,bits=struct.unpack_from('<HHIIHH',fmt)
    if codec==65534:
        if len(fmt)!=40:raise ValueError('Unsupported extensible format size')
        extension,valid_bits,mask=struct.unpack_from('<HHI',fmt,16)
        # Installed Wwise Recorder emits zero valid-bits with this exact 5.1
        # layout. Container width/subtype and source-matched PCM establish16bit;
        # do not generalize the zero field to arbitrary formats.
        known_zero=valid_bits==0 and (channels,rate,mask)==(6,48000,1551)
        if (extension!=22 or not (valid_bits==16 or known_zero)
                or fmt[24:40]!=bytes.fromhex('0100000000001000800000aa00389b71')):
            raise ValueError('Unsupported extensible PCM')
    elif codec!=1:raise ValueError('Unsupported Recorder codec')
    if (not channels or not rate or bits!=16 or block!=channels*2 or byte_rate!=rate*block
            or len(parts[b'data'])%block):raise ValueError('Incomplete/unsupported PCM frames')
    x,metadata=recorder(path)
    metadata['format']=dict(codec=codec,container_bits=bits,
                            valid_bits=struct.unpack_from('<H',fmt,18)[0] if codec==65534 else bits)
    return x,metadata


def summarize(case, source):
    objects,parents,_=graph(source)
    rows={};rtpcs={}
    for sample in case['samples']:
        voices={str(v['pipelineID']):v for v in sample['voices']}
        for key,value in sample['contributions'].items():
            v=voices.get(key);d=value['return']
            if not v or not d['objects'] or v['objectGUID'] not in objects:continue
            chain=[n for n in ancestors(objects[v['objectGUID']],parents) if n.get('ShortID')]
            ids=[int(n.get('ShortID')) for n in chain]
            names=[n.get('Name') for n in chain]
            role=('cue' if 1029261546 in ids else 'rest' if 4111369 in ids else
                  'outro' if 800050000 in ids else 'combat' if 'village_combat' in names else 'other')
            row=rows.setdefault(key,dict(pipeline=int(key),guid=v['objectGUID'],role=role,ids=ids,path=names,envelope=[]))
            row['envelope'].append([sample['time'],d['volume'],v['isStarted'],v['isVirtual']])
        for r in sample['rtpcs']:
            rtpcs.setdefault(str(r['gameObjectId'])+':'+r['name'],set()).add(r['value'])
    for row in rows.values():
        env=row['envelope'];row.update(first=env[0][0],last=env[-1][0],peak=max(e[1] for e in env),
            started_first=min((e[0] for e in env if e[2]),default=None),
            audible_first=min((e[0] for e in env if e[2] and not e[3] and e[1]>-90),default=None),
            audible_last=max((e[0] for e in env if e[2] and not e[3] and e[1]>-90),default=None))
    return dict(case=case['case'],events=case['events'],complete=case['complete'],pipelines=list(rows.values()),
                rtpcs={k:sorted(v) for k,v in rtpcs.items()},last_sample=case['samples'][-1]['time'])


def measure(folder, output):
    folder=build_path(folder);output=build_path(output)
    if output.exists():raise FileExistsError(output)
    raw=read(folder/'results.json')
    if not raw['complete'] or raw['cleanup_errors'] or raw.get('error'):raise ValueError('Incomplete/unclean capture')
    source=ET.parse(folder.parent/'authored-music.xml').getroot();cases=[]
    for case in raw['cases']:
        row=summarize(case,source)
        try:
            _,row['pcm']=verified_pcm(folder/(case['case']+'.wav'));row['pcm']['valid']=True
        except (ValueError,KeyError) as error:
            row['pcm']=dict(valid=False,error=str(error),sha256=digest(folder/(case['case']+'.wav')))
        cases.append(row)
        print(json.dumps(dict(case=row['case'],cue=[[v['pipeline'],round(v['first'],3),round(v['last'],3)] for v in row['pipelines'] if v['role']=='cue'],
            rest=[[v['pipeline'],round(v['first'],3),round(v['last'],3)] for v in row['pipelines'] if v['role']=='rest'],
            outro=[[round(v['first'],3),round(v['last'],3),round(v['peak'],2)] for v in row['pipelines'] if v['role']=='outro'])),flush=True)
    result=dict(passed_capture=True,all_pcm_valid=all(c['pcm']['valid'] for c in cases),raw_sha256=digest(folder/'results.json'),source_sha256=digest(folder.parent/'authored-music.xml'),cases=cases,
                clock_note='Profiler/action times are wall-clock; Recorder samples are a separate clock. Pipeline lifetime is not equivalent to audible PCM duration.',retail_verified=False)
    output.write_text(json.dumps(result)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();measure(a.folder,a.output)
