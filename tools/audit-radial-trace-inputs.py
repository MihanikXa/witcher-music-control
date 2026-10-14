"""Read-only deployed RC1 snapshot; extraction only into ignored build/."""
import importlib.util,configparser,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'build/ink-radial-trace-work');a=ap.parse_args()
out=a.out.resolve();m.b.font.private_path(out);out.mkdir();parent=json.loads((m.ROOT/'build/ink-hud-v4-hotfix-rc1-final/receipt.json').read_text());cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(m.b.settings_text(m.v.SETTINGS));owners=m.b.owners(m.v.GAME,cfg,set(parent['resource_hashes']),out);m.b.write_json(out/'owners.json',owners);m.b.write_json(out/'live-before.json',m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS))
for k,h in parent['resource_hashes'].items():
 active=sorted([r for r in owners[k] if r.get('enabled')=='1'],key=lambda r:int(r.get('priority') or 9999));winner=active[0];print(Path(k).stem,winner['owner'],winner['priority'],winner['sha256']==h)
 if winner['sha256']!=h:raise ValueError('Installed RC1 mismatch')
 d=m.b.read_bundle(Path(winner['container']),next(e for e in m.b.audit.entries(Path(winner['container'])) if e['resource']==k),m.v.GAME,out);p=out/'inputs'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
 for stem in ['hud','hud_radialmenu','hud_iteminfo','panel_common','panel_overlay']:
  if Path(k).stem==stem:
   e=out/'exports'/stem;e.mkdir(parents=True);g=e/'source.gfx';g.write_bytes(m.r.p.movie(d)[1]);m.b.export(g,e)
