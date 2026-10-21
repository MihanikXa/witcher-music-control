"""Private opt-in diagnostic, not another Inventory release or native validation."""
import argparse,hashlib,importlib.util,io,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/approved-inventory-runtime-diagnostic-r5'
DEPLOY=ROOT/'deploy/approved-inventory-runtime-diagnostic-r5'
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build-approved-inventory')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def prepare():
    OUT.mkdir(exist_ok=True)
    frozen=b.freeze();pin=OUT/'protected-inputs.json'
    if pin.exists() and json.loads(pin.read_text())!=frozen:
        # A user's manual deployment between diagnostic iterations is expected;
        # capture a NEW local baseline, never silently replace an existing pin.
        raise ValueError('Protected inputs changed; start a fresh diagnostic OUT')
    write(pin,frozen)
    source=b.BASE/'prepared-inputs'/b.KEY
    if sha(source)!=b.gate.V4_SHA:raise ValueError('Not accepted v4')
    # Reuse the verified private r4 checkpoint for changed classes only, retaining
    # its original exact-v4 provenance and all previous candidate files.
    prior=ROOT/'build/approved-inventory-runtime-diagnostic-r4'
    if not (OUT/'prepared.json').exists() and (prior/'prepared.json').exists():
        receipt=json.loads((prior/'prepared.json').read_text());candidate=prior/'prepared-inputs'/b.KEY
        if receipt['input_sha256']!=b.gate.V4_SHA or sha(candidate)!=receipt['resource_sha256']:raise ValueError('Prior checkpoint mismatch')
        target=OUT/'prepared-inputs'/b.KEY;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(candidate.read_bytes());write(OUT/'prepared.json',receipt)
    transforms=dict(b.p.TRANSFORMS)
    transforms['MenuInventory']=lambda t:b.p.menu(t).replace('aiDiagnosticBuild:Boolean=false','aiDiagnosticBuild:Boolean=true')
    folder=OUT/('abc-'+str(len(list(OUT.glob('abc*')))+1).zfill(2))
    desired={name:fn(b.gate.one(name).read_text(encoding='utf-8-sig')) for name,fn in transforms.items()}
    working=source.read_bytes();before=b.BEFORE;selected=transforms;previous=None
    if (OUT/'prepared.json').exists():
        previous=json.loads((OUT/'prepared.json').read_text())
        checkpoint=OUT/'prepared-inputs'/b.KEY
        if previous['input_sha256']!=b.gate.V4_SHA or sha(checkpoint)!=previous['resource_sha256']:raise ValueError('Unverified incremental checkpoint')
        selected={name:(lambda text,replacement=text:replacement) for name,text in desired.items() if (Path(previous['abc'])/(name+'.as')).read_text(encoding='utf-8')!=text}
        if selected:working=checkpoint.read_bytes();before=Path(previous['abc'])/'after'
        else:selected=transforms
    data,compiled_changes=b.b.b.batch_compile(working,before,folder,selected)
    # Keep the complete source-to-v4 map even for a one-class incremental compile.
    changes=[]
    for name,text in desired.items():
        path=folder/(name+'.as')
        if not path.exists():path.write_text(text,encoding='utf-8',newline='\n')
        changes.append(dict(class_name=name,input_sha256=hashlib.sha256(b.gate.one(name).read_text(encoding='utf-8-sig').encode()).hexdigest(),output_sha256=hashlib.sha256(text.encode()).hexdigest()))
    audit=b.b.b.m.b.audit
    if [(c,v) for c,v in audit.swf_tags(source.read_bytes())[2] if c!=82]!=[(c,v) for c,v in audit.swf_tags(data)[2] if c!=82]:raise ValueError('Non-code tags changed')
    target=OUT/'prepared-inputs'/b.KEY;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    after=folder/'after';after.mkdir(exist_ok=True);(after/'source.gfx').write_bytes(b.b.b.m.r.p.movie(data)[1]);b.b.b.m.b.export(after/'source.gfx',after)
    contracts=b.b.b.m.b.class_contracts(b.BEFORE/'scripts',after/'scripts')
    write(OUT/'prepared.json',dict(input_sha256=sha(source),resource_sha256=sha(target),abc=str(folder),changes=changes,compiled_classes=[r['class_name'] for r in compiled_changes],incremental_from=previous['resource_sha256'] if previous and before!=b.BEFORE else None,contracts=contracts,native_validation=False,game_execution=False))
