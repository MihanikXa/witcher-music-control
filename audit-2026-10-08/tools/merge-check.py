# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Check installed merges against current vanilla and sources; never change live scripts."""
from inventory import *
import subprocess,difflib
def main():
 c=json.loads((ROOT/'evidence/loose-collisions.json').read_text());results=[]
 out=ROOT/'private/merge-check';out.mkdir(parents=True,exist_ok=True)
 for resource,records in c.items():
  merged=next((r for r in records if r['mod']=='mod0000_MergedFiles'),None)
  if not merged:continue
  base=GAME/'content/content0'/resource.removeprefix('content/')
  current=Path(merged['path']).read_text(encoding='utf-8-sig');a=out/'current.ws';b=out/'base.ws';s=out/'source.ws'
  a.write_text(current,encoding='utf-8',newline='\n');b.write_text(base.read_text(encoding='utf-8-sig'),encoding='utf-8',newline='\n')
  for r in records:
   if r==merged:continue
   s.write_text(Path(r['path']).read_text(encoding='utf-8-sig'),encoding='utf-8',newline='\n')
   p=subprocess.run(['git','merge-file','-p',str(a),str(b),str(s)],capture_output=True)
   delta=p.stdout.decode('utf-8');target=out/(Path(resource).stem+'-'+r['mod']+'.candidate.ws');target.write_bytes(p.stdout)
   result=dict(resource=resource,mod=r['mod'],exit=p.returncode,already_incorporated=p.returncode==0 and delta==current,candidate=str(target),baseline_sha256=sha(base),current_sha256=merged['sha256'],source_sha256=r['sha256'])
   results.append(result)
   if p.returncode==0 and delta!=current:
    (target.with_suffix('.diff')).write_text(''.join(difflib.unified_diff(current.splitlines(True),delta.splitlines(True))),encoding='utf-8')
 save('merge-source-check.json',results);print(json.dumps([{k:v for k,v in x.items() if k in ['resource','mod','exit','already_incorporated']} for x in results],indent=2))
if __name__=='__main__':main()
