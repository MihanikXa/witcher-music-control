# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Use existing QuickBMS to extract only colliding resources to private audit storage."""
from inventory import *
import subprocess
def main():
 c=json.loads((ROOT/'evidence/bundled-collisions.json').read_text())
 grouped=collections.defaultdict(list)
 for path,records in c.items():
  for r in records:grouped[(r['mod'],r['bundle'])].append(path)
 results=[]
 for (mod,bundle),resources in grouped.items():
  out=ROOT/'private/resources'/mod;out.mkdir(parents=True,exist_ok=True)
  filt=ROOT/'evidence'/('filter-'+mod+'.txt');filt.write_text('\n'.join(x.replace('/','\\') for x in resources))
  tool=GAME/'WitcherScriptMerger/Tools/QuickBMS'
  cmd=[str(tool/'quickbms.exe'),'-Q','-o','-f',str(filt),str(tool/'witcher3.bms'),bundle,str(out)]
  proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (ROOT/'evidence'/('quickbms-'+mod+'.log')).write_bytes(proc.stdout)
  results.append(dict(mod=mod,bundle=bundle,exit=proc.returncode))
  for resource in resources:
   p=out/resource
   if p.exists():
    for r in c[resource]:
     if r['mod']==mod and r['bundle']==bundle:r.update(sha256=sha(p),extracted=str(p),extracted_size=p.stat().st_size)
 save('bundled-collisions.json',c);save('extraction-results.json',results)
 print(json.dumps(results))
if __name__=='__main__':main()
