# Blood and Steel-first / Brawler-only private test variant

10 October 2026. User-approved direction implemented offline; **not deployed or
runtime accepted**. This replaces Core 01 only. The accepted analog-gait package
04 is preserved byte-for-byte. Do not repeat the original suite installation.

## Verified starting point

All 111 deployed Core members match `01-core-replacements.zip`, SHA-256
`0e63fc2f62fc73d3e325e4f698e62735cbaa12bf8977ce136676a48d547950f9`.
All thirteen deployed package-04 analog-gait members match SHA-256
`fbbe3b2ecfeab77965f13b4e7386c8891167f37f8d770b20a37c7c7fd9539909`.
Deployment manifests identify Core as the owner of Bestg/CSM/B&S menu overrides
and analog-gait as the owner of the merged locomotion override. Deployment uses
hardlinks. No deployed file or staging link was edited.

Installed Bestg files are the accepted Core derivatives of the earlier local
input, not newly downloaded replacements. Internal script comments span v0.2,
v1.1.16 and later feature revisions; these do not establish a single reliable
upstream release number. Source identity is pinned by the complete Core hash
and the per-file private inventory, not an inferred version label.
Blood and Steel identifies itself as v3.01, `useLooseScripts=false`, with no
source scripts and an authored `precompiled.rsblob`. Its sword/fist internal
selector rules cannot be verified from loose source.

F6 has no assignment anywhere in the inspected current input.settings or
installed bin/config and mod text inputs. F3 Outfit Wheel, F5 developer action,
keyboard walk/jog/sprint and existing controller mappings are untouched.

**Actual saved B&S settings differ from the historical preset:** Enabled,
CustomAttackEnabled and CustomDodgeEnabled are already true; CloseCamera is true,
Aggressiveness is 3. The prepared current diff changes only CloseCamera to false
and Aggressiveness to 1. No claim is made that the old selectors were still off.

## Function-level separation and conflicts

Paths below are relative to Bestg `content/scripts/local/`, unless stated.
The complete deterministic function/event inventory, annotation owners and call
edges are private in `brawler-only/dependency-map.json`; original input digest
is `b0f0689de0c89ed47ec7bb4d3c5b45e582762ef567513682082c3424817f9c4c`.
The public manifest records archive members and their hashes without source bodies.

