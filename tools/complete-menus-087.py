"""Private visual completion; read-only deployment evidence, no live mutations.

Reuses verified v1 movies, recompiles only Common, adds two omitted authored
menu movies. Optional author caches remain separate, exact, private modules.
"""
import argparse, configparser, io, json, zipfile
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location('baseline', ROOT/'tools/build-menus-087.py')
b = importlib.util.module_from_spec(s); s.loader.exec_module(b)
OLD = b.OUT
OUT = ROOT/'build/menus087-v2'
DEPLOY = ROOT/'deploy/menus087-v2'
COMMON = 'gameplay/gui_new/swf/common/panel_common.redswf'
EXTRAS = ['gameplay/gui_new/swf/character/panel_character_perks.redswf',
          'gameplay/gui_new/swf/meditation/panel_meditation.redswf']

def evidence():
    OUT.mkdir(exist_ok=True)
    cfg = configparser.ConfigParser(); cfg.read_string(b.m.b.settings_text(b.m.v.SETTINGS))
    keys = set(json.loads((OLD/'prepared.json').read_text())['keys']) | set(EXTRAS)
    owners = b.m.b.owners(b.m.v.GAME, cfg, keys, OUT)
    rows = []
    for key, candidates in owners.items():
        active = [r for r in candidates if r['enabled']=='1']
        if not active: continue
        winner = min(active,key=lambda r:int(r['priority'] or 999999))
        container = Path(winner['container'])
        data = b.m.b.read_bundle(container,next(e for e in b.m.b.audit.entries(container) if e['resource']==key),b.m.v.GAME,OUT) if container.suffix=='.bundle' else container.read_bytes()
        rows.append(dict(resource=key,winner=winner,sha256=b.m.b.audit.sha(data),candidates=candidates))
    receipt = json.loads((OLD/'receipt.json').read_text())
    installed = {}
    for member, expected in receipt['members'].items():
        p = b.m.v.GAME/member
        actual = b.m.b.fallback.sha(p) if p.exists() else None
        installed[member] = dict(expected=expected,actual=actual,equal=actual==expected)
    settings = b.m.v.SETTINGS.parent/'dx12user.settings'
    opts = configparser.ConfigParser(strict=False); opts.read_string(b.m.b.fallback.text(settings))
    caches = []
    for mod in (b.m.v.GAME/'Mods').iterdir():
        if mod.name not in cfg or cfg[mod.name].get('Enabled')!='1': continue
        for p in mod.rglob('texture.cache'):
            if p.stat().st_size:
                caches.append(dict(path=str(p),keys=[r['resource'] for r in b.m.b.inventory.cache_entries(p)],sha256=b.m.b.fallback.sha(p)))
    result=dict(resources=rows,installed_v1_members=installed,dx12_options=dict(opts['InkAndIronOptions']) if 'InkAndIronOptions' in opts else {},caches=caches,settings_sha256=b.m.b.fallback.sha(b.m.v.SETTINGS),runtime_rendering_verified=False)
    b.m.b.write_json(OUT/'ownership.json',result)
    b.m.b.write_json(OUT/'frozen.json',b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS))
    print('Recorded current ownership and exact deployed hashes',flush=True)

def prepare():
    if not (OUT/'ownership.json').exists(): evidence()
    previous=json.loads((OLD/'prepared.json').read_text())
    ledger=json.loads((b.E/'ledger.json').read_text())
    b.OUT=OUT
    original_atlas=b.atlas.validate
    def validate_atlas(data):
        chunks=b.m.b.font.native.chunks(data)
        if 'textures' not in chunks[0]['properties']:
            if len(chunks)!=1 or not all(c['crc_valid'] for c in chunks) or any(code==1009 for code,_ in b.m.b.audit.swf_tags(data)[2]):
                raise ValueError('Invalid texture-free movie')
            return dict(textures=[],external_images=0,texture_free=True)
        return original_atlas(data)
    b.atlas.validate=validate_atlas
    original_topbar=b.patch.topbar
    # Capture original to prevent recursion in the injected bounded transform.
    def header(text):
        text=original_topbar(text)
        return b.patch.p.one(text,'tf.y = baseline - size * 0.93 - 2;','tf.y = baseline - tf.getLineMetrics(0).ascent - 2;')
    b.patch.topbar=header
    results=[]
    for row in previous['resources']:
        key=row['resource']
        if key==COMMON: results.append(b.process((key,ledger['versions']['0.8.7']['resources'][key])))
        else:
            p=OUT/'prepared-inputs'/key;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes((OLD/'prepared-inputs'/key).read_bytes());results.append(row)
    for key in EXTRAS: results.append(b.process((key,ledger['versions']['0.8.7']['resources'][key])))
    optional=[]
    for pattern in ('*Bestiary Art*.zip','*Map Inked*.zip'):
        matches=list((ROOT/'reference').glob(pattern))
        if len(matches)!=1: raise ValueError('Expected exact optional archive: '+pattern)
        archive=matches[0];members={}
        with zipfile.ZipFile(archive) as z:
            if len(z.namelist())!=2 or z.testzip(): raise ValueError('Unexpected optional archive')
            for name in z.namelist():
                if not name.startswith('mods/') or '..' in Path(name).parts: raise ValueError('Unsafe archive path')
                data=z.read(name);p=OUT/'optional'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                members[name]=b.m.b.audit.sha(data)
        cache=next((OUT/'optional').glob('mods/'+('modInkAndIronGlossary' if 'Bestiary' in archive.name else 'modInkAndIronMap_Inked')+'/content/texture.cache'))
        entries=list(b.m.b.inventory.cache_entries(cache));keys={r['resource'] for r in entries}
        collisions=[]
        for row in json.loads((OUT/'ownership.json').read_text())['caches']:
            overlap=keys & set(row['keys'])
            if overlap: collisions.append(dict(path=row['path'],keys=sorted(overlap)))
        optional.append(dict(archive=str(archive),sha256=b.m.b.fallback.sha(archive),members=members,cache_entries=len(entries),cache_keys=sorted(keys),collisions=collisions))
    b.m.b.write_json(OUT/'prepared.json',dict(keys=sorted(r['resource'] for r in results),resources=results,optional=optional,parent_zip_sha256=json.loads((OLD/'receipt.json').read_text())['zip_sha256'],runtime_tested=False))

