# Inventory v2 — phase transition after Menus v4

**17 October 2026.** Current repo `ui-overhaul`, latest private build Menus v4 Typography Finishing (commit `76f1b0f`). User said **"Alright, all done. Let's continue to the next task, what should we do next?"** This ends the menu visual polishing work in conversation, but the user did not provide individual action-by-action test results. Do not imply that every menu, input and optional module was exhaustively retested.

## What is accepted/frozen

- Slim Ink & Iron 0.8.7 shared navigation and menu layout, menu backgrounds and engravings, targeted Icon Pack/Bestiary Art/Map Inked.
- QuietFolio/Gentium menu-specific small-cap styling, secondary label alignment/colors, heading/prose/footer typography as implemented in v4, subject to future specific regressions.
- Separately accepted custom HUD v4/RC2, with restored Tab/LB radial wheel, controller glyphs, bars and quickslots.
- Existing Hoods dye integration, Smooth Map, Outfit Wheel, SAHUD/FriendlyHUD, merged gameplay scripts and working font library remain in effect.
- Private Menus v4, v3/v2 and Gear-grid v1 releases must remain intact/rollbackable. No automatic modifications to Vortex/game/settings/saves.

**Technical note:** The Menus v4 WCC native cook stalled twice; its resulting packaged ZIP was produced through a byte-checked same-key reconstruction fallback, with 13 targeted static tests. User says work is done, but this does not establish native commandlet validation. If convenient, `tools/build-menu-finishing.py verify-native` may be retried **separately** when WCC startup works; avoid reopening accepted visual design for this.

## Next task: true Inventory redesign, not v1 polishing

The **user-approved goal** is one coherent Witcher Inventory screen with a dominant browsable grid including equipped items, unobtrusive equipped markers, a somewhat larger **unobstructed Geralt preview**, one focused details/comparison region, and compact access to utility/satchel/crafting. Fewer labels, icons/dotted empty-cell markers and persistent footer hints; separate low-value materials from frequent gear without deleting or hiding quest-critical objects. Preserve Witcher identity and the **current** 0.8.7 menu typography/artwork. Investigate any optional translucent backdrop only later, after proving a live world image exists beneath the menu and readability remains adequate.

**Explicit v1 complaints to avoid repeating** (`research/ink-gear-grid-v1-user-feedback.md`, screenshots and assistant review):
- Dotted empty-cell wallpaper too visually busy while the usable browse grid is too small and subordinate.
- Geralt too small; utility slots relocated over his feet. Simply moving native paperdoll slots around is not a redesign.
- Too many permanent headings, informational fragments and bottom button hints.
- An isolated details column not integrated with a meaningful selection/focus hierarchy.
- Hardcoded Gear title incorrectly overlapping native Alchemy/Crafting title; category-dependent layout was missing.
- Need less administrative work for resources, junk and miscellaneous items without inaccessible categories.

## Recommended implementation sequence

1. **Source/release gate**: Make the now-accepted v4 `panel_inventory.redswf` and the actual deployed Hoods/OW/menu owners the new immutable **functional base**. Inspect current v4 action/text modifications, `SlotPaperdoll`, `InventoryTabbedListModule`, `TooltipInventory`, and their focus/drag/dye/quickslot/Roach contracts. Compare v1 code paths to find portable functional improvements without copying its old SWF or visual geometry. Recheck modern 0.8.7 Inventory and Hoods patch compatibility, not stale 0.8.0 owner priorities.
2. **One cohesive composition pass**: Give actual item browsing visual priority with an item-driven grid and invisible or very subdued unused cells; Geralt larger and free of overlapping slots; one contextual inspection area; category-appropriate layouts, display-only marker/spacing changes. Design for both six-item level-1 inventory and populated late-game inventory, including long names and different aspect ratios.
3. **Functional vertical slice**: Gear selection, equipped markers, equip/unequip/re-equip, comparison, mouse/keyboard/controller incl one D-pad movement per press, Tab/LS auxiliary focus, clean access to Hoods dyes/hoods, Roach gear and quickslots. Keep existing slot objects/contracts accessible, e.g. a discrete auxiliary panel or mode, instead of silently destroying hidden native elements.
4. **Broader category organization after Gear works**: Usables, resources/quest materials and filters within one screen. Do not invent a Recent tab without actual reliable acquisition timestamps. Preserve Shop/Stash/Loot shared-movie states, weight, quest objects and special gear.
5. **One private candidate and user game check**: Native validation where possible, hashes and resource collision gate, 1080p/4K/early and full inventory tests, manual Vortex installation/rollback. Compare composition and real action-count/interaction behavior, not static preview alone.

This is a **single workstream**; do not expand into Map/Quests/Character redesign or revert menu v4 typography. A fuller upstream compatibility update is unnecessary without an observed deficiency. If a radical new layout cannot be made functional in one Codex run, prefer a clean architecture + one working Gear slice over multiple unusable approximations.

**Next deliverable:** a targeted source-based Gear-grid v2 first playable candidate using the current Menus v4 base and a visual/interaction contract map. Do not begin with a cosmetic v1 v2-delta that merely squeezes the old three independent layouts.
