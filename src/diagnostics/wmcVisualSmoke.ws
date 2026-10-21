// Optional, finite UI liveness diagnostic. No saved data, logging or audio calls.
// At most two notifications per CR4Game instance; no continuous observer.
@addField(CR4Game)
var wmcVisualSmokeMessages : int;

@addField(CR4Player)
var wmcVisualSmokeTicks : int;

@addMethod(CR4Game)
function WMCVisualSmokeMarkMessage()
{
    wmcVisualSmokeMessages += 1;
}

@addMethod(CR4Player)
function WMCVisualSmokeBegin()
{
    RemoveTimer('WMCVisualSmokeTick');
    wmcVisualSmokeTicks = 0;
    AddTimer('WMCVisualSmokeTick', 1.0, true);
}

@addMethod(CR4Player)
timer function WMCVisualSmokeTick(dt : float, id : int)
{
    var row : string;
    var travel : string;
    wmcVisualSmokeTicks += 1;
    if(wmcVisualSmokeTicks > 30 || theGame.wmcVisualSmokeMessages >= 2)
    {
        RemoveTimer('WMCVisualSmokeTick');
        return;
    }
    if(wmcVisualSmokeTicks < 3 || !theGame.GetGuiManager() || !theSound ||
       !theGame.GetCommonMapManager() || !theGame.envMgr) return;
    if(theGame.IsPaused() || theGame.IsDialogOrCutscenePlaying() ||
       theGame.IsLoadingScreenVideoPlaying()) return;
    if(theGame.wmcVisualSmokeMessages == 0)
    {
        theGame.GetGuiManager().ShowNotification("WMCVIS1 begin - diagnostic active", 4.0, false);
        theGame.WMCVisualSmokeMarkMessage();
        // Allow the first message to finish even if GUI readiness was delayed.
        wmcVisualSmokeTicks = 3;
        return;
    }
    if(wmcVisualSmokeTicks < 10) return;
    travel = "foot";
    if(IsUsingHorse(true)) travel = "horse";
    if(IsUsingBoat()) travel = "boat";
    row = "WMCVIS1 snapshot | region=" + theGame.GetCommonMapManager().GetCurrentArea() +
        " | state=" + theSound.GetCurrentGameState() + " | combat=" + ShouldEnableCombatMusic() +
        " | night=" + theGame.envMgr.IsNight() + " | travel=" + travel +
        " | owner/outro=unknown";
    theGame.GetGuiManager().ShowNotification(row, 12.0, false);
    theGame.WMCVisualSmokeMarkMessage();
    RemoveTimer('WMCVisualSmokeTick');
}

@wrapMethod(CR4Game)
function OnAfterLoadingScreenGameStart()
{
    wrappedMethod();
    if(thePlayer && wmcVisualSmokeMessages < 2)
    {
        thePlayer.WMCVisualSmokeBegin();
    }
}
