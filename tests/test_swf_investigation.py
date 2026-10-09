"""Diagnostic separation, sampling distance and source decoding without assets."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / 'tools' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('state', 'investigate-swf-state.py')
padding = load('padding', 'analyze-npc-atlas-padding.py')
fallback = load('fallback', 'check-npc-fallback.py')


class InvestigationTests(unittest.TestCase):
    def test_assertion_is_not_confused_with_successful_save(self):
        log = ('[Info] saved\n[Error][Assert] [D:\\Main.Lava\\dev\\src\\common\\core\\diskFile.cpp:2633] '
               'Corrupted internal flag state\n')
        d = state.diagnostics(log)
        self.assertEqual(len(d['resource_assertions']), 1)
        self.assertEqual(d['assertion_sites']['common\\core\\diskFile.cpp:2633'], 1)

    def test_cancelled_overwrite_is_reported_separately(self):
        d = state.diagnostics('[Error] overwriting is cancelled')
        self.assertTrue(d['overwrite_cancelled'])
        self.assertEqual(d['resource_assertions'], [])

    def test_exclusive_rectangle_and_filter_border(self):
        rect = (10, 20, 14, 24)
        for x, y, expected in ((10, 20, 0), (13, 23, 0), (14, 24, 1), (15, 25, 2), (8, 18, 2)):
            self.assertEqual(padding.distance(x, y, rect), expected)

    def test_utf8_and_utf16_source_line_endings(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'source.ws'
            for encoding in ('utf-8-sig', 'utf-16'):
                p.write_bytes('class X\r\n{\r\n}\r\n'.encode(encoding))
                self.assertEqual(fallback.text(p), 'class X\n{\n}\n')


if __name__ == '__main__':
    unittest.main()
