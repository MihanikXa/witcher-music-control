"""Private Gear Prototype 1. One v4 movie + original annotations; never deploys."""
import argparse, configparser, importlib.util, io, json, struct, subprocess, zipfile, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build-menus-087');p=load('patch-adaptive-inventory');old=load('build-ink-gear-grid');meta=load('relocate-inventory-metadata')
OUT=ROOT/'build/adaptive-inventory-v2-p1';DEPLOY=ROOT/'deploy/adaptive-inventory-v2-p1'
BASE=ROOT/'build/menus087-v4-final';KEY=old.KEY;MOD='modAdaptiveInventoryV2GearP1'
def write(path,obj): b.m.b.write_json(path,obj)
def frozen(): return old.frozen()
def v4_files():
    receipt=json.loads((BASE/'receipt.json').read_text())
    observed={name:b.m.b.fallback.sha(b.m.v.GAME/name) for name in receipt['members']}
    if observed!=receipt['members']:raise ValueError('Accepted v4 deployed file changed')
    return observed
def prepare():
    OUT.mkdir(exist_ok=True)
    subprocess.run(['python',str(ROOT/'tools/verify-menu-visual-install.py'),'--release',str(BASE/'receipt.json'),'--report',str(OUT/'installed-v4.json')],check=True)
    source=(BASE/'prepared-inputs'/KEY).read_bytes()
    receipt=json.loads((BASE/'receipt.json').read_text())
    expected=next(r['output_sha256'] for r in receipt['resources'] if r['resource']==KEY)
    if b.m.b.audit.sha(source)!=expected:raise ValueError('Accepted v4 source pin differs')
    if not (OUT/'frozen.json').exists():write(OUT/'frozen.json',frozen())
    if frozen()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected files changed')
    write(OUT/'accepted-v4-files.json',v4_files())
    before=OUT/'before'
    if not (before/'scripts').exists():
        before.mkdir(exist_ok=True);gfx=before/'source.gfx';gfx.write_bytes(b.m.r.p.movie(source)[1]);b.m.b.export(gfx,before)
    if (before/'source.gfx').read_bytes()!=b.m.r.p.movie(source)[1]:raise ValueError('Wrong v4 export')
    data,changes=b.batch_compile(source,before,OUT/'abc',p.TRANSFORMS)
    after=OUT/'after'
    if not (after/'scripts').exists():
        after.mkdir(exist_ok=True);gfx=after/'source.gfx';gfx.write_bytes(b.m.r.p.movie(data)[1]);b.m.b.export(gfx,after)
    if [(c,v) for c,v in b.m.b.audit.swf_tags(source)[2] if c!=82] != [(c,v) for c,v in b.m.b.audit.swf_tags(data)[2] if c!=82]:raise ValueError('Non-code artwork changed')
    if [c['tail'] for c in b.m.b.font.native.chunks(source)[1:]] != [c['tail'] for c in b.m.b.font.native.chunks(data)[1:]]:raise ValueError('Texture changed')
    if not all(c['crc_valid'] for c in b.m.b.font.native.chunks(data)):raise ValueError('Native CRC failure')
    contracts=b.m.b.class_contracts(before/'scripts',after/'scripts')
    changed=[f.stem for f in (before/'scripts').rglob('*.as') if f.read_bytes()!=(after/'scripts'/f.relative_to(before/'scripts')).read_bytes()]
    if set(changed)!=set(p.TRANSFORMS):raise ValueError('Unexpected class changes '+str(changed))
    # Dye handling is already on v4; do not reimport an older official movie.
    for name in ('SlotPaperdoll','ItemDataStub'):
        if old.unique(before/'scripts',name+'.as').read_bytes()!=old.unique(after/'scripts',name+'.as').read_bytes():raise ValueError('Hoods contract changed')
    dest=OUT/'prepared-inputs'/KEY;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write(OUT/'prepared.json',dict(version='Adaptive Inventory v2 — Gear Prototype 1',key=KEY,input_sha256=expected,resource_sha256=b.m.b.audit.sha(data),changes=changes,changed_classes=changed,contracts=contracts,atlas=old.atlas.validate(data),non_code_and_textures_exact=True,hoods_classes_exact=True,runtime_tested=False))
    print('Prepared eight Inventory classes on accepted v4',flush=True)
