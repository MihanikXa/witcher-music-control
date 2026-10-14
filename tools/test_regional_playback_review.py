"""Synthetic controls for bounded outro evidence acceptance."""
import unittest
from regional_playback_review import outro_checks


def fixture():
    return {'cases': [{'mode': m, 'case': c, 'events': [{'state': 'exploration', 'accepted': 13}],
        'voices': {'world/transition_to_expl/outro': {'peak_db': -18, 'last': 21,
                                                    'ended_before_capture_stop': True}}}
        for m in ('native-reference', 'manifest') for c in ('e-combat', 'e-combat-offset')]}


class PlaybackTests(unittest.TestCase):
    def test_complete_native_volume_outro_passes(self):
        self.assertEqual(len(outro_checks(fixture(), 'transition_to_expl', -18)), 4)

    def test_old_ancestor_mute_fails(self):
        data = fixture(); data['cases'][2]['voices']['world/transition_to_expl/outro']['peak_db'] = -218
        with self.assertRaises(ValueError): outro_checks(data, 'transition_to_expl', -18)

    def test_capture_ends_before_outro_finishes_fails(self):
        data = fixture(); data['cases'][3]['voices']['world/transition_to_expl/outro']['ended_before_capture_stop'] = False
        with self.assertRaises(ValueError): outro_checks(data, 'transition_to_expl', -18)

    def test_missing_second_phase_fails(self):
        data = fixture(); data['cases'].pop()
        with self.assertRaises(ValueError): outro_checks(data, 'transition_to_expl', -18)

    def test_duplicate_controls_cannot_replace_candidate_evidence(self):
        data = fixture(); data['cases'][2]['mode'] = 'native-reference'
        with self.assertRaises(ValueError): outro_checks(data, 'transition_to_expl', -18)
