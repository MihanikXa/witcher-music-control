"""Bounded P2 structural Gear build. Never writes game, settings or Vortex."""
import argparse,configparser,hashlib,importlib.util,io,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build-adaptive-inventory');p=load('patch-inventory-p2');proof=load('verify-inventory-p2')
OUT=ROOT/'build/adaptive-inventory-p2';DEPLOY=ROOT/'deploy/adaptive-inventory-p2';KEY=b.KEY;BASE=b.BASE
BEFORE=ROOT/'build/adaptive-inventory-v2-p1/before';MOD='modAdaptiveInventoryP2'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj):b.write(path,obj)
def freeze():
    state=b.frozen()
    for name,value in b.v4_files().items():state[str(b.b.m.v.GAME/name)]=value
    return state
def inspect():
    proof.main()
    state=freeze();write(OUT/'frozen.json',state)
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.b.m.b.settings_text(b.b.m.v.SETTINGS))
    rows=b.b.m.b.owners(b.b.m.v.GAME,cfg,{KEY,'gameplay/gui_new/swf/common/panel_common.redswf'},OUT)
    write(OUT/'installed-owners.json',rows)
    print('Installed ownership captured read-only; v4 on-disk files exact. P1 may still own Inventory until manually disabled.')
def prepare():
    if not (OUT/'frozen.json').exists():inspect()
    if freeze()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected files changed')
    cases=proof.fixtures();proof.verify_cases(cases)
    source=(BASE/'prepared-inputs'/KEY).read_bytes()
    data,changes=b.b.batch_compile(source,BEFORE,OUT/'abc',p.TRANSFORMS)
    after=OUT/'after'
    if not (after/'scripts').exists():
        after.mkdir(exist_ok=True);gfx=after/'source.gfx';gfx.write_bytes(b.b.m.r.p.movie(data)[1]);b.b.m.b.export(gfx,after)
    if [(c,v) for c,v in b.b.m.b.audit.swf_tags(source)[2] if c!=82] != [(c,v) for c,v in b.b.m.b.audit.swf_tags(data)[2] if c!=82]:raise ValueError('Non-code movie changes')
    if [c['tail'] for c in b.b.m.b.font.native.chunks(source)[1:]] != [c['tail'] for c in b.b.m.b.font.native.chunks(data)[1:]]:raise ValueError('Atlas changed')
    if not all(c['crc_valid'] for c in b.b.m.b.font.native.chunks(data)):raise ValueError('Native CRC failure')
    contracts=b.b.m.b.class_contracts(BEFORE/'scripts',after/'scripts')
    for name in ('SlotPaperdoll','ItemDataStub','ModuleInputFeedback','InputFeedbackButton'):
        if b.old.unique(BEFORE/'scripts',name+'.as').read_bytes()!=b.old.unique(after/'scripts',name+'.as').read_bytes():raise ValueError('Frozen class changed '+name)
    changed=[f.stem for f in (BEFORE/'scripts').rglob('*.as') if f.read_bytes()!=(after/'scripts'/f.relative_to(BEFORE/'scripts')).read_bytes()]
    if set(changed)!=set(p.TRANSFORMS):raise ValueError('Unexpected changed classes '+str(changed))
    dest=OUT/'prepared-inputs'/KEY;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write(OUT/'prepared.json',dict(version='Adaptive Inventory P2 — Coherent Gear Prototype',input_sha256=sha(BASE/'prepared-inputs'/KEY),resource_sha256=hashlib.sha256(data).hexdigest(),changes=changes,changed_classes=changed,contracts=contracts,geometry_cases=len(cases),atlas=b.old.atlas.validate(data),non_code_and_textures_exact=True,shared_and_hoods_classes_exact=True,runtime_tested=False))
    print('P2 prepared from v4: contiguous native gallery, identity data bridge and one native footer.')
def native():
    if freeze()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected files changed')
    history=OUT/'native-commands.json'
    if history.exists():
        commands=json.loads(history.read_text())
        passed={r['label'] for r in commands if r['passed']}
        if passed=={'cook','validate','pack'} and commands[-1]['label']=='metadata' and commands[-1]['exit_code'] is None:
            data=(OUT/'prepared-inputs'/KEY).read_bytes()
            if (OUT/'cooked'/KEY).read_bytes()!=data or b.b.m.b.bars.extract(OUT/'packed/blob0.bundle',KEY)!=data:raise ValueError('Native resume content changed')
            for suffix in ('full.log','stdout.log'):
                path=OUT/('metadata.'+suffix)
                if path.exists():path.rename(OUT/('metadata-timeout-'+str(len(commands))+'.'+suffix))
            temporary=OUT/'temp-metadata'
            if temporary.exists():temporary.rename(OUT/('temp-metadata-timeout-'+str(len(commands))))
            runner=ROOT/'build/ink-hud-v3-native-runner'
            with b.old.b.mount(runner,OUT,{}) as workspace:
                ok,_=b.old.native_tool.native(runner,OUT,'metadata',['metadatastore','-path='+str(OUT/'packed')],commands)
                if not ok:raise ValueError('Native metadata retry did not pass; no fallback')
            print('Native metadata retry passed; original timeout retained');return
        if passed=={'cook','validate','pack','metadata'}:raise ValueError('All native stages already complete')
    b.old.native(OUT)
