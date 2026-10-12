"""Restricted private ABC/font edits in observed CR2W v164 HUD resources.

Not a general CR2W serializer. Preserve tables/properties/atlases verbatim;
replace only the existing framed compressed movie, fix export offsets/CRCs and
header CRC. Native cooker/validator acceptance is a separate required gate.
CRC field layout corroborated against WolvenKit-7 CR2WFile.cs; v164 structure
and DEADBEEF-header CRC independently checked on each actual source.
"""
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    s = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


b = load('build-ink-hud-bars')
audit = b.audit


def header_crc(data):
    header = bytearray(data[:160])
    struct.pack_into('<I', header, 32, 0xDEADBEEF)
    return zlib.crc32(header)


def movie(data):
    pos, signature, tags = audit.swf_tags(data)
    if signature != 'CFX':
        raise ValueError('Observed compressed GFx resource required')
    stream = zlib.decompressobj()
    body = stream.decompress(data[pos+8:])
    if not stream.eof:
        raise ValueError('Incomplete GFx stream')
    size = len(data[pos+8:])-len(stream.unused_data)+8
    return pos, data[pos:pos+size], body, tags


def interaction_shadow(gfx, trial):
    """Copy only the current trial's exact authored prompt shadow record."""
    npc = load('prepare-npc-shadow')
    old_record = struct.pack('<B4B2iHB',2,0,0,0,255,4<<16,4<<16,3<<8,0x21)
    # The v2 trial uses the same accepted 24-byte subdued shadow record.
    shadow = npc.shadow_record(True)
    trial_tags = audit.swf_tags(trial)[2]
    trial_sprite = next(p for c,p in trial_tags if c==39 and struct.unpack_from('<H',p)[0]==216)
    if shadow not in trial_sprite:
        raise ValueError('Deployed trial prompt shadow changed')
    _,raw,body,tags = movie(gfx)
    replacements = {}
    shader = load('prepare-text-shadow')
    rect = (5+4*(body[0]>>3)+7)//8
    paths = shader.payloads(body,rect+4)
    for path,(code,payload) in paths.items():
        if code==70 and b'tfActionName\0' in payload and payload.count(old_record)==1:
            replacements[path] = payload.replace(old_record,shadow)
    if len(replacements)!=1:
        raise ValueError('Missing unique authored action-name filter')
    body = shader.splice(body,rect+4,replacements)
    return b'CFX'+raw[3:4]+struct.pack('<I',len(body)+8)+zlib.compress(body)


def replace_movie(source, gfx):
    if header_crc(source) != struct.unpack_from('<I', source, 32)[0]:
        raise ValueError('Unsupported or invalid source header CRC')
    if struct.unpack_from('<II', source, 24) != (len(source), len(source)):
        raise ValueError('External/trailing buffers unsupported')
    tables = [struct.unpack_from('<III', source, 40+i*12) for i in range(10)]
    if any(tables[i][1] for i in (2,5,6,7,8,9)):
        raise ValueError('Imports/buffer tables outside bounded writer')
    for i, stride in ((0,1),(1,8),(3,16),(4,24)):
        offset, count, crc = tables[i]
        if zlib.crc32(source[offset:offset+count*stride]) != crc:
            raise ValueError('Invalid input table CRC')
    chunks = b.font.native.chunks(source)
    if chunks[0]['class_name'] != 'CSwfResource' or any(c['class_name'] != 'CSwfTexture' for c in chunks[1:]):
        raise ValueError('Only resource plus embedded atlas chunks supported')
    if not all(c['crc_valid'] for c in chunks):
        raise ValueError('Invalid input chunk CRC')
    pos, old, _, _ = movie(source)
    _, replacement, _, _ = movie(gfx)
    if source[pos-4:pos] != struct.pack('<I', len(old)) or pos+len(old)+4 != chunks[0]['offset']+chunks[0]['size']:
        raise ValueError('Unexpected movie framing')
    if source[pos+len(old):pos+len(old)+4] != b'\0'*4:
        raise ValueError('Unexpected resource trailer')
    if old == replacement:
        return source
    delta = len(replacement)-len(old)
    result = bytearray(source[:pos-4]+struct.pack('<I',len(replacement))+replacement+source[pos+len(old):])
    export_offset, count, _ = tables[4]
    for i, chunk in enumerate(chunks):
        record = export_offset+i*24
        size = chunk['size']+(delta if i == 0 else 0)
        offset = chunk['offset']+(delta if i else 0)
        struct.pack_into('<II',result,record+8,size,offset)
        struct.pack_into('<I',result,record+20,zlib.crc32(result[offset:offset+size]))
    struct.pack_into('<I',result,40+4*12+8,zlib.crc32(result[export_offset:export_offset+count*24]))
    struct.pack_into('<II',result,24,len(result),len(result))
    struct.pack_into('<I',result,32,header_crc(result))
    after = b.font.native.chunks(result)
    if not all(c['crc_valid'] for c in after) or header_crc(result) != struct.unpack_from('<I',result,32)[0]:
        raise ValueError('Output CRC verification failed')
    for old_chunk,new_chunk in zip(chunks,after):
        if old_chunk['properties'] != new_chunk['properties']:
            raise ValueError('Resource properties changed')
    if [c['tail'] for c in after[1:]] != [c['tail'] for c in chunks[1:]]:
        raise ValueError('Atlas bytes changed')
    return bytes(result)


