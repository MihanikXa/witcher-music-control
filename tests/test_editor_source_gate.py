"""Prevent packaging a checked-out baseline as a changed movie."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).resolve().parents[1] / 'tools/verify-editor-assets.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def movie(code_payloads):
    body = b'\x08\x00' + bytes(4)
    for code, payload in code_payloads:
        body += struct.pack('<H', (code << 6) | len(payload)) + payload
    body += b'\0\0'
    return b'FWS\x0f' + struct.pack('<I', len(body) + 8) + body


class EditorSourceGateTests(unittest.TestCase):
    def test_unmodified_checked_out_code_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no cooker executed'):
            gate.verify_source_movie(movie([(82, b'new')]), movie([(82, b'old')]))

    def test_placement_regression_rejected(self):
        with self.assertRaises(ValueError):
            gate.verify_source_movie(movie([(39, b'shadow')]), movie([(39, b'vanill')]))

    def test_expected_import_bitmap_replacement_allowed(self):
        gate.verify_source_movie(movie([(82, b'code'), (36, b'image')]),
                                 movie([(82, b'code'), (1008, b'index')]))


if __name__ == '__main__':
    unittest.main()
