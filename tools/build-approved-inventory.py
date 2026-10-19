"""Private unified player Inventory candidate; read-only installed inputs."""
import argparse,configparser,hashlib,importlib.util,io,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build-adaptive-inventory');p=load('patch-approved-inventory');gate=load('inspect-approved-inventory');prior=load('build-inventory-p2')
OUT=ROOT/'build/approved-inventory-unified-p1';DEPLOY=ROOT/'deploy/approved-inventory-unified-p1'
KEY=b.KEY;BASE=b.BASE;BEFORE=gate.EXPORT;MOD='modApprovedInventoryUnifiedP1'
SCRIPT=ROOT/'src/inventory/unified/approvedInventory.ws';COMPILER=ROOT/'build/approved-inventory-unified-scripts-final/receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):b.write(path,value)
def freeze():return prior.freeze()
def inspect():
    OUT.mkdir(exist_ok=True)
    source=BASE/'prepared-inputs'/KEY
    if sha(source)!=gate.V4_SHA or b.b.m.r.p.movie(source.read_bytes())[1]!=(BEFORE/'source.gfx').read_bytes():raise ValueError('Exact v4 input/export mismatch')
    if sha(gate.REFERENCE)!=gate.AUTHORIZED_SHA:raise ValueError('Approved visual reference changed')
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.b.m.b.settings_text(b.b.m.v.SETTINGS))
    owners=b.b.m.b.owners(b.b.m.v.GAME,cfg,{KEY,'gameplay/gui_new/swf/common/panel_common.redswf'},OUT)
    winners={k:min([r for r in rows if r['enabled']=='1'],key=lambda r:int(r['priority'] or 999999)) for k,rows in owners.items()}
    if winners[KEY]['sha256']!=gate.V4_SHA:raise ValueError('Current Inventory owner is not accepted v4: '+str(winners[KEY]))
    write(OUT/'installed-owners.json',dict(owners=owners,winners=winners))
    frozen=OUT/'frozen.json';state=freeze()
    if frozen.exists() and json.loads(frozen.read_text())!=state:raise ValueError('Protected inputs changed')
    write(frozen,state);print(json.dumps(winners,indent=2),flush=True)
def prepare():
    inspect()
    source=(BASE/'prepared-inputs'/KEY).read_bytes()
    folders=sorted(OUT.glob('abc-*'));folder=OUT/('abc-'+str(len(folders)+1).zfill(2));folder.mkdir()
    data,changes=b.b.batch_compile(source,BEFORE,folder,p.TRANSFORMS)
    after=folder/'after';after.mkdir();(after/'source.gfx').write_bytes(b.b.m.r.p.movie(data)[1]);b.b.m.b.export(after/'source.gfx',after)
    if [(c,v) for c,v in b.b.m.b.audit.swf_tags(source)[2] if c!=82]!=[(c,v) for c,v in b.b.m.b.audit.swf_tags(data)[2] if c!=82]:raise ValueError('Non-code movie changes')
    if [c['tail'] for c in b.b.m.b.font.native.chunks(source)[1:]]!=[c['tail'] for c in b.b.m.b.font.native.chunks(data)[1:]]:raise ValueError('Texture atlas changed')
    if not all(c['crc_valid'] for c in b.b.m.b.font.native.chunks(data)):raise ValueError('Native resource CRC failure')
    contracts=b.b.m.b.class_contracts(BEFORE/'scripts',after/'scripts')
    changed=[f.stem for f in (BEFORE/'scripts').rglob('*.as') if f.read_bytes()!=(after/'scripts'/f.relative_to(BEFORE/'scripts')).read_bytes()]
    if set(changed)!=set(p.TRANSFORMS):raise ValueError('Unexpected classes '+str(changed))
    for name in ('SlotPaperdoll','ItemDataStub','ModuleInputFeedback','InputFeedbackButton','CharacterRendererController'):
        if gate.one(name).read_bytes()!=next((after/'scripts').rglob(name+'.as')).read_bytes():raise ValueError('Preserved class changed '+name)
    target=OUT/'prepared-inputs'/KEY;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    write(OUT/'prepared.json',dict(version='Approved Inventory — Unified P1',key=KEY,abc=str(folder),input_sha256=gate.V4_SHA,resource_sha256=sha(target),changes=changes,changed_classes=changed,contracts=contracts,atlas=b.old.atlas.validate(data),non_code_and_textures_exact=True,runtime_tested=False))
    print('Prepared exact-v4 unified player Inventory',flush=True)
