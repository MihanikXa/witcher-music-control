import copy
import unittest
import xml.etree.ElementTree as E
import tempfile
import wave
import struct
from pathlib import Path
from unittest.mock import Mock,patch

from sparse_reentry_author import (build,validate,SELECTED,GENERAL,WORLD,REGION,RETURN,CAMP_RETURN,REST_ITEM,MUSIC_ITEM)
from sparse_reentry_pilot import cases,observe_engine,observe_settling
from sparse_reentry_measure import verified_pcm
from sparse_reentry_review import combat_metrics,redundant_metrics,intensity_metrics,master_metrics
from sparse_reentry_pcm import compare
import numpy as np
from white_orchard_state_volume_author import semantic


def fixture():
    root=E.Element('Root')
    nodes={}
    for ident,name in [(REGION,'region'),(WORLD,'world'),(GENERAL,'general')]:
        parent=root
        if ident!=REGION:
            parent=nodes[REGION if ident==WORLD else WORLD]
            children=parent.find('ChildrenList')
            if children is None:children=E.SubElement(parent,'ChildrenList')
            parent=children
        node=E.SubElement(parent,'MusicSwitchContainer',ID=ident,Name=name);nodes[ident]=node
        ref=E.SubElement(E.SubElement(node,'ReferenceList'),'Reference',Name='TransitionRoot')
        tr=E.SubElement(E.SubElement(ref,'Custom'),'MusicTransition',ID=ident+'root')
        children=E.SubElement(tr,'ChildrenList')
        rule=E.SubElement(children,'MusicTransition',ID=ident+'default')
        E.SubElement(rule,'PropertyList');E.SubElement(rule,'TransitionInfo')
        if ident==GENERAL:
            rule=E.SubElement(children,'MusicTransition',ID=RETURN)
            props=E.SubElement(rule,'PropertyList')
            E.SubElement(props,'Property',Name='DestinationJumpPositionPreset',Type='int16',Value='1')
            E.SubElement(props,'Property',Name='UseTransitionObject',Type='bool',Value='True')
            E.SubElement(rule,'TransitionInfo')
        if ident==REGION:
            rule=E.SubElement(children,'MusicTransition',ID=CAMP_RETURN)
            E.SubElement(rule,'PropertyList');refs=E.SubElement(rule,'ReferenceList')
            for key,target in [('SourceContextObject',WORLD),('DestinationContextObject',GENERAL)]:
                E.SubElement(E.SubElement(refs,'Reference',Name=key),'ObjectRef',ID=target)
            E.SubElement(rule,'TransitionInfo')
    children=E.SubElement(nodes[GENERAL],'ChildrenList')
    selected=E.SubElement(children,'MusicPlaylistContainer',ID=SELECTED,Name='selected')
    ref=E.SubElement(E.SubElement(selected,'ReferenceList'),'Reference',Name='PlaylistRoot')
    seq=E.SubElement(E.SubElement(ref,'Custom'),'MusicPlaylistItem',ID='playlist')
    children=E.SubElement(seq,'ChildrenList')
    E.SubElement(children,'MusicPlaylistItem',ID=MUSIC_ITEM)
    E.SubElement(children,'MusicPlaylistItem',ID=REST_ITEM)
    return root


