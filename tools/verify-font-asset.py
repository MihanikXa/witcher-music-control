"""Official single English font resource cook/validate/bundle round trip.

Reuses one private runner, temporarily mounting a single saved resource.
Never creates a CR2W header, imports SWF, edits a source project or deploys.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import zlib
from contextlib import contextmanager

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('native',ROOT/'tools/compare-native-npc.py')
native=importlib.util.module_from_spec(spec); spec.loader.exec_module(native)
audit=native.audit
KEY='gameplay/gui_new/swf/witcher3/fonts_en.redswf'
COMPILER_SHA='9f448e0c8b9ea1ea803d0ae543f2fcd6e905088b8b71f54da2bff22c6cf318fc'
BASELINE_SHA='a1223e1a26e0c541a69cb1c6ad8bffbd70c074f1d4603193758b2bf220e95f81'


def private_path(path):
    path=path.resolve()
    if ROOT/'build' not in path.parents:
        raise ValueError('Private build path required')
    return path


def workspace_inventory(path):
    return {str(p.relative_to(path)): audit.sha(p.read_bytes())
            for p in path.rglob('*') if p.is_file()} if path.exists() else None


@contextmanager
def mounted_input(runner, out, resource):
    runner=private_path(runner); out=private_path(out)
    if runner in out.parents or out in runner.parents:
        raise ValueError('Runner and output must be separate directories')
    workspace=runner/'bin/workspace'
    backup=runner/'bin/workspace-font-backup'
    preserved=out/'staged-workspace'
    if backup.exists() or preserved.exists() or workspace.is_symlink() or workspace.is_junction():
        raise ValueError('Workspace mount is not safe or another build is active')
    if workspace.exists() and any(p.is_symlink() or p.is_junction() for p in workspace.rglob('*')):
        raise ValueError('Workspace contains linked paths')
    before=workspace_inventory(workspace)
    if workspace.exists(): workspace.rename(backup)
    try:
        dest=workspace/KEY; dest.parent.mkdir(parents=True)
        shutil.copy2(resource,dest)
        yield workspace
    finally:
        if workspace.exists(): workspace.rename(preserved)
        if backup.exists(): backup.rename(workspace)
        if workspace_inventory(workspace)!=before:
            raise ValueError('Original private runner workspace was not restored')


def movie_tags(data):
    offset, _, tags = audit.swf_tags(data)
    raw = data[offset:]
    body = zlib.decompress(raw[8:]) if raw[:1] == b'C' else raw[8:]
    rect_size = (5 + 4 * (body[0] >> 3) + 7) // 8
    # Also retain movie version, stage bounds, frame rate and frame count.
    return raw[3], body[:rect_size+4], [(c,b) for c,b in tags if c not in (1000,88)]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runner',type=Path,default=ROOT/'build/npc-state-expanded',
                    help='Existing private CLI runner; no installation/depot copies')
    ap.add_argument('--resource',type=Path,required=True)
    ap.add_argument('--expected-swf',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    resource=a.resource.resolve(); expected=a.expected_swf.resolve()
    source=resource.read_bytes(); swf=expected.read_bytes()
    if movie_tags(source)!=movie_tags(swf): raise ValueError('Saved font movie does not match intended SWF; no cooker executed')
    runner=private_path(a.runner); out=private_path(a.out)
    if out.exists(): raise ValueError('Fresh private output required')
    if (runner/'projects').exists() or (runner/'bin/x64_RedKit/editor.exe').exists():
        raise ValueError('Use a private CLI runner, not an Editor environment')
    exe=runner/'bin/x64_RedKit/wcc_lite.exe'
    if audit.sha(exe.read_bytes())!=COMPILER_SHA: raise ValueError('Current verified compiler required')
    if shutil.disk_usage(out.parent).free < 32*1024**2: raise ValueError('At least 32 MiB free space required')
    out.mkdir()
    with mounted_input(runner,out,resource) as workspace:
        receipt=execute_pipeline(out,resource,expected,source,swf,exe,workspace)
    receipt.update(runner_path=str(runner),runner_workspace_restored=True,toolchain_copied=False)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


def execute_pipeline(out,resource,expected,source,swf,exe,workspace):
    commands=[]

    def run(label,args):
        cmd=[str(exe),*args]
        try:
            p=subprocess.run(cmd,cwd=exe.parent,capture_output=True,timeout=60)
        except subprocess.TimeoutExpired as failure:
            (out/(label+'.stdout.log')).write_bytes((failure.stdout or b'')+(failure.stderr or b''))
            commands.append(dict(label=label,command=cmd,exit_code=None,timeout_seconds=60))
            (out/'commands.json').write_text(json.dumps(commands,indent=2))
            raise
        (out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
        log=(exe.parent.parent/'wcc.log').read_text(errors='replace')
        (out/(label+'.full.log')).write_text(log)
        assertions=[s for s in log.splitlines() if '[Error][Assert]' in s]
        commands.append(dict(label=label,command=cmd,exit_code=p.returncode,assertions=assertions))
        (out/'commands.json').write_text(json.dumps(commands,indent=2))
        if p.returncode or any('diskFile.cpp:2633' in s for s in assertions):
            raise ValueError('Official command failed/resource-state assertion: '+label)
        return log

    run('cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')])
    log=run('validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')])
    if 'Errors found in 0 resources:' not in log or 'Found 1 files to validate' not in log:
        raise ValueError('Single resource validation failed')
    cooked=(out/'cooked'/KEY).read_bytes()
    if movie_tags(cooked)!=movie_tags(swf): raise ValueError('Cooked font contracts changed')
    chunks=native.chunks(cooked)
    if [c['class_name'] for c in chunks]!=['CSwfResource'] or not all(c['crc_valid'] for c in chunks):
        raise ValueError('Unexpected font resource structure/CRC')
    baseline=(ROOT/'build/gentium-font-source-final/fonts_en.redswf').read_bytes()
    if audit.sha(baseline)!=BASELINE_SHA: raise ValueError('Verified runtime font baseline required')
    if chunks[0]['properties'].get('fonts')!=native.chunks(baseline)[0]['properties'].get('fonts'):
        raise ValueError('Runtime font registration descriptors changed')
    linkage=chunks[0]['properties']['linkageName']['value']
    exporters=[b for c,b in audit.swf_tags(cooked)[2] if c==1000]
    if len(exporters)!=1 or not linkage.endswith('.gfx') or linkage[:-4].encode() not in exporters[0]:
        raise ValueError('Official resource linkage and movie exporter descriptor disagree')
    # The official cooker omits the empty default array for this font library.
    textures=chunks[0]['properties'].get('textures')
    if textures is not None and textures['value']!='00000000':
        raise ValueError('Expected no embedded textures')
    if any(c in (1008,1009) for c,b in audit.swf_tags(cooked)[2]):
        raise ValueError('Unexpected bitmap dependencies')
    packed_input=out/'pack-input'/KEY; packed_input.parent.mkdir(parents=True)
    packed_input.write_bytes(cooked)
    run('pack',['pack','-dir='+str(out/'pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'])
    log=run('metadata',['metadatastore','-path='+str(out/'packed')])
    if 'Loaded 1 bundles with 1 entries' not in log: raise ValueError('Metadata inventory mismatch')
    bundle=out/'packed/blob0.bundle'
    entries=list(audit.entries(bundle))
    if len(entries)!=1 or entries[0]['resource']!=KEY or entries[0]['codec']!=1:
        raise ValueError('Incorrect bundle entry')
    e=entries[0]
    with bundle.open('rb') as f:
        f.seek(e['offset']); recovered=zlib.decompress(f.read(e['packed']))
    if recovered!=cooked: raise ValueError('Re-extraction mismatch')
    (out/'reextracted.redswf').write_bytes(recovered)
    metadata=(out/'packed/metadata.store').read_bytes()
    if KEY.replace('/','\\').encode() not in metadata: raise ValueError('Metadata key missing')
    if resource.read_bytes()!=source or expected.read_bytes()!=swf: raise ValueError('Source changed')
    receipt=dict(resource_key=KEY,source_path=str(resource),source_sha256=audit.sha(source),
                 expected_swf=str(expected),expected_swf_sha256=audit.sha(swf),compiler_sha256=audit.sha(exe.read_bytes()),
                 commands=commands,sources_unchanged=True,cooked_sha256=audit.sha(cooked),cooked_bytes=len(cooked),
                 font_tags_identical_to_source=True,chunk_crc_valid=True,texture_array_empty=True,
                 runtime_font_descriptors_identical=True,exporter_linkage_consistent=True,linkage_name=linkage,
                 bundle_sha256=audit.sha(bundle.read_bytes()),metadata_sha256=audit.sha(metadata),
                 entry=e,exact_reextraction=True,offline_build_verified=True,runtime_tested=False,package_path=None,
                 metadata_validation='official producer and single-entry key checked; independent store consumer untested')
    return receipt


if __name__=='__main__': main()
