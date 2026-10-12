"""Bounded movie writer and atomic rollback checks; no proprietary fixtures."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p = load('patch-ink-hud-movies')
b = load('build-ink-hud-batch')


def gfx(extra=b''):
    body = b'\x08\x00\x00\x1e\x01\x00'
    if extra:
        body += struct.pack('<HI',(82<<6)|63,len(extra))+extra
    body += b'\0\0'
    return b'CFX\x0a'+struct.pack('<I',len(body)+8)+zlib.compress(body)


def resource(movie=None):
    movie = movie or gfx()
    strings = b'\0CSwfResource\0'
    names = struct.pack('<IIII',0,0,1,0)
    export_offset = 160+len(strings)+len(names)
    chunk_offset = export_offset+24
    chunk = b'\0\0\0'+struct.pack('<I',len(movie))+movie+b'\0'*4
    exports = struct.pack('<HHIIIII',1,8192,0,len(chunk),chunk_offset,0,zlib.crc32(chunk))
    header = bytearray(160)
    header[:8] = b'CR2W'+struct.pack('<I',164)
    for index,offset,data,count in [(0,160,strings,len(strings)),(1,160+len(strings),names,2),
                                    (4,export_offset,exports,1)]:
        struct.pack_into('<III',header,40+index*12,offset,count,zlib.crc32(data))
    length = chunk_offset+len(chunk)
    struct.pack_into('<II',header,24,length,length)
    struct.pack_into('<I',header,32,p.header_crc(header))
    return bytes(header)+strings+names+exports+chunk


def refresh_header(data):
    struct.pack_into('<I',data,32,p.header_crc(data))
    return bytes(data)


class BoundedWriterTests(unittest.TestCase):
    def test_noop_identity_and_new_movie(self):
        original = resource()
        self.assertEqual(p.replace_movie(original,gfx()),original)
        changed = p.replace_movie(original,gfx(b'changed ABC payload'))
        self.assertNotEqual(original,changed)
        self.assertEqual(p.movie(changed)[1],gfx(b'changed ABC payload'))
        self.assertTrue(all(c['crc_valid'] for c in p.b.font.native.chunks(changed)))
        self.assertEqual(p.header_crc(changed),struct.unpack_from('<I',changed,32)[0])

    def test_invalid_header_rejected(self):
        data = bytearray(resource())
        data[12] ^= 1
        with self.assertRaisesRegex(ValueError,'header CRC'):
            p.replace_movie(bytes(data),gfx())

    def test_bad_export_crc_rejected(self):
        data = bytearray(resource())
        offset = struct.unpack_from('<I',data,88)[0]
        data[offset+22] ^= 1
        with self.assertRaisesRegex(ValueError,'table CRC'):
            p.replace_movie(refresh_header(data),gfx())

    def test_bad_chunk_crc_rejected(self):
        data = bytearray(resource())
        data[-1] = 1
        with self.assertRaisesRegex(ValueError,'chunk CRC'):
            p.replace_movie(bytes(data),gfx())

    def test_external_buffer_rejected(self):
        data = bytearray(resource())
        struct.pack_into('<I',data,28,len(data)+1)
        with self.assertRaisesRegex(ValueError,'buffers'):
            p.replace_movie(refresh_header(data),gfx())

    def test_unsupported_import_table_rejected(self):
        data = bytearray(resource())
        struct.pack_into('<I',data,40+2*12+4,1)
        with self.assertRaisesRegex(ValueError,'Imports'):
            p.replace_movie(refresh_header(data),gfx())

    def test_abc_cardinality_rejected(self):
        with self.assertRaisesRegex(ValueError,'ABC block count'):
            p.compose(resource(),gfx(b'new block'))

    def test_movie_truncation_rejected(self):
        with self.assertRaises(ValueError):
            p.movie(gfx()[:-3])

    def test_added_font_precedes_its_edit_text(self):
        def with_tags(tags):
            body = b'\x08\x00\x00\x1e\x01\x00'+b''.join(
                struct.pack('<HI',(c<<6)|63,len(v))+v for c,v in tags)
            return b'CFX\x0a'+struct.pack('<I',len(body)+8)+zlib.compress(body)
        old_field = struct.pack('<H',215)+b'old field'
        new_field = struct.pack('<H',215)+b'new field'
        original = with_tags([(37,old_field),(0,b'')])
        font = (75,struct.pack('<H',60000)+b'new font')
        tags = p.audit.swf_tags(p.compose(original,original,[font],new_field))[2]
        self.assertEqual(tags,[(75,font[1]),(37,new_field),(0,b'')])


class RollbackTests(unittest.TestCase):
    def test_enemy_and_interaction_atomic(self):
        selected = b.selection(['enemyfocus'])
        self.assertFalse({'enemyfocus','interactions'} & selected)
        self.assertIn('buffs',selected)
        self.assertNotIn('inkIronNpcPlate',b.selected_scripts(selected))

    def test_horse_pair_atomic(self):
        selected = b.selection(['horsepanicbar'])
        self.assertFalse({'horsepanicbar','horsestaminabar'} & selected)
        self.assertNotIn('inkIronHorse',b.selected_scripts(selected))

    def test_unknown_component_rejected(self):
        with self.assertRaises(ValueError):
            b.selection(['inventory'])

    def test_scale_helper_kept_for_remaining_dependent(self):
        self.assertIn('inkIronHudScale',b.selected_scripts(b.selection(['buffs'])))
        self.assertNotIn('inkIronHudScale',b.selected_scripts(b.selection(['buffs','timelapse'])))


class ExtendedContractTests(unittest.TestCase):
    def test_accessor_removal_detected(self):
        with tempfile.TemporaryDirectory() as d:
            before,after = Path(d)/'before',Path(d)/'after'
            before.mkdir();after.mkdir()
            (before/'Tween.as').write_text('public function get paused():Boolean { return false; }')
            (after/'Tween.as').write_text('public function tick():void {}')
            with self.assertRaisesRegex(ValueError,'accessor changed'):
                b.class_contracts(before,after)

    def atlas(self,width=40,height=46,rectangle=(0,0,40,46),linkage='atlas.dds'):
        tail = struct.pack('<7I',0,1,40,48,160,1920,16)+bytes(1920)
        chunks = [dict(properties={'textures':{'value':struct.pack('<II',1,2).hex()}}),
            dict(class_name='CSwfTexture',tail=tail,properties={
                'compression':{'value':'TCM_DXTAlpha'},'width':{'value':40},'height':{'value':48},
                'linkageName':{'value':'atlas.dds'}})]
        image = struct.pack('<5H',0,9,14,width,height)+b'\x01x'+bytes([len(linkage)])+linkage.encode()
        tags = [(1009,image),(1008,struct.pack('<6H',1,0,*rectangle))]
        with patch.object(b.font.native,'chunks',return_value=chunks),patch.object(b.audit,'swf_tags',return_value=(0,'CFX',tags)):
            return b.atlas_contract(b'synthetic')

    def test_bc3_padding_allowed(self):
        self.assertEqual(self.atlas()['rectangles'],1)

    def test_unresolved_texture_linkage_rejected(self):
        with self.assertRaisesRegex(ValueError,'atlas linkage'):
            self.atlas(linkage='missing.dds')

    def test_rectangle_outside_atlas_rejected(self):
        with self.assertRaisesRegex(ValueError,'outside atlas'):
            self.atlas(rectangle=(0,0,41,46))

    def test_dimension_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'dimensions differ'):
            self.atlas(width=32)


if __name__=='__main__':
    unittest.main()
