"""Authored input/state regression fixtures; no native engine/game execution."""
import importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'tools'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def checks():
 v=load('verify-approved-inventory');source=(ROOT/'src/inventory/unified/Scene.asinc').read_text()
 def fn(name,text=source):
  args,body=v.method(text,name)
  erased=v.erase(args+'@@'+body)
  erased=re.sub(r':\s*(?:Event|InputEvent|InputDetails|Point|Rectangle|Error|SlotsListGrid)\b','',erased)
  return erased.split('@@')
 js="""const assert=require('node:assert/strict');
const InputValue={KEY_UP:'keyUp',KEY_DOWN:'keyDown',KEY_HOLD:'keyHold'};
const NavigationCode={UP:'up',DOWN:'down',LEFT:'left',RIGHT:'right',DPAD_UP:'dpad_up',DPAD_DOWN:'dpad_down',DPAD_LEFT:'dpad_left',DPAD_RIGHT:'dpad_right',GAMEPAD_A:'enter-gamepad_A',ENTER:'enter',GAMEPAD_B:'escape-gamepad_B',GAMEPAD_L3:'gamepad_L3',GAMEPAD_BACK:'back',GAMEPAD_L2:'gamepad_L2'};
const KeyCode={F8:119,SPACE:32,ESCAPE:27,TAB:9,I:73,SHIFT:16,SHIFT_LEFT:160,SHIFT_RIGHT:161};
const SlotBase={aiDiagnostics:false};function getTimer(){return 0;}
const CommonUtils={fixupKeyCode(){},convertWASDCodeToNavEquivalent(d){if(d.code===87)d.navEquivalent='up';}};
const ctx={aiFault:false,aiActive:true,aiFocus:1,aiNavOwners:{},modal:false,moves:0,groups:0,requests:0,
 aiEvidence(){},aiModal(){return this.modal;},aiMode(n){this.aiFocus=n;this.requests++;},
 aiShowGroup(n){this.aiGroup=n;this.groups++;},aiGroup:1,aiTip:{iaiScrBy(){},showEquippedTooltip(){}},
 mcPlayerInventory:{mcPlayerGrid:{aiMove(n){ctx.moves+=n;}}}};
"""
 for name in ('aiNavAllow','aiInput'):
  args,body=fn(name);js+='ctx.'+name+'=function('+args+'){with(this){'+body+'}};\n'
 js+="""
function input(code,nav,value){let e={handled:false,details:{code,navEquivalent:nav,value},stopImmediatePropagation(){this.stopped=true;}};ctx.aiInput(e);return e;}
function pair(nav,raw,arrow){input(raw,'dpad_'+nav,'keyDown');input(arrow,nav,'keyDown');input(raw,'dpad_'+nav,'keyUp');input(arrow,nav,'keyUp');}
pair('down',143,40);assert.equal(ctx.moves,1);
pair('down',143,40);assert.equal(ctx.moves,2); // released tap is immediate
input(143,'dpad_down','keyDown');input(40,'down','keyDown');
for(let i=0;i<5;i++){input(143,'dpad_down','keyHold');input(40,'down','keyHold');}
assert.equal(ctx.moves,8); // one down + five native holds, no duplicate stream
input(143,'dpad_down','keyUp');input(40,'down','keyUp');
input(38,'up','keyDown');input(38,'up','keyHold');input(38,'up','keyUp');assert.equal(ctx.moves,6);
input(87,null,'keyDown');input(87,null,'keyUp');assert.equal(ctx.moves,5);
ctx.aiFocus=0;let e=input(130,'enter-gamepad_A','keyUp');assert.equal(ctx.aiFocus,1);assert.equal(e.handled,true);
e=input(130,'enter-gamepad_A','keyUp');assert.equal(e.handled,false); // native action path, no custom equip
ctx.aiFocus=2;e=input(131,'escape-gamepad_B','keyUp');assert.equal(ctx.aiFocus,1);assert.equal(e.handled,true);
e=input(131,'escape-gamepad_B','keyUp');assert.equal(e.handled,false); // native close from browse
ctx.aiFocus=3;e=input(131,'escape-gamepad_B','keyUp');assert.equal(ctx.aiFocus,1);assert.equal(e.handled,true);
ctx.modal=true;ctx.aiFocus=2;e=input(131,'escape-gamepad_B','keyUp');assert.equal(e.handled,false);assert.equal(ctx.aiFocus,2);
ctx.modal=false;
function dispatch(priority){let native=0,stopped=false;let listeners=[{p:1,f(){native++;}},{p:priority,f(){stopped=true;}}];listeners.sort((a,b)=>b.p-a.p);for(let l of listeners){if(!stopped)l.f();}return native;}
assert.equal(dispatch(120),0);assert.equal(dispatch(0),1);
"""
 # Exercise native-focus acquisition after a delayed real projection fixture.
 args,body=fn('aiFocusList');js+='ctx.aiFocusList=function('+args+'){with(this){'+body+'}};\n'
 js+="""
ctx.aiFocus=1;ctx.mcPlayerInventory.focused=0;let grid=ctx.mcPlayerInventory.mcPlayerGrid;
grid.data=[{id:31},{id:81}];grid.focused=0;grid.selectedIndex=1;grid.applySelectionContext=function(){this.contextApplied=true;};
ctx.selectTargetModule=function(m){assert.equal(m,ctx.mcPlayerInventory);};
ctx.aiFocusList();assert.equal(grid.focused,1);assert.equal(ctx.mcPlayerInventory.focused,1);assert.equal(grid.selectedIndex,1);assert.equal(grid.contextApplied,true);
grid.focused=0;ctx.modal=true;ctx.aiFocusList();assert.equal(grid.focused,0);ctx.modal=false;
"""
 native_module=next((ROOT/'build/adaptive-inventory-v2-p1/before/scripts').rglob('InventoryTabbedListModule.as')).read_text(encoding='utf-8-sig')
 patched_module=v.patch.module(native_module)
 for label,text in [('nativeCapacity',native_module),('customCapacity',patched_module)]:
  args,body=fn('hasSelectableItems',text);body=body.replace('super.hasSelectableItems()','nativeTabs()')
  js+='function '+label+'(c){with(c){'+body+'}}\n'
 js+="""
let capacity={aiModuleBase:{},iaiEqBlock:false,mcPlayerGrid:{data:[{id:31},{id:81}]},nativeTabs(){return false;}};
assert.equal(nativeCapacity(capacity),false);assert.equal(customCapacity(capacity),true);
capacity.aiModuleBase=null;assert.equal(customCapacity(capacity),false);
capacity.aiModuleBase={};capacity.mcPlayerGrid.data=[];assert.equal(customCapacity(capacity),false);
"""
 # Stats transition: reproduce the released unassigned white Shape, then run
 # corrected authored aiTick with identical display-tree fixture.
 receipt=json.loads((ROOT/'build/approved-inventory-runtime-diagnostic-r4/prepared.json').read_text())
 old=(Path(receipt['abc'])/'MenuInventory.as').read_text(encoding='utf-8')
 for label,text in [('oldTick',old),('newTick',source)]:
  args,body=fn('aiTick',text);js+='function '+label+'(c){with(c){'+body+'}}\n'
 js+="""
const ContextInfoManager={};const SlotsTransferManager={getInstance(){return {isDragging(){return false;}};}};
const IMS_Player=0;
function Rectangle(){}
function scene(){let s={aiFault:false,aiAllowed:true,_inventoryMode:0,aiActive:true,aiRefresh:false,
 aiSuspended:false,aiTargetState:false,aiSortState:false,aiFocus:1,aiCurrentID:31,
 aiStatsDiagnosticVisible:true,aiDiagnosticText:{visible:true},aiBase:{mask:null},aiScene:{},aiTip:{},aiPendingName:{},
 mcPaperDollModule:{aiTargets(){}},mcSelectionMode:{isActive(){return false;}},mcSortingMode:{visible:false},
 mcPlayerInventory:{mcPlayerGrid:{}},_rendererController:{isActive(){return true;}},
 aiEvidence(){},aiSelectData(){},selectTargetModule(){},aiFocusList(){},getChildIndex(){return 1;},
 addChildAt(o){o.parent=this;},removeChild(o){o.parent=null;}};
 s.aiModelMask={parent:s};s.mcCharacterRenderer={mask:s.aiModelMask};return s;}
SlotBase.aiLog=function(){};
let oldScene=scene();oldTick(oldScene);assert.equal(oldScene.mcCharacterRenderer.mask,null);assert.equal(oldScene.aiModelMask.parent,oldScene);
let fixedScene=scene();newTick(fixedScene);assert.equal(fixedScene.aiModelMask.parent,null);assert.equal(fixedScene.aiDiagnosticText.visible,false);
fixedScene._rendererController.isActive=()=>false;newTick(fixedScene);assert.equal(fixedScene.aiModelMask.parent,fixedScene);assert.equal(fixedScene.mcCharacterRenderer.mask,fixedScene.aiModelMask);assert.equal(fixedScene.aiDiagnosticText.visible,true);
console.log(JSON.stringify({input_cases:11,late_focus_cases:2,stats_negative_control:true,native_input_tracking_before_custom:true,native_engine_executed:false}));
"""
 native=(ROOT/'build/adaptive-inventory-v2-p1/before/scripts/red/game/witcher3/managers/InputManager.as').read_text(encoding='utf-8-sig')
 if 'this.handleDelegatedInput,false,1,true' not in native or 'aiInput,false,0,true' not in source:raise AssertionError('Native tracker priority contract changed')
 out=ROOT/'build/approved-inventory-input-tests';out.mkdir(exist_ok=True);path=out/'authored-input.js';path.write_text(js)
 result=subprocess.run(['node',str(path)],capture_output=True,text=True)
 if result.returncode:raise AssertionError(result.stdout+result.stderr)
 report=json.loads(result.stdout);(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(checks(),indent=2))
