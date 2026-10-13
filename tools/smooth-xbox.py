"""Private smooth Xbox paths: analytic quadratic geometry, never pixel tracing.
Install fonttools==4.60.1 in build/hud-v4-python; vendor font stays local.
"""
import math,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'build/hud-v4-python'))
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('flat',ROOT/'tools/flat-vector-xbox.py');flat=importlib.util.module_from_spec(s);s.loader.exec_module(flat)
f=flat.f

def circle(cx,cy,r,reverse=False):
    sign=-1 if reverse else 1;p=[('M',(cx+r,cy))]
    for i in range(8):
        a=sign*i*math.pi/4;b=sign*(i+1)*math.pi/4;m=(a+b)/2
        p.append(('Q',(cx+r/math.cos(math.pi/8)*math.cos(m),cy+r/math.cos(math.pi/8)*math.sin(m),cx+r*math.cos(b),cy+r*math.sin(b))))
    return p

def rounded(cx,cy,w,h,r,reverse=False):
    x=cx-w/2;y=cy-h/2
    p=[('M',(x+r,y)),('L',(x+w-r,y)),('Q',(x+w,y,x+w,y+r)),('L',(x+w,y+h-r)),('Q',(x+w,y+h,x+w-r,y+h)),('L',(x+r,y+h)),('Q',(x,y+h,x,y+h-r)),('L',(x,y+r)),('Q',(x,y,x+r,y))]
    if reverse:
        edges=[];at=p[0][1]
        for k,v in p[1:]:edges.append((k,at,v));at=v[-2:]
        p=[('M',at)]+[(k,old if k=='L' else v[:2]+old) for k,old,v in reversed(edges)]
    return p

class Outline(BasePen):
    def __init__(self,gs):super().__init__(gs);self.paths=[];self.start=None
    def _moveTo(self,p):self.start=p;self.paths.append(('M',p))
    def _lineTo(self,p):self.paths.append(('L',p))
    def _qCurveToOne(self,c,p):self.paths.append(('Q',c+p))
    def _closePath(self):self.paths.append(('L',self.start))
    def _endPath(self):pass

