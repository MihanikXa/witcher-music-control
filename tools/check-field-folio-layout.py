"""Measure authored action bounds against serialized utility/Gentium metrics."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('field',ROOT/'tools/prepare-field-folio.py')
field=importlib.util.module_from_spec(spec);spec.loader.exec_module(field)
SAMPLES=['Talk','Loot','Open','Ignite','Extinguish','Mount','Dismount','Investigate',
         'Use Witcher Senses','Read Notice Board','Fast Travel','Hold to examine',
         'Inspect the mysterious object','Café — Łódź…','0123456789','100 / 250']


def pair_table(payload):
    info=field.convert.prep.layout(payload)
    count=info['kerning_count']
    return info,{(a,b):n for a,b,n in struct.iter_unpack('<HHh',payload[len(payload)-count*6:])} if count else {}


def width(info,pairs,text):
    advances=dict(zip(info['codes'],info['advances']))
    return sum(advances[ord(c)] for c in text)+sum(pairs.get((ord(a),ord(b)),0) for a,b in zip(text,text[1:]))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build',type=Path,required=True)
    a=ap.parse_args();work=a.build.resolve()
    if ROOT/'build' not in work.parents:raise ValueError('Private source output required')
    candidate=(work/'input/hud_interactions_ff_regular.swf').read_bytes()
    records={struct.unpack_from('<H',b)[0]:b for c,b in field.audit.swf_tags(candidate)[2] if c==75}
    gentium=next(b for c,b in field.audit.swf_tags((ROOT/'build/gentium-candidate-v1/cooked'/field.convert.prep.KEY).read_bytes())[2] if c==75)
    gi,gp=pair_table(gentium);styles=[]
    for style in ('Regular','Medium'):
        payload=records[field.IDS[style]];info,pairs=pair_table(payload)
        source=work/('QuietFolioUtility-'+style+'.ttf');font=TTFont(source)
        upem=font['head'].unitsPerEm;hbfont=hb.Font(hb.Face(source.read_bytes()));hbfont.scale=(upem,upem)
        features={r.FeatureTag:False for t in ('GPOS','GSUB') for r in font[t].table.FeatureList.FeatureRecord}
        features['kern']=True;results=[]
        for text in SAMPLES:
            pixels=width(info,pairs,text)*22/20480
            buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();buf.direction='ltr';buf.language='en'
            hb.shape(hbfont,buf,features)
            full=sum(p.x_advance for p in buf.glyph_positions)*22/upem
            # SWF advances and kerning independently round each coordinate.
            error=abs(pixels-full)
            if error > .02:raise ValueError('Sample pair widths diverge from full-run GPOS: '+text)
            results.append(dict(text=text,width_px=round(pixels,3),gentium_width_px=round(width(gi,gp,text)*22/20480,3),
                                within_authored_400px=pixels<=400,full_run_rounding_error_px=round(error,5)))
        advances=dict(zip(info['codes'],info['advances']))
        digits=[advances[c] for c in range(48,58)]
        styles.append(dict(style=style,font_id=field.IDS[style],digit_advances=digits,tabular_digits=len(set(digits))==1,
                           samples=results,maximum_sample_width_px=max(r['width_px'] for r in results)))
    receipt=dict(font_size_px=22,bounds_width_px=400,bounds_height_px=30.2,
                 layout_changed=False,styles=styles,full_run_gpos_samples_verified=True,
                 runtime_baseline_clipping_and_autosizing_verified=False)
    (work/'layout.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
