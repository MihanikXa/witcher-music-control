"""Synthetic verification tests, not generated Wwise banks or licence evidence."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
import uuid
import argparse
from unittest.mock import patch

from white_orchard_build_gate import compare_pair, generation, plugins, run
from white_orchard_compare import read_bank
from white_orchard_state_bank_audit import state_chunk


def chunk(name, data):
    return name.encode() + struct.pack('<I', len(data)) + data


def bank(path, project=39, body=b'native', stmg=b'globals', registrations=None):
    registrations = registrations if registrations is not None else struct.pack('<I', 1) + struct.pack('<I', 123) + b'Plugin\0'
    hirc = struct.pack('<I', 1) + struct.pack('<BII', 8, 4 + len(body), 42) + body
    bkhd = struct.pack('<6I', 150, 1355168291, 393239870, 16, project, 0) + bytes(16) + bytes(8)
    path.write_bytes(chunk('BKHD', bkhd) + chunk('INIT', registrations) + chunk('STMG', stmg) + chunk('HIRC', hirc))
    return read_bank(path)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'build')
        self.root = Path(self.temp.name)
        assert self.root.resolve().is_relative_to(Path(__file__).resolve().parents[1] / 'build')
        self.meta = self.root / 'SoundbanksInfo.xml'
        self.meta.write_text('<SoundBanksInfo><SoundBanks><SoundBank Id="1355168291" Hash="{00000000-0000-0000-0000-000000000000}"/></SoundBanks></SoundBanksInfo>')
        self.native = bank(self.root / 'native.bnk')

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_control_passes(self):
        self.assertTrue(compare_pair(self.native, bank(self.root / 'copy.bnk'), self.meta)['passed'])

    def test_project_zero_rejected(self):
        result = compare_pair(self.native, bank(self.root / 'copy.bnk', project=0), self.meta)
        self.assertFalse(result['passed'])
        self.assertIn('project_id', result['header_field_differences'])

    def test_unrelated_hirc_change_rejected(self):
        self.assertFalse(compare_pair(self.native, bank(self.root / 'copy.bnk', body=b'changed'), self.meta)['passed'])

    def test_full_stmg_change_rejected(self):
        self.assertFalse(compare_pair(self.native, bank(self.root / 'copy.bnk', stmg=b'changed'), self.meta)['passed'])

    def test_missing_plugin_rejected(self):
        self.assertFalse(compare_pair(self.native, bank(self.root / 'copy.bnk', registrations=bytes(4)), self.meta)['passed'])

    def test_metadata_hash_mismatch_rejected(self):
        self.meta.write_text('<SoundBanksInfo><SoundBank Id="1355168291" Hash="{' + str(uuid.UUID(int=1)) + '}"/></SoundBanksInfo>')
        self.assertFalse(compare_pair(self.native, self.native, self.meta)['passed'])

    def test_registration_parser_rejects_malformed_and_duplicate(self):
        for payload in (b'', struct.pack('<I', 1) + struct.pack('<I', 12) + b'NoNul',
                        struct.pack('<I', 2) + (struct.pack('<I', 12) + b'Plugin\0') * 2,
                        bytes(4) + b'trailing'):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                plugins(payload)

    def test_empty_registration_name_is_preserved(self):
        self.assertEqual(plugins(struct.pack('<II', 1, 11403271) + b'\0'), {11403271: ''})

    def test_bank_reader_rejects_duplicates_and_truncation(self):
        path = self.root / 'invalid.bnk'
        valid = (self.root / 'native.bnk').read_bytes()
        for data in (valid[:-1], valid + chunk('STMG', b'duplicate'), valid[:5]):
            path.write_bytes(data)
            with self.subTest(size=len(data)), self.assertRaises((ValueError, struct.error)):
                read_bank(path)

    def test_duplicate_state_property_rejected(self):
        body = bytes(28) + bytes([1, 0, 2, 1, 1]) + struct.pack('<IBB', 766723505, 0, 1)
        body += struct.pack('<IHHHff', 2582085496, 2, 0, 0, -200, -100)
        with self.assertRaises(ValueError):
            state_chunk(body)

    def test_generation_gate(self):
        banner = 'Wwise | v2023.1.19 | Build no.8928\n'
        folder = self.root/'generation'
        folder.mkdir()
        for name in ('Init.bnk', 'music_prologue.bnk'):
            (folder/name).write_bytes(b'synthetic-file-presence')
        for code, log, expected in ((0, banner, True), (1, banner, False), (2, banner, False),
                                    (0, banner + 'SoundBankGeneration\tError\tNone\tNo license for Mastering Suite\n', False),
                                    (0, banner + 'SoundBankGeneration\tWarning\tUnknown\tReview me\n', False),
                                    (0, 'wrong tool', False)):
            (folder / 'result.json').write_text(json.dumps({'exit_code': code, 'banks': ['Init.bnk', 'music_prologue.bnk']}))
            (folder / 'generation.log').write_text(log)
            with self.subTest(code=code, log=log):
                self.assertEqual(generation(folder)['passed'], expected)
        (folder / 'generation.log').write_text(banner)
        (folder / 'extra.bnk').write_bytes(b'extra')
        self.assertFalse(generation(folder)['passed'])

    def test_missing_evidence_writes_failure_report(self):
        repo_build = Path(__file__).resolve().parents[1] / 'build'
        with tempfile.TemporaryDirectory(dir=repo_build) as directory:
            root = Path(directory)
            args = argparse.Namespace(mode='baseline', native=root/'native', baseline=root/'banks',
                                      baseline_project=root/'project', candidate=None, candidate_project=None,
                                      game_init=root/'native-init.bnk', baseline_report=None,
                                      output=root/'reports/missing.json')
            self.assertEqual(run(args), 1)
            report = json.loads(args.output.read_text())
            self.assertFalse(report['passed'])
            self.assertIn('invalid_or_missing_evidence:FileNotFoundError', report['failures'])

    def test_stale_baseline_proof_blocks_candidate_audit(self):
        repo_build = Path(__file__).resolve().parents[1] / 'build'
        with tempfile.TemporaryDirectory(dir=repo_build) as directory:
            root = Path(directory)
            proof = root/'baseline.json'
            proof.write_text(json.dumps({'mode':'baseline', 'passed':True, 'input_hashes':{'old':'hash'}}))
            args = argparse.Namespace(mode='candidate', native=root/'native', baseline=root/'banks',
                                      baseline_project=root/'project', candidate=root/'candidate-banks', candidate_project=root/'candidate-project',
                                      game_init=root/'native-init.bnk', baseline_report=proof,
                                      output=root/'reports/stale.json')
            with patch('white_orchard_build_gate.inputs', return_value={'new':'hash'}), \
                 patch('white_orchard_build_gate.baseline', return_value={'checks':{'fidelity':True}}), \
                 patch('white_orchard_build_gate.audit') as state_audit:
                self.assertEqual(run(args), 1)
                state_audit.assert_not_called()
                self.assertIn('baseline_report_missing_or_stale', json.loads(args.output.read_text())['failures'])

    def test_inputs_changed_during_validation_fail(self):
        repo_build = Path(__file__).resolve().parents[1] / 'build'
        with tempfile.TemporaryDirectory(dir=repo_build) as directory:
            root = Path(directory)
            args = argparse.Namespace(mode='baseline', native=root/'native', baseline=root/'banks',
                                      baseline_project=root/'project', candidate=None, candidate_project=None,
                                      game_init=root/'native-init.bnk', baseline_report=None,
                                      output=root/'reports/changed.json')
            with patch('white_orchard_build_gate.inputs', side_effect=[{'file':'before'}, {'file':'after'}]), \
                 patch('white_orchard_build_gate.baseline', return_value={'checks':{'fidelity':True}}):
                self.assertEqual(run(args), 1)
                self.assertIn('inputs_changed_during_validation', json.loads(args.output.read_text())['failures'])


if __name__ == '__main__':
    unittest.main()
