"""Scoped native contract/algorithm checks; cannot establish runtime fidelity."""
import importlib.util,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class UnifiedInventory(unittest.TestCase):
    def test_authored_pool_selection_and_pad_algorithms(self):
        result=load('verify-approved-inventory').algorithm_checks()
        self.assertEqual(result['pooled_instances'],9);self.assertEqual(result['unchanged_icon_reloads'],0)
        self.assertEqual(result['category_cases'],21)
    def test_geometry_at_supported_viewports(self):
        self.assertEqual(len(load('verify-approved-inventory').geometry_checks()),4)
    def test_exact_baseline_and_frozen_classes(self):
        b=load('build-approved-inventory');d=json.loads((b.OUT/'prepared.json').read_text());after=Path(d['abc'])/'after/scripts'
        self.assertEqual(b.sha(b.BASE/'prepared-inputs'/b.KEY),b.gate.V4_SHA)
        for name in ('SlotPaperdoll','ItemDataStub','ModuleInputFeedback','InputFeedbackButton','CharacterRendererController'):
            self.assertEqual(b.gate.one(name).read_bytes(),next(after.rglob(name+'.as')).read_bytes())
    def test_script_uses_native_eligibility_actions_and_typed_identity(self):
        s=(ROOT/'src/inventory/unified/approvedInventory.ws').read_text()
        for token in ('ShouldShowItem(items[i])','previous = _playerInv.GetFilterType()','SetFilterType(previous)','GetAllItems(items)','CreateFlashObject("red.game.witcher3.menus.common.ItemDataStub")','wrappedMethod(itemId,flashObject)','GetTooltipData(item,_currentInv==_shopInv,true)'):
            self.assertIn(token,s)
        for api in ('EquipItem(','ConsumeItem(','ReadBook(','RemoveItem('):
            self.assertNotIn('_inv.'+api,s)
    def test_disabled_review_and_single_footer(self):
        scene=(ROOT/'src/inventory/unified/Scene.asinc').read_text();s=(ROOT/'src/inventory/unified/approvedInventory.ws').read_text()
        self.assertIn('"Review","Weapons","Armor"',scene);self.assertIn('"Not enabled"',scene)
        self.assertNotIn('new InputFeedbackButton',scene);self.assertNotIn('Inspect I /',scene)
        self.assertIn('UpdateGFxButtons(m_GFxInputBindings,true)',s)
    def test_stale_payload_and_competing_presentation_gates(self):
        p=load('patch-approved-inventory');root=p.menu(p.ROOT.joinpath('build/adaptive-inventory-v2-p1/before/scripts/red/game/witcher3/menus/inventory_menu/MenuInventory.as').read_text(encoding='utf-8-sig'))
        self.assertIn('int(payload.aiRequestSerial)!=aiRequestSerial',root)
        self.assertIn('if(aiActive){aiTick();return;}',root)
        a,z=p.p.trace.body_span(root,'override public function setCurrentModule(')
        self.assertLess(root[a:z].index('if(aiActive)'),root[a:z].index('selectedIndex = -1'))
        grid=p.grid(p.ROOT.joinpath('build/adaptive-inventory-v2-p1/before/scripts/red/game/witcher3/slots/SlotsListGrid.as').read_text(encoding='utf-8-sig'))
        a,z=p.p.trace.body_span(grid,'public function processOver(')
        self.assertLess(grid[a:z].index('if(aiRows)'),grid[a:z].index('this.addRow()'))
        self.assertIn('event.currentTarget!=_imageLoader',p.slot(p.ROOT.joinpath('build/adaptive-inventory-v2-p1/before/scripts/red/game/witcher3/slots/SlotBase.as').read_text(encoding='utf-8-sig')))
    def test_candidate_and_control_compiler_receipt(self):
        b=load('build-approved-inventory');d=json.loads(b.COMPILER.read_text())
        # Historical release receipt does not validate subsequent diagnostic edits.
        import zipfile,hashlib
        with zipfile.ZipFile(b.DEPLOY/'Approved-Inventory-Unified-P1-private.zip') as z:
            released=z.read('Mods/modApprovedInventoryUnifiedP1/content/scripts/local/approvedInventory.ws')
        self.assertEqual(d['source_sha256'],hashlib.sha256(released).hexdigest());self.assertEqual([x['exit_code'] for x in d['results']],[0,0])
        self.assertEqual(d['results'][0]['warnings'],d['results'][1]['warnings'])
    def test_tick_has_no_allocation_or_layout_rebuild(self):
        p=load('patch-approved-inventory');src=(ROOT/'src/inventory/unified/Scene.asinc').read_text();a,z=p.p.trace.body_span(src,'protected function aiTick(')
        body=src[a:z]
        for token in ('new Sprite','cleanup','aiArrange','aiSetItems','aiPresent','aiPaintRail'):
            self.assertNotIn(token,body)
    def test_native_tab_offstage_negative_control(self):
        r=load('diagnose-approved-inventory').regression()
        self.assertEqual(r['native_dispatches'],7);self.assertFalse(r['game_execution'])
    def test_native_delayed_subdata_writer_is_scoped(self):
        p=load('patch-approved-inventory');module=(ROOT/'src/inventory/unified/Module.asinc').read_text()
        a,z=p.p.trace.body_span(module,'override protected function updateSubData(')
        body=module[a:z]
        self.assertLess(body.index('if(aiModuleBase)'),body.index('super.updateSubData(index)'))
        native=next((ROOT/'build/adaptive-inventory-v2-p1/before/scripts').rglob('TabbedScrollingListModule.as')).read_text(encoding='utf-8-sig')
        a,z=p.p.trace.body_span(native,'protected function updateSubData(')
        self.assertIn('targetUIComponent.alpha = 0',native[a:z]);self.assertIn('GTweener.to(targetUIComponent',native[a:z])
        core=next((ROOT/'build/adaptive-inventory-v2-p1/before/scripts').rglob('CoreList.as')).read_text(encoding='utf-8-sig')
        self.assertIn('clip = parent.getChildByName(value + i)',core)
        self.assertIn('aiModuleBase.tabParking.addChild(parked.tab)',module)
        self.assertLess(module.index('tabsSaved.push'),module.index('for each(var parked:Object'))
        inventory_symbol=next((ROOT/'build/adaptive-inventory-v2-p1/before/scripts').rglob('InventoryGridRef.as')).read_text(encoding='utf-8-sig')
        self.assertIn('mcTabList.itemRendererInstanceName = "mcTabListItem"',inventory_symbol)
        self.assertIn('saved.parent.addChildAt(saved.tab',module)
    def test_diagnostics_cover_init_before_refresh_and_keep_native_asset_owner(self):
        scene=(ROOT/'src/inventory/unified/Scene.asinc').read_text();ws=(ROOT/'src/inventory/unified/approvedInventory.ws').read_text()
        self.assertIn('RuntimeAssetsManager.getInstanse().getAsset("ItemTooltipRef_mouse")',scene)
        self.assertIn('if(!RuntimeAssetsManager.getInstanse().isLoaded)return',scene)
        self.assertIn('catch(error:Error)',scene)
        self.assertNotIn('drawRect(0,115,1920,850)',scene)
        self.assertLess(ws.index('GetMemberFlashFunction("approvedDiagnostics")'),ws.index('GetMemberFlashFunction("approvedEnabled")'))
    def test_private_diagnostic_binary_and_script_pins_when_available(self):
        b=load('build-approved-inventory');out=ROOT/'build/approved-inventory-runtime-diagnostic'
        if (ROOT/'build/approved-inventory-runtime-diagnostic-r3/receipt.json').exists():out=ROOT/'build/approved-inventory-runtime-diagnostic-r3'
        if not (out/'receipt.json').exists():self.skipTest('Private diagnostic assets not available')
        d=json.loads((out/'receipt.json').read_text());source=(b.BASE/'prepared-inputs'/b.KEY).read_bytes();data=(out/'prepared-inputs'/b.KEY).read_bytes()
        native=b.b.b.m.b.font.native
        self.assertEqual([c['tail'] for c in native.chunks(source)[1:]],[c['tail'] for c in native.chunks(data)[1:]])
        self.assertTrue(all(c['crc_valid'] for c in native.chunks(data)))
        self.assertEqual(b.sha(b.SCRIPT),d['annotation_sha256'])
        self.assertEqual(b.sha(Path(d['zip_path'])),d['zip_sha256'])
        after=Path(d['abc'])/'after/scripts'
        for name in ('SlotPaperdoll','ItemDataStub','RuntimeAssetsManager','CharacterRendererController','ModuleInputFeedback'):
            self.assertEqual(b.gate.one(name).read_bytes(),next(after.rglob(name+'.as')).read_bytes())
        self.assertFalse(d['native_candidate_validated']);self.assertFalse(d['game_execution'])
if __name__=='__main__':unittest.main()
