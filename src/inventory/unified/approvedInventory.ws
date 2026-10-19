// Original unified player Inventory bridge. No saved fields/settings/dependencies.
@addField(CR4InventoryMenu) var aiApprovedActive : bool;
@addField(CR4InventoryMenu) var aiApprovedBusy : bool;
@addField(CR4InventoryMenu) var aiApprovedFocus : int;
@addField(W3GuiPlayerInventoryComponent) var aiApprovedProbe : bool;
@addField(W3PlayerWitcher) var aiApprovedTrace : bool;

@addMethod(CR4InventoryMenu)
function AiApprovedEnable(on : bool)
{
    var callback : CScriptedFlashFunction;
    aiApprovedActive = on;
    if (!on)
    {
        RemoveGFxButtonById(89101); RemoveGFxButtonById(89102); RemoveGFxButtonById(89103);
        if(GetCommonMenu()) GetCommonMenu().UpdateGFxButtons(m_GFxInputBindings,true);
    }
    if (GetMenuFlash())
    {
        callback = GetMenuFlash().GetMemberFlashFunction("approvedEnabled");
        if (callback) callback.InvokeSelfOneArg(FlashArgBool(on));
    }
}
@wrapMethod(CR4InventoryMenu)
function SetInitialTabNewFlags(out flags : array<bool>) : int
{
    var result : int;
    result = wrappedMethod(flags);
    AiApprovedEnable(_defaultInventoryState == IMS_Player && m_tagsFilter.Size() == 0);
    return result;
}
@wrapMethod(CR4InventoryMenu)
function SetInventoryState(targetMode : int) : void
{
    AiApprovedEnable(targetMode == IMS_Player && m_tagsFilter.Size() == 0);
    wrappedMethod(targetMode);
}
@wrapMethod(W3GuiPlayerInventoryComponent)
function isEquipped(item : SItemUniqueId) : bool
{
    if (aiApprovedProbe) return false;
    return wrappedMethod(item);
}
@addMethod(W3GuiPlayerInventoryComponent)
function AiApprovedGroup(item : SItemUniqueId) : int
{
    var cat : name;
    var slot : EEquipmentSlots;
    cat = _inv.GetItemCategory(item);
    if (_inv.ItemHasTag(item, 'Quest')) return 6;
    if (_inv.IsItemHorseItem(item) || _inv.IsItemTrophy(item)) return 7;
    if (cat == 'dye' || _inv.ItemHasTag(item,'mod_dye')) return 5;
    if (cat == 'petard') return 4;
    if (cat == 'potion' || cat == 'oil' || _inv.IsItemFood(item)) return 3;
    if (_inv.IsItemAnyArmor(item)) return 2;
    if (_inv.IsItemWeapon(item) || _inv.IsItemBolt(item) || cat == 'crossbow') return 1;
    slot = _inv.GetSlotForItemId(item);
    if (cat != 'dye' && (cat == 'mask' || cat == 'tool' || cat == 'usable' || slot == EES_Quickslot1 || slot == EES_Quickslot2)) return 5;
    return 7;
}
@wrapMethod(W3GuiPlayerInventoryComponent)
function SetInventoryFlashObjectForItem(itemId : SItemUniqueId, out flashObject : CScriptedFlashObject) : void
{
    wrappedMethod(itemId,flashObject);
    if (aiApprovedProbe)
    {
        flashObject.SetMemberFlashString("itemName",GetLocStringByKeyExt(_inv.GetItemLocalizedNameByUniqueID(itemId)));
        flashObject.SetMemberFlashString("aiSubtitle",GetLocStringByKeyExt("item_category_" + NameToString(_inv.GetItemCategory(itemId))));
        flashObject.SetMemberFlashInt("aiGroup",AiApprovedGroup(itemId));
        flashObject.SetMemberFlashBool("isEquipped",GetWitcherPlayer().IsItemEquipped(itemId));
    }
}
@addMethod(CR4InventoryMenu)
function OnApprovedRefresh()
{
    var items : array<SItemUniqueId>;
    var filters : array<EInventoryFilterType>;
    var previous : EInventoryFilterType;
    var data : CScriptedFlashArray;
    var obj : CScriptedFlashObject;
    var holder : CScriptedFlashObject;
    var i,j : int;
    var eligible : bool;
    var callback : CScriptedFlashFunction;
    if (!aiApprovedActive || aiApprovedBusy || !_playerInv) return;
    aiApprovedBusy = true;
    callback=GetMenuFlash().GetMemberFlashFunction("approvedDiagnostics");
    if(callback)callback.InvokeSelfOneArg(FlashArgBool(GetWitcherPlayer().aiApprovedTrace));
    previous = _playerInv.GetFilterType();
    filters.PushBack(IFT_Ingredients); filters.PushBack(IFT_QuestItems);
    filters.PushBack(IFT_Default); filters.PushBack(IFT_AlchemyItems);
    filters.PushBack(IFT_Weapons); filters.PushBack(IFT_Books);
    _inv.GetAllItems(items);
    data = m_flashValueStorage.CreateTempFlashArray();
    holder = m_flashValueStorage.CreateTempFlashObject();
    _playerInv.aiApprovedProbe = true;
    for (i=0; i<items.Size(); i+=1)
    {
        eligible = false;
        for (j=0; j<filters.Size(); j+=1)
        {
            _playerInv.SetFilterType(filters[j]);
            if (_playerInv.ShouldShowItem(items[i])) { eligible=true; break; }
        }
        if (eligible)
        {
            obj = holder.CreateFlashObject("red.game.witcher3.menus.common.ItemDataStub");
            _playerInv.SetInventoryFlashObjectForItem(items[i],obj);
            data.PushBackFlashObject(obj);
        }
    }
    _playerInv.aiApprovedProbe = false;
    _playerInv.SetFilterType(previous);
    m_flashValueStorage.SetFlashArray("inventory.approved.items",data);
    aiApprovedBusy = false;
}
// Retain true item IDs on native equip removal, including non-weapon slots.
@wrapMethod(CR4InventoryMenu)
function InventoryRemoveItem(item : SItemUniqueId, optional keepSelectionIdx : bool)
{
    if (aiApprovedActive && _inv.IsIdValid(item) && GetWitcherPlayer().IsItemEquipped(item)) InventoryUpdateItem(item);
    else wrappedMethod(item,keepSelectionIdx);
}
@wrapMethod(W3InventoryGridContext)
function execurePrimaryAction() : void
{
    if(invMenuRef && invMenuRef.aiApprovedActive && invMenuRef.aiApprovedFocus!=1)return;
    if (invMenuRef && invMenuRef.aiApprovedActive && invComponentRef && invComponentRef.IsIdValid(currentItemId)
        && GetWitcherPlayer().IsItemEquipped(currentItemId)
        && (invComponentRef.IsItemAnyArmor(currentItemId) || invComponentRef.IsItemWeapon(currentItemId)))
        invMenuRef.OnUnequipItem(currentItemId,-1);
    else wrappedMethod();
}
@wrapMethod(W3InventoryGridContext)
function updateInputFeedback() : void
{
    var i : int;
    wrappedMethod();
    if(invMenuRef && invMenuRef.aiApprovedActive && invMenuRef.aiApprovedFocus!=1)
    {
        m_inputBindings.Clear();m_contextBindings.Clear();m_managerRef.updateInputFeedback();return;
    }
    if (invMenuRef && invMenuRef.aiApprovedActive && invComponentRef && invComponentRef.IsIdValid(currentItemId)
        && GetWitcherPlayer().IsItemEquipped(currentItemId)
        && (invComponentRef.IsItemAnyArmor(currentItemId) || invComponentRef.IsItemWeapon(currentItemId)))
    {
        for(i=0;i<m_inputBindings.Size();i+=1)
            if(m_inputBindings[i].Gamepad_NavCode=="enter-gamepad_A") m_inputBindings[i].LocalizationKey="panel_button_inventory_unequip";
        m_managerRef.updateInputFeedback();
    }
}
// Feed the actual Common menu pipeline. Context actions remain native.
@addMethod(CR4InventoryMenu)
function OnApprovedMode(mode : int)
{
    var b : SKeyBinding;
    if (!aiApprovedActive) return;
    aiApprovedFocus=mode;
    if(m_currentContext)m_currentContext.UpdateContext();
    RemoveGFxButtonById(89101); RemoveGFxButtonById(89102); RemoveGFxButtonById(89103);
    b.ActionID=89101; b.Gamepad_NavCode="gamepad_L3"; b.Keyboard_KeyCode=IK_Tab;
    b.LocalizationKey="Equipment"; b.IsLocalized=true;
    m_GFxInputBindings.PushBack(b);
    b.ActionID=89102; b.Gamepad_NavCode="back"; b.Keyboard_KeyCode=IK_I;
    b.LocalizationKey="Details"; b.IsLocalized=true;
    m_GFxInputBindings.PushBack(b);
    if(mode==1)
    {
        b.ActionID=89103;b.Gamepad_NavCode="";b.Keyboard_KeyCode=IK_Q;
        b.LocalizationKey="panel_button_common_quick_sort_items";b.IsLocalized=false;
        m_GFxInputBindings.PushBack(b);
    }
    if(GetCommonMenu()) GetCommonMenu().UpdateGFxButtons(m_GFxInputBindings,true);
}

// Same native provider as ShowItemTooltip, with a request serial to reject
// hover/old-equipment payloads in the retained persistent presentation.
@addMethod(CR4InventoryMenu)
function OnApprovedDetails(item : SItemUniqueId, serial : int)
{
    var payload : CScriptedFlashObject;
    if(!aiApprovedActive || !_inv.IsIdValid(item))return;
    _tooltipDataProvider.setCurrentInventory(GetCurrentInventory(item));
    payload=_tooltipDataProvider.GetTooltipData(item,_currentInv==_shopInv,true);
    payload.SetMemberFlashInt("aiRequestSerial",serial);
    m_flashValueStorage.SetFlashObject("context.tooltip.data",payload);
}

exec function approvedInventoryTrace(on : bool)
{
    var player : W3PlayerWitcher;
    player=GetWitcherPlayer();
    player.aiApprovedTrace=on;
}
