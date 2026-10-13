"""Synthetic positive/negative source gates; no Wwise or installed inputs."""
import copy
import unittest
import xml.etree.ElementTree as E

from regional_music import plan, validate_source, expected_state, MUTED
from test_music_region_inventory import entry


def fixture():
    original = E.Element('Music')
    root = E.SubElement(original, 'MusicSwitchContainer', ID='root', Name='region', ShortID='1')
    children = E.SubElement(root, 'ChildrenList')
    world = E.SubElement(children, 'MusicSwitchContainer', ID='world', Name='world_music', ShortID='2')
    E.SubElement(children, 'MusicSwitchContainer', ID='quest', Name='quests_and_cutscenes', ShortID='3')
    sub = E.SubElement(world, 'ChildrenList')
    generic_scope = E.SubElement(sub, 'MusicSwitchContainer', ID='scope', Name='generic_scope')
    playlist = E.SubElement(E.SubElement(generic_scope, 'ChildrenList'), 'MusicPlaylistContainer', ID='generic', Name='generic', ShortID='4')
    E.SubElement(playlist, 'AudioFile').text = 'unchanged.wav'
    protected_scope = E.SubElement(sub, 'MusicSwitchContainer', ID='protected_scope', Name='authored')
    E.SubElement(E.SubElement(protected_scope, 'ChildrenList'), 'MusicPlaylistContainer', ID='protected', Name='protected', ShortID='5')
    entry(generic_scope, 'generic')
    entry(protected_scope, 'protected')
    states = {n: n + '-id' for n in sorted(MUTED) + ['combat', 'gwent'] + ['s'+str(i) for i in range(14)]}
    template = E.Element('StateInfo')
    E.SubElement(E.SubElement(template, 'StatePropertyList'), 'Property', Name='Volume')
    ref = E.SubElement(E.SubElement(template, 'StateGroupList'), 'StateGroupInfo')
    E.SubElement(ref, 'StateGroupRef', Name='game_state', ID='group')
    rows = E.SubElement(template, 'CustomStateList')
    for i, (name, ident) in enumerate(states.items()):
        row = E.SubElement(rows, 'CustomState')
        E.SubElement(row, 'StateRef', Name=name, ID=ident)
        E.SubElement(row, 'CustomState', Name='', ID='local-'+str(i), ShortID=str(1000+i))
    spec = {'schema': 1, 'wwise_build': 8928, 'purpose': 'exception-fixture', 'region': 'region',
            'game_state_group': 'group', 'muted_states': sorted(MUTED),
            'facts': {k: {'id': k, 'name': name, 'short_id': str(i+1)} for i, (k, name) in enumerate(
                [('root','region'), ('world','world_music'), ('quest','quests_and_cutscenes')])},
            'state_scopes': ['scope'], 'static_targets': ['generic'], 'decisions': {
                'generic': {'name':'generic','short_id':4,'classification':'generic','policy':'approved','evidence':'reviewed route','original_volume':0},
                'protected': {'name':'protected','short_id':5,'classification':'protected','policy':'technical-fixture-only','evidence':'isolation proof','original_volume':0}}}
    candidate = copy.deepcopy(original)
    scope = next(n for n in candidate.iter() if n.get('ID') == 'scope')
    scope.append(expected_state(template, {n: -200 if n in spec['muted_states'] else 0 for n in states}, states, 'group'))
    p = next(n for n in candidate.iter() if n.get('ID') == 'generic')
    E.SubElement(E.SubElement(p, 'PropertyList'), 'Property', Name='Volume', Type='Real64', Value='-200')
    return original, candidate, spec, states, template


