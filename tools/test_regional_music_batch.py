"""Independent batch restoration rejects hidden cross-region changes."""
import copy
import unittest
import xml.etree.ElementTree as E
from test_regional_music import fixture
from regional_music_batch import batch_semantics, set_static_volume


def batch_fixture():
    original,_,spec,states,_=fixture()
    spec['state_scopes']=[]
    scope=original.find(".//MusicSwitchContainer[@ID='scope']")
    scope.set('ShortID','8')
    spec['static_consumer_paths']={'generic':[{'selector_id':'scope','selector_short_id':8,'states':['exploration']}]}
    # Clone an entirely separate region, including declarations and references.
    other=copy.deepcopy(original.find("MusicSwitchContainer[@ID='root']"))
    for n in other.iter():
        if n.get('ID'):n.set('ID',n.get('ID')+'-2')
        if n.get('ShortID'):n.set('ShortID',str(int(n.get('ShortID'))+100))
    original.append(other)
    second=copy.deepcopy(spec);second['region']='region-2'
    for k in ('root','world','quest'):
        second['facts'][k]['id']+='-2';second['facts'][k]['short_id']=str(int(second['facts'][k]['short_id'])+100)
    second['static_targets']=['generic-2']
    second['static_consumer_paths']={'generic-2':[{'selector_id':'scope-2','selector_short_id':108,'states':['exploration']}]}
    second['decisions']={k+'-2':dict(v,short_id=int(v['short_id'])+100) for k,v in second['decisions'].items()}
    candidate=copy.deepcopy(original)
    for ident in ('generic','generic-2'):
        node=candidate.find(".//MusicPlaylistContainer[@ID='%s']"%ident)
        E.SubElement(E.SubElement(node,'PropertyList'),'Property',Name='Volume',Type='Real64',Value='-200')
    return original,candidate,[spec,second],states


class BatchTests(unittest.TestCase):
    def test_new_property_list_precedes_references_and_children(self):
        node=E.fromstring('<MusicPlaylistContainer><ReferenceList/><ChildrenList/><PositioningInfo/></MusicPlaylistContainer>')
        set_static_volume(node)
        self.assertEqual([c.tag for c in node],['PropertyList','ReferenceList','ChildrenList','PositioningInfo'])
        set_static_volume(node)
        self.assertEqual(len(node.findall('PropertyList')),1)

    def test_native_value_list_is_updated_without_duplicate_attribute(self):
        node=E.fromstring('<MusicPlaylistContainer><PropertyList><Property Name="Volume" Type="Real64"><ValueList><Value>-4</Value></ValueList></Property></PropertyList></MusicPlaylistContainer>')
        set_static_volume(node)
        prop=node.find('./PropertyList/Property')
        self.assertNotIn('Value',prop.attrib)
        self.assertEqual(prop.findtext('./ValueList/Value'),'-200')

    def test_duplicate_volume_forms_rejected(self):
        a,b,s,st=batch_fixture()
        p=b.find('.//Property');E.SubElement(E.SubElement(p,'ValueList'),'Value').text='-200'
        with self.assertRaisesRegex(ValueError,'Volume property'):batch_semantics(a,b,s,st)

    def test_two_regions_restore_exactly(self):
        a,b,s,st=batch_fixture()
        self.assertEqual(batch_semantics(a,b,s,st)['static_targets'],2)

    def test_unrelated_change_fails(self):
        a,b,s,st=batch_fixture();b.find('.//AudioFile').text='changed.wav'
        with self.assertRaisesRegex(ValueError,'Unexpected routing'):batch_semantics(a,b,s,st)

    def test_missing_second_edit_fails(self):
        a,b,s,st=batch_fixture();b.find(".//MusicPlaylistContainer[@ID='generic-2']/PropertyList/Property").set('Value','0')
        with self.assertRaisesRegex(ValueError,'Volume property'):batch_semantics(a,b,s,st)

    def test_extra_volume_field_fails(self):
        a,b,s,st=batch_fixture();b.find('.//Property').set('Unexpected','1')
        with self.assertRaisesRegex(ValueError,'Volume property'):batch_semantics(a,b,s,st)

    def test_overlapping_region_and_contextual_scope_fail(self):
        a,b,s,st=batch_fixture()
        with self.assertRaisesRegex(ValueError,'duplicate'):batch_semantics(a,b,[s[0],s[0]],st)
        s[0]['state_scopes']=['scope']
        with self.assertRaisesRegex(ValueError,'static-only'):batch_semantics(a,b,s,st)

    def test_authored_alias_is_explicitly_pinned(self):
        a,b,s,st=batch_fixture()
        a.find(".//MusicSwitchContainer[@ID='quest']").set('Name','quests_cutscenes')
        b.find(".//MusicSwitchContainer[@ID='quest']").set('Name','quests_cutscenes')
        s[0]['facts']['quest']['name']='quests_cutscenes'
        self.assertTrue(batch_semantics(a,b,s,st)['passed'])
        s[0]['facts']['quest']['name']='quests_and_cutscenes'
        with self.assertRaisesRegex(ValueError,'Identity mismatch'):batch_semantics(a,b,s,st)
