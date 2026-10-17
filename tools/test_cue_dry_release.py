"""Synthetic regression for the opt-in S18 dry release, no audio assets."""
import unittest
import numpy as np
from cue_freeze_dsp import dry_db_release,dry_envelope


class DryReleaseTests(unittest.TestCase):
    def test_log_slope_and_quiet_cleanup(self):
        rate=48000
        e=dry_db_release(3*rate,rate,.1,.8,3)
        self.assertTrue(np.isfinite(e).all())
        self.assertTrue((np.diff(e[rate:])<=0).all())
        db=20*np.log10(e[rate:round(2.97*rate)])
        self.assertLess(np.ptp(np.diff(db)),1e-9)
        self.assertAlmostEqual(e[round(2.98*rate)-1],10**(-72/20))
        self.assertEqual(e[-1],0)
        self.assertLess(np.max(np.abs(np.diff(e[-960:]))),5e-7)

    def test_unmodified_before_release_and_after_stop(self):
        e=dry_db_release(4000,1000,.2,1,3)
        legacy=dry_envelope(4000,1000,.2,1,3)
        np.testing.assert_array_equal(e[:1000],legacy[:1000])
        self.assertTrue((e[3000:]==0).all())
        self.assertEqual(e[1000],1)

    def test_reject_invalid_settings(self):
        for kw in [dict(depth_db=float('nan')),dict(depth_db=10),
                   dict(onset_seconds=4),dict(cleanup_seconds=4),
                   dict(cleanup_seconds=0)]:
            with self.assertRaises(ValueError):dry_db_release(3000,1000,.1,1,3,**kw)


if __name__=='__main__':unittest.main()