def native(): old.native(OUT)
def reconstruct(*, diagnostic_only=False):
    # Explicit diagnostic packaging may reuse the same independently tested
    # reconstruction without manufacturing a native timeout/validation receipt.
    if not diagnostic_only:
        commands=json.loads((OUT/'native-commands.json').read_text())
        if len(commands)!=1 or commands[0]['exit_code'] is not None:raise ValueError('Fallback only for bounded cook startup timeout')
        if (OUT/'cook.full.log').stat().st_size or (OUT/'cook.stdout.log').stat().st_size:raise ValueError('Nonblank native diagnostics require investigation')
    # Same-key reconstruction of an actual one-movie native bundle, including independent changed controls.
    def bundle(template,data):
        raw=template.read_bytes();entries=list(b.m.b.audit.entries(template))
        if len(entries)!=1 or raw[:8]!=b'POTATO70' or struct.unpack_from('<I',raw,16)[0]!=304:raise ValueError('Unsupported template')
        e=entries[0]
        if e['resource']!=KEY or e['codec']!=1 or e['offset']!=336 or e['offset']+e['packed']!=len(raw):raise ValueError('Unexpected native layout')
        out=bytearray(raw[:336]);packed=zlib.compress(data,9);out.extend(packed)
        struct.pack_into('<QIIII',out,32+272,336,len(data),len(packed),zlib.crc32(data),1)
        struct.pack_into('<Q',out,8,(len(out)+15)//16*16);return bytes(out)
    templates=[ROOT/'build/ink-gear-grid-v1-focus/packed',ROOT/'build/ink-gear-grid-v1-final/packed']
    controls=[]
    for folder in templates:
        path=folder/'blob0.bundle';data=b.m.b.bars.extract(path,KEY)
        if bundle(path,data)!=path.read_bytes():raise ValueError('Native bundle control failed')
        controls.append(dict(path=str(folder),bundle_sha256=b.m.b.fallback.sha(path),byte_identical=True))
    if bundle(templates[0]/'blob0.bundle',b.m.b.bars.extract(templates[1]/'blob0.bundle',KEY))!=(templates[1]/'blob0.bundle').read_bytes():raise ValueError('Independent changed bundle failed')
    metadata_controls=[]
    for name in ('ink-gear-grid-v1-focus','editor-cook-resolved','npc-shadow-unique-cook','field-folio-control-v2','subtitle-shadow-control-v1'):
        folder=ROOT/'build'/name/'packed';md=(folder/'metadata.store').read_bytes()
        if meta.write(meta.replace_single(meta.parse(md),folder/'blob0.bundle'))!=md:raise ValueError('Native metadata identity control failed')
        metadata_controls.append(dict(path=str(folder),sha256=b.m.b.audit.sha(md),byte_identical=True))
    msource=ROOT/'build/editor-cook-resolved/packed';mchanged=ROOT/'build/npc-shadow-unique-cook/packed'
    if meta.write(meta.replace_single(meta.parse((msource/'metadata.store').read_bytes()),mchanged/'blob0.bundle'))!=(mchanged/'metadata.store').read_bytes():raise ValueError('Independent changed native metadata failed')
    data=(OUT/'prepared-inputs'/KEY).read_bytes()
    for index in (2,5,6,7,8,9):
        if struct.unpack_from('<III',data,40+index*12)[1]:raise ValueError('New dependencies/buffers')
    packed=OUT/'packed';packed.mkdir();target=packed/'blob0.bundle';target.write_bytes(bundle(templates[0]/'blob0.bundle',data))
    (packed/'metadata.store').write_bytes(meta.write(meta.replace_single(meta.parse((templates[0]/'metadata.store').read_bytes()),target)))
    if b.m.b.bars.extract(target,KEY)!=data:raise ValueError('Extraction failed')
    write(OUT/'reconstruction.json',dict(native_candidate_validated=False,controls=controls,metadata_controls=metadata_controls,independent_changed_bundle_and_metadata_exact=True,exact_extraction=True,method='same-key one-resource native-control reconstruction; no native success claimed'))
def package():
    if DEPLOY.exists():raise ValueError('Fresh release path required')
    if frozen()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected files changed')
    if v4_files()!=json.loads((OUT/'accepted-v4-files.json').read_text()):raise ValueError('Accepted v4 changed')
    prepared=json.loads((OUT/'prepared.json').read_text());commands=json.loads((OUT/'native-commands.json').read_text())
    native_complete={r['label'] for r in commands if r['passed']}=={'cook','validate','pack','metadata'}
    reconstruction=None if native_complete else json.loads((OUT/'reconstruction.json').read_text())
    script=ROOT/'src/inventory/inkGearGrid.ws';compiler=json.loads((ROOT/'build/adaptive-inventory-v2-p1-scripts/receipt.json').read_text())
    if compiler['source_sha256']!=b.m.b.fallback.sha(script):raise ValueError('Compiled annotation pin differs')
    data=(OUT/'prepared-inputs'/KEY).read_bytes();bundle=OUT/'packed/blob0.bundle'
    if prepared['resource_sha256']!=b.m.b.audit.sha(data) or b.m.b.bars.extract(bundle,KEY)!=data:raise ValueError('Resource mismatch')
    if [r['resource'] for r in b.m.b.audit.entries(bundle)]!=[KEY]:raise ValueError('Unrelated resource')
    prefix='Mods/'+MOD+'/content/';members={prefix+name:(OUT/'packed'/name).read_bytes() for name in ('blob0.bundle','metadata.store')}
    members[prefix+'scripts/local/inkGearGrid.ws']=script.read_bytes()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(members.items()):
            info=zipfile.ZipInfo(name,(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,value)
    DEPLOY.mkdir();path=DEPLOY/'Adaptive-Inventory-v2-Gear-Prototype-1-private.zip';path.write_bytes(stream.getvalue())
    with zipfile.ZipFile(path) as z:
        if z.testzip() or {n:z.read(n) for n in z.namelist()}!=members:raise ValueError('ZIP check failed')
    prepared.update(zip_path=str(path),zip_sha256=b.m.b.fallback.sha(path),bytes=path.stat().st_size,members={n:b.m.b.audit.sha(v) for n,v in members.items()},native_commands=commands,native_complete=native_complete,reconstruction=reconstruction,compiler=compiler,live_unchanged=True,frozen_inputs=frozen(),effective_base=json.loads((OUT/'installed-v4.json').read_text())['effective_winners'][KEY])
    prepared['original_source_hashes']={str(f.relative_to(ROOT)):b.m.b.fallback.sha(f) for f in [ROOT/'tools/build-adaptive-inventory.py',ROOT/'tools/patch-adaptive-inventory.py',*list((ROOT/'src/inventory/adaptive').glob('*.asinc')),ROOT/'src/inventory/inkGearGrid.ws']}
    write(OUT/'receipt.json',prepared);write(DEPLOY/'manifest.json',prepared)
    print(path,prepared['zip_sha256'],flush=True)
def verify_installed():
    """Optional read-only check AFTER the user's manual candidate deployment."""
    release=json.loads((OUT/'receipt.json').read_text());baseline=json.loads((BASE/'receipt.json').read_text())
    expected={r['resource']:r['output_sha256'] for r in baseline['resources']};expected[KEY]=release['resource_sha256']
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.m.b.settings_text(b.m.v.SETTINGS))
    owners=b.m.b.owners(b.m.v.GAME,cfg,set(expected),OUT);observed={};winners={};errors=[]
    for key,rows in owners.items():
        active=[r for r in rows if r['enabled']=='1']
        if not active:errors.append(dict(missing=key));continue
        best=min(active,key=lambda r:int(r['priority'] or 999999));winners[key]=best
        path=Path(best['container']);data=b.m.b.read_bundle(path,next(e for e in b.m.b.audit.entries(path) if e['resource']==key),b.m.v.GAME,OUT) if path.suffix=='.bundle' else path.read_bytes()
        observed[key]=b.m.b.audit.sha(data)
        if observed[key]!=expected[key]:errors.append(dict(resource=key,expected=expected[key],actual=observed[key],owner=best['owner']))
    for name,value in release['members'].items():
        path=b.m.v.GAME/name
        if not path.exists() or b.m.b.fallback.sha(path)!=value:errors.append(dict(file=name,expected=value))
    v4_files()
    for path,value in release['frozen_inputs'].items():
        if Path(path)==b.m.v.SETTINGS:continue
        if b.m.b.fallback.sha(Path(path))!=value:errors.append(dict(protected_file=path))
    write(OUT/'installed-candidate.json',dict(passed=not errors,errors=errors,effective_winners=winners,runtime_tested=False))
    print('PASS: candidate owns Inventory; all other accepted movies/files match.' if not errors else 'FAIL: see installed-candidate.json')
    if errors:raise SystemExit(1)
def main():
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','native','reconstruct','package','verify-installed']);a=ap.parse_args()
    globals()[a.stage.replace('-','_')]()
if __name__=='__main__':main()
