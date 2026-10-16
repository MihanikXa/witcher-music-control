"""Original bounded Inventory transforms; vendor sources remain in reference/."""
from pathlib import Path
import importlib.util,re
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('trace',ROOT/'tools/instrument-radial-movies.py');trace=importlib.util.module_from_spec(s);s.loader.exec_module(trace)
def snippet(name):return (ROOT/'src/inventory'/name).read_text(encoding='utf-8-sig')
def one(text,old,new):
 if text.count(old)!=1:raise ValueError('Expected unique source anchor '+old[:70])
 return text.replace(old,new,1)
def prefix(text,signature,code):
 a,z=trace.body_span(text,signature);return text[:a+1]+'\n'+code+'\n'+text[a+1:]
def append(text,signature,code):
 a,z=trace.body_span(text,signature);return text[:z]+code+'\n'+text[z:]
def add(text,name,code):return trace.insert_helper(text,name,code)
def slot_base(text):return add(text,'SlotBase',snippet('GearPad.asinc'))
def item_data(text):return one(text,'public var canBeDyed:Boolean;','public var canBeDyed:Boolean;\n      public var isDyeable:Boolean;')
def slot_paperdoll(text,official):
 sig='public function canDrop(dragData:IDragTarget) : Boolean';a,z=trace.body_span(text,sig);b,y=trace.body_span(official,sig)
 if 'slotData.isDyeable' not in official[b:y] or 'slotData.isDyeable' in text[a:z]:raise ValueError('Official dye rule precondition')
 text=text[:a+1]+official[b+1:y]+text[z:]
 return one(text,'override protected function iaiRound() : Boolean\n      {\n         return true;','override protected function iaiRound() : Boolean\n      {\n         return !SlotBase.qfGearGrid;')
def paperdoll(text):
 # FFDec renders nested unary negation as invalid predecrement on a literal.
 text=re.sub(r'--([0-9]+(?:\.[0-9]+)?)',r'-(-\1)',text)
 text=one(text,'import flash.display.Graphics;','import flash.display.Graphics;\n   import flash.display.DisplayObject;')
 text=add(text,'ModulePaperdoll',snippet('GearPaperdoll.asinc'))
 return prefix(text,'override public function handleInput(event:InputEvent)','''         if(SlotBase.qfGearGrid && event.details && String(event.details.navEquivalent).indexOf("rightStick") == 0) return;''')
def tooltip(text):
 # Fixed card location retains 0.8.4 stats/compare/scroll rendering.
 return one(text,'var s:Rectangle = iaiPopSlot;','var s:Rectangle = SlotBase.qfGearGrid ? null : iaiPopSlot;')
def context(text):
 return prefix(text,'protected function iaiPlaceDock()','''         if(SlotBase.qfGearGrid && TooltipInventory.iaiDock)
         {
            TooltipInventory.iaiDock = new Rectangle(1280,166,600,720);
            TooltipInventory.iaiPopSlot = null;
            TooltipInventory.iaiPopLeft = false;
            TooltipInventory.iaiPopFix = false;
            return;
         }''')
def slot_list(text):
 text=one(text,'import flash.utils.Dictionary;','import flash.utils.Dictionary;\n   import flash.utils.getTimer;')
 return prefix(text,'public function handleInputNavSimple(event:InputEvent)','''         if(!event.handled && !SlotBase.qfGearPadAllow(event.details,getTimer()))
         { event.handled = true; return; }''')
def menu(text):
 text=add(text,'MenuInventory',snippet('GearMenu.asinc'))
 text=prefix(text,'public function setInventoryMode(value:int)', '         if(value != IMS_Player) this.qfGearRestore();')
 text=append(text,'public function setInventoryMode(value:int)', '         this.qfGearRefresh();')
 text=append(text,'protected function iaiTick(e:Event)', '         this.qfGearRefresh();')
 text=prefix(text,'protected function iaiPadCross(event:InputEvent)', '         if(SlotBase.qfGearGrid) return;')
 text=prefix(text,'protected function iaiArtLoad(key:String)', '         if(this.qfGearOn) return;')
 return text
