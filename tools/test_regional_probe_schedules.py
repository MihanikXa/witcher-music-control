import unittest
from white_orchard_transition_probe import regional_cases
from white_orchard_transition_probe import protected_audition
from white_orchard_transition_probe import primeable_location
import xml.etree.ElementTree as E


class RegionalProbeScheduleTests(unittest.TestCase):
    def test_boat_return_observed_after_combat(self):
        seq = regional_cases()['boat-combat']
        self.assertEqual([x[1] for x in seq], ['exploration', 'boat', 'combat', 'boat', 'exploration'])
        self.assertEqual(seq[-1][0], 30)
        self.assertTrue(all(a[0] < b[0] for a,b in zip(seq,seq[1:])))

    def test_preserved_states_have_separate_controls(self):
        cases = regional_cases()
        self.assertEqual(cases['minigames'], [(0, 'minigames', None)])
        self.assertEqual(cases['music-master'], [(0, 'dialog_scene', None)])

    def test_authored_audition_rejects_wrong_ancestry_or_edit(self):
        tree=E.fromstring('<Music><MusicSwitchContainer ID="quest"><MusicPlaylistContainer ID="authored" /></MusicSwitchContainer><MusicPlaylistContainer ID="generic" /></Music>')
        spec={'facts':{'quest':{'id':'quest'}},'static_targets':['generic']}
        self.assertEqual(protected_audition(tree,spec,'authored'),'authored')
        for ident in ('generic','missing','quest'):
            with self.assertRaises(ValueError):protected_audition(tree,spec,ident)
        spec['static_targets'].append('authored')
        with self.assertRaises(ValueError):protected_audition(tree,spec,'authored')

    def test_location_priming_rejects_play_or_missing_event(self):
        tree=E.fromstring('<Events><Event Name="location"><ChildrenList><Action><PropertyList><Property Name="ActionType" Value="23" /></PropertyList></Action></ChildrenList></Event></Events>')
        primeable_location(tree,'location')
        tree.find('.//Property').set('Value','1')
        for name in ('location','missing'):
            with self.assertRaisesRegex(ValueError,'switch-only'):primeable_location(tree,name)
