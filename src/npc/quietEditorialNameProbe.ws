// Original bounded diagnostic. Disable v2; never run both packages together.
// Reports through supported notifications, with optional Log/console evidence.
// Only Roach and Vesemir are tested; all wrappers preserve the event result.
@addField(CR4ScriptedHud)
var qeProbeHudSeconds : float;
@addField(CR4ScriptedHud)
var qeProbeHudReported : bool;
@addField(CR4ScriptedHud)
var qeProbeHudStatusReported : bool;
@addField(CR4HudModuleEnemyFocus)
var qeProbeTicks : int;
@addField(CR4HudModuleEnemyFocus)
var qeProbeNameCalls : int;
@addField(CR4HudModuleEnemyFocus)
var qeProbeSeconds : float;
@addField(CR4HudModuleEnemyFocus)
var qeProbeTarget : CGameplayEntity;
@addField(CR4HudModuleEnemyFocus)
var qeProbePhase : int;
@addField(CR4HudModuleEnemyFocus)
var qeProbeInitial : int;
@addField(CR4HudModuleEnemyFocus)
var qeProbeRoachDone : bool;
@addField(CR4HudModuleEnemyFocus)
var qeProbeVesemirDone : bool;
@addField(CR4HudModuleEnemyFocus)
var qeProbeReports : int;

function QEProbeNotice(message : string)
{
    Log("[QE-NPC] " + message);
    theGame.GetGuiManager().ShowNotification("QE: " + message, 4000);
}

function QEProbePalette(original : int) : int
{
    switch (original)
    {
        case 7977213: return 15327954;
        case 13869949: return 11845792;
        case 16711680: return 14065811;
        case 16561481: return 11846353;
        case 5963520: return 14008462;
    }
    return original;
}

// Independent beacon: this does not depend on EnemyFocus OnTick executing.
@wrapMethod(CR4ScriptedHud)
function OnTick(timeDelta : float)
{
    var result : bool;
    var enemy : CR4HudModuleEnemyFocus;
    var target : CGameplayEntity;
    var targetName : string;
    result = wrappedMethod(timeDelta);
    if (!qeProbeHudStatusReported)
        qeProbeHudSeconds += timeDelta;
    if (!qeProbeHudReported)
    {
        if (qeProbeHudSeconds >= 2.0)
        {
            qeProbeHudReported = true;
            enemy = (CR4HudModuleEnemyFocus)GetHudModule("EnemyFocusModule");
            if (enemy)
                QEProbeNotice("HUD wrapper loaded; NPC ticks=" + enemy.qeProbeTicks + " name calls=" + enemy.qeProbeNameCalls);
            else
                QEProbeNotice("HUD wrapper loaded; EnemyFocus module absent");
        }
    }
    if (!qeProbeHudStatusReported && qeProbeHudSeconds >= 30.0)
    {
        qeProbeHudStatusReported = true;
        targetName = "none";
        target = thePlayer.GetDisplayTarget();
        if (target) targetName = target.GetDisplayName();
        enemy = (CR4HudModuleEnemyFocus)GetHudModule("EnemyFocusModule");
        if (enemy)
            QEProbeNotice("STATUS: ticks=" + enemy.qeProbeTicks + " names=" + enemy.qeProbeNameCalls + " target=[" + targetName + "] reports=" + enemy.qeProbeReports);
        else
            QEProbeNotice("STATUS: EnemyFocus absent; target=[" + targetName + "]");
    }
    return result;
}

// A normal method counter separates name-update execution from event wrapping.
@wrapMethod(CR4HudModuleEnemyFocus)
function UpdateName(enemyName : string)
{
    wrappedMethod(enemyName);
    qeProbeNameCalls += 1;
}

