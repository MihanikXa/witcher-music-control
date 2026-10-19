import unittest
from pathlib import Path
from sparse_observer_trace import normalize,replay,state
from sparse_context_policy import PROFILES
from sparse_request_probe import request_spec,validate_actions,SELECTED,GENERAL
from sparse_observer_build import assertion_control_source, diagnostics

BEGIN='WMCCTX1|epoch=1|seq=1|t=0|begin|origin=load_or_spawn\n'
ROW='snapshot|origin=timer|available=1|region=1|location=unknown|state=1|combat=0|threat=0|night=0|activity=foot|scene=0|paused=0|loading_video=0|interior=0|owner=unknown|outro=unknown|selector=unknown'


def line(payload=ROW,ep=1,seq=2,t=1):return f'WMCCTX1|epoch={ep}|seq={seq}|t={t}|{payload}\n'


class ObserverTests(unittest.TestCase):
    def test_snapshot_unknowns_and_replay(self):
        t=normalize(BEGIN+line()+line(seq=3,t=500))
        c=t['events'][1]['values']
        self.assertEqual(c['game_state'],'exploration')
        for k in ('outro_clear','loading','location','selector','weather'):self.assertIsNone(c[k])
        self.assertEqual(c['native_owner'],'unknown')
        m=replay(t,[dict(id='fixture',family='one',seconds=20,role='punctuation')],PROFILES['contrast'])
        self.assertFalse(m.intervals);self.assertIsNone(m.active)

    def test_enum_map(self):
        self.assertEqual(state('ESGS_Combat'),state('6'))
        self.assertEqual(state('ESGS_Dialog'),'dialog_scene')
        for s in ('-1','21','ESGS_Nonexistent','exploration'):
            with self.assertRaises(ValueError):state(s)

    def test_lifecycle_not_wall_clock(self):
        t=normalize(BEGIN+line(t=100)+line('begin|origin=load_or_spawn',ep=2,seq=1,t=0)+line(ep=2,seq=2,t=1))
        self.assertEqual([e.get('generation') for e in t['events'] if e['kind']=='context'],[1,2])
        self.assertAlmostEqual(t['duration'],101.001)
        self.assertIn('unknown',t['timestamp_semantics'])

    def test_only_first_local_discovery(self):
        payload='discovery|origin=player_first_trigger|local=1|first=1|id=1'
        t=normalize(BEGIN+line(payload))
        self.assertEqual(t['events'][-1]['type'],'first_discovery')
        for bad in (payload.replace('first=1','first=0'),payload.replace('local=1','local=0'),
                    payload.replace('player_first_trigger','map_pin_changed'),payload.replace('id=1','id=33')):
            with self.assertRaises(ValueError):normalize(BEGIN+line(bad))
        with self.assertRaises(ValueError):normalize(BEGIN+line(payload)+line(payload,seq=3,t=2))

    def test_missing_objects_clear_observations(self):
        t=normalize(BEGIN+line()+line('snapshot|origin=timer|available=0',seq=3,t=2))
        self.assertIsNone(t['events'][-1]['values']['region'])
        self.assertIsNone(t['events'][-1]['values']['threatened'])

    def test_reject_malformed_reverse_and_forged_owner(self):
        for text in ('not a diagnostic',line(),BEGIN+line(t=float('nan')),BEGIN+line()+line(),
                     BEGIN+line().replace('owner=unknown','owner=generic'),BEGIN+line().replace('paused=0','paused=maybe'),
                     BEGIN+line()+line(seq=3,t=.5),BEGIN+line().replace('|region=1','|region=1|region=2')):
            with self.assertRaises((ValueError,KeyError)):normalize(text)

    def test_native_enum_priority_and_daynight(self):
        for raw,want in [('6','combat'),('8','dialog_scene'),('13','movie'),('19','gwent')]:
            values=normalize(BEGIN+line(ROW.replace('state=1','state='+raw).replace('night=0','night=1')))['events'][-1]['values']
            self.assertEqual(values['game_state'],want);self.assertEqual(values['daypart'],'night')

    def test_row_bound(self):
        with self.assertRaises(ValueError):normalize(BEGIN+''.join(line(seq=i,t=i) for i in range(2,602)))
        self.assertEqual(len(normalize(BEGIN+''.join(line(seq=i,t=i) for i in range(2,601)))['observations']),600)

    def test_original_source_is_diagnostic_only(self):
        s=(Path(__file__).resolve().parents[1]/'src/diagnostics/wmcContextObserver.ws').read_text(encoding='utf-8')
        for forbidden in ('SoundMusicEvent(', 'SoundEvent(', 'SetState(', 'SetSwitch(', 'saved var', '@replaceMethod'):
            self.assertNotIn(forbidden,s)
        self.assertEqual(s.count('wrappedMethod('),3)
        self.assertIn('manager.IsEntityMapPinDiscovered(entityName)',s)
        self.assertIn('activator.GetEntity() == thePlayer',s)
        self.assertIn('AddTimer(\'WMCContextSample\', 1.0, true)',s)

    def test_request_is_seek_never_play(self):
        for target in (SELECTED,GENERAL):
            d=request_spec(target)
            self.assertEqual(len(d['children']),1)
            self.assertEqual(d['children'][0]['@ActionType'],36)
            self.assertEqual(d['children'][0]['@Target'],target)

    def test_matched_compile_control_preserves_hooks(self):
        text=assertion_control_source()
        self.assertEqual(text.count('@wrapMethod('),3)
        self.assertEqual(text.count('wrappedMethod('),3)
        self.assertIn('ShouldEnableCombatMusic()',text)
        self.assertIn('declaration-control',text)
        self.assertNotIn('"WMCCTX1|epoch="',text)

    def test_loaded_action_allowlist_rejects_bypass(self):
        a=dict(request_spec()['children'][0]);a['@Target']={'id':SELECTED}
        validate_actions([a],SELECTED)
        for key,value in [('type','Event'),('@ActionType',3),('@Target',{'id':GENERAL}),
                          ('@SeekType',0),('@SeekPercent',0),('@SeekToMarker',True)]:
            bad=dict(a);bad[key]=value
            with self.assertRaises(ValueError):validate_actions([bad],SELECTED)
        for bad in ([],[a,a]):
            with self.assertRaises(ValueError):validate_actions(bad,SELECTED)

    def test_diagnostics_do_not_hide_assertions(self):
        d=diagnostics('[date][Error][Assert] native metadata\n[date][Warning][WCC] notice\n[date][Info] done')
        self.assertEqual(sum(d.values()),2)
        self.assertEqual(d['[Error][Assert] native metadata'],1)


if __name__=='__main__':unittest.main()
