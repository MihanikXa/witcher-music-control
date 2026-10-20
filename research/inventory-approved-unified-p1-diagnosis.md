# Unified P1 — bounded failure diagnosis, 19–20 October 2026

**Latest status, 20 October:** the user's r2 screenshot now confirms the first
failing **method boundary**: `rail.icons.begin → TypeError #1009`, before
`rail.icons.end` / module arrangement. Exact operation inside the icon method
remains unconfirmed. See the runtime follow-up below. Not a fixed/accepted release.
Authority: [user failure](inventory-approved-unified-p1-runtime-failure.md),
[approved composition](../design/inventory-reference-accepted-review.md).
No live game, deployment, settings, merge or save changes were performed.

## Installed ownership, checked again read-only

| Input | Effective owner / priority | SHA-256 |
|---|---|---|
| Inventory | `modApprovedInventoryUnifiedP1`, **11** | `8a61619d9439887c72142c95e43430db3be8ed56f294ae364d4bcb5183478436` |
| Common | `modInkIronMenus087`, **14** | `54915e76c9bea31d67d9f64ec688b268ee86939e58c6712438cbc3192c82eb8c` |
| Accepted v4 Inventory, losing resource | `modInkIronMenus087`, 14 | `a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a` |
| Hoods Inventory, losing resource | `modHoods`, 16 | `2a2dacc886c86d4b08fced4cdc68c7882f2017d2f9d850b41b9ef98df060c68e` |
| Installed annotation | `Mods/modApprovedInventoryUnifiedP1/content/scripts/local/approvedInventory.ws` | `3e081eb6506d60776c5082a2254affc8bf3f1d70a9160e96d605a14dac727740` |

Movie and annotation match the original release manifest exactly. The enabled
Mods script scan finds only this file declaring `AiApprovedEnable` /
`OnApprovedRefresh`; it does not find a second candidate implementation.
Current merged Inventory/provider source remains the installed integration
assembly used by the compiler controls. **Files and offline compiler receipts
cannot reveal the game's current compiled annotation state.** No relevant game
exception/Scaleform trace was available in the inspected local logs. The
screenshot proves custom scene code executes, not the full bridge.

Private evidence: `build/approved-inventory-runtime-diagnosis/installed.json`.
Use `python tools/diagnose-approved-inventory.py inspect` to repeat read-only.

## First hazardous boundary reproduced from authored code

Released `MenuInventory.aiEnter` creates the background and all rail text, then
calls `aiConfigureRailIcons` **before** `mcPlayerInventory.aiArrange`, row creation,
tooltip creation, paperdoll suppression, `aiMode(1)` and `aiRefresh=true`.

Its fallback constructs `TabListItemRef`, calls `setData`, then `validateNow`
without attaching the tab to a display parent. The accepted movie's actual
inheritance is `TabListItemRef → AdvancedTabListItem → TabListItem → BaseListItem
→ ListItemRenderer → Button → UIComponent`. `UIComponent.initialize` invalidates
all state; `Button.draw` calls the overridden `updateAfterStateChange`.
`TabListItem.updateAfterStateChange` contains:

```as
if (this.mcIcon) {
    stage.dispatchEvent(new Event(W3ScrollingList.REPOSITION));
    if (data) this.mcIcon.gotoAndStop(data.icon);
}
```

An unattached tab has null `stage`. The fallback is needed at least for Quest
and Other, which have no paperdoll slot in the authored map; it can be reached
earlier if native slot silhouettes are not yet available. The earlier tests
never executed this initialization path.

`diagnose-approved-inventory.py regression` executes the **released authored rail
method** and **native authored state-update body** after type erasure, with a
null-stage display fixture. Negative control throws specifically at
`dispatchEvent`. The corrected authored rail attaches the tab before validation;
all seven fallback tabs complete and dispatch. This is a regression of the
unsafe call, **not execution of Flash/Scaleform or proof that this was the
earliest exception in the user's game**. Native tab asset, frame labels and
inheritance were checked against the exact v4 export.

The screenshot is consistent with this interruption: rail/background exist,
but later takeover steps do not. A game checkpoint ending at `rail.icons.begin`
with a null-object fault would establish that edge; a different ending must be
investigated instead. No claim of an observed game exception is made.

## Boundary and consequence map

