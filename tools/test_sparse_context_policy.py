import copy
import math
from html.parser import HTMLParser
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from sparse_context_policy import Model,Profile,PROFILES,run
from sparse_context_trial import initial,context,opportunity,metrics,independent_check,write_html,demo_cues
from sparse_context_audit import locate

CUES=[dict(id='a',family='same_composition',seconds=20.,role='punctuation'),
      dict(id='b',family='same_composition',seconds=25.,role='punctuation'),
      dict(id='c',family='other_composition',seconds=45.,role='atmospheric')]
FAST=Profile('test_only',10,10,10,stable=0,quiet_floor=0,ramp=.01,excerpt_gap=0,family_gap=0,recovery=0)


def trace(events,duration=200):return dict(provenance='simulated',duration=duration,events=sorted(events,key=lambda e:e['time']))
def starts(m):return [(r['time'],r['cue']) for r in m.records if r['kind']=='start']


class ContextPolicyTests(unittest.TestCase):
    def test_seeded_replay_and_no_compulsory_interval(self):
        t=trace([context(0,**initial())],3600)
        a=run(t,CUES,PROFILES['restrained'],8);b=run(t,CUES,PROFILES['restrained'],8)
        self.assertEqual(a.records,b.records)
        self.assertEqual(a.intervals,b.intervals)
        self.assertNotEqual(starts(a),starts(run(t,CUES,PROFILES['restrained'],9)))
        zero=replace(FAST,baseline=0,opportunity=0,random_rate=0)
        self.assertEqual(starts(run(t,CUES,zero,0)),[])

    def test_exact_hazard_invariant_to_polling_and_partitioning(self):
        t=trace([context(0,**initial(daypart='night',game_state='exploration_night'))],1800)
        reference=run(t,CUES,PROFILES['contrast'],5)
        for step in (1.,.25):
            dense=copy.deepcopy(t)
            dense['events']+= [dict(time=i*step,kind='poll') for i in range(1,int(1800/step))]
            dense['events'].sort(key=lambda e:e['time'])
            actual=run(dense,CUES,PROFILES['contrast'],5)
            self.assertEqual([id for _,id in starts(reference)],[id for _,id in starts(actual)])
            for (a,_),(b,_) in zip(starts(reference),starts(actual)):self.assertAlmostEqual(a,b,places=7)

    def test_duplicate_snapshots_do_not_restart_eligibility(self):
        t=trace([context(0,**initial())],1200)
        other=copy.deepcopy(t);other['events'] +=[context(i,location='synthetic_generic_A') for i in range(1,1200)]
        a=run(t,CUES,PROFILES['contrast'],2);b=run(other,CUES,PROFILES['contrast'],2)
        self.assertEqual([id for _,id in starts(a)],[id for _,id in starts(b)])
        for (x,_),(y,_) in zip(starts(a),starts(b)):self.assertAlmostEqual(x,y,7)

    def test_duplicate_opportunity_does_not_renew_window_or_rng(self):
        zero=replace(FAST,baseline=0,opportunity=.001,window=30)
        t=trace([context(0,**initial()),opportunity(1,'unique')],60)
        other=trace(t['events']+[opportunity(i,'unique') for i in range(2,50)],60)
        a,b=run(t,CUES,zero,0),run(other,CUES,zero,0)
        self.assertEqual(starts(a),starts(b));self.assertEqual(starts(a),[])
        expired=[r for r in b.records if r['kind']=='opportunity_expired']
        self.assertEqual(len(expired),1);self.assertEqual(expired[0]['time'],31)

    def test_window_may_expire_and_does_not_force_cue(self):
        p=replace(FAST,baseline=0,opportunity=0)
        m=run(trace([context(0,**initial()),opportunity(1,'x')]),CUES,p,1)
        self.assertEqual(len(m.windows),0);self.assertEqual(starts(m),[])
        self.assertTrue(any(r['kind']=='opportunity_expired' for r in m.records))

    def test_constant_hazard_matches_exponential_cdf_not_poll_count(self):
        profile=replace(FAST,random_rate=.01)
        t=trace([context(0,**initial())],10)
        observed=sum(bool(starts(run(t,CUES,profile,seed,'randomized'))) for seed in range(2000))/2000
        self.assertAlmostEqual(observed,1-math.exp(-.01*10),delta=.02)

    def test_opportunity_changes_palette_weight_but_burst_does_not_stack_hazard(self):
        m=Model(CUES,FAST,0);m.apply_batch([context(0,**initial(daypart='night',game_state='exploration_night'))])
        before={c['id']:w for c,w in m.choices()}
        m.apply_batch([opportunity(0,'weather','weather_change')])
        after={c['id']:w for c,w in m.choices()}
        self.assertEqual(after['c'],2*before['c']);self.assertEqual(after['a'],before['a'])
        mass=m.mass(0,10)
        m.apply_batch([opportunity(0,str(i)) for i in range(10)])
        self.assertEqual(m.mass(0,10),mass)

    def test_window_expiration_cannot_cut_committed_phrase(self):
        p=replace(FAST,baseline=0,window=1)
        t=trace([context(0,**initial()),opportunity(0,'x')],40)
        m=run(t,[CUES[0]],p,0)
        self.assertTrue(m.intervals)
        self.assertEqual(m.intervals[0]['reason'],'natural')
        self.assertAlmostEqual(m.intervals[0]['end']-m.intervals[0]['start'],20)

    def test_pause_and_loading_block_and_clear_opportunities(self):
        for flag in ('paused','loading'):
            t=trace([context(0,**initial()),context(5,**{flag:True}),opportunity(6,'blocked'),
                     context(20,**{flag:False})],80)
            m=run(t,CUES,replace(FAST,quiet_floor=10),0)
            self.assertFalse(any(t<30 for t,_ in starts(m)))
            self.assertFalse(any(r['kind']=='opportunity_open' for r in m.records))

    def test_event_while_playing_not_queued(self):
        m=run(trace([context(0,**initial()),opportunity(2,'while-playing')],10),CUES,FAST,0)
        self.assertTrue(starts(m));self.assertEqual(m.windows,{})
        self.assertTrue(any(r['kind']=='opportunity_rejected' for r in m.records))

    def test_unknown_and_authored_owner_override_exploration(self):
        for owner in ('authored','unknown',None):
            m=run(trace([context(0,**initial()),context(5,native_owner=owner)],100),CUES,FAST,0)
            self.assertEqual(m.intervals[0]['end'],5)
            self.assertFalse(any(t>=5 for t,_ in starts(m)))
            self.assertTrue(independent_check(m,trace([context(0,**initial()),context(5,native_owner=owner)],100)))

    def test_world_label_without_reviewed_selector_fails_closed(self):
        for selector in (None,'world','ambiguous_world','authored_world'):
            m=run(trace([context(0,**initial(selector=selector))]),CUES,FAST,1)
            self.assertEqual(starts(m),[])

    def test_combat_exit_is_not_outro_completion(self):
        t=trace([context(0,**initial()),context(5,game_state='combat',native_owner='combat'),
                 context(10,game_state='exploration',native_owner='generic',outro_clear=True)],500)
        m=run(t,CUES,FAST,0)
        self.assertFalse(any(t>=5 for t,_ in starts(m)));self.assertFalse(m.context['outro_clear'])

    def test_old_outro_and_duplicate_completion_do_not_clear_new_combat(self):
        events=[context(0,**initial()),context(5,game_state='combat',native_owner='combat'),
                context(10,game_state='exploration',native_owner='generic'),
                context(12,game_state='combat',native_owner='combat'),context(16,game_state='exploration',native_owner='generic'),
                dict(time=18,kind='outro_end',generation=0,combat_epoch=1),
                dict(time=22,kind='outro_end',generation=0,combat_epoch=2),
                dict(time=30,kind='outro_end',generation=0,combat_epoch=2)]
        m=run(trace(events,50),CUES,replace(FAST,recovery=5),0)
        self.assertFalse(any(5<t<27 for t,_ in starts(m)))
        self.assertTrue(any(t>=27 for t,_ in starts(m)))
        self.assertEqual(m.recover_until,27)
        self.assertEqual([r['accepted'] for r in m.records if r['kind']=='outro_observation'],[False,True,False])

    def test_missing_combat_exit_cannot_accept_outro_ack(self):
        m=run(trace([context(0,**initial()),context(5,game_state='combat',native_owner='combat'),
                     dict(time=10,kind='outro_end',generation=0,combat_epoch=1)]),CUES,FAST,0)
        self.assertFalse(m.context['outro_clear']);self.assertFalse(any(t>5 for t,_ in starts(m)))

    def test_load_invalidates_stale_snapshot_and_events(self):
        t=trace([context(0,**initial()),dict(time=5,kind='load'),context(5,**initial()),
                 context(20,generation=1,**initial()),opportunity(21,'stale')],50)
        m=run(t,CUES,FAST,1)
        self.assertEqual(m.intervals[0]['end'],5)
        self.assertFalse(any(5<=t<20 for t,_ in starts(m)))
        self.assertTrue(any(r['kind']=='stale_context' for r in m.records))
        self.assertTrue(any(r['kind']=='stale_opportunity' for r in m.records))

    def test_same_time_native_veto_wins_exact_hazard_tie(self):
        for reverse in (False,True):
            m=Model(CUES,FAST,0);m.apply_batch([context(0,**initial())]);m.budget=m.mass(0,5)
            m.advance(5);self.assertEqual(starts(m),[])
            events=[opportunity(5,'x'),context(5,native_owner='authored')]
            m.apply_batch(events[::-1] if reverse else events);m.advance(100)
            self.assertEqual(starts(m),[])

    def test_source_family_rejects_other_excerpt_until_gap(self):
        p=replace(FAST,excerpt_gap=40,family_gap=20)
        m=Model(CUES,p,0);m.apply_batch([context(0,**initial())]);m.history.append(dict(id='a',family='same_composition',end=0))
        m.t=15;self.assertEqual(m.choices(),[])
        m.t=21;self.assertEqual([c['id'] for c,w in m.choices()],['b'])
        m.t=41;self.assertEqual({c['id'] for c,w in m.choices()},{'a','b'})

    def test_no_suitable_palette_stays_silent(self):
        m=run(trace([context(0,**initial(activity='horse'))]),[CUES[2]],FAST,0)
        self.assertEqual(starts(m),[]);self.assertGreater(metrics(m,trace([],200))['palette_blocked_seconds'],0)

    def test_rapid_true_context_changes_settle_but_duplicates_do_not_starve(self):
        p=replace(FAST,stable=8)
        events=[context(0,**initial())]+[context(t,location=str(t%2)) for t in range(1,10)]
        events +=[context(t,location='1') for t in range(10,30)]
        m=run(trace(events,50),CUES,p,0)
        self.assertTrue(starts(m));self.assertGreaterEqual(starts(m)[0][0],17)
        self.assertLess(starts(m)[0][0],18)

    def test_remote_or_already_known_discovery_never_opens(self):
        e=opportunity(1,'remote');e['local']=False
        f=opportunity(2,'known');f['first']=False
        m=run(trace([context(0,**initial()),e,f]),CUES,replace(FAST,baseline=0),0)
        self.assertEqual(starts(m),[]);self.assertEqual(m.windows,{})

    def test_window_capacity_and_history_are_bounded(self):
        p=replace(FAST,baseline=0,opportunity=0)
        m=Model(CUES,p,0);m.apply_batch([context(0,**initial())])
        m.apply_batch([opportunity(0,str(i)) for i in range(300)])
        self.assertEqual(len(m.windows),16);self.assertEqual(len(m.seen),256)
        m.apply_batch([opportunity(0,'0')]);self.assertEqual(m.windows['first_discovery:0']['end'],p.window)

    def test_invalid_profile_time_trace_or_scope_rejected(self):
        for value in (-1,float('nan'),float('inf'),True):
            with self.assertRaises(ValueError):replace(FAST,baseline=value)
        with self.assertRaises(ValueError):run(dict(provenance='game capture',events=[],duration=1),CUES,FAST,0)
        with self.assertRaises(ValueError):run(trace([context(0,**initial())],-1),CUES,FAST,0)
        with self.assertRaises(ValueError):Model(CUES*2,FAST,0)
        with self.assertRaises(ValueError):run(trace([context(0,unsupported='x')]),CUES,FAST,0)
        with self.assertRaises(ValueError):run(trace([context(0,region='a'),context(0,region='b')]),CUES,FAST,0)

    def test_source_anchor_requires_unique_actual_definition(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample.ws';p.write_text('function Real()\n',encoding='utf-8')
            self.assertEqual(locate(p,'Real()')['line'],1)
            with self.assertRaises(ValueError):locate(p,'Imagined()')
            p.write_text('Real()\nReal()\n',encoding='utf-8')
            with self.assertRaises(ValueError):locate(p,'Real()')

    def test_private_trace_html_escapes_metadata_and_has_local_review_links(self):
        class Parser(HTMLParser):
            def __init__(self):super().__init__();self.links=[];self.svg=0
            def handle_starttag(self,tag,attrs):
                if tag=='a':self.links.append(dict(attrs)['href'])
                if tag=='svg':self.svg+=1
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'index.html'
            rep=dict(id='<script>bad</script>',approach='contextual',duration=20,
                     exposure=[dict(start=0,end=20,reason='eligible',hazard=.1)],records=[],allocations=[],metrics={})
            write_html(p,[rep],[]);text=p.read_text(encoding='utf-8');parser=Parser();parser.feed(text)
            self.assertNotIn('<script>',text);self.assertIn('&lt;script&gt;',text)
            self.assertEqual(parser.svg,1);self.assertEqual(set(parser.links),{'results.json','traces.json','summary.csv'})

    def test_metadata_replay_never_pretends_to_verify_missing_audio(self):
        catalog={'approved_cues':[dict(id=id,composition_key=family,model_duration_seconds=20,
                                      file='build/absent-policy-test-file.wav',sha256='not-an-audio-hash')
                                  for id,family in [('S04-a','a'),('S04-b','a'),('S16-2','b')]]}
        self.assertEqual(len(demo_cues(catalog,False)),3)
        with self.assertRaises(FileNotFoundError):demo_cues(catalog,True)


if __name__=='__main__':unittest.main()
