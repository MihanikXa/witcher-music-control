"""Synthetic bounded metadata relocation tests; no vendor fixtures."""
import importlib.util
from pathlib import Path
import struct
import unittest
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('relocator',ROOT/'tools/relocate-hud-metadata.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def fixture(entries,length):
    result=bytes.fromhex('0356544d07000000')+struct.pack('<II',max(e['packed'] for e in entries),max(e['size'] for e in entries))
    for e in entries:result+=struct.pack('<III',e['size'],e['packed'],e['offset'])+b'KEY\0'+struct.pack('<I',e['packed'])
    return result+struct.pack('<II',min(e['offset'] for e in entries),(length+15)//16*16-min(e['offset'] for e in entries))

class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.old=[dict(resource='first',size=100000,packed=30000,offset=4096),dict(resource='second',size=50000,packed=20000,offset=40000)]
        self.new=[dict(resource='first',size=99000,packed=29000,offset=4096),dict(resource='second',size=110000,packed=35000,offset=39000)]

    def test_exact_record_relocation_and_changed_header_maxima(self):
        output,patches=m.relocate(fixture(self.old,60000),self.old,self.new,60000,74000)
        self.assertEqual(output,fixture(self.new,74000));self.assertTrue(patches)

    def test_key_order_change_rejected(self):
        with self.assertRaises(ValueError):m.relocate(fixture(self.old,60000),self.old,self.new[::-1],60000,74000)

    def test_unrecognized_layout_or_ambiguous_values_rejected(self):
        data=fixture(self.old,60000)
        with self.assertRaises(ValueError):m.relocate(b'BAD!'+data[4:],self.old,self.new,60000,74000)
        with self.assertRaises(ValueError):m.relocate(data+struct.pack('<I',self.old[0]['packed']),self.old,self.new,60000,74000)

if __name__=='__main__':unittest.main()
