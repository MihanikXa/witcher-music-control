# Inventory-first UX direction — 11 October 2026

**Latest explicit user decision; supersedes older inventory layout proposals.** This is an intention and design hypothesis, not a claim that code exists.

## 16 October 2026 — newest explicit visual feedback and revised order

See [verbatim user feedback](../research/ink-gear-grid-v1-user-feedback.md). The user finds the v1 item grid **too dotted/busy yet too small/secondary**, wants **Geralt somewhat bigger**, **less persistent text and item details**, **far fewer/less intrusive footer hints**, and an **extremely clean potentially translucent backdrop**. They also find the current top navigation busy and expect **Ink & Iron's complete menu implementation** to improve it. The previously identified auxiliary slots under Geralt and disconnected detail region remain unacceptable.

**Sequencing correction:** **Before Gear-grid v2, integrate and test the 0.8.6 Ink & Iron menu UI baseline** (not All-in-One HUD overwrite) in a cloned profile. Its source archives are already locally hashed in [the v1 implementation](../research/ink-gear-grid-v1.md), but installed shared menus and current compatibility contracts must be independently verified. Preserve custom HUD RC2, QuietFolio, Outfit Wheel/Smooth Map/Hoods and the reversible v1 prototype. Once a coherent common menu visual language exists, redesign Inventory for **dominant clean browse grid, larger unobstructed Geralt, contextual compact details/actions, minimal visible prompts, no dotted empty-cell wallpaper**, with background translucency only after a genuine world-behind-menu and readability check.

These requirements explicitly outrank older assistant-only ideas to just reposition the existing grid/slots/details.

## 16 October 2026 — version-specific Inventory implementation

**Latest requested source is Ink & Iron 0.8.6**, not the archived `reference/ink-and-iron-0.8/` (0.8.0) resource inventory. Upstream 0.8.6 fixes Equipment First D-pad skipping, 0.8.5 adds a hide-connector option, and 0.8.4 changes Inventory item cards; the official Hoods optional patch originates in 0.8.3. Exact current source artifacts and dependencies must be verified locally before a build. See [0.8.6 Inventory handoff](../research/ink-and-iron-0.8.6-inventory-handoff.md). **Freeze the working custom HUD v4/RC2**; only Inventory is in scope.

## 15 October 2026 — official Ink & Iron / Hoods compatibility update

The user corrected the earlier assumption that Hoods inventory ownership remains an outstanding integration blocker: **Ink & Iron now supplies its own Hoods Compatibility patch**. The author added this optional file in **Ink & Iron 0.8.3 (13 October 2026)**; the Nexus file description says it **restores Hoods dye handling on top of Ink & Iron inventory**, requires both Hoods and Ink & Iron UI, and is to be installed alongside them. Official sources: https://www.nexusmods.com/witcher3/mods/13111?tab=files and the 0.8.3 changelog. This supersedes the **default assumption of an unsolved Hoods versus I&I inventory merge**, not the need to check the actual installed file owner and functionality.

**New implementation baseline:** Start from the effective **current-version I&I Inventory plus its official Hoods patch**, not the old Hoods-owned/retail inventory movie as the expected interface. Read the local patch manifest, `panel_inventory.redswf` ownership and priority, compare Hoods dye/hood behavior and menu/action contracts, and preserve the patch's compatibility hooks in the custom Gear-grid vertical slice. If there is any mismatch, identify the exact gap rather than automatically rebuilding Hoods support. The user's intended one-screen grid/Geralt preview/equipped markers and organization reform remain unchanged.

**Current I&I design has also evolved:** in 0.8.4, the author changed Inventory item previews to contextual pop-up cards beside hovered slots, with content-sized descriptions and Shift comparison, while adjusting its Equipment First view. Inspect the current installed implementation rather than reproducing assumptions based on 0.7.4 or 0.8.0 screenshots. This upstream enhancement may inform detail-card treatment, but does not supersede the user's preference against the circular equipment constellation.

## Core decision

**Keep Witcher 3's Inventory as one screen.** The user **rejects the entire Ink & Iron equipment-around-Geralt composition**, not merely the sparse grid. The circular equipment orbit (swords/armor, ranged equipment, consumables, Roach, pockets/bombs) appears spatially arbitrary, makes the paper doll decorative rather than organizing the view, and scatters unrelated subsystems across black negative space.

The user proposes a Breath-of-the-Wild-like **inventory-first grid**:

