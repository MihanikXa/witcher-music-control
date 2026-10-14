"""Bounded diagnostic-only POTATO70 reconstruction, checked against native controls.
Never a substitute claim for native cooking/validation. Same 22 self-contained keys.
"""
import argparse,struct,zlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-ink-hud-batch.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)

def reconstruct(template,files):
 raw=template.read_bytes();entries=list(b.audit.entries(template));table=struct.unpack_from('<I',raw,16)[0]
 if len(entries)!=22 or table!=22*304 or raw[:8]!=b'POTATO70':raise ValueError('Only exact native 22-key 304-byte table supported')
 if set(files)!={e['resource'] for e in entries}:raise ValueError('No new/reordered keys allowed')
 if min(e['offset'] for e in entries)!=32+table or max(e['offset']+e['packed'] for e in entries)!=len(raw):raise ValueError('Opaque gaps/footer unsupported')
 data=bytearray(raw[:32+table])
 for index,e in sorted(enumerate(entries),key=lambda pair:pair[1]['offset']):
  if e['codec']!=1:raise ValueError('Only observed ZLIB codec')
  source=files[e['resource']];packed=zlib.compress(source,9)
  while len(data)%16:data.append(0)
  offset=len(data);data.extend(packed)
  struct.pack_into('<QIIII',data,32+index*304+272,offset,len(source),len(packed),zlib.crc32(source),1)
 struct.pack_into('<I',data,8,(len(data)+15)//16*16)
 return bytes(data)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();b.font.private_path(out)
 controls=[]
 for directory in ('ink-hud-refinement-v2-release-final','ink-hud-v3-diagnostic-final','ink-radial-trace-d1-final'):
  control=ROOT/'build'/directory/'packed/blob0.bundle';files={e['resource']:b.bars.extract(control,e['resource']) for e in b.audit.entries(control)}
  reproduced=reconstruct(control,files)
  if reproduced!=control.read_bytes():raise ValueError('Native control not reproduced exactly '+directory)
  controls.append(dict(path=str(control),sha256=b.audit.sha(reproduced),byte_identical=True))
 template=ROOT/'build/ink-radial-trace-d1-final/packed/blob0.bundle';files={e['resource']:(out/'prepared-inputs'/e['resource']).read_bytes() for e in b.audit.entries(template)}
 for key,source in files.items():
  chunks=b.font.native.chunks(source)
  if chunks[0]['class_name']!='CSwfResource':raise ValueError('Unexpected native class')
  for index in (2,5,6,7,8,9):
   if struct.unpack_from('<III',source,40+index*12)[1]:raise ValueError('Dependencies require native regeneration')
  b.audit.swf_tags(source)
 packed=out/'packed';packed.mkdir(exist_ok=True);target=packed/'blob0.bundle'
 if target.exists():raise ValueError('Do not overwrite')
 target.write_bytes(reconstruct(template,files))
 for key,data in files.items():
  if b.bars.extract(target,key)!=data:raise ValueError('Exact extraction mismatch')
 b.write_json(out/'bundle-reconstruction.json',dict(diagnostic_only=True,native_candidate_cook_validated=False,method='bounded native-table reconstruction; ZLIB level 9; CRC32; 16-byte payload alignment',controls=controls,bundle_sha256=b.fallback.sha(target),all_resources_reextracted_exact=True))
 print('Three native bundles reproduced byte-identically; diagnostic bundle reconstructed')
if __name__=='__main__':main()
