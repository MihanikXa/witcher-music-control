"""Synthetic regression for the opt-in S18 dry release, no audio assets."""
import unittest
import numpy as np
from cue_freeze_dsp import aligned_dry_envelope,dry_db_release,dry_envelope
from cue_freeze_dsp import render_continuous


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

    def test_local_send_fade_is_smooth_and_ends_before_cut(self):
        rate=48000; source=np.zeros((4*rate,2)); source[:,0]=source[:,1]=.1
        s=dict(source_in=0.,source_out=4.,dry_fade=[1.5,4.],fade_in=.2,
               highpass_hz=170,lowpass_hz=3900,send_policy='pre_ending_fade',
               send_stop_guard_seconds=.02,continuous_wet_db=-14)
        s['local_send_fade']=dict(center_source_seconds=3.2,width_seconds=.5)
        out,proof,c=render_continuous(source,s,5.5,wet_gain=.02)
        self.assertEqual(proof['local_send_fade'],s['local_send_fade'])
        send=c['send_envelope'];a=round(2.95*rate);b=round(3.45*rate)
        self.assertEqual(send[a],1.)
        self.assertTrue(np.all(np.diff(send[a:b+1])<=1e-12))
        self.assertEqual(send[b],0.)
        self.assertTrue(np.all(send[b:]==0))

    def test_local_send_fade_invalid_or_crosses_cut_rejected(self):
        rate=48000; source=np.ones((4*rate,2))*.01
        s=dict(source_in=0.,source_out=4.,dry_fade=[1.,4.],fade_in=.2,
               highpass_hz=170,lowpass_hz=3900,send_policy='pre_ending_fade',
               send_stop_guard_seconds=.02,continuous_wet_db=-14,
               local_send_fade=dict(center_source_seconds=4.,width_seconds=.5))
        with self.assertRaises(ValueError):render_continuous(source,s,5.5,wet_gain=.02)

    def test_local_alignment_smoothly_delays_fade_progress_without_reversal(self):
        rate=48000;frames=3*rate
        old=dry_envelope(frames,rate,.1,.8,3.)
        for center in (1.45,1.575,1.65):
            new=aligned_dry_envelope(frames,rate,.1,.8,3.,center,.1,.5)
            self.assertTrue(np.isfinite(new).all())
            self.assertTrue((np.diff(new[round(.8*rate):])<=1e-12).all())
            self.assertGreater(new[round(center*rate)],old[round(center*rate)])
            self.assertEqual(new[round(3*rate)-1],old[round(3*rate)-1])
            np.testing.assert_array_equal(new[:round(.8*rate)],old[:round(.8*rate)])
            lo=round((center-.25)*rate);hi=round((center+.25)*rate)
            np.testing.assert_array_equal(new[:lo],old[:lo])
            np.testing.assert_array_equal(new[hi:],old[hi:])

    def test_local_alignment_rejects_bad_center_and_shape(self):
        for args in [(0.8,.1,.5),(3.2,.1,.5),(1.5,3.,.5),(1.5,.1,0)]:
            with self.assertRaises(ValueError):aligned_dry_envelope(3*48000,48000,.1,.8,3.,*args)


if __name__=='__main__':unittest.main()
