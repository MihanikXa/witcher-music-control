"""Batch scope, explicit timing and quiet-native-release safety regressions."""
import copy
import unittest
import numpy as np
from cue_remainder_batch import REPO,PLAN,RATE,read,validate_plan,render_source_release


class RemainderBatchTests(unittest.TestCase):
    def setUp(self):
        self.plan=read(PLAN)
        self.ledger=read(REPO/'research/69-treatment-predictions.json')

    def test_reviewed_twelve_cue_scope_and_three_single_variable_alternatives(self):
        validate_plan(self.plan,self.ledger)
        self.assertEqual(sum(bool(c['alternative_changes']) for c in self.plan['cues']),3)
        self.assertNotIn('S18-3',[c['cue'] for c in self.plan['cues']])

    def test_reject_changed_explicit_fade_or_source_cut(self):
        for field in ('dry_fade','source_out'):
            p=copy.deepcopy(self.plan);c=next(c for c in p['cues'] if c['cue']=='S11-long')
            if field=='dry_fade':c['settings'][field][0]-=.1
            else:c['settings'][field]-=.1
            with self.assertRaises(ValueError):validate_plan(p,self.ledger)

    def test_reject_lost_restriction_and_unapproved_cue(self):
        p=copy.deepcopy(self.plan);p['cues'][-1]['comparison_only']=False
        with self.assertRaises(ValueError):validate_plan(p,self.ledger)
        p=copy.deepcopy(self.plan);p['cues'][0]['cue']='S18-3'
        with self.assertRaises(ValueError):validate_plan(p,self.ledger)

    def test_reject_multi_variable_and_excess_alternatives(self):
        p=copy.deepcopy(self.plan);p['cues'][0]['alternative_changes']['rt60']=8
        with self.assertRaises(ValueError):validate_plan(p,self.ledger)
        p=copy.deepcopy(self.plan);next(c for c in p['cues'] if c['cue']=='S07-a')['alternative_changes']={'send_policy':'pre_ending_fade'}
        with self.assertRaises(ValueError):validate_plan(p,self.ledger)

    def test_quiet_release_keeps_original_timing_and_stereo_without_added_tail(self):
        t=np.arange(5*RATE)/RATE
        source=np.stack([.1*np.sin(2*np.pi*220*t)*np.exp(-3*t),.07*np.sin(2*np.pi*330*t)*np.exp(-3*t)],axis=1)
        s=dict(source_in=1.,source_out=4.5,dry_fade=[4.48,4.5],fade_in=.02,guard_peak_ceiling_dbfs=-60)
        audio,p,c=render_source_release(source,s)
        self.assertEqual(len(audio),round(8.5*RATE))
        self.assertEqual(p['wet_gain'],0)
        self.assertEqual(p['tail_extra'],0)
        self.assertTrue(np.all(c['wet']==0))
        self.assertTrue(np.all(audio[:2*RATE]==0));self.assertTrue(np.all(audio[-3*RATE:]==0))
        a=round(1.02*RATE);b=round(4.48*RATE)
        np.testing.assert_array_equal(audio[round(2.02*RATE):round(5.48*RATE)],source[a:b])
        self.assertEqual(p['source_end_frame'],round(4.5*RATE))

    def test_quiet_guard_rejects_active_source_and_no_added_room_policy(self):
        s=dict(source_in=0.,source_out=2.,dry_fade=[1.98,2.],fade_in=.02,guard_peak_ceiling_dbfs=-60)
        with self.assertRaises(ValueError):render_source_release(np.ones((2*RATE,2))*.1,s)
        p=copy.deepcopy(self.plan);c=next(c for c in p['cues'] if c['cue']=='S12-4');c['settings']['rt60']=4.5
        with self.assertRaises(ValueError):validate_plan(p,self.ledger)
        p=copy.deepcopy(self.plan);c=next(c for c in p['cues'] if c['cue']=='S12-4');c['settings']['dry_fade'][0]-=.2
        with self.assertRaises(ValueError):validate_plan(p,self.ledger)

    def test_source_release_headroom_only_attenuates_entire_stereo_cue(self):
        source=np.ones((2*RATE,2))*.995;source[:,1]*=.5;source[-RATE//2:]=1e-7
        s=dict(source_in=0.,source_out=2.,dry_fade=[1.98,2.],fade_in=.02,guard_peak_ceiling_dbfs=-60)
        audio,p,c=render_source_release(source,s)
        self.assertLess(p['headroom_gain'],1.)
        self.assertAlmostEqual(np.max(np.abs(audio)),.96)
        np.testing.assert_array_equal(audio[3*RATE],source[RATE]*p['headroom_gain'])
        self.assertEqual(p['wet_gain'],0)


if __name__=='__main__':unittest.main()
