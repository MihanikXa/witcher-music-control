"""Read-only four-layer evidence; vendor exports stay under ignored reference/."""
import configparser,concurrent.futures,importlib.util,json,shutil,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
REF=ROOT/'reference/ink-and-iron-0.8.7';OUT=REF/'migration-evidence'
MODULES=('UI','Buttons','HUD','Fonts','MainMenu')
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
def export(job):
 label,key,data=job;folder=OUT/label/Path(key).stem;gfx=folder/'source.gfx'
 write(gfx,m.r.p.movie(data)[1])
 if not (folder/'scripts').exists():m.b.export(gfx,folder)
 return str(folder)
def main():
 OUT.mkdir(exist_ok=True);versions={};pins={}
 archive=next(Path('C:/Users/micha/Downloads').glob('*0.8.7*.zip'));dest=REF/'archives'/archive.name
 if not dest.exists():dest.parent.mkdir(exist_ok=True);shutil.copy2(archive,dest)
 if m.b.fallback.sha(dest)!='1dbc4884fb61418af69066f972eafab61be373ed28ed1ef05c06bb091b73a56b':raise ValueError('0.8.7 archive pin changed')
 checked=0
 with zipfile.ZipFile(dest) as z:
  for p in REF.rglob('*'):
   if p.is_file() and 'migration-evidence' not in p.parts and 'archives' not in p.parts:
    key=p.relative_to(REF).as_posix()
    if key not in z.namelist() or z.read(key)!=p.read_bytes():raise ValueError('Archive member differs '+key)
    checked+=1
 pins['archive']={'path':str(dest),'sha256':m.b.fallback.sha(dest),'verified_extracted_members':checked}
 for version in ('0.8','0.8.6','0.8.7'):
  base=ROOT/('reference/ink-and-iron-'+version);resources={};loose={}
  for mod in MODULES:
   for bundle in (base/'mods'/('modInkAndIron'+mod)).rglob('*.bundle'):
    for e in m.b.audit.entries(bundle):
     data=m.b.read_bundle(bundle,e,m.v.GAME,OUT)
     key=e['resource'];target=OUT/version/key;write(target,data)
     resources[key]={'module':mod,'sha256':m.b.audit.sha(data),'bytes':len(data),'path':str(target)}
   for p in (base/'mods'/('modInkAndIron'+mod)).rglob('*.ws'):loose[str(p.relative_to(base))]=m.b.fallback.sha(p)
  versions[version]={'resources':resources,'scripts':loose}
 cfg=configparser.ConfigParser();cfg.read_string(m.b.settings_text(m.v.SETTINGS));keys=set(versions['0.8.7']['resources'])
 owners=m.b.owners(m.v.GAME,cfg,keys,OUT);winners={}
 for key,rows in owners.items():
  enabled=[r for r in rows if r['enabled']=='1']
  if not enabled:continue
  row=min(enabled,key=lambda r:int(r['priority'] or 999999));container=Path(row['container'])
  data=m.b.read_bundle(container,next(e for e in m.b.audit.entries(container) if e['resource']==key),m.v.GAME,OUT) if container.suffix=='.bundle' else container.read_bytes()
  write(OUT/'installed'/key,data);winners[key]=row
 frozen=m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)
 ledger={'archive':pins,'versions':versions,'owners':owners,'winners':winners,'frozen':frozen,'settings_sha256':m.b.fallback.sha(m.v.SETTINGS)}
 m.b.write_json(OUT/'ledger.json',ledger)
 wanted={'panel_common','panel_overlay','panel_worldmap','panel_inventory','panel_ingamemenu','panel_alchemy','panel_crafting','panel_blacksmith','popup_item_selection','panel_transmog','hud_wolfstatbars','hud_journalupdate','hud_radialmenu','hud','panel_modmenu'}
 jobs=[]
 for version in ('0.8','0.8.7'):
  for key,row in versions[version]['resources'].items():
   if Path(key).stem in wanted and key.endswith('.redswf'):jobs.append((version+'-export',key,Path(row['path']).read_bytes()))
 for key,row in winners.items():
  if Path(key).stem in wanted and key.endswith('.redswf'):jobs.append(('installed-export',key,(OUT/'installed'/key).read_bytes()))
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for p in pool.map(export,jobs):print('Exported',p,flush=True)
 print('Pinned source and actual owners',len(keys),flush=True)
if __name__=='__main__':main()