| Original hooks / dependencies | Disposition and exact mechanism |
|---|---|
| Damage: BG2_GloveEnhancementCount, BG2_IsFightingWithFists, BG2_BrawlerSocketDamageBonus/DefenseBonus | Retain authored helpers. No school enum dependency. Existing Brawler menu values are read on use. |
| Damage: W3DamageManager.ProcessAction | Rewrite to retain only the original fist/socket damage calculation. Require active Brawler, actual fists, direct melee and Geralt attacker; per-action flag prevents duplicate multiplication. Normal mode, swords, bombs and DoT pass through. |
| Damage: W3PlayerWitcher.ReduceDamage | Native wrapper runs first; retain only Brawler direct-melee toughness/socket reduction, minimum 35% incoming factor. Require an actual other actor. No permanent armor/HP/stat modification. |
| Damage: CActor.FistFightCheck; CR4Player.PerformParryCheck/PerformCounterCheck | Retain native-first light fist-guard exception and native parry/counter dispatch. Heavy/super-heavy attacks still reject Brawler parry/counter. Gate through the new context-aware active predicate. |
| Damage: BG2_HeldSwordHasOil, OnPreAttackEvent, BG2_PhysicalGuardHit, W3DamageManagerProcessor.ProcessAction, PlayHitAnimation, CNewNPC.PerformParryCheck | Remove oil/school guard capture, Bear paid guard/hit-reaction suppression and shield staggering. No sword-mode modifier remains. |
| State: CR4Player and WeaponHolster.GetMostConvenientMeleeWeapon | Rewrite the existing two interception points to choose fists only in active Brawler; otherwise return the original chain. Ciri and scripted/restricted contexts are excluded. |
| State: BG2_RefreshBrawlerWeapon, BG2_SetStance, BG2_ApplyPending, OnWeaponDrawStart | Replace with dedicated toggle/pending controller. Equip fists once when safe; do not continually force equipment or interrupt an accepted attack. Explicit manual weapon commands remain native. Exiting does not force sword draw; normal draw/attack selection resumes natively. |
| State: BG2_AttackFactor, BG2_CompatibilityEvadeFactor, all speed IDs/reset/fallback methods, FillDodgePlaylists, school console commands | Remove. No EBG2Stance/school selection, timing ownership, pirouette alteration or neutral-Witcher 95% factor remains. |
| AttackStyles: BG2_BuildAttackStyle, OnComboAttackCallback, OnPerformAttack, BG2_AddDirectionalLight/BG2_AddRestrainedHeavy | Remove entire file. B&S/vanilla retain attack clips and callback flow. This avoids a loose Bestg attack selector layered on the compiled B&S selector. |
| Config: BG2_Config | Retain numeric read/clamp helper; remove menu initialization and school migration calls. All config-group, sign-power, sign-stat, stamina-cost and agile/Viper migration hooks removed. Only BG2Brawler menu group survives. |
| Input: Initialize, OnBG2* events, sword/potion/sign/sheath/throw handlers, Pad/KbmModifier helpers, OnRadialMenu chords | Remove old listeners/chords/consumption flags. New Initialize registers only CompatBrawlerToggle. One F6 press toggles; held/repeated press is suppressed until release. No controller chords are consumed. |
| Features: BG2_StartFeatureTick, BG2_BrawlerArrowDeflectWanted, BG2_UpdateBrawlerArrowDeflect, BG2_FeatureTick | Omit temporary bounce_arrows ability and polling feature. The original ownership flag is not saved, so reliable cleanup across reload/shared ability sources is unproven. No AddAbility/RemoveAbility is added by this variant. |
| HUD/Medallion/Radial/Poses/ViperStrikeHud: feedback/icon queues, DisplayPending, UpdateVitality, ShowRadialMenu, effect display hooks and pose helpers | Remove all these files and the Bestg HUD bundle, texture cache and metadata. Locale label files remain for the Brawler settings page. SAH and FriendlyHUD are untouched; no HUD override remains in Bestg. |
| ViperAlchemy: potion/crit wrappers, strike timer, toxicity capacity modification | Remove entirely. Old saved stance/profile fields are absent; new toggle state is deliberately not saved. No new persistent toxicity/stat change is introduced. See migration precaution below. |
| CSMAnimation, Calculation, Configuration, Console, Finishers, PlayerHooks/State/Stats, SwordHooks | Remove all ten CSM source files, including replacement dodge/special-attack methods and Bestg factor calls. Native/compiled B&S functions regain those targets. Empty modCombatSpeed.xml is only a harmless menu-filelist compatibility descriptor, not a speed-system shim. |
| CSM_EndExplorationTiming / ResponsiveMovementEndTransitionAnimation | Preserve the cleanup purpose through original tiny wrappers on accepted OnCombatActionStart and SetIsCurrentlyDodging. Reset RM's own transition multiplier only; no CSM ID/factor/API survives. The existing RM exploration/combat guard remains byte-identical. |
| Arrow Parry Manual: AddCounterTimeStamp, APM_TryManualParry, OnProjectileCollision, damage hooks | Unchanged package 03. APM_TryManualParry explicitly requires a held sword, so retaining it does not promise manual fist-arrow deflection. That extra Brawler feature is deliberately sacrificed. |
| Movement / merged playerInput, r4Player, locomotionDirectController; AutoLoot; SAH/FriendlyHUD; Living Camera; quests/Gwent/localization; Colors/Shadows/QuietFolio | No payload changes. No installed loose-script call outside Bestg/CSM references the removed APIs in the cross-reference scan. Compiled-only dependencies remain outside that assertion. |

## Behavior and trade-offs

Normal mode has no Bestg speed, damage, defense, sign, alchemy, dodge or clip
effects. Brawler preserves fists, socket damage/defense and light guards/counters
through the authored native-wrapper route. Both states retain native hitlag.
Blood and Steel owns sword attack/dodge selection with Less Spins as a test
preference, not a locked algorithm. Its compiled internals and interaction with
unarmed targeting/counter clips remain gameplay risks; no binary blob was edited.

