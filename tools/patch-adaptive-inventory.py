"""Original Inventory v2 transforms, exclusively against the accepted v4 movie."""
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location('gear_patch', ROOT/'tools/patch-ink-gear-grid.py')
p = importlib.util.module_from_spec(s); s.loader.exec_module(p)

def snippet(name):
    return (ROOT/'src/inventory/adaptive'/name).read_text(encoding='utf-8')

def slot(text):
    text = p.slot_base(text)
    text = p.add(text, 'SlotBase', '      public static var qfAdaptiveTargets:Boolean = false;')
    # Invisible unused cells, retaining their selection, drag and grid objects.
    text = p.prefix(text, 'protected function iaiDrawLess(',
        '         if(qfGearGrid && empty && !sel && (flags & 2) == 0) return;')
    # Quiet, single selection frame; native equipped marker remains in iaiAfter.
    return p.prefix(text, 'protected function iaiDrawLess(', '''
         if(qfGearGrid && !this.iaiRound() && sel)
         {
            g.lineStyle((act ? 1.5 : 1) * k,0xC5B589,act ? 0.9 : 0.45,true,"none");
            g.beginFill(0xC5B589,0.035);
            g.drawRoundRect(r.x + 3*k,r.y + 3*k,r.width - 6*k,r.height - 6*k,6*k,6*k);
            g.endFill(); return;
         }''')

def paperdoll(text):
    text = p.paperdoll(text)
    # The original reusable adapter saves all 20 clips and decoration contracts.
    text = text.replace('var order:Array = targetMode ? gear.concat(utility) : utility;',
                        'var order:Array = targetMode ? gear.concat(utility) : [];')
    text = p.one(text, 'for each(i in gear)', 'for each(i in gear.concat(utility))')
    text = p.one(text, 'factor = 52 / Math.max(r.width,r.height);',
                       'factor = 72 / Math.max(r.width,r.height);')
    text = p.one(text, '786 + (i % (targetMode ? 5 : 7)) * 66,(targetMode ? 620 : 798) + Math.floor(i / (targetMode ? 5 : 7)) * 78',
                       '136 + (i % 5) * 100,272 + Math.floor(i / 5) * 126')
    return text

def tooltip(text):
    text = p.tooltip(text)
    return p.add(text, 'TooltipInventory', snippet('AdaptiveTooltip.asinc'))

def context(text):
    return p.prefix(text, 'protected function iaiPlaceDock()', '''
         if(SlotBase.qfGearGrid && TooltipInventory.iaiDock)
         {
            TooltipInventory.iaiDock = SlotBase.qfAdaptiveTargets ? new Rectangle(620,166,390,790) : new Rectangle(72,166,920,790);
            TooltipInventory.iaiPopSlot = null;
            TooltipInventory.iaiPopLeft = false;
            TooltipInventory.iaiPopFix = false;
            return;
         }''')

def menu(text):
    text = p.add(text, 'MenuInventory', snippet('AdaptiveMenu.asinc'))
    text = p.prefix(text, 'public function setInventoryMode(value:int)',
                    '         this.qfAdaptiveRestore();\n         this.mcPlayerInventory.qfAdaptivePlayer = false;')
    text = p.append(text, 'public function setInventoryMode(value:int)',
                    '         this.mcPlayerInventory.qfAdaptivePlayer = this.qfGearOn && value == IMS_Player;')
    text = p.append(text, 'protected function iaiTick(e:Event)',
                    '         this.qfAdaptiveRefresh();')
    text = p.prefix(text, 'protected function iaiPadCross(event:InputEvent)',
                    '         if(SlotBase.qfGearGrid) return;')
    return text

