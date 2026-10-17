# Adaptive Inventory v2 — Gear Prototype 1

17 October 2026. Private, implemented game-test candidate on `ui-overhaul`.
The user must perform in-game acceptance. Offline compilation, native resource
validation and package checks cannot establish controller feel or visual parity.

**Release ready for manual installation:**
`C:\Dev\witcher-ui-overhaul\deploy\adaptive-inventory-v2-p1\Adaptive-Inventory-v2-Gear-Prototype-1-private.zip`
— **1,119,437 bytes**, SHA-256
`876abb880f91ceac0fd888e0c98661ca947833db97317f3cc7477fecc5875b74`.
[Exact release manifest](adaptive-inventory-v2-gear-p1-manifest.json).

**Passed on the final candidate:** native cook, one-resource validation (zero
resource errors), pack and metadata; **no reconstruction fallback used**.
Cooked resource equals prepared bytes. Inventory output SHA-256:
`942b5d14e3affc9885ec9c01f4260ad33bdbbf3eced7d1c5f537091b365a6691`.
All **16 targeted tests pass**: API/data/filter preservation, original artwork
and Hoods classes, ID/scroll restoration contracts, executed pure D-pad gate and
native-payload summary projections, viewport/scroll-page restoration, script
control/candidate diagnostics, exact package extraction, metadata and live freeze.
**4,269 original method/accessor declarations retained**. Pure-function tests run
translated isolated algorithms in Node; they do not execute Scaleform/the game.
Native logs retain the established isolated depot-path/sound-bank assertions;
there are no reported Inventory resource errors. Full logs remain ignored locally,
with command/log hashes in the manifest. Three decompiler-only normalizations
(empty condition inversion, redundant uint coercion, NaN notation) were checked
explicitly rather than treating text differences as gameplay changes.

## Foundation and ownership

Pulled `origin/ui-overhaul` with `--ff-only`; it was already at `44478c3`.
The read-only deployment gate passes for all **40 accepted Menus v4 movies** and
every release file, including art modules. Effective Inventory owner is currently
**modInkIronMenus087, priority 13**, SHA-256
`a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a`.
Hoods is enabled at 15; frozen RC2 at 35. These are observed current priorities,
not the historical v3/v1 numbers.

Input is exactly the v4 `prepared-inputs` Inventory resource, byte-checked against
the accepted release and the installed effective owner. Its root package is
Menus v4 ZIP SHA `4566e39878e234f3f4d96bece03804a625f0338f8d2cb7680c9627b044bf44d0`.
V4 provenance remains the pinned private Ink & Iron 0.8.7 UI, official Hoods
method port, accepted Gentium/typography/glyph work and existing item-art stack;
see [v4 receipt](menus087-v4-typography-finishing.md) and its manifest. Vendor
resources retain their authors' licenses/copyrights and remain gitignored.
Only original adaptation tools, snippets, tests and hash/evidence documents enter
Git. This is personal modification, not a redistribution package.

The old 0.8.6 movie is **not an input** to this release. Its original private
annotation adapter and input/slot-contract helpers are reused as source.
Hoods' current `SlotPaperdoll` and `ItemDataStub` remain **source-identical** to
v4; no old Hoods movie is overlaid. The public/protected native interfaces remain.

## Implemented composition and contracts

