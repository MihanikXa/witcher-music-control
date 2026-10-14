"""Hotfix contracts: letter-only geometry, exact radial ABC and frozen v4."""
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('hotfix',ROOT/'tools/build-ink-hud-v4-hotfix.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
class HotfixTests(unittest.TestCase):
 def test_only_face_letter_layers_shrink(self):
  for label in ['A','B','X','Y']:
   a=h.original_paths('ICO_Xbox_'+label,64,64,h.m.FONT);b=h.small_paths('ICO_Xbox_'+label,64,64,h.m.FONT)
   self.assertEqual(a[:2],b[:2]);self.assertEqual(a[2][0],b[2][0])
   for (ka,pa),(kb,pb) in zip(a[2][1],b[2][1]):
    self.assertEqual(ka,kb)
    for old,new in zip(pa,pb):self.assertAlmostEqual(new,32+(old-32)*.8)
 def test_all_other_button_art_exact(self):
  for label in ['L_hold','R_tabs','LB','RB','LT','RT','dpad_up','Home','Menu','View']:
   self.assertEqual(h.original_paths('ICO_Xbox_'+label,64,64,h.m.FONT),h.small_paths('ICO_Xbox_'+label,64,64,h.m.FONT))
 @unittest.skipUnless((ROOT/'build/ink-hud-v4-hotfix-rc1-final/prepared.json').exists(),'Private build absent')
 def test_actual_radial_code_is_working_v3(self):
  key='gameplay/gui_new/swf/hud/hud_radialmenu.redswf';a=(h.V3/'pack-input'/key).read_bytes();b=(ROOT/'build/ink-hud-v4-hotfix-rc1-final/prepared-inputs'/key).read_bytes()
  self.assertEqual([p for c,p in h.m.b.audit.swf_tags(a)[2] if c==82],[p for c,p in h.m.b.audit.swf_tags(b)[2] if c==82])
 @unittest.skipUnless((ROOT/'build/ink-hud-v4-hotfix-rc1-final/prepared.json').exists(),'Private build absent')
 def test_every_nonbutton_component_exact_v4(self):
  out=ROOT/'build/ink-hud-v4-hotfix-rc1-final';p=json.loads((h.BASE/'receipt.json').read_text());r=json.loads((out/'prepared.json').read_text())
  self.assertEqual(len(r['changes']),9);self.assertEqual(len(r['unchanged_keys']),14)
  for k in r['unchanged_keys']:self.assertEqual(h.m.b.fallback.sha(out/'prepared-inputs'/k),p['resource_hashes'][k])
  self.assertIn('gameplay/gui_new/swf/hud/hud_enemyfocus.redswf',r['unchanged_keys'])
 @unittest.skipUnless((ROOT/'build/ink-hud-v4-hotfix-rc1-final/prepared.json').exists(),'Private build absent')
 def test_iteminfo_and_root_bytecode_exact_v4(self):
  for stem in ['hud_iteminfo','hud']:
   key='gameplay/gui_new/swf/hud/'+stem+'.redswf';a=(h.BASE/'pack-input'/key).read_bytes();b=(ROOT/'build/ink-hud-v4-hotfix-rc1-final/prepared-inputs'/key).read_bytes()
   self.assertEqual([p for c,p in h.m.b.audit.swf_tags(a)[2] if c==82],[p for c,p in h.m.b.audit.swf_tags(b)[2] if c==82])
 def test_null_equality_does_not_prove_live_exception(self):
  # Model the AS nullable equality hazard. No assertion that the game visits
  # this state: that's precisely the missing runtime observation.
  gpad=xbox=None;self.assertTrue(gpad==xbox)
  with self.assertRaises(AttributeError):bool(gpad.visible)
if __name__=='__main__':unittest.main()
