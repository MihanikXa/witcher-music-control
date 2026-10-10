"""Require one approved filter delta; reject unrelated code/placement edits."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('package', Path(__file__).resolve().parents[1] / 'tools/package-npc-shadow.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def tag(code, data):
    return struct.pack('<HI', (code << 6) | 63, len(data)) + data


def movie(changed, code=b'original', flags_change=False):
    record = bytearray(package.shadow.shadow_record(changed))
    if flags_change:
        record[-1] ^= 1
    placement = bytes([0x26, 1]) + struct.pack('<HH', 35, 38) + b'tfName\0' + bytes([1]) + record
    sprite = struct.pack('<HH', 63, 1) + tag(70, placement) + bytes(2)
    body = b'\x08\x00' + bytes(4) + tag(82, code) + tag(39, sprite) + bytes(2)
    return b'FWS\x0f' + struct.pack('<I', len(body) + 8) + body


class ShadowPackageGateTests(unittest.TestCase):
    def test_approved_shadow_only_delta(self):
        result = package.contract_delta(movie(False), movie(True))
        self.assertTrue(result['only_approved_filter_changed'])

    def test_code_change_rejected(self):
        with self.assertRaises(ValueError):
            package.contract_delta(movie(False), movie(True, code=b'newcode'))

    def test_filter_flags_change_rejected(self):
        with self.assertRaises(ValueError):
            package.contract_delta(movie(False), movie(True, flags_change=True))

    def test_unchanged_copy_rejected(self):
        with self.assertRaises(ValueError):
            package.contract_delta(movie(False), movie(False))


if __name__ == '__main__':
    unittest.main()