| Surface | Implementation |
|---|---|
| Gear browse | Native category 4, nine columns and native section grouping; 1.4 display scale, six visible rows. Actual grid, real IDs and native sorting/filtering. Tall items retain native two-cell footprints. The matching mask, scroll page, visible rows and bounds change together; restore is exact outside Gear. |
| Empty cells / selection | Empty wells do not paint dots. Actual cell objects and drop contracts remain. One quiet frame around selection; I&I's original equipped corner marker remains. No repeated item names in the grid. |
| Equipped data | Original `inkGearGrid.ws`: scoped suppression of equipped weapon/armor exclusion **inside the original ShouldShowItem**; other native filters remain. Equipped state comes separately from the player. Native appendItemData first removes the same ID, retaining deduplication. |
| Equip / unequip | Native reversible actions and restrictions; equipped grid primary action calls native OnUnequipItem, native feedback says Unequip. Equipped removal becomes real item update. No additional equip confirmation or campaign data model. |
| Selection | SlotsListGrid updateItemData/updateItems capture selected **ID** and scroll before the native rebuild and restore that ID if it survives. Handles index zero independently of the native cached-index truthiness. Gear category stores ID/scroll for returning; missing items use native fallback. |
| Preview | Character renderer moved right and display scale increased 12% over its captured native value; live renderer/equipment update contract retained. No equipment orbit or foot-level cluster in Gear. Native advanced stats/renderer focus temporarily restores the baseline layout. Model framing still needs game screenshots. |
| Compact summary | Beneath grid at logical x72/y816, width 900. Item name, native primary value and equipped value/native colored PrimaryStatDiffStr, level/warning/socket counts, up to three actual bonus/resistance rows with matching equipped values. Values are transparent pairs, not an invented quality score. |
| Inspect | **I / controller View/Select**, or mouse button. Full original TooltipInventory information over the browse region; native Equipment First scroll engine reused at readable scale. Shift/LT comparison remains native. D-pad/arrows/right-stick/Page Up/Down and wheel scroll details. Modal keys prevent accidental item actions/sorting; Esc/B/Inspect returns without assigning a new selected index or scroll position. |
| Auxiliary equipment | **Tab / left-stick click**, or mouse Equipment button. All 20 original native equipment targets form a five-column panel to the left; the native tooltip sits beside it. Includes weapons/armor, crossbow/bolts, quickslots, Hoods and Roach. Native selection mode/drag exposes targets automatically. No slots are destroyed. Back returns focus to the grid. |
| Input | Original native grid/category/sort handlers retained; duplicate D-pad downs suppressed, 400 ms initial hold delay, 110 ms repeat. Inspect uses View, preserving native right-stick sorting. Mouse buttons expose the same modes. Wheel capture in Inspect prevents model zoom. |
| Other contexts | Layout requires unfiltered player Inventory **and actual category 4**. Shop, stash, horse and other categories restore v4 geometry/viewport/tooltip state. Shared navigation, background artwork and all other movies are unchanged. |

Changed resource key only:
`gameplay/gui_new/swf/inventory/panel_inventory.redswf`.

Eight changed GFx classes: **MenuInventory, InventoryTabbedListModule,
SlotsListGrid, SlotsListBase, SlotBase, ModulePaperdoll, TooltipInventory,
ContextInfoManager**. No non-DoABC SWF tag, font definition/import, symbol,
shape, texture/atlas pixel or unrelated movie changes. The atlas contract checks
the original inventory textures. Hoods dye handling, OW, Smooth Map, RC2 and
the menu/art caches remain on their accepted resources.

Exact WitcherScript contracts reused: addFields on CR4InventoryMenu and
W3GuiPlayerInventoryComponent; addMethod QfSetGearEnabled; wraps
SetInitialTabNewFlags, SetInventoryState, ShouldShowItem, isEquipped,
SetInventoryFlashObjectForItem, InventoryRemoveItem,
W3InventoryGridContext.execurePrimaryAction and updateInputFeedback.
The spelling `execurePrimaryAction` is the actual game method.
This is a loose original annotation source, **not** a replacement merged script
or shipped precompiled blob. A fresh compile against the checked current 5.01
merged Inventory/Hoods assembly and a disabled-flag control has matching diagnostics.
Opaque provider dependencies remain outside that assembly's source recompilation.

## Deliberately bounded first release

Native categories remain discoverable; no new permanent tabs. Internal context
projection recognizes Gear (4), Usables (native Alchemy, 3), and Satchel (other
native categories). Native Default is mixed content and is **not** falsely
treated as a finished consumables classifier. Only Gear currently changes density.
The compact-summary projection is separate from item ownership and acquisition
state; it can later consume genuine review records without duplicating item IDs.

No fake recency, timestamps, favorite persistence, bulk sale/dismantle, optional
runtime dependency or automatic inventory cleanup. See the [QoL findings and
adoption matrix](adaptive-inventory-v2-qol.md). Next implementation after Gear
acceptance should be **adaptive Usables/Satchel**, with Review following once its
durable identity/dismissal contract is decided. Cleanup comes last.

Known limits: compact summary deliberately shows only the primary difference,
socket count and first three native stat rows; it is not every property or a
numeric delta for every resistance. Rune identities, oils, set bonuses and long
prose stay in full Details. Long compact rows may clip; use Inspect. Native action
footer hints are retained for safety/discoverability in this first pass, alongside
two small mode buttons; a later runtime pass can reduce redundant hints. Sparse
inventories show only actual items; no fabricated filler. Human tests must verify
native 3D framing, mouse hover/card lifetime, mode transitions, controller glyph
discovery and performance with large inventories. No new runtime results are claimed.

