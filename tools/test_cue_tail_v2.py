"""Regression tests for continuous-send architecture and diagnostic counterexamples."""
import unittest
import numpy as np
from cue_freeze_dsp import RATE,render_continuous,release_diagnostics,validate_wet_control,finish_quiet_tail


class ContinuousTailTests(unittest.TestCase):
    def source(self):
        t=np.arange(5*RATE)/RATE
        return np.stack([.15*np.sin(2*np.pi*317*t),.13*np.sin(2*np.pi*419*t)],axis=1)

    def settings(self):
        return dict(source_in=0,source_out=5,dry_fade=[3,5],fade_in=.02,
                    highpass_hz=180,lowpass_hz=3800,continuous_wet_db=-21)

    def test_continuous_send_and_decay(self):
        x,p,c=render_continuous(self.source(),self.settings(),4)
        self.assertGreater(np.sqrt(np.mean(c['wet'][RATE:2*RATE]**2)),1e-5)
        self.assertLess(p['cleanup_peak_dbfs'],-100)
        self.assertLess(p['energy_trace'][-1]['state_energy'],p['initial_energy']*1e-8)
        self.assertFalse(p['release_diagnostics']['rebound_review'])
        self.assertFalse(p['release_diagnostics']['plateau_window_starts'])
        self.assertFalse(np.any(x[:2*RATE]));self.assertFalse(np.any(x[-3*RATE:]))
        self.assertLess(p['dry_stop_max_sample_delta'],.02)

    def test_freeze_same_field_and_single_release(self):
        b,p,bc=render_continuous(self.source(),self.settings(),4)
        c,q,cc=render_continuous(self.source(),self.settings(),4,True,p['wet_gain'])
        self.assertTrue(np.array_equal(b[:7*RATE],c[:7*RATE]))
        self.assertLess(q['settled_energy_relative_range'],1e-10)
        self.assertFalse(q['release_diagnostics']['plateau_window_starts'])
        self.assertFalse(q['release_diagnostics']['rebound_review'])

    def test_explicit_onset_edit_no_clock_shift(self):
        s=self.settings();s.update(onset_mute_seconds=1,onset_ramp_seconds=.3)
        x,p,c=render_continuous(self.source(),s,4)
        self.assertFalse(np.any(x[2*RATE:3*RATE]))
        self.assertEqual(p['source_start_frame'],0);self.assertEqual(p['source_end_frame'],5*RATE)
        self.assertGreater(np.max(np.abs(x[4*RATE:5*RATE])),.05)

    def test_rebound_plateau_and_truncation_rejected(self):
        # Deliberately bad v1-like envelope: dip, swell, hold, later second fade.
        t=np.arange(8*RATE)/RATE
        amp=np.interp(t,[0,1,2,5,8],[.08,.005,.07,.07,0])
        signal=np.repeat((amp*np.sin(2*np.pi*400*t))[:,None],2,axis=1)
        p=release_diagnostics(signal,0)
        self.assertTrue(p['rebound_review']);self.assertTrue(p['plateau_window_starts'])
        # Overly loud source cannot silently normalize itself to pass.
        with self.assertRaises(ValueError):render_continuous(self.source()*20,self.settings(),4)
        with self.assertRaises(ValueError):render_continuous(self.source(),self.settings(),20)

    def test_longer_rt60_is_real_decay_not_extra_padding(self):
        _,a,_=render_continuous(self.source(),self.settings(),3)
        _,b,_=render_continuous(self.source(),self.settings(),7)
        def loss(p):
            trace=p['energy_trace'];first=next(r['state_energy'] for r in trace if r['seconds']>1)
            late=next(r['state_energy'] for r in trace if r['seconds']>3)
            return 10*np.log10(late/first)
        self.assertLess(loss(a),loss(b)-10)

    def test_component_control_catches_late_attack_hold_and_second_fade(self):
        stop=RATE;g=np.ones(4*RATE)
        self.assertTrue(validate_wet_control(g,stop,False)['no_late_wet_attack'])
        late=g.copy();late[:stop]=np.linspace(0,1,stop)
        with self.assertRaisesRegex(ValueError,'Late wet'):validate_wet_control(late,stop,False)
        hold=g.copy();hold[2*RATE:]=np.linspace(1,0,2*RATE)
        with self.assertRaisesRegex(ValueError,'plateau'):validate_wet_control(hold,stop,True)
        with self.assertRaisesRegex(ValueError,'Artificial'):validate_wet_control(hold,stop,False)
        rebound=g.copy();rebound[stop:2*RATE]=np.linspace(1,.3,RATE)
        with self.assertRaisesRegex(ValueError,'rebounds'):validate_wet_control(rebound,stop,True)

    def test_premature_tail_truncation_fails_before_safety_fade(self):
        loud=np.full((RATE,2),.0001) # -80dBFS: not an acceptable hidden cleanup.
        with self.assertRaisesRegex(ValueError,'extend actual render'):finish_quiet_tail(loud)
        self.assertTrue(np.all(loud==.0001)) # Never fade first, then measure it.
        quiet=np.full((RATE,2),1e-6)
        self.assertEqual(finish_quiet_tail(quiet),1e-6)
        self.assertTrue(np.all(quiet[-1]==0))

    def test_pre_ending_send_changes_room_without_changing_dry_or_cut(self):
        source=self.source();s=self.settings()
        a,p,ac=render_continuous(source,s,4)
        b,q,bc=render_continuous(source,{**s,'send_policy':'pre_ending_fade'},4,wet_gain=p['wet_gain'])
        self.assertTrue(np.array_equal(ac['dry'],bc['dry']))
        self.assertTrue(np.array_equal(a[:5*RATE],b[:5*RATE])) # Up to player5 = source fade start3.
        self.assertEqual(p['source_end_frame'],q['source_end_frame'])
        self.assertGreater(q['post_stop_first_second_dbfs'],p['post_stop_first_second_dbfs']+5)
        self.assertEqual(q['send_stop_guard_seconds'],.02)
        self.assertLess(q['cleanup_peak_dbfs'],-100)
        self.assertFalse(q['release_diagnostics']['rebound_review'])

    def test_unreviewed_send_policies_and_onset_paths_fail_closed(self):
        for settings in [{**self.settings(),'send_policy':'unknown'},
                         {**self.settings(),'send_policy':'pre_ending_fade','onset_mute_seconds':.5},
                         {**self.settings(),'send_policy':'pre_ending_fade','send_stop_guard_seconds':3}]:
            with self.assertRaises(ValueError):render_continuous(self.source(),settings,4)

    def test_fractional_taper_keeps_dry_and_pre_fade_exact(self):
        s=self.settings();source=self.source()
        a,p,ac=render_continuous(source,s,4)
        b,q,bc=render_continuous(source,{**s,'send_policy':'tapered_ending','send_ending_fade_power':.5},4,wet_gain=p['wet_gain'])
        self.assertTrue(np.array_equal(ac['dry'],bc['dry']))
        self.assertTrue(np.array_equal(a[:5*RATE],b[:5*RATE]))
        self.assertGreater(q['post_stop_first_second_dbfs'],p['post_stop_first_second_dbfs'])
        self.assertEqual(q['send_ending_fade_power'],.5)
        self.assertLess(q['cleanup_peak_dbfs'],-100)
        for power in [None,0,1,2]:
            with self.assertRaises(ValueError):render_continuous(source,{**s,'send_policy':'tapered_ending','send_ending_fade_power':power},4)


if __name__=='__main__':unittest.main()
