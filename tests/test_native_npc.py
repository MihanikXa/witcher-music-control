"""Independent known BC3 blocks and malformed resource checks; no game assets."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('native', Path(__file__).resolve().parents[1] / 'tools/compare-native-npc.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class NativeInspectorTests(unittest.TestCase):
    def test_opaque_red_and_partial_block(self):
        block = bytes([255, 0]) + bytes(6) + struct.pack('<HHI', 0xf800, 0, 0)
        self.assertEqual(native.bc3(block, 4, 3), [[255, 0, 0, 255]] * 12)

    def test_alpha_interpolation_and_transparent_selector(self):
        selectors = sum(7 << (3 * i) for i in range(16))
        block = bytes([0, 255]) + selectors.to_bytes(6, 'little') + struct.pack('<HHI', 0xffff, 0, 0)
        self.assertEqual(native.bc3(block, 4, 4), [[255, 255, 255, 255]] * 16)
        selectors = sum(6 << (3 * i) for i in range(16))
        block = block[:2] + selectors.to_bytes(6, 'little') + block[8:]
        self.assertEqual(native.bc3(block, 4, 4), [[255, 255, 255, 0]] * 16)

    def test_truncated_bc3_rejected(self):
        with self.assertRaises(ValueError):
            native.bc3(bytes(15), 4, 4)

    def test_unknown_and_truncated_cr2w_rejected(self):
        for data in (b'CR2W', b'CR2W' + struct.pack('<I', 163) + bytes(152)):
            with self.assertRaises(ValueError):
                native.chunks(data)

    def test_table_bounds_rejected(self):
        data = bytearray(160)
        data[:8] = b'CR2W' + struct.pack('<I', 164)
        struct.pack_into('<III', data, 40, 160, 1, 0)
        with self.assertRaisesRegex(ValueError, 'table bounds'):
            native.chunks(data)


if __name__ == '__main__':
    unittest.main()