| Boundary | Existing evidence / diagnostic |
|---|---|
| `AiApprovedEnable → approvedEnabled` | Rail implies custom entry was permitted; fresh diagnostic records enable state, tag count and Flash callback before entry. Script load still needs live evidence. |
| `aiEnter → rail icons → aiArrange` | Authored off-stage negative control above; `enter.begin`, `rail.icons.begin/end`, `module.arrange.begin/end`, or `FAULT` distinguish exact stop. |
| `aiArrange → aiEnable` | Original native tab/title/section hiding and nine-row pool happen here. `rows.enable.begin/end`, `row-create` record actual execution. |
| `aiRefresh → OnApprovedRefresh` | Set only late in successful entry. Diagnostic records `refresh.request`; absence after an entry fault is expected, not proof of missing script. |
| `_inv.GetAllItems → eligibility → publish` | Opt-in script logs total owned IDs, equipped state, each real Flash ID, native six-filter eligibility without the probe, custom eligibility/group, published count and restored filter/probe. |
| binding → `aiData → aiAll → aiShowGroup → aiSetItems → aiPaint` | Logs received array length, group, row count/bind IDs; catches binding exceptions visibly. F8 snapshots retained pool, renderer counts, parents, selection and stage bounds. |
| selected ID/serial → `OnApprovedDetails → context.tooltip.data → aiPayload → aiPresent` | Existing serial/ID checks retained; request, script publication, payload receipt, successful presentation or details fault are separately recorded. |
| input → native primary action | Flash logs key-up/focus; script logs native `execurePrimaryAction` entry and ID/focus. Seeing a key does not establish equip success. |

If entry is interrupted, `aiActive` was already set true, so later ticks skip
entry without completing it. Native tab/grid/orbit hiding is downstream; it
never executes in the reproduced interruption. This explains their survival
**under that failure path**, rather than assuming every native clip was hidden
and subsequently restored. The native `aiApprovedFocus` remains its default zero
until `aiMode(1)` runs; the primary-action wrapper returns when active focus is
not one. Thus partial initialization can leave visible native items whose
ordinary action is blocked. The details request has no custom selected row to
start from. These are source-established consequences, pending live path proof.

## Missing items: not yet established

Installed native `W3GuiPlayerInventoryComponent.ShouldShowItem` excludes equipped
items using `isEquipped`. One spare sword in the remaining native grid can
therefore coexist with equipped swords in the orbit. That is a **possible
explanation**, not a same-save count or a dismissal of the user's failure report.
No save was loaded/read/modified to invent owned counts.

The probe temporarily overrides only that exclusion; its six-filter union and
the original filter restoration remain unchanged. New diagnostics compare native
eligibility without the probe against the published custom projection on the
same live inventory. Native filter indices in the per-item trace are **0
Ingredients, 1 Quest, 2 Default, 3 Alchemy, 4 Weapons, 5 Books** (positions in the
diagnostic array, not native enum numeric values). Group 1 is Weapons.
Then `binding.items`, row-bind IDs and snapshot visibility separate enumeration,
conversion, binding, classification and clipping. Actual parity remains open.

## Additional bounded corrections / stability

- Attach native fallback tabs before validation. Keep their original assets.
- Fix the category display owner itself: compiled `InventoryGridRef` assigns
  `mcTabList.itemRendererInstanceName = "mcTabListItem"`; `CoreList` resolves
  these with **parent.getChildByName**, so they are external sibling renderers.
  Hiding only `mcTabList` is insufficient even if entry completes.
  `W3ScrollingList.ShowRenderers(true)` and `populateData` can show them again.
  Unified mode now retains the actual instances under one hidden parking parent,
  snapshotting all original parents/indices before moving any object and restoring
  them on leave. References/callbacks survive; no per-frame hide or destruction.
- Obtain `ItemTooltipRef_mouse` through native `RuntimeAssetsManager.getAsset`,
  as `ContextInfoManager` does. Wait on its verified `isLoaded` state before entry.
  This removes a direct global-definition dependency, not a proven second game
  exception. The tooltip is a ComponentsLib runtime asset, not a local Inventory
  symbol in the exact export.
- Override inherited `TabbedScrollingListModule.updateSubData` only while
  `aiModuleBase` owns normal browsing. Native code writes grid data/selection,
  visibility and **alpha=0 followed by GTweener alpha=1**. It is an independently
  verified competing writer and plausible flashing source. The new owner asks
  for projection refresh instead; special modes still call `super`. This is not
  an observed flashing root cause or a hide-every-frame workaround.
