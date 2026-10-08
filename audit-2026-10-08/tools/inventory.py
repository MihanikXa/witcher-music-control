# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Read-only local Witcher audit. Writes evidence only below this audit directory."""
from pathlib import Path
import os,json,hashlib,struct,collections,configparser
ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3')
DOC=Path(r'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3')
STAGE=Path(os.environ['APPDATA'])/'Vortex/witcher3/mods'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(n,x):
 (ROOT/'evidence').mkdir(exist_ok=True)
 (ROOT/'evidence'/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def bundles(p):
 length=p.stat().st_size
 with p.open('rb') as f:
  hdr=f.read(32)
  if hdr[:8]!=b'POTATO70':raise ValueError('Unknown bundle magic: '+str(p))
  table=struct.unpack_from('<I',hdr,16)[0]
  f.seek(0x130); probe=struct.unpack('<I',f.read(4))[0]
  stride=0x130 if probe else 0x140
  if table%stride: raise ValueError('Invalid table length: '+str(p))
  f.seek(32)
  for i in range(table//stride):
   b=f.read(stride);name=b[:256].split(b'\0')[0].decode('utf-8')
   if stride==0x130:off,size,zsize,_,codec=struct.unpack_from('<QIIII',b,272)
   else:size,zsize,off=struct.unpack_from('<III',b,276);codec=struct.unpack_from('<I',b,316)[0]
   if off+zsize>length:raise ValueError('Invalid offset')
   yield dict(resource=name.lower().replace('\\','/'),size=size,compressed_size=zsize,offset=off,codec=codec,header_hash=b[256:272].hex(),bundle=str(p))
def main():
 manifests=[];ownership={}
 for p in GAME.rglob('vortex.deployment*.json'):
  d=json.loads(p.read_text(encoding='utf-8-sig'));d['manifest']=str(p);manifests.append(d)
  target=Path(d.get('targetPath',str(p.parent)))
  for e in d['files']:
   dest=target/e.get('target','')/e['relPath'];ownership[str(dest).lower()]=dict(e,manifest=str(p))
 save('deployment-manifests.json',manifests)
 settings=configparser.ConfigParser();settings.read(DOC/'mods.settings')
 save('mods-settings.json',{k:dict(settings[k]) for k in settings.sections()})
 allfiles=[];mods=[];entries=[];errors=[]
 for category in ['Mods','DLC']:
  for mod in sorted((GAME/category).iterdir()):
   if not mod.is_dir():continue
   rec=dict(name=mod.name,category=category,settings=dict(settings[mod.name]) if settings.has_section(mod.name) else {},files=0,bytes=0,owners=set(),unowned=0)
   for p in mod.rglob('*'):
    if not p.is_file():continue
    st=p.stat();own=ownership.get(str(p).lower());source=None;same=None
    if own:
     candidates=[STAGE/own['source']/own['relPath'],STAGE/own['source']/p.relative_to(GAME),STAGE/own['source']/p.name]
     source=next((x for x in candidates if x.is_file()),None)
     if source:same=os.path.samefile(p,source)
     rec['owners'].add(own['source'])
    else:rec['unowned']+=1
    item=dict(path=str(p),relative=str(p.relative_to(mod)).replace('\\','/'),mod=mod.name,category=category,size=st.st_size,mtime_ns=st.st_mtime_ns,inode=st.st_ino,managed=own,staged_source=str(source) if source else None,samefile=same)
    # Hash every loose file and bundle (streamed, no extraction).
    item['sha256']=sha(p);allfiles.append(item);rec['files']+=1;rec['bytes']+=st.st_size
    if p.suffix.lower()=='.bundle':
     try:entries.extend(dict(e,mod=mod.name,category=category) for e in bundles(p))
     except Exception as ex:errors.append(str(ex))
   rec['owners']=sorted(rec['owners']);mods.append(rec)
 save('installed-mods.json',mods);save('installed-files.json',allfiles);save('bundle-entries.json',entries);save('bundle-errors.json',errors)
 staging=[]
 for d in STAGE.iterdir():
  if not d.is_dir():continue
  files=list(p for p in d.rglob('*') if p.is_file())
  staging.append(dict(name=d.name,files=len(files),bytes=sum(p.stat().st_size for p in files),deployed=sum(1 for e in ownership.values() if e['source']==d.name),paths=[str(p.relative_to(d)) for p in files]))
 save('staging.json',staging)
 extra=[]
 for part in ['bin','initialdata','plugins','ArrowParryManual','dlc-tombstones']:
  for p in (GAME/part).rglob('*'):
   if p.is_file():extra.append(dict(path=str(p),size=p.stat().st_size,managed=ownership.get(str(p).lower()),sha256=sha(p)))
 for p in GAME.iterdir():
  if p.is_file():extra.append(dict(path=str(p),size=p.stat().st_size,managed=ownership.get(str(p).lower()),sha256=sha(p)))
 save('other-game-files.json',extra)
 print(json.dumps(dict(mods=len(mods),files=len(allfiles),bundle_entries=len(entries),bundle_errors=errors,staged=len(staging),other_files=len(extra))))
if __name__=='__main__':main()
