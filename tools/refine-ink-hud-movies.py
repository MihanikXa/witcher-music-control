"""Original bounded private v2 edits; no vendor source or assets in this file.

Retains ABC contracts, authored timelines and dictionary IDs. A separate private atlas supplies existing Xbox image IDs; original texture
chunks and other image rectangles remain unchanged.
"""
import copy
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    s = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


b = load('build-ink-hud-batch')
p = b.patcher
shadow = load('prepare-text-shadow')
PALETTE = {'neutral': (0xE9E2D2, 0xEEE3CF), 'friendly': (0xB4C0A0, 0xAEC795),
           'hostile': (0xD6A093, 0xDE9C89), 'Axii': (0xB4C2D1, 0xA8C5DF),
           'VIP': (0xD5C08E, 0xDFC183)}
SOFT = 'new DropShadowFilter(1,45,1316632,0.6509803922,2,2,1,1,false,false,false)'


def method(text, name, body):
    match = re.search(r'(\bfunction '+re.escape(name)+r'\([^)]*\)\s*:\s*[\w*]+\s*)\{', text)
    if not match: raise ValueError('Missing bounded method '+name)
    start = match.end()-1; depth = 1; end = start+1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[:start]+'{\n'+body+'\n      }'+text[end:]


def enemy(text):
    for old,new in PALETTE.values():
        text = p.one(text,'tfName.textColor = '+str(old)+';', 'tfName.textColor = '+str(new)+';')
    text = p.one(text,'Math.round(hb.y + hb.height / 2 - 3),150,6', 'Math.round(hb.y + hb.height / 2 - 1.9),150,3.8')
    text = p.one(text,'this.iaiHealthRect.bottom + 5', 'this.iaiHealthRect.bottom + 3')
    text = p.one(text,'new TextFormat("$TitleFont",21,this.iaiNameColor)', 'new TextFormat("$TitleFont",19,this.iaiNameColor)')
    text = p.one(text,'r.y - 30', 'r.y - 25')
    text = p.one(text,'r.y - 10 - tf.getLineMetrics(0).ascent', 'r.y - 5 - tf.getLineMetrics(0).ascent')
    text = p.one(text,'new TextFormat("$TitleFont",22,this.iaiNameColor)', 'new TextFormat("$TitleFont",20,this.iaiNameColor)')
    text = p.one(text,'new TextFormat("$TitleFont",15,this.iaiNameColor)', 'new TextFormat("$TitleFont",14,this.iaiNameColor)')
    text = p.one(text,'tf.textHeight + 5', 'tf.textHeight + 2')
    text = p.one(text,'Math.round(ly + 5)', 'Math.round(ly + 2)')
    text = p.one(text,'fmt.letterSpacing = 2;', 'fmt.letterSpacing = 1;')
    # Friendly ghost/role names share the same compact hierarchy. Remove only
    # the decorative rule/lozenge, retaining role data and placement protocol.
    start = text.index('         hw = Math.max(60,')
    end = text.index('         return bottom;',start)
    text = text[:start]+'         g.lineStyle();\n'+text[end:]
    text = p.one(text,'private var iaiNpcNoRole:Number = 22;', 'private var iaiNpcNoRole:Number = 12;')
    text = p.one(text,'this.iaiDrawBar(g,this.iaiHealthRect,this.iaiValue,this.iaiLag,9312788,4);',
                 'this.iaiDrawBar(g,this.iaiHealthRect,this.iaiValue,this.iaiLag,11171173,0);') # AA7565
    text = method(text,'iaiDrawBar','''         var w:Number = r.width * v;
         g.beginFill(1316632,0.82);
         g.drawRect(r.x - 0.5,r.y - 0.5,r.width + 1,r.height + 1);
         g.endFill();
         if (lag > v) {
            g.beginFill(0xC3A18F,0.85);
            g.drawRect(r.x+w,r.y,r.width*(lag-v),r.height);
            g.endFill();
         }
         if (w > 0.5) {
            g.beginFill(col,1);
            g.drawRect(r.x,r.y,w,r.height);
            g.endFill();
         }
         g.lineStyle();''')
    # Retain level/skull hierarchy but drop the framed background.
    text = p.one(text,'g.drawRect(cx - 13,cy - 10,26,20);','g.drawRect(cx - 10,cy - 8,20,16);')
    text = p.one(text,'g.lineStyle(1,st == "highLevel" || st == "deadlyLevel" ? 9312788 : 7828330,1);',
                 'g.lineStyle(0,0,0);')
    text = p.one(text,'g.drawRect(cx - 13.5,cy - 10.5,27,21);','// No decorative level border.')
    text = text.replace('st == "deadlyLevel" ? 9312788 : 789258','st == "deadlyLevel" ? 11171173 : 1316632')
    text = p.one(text,'         tfl = f.mcEnemyLevel.textField;',
                 '         tfl = f.mcEnemyLevel.textField;\n         tfl.setTextFormat(new TextFormat(null,16));')
    text = p.one(text,'g.drawCircle(cx,cy - 2,5.5);','g.drawCircle(cx,cy - 2,4.2);')
    text = method(text,'iaiSetupLockRing','''         var f:MovieClip = this.mcNPCFocus;
         if (!f.mcFocusLock) return;
         var tb:Rectangle = f.mcEnemyLevel.textField.getBounds(f);
         var cx:Number = Math.round(tb.x + tb.width / 2);
         var cy:Number = this.iaiHealthRect.y + this.iaiHealthRect.height / 2;
         this.iaiLockRight = cx + 15;
         this.iaiLockRing = new Shape();
         this.iaiLockRing.graphics.lineStyle(1,this.iaiLockGold ? 0xB4A471 : 0xAAA698,0.8);
         this.iaiLockRing.graphics.drawCircle(cx,cy,13);
         this.iaiLockRing.alpha = 0.6;
         if (!this.qfLockCaptured) {
            this.qfLockBaseX = f.mcFocusLock.scaleX;
            this.qfLockBaseY = f.mcFocusLock.scaleY;
            this.qfLockCaptured = true;
         }
         f.addChildAt(this.iaiLockRing,f.getChildIndex(this.iaiBar)+1);
         f.mcFocusLock.alpha = 0;
         this.iaiLockRing.visible = f.mcFocusLock.visible;''')
    setup = '''         if (f.mcCharacterIcon) { f.mcCharacterIcon.scaleX *= 0.8; f.mcCharacterIcon.scaleY *= 0.8; }
         if (f.mcDodgeFeedback) { f.mcDodgeFeedback.scaleX *= 0.8; f.mcDodgeFeedback.scaleY *= 0.8; }
'''
    text = p.one(text,'         this.iaiHideLevelArt();\n         this.iaiSetupLockRing();',setup+'         this.iaiHideLevelArt();\n         this.iaiSetupLockRing();')
    # Repair an accepted-v4 script paint if it lands after setEnemyType. The
    # original v4 package stays enabled; already revised/unknown colors untouched.
    cases = '\n'.join('            case '+str(old)+': f.tfName.textColor = '+str(new)+'; break;' for old,new in PALETTE.values())
    sync = '''         switch (f.tfName.textColor) {
'''+cases+'''
         }
         this.iaiNameColor = f.tfName.textColor;
         if (this.iaiRoleTf) this.iaiRoleTf.textColor = this.iaiNameColor;
'''
    text = p.one(text,'         if(this.iaiGhostName)\n',sync+'         if(this.iaiGhostName)\n')
    return text


