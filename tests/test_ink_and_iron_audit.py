"""Bounds and identity tests for read-only format inspectors, synthetic inputs."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('ink_audit',Path(__file__).resolve().parents[1]/'tools/audit-ink-and-iron.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class CacheTests(unittest.TestCase):
    def make(self, offset=0, name_offset=0):
        names=b'gameplay\\gui_new\\icons\\test.png\0'
        entry=bytearray(52)
        struct.pack_into('<IiIII',entry,0,0x12345678,name_offset,offset,4,8)
        struct.pack_into('<HH',entry,24,64,128)
        return b'data'+names+entry+struct.pack('<QIIII4sI',0,0,1,len(names),0,b'HCXT',6)
    def read(self,b):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'texture.cache'; p.write_bytes(b)
            return list(mod.cache_entries(p))
    def test_named_texture(self):
        rows=self.read(self.make())
        self.assertEqual(rows[0]['resource'],'gameplay/gui_new/icons/test.png')
        self.assertEqual(rows[0]['key_hash'],'12345678')
        self.assertEqual((rows[0]['width'],rows[0]['height']),(64,128))
    def test_outside_payload(self):
        with self.assertRaises(ValueError): self.read(self.make(offset=1))
    def test_invalid_string_offset(self):
        with self.assertRaises(ValueError): self.read(self.make(name_offset=-1))
    def test_truncated_footer(self):
        with self.assertRaises(ValueError): self.read(b'')
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): mod.output_resource('module','../../../outside.redswf')

class AnnotationTests(unittest.TestCase):
    def test_comments_and_utf16(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.ws'
            p.write_text('// @wrapMethod(Fake) function Wrong(){}\n/* @addField(Fake) var no : int; */\n@wrapMethod(Real) private function Run(){}\n@addField(Real) var field : int;',encoding='utf-16')
            rows=mod.scripts(p,'synthetic')
            self.assertEqual([(x['class_name'],x['member']) for x in rows],[('Real','Run'),('Real','field')])

class StringTests(unittest.TestCase):
    def test_english_ids_match_across_plain_and_xor_indexes(self):
        sid=2117650101
        def blob(mask,key1,key2):
            encoded=sid^mask
            return b'RTSW'+struct.pack('<IH',164,key1)+b'\x01'+struct.pack('<III',encoded,0,1)+b'\x01'+struct.pack('<II',123,encoded)+b'\x02x\0'+struct.pack('<H',key2)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'en.w3strings'
            p.write_bytes(blob(0,0,0)); plain=mod.string_index(p)
            p.write_bytes(blob(0x79321793,17303,20793)); encoded=mod.string_index(p)
            self.assertEqual(plain['ids'],encoded['ids'])
            self.assertEqual(plain['keys'],encoded['keys'])
            self.assertEqual(encoded['ids'],[sid])

if __name__=='__main__': unittest.main()
