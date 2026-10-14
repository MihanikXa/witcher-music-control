// Original temporary radial diagnostic. No forced opening or input gate changes.
@addField(CR4ScriptedHud)
var qfRadialMonitorReady : bool;

@addMethod(CR4ScriptedHud)
function QfRadialTraceNative(message : string)
{
    var movie : CScriptedFlashSprite;
    var report : CScriptedFlashFunction;
    LogChannel('GWINT_AI', "[QFR] " + message);
    movie = GetHudFlash();
    if (!movie) return;
    report = movie.GetMemberFlashFunction("qfRadialTrace");
    if (report) report.InvokeSelfOneArg(FlashArgString(message));
}

@wrapMethod(CR4ScriptedHud)
function OnConfigUI()
{
    QfRadialTraceNative("WS HUD OnConfigUI enter");
    wrappedMethod();
    QfRadialTraceNative("WS HUD OnConfigUI exit");
}

@addField(CR4ScriptedHud)
var qfRadialProbeSeconds : float;
@addField(CR4ScriptedHud)
var qfRadialStatusSent : bool;

@addField(CR4HudModuleRadialMenu)
var qfRadialConfigEntered : bool;
@addField(CR4HudModuleRadialMenu)
var qfRadialConfigCompleted : bool;

@addMethod(CR4HudModuleRadialMenu)
function QfRadialDiagnosticStatus() : string
{
    return "configEnter=" + (string)qfRadialConfigEntered + " configDone=" + (string)qfRadialConfigCompleted + " shown=" + (string)m_shown;
}

@addMethod(CR4ScriptedHud)
function QfRadialProbeStatus()
{
    var radial : CR4HudModuleRadialMenu;
    radial = (CR4HudModuleRadialMenu)GetHudModule("RadialMenuModule");
    if (radial) QfRadialTraceNative("WS radial status " + radial.QfRadialDiagnosticStatus());
    else QfRadialTraceNative("WS radial status MODULE ABSENT");
}

@wrapMethod(CR4ScriptedHud)
function OnTick(timeDelta : float)
{
    var result : bool;
    result = wrappedMethod(timeDelta);
    if (!qfRadialMonitorReady)
    {
        qfRadialMonitorReady = true;
        theInput.RegisterListener(this, 'QfRadialProbeInput', 'RadialMenu');
        QfRadialTraceNative("WS independent RadialMenu monitor ready");
    }
    qfRadialProbeSeconds += timeDelta;
    if (!qfRadialStatusSent && qfRadialProbeSeconds >= 2.0)
    {
        qfRadialStatusSent = true;
        QfRadialProbeStatus();
    }
    return result;
}

@addMethod(CR4ScriptedHud)
function QfRadialProbeInput(action : SInputAction) : bool
{
    if (IsPressed(action))
    {
        QfRadialTraceNative("WS input RadialMenu pressed (independent monitor)");
        QfRadialProbeStatus();
    }
    return false;
}

@wrapMethod(CR4HudModuleRadialMenu)
function OnConfigUI()
{
    var hud : CR4ScriptedHud;
    hud = (CR4ScriptedHud)theGame.GetHud();
    qfRadialConfigEntered = true;
    if (hud) hud.QfRadialTraceNative("WS radial OnConfigUI enter");
    wrappedMethod();
    qfRadialConfigCompleted = true;
    if (hud) hud.QfRadialTraceNative("WS radial OnConfigUI exit: listeners registered");
}

@wrapMethod(CR4HudModuleRadialMenu)
function OnRadialMenu(action : SInputAction)
{
    var hud : CR4ScriptedHud;
    hud = (CR4ScriptedHud)theGame.GetHud();
    if (IsPressed(action) && hud)
    {
        hud.QfRadialTraceNative("WS radial OnRadialMenu pressed");
        if (m_shown) hud.QfRadialTraceNative("WS gate: already shown");
        if (!thePlayer.IsActionAllowed(EIAB_RadialMenu)) hud.QfRadialTraceNative("WS gate: radial action disallowed");
        if (theGame.IsDialogOrCutscenePlaying()) hud.QfRadialTraceNative("WS gate: dialogue/cutscene");
        if (theGame.IsBlackscreenOrFading()) hud.QfRadialTraceNative("WS gate: blackscreen/fade");
        if (!thePlayer.GetBIsInputAllowed() && !GetWitcherPlayer().IsUITakeInput()) hud.QfRadialTraceNative("WS gate: input denied");
    }
    return wrappedMethod(action);
}

@wrapMethod(CR4HudModuleRadialMenu)
function ShowRadialMenu()
{
    var hud : CR4ScriptedHud;
    hud = (CR4ScriptedHud)theGame.GetHud();
    if (hud) hud.QfRadialTraceNative("WS ShowRadialMenu enter shown=" + (string)m_shown);
    wrappedMethod();
    if (hud) hud.QfRadialTraceNative("WS ShowRadialMenu exit shown=" + (string)m_shown);
}

@wrapMethod(CR4ScriptedHud)
function OnRadialOpened()
{
    QfRadialTraceNative("WS HUD OnRadialOpened enter");
    wrappedMethod();
    QfRadialTraceNative("WS HUD OnRadialOpened exit");
}
