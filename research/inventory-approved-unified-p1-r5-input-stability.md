# Unified P1 r5 — input/focus and stats-mask correction

20–21 October 2026. **Corrective diagnostic; gamepad acceptance still pending.**

## User evidence and scope

User confirms equip/unequip works generally, but explicitly says gamepad cannot
equip/unequip, navigation is confusing, focus has no clear indication, and
contextual actions do not appear/usefully open. Do not turn that into cross-device
action acceptance. R4 data/row/details evidence remains valid.

Screenshot SHA-256 `27aa0cdf2ac24d463f171be4be4cc3037c56bd2fa6bb8295956b7d1038682495`,
3840×2160; private unchanged copy/receipt under
`build/approved-inventory-r5-runtime-evidence/`. It shows native Player Stats with
a huge white rectangle, diagnostic overlay, owned=52/published=40/binding=40,
equipped=9, filter restored and probe=false. It does not demonstrate r5 behavior.

This work corrects reported functional defects within the approved composition.
No categories, Review ledger, cleanup, item policy, artwork, shared movies or
HUD are expanded. Known rarity/optional-art/Drop/remaining footer issues persist.

## Source-established defects and bounded corrections

| Owner / defect | Correction |
|---|---|
| `MenuInventory.aiInput` subscribed to InputDelegate at priority **120**, then called `stopImmediatePropagation`. Native `InputManager.handleDelegatedInput` subscribes at **1** and owns device detection + held-event generation. Consumed navigation could bypass that tracker. | Custom subscriber moves to **0**, after the native tracker. No replacement repeat timer or device detector. |
| Custom directions recognized `up/down/left/right`, but not raw `dpad_*`. Prior user traces show raw pad codes plus arrow equivalents. The old debounce was limited to codes 142–145, while the custom path chiefly consumed arrow codes. Native character/navigation consumers could receive the raw stream independently. | Normalize D-pad navigation into the existing logical directions; one source code owns a logical press until release. Duplicate streams are consumed, native KEY_HOLD events from the owner retain their cadence. |
| Native `CoreMenu.currentModuleIdx` filters modules using `hasSelectableItems`. Inventory's inherited implementation consults old native tab data, not the custom projection. Initial custom selection also occurs before data arrives. | Scoped `InventoryTabbedListModule.hasSelectableItems` uses actual custom grid data only while unified mode owns it. Reacquire module + grid focus and apply native selection context after data/category changes, device changes and modal return. Do not reset selected ID. |
| Rail and selected row remained similarly highlighted regardless of logical focus. A on rail did not enter items; non-list mode intentionally clears native item actions. | Bright focus follows the active existing rail/row/details region. A/Enter/Space on rail enters items and consumes that transition press. Browse uses the existing Common glyph/feedback provider; selected-row actions stay native. |
| Re-entering an unchanged mode could reselect/re-request details and rebuild footer bindings on repeated lateral input. | Same-mode transitions are no-ops; explicit forced restoration is retained for sorting/stats close. |
| `aiModelMask` is a white Shape drawn at `(1245,120,630,810)`. `aiTick` unassigns it when native stats activates but leaves it in the display tree. | Detach the unassigned mask during stats, restore its parent and mask role on return. No recoloring/cover-up/new texture or model replacement. |

The mask rectangle projects at 4K to **x=2490, y=240, width=1260, height=1620**,
matching the supplied white block. The authored old/new state test reproduces
the old attached/unassigned Shape and verifies detachment/restoration. It does
not execute a Flash renderer. Native character-controller/stat-panel classes
remain untouched. Diagnostic overlay visibility is suspended during native stats
and restored to its prior state afterward.

`aiFocusList` does not steal native modal/stats/drag focus. Browse grid enabled,
focus and active-selection state are set explicitly. Custom data remains keyed
by native item IDs. Gamepad A at item focus is passed through to the existing
native action path; no direct generic equip implementation is added. Its native
primary handler now emits a low-volume diagnostic acknowledgement without
requiring the verbose console flag.

Focus feedback changes existing selection emphasis, header color and a small
details focus rule; the approved column bounds, Geralt size/position, Gentium,
item art, equipped notch and native tooltip hierarchy do not change. No new
popup action-menu model is introduced; available item actions use native context
handlers/feedback, and existing native modals retain ownership.

## Verification and honest limits

`tools/verify-approved-inventory-input.py` executes authored `aiInput`, logical
navigation ownership, late-focus acquisition and `aiTick` bodies after type
erasure against explicit display/event fixtures. Cases cover paired raw/arrow
directions, released taps, native holds, keyboard arrows/W, rail A, native item A
pass-through, Details/Aux Back, native modal delegation, initial empty native
tab eligibility versus a populated projection, and stats-mask old/new transitions.
Native priority 1 is checked against the exact exported installed class.

These tests do **not** execute the gamepad device, native dispatcher, FocusManager
or actual equip handler. They establish algorithm/state contracts, not in-game
input parity. Fourteen targeted tests pass. Both annotation compiler controls
pass against the verified installed merged/provider assembly. Three movie classes
change from r4: `MenuInventory`, `InventoryTabbedListModule`, `SlotBase`.
Exact-v4 provenance, original declarations, non-code tags, texture atlases,
preserved compatibility classes, exact extraction and reconstruction controls
remain checked. Native cook/validation is not attempted or claimed.

Private build commands (fresh compiler destination):

```powershell
python tools/verify-approved-inventory-input.py
python tools/compile-ink-gear-grid.py --out build/approved-inventory-runtime-diagnostic-r5-scripts --source src/inventory/unified/approvedInventory.ws --disabled-assignment 'aiApprovedActive = on;'
python tools/build-approved-inventory-diagnostic.py prepare
python tools/build-approved-inventory-diagnostic.py package
python -m unittest discover -s tests -p test_approved_inventory_unified.py
```

Package/annotation/resource hashes are in
`inventory-approved-unified-p1-diagnostic-r5-manifest.json`. Original archives
and accepted Menus v4/HUD remain intact. No live deployment/settings/merge/save
edits were performed; only private build files and original source/docs/tests.

## Short manual gamepad test

Close the game; disable r4 and install only r5 in the cloned profile, same
`modApprovedInventoryUnifiedP1` subtree and priority ahead of Menus v4. Never
enable both candidates. Load the same test source save; do not save over it.

1. On the list, tap and hold D-pad Up/Down. Each tap should move once; held
   movement should repeat normally. Left reaches categories with clear rail
   focus; A enters items. Selection/scroll must survive the round trip.
2. On an unrestricted starter sword, check native action hints and press A to
   unequip/re-equip. Verify actual action, selected ID, notch/model and continuing
   browsing. Disglair remains restricted at level 1. If action fails, capture the
   overlay/primary-handler acknowledgement rather than repeatedly pressing A.
3. Right/View focuses persistent Details; Up/Down scrolls it. B returns to items
   before a subsequent B closes Inventory. On-demand equipment remains native.
4. Open native Player Stats with its displayed command; the white rectangle
   should be absent. Back out using the native command; item focus and actions
   should return. Record any jump, duplicate movement, missing action or flicker.

This is still a correction test, not final visual acceptance or full compatibility
signoff. Rollback: disable/remove only r5 and manually redeploy Menus v4 (or restore
the preserved r4 test candidate). No merge regeneration or settings reset.
