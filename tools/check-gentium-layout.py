"""Offline widths, metrics and independently exported SWF glyph preview.

No UI geometry is edited. Width/clipping checks are models, not engine output.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'tools/build-gentium-swf.py')
builder=importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
SAMPLES=['Roach','Vesemir','Geralt of Rivia','Kaer Morhen','Villentretenmerth',
         'Emhyr var Emreis, Emperor of Nilfgaard','Philippa Eilhart','Nicolas de la Rivière',
         'Dandelion’s lute — “A tale…”','É Ł Œ ß æ Å','AV To Wa','0123456789',
         '99,999 / 100,000','Graphics and display settings','Alternative movement response',
         'The truth is a shard of ice. What matters is the story we choose to tell.',
         'I’m looking for someone. Have you seen a woman with ashen hair?',
         'ŉ ℃ ℅ ℉ Å ℮']


def baseline_metrics(payload):
    info=builder.prep.layout(payload)
    base=7+payload[4]; unit=4 if info['flags']&8 else 2
    offset=struct.unpack_from('<I' if unit==4 else '<H',payload,base+info['glyphs']*unit)[0]
    pos=base+offset+2*info['glyphs']+6+2*info['glyphs']
    for _ in range(info['glyphs']): pos=builder.prep.rect_end(payload,pos)
    count=struct.unpack_from('<H',payload,pos)[0]
    pairs={}
    for i in range(count):
        a,b,amount=struct.unpack_from('<HHh',payload,pos+2+i*6); pairs[a,b]=amount
    return dict(zip(info['codes'],info['advances'])),pairs


def width(text,advances,pairs):
    codes=list(map(ord,text))
    return (sum(advances[c] for c in codes)+sum(pairs.get((a,b),0) for a,b in zip(codes,codes[1:])))/20480


def main():
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont
    from PIL import Image,ImageDraw,ImageFont
    ap=argparse.ArgumentParser(); ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--ffdec', type=Path, default=ROOT/'build/tools/ffdec/ffdec.jar')
    a=ap.parse_args(); work=a.build.resolve()
    if ROOT/'build' not in work.parents: raise ValueError('Private build required')
    if not (work/'jpexs-fonts').exists():
        candidate=work/'input/fonts_en_qf_book_v1.swf'
        result=subprocess.run(['java','-jar',str(a.ffdec.resolve()),'-export','font',str(work/'jpexs-fonts'),str(candidate)],capture_output=True,timeout=60)
        (work/'jpexs-export.log').write_bytes(result.stdout+result.stderr)
        if result.returncode: raise ValueError('Independent SWF font export failed')
    tags=builder.audit.swf_tags((work/'fonts_en.redswf').read_bytes())[2]
    old=[b for c,b in tags if c==75]
    root=ET.parse(work/'candidate.xml').getroot()
    fonts=[n for n in root.iter() if n.get('type')=='DefineFont3Tag']
    results=[]
    image=Image.new('RGB',(1400,1030),'#eee8dc'); draw=ImageDraw.Draw(image)
    draw.text((25,15),'Decoded SWF font preview - not in-game; displayed larger than game text',fill='#141718')
    for index,(node,payload,style) in enumerate(zip(fonts,old,('Regular','Italic','Bold'))):
        codes=[int(c.text) for c in node.find('codeTable')]
        advances=dict(zip(codes,[int(c.text) for c in node.find('fontAdvanceTable')]))
        pairs={(int(n.get('fontKerningCode1')),int(n.get('fontKerningCode2'))):int(n.get('fontKerningAdjustment')) for n in node.find('fontKerningTable')}
        old_adv,old_pairs=baseline_metrics(payload)
        ttpath=work/('QuietFolioBook-'+style+'.ttf')
        f=TTFont(ttpath); upem=f['head'].unitsPerEm
        hbfont=hb.Font(hb.Face(ttpath.read_bytes())); hbfont.scale=(upem,upem)
        features={}
        for table in ('GPOS','GSUB'):
            for record in f[table].table.FeatureList.FeatureRecord: features[record.FeatureTag]=False
        features['kern']=True
        samples=[]
        for text in SAMPLES:
            if set(map(ord,text))-set(advances): raise ValueError('Sample contains unsupported baseline character')
            old_width,new_width=width(text,old_adv,old_pairs),width(text,advances,pairs)
            buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); buf.language='en'
            hb.shape(hbfont,buf,features)
            hb_width=sum(p.x_advance for p in buf.glyph_positions)/upem
            samples.append(dict(text=text,vanilla_em=old_width,trial_em=new_width,
                                trial_to_vanilla=new_width/old_width,trial_px_at20=new_width*20,
                                gpos_full_run_em=hb_width,pair_model_minus_full_gpos_em=new_width-hb_width))
        boxes=[(c,int(b.get('Ymin')),int(b.get('Ymax'))) for c,b in zip(codes,node.find('fontBoundsTable'))]
        ascent,descent=int(node.get('fontAscent')),int(node.get('fontDescent'))
        overshoots=[dict(code=f'U+{c:04X}',top=max(0,-ymin-ascent),bottom=max(0,ymax-descent))
                    for c,ymin,ymax in boxes if -ymin>ascent or ymax>descent]
        digits=[advances[ord(c)] for c in '0123456789']
        if len(set(digits))!=1: raise ValueError('Non-tabular default digits')
        results.append(dict(style=style,samples=samples,tabular_digits=True,digit_advance=digits[0],
                            ascent=ascent,descent=descent,leading=int(node.get('fontLeading')),
                            accent_metric_overshoots=overshoots))
        exported=next((work/'jpexs-fonts').glob(str(int(node.get('fontID')))+'_*.ttf'))
        face=ImageFont.truetype(str(exported),36)
        y=60+index*315
        draw.text((25,y),style+' - SWF ID '+node.get('fontID'),fill='#141718')
        for j,text in enumerate(('Roach   Vesemir   Geralt of Rivia   Villentretenmerth',
                                'Dandelion’s lute — “A tale…”   É Ł Œ ß æ Å',
                                'ŉ   ℃   ℅   ℉   Å   ℮',
                                '0123456789   99,999 / 100,000',
                                'The truth is a shard of ice. What matters is the story.')):
            draw.text((25,y+28+j*48),text,font=face,fill='#141718')
    image.save(work/'decoded-swf-preview.png')
    npc=ET.parse(ROOT/'build/native-npc/native.xml').getroot()
    field=next(n for n in npc.iter() if n.get('type')=='DefineEditTextTag' and n.get('characterID')=='38')
    bounds=field.find('bounds')
    authored_width=(int(bounds.get('Xmax'))-int(bounds.get('Xmin')))/20
    authored_height=(int(bounds.get('Ymax'))-int(bounds.get('Ymin')))/20
    receipt=dict(styles=results,npc_name_authored_width_px=authored_width,npc_name_authored_height_px=authored_height,
                 npc_runtime_size_preserved=20,npc_longest_sample_px_at20=max(s['trial_px_at20'] for s in results[0]['samples'][:8]),
                 npc_sample_widths_fit_authored_bounds=all(s['trial_px_at20']<authored_width for s in results[0]['samples'][:8]),
                 text_bounds_changed=False,subtitle_scaling_changed=False,natural_proportions_preserved=True,
                 preview='independent JPEXS SWF-to-TTF export, raster preview only; exporter has head-table trailing-byte warning',
                 renderer_metrics_and_runtime_wrapping_verified=False,
                 contextual_gpos='Two-character positioning converted exactly. Longer-context GPOS/mark shaping is not representable in DefineFont3 pairs; full-run differences reported.')
    (work/'layout.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({k:v for k,v in receipt.items() if k!='styles'},indent=2))


if __name__=='__main__': main()
