"""Private reference composite, expressly static. No SWF, game, save or ZIP writes.

User authorized local composition/image editing with the exact approved PNG.
Reference-derived Geralt/details/header/footer are retained, not game renders.
"""
import hashlib, importlib.util, json, math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=load('inspect-approved-inventory');p=load('preview-menu-refinement')
OUT=a.OUT;W,H=1672,941
FONT=ROOT/'build/gentium-font-source-final/QuietFolioBook-Regular.ttf'
EDIT=[(30,140,292,790),(308,170,627,808)]
PROTECTED={'global_header':(0,0,1672,130),'details':(632,138,1080,810),'geralt_and_backdrop':(1080,100,1672,820),'footer':(0,820,1672,941)}
ITEMS=[
 ('Gnomish Gwyhyr','Steel sword','unique_gwyhyr_64x128.png'),
 ('Silver sword','Silver sword','gnomish_silver_sword_lvl1-64x128.png'),
 ('Rusty Novigrad sword','Steel sword','novigraadan_steel_sword_rusty_64x128.png'),
 ('Rusty Velen sword','Steel sword','nomansland_steel_sword_rusty_64x128.png'),
 ('Gnomish steel sword','Steel sword','gnomish_steel_sword_lvl1_64x128.png'),
 ('Rusty Skellige sword','Steel sword','skellige_steel_sword_rusty_64x128.png'),
 ('Enhanced Legendary Wolven Silver Sword','Silver sword','witcher_silver_wolf_sword_lvl1_64x128.png'),
]
def digest(image):return hashlib.sha256(image.tobytes()).hexdigest()
def font(size):return ImageFont.truetype(str(FONT),size)
def clean_band(image,box,edges=None):
    # Reconstruct obscured UI substrate from reference edge samples at SAME Y.
    # This is a reference-composite limitation, not a new background asset.
    x0,y0,x1,y1=box;pix=image.load()
    for y in range(y0,y1):
        left=pix[edges[0] if edges else x0-3,y];right=pix[edges[1] if edges else x1+1,y]
        for x in range(x0,x1):
            t=(x-x0)/(x1-x0)
            pix[x,y]=tuple(round(left[c]*(1-t)+right[c]*t) for c in range(3))
def fit(text,width,face):
    if face.getlength(text)<=width:return text
    while text and face.getlength(text+'…')>width:text=text[:-1]
    return text.rstrip()+'…'
def mark(image,x,y,source):
    # Exact existing v4 SlotBase mark: same geometry/color/alpha, k cancels scale.
    u=W/1920;overlay=Image.new('RGBA',image.size)
    vertices=[(x+vx*u,y+vy*u) for vx,vy in source['vertices']]
    c=source['color'];ImageDraw.Draw(overlay).polygon(vertices,fill=(c>>16,(c>>8)&255,c&255,round(source['alpha']*255)))
    image.paste(overlay,(0,0),overlay)
