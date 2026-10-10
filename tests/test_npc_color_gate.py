"""The private archive must never silently accept a diagnostic regression."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('package', Path(__file__).resolve().parents[1] / 'tools/package-npc-color-trial.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class ColorGateTests(unittest.TestCase):
    def setUp(self):
        self.source = b'original candidate'
        self.receipt = {'source_inputs_unchanged': True, 'results': []}
        for label in ('baseline', 'npc_noop', 'hud_noop', 'candidate'):
            self.receipt['results'].append(dict(label=label, success=True, errors=[],
                source_sha256=hashlib.sha256(self.source).hexdigest(),
                assertions_added={'scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())': 1},
                assertions_removed={}, warnings_added={}, warnings_removed={}))

    def test_controlled_diagnostic_accepted(self):
        package.gate(self.receipt, self.source)

    def test_changed_candidate_rejected(self):
        with self.assertRaises(ValueError): package.gate(self.receipt, b'changed')

    def test_extra_assertion_rejected(self):
        self.receipt['results'][-1]['assertions_added']['diskFile.cpp:2633'] = 1
        with self.assertRaises(ValueError): package.gate(self.receipt, self.source)

    def test_warning_regression_rejected(self):
        self.receipt['results'][-1]['warnings_added'] = {'new warning': 1}
        with self.assertRaises(ValueError): package.gate(self.receipt, self.source)

    def test_failed_control_rejected(self):
        self.receipt['results'][2]['success'] = False
        with self.assertRaises(ValueError): package.gate(self.receipt, self.source)

    def test_declaration_matched_probe_control(self):
        self.receipt['results'] = [self.receipt['results'][0], self.receipt['results'][1], self.receipt['results'][-1]]
        self.receipt['results'][1]['label'] = 'paired_noop'
        for r in self.receipt['results'][1:]:
            r['assertions_added'] = {'scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())': 6}
        package.gate(self.receipt, self.source, probe=True)
        self.receipt['results'][-1]['assertions_added'] = {'scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())': 7}
        with self.assertRaises(ValueError): package.gate(self.receipt, self.source, probe=True)


if __name__ == '__main__': unittest.main()
