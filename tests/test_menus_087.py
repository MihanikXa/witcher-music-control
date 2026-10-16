"""Targeted migration contracts, not in-game navigation certification."""
import copy,importlib.util,json,re,unittest,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-menus-087.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
E=b.E
class MigrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.ledger=json.loads((E/'ledger.json').read_text());cls.prepared=json.loads((b.OUT/'prepared.json').read_text())
 def test_all_menu_ui_keys_are_actual_086_bytes_in_087(self):
  a=self.ledger['versions']['0.8.6']['resources'];c=self.ledger['versions']['0.8.7']['resources']
  for key,row in c.items():
   if row['module']=='UI':self.assertEqual(row['sha256'],a[key]['sha256'],key)
 def test_no_hud_font_library_overlay_or_gear_layout_packaged(self):
  for key in self.prepared['keys']:
   self.assertNotIn('/hud/',key);self.assertNotIn('/witcher3/',key);self.assertFalse(key.endswith('fonts.xml'));self.assertNotIn('/overlay/',key)
  self.assertNotIn('panel_character_perks.redswf',str(self.prepared['keys']))
  source=(b.SCRIPTS/'vendor').glob('*.ws')
  for p in source:self.assertNotIn('qfGear',p.read_text(encoding='utf-8'))
 def test_hoods_dye_rule_is_exact_official_body(self):
  official=b.patch.one_file(ROOT/'reference/ink-and-iron-0.8.6/inventory-source/hoods-export/scripts','SlotPaperdoll').read_text(encoding='utf-8-sig')
  after=b.patch.one_file(b.OUT/'movies/panel_inventory/after/scripts','SlotPaperdoll').read_text(encoding='utf-8-sig')
  _,a,z=b.patch.body(official,'canDrop');_,c,y=b.patch.body(after,'canDrop');self.assertEqual(official[a+1:z],after[c+1:y])
  data=b.patch.one_file(b.OUT/'movies/panel_inventory/after/scripts','ItemDataStub').read_text(encoding='utf-8-sig');self.assertEqual(data.count('var isDyeable:Boolean'),1)
 def test_outfit_wheel_exports_events_and_private_helpers_retained(self):
  before=b.patch.one_file(E/'installed-export/panel_common/scripts','MenuCommon').read_text(encoding='utf-8-sig');after=b.patch.one_file(b.OUT/'movies/panel_common/after/scripts','MenuCommon').read_text(encoding='utf-8-sig')
  for name in re.findall(r'function ((?:OW|ow)\w+)\(',before):
   self.assertRegex(after,r'function '+name+r'\(')
  self.assertIn('path.indexOf("inkart:")',after)
  for name in re.findall(r'GameEvent\.CALL,"(OnOW\w+)"',before):self.assertIn('"'+name+'"',after)
 def test_smooth_map_timer_preserves_installed_algorithm(self):
  current=(E/'installed-export/panel_worldmap/scripts/red/game/witcher3/menus/worldmap/HubMap.as').read_text(encoding='utf-8-sig')
  patched=(b.OUT/'movies/panel_worldmap/abc/HubMap.as').read_text(encoding='utf-8')
  current=current.replace('_smLastScrollTime','inkLastPanTime').replace('_smZoomAccum','inkZoomAccum')
  _,a,z=b.patch.body(current,'handleScrollAndZoomTimer');_,c,y=b.patch.body(patched,'handleScrollAndZoomTimer');self.assertEqual(current[a+1:z],patched[c+1:y])
  self.assertIn('SHOW_INTERVAL:* = 1;',patched);self.assertNotIn('_smZoomAccum',patched)
 def test_no_undefined_footer_identifier_and_upstream_button_helpers_survive(self):
  for row in self.prepared['resources']:
   folder=b.OUT/'movies'/Path(row['resource']).stem
   for p in (folder/'after/scripts').rglob('ModuleInputFeedback.as'):
    t=p.read_text(encoding='utf-8-sig')
    if 'buttonsSize' in t:
     _,a,z=b.patch.body(t,'repositionButtons');self.assertIn('var buttonsSize:Number',t[a+1:z])
    self.assertNotIn('this._cachedWidth > 0 && buttonsSize > this._cachedWidth',t)
   for p in (folder/'abc').glob('InputFeedbackButton.as'):
    t=p.read_text(encoding='utf-8');self.assertIn('qfXboxScaleX * 0.6875',t)
    original=list((E/'0.8.7-export'/folder.name/'scripts').rglob('InputFeedbackButton.as'))
    if original and 'iaiPadIcon' in original[0].read_text(encoding='utf-8-sig'):self.assertIn('function iaiPadIcon',t)
 def test_header_does_not_require_missing_rc2_renderer_helper(self):
  provider=b.patch.one_file(E/'installed-export/hud/scripts','InputFeedbackButton').read_text(encoding='utf-8-sig');self.assertNotIn('function iaiPadIcon',provider)
  header=b.patch.one_file(b.OUT/'movies/panel_common/after/scripts','TopBarNew').read_text(encoding='utf-8-sig')
  self.assertNotIn('.iaiPadIcon()',header);self.assertIn('qfMenuPadIcon(this.mcLeftGamepadButton)',header);self.assertIn('qfMenuPadIcon(btn)',header);self.assertIn('"mcIconXbox"',header)
 def test_older_renderer_hold_models_are_adapted_without_replacing_them(self):
  for stem,condition in [('panel_inventorysockets','this.tfHoldPrefix.visible'),('panel_preparation','this._holdDuration > 0')]:
   old=b.patch.one_file(b.OUT/'movies'/stem/'before/scripts','InputFeedbackButton').read_text(encoding='utf-8-sig');self.assertIn(condition,old)
   new=b.patch.menu_button(old);self.assertEqual(new,(b.OUT/'movies'/stem/'abc/InputFeedbackButton.as').read_text(encoding='utf-8'));self.assertIn('Math.abs(this._gpadIcon.scaleX)',new)
 def test_glyphs_are_same_accepted_direct_vector_paths_with_small_letters(self):
  font=b.m.FONT;name='exported.ICO_Xbox_A';base=b.hotfix.original_paths(name,64,64,font);small=b.hotfix.small_paths(name,64,64,font)
  self.assertEqual(base[:2],small[:2]);self.assertEqual(base[2][0],small[2][0])
  for (kind,points),(newkind,newpoints) in zip(base[2][1],small[2][1]):
   self.assertEqual(kind,newkind)
   for i,(old,new) in enumerate(zip(points,newpoints)):self.assertAlmostEqual(new,32+(old-32)*0.8)
 def test_font_aliases_resolve_same_english_library(self):
  old=ET.fromstring((E/'installed/gameplay/gui_new/fonts.xml').read_bytes()).find("lang[@name='EN']")
  upstream=ET.fromstring((E/'0.8.7/gameplay/gui_new/fonts.xml').read_bytes()).find("lang[@name='EN']")
  vanilla_alias=ET.fromstring((E/'0.8/gameplay/gui_new/fonts.xml').read_bytes()).find("lang[@name='EN']")
  self.assertEqual(old.attrib,upstream.attrib)
  self.assertEqual([(n.tag,n.attrib) for n in old],[(n.tag,n.attrib) for n in vanilla_alias])
  self.assertEqual({n.tag for n in old},{n.tag for n in upstream})
 def test_existing_hud_options_unchanged_and_menu_vars_unique(self):
  receipt=json.loads((b.SCRIPTS/'receipt.json').read_text());old=ET.parse(receipt['options_base_path']).getroot();new=ET.parse(b.SCRIPTS.parent/'options/modInkIronHUDBatch.xml').getroot()
  ids=[n.get('id') for n in new.findall('.//Var')];self.assertEqual(len(ids),len(set(ids)))
  for node in old.findall('.//Var'):
   other=next(n for n in new.findall('.//Var') if n.get('id')==node.get('id'));a=copy.deepcopy(node);c=copy.deepcopy(other);a.tail=c.tail=None;self.assertEqual(ET.tostring(a),ET.tostring(c))
 def test_compiler_control_diagnostics_match(self):
  rows=json.loads((b.SCRIPTS/'receipt.json').read_text())['results'];self.assertEqual([r['exit_code'] for r in rows],[0,0]);self.assertEqual(rows[0]['warnings'],rows[1]['warnings']);self.assertEqual(rows[0]['assertions'],rows[1]['assertions'])
 def test_original_exports_atlases_and_crcs(self):
  for row in self.prepared['resources']:
   key=row['resource'];data=(b.OUT/'prepared-inputs'/key).read_bytes();original=Path(self.ledger['versions']['0.8.7']['resources'][key]['path']).read_bytes()
   self.assertEqual(b.m.b.contracts.symbols(b.m.b.audit.swf_tags(data)[2]),b.m.b.contracts.symbols(b.m.b.audit.swf_tags(original)[2]));b.atlas.validate(data)
   font_tags=lambda blob:[(c,p) for c,p in b.m.b.audit.swf_tags(blob)[2] if c in (48,57,71,75,88,91)]
   self.assertEqual(font_tags(data),font_tags(original),key)
 def test_menu_art_cache_has_no_live_overlap_and_all_background_keys(self):
  report=json.loads((b.OUT/'texture-cache-check.json').read_text());self.assertFalse(report['collisions']);self.assertEqual(report['entries'],24)
  keys={r['resource'] for r in b.m.b.inventory.cache_entries(b.REF/'mods/modInkAndIronUI/content/texture.cache')}
  text=b.patch.one_file(E/'0.8.7-export/panel_common/scripts','MenuCommon').read_text(encoding='utf-8-sig');part=text.split('INKBG_ART_BOX:Object = {',1)[1].split('};',1)[0]
  for name in re.findall(r'"([\w]+)":\[',part):self.assertIn('gameplay/gui_new/icons/inkiron/bgart/'+name+'.png',keys)
 def test_native_pack_extraction_and_live_baseline_frozen(self):
  receipt=json.loads((b.OUT/'receipt.json').read_text());self.assertEqual({r['label'] for r in receipt['native'] if r['passed']},{'cook','validate','pack','metadata'})
  for key in self.prepared['keys']:self.assertEqual(b.m.b.bars.extract(b.OUT/'packed/blob0.bundle',key),(b.OUT/'prepared-inputs'/key).read_bytes())
  self.assertEqual(b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS),self.ledger['frozen'])
  with zipfile.ZipFile(receipt['zip_path']) as z:self.assertIsNone(z.testzip());self.assertFalse(any('inkGearGrid' in n for n in z.namelist()))
if __name__=='__main__':unittest.main()