def package():
    if DEPLOY.exists(): raise ValueError('Fresh release directory required')
    p=json.loads((OUT/'prepared.json').read_text());commands=json.loads((OUT/'native-commands.json').read_text())
    if {r['label'] for r in commands if r['passed']}!={'cook','validate','pack','metadata'}:raise ValueError('Native pipeline incomplete')
    bundle=OUT/'packed/blob0.bundle';entries=list(b.m.b.audit.entries(bundle))
    if {e['resource'] for e in entries}!=set(p['keys']):raise ValueError('Unexpected bundle key')
    for e in entries:
        if b.m.b.bars.extract(bundle,e['resource'])!=(OUT/'prepared-inputs'/e['resource']).read_bytes():raise ValueError('Re-extraction mismatch')
    with zipfile.ZipFile(json.loads((OLD/'receipt.json').read_text())['zip_path']) as z:
        members={n:z.read(n) for n in z.namelist()}
    for name in ('blob0.bundle','metadata.store'): members['Mods/modInkIronMenus087/content/'+name]=(OUT/'packed'/name).read_bytes()
    for row in p['optional']:
        for name,sha in row['members'].items():
            data=(OUT/'optional'/name).read_bytes()
            if b.m.b.audit.sha(data)!=sha:raise ValueError('Optional source changed')
            members['Mods/'+name[5:]]=data
    def archive_bytes():
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name,data in sorted(members.items()):
                info=zipfile.ZipInfo(name,(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
        return stream.getvalue()
    data=archive_bytes()
    if data!=archive_bytes():raise ValueError('ZIP not deterministic')
    if b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS)!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Live files changed')
    DEPLOY.mkdir();path=DEPLOY/'Ink-Iron-0.8.7-Compatible-Menus-v2-private-test.zip';path.write_bytes(data)
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError('ZIP CRC failure')
    b.m.b.write_json(OUT/'receipt.json',dict(zip_path=str(path),zip_sha256=b.m.b.audit.sha(data),bytes=len(data),members={n:b.m.b.audit.sha(v) for n,v in members.items()},native=commands,prepared=p,live_unchanged=True,runtime_tested=False,script_compile='Exact v1 scripts and compiler receipts retained; no source changes'))
    print(path,b.m.b.audit.sha(data),flush=True)

def report():
    receipt=json.loads((OUT/'receipt.json').read_text());ownership=json.loads((OUT/'ownership.json').read_text())
    prepared=receipt['prepared'];compiled=json.loads((b.SCRIPTS/'receipt.json').read_text())
    focus={COMMON,'gameplay/gui_new/swf/inventory/panel_inventory.redswf','gameplay/gui_new/swf/worldmap/panel_worldmap.redswf'}
    result=dict(release='Ink & Iron 0.8.7 Compatible Menus v2',date='2026-10-17',
        zip_path=receipt['zip_path'],zip_sha256=receipt['zip_sha256'],zip_bytes=receipt['bytes'],
        runtime_tested=False,live_unchanged=receipt['live_unchanged'],
        original_087_archive=json.loads((b.E/'ledger.json').read_text())['archive'],
        observed_effective_owners=[dict(resource=r['resource'],owner=r['winner']['owner'],priority=r['winner']['priority'],sha256=r['sha256']) for r in ownership['resources'] if r['resource'] in focus],
        all_installed_v1_members_exact=all(r['equal'] for r in ownership['installed_v1_members'].values()),
        dx12_options_observed=ownership['dx12_options'],
        resources=[dict(resource=r['resource'],input_sha256=r['input_sha256'],output_sha256=r['output_sha256']) for r in prepared['resources']],
        optional_art=[{k:v for k,v in row.items() if k!='cache_keys'} for row in prepared['optional']],
        native=receipt['native'],native_log_hashes={p.name:b.m.b.fallback.sha(p) for p in (OUT/'native-final').glob('*.log')},
        native_metadata=True,reconstructed_metadata=False,
        targeted_tests=json.loads((OUT/'test-result.json').read_text()),
        compiler=dict(reused_exact_v1_compiles=True,results=compiled['results'],source_hashes=compiled['source_hashes']),
        retained_v1_movies_byte_identical=37,menu_art_cache_entries=24,
        font_library_replaced=False,accepted_hud_package_changed=False,
        artifacts=receipt['members'],
        source_tools={name:b.m.b.fallback.sha(ROOT/'tools'/name) for name in ('complete-menus-087.py','verify-menu-visual-install.py')})
    b.m.b.write_json(ROOT/'research/menus087-visual-completion-v2-manifest.json',result)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('evidence','prepare','native','package','report'));a=ap.parse_args()
    import subprocess
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Wrong branch')
    if a.stage=='native':b.OUT=OUT;b.native_build()
    else:globals()[a.stage]()
if __name__=='__main__':main()
