// Original private Gear-grid adapter. No settings writes or replaced native methods.
@addField(CR4InventoryMenu) var qfGearGridActive : bool;
@addField(W3GuiPlayerInventoryComponent) var qfGearGridActive : bool;
@addField(W3GuiPlayerInventoryComponent) var qfGearListing : bool;

@addMethod(CR4InventoryMenu)
function QfSetGearEnabled(on : bool)
{
    var flash : CScriptedFlashSprite;
    var callback : CScriptedFlashFunction;
    qfGearGridActive = on;
    if (_playerInv) _playerInv.qfGearGridActive = on;
    flash = GetMenuFlash();
    if (flash)
    {
        callback = flash.GetMemberFlashFunction("qfGearEnabled");
        if (callback) callback.InvokeSelfOneArg(FlashArgBool(on));
    }
}

@wrapMethod(CR4InventoryMenu)
function SetInitialTabNewFlags(out hasNewItems : array<bool>) : int
{
    QfSetGearEnabled(_defaultInventoryState == IMS_Player && m_tagsFilter.Size() == 0);
    return wrappedMethod(hasNewItems);
}

@wrapMethod(CR4InventoryMenu)
function SetInventoryState(targetMode : int) : void
{
    QfSetGearEnabled(targetMode == IMS_Player && m_tagsFilter.Size() == 0);
    wrappedMethod(targetMode);
}

// Preserve ALL existing quest/tag/category filters. Suppress only the equipped
// exclusion while the original ShouldShowItem queries its own isEquipped helper.
@wrapMethod(W3GuiPlayerInventoryComponent)
function ShouldShowItem(item : SItemUniqueId) : bool
{
    var previous : bool;
    var result : bool;
    previous = qfGearListing;
    qfGearListing = qfGearGridActive;
    result = wrappedMethod(item);
    qfGearListing = previous;
    return result;
}

@wrapMethod(W3GuiPlayerInventoryComponent)
function isEquipped(item : SItemUniqueId) : bool
{
    if (qfGearListing && (_inv.IsItemAnyArmor(item) || _inv.IsItemWeapon(item))) return false;
    return wrappedMethod(item);
}

@wrapMethod(W3GuiPlayerInventoryComponent)
function SetInventoryFlashObjectForItem(itemId : SItemUniqueId, out flashObject : CScriptedFlashObject) : void
{
    wrappedMethod(itemId, flashObject);
    if (qfGearGridActive) flashObject.SetMemberFlashBool("isEquipped", GetWitcherPlayer().IsItemEquipped(itemId));
}

// Native equip removes its former grid entry. Keep its real ID and refresh the
// actual equipped state instead; removed/dropped/consumed items use original path.
@wrapMethod(CR4InventoryMenu)
function InventoryRemoveItem(item : SItemUniqueId, optional keepSelectionIdx : bool)
{
    if (qfGearGridActive && _inv.IsIdValid(item) && GetWitcherPlayer().IsItemEquipped(item)
        && (_inv.IsItemAnyArmor(item) || _inv.IsItemWeapon(item))) InventoryUpdateItem(item);
    else wrappedMethod(item, keepSelectionIdx);
}

@wrapMethod(W3InventoryGridContext)
function execurePrimaryAction() : void
{
    if (invMenuRef && invMenuRef.qfGearGridActive && invComponentRef && invComponentRef.IsIdValid(currentItemId)
        && GetWitcherPlayer().IsItemEquipped(currentItemId)
        && (invComponentRef.IsItemAnyArmor(currentItemId) || invComponentRef.IsItemWeapon(currentItemId)))
        invMenuRef.OnUnequipItem(currentItemId, -1);
    else wrappedMethod();
}

@wrapMethod(W3InventoryGridContext)
function updateInputFeedback() : void
{
    var i : int;
    wrappedMethod();
    if (invMenuRef && invMenuRef.qfGearGridActive && invComponentRef && invComponentRef.IsIdValid(currentItemId)
        && GetWitcherPlayer().IsItemEquipped(currentItemId)
        && (invComponentRef.IsItemAnyArmor(currentItemId) || invComponentRef.IsItemWeapon(currentItemId)))
    {
        for (i = 0; i < m_inputBindings.Size(); i += 1)
            if (m_inputBindings[i].Gamepad_NavCode == "enter-gamepad_A")
                m_inputBindings[i].LocalizationKey = "panel_button_inventory_unequip";
        m_managerRef.updateInputFeedback();
    }
}
