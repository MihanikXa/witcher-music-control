"""Source-derived 2048x1152 text model, not an in-game rendering certificate."""
import configparser,importlib.util,json,struct,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build-menu-finishing');prep=load('prepare-english-gentium');widths=load('check-gentium-layout')

def main():
 from PIL import Image,ImageDraw,ImageFont
 cfg=configparser.ConfigParser();cfg.read_string(b.b.m.b.settings_text(b.b.m.v.SETTINGS));key='gameplay/gui_new/swf/witcher3/fonts_en.redswf'
 owners=b.b.m.b.owners(b.b.m.v.GAME,cfg,{key},b.OUT);owner=min([r for r in owners[key] if r['enabled']=='1'],key=lambda r:int(r['priority']));container=Path(owner['container'])
 data=b.b.m.b.read_bundle(container,next(e for e in b.b.m.b.audit.entries(container) if e['resource']==key),b.b.m.v.GAME,b.OUT);(b.OUT/'installed-font.redswf').write_bytes(data)
 fonts={struct.unpack_from('<H',p)[0]:p for c,p in prep.audit.swf_tags(data)[2] if c==75}
 tables={i:widths.baseline_metrics(p) for i,p in fonts.items()};metrics=prep.layout(fonts[1]);asc=metrics['ascent']/20480;desc=metrics['descent']/20480;cap_ratio=1260/1940
 if not (b.OUT/'alchemy-v3.xml').exists():
  resource='gameplay/gui_new/swf/alchemy/panel_alchemy.redswf';gfx=b.OUT/'alchemy-v3.gfx';gfx.write_bytes(b.b.m.r.p.movie((b.parent.OUT/'prepared-inputs'/resource).read_bytes())[1]);b.b.java(b.OUT,'inspect-xml',['-swf2xml',gfx,b.OUT/'alchemy-v3.xml'])
 xml=ET.parse(b.OUT/'alchemy-v3.xml').getroot();fields={n.get('characterID'):n for n in xml.iter() if n.get('type')=='DefineEditTextTag'}
 description_width=(int(fields['320'].find('bounds').get('Xmax'))-int(fields['320'].find('bounds').get('Xmin')))/20
 phrase='Can be used to enhance Abilities or create mutagen decoctions.';a,k=tables[1];plain=widths.width(phrase,a,k)
 fitting=19
 while fitting>17.5 and plain*fitting>description_width-4:fitting-=.25
 row={}
 for version,size,status,ratio in [('v3',18,16,.8),('v4',19.5,15.5,.9)]:
  name_y=9;status_y=42.45
  if version=='v4':
   cap_a=size*asc*cap_ratio;cap_b=status*asc*cap_ratio;center=(9+2+size*asc-cap_a+42.45+2+status*asc)/2;top=center-(cap_a+4+cap_b)/2
   name_y=top+cap_a-size*asc-2;status_y=top+cap_a+4+cap_b-status*asc-2
  row[version]=dict(name_y=name_y,status_y=status_y,name_baseline=name_y+2+size*asc,status_baseline=status_y+2+status*asc,field_origin_gap=status_y-name_y)
 samples=[]
 for text,size,ratio,tracking,heavy,available in [('Greater Blue Mutagen',32,.92,1.6,True,530),('Enhanced Legendary Wolven Silver Sword',32,.92,1.6,True,320),('Alchemy ingredients',21.5,.9,1.1,False,480),('Élixir de la Rivière',19.5,.9,.85,False,459.85),('Ingredients missing',15.5,.86,.5,False,459.85)]:
  advances,pairs=tables[5 if heavy else 1];parts=[]
  for ch in text:parts.append(widths.width(ch.upper(),advances,pairs)*size*(ratio if ch!=ch.upper() else 1))
  measured=sum(parts)+tracking*len(text);minimum=.5625 if size>=28 else .82;required=min(1,(available-4)/measured);fit=max(minimum,required);wrapped=required<minimum and size>=28
  lines=[text]
  def measure(s):return sum(widths.width(ch.upper(),advances,pairs)*size*(ratio if ch!=ch.upper() else 1) for ch in s)*fit+tracking*fit*len(s)
  if wrapped:
   lines=['']
   for word in text.split(' '):
    candidate=(lines[-1]+' '+word).strip()
    if measure(candidate)>available-4 and lines[-1]:lines.append(word)
    else:lines[-1]=candidate
  line_width=max(measure(line) for line in lines);height=len(lines)*size*fit*(asc+desc)+4
  samples.append(dict(text=text,size=size,ratio=ratio,tracking=tracking,bold=heavy,width_before_fit=measured,width_after_fit=measured*fit,available=available,fit=fit,wrap=wrapped,display_lines=lines,max_line_width=line_width,estimated_height=height,fits=line_width<=available-4+.01 and (not wrapped or height<=48)))
 image=Image.new('RGB',(4096,2304),'#16191a');draw=ImageDraw.Draw(image);regular=ROOT/'build/gentium-font-source-final/QuietFolioBook-Regular.ttf';bold=regular.with_name('QuietFolioBook-Bold.ttf')
 def text(x,y,s,size,color='#ddd2bb',ratio=None,tracking=0,heavy=False):
  if ratio is None:
   draw.text((x*2,y*2),s,font=ImageFont.truetype(str(bold if heavy else regular),round(size*2)),fill=color,anchor='ls');return
  for ch in s:
   font=ImageFont.truetype(str(bold if heavy else regular),round(size*2*(ratio if ch!=ch.upper() else 1)));draw.text((x*2,y*2),ch.upper(),font=font,fill=color,anchor='ls');x+=font.getlength(ch.upper())/2+tracking
 text(32,40,'Source-derived typography model at 2048 x 1152; not a game screenshot',21)
 scale=2048/1920
 for index,(version,size,status,ratio) in enumerate([('v3',18,16,.8),('v4',19.5,15.5,.9)]):
  y=100+index*180;text(32,y-20,version+' internal recipe labels (same 80px row / icon bounds)',18)
  draw.rectangle((32*2,y*2,(32+556*scale)*2,(y+80*scale)*2),outline='#b48c44',width=2)
  text(32+86*scale,y+row[version]['name_baseline']*scale,'Greater Blue Mutagen',size*scale,'#e2c47f',ratio,.85 if version=='v4' else .65)
  text(32+86*scale,y+row[version]['status_baseline']*scale,'Ingredients missing',status*scale,'#928b7e',.86 if version=='v4' else .8,.5 if version=='v4' else .65)
 text(32,520,'Major item title: v3 / v4',18)
 text(32,575,'Greater Blue Mutagen',30,ratio=.8,tracking=.65)
 text(32,645,'Greater Blue Mutagen',32,ratio=.92,tracking=1.6,heavy=True)
 text(32,740,'Bounded short prose: original size 19 / measured fitting size '+str(fitting),18)
 text(32,795,phrase,19)
 text(32,850,phrase,fitting)
 text(32,960,'Menu footer lettering model: Select / [Hold] Description size / Back',18)
 text(32,1010,'Select   [Hold] Description size   Back',17,'#a4997f',.88,.55)
 image.resize((2048,1152),Image.Resampling.LANCZOS).save(b.OUT/'typography-finishing-model.png')
 b.b.m.b.write_json(b.OUT/'font-model.json',dict(font_owner=owner,regular_glyphs=len(metrics['codes']),ascent=asc,descent=desc,cap_to_ascender_ratio=cap_ratio,row_metrics=row,description=dict(text=phrase,field_width=description_width,usable_width=description_width-4,width_at_19=plain*19,fitted_size=fitting,fitted_width=plain*fitting),sample_headings=samples,model_only=True,rendered_preview_size=[2048,1152],runtime_verified=False))
 print('Font model uses actual deployed English SWF',owner['sha256'],'short prose fit',fitting)
if __name__=='__main__':main()
