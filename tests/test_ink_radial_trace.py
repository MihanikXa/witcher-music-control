"""Diagnostic safety and checkpoint coverage; no gameplay success claims."""
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('i',ROOT/'tools/instrument-radial-movies.py');i=importlib.util.module_from_spec(s);s.loader.exec_module(i)
class TraceTests(unittest.TestCase):
 def test_span_handles_strings_comments_nested_blocks(self):
  t='function f() { var s:String="}"; /* { */ if(true) { x(); } } next'
  a,z=i.body_span(t,'function f()');self.assertEqual(t[z:],'} next')
 def test_exceptions_rethrown_original_body_retained(self):
  old='function f() : void { nativeCall(); }';new=i.wrap(old,'function f()','test')
  self.assertIn('nativeCall();',new);self.assertIn('throw qfDiagError;',new)
 def test_constructor_super_precedes_observers(self):
  text='public class InputFeedbackButton { public function InputFeedbackButton() { super(); body(); } }'
  new=i.wrap(text,'public function InputFeedbackButton()','ctor')
  self.assertLess(new.index('super();'),new.index('qfDiagEmit'));self.assertLess(new.index('super();'),new.index('try {'))
 def test_ledger_does_not_affect_hud_child_count(self):
  self.assertIn('stage.addChild(this.qfDiagText)',i.ROOT_HELPER)
  self.assertNotIn('\n               addChild(this.qfDiagText)',i.ROOT_HELPER)
  self.assertIn('mouseEnabled = false',i.ROOT_HELPER)
 def test_native_observer_not_forcing_or_handling_open(self):
  t=(ROOT/'src/hud/inkRadialDiagnostic.ws').read_text(encoding='utf-8-sig')
  a=t.index('function QfRadialProbeInput');z=t.index('\n}',a);body=t[a:z]
  self.assertIn('return false;',body);self.assertNotIn('ShowRadialMenu(',body)
  self.assertIn('return wrappedMethod(action);',t)
 def test_provider_query_is_guarded(self):
  text='class ModuleInputFeedback { public function ModuleInputFeedback() { super(); } protected function createButton(a:Object) : Object { var _loc3_:InputFeedbackButton = new ClassRef() as InputFeedbackButton; return _loc3_; } protected function repositionButtons() : void { foo(); } }'
  patched=i.prompt(text,'ModuleInputFeedback','hud')
  self.assertIn('"qfDiagProvider" in _loc3_',patched)
  self.assertIn('un-instrumented first-domain class',patched)
 def test_all_early_gate_observations_present(self):
  t=(ROOT/'src/hud/inkRadialDiagnostic.ws').read_text(encoding='utf-8-sig')
  for gate in ['already shown','radial action disallowed','dialogue/cutscene','blackscreen/fade','input denied']:self.assertIn(gate,t)
  self.assertIn('qfRadialConfigCompleted = true',t)
 @unittest.skipUnless((ROOT/'build/ink-radial-trace-d1-release-final/prepared.json').exists(),'Private completed build absent')
 def test_actual_non_abc_definitions_and_images_frozen(self):
  s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  import json
  root=ROOT/'build/ink-radial-trace-d1-release-final';receipt=json.loads((root/'prepared.json').read_text())
  self.assertEqual(len(receipt['movie_contracts']),3);self.assertEqual(len(receipt['unchanged_keys']),20)
  for k in receipt['movie_contracts']:
   a=(ROOT/'build/ink-radial-trace-work/inputs'/k).read_bytes();b=(root/'prepared-inputs'/k).read_bytes()
   self.assertEqual([(c,p) for c,p in m.b.audit.swf_tags(a)[2] if c!=82],[(c,p) for c,p in m.b.audit.swf_tags(b)[2] if c!=82])
   self.assertEqual([c['tail'] for c in m.b.font.native.chunks(a)[1:]],[c['tail'] for c in m.b.font.native.chunks(b)[1:]])
 @unittest.skipUnless((ROOT/'build/ink-radial-trace-d1-release-final/receipt.json').exists(),'Private packaged diagnostic absent')
 def test_native_bundle_controls_reproduced(self):
  s=importlib.util.spec_from_file_location('packer',ROOT/'tools/reconstruct-radial-trace-bundle.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
  for name in ('ink-hud-refinement-v2-release-final','ink-hud-v3-diagnostic-final','ink-radial-trace-d1-final'):
   bundle=ROOT/'build'/name/'packed/blob0.bundle';files={e['resource']:p.b.bars.extract(bundle,e['resource']) for e in p.b.audit.entries(bundle)}
   self.assertEqual(p.reconstruct(bundle,files),bundle.read_bytes())
 @unittest.skipUnless((ROOT/'build/ink-radial-trace-d1-release-final/receipt.json').exists(),'Private packaged diagnostic absent')
 def test_package_retains_rc1_support_and_does_not_claim_native_success(self):
  import json,zipfile,hashlib
  new=json.loads((ROOT/'build/ink-radial-trace-d1-release-final/receipt.json').read_text());old=json.loads((ROOT/'build/ink-hud-v4-hotfix-rc1-final/receipt.json').read_text())
  self.assertFalse(new['official_cook_validated']);self.assertFalse(new['runtime_tested']);self.assertFalse(new['root_cause_confirmed'])
  with zipfile.ZipFile(new['zip_path']) as z:
   self.assertIsNone(z.testzip());self.assertEqual(hashlib.sha256(Path(new['zip_path']).read_bytes()).hexdigest(),new['zip_sha256'])
   for key,value in old['package_members'].items():
    if key.endswith(('blob0.bundle','metadata.store')) and '/modInkIronHUDRefinementV4/' in key:continue
    self.assertEqual(hashlib.sha256(z.read(key)).hexdigest(),value)
if __name__=='__main__':unittest.main()
