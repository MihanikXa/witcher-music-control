"""Read-only I&I inventory. Writes only ignored build/ink-and-iron-audit.

Bundle reader: existing validated audit-ui.py. Cache table layout checked against
Systemcluster/w3edit src/texture_cache.rs and local HCXT v6 files. No cooking.
"""
import argparse
import collections
import configparser
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/ink-and-iron-0.8-audit'
spec = importlib.util.spec_from_file_location('audit', ROOT/'tools/audit-ui.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
spec2 = importlib.util.spec_from_file_location('shadows', ROOT/'tools/audit-text-shadows.py')
shadows = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(shadows)

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def output_resource(module, key):
    dest=(OUT/'payloads'/module/key).resolve()
    if not dest.is_relative_to((OUT/'payloads').resolve()): raise ValueError('Unsafe resource key')
    return dest

def cache_entries(p):
    length = p.stat().st_size
    with p.open('rb') as f:
        if length < 32: raise ValueError('Truncated cache')
        f.seek(-32, 2); foot = f.read(32)
        _, pages, count, strings, mips, magic, version = struct.unpack('<QIIII4sI', foot)
        if magic != b'HCXT' or version not in (6, 7): raise ValueError('Unknown cache format')
        start = length-32-count*52; ss = start-strings; ms = ss-mips*4
        if ms < 0 or pages*4096 > ms: raise ValueError('Invalid cache tables')
        f.seek(ss); names = f.read(strings)
        f.seek(start); table = f.read(count*52)
        for i in range(count):
            b = table[i*52:(i+1)*52]
            keyhash, noff, page, packed, size = struct.unpack_from('<IiIII', b)
            end = names.find(b'\0', noff)
            if noff < 0 or end < noff: raise ValueError('Invalid cache name')
            name = names[noff:end].decode('utf-8').lower().replace('\\','/')
            if not name or page*4096+packed > ms: raise ValueError('Invalid cache entry')
            yield dict(resource=name, key_hash=f'{keyhash:08x}', offset=page*4096,
                       packed=packed, size=size, width=struct.unpack_from('<H',b,24)[0],
                       height=struct.unpack_from('<H',b,26)[0], version=version,
                       container=str(p), kind='texture')

def scripts(p, owner):
    b = p.read_bytes()
    t = b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
    t = re.sub(r'/\*.*?\*/|//[^\n]*', '', t, flags=re.S)
    rows=[]
    for m in re.finditer(r'@(wrapMethod|replaceMethod|addMethod|addField)\s*\(\s*(\w+)\s*\)\s*(?:\w+\s+)*?(?:function|event|var)\s+(\w+)',t):
        rows.append(dict(owner=owner,path=str(p),annotation=m[1],class_name=m[2],member=m[3]))
    return rows

def string_index(p):
    b=p.read_bytes()
    if b[:4]!=b'RTSW': raise ValueError('Unknown strings format')
    def count(pos):
        first=b[pos]; pos+=1; n=first&63
        if first&64:
            shift=6
            while True:
                v=b[pos]; pos+=1; n|=(v&127)<<shift; shift+=7
                if not v&128: break
        return n,pos
    n,pos=count(10); ids=[struct.unpack_from('<III',b,pos+i*12)[0] for i in range(n)]; pos+=n*12
    n,pos=count(pos); keys=[struct.unpack_from('<II',b,pos+i*8) for i in range(n)]
    pair=(struct.unpack_from('<H',b,8)[0],struct.unpack('<H',b[-2:])[0])
    # Current I&I has unencrypted v164 indexes; installed EN uses the established
    # English XOR mask. Comparing raw indexes across these schemes misses IDs.
    magic=0
    if p.stem.lower()=='en':
        if pair==(17303,20793): magic=0x79321793
        elif pair!=(0,0): raise ValueError('Unknown English localization key pair')
    return dict(ids=[i^magic for i in ids],keys={k:i^magic for k,i in keys},key_pair=pair,
                english_normalized=p.stem.lower()=='en')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--game',type=Path,required=True)
    ap.add_argument('--reference',type=Path,default=ROOT/'reference/ink-and-iron-0.8')
    ap.add_argument('--out',type=Path,default=ROOT/'build/ink-and-iron-0.8-audit')
    ap.add_argument('--mods-settings',type=Path,required=True)
    ap.add_argument('--vanilla-fonts-archive',type=Path)
    ap.add_argument('--all-in-one-archive',type=Path,help='Read-only provenance and alternative IM Fell inventory; NOT an install recommendation')
    a=ap.parse_args()
    global OUT
    OUT=a.out.resolve()
    if not OUT.is_relative_to((ROOT/'build').resolve()): raise ValueError('Audit output must stay in ignored build/')
    OUT.mkdir(parents=True,exist_ok=True)
    refs=a.reference.resolve()
    if a.vanilla_fonts_archive:
        dest=OUT/'fonts-vanilla-original'; dest.mkdir(exist_ok=True)
        with zipfile.ZipFile(a.vanilla_fonts_archive) as z:
            for n in z.namelist():
                target=(dest/n).resolve()
                if not target.is_relative_to(dest.resolve()): raise ValueError('Unsafe ZIP path')
            z.extractall(dest)
    provenance=[]
    if a.all_in_one_archive:
        dest=OUT/'im-fell-original'; dest.mkdir(exist_ok=True)
        with zipfile.ZipFile(a.all_in_one_archive) as z:
            for n in z.namelist():
                if n.endswith('/'): continue
                if '/modInkAndIronFonts/' in n:
                    target=(dest/n).resolve()
                    if not target.is_relative_to(dest.resolve()): raise ValueError('Unsafe ZIP path')
                    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(z.read(n))
                local=refs/n
                if local.is_file():
                    h=hashlib.sha256()
                    with z.open(n) as member:
                        for chunk in iter(lambda: member.read(1048576),b''): h.update(chunk)
                    provenance.append(dict(path=n,canonical_sha256=digest(local),archive_member_sha256=h.hexdigest()))
    config=configparser.ConfigParser(); config.read(a.mods_settings,encoding='utf-8-sig')
    order={k.lower():dict(enabled=config[k].get('Enabled'),priority=config[k].get('Priority'),package=config[k].get('VK')) for k in config.sections()}
    files=[]; resources=[]; installed=[]; annotations=[]; errors=[]
    def scan(base, target, reference=False, label=None):
        for p in sorted(base.rglob('*')):
            if not p.is_file(): continue
            rel=p.relative_to(base).as_posix(); parts=p.relative_to(base).parts
            owner=label or (parts[1] if parts[0].lower() in ('mods','dlc') else 'vanilla' if not reference else 'configuration')
            if reference: files.append(dict(module=owner,path=rel,bytes=p.stat().st_size,sha256=digest(p)))
            if p.suffix.lower()=='.ws': annotations.extend(scripts(p,owner))
            if p.suffix.lower()=='.bundle' or p.name=='texture.cache':
                try:
                    es=shadows.index(p) if p.suffix.lower()=='.bundle' else cache_entries(p)
                    for e in es:
                        if not reference and e['resource'] not in wanted: continue
                        if reference: output_resource(owner,e['resource'])
                        e.update(module=owner,container=str(p),kind=e.get('kind','bundle'),order=order.get(owner.lower()))
                        target.append(e)
                except Exception as ex: errors.append(dict(path=str(p),error=str(ex)))
            elif 'content' in parts and p.name not in ('metadata.store',) and not p.name.endswith('.cache'):
                key='/'.join(parts[parts.index('content')+1:]).lower()
                if not reference and key not in wanted: continue
                target.append(dict(module=owner,resource=key,container=str(p),kind='loose',sha256=digest(p) if reference else None,order=order.get(owner.lower())))
            elif parts[0].lower()=='bin' and reference:
                target.append(dict(module=owner,resource=rel.lower(),container=str(p),kind='loose',sha256=digest(p)))
    scan(refs,resources,True)
    if a.vanilla_fonts_archive: scan(OUT/'fonts-vanilla-original',resources,True,'Fonts_Vanilla_archive')
    if a.all_in_one_archive: scan(OUT/'im-fell-original',resources,True,'Fonts_IM_Fell_archive')
    wanted={e['resource'] for e in resources}
    print('Reference inventory complete; reading deployed and vanilla indexes.',flush=True)
    for folder in ('Mods','DLC','content'): scan(a.game/folder,installed)
    print('Indexes complete; hashing and inspecting reference payloads.',flush=True)
    # scan() bases Mods/DLC need explicit owners (relative first component).
    for e in installed:
        p=Path(e['container']); rel=p.relative_to(a.game); e['module']=rel.parts[1] if rel.parts[0].lower() in ('mods','dlc') else 'vanilla'
        e['order']=order.get(e['module'].lower())
    for row in annotations:
        p=Path(row['path'])
        if p.is_relative_to(a.game):
            parts=p.relative_to(a.game).parts; row['owner']=parts[1] if parts[0].lower() in ('mods','dlc') else 'vanilla'
    owners=collections.defaultdict(list)
    for e in installed: owners[e['resource']].append(e)
    for container in sorted({e['container'] for e in resources if e['kind']=='bundle' and e['codec']==5}):
        subset=[e for e in resources if e['container']==container]
        dest=OUT/'payloads'/subset[0]['module']; dest.mkdir(parents=True,exist_ok=True)
        quick=a.game/'WitcherScriptMerger/Tools/QuickBMS'
        run=subprocess.run([str(quick/'quickbms.exe'),'-Q','-o',str(quick/'witcher3.bms'),container,str(dest)],capture_output=True,timeout=60)
        if run.returncode: raise ValueError('QuickBMS extraction failed: '+run.stdout.decode(errors='replace'))
    for e in resources:
        if e['kind']!='loose':
            with Path(e['container']).open('rb') as f:
                f.seek(e['offset']); b=f.read(e['packed'])
            e['stored_sha256']=hashlib.sha256(b).hexdigest()
            if e['kind']=='bundle':
                if e['codec']==0: raw=b
                elif e['codec']==1: raw=zlib.decompress(b)
                elif e['codec']==5: raw=(OUT/'payloads'/e['module']/e['resource']).read_bytes()
                else: raise ValueError('Unsupported resource codec')
                if raw is not None:
                    if len(raw)!=e['size']: raise ValueError('Invalid resource size')
                    e['sha256']=hashlib.sha256(raw).hexdigest()
                    dest=output_resource(e['module'],e['resource']); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(raw)
                    if e['resource'].endswith('.redswf'):
                        try:
                            off,sig,tags=audit.swf_tags(raw)
                            fonts=[audit.font_info(c,b) for c,b in tags if c in (48,75)]
                            strings=sorted(set(s.decode('utf-8',errors='replace') for c,b in tags for s in re.findall(rb'[\x20-\x7e]{4,}',b)))
                            e['movie']=dict(signature=sig,fonts=fonts,strings=strings)
                            dest.with_suffix('.gfx').write_bytes(raw[off:])
                        except Exception as ex: errors.append(dict(resource=e['resource'],error=str(ex)))
        matches=owners[e['resource']]
        if e['resource'].endswith('.w3strings'):
            si=string_index(Path(e['container'])); e['string_index']=si
            matches=[x for x in matches if set(si['ids']) & set(string_index(Path(x['container']))['ids']) or set(si['keys']) & set(string_index(Path(x['container']))['keys'])]
        e['owners']=[{k:v for k,v in x.items() if k in ('module','container','order','kind','sha256')} for x in matches]
        for x,o in zip(matches,e['owners']):
            if x['module']=='vanilla': continue
            if x['kind']=='loose': o['sha256']=digest(Path(x['container']))
            elif x['kind']=='texture':
                with Path(x['container']).open('rb') as f:
                    f.seek(x['offset']); o['stored_sha256']=hashlib.sha256(f.read(x['packed'])).hexdigest()
            else:
                data=shadows.read_resource(dict(x,bundle=x['container']),a.game,OUT/'live-read'/x['module'])
                o['sha256']=hashlib.sha256(data).hexdigest()
                if x['resource'].endswith('.redswf'):
                    dest=OUT/'live'; dest.mkdir(exist_ok=True)
                    (dest/(x['module']+'-'+Path(x['resource']).name)).write_bytes(data)
        mods=[x for x in e['owners'] if x['module']!='vanilla']
        e['classification']='overlap_requires_review' if mods else 'vanilla_replacement' if e['owners'] else 'no_detected_owner'
    overlaps=[]
    for row in annotations:
        if not Path(row['path']).is_relative_to(refs): continue
        hits=[x for x in annotations if Path(x['path']).is_relative_to(a.game) and x['owner']!='vanilla' and (x['class_name'],x['member'])==(row['class_name'],row['member'])]
        overlaps.append(dict(row,existing=hits))
    manifests=[]
    for p in (a.game/'Mods/vortex.deployment.json',a.game/'vortex.deployment.witcher3menumodroot.json',a.game/'vortex.deployment.witcher3tl.json'):
        if p.exists():
            data=json.loads(p.read_text(encoding='utf-8')); manifests.append(dict(path=str(p),sha256=digest(p),deploymentTime=data.get('deploymentTime'),stagingPath=data.get('stagingPath')))
    # Control hashes include all working compatibility scripts, not a rebuilt merge.
    controls=[dict(path=p.relative_to(a.game).as_posix(),sha256=digest(p)) for p in sorted((a.game/'Mods/mod0000_MergedFiles').rglob('*.ws'))]
    result=dict(reference_root=str(refs),game=str(a.game),mods_settings_sha256=digest(a.mods_settings),order=order,files=files,resources=resources,annotations=overlaps,all_annotations=annotations,errors=errors,deployment_manifests=manifests,controls=controls,archive=dict(path=str(a.vanilla_fonts_archive),sha256=digest(a.vanilla_fonts_archive)) if a.vanilla_fonts_archive else None,all_in_one_archive=dict(name=a.all_in_one_archive.name,sha256=digest(a.all_in_one_archive)) if a.all_in_one_archive else None,provenance=provenance)
    (OUT/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(files=len(files),resources=len(resources),modules=dict(collections.Counter(e['module'] for e in resources)),overlaps=dict(collections.Counter(e['module'] for e in resources if e['classification']=='overlap_requires_review')),annotation_overlaps=sum(bool(x['existing']) for x in overlaps),errors=errors),indent=2))

if __name__=='__main__': main()
