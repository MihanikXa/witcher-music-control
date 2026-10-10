"""Synthetic layout bounds tests; no proprietary font fixtures."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('prep', Path(__file__).resolve().parents[1] / 'tools/prepare-english-gentium.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


def fixture():
    # One glyph, wide offsets/codes, one byte dummy shape; no kerning.
    return (struct.pack('<HBBB', 1, 140, 1, 1) + b'X' + struct.pack('<H', 1)
            + struct.pack('<II', 8, 9) + b'\0' + struct.pack('<H', 65)
            + struct.pack('<HHhh', 18000, 4000, 0, 10000) + b'\0' + b'\0\0')


class FontPreparationTests(unittest.TestCase):
    def test_observed_layout_fields(self):
        result = prep.layout(fixture())
        self.assertEqual(result['advances'], [10000])
        self.assertEqual(result['codes'], [65])
        self.assertEqual(result['kerning_count'], 0)

    def test_truncated_layout_rejected(self):
        with self.assertRaises((ValueError, struct.error)):
            prep.layout(fixture()[:-1])

    def test_trailing_data_rejected(self):
        with self.assertRaises(ValueError):
            prep.layout(fixture() + b'\0')

    def test_truncated_rect_rejected(self):
        with self.assertRaises(ValueError):
            prep.rect_end(b'\xf8', 0)


if __name__ == '__main__':
    unittest.main()