def tabs(text):
    text = p.add(text, 'InventoryTabbedListModule', '''
      protected var qfAdaptivePositions:Object = {};
      public var qfAdaptivePlayer:Boolean = false;
      protected var qfAdaptiveViewportBase:Object;
      public function qfAdaptiveViewport(on:Boolean) : void
      {
         if(on && !this.qfAdaptiveViewportBase && this.maskClip)
         {
            this.qfAdaptiveViewportBase = {height:this._gridRenderHeight,mask:this.maskClip.height};
            GTweener.removeTweens(this.maskClip);
            this._gridRenderHeight = 384;
            this.maskClip.height = 384 + this.gridMaskOffset;
            this.mcPlayerGrid.qfAdaptiveViewport(384);
         }
         else if(!on && this.qfAdaptiveViewportBase)
         {
            GTweener.removeTweens(this.maskClip);
            this._gridRenderHeight = this.qfAdaptiveViewportBase.height;
            this.maskClip.height = this.qfAdaptiveViewportBase.mask;
            this.qfAdaptiveViewportBase = null;
            this.mcPlayerGrid.qfAdaptiveViewport(0);
         }
      }
      public function qfAdaptiveContext() : String
      {
         if(currentlySelectedTabIndex == 4) return "Gear";
         if(currentlySelectedTabIndex == 3) return "Usables";
         return "Satchel";
      }
      protected function qfAdaptiveRemember() : void
      {
         if(!SlotBase.qfGearGrid) return;
         var s:SlotBase = this.mcPlayerGrid.getSelectedRenderer() as SlotBase;
         if(s && s.data) this.qfAdaptivePositions[String(currentlySelectedTabIndex)] = {id:s.data.id,scroll:this.mcPlayerGrid.scrollPosition};
      }
      protected function qfAdaptiveRecall(index:int) : void
      {
         var saved:Object = this.qfAdaptivePositions[String(index)];
         if(!this.qfAdaptivePlayer || index != 4 || !saved) return;
         var s:SlotInventoryGrid = this.mcPlayerGrid.getSlotByID(saved.id) as SlotInventoryGrid;
         if(s) { this.mcPlayerGrid.selectedIndex = s.index; this.mcPlayerGrid.scrollPosition = saved.scroll; }
      }
''')
    text = p.prefix(text, 'override protected function onTabListItemSelected(event:ListEvent)',
                    '         if(event.index != currentlySelectedTabIndex) this.qfAdaptiveRemember();')
    text = p.append(text, 'override protected function setSubData(index:int, data:Array)',
                    '         this.qfAdaptiveRecall(index);')
    return text

def grid(text):
    text = p.add(text, 'SlotsListGrid', '''
      protected var qfAdaptiveViewportBase:Object;
      public function qfAdaptiveViewport(h:Number) : void
      {
         if(h > 0 && !this.qfAdaptiveViewportBase)
         {
            this.qfAdaptiveViewportBase = {rows:this._rows,height:this._gridRenderHeight,visible:this._numRowsVisible};
            this._gridRenderHeight = h;
            this._numRowsVisible = this._rows = uint(h / this._gridSquareSize);
         }
         else if(h == 0 && this.qfAdaptiveViewportBase)
         {
            this._rows = this.qfAdaptiveViewportBase.rows;
            this._gridRenderHeight = this.qfAdaptiveViewportBase.height;
            this._numRowsVisible = this.qfAdaptiveViewportBase.visible;
            this.qfAdaptiveViewportBase = null;
         }
         this.removeUselessRows();
         this.updateRendererBounds();
         this.updateScrollBar();
         this.validateRenderersSpecial();
      }
''')
    for sig in ('override public function updateItems(itemsList:Array)',
                'override public function updateItemData(itemData:Object)'):
        text = p.prefix(text, sig, '''
         var qfSavedSlot:SlotBase = getSelectedRenderer() as SlotBase;
         var qfSavedId:Number = SlotBase.qfGearGrid && qfSavedSlot && qfSavedSlot.data ? Number(qfSavedSlot.data.id) : NaN;
         var qfSavedScroll:Number = scrollPosition;
''')
        text = p.append(text, sig, '''
         if(!isNaN(qfSavedId))
         {
            var qfNewIndex:int = getIdIndex(uint(qfSavedId));
            if(qfNewIndex >= 0) { selectedIndex = qfNewIndex; scrollPosition = qfSavedScroll; }
         }
''')
    return text

TRANSFORMS = {'SlotBase':slot,'SlotsListBase':p.slot_list,'ModulePaperdoll':paperdoll,
              'TooltipInventory':tooltip,'ContextInfoManager':context,
              'InventoryTabbedListModule':tabs,'SlotsListGrid':grid,'MenuInventory':menu}
