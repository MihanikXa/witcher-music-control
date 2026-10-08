"""Inspect pinned Gwent inputs and extract two scene collisions privately; never deploy."""
import argparse,json,re,subprocess,sys
from pathlib import Path
from importlib.machinery import SourceFileLoader
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))
from inventory import bundles,sha
loc=SourceFileLoader('gwent_loc',str(Path(__file__).with_name('localization-audit.py'))).load_module()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);game=ap.parse_args().game.resolve()
 rows=json.loads((ROOT/'evidence/current-gwent-layout.json').read_text(encoding='utf-8'))
 for row in rows:assert sha(Path(row['path']))==row['sha256'],row['relative']
 mod=game/'Gwent Deck Choice - Vanilla Gwent/mods/mod_GwentDeckChoice'
 tables=list(bundles(mod/'content/blob0.bundle'))
 scripts=list(mod.rglob('*.ws'));alltext='\n'.join(p.read_text(encoding='utf-8-sig') for p in scripts)
 csv=set(re.findall(r'LoadCSV\(\s*"([^"]+)"',alltext))
 available={x['resource'].lower() for x in tables}
 fallbacks={'gameplay\\globals\\card_sources.csv','qa\\card_sources.csv'}
 assert all(x.replace('\\','/').lower() in available for x in csv-fallbacks),csv
 # Compare signatures as types/parameters, disregarding visibility and annotations.
 hooks=['OnGwintSetupSkellige','FindCardSources','HasCardInCollection','OpenBetPopup','AddItemQuest','UnlockSkelligeGwentDeck','GiveSpecificGwentCardViaMerchantQuest','GiveMerchantRandomGwintCardToPlayerQuest']
 native='\n'.join(p.read_text(encoding='utf-8-sig') for p in (game/'content/content0/scripts').rglob('*.ws'))
 signatures={}
 for name in hooks:
  pattern=r'\b(?:function|event)\s+'+name+r'\s*(\([^)]*\)(?:\s*:\s*[\w<> ]+)?\s*)(?=[;{])'
  def signature(t):
   matches=re.findall(pattern,t);assert len(matches)==1,(name,len(matches))
   return re.sub(r'\s+','',matches[0])
  assert signature(native)==signature(alltext),name
  signatures[name]=signature(native)
 indexed=json.loads((ROOT/'evidence/localization-index.json').read_text(encoding='utf-8'));strings=[]
 for p in mod.rglob('*.w3strings'):
  item=loc.index(p)
  for old in indexed:
   if old['language']==p.stem:
    assert not set(item['ids'])&set(old['ids']),('Gwent ID collision',p.stem,old['mod'])
    assert set(item['keys'])&set(old['keys']) <= {str(0x4d5f8b0c)},('Gwent key collision',p.stem,old['mod'])
  strings.append(dict(language=p.stem,count=item['count']))
 collisions=json.loads((ROOT/'evidence/gwent-new-collisions.json').read_text(encoding='utf-8'))
 bia=json.loads((ROOT/'evidence/bundle-entries.json').read_text(encoding='utf-8'))
 results=[];tool=game/'WitcherScriptMerger/Tools/QuickBMS'
 resources=[x for x in collisions if x['resource']!='strings.list']
 for owner in ['mod_GwentDeckChoice','modbrothersinarms']:
  entries=resources if owner=='mod_GwentDeckChoice' else [next(x for x in bia if x['mod']==owner and x['resource']==r['resource']) for r in resources]
  groups={}
  for x in entries:groups.setdefault(x['bundle'],[]).append(x)
  for bundle,entries in groups.items():
   out=ROOT/'private/gwent-scenes'/owner;out.mkdir(parents=True,exist_ok=True)
   filt=ROOT/'private/gwent-scenes'/(owner+'.txt');filt.write_text('\n'.join(x['resource'].replace('/','\\') for x in entries),encoding='utf-8')
   proc=subprocess.run([str(tool/'quickbms.exe'),'-Q','-o','-f',str(filt),str(tool/'witcher3.bms'),bundle,str(out)],capture_output=True)
   assert proc.returncode==0,proc.stdout.decode(errors='replace')
   for row in entries:
    p=out/row['resource'];assert p.stat().st_size==row['size']
    raw=p.read_bytes();assert raw[:4]==b'CR2W'
    results.append(dict(resource=row['resource'],mod=owner,bundle=bundle,extracted=str(p),extracted_size=len(raw),sha256=sha(p),format_version=int.from_bytes(raw[4:8],'little')))
 info=json.loads((mod/'content/info.json').read_text(encoding='utf-8'))
 report=dict(source_hashes_checked=len(rows),mod_files=len([p for p in mod.rglob('*') if p.is_file()]),csv_dependencies=sorted(csv),signatures=signatures,localization=strings,scenes=results,info=info,engine_compile=False,runtime_test=False)
 (ROOT/'evidence/gwent-integration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in ['scenes','info']}))
if __name__=='__main__':main()
