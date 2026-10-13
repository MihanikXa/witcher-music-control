import struct
import unittest

from regional_music_cache import verify_bytes


def cache(expected):
    data=bytearray(64);data[:8]=b'CS3W\x02\0\0\0';rows=[];names=bytearray()
    for name,payload in expected.items():
        rows.append((len(names),len(data),len(payload)));names+=name.encode()+b'\0';data+=payload
    start=len(data);data+=names
    for row in rows:data+=struct.pack('<QQQ',*row)
    struct.pack_into('<I',data,24,len(rows));struct.pack_into('<Q',data,32,start);struct.pack_into('<I',data,40,len(names))
    return bytes(data)


class CacheTests(unittest.TestCase):
    def test_single_exact_payload(self):
        expected={'music_prologue.bnk':b'bank'};self.assertTrue(verify_bytes(cache(expected),expected)['passed'])

    def test_two_expected_regional_entries(self):
        expected={'music_prologue.bnk':b'one','music_nomansgrad.bnk':b'two'}
        self.assertEqual(len(verify_bytes(cache(expected),expected)['entries']),2)

    def test_init_forbidden(self):
        expected={'Init.bnk':b'init'}
        with self.assertRaisesRegex(ValueError,'no Init'):
            verify_bytes(cache(expected),expected)

    def test_payload_change_rejected(self):
        expected={'music_nomansgrad.bnk':b'two'}
        with self.assertRaisesRegex(ValueError,'changed payload'):
            verify_bytes(cache(expected),{'music_nomansgrad.bnk':b'bad'})

    def test_extra_entries_rejected(self):
        expected={'music_prologue.bnk':b'one','music_nomansgrad.bnk':b'two'}
        with self.assertRaisesRegex(ValueError,'count'):
            verify_bytes(cache(expected),{'music_prologue.bnk':b'one'})

    def test_bad_table_bounds_rejected(self):
        expected={'music_prologue.bnk':b'one'}
        with self.assertRaisesRegex(ValueError,'bounds'):
            verify_bytes(cache(expected)[:-1],expected)
