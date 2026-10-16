"""Build a private local listening index and measurements, never a game mod.

Requires explicit trusted installed FFmpeg, source paths and fresh ignored output.
No bundled tools, executable downloads, Wwise, bank generation or integration.
"""
import argparse
from array import array
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import re
import statistics
import subprocess

from music_material_opus import rewrap,verify_rewrap
from regional_baseline_reference import cache_index
from white_orchard_prepare import build_path,digest


def command(exe,args):
    p=subprocess.run([str(exe),'-hide_banner','-nostdin',*args],capture_output=True,timeout=180)
    if p.returncode:raise ValueError(p.stderr.decode('utf-8',errors='replace'))
    return p


def db(value):return round(20*math.log10(max(value,1e-12)),3)


def metrics(exe,path):
    p=command(exe,['-v','error','-i',str(path),'-map','0:a:0','-ac','2','-ar','8000','-f','f32le','pipe:1'])
    data=array('f');data.frombytes(p.stdout)
    if not data or any(not math.isfinite(x) for x in data):raise ValueError('Invalid decoded PCM')
    env=[]
    for start in range(0,len(data),1600):
        part=data[start:start+1600];env.append(db(math.sqrt(sum(x*x for x in part)/len(part))))
    quiet=[]
    for i,v in enumerate(env):
        if v<-60:
            if not quiet or i*.1-quiet[-1][1]>.101:quiet.append([round(i*.1,2),round((i+1)*.1,2)])
            else:quiet[-1][1]=round((i+1)*.1,2)
    quiet=[[a,min(b,len(data)/16000)] for a,b in quiet if min(b,len(data)/16000)-a>=.5]
    valleys=[]
    # Inspection anchors only: low local energy is NOT a musical phrase ending.
    for i in sorted(range(50,len(env)-50),key=lambda n:statistics.mean(env[n-5:n+5])):
        if all(abs(i*.1-t)>15 for t in valleys):valleys.append(round(i*.1,1))
        if len(valleys)==3:break
    sorted_env=sorted(env)
    return dict(seconds=len(data)/16000,analysis_rate=8000,analysis_channels=2,downsampled_analysis_only=True,
        rms_dbfs=db(math.sqrt(sum(x*x for x in data)/len(data))),peak_downsampled_dbfs=db(max(abs(x) for x in data)),
        envelope_p10_dbfs=sorted_env[int(len(env)*.1)],envelope_p90_dbfs=sorted_env[int(len(env)*.9)],
        first_second_rms_dbfs=statistics.mean(env[:10]),last_second_rms_dbfs=statistics.mean(env[-10:]),
        quiet_below_minus60=quiet,low_energy_inspection_seconds=sorted(valleys),rms100ms_dbfs=env)


def choose(catalog,item):
    if item['pool']=='native':
        s=next(s for s in catalog['native']['segments'] if s['segment']==item['key'])
        t=next(t for t in s['tracks'] if any(x['id']==item['media'] for x in t['sources']))
        if not t['reviewed_generic']:raise ValueError('Native target lacks existing reviewed generic ancestry')
        src=next(x for x in t['sources'] if x['id']==item['media'])
        paths={x['file'] for x in src['originals']}
        if len(paths)!=1:raise ValueError('Missing/ambiguous original audio mapping')
        authored_reuse=[]
        for other in catalog['native']['segments']:
            for tr in other['tracks']:
                if any(x['id']==item['media'] for x in tr['sources']) and any(
                    x['name'] in ('quests_and_cutscenes','quests_cutscenes') for x in tr['ancestry']):
                    authored_reuse.append(dict(bank=other['bank'],segment=other['segment'],track=tr['id']))
        return dict(original=next(iter(paths)),bank=s['bank'],segment=s['segment'],track=t['id'],media=item['media'],
            native_segment_ms=s['duration_ms'],markers=s['markers'],clips=t['clips'],
            other_stems=[dict(track=x['id'],name=x['name'],rtpc=x['rtpc']) for x in s['tracks'] if x['id']!=t['id']],
            selected_rtpc=t['rtpc'],authored_reuse=authored_reuse,
            preview_note='Full original source; base stem only where noted. Not a simulated Wwise mix; segment and file clocks can differ.')
    t=next(t for t in catalog['music_plus']['tracks'] if item['key'] in [w for group in t['wems'] for w in group])
    if sum(map(len,t['wems']))!=1:raise ValueError('Layered/alternative MP source needs explicit separate review')
    if not t['assignments'] or any(not a['representative_segments'] for a in t['assignments']):
        raise ValueError('Selected MP source lacks segment join')
    expected=int(item['key'][:-4])
    for assignment in t['assignments']:
        actual={src['id'] for s in assignment['representative_segments'] for tr in s['tracks'] for src in tr['sources']}
        if actual!={expected}:raise ValueError('Selected MP segment/source mismatch')
    a=t['assignments'][0];s=a['representative_segments'][0]
    return dict(source=t['source'],name=t['name'],wem=item['key'],media=int(item['key'][:-4]),
        bank=a['bank'],segment=s['segment'],tracks=[x['id'] for x in s['tracks']],
        markers=s['markers'],segment_ms=s['duration_ms'],editor_ms=t['editor_ms'],
        assignments=[{k:a[k] for k in ('playlist_index','track_index','region','title','bank')} for a in t['assignments']],
        preview_note='Unchanged compressed packets, standard Ogg wrapper. Display title/source are MP metadata, not independently authenticated credits.')


