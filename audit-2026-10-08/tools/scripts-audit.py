# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
from inventory import *
import re,difflib
def clean(t):
 return re.sub(r'//[^\n]*|/\*.*?\*/',lambda m:'\n'*m[0].count('\n'),t,flags=re.S)
def main():
 files=json.loads((ROOT/'evidence/installed-files.json').read_text());ann=[];decl=[]
 for item in files:
  if not item['relative'].lower().endswith('.ws'):continue
  text=Path(item['path']).read_text(encoding='utf-8-sig',errors='replace');t=clean(text)
  for m in re.finditer(r'@(wrapMethod|replaceMethod|addMethod|addField)\s*\(\s*([\w]+)\s*\)\s*(?:@[\w]+\([^)]*\)\s*)*(?:[\w]+\s+)*(function|event|var|autobind)\s+(\w+)',t):
   tail=t[m.end():];op=m[1];end=tail.find('{')
   record=dict(mod=item['mod'],path=item['path'],line=t[:m.start()].count('\n')+1,op=op,cls=m[2],member=m[4],signature=tail[:end].strip() if m[3] in ['function','event'] else tail.split(';')[0].strip())
   record['calls_wrapped']=bool(re.search(r'\bwrappedMethod\s*\(',tail[:tail.find('\n}')+2] if '\n}' in tail else tail))
   ann.append(record)
  for m in re.finditer(r'^\s*(?:public\s+|private\s+|protected\s+|static\s+|saved\s+|final\s+|latent\s+|exec\s+)*(class|struct|enum|function)\s+(\w+)',t,re.M):
   # Global type names are candidates; functions require scope review.
   decl.append(dict(mod=item['mod'],path=item['path'],line=t[:m.start()].count('\n')+1,kind=m[1],name=m[2]))
 g=collections.defaultdict(list)
 for a in ann:g[a['cls']+'.'+a['member']].append(a)
 collisions={k:v for k,v in g.items() if len(set(x['mod'] for x in v))>1}
 save('annotations.json',ann);save('annotation-collisions.json',collisions)
 d=collections.defaultdict(list)
 for x in decl:
  if x['kind'] in ['class','struct','enum']:d[x['kind']+' '+x['name']].append(x)
 save('duplicate-types.json',{k:v for k,v in d.items() if len(set(x['mod'] for x in v))>1})
 loose=json.loads((ROOT/'evidence/loose-collisions.json').read_text());out=ROOT/'private/diffs';out.mkdir(parents=True,exist_ok=True)
 for rel,rs in loose.items():
  if not rel.endswith('.ws'):continue
  vanilla=GAME/'content/content0'/rel.removeprefix('content/')
  if not vanilla.is_file():continue
  base=vanilla.read_text(encoding='utf-8-sig',errors='replace').splitlines(True)
  for r in rs:
   t=Path(r['path']).read_text(encoding='utf-8-sig',errors='replace').splitlines(True)
   delta=''.join(difflib.unified_diff(base,t,fromfile=str(vanilla),tofile=r['path']))
   (out/(Path(rel).stem+'-'+r['mod']+'.diff')).write_text(delta,encoding='utf-8')
 print('Annotations',len(ann),'cross-mod methods',len(collisions))
 print('\n'.join(k+' '+str([(x['mod'],x['op'],x['line']) for x in v]) for k,v in collisions.items()))
if __name__=='__main__':main()
