"""Original unified Inventory transforms, applied only to pinned accepted v4."""
import importlib.util,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=load('patch-ink-gear-grid')
def code(name):return (ROOT/'src/inventory/unified'/name).read_text(encoding='utf-8-sig')
def imports(t,*names):
    at=t.index('\n   public ')
    missing=''.join('   import '+n+';\n' for n in names if 'import '+n+';' not in t)
    return t[:at]+'\n'+missing+t[at:]
def scoped(t,sig,old,new):
    a,z=p.trace.body_span(t,sig);return t[:a]+p.one(t[a:z],old,new)+t[z:]
def menu(t):
    t=imports(t,'red.game.witcher3.slots.SlotsListGrid','red.game.witcher3.constants.InventorySlotType','red.game.witcher3.menus.common.ItemDataStub','flash.geom.Matrix','flash.geom.ColorTransform','flash.display.Bitmap','flash.display.BitmapData','flash.display.Shape','scaleform.clik.events.ListEvent','scaleform.clik.ui.InputDetails','scaleform.clik.constants.InputValue','scaleform.clik.constants.NavigationCode','scaleform.clik.core.InputDelegate','red.game.witcher3.events.ControllerChangeEvent')
    t=p.add(t,'MenuInventory',code('Scene.asinc'))
    t=p.prefix(t,'public function setInventoryMode(value:int)','         if(aiActive && value==IMS_Player)return;\n         if(value!=IMS_Player)aiLeave();')
    t=p.prefix(t,'protected function iaiTick(e:Event)','         if(aiActive){aiTick();return;}')
    t=p.append(t,'protected function iaiTick(e:Event)','         aiTick();')
    t=p.prefix(t,'protected function iaiPadCross(event:InputEvent)','         if(aiActive)return;')
    t=p.prefix(t,'protected function iaiArtLoad(key:String)','         if(aiActive)return;')
    t=p.prefix(t,'override public function setCurrentModule(value:int)', '''
         if(aiActive)
         {
            super.setCurrentModule(value);
            if(value==0)mcPlayerInventory.focused=1;
            return;
         }''')
    t=p.append(t,'private function sortingModeClosed()', '         if(aiActive)aiMode(aiFocus);')
    t=p.append(t,'private function handleCharStatsShown(', '''
         if(aiActive)
         {
            InputFeedbackManager.removeButton(this,89101);
            InputFeedbackManager.removeButton(this,89102);
            InputFeedbackManager.removeButton(this,89103);
         }''')
    t=p.append(t,'private function handleCharStatHidden(', '''
         if(aiActive)
         {
            aiDevice(null);
            if(_btn_sort_id!=-1)InputFeedbackManager.removeButton(this,_btn_sort_id);
            _btn_sort_id=InputFeedbackManager.appendButton(this,NavigationCode.GAMEPAD_RSTICK_HOLD,KeyCode.F,"panel_button_common_sort_items");
            aiMode(aiFocus);
         }''')
    t=p.prefix(t,'private function handleSortClick(', '         if(aiActive){aiSortCurrent();return;}')
    t=p.prefix(t,'protected function iaiSortContainer(mode:int)','         if(aiActive){mcPlayerInventory.mcPlayerGrid.setCurrentSort(mode);aiSortCurrent();return;}')
    t=scoped(t,'private function sortingModeApply(', 'this.mcPlayerInventory.mcPlayerGrid.selectedIndex = -1;', 'if(!aiActive)this.mcPlayerInventory.mcPlayerGrid.selectedIndex = -1;')
    # Register the one projection binding alongside the existing root bindings.
    t=p.append(t,'protected function initDataBindings()', '         dispatchEvent(new GameEvent(GameEvent.REGISTER,"inventory.approved.items",[aiData]));')
    return t
def slot(t):
    t=imports(t,'flash.text.TextField','flash.text.TextFormat','flash.utils.getTimer','red.game.witcher3.menus.common.ItemDataStub')
    t=p.add(p.slot_base(t),'SlotBase',code('Row.asinc'))
    t=p.prefix(t,'public function getSlotRect()', '         if(aiRow)return new Rectangle(0,0,338,90);')
    t=p.prefix(t,'protected function iaiDrawLess(', '         if(aiRow){aiPaintRow(g,r,k,sel,flags);return;}')
    t=p.prefix(t,'protected function handleIconLoaded(event:Event)', '         if(aiRow && event.currentTarget!=_imageLoader){aiLog("stale-icon");return;}')
    t=p.prefix(t,'protected function fitImage(', '         if(aiRow){aiFormatRow();return;}')
    t=p.append(t,'protected function loadIcon(iconPath:String)', '         if(aiRow){_loadedImagePath=iconPath;aiLog("icon-load",iconPath);}')
    t=p.append(t,'protected function updateData()', '         if(aiRow)aiFormatRow();')
    return t
def inventory_slot(t):
    t=p.prefix(t,'override protected function updateSize()', '         if(aiRow){aiFormatRow();return;}')
    return p.append(t,'override protected function updateData()', '         if(aiRow)aiFormatRow();')
