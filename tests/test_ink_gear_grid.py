"""Targeted private Gear slice checks. No runtime gameplay success inferred."""
import importlib.util,json,re,shutil,subprocess,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
patch=load('patch-ink-gear-grid');meta=load('relocate-inventory-metadata');build=load('build-ink-gear-grid')
OUT=ROOT/'build/ink-gear-grid-v1-focus'
class PadTests(unittest.TestCase):
 @unittest.skipUnless(shutil.which('node'),'Node unavailable for source-predicate test')
 def test_actual_pad_predicate_duplicate_down_hold_release_and_repress(self):
  source=patch.snippet('GearPad.asinc');a,z=patch.trace.body_span(source,'public static function qfGearPadAllow(');body=source[a+1:z].replace('var key:String','var key')
  js='let qfGearGrid=true,qfGearHeld={},qfGearDown={},qfGearFire={}; function allow(d,now){'+body+'};'
  js+='''
const assert=require('assert');
const key=(value,now,code=142)=>allow({code,value},now);
assert.strictEqual(key('keyDown',1000),true);
assert.strictEqual(key('keyDown',1001),false);
assert.strictEqual(key('keyHold',1010),false);
assert.strictEqual(key('keyHold',1399),false);
assert.strictEqual(key('keyHold',1400),true);
assert.strictEqual(key('keyHold',1450),false);
assert.strictEqual(key('keyUp',1500),true);
assert.strictEqual(key('keyDown',1510),true);
assert.strictEqual(key('keyDown',1511,143),true);
assert.strictEqual(key('keyDown',1512,143),false);
assert.strictEqual(key('keyDown',1512,140),true);
qfGearGrid=false;
assert.strictEqual(key('keyDown',1513,143),true);
'''
  result=subprocess.run([shutil.which('node')],input=js,text=True,capture_output=True,timeout=10);self.assertEqual(result.returncode,0,result.stderr)
class MetadataTests(unittest.TestCase):
 def test_native_one_key_controls_roundtrip_and_changed_control(self):
  for name in ('editor-cook-resolved','npc-shadow-unique-cook','field-folio-control-v2','subtitle-shadow-control-v1'):
   folder=ROOT/'build'/name/'packed'
   if not folder.exists():self.skipTest('Private native controls absent')
   raw=(folder/'metadata.store').read_bytes();parsed=meta.parse(raw)
   self.assertEqual(meta.write(parsed),raw);self.assertEqual(meta.write(meta.replace_single(parsed,folder/'blob0.bundle')),raw)
  a=ROOT/'build/editor-cook-resolved/packed';b=ROOT/'build/npc-shadow-unique-cook/packed'
  self.assertEqual(meta.write(meta.replace_single(meta.parse((a/'metadata.store').read_bytes()),b/'blob0.bundle')),(b/'metadata.store').read_bytes())
 def test_unknown_version_rejected(self):
  with self.assertRaises(ValueError):meta.parse(b'\x03VTM'+(8).to_bytes(4,'little')+bytes(20))
