import copy
from datetime import datetime, timezone
from pathlib import Path
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

from observer_log_smoke import config_bytes, inspect_log
from observer_native_log_audit import PE, file_logger_layout
from sparse_stinger_probe import rest_only, validate_source, stinger_spec, TRIGGER, CUE
from sparse_reentry_author import SELECTED, REST_ITEM, MUSIC_ITEM
from sparse_interface_review import audible_overlap


def fixture():
    return ET.fromstring(f'''<Root><MusicPlaylistContainer ID="{SELECTED}">
      <PropertyList><Property Name="Volume"><Value>0</Value></Property></PropertyList>
      <ReferenceList><Reference Name="PlaylistRoot"><Custom><MusicPlaylistItem><ChildrenList>
      <MusicPlaylistItem ID="{REST_ITEM}"/><MusicPlaylistItem ID="{MUSIC_ITEM}"/>
      </ChildrenList></MusicPlaylistItem></Custom></Reference></ReferenceList>
      <Transitions Native="unchanged"/></MusicPlaylistContainer><Protected ID="native"/></Root>''')


class InterfaceTests(unittest.TestCase):
    def test_rest_only_restoration(self):
        a=fixture();b=rest_only(a)
        self.assertTrue(validate_source(a,b)['passed'])
        self.assertEqual(len(list(a.iter('MusicPlaylistItem'))),3)
        self.assertEqual(len(list(b.iter('MusicPlaylistItem'))),2)

    def test_rest_only_rejects_unrelated_and_transition_change(self):
        a=fixture()
        for name in ('Protected','Transitions','Value'):
            b=rest_only(a);next(b.iter(name)).text='unauthorized'
            with self.assertRaises(ValueError):validate_source(a,b)
        a.find('.//MusicPlaylistItem/ChildrenList')[0].set('ID','wrong')
        with self.assertRaises(ValueError):rest_only(a)

    def test_trigger_is_local_existing_definition_not_play_or_queue(self):
        s=stinger_spec()
        self.assertEqual(s['@Trigger'],TRIGGER);self.assertEqual(s['@Segment'],CUE)
        self.assertEqual(s['@NumSegmentAdvance'],0)
        self.assertNotIn('@Target',s);self.assertNotIn('@ActionType',s)

    def test_config_preserves_original_bytes_and_is_never_an_installer(self):
        a=b'[General]\r\nConfigVersion=7\r\n'
        b=config_bytes(a,Path(tempfile.gettempdir())/'wmc')
        self.assertTrue(b.startswith(a));self.assertIn(b'DebugScriptsForceFlush=true',b)
        with self.assertRaises(ValueError):config_bytes(a+b'[Scripts]\n',Path('test'))
        with self.assertRaises(ValueError):config_bytes(a,Path('bad\npath'))

    def test_capture_header_not_equivalent_to_observer(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'scriptslog.txt';p.write_bytes(b'Debugging scripts for version\n[Other] private text\n')
            r,rows=inspect_log(p,datetime(2000,1,1,tzinfo=timezone.utc))
            self.assertTrue(r['native_header_seen']);self.assertFalse(r['retail_marker_observed'])
            self.assertEqual(rows,[]);self.assertNotIn('private',str(r))
            with self.assertRaises(ValueError):inspect_log(p,datetime(2100,1,1,tzinfo=timezone.utc))
            with self.assertRaises(ValueError):inspect_log(p,datetime(2000,1,1))

    def test_only_existing_parser_accepts_wmc_records(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'scriptslog.txt'
            p.write_bytes(b'[WMCContext] WMCCTX1|epoch=1|seq=1|t=0|begin|origin=load_or_spawn\n')
            r,rows=inspect_log(p,datetime(2000,1,1,tzinfo=timezone.utc))
            self.assertTrue(r['normalization_passed']);self.assertEqual(len(rows),1)
            p.write_bytes(b'[WMCContext] WMCCTX1|forged\n')
            with self.assertRaises((ValueError,KeyError)):inspect_log(p,datetime(2000,1,1,tzinfo=timezone.utc))

    def test_pe_bounds_and_function_mapping(self):
        x=bytearray(0x800);x[:2]=b'MZ';struct.pack_into('<I',x,60,0x80)
        x[0x80:0x84]=b'PE\0\0';struct.pack_into('<HH',x,0x84,0x8664,3)
        struct.pack_into('<H',x,0x94,0xf0);struct.pack_into('<H',x,0x98,0x20b)
        struct.pack_into('<Q',x,0xb0,0x140000000)
        struct.pack_into('<II',x,0x98+112+24,0x3000,12)
        for i,(name,rva,raw,flags) in enumerate([('.text',0x1000,0x200,0x60000020),('.data',0x2000,0x400,0xc0000040),('.pdata',0x3000,0x600,0x40000040)]):
            a=0x188+40*i;x[a:a+8]=name.encode().ljust(8,b'\0')
            struct.pack_into('<III',x,a+12,rva,0x200,raw);struct.pack_into('<I',x,a+36,flags)
        struct.pack_into('<III',x,0x600,0x1000,0x1010,0)
        p=PE(x);self.assertEqual(p.function(0x1005),(0x1000,0x1010))
        self.assertTrue(p.section(0x2000)['flags']&0x80000000)
        for op in (lambda:p.off(0x4000),lambda:p.bytes(-1,2),lambda:p.function(0x1050),lambda:PE(x[:80]),lambda:file_logger_layout(p,'unreviewed')):
            with self.assertRaises(ValueError):op()

    def test_lifetime_alone_does_not_establish_audible_overlap(self):
        rows=[dict(role='cue',audible_first=None,audible_last=None),
              dict(role='outro',audible_first=20,audible_last=30)]
        self.assertEqual(audible_overlap(rows,'cue','outro'),[])
        rows[0].update(audible_first=28,audible_last=40)
        self.assertEqual(audible_overlap(rows,'cue','outro'),[[28,30]])
        rows[0].update(audible_first=31,audible_last=40)
        self.assertEqual(audible_overlap(rows,'cue','outro'),[])


if __name__=='__main__':unittest.main()
