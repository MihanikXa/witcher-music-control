"""Synthetic selector-graph controls; no installed input or Wwise needed."""
import unittest
import xml.etree.ElementTree as E
from pathlib import Path
import struct
import tempfile

from music_region_inventory import REGIONS, entries, inventory, native_banks


def entry(parent, target, state='exploration'):
    node = E.SubElement(parent, 'ObjectLists')
    node = E.SubElement(node, 'ObjectList', Name='Entries')
    node = E.SubElement(E.SubElement(E.SubElement(node, 'Reference'), 'Local'), 'MultiSwitchEntry')
    if target:
        ref = E.SubElement(E.SubElement(node, 'ReferenceList'), 'Reference', Name='AudioNode')
        E.SubElement(ref, 'ObjectRef', ID=target, Name='playlist')
    ref = E.SubElement(E.SubElement(E.SubElement(node, 'ObjectLists'), 'ObjectList', Name='EntryPath'), 'Reference')
    E.SubElement(ref, 'ObjectRef', ID='state', Name=state)


def fixture():
    music, events, banks = E.Element('Music'), E.Element('Events'), E.Element('Banks')
    for i, name in enumerate(REGIONS):
        root = E.SubElement(music, 'MusicSwitchContainer', ID=f'r{i}', Name=name)
        children = E.SubElement(root, 'ChildrenList')
        world = E.SubElement(children, 'MusicSwitchContainer', ID=f'w{i}', Name='world_music')
        quest = E.SubElement(children, 'MusicSwitchContainer', ID=f'q{i}',
                             Name='quests_cutscenes' if i == 6 else 'quests_and_cutscenes')
        selector = E.SubElement(E.SubElement(world, 'ChildrenList'), 'MusicSwitchContainer', ID=f's{i}', Name='location')
        playlist = E.SubElement(E.SubElement(selector, 'ChildrenList'), 'MusicPlaylistContainer', ID=f'p{i}', Name='generic', ShortID=str(i + 1))
        E.SubElement(playlist, 'AudioFile').text = 'shared.wav'
        qlist = E.SubElement(E.SubElement(quest, 'ChildrenList'), 'MusicPlaylistContainer', ID=f'qp{i}', Name='authored')
        E.SubElement(qlist, 'AudioFile').text = 'shared.wav'
        entry(world, f's{i}', 'location_value')
        entry(selector, f'p{i}')
        E.SubElement(banks, 'SoundBank', Name=name)
    return music, events, banks


class InventoryTests(unittest.TestCase):
    def test_eight_regions_and_misty_alias(self):
        r = inventory(*fixture())['regions']
        self.assertEqual(len(r), 8)
        self.assertEqual(r[6]['quest']['name'], 'quests_cutscenes')

    def test_shared_source_is_evidence_not_policy(self):
        r = inventory(*fixture())
        self.assertEqual(r['regions'][0]['playlists'][0]['quest_branch_shared_files'], ['shared.wav'])
        self.assertEqual(r['policy_classification'], 'none; human-reviewed decisions required')

    def test_entries_ignore_descendant_routes(self):
        music, _, _ = fixture()
        root = music[0]
        self.assertEqual(entries(root), [])
        self.assertEqual(len(entries(root.find('./ChildrenList/*'))), 1)

    def test_explicit_empty_choice_retained(self):
        n = E.Element('MusicSwitchContainer')
        entry(n, None, 'credits')
        self.assertIsNone(entries(n)[0]['target'])
        self.assertEqual(entries(n)[0]['path'][0]['Name'], 'credits')

    def test_unresolved_audio_node_fails(self):
        m, e, b = fixture()
        entry(m[0], 'missing')
        with self.assertRaisesRegex(ValueError, 'Unresolved AudioNode'):
            inventory(m, e, b)

    def test_missing_region_fails(self):
        m, e, b = fixture()
        m.remove(m[0])
        with self.assertRaisesRegex(ValueError, 'regional root'):
            inventory(m, e, b)

    def test_missing_bank_fails(self):
        m, e, b = fixture()
        b.remove(b[0])
        with self.assertRaisesRegex(ValueError, 'regional bank'):
            inventory(m, e, b)

    def test_cross_branch_consumer_detected(self):
        m, e, b = fixture()
        quest = m[0].find('./ChildrenList/*[@Name="quests_and_cutscenes"]')
        entry(quest, 'p0', 'quest_cue')
        result = inventory(m, e, b)['regions'][0]['playlists'][0]
        self.assertEqual(result['outside_world_consumers'][0]['path'], ['quest_cue'])

    def test_native_membership_reports_absence_and_cross_bank_presence(self):
        result = inventory(*fixture())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in (*REGIONS, 'music_shared'):
                # ID1 absent from its own bank, present in shared. No ownership
                # conclusion is allowed from this independent membership fact.
                ids = [1] if name == 'music_shared' else []
                hirc = struct.pack('<I', len(ids)) + b''.join(
                    struct.pack('<BII', 13, 4, ident) for ident in ids)
                (root / (name + '.bnk')).write_bytes(b'HIRC' + struct.pack('<I', len(hirc)) + hirc)
            native_banks(result, root)
        bank = result['regions'][0]['native_bank']
        self.assertEqual(bank['world_playlists_absent'][0]['id'], 'p0')
        self.assertEqual(bank['world_playlist_ids_present_elsewhere'], {'music_shared': [1]})

    def test_missing_native_bank_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                native_banks(inventory(*fixture()), Path(tmp))


if __name__ == '__main__':
    unittest.main()
