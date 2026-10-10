"""Synthetic SWF regression guards; no game assets in tests."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('shadow', Path(__file__).resolve().parents[1] / 'tools/prepare-npc-shadow.py')
shadow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shadow)


def tag(code, payload):
    return struct.pack('<H', (code << 6) | 63) + struct.pack('<I', len(payload)) + payload


def sprite(record):
    placement = bytes([0x26, 1]) + struct.pack('<HH', 35, 38) + b'tfName\0' + bytes([1]) + record
    return struct.pack('<HH', 63, 1) + tag(70, placement) + b'\0\0'


class ShadowSourceTests(unittest.TestCase):
    def test_only_filter_changes_accepted(self):
        old, new = sprite(shadow.shadow_record()), sprite(shadow.shadow_record(True))
        offset = shadow.accept_sprite(old, new)
        self.assertEqual(old[:offset], new[:offset])
        self.assertEqual(old[offset + 24:], new[offset + 24:])
        self.assertEqual(sum(a != b for a, b in zip(old, new)), 7)

    def test_angle_flags_name_depth_and_extra_changes_rejected(self):
        old, new = sprite(shadow.shadow_record()), sprite(shadow.shadow_record(True))
        offset = shadow.accept_sprite(old, new)
        for pos in (0, 12, offset + 13, offset + 23):
            bad = bytearray(new)
            bad[pos] ^= 1
            with self.assertRaises(ValueError):
                shadow.accept_sprite(old, bytes(bad))

    def test_wrong_original_filter_rejected(self):
        with self.assertRaises(ValueError):
            shadow.accept_sprite(sprite(shadow.shadow_record(True)), sprite(shadow.shadow_record(True)))

    def test_truncation_and_trailing_data_rejected(self):
        for data in (b'\0', b'\0\0x', struct.pack('<H', (70 << 6) | 63), tag(70, b'x')[:-1]):
            with self.assertRaises(ValueError):
                shadow.records(data, 0)

    def test_non_native_containers_and_length_rejected(self):
        for data in (b'CR2W' + bytes(40), b'GFX' + bytes(40), b'FWS\x0f' + struct.pack('<I', 999) + b'x'):
            with self.assertRaises(ValueError):
                shadow.body(data)


if __name__ == '__main__':
    unittest.main()