- **Geralt remains a clean character preview**, without equipment circles arrayed around him.
- **Equipped gear exists in the same item grid**, distinguished by an unobtrusive but obvious equipped marker/border. Preserve equipment slot identity and actions underneath; don't simply hide active equipment controls if they are necessary for navigating/equipping.
- **One selected item** has a focused description, stats and comparison with equipped equivalent; detail should not float between competing layout systems.
- **Contextual category navigation** and compact, coherent placement of actions replace independent radial groups. Preserve controller, mouse, sorting, equip/unequip, comparison and quick-slot assignments.
- **Do not create separate top-level equipment/satchel menus.** In-screen tabs/filters are permitted; do not needlessly duplicate item collections.

The user's stronger complaint is *inventory item accumulation and administrative overload*—many crafting materials, miscellaneous objects and largely equivalent items clutter the normal browse path. Cosmetic alignment cannot solve that alone.

## Three distinct problems and responses

| Problem | Mechanism | Preferred remedy |
|---|---|---|
| Compositional clutter | Disconnected equipment circles, small sparse inventory grid, separate inspection column | Replace entire inventory arrangement with a clear grid + character + contextual detail hierarchy |
| Organizational clutter | Gear, potions, crafting components, junk and documents all demand category navigation | Intent-based tabs and filters, equipped/recent defaults, predictable sort; low-importance materials accessible but not foregrounded |
| Management clutter | Repeated low-value loot and crafting ingredients accumulate; rarely inspected individually | Favor existing inventory/loot sorting and acquisition filters first; consider recipe-level material visibility, recent acquisitions and accessible stash resources only if safe |

### Proposed hierarchy

1. **Gear** — weapons/armor and relevant equipment; show currently equipped markers. Sorting by utility, category or recently acquired, rather than arbitrary spatial slots.
2. **Usables** — potions, oils, bombs and common actionable utility.
3. **Recent** — recently acquired objects if feasible; must have explicit reliable recency tracking, not a fake cosmetic tab.
4. **Satchel / All** — resources, crafting components, books, quest items, junk, miscellaneous; no deletion of data and no hidden quest-critical objects.
5. **Filters** — item type, equipped/new, weight/value/rarity, usable-now where available. Avoid large persistent category stacks; preserve direct discoverability of any hidden-by-default group.
6. **Details** — one place for stats/requirements/durability/set bonuses and direct current-equipment comparison; expand deeper information on request.

These names and exact tabs are **proposals**, not a mandate to add six new data models. Prefer reusing existing categories, predicates and menu views.

## Reference-mod research (not blanket install recommendations)

- **Ink & Iron 0.7.4:** coherent default UI aesthetic worth keeping almost universally **except its Inventory and Shop layout**. Its experimental equipment-first option focuses on slots+Satchel and is the wrong layout direction, though its controller behavior and code can be studied.
- **Sort Everything 1.53:** potential sorting / selection-order reference; verify local compatibility and intersections.
- **Recent Loot Tab:** potential recent-acquisition reference; investigate underlying tracking, category data and menu integration.
- **Friendly Stash:** potential crafting-from-stash mechanism, but requires current-version adaptation and safety review; do not assume working on Remastered 5.01.
- **Current AutoLoot replacement:** may already offer optional category/value filters; prefer existing tested options to new item-deletion logic.

Source of truth for implementation is actual current 5.01 runtime menus and installed mod stack. A reference mod being relevant does not mean it should be installed simultaneously.

## What to prototype — only one functional vertical slice

First create a *proof of operation* for a simple Gear view on the same Inventory screen:

- selecting a sword in the grid, marker on the equipped sword;
- stat comparison, equip/re-equip/unequip where allowed;
- keyboard/mouse and controller focus and back navigation;
- no floating paper-doll slot constellation; Geralt visible as a coherent preview;
- intact quick-slot, Roach gear, weight, DLC item behavior and relevant Hoods features even if visually subordinated;
- same user save and selected item for before/after screenshot and action-count comparison.

**Gate:** Do not remove the equipment UI contract unless input routing and state transitions have been examined. Hidden movie elements may contain functional hit areas/logic. A one-screen redesign can still be a substantial SWF/ActionScript task; investigate rather than promising it's trivial.

## Validation / success

Grid easier to scan than vanilla and Ink & Iron; item selection faster, no extra menu hops; material/junk overload no longer dominates primary inventory; recipe/crafting and quest items still discoverable; visually composed Geralt preview and coherent separate browse/details regions; working special equip categories, stash, loot, merchants and mod-specific equipment mechanics. At least 1080p and 4K, controller and keyboard.

Preserve accepted NPC/QuietFolio/movement patches and use a separate reversible Vortex profile. Avoid distributing adapted Ink & Iron author assets without permission. See [integration plan](../research/ink-and-iron-integration-plan.md).
