"""Execute authored request/commit methods; display/native APIs are fixtures.

This is not a Flash renderer, native dispatcher or gameplay test.
"""
import importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def checks():
    spec=importlib.util.spec_from_file_location('verify',ROOT/'tools/verify-approved-inventory.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    scene=(ROOT/'src/inventory/unified/Scene.asinc').read_text(encoding='utf-8-sig')
    details=(ROOT/'src/inventory/unified/Details.asinc').read_text(encoding='utf-8-sig')
    prior=ROOT/'build/approved-inventory-runtime-diagnostic-r6/abc-01'
    old_scene=(prior/'MenuInventory.as').read_text(encoding='utf-8-sig')
    old_tip=(prior/'TooltipInventory.as').read_text(encoding='utf-8-sig')
    def function(text,name):
        args,body=v.method(text,name)
        args,body=re.sub(r':\s*(?:Event|Rectangle|SlotsListGrid)\b','',v.erase(args+'@@'+body)).split('@@')
        return 'function('+args+'){with(this){'+body+'}}'
    js='''const assert=require('node:assert/strict');
const uint=n=>Number(n)>>>0,int=n=>Number(n)|0;
const SlotBase={aiLog(){}};const ContextInfoManager={aiPayload:null};
function GameEvent(type,name,args){this.name=name;this.args=args;}GameEvent.CALL='call';
function Rectangle(x,y,w,h){Object.assign(this,{x,y,width:w,height:h});}
const IAI_OX=0,IAI_OY=0;
'''
    for variable,text,name in [('select',scene,'aiSelectData'),('receive',scene,'aiPayloadApply'),
            ('pending',details,'aiPending'),('present',details,'aiPresent'),
            ('oldSelect',old_scene,'aiSelectData'),('oldReceive',old_scene,'aiPayloadApply'),
            ('oldPending',old_tip,'aiPending'),('oldPresent',old_tip,'aiPresent'),
            ('mode',scene,'aiMode'),('group',scene,'aiShowGroup')]:
        js+='const '+variable+'='+function(text,name)+';\n'
    js+='''
function fixture(old=false){
 let tip={aiItem:1,visible:true,iaiScr:72,iaiDocked:true,iaiDock:{},iaiPopOn:false,
  iaiEqCard:true,iaiScrOn:true,commits:[],validations:0,
  validateNow(){this.validations++;this.commits.push({id:this.data.ItemId,serial:this.data.aiRequestSerial,scroll:this.iaiScr});},
  aiPending:old?oldPending:pending,aiPresent:old?oldPresent:present};
 tip.data={ItemId:1,aiRequestSerial:0,ItemName:'A',StatsList:['complete']};
 let grid={data:[{id:1,itemName:'A'}],aiTop:0,aiSelected(){return this.data[0]||null;},
 aiSort(){},aiSetItems(list){this.data=list;}};
 let s={aiActive:true,aiFocus:1,aiSuspended:false,aiTargetState:false,aiCurrentID:1,
 aiRequestSerial:0,aiPayloadRevision:0,aiTip:tip,aiPendingName:{text:'',visible:true},
 aiDetailsRect:{x:747,y:190,width:464,height:730,clone(){return {...this};}},
 mcPlayerInventory:{mcPlayerGrid:grid},requests:[],dispatchEvent(e){this.requests.push(e);},
 aiSelectData:old?oldSelect:select,aiPayloadApply:old?oldReceive:receive,
 aiFocusList(){},mcPaperDollModule:{aiTargets(){},mcPaperdoll:{},mcPaperDollSlot3:{index:3}},
 aiPaintRail(){},aiHeader:{},aiFocusMark:{graphics:{clear(){},lineStyle(){},moveTo(){},lineTo(){}}},
 aiStates:{},aiGroup:1,aiAll:[],aiUpdating:false,aiShowGroup:group};
 s.select=(id,force=false)=>{grid.data=id?[{id,itemName:String(id)}]:[];s.aiSelectData(force);};
 s.deliver=(id,serial)=>{ContextInfoManager.aiPayload={ItemId:id,aiRequestSerial:serial,ItemName:String(id),StatsList:['complete']};s.aiPayloadApply({});};
 return s;
}
// Exact r6 negative control: generic title visible, complete panel hidden until reply.
let old=fixture(true);old.select(2);assert.equal(old.aiPendingName.text,'2');assert.equal(old.aiTip.visible,false);
assert.equal(old.aiTip.data.ItemId,1);old.deliver(2,1);assert.equal(old.aiTip.visible,true);assert.equal(old.aiPendingName.text,'');
let s=fixture();s.select(2);assert.equal(s.aiTip.visible,true);assert.equal(s.aiTip.data.ItemId,1);
assert.equal(s.aiTip.iaiScr,72);assert.equal(s.aiPendingName.text,'');assert.equal(s.aiCurrentID,2);
s.deliver(2,1);assert.equal(s.aiTip.data.ItemId,2);assert.equal(s.aiTip.iaiScr,0);assert.equal(s.aiTip.validations,1);
// Out-of-order A -> B -> C, then A -> B -> A: identity alone is insufficient.
s=fixture();s.select(2);s.select(3);s.deliver(2,1);assert.equal(s.aiTip.data.ItemId,1);
s.deliver(3,2);assert.equal(s.aiTip.data.ItemId,3);s.deliver(2,1);assert.equal(s.aiTip.data.ItemId,3);
s=fixture();s.select(2);s.select(1);s.deliver(1,0);assert.equal(s.aiTip.validations,0);
s.deliver(2,1);assert.equal(s.aiTip.validations,0);s.deliver(1,2);assert.equal(s.aiTip.validations,1);
// Invalid/null/zero and duplicate payloads cannot replace or revalidate the panel.
s=fixture();s.select(2);ContextInfoManager.aiPayload=null;s.aiPayloadApply({});
s.deliver(0,1);s.deliver(999,1);s.deliver(2,0);assert.equal(s.aiTip.validations,0);
s.deliver(2,1);s.aiTip.iaiScr=56;s.deliver(2,1);assert.equal(s.aiTip.validations,1);assert.equal(s.aiTip.iaiScr,56);
// Equip/ownership refresh of SAME ID is explicit, serialled and retains scroll.
s.select(2,true);assert.equal(s.aiTip.visible,true);s.deliver(2,1);assert.equal(s.aiTip.validations,1);
s.deliver(2,2);assert.equal(s.aiTip.validations,2);assert.equal(s.aiTip.iaiScr,56);
// Repeated unchanged selection / Inspect / Back do not request identical data.
let n=s.requests.length;s.select(2);assert.equal(s.requests.length,n);
mode.call(s,2);mode.call(s,1);mode.call(s,1);assert.equal(s.requests.filter(x=>x.name==='OnApprovedDetails').length,2);
// Category change runs actual projection method; empty category clears intentional details.
s=fixture();s.aiAll=[{id:1,aiGroup:1},{id:4,aiGroup:2}];s.aiShowGroup(2);
assert.equal(s.aiCurrentID,4);assert.equal(s.aiTip.data.ItemId,1);s.deliver(4,1);assert.equal(s.aiTip.data.ItemId,4);
s.aiShowGroup(7);assert.equal(s.aiCurrentID,0);assert.equal(s.aiTip.visible,false);
s.deliver(0,s.aiRequestSerial);assert.equal(s.aiTip.data.ItemId,4);
// Rapid repeat simulates selection callbacks; native device routing is separately tested.
s=fixture();let retained=s.aiTip;for(let i=0;i<120;i++){s.select(2+i%3);assert.equal(s.aiTip.visible,true);assert.equal(s.aiTip,retained);}
for(let i=119;i>=0;i--)s.deliver(2+i%3,i+1);
assert.equal(s.aiTip.validations,1);assert.equal(s.aiTip.data.ItemId,s.aiCurrentID);
// Old content remains scrollable while pending; reset happens only on different-item commit.
s=fixture();s.select(2);s.aiTip.iaiScr=100;assert.equal(s.aiTip.data.ItemId,1);s.deliver(2,1);assert.equal(s.aiTip.iaiScr,0);
'''
    ws=(ROOT/'src/inventory/unified/approvedInventory.ws').read_text(encoding='utf-8-sig')
    js+='const primary='+function(ws,'execurePrimaryAction')+';\n'
    js+='''
// Execute the existing annotation action wrapper, with native handlers stubbed.
let equipped=false,acted=[];function GetWitcherPlayer(){return {IsItemEquipped(){return equipped;}};}
s=fixture();s.select(2);
let action={currentItemId:2,invMenuRef:{aiApprovedActive:true,aiApprovedFocus:1,AiApprovedStatus(){},OnUnequipItem(id){acted.push(['unequip',id]);}},
 invComponentRef:{IsIdValid(){return true;},IsItemAnyArmor(){return false;},IsItemWeapon(){return true;}},wrappedMethod(){acted.push(['primary',this.currentItemId]);}};
function ItemToFlashUInt(n){return n;}primary.call(action);equipped=true;primary.call(action);
assert.equal(s.aiTip.data.ItemId,1);assert.deepEqual(acted,[['primary',2],['unequip',2]]);
console.log(JSON.stringify({r6_negative_control:true,rapid_selection_events:120,stale_responses_rejected:119,
 transition_cases:12,action_wrapper_cases:2,native_engine_executed:false}));
'''
    assert 'aiPendingName' not in scene
    assert 'data=value;validateNow();visible=true;' in details
    for name in ('aiSelectData','aiPayloadApply'):
        _,body=v.method(scene,name)
        for token in ('new Tooltip','removeChild','aiClose','cleanup','aiSetItems'):
            assert token not in body
    # Working actions/row/equipped-marker source must be exact r6 originals.
    manifest=json.loads((ROOT/'research/inventory-approved-unified-p1-diagnostic-r6-manifest.json').read_text(encoding='utf-8-sig'))
    import hashlib
    for path in ('src/inventory/unified/Row.asinc','src/inventory/unified/approvedInventory.ws','src/inventory/unified/List.asinc','src/inventory/unified/Module.asinc'):
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==manifest['source_hashes'][path],path
    out=ROOT/'build/approved-inventory-details-transition-tests';out.mkdir(exist_ok=True)
    script=out/'authored-details.js';script.write_text(js,encoding='utf-8')
    result=subprocess.run(['node',str(script)],capture_output=True,text=True)
    if result.returncode:raise AssertionError(result.stdout+result.stderr)
    report=json.loads(result.stdout);(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(checks(),indent=2))