class RegionalTests(unittest.TestCase):
    def test_transition_consumer_missing_review_fails(self):
        a,b,s,states,t=fixture();playlist=next(n for n in a.iter() if n.get('ID')=='generic')
        E.SubElement(E.SubElement(playlist,'ChildrenList'),'MusicSegment',ID='transition-segment')
        E.SubElement(a,'TransitionObjectRef',ID='transition-segment')
        with self.assertRaisesRegex(ValueError,'Unreviewed native transition attenuation'):plan(a,s,states)

    def test_explicit_transition_review_is_required(self):
        a,b,s,states,t=fixture();playlist=next(n for n in a.iter() if n.get('ID')=='generic')
        E.SubElement(E.SubElement(playlist,'ChildrenList'),'MusicSegment',ID='transition-segment')
        E.SubElement(a,'TransitionObjectRef',ID='transition-segment')
        s['decisions']['generic'].update(transition_attenuation_approved=True,transition_evidence='Synthetic approved generic transition only')
        plan(a,s,states)
        s['decisions']['generic']['transition_evidence']=''
        with self.assertRaisesRegex(ValueError,'Unreviewed native transition attenuation'):plan(a,s,states)

    def test_isolated_exception_and_coverage_pass(self):
        self.assertTrue(validate_source(*fixture())['passed'])

    def test_local_guid_changes_do_not_change_policy(self):
        a,b,s,states,t = fixture()
        for row in b.findall('.//StateInfo/CustomStateList/CustomState'):
            row.find('CustomState').set('ID', 'fresh-'+row.find('StateRef').get('Name'))
        self.assertTrue(validate_source(a,b,s,states,t)['passed'])

    def test_root_attenuation_leaks_into_protected_path(self):
        a,b,s,states,t = fixture();s['state_scopes']=['world']
        with self.assertRaisesRegex(ValueError,'ancestry attenuated'):
            plan(a,s,states)

    def test_unresolved_path_cannot_be_muted(self):
        a,b,s,states,t = fixture();s['decisions']['generic']['classification']='unresolved'
        with self.assertRaisesRegex(ValueError,'ancestry attenuated'):
            plan(a,s,states)

    def test_mixed_combat_static_target_rejected(self):
        a,b,s,states,t = fixture();scope=next(n for n in a.iter() if n.get('ID')=='scope');entry(scope,'generic','combat')
        with self.assertRaisesRegex(ValueError,'mixed-use'):
            plan(a,s,states)

    def test_static_consumer_outside_reviewed_scope_rejected(self):
        a,b,s,states,t = fixture();scope=next(n for n in a.iter() if n.get('ID')=='protected_scope');entry(scope,'generic')
        with self.assertRaisesRegex(ValueError,'reviewed scopes'):
            plan(a,s,states)

    def test_native_routing_change_rejected(self):
        a,b,s,states,t = fixture();next(b.iter('AudioFile')).text='different.wav'
        with self.assertRaisesRegex(ValueError,'Unexpected routing'):
            validate_source(a,b,s,states,t)

    def test_wrong_state_value_rejected(self):
        a,b,s,states,t = fixture();b.find('.//StateInfo//PropertyList/Property').set('Value','-199')
        with self.assertRaisesRegex(ValueError,'State serialization'):
            validate_source(a,b,s,states,t)

    def test_wrong_global_reference_rejected(self):
        a,b,s,states,t = fixture();b.find('.//StateInfo/CustomStateList/CustomState/StateRef').set('ID','wrong')
        with self.assertRaisesRegex(ValueError,'State serialization'):
            validate_source(a,b,s,states,t)

    def test_unexpected_static_property_rejected(self):
        a,b,s,states,t = fixture();p=next(n for n in b.iter() if n.get('ID')=='generic');E.SubElement(p.find('PropertyList'),'Property',Name='Pitch',Value='1')
        with self.assertRaisesRegex(ValueError,'Unexpected routing'):
            validate_source(a,b,s,states,t)

    def test_missing_decision_rejected(self):
        a,b,s,states,t = fixture();del s['decisions']['protected']
        with self.assertRaisesRegex(ValueError,'Undeclared'):
            plan(a,s,states)

    def test_combat_policy_mute_rejected(self):
        a,b,s,states,t = fixture();s['muted_states'].append('combat')
        with self.assertRaisesRegex(ValueError,'Combat/Gwent'):
            plan(a,s,states)

    def test_generic_coverage_gap_rejected(self):
        a,b,s,states,t = fixture();s['state_scopes']=[];s['static_targets']=[]
        with self.assertRaisesRegex(ValueError,'coverage gap'):
            plan(a,s,states)

    def test_incomplete_table_rejected(self):
        a,b,s,states,t = fixture();rows=b.find('.//StateInfo/CustomStateList');rows.remove(rows[0])
        with self.assertRaisesRegex(ValueError,'State serialization'):
            validate_source(a,b,s,states,t)

    def test_pending_generic_state_policy_rejected(self):
        a,b,s,states,t = fixture();s['static_targets']=[];s['decisions']['generic']['policy']='pending'
        with self.assertRaisesRegex(ValueError,'Pending policy'):
            plan(a,s,states)

    def test_intermediate_state_blanket_mute_rejected(self):
        a,b,s,states,t = fixture();s['muted_states'].append('s0')
        with self.assertRaisesRegex(ValueError,'nine-State'):
            plan(a,s,states)

    def test_local_identity_collision_rejected(self):
        a,b,s,states,t = fixture();rows=b.findall('.//StateInfo/CustomStateList/CustomState')
        rows[1].find('CustomState').set('ID',rows[0].find('CustomState').get('ID'))
        with self.assertRaisesRegex(ValueError,'identity collision'):
            validate_source(a,b,s,states,t)


if __name__ == '__main__':
    unittest.main()
