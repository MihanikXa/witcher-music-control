import io
import struct
import unittest
from regional_baseline_reference import cache_index


def cache():
    b=bytearray(64);b[:8]=b'CS3W\x02\0\0\0';b+=b'abcd';name=b'123.wem\0'
    struct.pack_into('<I',b,24,1);struct.pack_into('<Q',b,32,68);struct.pack_into('<I',b,40,len(name))
    b+=name;b+=struct.pack('<QQQ',0,64,4);return b


class BaselineCacheBounds(unittest.TestCase):
    def test_bounded_index(self):
        self.assertEqual(cache_index(io.BytesIO(cache())),{'123.wem':(64,4)})

    def test_truncation_and_bad_offset_fail(self):
        b=cache()
        with self.assertRaises(ValueError):cache_index(io.BytesIO(b[:-1]))
        struct.pack_into('<Q',b,len(b)-16,10000)
        with self.assertRaises(ValueError):cache_index(io.BytesIO(b))

    def test_unterminated_name_fails(self):
        b=cache();b[75]=65
        with self.assertRaises(ValueError):cache_index(io.BytesIO(b))
