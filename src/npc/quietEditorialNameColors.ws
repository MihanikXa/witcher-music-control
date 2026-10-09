// Original experimental fallback: recolor only known vanilla NPC-name colors.
// Keep the current movie, all merged methods, visibility and health logic.
// Not approved for packaging until the full profile compile gate passes.
@wrapMethod(CR4HudModuleEnemyFocus)
function OnTick(timeDelta : float)
{
    var movie : CScriptedFlashSprite;
    var focus : CScriptedFlashSprite;
    var label : CScriptedFlashObject;
    var originalColor : int;
    var newColor : int;

    wrappedMethod(timeDelta);
    // Flash handles are not Witcher object references and have no supported
    // Boolean conversion. Follow the module's existing initialized OnTick
    // lifecycle; its vanilla/FriendlyHUD handlers use the same bindings.
    movie = GetModuleFlash();
    focus = movie.GetChildFlashSprite("mcNPCFocus");
    label = focus.GetMemberFlashObject("tfName");
    originalColor = (int)label.GetMemberFlashNumber("textColor");
    newColor = originalColor;
    switch (originalColor)
    {
        case 7977213: newColor = 15327954; break;  // neutral -> E9E2D2
        case 13869949: newColor = 11845792; break; // friendly -> B4C0A0
        case 16711680: newColor = 14065811; break; // hostile -> D6A093
        case 16561481: newColor = 11846353; break; // Axii -> B4C2D1
        case 5963520: newColor = 14008462; break;  // VIP -> D5C08E
    }
    if (newColor != originalColor)
    {
        label.SetMemberFlashNumber("textColor", (float)newColor);
    }
}
