# Movement correction for the deployed compatibility profile

This is an update to the **existing Witcher Compatibility Test** profile, not a reinstall. The user reports Remastered 5.01 now compiles, starts, loads gameplay and shows all 15 menus. Those runtime observations are user-reported. Read-only verification found all 171 deployed release payloads byte-identical to the five archives. Documents/mods.settings enables Movement Tweaks and Responsive Movement; merged files are owned by `04-updated-merges` at priority 2. That relative source winner is valid and is preserved.

## Cause and selected behaviour

The effective merged playerInput OnCommSprint retains Movement Tweaks' commented-out native `SetSprintActionPressed(true)`. Current CanSprint in the deployed r4Player still rejects non-toggle sprint when `sprintActionPressed` is false. Movement Tweaks' IsSprintActionPressed separately reads the physical action; that does not satisfy CanSprint's direct private-field test. The earlier source-preservation checks missed this cross-file contract mismatch. It is a demonstrated explanation for failed held sprint; runtime evidence is still needed to establish every contributor to the reported jogging failure.

Current keyboard bindings are Ctrl= Sprint and Shift= PCAlternate (alternate/heavy attack), not Shift= Sprint. Controller A/Cross maps to Sprint; left-thumb maps to SprintToggle and is gated by the game's LeftStickSprint option. C= SwordSheathe intentionally toggles Movement Tweaks' slower 0.30 walk. Native stamina, encumbrance, terrain, air, guard and quest movement restrictions remain unchanged.

The user explicitly selected **standard held-key sprinting, walk-by-default and a separate jog toggle**. This deliberately replaces Movement Tweaks' held-key jog-only gesture while retaining its locomotion implementation, default walk, slow walk and controller analog gaits.

The hotfix changes only merged playerinput.ws:

- OnCommSprint restores the native press/release flag and remembers the previous walk/jog choice, restoring it on release. Native alternate-sign early return and ranged-weapon holstering stay in their original order. Duplicate press events cannot overwrite the remembered gait.
- OnCommWalkToggle adds the on-foot walk/jog toggle after the unchanged horse handler's return. Toggling during a held sprint changes the gait to restore afterward.
- OnCommSprintToggle clears the authored slow-walk mode only when enabling sprint-toggle, avoiding the 0.30 cap on controller toggle sprint. Existing input-mode gate/toggle/holster logic stays intact.

No r4Player, Movement Tweaks source, Responsive Movement source, input.xml, combat script, menu XML or other package is changed. If a quest genuinely disallows running, this patch does not override that lock.

## Artifact and checks

`C:\Dev\witcher-mods-merger\audit-2026-10-08\release\witcher-compatibility\movement-fix\04-updated-merges-movement-fix.zip`

SHA-256: `6ce762947cfbc02223ac50e635277065df65962f233909acb7a7950398b990d3`.

Twelve real files with the same Mods/mod0000_MergedFiles layout; eleven members byte-identical. CRC, unrelated source/control-flow preservation, repeat-build hash and installed Vortex top-level path routing pass. The original five archives remain unchanged. All 21 protected live movement scripts/settings hashes remained unchanged. All 1,753 compiler-reference input hashes still match the earlier isolated source assembly.

Official wcc compiles the corrected assembled sources and unchanged Gwent patch: exit 0, success message, real patch blob. It reports the same 379 warnings/23,591 assertions as the earlier broad source assembly; this is not a clean certification of opaque compiled dependencies or exact deployment order. No compiler workaround or code deletion was performed. The corrected runtime behaviour is **not yet tested in-game**. Private receipt/log: movement-fix/validation.json and C:\REDkitProjects\WitcherCompatibility\compatibility-validation\movement-hotfix\compiler.log. The script blob is validation-only, not deployed or included in the ZIP.

Reproduce package only (no live writes):

```powershell
C:\Python314\python.exe .\audit-2026-10-08\tools\build-movement-fix.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3'
```

`--compile` additionally uses the preserved isolated compiler baseline and a fresh movement-hotfix project directory. Archive generation pins the prior package and accepts only the original or hotfixed deployed playerInput; changed inputs require review. Keep the original build-release.py workflow plus this incremental builder; full-package regeneration alone does not include this hotfix.

## Update this profile only

