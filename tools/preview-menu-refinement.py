"""Private evidence previews; decoded BC3 icons and Gentium width model.

No game or texture writes. Font preview is a model, not GFx/runtime validation.
Run with build/font-preparation-venv/Scripts/python.exe.
"""
import importlib.util,io,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('builder',ROOT/'tools/build-menu-typography.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)

def decode(path,row):
 with path.open('rb') as f:f.seek(row['offset']);block=f.read(row['packed'])
 packed,size,kind=struct.unpack_from('<IIB',block)
 if kind!=0 or packed+9!=len(block):raise ValueError('Unobserved texture block')
 raw=zlib.decompress(block[9:])
 if len(raw)!=size or size!=row['size'] or size!=((row['width']+3)//4)*((row['height']+3)//4)*16:raise ValueError('Not observed BC3 single mip')
 header=b'DDS '+struct.pack('<7I',124,0x81007,row['height'],row['width'],len(raw),0,1)+bytes(44)+struct.pack('<II4s5I',32,4,b'DXT5',0,0,0,0,0)+struct.pack('<5I',0x1000,0,0,0,0)
 from PIL import Image
 return Image.open(io.BytesIO(header+raw)).convert('RGBA'),b.b.m.b.audit.sha(raw)

def main():
 from PIL import Image,ImageDraw,ImageFont
 from fontTools.ttLib import TTFont
 out=b.OUT;out.mkdir(exist_ok=True)
 source=b.b.REF/'mods/modInkAndIronIcons/content/texture.cache';rows=list(b.b.m.b.inventory.cache_entries(source))
 samples=[next(r for r in rows if r['resource'].endswith('/mutagen-0'+str(i)+'-normal-64x64.png')) for i in (1,2,3)]
 for category in ('ingredients/alchemy','weapons','armors','food'):
  samples.append(next(r for r in rows if '/icons/inventory/'+category+'/' in r['resource']))
 wanted={r['resource'] for r in samples};base={k:[] for k in wanted}
 for path in (b.b.m.v.GAME/'content').rglob('texture.cache'):
  if not path.stat().st_size:continue
  for row in b.b.m.b.inventory.cache_entries(path):
   if row['resource'] in wanted:base[row['resource']].append((path,row))
 sheet=Image.new('RGB',(1000,len(samples)*150+45),'#171919');draw=ImageDraw.Draw(sheet);draw.text((10,8),'Decoded native inventory icons: author I&I | installed base cache candidates (no HDR adjustment)',fill='#ded6bd');proof=[]
 for i,row in enumerate(samples):
  y=i*150+45;im,sha=decode(source,row);im.thumbnail((115,115));sheet.paste(im,(12,y),im)
  candidates=[]
  for j,(path,orig) in enumerate(base[row['resource']]):
   old,oldsha=decode(path,orig);old.thumbnail((115,115));sheet.paste(old,(155+j*125,y),old);candidates.append(dict(path=str(path),sha256=oldsha,different_from_author=sha!=oldsha))
  draw.text((12,y+118),Path(row['resource']).name,fill='#bcb39f');proof.append(dict(resource=row['resource'],author_decoded_sha256=sha,base_candidates=candidates))
 sheet.save(out/'icon-comparison.png')
 font=ROOT/'build/gentium-font-source-final/QuietFolioBook-Regular.ttf';f=TTFont(font)
 features=sorted({r.FeatureTag for r in f['GSUB'].table.FeatureList.FeatureRecord})
 fontsheet=Image.new('RGB',(1800,640),'#171919');draw=ImageDraw.Draw(fontsheet);metrics=[]
 phrases=[('Greater Blue Mutagen',18,480),('Ingredients missing',16,480),('Alchemy ingredients',21,480),('Élixir de la Rivière — Wolf’s Hour',18,480),('Enhanced Legendary Wolven Silver Sword',18,480)]
 for i,(phrase,size,width) in enumerate(phrases):
  baseline=70+i*105;x=30;native=ImageFont.truetype(str(font),size*2);draw.text((950,baseline-30),phrase,font=native,fill='#a49b88');start=x
  for ch in phrase:
   small=ch!=ch.upper();face=ImageFont.truetype(str(font),round(size*2*(0.8 if small else 1)));draw.text((x,baseline),ch.upper(),font=face,fill='#ddd2bb',anchor='ls');x+=face.getlength(ch.upper())+1.3
  measured=(x-start)/2;metrics.append(dict(text=phrase,base_size=size,lowercase_size=size*.8,width=measured,authored_width=width,fits_model=measured<=width-4))
 fontsheet.save(out/'gentium-smallcaps-preview.png')
 b.b.m.b.write_json(out/'preview-evidence.json',dict(font_path=str(font),font_sha256=b.b.m.b.fallback.sha(font),gentium_opentype_features=features,smcp_available_in_ttf='smcp' in features,uses_existing_swf_glyphs=True,model_metrics=metrics,icons=proof,runtime_rendering_proven=False))
 print('Private icon/font previews and measured sample receipt ready')
if __name__=='__main__':main()
