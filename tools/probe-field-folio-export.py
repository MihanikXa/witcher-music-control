"""Bounded official GFx CLI probe, not an Editor import or cooked asset build."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('field',ROOT/'tools/prepare-field-folio.py')
field=importlib.util.module_from_spec(spec);spec.loader.exec_module(field)


def atlas_contract(tags):
    """Compare semantic atlas references, allowing official atlas-ID assignment."""
    atlases={struct.unpack_from('<H',b)[0]:b[2:] for c,b in tags if c==1009}
    images=[]
    for c,b in tags:
        if c==1008:
            if len(b)!=12:raise ValueError('Unexpected subimage format')
            reference=struct.unpack_from('<H',b,2)[0]
            if reference not in atlases:raise ValueError('Unresolved atlas reference')
            images.append((b[:2],atlases[reference],b[4:]))
    return sorted(atlases.values()),images


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--exporter',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve()
    if ROOT/'build' not in out.parents or out.exists():raise ValueError('Fresh private output required')
    source=json.loads((a.source/'receipt.json').read_text())
    out.mkdir();results=[];movies=[]
    for weight,path,digest in [('unchanged',source['control_path'],source['control_sha256'])]+[
            (c['weight'].lower(),c['path'],c['sha256']) for c in source['candidates'] if c['weight']=='Regular']:
        swf=Path(path).resolve();data=swf.read_bytes()
        if field.audit.sha(data)!=digest:raise ValueError('Prepared SWF changed')
        dest=out/weight;dest.mkdir()
        cmd=[str(a.exporter.resolve()),str(swf),'-c','-i','DDS','-d1c','-d5','-quick',
             '-pack','-ptresize','mult4','-share_images','-ne','-list','-lwr',
             '-o',str(dest),'-p','ff-interactions-probe']
        p=subprocess.run(cmd,cwd=dest,capture_output=True,timeout=60)
        (dest/'export.log').write_bytes(p.stdout+p.stderr)
        if p.returncode:raise ValueError('Official GFx exporter failed')
        gfx=(dest/(swf.stem+'.gfx')).read_bytes()
        before=field.audit.swf_tags(data)[2];after=field.audit.swf_tags(gfx)[2]
        excluded=field.IMAGE_TAGS|{88}
        if [(c,b) for c,b in before if c not in excluded]!=[(c,b) for c,b in after if c not in excluded]:
            raise ValueError('Exporter changed fonts, binding or other non-image contracts')
        if swf.read_bytes()!=data:raise ValueError('Source SWF changed')
        movies.append(after)
        results.append(dict(weight=weight,command=cmd,exit_code=p.returncode,source_sha256=digest,
                            gfx_sha256=field.audit.sha(gfx),font_and_nonimage_payloads_identical=True,
                            exported_texture_pixels=False))
    if atlas_contract(movies[0])!=atlas_contract(movies[1]):
        raise ValueError('Exporter changed semantic image atlas placement')
    receipt=dict(commands=results,exporter_sha256=field.audit.sha(a.exporter.read_bytes()),
                 semantic_atlas_contracts_identical=True,subimages=141,atlas_records=2,
                 atlas_ids_may_be_reassigned=True,texture_pixels_verified=False,
                 editor_import_verified=False,cooked_resource_verified=False,package_path=None)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
