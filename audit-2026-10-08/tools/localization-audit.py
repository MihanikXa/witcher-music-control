# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Inspect localization index IDs and key hashes, without decrypting or rewriting strings."""
from inventory import *
def bit6(d,p):
 b=d[p];p+=1;v=b&63
 if b&64:
  shift=6
  while True:
   b=d[p];p+=1;v|=(b&127)<<shift;shift+=7
   if not b&128:break
 return v,p
def index(p):
 d=p.read_bytes()
 if d[:4]!=b'RTSW':raise ValueError('Bad magic')
 version,key1=struct.unpack_from('<IH',d,4);n,pos=bit6(d,10)
 ids=[struct.unpack_from('<III',d,pos+12*i) for i in range(n)];pos+=n*12
 m,pos=bit6(d,pos);keys=[struct.unpack_from('<II',d,pos+8*i) for i in range(m)];pos+=m*8
 count,pos=bit6(d,pos)
 # 162/163 UTF16 character counts; 164 UTF8 byte counts.
 unit=next((u for u in (1,2) if pos+count*u+2==len(d)),None)
 if unit is None:raise ValueError('Unrecognized string block length')
 key2=struct.unpack_from('<H',d,pos+count*unit)[0]
 return dict(version=version,key1=key1,key2=key2,ids={str(i):hashlib.sha256(d[pos+off*unit:pos+(off+ln)*unit]).hexdigest() for i,off,ln in ids},keys={str(k):i for k,i in keys},count=n)
def main():
 files=json.loads((ROOT/'evidence/installed-files.json').read_text());rs=[];errors=[]
 for f in files:
  if not f['path'].lower().endswith('.w3strings'):continue
  try:rs.append(dict(mod=f['mod'],language=Path(f['path']).stem.lower(),path=f['path'],**index(Path(f['path']))))
  except Exception as e:errors.append(dict(path=f['path'],error=str(e)))
 collisions=[]
 for language in sorted(set(x['language'] for x in rs)):
  byid=collections.defaultdict(list);bykey=collections.defaultdict(list)
  for r in rs:
   if r['language']!=language:continue
   for sid,h in r['ids'].items():byid[sid].append(dict(mod=r['mod'],hash=h,version=r['version']))
   for key,sid in r['keys'].items():bykey[key].append(dict(mod=r['mod'],id=sid))
  for kind,groups in [('id',byid),('key',bykey)]:
   for key,values in groups.items():
    if len(set(v['mod'] for v in values))>1:collisions.append(dict(language=language,kind=kind,key=key,values=values))
 save('localization-index.json',rs);save('localization-collisions.json',collisions);save('localization-errors.json',errors)
 print(json.dumps(dict(files=len(rs),errors=errors,collisions=len(collisions),groups=dict(collections.Counter((c['kind'] for c in collisions))),examples=collisions[:1]),indent=2))
if __name__=='__main__':main()
