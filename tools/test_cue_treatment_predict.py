import unittest
import numpy as np
from cue_treatment_predict import source_features,predict,TRIAL
from cue_freeze_dsp import RATE


class TreatmentPredictionTests(unittest.TestCase):
    def settings(self):
        return dict(source_in=0,source_out=4,dry_fade=[3.3,4],fade_in=.02,
                    highpass_hz=200,lowpass_hz=3800)

    def features(self):
        t=np.arange(4*RATE)/RATE
        x=np.repeat((.1*np.sin(2*np.pi*330*t))[:,None],2,axis=1)
        return source_features(x,self.settings())

    def test_source_measurement_and_limits(self):
        f=self.features()
        self.assertAlmostEqual(f['last_half_second_dbfs'],-23.0103,places=3)
        self.assertLess(f['pitch_class_change_p90'],.01)
        self.assertIsNone(f['original_room_rt60'])
        self.assertEqual(f['crop_frames'],[0,4*RATE])
        self.assertEqual(len(f['ending_100ms_rms_dbfs']),40)

    def test_short_provisional_vs_explicit_fades(self):
        s=self.settings();f=self.features()
        p=predict(s,f,False);q=predict(s,f,True)
        self.assertEqual(p['send_policy'],'pre_ending_fade')
        self.assertAlmostEqual(p['dry_fade'][0],1.8)
        self.assertEqual(q['dry_fade'],s['dry_fade'])
        self.assertEqual(p['source_out'],q['source_out'])

    def test_quiet_endpoint_not_amplified_or_early_frozen(self):
        f={**self.features(),'last_half_second_dbfs':-80,'source_ending_change_db':-30}
        p=predict(self.settings(),f,False)
        self.assertEqual(p['family'],'already_dissipating')
        self.assertEqual(p['continuous_wet_db'],-23)
        self.assertEqual(p['treatment'],'natural_decay')
        self.assertEqual(p['dry_fade'],self.settings()['dry_fade'])

    def test_long_fade_and_high_activity(self):
        s={**self.settings(),'source_out':8,'dry_fade':[3,8]}
        f={**self.features(),'original_dry_fade_seconds':5,'spectral_flux_p90':.6}
        p=predict(s,f,True)
        self.assertEqual(p['send_policy'],'post_fader')
        self.assertEqual(p['rt60'],6)
        self.assertEqual(p['dry_fade'],s['dry_fade'])
        self.assertEqual(len(set(TRIAL)),6)
        self.assertFalse(any(c.startswith('S14') for c in TRIAL))

    def test_source_range_failure(self):
        with self.assertRaises(ValueError):source_features(np.zeros((RATE,2)),self.settings())


if __name__=='__main__':unittest.main()
