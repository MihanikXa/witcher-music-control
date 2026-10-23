// V2: notification durations are milliseconds, not timer seconds.
// Optional, finite UI liveness diagnostic. No saved data, logging or audio calls.
// At most two notifications per CR4Game instance; no continuous observer.
@addField(CR4Game)
var wmcVisualSmokeV2Messages : int;

@addField(CR4Player)
var wmcVisualSmokeV2Ticks : int;

@addMethod(CR4Game)
function WMCVisualSmokeV2MarkMessage()
{
    wmcVisualSmokeV2Messages += 1;
}

@addMethod(CR4Player)
function WMCVisualSmokeV2Begin()
{
    RemoveTimer('WMCVisualSmokeV2Tick');
    wmcVisualSmokeV2Ticks = 0;
    AddTimer('WMCVisualSmokeV2Tick', 1.0, true);
}

@addMethod(CR4Player)
timer function WMCVisualSmokeV2Tick(dt : float, id : int)
{
    var row : string;
    var travel : string;
    wmcVisualSmokeV2Ticks += 1;
    if(wmcVisualSmokeV2Ticks > 30 || theGame.wmcVisualSmokeV2Messages >= 2)
    {
        RemoveTimer('WMCVisualSmokeV2Tick');
        return;
    }
    if(wmcVisualSmokeV2Ticks < 3 || !theGame.GetGuiManager() || !theSound ||
       !theGame.GetCommonMapManager() || !theGame.envMgr) return;
    if(theGame.IsPaused() || theGame.IsDialogOrCutscenePlaying() ||
       theGame.IsLoadingScreenVideoPlaying()) return;
    if(theGame.wmcVisualSmokeV2Messages == 0)
    {
        theGame.GetGuiManager().ShowNotification("WMCVIS2 begin - diagnostic active", 4000.0, false);
        theGame.WMCVisualSmokeV2MarkMessage();
        // Allow the first message to finish even if GUI readiness was delayed.
        wmcVisualSmokeV2Ticks = 3;
        return;
    }
    if(wmcVisualSmokeV2Ticks < 10) return;
    travel = "foot";
    if(IsUsingHorse(true)) travel = "horse";
    if(IsUsingBoat()) travel = "boat";
    row = "WMCVIS2 snapshot | region=" + theGame.GetCommonMapManager().GetCurrentArea() +
        " | state=" + theSound.GetCurrentGameState() + " | combat=" + ShouldEnableCombatMusic() +
        " | night=" + theGame.envMgr.IsNight() + " | travel=" + travel +
        " | owner/outro=unknown";
    theGame.GetGuiManager().ShowNotification(row, 12000.0, false);
    theGame.WMCVisualSmokeV2MarkMessage();
    RemoveTimer('WMCVisualSmokeV2Tick');
}

@wrapMethod(CR4Game)
function OnAfterLoadingScreenGameStart()
{
    wrappedMethod();
    if(thePlayer && wmcVisualSmokeV2Messages < 2)
    {
        thePlayer.WMCVisualSmokeV2Begin();
    }
}
