"""Visual wiring and ownership gates, not a claim of screenshot acceptance."""
import importlib.util,json,re,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('complete-menus-087');b=c.b
class VisualTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.prepared=json.loads((c.OUT/'prepared.json').read_text());cls.receipt=json.loads((c.OUT/'receipt.json').read_text())
 def test_current_root_cause_is_effective_owner_not_corrupt_release(self):
  e=json.loads((c.OUT/'ownership.json').read_text())
  self.assertTrue(all(r['equal'] for r in e['installed_v1_members'].values()))
  common=next(r for r in e['resources'] if r['resource']==c.COMMON)
  self.assertEqual(common['winner']['owner'],'modInkIronHUDRefinementV4')
  self.assertNotEqual(common['sha256'],next(r for r in json.loads((c.OLD/'prepared.json').read_text())['resources'] if r['resource']==c.COMMON)['output_sha256'])
 def test_gate_rejects_installed_but_shadowed_resources(self):
  check=load('verify-menu-visual-install')
  self.assertEqual(check.mismatches({'common':'new'},{'common':'old'}),[dict(resource='common',expected='new',actual='old')])
  self.assertEqual(check.mismatches({'common':'new'},{'common':'new'}),[])
 def test_shared_header_authored_layout_and_gentium_baseline(self):
  text=b.patch.one_file(c.OUT/'movies/panel_common/after/scripts','TopBarNew').read_text(encoding='utf-8-sig')
  for item in ['this.mcTabList.alpha = 0','this.inkMedallion(','tf.textWidth','tf.getLineMetrics(0).ascent','qfMenuPadIcon']:
   self.assertIn(item,text)
  self.assertNotIn('baseline - size * 0.93',text);self.assertNotIn('.iaiPadIcon()',text)
 def test_shared_art_protocol_and_all_dispatched_keys_have_cache_entries(self):
  common=b.patch.one_file(c.OUT/'movies/panel_common/after/scripts','MenuCommon').read_text(encoding='utf-8-sig')
  self.assertIn('path.indexOf("inkart:")',common)
  self.assertIn('img://icons/inkiron/bgart/',common)
  cache={r['resource'] for r in b.m.b.inventory.cache_entries(b.REF/'mods/modInkAndIronUI/content/texture.cache')}
  self.assertEqual(len(cache),24)
  script=(b.SCRIPTS/'vendor/inkironui_bgart.ws').read_text(encoding='utf-8')
  for key in re.findall(r'return "(\w+)";',script):self.assertIn('gameplay/gui_new/icons/inkiron/bgart/'+key+'.png',cache)
  self.assertIn('wrappedMethod( MenuName, MenuState );',script)
 def test_37_v1_movies_and_all_existing_scripts_options_cache_unchanged(self):
  old=json.loads((c.OLD/'prepared.json').read_text())
  for row in old['resources']:
   if row['resource']!=c.COMMON:self.assertEqual((c.OLD/'prepared-inputs'/row['resource']).read_bytes(),(c.OUT/'prepared-inputs'/row['resource']).read_bytes())
  prior=json.loads((c.OLD/'receipt.json').read_text())['members']
  for name,sha in prior.items():
   if not name.endswith(('blob0.bundle','metadata.store')):self.assertEqual(self.receipt['members'][name],sha)
 def test_missing_auxiliary_menu_movies_present_without_font_library_replacement(self):
  for key in c.EXTRAS:self.assertIn(key,self.prepared['keys'])
  self.assertEqual(len(self.prepared['keys']),40)
  for key in self.prepared['keys']:
   self.assertNotIn('/hud/',key);self.assertNotIn('/overlay/',key);self.assertNotIn('/witcher3/',key);self.assertNotIn('fonts.xml',key)
 def test_current_live_snapshot_and_compiled_scripts_unchanged(self):
  self.assertEqual(b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS),json.loads((c.OUT/'frozen.json').read_text()))
  scripts=json.loads((b.SCRIPTS/'receipt.json').read_text())
  for name,sha in scripts['source_hashes'].items():self.assertEqual(b.m.b.fallback.sha(b.SCRIPTS/'vendor'/name),sha)
  self.assertEqual(scripts['results'][0]['warnings'],scripts['results'][1]['warnings'])
  for result in scripts['results']:
   self.assertEqual(b.m.b.fallback.sha(b.SCRIPTS/result['label']/'blob.rsblob'),result['blob_sha256'])
 def test_common_exports_fonts_and_upstream_methods_retained(self):
  old=(c.OLD/'prepared-inputs'/c.COMMON).read_bytes();new=(c.OUT/'prepared-inputs'/c.COMMON).read_bytes()
  before=b.m.b.audit.swf_tags(old)[2];after=b.m.b.audit.swf_tags(new)[2]
  self.assertEqual(b.m.b.contracts.symbols(before),b.m.b.contracts.symbols(after))
  # Font definition/import tags remain exact: no embedded replacement family.
  font_tags={10,13,48,57,62,75,88,91}
  self.assertEqual([(code,data) for code,data in before if code in font_tags],[(code,data) for code,data in after if code in font_tags])
  name='TopBarNew';a=b.patch.one_file(c.OLD/'movies/panel_common/after/scripts',name).read_text(encoding='utf-8-sig');z=b.patch.one_file(c.OUT/'movies/panel_common/after/scripts',name).read_text(encoding='utf-8-sig')
  self.assertEqual(a.replace('tf.y = baseline - size * 0.93 - 2;','tf.y = baseline - tf.getLineMetrics(0).ascent - 2;'),z)
 def test_optional_art_is_exact_author_archive_and_collision_scope_recorded(self):
  self.assertEqual(len(self.prepared['optional']),2)
  with zipfile.ZipFile(self.receipt['zip_path']) as release:
   for row in self.prepared['optional']:
    self.assertEqual(b.m.b.fallback.sha(Path(row['archive'])),row['sha256'])
    self.assertGreater(row['cache_entries'],0)
    with zipfile.ZipFile(row['archive']) as upstream:
     for name in upstream.namelist():self.assertEqual(upstream.read(name),release.read('Mods/'+name[5:]))
 def test_native_zero_error_pipeline_and_exact_reextraction(self):
  self.assertEqual({r['label'] for r in self.receipt['native'] if r['passed']},{'cook','validate','pack','metadata'})
  log=(c.OUT/'native-final/validate.full.log').read_text(errors='replace')
  self.assertIn('Errors found in 0 resources:',log)
  for e in b.m.b.audit.entries(c.OUT/'packed/blob0.bundle'):
   self.assertEqual(b.m.b.bars.extract(c.OUT/'packed/blob0.bundle',e['resource']),(c.OUT/'prepared-inputs'/e['resource']).read_bytes())
if __name__=='__main__':unittest.main()