def base(t):
    t=p.prefix(t,'public function set data(value:Array)', '         if(this is SlotsListGrid && SlotsListGrid(this).aiRows){SlotsListGrid(this).aiNeedData();return;}')
    return p.prefix(t,'public function clearRenderers()', '         if(this is SlotsListGrid && SlotsListGrid(this).aiRows)return;')
def grid(t):
    t=imports(t,'red.game.witcher3.menus.common.ItemDataStub')
    t=p.add(t,'SlotsListGrid',code('List.asinc'))
    for sig in ('override protected function populateData()', 'public function setItemSections(', 'protected function saveItemPosition(', 'protected function handleSlotChanged(', 'public function set offset(', 'protected function updateScrollBar(', 'private function cleanUpRenderers('):
        t=p.prefix(t,sig,'         if(aiRows)return;')
    for sig in ('override public function updateItems(', 'override public function updateItemData(', 'override public function removeItem('):
        t=p.prefix(t,sig,'         if(aiRows){aiNeedData();return;}')
    t=p.prefix(t,'override public function applySelectionContext()', '         if(aiRows){super.applySelectionContext();return;}')
    t=p.prefix(t,'protected function onScroll(', '         if(aiRows)return;')
    t=p.prefix(t,'public function processOver(avatar:SlotDragAvatar)', '''
         if(aiRows)
         {
            _currentDropRenderer=null;
            var aiSource:IInventorySlot=avatar?avatar.getSourceContainer() as IInventorySlot:null;
            return aiSource is SlotPaperdoll?SlotDragAvatar.ACTION_GRID_DROP:SlotDragAvatar.ACTION_NONE;
         }''')
    t=p.prefix(t,'public function canDrop(dragData:IDragTarget)', '         if(aiRows)return dragData is SlotPaperdoll;')
    t=p.prefix(t,'public function applyDrop(dragData:IDragTarget)', '''
         if(aiRows)
         {
            if(dragData is SlotPaperdoll)
            {
               var aiDrop:Object=dragData.getDragData();
               if(aiDrop)dispatchEvent(new GameEvent(GameEvent.CALL,"OnUnequipItem",[uint(aiDrop.id),-1]));
            }
            aiNeedData();return;
         }''')
    t=p.prefix(t,'public function handleInputNavSimple(', '         if(aiRows)return;') if 'public function handleInputNavSimple(' in t else t
    return t
def module(t):
    t=imports(t,'flash.geom.Rectangle')
    t=p.add(t,'InventoryTabbedListModule',code('Module.asinc'))
    for sig in ('protected function iaiDrawTabs(', 'protected function iaiClampTabs(', 'override protected function onTabListItemSelected(', 'public function setItemSections('):
        t=p.prefix(t,sig,'         if(aiModuleBase)return;')
    for sig in ('protected function handleItemUpdate(', 'protected function handleItemsUpdate('):
        t=p.prefix(t,sig,'         if(aiModuleBase){mcPlayerGrid.aiNeedData();return;}')
    for sig in ('override protected function ApplyOpenAnimationToMask(', 'override protected function ApplyCloseAnimationToMask(', 'public function forceSelectItem('):
        t=p.prefix(t,sig,'         if(aiModuleBase)return;')
    return t
def context(t):
    t=p.add(t,'ContextInfoManager','''
      public static var aiUnified:Boolean=false;
      public static var aiNativeTargets:Boolean=false;
      public static var aiPayload:Object;
''')
    t=p.prefix(t,'public function dataReceiver(value:Object)', '''
         if(aiUnified && !aiNativeTargets && value && value.ItemId!=null)
         {removeCurrentTooltip();aiPayload=value;dispatchEvent(new Event("approvedPayload"));return;}''')
    t=p.prefix(t,'protected function showTooltip(', '         if(aiUnified && !aiNativeTargets)return;')
    t=imports(t,'red.game.witcher3.managers.SlotsTransferManager')
    return t
def tooltip(t):
    t=p.add(t,'TooltipInventory',code('Details.asinc'))
    a,z=p.trace.body_span(t,'protected function iaiDecorate()')
    body=t[a:z].replace('104 * k','(aiPersistent ? 0 : 104) * k')
    t=t[:a]+body+t[z:]
    t=p.append(t,'protected function iaiDecorate()', '''
         if(aiPersistent){if(iaiDeco)iaiDeco.graphics.clear();if(iaiIconBox)iaiIconBox.visible=false;if(btnCompareHint)btnCompareHint.visible=false;}''')
    return t
def paper(t):
    # Reuse only original native target snapshot/restore, never P2 gallery/scene.
    old=load('patch-inventory-p2')
    return old.paper(t).replace('p2Original','aiOriginal').replace('p2LastMode','aiLastMode').replace('p2Targets','aiTargets').replace('p2Restore','aiRestore')
TRANSFORMS={'SlotBase':slot,'SlotInventoryGrid':inventory_slot,'SlotsListBase':base,'SlotsListGrid':grid,'InventoryTabbedListModule':module,'ModulePaperdoll':paper,'ContextInfoManager':context,'TooltipInventory':tooltip,'MenuInventory':menu}
