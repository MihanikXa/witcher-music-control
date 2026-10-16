"""Original synthetic DSP/plan tests; no copyrighted audio or app sessions."""
import copy
import json
from pathlib import Path
import unittest
import numpy as np

from cue_freeze_dsp import MATRIX,RATE,Field,render_variants,dry_envelope
from cue_edit_render import validate_plan,page,FEEDBACK


def settings():
    return dict(source_in=.25,source_out=2.25,dry_fade=[1.75,2.25],fade_in=.02,
        tail_extra=2,hold_after_dry=.1,wet_attack=.3,rt60=1,prime_seconds=1,
        highpass_hz=180,lowpass_hz=4000,freeze_transition=.05,wet_db_relative=-14,
        variants=['A','B','C'])


class FreezeTests(unittest.TestCase):
    def test_lossless_state_vs_decay(self):
        self.assertTrue(np.array_equal(MATRIX@MATRIX.T,np.eye(16)))
        for frozen in (False,True):
            f=Field(1)
            impulse=np.zeros((RATE//2,2));impulse[0]=[.5,.25];f.process(impulse)
            out,trace=f.process(np.zeros((RATE*2,2)),freeze=frozen,transition=.05,ledger=True)
            energy=[r['state_energy'] for r in trace if r['seconds']>.1]
            self.assertGreater(np.max(np.abs(out)),0)
            if frozen:self.assertLess((max(energy)-min(energy))/max(energy),1e-10)
            else:self.assertLess(energy[-1]/energy[0],1e-8)
        with self.assertRaises(ValueError):Field().process(np.ones((10,2)),freeze=True)

    def test_source_clock_envelopes_and_quiet_context(self):
        t=np.arange(RATE*3)/RATE;x=np.column_stack((.2*np.sin(2*np.pi*330*t),.15*np.sin(2*np.pi*440*t)))
        outputs,p,dry,env=render_variants(x,settings())
        self.assertEqual(p['source_start_frame'],RATE//4)
        self.assertEqual(p['source_end_frame'],round(2.25*RATE))
        self.assertTrue(np.array_equal(dry,x[RATE//4:round(2.25*RATE)]*env[:,None]))
        self.assertEqual(len({len(a) for a in outputs.values()}),1)
        for a in outputs.values():
            self.assertFalse(np.any(a[:2*RATE]));self.assertFalse(np.any(a[-3*RATE:]));self.assertLessEqual(np.max(np.abs(a)),.96)
        self.assertFalse(np.any(outputs['A'][4*RATE:]))
        self.assertGreater(np.std(outputs['C'][round(4.1*RATE):round(4.5*RATE)]),1e-5)
        self.assertLess(p['field_proof']['C']['settled_relative_energy_range'],1e-10)

    def test_invalid_empty_and_cut_ranges_fail(self):
        x=np.zeros((RATE*3,2))
        with self.assertRaises(ValueError):render_variants(x,settings())
        for patch in ({'source_in':-1},{'source_out':5},{'dry_fade':[2.5,2.2]}):
            with self.subTest(patch=patch),self.assertRaises(ValueError):render_variants(x,dict(settings(),**patch))

    def test_touching_wet_attack_and_fade_is_continuous(self):
        t=np.arange(RATE*3)/RATE;x=np.column_stack([.1*np.sin(2*np.pi*440*t)]*2)
        s=settings();s['wet_attack']=.6 # .5s dry ending plus .1s hold.
        out,proof,_,_=render_variants(x,s)
        self.assertTrue(np.isfinite(out['C']).all())
        self.assertLess(proof['field_proof']['C']['settled_relative_energy_range'],1e-10)

    def test_canonical_feedback_and_authored_restriction(self):
        plan=json.loads((Path(__file__).resolve().parents[1]/'research/61-private-cue-edit-plan.json').read_text(encoding='utf-8'))
        users={r['id']:r for r in json.loads(FEEDBACK.read_text(encoding='utf-8'))}
        validate_plan(plan,users)
        cues={r['cue']:r for r in plan['cues']}
        for ident,a,b,fade in [('S04-a',0,34,[33,34]),('S05-main',0,47.5,[42,47]),
           ('S05-short',0,23.7,[23,23.7]),('S11-short',0,20,[18,20]),('S11-long',0,93,[90,93]),
           ('S07-a',0,72.7,[67,72.7]),('S07-b',81,115,[111,115]),('S07-c',156,176.9,[172,176.9])]:
            c=cues[ident];self.assertEqual((c['source_in'],c['source_out'],c['dry_fade']),(a,b,fade))
        self.assertFalse(any(c['source'] in ('S01','S06','S19') for c in plan['cues']))
        x=copy.deepcopy(plan);x['cues'][0]['verbatim_notes']='invented'
        with self.assertRaises(ValueError):validate_plan(x,users)
        x=copy.deepcopy(plan);next(c for c in x['cues'] if c['source']=='S14')['comparison_only']=False
        with self.assertRaises(ValueError):validate_plan(x,users)


if __name__=='__main__':unittest.main()
