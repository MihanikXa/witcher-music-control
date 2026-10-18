"""P2 structural transforms on accepted v4, not on the rejected P1 movie."""
import importlib.util,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('gear',ROOT/'tools/patch-ink-gear-grid.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
def code(name):return (ROOT/'src/inventory/p2'/name).read_text(encoding='utf-8-sig')
def menu(t):
    for name in ('Geometry.asinc','Footer.asinc','Menu.asinc'):t=p.add(t,'MenuInventory',code(name))
    t=p.one(t,'import flash.display.Graphics;','import flash.display.Graphics;\n   import flash.utils.getQualifiedClassName;\n   import red.game.witcher3.data.KeyBindingData;\n   import scaleform.clik.events.ListEvent;')
    t=p.prefix(t,'public function setInventoryMode(value:int)','         this.p2Leave();')
    t=p.append(t,'protected function iaiTick(e:Event)','         this.p2Tick();')
    t=p.prefix(t,'protected function iaiPadCross(event:InputEvent)','         if(this.p2Active) return;')
    # Original typography traversal remains, but owns no P2 summary fields.
    return t
def grid(t):
    t=p.add(t,'SlotsListGrid',code('Gallery.asinc'))
    t=p.prefix(t,'override protected function populateData()','         if(this.p2Gallery) { this.p2Populate(true); return; }')
    t=p.prefix(t,'protected function getItemSection(sectionId:int)','         if(this.p2Gallery) return null;')
    t=p.prefix(t,'protected function getSectionByRendererIdx(rendererIdx:int)','         if(this.p2Gallery) return null;')
    t=p.prefix(t,'protected function isSectionCorrect(','         if(this.p2Gallery) return true;')
    t=p.prefix(t,'protected function saveItemPosition(','         if(this.p2Gallery) return;')
    t=p.prefix(t,'private function updateColumnsPaddingMap()','         if(this.p2Gallery) { this._paddingsMap = null; return; }')
    t=p.one(t,'if(Boolean(this._itemSectionsList && this._itemSectionsList.length > 0) && Boolean(isRStick)', 'if(!this.p2Gallery && Boolean(this._itemSectionsList && this._itemSectionsList.length > 0) && Boolean(isRStick)')
    for sig in ('override public function updateItems(', 'override public function updateItemData(', 'override public function removeItem('):
        t=p.prefix(t,sig,'''         var p2Selected:Object = this.p2Gallery ? this.p2Selected() : null;
         var p2Id:Number = p2Selected ? Number(p2Selected.id) : NaN;
         var p2Scroll:uint = scrollPosition;''')
        t=p.append(t,sig,'''         if(this.p2Gallery)
         {
            this.p2Populate();
            var p2Index:int = isNaN(p2Id) ? -1 : getIdIndex(uint(p2Id));
            if(p2Index >= 0) { selectedIndex = p2Index; scrollPosition = Math.min(p2Scroll,this._maxOffset); }
         }''')
    return t
def module(t):
    t=p.one(t,'import flash.geom.Point;','import flash.geom.Point;\n   import flash.geom.Rectangle;')
    t=p.add(t,'InventoryTabbedListModule',code('Module.asinc'))
    t=p.prefix(t,'override protected function onTabListItemSelected(','''         if(this.p2ModuleBase && event.index != 4) dispatchEvent(new Event("p2Exit",true));''')
    for sig in ('protected function iaiDrawTabs(', 'protected function iaiClampTabs('):
        t=p.prefix(t,sig,'         if(this.p2ModuleBase) { if(txtTitle) txtTitle.visible = false; return; }')
    return t
def context(t):
    t=p.add(t,'ContextInfoManager','''
      public static var p2Active:Boolean = false;
      public static var p2Mode:String = "Browse";
      public static var p2Payloads:Object = {};
      public static var p2Area:Rectangle;
''')
    t=p.prefix(t,'public function dataReceiver(value:Object)', '''
         if(p2Active && value && value.ItemId != null)
         {
            p2Payloads[String(uint(value.ItemId))] = value;
            dispatchEvent(new Event("p2ItemData"));
            if(p2Mode != "Auxiliary") return;
         }''')
    t=p.prefix(t,'protected function showTooltip(keyValues:Array, dataObject:TooltipData)', '''
         if(p2Active && p2Mode != "Auxiliary") return;''')
    t=p.prefix(t,'protected function iaiPlaceDock()', '''
         if(p2Active && p2Area)
         {
            TooltipInventory.iaiDock = p2Area.clone();
            TooltipInventory.iaiPopSlot = null; TooltipInventory.iaiPopLeft = false; TooltipInventory.iaiPopFix = false;
            return;
         }''')
    # Inspection's own native tooltip is outside _tooltip; keep native LT/Shift
    # comparison updates through the Menu's explicit detail instance.
    return t
def paper(t):
    t=re.sub(r'--([0-9]+(?:\.[0-9]+)?)',r'-(-\1)',t)
    t=p.one(t,'import flash.display.Graphics;','import flash.display.Graphics;\n   import flash.display.DisplayObject;')
    original=p.snippet('GearPaperdoll.asinc')
    # Reuse only snapshot/restore and the native navigation contracts.
    a,z=p.trace.body_span(original,'public function qfGearRestore(')
    restore=original[a+1:z].replace('qfGearOriginal','p2Original').replace('qfGearLastMode','p2LastMode')
    helper='''
      protected var p2Original:Array;
      protected var p2LastMode:int = -1;
      public function p2Targets(area:Rectangle, on:Boolean) : void
      {
         if(!this.p2Original)
         {
            this.p2Original = [];
            for(var i:int = 1; i <= 20; i++)
            {
               var slot:SlotPaperdoll = this["mcPaperDollSlot" + i] as SlotPaperdoll;
               if(slot) this.p2Original.push({slot:slot,x:slot.x,y:slot.y,sx:slot.scaleX,sy:slot.scaleY,visible:slot.visible});
            }
            for each(var deco:DisplayObject in [this.tfCurrentState,this.tfPotions,this.tfPockets,this.tfPetards,this.tfMasks,this.mcSegmentBorderWeapons,this.mcSegmentBorderArmor,this.mcSegmentBorderPotion,this.mcSegmentBorderBombs,this.mcSegmentBorderHorse,this.iaiDeco,this.iaiHorse])
               if(deco) this.p2Original.push({slot:deco,x:deco.x,y:deco.y,sx:deco.scaleX,sy:deco.scaleY,visible:deco.visible});
         }
         if(this.p2LastMode == int(on)) return;
         this.p2LastMode = int(on);
         for each(var saved:Object in this.p2Original) saved.slot.visible = false;
         for(i = 1; i <= 20; i++)
         {
            slot = this["mcPaperDollSlot" + i] as SlotPaperdoll;
            if(!slot) continue;
            slot.visible = on;
            var r:Rectangle = slot.getSlotRect();
            var cell:Number = Math.min(area.width / 5,area.height / 4);
            var factor:Number = Math.min(84,cell * 0.64) / Math.max(r.width,r.height);
            var point:Point = slot.parent.globalToLocal(this.parent.localToGlobal(new Point(area.x + (Number((i - 1) % 5) + 0.5) * area.width / 5,area.y + (Math.floor((i - 1) / 5) + 0.5) * area.height / 4)));
            slot.scaleX = slot.scaleY = factor;
            slot.x = point.x - (r.x + r.width / 2) * factor; slot.y = point.y - (r.y + r.height / 2) * factor;
            slot.iaiRedraw();
         }
         this.iaiNav();
      }
      public function p2Restore() : void
      {'''+restore+'''
      }
'''
    return p.add(t,'ModulePaperdoll',helper)
def slot(t):
    t=p.slot_base(t)
    return p.prefix(t,'protected function iaiDrawLess(','''         if(qfGearGrid && empty && !sel && (flags & 2) == 0) return;''')
def tooltip(t):return p.add(t,'TooltipInventory',code('Tooltip.asinc'))
TRANSFORMS={'SlotBase':slot,'SlotsListBase':p.slot_list,'SlotsListGrid':grid,'InventoryTabbedListModule':module,'ModulePaperdoll':paper,'ContextInfoManager':context,'TooltipInventory':tooltip,'MenuInventory':menu}
