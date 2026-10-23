# Unified Inventory r7 — retained formatted details transitions

23 October 2026. Minimal correction from verified r6; in-game r7 acceptance pending.

## Evidence and exact cause

The user confirms prior functional faults now work, while reporting a several-frame
plain white item name between formatted details. Their two-frame evidence is
recorded in [r6 runtime feedback](inventory-approved-unified-p1-r6-runtime-feedback.md).
This is acceptance of reported functional repairs, not all item parity or visuals.

R6 `MenuInventory.aiSelectData` wrote `aiPendingName`, a separate generic 32-point
TextField. It called `TooltipInventory.aiPending`, which hid the formatted panel
and reset its scroll on a changed item ID. Only a later current-ID/current-serial
response called `aiPresent` and cleared the generic title. This deliberately
produced the user's intermediate state; global fonts do not explain it.

## Implemented boundary

- `MenuInventory`: remove the pending-title field, creation and all writers.
  `aiSelectData` changes logical selected ID and requests details without touching
  the last formatted panel. No substitute text/loading panel is created.
- `TooltipInventory.aiPending`: retain the compatibility method as a no-op;
  waiting does not change visibility, content or scroll. Ordinary browsing no
  longer calls it. `aiPresent` remains the existing retained presenter commit.
- `aiPayloadApply`: preserve item ID and serial rejection; additionally reject
  zero current ID and duplicate already-committed serials. Only a matching newest
  payload reaches `aiPresent`; committed serial is recorded after validation.
- Returning to Browse through `aiMode` uses `aiSelectData(false)`, avoiding
  redundant requests solely for Details/Back. Dataset/equipment updates still
  force serialled refreshes, including same-item refreshes. No cache is added.

An actually empty category has no valid selected item: hiding its details remains
intentional. Initial opening waits for the first real payload without fabricated
content. Existing Stats/Aux/modal visibility rules remain. During a valid A→B
wait, A's complete details may remain briefly visible; B is already the selected
native item. No pending display field supplies any action target.

Only `MenuInventory` and `TooltipInventory` change from r6. Row, list, module,
equipped notch, action annotation, input handlers, masks, character controller,
background, shared menu and HUD source are retained. No broad styling is included.

## Atomicity and action ownership

`aiPresent` already executes `data=value; validateNow(); visible=true` in one
synchronous callback. The native data setter calculates comparison differences;
`populateData/populateItemData` populate fields and synchronously validate the
attribute, socket, set and property lists. Different-item scroll resets only at
this commit; a same-item refresh preserves it. This is the smallest source-backed
transaction boundary. It does not prove every native rendering operation happens
within a single displayed frame: native comparison layout has a deferred
`handleComparisonTooltipValidate` callback, and optional imagery has loaders.
Neither warrants speculative double buffering before the user tests the retained
panel. If residual tearing remains, capture frames and identify which child/layout
writer is late before adding a retained staging presenter.

Native `OnSelectInventoryItem` passes the selected ID to
`m_currentContext.SetCurrentItem`, which assigns `currentItemId` independently
of tooltip data. Native selected-renderer/context actions remain authoritative. Existing
`W3InventoryGridContext.execurePrimaryAction` reads `currentItemId`, not the
retained `TooltipInventory.aiItem` or its `_data.ItemId`. The existing wrapped
native primary action and native unequip path are unchanged. An authored-wrapper
fixture verifies both paths with selected ID B while displayed tooltip ID A.
That executes the wrapper with native dependencies stubbed, not the game itself.

## Verification

`tools/verify-approved-inventory-details-transition.py` executes actual authored
request, response, pending, present, category and mode bodies after type erasure
against explicit native/display fixtures. It uses the verified r6 exported methods
as its negative control, proving generic title + hidden details until the reply.

Corrected cases: A→B, A→B→C, A→B→A, null/zero/wrong-ID/wrong-serial responses,
duplicate response, forced same-ID equipment refresh, unchanged selection,
Details/Back without another request, actual category projection, empty category,
120 rapid selections with 119 stale replies rejected, pending scroll retention and
commit reset, and two action-wrapper paths using new ID while old details remain.
Retained presenter identity stays constant. Source contracts prohibit pending
title references and transition-time presenter destruction/list reconstruction.
Exact r6 source hashes preserve rows/notch, list, module and action annotation.
Existing input/mouse/selection/pooling tests run alongside these fixtures.

These tests execute authored logic; native event dispatch, FocusManager, 60fps
rendering, gamepad hardware and game actions require the user's runtime test.
All 16 targeted tests pass. No claim of eliminated in-game flicker follows from offline success.

Build entry point: `tools/build-approved-inventory-diagnostic.py prepare` then
`package`. R7 seeds the verified r6 resource, recompiles only the two changed
classes and verifies source agreement, preserved native declarations/non-code
tags/textures/CRC, unchanged script and exact bundle extraction. Its unchanged
annotation reuses r5's two successful compiler controls. Native cook/validate is
not claimed; controlled reconstruction retains independently checked bundle and
metadata controls. A new full cook is not attempted: prior commandlet startup
stalls do not justify a long unrelated rebuild for this two-class patch. See the r7 manifest for final hashes and test count. Prior
native startup timeouts remain historical; none is fabricated for this run.
Protected installed files are fingerprinted before/after private packaging.

## Manual acceptance and rollback

1. Close the game. In the cloned test profile, disable r6 and install only r7,
   replacing the same `modApprovedInventoryUnifiedP1` subtree and retaining its
   priority ahead of Menus v4. Do not enable both packages or regenerate merges.
2. Load the same test save. On controller, move repeatedly between Witcher's
   silver sword, Witcher's steel sword and Disglair; hold Up/Down several seconds.
   Exactly one row should remain selected. The middle panel should retain its
   established formatting until the next complete details arrive, with no plain
   title, blank interval or typography jump. Repeat with mouse and keyboard.
3. Unequip/re-equip an unrestricted starter sword, including during rapid
   navigation. Verify actual selected item, notch, comparison and Geralt update.
   Open Details/Back, switch categories and return; preserve selection/scroll.
4. Record at 60fps or higher. Toggle the existing F8 overlay off for a clear
   visual comparison; re-enable only to capture a fault. Residual intermediate
   frames need a recording, not another static-compilation claim.

No installation, Vortex, settings, Script Merger or save writes were performed.
Rollback: disable r7 and restore preserved r6 (or accepted Menus v4) manually.
No settings reset. The [separate finishing plan](../design/inventory-visual-finishing-after-r7.md)
does not authorize adding its changes to r7.