def compose(source, changed, added_fonts=(), field=None):
    _, raw, body, tags = movie(source)
    new_tags = audit.swf_tags(changed)[2]
    old_abc = [p for c,p in tags if c==82]
    new_abc = [p for c,p in new_tags if c==82]
    if len(old_abc) != len(new_abc):
        raise ValueError('ABC block count changed')
    # Reuse every original non-ABC tag instead of JPEXS reserialization.
    index = 0
    result = []
    for code,payload in tags:
        if code == 82:
            payload = new_abc[index]
            index += 1
        if field and code==37 and struct.unpack_from('<H',payload)[0]==215:
            result.extend(added_fonts)
            payload = field
        result.append((code,payload))
    rect = (5+4*(body[0]>>3)+7)//8
    body = body[:rect+4]+b''.join(struct.pack('<HI',(c<<6)|63,len(p))+p for c,p in result)
    return b'CFX'+raw[3:4]+struct.pack('<I',len(body)+8)+zlib.compress(body)


def one(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Nonunique source edit: '+before[:70])
    return text.replace(before,after,1)


def transform(name, text):
    if name=='HudModuleBuffs':
        additions = '\n      public var sahCellCount:int = 0;\n'
        additions += ''.join('      public var sahBuffCell'+str(i)+':Object;\n' for i in range(16))
        additions += '''      public function sahRefreshCells():void {
         sahCellCount = this.itemListVector ? Math.min(16, this.itemListVector.length) : 0;
         for (var i:int=0; i<16; i++) {
            this["sahBuffCell"+i] = i < sahCellCount ? this.itemListVector[i] : null;
         }
      }
'''
        return one(text,'      public function HudModuleBuffs()',additions+'      public function HudModuleBuffs()')
    if name=='HudBuff':
        return one(text,'private var expireTween:GTween;',
                   'public var expireTween:GTween;\n      public var sahRendererId:int = 0;')
    if name=='GTween':
        # AS3 sealed classes cannot accept SAHUD's ownership flag as an
        # arbitrary expando. Export the exact property its current script uses.
        return one(text,'      public function GTween(',
                   '      public var sahExpiryOwned:Boolean = false;\n\n      public function GTween(')
    if name=='HudModuleEnemyFocus':
        text = one(text,'import flash.filters.GlowFilter;', 'import flash.filters.GlowFilter;\n   import flash.filters.DropShadowFilter;\n   import flash.events.Event;')
        for old,new in [(7977213,15327954),(13869949,11845792),(16711680,14065811),(16561481,11846353),(5963520,14008462)]:
            text = one(text,'tfName.textColor = '+str(old)+';', 'tfName.textColor = '+str(new)+';')
        text = one(text,'param1 == "enemy" ? 13616301 : this.mcNPCFocus.tfName.textColor', 'this.mcNPCFocus.tfName.textColor')
        text = one(text,'new TextFormat("$TitleFont",22,13616301)', 'new TextFormat("$TitleFont",22,this.iaiNameColor)')
        text = one(text,'new TextFormat("$TitleFont",15,12432026)', 'new TextFormat("$TitleFont",15,this.iaiNameColor)')
        pattern = 'new GlowFilter(789258,0.95,5,5,3,2)'
        if text.count(pattern) != 3:
            raise ValueError('Unexpected name/role filter sites')
        text = text.replace(pattern,'new DropShadowFilter(1,45,1316632,0.6509803922,2,2,1,1,false,false,false)')
        text = one(text,'this.iaiLockRing.alpha = 0.6;', '''this.iaiLockRing.alpha = 0.6;
         if (!this.qfLockCaptured) {
            this.qfLockBaseX = f.mcFocusLock.scaleX;
            this.qfLockBaseY = f.mcFocusLock.scaleY;
            this.qfLockCaptured = true;
         }''')
        # Expose new drawing layers to an original script bridge. Native clips
        # remain alpha-zero data/visibility proxies; no gameplay flags change.
        additions = '''
      private var qfLockBaseX:Number = 1;
      private var qfLockBaseY:Number = 1;
      private var qfLockCaptured:Boolean = false;
      public function qfSyncVisibility():void {
         var f:MovieClip = this.mcNPCFocus;
         if (this.iaiBar) this.iaiBar.visible = f.mcHealthBar.visible || f.mcStaminaBar.visible;
         if (this.iaiLockRing) {
            this.iaiLockRing.visible = f.mcFocusLock.visible;
            var bounds:Rectangle = this.iaiLockRing.getBounds(this.iaiLockRing);
            var sx:Number = this.qfLockBaseX != 0 ? f.mcFocusLock.scaleX / this.qfLockBaseX : 1;
            var sy:Number = this.qfLockBaseY != 0 ? f.mcFocusLock.scaleY / this.qfLockBaseY : 1;
            this.iaiLockRing.scaleX = sx;
            this.iaiLockRing.scaleY = sy;
            this.iaiLockRing.x = (1 - sx) * (bounds.x + bounds.width / 2);
            this.iaiLockRing.y = (1 - sy) * (bounds.y + bounds.height / 2);
         }
         if (this.iaiGhostName) this.iaiGhostName.textColor = this.iaiNameColor;
         if (this.iaiGhostRole) this.iaiGhostRole.textColor = this.iaiNameColor;
      }
'''
        return one(text,'      public function HudModuleEnemyFocus()', additions+'      public function HudModuleEnemyFocus()')
    if name=='HudModuleInteractions':
        text = one(text,'import flash.filters.GlowFilter;', 'import flash.filters.GlowFilter;\n   import flash.filters.DropShadowFilter;')
        text = one(text,'new TextFormat("$TitleFont",17,14071928)', 'new TextFormat("Quiet Folio Utility",17,14071928)')
        text = one(text,'new GlowFilter(789258,0.95,4,4,3,2)', 'new DropShadowFilter(1,45,1316632,0.6509803922,2,2,1,1,false,false,false)')
        # Dynamic NPC-row formatting and restoration both use the trial face.
        text = one(text,'fmt.align = "center";\n               fmt.letterSpacing = 0;', 'fmt.font = "Quiet Folio Utility";\n               fmt.size = 17;\n               fmt.align = "center";\n               fmt.letterSpacing = 0;')
        return text
    raise ValueError('Unknown bounded transform')


def prepare(movie_name, source, probe, out, trial=None):
    out.mkdir(parents=True)
    _, gfx, _, _ = movie(source)
    current = out/'original.gfx'
    current.write_bytes(gfx)
    classes = {'hud_buffs':['HudModuleBuffs','HudBuff','GTween'], 'hud_enemyfocus':['HudModuleEnemyFocus'],
               'hud_interactions':['HudModuleInteractions']}[movie_name]
    edits = []
    for index,name in enumerate(classes):
        files = list(probe.rglob(name+'.as'))
        if len(files)!=1:
            raise ValueError('Missing/ambiguous decompiler source')
        original = files[0].read_text(encoding='utf-8-sig')
        modified = transform(name,original)
        patch = out/(name+'.as')
        patch.write_text(modified, encoding='utf-8', newline='\n')
        namespace = files[0].relative_to(probe/'scripts').with_suffix('').as_posix().replace('/','.')
        dest = out/('changed-'+str(index)+'.gfx')
        command = ['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-replace',str(current),str(dest),namespace,str(patch)]
        p = subprocess.run(command,capture_output=True,timeout=60)
        (out/(name+'.compile.log')).write_bytes(p.stdout+p.stderr)
        if p.returncode or not dest.exists():
            raise ValueError('JPEXS compilation failed: '+name)
        edits.append(dict(class_name=namespace, source_sha256=audit.sha(original.encode()),
                          private_modified_source_sha256=audit.sha(modified.encode()),command=command))
        current = dest
    fonts, field = [], None
    if trial:
        trial_tags = audit.swf_tags(trial)[2]
        fonts = [(c,p) for c,p in trial_tags if c in (48,75) and audit.font_info(c,p)['name']=='Quiet Folio Utility']
        if len(fonts)!=1:
            raise ValueError('Exact trial utility font required')
        code,payload = fonts[0]
        fonts = [(code,struct.pack('<H',60000)+payload[2:])]
        tags = audit.swf_tags(source)[2]
        definitions = {2,6,7,10,11,14,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90,91,1008,1009}
        if any(c in definitions and struct.unpack_from('<H',p)[0]==60000 for c,p in tags):
            raise ValueError('Reserved font ID occupied')
        original = next(p for c,p in tags if c==37 and struct.unpack_from('<H',p)[0]==215)
        field = load('prepare-field-folio').field_binding(original,60000)
        pos = load('build-gentium-swf').prep.rect_end(field,2)
        # HasFont, no FontClass: two flag bytes, font id, then height.
        changed = bytearray(field)
        struct.pack_into('<H',changed,pos+4,340)
        field = bytes(changed)
    combined = compose(source,current.read_bytes(),fonts,field)
    if trial:
        combined = interaction_shadow(combined,trial)
    result = replace_movie(source,combined)
    (out/'candidate.redswf').write_bytes(result)
    (out/'candidate.gfx').write_bytes(combined)
    receipt = dict(input_sha256=audit.sha(source), output_sha256=audit.sha(result), edits=edits,
                   atlas_bytes_unchanged=True, resource_properties_unchanged=True,
                   input_header_crc_verified=True,output_header_crc_verified=True,
                   font_added_from_trial=bool(trial),native_validation_pending=True)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    return result,receipt
