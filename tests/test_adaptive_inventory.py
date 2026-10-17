"""Targeted offline gates. These do not execute the game's Scaleform player."""
import importlib.util, json, re, shutil, subprocess, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('adaptive_build',ROOT/'tools/build-adaptive-inventory.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
OUT=b.OUT

class AdaptiveInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=json.loads((OUT/'receipt.json').read_text())
    def source(self,name,after=True):
        return b.old.unique(OUT/('after' if after else 'before')/'scripts',name+'.as').read_text(encoding='utf-8-sig')
    def body(self,name,sig,after=True):
        text=self.source(name,after);a,z=b.p.p.trace.body_span(text,sig);return text[a+1:z]
    def test_accepted_v4_is_the_exact_movie_input(self):
        data=(b.BASE/'prepared-inputs'/b.KEY).read_bytes()
        self.assertEqual(b.b.m.b.audit.sha(data),self.receipt['input_sha256'])
        self.assertEqual(b.b.m.r.p.movie(data)[1],(OUT/'before/source.gfx').read_bytes())
    def test_only_eight_expected_classes_and_no_art_changes(self):
        self.assertEqual(set(self.receipt['changed_classes']),set(b.p.TRANSFORMS))
        a=(b.BASE/'prepared-inputs'/b.KEY).read_bytes();z=(OUT/'prepared-inputs'/b.KEY).read_bytes()
        self.assertEqual([(c,d) for c,d in b.b.m.b.audit.swf_tags(a)[2] if c!=82],[(c,d) for c,d in b.b.m.b.audit.swf_tags(z)[2] if c!=82])
        self.assertEqual([c['tail'] for c in b.b.m.b.font.native.chunks(a)[1:]],[c['tail'] for c in b.b.m.b.font.native.chunks(z)[1:]])
        self.assertTrue(all(c['crc_valid'] for c in b.b.m.b.font.native.chunks(z)))
    def test_hoods_dye_contract_remains_exact(self):
        for name in ('SlotPaperdoll','ItemDataStub'):
            self.assertEqual(self.source(name),self.source(name,False))
        self.assertIn('slotData.isDyeable',self.body('SlotPaperdoll','public function canDrop('))
    def test_original_public_and_protected_exports_retained(self):
        for name in b.p.TRANSFORMS:
            old=re.findall(r'(?:public|protected) function [^\n]+',self.source(name,False))
            new=re.findall(r'(?:public|protected) function [^\n]+',self.source(name))
            self.assertTrue(set(old)<=set(new),name)
    def test_scoped_player_gear_gate_and_full_restore(self):
        refresh=self.body('MenuInventory','protected function qfAdaptiveRefresh(')
        self.assertIn('this._inventoryMode == IMS_Player',refresh)
        self.assertIn('qfAdaptiveContext() == "Gear"',refresh)
        restore=self.body('MenuInventory','protected function qfAdaptiveRestore(')
        for code in ('qfGearRestore()','this.qfAdaptiveBase.sx','this.qfAdaptiveBase.rsx','removeEventListener','this.qfAdaptiveTip.visible = true'):
            self.assertIn(code,restore)
        self.assertIn('!this.qfAdaptivePlayer',self.body('InventoryTabbedListModule','protected function qfAdaptiveRecall('))
    def test_equipped_ids_use_native_filters_no_shadow_items(self):
        script=(ROOT/'src/inventory/inkGearGrid.ws').read_text()
        self.assertIn('result = wrappedMethod(item);',script)
        self.assertIn('qfGearListing = previous;',script)
        self.assertIn('m_tagsFilter.Size() == 0',script)
        self.assertIn('InventoryUpdateItem(item)',script)
        self.assertIn('OnUnequipItem(currentItemId, -1)',script)
        self.assertEqual(b.b.m.b.fallback.sha(ROOT/'src/inventory/inkGearGrid.ws'),self.receipt['compiler']['source_sha256'])
    def test_update_selection_tracks_item_identity_including_index_zero(self):
        for sig in ('override public function updateItems(','override public function updateItemData('):
            body=self.body('SlotsListGrid',sig)
            self.assertLess(body.index('qfSavedSlot'),body.index('selectedIndex = -1'))
            self.assertIn('getIdIndex(uint(qfSavedId))',body)
            self.assertIn('scrollPosition = qfSavedScroll',body)
        # Native deduplication is retained, rather than adding duplicate renderers.
        self.assertEqual(self.body('SlotsListGrid','protected function appendItemData('),self.body('SlotsListGrid','protected function appendItemData(',False))
    def test_dpad_taps_duplicate_down_and_hold_gate_execute(self):
        node=shutil.which('node')
        self.assertIsNotNone(node,'Node required to execute the pure input gate')
        body=self.body('SlotBase','public static function qfGearPadAllow(')
        body=re.sub(r'var (\w+):\w+',r'var \1',body)
        code='var qfGearGrid=true,qfGearHeld={},qfGearDown={},qfGearFire={};function allow(d,now){'+body+'}\n'
        events=[('keyDown',0),('keyDown',1),('keyHold',100),('keyHold',399),('keyHold',400),('keyHold',420),('keyHold',509),('keyHold',510),('keyUp',515),('keyDown',600)]
        code+='console.log(JSON.stringify('+json.dumps(events)+'.map(e=>allow({code:142,value:e[0]},e[1]))));'
        result=json.loads(subprocess.check_output([node,'-e',code],text=True))
        self.assertEqual(result,[True,False,False,False,True,False,False,True,True,True])
    def test_viewport_updates_scroll_page_and_restores_native_values(self):
        viewport=self.body('SlotsListGrid','public function qfAdaptiveViewport(')
        self.assertRegex(viewport,r'this\._rows = (?:uint\()?h / this\._gridSquareSize\)?')
        self.assertIn('protected var _rows:uint;',self.source('SlotsListGrid'))
        for token in ('this._gridRenderHeight = h','this._rows = this.qfAdaptiveViewportBase.rows','this.updateRendererBounds()','this.updateScrollBar()'):
            self.assertIn(token,viewport)
        self.assertEqual(self.body('SlotsListGrid','protected function updateScrollBar(').replace('Number(NaN)','NaN'),self.body('SlotsListGrid','protected function updateScrollBar(',False).replace('Number(NaN)','NaN'))
        module=self.body('InventoryTabbedListModule','public function qfAdaptiveViewport(')
        self.assertIn('this.maskClip.height = 384 + this.gridMaskOffset',module)
        self.assertIn('this.mcPlayerGrid.qfAdaptiveViewport(0)',module)
    def test_native_payload_summary_projection_executes_with_and_without_equipment(self):
        body=self.body('TooltipInventory','public function qfAdaptiveSummary(')
        body=re.sub(r'var (\w+):\w+',r'var \1',body)
        body=re.sub(r'for each\(var (\w+) in (\w+)\)',r'for(var \1 of (\2 || []))',body)
        body=body.replace(' as Array','')
        body=re.sub(r'([\w.]+) is Array',r'Array.isArray(\1)',body)
        code='var _data;var view={iaiCmpPlain:v=>String(v||""),iaiCmpPrim:o=>o.PrimaryStatValue?String(o.PrimaryStatValue):"",summary:function(){'+body+'}};'
        payload={'ItemName':'Long sword','PrimaryStatLabel':'Damage','PrimaryStatValue':110,'PrimaryStatDiffStr':'<font color="#70A070">+10</font>','RequiredLevel':'Level 5','SocketsList':[{},{}],'StatsList':[{'id':1,'name':'Critical chance','value':'+5%'}],'equippedItemData':{'PrimaryStatValue':100,'SocketsList':[{}],'StatsList':[{'id':1,'name':'Critical chance','value':'+3%'}]}}
        code+='_data='+json.dumps(payload)+';var a=view.summary();delete _data.equippedItemData;var b=view.summary();_data=null;console.log(JSON.stringify([a,b,view.summary()]));'
        results=json.loads(subprocess.check_output([shutil.which('node'),'-e',code],text=True))
        self.assertIn('110    /    100 equipped',results[0][1]);self.assertIn('+10</font>',results[0][1])
        self.assertIn('Sockets 2 / 1 equipped',results[0][2]);self.assertIn('+5%    /    +3% equipped',results[0][3])
        self.assertNotIn('equipped',results[1][1]);self.assertEqual(results[2],[])
    def test_inspect_preserves_native_sort_binding_and_restores_key_up(self):
        text=self.body('MenuInventory','protected function qfAdaptiveInput(')
        self.assertIn('KeyCode.PAD_BACK_SELECT',text)
        self.assertNotIn('KeyCode.PAD_RIGHT_THUMB',text)
        self.assertLess(text.index('delete this.qfAdaptiveHeld'),text.index('var inspect:'))
        self.assertIn('wasHeld',text)
        inspect=self.body('MenuInventory','protected function qfAdaptiveToggleInspect(')
        self.assertNotIn('selectedIndex =',inspect)
        self.assertNotIn('scrollPosition =',inspect)
        self.assertEqual(self.body('MenuInventory','override protected function handleInputNavigate('),self.body('MenuInventory','override protected function handleInputNavigate(',False))
    def test_context_summary_uses_native_values_and_full_details_unchanged(self):
        summary=self.body('TooltipInventory','public function qfAdaptiveSummary(')
        for token in ('equippedItemData','PrimaryStatDiffStr','SocketsList','RequiredLevel','StatsList'):
            self.assertIn(token,summary)
        for sig in ('protected function iaiCmpBlock(','override public function set data(','protected function createComparisonTooltip('):
            before=self.body('TooltipInventory',sig,False);after=self.body('TooltipInventory',sig)
            if sig == 'protected function createComparisonTooltip(':
                # FFDec inverts this empty field-only condition. Both read the
                # same field once; neither branch performs an operation.
                empty=r'if\(!?tooltipData\.EquippedTitle\)\s*\{\s*\}'
                self.assertEqual(len(re.findall(empty,before)),1)
                self.assertEqual(len(re.findall(empty,after)),1)
                before=re.sub(empty,'',before);after=re.sub(empty,'',after)
            self.assertEqual(after,before)
        details=self.body('TooltipInventory','public function qfAdaptiveDetails(')
        self.assertIn('iaiEqCard = iaiScrOn = on',details)
        self.assertIn('this.populateData()',details)
        self.assertIn('this.iaiScrOff()',details)
        self.assertIn('this.qfAdaptiveTip.iaiScrBy',self.body('MenuInventory','protected function qfAdaptiveInput('))
    def test_auxiliary_native_twenty_slots_and_empty_cells(self):
        body=self.body('ModulePaperdoll','public function qfGearReflow(')
        self.assertIn('gear.concat(utility)',body)
        self.assertIn('targetMode ? gear.concat(utility) : []',body)
        self.assertIn('136 + i % 5 * 100',body)
        self.assertIn('qfGearGrid && empty && !sel',self.body('SlotBase','protected function iaiDrawLess('))
    def test_script_compiler_control_and_candidate_match(self):
        a,z=self.receipt['compiler']['results']
        self.assertEqual(a['exit_code'],0);self.assertEqual(z['exit_code'],0)
        self.assertEqual(a['warnings'],z['warnings']);self.assertEqual(a['assertions'],z['assertions'])
    def test_one_resource_zip_exact_extraction_and_metadata(self):
        path=Path(self.receipt['zip_path'])
        self.assertEqual(b.b.m.b.fallback.sha(path),self.receipt['zip_sha256'])
        with zipfile.ZipFile(path) as z:
            self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),3)
            self.assertEqual({n:b.b.m.b.audit.sha(z.read(n)) for n in z.namelist()},self.receipt['members'])
        bundle=OUT/'packed/blob0.bundle';entries=list(b.b.m.b.audit.entries(bundle));self.assertEqual([e['resource'] for e in entries],[b.KEY])
        self.assertEqual(b.b.m.b.bars.extract(bundle,b.KEY),(OUT/'prepared-inputs'/b.KEY).read_bytes())
        md=b.meta.parse((OUT/'packed/metadata.store').read_bytes())
        self.assertEqual(b.meta.write(b.meta.replace_single(md,bundle)),(OUT/'packed/metadata.store').read_bytes())
    def test_honest_native_status_and_unchanged_live_inputs(self):
        passed={r['label'] for r in self.receipt['native_commands'] if r['passed']}
        self.assertEqual(self.receipt['native_complete'],passed=={'cook','validate','pack','metadata'})
        if not self.receipt['native_complete']:
            self.assertFalse(self.receipt['reconstruction']['native_candidate_validated'])
            self.assertTrue(self.receipt['reconstruction']['independent_changed_bundle_and_metadata_exact'])
        self.assertEqual(b.frozen(),self.receipt['frozen_inputs'])
        self.assertEqual(b.v4_files(),json.loads((OUT/'accepted-v4-files.json').read_text()))

if __name__=='__main__':unittest.main()
