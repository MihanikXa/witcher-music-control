"""Format/bounds regression tests for the read-only inspector, no game assets."""
import importlib.util
from pathlib import Path
import struct, tempfile, unittest, zlib

spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'tools/audit-ui.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class InspectorTests(unittest.TestCase):
    def test_both_bundle_layouts(self):
        for stride in (0x130,0x140):
            with self.subTest(stride=stride), tempfile.TemporaryDirectory() as folder:
                h=bytearray(32);h[:8]=b'POTATO70';struct.pack_into('<I',h,16,stride)
                b=bytearray(stride);name=b'Gameplay\\GUI\\test.redswf';b[:len(name)]=name
                if stride==0x130:struct.pack_into('<QIIII',b,272,32+stride,3,3,0,0)
                else:struct.pack_into('<III',b,276,3,3,32+stride)
                p=Path(folder)/'test.bundle';p.write_bytes(h+b+b'abc')
                e=list(audit.entries(p));self.assertEqual(e[0]['resource'],'gameplay/gui/test.redswf');self.assertEqual(e[0]['size'],3)
                p.write_bytes(h+b+b'a')
                with self.assertRaisesRegex(ValueError,'bounds'):list(audit.entries(p))

    def test_standard_and_gfx_payloads_with_variable_wrapper(self):
        # RECT (nbits1, all zero), rate/count, End tag.
        body=b'\x08\x00'+b'\x00\x18\x01\x00'+b'\x00\x00'
        for signature in (b'FWS',b'CWS',b'CFX'):
            length=8+len(body)+(99 if signature==b'CFX' else 0)
            packed=zlib.compress(body) if signature.startswith(b'C') else body
            offset,kind,tags=audit.swf_tags(b'wrapper-variable-size'+signature+b'\x0f'+struct.pack('<I',length)+packed)
            self.assertEqual(offset,21);self.assertEqual(tags,[(0,b'')])

    def test_missing_end_is_rejected(self):
        body=b'\x08\x00'+b'\x00\x18\x01\x00'+b'\x40\x00'
        with self.assertRaises(ValueError):audit.swf_tags(b'FWS\x0f'+struct.pack('<I',8+len(body))+body)

    def test_stripped_zero_glyph_font(self):
        name=b'$NormalFont';b=struct.pack('<HBBB',1,0,1,len(name))+name+b'\x00\x00'
        self.assertEqual(audit.font_info(48,b)['glyphs'],0)

    def test_unknown_signature_is_rejected(self):
        with self.assertRaises(ValueError):audit.swf_tags(b'not-a-flash-resource')

if __name__=='__main__':unittest.main()
