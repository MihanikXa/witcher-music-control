"""Original synthetic refinement regressions; no vendor asset fixtures."""
import importlib.util
from pathlib import Path
import struct
import unittest
import zlib

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('refinement',ROOT/'tools/refine-ink-hud-movies.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)


def native_fixture():
    names=['','CSwfResource','CSwfTexture','textures','array:handle:CSwfTexture','width','height','Uint32','compression','ETextureCompression','TCM_DXTAlpha','textureGroup','CName','GUIWithAlpha','linkageName','String']
    strings=b'';records=b''
    for name in names:
        records+=struct.pack('<II',len(strings),0);strings+=name.encode()+b'\0'
    def prop(name,typ,value):return struct.pack('<HHI',names.index(name),names.index(typ),len(value)+4)+value
    resource=b'\0'+prop('textures','array:handle:CSwfTexture',struct.pack('<II',1,2))+b'\0\0'
    texture=b'\0'+prop('width','Uint32',struct.pack('<I',4))+prop('height','Uint32',struct.pack('<I',4))
    texture+=prop('compression','ETextureCompression',struct.pack('<H',10))+prop('textureGroup','CName',struct.pack('<H',13))
    texture+=prop('linkageName','String',b'\x8bfixture.dds')+b'\0\0'+struct.pack('<7I',0,1,4,4,16,16,16)+r.encode_block([(0,0,0,0)]*16)
    # fixture.dds is eleven bytes including its spelling, String header count=11.
    eo=160+len(strings)+len(records);offset=eo+48;exports=b''
    for cls,body in ((1,resource),(2,texture)):
        exports+=struct.pack('<HHIIIII',cls,8192,0,len(body),offset,0,zlib.crc32(body));offset+=len(body)
    header=bytearray(160);header[:8]=b'CR2W'+struct.pack('<I',164)
    for i,pos,value,count in [(0,160,strings,len(strings)),(1,160+len(strings),records,len(names)),(4,eo,exports,2)]:struct.pack_into('<III',header,40+i*12,pos,count,zlib.crc32(value))
    struct.pack_into('<II',header,24,offset,offset);struct.pack_into('<I',header,32,r.p.header_crc(header))
    return bytes(header)+strings+records+exports+resource+texture


class RefinementTests(unittest.TestCase):
    def test_method_keeps_signature(self):
        text='public function draw(v:Number) : void { if (v) { old(); } }\npublic function rest():void { keep(); }'
        result=r.method(text,'draw','         replacement();')
        self.assertIn('public function draw(v:Number) : void',result)
        self.assertIn('replacement();',result)
        self.assertNotIn('old();',result)
        self.assertIn('public function rest():void { keep(); }',result)

    def test_unknown_method_rejected(self):
        with self.assertRaises(ValueError):r.method('','unknown','')

    def test_palette_distinct_and_bounded(self):
        self.assertEqual(len(set(new for old,new in r.PALETTE.values())),5)
        for old,new in r.PALETTE.values():
            before=[old>>n&255 for n in (16,8,0)];after=[new>>n&255 for n in (16,8,0)]
            self.assertLessEqual(max(abs(a-b) for a,b in zip(before,after)),20)
            self.assertLess(max(after)-min(after),110)

    def test_bc3_constant_opacity(self):
        for alpha in (0,166,255):
            pixels=[(239,227,206,alpha)]*16
            decoded=r.decode_block(r.encode_block(pixels))
            self.assertTrue(all(p[3]==alpha for p in decoded))
            self.assertEqual(len(set(p[:3] for p in decoded)),1)

    def test_bc3_alpha_ramp(self):
        pixels=[(239,227,206,i*17) for i in range(16)]
        decoded=r.decode_block(r.encode_block(pixels))
        self.assertLessEqual(max(abs(a[3]-b[3]) for a,b in zip(pixels,decoded)),18)

    def test_flat_backing_retains_two_uniform_regions(self):
        pixels=[(20,23,24,224)]*8+[(239,227,206,255)]*8
        result=r.decode_block(r.encode_block(pixels))
        self.assertEqual(len(set(p[:3] for p in result[:8])),1)
        self.assertEqual(len(set(p[:3] for p in result[8:])),1)
        self.assertLess(max(result[0][:3]),32)
        self.assertGreater(min(result[-1][:3]),200)

    def test_rgb565_extremes(self):
        self.assertEqual(r.rgb565(0),(0,0,0))
        self.assertEqual(r.rgb565(65535),(255,255,255))

    def test_soft_effect_preserves_source_compositing(self):
        import xml.etree.ElementTree as E
        effect=E.fromstring('<item type="DROPSHADOWFILTER" blurX="4" blurY="4" strength="20" angle="0" innerShadow="false" knockout="false" compositeSource="true" passes="3"><dropShadowColor red="0" green="0" blue="0" alpha="255"/></item>')
        out=r.shadow.shadow(effect)
        self.assertEqual(out.get('angle'),'0')
        self.assertEqual(out.get('passes'),'3')
        self.assertEqual(out.get('strength'),'1.0')
        self.assertEqual(out.find('dropShadowColor').get('alpha'),'166')

    def test_semantic_effect_rejected(self):
        import xml.etree.ElementTree as E
        effect=E.fromstring('<item type="GLOWFILTER"><glowColor red="1" green="0" blue="0" alpha="255"/></item>')
        with self.assertRaises(ValueError):r.shadow.shadow(effect)

    def test_native_color_difference(self):
        # One BC3 constant cannot encode a baked bevel or color gradient.
        data=r.encode_block([(239,227,206,255)]*16)
        self.assertEqual(struct.unpack('<HH',data[8:12])[0],struct.unpack('<HH',data[8:12])[1])

    def test_private_atlas_append_retains_original_pixels(self):
        original=native_fixture();before=r.b.font.native.chunks(original)
        after=r.append_atlas(original,'private.dds',4,4,r.encode_block([(239,227,206,255)]*16))
        chunks=r.b.font.native.chunks(after)
        self.assertEqual(len(chunks),3)
        self.assertEqual(chunks[1]['tail'],before[1]['tail'])
        self.assertEqual(chunks[0]['properties']['textures']['value'],'020000000200000003000000')
        self.assertTrue(all(c['crc_valid'] for c in chunks))
        self.assertEqual(r.p.header_crc(after),struct.unpack_from('<I',after,32)[0])

    def test_private_atlas_length_rejected(self):
        with self.assertRaisesRegex(ValueError,'Fixed-length'):r.append_atlas(native_fixture(),'different-long-name.dds',4,4,b'\0'*16)

    def test_external_native_buffers_rejected(self):
        original=bytearray(native_fixture());struct.pack_into('<I',original,40+5*12+4,1)
        with self.assertRaisesRegex(ValueError,'self-contained'):r.append_atlas(bytes(original),'private.dds',4,4,b'\0'*16)


if __name__=='__main__':unittest.main()
