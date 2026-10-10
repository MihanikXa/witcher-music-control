# Proposed Blood and Steel-first combat with a Brawler-only toggle

**Implementation status:** the user approved this direction; the offline
Core-only candidate and official source compilation are complete. See
[brawler-only.md](brawler-only.md) and brawler-manifest.json. This plan remains
the requirements record. No deployment or runtime acceptance is implied.

**Decision source:** User requests proceeding with a dedicated Brawler toggle,
while removing the remaining Bestg school stances and restoring Blood and Steel
as the main sword-combat system (10 October 2026).

**Authorization boundary:** Proceed with read-only audit, original build tooling,
isolated source changes, reproducible private test archives and documentation.
Do **not** modify a live game, installed Mods, Vortex profile/staging, Documents
settings, controller software, existing save, Script Merger output or accepted
packages without separate user approval. No Computer Use or desktop automation.
Any GUI-dependent steps belong to the user and should be as short as possible.

## Accepted behavior and boundaries

- **Normal sword mode:** Blood and Steel (installed Remastered v3.01) owns
  contextual sword attacks, animation selection, direction/flanking and optional
  custom dodge behavior. Begin with its configurable **Less Spins** preset as
  a trial, not a forced permanent value. Let Living Camera retain camera
  ownership. Normal mode must not apply any Bestg school bonuses or hidden
  speed multipliers.
- **Brawler:** Retain only the fun, functional unarmed fighting mechanisms from
  the actually installed Bestg source: prevent automatic sword draw when
  appropriate, fist damage/defense, light-attack blocks/counters, optional
  gauntlet/socket and fist-arrow-deflection behaviors as feasible and compatible.
  Do not assume each works without the underlying stance framework.
- **One-key control:** A dedicated configurable keyboard binding, candidate
  **F6**, which **toggles** between Brawler and normal sword mode.
  The original Bestg F6 action only selects Brawler and may not toggle back;
  implement and test a true reversible state transition. Check actual current
  [Combat]/[Exploration] input bindings and existing menus before choosing F6.
  Do not overwrite whole input.xml or input.settings. Controller mapping may
  be provided afterward by the user through Flydigi, not guessed here.
- **Removed:** Witcher/Feline/Bear/Griffin/Viper styles, all school-specific
  speed/damage/dodge/sign/oil/bomb bonuses, school selection radial/styling,
  stance popup/medallion, and any Bestg-to-CSM factor dependency not strictly
  necessary for independently functioning unarmed combat.
- **Preserved without regression:** tested package-04 analog gait and working
  keyboard gamepad sprint, unmodified movement and Responsive Movement
  exploration fix, AutoLoot, FriendlyHUD, Seamless Adaptive HUD as the wolf
  HUD owner, Living Camera, Arrow Parry Manual where independent, native
  hitlag, quest/Gwent/localization fixes and accepted separate
  UI mods Colors v4 / Shadow v1 / QuietFolio English Gentium v1.
- **No hidden stacking:** neither Bestg nor Combat Speed Mod may secretly
  leave attack/dodge animation multipliers active when Blood and Steel controls
  sword combat. Clean up temporary damage/guard/weapon-state modifiers on
  exit, interruption, death, save/load, combat transitions and mode changes.
  Quest/scripted unarmed sections must continue to function without forcing
  sword draw. Avoid reimplementing base engine combat unnecessarily.

## Evidence and why an audit is mandatory

The previous tested/installed compatibility **Core 01** includes *four*
replacement components under their original mod names: Bestg, Combat Speed Mod
(CSM), AutoLoot and Responsive Movement. Its builder in
`tools/build-release.py` integrates Bestg factor methods
(`BG2_AttackFactor`, `BG2_CompatibilityEvadeFactor`) into
`CSMCalculation.ws`, and changes Bestg's own animation-speed ownership. It
explicitly defaults Blood and Steel's `BaS_CustomAttackEnabled` and
`BaS_CustomDodgeEnabled` to false in a B&S menu XML; saved Documents settings
can override these defaults. Thus merely switching off Bestg in Vortex and
checking the two B&S boxes is not a safe verified migration.

`general-merge/audit-2026-10-08/decisions.md`, `conflicts.md`, `release.md`,
`implementation.md`, `analog-gait.md` and `handoff.md` explain this stack.
Keep the deployed known-good archives and hashes recoverable. The earlier
`Bestg wolfstatbars` conflict is resolved by SAH taking priority; removal of
Bestg should not undo that.

Upstream Bestg describes Brawler-specific blocking/counters and F6 selection,
and warns that *full* Bestg + B&S + CSM can overlap. Current descriptions do
not prove a stripped Brawler-only implementation is safe:
- https://www.nexusmods.com/witcher3/mods/13595
- https://www.nexusmods.com/witcher3/mods/9674

**Inspect the actual installed sources, not only public prose.** Original
repo manifest previously reported local Bestg source/version ambiguity
(staging/archive v1.1.0 versus development notes v1.1.45 balance-preset test).
Pin actual hashes, identify exact source/version and do not silently exchange
a different downloaded version. Blood and Steel's relevant implementation
is compiled-only in this setup; source-level compatibility with its selectors
cannot be assumed.

