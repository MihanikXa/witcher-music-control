"""Official single-resource pipeline and multi-atlas contract gates."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


font=load('verify-font-asset');field=load('prepare-field-folio');probe=load('probe-field-folio-export')
audit=font.audit;KEY=field.KEY


def critical(data):
    version,header,tags=font.movie_tags(data)
    return version,header,[(c,b) for c,b in tags if c not in field.IMAGE_TAGS]


def textures(data):
    cs=font.native.chunks(data)
    if [c['class_name'] for c in cs]!=['CSwfResource','CSwfTexture','CSwfTexture'] or not all(c['crc_valid'] for c in cs):
        raise ValueError('Expected resource and two valid texture chunks')
    if cs[0]['properties']['textures']['value']!='020000000200000003000000':
        raise ValueError('Texture handles lost or changed')
    tags=audit.swf_tags(data)[2];references={};result={}
    for code,b in tags:
        if code==1009:
            at=11+b[10];n=b[at];name=b[at+1:at+1+n].decode('ascii')
            references[struct.unpack_from('<H',b)[0]]=name
    for c in cs[1:]:
        props=c['properties'];name=props['linkageName']['value']
        ids=[i for i,n in references.items() if n==name]
        if len(ids)!=1 or props['textureGroup']['value']!='GUIWithAlpha' or props['compression']['value']!='TCM_DXTAlpha':
            raise ValueError('Texture linkage or configuration changed')
        resident,count,w,h,pitch,size,alignment=struct.unpack_from('<7I',c['tail'])
        pixels=c['tail'][28:]
        if resident!=0 or count!=1 or size!=len(pixels) or size!=((w+3)//4)*((h+3)//4)*16 or w!=props['width']['value'] or h!=props['height']['value']:
            raise ValueError('Invalid DXT5 mip metadata')
        suffix=name[name.rindex('_i'):]
        result[suffix]=dict(id=ids[0],width=w,height=h,pitch=pitch,alignment=alignment,pixels=pixels,
                            rectangles=[struct.unpack('<6H',b) for t,b in tags if t==1008 and struct.unpack_from('<H',b,2)[0]==ids[0]])
    if len(result)!=2:raise ValueError('Both atlas dependencies required')
    return cs,result


def compare_textures(original,candidate):
    _,a=textures(original);_,b=textures(candidate);report=[]
    if set(a)!=set(b):raise ValueError('Atlas keys changed')
    for key,x in a.items():
        y=b[key]
        if any(x[k]!=y[k] for k in ('width','height','pitch','alignment')):
            raise ValueError('Cooked texture metadata changed')
        if [r[:1]+r[2:] for r in x['rectangles']]!=[r[:1]+r[2:] for r in y['rectangles']]:
            raise ValueError('Subimage bounds or character IDs changed')
        w,h=x['width'],x['height'];p=font.native.bc3(x['pixels'],w,h);q=font.native.bc3(y['pixels'],w,h)
        visible=[i for i,(s,t) in enumerate(zip(p,q)) if s[3]!=t[3] or ((s[3] or t[3]) and s[:3]!=t[:3])]
        # The second external image has no DefineSubImage tag: its full footprint is used.
        rects=x['rectangles'] or [(0,x['id'],0,0,w,h)]
        used=sum(any(max(0,x1-1)<=i%w<min(w,x2+1) and max(0,y1-1)<=i//w<min(h,y2+1)
                     for _,_,x1,y1,x2,y2 in rects) for i in visible)
        report.append(dict(atlas=key,width=w,height=h,full_visible_pixel_differences=len(visible),
                           used_and_one_pixel_border_differences=used,
                           transparent_rgb_differences=sum(s[3]==t[3]==0 and s[:3]!=t[:3] for s,t in zip(p,q)),
                           compressed_payload_identical=x['pixels']==y['pixels'],
                           original_sha256=audit.sha(x['pixels']),candidate_sha256=audit.sha(y['pixels'])))
    return report


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',type=Path,required=True)
    ap.add_argument('--expected-swf',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--runner',type=Path,default=ROOT/'build/npc-state-expanded');ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();out=font.private_path(a.out);runner=font.private_path(a.runner)
    saved=a.resource.resolve().read_bytes();swf=a.expected_swf.resolve().read_bytes();baseline=a.baseline.resolve().read_bytes()
    if critical(saved)!=critical(swf):raise ValueError('Saved resource does not match intended source')
    if out.exists() or (runner/'projects').exists() or (runner/'bin/x64_RedKit/editor.exe').exists():raise ValueError('Fresh output and private CLI runner required')
    exe=runner/'bin/x64_RedKit/wcc_lite.exe'
    if audit.sha(exe.read_bytes())!=font.COMPILER_SHA:raise ValueError('Current verified compiler required')
    out.mkdir();commands=[]
    def run(label,args):
        cmd=[str(exe),*args]
        p=subprocess.run(cmd,cwd=exe.parent,capture_output=True,timeout=60)
        (out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
        log=(exe.parent.parent/'wcc.log').read_text(errors='replace');(out/(label+'.full.log')).write_text(log)
        asserts=[s for s in log.splitlines() if '[Error][Assert]' in s]
        commands.append(dict(label=label,command=cmd,exit_code=p.returncode,assertions=asserts))
        (out/'commands.json').write_text(json.dumps(commands,indent=2))
        if p.returncode or any(not any(x in s for x in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for s in asserts):
            raise ValueError('Official command failed or new assertion: '+label)
        return log
    with font.mounted_input(runner,out,a.resource.resolve(),key=KEY) as workspace:
        run('cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')])
        log=run('validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')])
        if 'Found 1 files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Single-resource validation failed')
        cooked=(out/'cooked'/KEY).read_bytes()
        if critical(cooked)!=critical(swf):raise ValueError('Cooked font, field or other nonimage contracts changed')
        cs,_=textures(cooked)
        names=[audit.font_info(c,b)['name'] for c,b in audit.swf_tags(cooked)[2] if c==75]
        desc=bytes.fromhex(cs[0]['properties']['fonts']['value'])
        if struct.unpack_from('<I',desc)[0]!=len(names) or any(name.encode() not in desc for name in names):raise ValueError('Official font descriptor registration incomplete')
        reports=compare_textures(baseline,cooked);(out/'textures.json').write_text(json.dumps(reports,indent=2))
        if any(r['used_and_one_pixel_border_differences'] for r in reports):raise ValueError('Visible image footprints changed; not packaging')
        dest=out/'pack-input'/KEY;dest.parent.mkdir(parents=True);dest.write_bytes(cooked)
        run('pack',['pack','-dir='+str(out/'pack-input'),'-outdir='+str(out/'packed'),'-compression=ZLIB'])
        log=run('metadata',['metadatastore','-path='+str(out/'packed')])
        if 'Loaded 1 bundles with 1 entries' not in log:raise ValueError('Official metadata inventory differs')
        bundle=out/'packed/blob0.bundle';entries=list(audit.entries(bundle))
        if len(entries)!=1 or entries[0]['resource']!=KEY or entries[0]['codec']!=1:raise ValueError('Bundle scope differs')
        e=entries[0]
        with bundle.open('rb') as f:
            f.seek(e['offset']);recovered=zlib.decompress(f.read(e['packed']))
        if recovered!=cooked:raise ValueError('Re-extraction differs')
        (out/'reextracted.redswf').write_bytes(recovered)
        metadata=(out/'packed/metadata.store').read_bytes()
        if KEY.replace('/','\\').encode() not in metadata:raise ValueError('Canonical metadata key missing')
    if a.resource.read_bytes()!=saved or a.expected_swf.read_bytes()!=swf or a.baseline.read_bytes()!=baseline:raise ValueError('Inputs changed')
    receipt=dict(resource_key=KEY,source_path=str(a.resource.resolve()),source_sha256=audit.sha(saved),
                 expected_swf=str(a.expected_swf.resolve()),expected_swf_sha256=audit.sha(swf),
                 baseline_path=str(a.baseline.resolve()),baseline_sha256=audit.sha(baseline),
                 commands=commands,compiler_sha256=audit.sha(exe.read_bytes()),cooked_sha256=audit.sha(cooked),
                 bundle_sha256=audit.sha(bundle.read_bytes()),metadata_sha256=audit.sha(metadata),
                 textures=reports,font_definitions_identical_to_source=True,official_font_descriptors_present=True,
                 sources_unchanged=True,runner_workspace_restored=True,toolchain_copied=False,
                 exact_reextraction=True,offline_pipeline_verified=True,runtime_tested=False,package_path=None)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
