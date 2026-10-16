"""Read-only profiler/50ms PCM evidence for the bounded sparse fixture."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path, digest
from white_orchard_fade_measure import pcm
from regional_music import graph, ancestors


def intervals(times, maximum_gap=1.5):
    result=[]
    for time in sorted(times):
        if not result or time-result[-1][-1]>maximum_gap:result.append([time,time])
        else:result[-1][-1]=time
    return result


def audio(path):
    samples,channels,rate=pcm(path)
    hop=(rate//20)*channels
    envelope=[]
    for offset in range(0,len(samples),hop):
        chunk=samples[offset:offset+hop]
        envelope.append(math.sqrt(sum(v*v for v in chunk)/len(chunk)))
    return dict(sha256=digest(path),seconds=len(samples)/channels/rate,channels=channels,rate=rate,
                rms50ms=envelope,zero_windows=intervals([i*.05 for i,v in enumerate(envelope) if v==0],.051))


def case_summary(case, source=None):
    voices={};effective={}
    if source is not None:objects,parents,_=graph(source)
    for sample in case['samples']:
        for pipeline,contribution in sample['contributions'].items():
            d=contribution['return'];names=[n['name'] for n in d['objects']]
            if not names:continue  # Freed pipeline between independent profiler queries.
            key='/'.join(names)
            row=voices.setdefault(key,dict(path=names,times=[],db=[],objects=d['objects'],guids=set()))
            row['times'].append(sample['time']);row['db'].append(d['volume'])
            row['guids'].update(v['objectGUID'] for v in sample['voices'] if str(v['pipelineID'])==pipeline)
        for v in sample['rtpcs']:
            key=str(v['gameObjectId'])+':'+v['name']
            effective.setdefault(key,set()).add(v['value'])
    result={}
    for key,row in voices.items():
        result[key]=dict(path=row['path'],intervals=intervals(row['times']),
            audible_intervals=intervals([t for t,v in zip(row['times'],row['db']) if v>-90]),
            peak_db=max(row['db']),median_db=statistics.median(row['db']),
            envelope=list(zip(row['times'],row['db'])),sample_objects=row['objects'],voice_guids=sorted(row['guids']))
        if source is not None:
            result[key]['source_ancestry']={g:[dict(id=n.get('ID'),short_id=n.get('ShortID'),type=n.tag,name=n.get('Name'))
                for n in ancestors(objects[g],parents) if n.get('ShortID')]
                for g in sorted(row['guids']) if g in objects}
    times=[s['time'] for s in case['samples']]
    return dict(case=case['case'],mode=case['mode'],complete=case['complete'],events=case['events'],
                raw_case_sha256=hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest(),
                effective_rtpcs={k:sorted(v) for k,v in effective.items()},voices=result,
                sample_spacing_median=statistics.median([b-a for a,b in zip(times,times[1:])]))


def measure(folder):
    folder=build_path(folder)
    output=folder/'sparse-measurements.json'
    if output.exists():raise FileExistsError(output)
    raw=json.loads((folder/'results.json').read_text())
    if not raw['complete'] or raw['cleanup_errors'] or any(not c['complete'] for c in raw['cases']):
        raise ValueError('Incomplete/unclean captures are retained rejected evidence')
    result=dict(mode=raw['mode'],raw_sha256=digest(folder/'results.json'),cases=[],
                timing_note='Recorder output can retain only a later portion after routing/virtualization changes; use profiler wall time for transitions. Uninterrupted cycle PCM is analyzed separately.',
                fixtures_only=True,retail_verified=False)
    source=ET.parse(folder.parent/'authored-music.xml')
    for case in raw['cases']:
        summary=case_summary(case,source);path=folder/(case['case']+'.wav')
        if not path.exists():raise ValueError('Missing Recorder output cannot prove silence')
        summary['pcm']=audio(path)
        result['cases'].append(summary)
        print(json.dumps(dict(mode=raw['mode'],case=case['case'],seconds=summary['pcm']['seconds'])),flush=True)
    output.write_text(json.dumps(result)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',type=Path,required=True)
    measure(p.parse_args().folder)