def package():
    if DEPLOY.exists():raise ValueError('Fresh private deploy path required')
    d=json.loads((OUT/'prepared.json').read_text());commands=json.loads((OUT/'native-commands.json').read_text())
    passed={r['label'] for r in commands if r['passed']};reconstruction=None
    if not {'cook','validate','pack'}<=passed:raise ValueError('Native resource gates incomplete')
    if 'metadata' not in passed:
        reconstruction=json.loads((OUT/'metadata-reconstruction.json').read_text())
        if not reconstruction['native_control_byte_identical'] or not reconstruction['independent_changed_control_exact']:raise ValueError('Metadata controls incomplete')
        if reconstruction['output_metadata_sha256']!=sha(OUT/'packed/metadata.store') or reconstruction['candidate_bundle_sha256']!=sha(OUT/'packed/blob0.bundle'):raise ValueError('Metadata reconstruction content changed')
    if freeze()!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Protected files changed')
    bundle=OUT/'packed/blob0.bundle';data=(OUT/'prepared-inputs'/KEY).read_bytes()
    if sha(OUT/'prepared-inputs'/KEY)!=d['resource_sha256'] or (OUT/'cooked'/KEY).read_bytes()!=data:raise ValueError('Cooked/prepared pin changed')
    # Reject packaging an older compiled checkpoint after a source edit.
    for name,transform in p.TRANSFORMS.items():
        if (OUT/'abc'/(name+'.as')).read_text(encoding='utf-8')!=transform(b.old.unique(BEFORE/'scripts',name+'.as').read_text(encoding='utf-8-sig')):raise ValueError('Current source differs from compiled candidate '+name)
    if [e['resource'] for e in b.b.m.b.audit.entries(bundle)]!=[KEY] or b.b.m.b.bars.extract(bundle,KEY)!=data:raise ValueError('Exact one-key extraction failed')
    compiler=json.loads((ROOT/'build/adaptive-inventory-p2-scripts/receipt.json').read_text())
    script=ROOT/'src/inventory/inkGearGrid.ws'
    if compiler['source_sha256']!=sha(script):raise ValueError('Annotation source pin changed')
    prefix='Mods/'+MOD+'/content/'
    members={prefix+n:(OUT/'packed'/n).read_bytes() for n in ('blob0.bundle','metadata.store')};members[prefix+'scripts/local/inkGearGrid.ws']=script.read_bytes()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,(2026,10,18,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
    DEPLOY.mkdir();path=DEPLOY/'Adaptive-Inventory-P2-Coherent-Gear-private.zip';path.write_bytes(stream.getvalue())
    with zipfile.ZipFile(path) as z:
        if z.testzip() or {n:z.read(n) for n in z.namelist()}!=members:raise ValueError('ZIP check failed')
    d.update(zip_path=str(path),zip_sha256=sha(path),bytes=path.stat().st_size,members={n:hashlib.sha256(v).hexdigest() for n,v in members.items()},native_commands=commands,native_resource_complete=True,native_complete='metadata' in passed,reconstruction_used=reconstruction is not None,metadata_reconstruction=reconstruction,compiler=compiler,frozen_inputs=freeze(),live_unchanged=True)
    d['original_sources']={str(f.relative_to(ROOT)):sha(f) for f in [Path(__file__),ROOT/'tools/patch-inventory-p2.py',ROOT/'tools/verify-inventory-p2.py',*list((ROOT/'src/inventory/p2').glob('*.asinc'))]}
    write(OUT/'receipt.json',d);write(DEPLOY/'manifest.json',d);print(path,d['zip_sha256'])

def verify_installed():
    # Existing read-only effective-owner gate, pointed at this release. It checks
    # every accepted v4 movie, package member and protected HUD/merged input.
    b.OUT=OUT;b.MOD=MOD;b.verify_installed()

def metadata_fallback():
    commands=json.loads((OUT/'native-commands.json').read_text())
    if commands[-1]['label']!='metadata' or commands[-1]['exit_code'] is not None:raise ValueError('Only metadata startup timeout is eligible')
    if any((OUT/('metadata.'+suffix)).stat().st_size for suffix in ('full.log','stdout.log')):raise ValueError('Nonblank diagnostics require investigation')
    subprocess.run(['python',str(ROOT/'tools/relocate-inventory-metadata.py'),'--out',str(OUT)],check=True)
def main():
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Branch guard')
    a=argparse.ArgumentParser();a.add_argument('stage',choices=('inspect','prepare','native','metadata-fallback','package','verify-installed'));stage=a.parse_args().stage;globals()[stage.replace('-','_')]()
if __name__=='__main__':main()
