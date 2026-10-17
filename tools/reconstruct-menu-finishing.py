"""Fail-closed 40-key reconstruction after WCC startup failure.

Must reproduce both native control bundles and independently changed metadata
exactly. Does NOT confer native cook/validate/pack/metadatastore success.
"""
import copy,importlib.util,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
build=load('build-menu-finishing');m=load('relocate-inventory-metadata');b=build.b

def bundle(template,files):
 raw=template.read_bytes();entries=list(b.m.b.audit.entries(template));table=struct.unpack_from('<I',raw,16)[0]
 if len(entries)!=40 or table!=40*304 or raw[:8]!=b'POTATO70' or set(files)!={e['resource'] for e in entries}:raise ValueError('Only native same 40-key layout allowed')
 if min(e['offset'] for e in entries)!=32+table or max(e['offset']+e['packed'] for e in entries)!=len(raw):raise ValueError('Unobserved bundle gaps/tail')
 result=bytearray(raw[:32+table])
 for index,e in sorted(enumerate(entries),key=lambda pair:pair[1]['offset']):
  if e['codec']!=1:raise ValueError('Only native ZLIB supported')
  data=files[e['resource']];packed=zlib.compress(data,9)
  while len(result)%16:result.append(0)
  offset=len(result);result.extend(packed)
  struct.pack_into('<QIIII',result,32+index*304+272,offset,len(data),len(packed),zlib.crc32(data),1)
 struct.pack_into('<Q',result,8,(len(result)+15)//16*16)
 return bytes(result)

def metadata(source,native_bundle):
 obj=m.parse(source);entries=list(b.m.b.audit.entries(native_bundle));bykey={e['resource']:e for e in entries}
 if m.write(obj)!=source or obj['version']!=7 or [len(x) for x in obj['sections']]!=[41,41,2,0,24,40,40]:raise ValueError('Unobserved native metadata layout')
 names=m.paths(obj);keys=[x.lower().replace('\\','/') for x in names[1:]]
 if len(entries)!=40 or set(keys)!=set(bykey):raise ValueError('Identical native resource set required')
 output=copy.deepcopy(obj)
 for index,key in enumerate(keys,1):
  e=bykey[key];row=list(output['sections'][0][index]);data=output['sections'][1][index]
  if row[4]!=index or row[6:]!=[0,0] or data[0:2]!=(index,1) or data[4]!=0:raise ValueError('Buffer/extra-location tables unsupported')
  row[2]=e['packed'];row[3]=e['size'];row[5]=e['codec'];output['sections'][0][index]=tuple(row)
  output['sections'][1][index]=(index,1,e['offset'],e['packed'],0)
 header=native_bundle.read_bytes()[:32];length=struct.unpack_from('<Q',header,8)[0];start=32+struct.unpack_from('<I',header,16)[0]
 if start!=12192 or length<native_bundle.stat().st_size or length-native_bundle.stat().st_size>=16:raise ValueError('Native alignment contract differs')
 record=output['sections'][2][1]
 if record[:3]!=(1,1,40) or record[4:]!=(12192,0):raise ValueError('Bundle mapping differs')
 output['sections'][2][1]=(1,1,40,length-start,start,0)
 output['packed']=max(e['packed'] for e in entries);output['size']=max(e['size'] for e in entries)
 return m.write(output)

def main():
 out=build.OUT;controls=[]
 for folder in ('native-startup-failed','native-final'):
  attempts=json.loads((out/folder/'native-commands.json').read_text())
  if len(attempts)!=1 or attempts[0]['label']!='cook' or attempts[0]['exit_code'] is not None or attempts[0].get('timeout_seconds')!=90:raise ValueError('Fallback only permitted after the recorded bounded startup failures')
  if any((out/folder/name).stat().st_size for name in ('cook.full.log','cook.stdout.log')):raise ValueError('Nonblank native diagnostics require investigation, not this fallback')
 for name in ('menus087-v2','menus087-v3'):
  folder=ROOT/'build'/name/'packed';path=folder/'blob0.bundle';files={e['resource']:b.m.b.bars.extract(path,e['resource']) for e in b.m.b.audit.entries(path)}
  if bundle(path,files)!=path.read_bytes():raise ValueError('Native bundle control differs '+name)
  raw=(folder/'metadata.store').read_bytes()
  if metadata(raw,path)!=raw:raise ValueError('Native metadata identity control differs '+name)
  controls.append(dict(name=name,bundle_sha256=b.m.b.fallback.sha(path),metadata_sha256=b.m.b.audit.sha(raw),bundle_and_metadata_byte_identical=True))
 source=ROOT/'build/menus087-v2/packed';changed=ROOT/'build/menus087-v3/packed'
 changed_files={e['resource']:b.m.b.bars.extract(changed/'blob0.bundle',e['resource']) for e in b.m.b.audit.entries(changed/'blob0.bundle')}
 if bundle(source/'blob0.bundle',changed_files)!=(changed/'blob0.bundle').read_bytes():raise ValueError('Independent changed native bundle control differs')
 if metadata((source/'metadata.store').read_bytes(),changed/'blob0.bundle')!=(changed/'metadata.store').read_bytes():raise ValueError('Independent changed native metadata control differs')
 prepared=json.loads((out/'prepared.json').read_text());files={key:(out/'prepared-inputs'/key).read_bytes() for key in prepared['keys']}
 for key,data in files.items():
  chunks=b.m.b.font.native.chunks(data)
  if chunks[0]['class_name']!='CSwfResource' or not all(c['crc_valid'] for c in chunks):raise ValueError('Invalid native movie')
  for index in (2,5,6,7,8,9):
   if struct.unpack_from('<III',data,40+index*12)[1]:raise ValueError('External dependencies/buffers require native regeneration')
 target=out/'packed'
 if target.exists():raise ValueError('Fresh output required')
 target.mkdir();path=target/'blob0.bundle';path.write_bytes(bundle(changed/'blob0.bundle',files))
 raw=metadata((changed/'metadata.store').read_bytes(),path);(target/'metadata.store').write_bytes(raw)
 for key,value in files.items():
  if b.m.b.bars.extract(path,key)!=value:raise ValueError('Candidate extraction mismatch')
 b.m.b.write_json(out/'reconstruction.json',dict(method='same 40-key native-control verified bundle and metadata reconstruction',native_candidate_cook_validated=False,native_candidate_pack_passed=False,native_candidate_metadata_passed=False,controls=controls,independent_changed_metadata_exact=True,independent_changed_bundle_exact=True,self_contained_no_new_dependencies=True,bundle_sha256=b.m.b.fallback.sha(path),metadata_sha256=b.m.b.audit.sha(raw),exact_extraction=True))
 print('Both native controls exact; independent changed metadata exact; candidate reconstructed. Native validation remains unavailable.')
if __name__=='__main__':main()
