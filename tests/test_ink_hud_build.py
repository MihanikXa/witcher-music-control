"""Synthetic fail-closed package and contract identity checks."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


build = load('build-ink-hud-bars')
contracts = load('audit-hud-contracts')


def bundle(data=b'asset', copies=1, codec=1, size=None):
    compressed = zlib.compress(data)
    head = bytearray(32)
    head[:8] = b'POTATO70'
    struct.pack_into('<I', head, 16, copies*0x130)
    index = bytearray()
    for _ in range(copies):
        e = bytearray(0x130)
        name = build.KEY.encode()
        e[:len(name)] = name
        struct.pack_into('<QIIII', e, 272, 32+copies*0x130, len(data) if size is None else size,
                         len(compressed), 0, codec)
        index.extend(e)
    return head+index+compressed


class BundleTests(unittest.TestCase):
    def extract(self, data):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'test.bundle'
            p.write_bytes(data)
            return build.extract(p, build.KEY)

    def test_exact_reextraction(self):
        self.assertEqual(self.extract(bundle()), b'asset')

    def test_duplicate_key_rejected(self):
        with self.assertRaises(ValueError):
            self.extract(bundle(copies=2))

    def test_wrong_codec_rejected(self):
        with self.assertRaises(ValueError):
            self.extract(bundle(codec=0))

    def test_wrong_length_rejected(self):
        with self.assertRaises(ValueError):
            self.extract(bundle(size=7))


class ContractTests(unittest.TestCase):
    def test_duplicate_symbol_rejected(self):
        payload = struct.pack('<HH', 2, 1)+b'name\0'+struct.pack('<H', 2)+b'name\0'
        with self.assertRaises(ValueError):
            contracts.symbols([(76, payload)])

    def test_trailing_symbol_bytes_rejected(self):
        with self.assertRaises(ValueError):
            contracts.symbols([(76, struct.pack('<HH', 1, 1)+b'name\0junk')])

    def test_different_actionscript_rejected(self):
        def movie(abc):
            # Minimal valid stage/frame header, one DoABC and an End tag.
            body = b'\x08\x00\x00\x1e\x01\x00'+struct.pack('<H', (82<<6)|len(abc))+abc+b'\0\0'
            return b'FWS\x0a'+struct.pack('<I', len(body)+8)+body
        self.assertTrue(build.same_movie(movie(b'abcd'), movie(b'abcd')))
        self.assertFalse(build.same_movie(movie(b'abcd'), movie(b'abce')))


if __name__ == '__main__':
    unittest.main()