@unittest.skipUnless((OUT/'receipt.json').exists(),'Private completed prototype absent')
class PrototypeTests(unittest.TestCase):
 def setUp(self):self.receipt=json.loads((OUT/'receipt.json').read_text())
 def test_native_events_and_original_function_contracts(self):
  before=build.REF/'ui-export/scripts';after=OUT/'after/scripts'
  self.assertGreater(build.b.class_contracts(before,after)['original_declarations_retained'],1000)
  old=build.unique(before,'MenuInventory.as').read_text(encoding='utf-8-sig');new=build.unique(after,'MenuInventory.as').read_text(encoding='utf-8-sig')
  old_exports=build.b.public_chain(before,'MenuInventory');new_exports=build.b.public_chain(after,'MenuInventory')
  for name,value in old_exports.items():self.assertEqual(new_exports[name],value)
  event=lambda t:set(re.findall(r'GameEvent\.(?:REGISTER|CALL),"([^"]+)"',t))
  self.assertEqual(event(old),event(new))
 def test_no_artwork_font_symbol_or_atlas_pixel_changes(self):
  old=(build.REF/'ui'/build.KEY).read_bytes();new=(OUT/'prepared-inputs'/build.KEY).read_bytes()
  self.assertEqual([(c,p) for c,p in build.b.audit.swf_tags(old)[2] if c!=82],[(c,p) for c,p in build.b.audit.swf_tags(new)[2] if c!=82])
  self.assertEqual([c['tail'] for c in build.b.font.native.chunks(old)[1:]],[c['tail'] for c in build.b.font.native.chunks(new)[1:]])
  report=build.atlas.validate(new);self.assertEqual({t['compression'] for t in report['textures']},{'TCM_DXTAlpha','TCM_DXTNoAlpha'})
 def test_official_dye_method_exact_and_upstream_086_behaviors_retained(self):
  after=OUT/'after/scripts';old=build.REF/'ui-export/scripts';official=build.unique(build.REF/'hoods-export/scripts','SlotPaperdoll.as').read_text(encoding='utf-8-sig');current=build.unique(after,'SlotPaperdoll.as').read_text(encoding='utf-8-sig');signature='public function canDrop(dragData:IDragTarget) : Boolean'
  a,z=patch.trace.body_span(official,signature);b,y=patch.trace.body_span(current,signature);self.assertEqual(official[a+1:z],current[b+1:y])
  atext=build.unique(old,'MenuInventory.as').read_text(encoding='utf-8-sig');btext=build.unique(after,'MenuInventory.as').read_text(encoding='utf-8-sig')
  for signature in ('protected function iaiEqStep(', 'public function iaiSetRarityStyle('):
   a,z=patch.trace.body_span(atext,signature);b,y=patch.trace.body_span(btext,signature);self.assertEqual(atext[a+1:z],btext[b+1:y])
 def test_native_resource_and_script_compiler_gates(self):
  native=self.receipt['native_commands'];self.assertTrue({'cook','validate','pack'} <= {r['label'] for r in native if r['passed']})
  if not self.receipt['native_metadata_passed']:self.assertTrue(self.receipt['metadata_reconstruction']['native_control_byte_identical'])
  compile=self.receipt['compiler'];self.assertEqual(compile['source_sha256'],build.b.fallback.sha(ROOT/'src/inventory/inkGearGrid.ws'))
  self.assertEqual(compile['results'][0]['warnings'],compile['results'][1]['warnings']);self.assertEqual(compile['results'][0]['assertions'],compile['results'][1]['assertions'])
 def test_only_inventory_native_resource_and_original_script_packaged(self):
  with zipfile.ZipFile(self.receipt['zip_path']) as z:
   self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),3)
   self.assertTrue(all(n.startswith('Mods/modInkIronGearGridPrototype/content/') for n in z.namelist()))
   self.assertEqual(z.read('Mods/modInkIronGearGridPrototype/content/scripts/local/inkGearGrid.ws'),(ROOT/'src/inventory/inkGearGrid.ws').read_bytes())
  entries=list(build.b.audit.entries(OUT/'packed/blob0.bundle'));self.assertEqual([e['resource'] for e in entries],[build.KEY]);self.assertEqual(build.b.bars.extract(OUT/'packed/blob0.bundle',build.KEY),(OUT/'prepared-inputs'/build.KEY).read_bytes())
 def test_reconstructed_metadata_matches_native_bundle_and_inventory_hash(self):
  parsed=meta.parse((OUT/'packed/metadata.store').read_bytes());entry=list(build.b.audit.entries(OUT/'packed/blob0.bundle'))[0]
  self.assertEqual(parsed['version'],7);self.assertEqual(meta.paths(parsed)[1].lower().replace('\\','/'),build.KEY)
  self.assertEqual(parsed['sections'][0][1][2:4],(entry['packed'],entry['size']));self.assertEqual(parsed['sections'][0][1][5],entry['codec']);self.assertEqual(parsed['sections'][1][1],(1,1,entry['offset'],entry['packed'],0))
  if not self.receipt['native_metadata_passed']:self.assertTrue(self.receipt['metadata_reconstruction']['inventory_lookup_hash_matches_installed_native_v7'])
 def test_saved_hidden_paperdoll_focus_returns_to_live_grid(self):
  text=build.unique(OUT/'after/scripts','MenuInventory.as').read_text(encoding='utf-8-sig')
  a,z=patch.trace.body_span(text,'protected function qfGearRefresh(');body=text[a+1:z]
  self.assertIn('this.mcPaperDollModule.focused > 0',body)
  self.assertRegex(body,r'if\(!qfFocusedSlot\s*\|\|\s*!qfFocusedSlot.visible\)\s*\{?\s*selectTargetModule\(this.mcPlayerInventory\)')
  self.assertLess(body.index('qfGearReflow('),body.index('var qfFocusedSlot:SlotPaperdoll'))
 def test_protected_deployed_hud_and_merged_inventory_unchanged(self):
  self.assertEqual(build.frozen(),self.receipt['frozen_inputs'])
if __name__=='__main__':unittest.main()