## Work order for Codex

### Gate 1 — dependency and conflict inventory (read-only)

1. Inspect live installed Bestg script sources, its input/menu XML, merged
   scripts, generated Core 01 private package and the current Vortex ownership
   metadata. Report all `BG2` Brawler state, guard, counter, damage,
   enhanced gauntlet, auto-draw, animation-speed, target/hit and input hooks.
   Find each invocation by cross-reference, not name guesses.
2. Build a graph: which pieces are Brawler-specific, which are shared with
   the discarded schools, which are required base functions, and which can
   be deleted or neutralized. Identify any player save/persistence fields.
3. Trace CSM/Bestg integrator code and dependency on Responsive Movement
   cleanup. Determine whether CSM can be removed outright or needs a neutral
   shim for a separate non-school feature; **prefer not retaining a redundant
   speed system**.
4. Inspect user settings, B&S menu and compiled resources without editing
   them. Identify the original B&S custom attack/dodge selectors, aggressiveness
   preset, impact on unarmed animations, targeting and camera. Do not invent
   access to compiled-only source. Inspect Arrow Parry Manual and Bestg unarmed
   guarding overlap. Inspect F6 conflicts in all relevant contexts.
5. Output a table of **retained / removed / rewritten / unresolved** hooks
   with relevant paths/functions and a deterministic exact source inventory.
   If Brawler cannot be separated without unknown compiled conflicts, state
   the smallest testable fallback and stop; do not silently keep all Bestg.

### Gate 2 — minimum working Brawler-only candidate

1. Choose the smallest supported implementation, preferably an original
   source transformation retaining only Brawler mechanics and necessary common
   helpers. Preserve author attribution and licenses. If technically
   appropriate, keep the Bestg mod's original folder name inside a *private*
   single-owner replacement; don't deploy two competing copies. Do not
   republish proprietary mods or claim an original standalone release.
2. Implement true F6 toggle to a **neutral base state**, not the old
   Bestg `Witcher` stance with residual buffs. The state must survive or
   safely reinitialize after save/reload without retaining stale modifiers.
   No school menu/notification dependencies. No duplicate input action owner.
3. Build a B&S-first private `Core 01` replacement that preserves the
   unaffected AutoLoot/Responsive Movement changes. Remove the Bestg-to-CSM
   school factor integration and entire unnecessary CSM implementation if
   safe; do not lose unrelated CSM-era exploration cleanup without analyzing
   its need. Prepare only necessary, narrow input/B&S settings changes.
4. Preserve package 04 analog-gait payload byte-for-byte unless a narrow,
   evidenced change is essential; if unavoidable, stop and request approval.
   Do not regenerate all merges. Keep shared HUD/layout files owned by SAH.
5. Restore B&S attack and dodge features as **explicit opt-in suggested settings**
   (plus Less Spins candidate); existing saved settings take precedence over
   mod XML defaults. Provide small targeted setting edits and backups,
   not a wholesale replacement of dx12user.settings or input.settings.
6. Build a clean offline compile + regression test. Compare changed source
   hooks, packages, menu owners, optional binding contexts and mod priority
   with the working baseline. Record any unresolved compiled-only risk
   explicitly, and confirm a genuine fallback/one-package rollback.

### Gate 3 — bounded private test and user acceptance

Package a separate private, reversible test variant with exact SHA-256,
changed-member inventory, original working archive backup and explicit
Vortex ownership instructions. Test on **Witcher Compatibility Test** and a
disposable/copy save, only after user authorization to install.

Test: startup/compiler, toggle F6 once/on repeat, sword drawn and sheathed,
auto-draw suppressed only for Brawler, normal sword combat after exit, light/
heavy enemy attacks on fist guard, hit reactions/counters, gauntlet bonus,
arrow parry boundaries, fight-club/quest fist fights, B&S directional flanking
and target switching, dodge/roll, hitlag, Whirl/Rend, finishers, transitions,
combat end/death, save/reload, Ciri (Brawler should not apply), SAH HUD, and
analog movement/sprint. Confirm **zero** stuck animation speeds and no
persistent defense/damage multiplier after reverting to normal.

Only after tests pass report the Brawler-only variant as user-accepted.
Compiler acceptance is not evidence of in-game behavior.

## Specific stop rules

- No Computer Use/desktop automation.
- Do not modify current Vortex deployment, game, settings or live save.
- Do not make unproven edits inside Blood and Steel compiled blobs.
- Do not reuse superseded baseline/preset hashes as if current.
- Do not delete/disable whole Core 01 or package 04 just to strip Bestg.
- Do not treat a key that selects Brawler as a successful two-way toggle.
- If no clean separation is possible, document a bounded fallback and report
  the blocker rather than making an incompatible package.

## Handoff deliverables

Before any install: (1) verified Brawler dependency graph and hooked functions,
(2) exact source/hashes and B&S selector/setting locations, (3) changed vs
preserved payload table, (4) isolated compilation/tests and any genuine issues,
(5) private Vortex package path/hash if verified, (6) narrow manual user steps,
(7) rollback to the **already working** Core 01 + package 04 + original settings.