The new controller resets to normal on load/input reconstruction. A requested
switch waits until attack/dodge/finisher and weapon restrictions clear. Repeated
individual presses reverse the pending request; held repeat does not. Death,
vehicle/boat/swim/airborne/interaction/focus/fade or a scripted state invalidates
the mode and clears the timer. Quest fist-fight minigames remain wholly native
and deliberately receive no Brawler bonus. The user must re-enable Brawler after
these exclusions, including a jump; this conservative behavior avoids carrying
an equipment override into scripted movement. No mode UI/popup is added.

Sacrifices: all five school styles, school guard/sign/alchemy modifiers,
custom school attack/dodge choices, stance UI, CSM timing/layers/stats and optional
fist-arrow ability. The useful isolated fist mechanics survive. Full sword-mode
neutrality and coherent B&S ownership are worth those removals under the approved
direction. Normal mode means native sword control is restored, not that F6
immediately draws a sword without your usual weapon/attack command.

## Install candidate — user approval/deployment only

Private ZIP:
`C:\Dev\witcher-mods-merger\audit-2026-10-08\release\witcher-compatibility\brawler-only\01-brawler-only-core.zip`

SHA-256: `4a0d5a4fea809600dd08a42e07e20ec803bf6c43635d514d4c77836586f1ae3d`.
52 files: 46 byte-identical Core members, three changed XML descriptors and three
Brawler scripts. Sixty-two old members are withdrawn. All AutoLoot and RM
payloads are byte-identical. Packages 02/03/04/05 are not rebuilt.

1. Prepare a disposable test save/profile backup and retain the accepted Core
   ZIP and current settings backups. First smoke-test a new game. For an existing
   copy save, save under the old setup in neutral Witcher mode, unguarded, outside
   Viper/Brawler and without an active action. Wait for old feature timers to
   clear, then quit fully before switching packages. Do not save over a campaign
   slot during these tests. This avoids knowingly carrying temporary arrow or
   toxicity state; it is not proof of old-save serialization safety.
2. In **Witcher Compatibility Test**, install the ZIP as a new Core version.
   Disable the accepted Core 01 entry, enable this variant and deploy through
   Vortex. Keep originals Bestg, CSM, AutoLoot and standalone RM disabled. Keep
   B&S enabled. Only one Core version may own the replacement folders.
3. Preserve package 04 analog-gait and packages 02/03/05 unchanged. Preserve
   movement, quests, UI colors/shadows/QuietFolio, SAH/FriendlyHUD and their rules.
   Keep merged files ahead of Movement Tweaks and SAH ahead of Bestg. The new
   Core's modBloodAndSteel.xml must still win the file conflict with B&S's menu.
   Bestg keeps its existing relative position. The obsolete modCombatSpeed
   folder/component must disappear on deployment; disable a stale load-order
   entry if Vortex still lists it. Do not disable Core as a whole to remove CSM.
   Inspect Vortex removal prompts rather than manually deleting deployed files.
4. Do not run Script Merger or regenerate the accepted merges. Confirm no CSM
   source remains active and Bestg now has only the three CompatBrawler scripts.
   Brawler is its only settings group; CSM has no visible settings group. Vortex's
   existing menu filelist entries are compatible with the empty CSM descriptor.
5. Apply only these two input.settings additions, after checking F6 is still
   vacant: `[Combat] IK_F6=(Action=CompatBrawlerToggle)` and the same line in
   `[Exploration]`. There are no new controller mappings or whole input/XML
   replacements. Offline `.diff` and `.delta.json` files are beside the ZIP;
   do not install `.proposed` settings wholesale or import them as game-root files.
6. Verify B&S **Enabled, Custom Attacks and Custom Dodges On**. Set
   `[BaS_Main] BaS_Aggressiveness=1` (**Less Spins**) and
   `BaS_CloseCamera=false` (**Off**) to retain Living Camera ownership. Preserve
   Targeting, DamageIncrease and all unrelated settings. Do not apply a complete
   B&S preset that resets those preferences. Current saved selectors are already
   On; menu defaults alone do not supersede them. Review the narrow offline diff
   against your latest settings before applying any change.

## Offline gates and boundaries

