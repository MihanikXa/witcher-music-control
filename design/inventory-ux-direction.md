# Inventory-first UX direction — 11 October 2026

**Latest explicit user decision; supersedes older inventory layout proposals.** This is an intention and design hypothesis, not a claim that code exists.

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
