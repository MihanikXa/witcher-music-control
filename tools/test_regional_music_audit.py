"""Source-only membership and indirect event consumers are audit facts, not policy."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as E
from regional_music_audit import audit


class AuditTests(unittest.TestCase):
    def test_descendant_events_and_absent_objects_never_become_approved(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for d in ('Interactive Music Hierarchy','Events','SoundBanks'):(root/d).mkdir()
            music=E.fromstring('<Music><MusicSwitchContainer ID="root" Name="region"><ChildrenList><MusicSwitchContainer ID="world" Name="world_music" ShortID="2"><ChildrenList><MusicPlaylistContainer ID="p" Name="quest_looks_generic" ShortID="4"><ChildrenList><MusicSegment ID="segment" ShortID="5"/></ChildrenList></MusicPlaylistContainer></ChildrenList></MusicSwitchContainer></ChildrenList></MusicSwitchContainer></Music>')
            E.ElementTree(music).write(root/'Interactive Music Hierarchy/music.wwu')
            (root/'Events/music.wwu').write_text('<Events><Event ID="event"><ChildrenList><Action><ObjectRef ID="segment"/></Action></ChildrenList></Event></Events>')
            (root/'SoundBanks/music.wwu').write_text('<Banks/>')
            row={'name':'region','playlists':[{'id':'p','name':'quest_looks_generic','short_id':'4','audio_files':[]} ]}
            with patch('regional_music_audit.inventory',return_value={'regions':[row]}),patch('regional_music_audit.read_bank',return_value={'records':{},'sha256':'fixture'}):
                result=audit(root,root,['region'])
            target=result['regions'][0]['reviewed_targets'][0]
            self.assertFalse(target['native_present'])
            self.assertEqual(target['all_event_descendant_consumers'][0]['event_id'],'event')
            self.assertNotIn('classification',target)
