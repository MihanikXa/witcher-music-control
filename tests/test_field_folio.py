"""Original synthetic field/font isolation controls; no game fixtures."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

spec=importlib.util.spec_from_file_location('field',Path(__file__).resolve().parents[1]/'tools/prepare-field-folio.py')
field=importlib.util.module_from_spec(spec);spec.loader.exec_module(field)
spec=importlib.util.spec_from_file_location('probe',Path(__file__).resolve().parents[1]/'tools/probe-field-folio-export.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)


def text():
    return struct.pack('<H',215)+field.convert.encode_rect((-40,7960,-40,564))+bytes.fromhex('8cb3')+b'$NormalFont\0'+b'preserved field tail'


def movie(tags):
    body=field.convert.encode_rect((0,400,0,400))+struct.pack('<HH',30*256,1)
    body+=b''.join(field.convert.tag(c,b) for c,b in tags)
    return b'CWS\x0f'+struct.pack('<I',len(body)+8)+zlib.compress(body)


class FieldFolioTests(unittest.TestCase):
    def test_only_font_selector_changes(self):
        old=text();new=field.field_binding(old,218);pos=field.convert.prep.rect_end(old,2)
        self.assertEqual(old[:pos],new[:pos])
        self.assertEqual(new[pos:pos+4],bytes.fromhex('8d33')+struct.pack('<H',218))
        self.assertEqual(old[pos+14:],new[pos+4:])

    def test_wrong_field_rejected(self):
        with self.assertRaises(ValueError):field.field_binding(b'\x01\0'+text()[2:],218)

    def test_unexpected_font_class_rejected(self):
        with self.assertRaises(ValueError):field.field_binding(text().replace(b'$NormalFont',b'$OtherFontX'),218)

    def test_invalid_font_id_rejected(self):
        for value in (0,-1,65535,65536):
            with self.assertRaises(ValueError):field.field_binding(text(),value)

    def test_other_movie_code_and_tags_preserved(self):
        native=movie([(82,b'original ABC'),(37,text()),(76,b'original symbols'),(0,b'')])
        fonts={s:struct.pack('<H',field.IDS[s])+b'synthetic font' for s in field.IDS}
        candidate=field.assemble(native,fonts,'Regular')
        self.assertTrue(field.verify_delta(native,candidate,fonts,'Regular')['other_tags_byte_identical'])
        bad=candidate
        # Rebuild the changed movie with an unrelated code mutation.
        tags=[(c,b.replace(b'original ABC',b'mutated ABC')) for c,b in field.audit.swf_tags(bad)[2]]
        with self.assertRaises(ValueError):field.verify_delta(native,movie(tags),fonts,'Regular')

    def test_duplicate_font_ids_rejected_by_independent_verifier(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fonts.xml'
            p.write_text('<swf><tags><item type="DefineFont3Tag" fontID="218"/><item type="DefineFont3Tag" fontID="218"/></tags></swf>')
            with self.assertRaisesRegex(ValueError,'duplicated'):
                field.convert.verify_xml(p,{218:None,219:None},{218:None,219:None})

    def test_atlas_reassignment_preserves_semantic_reference(self):
        def tags(ref,right=32):
            return [(1009,struct.pack('<H',ref)+b'atlas descriptor'),
                    (1008,struct.pack('<6H',1,ref,0,0,right,16))]
        self.assertEqual(probe.atlas_contract(tags(0)),probe.atlas_contract(tags(1)))
        self.assertNotEqual(probe.atlas_contract(tags(0)),probe.atlas_contract(tags(1,33)))

    def test_unresolved_atlas_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unresolved'):
            probe.atlas_contract([(1008,struct.pack('<6H',1,9,0,0,32,16))])


if __name__=='__main__':unittest.main()
