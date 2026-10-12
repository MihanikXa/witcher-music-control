"""Negative controls for the bounded read-only playlist delta verifier."""
import struct
import unittest

from white_orchard_transition_package import playlist_delta


def body(value=None):
    # Own synthetic prefix/suffix, not a redistributed bank record.
    bundle = b"\0" if value is None else b"\x01\0" + struct.pack("<f", value)
    return bytes(range(14)) + bundle + b"routing-and-transition-sentinel"


class PlaylistGateTests(unittest.TestCase):
    def test_existing_volume_only(self):
        self.assertTrue(playlist_delta(body(1), body(-200), 1)["prefix_suffix_exact"])

    def test_implicit_unity_only(self):
        self.assertTrue(playlist_delta(body(), body(-200), 0)["prefix_suffix_exact"])

    def test_changed_reference_prefix_rejected(self):
        changed = bytearray(body(-200)); changed[9] ^= 1
        with self.assertRaises(ValueError):
            playlist_delta(body(1), changed, 1)

    def test_changed_transition_suffix_rejected(self):
        with self.assertRaises(ValueError):
            playlist_delta(body(1), body(-200) + b"extra", 1)

    def test_wrong_property_id_rejected(self):
        changed = bytearray(body(-200)); changed[15] = 1
        with self.assertRaises(ValueError):
            playlist_delta(body(1), changed, 1)

    def test_wrong_value_rejected(self):
        with self.assertRaises(ValueError):
            playlist_delta(body(1), body(-96), 1)

    def test_unknown_bundle_rejected(self):
        changed = bytearray(body(-200)); changed[14] = 2
        with self.assertRaises(ValueError):
            playlist_delta(body(1), changed, 1)

    def test_truncated_body_rejected(self):
        with self.assertRaises(ValueError):
            playlist_delta(b"\0", body(-200), 0)


if __name__ == "__main__":
    unittest.main()
