"""Official one-resource, no-bitmap subtitle control/candidate pipeline."""
import argparse
import json
from pathlib import Path
import subprocess
import shutil
import zlib
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pipeline',ROOT/'tools/verify-field-folio-asset.py')
pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)
font=pipeline.font;audit=pipeline.audit
KEY='gameplay/gui_new/swf/hud/hud_subtitles.redswf'


def structure(data):
    cs=font.native.chunks(data)
    if [c['class_name'] for c in cs]!=['CSwfResource'] or not all(c['crc_valid'] for c in cs):
        raise ValueError('Expected one valid subtitle resource chunk')
    props=cs[0]['properties']
    for name in ('textures','fonts'):
        if name in props and props[name]['value']!='00000000':raise ValueError('Unexpected '+name+' array')
    if any(c in (35,36,75,1008,1009) for c,b in audit.swf_tags(data)[2]):
        raise ValueError('Unexpected embedded font/bitmap dependency')
    linkage=props['linkageName']['value'];exporters=[b for c,b in audit.swf_tags(data)[2] if c==1000]
    if len(exporters)!=1 or not linkage.endswith('.gfx') or linkage[:-4].encode() not in exporters[0]:
        raise ValueError('Resource/movie linkage inconsistent')
    return dict(chunk_crc_valid=True,texture_array_empty=True,font_array_empty=True,
                exporter_linkage_consistent=True,linkage_name=linkage)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',type=Path,required=True)
    ap.add_argument('--expected-swf',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--runner',type=Path,default=ROOT/'build/npc-state-expanded')
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--control',action='store_true')
    ap.add_argument('--resume-metadata',action='store_true')
    ap.add_argument('--metadata-timeout',type=int,choices=(60,120),default=60);a=ap.parse_args()
    saved=a.resource.read_bytes();swf=a.expected_swf.read_bytes();baseline=a.baseline.read_bytes()
    structure(saved);structure(baseline)
    if pipeline.critical(saved)!=pipeline.critical(swf):raise ValueError('Saved subtitle does not match source')
    if a.control and pipeline.critical(swf)!=pipeline.critical(baseline):raise ValueError('Unchanged control differs')
    runner=font.private_path(a.runner);out=font.private_path(a.out);exe=runner/'bin/x64_RedKit/wcc_lite.exe'
    if (out.exists() and not a.resume_metadata) or (runner/'projects').exists() or (runner/'bin/x64_RedKit/editor.exe').exists():raise ValueError('Fresh output and private CLI runner required')
    if audit.sha(exe.read_bytes())!=font.COMPILER_SHA:raise ValueError('Current compiler required')
    if a.resume_metadata:
        old=json.loads((out/'commands.json').read_text())
        if [c['label'] for c in old]!=['cook','validate','pack','metadata'] or old[-1].get('timeout_seconds')!=60:
            raise ValueError('Only a bounded metadata-timeout resume is supported')
        if any(c['exit_code']!=0 or any(not any(s in x for s in ('depotDirectory.cpp:11','soundFileLoader.cpp:101'))
               for x in c['assertions']) for c in old[:3]):raise ValueError('Prior stages failed')
        for name in ('commands.json','metadata.stdout.log'):
            backup=out/(name+'.first-timeout')
            if backup.exists():raise ValueError('Metadata resume already attempted')
            shutil.copy2(out/name,backup)
        commands=old[:3];mount=out/'metadata-resume';mount.mkdir()
    else:out.mkdir();commands=[];mount=out
    def run(label,args):
        cmd=[str(exe),*args]
        timeout=a.metadata_timeout if label=='metadata' else 60
        try:p=subprocess.run(cmd,cwd=exe.parent,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as ex:
            (out/(label+'.stdout.log')).write_bytes((ex.stdout or b'')+(ex.stderr or b''))
            commands.append(dict(label=label,command=cmd,exit_code=None,timeout_seconds=timeout))
            (out/'commands.json').write_text(json.dumps(commands,indent=2));raise
        (out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
        log=(exe.parent.parent/'wcc.log').read_text(errors='replace');(out/(label+'.full.log')).write_text(log)
        asserts=[s for s in log.splitlines() if '[Error][Assert]' in s]
        commands.append(dict(label=label,command=cmd,exit_code=p.returncode,assertions=asserts))
        (out/'commands.json').write_text(json.dumps(commands,indent=2))
        if p.returncode or any(not any(x in s for x in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for s in asserts):
            raise ValueError('Official command failed or new assertion: '+label)
        return log
    with font.mounted_input(runner,mount,a.resource.resolve(),key=KEY) as workspace:
        if not a.resume_metadata:
            run('cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')])
            log=run('validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')])
        else:log=(out/'validate.full.log').read_text(errors='replace')
        if 'Found 1 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Single-resource validation failed')
        cooked=(out/'cooked'/KEY).read_bytes();info=structure(cooked)
        if pipeline.critical(cooked)!=pipeline.critical(swf):raise ValueError('Cooked movie contracts differ')
        if not a.resume_metadata:
            dest=out/'pack-input'/KEY;dest.parent.mkdir(parents=True);dest.write_bytes(cooked)
            run('pack',['pack','-dir='+str(out/'pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'])
        elif (mount.parent/'staged-workspace'/KEY).read_bytes()!=saved:
            raise ValueError('Original staged source changed')
        log=run('metadata',['metadatastore','-path='+str(out/'packed')])
        if 'Loaded 1 bundles with 1 entries' not in log:raise ValueError('Metadata inventory differs')
        bundle=out/'packed/blob0.bundle';entries=list(audit.entries(bundle))
        if len(entries)!=1 or entries[0]['resource']!=KEY or entries[0]['codec']!=1:raise ValueError('Bundle scope differs')
        e=entries[0]
        with bundle.open('rb') as f:f.seek(e['offset']);recovered=zlib.decompress(f.read(e['packed']))
        if recovered!=cooked:raise ValueError('Re-extraction differs')
        (out/'reextracted.redswf').write_bytes(recovered);metadata=(out/'packed/metadata.store').read_bytes()
        if KEY.replace('/','\\').encode() not in metadata:raise ValueError('Metadata key missing')
    if a.resource.read_bytes()!=saved or a.expected_swf.read_bytes()!=swf or a.baseline.read_bytes()!=baseline:raise ValueError('Inputs changed')
    receipt=dict(resource_key=KEY,source_path=str(a.resource.resolve()),source_sha256=audit.sha(saved),
        expected_swf=str(a.expected_swf.resolve()),expected_swf_sha256=audit.sha(swf),
        baseline_path=str(a.baseline.resolve()),baseline_sha256=audit.sha(baseline),
        compiler_sha256=font.COMPILER_SHA,commands=commands,cooked_sha256=audit.sha(cooked),
        bundle_sha256=audit.sha(bundle.read_bytes()),metadata_sha256=audit.sha(metadata),control=a.control,
        sources_unchanged=True,runner_workspace_restored=True,exact_reextraction=True,
        offline_pipeline_verified=True,runtime_tested=False,
        metadata_resumed_after_timeout=a.resume_metadata,metadata_timeout_seconds=a.metadata_timeout,**info)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
