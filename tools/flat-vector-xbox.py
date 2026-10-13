"""Original flat Xbox timeline repair. No new external images or texture handles.

BitmapData exports remain valid; only authored timeline placements use shapes.
The accepted v2 ABC, fonts, frames, transforms and interaction bindings survive.
"""
import importlib.util
import struct
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load('refine-ink-hud-movies');b=r.b;f=load('build-gentium-swf');parser=load('prepare-npc-shadow')

def rectangles(image):
    """Two solid colors, transparent outside; merge equal runs vertically."""
    rows={};finished=[]
    for y in range(image.height):
        runs=[];x=0
        while x<image.width:
            pixel=image.getpixel((x,y))
            color=0 if pixel[3]<100 else (2 if sum(pixel[:3])>300 else 1)
            left=x;x+=1
            while x<image.width:
                p=image.getpixel((x,y));c=0 if p[3]<100 else (2 if sum(p[:3])>300 else 1)
                if c!=color:break
                x+=1
            if color:runs.append((left,x,color))
        following={}
        for run in runs:following[run]=rows.pop(run,(run[0],y,run[1],y,run[2]))[:3]+(y+1,run[2])
        finished.extend(rows.values());rows=following
    return finished+list(rows.values())

def shape(cid,image):
    bits=f.Bits();bits.put(2,4);bits.put(0,4)
    for left,top,right,bottom,color in rectangles(image):
        x,y=left*20,top*20
        bits.put(0,1);bits.put(3,5);n=f.signed_bits((x,y))
        bits.put(n,5);bits.put(x,n,True);bits.put(y,n,True);bits.put(color,2)
        for dx,dy in (((right-left)*20,0),(0,(bottom-top)*20),(-(right-left)*20,0),(0,-(bottom-top)*20)):
            n=max(2,f.signed_bits((dx,dy)));bits.put(1,1);bits.put(1,1);bits.put(n-2,4);bits.put(1,1)
            bits.put(dx,n,True);bits.put(dy,n,True)
    bits.put(0,6)
    # Two solid RGBA fills and zero line styles. No bitmap/gradient dependency.
    styles=bytes((2,0,20,23,24,224,0,239,227,206,255,0))
    return struct.pack('<H',cid)+f.encode_rect((0,image.width*20,0,image.height*20))+styles+bits.bytes()

def rewrite_tags(tags,mapping,counts):
    result=[]
    for code,payload in tags:
        if code==39:
            children=[(c,payload[a:e]) for c,a,e in parser.records(payload,4)]
            payload=payload[:4]+b''.join(f.tag(c,p) for c,p in rewrite_tags(children,mapping,counts))
        elif code in (4,26,70):
            pos=None
            if code==4:pos=0
            elif code==26 and payload[0]&2:pos=3
            elif code==70 and payload[0]&2:
                pos=4
                # GFx omits the SWF-only implied image class string. Only
                # HasClassName supplies one in these observed CFX movies.
                if payload[1]&8:pos=payload.index(0,pos)+1
            if pos is not None:
                cid=struct.unpack_from('<H',payload,pos)[0]
                if cid in mapping:
                    payload=payload[:pos]+struct.pack('<H',mapping[cid])+payload[pos+2:]
                    if code==70:payload=payload[:1]+bytes((payload[1]&~16,))+payload[2:]
                    counts[cid]=counts.get(cid,0)+1
        result.append((code,payload))
    return result

