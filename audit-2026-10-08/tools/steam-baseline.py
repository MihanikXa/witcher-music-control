# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Read cached installed Steam depot manifests, verify local files without repair/download.
Wire fields follow SteamKit2 DepotManifest and Steam's ContentManifestPayload.
"""
from inventory import *
import re,time
STEAM=GAME.parents[2]
def varint(b,p):
 v=0;s=0
 while True:
  x=b[p];p+=1;v|=(x&127)<<s;s+=7
  if not x&128:return v,p
def protobuf(b):
 out=collections.defaultdict(list);p=0
 while p<len(b):
  tag,p=varint(b,p);n,w=tag>>3,tag&7
  if w==0:x,p=varint(b,p)
  elif w==2:
   size,p=varint(b,p);x=b[p:p+size];p+=size
  elif w==5:x=b[p:p+4];p+=4
  elif w==1:x=b[p:p+8];p+=8
  else:raise ValueError('Unknown protobuf wire type')
  out[n].append(x)
 return out
def manifest(p):
 b=p.read_bytes();magic,length=struct.unpack_from('<II',b)
 if magic!=0x71F617D0:raise ValueError('Not a Steam content manifest')
 payload=protobuf(b[8:8+length]);out=[]
 for raw in payload[1]:
  x=protobuf(raw);name=x[1][0].decode('utf-8');size=x.get(2,[0])[0];flags=x.get(3,[0])[0];h=x.get(5,[b''])[0].hex()
  out.append(dict(relative=name.replace('\\','/'),size=size,flags=flags,sha1=h))
 return out
def sha1(p):
 h=hashlib.sha1()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 app=(STEAM/'steamapps/appmanifest_292030.acf').read_text();pairs=re.findall(r'"(\d+)"\s*\{\s*"manifest"\s*"(\d+)"',app)
 known={};missing=[];errors=[]
 for depot,gid in pairs:
  p=STEAM/'depotcache'/(depot+'_'+gid+'.manifest')
  if not p.exists():missing.append(str(p));continue
  try:
   for x in manifest(p):known[x['relative'].lower()]=dict(x,depot=depot,manifest=gid)
  except Exception as ex:errors.append(dict(manifest=str(p),error=str(ex)))
 save('steam-manifest-files.json',list(known.values()));save('steam-manifest-limitations.json',dict(missing=missing,errors=errors))
 results=[];nbytes=0;start=time.time()
 print('Manifest files',len(known),'missing manifests',len(missing),flush=True)
 for i,(rel,x) in enumerate(known.items()):
  if x['flags']&64:continue
  p=GAME/x['relative'];result=dict(x,path=str(p))
  if not p.exists():result['status']='missing'
  elif p.stat().st_size!=x['size']:result['status']='different-size';result['actual_size']=p.stat().st_size
  elif x['size']==0 and x['sha1']=='0'*40:result['status']='matches-empty-no-content-hash'
  else:
   actual=sha1(p);nbytes+=p.stat().st_size;result['actual_sha1']=actual;result['status']='matches' if actual==x['sha1'] else 'different-hash'
  results.append(result)
  if i%100==0:
   save('steam-verification-progress.json',dict(checked=len(results),bytes=nbytes,seconds=round(time.time()-start)))
 save('steam-verification.json',results)
 print(json.dumps(dict(files=len(results),bytes_hashed=nbytes,statuses=dict(collections.Counter(x['status'] for x in results)),seconds=round(time.time()-start))),flush=True)
 print('Differences:',[(x['relative'],x['status']) for x in results if x['status']!='matches'],flush=True)
if __name__=='__main__':main()