- Catch/report entry, binding and details faults; stop further custom tick work
  after a fault. Partial teardown tolerates absent tooltip/model mask. No automatic
  retry/reconstruction loop was added.
- Preserve nine retained rows, native IDs/actions, category logic and original
  tooltip statistics. No dummy values or second Weapons-only architecture.

## Background and hierarchy

Released `aiScene` is inserted below Inventory/model siblings, then paints its own
nearly opaque 1920×850 rectangle from authored y=115 to 965, plus an independent
small ellipse. This gives the rail, list and model a second cropped material
above the inherited global background. At a 2048×1152 projection, its authored
bottom is about y=1029, consistent with the supplied screenshot's hard cutoff.
That correspondence is not a measured runtime mask trace.

The bounded diagnostic removes **both custom fills**, retaining the inherited
global canvas while keeping Inventory-only orbit artwork suppression. It does
not touch Common, artwork caches, HDR, other menu backgrounds or the approved
column geometry. First prove sole scene ownership on that canvas; judge final
grounding/cohesion from the next screenshot. Removing the rectangle does not
by itself establish a finished attractive background.

## Validation and reproduction

Commands (repository root, PowerShell):

```powershell
python tools/diagnose-approved-inventory.py inspect
python tools/diagnose-approved-inventory.py regression
python -m unittest discover -s tests -p test_approved_inventory_unified.py
python tools/compile-ink-gear-grid.py --out build/approved-inventory-runtime-diagnostic-scripts-final --source src/inventory/unified/approvedInventory.ws --disabled-assignment 'aiApprovedActive = on;'
python tools/build-approved-inventory-diagnostic.py prepare
python tools/build-approved-inventory-diagnostic.py package
```

Compiler output directories must be fresh; existing receipts are preserved.
The diagnostic builder freezes protected inputs before/after, starts from exact
v4, checks non-code tags/declarations, source/compiled checkpoint consistency,
script compiler receipts, exact resource extraction and ZIP contents. It uses
the existing independent bundle/metadata reconstruction controls explicitly as
**diagnostic packaging without a native cook attempt**. It does not fabricate
a timeout to unlock reconstruction or claim native validation.

Twelve targeted tests pass. Both final WitcherScript compiler controls pass with
matching diagnostic counters. Native/game testing remains pending. The historical
release compiler test now checks the archived release annotation, so its receipt
is not falsely applied to current diagnostic source edits.

### Short manual diagnostic procedure

1. Close the game. In a cloned test profile preserve the original P1 package and
   disable it. Install the **diagnostic** archive as its replacement; it deliberately
   uses the **same** `modApprovedInventoryUnifiedP1` subtree. Never enable both
   packages. Keep the same priority ahead of Menus v4, currently 11 vs 14. Leave
   HUD/fonts/item art/Hoods/merged scripts untouched. Deploy manually.
2. Load the same existing test save; do not save over it. If an already available
   console exists, run `approvedInventoryTrace(true)` **before opening Inventory**.
   No settings/console-enablement edits are supplied or required automatically.
   The diagnostic movie's on-screen checkpoints are enabled by installing this
   explicitly labeled package; native owned-ID logging additionally requires the
   console flag. Without that flag, report the visible Flash checkpoints first.
3. Open Inventory and capture the diagnostic overlay immediately. A `FAULT`
   identifies the last reached edge. Stop there if present; do not interpret a
   partial native/custom screen as success. Supply the exact error ID/message.
4. If entry completes, select one real, permitted sword. Capture name/row/details,
   item counts and F8 snapshot (F8 captures then toggles overlay visibility; press
   again to show it). Existing `ApprovedInventory` LogChannel / `ApprovedEvidence`
   trace capture, if available, preserves per-ID/per-filter and full row snapshots.
   No log-file destination is assumed or silently configured.
5. Equip/unequip that permitted item once; capture `primary id=... focus=1`, the
   updated marker/details/model, and a short recording to assess flashing. Test
   a mouse selection and keyboard/controller selection separately. Restricted
   level-2 Disglair on level 1 is not a valid unrestricted-equip smoke case.