def rows(image,count,icons,marker):
    clean_band(image,EDIT[1]);metrics=[];d=ImageDraw.Draw(image)
    # Measured first and second reference row frames: 318..612, 174..251,
    # next at 266. One invariant row pitch in both inventory states.
    for i in range(count):
        x,y=318,174+i*92;selected=i==0
        layer=Image.new('RGBA',image.size);g=ImageDraw.Draw(layer)
        g.rounded_rectangle((x,y,611,y+77),radius=2,fill=(12,12,12,55),outline=(202,164,105,255) if selected else (94,94,87,125),width=1)
        if selected:
            glow=Image.new('RGBA',image.size);ImageDraw.Draw(glow).rounded_rectangle((x,y,611,y+77),radius=2,outline=(218,170,99,100),width=2)
            image.paste(glow.filter(ImageFilter.GaussianBlur(3)),(0,0),glow.filter(ImageFilter.GaussianBlur(3)))
        image.paste(layer,(0,0),layer)
        name,subtitle,_=ITEMS[i];im=icons[i].copy();im.thumbnail((46,70),Image.Resampling.LANCZOS)
        image.paste(im,(337+(46-im.width)//2,y+4+(70-im.height)//2),im)
        if i==1:mark(image,337,y+4,marker) # fixture: equipped silver sword
        face=font(17);display=fit(name,203,face)
        d.text((400,y+21),display,font=face,fill='#E6E0D2')
        d.text((400,y+44),subtitle,font=font(14),fill='#A29F96')
        metrics.append(dict(name=name,display=display,subtitle=subtitle,bounds=[x,y,612,y+78],icon_source=list(icons[i].size),icon_display=list(im.size),upscaled=False,text_width=face.getlength(display),text_allowance=203,equipped=i==1))
    return metrics
def rail(image,reference,weapons,review):
    clean_band(image,EDIT[0],(18,306));substrate=image.copy();d=ImageDraw.Draw(image)
    # Exact original seven rail rows, shifted one unchanged pitch to insert
    # the sole approved addition. No category compression or new icon system.
    for i in range(7):
        y=152+i*79;patch=reference.crop((45,y,284,y+75))
        if i==0:image.paste(patch,(45,y+79))
        else:
            # Retain original icon/type pixels without transplanting a block
            # of upper-screen background into lower atmospheric scenery.
            fg=patch.crop((0,0,201,75));under=image.crop((45,y+79,246,y+154))
            image.paste(ImageChops.lighter(under,fg),(45,y+79))
            d.line((45,y+154,284,y+154),fill='#252623',width=1)
    d.text((106,179),'REVIEW',font=font(17),fill='#D7D0C2')
    d.text((261,179),str(review),font=font(17),fill='#ADA28C',anchor='ra')
    counts=[weapons,4 if weapons==2 else 16,0,0,0,0,0]
    for i,n in enumerate(counts):
        y=152+(i+1)*79
        # Clear only original count, keeping actual reference icon/type untouched.
        image.paste(substrate.crop((247,y+23,278,y+49)),(247,y+23))
        if n:d.text((268,y+27),str(n),font=font(17),fill='#CBBBA1',anchor='ra')
def main():
    receipt=json.loads((OUT/'source-receipt.json').read_text(encoding='utf-8'))
    if a.sha(a.REFERENCE)!=receipt['reference']['sha256']:raise ValueError('Reference changed')
    reference=Image.open(a.REFERENCE).convert('RGB')
    cache=p.b.b.m.v.GAME/'Mods/modInkIronMenuItemArt/content/texture.cache'
    index=list(p.b.b.m.b.inventory.cache_entries(cache));icons=[];assets=[]
    for name,subtitle,suffix in ITEMS:
        row=next(r for r in index if r['resource'].endswith('/'+suffix))
        im,rawsha=p.decode(cache,row);icons.append(im)
        assets.append(dict(fixture_label=name,subtitle=subtitle,resource=row['resource'],source_dimensions=list(im.size),decoded_block_sha256=rawsha))
    outputs={};meta={}
    for state,visible,total,review in [('sparse',2,2,2),('populated',7,30,3),('six-row-fit',6,6,2)]:
        image=reference.copy();rail(image,reference,total,review)
        metrics=rows(image,visible,icons,receipt['marker'])
        if state=='populated':
            d=ImageDraw.Draw(image);d.line((622,174,622,805),fill='#383A38',width=1);d.line((622,174,622,320),fill='#9E8A62',width=2)
        path=OUT/(state+'-1672x941.png');image.save(path);outputs[state]=image
        for name,box in PROTECTED.items():
            if reference.crop(box).tobytes()!=image.crop(box).tobytes():raise ValueError('Protected region edited: '+name)
        for width,height in [(1920,1080),(3840,2160)]:
            image.resize((width,height),Image.Resampling.LANCZOS).save(OUT/(state+f'-{width}x{height}.png'))
        meta[state]=dict(path=str(path),sha256=a.sha(path),visible_rows=visible,total_weapon_rows=total,total_equipment_items=6 if state=='sparse' else None,review_count=review,review_count_illustrative=True,fixture_origin='Sparse: modeled reported two weapons plus four armor, not a save extraction. Dense: representative artwork and illustrative count, not an acquisition ledger.',rows=metrics,protected_pixel_hashes={n:digest(image.crop(box)) for n,box in PROTECTED.items()})
    sheet=Image.new('RGB',(W*3,H+56),'#151515');d=ImageDraw.Draw(sheet)
    for i,(label,im) in enumerate([('Approved reference',reference),('Sparse: 2 weapons + 4 armor; Review 2 illustrative',outputs['sparse']),('Populated: 30 weapons; Review 3 illustrative',outputs['populated'])]):
        sheet.paste(im,(i*W,56));d.text((i*W+24,16),label,font=font(22),fill='#E6DFCF')
    sheet.save(OUT/'reference-comparison.png')
    difference=Image.new('RGB',(W,H));src=reference.load();dst=outputs['populated'].load();px=difference.load()
    for y in range(H):
        for x in range(W):px[x,y]=(220,166,82) if src[x,y]!=dst[x,y] else (12,14,15)
    difference.save(OUT/'edited-pixels.png')
    report=dict(reference_sha256=a.sha(a.REFERENCE),font=dict(path=str(FONT),sha256=a.sha(FONT)),icon_cache=dict(path=str(cache),sha256=a.sha(cache)),assets=assets,outputs=meta,edit_rectangles=EDIT,protected_regions=PROTECTED,limitations=['Reference Geralt, details, scenery, header and footer retained as pixels: not actual game assets extracted or runtime reproduction.','Original selected details/stat numbers and currency/level/footer keys remain reference illustrations, not verified item stats or bindings.','Row names are representative English fixture labels; localized runtime names require native provider enrichment.','Review counts and dense inventory count are illustrative. Sparse membership is modeled from reported gear count, not save data.','1080p/4K exports are composition projections of a 1672x941 reference; do not establish runtime UI scale, source-art detail or 4K sharpness.','Occluded row substrate reconstructed from same-Y edge colors; neutral reference-derived interpolation, no replacement scenic asset.'],native_binary_built=False,runtime_behavior_proven=False)
    (OUT/'visual-receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Private sparse/populated proofs, six-row stress fit, reference comparison and receipts exported.')
if __name__=='__main__':main()