class ReentryTests(unittest.TestCase):
    def test_history_allowlist_and_mutations(self):
        before=fixture();after,ids=build(before,'history-rest',['new-general','new-region'])
        self.assertTrue(validate(before,after,'history-rest',ids)['passed'])
        for name,value in [('Tempo','120'),('Volume','-200'),('ExitSourceAt','0')]:
            bad=copy.deepcopy(after)
            n=next(n for n in bad.iter() if n.get('ID')==RETURN)
            E.SubElement(n.find('PropertyList'),'Property',Name=name,Type='Real64',Value=value)
            with self.assertRaises(ValueError):validate(before,bad,'history-rest',ids)
        bad=copy.deepcopy(after)
        next(n for n in bad.iter('JumpToPlaylistItemRef')).set('ID',MUSIC_ITEM)
        with self.assertRaises(ValueError):validate(before,bad,'history-rest',ids)
        bad=copy.deepcopy(after)
        next(n for n in bad.iter() if n.get('ID')=='new-general').set('ID','collision')
        with self.assertRaises(ValueError):validate(before,bad,'history-rest',ids)
        # A source/template defect can reconstruct exactly yet be rejected by
        # Wwise: context must not refer to the owning switch itself.
        invalid=fixture()
        template=next(n for n in invalid.iter() if n.get('ID')==CAMP_RETURN)
        template.find('./ReferenceList/Reference[@Name="SourceContextObject"]/ObjectRef').set('ID',REGION)
        invalid_after,invalid_ids=build(invalid,'history-rest',['new-general','new-region'])
        with self.assertRaises(ValueError):validate(invalid,invalid_after,'history-rest',invalid_ids)

    def test_rest_first_only_reorders(self):
        before=fixture();after,ids=build(before,'rest-first')
        self.assertEqual(ids,[]);self.assertTrue(validate(before,after,'rest-first',ids)['passed'])
        bad=copy.deepcopy(after);item=next(n for n in bad.iter() if n.get('ID')==REST_ITEM)
        E.SubElement(item,'PropertyList').append(E.Element('Property',Name='LoopCount',Value='0'))
        with self.assertRaises(ValueError):validate(before,bad,'rest-first',ids)
        with self.assertRaises(ValueError):validate(before,before,'rest-first',ids)

    def test_phase_plan_and_finite_capture(self):
        for mode in (None,'history-rest','rest-first'):
            plan=cases(mode);self.assertEqual(len({c['name'] for c in plan}),len(plan))
            for c in plan:
                self.assertEqual(c['actions'],sorted(c['actions'],key=lambda a:a[0]))
                self.assertTrue(all(0<t<c['duration'] for t,*_ in c['actions']))
            by={c['name']:c for c in plan}
            self.assertLess(by['combat-early']['actions'][0][0],by['combat-late']['actions'][0][0])
        self.assertEqual(cases('rest-first')[0]['actions'][0][0],6)

    def test_unknown_or_unused_identity_pins_fail(self):
        with self.assertRaises(ValueError):build(fixture(),'global-mute')
        with self.assertRaises(ValueError):build(fixture(),'rest-first',['unused'])

    def test_pcm_requires_finalized_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test.wav'
            with wave.open(str(path),'wb') as w:
                w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(bytes(4800*4))
            original=path.read_bytes();x,metadata=verified_pcm(path)
            self.assertEqual(x.shape,(4800,2));self.assertEqual(metadata['seconds'],.1)
            path.write_bytes(original[:4]+bytes([255])*4+original[8:])
            with self.assertRaises(ValueError):verified_pcm(path)
            path.write_bytes(original[:-1])
            with self.assertRaises(ValueError):verified_pcm(path)
            # Actual installed Recorder's bounded 5.1 PCM16 extensible layout.
            fmt=struct.pack('<HHIIHHHHI',65534,6,48000,576000,12,16,22,0,1551)
            fmt+=bytes.fromhex('0100000000001000800000aa00389b71')
            data=bytes(4800*12)
            def container(f):
                body=b'WAVEfmt '+struct.pack('<I',len(f))+f+b'data'+struct.pack('<I',len(data))+data
                return b'RIFF'+struct.pack('<I',len(body))+body
            path.write_bytes(container(fmt));x,metadata=verified_pcm(path)
            self.assertEqual(x.shape,(4800,6));self.assertEqual(metadata['format']['valid_bits'],0)
            for bad in (fmt[:18]+struct.pack('<H',8)+fmt[20:],fmt[:24]+bytes.fromhex('03000000')+fmt[28:]):
                path.write_bytes(container(bad))
                with self.assertRaises(ValueError):verified_pcm(path)

    def test_observer_uses_pinned_getter_guids(self):
        api=Mock();api.call.side_effect=[{'return':{'name':x}} for x in ('exploration','village','world_music')]
        with patch('sparse_reentry_pilot.time.sleep'):r=observe_engine(api)
        self.assertEqual(r['location']['return']['name'],'village')
        self.assertEqual(api.call.call_count,3)
        for call in api.call.call_args_list:
            args=call.args[1]
            self.assertTrue(args.get('stateGroup',args.get('switchGroup')).startswith('{'))

    def test_settling_observer_preserves_stale_initial_read(self):
        api=Mock()
        api.call.side_effect=[{'return':{'name':x}} for x in ('exploration','village','world_music')+('combat',)*5]
        with patch('sparse_reentry_pilot.time.sleep'):r=observe_settling(api)
        self.assertEqual(r['game_state']['return']['name'],'exploration')
        self.assertEqual([x['state'] for x in r['state_settling']],['exploration']+['combat']*5)
        self.assertTrue(all('get' in call.args[0] for call in api.call.call_args_list))

    def test_outro_and_finite_guard_are_independent_requirements(self):
        def voice(role,times,db):return dict(role=role,envelope=[[t,db,True,False] for t in times])
        row=dict(events=[dict(kind='state',name='combat',accepted=6),dict(kind='state',name='exploration',accepted=30)],
                 rtpcs={'18446744073709551614:threat_rating':[0,35,100]},
                 pipelines=[voice('combat',[7,8,9],-17),voice('outro',[31+i*.25 for i in range(21)],-19),voice('cue',[65,66],-19)])
        good=combat_metrics(row)
        self.assertTrue(good['complete_native_outro'] and good['bounded_quiet_return'] and good['tested_30s_guard'])
        bad=copy.deepcopy(row);bad['pipelines'][1]['envelope']=[p for p in bad['pipelines'][1]['envelope'] if p[0]<=33]
        self.assertFalse(combat_metrics(bad)['complete_native_outro'])
        bad=copy.deepcopy(row)
        for p in bad['pipelines'][1]['envelope']:p[1]=-219
        self.assertFalse(combat_metrics(bad)['complete_native_outro'])
        bad=copy.deepcopy(row);bad['pipelines'][-1]=voice('cue',[32,33],-19)
        self.assertFalse(combat_metrics(bad)['bounded_quiet_return'])
        bad=copy.deepcopy(row);bad['pipelines'].pop()
        self.assertFalse(combat_metrics(bad)['bounded_quiet_return'])
        bad=copy.deepcopy(row);bad['rtpcs']={'0:threat_rating':[0,35,100]}
        self.assertFalse(combat_metrics(bad)['threat_0_35_100'])

    def test_redundant_restarts_are_not_continuation(self):
        row=dict(events=[dict(name='repeat',accepted=t) for t in (6,44,57)],pipelines=[
            dict(role='cue',pipeline=1,first=2,last=42.85),dict(role='cue',pipeline=2,first=62.85,last=103.7)])
        self.assertTrue(redundant_metrics(row)['normal_cadence_preserved'])
        extra=copy.deepcopy(row);extra['pipelines'].append(dict(role='cue',pipeline=3,first=105,last=140))
        self.assertFalse(redundant_metrics(extra)['normal_cadence_preserved'])
        with self.assertRaises(ValueError):redundant_metrics(row,5)
        row['pipelines'][1]['first']=45
        self.assertFalse(redundant_metrics(row)['normal_cadence_preserved'])

    def test_intensity_and_master_require_real_control_windows(self):
        events=[dict(kind='state',name='combat',accepted=6),dict(kind='rtpc',name='threat_rating',value=35,accepted=12),
                dict(kind='rtpc',name='threat_rating',value=100,accepted=18),dict(kind='state',name='exploration',accepted=30)]
        env1=[[t,-17,True,False] for t in (10,14,20)]
        env2=[[10,-219,True,False],[14,-19,True,False],[20,-19,True,False]]
        row=dict(events=events,rtpcs={'18446744073709551614:threat_rating':[0,35,100]},pipelines=[
            dict(path=['layer1'],envelope=env1),dict(path=['layer2'],envelope=env2)])
        self.assertTrue(intensity_metrics(row)['passed'])
        bad=copy.deepcopy(row);bad['pipelines'][1]['envelope'][-1][1]=-219
        self.assertFalse(intensity_metrics(bad)['passed'])
        row=dict(events=[dict(kind='rtpc',name='menu_volume_music',value=50,accepted=8),
                         dict(kind='rtpc',name='menu_volume_music',value=100,accepted=16)],pipelines=[
                         dict(role='cue',envelope=[[11,-25.0206,True,False],[19,-19,True,False]])])
        self.assertTrue(master_metrics(row)['passed'])
        row['pipelines'][0]['envelope'][1][1]=-25.0206
        self.assertFalse(master_metrics(row)['passed'])

    def test_waveform_gate_detects_truncation_and_wrong_samples(self):
        expected=np.arange(40,dtype=float).reshape(-1,2)
        self.assertEqual(compare(expected,expected)['maximum_error_pcm16'],0)
        self.assertGreater(compare(expected+5,expected)['maximum_error_pcm16'],2)
        with self.assertRaises(ValueError):compare(expected[:-1],expected)


if __name__=='__main__':unittest.main()
