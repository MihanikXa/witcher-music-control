from pathlib import Path
import unittest

from visual_smoke_triage import corrected_source, contract
from visual_smoke_build import control_source


class VisualTriageTests(unittest.TestCase):
    def test_minimal_source_only_unit_and_identity_correction(self):
        root = Path(__file__).resolve().parents[1]/'src/diagnostics'
        original = (root/'wmcVisualSmoke.ws').read_text(encoding='utf-8')
        revised = (root/'wmcVisualSmokeV2.ws').read_text(encoding='utf-8')
        self.assertEqual(corrected_source(original), revised)
        self.assertEqual(revised.count('wrappedMethod();'), 1)
        self.assertIn("AddTimer('WMCVisualSmokeV2Tick', 1.0, true)", revised)
        self.assertEqual(revised.count('.ShowNotification('), 2)
        self.assertIn('4000.0, false', revised)
        self.assertIn('12000.0, false', revised)

    def test_control_keeps_ms_and_native_queries(self):
        source = 'abc ShowNotification(row, 12000.0, false) def'
        self.assertEqual(control_source(source),
                         'abc ShowNotification("WMCVIS1 snapshot-control", 12000.0, false) def')
        for bad in ('ShowNotification(row, value, false)', source+source):
            with self.assertRaises(ValueError):
                control_source(bad)

    def test_contract_fails_closed_on_changed_timer_or_forwarding(self):
        notification = '\n'.join(('private static const DEF_DURATION:Number = 4000;',
                                  'private static const ANIMATION_DURATION:Number = .3;',
                                  '_duration = msgDuration;',
                                  '_duration = _duration ? _duration : DEF_DURATION;',
                                  '_timer = new Timer(_duration)', 'initTimer();'))
        overlay = 'notificationModule.show(msgText, msgDuration);'
        self.assertEqual(contract(notification, overlay)['original_ms'], [4, 12])
        for bad in (notification.replace('4000', '4'), notification.replace('new Timer(_duration)',
                                                                                  'new Timer(_duration*1000)')):
            with self.assertRaises(ValueError):
                contract(bad, overlay)
        with self.assertRaises(ValueError):
            contract(notification, '')

    def test_does_not_silently_modify_unknown_original(self):
        with self.assertRaises(ValueError):
            corrected_source('unreviewed source')


if __name__ == '__main__':
    unittest.main()
