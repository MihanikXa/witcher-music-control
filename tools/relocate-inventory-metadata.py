"""Bounded single-Inventory metadata conversion, native-controls verified.
Original codec for documented v6/v7 field layout (Systemcluster/w3edit metadata.rs).
No native metadatastore success claimed. No hash/path guessing or extra resources.
"""
import argparse,copy,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('r',ROOT/'tools/relocate-hud-metadata.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
FORMATS=('8I',None,None,'I','2i','3i','2q')
def vlq(data,pos):
 first=data[pos];pos+=1;value=first&63;shift=6;more=first&64
 while more:
  byte=data[pos];pos+=1;value|=(byte&127)<<shift;shift+=7;more=byte&128
 if first&128 and value:raise ValueError('Negative count unsupported')
 return value,pos
def enc(value):
 if value==0:return b'\x80'
 out=bytearray([value&63]);value>>=6
 if value:out[0]|=64
 while value:
  byte=value&127;value>>=7;out.append(byte|(128 if value else 0))
 return bytes(out)
def parse(data):
 if data[:4]!=b'\x03VTM':raise ValueError('Not metadata')
 version,packed,size=struct.unpack_from('<3I',data,4)
 if version not in (6,7):raise ValueError('Unsupported metadata version')
 length,pos=vlq(data,16);strings=data[pos:pos+length];pos+=length;sections=[]
 for index,fmt in enumerate(FORMATS):
  fmt=fmt or ('Q4I' if version==7 else ('5I' if index==1 else '6I'));count,pos=vlq(data,pos);width=struct.calcsize('<'+fmt);rows=[]
  for n in range(count):
   row=struct.unpack_from('<'+fmt,data,pos);pos+=width
   if version==7 and index==0:row=(*row[:5],row[7],row[5],row[6])
   if version==7 and index==1:row=(row[3],row[4],row[0],row[1],row[2])
   if version==7 and index==2:row=(row[2],row[3],row[4],row[0],row[1],0)
   rows.append(tuple(row))
  sections.append(rows)
 if pos!=len(data):raise ValueError('Unparsed metadata tail')
 return dict(version=version,packed=packed,size=size,strings=strings,sections=sections)
def write(obj):
 version=obj['version'];out=bytearray(b'\x03VTM'+struct.pack('<3I',version,obj['packed'],obj['size'])+enc(len(obj['strings']))+obj['strings'])
 for index,rows in enumerate(obj['sections']):
  fmt=FORMATS[index] or ('Q4I' if version==7 else ('5I' if index==1 else '6I'));out.extend(b'\0' if version==6 and not rows else enc(len(rows)))
  for row in rows:
   if version==7 and index==0:row=(*row[:5],row[6],row[7],row[5])
   if version==7 and index==1:row=(row[2],row[3],row[4],row[0],row[1])
   if version==7 and index==2:
    if row[5]:raise ValueError('Burst data unsupported')
    row=(row[3],row[4],row[0],row[1],row[2])
   out.extend(struct.pack('<'+fmt,*row))
 return bytes(out)
def paths(obj):
 table=obj['strings'];return [table[row[0]:].split(b'\0',1)[0].decode() for row in obj['sections'][0]]
def replace_single(obj,bundle):
 result=copy.deepcopy(obj);entries=list(r.b.audit.entries(bundle))
 if len(entries)!=1 or len(result['sections'][0])!=2 or len(result['sections'][1])!=2 or len(result['sections'][2])!=2 or result['sections'][3]:raise ValueError('Only one file/no buffer supported')
 entry=entries[0]
 if paths(result)[1].lower().replace('\\','/')!=entry['resource']:raise ValueError('Same resource path required')
 result.update(version=7,packed=entry['packed'],size=entry['size']);file=list(result['sections'][0][1]);file[2]=entry['packed'];file[3]=entry['size'];file[5]=entry['codec']
 if file[6] or file[7]:raise ValueError('External buffers unsupported')
 result['sections'][0][1]=tuple(file);result['sections'][1][1]=(1,1,entry['offset'],entry['packed'],0)
 header=bundle.read_bytes()[:32];length=struct.unpack_from('<Q',header,8)[0];start=32+struct.unpack_from('<I',header,16)[0]
 if length<bundle.stat().st_size or length-bundle.stat().st_size>=16 or start>entry['offset']:raise ValueError('Unobserved native bundle layout')
 record=result['sections'][2][1];result['sections'][2][1]=(record[0],1,1,length-start,start,0)
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();r.b.font.private_path(out);commands=json.loads((out/'native-commands.json').read_text())
 if not {'cook','validate','pack'} <= {x['label'] for x in commands if x['passed']}:raise ValueError('Native resource stages required')
 controls=[]
 for name in ('editor-cook-resolved','npc-shadow-unique-cook','field-folio-control-v2','subtitle-shadow-control-v1'):
  folder=ROOT/'build'/name/'packed';data=(folder/'metadata.store').read_bytes();obj=parse(data)
  if write(obj)!=data:raise ValueError('Native metadata parse/write differs')
  if write(replace_single(obj,folder/'blob0.bundle'))!=data:raise ValueError('Native single-key field reconstruction differs')
  controls.append(dict(path=str(folder/'metadata.store'),sha256=r.b.audit.sha(data),byte_identical=True))
 source=ROOT/'build/editor-cook-resolved/packed';control=ROOT/'build/npc-shadow-unique-cook/packed'
 if write(replace_single(parse((source/'metadata.store').read_bytes()),control/'blob0.bundle'))!=(control/'metadata.store').read_bytes():raise ValueError('Independent changed native control not reproduced')
 template=ROOT/'reference/ink-and-iron-0.8.6/hoods-compat/mods/mod0InkAndIron_HoodsCompat/content';raw=(template/'metadata.store').read_bytes();original=parse(raw)
 if write(original)!=raw:raise ValueError('Official legacy metadata round-trip differs')
 installed=ROOT/'reference/ink-and-iron-0.8.6/inventory-source/installed-hoods-metadata.store';live=Path('C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3/Mods/modHoods/content/metadata.store')
 if not installed.exists():installed.write_bytes(live.read_bytes())
 native_inventory=parse(installed.read_bytes());target_name=paths(original)[1];index=paths(native_inventory).index(target_name)
 official_hash=dict((file_id,value) for value,file_id in original['sections'][6])[1];live_hash=dict((file_id,value) for value,file_id in native_inventory['sections'][6])[index]
 if official_hash!=live_hash:raise ValueError('Inventory lookup hash differs from native v7 installed control')
 obj=replace_single(original,out/'packed/blob0.bundle');metadata=write(obj)
 if parse(metadata)!=obj:raise ValueError('Candidate metadata reparse differs')
 target=out/'packed/metadata.store'
 if target.exists():raise ValueError('Do not overwrite metadata')
 target.write_bytes(metadata);r.b.write_json(out/'metadata-reconstruction.json',dict(method='documented v6 to v7 same-key table conversion; native bundle fields',native_metadatastore_passed=False,native_control_byte_identical=True,controls=controls,independent_changed_control_exact=True,legacy_source_roundtrip_exact=True,inventory_lookup_hash_matches_installed_native_v7=True,template_metadata_sha256=r.b.audit.sha(raw),output_metadata_sha256=r.b.audit.sha(metadata),candidate_bundle_sha256=r.b.fallback.sha(out/'packed/blob0.bundle'),format_reference='https://github.com/Systemcluster/w3edit/blob/main/src/metadata.rs'))
 print('Four native metadata controls exact; changed native control reproduced; Inventory v7 metadata reconstructed')
if __name__=='__main__':main()
