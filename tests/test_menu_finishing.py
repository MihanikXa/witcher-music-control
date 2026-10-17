"""Menus v4 contracts/metrics; cannot establish runtime screenshot parity."""
import importlib.util,json,re,unittest,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('build',ROOT/'tools/build-menu-finishing.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class FinishingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.receipt=json.loads((b.OUT/'receipt.json').read_text());cls.prepared=json.loads((b.OUT/'prepared.json').read_text());cls.model=json.loads((b.OUT/'font-model.json').read_text())
 def source(self,stem,name,stage='after'):
  return b.b.patch.one_file(b.OUT/'movies'/stem/stage/'scripts',name).read_text(encoding='utf-8-sig')
 def body(self,text,name):
  _,a,z=b.f.p.body(text,name);return text[a+1:z]
 def test_original_row_position_contract_and_internal_correction(self):
  xml=ET.parse(b.OUT/'alchemy-v3.xml').getroot();placements=[n for n in xml.iter() if n.get('name')=='tfSecondLine' and n.find('matrix') is not None]
  self.assertEqual(int(placements[0].find('matrix').get('translateY'))/20,42.45)
  original=(b.OUT/'movies/panel_alchemy/before/scripts/red/game/witcher3/menus/common/RecipeIconItemRenderer.as').read_text(encoding='utf-8-sig');self.assertIn('textField.y = 9;',original)
  after=self.source('panel_alchemy','ItemCraftingModule');alignment=self.body(after,'qfAlignRecipe')
  for token in ('originalName.y','originalStatus.y','name.getLineMetrics','status.getLineMetrics','name.y =','status.y ='):self.assertIn(token,alignment)
  self.assertNotIn('.x =',alignment);self.assertNotIn('+=',alignment.split('name.y =')[1])
  # Actual installed-font model preserves optical center while tightening the group.
  self.assertLess(self.model['row_metrics']['v4']['field_origin_gap'],20)
  self.assertGreater(self.model['row_metrics']['v3']['field_origin_gap'],33)
 def test_recipe_only_row_drawing_icons_levels_and_scroll_contracts_unchanged(self):
  for stem in ('panel_alchemy','panel_crafting'):
   old=self.source(stem,'ItemCraftingModule','before');new=self.source(stem,'ItemCraftingModule')
   for name in ('inkWalk','inkLevelTag','inkRect','inkRing','inkListTop'):
    self.assertEqual(self.body(old,name),self.body(new,name),name)
   a=self.body(old,'inkRow').split('own = this.inkOwnTF')[0];z=self.body(new,'inkRow').split('own = this.inkOwnTF')[0];self.assertEqual(a,z)
   self.assertIn('this.qfAlignRecipe(nm,own,tf,s2,h)',new);self.assertIn('if(well)',new)
 def test_roles_explicit_cache_and_bounded_non_cumulative_wrapping(self):
  text=self.source('panel_alchemy','ItemCraftingModule');body=self.body(text,'qfCaps')
  for token in ('rec.explicit','rec.ratio','rec.tracking','rec.heavy','originalWrap','!rec.didWrap','tf.replaceText','tracking * fit'):
   self.assertIn(token,body)
  self.assertIn('this.qfCaps(own,19.5,0.9,0.85)',text)
  self.assertIn('this.qfCaps(own,15.5,0.86,0.5)',text)
  self.assertIn('this.qfCaps(rec.title,32,0.92,1.6,true)',text)
 def test_palette_is_only_secondary_recipe_text(self):
  text=self.source('panel_alchemy','ItemCraftingModule');craft=self.body(text,'inkCraft')
  self.assertIn('tf.textColor = good ? 10787199 : 9603966',craft)
  self.assertIn('ct.textColor = good ? 14861439 : 9603966',craft)
  self.assertIn('own.textColor = sel ? 14861439 : 10787199',self.body(text,'inkRow'))
  # Native level warnings and all positive/negative stat-row colors are unchanged.
  for name in ('inkLevelTag','inkTipRows'):
   self.assertEqual(self.body(self.source('panel_alchemy','ItemCraftingModule','before'),name),self.body(text,name))
 def test_short_prose_fit_is_bounded_and_before_layout(self):
  text=self.source('panel_alchemy','ItemCraftingModule');body=self.body(text,'qfProse');frame=self.body(text,'inkFrame')
  self.assertIn('tf.length > 100',body);self.assertIn('17.5',body);self.assertIn('probe.textWidth',body);self.assertNotIn('tf.text =',body)
  self.assertLess(frame.index('this.qfProse'),frame.index('this.inkTipLayout'))
  model=self.model['description'];self.assertGreater(model['width_at_19'],model['usable_width']);self.assertLessEqual(model['fitted_width'],model['usable_width']);self.assertGreaterEqual(model['fitted_size'],17.5)
 def test_font_model_uses_actual_current_library_and_long_title_fits(self):
  self.assertEqual(self.model['font_owner']['sha256'],b.b.m.b.fallback.sha(b.OUT/'installed-font.redswf'))
  self.assertEqual(self.model['regular_glyphs'],383)
  self.assertTrue(all(r['fits'] for r in self.model['sample_headings']))
  self.assertTrue(any(r['wrap'] for r in self.model['sample_headings']))
 def test_header_and_renderer_classes_are_exact(self):
  for name in ('TopBarNew','ModuleInputFeedback','InputFeedbackButton'):
   a=self.source('panel_common',name,'before');z=b.b.patch.one_file(b.OUT/'common-retained-check/scripts',name).read_text(encoding='utf-8-sig');self.assertEqual(a,z)
 def test_footer_is_menu_local_and_preserves_buttons_and_warning_states(self):
  text=self.source('panel_common','MenuCommon');footer=self.body(text,'qfFooter')
  self.assertIn('this.qfFooter(this.mcInpuFeedback)',text);self.assertIn('rec.lastY',footer);self.assertIn('prefix.textWidth + 4',footer);self.assertIn('red > green + 50',footer);self.assertIn('color != 14861439',footer)
  for token in ('graphics','_currentWidth','button.scale','button.x =','addEventListener','dispatchEvent'):self.assertNotIn(token,footer)
  old=self.source('panel_common','MenuCommon','before')
  for name in re.findall(r'function ((?:OW|ow)\w+)\(',old):self.assertEqual(self.body(old,name),self.body(text,name))
 def test_all_native_interfaces_and_listeners_retained(self):
  for row in self.prepared['resources']:
   for change in row.get('classes',[]):
    name=change['class_name'];stem=Path(row['resource']).stem;old=self.source(stem,name,'before');new=self.source(stem,name)
    for sig in re.findall(r'(?:public|protected) function [^\n]+',old):self.assertIn(sig,new)
    self.assertEqual(re.findall(r'addEventListener\([^\n]+',old),re.findall(r'addEventListener\([^\n]+',new))
 def test_non_code_geometry_fonts_and_all_31_unchanged_movies(self):
  changed=0;exact=0
  for row in self.prepared['resources']:
   a=(b.parent.OUT/'prepared-inputs'/row['resource']).read_bytes();z=(b.OUT/'prepared-inputs'/row['resource']).read_bytes()
   self.assertEqual([(c,p) for c,p in b.b.m.b.audit.swf_tags(a)[2] if c!=82],[(c,p) for c,p in b.b.m.b.audit.swf_tags(z)[2] if c!=82])
   if a==z:exact+=1
   else:changed+=1
   self.assertNotIn('/hud/',row['resource']);self.assertNotIn('/witcher3/',row['resource'])
  self.assertEqual((changed,exact),(9,31))
 def test_scripts_options_item_bestiary_and_map_assets_exact(self):
  parent=json.loads((b.parent.OUT/'receipt.json').read_text())
  for name,sha in parent['members'].items():
   if name in ('Mods/modInkIronMenus087/content/blob0.bundle','Mods/modInkIronMenus087/content/metadata.store'):continue
   self.assertEqual(sha,self.receipt['members'][name],name)
 def test_native_or_verified_reconstruction_and_exact_extraction(self):
  if self.receipt['native_candidate_cook_validated']:
   self.assertEqual({r['label'] for r in self.receipt['native'] if r['passed']},{'cook','validate','pack','metadata'})
   self.assertIn('Errors found in 0 resources:',(b.OUT/'native-final/validate.full.log').read_text(errors='replace'))
  else:
   proof=self.receipt['reconstruction'];self.assertFalse(proof['native_candidate_cook_validated']);self.assertTrue(proof['independent_changed_metadata_exact']);self.assertEqual(len(proof['controls']),2);self.assertTrue(all(r['bundle_and_metadata_byte_identical'] for r in proof['controls']))
   self.assertEqual(self.receipt['native'][0]['timeout_seconds'],90);self.assertIsNone(self.receipt['native'][0]['exit_code'])
  for row in self.prepared['resources']:self.assertEqual(b.b.m.b.bars.extract(b.OUT/'packed/blob0.bundle',row['resource']),(b.OUT/'prepared-inputs'/row['resource']).read_bytes())
 def test_zip_crc_member_hashes_and_live_snapshot(self):
  self.assertEqual(b.b.m.b.fallback.sha(Path(self.receipt['zip_path'])),self.receipt['zip_sha256'])
  with zipfile.ZipFile(self.receipt['zip_path']) as z:
   self.assertIsNone(z.testzip())
   for name,sha in self.receipt['members'].items():self.assertEqual(b.b.m.b.audit.sha(z.read(name)),sha)
  self.assertEqual(b.b.m.b.bars.snapshot(b.b.m.v.GAME,b.b.m.v.SETTINGS),json.loads((b.OUT/'frozen.json').read_text()))
if __name__=='__main__':unittest.main()