1. Close the game. Keep the existing test profile and settings; back up the current input.settings and retain the old **04 Updated Merges** archive/version. Do not recreate the profile or remove manual files again.
2. In Vortex, import **04-updated-merges-movement-fix.zip** as an update/replacement for the existing **04 Updated Merges** package. If Vortex offers Update/Replace, select that entry. Otherwise install the new version, disable only the old 04 entry and enable only the new 04 entry. Do not enable two owners of mod0000_MergedFiles. Keep the old version available for rollback.
3. Keep packages **01, 02, 03 and 05 unchanged and enabled**. Keep Movement Tweaks and Responsive Movement installed/enabled; keep the replaced original packages disabled. Core remains installed throughout this update. Preserve existing resource priorities/conflict rules, including the merged folder's current priority 2, UPR/Gwent before BIA and SAH before Bestg. No new load-order relationship or Script Merger regeneration is required.
4. Deploy through Vortex. Verify mod0000_MergedFiles is enabled and contains the new playerinput.ws; the other eleven merged/adapted files must remain unchanged. Do not edit deployed hardlinks or accept unrelated deletion prompts.
5. Bind **Toggle walk/run** to **Caps Lock** using the existing game's keybindings menu. Alternatively, with the game closed, apply only the two added `IK_CapsLock=(Action=WalkToggle)` lines in movement-fix/prepared-input.settings.diff, under BASE_CharacterMovementWithSprint and Exploration. Caps Lock was unassigned in the inspected file. Do not copy the entire prepared settings file. The helper-generated offline copy preserves all unrelated assignments. No new binding is required for Arrow or other mods.
6. Keep Ctrl as the Sprint binding for the first verification. If you prefer Shift, use the game's Run/Sprint keybinding menu afterward and review any overlap with its existing alternate/heavy-attack modifier; this hotfix does not silently change it. Controller A/Cross held sprint uses the existing mapping. For left-thumb toggle sprint, enable the game's left-stick sprint option and test that mode separately; do not reset the controller layout.

## Responsive Movement and jitter

The inspected dx12user.settings already has ResponsiveMovement Enabled=false, ImmediateInput=false, StopSoonerLevel=0, TransitionSpeedLevel=0, KeepRunningOnTurns=false, TighterTurnsLevel=0, RunNearEnemies=false and CombatMovement=false. Its guarded locomotion adjustments therefore do not explain the present missing sprint. Jitter's precise earlier cause was not reproduced; we do not claim a specific setting has been proven responsible.

Leave those saved values unchanged for the first movement test. After it passes, you may turn only ResponsiveMovement **Enabled=true**, keeping the listed locomotion settings off/zero and the existing combat/attack/sign/swim/climb settings unchanged. This allows testing the already configured horse improvements without stacking its immediate-input, turn, stopping and transition-timing changes onto Movement Tweaks. Do not press Reset/Profile presets. If jitter returns, revert only Enabled to false and report the movement/state where it occurs. No Vortex enabled-state change or Core replacement is needed.

## Running the Walls acceptance and rollback

In the tutorial on a clear running segment, using the existing suitable test save:

1. W alone: normal walk. C: slower walk; press the Sprint key and confirm that slow-walk state clears.
2. Caps Lock then W: jog. Caps Lock again: walk. Verify no unintended horse-gait change when on foot.
3. W+Ctrl: sprint where the tutorial allows it. Release Ctrl: return to the selected walk/jog gait. Repeat from both gaits; toggle Caps Lock during the hold and verify the post-release choice. Confirm sprint can be started again after stopping and after save/reload.
4. Controller partial stick: walk; full stick: jog; configured held sprint: sprint. Separately test left-thumb toggle if that option is enabled. Try C slow-walk followed by controller sprint-toggle and verify it no longer stays capped at slow walk.
5. Finish the tutorial's run/jump/climb sequence. Check turns/stops for jitter, horse walk/canter controls, Bestg stances/dodges/CSM timing and HUD transitions. Do not infer unrestricted quest movement from a successful sprint test; native movement locks are preserved.

If startup fails, collect the complete compiler dialog and active mods.settings. If movement still fails, report whether the failure affects **Caps Lock jog**, held Sprint, controller toggle or all three; include the Running the Walls objective, current Run/Sprint binding and left-stick sprint option. Do not remove quest locks or reset saves to force movement.

Rollback **only this update**: close the game, switch 04 back to its retained previous version (`49220f25110566c6355e19be9464822ef47d0bf12a43b31d209e8d3ef151813a`) in Vortex, deploy and verify the merged folder's existing priority. Leave Core/02/03/05, Movement Tweaks and the rest of the profile intact. Reverse only the added Caps Lock binding/rebinding and any optional RM master-toggle change. No full compatibility-release rollback, profile recreation, purge or save editing is needed. This restores the prior working setup **with its reported movement regression**.
