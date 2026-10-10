"""Original synthetic serialization checks; no game/font fixtures."""
import importlib.util
from pathlib import Path
import unittest
import struct
import tempfile

spec = importlib.util.spec_from_file_location('convert', Path(__file__).resolve().parents[1] / 'tools/build-gentium-swf.py')
convert = importlib.util.module_from_spec(spec)
spec.loader.exec_module(convert)
vspec = importlib.util.spec_from_file_location('verify', Path(__file__).resolve().parents[1] / 'tools/verify-font-asset.py')
verify = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(verify)


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def read(self, count, signed=False):
        value = 0
        for _ in range(count):
            value = value * 2 + ((self.data[self.pos // 8] >> (7 - self.pos % 8)) & 1)
            self.pos += 1
        return value - (1 << count) if signed and value & (1 << (count - 1)) else value


class SerializationTests(unittest.TestCase):
    def test_signed_extremes_and_padding(self):
        bits = convert.Bits()
        bits.put(-16, 5, True); bits.put(15, 5, True)
        read = Reader(bits.bytes())
        self.assertEqual((read.read(5, True), read.read(5, True)), (-16, 15))
        self.assertEqual(read.read(6), 0)

    def test_overflow_rejected(self):
        for value, count, signed in ((16, 5, True), (-17, 5, True), (-1, 5, False), (32, 5, False)):
            with self.assertRaises(ValueError):
                convert.Bits().put(value, count, signed)

    def test_rect_negative_bearings(self):
        wanted = (-400, 22000, -19940, 5500)
        read = Reader(convert.encode_rect(wanted))
        n = read.read(5)
        self.assertEqual(tuple(read.read(n, True) for _ in range(4)), wanted)

    def test_shape_sets_fill_before_first_edge(self):
        read = Reader(convert.shape([('M', (-40, 50)), ('L', (60, 50)), ('L', (-40, 50))]))
        self.assertEqual((read.read(4), read.read(4)), (1, 0))
        self.assertEqual((read.read(1), read.read(5)), (0, 3))
        n = read.read(5)
        self.assertEqual((read.read(n, True), read.read(n, True), read.read(1)), (-40, 50, 1))
        self.assertEqual((read.read(1), read.read(1)), (1, 1))
        n = read.read(4) + 2
        self.assertEqual(read.read(1), 1)
        self.assertEqual((read.read(n, True), read.read(n, True)), (100, 0))

    def test_quadratic_control_and_anchor_are_relative(self):
        read = Reader(convert.shape([('M', (0, 0)), ('Q', (50, -100, 100, 0)), ('L', (0, 0))]))
        read.read(8); read.read(6)
        n = read.read(5); read.read(n * 2); read.read(1)
        self.assertEqual((read.read(1), read.read(1)), (1, 0))
        n = read.read(4) + 2
        self.assertEqual(tuple(read.read(n, True) for _ in range(4)), (50, -100, 50, 100))

    def test_space_is_valid_end_shape(self):
        self.assertEqual(convert.shape([]), b'\x10\x00')

    def test_glyph_edges_cannot_overflow_swf_limit(self):
        with self.assertRaisesRegex(ValueError, 'overflow'):
            convert.shape([('M', (0, 0)), ('L', (1 << 18, 0))])

    def test_resource_check_includes_frame_header(self):
        def fixture(rate):
            body = convert.encode_rect((0, 1000, 0, 500)) + struct.pack('<HH', rate, 1) + b'\0\0'
            return b'FWS\x0a' + struct.pack('<I', len(body) + 8) + body
        self.assertNotEqual(verify.movie_tags(fixture(2560)), verify.movie_tags(fixture(5120)))

    def test_fontname_metadata_does_not_mask_other_tags(self):
        def fixture(code):
            body = convert.encode_rect((0, 0, 0, 0)) + struct.pack('<HH', 2560, 1)
            body += convert.tag(code, b'\x01\0name\0copyright\0') + b'\0\0'
            return b'FWS\x0a' + struct.pack('<I', len(body) + 8) + body
        self.assertEqual(verify.movie_tags(fixture(88))[2], [(0, b'')])
        self.assertEqual(len(verify.movie_tags(fixture(87))[2]), 2)

    def test_reused_workspace_restored_after_exception(self):
        with tempfile.TemporaryDirectory(dir=verify.ROOT/'build', prefix='font-mount-test-') as tmp:
            root=Path(tmp); runner=root/'runner'; out=root/'output'; out.mkdir()
            old=runner/'bin/workspace/original.dat'; old.parent.mkdir(parents=True); old.write_bytes(b'original')
            resource=root/'input.redswf'; resource.write_bytes(b'synthetic-resource')
            with self.assertRaisesRegex(RuntimeError, 'controlled failure'):
                with verify.mounted_input(runner,out,resource) as workspace:
                    self.assertEqual((workspace/verify.KEY).read_bytes(), b'synthetic-resource')
                    self.assertFalse((workspace/'original.dat').exists())
                    raise RuntimeError('controlled failure')
            self.assertEqual(old.read_bytes(), b'original')
            self.assertEqual((out/'staged-workspace'/verify.KEY).read_bytes(), b'synthetic-resource')
            self.assertFalse((runner/'bin/workspace-font-backup').exists())

    def test_initially_absent_workspace_remains_absent(self):
        with tempfile.TemporaryDirectory(dir=verify.ROOT/'build', prefix='font-mount-test-') as tmp:
            root=Path(tmp); runner=root/'runner'; (runner/'bin').mkdir(parents=True)
            out=root/'output'; out.mkdir(); resource=root/'input.redswf'; resource.write_bytes(b'synthetic')
            with verify.mounted_input(runner,out,resource): pass
            self.assertFalse((runner/'bin/workspace').exists())
            self.assertTrue((out/'staged-workspace'/verify.KEY).exists())

    def test_workspace_mount_rejects_outputs_inside_runner(self):
        with tempfile.TemporaryDirectory(dir=verify.ROOT/'build', prefix='font-mount-test-') as tmp:
            root=Path(tmp); runner=root/'runner'; out=runner/'output'; out.mkdir(parents=True)
            resource=root/'input.redswf'; resource.write_bytes(b'synthetic')
            with self.assertRaises(ValueError):
                with verify.mounted_input(runner,out,resource): pass


if __name__ == '__main__':
    unittest.main()
