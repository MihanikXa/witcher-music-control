"""Validate the original compiler-control transformation, not UI behavior."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('diagnostics', ROOT / 'tools/compare-npc-wrapper-diagnostics.py')
diagnostics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostics)


class ProbeControlTests(unittest.TestCase):
    def test_declarations_preserved_and_effects_removed(self):
        source = (ROOT / 'src/npc/quietEditorialNameProbe.ws').read_text()
        control = diagnostics.make_probe_noop(source)
        headers = r'\bfunction\s+\w+\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{'
        self.assertEqual(re.findall(headers, source), re.findall(headers, control))
        self.assertEqual(source.count('@addField'), control.count('@addField'))
        self.assertEqual(source.count('@wrapMethod'), control.count('@wrapMethod'))
        self.assertNotIn('SetMemberFlash', control)
        self.assertNotIn('ShowNotification(', control)
        self.assertEqual(control.count('wrappedMethod('), 3)

    def test_unclosed_body_rejected(self):
        with self.assertRaises(ValueError):
            diagnostics.make_probe_noop('function qeprobe() {')

    def test_unknown_function_rejected(self):
        with self.assertRaises(ValueError):
            diagnostics.make_probe_noop('function unrelated() {}')


if __name__ == '__main__': unittest.main()