def option(text):
    text = p.one(text,'var sz:Number = 23;', 'var sz:Number = 21;')
    text = p.one(text,'sz = Math.round(sz / 0.88);', 'sz = Math.round(sz / 0.88 * 0.82);')
    text = p.one(text,'new TextFormat("$TitleFont",15,14198849)', 'new TextFormat("$TitleFont",13,14198849)')
    text = p.one(text,'new DropShadowFilter(2,90,0,0.95,5,5,1.6,2),new GlowFilter(0,0.55,10,10,1.3,2)', SOFT)
    text = p.one(text,'new DropShadowFilter(1,90,0,0.95,4,4,1.6,2)',SOFT)
    text = p.one(text,'this.mcHitTest.height = this.tfLine.height;', 'this.mcHitTest.height = Math.max(35,this.tfLine.height);')
    return text


def option_container(text):
    text = p.one(text,'DIALOG_STEP_Y:Number = 40;', 'DIALOG_STEP_Y:Number = 36;')
    return p.one(text,'DIALOG_STEP_Y_EXTRA:Number = 35;', 'DIALOG_STEP_Y_EXTRA:Number = 29;')


def compile_classes(source, before, out, transforms, cache=None):
    out.mkdir(parents=True)
    current = out/'input.gfx'; current.write_bytes(p.movie(source)[1])
    changes=[]
    for name,transform in transforms.items():
        paths=list(before.rglob(name+'.as'))
        if len(paths)!=1: raise ValueError('Nonunique class '+name)
        path=paths[0]; original=path.read_text(encoding='utf-8-sig'); modified=transform(original)
        patch=out/(name+'.as');patch.write_text(modified,encoding='utf-8',newline='\n')
        namespace=path.relative_to(before/'scripts').with_suffix('').as_posix().replace('/','.')
        dest=out/(name+'.gfx')
        cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-replace',str(current),str(dest),namespace,str(patch)]
        reused=False
        if cache:
            b.font.private_path(cache.resolve())
            original_input=cache/('input.gfx' if not changes else list(transforms)[len(changes)-1]+'.gfx')
            if original_input.read_bytes()!=current.read_bytes() or (cache/(name+'.as')).read_text(encoding='utf-8-sig')!=modified:raise ValueError('Cached AS compile inputs changed')
            log=(cache/(name+'.compile.log')).read_bytes();data=(cache/(name+'.gfx')).read_bytes()
            if b'Error' in log or len([v for c,v in b.audit.swf_tags(data)[2] if c==82])!=len([v for c,v in b.audit.swf_tags(current.read_bytes())[2] if c==82]):raise ValueError('Cached compiler result invalid')
            dest.write_bytes(data);(out/(name+'.compile.log')).write_bytes(log);reused=True
        else:
            proc=subprocess.run(cmd,capture_output=True,timeout=90)
            (out/(name+'.compile.log')).write_bytes(proc.stdout+proc.stderr)
            if proc.returncode or not dest.exists():raise ValueError('Class compile failed '+name)
        changes.append(dict(class_name=namespace,input_sha256=b.audit.sha(original.encode()),output_sha256=b.audit.sha(modified.encode()),compiled_gfx_sha256=b.fallback.sha(dest),compile_reused=reused,compile_cache=str(cache) if reused else None))
        current=dest
    gfx=p.compose(source,current.read_bytes())
    return p.replace_movie(source,gfx),changes


