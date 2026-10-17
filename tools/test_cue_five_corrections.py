"""Bounded correction policies and exact preferred-PCM crop regression."""
import copy
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from cue_five_corrections import RATE, crop_preferred_pcm, validate_settings
from cue_freeze_dsp import dry_envelope, render_continuous


class FiveCorrectionsTests(unittest.TestCase):
    def settings(self,key):
        a,b={'S04-a':(3.15,34),'S16-1':(0,42.3),'S18-2':(61,100.8),
             'S14-1':(0,64.5),'S14-2':(64.5,132)}[key]
        s=dict(cue=key,source_in=a,source_out=b,dry_fade=[b-7.3,b],
               comparison_only=False,treatment='natural_decay',rt60=9,
               highpass_hz=80,lowpass_hz=3000,continuous_wet_db=-14,
               send_policy='post_fader',fade_in=.02)
        if key=='S04-a':s.update(dry_fade=[31,34],send_policy='pre_ending_fade')
        return s

    def test_all_five_scopes_accepted(self):
        for key in ['S04-a','S16-1','S18-2','S14-1','S14-2']:
            s=self.settings(key);validate_settings(key,s,{'settings':s})

    def test_forbidden_boundary_and_policy_changes(self):
        for key,change in [('S16-1',{'source_out':43}),('S18-2',{'source_out':101.5}),
                           ('S14-1',{'comparison_only':True}),('S14-2',{'highpass_hz':250}),
                           ('S16-1',{'dry_fade':[40.1,42.3]})]:
            s=self.settings(key);s.update(change)
            with self.assertRaises(ValueError):validate_settings(key,s,{'settings':s})

    def test_preferred_c_ending_is_pinned(self):
        prior=self.settings('S04-a');s=copy.deepcopy(prior);s['rt60']=10
        with self.assertRaises(ValueError):validate_settings('S04-a',s,{'settings':prior})

    def test_crop_preserves_stereo_pcm_suffix_and_lead(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a.wav',Path(tmp)/'b.wav'
            pcm=np.arange(4*RATE*2,dtype=np.int16).reshape(-1,2);pcm[:2*RATE]=0
            with wave.open(str(a),'wb') as w:
                w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
            crop_preferred_pcm(a,b,.25)
            with wave.open(str(b),'rb') as r:out=np.frombuffer(r.readframes(r.getnframes()),dtype=np.int16).reshape(-1,2)
            np.testing.assert_array_equal(out[:2*RATE],0)
            np.testing.assert_array_equal(out[2*RATE:],pcm[round(2.25*RATE):])

    def test_gradual_release_reduces_processing_steepness(self):
        # Constant stereo source isolates processing from natural musical dynamics.
        frames=round(42.3*RATE)
        old=dry_envelope(frames,RATE,.02,40.1,42.3)
        new=dry_envelope(frames,RATE,.02,35.,42.3)
        def span(e):
            release=e[35*RATE:]
            return (np.flatnonzero(release<.1)[0]-np.flatnonzero(release<.9)[0])/RATE
        self.assertGreater(span(new),span(old)*3)
        self.assertEqual(new[-1],0)

    def test_lower_send_highpass_carries_low_instrument(self):
        t=np.arange(RATE)/RATE;x=np.sin(2*np.pi*100*t)
        def rms(hp):
            y=signal.sosfilt(signal.butter(2,hp,'highpass',fs=RATE,output='sos'),x)
            return np.sqrt(np.mean(y[RATE//2:]**2))
        self.assertGreater(20*np.log10(rms(80)/rms(250)),10)

    def test_rejected_future_samples_never_feed_room(self):
        t=np.arange(4*RATE)/RATE
        source=np.column_stack([.05*np.sin(2*np.pi*180*t),.04*np.sin(2*np.pi*227*t)])
        s=dict(source_in=0,source_out=2.5,dry_fade=[1.8,2.5],fade_in=.02,
               highpass_hz=80,lowpass_hz=3000,continuous_wet_db=-16,send_policy='post_fader')
        a,p,_=render_continuous(source,s,2)
        source[round(2.5*RATE):]=.8
        b,q,_=render_continuous(source,s,2)
        np.testing.assert_array_equal(a,b)
        self.assertLess(p['cleanup_peak_dbfs'],-100)
        self.assertEqual(p['source_end_frame'],round(2.5*RATE))


if __name__=='__main__':unittest.main()
