# Inventory Review — acquisition-aware attention filter

**18 October 2026 · proposed behavior specification for the user's approved first rail category; no implementation yet.**

## Explicit authority and boundary

The user explicitly approves a **Review** category **first**, surfacing *new acquisitions that matter* while excluding the hundredth mundane crafting material; this is **not** an ordinary Recent list. The user also approves the specific visual reference and previously accepted equipped notch. Source authority: `design/inventory-reference-accepted-review.md`.

What is **not** yet user-specified: exact rarity/category thresholds, which equippable commons merit attention, whether acquired diagrams route to Crafting, how long pending entries stay, default launch category when Review empty, and the exact dismiss control. These are **implementation proposals** that should be validated with concrete item examples before promotion; they are not direct user ratings or a hidden quality model.

The Review row presentation, selected detail and Geralt are **identical** to normal categories. The only special elements are the first category name and an optional restrained pending count. Do not insert a popup, extra tab row, auto-sell button, or a second visual layout.

## 1. Source mechanism audit

`research/adaptive-inventory-v2-qol.md` audited the locally supplied `RecentLootTab (5.01)` archive. It wraps real `OnItemGiven`, stores item IDs/acquired quantity/source and aggregates arrivals within a short event window; it ignores some horse/stash transfers. The implementation has **one aggregate saved viewed flag**, **no durable per-item review state**, and no universal wall-clock acquisition timestamps. It modifies the Inventory, Alchemy and Crafting movie/script paths and overlaps native/FriendlyHUD/other wrappers. **Do not install its overlapping whole movies** or directly paste proprietary code; study the event and persistence mechanisms as compatible, licensed *architectural evidence*.

The existing FriendlyHUD can already suppress low-value native "new" indicators; that is a **separate feature**, not a Review acquisition source. The existing AutoLoot may produce many individual or batched acquisition callbacks; Review must tolerate duplicates and batch stacking without creating separate review rows.

## 2. Proposed minimal state machine

Each reviewable entry is based on a **validated acquisition event** with a currently owned, safely resolvable underlying inventory item:

- `pending` — newly acquired, eligible, user has not deliberately dealt with it.
- `reviewed` — user explicitly inspected its full details or equipped/used it (when applicable).
- `dismissed` — user explicitly chose not to review it.

Reviewed/dismissed entries leave Review but **remain in their normal inventory category**. There is no hidden destruction. Simply focusing/hovering or briefly opening Inventory **does not clear** a pending entry. An acquisition of a distinct item after a review can create a new pending entry even if its *type* is familiar. A second identical routine material addition does not.

Use a **save-scoped versioned ledger** with provenance and safe resolution, not the visible row's ordinal position as identity. Proposed logical fields: acquisition event ordinal, engine item's unique ID (with validity checks), item type/template/tag, count gained, category/source, current resolution state, decision reason, last action state and ledger schema version. Exact WitcherScript storage type/save declaration and ID lifetime must be verified against local 5.01 engine before claiming persistence. Do not reuse `JNT_mark` values or overwrite other mods' save fields.

Canonical Review list is `pending entries ∩ items still resolvable in player Inventory ∩ eligible policy`, sorted newest genuine acquisitions first. Deduplicate **visible rows by current item identity**; preserve the most recent acquisition ordering and safe quantity semantics for multiple grants/stack merges. On split/merge, stash move, sale, dismantle, consume, drop, load and NG+ transition, reconcile with current inventory; retire invalid entries without generating ghosts or deleting items. Stash-to-inventory transfer shouldn't automatically look like new loot if the underlying item was already owned.

## 3. Eligibility — policy candidates, not authoritative user thresholds

Classification must be **conservative, explainable and cheap**. It must not compute a universal item score or pretend "rarer always means better".

Suggested first-shippable baseline **pending user example tests**:

