# Final installation handoff — 9 October 2026

Verified against release.md after review of 21a0e442: all five current ZIPs match SHA-256, byte size and file count; CRC/unique names/install roots pass. Total: 171 files. No rebuild or payload change during this handoff. Current DX12 executable still reports 5.0.0.1048522. Private receipt: release/witcher-compatibility/handoff-verification.json.

Archives: `C:\Dev\witcher-mods-merger\audit-2026-10-08\release\witcher-compatibility\`.

## Ordered Vortex checklist

1. **Back up before changing deployment.** Close the game. Clone the current Vortex profile as Compatibility Test. Independently copy Documents/The Witcher 3 settings (dx12user.settings, input.settings, mods.settings, profile.settings), current load order, manual Mods/mod0000_MergedFiles and Script Merger MergeInventory.xml if present. Preserve campaign saves separately and use a new-game test or copied pre-GDC save. Vortex profiles do not independently protect unmanaged merges, shared document settings or saves.
2. **Import** the five numbered ZIPs through **Mods > Install From File**. Name them Compatibility Core, English Text, Arrow Layout, Updated Merges and Gwent Layout. No wrapper folder belongs above Mods/bin/DLC. Retain original installed packages for rollback.
3. **Replace ownership before enabling.** Disable original Bestg School Stances, Combat Speed, AutoLoot and Responsive Movement packages; enable **Core and Updated Merges together**. Before enabling Updated Merges, move only the independently backed-up, confirmed manual mod0000_MergedFiles folder out of Mods. If Vortex owns that folder, withdraw its owner through Vortex instead; never move staging hardlinks. Disable original Arrow Deflection/Arrow Parry package when enabling Arrow Layout. Disable original mislaid Gwent Deck Choice package when enabling Gwent Layout. Its Mods and DLC are one indivisible package; omit Gwent My Way. Enable English Text. Keep B&S, SAH, UPR, BIA, Sharedutils and paired DLC, FriendlyHUD, Outfit Wheel and other retained dependencies enabled.
4. **File conflict rule:** set Compatibility Core **after** Blood and Steel so Core's `bin/config/r4game/user_config_matrix/pc/modBloodAndSteel.xml` wins. This is file ownership, separate from mod resource load order. There should be no enabled original package competing with its replacement. Resolve any unlisted conflict before startup rather than blindly accepting overwrite/delete prompts.
5. **Resource load order:** in Vortex's Witcher load-order page, use the reference below; preserve the other component positions from private load-order.json. All enabled sections need unique priorities. **Lower number wins.** Set Outfit Wheel explicitly enabled. Let Vortex persist order; copying mods.settings alone is insufficient.
6. **Saved settings:** with the game closed, apply only the 23 keys in the table below to the current Documents/The Witcher 3/**dx12user.settings**, using prepared-settings/dx12user.settings.diff as a review aid. Do not replace the whole file with an old prepared copy. Saved B&S values override XML defaults. Leave input.settings unchanged unless you want the optional F8–F11 bindings; Arrow uses the existing guard binding.
7. **Deploy yourself**, then inspect resulting Mods paths, menu XML ownership and generated Documents/mods.settings. Confirm the priority relationships, enabled replacement components and paired DLC. Confirm GwentDeckChoice.xml and other imported mod menu XMLs are registered in the applicable DX12 menu file list; preserve existing entries, never replace the entire list. Do not run automatic Script Merger regeneration over the reviewed merged outputs.
8. **First start:** launch the same DX12 configuration on the isolated test setup, reach the main menu and inspect the required mod settings before loading a test save. Confirm B&S selectors off and CSM settings below. If compilation fails or the game crashes, follow the failure procedure. If startup succeeds, test HUD/stance selection and attack-to-dodge cleanup first; then Arrow/Gwent and quest transitions using test-plan.md. Keep campaign saves untouched.

| Component | Priority |
|---|---:|
| mod0000_MergedFiles | 1 |
| mod0000_CompatibilityText | 2 |
| modunreasonableplotredesigned | 7 |
| mod_GwentDeckChoice | 8 |
| modbrothersinarms | 9 |
| modCombatSpeed | 21 |
| modArrowParryManual | 29 |
| modSeamlessAdaptiveHUD | 31 |
| modBestGsSchoolStances | 32 |
| modAutoLoot | 34 |
| modResponsiveMovement | 35 |
| modGeraltOutfitWheel | 38 |

These are folder priorities, not five archive priorities. Core supplies four component folders. UPR and Gwent must precede BIA; SAH must precede Bestg. Full 38-component reference: release/witcher-compatibility/load-order.json.

| Saved section | Exact values |
|---|---|
| BaS_Main | BaS_CustomAttackEnabled=false; BaS_CustomDodgeEnabled=false; BaS_DamageIncrease=0; BaS_CloseCamera=false |
| csmGeneral | CSM_On=1; CSM_HCap=1; CSM_LCap=1; CSM_MinSpeed=50; CSM_MaxSpeed=200; CSM_ApplyToFinishers=0 |
| csmBaseSpeed / csmSkillSpeed / csmArmorSpeed | CSM_Base=0 / CSM_SR=0 / CSM_Arm=0 |
| csmAdrenaline | CSM_Adren=0; CSM_RFSR=0 |
| fhudHUD | fhudEnableCombatModules=false; fhudEnableCombatModulesOnUnsheathe=false; fhudEnableWolfModuleOnVitalityChanged=false; fhudEnableWitcherSensesModules=false; fhudEnableMeditationModules=false; fhudEnableRadialMenuModules=false |
| fhudMarkers | fhud3DMarkersEnabled=false; fhudCompassMarkersEnabled=false |

## First-startup failure: collect, close, revert

1. Stop before loading/saving. Record launch time and DX12, active Vortex profile, enabled packages and stage. Capture the **complete** script compilation error list (all file paths, lines and messages; copy text if supported, otherwise screenshots). A compiler dialog may be the only script-error record; do not assume a script.log exists.
2. Copy the generated Documents/The Witcher 3/mods.settings and the relevant settings deltas, Vortex enabled/order/conflict-rule screenshots, and `C:\Users\micha\AppData\Roaming\Vortex\vortex.log` plus the newest rotated vortexN.log covering deployment. These are private diagnostic evidence, not public GitHub payloads.
3. For a native crash, collect `C:\Users\micha\AppData\Roaming\The Witcher 3\CrashInfo.json` if updated at the failure time, and newly generated crash dumps/stack traces/logs if present. Existing `bin/x64_dx12/ReShade.log` and `rt_optimizer.log` can help only if they cover that attempt. If no new crash record exists, note that and collect the Windows Event Viewer Application error for witcher3.exe (faulting module/exception). Old REDkit compiler logs do not describe this launch.
4. Close the game/compiler dialog before changing Vortex. First revert the last independent installation stage. Arrow and English Text can revert independently. Gwent's Mods/DLC must revert together; use a matching pre-GDC/new-game save. If core or merged scripts are implicated, **disable Core and Updated Merges together**, re-enable the original four packages, restore the old B&S menu winner and prior order/settings, then deploy through Vortex.
5. Restore the manual merged-folder backup only after Updated Merges' managed deployment is withdrawn and Vortex no longer owns those paths. Restore only changed settings keys; if no unrelated preferences changed, the fresh whole-file backup is also available. Verify the prior profile/order/deployed ownership before retrying the independent test save. Do not purge, delete hardlinks, edit saves, remove functions to silence errors, or rerun Script Merger blindly. This rollback restores the prior installation; it does not certify the prior stale merges as campaign-safe. Full details: rollback.md.

## Isolated-test safety assessment

No verified defect currently requires withholding a non-destructive startup test. The remaining broad compiler/opaque-blob uncertainty is a test risk, not proof of clean startup or runtime safety. UPR/BIA quest preservation is unproved; SAH wins the HUD resource; B&S custom attack/dodge functionality is deliberately disabled. Successful startup is not quest certification.

**Do not start even an isolated test** if backups/test-save separation are missing; Core/Merges are only partly installed; original and replacement owners remain simultaneously enabled; required dependencies or Gwent's paired DLC are missing; priorities/settings above were not applied; or deployment has unexplained overwrites/deletions. A Vortex profile alone does not prevent campaign-save or shared-setting damage. If the game/mod inputs have changed from this release, its verification does not cover that new configuration. Never continue a GDC-modified save with only part/all of GDC removed.

No agent deployment, settings mutation or game launch occurred during this handoff.
