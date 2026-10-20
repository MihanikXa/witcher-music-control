# Unified P1 r3 runtime → r4 data-boundary diagnostic

20 October 2026. **Not functional/accepted; no item parity or action success yet.**
Follow-up to [bounded diagnosis](inventory-approved-unified-p1-diagnosis.md).

**Subsequent actual user test:** r4 now publishes and binds 38 items from 50
owned; real Weapons/Other rows and selected native details/comparison appear.
See [r4 runtime proof and remaining gates](inventory-approved-unified-p1-r4-runtime-proof.md).
Equip/action, excluded-ID parity, flicker and visual acceptance are still pending.

## Actual r3 evidence

User screenshot, 3840×2160, SHA-256
`9362f59e2e72f7499a80b44d4a6e7b34232daf1409a3966f069b01d36ecb8bc4`.
Unchanged private copy:
`build/approved-inventory-runtime-diagnosis-r4/user-r3-empty-projection.png`.

- Native category strip, dotted grid, equipment orbit and grey fixed rectangle
  are absent; live model has the custom transform. Entry got past the previous stop.
- Navigation records groups 3, 2, 1, each with `rows.items 0`. Device switching is
  recorded, but input parity is not established. Native Drop/footer remain visible.
- First optional error is now specifically **`1 lookup TypeError #1009`**.
- No actual item row, details or equip result appears. Zero rows does not prove
  zero owned items, a zero published array, or successful callback invocation.

Read-only ownership still matches r3: candidate Inventory priority **11**, SHA
`86394907411444998c7032a32b5f3c7ddd9552b47efbb5ea7197a0619df62bd7`;
annotation SHA `5768901288270aaac4f2a139b7b6debf4f11b0fcd7fabf808117c04915b38bf7`.
Menus v4 priority 14 and Hoods 16 remain losing Inventory owners. Audit is private
`build/approved-inventory-runtime-diagnosis-r4/installed.json`. Its `release_exact`
field compares against original P1, not r3; false is expected for this annotation.

The decorative lookup calls `SlotsListPaperdoll.getRendererForSlotType →
getIndexForSlotType`. `_slotTypeToIndexMap` starts null and is allocated by
`initializeSlots` inside native `populateData`. Premature lookup is a
source-supported explanation; the exact null member is not visible in the trace.
Optional-art isolation is working. Do not redesign art or let that warning block
investigation of the independent data bridge.

## Verified callback-contract mismatch

Our three Flash calls `OnApprovedRefresh`, `OnApprovedMode`, `OnApprovedDetails`
targeted ordinary WitcherScript **functions**. Native
`CoreComponent.handleGameEvent → callGameEvent → _NATIVE_callGameEvent` is the
Flash event bridge. Installed Inventory declares `OnSortingRequested`,
`OnTabDataRequested`, `OnSetCurrentPlayerGrid`, `OnGetItemData` and other Flash
handlers as **events**. Accepted Ink & Iron's `inkironui_saveload.ws` likewise
adds `@addMethod(...) event OnInkSaveOverwrite` for its custom Flash callback.

R4 changes just those three declarations to the observed native event contract.
Compiler feedback requires bool-compatible exits: false for rejected/early exit,
true after completed handling. Directly called script helpers remain functions.
Both final compiler controls pass against the verified merged/provider assembly.
Previous function compilation never established event dispatch.

This is a concrete source-contract correction, **not an observed successful
engine dispatch** or proof that it is the only empty-list cause. The native C++
dispatcher was not run here. The r3 screenshot lacks persistent refresh/binding
evidence, so it cannot by itself establish that this edge is the first data fault.

## Visible evidence without console setup

Low-volume `AiApprovedStatus` reports refresh entry, owned/published counts,
mode and detail requests back to the diagnostic movie even when console tracing
is off. Per-item/filter logging stays opt-in. Overlay now pins:

- Refresh requests sent by Flash.
- Script refresh acknowledgement, or **not received**.
- Actual native owned count and published count, or **not received**.
- Binding callback array length, or **not received**.

Unknown is never labeled zero. Later category/input logs cannot erase these
statuses. No eligibility, classification, native action logic, layout, auxiliary
target or Review work is added. Only `MenuInventory` and the annotation change
from r3; original unified category/row/details code remains intact.

## Validation and reproduction

Thirteen targeted tests pass, including matching every authored custom Flash
callback to a script **event**, plus existing lifecycle negative controls,
retained-row algorithms and private binary/atlas/compatibility checks. The event
test is a source contract check, not a mock claim of engine dispatch.
Both final annotation compiler controls pass. Reconstructed bundle/metadata use
the same independent identity/changed-resource controls and exact extraction.
**No native cook or in-game r4 execution.** No live files/settings/merges/saves changed.

Commands from repository root (fresh compiler output directory):

```powershell
python tools/compile-ink-gear-grid.py --out build/approved-inventory-runtime-diagnostic-r4-scripts-final --source src/inventory/unified/approvedInventory.ws --disabled-assignment 'aiApprovedActive = on;'
python tools/build-approved-inventory-diagnostic.py prepare
python tools/build-approved-inventory-diagnostic.py package
python -m unittest discover -s tests -p test_approved_inventory_unified.py
```

Manual test: close game, disable r3, install only r4 in the cloned test profile.
Same mod subtree/priority ahead of v4; never enable both. Load the same unsaved
test source save, open Inventory and capture the overlay **before navigating**.
No console command is needed for the pinned counters.

| Result | Next boundary to investigate |
|---|---|
| Refresh sent >0, script not received | Native event dispatch still blocked |
| Script ack, owned >0, published 0 | Native eligibility/conversion |
| Published >0, binding not received | Binding registration/delivery |
| Binding >0, rows 0 | Deduplication/grouping/projection |
| Rows bound but invisible | Actual parents/transforms/masks |
| Real row/details visible | Test one permitted native equip/unequip |

If a later FAULT occurs, stop and supply it. Do not claim success from a nonempty
counter alone. Rollback: disable r4 and manually redeploy accepted Menus v4; no
merge regeneration or save/settings changes. Original P1/r2/r3 archives remain
intact. R4 path/hashes: `inventory-approved-unified-p1-diagnostic-r4-manifest.json`.
