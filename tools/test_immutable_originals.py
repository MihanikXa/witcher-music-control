"""Immutable build-audio linking: identity, stale input and containment controls."""
import os
from pathlib import Path
import tempfile
import unittest
from white_orchard_prepare import REPO, stage_original, digest


class ImmutableOriginalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=REPO / 'build')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.relative = Path('Originals/SFX/test.wav')
        self.source = self.root / 'installed'
        self.pool = self.root / 'canonical'
        for folder in (self.source, self.pool):
            p = folder / self.relative
            p.parent.mkdir(parents=True)
            p.write_bytes(b'immutable audio')
        self.target = self.root / 'candidate' / self.relative

    def test_verified_link_not_installed_link(self):
        sha = stage_original(self.source, self.target, self.relative, self.pool)
        self.assertTrue(os.path.samefile(self.pool / self.relative, self.target))
        self.assertFalse(os.path.samefile(self.source / self.relative, self.target))
        self.assertEqual(sha, digest(self.target))

    def test_independent_default_copy(self):
        stage_original(self.source, self.target, self.relative)
        self.assertFalse(os.path.samefile(self.source / self.relative, self.target))

    def test_stale_pool_rejected(self):
        (self.pool / self.relative).write_bytes(b'stale')
        with self.assertRaises(ValueError):
            stage_original(self.source, self.target, self.relative, self.pool)
        self.assertFalse(self.target.exists())

    def test_existing_destination_rejected(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):
            stage_original(self.source, self.target, self.relative, self.pool)
        self.assertEqual(self.target.read_bytes(), b'preserve')

    def test_work_unit_and_escape_rejected(self):
        for rel in ('States/test.wwu', 'Originals/SFX/../../../test.wav'):
            with self.assertRaises(ValueError):
                stage_original(self.source, self.target, rel, self.pool)
