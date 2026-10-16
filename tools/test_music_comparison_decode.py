import struct
import unittest

from music_comparison_decode import music, track
from music_plus_audit import fnv, event_switch, playback_closure
from test_regional_music_bank import node


def common():
    return node()[:-4] + struct.pack('<IddfBBBI', 0, 1000, 0, 120, 4, 4, 0, 0)


def item(segment=0, children=0, loop=1, weight=50000):
    return struct.pack('<IIIIhhhIHBB', segment, 21, children, 0, loop, 0, 0, weight, 0, 1, 0)


def playlist():
    return common() + struct.pack('<II', 0, 2) + item(children=1) + item(99)


def switch(nodes=None):
    nodes = nodes if nodes is not None else [(0, 1 | (1 << 16), 50, 100), (11, 99, 50, 100)]
    return (common() + struct.pack('<IBIIBIB', 0, 0, 1, 7, 1, len(nodes) * 12, 0)
            + b''.join(struct.pack('<IIHH', *n) for n in nodes))


class MusicInspectionTests(unittest.TestCase):
    def test_playlist(self):
        d = music(13, playlist())
        self.assertEqual([i['segment'] for i in d['playlist']], [0, 99])
        self.assertEqual(d['parent'], 123)
        self.assertEqual(d['playlist'][1]['offset'] - d['playlist'][0]['offset'], 30)

    def test_switch(self):
        d = music(12, switch())
        self.assertEqual(d['arguments'], [(7, 1)])
        self.assertEqual(d['entries'][0]['target'], 99)
        self.assertEqual(d['entries'][0]['path'], [11])

    def test_segment(self):
        d = music(10, common() + struct.pack('<dIId', 12000, 1, 1, 11000) + b'exit\0')
        self.assertEqual(d['duration_ms'], 12000)
        self.assertEqual(d['markers'][0]['position'], 11000)

    def test_truncation_and_trailing(self):
        b = playlist()
        for size in range(len(b)):
            with self.subTest(size=size), self.assertRaises(ValueError):
                music(13, b[:size])
        with self.assertRaises(ValueError):
            music(13, b + b'X')

    def test_bad_playlist_counts(self):
        for b in [common() + struct.pack('<II', 0, 1) + item(children=1),
                  common() + struct.pack('<II', 0, 2) + item() + item(9),
                  common() + struct.pack('<II', 0, 0xffffffff)]:
            with self.assertRaises(ValueError):
                music(13, b)

    def test_invalid_tree(self):
        for nodes in [[(0, 0 | (1 << 16), 50, 100), (11, 99, 50, 100)],
                      [(0, 12 | (1 << 16), 50, 100), (11, 99, 50, 100)],
                      [(0, 1 | (1 << 16), 50, 100), (11, 99, 50, 100), (12, 98, 50, 100)]]:
            with self.assertRaises(ValueError):
                music(12, switch(nodes))

    def test_unknown_layout_version(self):
        for kind, version in [(11, 150), (13, 149)]:
            with self.assertRaises(ValueError):
                music(kind, playlist(), version)

    def test_nonautomated_listener_prefix(self):
        b = bytearray(playlist())
        b[16] = 3
        b[17:17] = b'\0'
        self.assertEqual(music(13, b)['positioning'], [3, 0])
        b[16] = 35
        with self.assertRaises(ValueError):
            music(13, b)

    def test_track_and_bad_tail(self):
        # Source/clip/automation counts, NodeBase without MusicNode flag, type/lookahead.
        b = b'\0' + bytes(12) + node()[1:-4] + struct.pack('<Bi', 0, 200)
        self.assertEqual(track(b)['lookahead'], 200)
        self.assertEqual(track(b)['sources'], [])
        for changed in [b[:-1], b + b'X']:
            with self.assertRaises(ValueError):
                track(changed)

    def test_name_hash_crosschecked_native_identity(self):
        self.assertEqual(fnv('game_state'), 766723505)
        self.assertEqual(fnv('music_type'), 884382085)
        self.assertEqual(fnv('Music'), 3991942870)

    def test_action_and_fail_closed(self):
        body = b'\x01\x19' + struct.pack('<I', 12) + bytes(3) + struct.pack('<II', 7, 12)
        bank = {'records': {fnv('event'): (4, b'\1' + struct.pack('<I', 9)), 9: (3, body)}}
        self.assertEqual(event_switch(bank, 'event'), (7, 12))
        for bad in [body + b'X', b'\0' + body[1:], body[:-1], body[:2] + bytes(4) + body[6:]]:
            bank['records'][9] = (3, bad)
            with self.assertRaises(ValueError):
                event_switch(bank, 'event')

    def test_conservative_closure(self):
        bank = {'records': {1: (12, switch()), 99: (13, playlist()),
                            77: (13, playlist())}}
        self.assertEqual(playback_closure(bank, 1), {1, 99})

    def test_nan_duration(self):
        with self.assertRaises(ValueError):
            music(10, common() + struct.pack('<dI', float('nan'), 0))


if __name__ == '__main__':
    unittest.main()
