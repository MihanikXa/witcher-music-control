"""Execute authored list/repeat algorithms after type erasure; not a game test.

Only Flash display/event APIs are mocked. This deliberately tests the actual
AS method bodies, rather than a second Python implementation of the list.
"""
import importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('patch',ROOT/'tools/patch-approved-inventory.py');patch=importlib.util.module_from_spec(s);s.loader.exec_module(patch)
def method(source,name):
    a,z=patch.p.trace.body_span(source,'function '+name+'(');body=source[a+1:z]
    header=source[source.rfind('function '+name+'(',0,a):a]
    args=header[header.index('(')+1:header.rfind(')')]
    return args,body
def erase(text):
    text=re.sub(r'\bfor each\((.*?) in (.*?)\)',r'for (\1 of \2)',text)
    text=re.sub(r':\s*(?:Vector\.<\w+>|int\b|uint\b|Number\b|Boolean\b|String\b|Object\b|Array\b|SlotBase\b|IBaseSlot\b|ItemDataStub\b|SItemUniqueId\b|name\b|EEquipmentSlots\b)', '',text)
    text=re.sub(r'\s+as\s+[A-Za-z_]\w*','',text)
    return text.replace('new Vector.<IBaseSlot>()','[]')
def algorithm_checks():
    source=(ROOT/'src/inventory/unified/List.asinc').read_text()
    js='''const assert=require('node:assert/strict');
var aiRows=false,aiTop=0,aiRevision=0,aiItems=[],aiPool=[],aiGridBase=null;
var _renderers=[],_data=[],_selectedIndex=-1,_renderersCount=0;
var _columns=9,_rows=10,_gridSquareSize=64,_gridRenderHeight=520,_numRowsVisible=8,handleScrollBar=true,_offset=2;
var _scrollBar={visible:true},_highlightCanvas={visible:true},_canvas={x:0,y:-128,addChild(){},removeChild(){}};
var creations=0,destroys=0,loads=0,events=[];
function Event(name,bubbles){this.name=name;}
function DisplayObject(x){return x;}
function uint(x){return Number(x)>>>0;} function int(x){return Number(x)|0;}
function setupRenderer(){} function cleanUpRenderer(){destroys++;}
function invalidateData(){} function dispatchEvent(e){events.push(e.name);}
function getSelectedRenderer(){return _renderers[_selectedIndex]||null;}
Object.defineProperty(globalThis,'selectedIndex',{get(){return _selectedIndex;},set(v){_selectedIndex=v;for(var r of _renderers)r.selected=r.index===v;}});
const SlotBase={aiLog(){}};function aiLog(){}
class Row {
 constructor(){creations++;this._data=null;this.aiSignature='';this.selected=false;}
 get data(){return this._data;}
 set data(v){if(!this._data||this._data.iconPath!==v.iconPath)loads++;this._data=v;}
 forceValidateNow(){} aiFormatRow(){} cleanup(){}
}
var _slotRendererRef=Row;
'''
    args,body=method((ROOT/'src/inventory/unified/Row.asinc').read_text(),'aiBind')
    js+='Row.prototype.aiBind=function('+erase(args)+'){with(this){'+erase(body)+'}};\n'
    for name in ('aiEnable','aiDisable','aiSelected','aiIndex','aiSetItems','aiPaint','aiMove','aiWheel'):
        args,body=method(source,name);js+='function '+name+'('+erase(args)+'){'+erase(body)+'}\n'
    js+='''
function items(n){return Array.from({length:n},(_,i)=>({id:i+1,iconPath:'item'+(i+1),itemName:'Item '+i,aiSubtitle:'native',quantity:1,isEquipped:i===1,hasOwnProperty:Object.prototype.hasOwnProperty}));}
aiEnable();assert.equal(creations,9);assert.equal(_canvas.y,0);assert.equal(_scrollBar.visible,false);
aiSetItems(items(2),2,0);assert.equal(aiSelected().id,2);assert.equal(_renderers.length,2);
var initialLoads=loads,instances=_renderers.slice();
for(var i=0;i<15;i++){aiSetItems(items(2),2,0);assert.equal(aiSelected().id,2);assert.deepEqual(_renderers,instances);}
assert.equal(loads,initialLoads);assert.equal(creations,9);assert.equal(destroys,0);
aiSetItems(items(180),2,0);for(var i=0;i<50;i++)aiMove(1);
assert.equal(aiSelected().id,52);assert.ok(aiTop>0);assert.equal(_renderers.length,7);assert.equal(creations,9);
var selected=aiSelected().id,page=aiTop,retained=getSelectedRenderer();
var changed=items(180);changed[51].isEquipped=true;initialLoads=loads;
aiSetItems(changed,selected,page);assert.equal(aiSelected().id,selected);assert.equal(getSelectedRenderer(),retained);assert.equal(aiTop,page);assert.equal(loads,initialLoads);
aiSetItems(changed.filter(x=>x.id!==selected),selected,page);assert.ok(aiSelected());assert.equal(aiSelected().id,53);
aiSetItems([],0,0);assert.equal(aiSelected(),null);assert.equal(_renderers.length,0);assert.equal(aiTop,0);
aiDisable();assert.equal(destroys,9);assert.equal(_columns,9);assert.equal(_canvas.y,-128);assert.equal(_scrollBar.visible,true);
'''
    pad=(ROOT/'src/inventory/GearPad.asinc').read_text()
    js+='var qfGearGrid=true,qfGearHeld={},qfGearDown={},qfGearFire={};\n'
    for name in ('qfGearPadAllow','qfGearResetPad'):
        args,body=method(pad,name);js+='function '+name+'('+erase(args)+'){'+erase(body)+'}\n'
    js+='''
let d={code:142,value:'keyDown'};
assert.equal(qfGearPadAllow(d,0),true);assert.equal(qfGearPadAllow(d,1),false);
d.value='keyHold';assert.equal(qfGearPadAllow(d,200),false);assert.equal(qfGearPadAllow(d,400),true);assert.equal(qfGearPadAllow(d,450),false);assert.equal(qfGearPadAllow(d,510),true);
d.value='keyUp';qfGearPadAllow(d,520);d.value='keyDown';assert.equal(qfGearPadAllow(d,530),true);
qfGearResetPad();assert.equal(qfGearPadAllow(d,540),true);
'''
    args,body=method((ROOT/'src/inventory/unified/approvedInventory.ws').read_text(),'AiApprovedGroup')
    js+='''
var EES_Quickslot1=10,EES_Quickslot2=11;
var _inv={GetItemCategory(i){return i.category;},ItemHasTag(i,t){return (i.tags||[]).includes(t);},IsItemHorseItem(i){return !!i.horse;},IsItemTrophy(i){return !!i.trophy;},IsItemFood(i){return !!i.food;},IsItemAnyArmor(i){return !!i.armor;},IsItemWeapon(i){return !!i.weapon;},IsItemBolt(i){return !!i.bolt;},GetSlotForItemId(i){return i.slot||0;}};
'''
    js+='function AiApprovedGroup('+erase(args)+'){'+erase(body)+'}\n'
    js+='''
var fixtures=[
['steel sword',{category:'steel',weapon:true},1],['silver sword',{category:'silver',weapon:true},1],['crossbow',{category:'crossbow'},1],['bolt',{category:'bolt',bolt:true},1],
['armor',{category:'armor',armor:true},2],['boots',{category:'boots',armor:true},2],
['potion/decoction',{category:'potion'},3],['oil',{category:'oil'},3],['food',{category:'edibles',food:true},3],
['bomb',{category:'petard'},4],['pocket',{category:'misc',slot:10},5],['mask',{category:'mask'},5],['dye',{category:'dye'},5],['Hoods dye',{category:'misc',tags:['mod_dye']},5],
['quest sword',{category:'steel',tags:['Quest'],weapon:true},6],['quest book',{category:'book',tags:['Quest']},6],
['Roach saddle',{category:'saddle',horse:true},7],['trophy',{category:'trophy',trophy:true},7],['material',{category:'crafting'},7],['book',{category:'book'},7],['modded unknown',{category:'custom_new'},7]
];
for(var [name,facts,expected] of fixtures)assert.equal(AiApprovedGroup(facts),expected,name);
process.stdout.write(JSON.stringify({authored_algorithm_cases:12,category_cases:fixtures.length,pooled_instances:creations,unchanged_icon_reloads:0,native_display_engine_executed:false}));
'''
    result=subprocess.run(['node','-e',js],capture_output=True,text=True)
    if result.returncode:raise AssertionError(result.stderr)
    return json.loads(result.stdout)