def original_atlas_art(original,names,out,font):
    """Update original BC3 slots; refuse touching a neighboring live image.

    All bytes outside the glyph-intersecting compression blocks stay exact.
    Padding pixels are transparent. This also serves dynamic BitmapData users.
    """
    tags=b.audit.swf_tags(original)[2];images={}
    for c,p in tags:
        if c==1009:
            pos=11+p[10];images[struct.unpack_from('<H',p)[0]]=p[pos+1:pos+1+p[pos]].decode('ascii')
    chunks=b.font.native.chunks(original);result=bytearray(original);changed={};paint={}
    for c,p in tags:
        if c!=1008:continue
        cid,img,x1,y1,x2,y2=struct.unpack('<6H',p)
        if cid not in names:continue
        image=r.glyph(names[cid],x2-x1,y2-y1,font)
        for y in range(y1,y2):
            for x in range(x1,x2):paint[(img,x,y)]=image.getpixel((x-x1,y-y1))
    for img in {a for a,x,y in paint}:
        index=next(i for i,c in enumerate(chunks) if c['properties'].get('linkageName',{}).get('value')==images[img]);chunk=chunks[index]
        width=chunk['properties']['width']['value'];start=chunk['offset']+chunk['size']-len(chunk['tail'])+28
        blocks={(x//4,y//4) for a,x,y in paint if a==img};changed[index]=[]
        for bx,by in sorted(blocks):
            unsafe=False
            for tc,tp in tags:
                if tc!=1008:continue
                tid,ti,tx1,ty1,tx2,ty2=struct.unpack('<6H',tp)
                if tid not in names and ti==img and max(tx1,bx*4)<min(tx2,bx*4+4) and max(ty1,by*4)<min(ty2,by*4+4):unsafe=True
            # Preserve shared compression-border blocks verbatim. Authored
            # timeline shapes do not sample them; bitmap fallback may retain
            # at most this narrow original edge. Never recolor other UI art.
            if unsafe:continue
            pos=start+(by*((width+3)//4)+bx)*16;pixels=r.decode_block(original[pos:pos+16])
            for i,pixel in enumerate(pixels):
                coordinate=(img,bx*4+i%4,by*4+i//4)
                if coordinate in paint:pixels[i]=paint[coordinate]
                else:
                    # Exported atlases replicate edge texels into padding.
                    # Clear only unowned padding; actual neighboring rectangles
                    # must never be damaged by the fixed flat-color compressor.
                    _,px,py=coordinate
                    for tc,tp in tags:
                        if tc!=1008:continue
                        tid,ti,tx1,ty1,tx2,ty2=struct.unpack('<6H',tp)
                        if tid not in names and ti==img and tx1<=px<tx2 and ty1<=py<ty2:
                            raise ValueError('Unsafe block escaped guard')
                    pixels[i]=(0,0,0,0)
            result[pos:pos+16]=r.encode_block(pixels);changed[index].append(pos)
        eo=struct.unpack_from('<I',result,88)[0]
        struct.pack_into('<I',result,eo+index*24+20,zlib.crc32(result[chunk['offset']:chunk['offset']+chunk['size']]))
    eo,count,_=struct.unpack_from('<III',result,88);struct.pack_into('<I',result,96,zlib.crc32(result[eo:eo+count*24]));struct.pack_into('<I',result,32,r.p.header_crc(result))
    if not all(c['crc_valid'] for c in b.font.native.chunks(result)):raise ValueError('Atlas CRC failure')
    return bytes(result),{str(i):len(p) for i,p in changed.items()}

def repair(accepted,original,out,font):
    old=b.audit.swf_tags(original)[2];tags=b.audit.swf_tags(accepted)[2]
    symbols=b.contracts.symbols(tags);names={v:k for k,v in symbols.items() if 'ICO_Xbox_' in k}
    originals={struct.unpack_from('<H',p)[0]:p for c,p in old if c==1008}
    if not names or not set(names)<=set(originals):raise ValueError('Original Xbox subimages required')
    # Symbol/dictionary IDs across nested sprites are independently inventoried.
    definition_codes={2,6,7,10,11,14,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90,91,1008,1009}
    used={struct.unpack_from('<H',p)[0] for c,p in tags if c in definition_codes}
    nextid=max(used-{65534})+1;mapping={};added=[];details=[];out.mkdir(parents=True)
    for cid,name in sorted(names.items()):
        while nextid in used:nextid+=1
        if nextid>=65534:raise ValueError('Shape dictionary exhausted')
        _,_,x1,y1,x2,y2=struct.unpack('<6H',originals[cid]);image=r.glyph(name,x2-x1,y2-y1,font)
        image.save(out/(str(cid)+'.png'));mapping[cid]=nextid;added.append((32,shape(nextid,image)));nextid+=1
        details.append(dict(symbol=name,bitmap_id=cid,shape_id=mapping[cid],width=x2-x1,height=y2-y1))
    counts={};rewritten=rewrite_tags(tags,mapping,counts)
    added=[(c,p) for c,p in added if struct.unpack_from('<H',p)[0] in {mapping[i] for i in counts}]
    output=[];inserted=False
    for c,p in rewritten:
        if c==1009 and struct.unpack_from('<H',p)[0]==65534:continue
        if c==1008 and struct.unpack_from('<H',p)[0] in names:p=originals[struct.unpack_from('<H',p)[0]]
        if not inserted and c in (39,4,26,70):output.extend(added);inserted=True
        output.append((c,p))
    if not inserted:raise ValueError('No placement boundary')
    _,raw,body,_=r.p.movie(accepted);start=(5+4*(body[0]>>3)+7)//8+4
    stream=body[:start]+b''.join(f.tag(c,p) for c,p in output)
    native_base,atlas_blocks=original_atlas_art(original,names,out,font)
    candidate=r.p.replace_movie(native_base,b'CFX'+raw[3:4]+struct.pack('<I',len(stream)+8)+zlib.compress(stream))
    final=b.audit.swf_tags(candidate)[2]
    for codes in ({82},{48,75,57,71},{76}):
        if [(c,p) for c,p in tags if c in codes]!=[(c,p) for c,p in final if c in codes]:raise ValueError('ABC/font/SymbolClass changed')
    before=b.font.native.chunks(native_base);after=b.font.native.chunks(candidate)
    if len(before)!=len(after) or [c['tail'] for c in before[1:]]!=[c['tail'] for c in after[1:]]:raise ValueError('Patched original atlases changed')
    if not all(c['crc_valid'] for c in after):raise ValueError('Native CRC failure')
    b.atlas_contract(candidate)
    for d in details:
        d['placements']=counts.get(d['bitmap_id'],0)
        if not d['placements']:d['shape_id']=None
    return candidate,dict(glyphs=details,abc_fonts_exports_unchanged=True,original_atlas_slots=True,patched_blocks=atlas_blocks,new_external_images=0,placement_count=sum(counts.values()),input_sha256=b.audit.sha(accepted),native_base_sha256=b.audit.sha(original),output_sha256=b.audit.sha(candidate))
