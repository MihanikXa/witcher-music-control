// Original batch bridge. Run after SAHUD has applied its native-child rules.
// It forwards presentation state to the new I&I drawing layers; no targeting,
// data, quest or controller logic is replaced.
@wrapMethod(SahCore)
function Tick(dt : float)
{
    var hud : CR4ScriptedHud;
    var enemy : CR4HudModuleBase;
    var movie : CScriptedFlashSprite;
    var sync : CScriptedFlashFunction;

    wrappedMethod(dt);
    hud = (CR4ScriptedHud)theGame.GetHud();
    if (!hud)
        return;
    enemy = (CR4HudModuleBase)hud.GetHudModule("EnemyFocusModule");
    if (!enemy)
        return;
    movie = enemy.GetModuleFlash();
    if (!movie)
        return;
    sync = movie.GetMemberFlashFunction("qfSyncVisibility");
    if (sync)
        sync.InvokeSelf();
}