def native():
    if freeze()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected inputs changed')
    if (OUT/'native-commands.json').exists():
        archive=OUT/('native-prior-'+str(len(list(OUT.glob('native-prior-*')))+1).zfill(2));archive.mkdir()
        # Only explicitly named private build outputs; no installed paths.
        names=['native-commands.json','cooked','validation','packed']+[k+s for k in ('cook','validate','pack','metadata') for s in ('.full.log','.stdout.log')]+['temp-'+k for k in ('cook','validate','pack','metadata')]
        for name in names:
            path=OUT/name
            if path.exists():path.rename(archive/name)
    b.old.native(OUT)
def reconstruct():
    # Existing independently controlled same-key fallback, only on blank startup
    # timeout; this never claims native validation of the candidate.
    standard=load('native-zlib-control');original=b.zlib.compress
    try:
        b.OUT=OUT;b.zlib.compress=standard.compress;b.reconstruct()
    finally:b.zlib.compress=original
    report=json.loads((OUT/'reconstruction.json').read_text());report['compressor']='Standard zlib '+standard.version()
    write(OUT/'reconstruction.json',report)
def metadata_fallback():
    prior.OUT=OUT;prior.metadata_fallback()
def package():
    if DEPLOY.exists():raise ValueError('Private release already exists')
    if freeze()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected inputs changed')
    d=json.loads((OUT/'prepared.json').read_text());compiler=json.loads(COMPILER.read_text())
    if compiler['source_sha256']!=sha(SCRIPT):raise ValueError('Script/source mismatch')
    for row in compiler['results']:
        if row['exit_code']!=0 or sha(COMPILER.parent/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Script compiler control changed')
    for name,fn in p.TRANSFORMS.items():
        if (Path(d['abc'])/(name+'.as')).read_text(encoding='utf-8')!=fn(gate.one(name).read_text(encoding='utf-8-sig')):raise ValueError('ActionScript/source mismatch '+name)
    commands=json.loads((OUT/'native-commands.json').read_text());passed={r['label'] for r in commands if r['passed']}
    complete={'cook','validate','pack','metadata'}<=passed
    fallback=None
    if not complete:
        receipt=OUT/('metadata-reconstruction.json' if {'cook','validate','pack'}<=passed else 'reconstruction.json')
        fallback=json.loads(receipt.read_text())
        if 'metadata' in receipt.name:
            if fallback['output_metadata_sha256']!=sha(OUT/'packed/metadata.store') or fallback['candidate_bundle_sha256']!=sha(OUT/'packed/blob0.bundle'):raise ValueError('Fallback pins changed')
        elif not fallback['independent_changed_bundle_and_metadata_exact']:raise ValueError('Fallback controls incomplete')
    data=(OUT/'prepared-inputs'/KEY).read_bytes();bundle=OUT/'packed/blob0.bundle'
    if complete and (OUT/'cooked'/KEY).read_bytes()!=data:raise ValueError('Native candidate differs from current prepared source')
    if KEY.replace('/','\\').encode() not in (OUT/'packed/metadata.store').read_bytes():raise ValueError('Metadata does not name Inventory')
    if sha(OUT/'prepared-inputs'/KEY)!=d['resource_sha256'] or b.b.m.b.bars.extract(bundle,KEY)!=data or [e['resource'] for e in b.b.m.b.audit.entries(bundle)]!=[KEY]:raise ValueError('Exact one-resource extraction failed')
    prefix='Mods/'+MOD+'/content/'
    members={prefix+n:(OUT/'packed'/n).read_bytes() for n in ('blob0.bundle','metadata.store')}
    members[prefix+'scripts/local/approvedInventory.ws']=SCRIPT.read_bytes()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,(2026,10,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
    DEPLOY.mkdir();path=DEPLOY/'Approved-Inventory-Unified-P1-private.zip';path.write_bytes(stream.getvalue())
    with zipfile.ZipFile(path) as z:
        if z.testzip() or {n:z.read(n) for n in z.namelist()}!=members:raise ValueError('ZIP integrity failed')
    d.update(zip_path=str(path),zip_sha256=sha(path),members={n:hashlib.sha256(v).hexdigest() for n,v in members.items()},native_commands=commands,native_complete=complete,fallback=fallback,compiler=compiler,live_unchanged=True,runtime_tested=False)
    sources=[Path(__file__),ROOT/'tools/patch-approved-inventory.py',ROOT/'tools/verify-approved-inventory.py',ROOT/'tools/native-zlib-control.py',ROOT/'tools/compile-ink-gear-grid.py',ROOT/'tests/test_approved_inventory_unified.py',*list((ROOT/'src/inventory/unified').iterdir())]
    d['original_sources']={str(f.relative_to(ROOT)):sha(f) for f in sources}
    write(OUT/'receipt.json',d);write(DEPLOY/'manifest.json',d);print(str(path)+'\nSHA-256 '+d['zip_sha256'])
def main():
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul only')
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('inspect','prepare','native','reconstruct','metadata-fallback','package'));globals()[ap.parse_args().stage.replace('-','_')]()
if __name__=='__main__':main()
