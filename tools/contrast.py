"""Synthetic sRGB screening; no scene sampling, shadow or HDR simulation."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def rgb(h):
    return [int(h.lstrip('#')[i:i+2],16)/255 for i in (0,2,4)]
def luminance(values):
    linear=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in values]
    return sum(w*x for w,x in zip((0.2126,0.7152,0.0722),linear))
def ratio(a,b):
    low,high=sorted((luminance(a),luminance(b)))
    return (high+0.05)/(low+0.05)
def main():
    colors=json.loads((ROOT/'src/palette.json').read_text())['colors']
    backgrounds=dict(foliage='#596D56',snow='#E7ECEB',cave='#151B1C',bright='#F5F3E9',fire='#D79D49')
    rows={name:{scene:round(ratio(rgb(h),rgb(b)),2) for scene,b in backgrounds.items()}
          for name,h in colors.items()}
    backing=rgb(colors['contrast_surface']);snow=rgb(backgrounds['snow'])
    composite=[0.8*x+0.2*y for x,y in zip(backing,snow)]
    receipt=dict(synthetic=True,hdr=False,shadow_included=False,backgrounds=backgrounds,
                 fill_only=rows,snow_backing80={n:round(ratio(rgb(h),composite),2) for n,h in colors.items()})
    out=ROOT/'build/comparison';out.mkdir(parents=True,exist_ok=True)
    (out/'contrast.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