6. For the baseline comparison close the game, disable the diagnostic and manually
   redeploy accepted Menus v4; reload the **same unsaved source save**. Capture
   Weapons plus equipped swords in the native orbit. Compare those IDs/names with
   the diagnostic owned/eligible/weapon rows; do not equate native spare-grid
   count with total equipment count. Stop if the owned-item parity is unresolved.

Rollback: disable/remove only the diagnostic package and redeploy; Menus v4
regains Inventory at priority 14. No Script Merger regeneration, settings reset,
save migration or additional QoL installation is needed. The original P1 ZIP,
v4 and HUD RC2 remain intact.

The package receipt/path/hash are recorded separately in
`inventory-approved-unified-p1-diagnostic-manifest.json`. Runtime smoke criteria
are one navigation owner, real rows/details/IDs, successful ordinary native
action, hidden orbit/grid, unobstructed Geralt, no hard rectangle and no recurrent
flash. **None is marked passed by the offline checks.** Stop at this smoke gate;
do not expand categories, Review, merchant or other features.

## R2 actual runtime trace and bounded R3 follow-up — 20 October

User-supplied 3840×2160 PNG SHA-256
`12dd31d288e067c60accb0767aa666d220bb63a4e29ac08b756aace7dcf59993`;
private unchanged copy: `build/approved-inventory-runtime-diagnosis-r3/user-r2-runtime-fault.png`.
Visible trace:

```text
147 enabled true
149 enabled true
187 enter.begin
189 rail.icons.begin
189 FAULT TypeError #1009 Error #1009
```

This establishes an actual game exception inside the icon call, with no successful
return to `aiArrange`. It does **not** establish that the off-stage validation
hazard was the exact r2 instruction: r2 already attached fallback tabs first.
Null paperdoll/list lookup state, native symbol construction/configuration or
another operation inside that method remain candidates until operation evidence.
Do not label this a proven item enumeration/filter failure. Item publication,
custom selection and details request are all later in entry. The diagnostic's
large black rectangle is its labeled temporary evidence overlay, not the removed
background gradient or a final details panel.

Read-only deployed verification matches **r2**, not the original P1:
Inventory `modApprovedInventoryUnifiedP1` priority 11, SHA
`23f6ce2c3cbaf972e207387a8a65c76f494cc155e8a9403a32d1a3fe8440dd03`;
annotation SHA `5768901288270aaac4f2a139b7b6debf4f11b0fcd7fabf808117c04915b38bf7`.
Menus v4 priority 14 / Hoods 16 remain losing Inventory owners. The annotation
matches the r2 receipt (the audit's `release_exact:false` compares against the
older original P1 annotation, not against r2). No installation defect is implied.

R3 changes only icon handling / diagnostic presentation in `MenuInventory`: add nullable paperdoll-list
guard; record category index and exact operation (`lookup`, silhouette bounds /
allocation / draw / attach, tab definition / construction / attach / data /
validation / icon extraction); catch/report failures **per optional ornament**.
The first skipped-icon error stays pinned in the overlay, so later row/data
messages cannot erase the evidence before the user takes a screenshot.
An icon failure now preserves the rail label and returns control to functional
module/list/details initialization. This is failure isolation, not a claim that
an icon's internal cause is fixed or that the full Inventory now works. All
category projection, row, details and native action code is unchanged from r2.
The authored regression now also forces native symbol construction to throw
for all seven entries and verifies seven diagnostic reports without aborting.

R3 is compiled incrementally from the privately verified exact-v4-derived r2
checkpoint; only `MenuInventory` changes in that compile. Same nine-class
source-to-v4 map and unchanged non-code/compatibility controls remain required.
Annotations are unchanged: reuse their exact successful compiler receipt, without
another WitcherScript compile or native cook. Package reconstruction is explicitly
diagnostic-only. R2/original ZIPs and live deployment remain intact.

Next manual test: replace r2 with the r3 diagnostic (same mod subtree, never both
enabled), same priority/save. Capture the overlay immediately; it should show
`rail.icon.skipped <index> <operation> ...` where needed, then
`module.arrange.begin/end`. If a later `FAULT` occurs, stop and supply it. If
entry finishes, check one real sword row/details/action as above. No visual or
functional acceptance is inferred from compilation. R3 receipt is
`inventory-approved-unified-p1-diagnostic-r3-manifest.json`.
