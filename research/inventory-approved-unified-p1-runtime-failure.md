# Unified Inventory P1 — first in-game screenshot failure (19 October 2026)

**Direct user response:** "Check repo. No idea wtf this is."

Latest pre-feedback candidate: commit `02b9389991355afca9a32fd5301ec289d8c3ee17` on `ui-overhaul`; private ZIP in `deploy/approved-inventory-unified-p1/Approved-Inventory-Unified-P1-private.zip`. User screenshot `witcher3_rzn6sOpZxS.jpg` was supplied in conversation, **not committed to GitHub**. The screenshot is actual game output, not Codex's prior composite.

**Status: failed first visual/runtime integration test.** This is not the approved category rail → horizontal item list → full details → Geralt interface. Do not treat 8 mocked tests, final ABC compilation or controlled one-key bundle extraction as screen/interaction success. No claim of formal full interaction evaluation; user's description refers to the screenshot and confusion.

## Observed in-game

- New **REVIEW (Not enabled)** and tall vertical rail entries appear at left; some user-requested presentation code is active.
- Old **EQUIPMENT** label, native top category icon strip, **WEAPONS/ARMOR** section headers and dotted item grid remain visible. Old **20-slot equipment paperdoll/orbit** is still drawn around Geralt, with consumables, bombs, pockets, horse/roach items and drop targets.
- The specified **text+icon horizontal weapon rows** are not visible in the intended center-left region. Neither is the **persistent selected-item details panel**. There is significant blank/dead center space.
- New rail and native elements overlap (including old selection/status overlays). Geralt and environment are not composed according to the reference. Native footer persists.
- This is an **incompletely replaced screen/dual-scene**, not merely icon sizing or background aesthetics. The P1/P2 failure pattern of simultaneous old/new UI owners has reappeared.

## Verified code boundaries and plausible failure paths — hypotheses, NOT runtime cause confirmations

- `src/inventory/unified/Scene.asinc::aiEnter` constructs `aiScene` and calls `mcPlayerInventory.aiArrange()`, `mcPaperDollModule.aiTargets(...,false)`, sets visibility once for old Inventory art/heading, and registers data/input/selection listeners. Thus the new rail can render **even when the list/data bridge fails or later native lifecycle callbacks restore old components**.
- `Module.asinc::aiArrange` hides `mcTabList`, `txtTitle` and native section container; `List.asinc::aiEnable` snapshots and hides original row renderers, installs nine native-slot row instances; paperdoll `aiTargets` is adapted from P2 and hides native slot clips. Screenshot means at least some of these suppression/state assumptions **do not hold at capture time**. Specific source of restoration still unconfirmed.
- `Scene.asinc::aiTick` triggers `OnApprovedRefresh` via `GameEvent.CALL`; `approvedInventory.ws::OnApprovedRefresh` enumerates native items, probes eligibility and publishes `inventory.approved.items`; root `initDataBindings` registers `aiData`. If this script bridge/binding does not fire, **there will be no text rows and no selected-item details**, while the rail may still be drawn. Trace each hop in running game; do not assume the script is absent merely because a row is absent.
- `Scene.asinc::aiSelectData` requests `OnApprovedDetails` only from an actual selected row. If the dataset or selected row is unavailable, the middle details will necessarily remain blank. `Details.asinc::aiPending` also hides the retained tooltip while awaiting a matching payload. Establish true event order.
- `Scene.asinc::aiTick/aiMode`, native module on-enter/item refresh, `MenuInventory` public mode callbacks and `ModulePaperdoll` updates may compete for display-object visibility and native focus after the one-time `aiArrange`/paperdoll suppression. This is the leading structural class of failure to investigate; screenshot alone cannot prove which method writes the restored visibility.
- `research/inventory-approved-unified-p1.md` records final **native cook timeout after 90 seconds**, no final native validation, release packaged via exact controlled reconstruction. This is a **separate unvalidated-build risk**, not evidence by itself that reconstruction caused the visual failure. Exact resource winner/hash in the user's *current* game must be confirmed after installing the candidate.

## Required next action — runtime diagnosis, NOT another speculative full rebuild

1. **Rollback for regular play**: close game, disable only `modApprovedInventoryUnifiedP1` in cloned Vortex test profile, redeploy to restore accepted `modInkIronMenus087` owner; do not alter active HUD, Hoods, saves or merged scripts. Keep P1 private as reproducible negative control. Do not automatically edit the live game.
2. **Verify installation winner and script bridge** in the clone: exact active `panel_inventory.redswf` resource hash/priority and compiled annotation script presence, compare to P1 manifest. Because new rail appears, some candidate SWF code runs; distinguish patch/load order from failed init/data flow.
3. **Instrument native runtime at precise points** (opt-in, small traces only): `approvedEnabled → aiEnter → aiArrange/aiEnable → OnApprovedRefresh → aiData → aiShowGroup/aiSetItems → aiPaint → OnApprovedDetails → aiPayload/aiPresent`. Log count, selected real item ID, callback/binding success, row visibility, layer owner, renderer list length and exact display parent. No filler “passed” based on source existence.
4. **Track old UI writers**: at scene enter and after each native update/open animation, trace visibility/alpha/parent/owner of `mcTabList`, section titles, native grid renderers, `mcPaperDollSlot1..20`, relevant paperdoll icons and header. Identify and disable the *actual* writers in player-unfiltered unified mode; do not just repeatedly hide every frame or overlay a black mask.
5. **Find the first broken edge**, repair only it, and prove one actual native item row and one actual details payload appear, with the old grid/paperdoll absent. This is a narrow in-game smoke gate **before** returning to full seven-category work.
6. Restore full normal-category/action testing only after one coherent scene works. Do not invent fake item names/stats, create dummy UI surfaces, change design, or implement Review/QoL early.
7. Tests must reproduce actual movie load/event order, delayed native refresh and runtime binding delivery, not only mocked isolated list methods. Avoid claiming the final candidate was natively validated if another startup timeout occurs.

**Do not iterate by cosmetic repositioning of the visible overlap.** The selected visual composition is still approved; runtime scene ownership and data/display integration failed. No reason to revisit image design yet.

## User-facing check

The screenshot needs to show only one vertical category rail, one compact text-and-icon item list, one genuine middle details panel, Geralt integrated, no old dotted grid/top categories/orbit and a single footer. This is a minimum viability gate, not final gameplay acceptance.
