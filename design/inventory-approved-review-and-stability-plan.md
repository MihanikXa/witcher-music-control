# Approved list — acquisition and rendering contracts for the next slice

18 October 2026. Planning only. Companion to the
[Gate 0–1 source/proof receipt](../research/inventory-approved-gate0-1.md).
High-level Review is approved; example policy thresholds and empty/default
behavior remain proposals. No Review runtime code/save fields are installed.

## Real acquisitions and ownership

The current 5.01 assembly has `W3PlayerWitcher.OnItemGiven(SItemChangedData)`;
the native player event calls its superclass and registers the actual granted
`data.ids[0]` with GUI. The supplied Recent Loot reference wraps the same event,
then examines real IDs/gains/source. Its saved arrays contain SItemUniqueId,
quantity gained and provenance; its engine-time window groups arrivals rather
than furnishing durable acquisition timestamps. Actual append order supports
chronology without inventing time. Review should use a monotonic save-scoped
event ordinal, not native new-item flags or inferred wall-clock dates.

Recent Loot's **one** saved recentLootViewed bool is not per-item review state;
Inventory closing changes it. It also trims old records by cell budget, can
retain repeated IDs from later acquisitions and excludes equipped items from
its particular display. None of those policies should be imported for Review.
Its event wrapper is architectural evidence, not copied code or a guarantee that
all current engine/annotation signatures and saved identity behavior match.

Proposed original annotation boundary: wrap the verified player event, preserve
wrapped behavior/signature, observe the post-grant native IDs/quantities, and
classify only after actual ownership resolves. Audit full `data.ids`, not only
ids[0]; split/merged grants may require more than one record. Preserve native
inventory update and UI notifications. No raw NoShow/quest/filter bypass.

Other necessary boundaries, **only where real provenance requires them**:
CR4InventoryMenu OnMoveItem/OnMoveItems and horse/stash transfer paths;
native loot/container/HUD-popup paths; successful purchase/craft/reward sources.
Recent Loot's TakeAllItems/OnPopupTakeItem/OnPopupTakeAllItems/source stack shows
where transfers/grants originate, but installing those wrappers would intersect
FriendlyHUD/AutoLoot/current merged scripts. Build an exact signature/order audit
before adding wrappers; do not replace their methods, import the mod's whole
Inventory/Alchemy/Crafting/Gwent movies, or write its default settings.

## Save-scoped state proposal

Versioned original ledger, preferably on the player save owner, conceptually:
schema version; next event ordinal; records containing actual engine item ID,
template/category verification key, gained quantity, source, eligibility reason,
ordinal and pending/reviewed/dismissed state. A current resolved ID indexes rows;
record ordinal identifies acquisition history. **Neither template nor row index
alone is an item identity.** No existing JNT modifiers/foreign saved fields used.

`saved var array<SItemUniqueId>` is observed in Recent Loot; it establishes a
supported saved representation, **not** identity stability across stacking, save
conversion, equipment replacement, transfers or NG+. Decide native supported
record/parallel-array representation only after isolated compile and disposable
save tests. UI movie receives a projection, never owns durable state.

Reconciliation rules to test:

- Startup from legacy save: empty ledger, no retroactive acquisitions invented.
- Load/reopen: retain actual pending order/states; validate ID, native ownership,
  template/category and current quantity. Unresolvable records cannot be selected.
- Repeat grant/stack merge: one visible row per current ID, most recent genuine
  event ordinal, gain clamped to currently owned quantity. No repeated herb rows.
- Split/re-ID: do not map by template alone. Quarantine unresolved history until
  actual native change/transfer provenance identifies the successor.
- Sell/drop/dismantle/consume: retire invalid projection records, never touch the
  actual item. Reconciliation is not permission to remove inventory objects.
- Stash/horse return: already-owned transfer does not create a new acquisition.
- Two distinct same-template items remain distinct; after prior review a newly
  acquired distinct copy can become pending again.
- NG+/new save: separate save scope, reconcile only actual persisted ownership.
  Do not carry a global Documents registry between saves.

No truncation by visible row budget or expiry timer silently discards pending
important items. A later hard storage cap needs explicit policy, not a UI fix.

## Provisional explainable eligibility

`tools/propose-inventory-review-policy.py` is an executable **discussion model**.
Its normalized facts are not invented engine APIs/tags; metadata extraction is
still a future verified producer. It uses no damage score or automatic upgrade
decision and does not implement a ledger.

| Example | Proposed result | Reason / decision still needed |
|---|---|---|
| 100th celandine, common ore/monster-material increase | Exclude | Routine accumulation; explicit approved attention principle |
| New nonroutine named/set/relic/special weapon/armor | Include | Potential decision; map native metadata and agree exact boundary |
| Four functionally indistinct ordinary junk swords | Exclude provisionally | Common gear can flood attention too; no damage threshold |
| First unfamiliar equippable type, e.g. crossbow | Include provisionally | Novel affordance; saved novelty semantics need validation |
| Food/potion refill of established item | Exclude | Routine refill, not a new equipment decision |
| Unique inspectable unread document | Include provisionally | Actual meaningful action; keep normal quest/book access |
| Already-read ordinary book | Exclude | No fresh decision from the same read item |
| Auto-consumed learned recipe/diagram | Defer | No owned row; needs native target-jump rather than a dead item |
| Quest object / unknown mod type with no established action | Defer classification | Never hide it from native ordinary categories; no guessed eligibility |
| Sold or unresolved pending item | Exclude from projection | No real selectable target; no destructive action |
| Stash return of a noteworthy sword | Exclude as acquisition | Already owned; existing pending record can remain |

