"""P2 topology/data contracts; no claim of Scaleform or screenshot acceptance."""
import importlib.util,json,re,subprocess,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('buildp2',ROOT/'tools/build-inventory-p2.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def body(text,sig):
    a,z=b.p.p.trace.body_span(text,sig);return text[a+1:z]
def js_types(text):return re.sub(r'var (\w+):[\w*]+',r'var \1',text)
def runjs(code):return json.loads(subprocess.check_output(['node','-e',code],text=True,encoding='utf-8'))
class P2Preflight(unittest.TestCase):
    def test_sparse_dense_geometry_and_reachable_last_row(self):
        cases=b.proof.fixtures();b.proof.verify_cases(cases)
        self.assertEqual(len(cases),24)
        self.assertEqual({c['coordinatePolicy'] for c in cases},{'authored-fit','viewport-aspect'})
        self.assertEqual({c['count'] for c in cases},{6,24,80})
    def test_native_first_fit_spans_sections_without_duplicate_or_overlap(self):
        original=b.b.old.unique(b.BEFORE/'scripts','SlotsListGrid.as').read_text(encoding='utf-8-sig')
        valid=re.sub(r' as \w+','',js_types(body(b.p.grid(original),'protected function isItemPlaceValid(')))
        native='var _renderers=[];const grid={_columns:3,getItemSection:()=>null,getColumn:i=>i%3,valid:function(rendererIdx,size,sectionId=-1){'+valid+'}};'
        code=native+'''const out=[];for(const size of [2,2,2,1,1,2]){
          let at=0;while(!grid.valid(at,size,at%2))at++;
          while(_renderers.length<=at+3)_renderers.push({empty:true,uplink:null,isEmpty(){return this.empty;}});
          _renderers[at].empty=false;if(size>1){_renderers[at+3].empty=false;_renderers[at+3].uplink=at;}
          out.push({index:at,size});
        }console.log(JSON.stringify(out));'''
        placements=runjs(code);occupied=set()
        for item in placements:
            cells=[item['index']]+([item['index']+3] if item['size']==2 else [])
            self.assertFalse(set(cells)&occupied);occupied.update(cells)
        self.assertEqual(len(placements),6);self.assertLess(max(occupied),12)
    def test_payload_routes_by_native_item_id_without_tooltip(self):
        original=b.b.old.unique(b.BEFORE/'scripts','ContextInfoManager.as').read_text(encoding='utf-8-sig')
        receiver=body(b.p.context(original),'public function dataReceiver(')
        receiver=receiver.replace('uint(value.ItemId)','Number(value.ItemId)')
        receiver=receiver.replace('dispatchEvent(', 'this.dispatchEvent(')
        code='var p2Active=true,p2Mode="Browse",p2Payloads={};class Event{constructor(name){this.name=name;}};const target={dispatchEvent(e){this.event=e.name;},receive:function(value){'+receiver+'}};'
        code+='Object.defineProperty(target,"_tooltip",{get(){throw Error("Presentation dependency");}});'
        code+='target.receive({ItemId:42,ItemName:"Hunting sword",PrimaryStatValue:103});target.receive({ItemId:7,ItemName:"Boots"});console.log(JSON.stringify([p2Payloads,target.event]));'
        cache,event=runjs(code);self.assertEqual(cache['42']['ItemName'],'Hunting sword');self.assertEqual(cache['7']['ItemName'],'Boots');self.assertEqual(event,'p2ItemData')
    def test_summary_is_dirty_and_selected_identity_drives_verified_request(self):
        menu=(ROOT/'src/inventory/p2/Menu.asinc').read_text(encoding='utf-8')
        summary=body(menu,'protected function p2RenderSummary(')
        self.assertIn('grid.p2Selected()',summary);self.assertIn('"OnGetItemData",[id,int(stub.slotType)]',summary)
        self.assertIn('p2Payloads[String(id)]',summary)
        self.assertNotIn('iaiDockedTip',summary);self.assertNotIn('isHidden()',summary)
        self.assertIn('if(this.p2SummaryDirty)',body(menu,'protected function p2Tick('))
        self.assertNotIn('addChild',summary)
        gallery=(ROOT/'src/inventory/p2/Gallery.asinc').read_text()
        populate=body(gallery,'public function p2Populate(')
        self.assertNotIn('this.updateRendererBounds()',populate)
        self.assertIn('if(useData || sortNew) this.sortList(list)',populate)
    def test_actual_summary_method_selects_matching_payload_and_native_delta(self):
        menu=(ROOT/'src/inventory/p2/Menu.asinc').read_text(encoding='utf-8')
        summary=js_types(body(menu,'protected function p2RenderSummary('))
        summary=summary.replace('for each(var blank in this.p2Fields)', 'for(var blank of this.p2Fields)')
        summary=summary.replace('uint(stub.id)','Number(stub.id)').replace('int(stub.slotType)','Number(stub.slotType)').replace('dispatchEvent(', 'this.dispatchEvent(')
        summary=re.sub(r'(payload(?:\.equippedItemData)?\.SocketsList) is Array',r'Array.isArray(\1)',summary)
        code='''const TextField=x=>x;class GameEvent{static CALL="call";constructor(type,command,args){Object.assign(this,{command,args});}}
          const ContextInfoManager={p2Payloads:{42:{ItemName:"Fixture sword",PrimaryStatLabel:"Damage",PrimaryStatValue:100,PrimaryStatDelta:.1,PrimaryStatDiffStr:"<font color='#19D900'>+3</font>",RequiredLevel:"Level 2",SocketsList:[1],equippedItemData:{SocketsList:[]}},7:{ItemName:"Wrong item"}}};
          const grid={p2Selected:()=>({id:42,slotType:3,category:"steel"}),p2Revision:1};
          const target={mcPlayerInventory:{mcPlayerGrid:grid},p2Fields:[{},{},{}],p2Selection:0,p2SelectedRevision:-1,p2Mode:"Browse",dispatchEvent(e){this.request=e;},render:function(){'''+summary+'''}};
          target.render();console.log(JSON.stringify({fields:target.p2Fields,request:target.request}));'''
        value=runjs(code)
        self.assertEqual(value['fields'][0]['htmlText'],'Fixture sword')
        self.assertIn('90–110',value['fields'][1]['htmlText']);self.assertIn('+3',value['fields'][1]['htmlText'])
        self.assertIn('Level 2',value['fields'][2]['htmlText']);self.assertIn('Sockets 1 / 0',value['fields'][2]['htmlText'])
        self.assertEqual(value['request'],dict(command='OnGetItemData',args=[42,3]))
    def test_one_footer_native_device_renderer_and_scoped_restore(self):
        source=(ROOT/'src/inventory/p2/Footer.asinc').read_text()
        self.assertIn('this.p2Footer.handleSetupButtons(list)',source)
        self.assertNotIn('new Sprite',source);self.assertNotIn('I /',source)
        menu=(ROOT/'src/inventory/p2/Menu.asinc').read_text()
        self.assertIn('ControllerChangeEvent.CONTROLLER_CHANGE',menu)
        device=body(menu,'protected function p2Device(')
        self.assertNotIn('p2Selection',device);self.assertNotIn('p2SetMode',device)
        renderer=b.b.old.unique(b.BEFORE/'scripts','ModuleInputFeedback.as').read_text(encoding='utf-8-sig')
        self.assertIn('InputManager.getInstance().isGamepad()',renderer)
        self.assertIn('InputManager.getInstance().addEventListener(ControllerChangeEvent.CONTROLLER_CHANGE',renderer)
    def test_no_old_background_or_extra_controls_in_gear(self):
        menu=(ROOT/'src/inventory/p2/Menu.asinc').read_text()
        self.assertIn('this.iaiArtHost.visible = false',menu)
        self.assertIn('this.p2Scene.graphics.beginFill(0x0C0E0C,1)',menu)
        self.assertNotIn('qfAdaptiveButton',menu)
        self.assertNotIn('OnGetItemDataForMouse',menu)
        self.assertNotIn('1.4',menu)
    def test_original_annotations_are_reused_not_added_qol(self):
        script=(ROOT/'src/inventory/inkGearGrid.ws').read_text()
        self.assertIn('m_tagsFilter.Size() == 0',script)
        self.assertNotIn('saved var',script)
        self.assertIn('InventoryUpdateItem(item)',script)

@unittest.skipUnless((b.OUT/'prepared.json').exists(),'Compiled candidate not yet prepared')
class P2Compiled(unittest.TestCase):
    def test_unchanged_assets_and_hoods_common_classes(self):
        old=(b.BASE/'prepared-inputs'/b.KEY).read_bytes();new=(b.OUT/'prepared-inputs'/b.KEY).read_bytes()
        tags=b.b.b.m.b.audit.swf_tags
        self.assertEqual([(c,v) for c,v in tags(old)[2] if c!=82],[(c,v) for c,v in tags(new)[2] if c!=82])
        for name in ('SlotPaperdoll','ItemDataStub','ModuleInputFeedback','InputFeedbackButton'):
            self.assertEqual(b.b.old.unique(b.BEFORE/'scripts',name+'.as').read_bytes(),b.b.old.unique(b.OUT/'after/scripts',name+'.as').read_bytes())
    def test_gallery_not_native_section_parent_scale(self):
        text=b.b.old.unique(b.OUT/'after/scripts','SlotsListGrid.as').read_text(encoding='utf-8-sig')
        self.assertIn('this.p2Populate(true)',body(text,'override protected function populateData('))
        self.assertIn('if(this.p2Gallery)',body(text,'protected function getItemSection('))
        self.assertIn('if(this.p2Gallery)',body(text,'protected function saveItemPosition('))
    def test_data_bridge_and_native_public_methods_survive(self):
        data=json.loads((b.OUT/'prepared.json').read_text())
        self.assertEqual(set(data['changed_classes']),set(b.p.TRANSFORMS))
        self.assertGreater(data['contracts']['original_declarations_retained'],4200)
        context=b.b.old.unique(b.OUT/'after/scripts','ContextInfoManager.as').read_text(encoding='utf-8-sig')
        self.assertIn('value.ItemId',body(context,'public function dataReceiver('))
        self.assertIn('p2Payloads',body(context,'public function dataReceiver('))

@unittest.skipUnless((b.OUT/'receipt.json').exists(),'Private release not yet packaged')
class P2Release(unittest.TestCase):
    def test_native_and_exact_package(self):
        d=json.loads((b.OUT/'receipt.json').read_text());self.assertTrue(d['native_resource_complete'])
        passed={r['label'] for r in d['native_commands'] if r['passed']}
        self.assertTrue({'cook','validate','pack'}<=passed)
        self.assertEqual(d['native_complete'],'metadata' in passed)
        self.assertEqual(d['reconstruction_used'],'metadata' not in passed)
        if d['reconstruction_used']:
            self.assertTrue(d['metadata_reconstruction']['independent_changed_control_exact'])
            self.assertTrue(d['metadata_reconstruction']['native_control_byte_identical'])
            self.assertEqual(d['metadata_reconstruction']['output_metadata_sha256'],b.sha(b.OUT/'packed/metadata.store'))
        self.assertEqual(b.sha(Path(d['zip_path'])),d['zip_sha256'])
        with zipfile.ZipFile(d['zip_path']) as z:self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),3)
        self.assertEqual(b.b.b.m.b.bars.extract(b.OUT/'packed/blob0.bundle',b.KEY),(b.OUT/'prepared-inputs'/b.KEY).read_bytes())
    def test_protected_live_inputs_remain_exact(self):
        self.assertEqual(b.freeze(),json.loads((b.OUT/'frozen.json').read_text()))
if __name__=='__main__':unittest.main()
