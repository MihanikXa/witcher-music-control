"""Original synthetic timeline/vector tests; no extracted assets."""
import importlib.util
from pathlib import Path
import struct
import unittest
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('vector',ROOT/'tools/flat-vector-xbox.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)

class VectorTests(unittest.TestCase):
    def test_solid_shape_has_no_bitmap_or_gradient_styles(self):
        from PIL import Image
        image=Image.new('RGBA',(8,8),(239,227,206,255))
        data=v.shape(12,image);offset=2+(5+4*(data[2]>>3)+7)//8
        self.assertEqual(data[offset:offset+12],bytes((2,0,20,23,24,224,0,239,227,206,255,0)))
        self.assertEqual(v.rectangles(image),[(0,0,8,8,2)])

    def test_gfx_image_placement_loses_only_image_flag_and_changes_id(self):
        payload=bytes.fromhex('06100200910100')
        counts={};result=v.rewrite_tags([(70,payload)],{401:600},counts)
        self.assertEqual(result,[(70,bytes.fromhex('06000200580200'))])
        self.assertEqual(counts,{401:1})

    def test_nested_sprite_preserves_frames_transforms_and_other_ids(self):
        p=bytes((6,))+struct.pack('<HH',3,10)+b'\x00'
        other=bytes((6,))+struct.pack('<HH',4,11)+b'\x00'
        prefix=struct.pack('<HH',20,2)
        payload=prefix+v.f.tag(26,p)+v.f.tag(26,other)+v.f.tag(0,b'')
        counts={};result=v.rewrite_tags([(39,payload)],{10:30},counts)[0][1]
        self.assertEqual(result,prefix+v.f.tag(26,p[:3]+struct.pack('<H',30)+p[5:])+v.f.tag(26,other)+v.f.tag(0,b''))

    def test_classname_offset_is_preserved(self):
        p=bytes((2,8))+struct.pack('<H',7)+b'Class\0'+struct.pack('<H',10)
        result=v.rewrite_tags([(70,p)],{10:30},{})[0][1]
        self.assertEqual(result,p[:-2]+struct.pack('<H',30))

    def test_other_controllers_and_noncharacter_updates_unchanged(self):
        tags=[(26,bytes((1,))+struct.pack('<H',3)),(70,bytes((2,0))+struct.pack('<HH',3,99))]
        self.assertEqual(v.rewrite_tags(tags,{10:30},{}),tags)

if __name__=='__main__':unittest.main()
