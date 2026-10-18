import copy
import struct
import tempfile
from pathlib import Path
import unittest

from sparse_approved_bank import (SEGMENT, TRACK, MEDIA, SELECTED, embedded,
                                  new_records_gate, selected_gate, state_bytes, header_gate)
from test_music_comparison_decode import common, item


def fresh_records():
    # Independent explicit synthetic v150 default NodeBase, with max-voices=1.
    def base(parent):
        return (b'\0\0\0\0' + struct.pack('<II', 0, parent) + bytes(9)
                + b'\0\1\0\0\0\0' + b'\0\0\0\0')
    segment = (b'\0' + base(SELECTED) + struct.pack('<II', 1, TRACK)
               + struct.pack('<ddfBBBI', 16000, 0, 60, 4, 4, 1, 0)
               + struct.pack('<dIId', 40850, 2, 11, 0) + b'\0'
               + struct.pack('<Id', 12, 30850) + b'\0')
    tr = (b'\0' + struct.pack('<IIBIIB', 1, 262145, 0, MEDIA, 99, 0)
          + struct.pack('<IIIIddddII', 1, 0, MEDIA, 0, 0, 0, 0, 40850, 1, 0)
          + base(SEGMENT) + struct.pack('<Bi', 0, 0))
    return {SEGMENT:(10, segment), TRACK:(11, tr)}


class SparseBankTests(unittest.TestCase):
    def test_exact_new_nodes_and_every_byte_mutation(self):
        records = fresh_records()
        self.assertEqual(new_records_gate(records, [11,12], 99)['segment']['duration_ms'], 40850)
        for ident in records:
            for pos in range(len(records[ident][1])):
                altered = copy.deepcopy(records)
                body = bytearray(altered[ident][1]); body[pos] ^= 1
                altered[ident] = (altered[ident][0], bytes(body))
                with self.subTest(ident=ident, pos=pos), self.assertRaises(ValueError):
                    new_records_gate(altered, [11,12], 99)
        for ids, size in [([11,13],99),([11,12],98)]:
            with self.assertRaises(ValueError): new_records_gate(records, ids, size)

    def test_selected_exact_and_mutations(self):
        # Minimal native-shaped playlist, two physical children and three items.
        c = common()
        # common() has child-count=0 at byte32; retain its native meter/stingers.
        prefix = c[:32] + struct.pack('<III', 2,4111369,319905093) + c[36:]
        root = item(children=2)
        old = prefix + struct.pack('<II',0,3) + root + item(319905093) + item(319905093)
        # Native 3-item fixture is enough to exercise the declared sequence rewrite.
        from music_comparison_decode import music
        from sparse_approved_bank import item_bytes
        a = music(13,old); sa=a['state']; start=a['playlist'][0]['offset']-4
        entries=copy.deepcopy(a['playlist']); entries[0]['loop']=0
        entries[1]['segment']=SEGMENT; entries[2].update(segment=4111369,loop=3)
        new = (old[:sa['start']] + state_bytes(7,{1,2}) + old[sa['end']:sa['end']+2]
               + struct.pack('<4I',3,4111369,319905093,SEGMENT)
               + old[sa['end']+2+12:start] + struct.pack('<I',3)
               + b''.join(item_bytes(i) for i in entries))
        self.assertTrue(selected_gate((13,old),(13,new),7,{1,2})['immutable_remainder_exact'])
        for pos in range(len(new)):
            altered=bytearray(new);altered[pos]^=1
            with self.subTest(pos=pos),self.assertRaises((ValueError,UnicodeDecodeError)):
                selected_gate((13,old),(13,bytes(altered)),7,{1,2})
        with self.assertRaises(ValueError): selected_gate((13,old),(13,new),8,{1,2})
        with self.assertRaises(ValueError): selected_gate((13,old),(13,new),7,{1})

    def test_media_bounds_duplicates_overlap(self):
        def bank(idx,data=b'abcde'): return {'payload':{'DIDX':idx,'DATA':data}}
        valid=struct.pack('<III',1,0,3)+struct.pack('<III',2,3,2)
        self.assertEqual(embedded(bank(valid)),{1:b'abc',2:b'de'})
        for idx in [valid[:-1],valid+struct.pack('<III',1,0,1),
                    struct.pack('<III',1,4,2),struct.pack('<III',1,0,0),
                    struct.pack('<III',1,0,3)+struct.pack('<III',2,2,3)]:
            with self.assertRaises(ValueError):embedded(bank(idx))

    def test_bkhd_padding_is_derived_not_waived(self):
        import uuid
        ident=uuid.UUID('{D32207D0-DBC4-6014-DD35-26D0E6FBF4BE}')
        def bank(count,pad,project=17637):
            return {'payload':{'BKHD':struct.pack('<6I',150,3228744150,393239870,16,project,0)+ident.bytes_le+pad,
                               'DIDX':bytes(12*count),'DATA':b''}}
        a,b=bank(7,bytes(12)),bank(8,b'')
        with tempfile.TemporaryDirectory() as tmp:
            xml=Path(tmp)/'info.xml'
            xml.write_text('<Root><SoundBank Id="3228744150" Hash="'+str(ident)+'"/></Root>')
            self.assertEqual(header_gate(a,b,xml)['project_id'],17637)
            for bad in [bank(8,bytes(12)),bank(8,b'X'),bank(8,b'',39)]:
                with self.assertRaises(ValueError):header_gate(a,bad,xml)


if __name__=='__main__':unittest.main()