Rare **material** alone is not automatically important; a category/rarity name is
not sufficient evidence of actionability. Exact quality/tag mappings, familiar
common gear policy, meaningful crafted/quest rewards and any user-pinning feature
require concrete native examples. They are not silently fixed by the model.

## Review actions and persistent details

Review is a first **virtual rail category**, not native enum index 0 or another
top menu. It uses the identical row/details/action path. Counts come only from
the reconciled pending projection; proofs' 2/3 counts are explicitly illustrative.
Ordinary category visibility is independent and complete.

**The persistent middle panel changes an earlier Inspect assumption:** native
tooltip delivery, selection, hover or simply seeing the details cannot mark
reviewed; these happen automatically for every highlighted row. Only a deliberate
verified inspect/description action, successful applicable equip/use, or explicit
dismiss can clear pending. Failed actions do not clear. Exact gesture should use
the native binding provider after control mapping; no extra footer system.
Dismiss changes ledger state only, then selects the nearest remaining real ID.

Pending → reviewed/dismissed is durable. Ordinary unequip or closing Inventory
does not reopen/clear it. A new independent genuine acquisition can create new
pending state. When empty, preferred last-used-category/default and manual empty
view behavior need user agreement; no automatic empty-first-page trap is imposed.

Required later disposable-save tests: pending before/after reload; deliberate
versus hover; two copies and reacquisition; stack merge/split; invalid records;
transfer versus acquisition; AutoLoot batches; craft/purchase/reward; quest/DLC;
legacy/NG+; keyboard/pad/mouse; and ordinary category completeness. Python policy
examples **do not prove** any engine persistence or event completeness.

## P2 flashing: hypotheses and instrumentation

The user observed flashing. No live reproduction/traces were performed here, so
none of the following is asserted as the cause.

| Source path | Mechanism that could explain a flash | Trace / next implementation rule |
|---|---|---|
| P2 Gallery.p2Populate → cleanUpRenderers; SlotBase.cleanup → unloadIcon | Incremental item update can unload/reload **every** visible icon, although only one item changed | Record item ID, renderer instance, cleanup/load/complete frames; retained-ID diff must not reload unchanged paths |
| Native grid append/remove during equip, followed by P2 full population | Repeated state/data invalidations within one action; selection restored after intermediate callbacks | Log ordered update/remove/append/select revisions; coalesce one action's updates, maintain selected ID once |
| P2 p2Tick wanted predicate / p2Enter/p2Leave | Native renderer-active/category/state transition can tear down and restore an entire presentation | Log predicate terms and enter/leave reason once per change; no leave/enter from selected item or device alone |
| p2SetMode / p2Tick repeated visibility writes and p2Targets | Native selection/drag flags may temporarily suppress gallery/details while native handlers also change focus | Log visible transitions with writer/mode; one retained scene/state owner, native modals explicit |
| iaiDropDocked, native tooltip delayed hide/show, new p2Tip and asynchronous payload | Old card disappears before replacement, or stale payload populates after ID changed | Log tooltip instance, selected ID, request and payload ID/equipment revision; retain details surface and reject stale data |
| p2Feedback → handleSetupButtons → native cleanupButtons/respawnButtons | A new binding list rebuilds footer children; native provider may immediately overwrite it | Trace owning script list revision plus Common binding receiver; publish via existing Common bus and only on actual hint changes |
| Accepted v4 equipment-first iaiEqClear/layout and other EnterFrame owners | Independent mode/layout ownership may rebuild row children concurrently with P2 suppression | Trace actual method entry and transform/visibility writers; suppress competing Inventory presentation once at scoped transition |

The final P2 source already removed its known updateRendererBounds → invalidateData
loop before release; do not report that fixed loop as a reproduced cause of the
user's later flashing. Native/static validation never measured visible frame
continuity. The relevant remaining cleanup/visibility/tooltip paths still merit
instrumentation.

Future bounded debug slice: monotonically numbered frame/event ring buffer,
instance IDs, selected ID, mode, inventory/category/data/equipment revisions,
iconPath + load generation, tooltip request/response IDs, alpha/visible changes,
renderer anchor and binding-list owner/revision. Log **changes/events**, not
every item's full stats per frame. Instrument creation/destruction once; flush
only a small diagnostic file in the private test build workflow, with no save or
settings mutation. Reproduce one selection, equip/unequip, details focus, category,
device switch and native drag/modal transition independently before combining.

Acceptance invariants for the new retained scene:

- Selection/device switch: zero row destruction, zero unchanged-icon reloads,
  zero scene/model recreation and no geometry/visibility transition.
- Equip: update actual affected row(s), equipped revision and selected comparison;
  ID/page stays valid. Do not unload all item imagery or recreate details.
- Scroll: pool reuse is bounded; async load completion cannot attach another
  item's icon. No hidden duplicate grid selects a different row.
- Details update: name follows actual selected row immediately; only matching
  payload fills stats. Keep panel/typographic geometry stable while data arrives;
  never display stale stats as belonging to the next item.
- Category/modal: one explicit owner changes focus/content, snapshot/restore
  native contracts; no every-frame rebuild to conceal synchronization defects.

Screen recording and user perception, plus these event traces, establish
continuity. Offline tests/cook success alone cannot declare the flicker fixed.
