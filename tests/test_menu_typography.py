"""Targeted code/art/menu regressions. No claim of runtime visual acceptance."""
import importlib.util,json,re,struct,unittest,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('builder',ROOT/'tools/build-menu-typography.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class TypographyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.receipt=json.loads((b.OUT/'receipt.json').read_text());cls.prepared=json.loads((b.OUT/'prepared.json').read_text())
 def test_changed_movies_only_change_actionscript(self):
  count=0
  for row in self.prepared['resources']:
   old=(b.c.OUT/'prepared-inputs'/row['resource']).read_bytes();new=(b.OUT/'prepared-inputs'/row['resource']).read_bytes()
   a=b.b.m.b.audit.swf_tags(old)[2];z=b.b.m.b.audit.swf_tags(new)[2]
   self.assertEqual([(c,p) for c,p in a if c!=82],[(c,p) for c,p in z if c!=82])
   if old!=new:count+=1
  self.assertEqual(count,8)
 def test_slim_header_background_map_and_unmodified_movies_exact(self):
  for row in self.prepared['resources']:
   if Path(row['resource']).stem not in b.TARGETS:self.assertEqual((b.c.OUT/'prepared-inputs'/row['resource']).read_bytes(),(b.OUT/'prepared-inputs'/row['resource']).read_bytes())
  self.assertNotIn('panel_common',b.TARGETS);self.assertNotIn('panel_worldmap',b.TARGETS)
 def test_measured_per_character_caps_are_not_uniform_uppercase(self):
  helper=b.t.HELPER
  self.assertIn('lower.push(ch != ch.toUpperCase())',helper);self.assertIn('small.size = size * 0.80',helper)
  self.assertIn('tf.setTextFormat(small,starts[i],ends[i])',helper)
  self.assertIn('tf.textWidth > tf.width - 4',helper);self.assertIn('Math.max(0.82',helper)
  self.assertIn('rec.source',helper);self.assertIn('new flash.utils.Dictionary(true)',helper)
  self.assertNotIn('addEventListener',helper);self.assertNotIn('tf.x =',helper);self.assertNotIn('tf.y =',helper)
 def test_narrative_input_and_numerical_fields_not_case_transformed(self):
  for token in ['tf.type == "input"','name.indexOf("description")','name.indexOf("body")','name.indexOf("story")','name.indexOf("value")','name.indexOf("count")']:self.assertIn(token,b.t.HELPER)
  self.assertNotIn('.data =',b.t.HELPER);self.assertNotIn('SetVarValue',b.t.HELPER)
 def test_alchemy_role_and_status_changes_in_compiled_class(self):
  text=b.b.patch.one_file(b.OUT/'movies/panel_alchemy/after/scripts','ItemCraftingModule').read_text(encoding='utf-8-sig')
  self.assertIn('this.qfCaps(own,18)',text);self.assertIn('this.qfCaps(own,16)',text);self.assertIn('this.qfCaps(own,21)',text)
  self.assertIn('own.textColor = code == 4 ? 7829103 : 9603966',text)
  self.assertIn('good ? 10787199 : 14239803',text) # individual missing counts remain semantic
  self.assertIn('this.qfTypeTree(this.inkM)',text)
 def test_every_modified_class_has_exact_native_interface_and_no_new_listeners(self):
  for row in self.prepared['resources']:
   if not row.get('only_doabc_changed'):continue
   folder=b.OUT/'movies'/Path(row['resource']).stem
   for change in row['classes']:
    n=change['class_name'];a=b.b.patch.one_file(folder/'before/scripts',n).read_text(encoding='utf-8-sig');z=b.b.patch.one_file(folder/'after/scripts',n).read_text(encoding='utf-8-sig')
    for sig in re.findall(r'(?:public|protected) function [^\n]+',a):self.assertIn(sig,z)
    self.assertEqual(re.findall(r'addEventListener\([^\n]+',a),re.findall(r'addEventListener\([^\n]+',z))
 def test_no_global_font_or_hud_resources(self):
  for row in self.prepared['resources']:
   self.assertNotIn('/hud/',row['resource']);self.assertNotIn('/witcher3/',row['resource']);self.assertNotIn('fonts.xml',row['resource'])
  before=json.loads((b.c.OUT/'receipt.json').read_text())['members']
  for name,sha in before.items():
   if not name.endswith(('blob0.bundle','metadata.store')):self.assertEqual(self.receipt['members'][name],sha)
 def test_item_cache_index_roundtrip_payloads_and_exclusions(self):
  receipt=json.loads((b.OUT/'icons/receipt.json').read_text());source=Path(b.b.REF/'mods/modInkAndIronIcons/content/texture.cache')
  output=b.OUT/'icons/texture.cache';rows=list(b.b.m.b.inventory.cache_entries(output));self.assertEqual(len(rows),2079)
  self.assertEqual(len(receipt['excluded_existing_fixes']),9);self.assertFalse(set(r['resource'] for r in rows)&set(receipt['excluded_existing_fixes']))
  self.assertTrue(all('/icons/inventory/' in r['resource'] for r in rows))
  before=source.read_bytes();after=output.read_bytes()
  for row in rows:self.assertEqual(before[row['offset']:row['offset']+row['packed']],after[row['offset']:row['offset']+row['packed']])
  self.assertEqual(struct.unpack('<QIIII4sI',after[-32:])[-2:],(b'HCXT',6))
 def test_every_selected_texture_zlib_length_and_block_dimensions(self):
  path=b.OUT/'icons/texture.cache';data=path.read_bytes()
  for row in b.b.m.b.inventory.cache_entries(path):
   block=data[row['offset']:row['offset']+row['packed']];packed,size,kind=struct.unpack_from('<IIB',block)
   self.assertEqual(kind,0,row['resource']);self.assertEqual(packed+9,len(block),row['resource'])
   raw=zlib.decompress(block[9:]);self.assertEqual(len(raw),size);self.assertEqual(size,row['size'])
   blocks=((row['width']+3)//4)*((row['height']+3)//4)
   # Four original 83x83 bomb icons use uncompressed RGBA (27,556 bytes),
   # while the other 2,075 selected images have BC3-sized payloads.
   self.assertIn(len(raw),(blocks*8,blocks*16,row['width']*row['height']*4),row['resource'])
 def test_icon_preview_proves_actual_texture_differences(self):
  proof=json.loads((b.OUT/'preview-evidence.json').read_text());self.assertEqual(len(proof['icons']),7)
  for row in proof['icons']:
   self.assertTrue(row['base_candidates']);self.assertTrue(all(r['different_from_author'] for r in row['base_candidates']))
  self.assertTrue(proof['smcp_available_in_ttf']);self.assertTrue(all(r['fits_model'] for r in proof['model_metrics']))
 def test_uppercase_accent_samples_exist_in_accepted_383_glyph_swf(self):
  spec=importlib.util.spec_from_file_location('prep',ROOT/'tools/prepare-english-gentium.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
  data=(ROOT/'build/gentium-font-source-final/fonts_en.redswf').read_bytes();payload=next(p for code,p in prep.audit.swf_tags(data)[2] if code==75);codes=set(prep.layout(payload)['codes'])
  self.assertEqual(len(codes),383)
  sample='Élixir de la Rivière — Wolf’s Hour Greater Blue Mutagen Łódź Œuvre Æther'
  self.assertFalse(set(map(ord,sample.upper()))-codes)
 def test_official_native_and_packaged_extraction(self):
  self.assertEqual({r['label'] for r in self.receipt['native'] if r['passed']},{'cook','validate','pack','metadata'})
  self.assertIn('Errors found in 0 resources:',(b.OUT/'native-final/validate.full.log').read_text(errors='replace'))
  for row in self.prepared['resources']:
   self.assertEqual(b.b.m.b.bars.extract(b.OUT/'packed/blob0.bundle',row['resource']),(b.OUT/'prepared-inputs'/row['resource']).read_bytes())
 def test_package_hashes_and_live_freeze(self):
  self.assertEqual(b.b.m.b.fallback.sha(Path(self.receipt['zip_path'])),self.receipt['zip_sha256'])
  self.assertEqual(b.b.m.b.bars.snapshot(b.b.m.v.GAME,b.b.m.v.SETTINGS),json.loads((b.OUT/'frozen.json').read_text()))
  with zipfile.ZipFile(self.receipt['zip_path']) as z:
   self.assertIsNone(z.testzip())
   for name,sha in self.receipt['members'].items():self.assertEqual(b.b.m.b.audit.sha(z.read(name)),sha)
if __name__=='__main__':unittest.main()
