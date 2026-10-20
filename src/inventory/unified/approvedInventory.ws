// Original unified player Inventory bridge. No saved fields/settings/dependencies.
@addField(CR4InventoryMenu) var aiApprovedActive : bool;
@addField(CR4InventoryMenu) var aiApprovedBusy : bool;
@addField(CR4InventoryMenu) var aiApprovedFocus : int;
@addField(W3GuiPlayerInventoryComponent) var aiApprovedProbe : bool;
@addField(W3PlayerWitcher) var aiApprovedTrace : bool;

// Low-volume bridge acknowledgements reach the opt-in movie overlay even when
// the per-item console trace flag is off. Normal movies discard this evidence.
@addMethod(CR4InventoryMenu)
function AiApprovedStatus(message : string)
{
    var callback : CScriptedFlashFunction;
    if(!GetMenuFlash())return;
    callback=GetMenuFlash().GetMemberFlashFunction("approvedEvidence");
    if(callback)callback.InvokeSelfOneArg(FlashArgString(message));
}

@addMethod(CR4InventoryMenu)
function AiApprovedEvidence(message : string)
{
    var callback : CScriptedFlashFunction;
    if (!GetWitcherPlayer().aiApprovedTrace || !GetMenuFlash()) return;
    callback=GetMenuFlash().GetMemberFlashFunction("approvedEvidence");
    if(callback)callback.InvokeSelfOneArg(FlashArgString(message));
    LogChannel('ApprovedInventory',message);
}

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
        callback = GetMenuFlash().GetMemberFlashFunction("approvedDiagnostics");
        if(callback)callback.InvokeSelfOneArg(FlashArgBool(GetWitcherPlayer().aiApprovedTrace));
        AiApprovedEvidence("AiApprovedEnable on="+on+" state="+_defaultInventoryState+" tags="+m_tagsFilter.Size());
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
event OnApprovedRefresh()
{
    var items : array<SItemUniqueId>;
    var filters : array<EInventoryFilterType>;
    var previous : EInventoryFilterType;
    var data : CScriptedFlashArray;
    var obj : CScriptedFlashObject;
    var holder : CScriptedFlashObject;
    var i,j,published,nativeCount,equippedCount : int;
    var eligible : bool;
    var nativeEligibility : string;
    var callback : CScriptedFlashFunction;
    AiApprovedStatus("refresh.request active="+aiApprovedActive+" busy="+aiApprovedBusy);
    if (!aiApprovedActive || aiApprovedBusy || !_playerInv) return false;
    aiApprovedBusy = true;
    callback=GetMenuFlash().GetMemberFlashFunction("approvedDiagnostics");
    if(callback)callback.InvokeSelfOneArg(FlashArgBool(GetWitcherPlayer().aiApprovedTrace));
    previous = _playerInv.GetFilterType();
    filters.PushBack(IFT_Ingredients); filters.PushBack(IFT_QuestItems);
    filters.PushBack(IFT_Default); filters.PushBack(IFT_AlchemyItems);
    filters.PushBack(IFT_Weapons); filters.PushBack(IFT_Books);
    _inv.GetAllItems(items);
    AiApprovedStatus("owned="+items.Size()+" filter.before="+previous);
    data = m_flashValueStorage.CreateTempFlashArray();
    holder = m_flashValueStorage.CreateTempFlashObject();
    _playerInv.aiApprovedProbe = true;
    for (i=0; i<items.Size(); i+=1)
    {
        if(GetWitcherPlayer().IsItemEquipped(items[i]))equippedCount+=1;
        if(GetWitcherPlayer().aiApprovedTrace)
        {
            // Read-only negative control: actual native eligibility without the
            // equipped-inclusion probe, against the original active filter.
            _playerInv.aiApprovedProbe=false;_playerInv.SetFilterType(previous);
            if(_playerInv.ShouldShowItem(items[i]))nativeCount+=1;
            nativeEligibility="";
            for(j=0;j<filters.Size();j+=1)
            {
                _playerInv.SetFilterType(filters[j]);
                nativeEligibility+=" "+j+":"+_playerInv.ShouldShowItem(items[i]);
            }
            _playerInv.aiApprovedProbe=true;
        }
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
            published+=1;
        }
        AiApprovedEvidence("item="+ItemToFlashUInt(items[i])+" equipped="+GetWitcherPlayer().IsItemEquipped(items[i])+" eligible="+eligible+" group="+_playerInv.AiApprovedGroup(items[i])+" native.filters="+nativeEligibility);
    }
    _playerInv.aiApprovedProbe = false;
    _playerInv.SetFilterType(previous);
    AiApprovedStatus("publish="+published+" equipped="+equippedCount+" filter.restored="+_playerInv.GetFilterType()+" probe="+_playerInv.aiApprovedProbe);
    m_flashValueStorage.SetFlashArray("inventory.approved.items",data);
    aiApprovedBusy = false;
    return true;
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
    if(invMenuRef)invMenuRef.AiApprovedEvidence("primary id="+ItemToFlashUInt(currentItemId)+" focus="+invMenuRef.aiApprovedFocus);
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
event OnApprovedMode(mode : int)
{
    var b : SKeyBinding;
    if (!aiApprovedActive) return false;
    aiApprovedFocus=mode;
    AiApprovedStatus("mode="+mode);
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
    return true;
}

// Same native provider as ShowItemTooltip, with a request serial to reject
// hover/old-equipment payloads in the retained persistent presentation.
@addMethod(CR4InventoryMenu)
event OnApprovedDetails(item : SItemUniqueId, serial : int)
{
    var payload : CScriptedFlashObject;
    AiApprovedStatus("details id="+ItemToFlashUInt(item)+" serial="+serial+" valid="+_inv.IsIdValid(item));
    if(!aiApprovedActive || !_inv.IsIdValid(item))return false;
    _tooltipDataProvider.setCurrentInventory(GetCurrentInventory(item));
    payload=_tooltipDataProvider.GetTooltipData(item,_currentInv==_shopInv,true);
    payload.SetMemberFlashInt("aiRequestSerial",serial);
    m_flashValueStorage.SetFlashObject("context.tooltip.data",payload);
    AiApprovedStatus("details.published serial="+serial);
    return true;
}

exec function approvedInventoryTrace(on : bool)
{
    var player : W3PlayerWitcher;
    player=GetWitcherPlayer();
    player.aiApprovedTrace=on;
}
