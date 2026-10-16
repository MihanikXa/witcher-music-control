"""Pin official 0.8.6 UI and 0.8.4 Hoods archive members under ignored reference/."""
import argparse,importlib.util,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
REF=ROOT/'reference/ink-and-iron-0.8.6';KEY='gameplay/gui_new/swf/inventory/panel_inventory.redswf'
PINS={'ui':('Ink and Iron - All in One 13111 0.8.6 2026-10-15T18-45Z z2QRfnz9T.zip','2beb77716b6b5b5e8acf7d2c5ea65ba950ed9726d0c0e0cb5e40e1ce407d6e00'),'hoods':('Ink and Iron - Hoods Compatibility 13111 0.8.4 2026-10-13T15-59Z mlFpu6vCy.zip','617f6d37d94158d751b3a3e6c3c0c5308e567f65ec74e007a967108d1a56802c')}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--downloads',type=Path,default=Path('C:/Users/micha/Downloads'));a=ap.parse_args();evidence=REF/'inventory-source';evidence.mkdir(exist_ok=True);records={}
 for label,(filename,expected) in PINS.items():
  archive=REF/'archives'/filename;source=a.downloads/filename
  if not archive.exists():
   if m.b.fallback.sha(source)!=expected:raise ValueError('Archive pin mismatch')
   archive.parent.mkdir(exist_ok=True);shutil.copy2(source,archive)
  if m.b.fallback.sha(archive)!=expected:raise ValueError('Pinned reference archive changed')
  destination=REF if label=='ui' else REF/'hoods-compat';members={}
  with zipfile.ZipFile(archive) as z:
   for name in z.namelist():
    key=name.replace('\\','/')
    if name.endswith('/') or label=='ui' and not key.startswith('mods/modInkAndIronUI/'):continue
    path=(destination/key).resolve()
    if not path.is_relative_to(REF.resolve()):raise ValueError('Unsafe archive member')
    data=z.read(name);members[key]=m.b.audit.sha(data)
    if path.exists():
     if path.read_bytes()!=data:raise ValueError('Extraction differs '+str(path))
    else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
  bundle=next(destination.rglob('modInkAndIronUI/content/blob0.bundle')) if label=='ui' else destination/'mods/mod0InkAndIron_HoodsCompat/content/blob0.bundle'
  entries=list(m.b.audit.entries(bundle));entry=next(e for e in entries if e['resource']==KEY);data=m.b.read_bundle(bundle,entry,m.v.GAME,evidence)
  resource=evidence/label/KEY;resource.parent.mkdir(parents=True,exist_ok=True)
  if resource.exists() and resource.read_bytes()!=data:raise ValueError('Inventory cache differs')
  resource.write_bytes(data);export=evidence/(label+'-export');export.mkdir(exist_ok=True);gfx=export/'inventory.gfx';movie=m.r.p.movie(data)[1]
  if gfx.exists() and gfx.read_bytes()!=movie:raise ValueError('GFx source differs')
  gfx.write_bytes(movie)
  if not (export/'scripts').exists():m.b.export(gfx,export)
  records[label]=dict(archive_path=str(archive),archive_sha256=expected,archive_members=members,bundle_resources=[e['resource'] for e in entries],inventory_sha256=m.b.audit.sha(data),inventory_bytes=len(data),published_version='0.8.6' if label=='ui' else '0.8.4',source_url='https://www.nexusmods.com/witcher3/mods/13111?tab=files')
 # Preserve the actual working 5.01 Hoods interface as the native contract control.
 baseline=m.v.GAME/'Mods/modHoods/content/blob0.bundle';entry=next(e for e in m.b.audit.entries(baseline) if e['resource']==KEY)
 raw=m.b.read_bundle(baseline,entry,m.v.GAME,evidence);export=evidence/'installed-hoods-export';export.mkdir(exist_ok=True);gfx=export/'inventory.gfx';movie=m.r.p.movie(raw)[1]
 if gfx.exists() and gfx.read_bytes()!=movie:raise ValueError('Installed Hoods baseline changed')
 gfx.write_bytes(movie)
 if not (export/'scripts').exists():m.b.export(gfx,export)
 records['installed_hoods_baseline']=dict(bundle=str(baseline),inventory_sha256=m.b.audit.sha(raw))
 m.b.write_json(evidence/'source-manifest.json',records);print('Pinned 0.8.6 UI and official 0.8.4 Hoods inputs; no live changes')
if __name__=='__main__':main()