| Acquisition | Initial Review behavior | Rationale / open point |
|---|---|---|
| New named/set/relic/special equipment, unusual properties, meaningful non-routine gear | Include, if owned and inspectable | Important decisions are likely. Native metadata/quality tags must be checked. |
| Ordinary common sword/armor that is functionally indistinct from many previously acquired ones | Exclude by default unless explicitly pinned, or evidence of an unusual affordance | A hundred swords can become as noisy as a hundred crafting ingredients. Need exact safe criteria; never assume a higher damage number is an objective upgrade. |
| First acquisition of an unfamiliar equippable type | Candidate include | Novelty can be meaningful without an item-quality algorithm, but exact lifetime tracking must be validated. |
| Newly crafted unique equipment / meaningful quest reward | Candidate include | Event provenance should not drop because source is crafting/reward rather than looting. |
| New diagram/recipe that is auto-consumed or not an Inventory row | **Defer until native target-jump supported** | Do not create dead Review entries pointing at vanished items. Potential later Crafting/Alchemy deep-link. |
| Repeated herb, ore, monster component, alchemy crafting ingredient, bulk food refill | Exclude | Explicit user requirement to avoid trivial accumulation. |
| Routine stack increase to an already-owned item | Exclude unless item has a reason to be reviewed | Do not flood from quantity deltas. |
| Quest-critical object and unique document | Keep visible in native Quest/Other; include in Review only with valid semantics and safe navigation | Quest objects must never be hidden or altered by Review classification. |
| User-marked/pinned item | Include as a later optional feature if real persisted pin is supported | Avoid shipping a fake marker without identity guarantees. |

These are example **rules to evaluate**, not a license to preempt the user's review decisions. In the first implementation, record a short reason tag (e.g. new unique equipment / manually retained) for each included entry. If uncertain, keep items accessible normally and test the chosen inclusion threshold rather than silently hiding native items.

No screen-space budget or arbitrary "show 12 max" cutoff should discard pending important items. Use native list scrolling.

## 4. Interaction and focus contract

- The first category is **Review** at all times, with an accurate pending count only if confirmed by the real data model.
- Clicking/confirming a Review row selects the **actual item ID**, drives exactly the same middle selected-item details/compare data, and uses the **same item actions** as the item's normal category.
- Deliberate full-details examination may mark reviewed, but mere list highlight, controller D-pad passage or hover does **not**.
- A small dismiss action operates on the selected pending item without changing equipment, quantity or its ordinary-category visibility; after dismissal, focus moves predictably to the nearest pending entry and shows real details.
- Equip/consume/craft transitions should preserve menu state and selected identity where still valid; do not mark reviewed from failed actions.
- If the Review list becomes empty, show a restrained "Nothing to review" state in the existing list area or fall back to the previously active category **only after the user confirms preferred behavior**. Do not invent a new empty-state screen or add an intrusive explanation.
- Review must remain usable through controller, keyboard and mouse; hints come from the accepted **single device-aware footer**, no hardcoded mixed-key labels.
- Category switches preserve separate scroll/selection state without re-firing acquisition events.

## 5. Tests and release gates

**Pure policy/data tests before any GUI cook**:

1. 100 sequential identical herb pickups, one new legendary weapon: Review contains weapon only.
2. Four ordinary junk swords in a batch: no mandatory inspection spam; verify the exact chosen common-gear threshold.
3. New nonroutine item gets pending; hover it and close/reopen the menu: still pending; deliberate inspect/dismiss: no longer pending.
4. Save/load with pending items, including acquired-before-load order and count.
5. Acquire an item, then drop/sell/dismantle/consume it: no ghost selectable Review row and native inventory unaffected.
6. Equip an item, and subsequently unequip it: no duplicate Review row or false new acquisition.
7. Split/merge stack and send item to/from stash: no accidental duplicate pending and no loss of real owned items.
8. Acquire two distinct copies of same template and a new copy after prior review: stable per-item decisions and correct newest-first order.
9. Shop/stash/horse, quest and DLC/mutagen types: all native categories still contain complete item data; Review only filters a view.
10. Controller/keyboard navigation and changing input device with Review selected; no lost focus or duplicated footer.
11. Load legacy save without any review-ledger fields: initialize safely, no retroactive fabricated acquisitions.
12. Any record that cannot resolve to a real item is dropped or quarantined safely; never render a dead row with guessed stats.

**Integration gates:** exact collision matrix for `CR4InventoryMenu`, `W3GuiPlayerInventoryComponent`, `OnItemGiven`, `SetInventoryFlashObjectForItem`, FriendlyHUD/AutoLoot and currently merged scripts. Use independent test-save mode; no unapproved live Vortex deployment or save mutation. Validate in-game after list UI is accepted and stable, not in parallel with another large structural redesign.

## Acceptance definition

Review only interrupts the user for **newly acquired, potentially meaningful decisions**. The hundredth herb never becomes an administrative task; no item is lost from its normal category; reviewed/dismissed state really persists; native Inventory keeps working. No silent item ranking, auto-sale or destructive filtering.
