# Approved Inventory — unified normal-category implementation scope

**18 October 2026 · newest user correction.** The user explicitly asked whether building the approved redesign **for all Inventory categories together** would be easier and more coherent than a Weapons-only implementation with two competing logics/layouts. Treat this as the active first-playable architectural target, superseding the earlier Weapons-only Gate 2 release scope.

## Decision

Build **one Inventory composition and one row/data/focus architecture** for the normal unfiltered **player Inventory**. Internally implement and test categories incrementally, but do not design a second native layout as the permanent solution for non-Weapons categories. Final approved composition remains the exact category rail → single-column item list → persistent details → live Geralt, with same scale, background cohesion, native equipped notch and one input footer.

### Ordinary categories in the first unified candidate

| Rail category | Underlying data/action differences to preserve |
|---|---|
| Weapons | Steel/silver, ranged/crossbow/bolts, equip/unequip, restriction/comparison, icon/text row. |
| Armor | Armor parts, worn state, protections and requirements, compare/equip/unequip. |
| Consumables | Potions, oils, decoctions, food and actionable materials per native semantics, quantity and use/apply/assign actions. |
| Bombs | Bomb inventory, charges, quickslot/assignment/native selection restrictions. |
| Pockets | Pocket/utility items, Hoods/dye/special equipment interactions, masks/tools and native target semantics; never fake generic equip. |
| Quest Items | Native eligibility/quest tags, readable/use semantics, no dropping critical items, keep complete information. |
| Other | Ingredients, mutagens, crafting materials, books, runes/glyphs, Roach parts, trophies, junk and miscellaneous, classified by actual native tags; searchable/sortable according to safe native actions. |

**Native tab index is not category order.** Game tab enum 0 Ingredients / 1 Quest / 2 Default / 3 Alchemy / 4 Equipment / 5 Books is not a bijection with the approved rail, and Equipment tab 4 includes multiple types. Build a **single exhaustive native-eligible inventory projection** keyed by genuine item IDs and type/action data, then map to the rail without duplicates or omissions. Check the full source audit in `research/inventory-approved-gate0-1.md`. Review intentionally overlaps categories; ordinary categories are exhaustive/disjoint.

### Architecture

- One retained `SlotInventoryGrid`-compatible row renderer, one `SlotsListGrid`-compatible one-axis controller, one selection/event engine and one consistent scene/display hierarchy for **every ordinary player category**.
- One persistent middle details provider `ItemId → native tooltip payload`, adapting the fields (damage, armor, use/quantity, crafting info, quest/read info) instead of pretending every item is comparable equipment. No fake data or damage delta for herbs.
- One native action adapter keyed by verified item action/context (equip/unequip, use, assign, read, restrictions, drop where permitted); never implement all actions as `Equip`. Retain modal drag/target callbacks.
- One rail state machine: category switch changes data filter, row dataset and action/hints; **does not rebuild the entire scene, reset live Geralt or change layout**. Preserve separate per-category selection and scroll by valid item ID.
- One input-feedback owner via the verified Common script pipeline, keyboard/gamepad/mouse prompts appropriate to native available actions, not hardcoded dual prompts.
- Static item scale and native source-art quality; no P1/P2 size-to-item-count changes; retained row instances and icons, ID/revision-aware diff to prevent flicker.
- Old paperdoll orbit art stays suppressed only in custom player Inventory; native targets are accessible by on-demand controls. Preserve Menus v4 outside affected state.
- Background/ground/exact lighting may be simplified so long as cohesion, Geralt size/proportion and general aesthetic are analogous to the user's approved reference.

### Scope distinction — Review and special modes

**Review remains FIRST in the approved visual rail**, but the user-approved *attention-filtered Review* needs a save-scoped `OnItemGiven`/unique-ID acquisition ledger, classification, per-item pending/reviewed/dismissed, ownership reconciliation and safe persistence. This is a **different data-domain feature**. It should be implemented in a second gated phase after normal category parity and visual/interaction stability. Do **not** fake Review counts, route all new flags there, or leave a clickable inert Review item. At prototype time either provide an explicitly designed disabled/empty uninitialized state approved by the user or defer exposing it as an active category while retaining its reserved rail position. If source permits reliable ledger implementation cheaply and independently, separately report scope/cost and ask before broadening.

**Shop, stash and horse inventory modes** are *not just ordinary category filters*: they have distinct owner/state/action/provenance contracts. Keep their accepted native v4 behavior for this iteration behind state-specific mode gates, including correct restoration on entry/exit. Do not use this as a reason to keep a second native layout **within the normal player Inventory**.

**Crafting and Alchemy standalone menus** also stay on accepted v4; player Inventory views of consumables/ingredients are in scope.

## Development order within one candidate

1. Establish one common retained scene, renderer and category projection. Test Weapons + Armor first to verify equipment actions, but **don't ship Weapons as a completed separate visual system**.
2. Extend the **same row/detail controller** to Consumables, Bombs and Pockets, checking native quantities and use/assignment/drag and safe Hoods.
3. Extend the identical renderer to Quest Items and Other, ensuring exhaustive eligible tags, scrolling for very large materials lists, long titles, special actions, sorting and no phantom rows.
4. Test transitions between all ordinary categories, switching input devices, selected detail revision, equip/use/consume, stat changes, native modals and Shop/Stash mode boundary. Instrument blink/unload/visibility creation to prevent P2-type flashing.
5. Package **one** rollbackable private player Inventory candidate *only when basic category parity works*; if a specific category has a real blocker, record the exact method/data contract and offer a conscious fallback choice instead of silently giving it a different layout.
6. First manual in-game acceptance: visual fidelity, native action parity and zero recurrent flicker, sparse and dense inventory; Review ledger then added in a separate pass after this acceptance.

### Why this could simplify rather than complicate

The previous Weapons-only plan lowered initial coding surface but would have required swapping between a new row scene and unrelated native grid scene as the user switched common categories. Those transitions create presentation ownership, focus, footer, stale tooltip and visibility conflict risk, especially given observed P2 flashing. A single player-Inventory renderer and item-ID model require more **type/action mapping upfront**, but can reduce duplicated display code, runtime mode churn and long-term integration/debugging.

Do not assume total engineering time is guaranteed lower: heterogeneous native tags, quest restrictions, use/assign, books, Hoods/Roach and the complete 'Other' projection can be difficult. Test and document those rather than skipping them. Scope should be **unified normal categories**, not "all native movies and all third-party QoL features."
