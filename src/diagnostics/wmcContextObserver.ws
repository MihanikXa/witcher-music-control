// Optional log-only diagnostic. No saved fields, music calls or decisions.
// Native LogChannel delivery/file sink in retail still requires user validation.
@addField(CR4Game)
var wmcContextEpochCounter : int;

@addMethod(CR4Game)
function WMCContextNextEpoch() : int
{
    wmcContextEpochCounter += 1;
    return wmcContextEpochCounter;
}

@addField(CR4Player)
var wmcContextEpoch : int;
@addField(CR4Player)
var wmcContextRows : int;
@addField(CR4Player)
var wmcContextSequence : int;
@addField(CR4Player)
var wmcContextStarted : float;
@addField(CR4Player)
var wmcContextPrevious : string;
@addField(CR4Player)
var wmcContextHeartbeat : float;
@addField(CR4Player)
var wmcContextDiscoveries : array<name>;

@addMethod(CR4Player)
function WMCContextBegin()
{
    RemoveTimer('WMCContextSample');
    wmcContextEpoch = theGame.WMCContextNextEpoch();
    wmcContextRows = 0;
    wmcContextSequence = 0;
    wmcContextStarted = theGame.GetEngineTimeAsSeconds();
    wmcContextPrevious = "";
    wmcContextHeartbeat = 0;
    wmcContextDiscoveries.Clear();
    WMCContextEmit("begin|origin=load_or_spawn");
    AddTimer('WMCContextSample', 1.0, true);
}

@addMethod(CR4Player)
function WMCContextEmit(payload : string)
{
    if(wmcContextRows >= 600) return;
    wmcContextRows += 1;
    wmcContextSequence += 1;
    LogChannel('WMCContext', "WMCCTX1|epoch=" + wmcContextEpoch + "|seq=" + wmcContextSequence +
        "|t=" + (theGame.GetEngineTimeAsSeconds() - wmcContextStarted) + "|" + payload);
}

@addMethod(CR4Player)
timer function WMCContextSample(dt : float, id : int)
{
    var row : string;
    var activity : string;
    var clock : float;
    clock = theGame.GetEngineTimeAsSeconds() - wmcContextStarted;
    if(clock < 0) { WMCContextBegin(); return; }
    if(clock > 900 || wmcContextRows >= 600) { RemoveTimer('WMCContextSample'); return; }
    if(!theSound || !theGame.GetCommonMapManager() || !theGame.envMgr)
    {
        row = "available=0";
    }
    else
    {
        activity = "foot";
        if(IsUsingHorse(true)) activity = "horse";
        if(IsUsingBoat()) activity = "boat";
        row = "available=1|region=" + theGame.GetCommonMapManager().GetCurrentArea() +
            "|location=unknown|state=" + theSound.GetCurrentGameState() +
            "|combat=" + ShouldEnableCombatMusic() + "|threat=" + IsThreatened() +
            "|night=" + theGame.envMgr.IsNight() + "|activity=" + activity +
            "|scene=" + theGame.IsDialogOrCutscenePlaying() + "|paused=" + theGame.IsPaused() +
            "|loading_video=" + theGame.IsLoadingScreenVideoPlaying() + "|interior=" + IsInInterior() +
            "|owner=unknown|outro=unknown|selector=unknown";
    }
    if(row != wmcContextPrevious || clock >= wmcContextHeartbeat)
    {
        WMCContextEmit("snapshot|origin=timer|" + row);
        wmcContextPrevious = row;
        wmcContextHeartbeat = clock + 30;
    }
}

@addMethod(CR4Player)
function WMCContextDiscovery(tag : name)
{
    var i : int;
    if(wmcContextEpoch <= 0 || wmcContextRows >= 600) return;
    for(i=0; i<wmcContextDiscoveries.Size(); i+=1)
        if(wmcContextDiscoveries[i] == tag) return;
    if(wmcContextDiscoveries.Size() >= 32) return;
    wmcContextDiscoveries.PushBack(tag);
    // Local ordinal avoids exporting native tag/location/story strings.
    WMCContextEmit("discovery|origin=player_first_trigger|local=1|first=1|id=" + wmcContextDiscoveries.Size());
}

@wrapMethod(CR4Player)
function OnSpawned(spawnData : SEntitySpawnData)
{
    wrappedMethod(spawnData);
    WMCContextBegin();
}

@wrapMethod(CR4Game)
function OnAfterLoadingScreenGameStart()
{
    wrappedMethod();
    if(thePlayer) thePlayer.WMCContextBegin();
}

@wrapMethod(W3FastTravelEntity)
function OnAreaEnter(area : CTriggerAreaComponent, activator : CComponent)
{
    var eligible : bool;
    var manager : CCommonMapManager;
    manager = theGame.GetCommonMapManager();
    eligible = false;
    if(thePlayer && activator && area && manager && !isHubExit && GetWitcherPlayer() &&
       activator.GetEntity() == thePlayer && area == GetComponent("FirstDiscoveryTrigger") &&
       IsNameValid(entityName))
        eligible = !manager.IsEntityMapPinDiscovered(entityName);
    wrappedMethod(area, activator);
    if(eligible && thePlayer && manager.IsEntityMapPinDiscovered(entityName))
        thePlayer.WMCContextDiscovery(entityName);
}
