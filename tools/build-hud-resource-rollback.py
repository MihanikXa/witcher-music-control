"""Build a coherent private resource rollback; never stack annotation packages.
Both releases must have verified local receipts and exact ZIP/input hashes.
"""
import argparse,json,subprocess,sys
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
GROUPS={'enemy':{'hud_enemyfocus'},'quickslots':{'hud_iteminfo'},'buttons':{'hud','panel_common','panel_overlay','hud_controlsfeedback','hud_dialog','hud_interactions','hud_iteminfo','hud_journalupdate','hud_radialmenu'}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--restore',type=Path,required=True);ap.add_argument('--group',choices=GROUPS,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();m.b.font.private_path(out)
 if out.exists() or a.deploy.exists():raise ValueError('Fresh destinations required')
 manifests=[]
 for folder in (a.base.resolve(),a.restore.resolve()):
  m.b.font.private_path(folder);receipt=json.loads((folder/'receipt.json').read_text())
  if m.b.fallback.sha(Path(receipt['zip_path']))!=receipt['zip_sha256']:raise ValueError('Parent archive changed')
  for k,h in receipt['resource_hashes'].items():
   if m.b.fallback.sha(folder/'pack-input'/k)!=h:raise ValueError('Pinned rollback input changed')
  manifests.append(receipt)
 base,old=manifests
 if set(base['resource_hashes'])!=set(old['resource_hashes']):raise ValueError('Same resource set required')
 state=m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)
 out.mkdir();files={};restored=[]
 for k in base['resource_hashes']:
  restore=Path(k).stem in GROUPS[a.group];folder=a.restore if restore else a.base
  data=(folder/'pack-input'/k).read_bytes();files[k]=data
  p=out/'prepared-inputs'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  if restore:restored.append(k)
 m.b.write_json(out/'live-before.json',state)
 m.b.write_json(out/'prepared-contracts.json',dict(changes=dict(component_rollback=a.group,restored_keys=restored,base_zip_sha256=base['zip_sha256'],restore_zip_sha256=old['zip_sha256']),movie_contracts={},unchanged_keys=[]))
 commands=[];runner=ROOT/'build/ink-hud-v3-native-runner';native={k:d for k,d in files.items() if k.endswith('.redswf')}
 with m.b.mount(runner,out,native) as workspace:
  m.b.official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
  log=m.b.official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
  if 'Found 22 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Native validation gate')
 for k,d in native.items():
  if (out/'cooked'/k).read_bytes()!=d:raise ValueError('Cook altered rollback input')
  m.v.atlas_contract(d);p=out/'native-pack-input'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
 with m.b.mount(runner,out,{}) as workspace:
  m.b.official(runner,out,'pack',['pack','-dir='+str(out/'native-pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
  try:m.b.official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
  except (ValueError,subprocess.TimeoutExpired):pass
 m.b.write_json(out/'commands.json',commands)
 subprocess.run([sys.executable,str(ROOT/'tools/build-ink-hud-v4.py'),'--out',str(out),'--deploy',str(a.deploy),'--finish'],check=True)
 if m.b.bars.snapshot(m.v.GAME,m.v.SETTINGS)!=state:raise ValueError('Live inputs changed')
if __name__=='__main__':main()