def geometry_checks():
    cases=[]
    scene=(ROOT/'src/inventory/unified/Scene.asinc').read_text()
    module=(ROOT/'src/inventory/unified/Module.asinc').read_text()
    rows=(ROOT/'src/inventory/unified/List.asinc').read_text()
    def values(pattern,text):return tuple(map(float,re.search(pattern,text).groups()))
    details=values(r'aiDetailsRect:Rectangle = new Rectangle\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)',scene)
    x,y,pitch=values(r's.x=([\d.]+);s.y=([\d.]+)\+i\*([\d.]+)',scene)
    rail_w,rail_h=values(r's.graphics.drawRect\(0,0,([\d.]+),([\d.]+)\)',scene)
    list_w,list_h=values(r'maskClip.width=([\d.]+);maskClip.height=([\d.]+)',module)
    list_x,list_y=values(r'mcListContainer.x=([\d.]+);mcListContainer.y=([\d.]+)',module)
    row_pitch=float(re.search(r'r.y=i\*([\d.]+)',rows)[1])
    regions={'rail':(x,y,rail_w,7*pitch+rail_h),'list':(list_x,list_y,list_w,list_h),'details':details}
    preview=values(r'aiModelMask.graphics.drawRect\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)',scene)
    approved=json.loads((ROOT/'build/inventory-approved-gate1/visual-receipt.json').read_text())['outputs']['sparse']['rows'][0]['bounds']
    projected=(list_x*1672/1920,list_y*941/1080,(list_x+list_w)*1672/1920,(list_y+90)*941/1080)
    if any(abs(a-b)>1 for a,b in zip(approved,projected)):raise AssertionError('Row differs from approved Gate 1 proportions')
    for width,height in ((1649,928),(1672,941),(1920,1080),(3840,2160)):
        scale=min(width/1920,height/1080)
        for name,(rx,ry,rw,rh) in regions.items():
            if not (ry>=130 and ry+rh<950 and rx+rw<=1211):raise AssertionError(name)
        if not (x+rail_w<list_x and list_x+list_w<details[0] and details[0]+details[2]<preview[0]):raise AssertionError('Column collision')
        if not list_y+6*row_pitch+90<=list_y+list_h:raise AssertionError('Last row clipped')
        cases.append(dict(viewport=[width,height],scale=scale,logical_regions=regions,preview_mask=preview,real_character_pixels_unverified=True))
    return cases
def main():
    d=dict(algorithms=algorithm_checks(),geometry=geometry_checks(),runtime_acceptance=False)
    out=ROOT/'build/approved-inventory-unified-p1';out.mkdir(exist_ok=True)
    (out/'targeted-tests.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(d,indent=2))
if __name__=='__main__':main()
