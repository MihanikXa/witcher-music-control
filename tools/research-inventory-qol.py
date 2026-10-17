"""Read supplied archives and installed Inventory dependencies; write evidence only."""
import configparser, hashlib, importlib.util, json, re, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('menus',ROOT/'tools/build-menus-087.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
OUT=ROOT/'build/adaptive-inventory-v2-p1'
def sha(data):return hashlib.sha256(data).hexdigest()
def annotations(text):
    return [dict(kind=k,owner=c,method=m) for k,c,m in re.findall(r'@(wrapMethod|replaceMethod|addMethod|addField)\s*\(\s*(\w+)\s*\)\s*(?:(?:private|public|protected|saved)\s+)*(?:function|event|var)\s+(\w+)',text)]
def main():
    rows=[]
    for archive in sorted((ROOT/'reference/inventory-qol').rglob('*.zip')):
        mod=archive.parent.parent.name;dest=OUT/'qol'/mod;dest.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                target=(dest/name).resolve()
                if dest.resolve() not in target.parents:raise ValueError('Unsafe archive path')
            z.extractall(dest)
            scripts={n:dict(sha256=sha(z.read(n)),annotations=annotations(z.read(n).decode('utf-8-sig'))) for n in z.namelist() if n.endswith('.ws')}
            bundles={str(p.relative_to(dest)):[e['resource'] for e in b.m.b.audit.entries(p)] for p in dest.rglob('*.bundle')}
            infos={n:json.loads(z.read(n)) for n in z.namelist() if n.endswith('info.json')}
            rows.append(dict(archive=str(archive.relative_to(ROOT)),sha256=sha(archive.read_bytes()),members={n:sha(z.read(n)) for n in z.namelist() if not n.endswith('/')},scripts=scripts,bundle_keys=bundles,metadata=infos))
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.m.b.settings_text(b.m.v.SETTINGS))
    installed={}
    for mod in ('modFriendlyHUD','modAutoLoot','modHoods','modInkIronMenus087','modInkIronHUDRefinementV4','modsmoothmap'):
        folder=b.m.v.GAME/'Mods'/mod
        installed[mod]=dict(settings=dict(cfg[mod]) if mod in cfg else {},scripts={str(p.relative_to(folder)):sha(p.read_bytes()) for p in folder.rglob('*.ws')})
    user=b.m.v.SETTINGS.parent/'dx12user.settings';settings=configparser.ConfigParser(interpolation=None,strict=False);settings.read(user,encoding='utf-8-sig')
    merged=b.m.v.GAME/'Mods/mod0000_MergedFiles/content/scripts/game/gui/menus/inventorymenu.ws'
    report=dict(archives=rows,installed=installed,autoloot_saved_options=dict(settings['AutoLoot']),merged_inventory_sha256=sha(merged.read_bytes()),no_installation_or_runtime_test=True)
    b.m.b.write_json(OUT/'qol-evidence.json',report)
    b.m.b.write_json(ROOT/'research/adaptive-inventory-v2-qol-manifest.json',report)
    print('Three archives, member hashes, annotation ownership, bundle keys and installed evidence recorded.')
if __name__=='__main__':main()
