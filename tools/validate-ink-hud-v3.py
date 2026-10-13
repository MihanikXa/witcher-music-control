"""Independent post-build checks of private v3 movie contracts and shapes."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('v3',ROOT/'tools/build-ink-hud-v3.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
b=v.b

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
    receipt=json.loads((out/'receipt.json').read_text());parent=json.loads((v.V2/'receipt.json').read_text());results={}
    for key,contract in receipt['movie_contracts'].items():
        data=(out/'pack-input'/key).read_bytes();old=(v.V2/'pack-input'/key).read_bytes()
        if b.audit.sha(data)!=receipt['resource_hashes'][key]:raise ValueError('Output resource changed')
        if key.endswith('hud_enemyfocus.redswf'):continue
        tags=b.audit.swf_tags(data)[2];before=b.audit.swf_tags(old)[2]
        original=v.v.retail(key,out)[0] if key.endswith('hud_iteminfo.redswf') else (v.V2/'source-inputs'/key).read_bytes()
        original_tags=b.audit.swf_tags(original)[2]
        if [(c,p) for c,p in tags if c in (1008,1009)]!=[(c,p) for c,p in original_tags if c in (1008,1009)]:raise ValueError('Original bitmap/atlas mapping not restored')
        image_names={}
        for c,p in original_tags:
            if c==1009:
                pos=11+p[10];image_names[struct.unpack_from('<H',p)[0]]=p[pos+1:pos+1+p[pos]].decode('ascii')
        original_chunks=b.font.native.chunks(original);new_chunks=b.font.native.chunks(data)
        if [c['properties'] for c in original_chunks]!=[c['properties'] for c in new_chunks]:raise ValueError('Original native properties/texture handles differ')
        xbox_ids={g['bitmap_id'] for g in contract['glyphs']};protected=0
        for c,p in original_tags:
            if c!=1008:continue
            cid,img,x1,y1,x2,y2=struct.unpack('<6H',p)
            if cid in xbox_ids:continue
            index=next(i for i,ch in enumerate(original_chunks) if ch['properties'].get('linkageName',{}).get('value')==image_names[img])
            width=original_chunks[index]['properties']['width']['value'];a=original_chunks[index]['tail'][28:];d=new_chunks[index]['tail'][28:]
            for by in range(y1//4,(y2+3)//4):
                for bx in range(x1//4,(x2+3)//4):
                    offset=(by*((width+3)//4)+bx)*16
                    if a[offset:offset+16]!=d[offset:offset+16]:raise ValueError('Non-Xbox image compression block changed')
                    protected+=1
        for codes in ({82},{48,75,57,71},{76}):
            if [(c,p) for c,p in tags if c in codes]!=[(c,p) for c,p in before if c in codes]:raise ValueError('ABC/font/export mismatch')
        if any(c==1009 and struct.unpack_from('<H',p)[0]==65534 for c,p in tags):raise ValueError('Extra atlas remains')
        folder=out/'independent-shapes'/Path(key).stem;folder.mkdir(parents=True,exist_ok=True)
        gfx=out/'vectors'/Path(key).stem/'final.gfx'
        proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-format','shape:svg','-export','shape',str(folder),str(gfx)],capture_output=True,timeout=90)
        (folder/'export.log').write_bytes(proc.stdout+proc.stderr)
        if proc.returncode:raise ValueError('SVG serializer failed')
        count=0
        for glyph in contract['glyphs']:
            if glyph['shape_id'] is None:continue
            svg=folder/(str(glyph['shape_id'])+'.svg');tree=ET.parse(svg).getroot()
            paths=list(tree.iter('{http://www.w3.org/2000/svg}path'))
            if not paths or any(p.get('fill') not in ('#141718','#efe3ce','#EFE3CE') or not p.get('d') for p in paths):raise ValueError('Invalid solid vector contour')
            if any('Gradient' in n.tag or n.tag.endswith('image') for n in tree.iter()):raise ValueError('Glyph depends on bitmap or gradient')
            if tree.get('width')!=str(float(glyph['width']))+'px' or tree.get('height')!=str(float(glyph['height']))+'px':raise ValueError('Bounds changed')
            count+=1
        results[key]=dict(independent_solid_shape_svg_count=count,abc_fonts_exports_exact=True,no_added_atlas=True,non_xbox_compression_blocks_verified=protected,original_bitmap_links_and_native_properties_exact=True)
    for key in receipt['unchanged_keys']:
        if receipt['resource_hashes'][key]!=parent['resource_hashes'][key]:raise ValueError('Unchanged key differs')
    if b.bars.snapshot(v.v.GAME,v.v.SETTINGS)!=json.loads((out/'live-before.json').read_text()):raise ValueError('Live inputs changed')
    b.write_json(out/'independent-validation.json',dict(resources=results,live_snapshot_unchanged=True))
    print('Independent V3 validation passed',sum(x['independent_solid_shape_svg_count'] for x in results.values()),'shapes')

if __name__=='__main__':main()