def paths(name,w,h,font):
    label=name.split('ICO_Xbox_',1)[1].split('.',1)[0];cx=w/2;cy=h/2;u=min(w,h)/64
    pill=label in ('LB','RB','LT','RT','Start','Back','Home','Menu','View')
    outer=rounded(cx,cy,40*u,28*u,4*u) if pill else circle(cx,cy,19*u)
    inner=rounded(cx,cy,37.5*u,25.5*u,3*u,True) if pill else circle(cx,cy,17.75*u,True)
    # Winding-oriented ring; separately filled translucent inner silhouette.
    layers=[((20,23,24,128),outer),((239,227,206,255),outer+inner)]
    text=label[0] if label.startswith(('L_','R_')) else label
    if 'dpad' in label:
        p=[('M',(cx-3*u,cy-12*u)),('L',(cx+3*u,cy-12*u)),('L',(cx+3*u,cy-3*u)),('L',(cx+12*u,cy-3*u)),('L',(cx+12*u,cy+3*u)),('L',(cx+3*u,cy+3*u)),('L',(cx+3*u,cy+12*u)),('L',(cx-3*u,cy+12*u)),('L',(cx-3*u,cy+3*u)),('L',(cx-12*u,cy+3*u)),('L',(cx-12*u,cy-3*u)),('L',(cx-3*u,cy-3*u)),('L',(cx-3*u,cy-12*u))]
        layers.append(((159,153,142,255),p))
        for direction in ('left','right','up','down'):
            if direction not in label:continue
            dx,dy={'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}[direction]
            for distance in ([7,11] if 'double' in label else [9]):
                tx=cx+dx*distance*u;ty=cy+dy*distance*u
                pts=[(tx+dx*2.5*u,ty+dy*2.5*u),(tx-dy*2.5*u,ty+dx*2.5*u),(tx+dy*2.5*u,ty-dx*2.5*u)]
                layers.append(((239,227,206,255),[('M',pts[0])]+[('L',pt) for pt in pts[1:]+pts[:1]]))
        return layers
    if text in ('Start','Menu'):text='≡'
    if text in ('Back','View'):
        layers.append(((239,227,206,255),rounded(cx,cy,15*u,12*u,1*u)+rounded(cx,cy,12.5*u,9.5*u,0.5*u,True)))
        return layers
    if text=='Home':text='X'
    ft=TTFont(font);gs=ft.getGlyphSet();cmap=ft.getBestCmap();pen=Outline(gs);advance=0
    allp=[]
    for ch in text:
        glyph=cmap[ord(ch)];pen=Outline(gs);gs[glyph].draw(pen)
        allp += [(k,tuple(v[i]+(advance if i%2==0 else 0) for i in range(len(v)))) for k,v in pen.paths]
        advance+=ft['hmtx'][glyph][0]
    xs=[v[i] for k,v in allp for i in range(0,len(v),2)];ys=[v[i] for k,v in allp for i in range(1,len(v),2)]
    scale=min((15 if len(text)>1 else 21)*u/(max(ys)-min(ys)),28*u/(max(xs)-min(xs)))
    mx=(max(xs)+min(xs))/2;my=(max(ys)+min(ys))/2
    layers.append(((239,227,206,255),[(k,tuple(cx+(v[i]-mx)*scale if i%2==0 else cy-(v[i]-my)*scale for i in range(len(v)))) for k,v in allp]))
    directions=[d for d in ('left','right','up','down') if d in label]
    if 'scroll' in label:directions=['up','down']
    if 'tabs' in label:directions=['left','right']
    for d in directions:
        dx,dy={'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}[d];x=cx+dx*25*u;y=cy+dy*25*u
        pts=[(x+dx*3*u,y+dy*3*u),(x-dy*3*u,y+dx*3*u),(x+dy*3*u,y-dx*3*u)]
        layers.append(((239,227,206,255),[('M',pts[0])]+[('L',p) for p in pts[1:]+pts[:1]]))
    return layers

def shape(cid,name,w,h,font):
    layers=paths(name,w,h,font);bits=f.Bits();nfill=math.ceil(math.log2(len(layers)+1));bits.put(nfill,4);bits.put(0,4)
    for idx,(color,path) in enumerate(layers,1):
        x=y=0
        for k,vals in path:
            v=tuple(round(a*20) for a in vals)
            if k=='M':
                x,y=v;bits.put(0,1);bits.put(3,5);n=f.signed_bits(v);bits.put(n,5);bits.put(x,n,True);bits.put(y,n,True);bits.put(idx,nfill)
            elif k=='L':
                dx,dy=v[0]-x,v[1]-y
                if dx==dy==0:continue
                n=max(2,f.signed_bits((dx,dy)));bits.put(1,1);bits.put(1,1);bits.put(n-2,4);bits.put(1,1);bits.put(dx,n,True);bits.put(dy,n,True);x,y=v
            else:
                cx,cy,ax,ay=v;delta=(cx-x,cy-y,ax-cx,ay-cy);n=max(2,f.signed_bits(delta));bits.put(1,1);bits.put(0,1);bits.put(n-2,4)
                for a in delta:bits.put(a,n,True)
                x,y=ax,ay
    bits.put(0,6);styles=bytes((len(layers),))+b''.join(bytes((0,))+bytes(color) for color,p in layers)+b'\0'
    return struct.pack('<H',cid)+f.encode_rect((0,w*20,0,h*20))+styles+bits.bytes()

def preview(name,w,h,font,scale=1):
    from PIL import Image,ImageDraw
    factor=8*scale;im=Image.new('RGBA',(round(w*factor),round(h*factor)))
    # Each contour is a mask; reversed inner contours subtract from ring.
    for color,p in paths(name,w,h,font):
        mask=Image.new('L',im.size);draw=ImageDraw.Draw(mask);contours=[];points=[];at=None
        for k,v in p:
            if k=='M':
                if points:contours.append(points)
                points=[v];at=v
            elif k=='L':points.append(v);at=v
            else:
                cx,cy,x,y=v;sx,sy=at
                points += [((1-t)**2*sx+2*(1-t)*t*cx+t*t*x,(1-t)**2*sy+2*(1-t)*t*cy+t*t*y) for t in [j/32 for j in range(1,33)]];at=(x,y)
        if points:contours.append(points)
        for i,pts in enumerate(contours):
            area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))
            draw.polygon([(round(x*factor),round(y*factor)) for x,y in pts],fill=255 if area>=0 or i==0 else 0)
        layer=Image.new('RGBA',im.size,color);layer.putalpha(mask.point(lambda a:round(a*color[3]/255)));im.alpha_composite(layer)
    return im.resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS)
