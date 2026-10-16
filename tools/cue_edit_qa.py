"""Read-only private cue-pack gate: inputs, cut clocks, PCM, FDN state, links.
This is not a game-bank gate or proof of subjective/browser playback quality.
"""
import argparse
from functools import lru_cache
from html.parser import HTMLParser
import json
from pathlib import Path
import wave
import numpy as np

from cue_edit_render import SOURCES,FEEDBACK,decode,level,validate_plan
from cue_freeze_dsp import RATE,dry_envelope
from white_orchard_prepare import build_path,digest


class Links(HTMLParser):
    def __init__(self):super().__init__();self.audio=[];self.external=[];self.cards=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='audio':self.audio.append(a['src'])
        if tag=='article':self.cards+=1
        for key in ('src','href'):
            if a.get(key,'').startswith(('http:','https:')):self.external.append(a[key])


def verify(folder,plan_path,output):
    folder=build_path(folder);output=build_path(output)
    if output.exists():raise FileExistsError(output)
    plan=json.loads(plan_path.read_text(encoding='utf-8'));m=json.loads((folder/'renders.json').read_text(encoding='utf-8'))
    if digest(plan_path)!=m['plan_sha256'] or digest(FEEDBACK)!=m['feedback_sha256'] or digest(SOURCES/'auditions.json')!=m['source_metadata_sha256']:
        raise ValueError('Plan/feedback/source metadata fingerprint mismatch')
    users={r['id']:r for r in json.loads(FEEDBACK.read_text(encoding='utf-8'))};validate_plan(plan,users)
    sources={r['id']:r for r in json.loads((SOURCES/'auditions.json').read_text(encoding='utf-8'))}
    planned={c['cue']:c for c in plan['cues']}
    if {c['settings']['cue'] for c in m['cues']}!=set(planned):raise ValueError('Not every requested cue completed')
    files=[];proofs=[]
    @lru_cache(maxsize=1)
    def original(ident):
        row=sources[ident];path=SOURCES/row['preview']
        if digest(path)!=row['preview_sha256']:raise ValueError('Source preview changed')
        return decode(path)
    for cue in m['cues']:
        s=cue['settings'];p=cue['proof'];expected=dict(planned[s['cue']]);x=original(s['source'])
        if expected['source_out'] is None:expected['source_out']=len(x)/RATE
        if expected['dry_fade'] is None:expected['dry_fade']=[expected['source_out']-plan['fallback_fades'][s['cue']],expected['source_out']]
        if s!=expected:raise ValueError('Undeclared crop/DSP/assumption change')
        a,b=round(s['source_in']*RATE),round(s['source_out']*RATE)
        if (a,b)!=(p['source_start_frame'],p['source_end_frame']):raise ValueError('Clock offset')
        env=dry_envelope(b-a,RATE,s['fade_in'],s['dry_fade'][0]-s['source_in'],s['dry_fade'][1]-s['source_in'])
        dry=x[a:b]*env[:,None]*p['headroom_gain'];lead=round(plan['lead_silence']*RATE);trail=round(plan['trail_silence']*RATE)
        total=lead+(b-a)+round(s['tail_extra']*RATE)+trail
        if set(cue['renders'])!=set(s['variants']):raise ValueError('Missing comparison')
        cproof=p['field_proof']['C'];settled=[r['state_energy'] for r in cproof['energy_trace'] if r['seconds']>s['freeze_transition']+.03]
        drift=(max(settled)-min(settled))/max(settled)
        if drift>1e-10 or cproof['new_excitation_samples_after_capture']!=0:raise ValueError('Not a demonstrated lossless closed-input freeze')
        row=dict(cue=s['cue'],freeze_energy_relative_drift=drift,variants={})
        for v,record in cue['renders'].items():
            path=folder/record['file'];files.append(path.resolve())
            if digest(path)!=record['qa']['sha256']:raise ValueError('Rendered payload changed')
            with wave.open(str(path),'rb') as w:
                if (w.getnchannels(),w.getframerate(),w.getsampwidth(),w.getnframes())!=(2,RATE,2,total):raise ValueError('PCM layout/duration drift')
                pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2)
            y=pcm.astype(np.float64)/32768
            if np.any(pcm[:lead]) or np.any(pcm[-trail:]) or np.any(np.abs(pcm.astype(np.int32))>=32767):raise ValueError('Silence/headroom failed')
            n=b-a if v=='A' else round(p['freeze_relative']*RATE)
            if not np.array_equal(y[lead:lead+n],np.rint(dry[:n]*32767)/32768):raise ValueError('Incorrect source material/crop before wet entry')
            active=y[lead:-trail];post=active[b-a:]
            if v=='A' and np.any(post):raise ValueError('Dry control has an unexpected wet tail')
            if v=='C' and level(post[:RATE])<-72:raise ValueError('Inaudible freeze')
            if np.any(active[0]) or np.any(active[-1]):raise ValueError('Hard outer sample boundary')
            spec=np.abs(np.fft.rfft(post,axis=0))**2;freq=np.fft.rfftfreq(len(post),1/RATE)
            low=float(np.sum(spec[(freq>=20)&(freq<150)])/max(np.sum(spec[freq>=20]),1e-20))
            windows=[level(active[i:i+RATE//20]) for i in range(0,len(active),RATE//20)]
            row['variants'][v]=dict(sha256=record['qa']['sha256'],peak=float(np.max(np.abs(y))),
                first_post_dry_second_dbfs=level(post[:RATE]),tail_20_150hz_energy_fraction=low,
                final_100ms_before_context_dbfs=level(active[-RATE//10:]),pcm50ms_dbfs=windows)
        proofs.append(row)
    if set(files)!={p.resolve() for p in (folder/'audio').glob('*')} or len(files)!=len(set(files)):raise ValueError('Missing/extra/duplicate render payloads')
    parser=Links();parser.feed((folder/'index.html').read_text(encoding='utf-8'))
    if parser.cards!=len(planned) or parser.external or any(not (folder/a).is_file() for a in parser.audio):raise ValueError('Broken or nonlocal listening index')
    result=dict(passed=True,cues=len(proofs),renders=len(files),original_preview_hashes_verified=len({c['settings']['source'] for c in m['cues']}),
        lead_trail_exact_zero=True,crops_and_unprocessed_prefixes_exact=True,all_declared_fields_exact=True,
        clipping_samples=0,all_files_read_back=True,local_audio_links=len(parser.audio),external_resources=0,
        index_sha256=digest(folder/'index.html'),render_metadata_sha256=digest(folder/'renders.json'),
        browser_playback_verified=False,subjectively_listened=False,proofs=proofs)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='proofs'}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('folder','plan','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();verify(a.folder,a.plan,a.output)