## Reproduce and verify

Use the existing pinned local Python/Java/FFDec/REDkit setup and ignored inputs:

```powershell
python tools/research-inventory-qol.py
python tools/compile-ink-gear-grid.py --out build/adaptive-inventory-v2-p1-scripts
python tools/build-adaptive-inventory.py prepare
python tools/build-adaptive-inventory.py native
python tools/build-adaptive-inventory.py package
python -m unittest discover -s tests -p test_adaptive_inventory.py -v
```

Compiler/release destinations must be fresh; prepared class checkpoints may be
resumed only with exact input/source matches. Prior check iterations are kept
inside this candidate's ignored build directory. Native cook/validate/pack/metadata
outcomes and final ZIP/hash are recorded in the companion release manifest.
V4's historical reconstruction is not a native validation claim for v4; this
candidate's final native result is evaluated independently.

The optional `reconstruct` stage accepts only a blank-log, bounded cook startup
timeout; native diagnostics/errors are not bypassed. It verifies native bundle
and metadata controls plus independent changed-content controls. Any such output
must explicitly report native validation unavailable; it cannot count as a pass.

## Manual installation and rollback

1. Exit the game. Use a cloned test profile; retain accepted Menus v4, all art
   modules, RC2, Gentium/aliases, Hoods, Outfit Wheel, Smooth Map, SAHUD/FHUD and
   existing gameplay/merged scripts. Disable the old Gear-grid v1 candidate if
   present. Do not install the three reference QoL mods.
2. Install only the private ZIP listed in the release manifest. Its one new
   folder is `modAdaptiveInventoryV2GearP1`. Make this folder own **Inventory
   before modInkIronMenus087** (currently priority 13) and other Inventory owners.
   Lower numeric priority wins in this observed stack. Use relative Vortex rules;
   do not overwrite an existing priority number or replace the v4 package.
   This selects an already-combined movie; it does not merge binary resources.
3. Do not regenerate Script Merger, reset settings or replace the working merged
   Inventory. This package adds only original annotations; let the game compile
   them normally. It has no settings XML, caches, HUD or optional mod dependency.
4. After manual deployment run the read-only gate:

   ```powershell
   python tools/build-adaptive-inventory.py verify-installed
   ```

   It must confirm candidate Inventory ownership, all other accepted movie
   hashes/files, packaged annotation/bundle/metadata and protected HUD/merge inputs.
   Resolve failures before judging the appearance. The tool does not reorder mods.
5. Load a Geralt test save outside combat/dialogue. Choose native Equipment/Gear
   if FriendlyHUD opens another category. Perform the checklist below. Save
   changes only as desired; this candidate adds no new saved fields.

**One-package rollback:** exit, disable/remove only
`modAdaptiveInventoryV2GearP1` in the test profile and restore the recorded v4
relative order. Menus v4 automatically regains Inventory. Keep v4/art/RC2 enabled;
no save or settings migration, cache deletion or merge regeneration is required.
This run does not install anything or modify game/Vortex/Documents/saves.

## Prioritized in-game acceptance

1. **Equipment flow:** compare three swords in sequence, equip one, unequip and
   re-equip. Same item remains selected; equipped markers/comparison update;
   scrolling does not jump. Repeat on armor, including first grid index.
2. **Inspect/back:** mouse button, I and View open full details. Long description,
   set bonuses, sockets and native Shift/LT comparison; scroll to the end. Esc/B
   closes Details only. Selection/viewport return exactly. Right-stick sorting
   still works in browse; ordinary actions remain native.
3. **Navigation/composition:** ten distinct D-pad taps, then hold/release; arrows,
   category changes/return, mouse hover/double-click, scroll and sorting. Sparse
   and large inventories: no dotted wallpaper or item/summary overlap, larger
   unobstructed Geralt, no auxiliary slots until requested. Repeat at 1080p/4K.
4. **Equipment targets:** Tab/LS/mouse Equipment; Back restores focus. Test Hoods
   clothing/dye, Roach, crossbow/bolts, potion/bomb/oil/quickslot assignment and
   drag/drop target selection. Change category during ordinary browse and return.
5. **Shared states/regressions:** shop, stash, horse Inventory, quest items,
   modded/DLC gear, weight/capacity; repeated open/close/equip. Outside Inventory,
   accepted Menus v4 appearance, Tab/LB radial, RC2 bars/glyphs/quickslots and OW.

Report screenshots plus the first failing action/selection state. A successful
static/native build does not mark any of these scenarios accepted.
