# Adaptive Inventory — proposed staged build (17 October 2026)

Status: proposal for user review, not code deployed or runtime certified. Work only on ui-overhaul, preserve the accepted 0.8.7 Menus v4, Gentium/Item Art/Bestiary/Map and HUD RC2.

**18 October correction (supersedes P1 \"first playable\" success framing):** The
user *rejected* P1 in-game. Its old-orbit background, native topbar collisions,
tiny scattered groups, blank contextual summary, duplicate/hardcoded
keyboard/gamepad footer and detached Geralt contradict the agreed UX.
The active next work is [the P2 composition/interaction contract](adaptive-inventory-p2-composition-contract.md).
Do **not** infer that P1's native validation or 16 offline tests establish
visual usability; preserve P1 only as a functional experiment.

**Historical 17 October implementation update:** [Gear Prototype 1](../research/adaptive-inventory-v2-gear-p1.md)
is implemented and privately packaged on the accepted v4 Inventory. Final native
cook/validate/pack/metadata and 16 targeted offline tests pass; in-game acceptance
and manual installation remain pending. [QoL source findings/adoption matrix](../research/adaptive-inventory-v2-qol.md)
cover all three supplied archives and current FriendlyHUD/AutoLoot. No optional
runtime mod was integrated. After Gear acceptance, prioritize adaptive
Usables/Satchel before acquisition-aware Review or safe bulk cleanup.

## Guiding principle
Items that require no decision should generate no management task. Separate native item/action state, custom display/focus, and optional third-party filtering/cleanup. One Inventory screen, no persistent three-column details dashboard.

## First playable release: Gear
- Base exclusively on Menus v4 effective panel_inventory.redswf; read actual enabled mods.settings, Hoods dye, Outfit Wheel, FriendlyHUD and Script Merger ownership. Reuse tested 0.8.6 Gear-grid v1 *behavior*, not its rejected SWF/layout.
- Composition: broad item-driven equipment grid with little empty-cell ornament, larger unobstructed Geralt preview, selected-item compact delta strip within grid area; detailed stats on explicit inspect only. Selection must not move the whole layout. Gear in same grid including native equipped identity. Essential auxiliary/slot actions in contextual focus mode, not an always-on cluster.
- Input: gamepad/keyboard/mouse focus, category/filter changes, shift/LT compare, equip/unequip/re-equip and persistent selection. Verify stable D-pad single steps, hold, fast icon focus, instant summary rendering. Preserve Shop/Stash/Horse, Hoods quickslot2 dyes, Roach and 0.8.7 text.
- Don't invent a gear-quality score, acquisition timestamps, destructive rules, or permanent tabs. Use existing values transparently.

## Optional external mod research; no blanket installation
- Existing FriendlyHUD: already has default inventory category and low-value new-item suppression; confirm live settings before duplicating.
- Sort Everything 1.55: first sorting candidate, 5.01 AS + annotation support, damage/armor equipment and stash/crafting sorting. https://www.nexusmods.com/witcher3/mods/1710 ; avoid stacking with Smart Sorting.
- Recent Loot Tab 1.0: independently records acquisitions; inspect source/data model for *contextual* review area, not another permanent tab. https://www.nexusmods.com/witcher3/mods/13981 . Minor recipe-jump label bug documented.
- Junk Not Treasure 1.0: saved protect/sell flags plus confirmed bulk merchant/craftsman operations; only isolated safety tests, recent release and likely UI/input overlap. https://www.nexusmods.com/witcher3/mods/14451
- Quick Surplus Seller 1.x: material reserve before merchant sale; optional later, selling-button overlap with Junk Not Treasure. https://www.nexusmods.com/witcher3/mods/14170
- Friendly Stash Next Gen 0.9.4: earlier 4.x source only, **not** verified for Remastered 5.01, so leave to later. https://www.nexusmods.com/witcher3/mods/8023
- AutoLoot: identify user's current actual working setup; do not install a second system. Quick Inventory replacement touches HUD/radial; avoid due accepted RC2.
- Some previously claimed Stack Your Items Remastered versions were not corroborated; current public mod page shows 1.1.0, explicitly Next-Gen 4.x. Do not recommend unverified version as 5.01-safe.

## Next release after Gear passes
Implement adaptive Usables/Satchel density and saved category focus; audit Sort Everything script/runtime collisions. Add a restrained Review cue only if real acquisition records have durable item identity; never use isNew as a fake timestamp. No forced new tab. Existing items remain discoverable.

## Separate cleanup integration
Test protected marks and one confirmed batch merchant/craftsman action on disposable saves. Decide a *single* cleanup entry point after comparing Junk Not Treasure and reserve-based Quick Surplus Seller; never combine conflicting sell hooks by load-order guess. No automatic deletion or silent conversion of unique/quest items.

## Where to start
One targeted Codex run: inventory current-owner + method/class matrix, inspect optional mod archives if present under ignored reference/, inspect v1 functional paths, then implement an **actual Gear first-playable private ZIP** on the v4 base with no added external dependencies. Do not stop at a mockup or audit if source is sufficient. Keep rollback to v4. Capture source evidence and resource-key collision manifest; attempt native cook/validate/pack/metadata, document failures honestly. User tests screenshots and controller/keyboard actions in cloned Vortex profile.

Acceptance tasks: find/compare/equip an acquired sword without focus reset; browse a large equipment stash; unequip/re-equip safely; switch categories and return to previous selection; access quickslot/Roach/Hoods dye; verify Shop/Stash/crafting unaffected. Later measure sell 20 ordinary items with accurate preview and no valuable loss. Verify 1080p/4K, early-game sparse and late-game full inventory.

Code/version boundaries: no automatic Vortex, live game, settings or saves changes; don't distribute third-party code/compiled assets in Git. Original tooling/tests/manifest only. External mods are feature/comparison references until compatibility is tested.
