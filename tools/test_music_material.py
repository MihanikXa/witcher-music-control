"""Synthetic safety/format/UI tests; no reference binaries or audio required."""
import copy
from html.parser import HTMLParser
import struct
import unittest

from music_material_opus import chunks,inspect,rewrap,packet_samples,crc,verify_rewrap
from music_material_audition import page,choose


def riff(channels=2,mapping=0,samples=1608):
    # Two 20ms CELT packets; 312 encoder-delay samples, no end trim.
    fmt=bytearray(36)
    struct.pack_into('<HHI',fmt,0,0x3041,channels,48000)
    struct.pack_into('<IIHBB',fmt,24,samples,2,312,1,mapping)
    def chunk(tag,b):return tag+struct.pack('<I',len(b))+b+(b'\0' if len(b)&1 else b'')
    data=b'WAVE'+chunk(b'fmt ',fmt)+chunk(b'seek',struct.pack('<HH',3,3))+chunk(b'data',b'\xf8\xff\xfe'*2)
    return b'RIFF'+struct.pack('<I',len(data))+data


def pages(blob):
    out=[];offset=0
    while offset<len(blob):
        header=blob[offset:offset+27];n=header[26]
        sizes=blob[offset+27:offset+27+n];end=offset+27+n+sum(sizes)
        page=bytearray(blob[offset:end]);expected=struct.unpack_from('<I',page,22)[0]
        struct.pack_into('<I',page,22,0)
        if crc(page)!=expected:raise ValueError('Invalid page checksum')
        out.append((header,blob[offset+27+n:end]));offset=end
    if offset!=len(blob):raise ValueError('Invalid page bounds')
    return out


class MaterialTests(unittest.TestCase):
    def test_opus_packet_preservation_granules_crc(self):
        data=riff();wrapped,info=rewrap(data);p=pages(wrapped)
        self.assertEqual([x[1] for x in p[2:]],[b'\xf8\xff\xfe']*2)
        self.assertEqual(info['samples'],1608)
        self.assertEqual(struct.unpack_from('<H',p[0][1],10)[0],312)
        self.assertEqual(struct.unpack_from('<Q',p[-1][0],6)[0],1920)
        self.assertEqual(p[-1][0][5],4)
        self.assertEqual(packet_samples(b'\xf8\xff\xfe'),960)
        self.assertTrue(verify_rewrap(data,wrapped)['passed'])
        broken=bytearray(wrapped);broken[-1]^=1
        with self.assertRaises(ValueError):verify_rewrap(data,broken)

    def test_rejects_unknown_truncated_mismatched_streams(self):
        for data in (riff(channels=6),riff(mapping=1),riff(samples=4000),riff()[:-1]):
            with self.subTest(data=data[:36]),self.assertRaises(ValueError):inspect(data)
        data=bytearray(riff());struct.pack_into('<H',data,64,100)
        with self.assertRaises(ValueError):inspect(data)
        with self.assertRaises(ValueError):packet_samples(b'\xfb\x00')

    def test_final_odd_data_without_padding(self):
        data=riff();c=chunks(data);payload=c[b'data'][:-1]
        # Container traversal accepts the observed Wwise final-chunk convention;
        # the separate packet-size gate still rejects this corrupted Opus body.
        offset=data.index(b'data');out=bytearray(data[:offset]+b'data'+struct.pack('<I',len(payload))+payload)
        struct.pack_into('<I',out,4,len(out)-8)
        self.assertEqual(chunks(out)[b'data'],payload)
        with self.assertRaises(ValueError):inspect(out)

    def test_native_mapping_fails_closed(self):
        t=dict(id=1,reviewed_generic=True,sources=[dict(id=2,originals=[dict(file='one.wav')])],
               rtpc=[],clips=[],ancestry=[])
        c=dict(native=dict(segments=[dict(segment=3,tracks=[t],bank='test',duration_ms=1000,markers=[])]))
        item=dict(pool='native',key=3,media=2)
        self.assertEqual(choose(c,item)['original'],'one.wav')
        x=copy.deepcopy(c);x['native']['segments'][0]['tracks'][0]['reviewed_generic']=False
        with self.assertRaises(ValueError):choose(x,item)
        x=copy.deepcopy(c);x['native']['segments'][0]['tracks'][0]['sources'][0]['originals'].append(dict(file='two.wav'))
        with self.assertRaises(ValueError):choose(x,item)

    def test_page_escapes_metadata_and_offers_controls(self):
        row=dict(id='S01',title='<script>bad()</script>',function='punctuation',priority=True,
            reason='Provisional',risk='Unknown',listen_for='Ending',preview='audio/a.opus',
            identity=dict(markers=[],preview_note='Not listened'),
            metrics=dict(seconds=60,low_energy_inspection_seconds=[20],rms_dbfs=-20,
                         envelope_p10_dbfs=-30,envelope_p90_dbfs=-10))
        text=page([row])
        self.assertNotIn('<script>bad()',text)
        self.assertIn('&lt;script&gt;',text)
        self.assertIn('data-jump="40.000"',text)
        self.assertIn('Export listening decisions',text)
        self.assertNotIn('https://',text)


if __name__=='__main__':unittest.main()