CRC, unique names, deterministic rebuild, exact preserved-member hashes and
installed Vortex menu-root routing pass: 52 copies; component directories are
AutoLoot, Bestg and RM. All 128 protected deployed/Core/analog/config file hashes
remain unchanged. The public manifest enumerates actual ZIP members, hashes,
removed members and build inputs. No payload is public.

Official wcc compilation of the accepted assembled source context, with only
Bestg/CSM overlays substituted, **passes**, exit 0, zero WCC script errors,
374 warnings and 23,441 diagnostic assertions. The existing compiler harness
still emits environment/resource assertions; it is not a clean engine load.
Output blob SHA-256:
`e811bd5f93d68e18a63ea3da3e0be55716200f53f8bf08c718d1c086837a6839`.
Log: `C:\REDkitProjects\WitcherCompatibility\compatibility-validation\brawler-only\compiler.log`.
The first run rejected a reserved-word local identifier; renaming it did not
change behavior. The failed log is preserved separately. Blood and Steel and
other opaque compiled sources are not recompiled by this source-context test.

Generated-body fixtures pass toggle/pending transitions, repeat suppression,
invalid contexts/death, fist/socket multipliers, no duplicate damage, neutral and
sword passthrough, DoT/non-melee exclusion, native zero damage and heavy counter
limits. These are source execution tests, not engine/animation or save tests.
No Computer Use, game launch, live deployment, settings/save/controller edit or
depot regeneration was performed. Compiler output is validation evidence; the ZIP
ships loose scripts for retail compilation, not a replacement global scripts blob.

Rebuild with `tools/build-brawler.py --game <game> --documents <Documents>`;
add `--compile` only with a fresh isolated `compatibility-validation/brawler-only`
directory (archive the prior isolated result first). The builder refuses mismatched
accepted Core/analog inputs or occupied F6 and checks protected inputs afterward.
Run `node tools/test-brawler.cjs <private payloads> <receipt.json>` and the
existing Vortex topology checker before considering the generated ZIP ready.

## Required gameplay acceptance and rollback

Test incrementally on the disposable save:

1. Start/compile, inspect menus and unchanged SAH/FriendlyHUD/colors/font.
   Check keyboard/controller analog gait and sprint before combat.
2. In normal mode, test B&S Less Spins directional attacks, flanking/target
   changes, dodge/roll, native hitlag, Whirl/Rend and finishers. Look for speed
   stacking or missing clips. Do this before pressing F6.
3. F6 enters fists from sheathed/drawn sword; F6 again permits normal swords.
   Hold F6 and confirm a single toggle. Press during attack, dodge and finisher:
   selection must wait, never cancel animation. Verify no stuck damage/defense
   or speed after exit. Explicit weapon draws must remain usable.
4. Compare fist damage and incoming direct melee with Brawler off/on, including
   equipped glove sockets. Light guard/timed counter should work versus armed
   opponents; heavy/super-heavy hits should break through. Test DoT/Quen and
   non-melee damage without extra Brawler protection.
5. Test sword Arrow Parry Manual timing/held block unchanged. Fists have no added
   arrow-deflection ability in this variant. Test B&S behavior against several
   enemy types; unknown compiled fist/counter behavior is the principal runtime
   integration gate.
6. Save/reload, death, combat exit, jump/climb/swim/horse/boat and Ciri. Reload
   must start neutral; invalid contexts must clear mode. Quest/fight-club fists
   must stay native. Recheck analog controls, Roach, interactions and camera.

If compilation fails, record the complete error dialog and any generated script
compiler log. If runtime fails, record normal/Brawler mode, enemy/weapon/action,
B&S settings and whether it repeats with Brawler off; keep a short video and the
matching disposable save. Restore the entire accepted Core before attempting a
campaign. Do not patch around unknown B&S animation failures.

Rollback: quit fully, disable this Core variant, re-enable accepted
`01-core-replacements.zip` and deploy. Preserve package 04 and every unrelated
package/order. Restore the backed-up B&S keys (currently Aggressiveness 3,
CloseCamera true) and remove only the two newly added CompatBrawlerToggle F6
lines. Leave pre-existing selector values as they were. Use the matching pre-test
save/profile backup; a changed test save is not a guaranteed safe migration back
to removed/re-added saved school fields. Verify old Core owns its four component
folders again. No manual deletion, purge, save editing or full-suite reinstall.
