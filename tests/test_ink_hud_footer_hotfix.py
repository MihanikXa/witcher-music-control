"""Actual GFx regression tests for the shared footer #1065 correction."""
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('hotfix',ROOT/'tools/build-ink-hud-footer-hotfix.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
OUT=ROOT/'build/ink-hud-v4-hotfix-rc2-footer'
@unittest.skipUnless((OUT/'prepared.json').exists(),'Private compiled RC2 absent')
class FooterHotfixTests(unittest.TestCase):
 def test_faulty_name_is_lexically_resolved_in_installed_bytecode(self):
  source=h.one(h.WORK/'installed-pcode','ModuleInputFeedback.pcode').read_text()
  self.assertEqual(source.count('getlex Multiname("buttonsSize",'),3)
  self.assertIn('findproperty Multiname("buttonsSize",',source)
  self.assertIn('setproperty Multiname("buttonsSize",',source)
  original=h.one(h.WORK/'installed-export/scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
  self.assertNotIn('var buttonsSize',original)
 def test_corrected_bytecode_has_no_unresolved_buttons_size(self):
  source=h.one(OUT/'final-pcode','ModuleInputFeedback.pcode').read_text()
  self.assertNotIn('buttonsSize',source)
 def test_original_v3_alignment_and_accepted_v4_spacing(self):
  corrected=h.one(OUT/'after/scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
  working=h.one(ROOT/'build/ink-hud-v3-final/vector-export/hud/scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
  self.assertEqual(h.method(corrected),h.method(working));self.assertIn('BUTTONS_PADDING:Number = 20',corrected)
 def test_only_exact_footer_class_statements_changed(self):
  changed=[]
  for before in (OUT/'before/scripts').rglob('*.as'):
   after=OUT/'after/scripts'/before.relative_to(OUT/'before/scripts')
   if before.read_bytes()!=after.read_bytes():
    changed.append(before.name);self.assertEqual(h.repair.repair(before.read_text(encoding='utf-8-sig')),after.read_text(encoding='utf-8-sig'))
  self.assertEqual(changed,['ModuleInputFeedback.as'])
 @unittest.skipUnless((OUT/'receipt.json').exists(),'Private packaged RC2 absent')
 def test_entire_package_preserves_rc1_except_root_bundle_metadata(self):
  import zipfile,hashlib
  receipt=json.loads((OUT/'receipt.json').read_text());base=json.loads((h.BASE/'receipt.json').read_text())
  self.assertEqual(len(receipt['unchanged_keys']),22)
  self.assertNotIn('inkRadialDiagnostic',' '.join(receipt['package_members']))
  with zipfile.ZipFile(receipt['zip_path']) as z:
   self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),set(base['package_members']))
   for key,expected in base['package_members'].items():
    if key.endswith(('blob0.bundle','metadata.store')) and '/modInkIronHUDRefinementV4/' in key:continue
    self.assertEqual(hashlib.sha256(z.read(key)).hexdigest(),expected)
  for key,expected in base['resource_hashes'].items():
   if key!=h.KEY:self.assertEqual(receipt['resource_hashes'][key],expected)
if __name__=='__main__':unittest.main()