@wrapMethod(CR4HudModuleEnemyFocus)
function OnTick(timeDelta : float)
{
    var result : bool;
    var target : CGameplayEntity;
    var targetName : string;
    var focus : CScriptedFlashSprite;
    var field : CScriptedFlashObject;
    var typedField : CScriptedFlashTextField;
    var typedText : string;
    var objectText : string;
    var numberBefore : float;
    var uintBefore : int;
    var numberAfter : float;
    var uintAfter : int;
    var desired : int;
    var visibility : string;
    result = wrappedMethod(timeDelta);
    qeProbeTicks += 1;
    if (qeProbeRoachDone && qeProbeVesemirDone)
        return result;
    qeProbeSeconds += timeDelta;
    if (qeProbeSeconds < 5.0)
        return result;
    qeProbeSeconds = 0.0;
    target = thePlayer.GetDisplayTarget();
    if (!target)
        return result;
    targetName = target.GetDisplayName();
    if (targetName != "Roach" && targetName != "Vesemir")
        return result;
    if ((targetName == "Roach" && qeProbeRoachDone) ||
        (targetName == "Vesemir" && qeProbeVesemirDone))
        return result;
    if (qeProbeTarget != target)
    {
        qeProbeTarget = target;
        qeProbePhase = 0;
    }
    focus = GetModuleFlash().GetChildFlashSprite("mcNPCFocus");
    field = focus.GetMemberFlashObject("tfName");
    typedField = focus.GetChildFlashTextField("tfName");
    typedText = typedField.GetText();
    objectText = field.GetMemberFlashString("text");
    numberBefore = field.GetMemberFlashNumber("textColor");
    uintBefore = field.GetMemberFlashUInt("textColor");
    // Hard cap even if the user switches targets before a sequence completes.
    if (qeProbeReports >= 10)
    {
        if (qeProbeTarget == target && qeProbePhase > 0 &&
            typedText == targetName && objectText == targetName)
            field.SetMemberFlashUInt("textColor", QEProbePalette(qeProbeInitial));
        qeProbeRoachDone = true;
        qeProbeVesemirDone = true;
        return result;
    }
    qeProbeReports += 1;
    // No writes until both access paths identify the actual displayed target.
    if (typedText != targetName || objectText != targetName)
    {
        QEProbeNotice("FIELD " + targetName + ": typed=[" + typedText + "] object=[" + objectText + "] N=" + numberBefore + " U=" + uintBefore);
        if (targetName == "Roach") qeProbeRoachDone = true;
        else qeProbeVesemirDone = true;
        return result;
    }
    switch (qeProbePhase)
    {
        case 0:
            qeProbeInitial = uintBefore;
            if (qeProbeInitial <= 0 || qeProbeInitial > 16777215)
            {
                if (numberBefore > 0.0 && numberBefore <= 16777215.0)
                    qeProbeInitial = (int)numberBefore;
                else
                {
                    QEProbeNotice("READ " + targetName + ": N=" + numberBefore + " U=" + uintBefore + "; no restorable RGB, writes skipped");
                    if (targetName == "Roach") qeProbeRoachDone = true;
                    else qeProbeVesemirDone = true;
                    return result;
                }
            }
            if (focus.GetVisible()) visibility = "focus visible";
            else visibility = "focus hidden";
            if (field.GetMemberFlashBool("visible")) visibility += "/text visible";
            else visibility += "/text hidden";
            QEProbeNotice("READ " + targetName + ": " + visibility + "; N=" + numberBefore + " U=" + uintBefore);
            break;
        case 1:
            // Unmistakable cyan #00FFFF; independent of the RGB switch.
            field.SetMemberFlashNumber("textColor", 65535.0);
            numberAfter = field.GetMemberFlashNumber("textColor");
            uintAfter = field.GetMemberFlashUInt("textColor");
            QEProbeNotice("NUMBER " + targetName + ": before=" + uintBefore + " after N=" + numberAfter + " U=" + uintAfter);
            break;
        case 2:
            // Before is delayed readback from NUMBER; after tests the UInt setter.
            field.SetMemberFlashUInt("textColor", 65535);
            numberAfter = field.GetMemberFlashNumber("textColor");
            uintAfter = field.GetMemberFlashUInt("textColor");
            QEProbeNotice("UINT " + targetName + ": delayed N=" + numberBefore + " U=" + uintBefore + "; after N=" + numberAfter + " U=" + uintAfter);
            break;
        case 3:
            // Delayed UInt readback, then the existing palette (or original RGB).
            desired = QEProbePalette(qeProbeInitial);
            field.SetMemberFlashUInt("textColor", desired);
            uintAfter = field.GetMemberFlashUInt("textColor");
            QEProbeNotice("PALETTE " + targetName + ": delayed=" + uintBefore + " want=" + desired + " after=" + uintAfter);
            break;
        case 4:
            QEProbeNotice("FINAL " + targetName + ": N=" + numberBefore + " U=" + uintBefore + "; no further writes");
            if (targetName == "Roach") qeProbeRoachDone = true;
            else qeProbeVesemirDone = true;
            break;
    }
    qeProbePhase += 1;
    return result;
}

// Optional only if an existing console is available; no settings change needed.
// Recognized exec proves this source loaded independently of either OnTick hook.
exec function qeprobe()
{
    var hud : CR4ScriptedHud;
    var enemy : CR4HudModuleEnemyFocus;
    hud = (CR4ScriptedHud)theGame.GetHud();
    if (!hud)
    {
        Log("[QE-NPC] exec loaded; no HUD yet");
        return;
    }
    enemy = (CR4HudModuleEnemyFocus)hud.GetHudModule("EnemyFocusModule");
    if (enemy)
        QEProbeNotice("exec loaded; NPC ticks=" + enemy.qeProbeTicks + " name calls=" + enemy.qeProbeNameCalls);
    else
        QEProbeNotice("exec loaded; EnemyFocus module absent");
}