def soften_authored(source, out, names):
    """Independent XML serialization of explicitly named text placements only."""
    out.mkdir(parents=True)
    gfx=out/'original.gfx';gfx.write_bytes(p.movie(source)[1])
    def run(label,*args):
        proc=subprocess.run(['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),*map(str,args)],capture_output=True,timeout=90)
        (out/(label+'.log')).write_bytes(proc.stdout+proc.stderr)
        if proc.returncode:raise ValueError('XML stage failed '+label)
    run('export','-swf2xml',gfx,out/'before.xml')
    original=ET.parse(out/'before.xml').getroot();changed=copy.deepcopy(original)
    paths=shadow.locations(changed); edits=[]; approved=set()
    for path,node in paths:
        if node.get('type')!='PlaceObject3Tag' or node.get('name') not in names:continue
        effects=node.find('surfaceFilterList')
        if effects is None:continue
        for i,effect in enumerate(effects):
            color=effect.find('glowColor' if effect.get('type')=='GLOWFILTER' else 'dropShadowColor')
            if color is None:continue
            if all(int(color.get(c))==0 for c in ('red','green','blue')) and float(effect.get('strength','0'))>1:
                effects[i]=shadow.shadow(effect);approved.add(path)
                edits.append(dict(path=list(path),field=node.get('name'),before=effect.attrib,after=effects[i].attrib))
    if not edits:return source,[]
    ET.ElementTree(changed).write(out/'changed.xml',encoding='utf-8',xml_declaration=True)
    run('unchanged','-xml2swf',out/'before.xml',out/'unchanged.swf')
    run('changed','-xml2swf',out/'changed.xml',out/'changed.swf')
    _,raw,body,tags=p.movie(source);start=(5+4*(body[0]>>3)+7)//8+4
    body,trailer=split_export_padding(body,start,struct.unpack_from('<I',raw,4)[0]-8)
    old=shadow.payloads(body,start)
    def decoded(path):
        data=path.read_bytes()
        return p.movie(data)[2] if data.startswith(b'CFX') else shadow.npc.body(data)
    unchanged=shadow.payloads(decoded(out/'unchanged.swf'),start)
    modified=shadow.payloads(decoded(out/'changed.swf'),start)
    if any(old[q]!=unchanged[q] for q in approved):raise ValueError('Selected placement round-trip differs')
    final=shadow.splice(body,start,{q:modified[q][1] for q in approved})
    gfx=b'CFX'+raw[3:4]+struct.pack('<I',len(final)+8)+zlib.compress(final+trailer)
    result=p.replace_movie(source,gfx)
    (out/'verified.gfx').write_bytes(gfx);run('verify','-swf2xml',out/'verified.gfx',out/'verified.xml')
    if shadow.npc.canonical(ET.parse(out/'verified.xml').getroot())!=shadow.npc.canonical(changed):
        raise ValueError('Independent selected-filter XML delta differs')
    return result,edits


def split_export_padding(body,start,declared):
    """Retain observed allocation tail beyond an exact declared End boundary.

    Installed oneliners has 81,920 decompressed bytes, declared 79,747 body
    bytes ending at End. The remainder is opaque; exporter allocation padding is an inference.
    Never parse it as tags or silently discard it. Reject any other mismatch.
    """
    try:
        shadow.npc.records(body,start)
        return body,b''
    except ValueError:
        if not start<declared<len(body) or len(body)%4096:raise
        shadow.npc.records(body[:declared],start)
        return body[:declared],body[declared:]


def rgb565(value):
    return ((value>>11&31)*255//31,(value>>5&63)*255//63,(value&31)*255//31)


def decode_block(block):
    a0,a1=block[:2];bits=int.from_bytes(block[2:8],'little')
    alpha=[a0,a1]+([( (7-i)*a0+i*a1)//7 for i in range(1,7)] if a0>a1 else [((5-i)*a0+i*a1)//5 for i in range(1,5)]+[0,255])
    c0,c1,indices=struct.unpack('<HHI',block[8:]);c0,c1=rgb565(c0),rgb565(c1)
    colors=[c0,c1,tuple((2*x+y)//3 for x,y in zip(c0,c1)),tuple((x+2*y)//3 for x,y in zip(c0,c1))]
    return [colors[indices>>(2*i)&3]+(alpha[bits>>(3*i)&7],) for i in range(16)]


def encode_block(pixels):
    """Flat ivory/charcoal regions, antialiased edges; no baked shading."""
    color=(29<<11)|(56<<5)|25
    a=[v[3] for v in pixels];a0,a1=max(a),min(a)
    table=[a0,a1]+([((7-i)*a0+i*a1)//7 for i in range(1,7)] if a0>a1 else [((5-i)*a0+i*a1)//5 for i in range(1,5)]+[0,255])
    bits=sum(min(range(8),key=lambda j:abs(table[j]-v))<<(3*i) for i,v in enumerate(a))
    dark=(2<<11)|(5<<5)|3
    second=dark if any(v[3] and min(v[:3])<100 for v in pixels) else color
    c0,c1=rgb565(color),rgb565(second)
    palette=[c0,c1,tuple((2*x+y)//3 for x,y in zip(c0,c1)),tuple((x+2*y)//3 for x,y in zip(c0,c1))]
    indices=sum(min(range(4),key=lambda j:sum((palette[j][k]-v[k])**2 for k in range(3)))<<(2*i) for i,v in enumerate(pixels))
    return bytes((a0,a1))+bits.to_bytes(6,'little')+struct.pack('<HHI',color,second,indices)


def glyph(name,width,height,font_path):
    from PIL import Image,ImageDraw,ImageFont
    factor=4;im=Image.new('RGBA',(width*factor,height*factor));d=ImageDraw.Draw(im)
    w,h=im.size;cx,cy=w/2,h/2;unit=min(w,h);stroke=max(4,round(unit*.023));color=(239,227,206,255);backing=(20,23,24,224)
    label=name.split('ICO_Xbox_',1)[1].split('.',1)[0]
    radius=unit*.32
    if 'dpad' in label:
        arm=unit*.12;extent=unit*.30
        pts=[(cx-arm,cy-extent),(cx+arm,cy-extent),(cx+arm,cy-arm),(cx+extent,cy-arm),(cx+extent,cy+arm),(cx+arm,cy+arm),(cx+arm,cy+extent),(cx-arm,cy+extent),(cx-arm,cy+arm),(cx-extent,cy+arm),(cx-extent,cy-arm),(cx-arm,cy-arm),(cx-arm,cy-extent)]
        d.polygon(pts,fill=backing);d.line(pts,fill=color,width=stroke,joint='curve')
        directions=[s for s in ['left','right','up','down'] if s in label]
        for direction in directions:
            x,y={'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}[direction]
            px,py=cx+x*unit*.22,cy+y*unit*.22
            d.ellipse((px-unit*.035,py-unit*.035,px+unit*.035,py+unit*.035),fill=color)
    else:
        text=label
        if label.startswith(('L_','R_')):text=label[0]
        if label in ('Start','Menu'):text='\u2261'
        if label in ('Back','View'):text='\u25a3'
        if label=='Home':text='X'
        pill=label in ('LB','RB','LT','RT','Start','Back','Home','Menu','View')
        if pill:d.rounded_rectangle((cx-unit*.40,cy-unit*.25,cx+unit*.40,cy+unit*.25),radius=unit*.07,fill=backing,outline=color,width=stroke)
        else:d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=backing,outline=color,width=stroke)
        size=round(unit*(.26 if len(text)>1 else .36));font=ImageFont.truetype(str(font_path),max(8,size))
        box=d.textbbox((0,0),text,font=font);d.text((cx-(box[2]-box[0])/2-box[0],cy-(box[3]-box[1])/2-box[1]),text,font=font,fill=color)
        if label.startswith(('L_','R_')):
            direction=label.split('_',1)[1];ux,uy={'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}.get(direction,(0,0))
            if ux or uy:
                tx,ty=cx+ux*unit*.43,cy+uy*unit*.43
                d.polygon([(tx+ux*unit*.07,ty+uy*unit*.07),(tx-uy*unit*.055,ty+ux*unit*.055),(tx+uy*unit*.055,ty-ux*unit*.055)],fill=color)
            elif direction=='hold':
                d.arc((cx-unit*.42,cy-unit*.42,cx+unit*.42,cy+unit*.42),25,320,fill=color,width=stroke)
            elif direction in ('scroll','tabs'):
                for sign in (-1,1):
                    ax,ay=(0,sign) if direction=='scroll' else (sign,0)
                    tx,ty=cx+ax*unit*.43,cy+ay*unit*.43
                    d.polygon([(tx+ax*unit*.07,ty+ay*unit*.07),(tx-ay*unit*.055,ty+ax*unit*.055),(tx+ay*unit*.055,ty-ax*unit*.055)],fill=color)
    return im.resize((width,height),Image.Resampling.LANCZOS)


def property_slots(data,chunk):
    so,ss,_=struct.unpack_from('<III',data,40);no,count,_=struct.unpack_from('<III',data,52)
    names=[]
    for i in range(count):
        start=so+struct.unpack_from('<I',data,no+i*8)[0]
        names.append(data[start:data.index(0,start,so+ss)].decode())
    pos=chunk['offset']+1;result={}
    while struct.unpack_from('<H',data,pos)[0]:
        ident,typ,length=struct.unpack_from('<HHI',data,pos)
        result[names[ident]]=(pos+8,length-4);pos+=4+length
    return result


def append_atlas(source,linkage,width,height,pixels):
    """Observed self-contained resource: append one cloned texture export.

    Original texture chunks remain verbatim. Only resource texture handles,
    export offsets/CRCs/header sizes change. Native cooker is the release gate.
    """
    chunks=b.font.native.chunks(source)
    if len(chunks)<2 or not all(c['crc_valid'] for c in chunks):raise ValueError('Embedded texture template required')
    tables=[struct.unpack_from('<III',source,40+i*12) for i in range(10)]
    if any(tables[i][1] for i in (2,5,6,7,8,9)) or chunks[-1]['offset']+chunks[-1]['size']!=len(source):raise ValueError('Only self-contained texture exports supported')
    eo,count,_=tables[4]
    if count!=len(chunks) or chunks[0]['offset']!=eo+count*24 or any(a['offset']+a['size']!=c['offset'] for a,c in zip(chunks,chunks[1:])):raise ValueError('Noncontiguous native chunks unsupported')
    resource=chunks[0];first=bytearray(source[resource['offset']:resource['offset']+resource['size']])
    absolute,length=property_slots(source,resource)['textures'];pos=absolute-resource['offset']
    expected=struct.pack('<I',count-1)+b''.join(struct.pack('<I',i) for i in range(2,count+1))
    if bytes(first[pos:pos+length])!=expected:raise ValueError('Unexpected texture handles')
    handles=struct.pack('<I',count)+expected[4:]+struct.pack('<I',count+1)
    first[pos:pos+length]=handles;struct.pack_into('<I',first,pos-4,len(handles)+4)
    template=chunks[1];texture=bytearray(source[template['offset']:template['offset']+template['size']])
    slots=property_slots(source,template)
    for name,value in [('width',width),('height',height)]:
        absolute,length=slots[name]
        if length!=4:raise ValueError('Texture dimension not Uint32')
        struct.pack_into('<I',texture,absolute-template['offset'],value)
    absolute,length=slots['linkageName'];pos=absolute-template['offset']
    encoded=bytes((0x80|len(linkage),))+linkage.encode('ascii')
    if len(encoded)!=length or len(linkage)>=64:raise ValueError('Fixed-length native linkage required')
    texture[pos:pos+length]=encoded
    tail=len(texture)-len(template['tail'])
    texture[tail:]=struct.pack('<7I',0,1,width,height,width*4,len(pixels),16)+pixels
    bodies=[bytes(first)]+[source[c['offset']:c['offset']+c['size']] for c in chunks[1:]]+[bytes(texture)]
    records=[];offset=eo+(count+1)*24
    for i,body in enumerate(bodies):
        original=source[eo+(i if i<count else 1)*24:eo+(i if i<count else 1)*24+24]
        record=bytearray(original);struct.pack_into('<II',record,8,len(body),offset);struct.pack_into('<I',record,20,zlib.crc32(body))
        records.append(bytes(record));offset+=len(body)
    result=bytearray(source[:eo]+b''.join(records)+b''.join(bodies))
    struct.pack_into('<III',result,40+4*12,eo,count+1,zlib.crc32(b''.join(records)))
    struct.pack_into('<II',result,24,len(result),len(result));struct.pack_into('<I',result,32,p.header_crc(result))
    final=b.font.native.chunks(result)
    if [c['tail'] for c in final[1:-1]]!=[c['tail'] for c in chunks[1:]] or not all(c['crc_valid'] for c in final):raise ValueError('Original atlas changed or new CRC invalid')
    return bytes(result)


def flat_glyphs(source,out,font_path):
    from PIL import Image
    tags=b.audit.swf_tags(source)[2];symbols=b.contracts.symbols(tags)
    names={v:k for k,v in symbols.items() if 'ICO_Xbox_' in k}
    if not names:return source,[]
    out.mkdir(parents=True,exist_ok=True)
    rectangles={}
    for code,value in tags:
        if code==1008:
            cid,img,x1,y1,x2,y2=struct.unpack('<6H',value)
            if cid in names:rectangles[cid]=(x1,y1,x2,y2)
    if set(rectangles)!=set(names):raise ValueError('Xbox symbol lacks subimage')
    if any(x2-x1>64 or y2-y1>64 for x1,y1,x2,y2 in rectangles.values()):raise ValueError('Glyph exceeds fixed private atlas cell')
    image_tags=[v for c,v in tags if c==1009];image_ids={struct.unpack_from('<H',v)[0] for v in image_tags};newid=65534
    if newid in image_ids:raise ValueError('Private image ID occupied')
    chunks=b.font.native.chunks(source);oldlink=chunks[1]['properties']['linkageName']['value'];linkage='qf2-'+oldlink[4:]
    if linkage in {c['properties']['linkageName']['value'] for c in chunks[1:]}:raise ValueError('Private atlas linkage occupied')
    width=512;height=((len(names)+7)//8)*64;image=Image.new('RGBA',(width,height));changes=[];positions={}
    for i,(cid,name) in enumerate(sorted(names.items())):
        x,y=i%8*64,i//8*64;x1,y1,x2,y2=rectangles[cid];w,h=x2-x1,y2-y1
        fresh=glyph(name,w,h,font_path);image.paste(fresh,(x,y));fresh.save(out/(str(cid)+'-'+name.replace('.','_')+'.png'))
        positions[cid]=(x,y,x+w,y+h);changes.append(dict(symbol=name,id=cid,original_rectangle=list(rectangles[cid]),private_rectangle=list(positions[cid]),atlas=linkage,flat_rgb='#EFE3CE',flat_backing_rgb='#141718',backing_alpha=224))
    pixels=bytearray()
    for y in range(0,height,4):
        for x in range(0,width,4):pixels.extend(encode_block([image.getpixel((x+i%4,y+i//4)) for i in range(16)]))
    image.save(out/'flat-xbox-atlas.png')
    template=image_tags[0];pos=11+template[10];length=template[pos]
    export_name=('QF_FlatXbox_'+b.audit.sha(linkage.encode())[:12]).encode()
    newimage=bytearray(template[:10]+bytes((len(export_name),))+export_name+bytes((len(linkage),))+linkage.encode()+template[pos+1+length:])
    struct.pack_into('<H',newimage,0,newid);struct.pack_into('<HH',newimage,6,width,height)
    _,raw,body,_=p.movie(source);start=(5+4*(body[0]>>3)+7)//8+4;rewritten=[];inserted=False
    for code,value in tags:
        if code==1008 and not inserted:rewritten.append((1009,bytes(newimage)));inserted=True
        if code==1008:
            cid=struct.unpack_from('<H',value)[0]
            if cid in names:value=struct.pack('<6H',cid,newid,*positions[cid])
        rewritten.append((code,value))
    stream=body[:start]+b''.join(struct.pack('<HI',(c<<6)|63,len(v))+v for c,v in rewritten)
    gfx=b'CFX'+raw[3:4]+struct.pack('<I',len(stream)+8)+zlib.compress(stream)
    result=append_atlas(p.replace_movie(source,gfx),linkage,width,height,bytes(pixels))
    b.atlas_contract(result)
    return result,changes
