# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
from inventory import *
import subprocess
def main():
 entries=json.loads((ROOT/'evidence/vanilla-collision-baselines.json').read_text())
 mods=json.loads((ROOT/'evidence/bundle-entries.json').read_text())
 entries.extend(x for x in mods if x['mod']=='modOver9000')
 groups=collections.defaultdict(list)
 for x in entries:groups[(x.get('mod','vanilla'),x['bundle'])].append(x)
 results=[];tool=GAME/'WitcherScriptMerger/Tools/QuickBMS'
 for (owner,bundle),rs in groups.items():
  out=ROOT/'private/baselines'/owner;out.mkdir(parents=True,exist_ok=True)
  filt=ROOT/'evidence'/('baseline-filter-'+owner+'-'+Path(bundle).stem+'.txt');filt.write_text('\n'.join(x['resource'].replace('/','\\') for x in rs))
  p=subprocess.run([str(tool/'quickbms.exe'),'-Q','-o','-f',str(filt),str(tool/'witcher3.bms'),bundle,str(out)],capture_output=True)
  (ROOT/'evidence'/('baseline-extract-'+owner+'-'+Path(bundle).stem+'.log')).write_bytes(p.stdout+p.stderr)
  for x in rs:
   path=out/x['resource'];results.append(dict(owner=owner,resource=x['resource'],exit=p.returncode,path=str(path),sha256=sha(path) if path.is_file() else None))
 save('baseline-extraction.json',results);print('Extracted baselines:',len(results),'failed:',sum(not r['sha256'] for r in results))
if __name__=='__main__':main()
