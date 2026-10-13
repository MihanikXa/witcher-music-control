"""Synthetic V3 diagnostic regressions: no game/third-party fixtures."""
import importlib.util,struct,unittest
from pathlib import Path
import test_ink_hud_refinement as base
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('v3',ROOT/'tools/build-ink-hud-v3-diagnostic.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class DiagnosticTests(unittest.TestCase):
    def test_red_correction_changes_only_known_paints(self):
        old=int('DE9C89',16)
        text=f'head {old} native; {old} sync; 11171173,0); g.beginFill(12820879,0.85); dimensions=3.8; neutral=keep;'
        result=d.reds(text)
        self.assertEqual(result,text.replace(str(old),str(int('D87566',16))).replace('11171173',str(int('B65348',16))).replace('12820879','0xC98678'))
    def test_unknown_palette_rejected(self):
        with self.assertRaises(ValueError):d.reds('unknown')
    def test_marker_preserves_navigation_call(self):
        text='   import flash.display.Sprite;\n            this._gpadIcon.gotoAndStop(this.getPadIconFrameLabel(navCode));'
        result=d.button_probe(text)
        self.assertIn('gotoAndStop(this.getPadIconFrameLabel(navCode))',result)
        self.assertIn('getChildByName("qfGlyphPathV3")',result)
        self.assertNotIn('addEventListener',result)
        self.assertNotIn('hitArea =',result)
    def test_probe_changes_only_36_interior_blocks_and_crcs(self):
        original=d.r.append_atlas(base.native_fixture(),'private.dds',64,64,d.r.encode_block([(239,227,206,255)]*16)*256)
        changed,report=d.write_texture_mark(original,'private.dds',(0,0,64,64),'#FF00FF')
        before=d.b.font.native.chunks(original);after=d.b.font.native.chunks(changed)
        self.assertEqual([c['properties'] for c in before],[c['properties'] for c in after])
        self.assertEqual(before[1]['tail'],after[1]['tail'])
        old,new=before[2]['tail'][28:],after[2]['tail'][28:]
        self.assertEqual(sum(old[i:i+16]!=new[i:i+16] for i in range(0,len(old),16)),36)
        self.assertEqual(report['marked_rectangle'],[20,20,44,44])
        self.assertTrue(all(c['crc_valid'] for c in after))
        self.assertEqual(d.r.p.header_crc(changed),struct.unpack_from('<I',changed,32)[0])
    def test_probe_rejects_small_image(self):
        original=d.r.append_atlas(base.native_fixture(),'private.dds',64,64,d.r.encode_block([(239,227,206,255)]*16)*256)
        with self.assertRaises(ValueError):d.write_texture_mark(original,'private.dds',(0,0,8,8),'#FF00FF')
if __name__=='__main__':unittest.main()