def package():
    if b.freeze()!=json.loads((OUT/'protected-inputs.json').read_text()):raise ValueError('Protected inputs changed')
    compiler=json.loads((ROOT/'build/approved-inventory-runtime-diagnostic-r5-scripts/receipt.json').read_text())
    if sha(b.SCRIPT)!=compiler['source_sha256'] or [r['exit_code'] for r in compiler['results']]!=[0,0]:raise ValueError('Diagnostic script compiler mismatch')
    prepared=json.loads((OUT/'prepared.json').read_text())
    transforms=dict(b.p.TRANSFORMS)
    transforms['MenuInventory']=lambda t:b.p.menu(t).replace('aiDiagnosticBuild:Boolean=false','aiDiagnosticBuild:Boolean=true')
    for name,fn in transforms.items():
        expected=fn(b.gate.one(name).read_text(encoding='utf-8-sig'))
        if (Path(prepared['abc'])/(name+'.as')).read_text(encoding='utf-8')!=expected:raise ValueError('Compiled/source mismatch '+name)
    for row in compiler['results']:
        if sha(ROOT/'build/approved-inventory-runtime-diagnostic-r5-scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Compiler blob changed')
    data=(OUT/'prepared-inputs'/b.KEY).read_bytes()
    if hashlib.sha256(data).hexdigest()!=prepared['resource_sha256']:raise ValueError('Prepared resource changed')
    standard=load('native-zlib-control');module=b.b;original=module.zlib.compress
    packout=OUT/('package-'+Path(prepared['abc']).name)
    packout.mkdir();packinput=packout/'prepared-inputs'/b.KEY;packinput.parent.mkdir(parents=True);packinput.write_bytes(data)
    try:
        module.OUT=packout;module.zlib.compress=standard.compress;module.reconstruct(diagnostic_only=True)
    finally:module.zlib.compress=original
    prefix='Mods/modApprovedInventoryUnifiedP1/content/'
    members={prefix+n:(packout/'packed'/n).read_bytes() for n in ('blob0.bundle','metadata.store')}
    members[prefix+'scripts/local/approvedInventory.ws']=b.SCRIPT.read_bytes()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(members.items()):z.writestr(name,value)
    DEPLOY.mkdir(exist_ok=True);path=DEPLOY/'Approved-Inventory-P1-DIAGNOSTIC-r5-private.zip'
    if path.exists():raise ValueError('Preserve existing diagnostic archive')
    path.write_bytes(stream.getvalue())
    with zipfile.ZipFile(path) as z:
        if z.testzip() or {n:z.read(n) for n in z.namelist()}!=members:raise ValueError('ZIP mismatch')
    if b.b.b.m.b.bars.extract(packout/'packed/blob0.bundle',b.KEY)!=data:raise ValueError('Extraction mismatch')
    receipt=dict(prepared,zip_path=str(path),zip_sha256=sha(path),annotation_sha256=sha(b.SCRIPT),compiler=compiler,reconstruction=json.loads((packout/'reconstruction.json').read_text()),native_cook_attempted=False,native_candidate_validated=False,game_execution=False,manual_opt_in_only=True)
    write(OUT/'receipt.json',receipt);print(path);print(receipt['zip_sha256'])
def main():
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul only')
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','package']);a=ap.parse_args();globals()[a.stage]()
if __name__=='__main__':main()
