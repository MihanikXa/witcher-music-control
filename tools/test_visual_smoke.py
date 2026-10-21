import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import visual_smoke_build as visual


class VisualSmokeTests(unittest.TestCase):
    def test_constant_control_retains_queries_and_annotations(self):
        text = visual.SOURCE.read_text(encoding='utf-8')
        control = visual.control_source(text)
        self.assertEqual(control.count('@wrapMethod('), 1)
        for query in ('GetCurrentGameState()', 'GetCurrentArea()', 'IsUsingHorse(true)', 'IsUsingBoat()',
                      'ShouldEnableCombatMusic()', 'IsNight()', 'wrappedMethod();'):
            self.assertIn(query, control)
        self.assertEqual(control.replace('ShowNotification("WMCVIS1 snapshot-control", 12.0, false)',
                                         'ShowNotification(row, 12.0, false)'), text)
        with self.assertRaises(ValueError):
            visual.control_source('unexpected source')

    def test_finite_presentation_and_no_audio_or_saved_fields(self):
        text = visual.SOURCE.read_text(encoding='utf-8')
        self.assertIn('wmcVisualSmokeTicks > 30', text)
        self.assertIn('theGame.wmcVisualSmokeMessages >= 2', text)
        self.assertEqual(text.count('.ShowNotification('), 2)
        self.assertIn('owner/outro=unknown', text)
        for forbidden in ('LogChannel(', 'saved var', 'SoundEvent(', 'SoundMusicEvent(', '@replaceMethod',
                          'SetState(', 'SetSwitch(', 'FactsAdd(', 'SaveGame('):
            self.assertNotIn(forbidden, text)

    def exercise_build(self, directory, mismatch=False):
        root = Path(directory)/'private'
        root.mkdir()
        (root/'inputs.json').write_text(json.dumps({'inputs': []}))
        results = [dict(compiled=True, diagnostics={'native baseline': 1}),
                   dict(compiled=True, diagnostics={'annotation diagnostics': 2}),
                   dict(compiled=True, diagnostics={'changed' if mismatch else 'annotation diagnostics': 2})]
        old = visual.compiler.SOURCE
        with patch.object(visual.compiler, 'prepare', return_value=root), \
             patch.object(visual.compiler, 'compile_one', side_effect=results):
            if mismatch:
                with self.assertRaises(RuntimeError):
                    visual.build(root)
            else:
                visual.build(root)
        self.assertEqual(visual.compiler.SOURCE, old)
        return root

    def test_package_exact_single_source_after_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.exercise_build(directory)
            with zipfile.ZipFile(root/'manual/WMC Visual Smoke - Diagnostic.zip') as z:
                self.assertEqual(z.namelist(), [visual.MEMBER])
                self.assertEqual(z.read(visual.MEMBER), visual.SOURCE.read_bytes())

    def test_unexplained_control_difference_prevents_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.exercise_build(directory, mismatch=True)
            self.assertFalse((root/'manual').exists())
            self.assertFalse(json.loads((root/'visual-proof.json').read_text())['ready_for_optional_manual_test'])


if __name__ == '__main__':
    unittest.main()
