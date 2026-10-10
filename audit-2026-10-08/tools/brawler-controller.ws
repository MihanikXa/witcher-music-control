// Original compatibility controller; no school selection or animation multiplier.
// Non-saved state deliberately starts neutral after load or input reconstruction.
@addField(CR4Player) var compatBrawlerEnabled : bool;
@addField(CR4Player) var compatBrawlerPending : bool;
@addField(CR4Player) var compatBrawlerDesired : bool;
@addField(CPlayerInput) var compatBrawlerKeyHeld : bool;

@addMethod(CR4Player)
function CompatBrawlerContextAllowed() : bool
{
    var stateName : name;
    if(this != GetWitcherPlayer() || IsCiri() || !IsAlive()) return false;
    if(IsUsingVehicle() || IsOnBoat() || IsSwimming() || IsInAir()
        || IsInsideInteraction() || IsInFistFightMiniGame()) return false;
    if(theGame.IsFading() || theGame.IsBlackscreen() || theGame.IsFocusModeActive()) return false;
    stateName = GetCurrentStateName();
    return stateName == 'Exploration' || stateName == 'CombatSteel'
        || stateName == 'CombatSilver' || stateName == 'CombatFists' || stateName == 'Combat';
}

@addMethod(CR4Player)
function CompatBrawlerActive() : bool
{
    return compatBrawlerEnabled && CompatBrawlerContextAllowed();
}

@addMethod(CR4Player)
function CompatBrawlerClear()
{
    compatBrawlerEnabled = false;
    compatBrawlerPending = false;
    compatBrawlerDesired = false;
    RemoveTimer('CompatBrawlerTick');
}

@addMethod(CR4Player)
function CompatBrawlerToggle()
{
    if(!CompatBrawlerContextAllowed()) return;
    if(compatBrawlerPending) compatBrawlerDesired = !compatBrawlerDesired;
    else compatBrawlerDesired = !compatBrawlerEnabled;
    compatBrawlerPending = true;
    RemoveTimer('CompatBrawlerTick');
    AddTimer('CompatBrawlerTick', 0.1f, true);
    CompatBrawlerTick(0.f, 0);
}

@addMethod(CR4Player)
timer function CompatBrawlerTick(dt : float, id : int)
{
    if(!CompatBrawlerContextAllowed()) { CompatBrawlerClear(); return; }
    if(!compatBrawlerPending) return;
    // Do not cancel an accepted attack, evade, finisher or blocked weapon transition.
    if(IsInCombatAction() || IsCurrentlyDodging() || isInFinisher
        || !IsActionAllowed(EIAB_DrawWeapon)) return;
    compatBrawlerEnabled = compatBrawlerDesired;
    compatBrawlerPending = false;
    if(compatBrawlerEnabled && GetCurrentMeleeWeaponType() != PW_Fists)
        OnEquipMeleeWeapon(PW_Fists, true, true);
    // Normal mode leaves native/B&S weapon selection authoritative; no forced sword.
    if(!compatBrawlerEnabled) RemoveTimer('CompatBrawlerTick');
}

@wrapMethod(CPlayerInput)
function Initialize(isFromLoad : bool, optional previousInput : CPlayerInput)
{
    wrappedMethod(isFromLoad, previousInput);
    compatBrawlerKeyHeld = false;
    if(thePlayer) thePlayer.CompatBrawlerClear();
    theInput.UnregisterListener(this, 'CompatBrawlerToggle');
    theInput.RegisterListener(this, 'OnCompatBrawlerToggle', 'CompatBrawlerToggle');
}

@addMethod(CPlayerInput)
event OnCompatBrawlerToggle(action : SInputAction)
{
    if(IsReleased(action)) { compatBrawlerKeyHeld = false; return true; }
    if(IsPressed(action) && !compatBrawlerKeyHeld)
    {
        compatBrawlerKeyHeld = true;
        if(thePlayer && (theInput.GetContext() == 'Combat' || theInput.GetContext() == 'Exploration'))
            thePlayer.CompatBrawlerToggle();
        return true;
    }
    return false;
}

// Retain exploration timing cleanup at the original accepted-action boundaries.
@wrapMethod(CR4Player)
function OnCombatActionStart()
{
    if(this == GetWitcherPlayer() && defaultLocomotionController)
        ResponsiveMovementEndTransitionAnimation(defaultLocomotionController);
    wrappedMethod();
}

@wrapMethod(CR4Player)
function SetIsCurrentlyDodging(enable : bool, optional isRolling : bool)
{
    wrappedMethod(enable, isRolling);
    if(enable && this == GetWitcherPlayer() && defaultLocomotionController)
        ResponsiveMovementEndTransitionAnimation(defaultLocomotionController);
}

@wrapMethod(WeaponHolster)
function GetMostConvenientMeleeWeapon(targetToDrawAgainst : CActor, optional ignoreActionLock : bool) : EPlayerWeapon
{
    var p : CR4Player;
    p = GetWitcherPlayer();
    if(p && p.GetWeaponHolster() == this && p.CompatBrawlerActive()) return PW_Fists;
    return wrappedMethod(targetToDrawAgainst, ignoreActionLock);
}

@wrapMethod(CR4Player)
function GetMostConvenientMeleeWeapon(targetToDrawAgainst : CActor, optional ignoreActionLock : bool) : EPlayerWeapon
{
    if(CompatBrawlerActive()) return PW_Fists;
    return wrappedMethod(targetToDrawAgainst, ignoreActionLock);
}
