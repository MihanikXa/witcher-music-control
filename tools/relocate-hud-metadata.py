"""Bounded relocation of a native metadata table for identical self-contained keys.

Requires a second independently native-generated control: reproduce every byte
of its metadata before generating the candidate. Not a general metadata writer.
No native command success is asserted by this tool.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-ink-hud-batch.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)

def relocate(template,old,new,old_length,new_length):
    if [e['resource'] for e in old]!=[e['resource'] for e in new]:raise ValueError('Identical key order required')
    result=bytearray(template);seen={};patches=[]
    def patch(pos,before,after,label):
        if struct.unpack_from('<I',template,pos)[0]!=before:raise ValueError('Unexpected table value')
        if pos in seen and seen[pos]!=after:raise ValueError('Ambiguous table value')
        seen[pos]=after;struct.pack_into('<I',result,pos,after);patches.append(dict(offset=pos,before=before,after=after,label=label))
    if template[:8]!=bytes.fromhex('0356544d07000000'):raise ValueError('Only observed metadata version supported')
    for a,c in zip(old,new):
        for key,expected in (('size',1+(a['size']==max(e['size'] for e in old))),('packed',2+(a['packed']==max(e['packed'] for e in old))),('offset',1+(a['offset']==min(e['offset'] for e in old)))):
            needle=struct.pack('<I',a[key]);positions=[i for i in range(len(template)-3) if template[i:i+4]==needle]
            if len(positions)!=expected:raise ValueError('Unexpected native field multiplicity: '+a['resource']+' '+key)
            for pos in positions:patch(pos,a[key],c[key],a['resource']+' '+key)
    # Native header maxima, even if a different movie becomes the maximum.
    struct.pack_into('<II',result,8,max(e['packed'] for e in new),max(e['size'] for e in new))
    old_data=((old_length+15)//16*16)-min(e['offset'] for e in old)
    new_data=((new_length+15)//16*16)-min(e['offset'] for e in new)
    needle=struct.pack('<I',old_data);positions=[i for i in range(len(template)-3) if template[i:i+4]==needle]
    if len(positions)!=1:raise ValueError('Unique aligned bundle length required')
    patch(positions[0],old_data,new_data,'aligned bundle data length')
    return bytes(result),patches

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--verify-existing',action='store_true');a=ap.parse_args();out=a.out.resolve();b.font.private_path(out)
    source=ROOT/'build/ink-hud-refinement-v2-release-final/packed';control=ROOT/'build/ink-hud-v3-diagnostic-final/packed';target=out/'packed'
    old=list(b.audit.entries(source/'blob0.bundle'));native_control=list(b.audit.entries(control/'blob0.bundle'));new=list(b.audit.entries(target/'blob0.bundle'))
    template=(source/'metadata.store').read_bytes()
    reproduced,_=relocate(template,old,native_control,(source/'blob0.bundle').stat().st_size,(control/'blob0.bundle').stat().st_size)
    if reproduced!=(control/'metadata.store').read_bytes():raise ValueError('Independent native control is not reproduced byte for byte')
    for entry in new:
        data=b.bars.extract(target/'blob0.bundle',entry['resource'])
        chunks=b.font.native.chunks(data)
        if chunks[0]['class_name']!='CSwfResource':raise ValueError('Only self-contained movies supported')
        for i in (2,5,6,7,8,9):
            if struct.unpack_from('<III',data,40+i*12)[1]:raise ValueError('Imports/buffers/dependency tables require native regeneration')
    candidate,patches=relocate(template,old,new,(source/'blob0.bundle').stat().st_size,(target/'blob0.bundle').stat().st_size)
    if (target/'metadata.store').exists():
        if not a.verify_existing or (target/'metadata.store').read_bytes()!=candidate:raise ValueError('Do not overwrite metadata; existing bytes must match')
    else:(target/'metadata.store').write_bytes(candidate)
    b.write_json(out/'metadata-relocation.json',dict(method='verified relocation of existing native table',native_v3_metadatastore_passed=False,native_control_byte_identical=True,source_metadata_sha256=b.audit.sha(template),native_control_metadata_sha256=b.audit.sha(reproduced),output_metadata_sha256=b.audit.sha(candidate),source_bundle_sha256=b.fallback.sha(source/'blob0.bundle'),control_bundle_sha256=b.fallback.sha(control/'blob0.bundle'),target_bundle_sha256=b.fallback.sha(target/'blob0.bundle'),identical_ordered_keys=True,no_native_import_buffer_dependency_tables=True,patches=patches))
    print('Native control reproduced exactly; candidate metadata relocated',b.audit.sha(candidate))

if __name__=='__main__':main()
