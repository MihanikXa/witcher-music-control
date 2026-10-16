"""Inspect unchanged Inventory BC1/BC3 atlas contracts; no writes."""
import importlib.util,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-ink-hud-batch.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def validate(data):
 chunks=b.font.native.chunks(data);textures={};reports=[]
 if any(not c['crc_valid'] for c in chunks):raise ValueError('Native CRC invalid')
 for c in chunks[1:]:
  properties=c['properties'];resident,count,w,h,pitch,size,alignment=struct.unpack_from('<7I',c['tail']);compression=properties['compression']['value'];block={'TCM_DXTAlpha':16,'TCM_DXTNoAlpha':8}.get(compression)
  if c['class_name']!='CSwfTexture' or resident or count!=1 or not block:raise ValueError('Unobserved texture encoding')
  if w!=properties['width']['value'] or h!=properties['height']['value'] or size!=len(c['tail'])-28 or size!=((w+3)//4)*((h+3)//4)*block:raise ValueError('Mip dimensions/length invalid')
  name=properties['linkageName']['value']
  if name in textures:raise ValueError('Duplicate atlas')
  textures[name]=(w,h);reports.append(dict(linkage=name,width=w,height=h,compression=compression,pixels_sha256=b.audit.sha(c['tail'][28:])))
 expected=struct.pack('<I',len(textures))+b''.join(struct.pack('<I',i) for i in range(2,len(textures)+2))
 if bytes.fromhex(chunks[0]['properties']['textures']['value'])!=expected:raise ValueError('Texture handles invalid')
 tags=b.audit.swf_tags(data)[2];images={};rectangles=0
 for code,payload in tags:
  if code==1009:
   ident=struct.unpack_from('<H',payload)[0];position=11+payload[10];length=payload[position];name=payload[position+1:position+1+length].decode('ascii');w,h=struct.unpack_from('<HH',payload,6)
   if name not in textures or ident in images:raise ValueError('Unresolved image linkage')
   if (w,h)!=textures[name] and (((w+3)//4)*4,((h+3)//4)*4)!=textures[name]:raise ValueError('Image dimensions invalid')
   images[ident]=name
 for code,payload in tags:
  if code==1008:
   character,image,x1,y1,x2,y2=struct.unpack('<6H',payload)
   if image not in images:raise ValueError('Image ID missing')
   w,h=textures[images[image]]
   if not(0<=x1<x2<=w and 0<=y1<y2<=h):raise ValueError('Atlas rectangle invalid')
   rectangles+=1
 return dict(textures=reports,image_links=len(images),rectangles=rectangles)
