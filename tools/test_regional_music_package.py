"""Synthetic fail-closed package prerequisite checks; no native tool invocation."""
import copy
import unittest
from regional_music_package import require_proofs


def fixture():
    spec = {'region': 'music_nomansgrad', 'state_scopes': [], 'static_targets': [
        '{48810350-DE09-4F69-B3DA-FCF4667EF177}', '{958962C3-1AC8-4C75-939C-B5EBEC3C75DD}',
        '{E5564ADB-9A93-4E6A-8D72-DE209E1A1A2D}', '{FA35E341-DB95-427A-BC50-EC2DD414DA4C}']}
    proof = {'passed': True, 'manifest_sha256': 'manifest', 'candidate_music_sha256': 'source',
        'decoded_fields': {'passed': True, 'candidate_sha256': 'bank', 'global_generated_data_exact': True,
                           'paired_generated_media_exact': 423},
        'bank_preflight': {'passed': True, 'candidate_sha256': 'bank'},
        'complete_work_units': 1508, 'original_audio_unchanged': True,
        'original_nonmusic_units_unchanged': True, 'global_definitions_unchanged': True}
    proof['decoded_fields']['records'] = {i: {'kind': 13, 'parent': p, 'immutable_remainder_exact': True}
        for i, p in {'719937819': 193134718, '946096996': 193134718,
                     '132074504': 432285193, '568231384': 432285193}.items()}
    checks = [{'mode': m, 'case': c, 'passed': True} for m in ('native-reference', 'manifest')
              for c in ('e-combat', 'e-combat-offset')]
    playback = {'outro_checks': {l: copy.deepcopy(checks) for l in ('zone02', 'zone03')}}
    return spec, 'manifest', proof, 'bank', 'source', playback


class PackageTests(unittest.TestCase):
    def test_matching_complete_proofs_pass(self): require_proofs(*fixture())

    def test_stale_bank_fails(self):
        args = list(fixture()); args[3] = 'other'
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_missing_decoder_fails(self):
        args = fixture(); del args[2]['decoded_fields']
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_partial_source_proof_fails(self):
        args = fixture(); args[2]['original_audio_unchanged'] = False
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_missing_outro_capture_fails(self):
        args = fixture(); args[5]['outro_checks']['zone03'].pop()
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_unreviewed_new_targets_fail(self):
        args = fixture(); args[0]['static_targets'][0] = 'other'
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_state_scope_regression_fails(self):
        args = fixture(); args[0]['state_scopes'] = ['location']
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_missing_decoded_record_fails(self):
        args = fixture(); args[2]['decoded_fields']['records'].pop('719937819')
        with self.assertRaises(ValueError): require_proofs(*args)

    def test_wrong_parent_fails(self):
        args = fixture(); args[2]['decoded_fields']['records']['719937819']['parent'] = 432285193
        with self.assertRaises(ValueError): require_proofs(*args)
