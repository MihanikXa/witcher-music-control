import struct
import unittest
import xml.etree.ElementTree as ET
import copy

from regional_music_bank import Reader, decode, validate_record, record_gate


def node(volume=None, state=b'\0\0', parent=123, effects=0, aux=False):
    # Synthetic v150 music prefix, independent of licensed/game bytes.
    fx = b'\0' + bytes([effects]) + (b'\0' + bytes(6*effects) if effects else b'')
    props = b'\0' if volume is None else b'\1\0'+struct.pack('<f', volume)
    return b'\0'+fx+b'\0\0'+struct.pack('<II',0,parent)+b'\0'+props+b'\0\0'+bytes([8 if aux else 0])+(bytes(16) if aux else b'')+bytes(4)+bytes(6)+state+b'\0\0TAIL'


def state(ids=(1,2), value=-200, group=7, sync=0, prop=0):
    return bytes([1,prop,2,1,1])+struct.pack('<IBB',group,sync,len(ids))+b''.join(struct.pack('<IHHf',i,1,0,value) for i in ids)


class DecoderTests(unittest.TestCase):
    def test_dynamic_offsets(self):
        self.assertEqual(decode(12,node())['state']['start'],28)
        self.assertEqual(decode(13,node(-2))['state']['start'],33)
        self.assertEqual(decode(12,node(effects=1,aux=True))['state']['start'],51)

    def test_state_positive_and_tail(self):
        result=validate_record((12,node()),(12,node(state=state())),'state',123,7,{1,2})
        self.assertTrue(result['immutable_remainder_exact'])

    def test_volume_insertion(self):
        validate_record((13,node()),(13,node(-200)),'static',123)

    def test_volume_replacement(self):
        validate_record((13,node(-2)),(13,node(-200)),'static',123,original_volume=-2)

    def test_every_truncated_prefix_fails(self):
        original=node()
        for size in range(32):
            with self.subTest(size=size),self.assertRaises(ValueError):decode(12,original[:size])

    def test_bad_type_and_version(self):
        for kind,version in [(11,150),(12,149)]:
            with self.assertRaises(ValueError):decode(kind,node(),version)

    def test_spatial_unsupported(self):
        body=bytearray(node());body[16]=3
        with self.assertRaises(ValueError):decode(12,body)

    def test_invalid_varints(self):
        for raw in [b'\x80\0',b'\xff'*5,b'\x90\x80\x80\x80\0',b'\x81']:
            with self.subTest(raw=raw),self.assertRaises(ValueError):Reader(raw).var()

    def test_impossible_state_count(self):
        with self.assertRaises(ValueError):decode(12,node(state=b'\xff\x7f'))

    def test_duplicate_states(self):
        with self.assertRaises(ValueError):decode(12,node(state=state(ids=(1,1))))

    def test_nonfinite_state(self):
        for value in [float('nan'),float('inf')]:
            with self.assertRaises(ValueError):decode(12,node(state=state(value=value)))

    def test_wrong_group_sync_value_ids(self):
        for data in [state(group=8),state(sync=1),state(value=-199),state(ids=(1,3)),state(prop=1)]:
            with self.assertRaises(ValueError):validate_record((12,node()),(12,node(state=data)),'state',123,7,{1,2})

    def test_parent_and_tail_changes(self):
        for data in [node(state=state(),parent=124),node(state=state())[:-1]+b'X']:
            with self.assertRaises(ValueError):validate_record((12,node()),(12,data),'state',123,7,{1,2})

    def test_static_unapproved_state_change(self):
        with self.assertRaises(ValueError):validate_record((13,node()),(13,node(-200,state=state())),'static',123)

    def test_static_wrong_original(self):
        with self.assertRaises(ValueError):validate_record((13,node(-2)),(13,node(-200)),'static',123)

    def test_existing_state_not_overwritten(self):
        with self.assertRaises(ValueError):validate_record((12,node(state=state())),(12,node(state=state())),'state',123,7,{1,2})


class RecordGateTests(unittest.TestCase):
    def setUp(self):
        self.music=ET.fromstring('<MusicSwitchContainer ID="parent" ShortID="123"><ChildrenList><MusicSwitchContainer ID="scope" ShortID="124"/><MusicPlaylistContainer ID="static" ShortID="125"/></ChildrenList></MusicSwitchContainer>')
        self.globals=ET.fromstring('<StateGroup ID="group" Name="game_state"/>')
        self.sync={'group':7};self.meta=ET.Element('Info');g=ET.SubElement(self.meta,'StateGroup',Id='7',Name='game_state');rows=ET.SubElement(g,'States')
        for i in range(25):
            ET.SubElement(self.globals,'State',ID=str(i),Name='s'+str(i));self.sync[str(i)]=i+1
            ET.SubElement(rows,'State',Id=str(i+1),Name='s'+str(i))
        self.spec={'game_state_group':'group','state_scopes':['scope'],'static_targets':['static'],'muted_states':['s0','s1'],'decisions':{'static':{'original_volume':-2}}}
        self.before={'records':{124:(12,node()),125:(13,node(-2))}}
        self.after={'records':{124:(12,node(state=state())),125:(13,node(-200))}}

    def gate(self):
        return record_gate(self.before,self.after,self.spec,self.music,self.globals,self.meta,{7},self.sync)

    def test_complete_field_allowlist(self):self.assertEqual(len(self.gate()),2)

    def test_repeated_metadata_requires_consistency(self):
        self.meta.append(copy.deepcopy(self.meta[0]));self.assertEqual(len(self.gate()),2)
        self.meta[1].find('./States/State').set('Name','wrong')
        with self.assertRaises(ValueError):self.gate()

    def test_non_target_combat_cannot_change(self):
        self.before['records'][126]=(13,node());self.after['records'][126]=(13,node(-200))
        with self.assertRaises(ValueError):self.gate()

    def test_no_additions(self):
        self.after['records'][126]=(13,node())
        with self.assertRaises(ValueError):self.gate()

    def test_missing_edit(self):
        self.after['records'][125]=self.before['records'][125]
        with self.assertRaises(ValueError):self.gate()

    def test_wrong_global_reference(self):
        self.sync['0']=999
        with self.assertRaises(ValueError):self.gate()

    def test_incomplete_global_table(self):
        self.globals.remove(self.globals[0])
        with self.assertRaises(ValueError):self.gate()


if __name__=='__main__':unittest.main()