def page(rows):
    def e(x):return html.escape(str(x),quote=True)
    cards=[]
    for r in rows:
        m=r['metrics'];ident=r['identity'];duration=m['seconds'];priority='Priority audition' if r['priority'] else 'Further comparison'
        markers='; '.join(f"{x['position']/1000:.3f}s (ID{x['id']})" for x in ident['markers'])
        buttons=''.join(f'<button type="button" data-jump="{t:.3f}">{label}</button>' for label,t in
            [('Beginning',0),('Middle',duration/2),('Ending',max(0,duration-20))])
        buttons+=''.join(f'<button type="button" data-jump="{t}">Energy valley {t:.1f}s</button>' for t in m['low_energy_inspection_seconds'])
        risk=r['risk']+(' VERIFIED native dedicated-authored reuse; do not repurpose without explicit policy review.' if ident.get('authored_reuse') else '')
        public_identity=dict(ident)
        if 'assignments' in public_identity:
            public_identity['assignments']=[{k:v for k,v in a.items() if k!='title'} for a in ident['assignments']]
        cards.append(f'''<article data-id="{e(r['id'])}"><h2>{e(r['id'])} · {e(r['title'])}</h2>
<p class="tag">{priority} · {e(r['function'])} · {duration:.2f}s · {e(ident.get('source','The Witcher 3 / REDkit original'))}</p>
<audio controls preload="none" src="{e(r['preview'])}"></audio><div>{buttons}</div>
<p>{e(r['reason'])}</p><p><b>Listen for:</b> {e(r['listen_for'])}</p><p><b>Risk:</b> {e(risk)}</p>
<p class="small">{e(ident['preview_note'])} Nothing has been subjectively auditioned by Codex.</p>
<label>Your decision <select class="decision"><option>Unreviewed</option><option>Keep</option><option>Maybe</option><option>Reject</option></select></label>
<label>Possible role <select class="role"><option>Undecided</option><option>Brief punctuation</option><option>Atmospheric development</option><option>Regional identity</option><option>Long situation-specific piece</option><option>Resolution</option></select></label>
<p><textarea rows="2" placeholder="Your notes: entrance, middle, ending, story association, too insistent?"></textarea></p>
<details><summary>Measurements and source identity</summary><p>Stereo-analysis RMS {m['rms_dbfs']:.1f}dBFS; 10–90% envelope {m['envelope_p10_dbfs']:.1f} to {m['envelope_p90_dbfs']:.1f}dBFS. Not LUFS, perceived loudness or proof of quiet instrumentation. No loudness normalization.</p>
<p>Native/MP segment-clock markers: {e(markers)}. Buttons seek the full source-file clock, not translated segment markers; energy valleys are inspection points, not approved edit boundaries.</p><pre>{e(json.dumps(public_identity,indent=2))}</pre></details></article>''')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WMC — Private Sparse Auditions</title>
<style>body{max-width:960px;margin:32px auto;padding:0 20px;background:#151a1c;color:#e9e4da;font:17px/1.5 system-ui}article{border:1px solid #495456;border-radius:12px;padding:20px;margin:24px 0}h1,h2{line-height:1.2}.tag{color:#b8d5c5}.small,details{font-size:14px;color:#bdc7c7}audio,textarea{width:100%}button,select{margin:5px;padding:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#a0d8e8}</style>
<h1>Sparse exploration — listening shortlist</h1><p>Private local audition only. No mod installation or soundtrack decision. Start with S01–S07; compare the remaining material only if useful. Codex selected structural prospects and measured audio; it has not listened or judged their musical quality.</p>
<p>Listen to each entrance after a little real silence, then its ending before judging the middle. Full native files/stems may not resolve like their in-game layered arrangements. Imported credits are Music Plus labels. No previews are normalized: use a comfortable volume; do not equate raw level with musical restraint.</p>
<p>Beginning / Middle / Ending buttons seek the complete recording; nothing is cut or looped. Only one player runs at a time. Notes save locally when browser storage is available; export before closing to be safe.</p>
<button id="stop">Stop all</button><button id="export">Export listening decisions (JSON)</button><a href="auditions.m3u8">M3U fallback</a><p id="storage"></p>'''+''.join(cards)+'''
<script>
const cards=[...document.querySelectorAll('article')];
for(const card of cards){const a=card.querySelector('audio');a.addEventListener('play',()=>{document.querySelectorAll('audio').forEach(x=>{if(x!==a)x.pause()})});
card.querySelectorAll('[data-jump]').forEach(b=>b.onclick=()=>{const seek=()=>{a.currentTime=Number(b.dataset.jump);a.play().catch(()=>{})};if(a.readyState)seek();else{a.addEventListener('loadedmetadata',seek,{once:true});a.load()}});
const inputs=[...card.querySelectorAll('select,textarea')];try{const prior=JSON.parse(localStorage.getItem('wmc-audition-'+card.dataset.id)||'null');if(prior)inputs.forEach((x,i)=>x.value=prior[i])}catch(e){document.querySelector('#storage').textContent='Browser storage unavailable: export your decisions.'}
inputs.forEach(x=>x.oninput=()=>{try{localStorage.setItem('wmc-audition-'+card.dataset.id,JSON.stringify(inputs.map(x=>x.value)))}catch(e){document.querySelector('#storage').textContent='Browser storage unavailable: export your decisions.'}})}
document.querySelector('#stop').onclick=()=>document.querySelectorAll('audio').forEach(a=>a.pause());
document.querySelector('#export').onclick=()=>{const rows=cards.map(c=>({id:c.dataset.id,title:c.querySelector('h2').textContent,decision:c.querySelector('.decision').value,role:c.querySelector('.role').value,notes:c.querySelector('textarea').value}));const url=URL.createObjectURL(new Blob([JSON.stringify(rows,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='wmc-listening-decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
</script></html>'''


def build(catalog,selection,source,audit,ffmpeg,output):
    output=build_path(output)
    if any(x in str(ffmpeg.resolve()).lower() for x in ('music-plus','reference')):
        raise ValueError('Bundled/reference executable forbidden')
    if not ffmpeg.is_file():raise FileNotFoundError(ffmpeg)
    output.mkdir(exist_ok=False);(output/'audio').mkdir()
    c=json.loads(catalog.read_text(encoding='utf-8'));items=json.loads(selection.read_text(encoding='utf-8'))
    if digest(source/'Interactive Music Hierarchy/music.wwu')!=c['native']['music_source_sha256']:
        raise ValueError('Native source changed since inventory')
    if digest(audit/'main/mods/modMusicPlus/editor/index.json')!=c['music_plus']['editor_sha256']:
        raise ValueError('Editor metadata changed since inventory')
    if len({r['id'] for r in items})!=len(items):raise ValueError('Duplicate audition ID')
    inputs={};rows=[]
    cache=audit/'pack/mods/modMusicPlus/content/soundspc.cache'
    if digest(cache)!=c['music_plus']['pack_sha256']:raise ValueError('Pack changed since inventory')
    with cache.open('rb') as f:
        entries=cache_index(f)
        for item in items:
            identity=choose(c,item)
            filename=item['id']+'-'+re.sub('[^A-Za-z0-9 -]','',item['title']).replace(' ','-')+'.opus'
            preview=output/'audio'/filename
            if item['pool']=='mp':
                offset,n=entries[item['key']];f.seek(offset);data=f.read(n)
                wrapped,info=rewrap(data);preview.write_bytes(wrapped)
                identity['packet_readback']=verify_rewrap(data,preview.read_bytes())
                identity['wem_sha256']=hashlib.sha256(data).hexdigest();identity['opus_header']=info
                measure=metrics(ffmpeg,preview)
                if abs(measure['seconds']-info['seconds'])>1/8000:raise ValueError('Decoded duration disagrees with Wwise header')
            else:
                original=(source/'Originals/SFX'/identity['original']).resolve()
                if not original.is_relative_to((source/'Originals/SFX').resolve()):raise ValueError('Source traversal')
                sha=digest(original);inputs[str(original)]=sha;identity['original_sha256']=sha
                measure=metrics(ffmpeg,original)
                command(ffmpeg,['-v','error','-i',str(original),'-map','0:a:0','-c:a','libopus','-b:a','160k',str(preview)])
                check=metrics(ffmpeg,preview)
                if abs(check['seconds']-measure['seconds'])>.01:raise ValueError('Preview duration drift')
                if digest(original)!=sha:raise ValueError('Original input changed')
            row=dict(item,identity=identity,metrics=measure,preview='audio/'+filename,preview_sha256=digest(preview))
            rows.append(row);print(json.dumps(dict(id=item['id'],seconds=measure['seconds'],preview=filename)),flush=True)
    (output/'index.html').write_text(page(rows),encoding='utf-8')
    (output/'auditions.m3u8').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{r['metrics']['seconds']:.3f},{r['id']} {r['title']}\n{r['preview']}\n" for r in rows),encoding='utf-8')
    (output/'auditions.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    with (output/'auditions.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['id','title','source','seconds','function','risk','file'])
        for r in rows:w.writerow([r['id'],r['title'],r['identity'].get('source','The Witcher 3'),r['metrics']['seconds'],r['function'],r['risk'],r['preview']])
    provenance=dict(ffmpeg_path=str(ffmpeg.resolve()),ffmpeg_sha256=digest(ffmpeg),
        version=command(ffmpeg,['-version']).stdout.decode('utf-8',errors='replace'),
        catalog_sha256=digest(catalog),selection_sha256=digest(selection),original_inputs=inputs,
        preview_count=len(rows),index_sha256=digest(output/'index.html'),subjectively_listened=False,
        private_audition_only=True,no_game_resources_written=True)
    (output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('catalog','selection','source','audit','ffmpeg','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();build(a.catalog,a.selection,a.source,a.audit,a.ffmpeg,a.output)
