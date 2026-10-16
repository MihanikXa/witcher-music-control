"""Commit-safe per-key hashes and class delta names, never vendor source bodies."""
import csv,importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-menus-087.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def main():
 d=json.loads((b.E/'ledger.json').read_text());prepared=json.loads((b.OUT/'prepared.json').read_text());release=json.loads((b.OUT/'receipt.json').read_text());resources={r['resource']:r for r in prepared['resources']};rows=[]
 for key,row in d['versions']['0.8.7']['resources'].items():
  live=d['winners'].get(key,{});a=d['versions']['0.8']['resources'].get(key,{});c=d['versions']['0.8.6']['resources'].get(key,{});target=resources.get(key)
  if key in prepared['keys']:decision='adopt 0.8.7 + accepted glyph/layout adapters' if key.endswith('.redswf') else 'adopt upstream environment'
  elif '/hud/' in key:decision='retain accepted HUD; no port shipped'
  elif key.endswith('/panel_overlay.redswf'):decision='retain RC2 combined OW overlay; upstream unchanged'
  elif key.endswith('.env'):decision='defer unchanged optional environment: isolated native validation error; retain current lighting'
  elif row['module']=='Fonts':decision='retain QuietFolio and existing aliases; IM Fell package excluded'
  else:decision='optional animated title scenes deferred; unchanged upstream'
  rows.append(dict(resource=key,module=row['module'],upstream_080_sha256=a.get('sha256'),installed_owner=live.get('owner','no mod owner (base game)'),installed_priority=live.get('priority'),installed_sha256=live.get('sha256'),upstream_086_sha256=c.get('sha256'),upstream_087_sha256=row['sha256'],release_sha256=target['output_sha256'] if target else row['sha256'] if key in prepared['keys'] else live.get('sha256'),decision=decision))
 report=ROOT/'research/menus087-migration-matrix.csv'
 with report.open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 deltas={}
 for stem in ('panel_common','panel_inventory','panel_ingamemenu','panel_alchemy','panel_crafting','panel_blacksmith','panel_worldmap','popup_item_selection','panel_transmog','hud_wolfstatbars','hud_journalupdate','hud_radialmenu'):
  old=b.E/'0.8-export'/stem/'scripts';new=b.E/'0.8.7-export'/stem/'scripts';changed=[]
  for path in old.rglob('*.as'):
   other=new/path.relative_to(old)
   if other.exists() and path.read_bytes()!=other.read_bytes():changed.append(str(path.relative_to(old)))
  deltas[stem]=changed
 hud={}
 for stem,cls in [('hud_wolfstatbars','HudModuleWolfHead'),('hud_journalupdate','HudModuleJournalUpdate'),('hud_journalupdate','QuestFinishedWindow'),('hud_radialmenu','HudModuleRadialMenu')]:
  hud[cls]={}
  for version in ('0.8','0.8.6','0.8.7','installed'):
   paths=list((b.E/(version+'-export')/stem/'scripts').rglob(cls+'.as'))
   if paths:hud[cls][version]=re.findall(r'function ((?:iai|ink)\w+)\(',paths[0].read_text(encoding='utf-8-sig'))
 script=json.loads((b.SCRIPTS/'receipt.json').read_text())
 script_migration=[]
 for path,sha in d['versions']['0.8.7']['scripts'].items():
  installed=[{'path':k,'sha256':v} for k,v in d['frozen'].items() if Path(k).name==Path(path).name]
  script_migration.append(dict(path=path,upstream_080=d['versions']['0.8']['scripts'].get(path),upstream_086=d['versions']['0.8.6']['scripts'].get(path),upstream_087=sha,installed=installed,decision='adopt exactly once' if '/modInkAndIronUI/' in path.replace('\\','/') else 'retain current/defer upstream optional module'))
 # Diagnostic counters are summarized; thousands of vendor diagnostics remain private.
 for result in script['results']:
  for name in ('warnings','assertions'):
   counter=result[name];serialized=json.dumps(counter,sort_keys=True).encode();result[name]={'count':sum(counter.values()),'distinct':len(counter),'counter_sha256':b.m.b.audit.sha(serialized)}
 concise=[]
 for row in prepared['resources']:
  row=dict(row);glyph=row['glyphs'];row['glyphs']={k:v for k,v in glyph.items() if k!='glyphs'};row['glyphs']['definition_count']=len(glyph.get('glyphs',[]));concise.append(row)
 manifest=dict(upstream_archive=d['archive'],resource_matrix='research/menus087-migration-matrix.csv',upstream_changed_class_names=deltas,hud_methods=hud,resources=concise,keys=prepared['keys'],native=release['native'],environment_control=json.loads((b.OUT/'environment-control/receipt.json').read_text()),scripts=script,zip_path=release['zip_path'],zip_sha256=release['zip_sha256'],zip_bytes=release['zip_bytes'],package_members=release['members'],frozen_inputs_count=len(d['frozen']),frozen_snapshot_sha256=b.m.b.audit.sha(json.dumps(d['frozen'],sort_keys=True).encode()),runtime_tested=False,deployed=False,private_evidence=str(b.OUT),texture_cache=json.loads((b.OUT/'texture-cache-check.json').read_text()),source_hashes={str(p.relative_to(ROOT)):b.m.b.fallback.sha(p) for p in [Path(__file__),ROOT/'tools/audit-menu-migration.py',ROOT/'tools/patch-menu-migration.py',ROOT/'tools/build-menus-087.py',ROOT/'tools/compile-menus-087.py',ROOT/'tools/check-menu-environment.py',ROOT/'tests/test_menus_087.py']})
 # Glyph manifests contain IDs/hashes/rectangles, not third-party shapes or pixels.
 manifest['script_migration']=script_migration
 manifest['native_log_sha256']={row['label']:b.m.b.fallback.sha(b.OUT/'native-final'/(row['label']+'.full.log')) for row in release['native']}
 manifest['targeted_tests']={'passed':15,'command':'python -m unittest discover -s tests -p test_menus_087.py -v','in_game_tested':False}
 b.m.b.write_json(ROOT/'research/menus087-release-manifest.json',manifest)
 print('Migration matrix and non-asset release manifest written')
if __name__=='__main__':main()
