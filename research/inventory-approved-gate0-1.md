# Approved Inventory — Gate 0–1 source receipt and visual proofs

18 October 2026. **Static proofs for review, not a playable candidate.** No native
cook, movie patch, installation, settings/merge/save change or mod ZIP in this run.
Authority: [implementation map](../design/inventory-approved-implementation-map.md),
[approved reference](../design/inventory-reference-accepted-review.md),
[Review contract](../design/inventory-review-behavior-contract.md).

## Reference identity and current baseline

The local original is **1672×941**. Its SHA-256 differs from the specification:

- Specification: `9e7d6bdb0bad0d28b5bacfc02e8433dac177b34690303acee8af6cd03b235ac9`.
- Actual local PNG: `b1443ffafc009a5f123d6c971e3ea1e47572763b229595ab78d76799bde87313`.
- After this was reported, the user explicitly replied **“Use the current local image”**.

This run pins that authorized copy, unchanged, at
`reference/inventory-design/approved-inventory-reference.png`. It does not
silently update the historical hash or substitute P1/P2. The image stays ignored.

Fresh read-only ownership: **modInkIronMenus087 at priority 13 owns both**
`gameplay/gui_new/swf/inventory/panel_inventory.redswf` (SHA
`a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a`) and
`gameplay/gui_new/swf/common/panel_common.redswf` (SHA
`54915e76c9bea31d67d9f64ec688b268ee86939e58c6712438cbc3192c82eb8c`).
Thus the earlier P2 research's P1-owner finding is historical, not today's state.
Lower numeric priority wins in this stack. The existing private v4 export under
`build/adaptive-inventory-v2-p1/before/` was checked byte-for-byte against v4,
not the P1 output. Protected live inputs were hashed before/after the work.
All 55 currently required script-provider pins from the verified assembly receipt
also match; no script compilation was needed for this source check.

Private detailed receipts: `build/inventory-approved-gate1/source-receipt.json`
and `visual-receipt.json`, including class, source art, font and output hashes.

## Verified ownership and implementation boundary

Class names below refer to the exact accepted Inventory export unless Common or
WitcherScript is stated. Vendor source stays private; this table describes it.

| Region / object | Exact source owner and contract | Treatment for approved design |
|---|---|---|
| Global nav / level / weight | Common `MenuCommon`, `TopBarNew`, `mcPlayerDetails`; `updateWeight/updateMoney/updatePlayerLevel` | Retain accepted common movie/navigation and live values. |
| Native category UI | `InventoryTabbedListModule.mcTabList`, actual `TabListItemRef`/`AdvancedTabListItem`, `onTabListItemSelected`, `requestTabdata` | New vertical presentation; retain semantic filters, new-state data and selection delivery. Do not shift native tab enum indices to insert Review. |
| Category data | `CR4InventoryMenu.PopulateTabData`, `PopulateDataForTab`; `player.inventory.menu.tabs.data<N>` | Adapt filtered views over native eligible data, preserve current inventory owner/state; deduplicate IDs. |
| Item identity/data | `ItemDataStub`, `W3GuiBaseInventoryComponent.SetInventoryFlashObjectForItem`, player override | Keep ID, iconPath, slot/action types, quantities, quality, requirements/action flags; add localized row labels at producer boundary. |
| Item actions | `SlotBase` mouse/double-click/drag machinery, `SlotActionEvent`, native `W3InventoryGridContext.execurePrimaryAction` | Specialize a native slot for each visible row, not a duplicate action proxy. Preserve native dye/read/repair/equip/use handling. |
| Current selection | `InventoryTabbedListModule.updateActiveContext`, `CurrentItemDataStub`, `getSlotByID`; `OnSelectInventoryItem(id,slot,x,y)` | One selected ID; row indices are only presentation positions. Maintain native player-grid context and global anchor coordinates. |
| Incremental updates | `handleItemUpdate/handleItemsUpdate`, `inventoryRemoveItem`; `inventory.grid.player.itemsUpdate` | ID-based retained row diff; replace grid cleanup/append paths for list mode only. Reconcile selected ID/page after actual removals. |
| Native grid internals | `SlotsListGrid.populateData/populateItemData`, `findItemPlace`, `uplink`, section maps, `saveItemPosition` | Replace packing/navigation in list controller. Keep item metadata; never persist temporary row coordinates as native grid positions. |
| Exact equipped notch | `SlotInventoryGrid.iaiFlags` sets flag 4 from `_data.isEquipped`; `SlotBase.iaiDrawLess` draws into `iaiWell:Shape` | Carry exact corner polygon/style, independently of selected state; no new check/circle/sidebar. |
| Persistent details | `ContextInfoManager` registers `context.tooltip.data`; native `OnGetItemData` → `ShowItemTooltip` → `W3TooltipComponent.GetTooltipData`; `TooltipInventory`/`TooltipStatRenderer` | Retain values/content/comparison, project into approved middle hierarchy. Payload keyed by ItemId, no visibility dependency; details instance remains mounted. |
| Geralt | `mcCharacterRenderer`, `mcCharacterModelAnchor`, `CharacterRendererController.setDefaultAnchor`; `mcTextureHolder` under authored renderer | Retain live render texture/equipment updates. Calibrate the reference silhouette and mask without P2's +10% formula. |
| Renderer interaction | Native `OnRotateCharRenderer`, `OnScaleCharRenderer`, `OnMoveCharRenderer`, `OnResetPlayerPosition`; stats focus callbacks | Preserve native animation/interaction; list layout does not recreate/reinitialize renderer. |
| Auxiliary targets | `ModulePaperdoll.mcPaperDollSlot1..20`, `SlotPaperdoll.canDrop`, `ItemDataStub.isDyeable` | Retain all contracts, expose only on demand; native Hoods code exact. No orbit/feet cluster in normal view. |
| Local artwork | `MenuInventory.iaiArtHost` loading inventory/inventory_ef PNGs; `iaiBg` tooltip backing; paperdoll `iaiDeco/iaiHorse`/segment borders | Suppress only Inventory-specific slot-orbit invocation/layers after snapshot; do not mistake iaiBg for the entire artwork. |
| Common art | `MenuCommon.inkBgArtHost` under `mcMenuBackgroundContainer`; `inkart:inventory`, inventory_ef and efband extras | Separate owner; preserve cache/other menus. Design scoped invocation suppression, not P2 opaque fill. |
| Footer data owner | `CR4ContextManager.updateInputFeedback` → `CR4CommonMenu.UpdateContextButtons/UpdateGFxButtons/UpdateInputFeedback` → **common.input.feedback.setup** | Use this existing script data route, not P2's reflective stage search/foreign binding injection. No second footer. |
| Footer renderer/device | Common `handleSetupBindings` → `mcInpuFeedback.handleSetupButtons`; `ModuleInputFeedback`, `InputFeedbackButton`; `InputManager.isGamepad/isMouse`, `ControllerChangeEvent.CONTROLLER_CHANGE` | Retain v4 glyphs/styles; mode/device changes affect binding data/focus only. Literal reference R/F/C/L are not proof of native key assignments. |

The footer route is a new concrete finding: `commonMenu.ws` creates real
`red.game.witcher3.data.KeyBindingData` Flash objects and gathers context/GFx/default
lists at levels 2/1/0. `MenuCommon` registers the binding at config time. Publishing
through the owning script/provider avoids guessing whether Inventory and Common
share an ActionScript stage/application domain. P2's displayed native hints are
not evidence that its attempted override succeeded. Actual action-to-binding
transitions still need runtime instrumentation in the later slice.

## Equipped mark: exact geometry, not a new badge

The accepted v4 grid mark is **procedural**, not a bitmap/exported icon.
`SlotInventoryGrid.updateData` still mentions `equipedIcon`, but `iaiFlags`
sets that clip's alpha to zero. It is not the visible Ink & Iron mark.
Flag 4 paints an upper-left triangle with vertices `(3,3) → (12,3) → (3,12)`
relative to the well rectangle, **#B48C44 at alpha 0.9**, closing to the start.
The draw scale `k = 1 / abs(concatenatedMatrix.a)` preserves its physical size.
Prototype uses this same geometry/color/opacity at the reference-to-stage scale;
the runtime plan transfers the native branch, not a visually guessed badge.

There is a **different existing** equipment-first row stripe:
`MenuInventory.iaiEqPaintRow`, unselected `o.k == 1`, draws a 3-unit vertical bar
of color 7297587; selected rows have their own selection bar. This is not the
grid notch, rarity lozenge or reference's empty socket-like circle. Both source
paths are recorded to avoid conflating them. These proofs use the v4 grid notch
on the equipped silver sword and remove the concept's repeated right-edge circles;
the user's visual gate must confirm that this is the intended accepted mark.

## Recommended row architecture

**Retained native-slot row specialization plus a one-axis list controller.**
Proposed class names below are new design names, not claimed existing APIs.
The practical first implementation should express these roles as **scoped
list-mode branches/helpers in the existing SlotsListGrid/SlotInventoryGrid
classes**, using the existing symbol instances and verified class-replacement
toolchain. This requires no unproven new SWF class/symbol insertion. The role
names below describe separation of responsibilities, not a new runtime dependency.

| Approach | Cost / native compatibility | Reason to accept/reject |
|---|---|---|
| Reposition native grid cells | Small initial change; retains actions | Reject: tall uplinks, section packing, wells, narrow hit geometry and icon scaling survive; cannot meet reference by scaling/repositioning. |
| W3ScrollingList + generic IconItemRenderer | Convenient text/icon hierarchy and keyboard list | Medium/high integration: IconItemRenderer is a dropdown renderer, lacks Inventory SlotBase contracts; new drag/target/action adapter required. It is not a drop-in Inventory renderer. |
| New visual rows over a hidden native action grid | Initially convenient action reuse | Reject for first slice: two selection/order/hit systems, stale ID/index mapping, hidden modal targets and async tooltip races. |
| **SlotInventoryGrid-specialized rows + SlotsListGrid-compatible one-axis controller** | Bounded but real engineering; preserves native module types, SlotBase events and ItemDataStub | Recommend: one actual actionable slot per row; reuse action state, image source and selected-ID context, replace population/geometry/navigation explicitly. |

`InventoryRowsList` should remain compatible with the module's declared
`SlotsListGrid` type; `InventoryItemRow` remains a `SlotBase`/`IInventorySlot`.
Override full/incremental population and relevant input/selection geometry rather
than calling native first-fit internals. Private grid cleanup helpers cannot be
overridden: the new population path must not enter them. Source data's `gridSize`
remains intact for native gameplay/drag; its two-cell visual uplink is not created
by the one-axis controller. Do not set every data.gridSize to 1 to fake rows.

Rows are retained by real ID, with a fixed visible pool plus a small scroll buffer.
Selection stays stable across sorting and updates. Only explicit sort/category
changes reorder the collection; ordinary equip updates the affected state and
comparison revision. Mouse hit regions cover the row; keyboard/controller up/down
step one row, hold repeat remains native; left/right category/details focus must
be deliberately mapped instead of inheriting nine-column navigation. Drag avatar
and native equipment targets need separate native-size geometry from the row hitbox.

Keep one icon loader per retained row, downscale 64×128 sources into the measured
46×70 reference allowance; no enlarged grid parent. Set source only when iconPath
changes; generation/ID tokens reject stale completions when pool rows are rebound.
Text uses accepted Gentium aliases, name/subtitle bounds and display ellipsis;
complete localized name remains available in the persistent details region.
English acceptance includes accents/punctuation; no Cyrillic claim is made.

**Mandatory producer change:** ItemDataStub declares `itemName`, but the regular
base producer does not populate it reliably. The player file's observed populated
itemName path is crafted-item information, not all ordinary items. Add a scoped
original wrapper around the player `SetInventoryFlashObjectForItem`, preserving
wrappedMethod, using the verified `GetItemLocalizedNameByUniqueID` + localization
path and native category label for subtitle. Avoid requesting a full tooltip for
every offscreen item. Selected details use native full payload, cached by
`ItemId + equipmentRevision`, with stale payload rejection even when selection
changes quickly. No fake static item stats in runtime code.

Accepted v4 already has `iaiEqMakeRow/iaiEqIcon` equipment-first rows, showing that
native icon/name rows and native action routing are feasible. Do not copy their
layout or lifecycle: `iaiEqClear` removes row children, icon loaders are recreated,
and that mode handles selected equipment candidates, not the complete approved
category model. P1/P2 contribute only identity/action/data evidence.

No runtime row/UI state is saved. Reopen/load reconstructs from native owned
items; per-category selection/offset is a transient ID-based cache. Review's
save-scoped acquisition ledger is separate, described in the companion plan.

## Complete category coverage

Native tab enums are 0 Ingredients, 1 Quest Items, 2 Default, 3 Potions/Alchemy,
4 Weapons/Equipment, 5 Books. Current Remastered's normal presentation need not
show all six. `IFT_Weapons` is broader than its label: includes armor, upgrades,
tools, usable/quickslot items and dyes. Never map rail categories by label alone.

| Eligible native data | Approved rail destination (proposed deterministic projection) |
|---|---|
| Equipment tab 4: steel/silver/secondary weapons, crossbows, bolts | Weapons, preserving subtype/native actions |
| Tab 4 armor/chest/gloves/pants/boots | Armor |
| Tab 3 potions, decoctions, oils; tab 2 food | Consumables; native oil application and quantity behavior |
| Tab 3 petards | Bombs |
| Tab 4 quickslot/mask/tool/usable objects | Pockets, with Hoods/painting/quest semantics preserved; classify by actual slot/action |
| Quest-tagged eligible items from native quest path | Quest Items, precedence over ordinary category classification |
| Tab 0 alchemy/crafting ingredients; mutagens; tab 4 runes/glyphs/dyes/repair kits; tab 2 Roach/trophies; nonquest books/junk | Other; no new top-level rail categories. Future within-category sorting/filter only after approval |
| Tab 5 Books where available; readable objects already delivered by native quest/default providers | Nonquest books → Other; quest books → Quest Items; no duplicates |
| Learned/auto-consumed diagrams, technical NoShow items | Preserve native exclusion and native Crafting/Alchemy access; no fabricated inventory row |
| New valid acquisition satisfying later policy | Review first as a virtual ID view; same item remains in ordinary category |

Build from the union of **native eligible providers**, not unrestricted IFT_None
or raw GetAllItems ignoring ShouldShowItem/tag/quest restrictions. Ordinary
category projection is exhaustive/disjoint; Review intentionally overlaps by ID.
Native sorting comparator and current input context remain authoritative.
Shop/stash/horse retain native v4 layout/providers until explicitly redesigned;
every new list behavior is gated by unfiltered IMS_Player.

## Geometry and private visual proofs

The reference is the coordinate authority, not P2 Geometry.asinc. Authored SWF
is 1920×1080 logical units; uniform fit to 1672×941 is 0.8708333 with approximately
0.25 px vertical letterbox allowance. This is an authored fit model, **not a
measurement of runtime UI scale**. Anchor bounds, render texture and footer's
internal child origins must be measured in the later game instrumentation.

Measured reference row frames: x=318..612, first y=174..251, next y=266;
invariant **92 px pitch**, approximately 78 px frame. Rail pitch remains
**79 px**. Inserting Review at the first original rail position shifts the seven
original entries down one unchanged pitch; the final entry ends before footer.
Details x=632..1080, Geralt/right scenery x=1080..1672, header y=0..130 and
footer y=820..941 are protected **pixel-identically** in the main proofs.

Private outputs in `C:/Dev/witcher-ui-overhaul/build/inventory-approved-gate1/`:

- `sparse-1672x941.png`: modeled reported six gear pieces, **2 Weapons + 4 Armor**;
  Weapons selected, two visible rows and deliberate empty list space. Membership
  is not extracted from a save. No false claim of six visible weapon rows.
- `populated-1672x941.png`: 30 illustrative weapon entries, seven visible rows,
  source artwork, equipped notch, scrollbar and long-name ellipsis.
- `six-row-fit-1672x941.png`: six visible representative weapon rows at the
  **same** pitch/icon scale; fit check, not an alternative design.
- `reference-comparison.png`: reference/sparse/populated side by side with labels.
- `edited-pixels.png`: changed pixels only; protected composition remains exact.
- Corresponding `*-1920x1080.png` / `*-3840x2160.png`: composition projections,
  not native game captures or additional image detail.

Provenance: native item PNG payloads decoded from accepted installed
`modInkIronMenuItemArt/content/texture.cache`; actual Gentium/QuietFolio font.
These are private decoded copies, with resource keys/source dimensions/hashes in
the receipt. Primary 1672 proofs **downscale**, never enlarge icon pixels.

**Real limitations:** reference Geralt, scenic background, selected details,
global header/footer remain reference pixels. They are neither extracted native
models nor newly proven engine output. Statistics/currency/keys in the concept
remain illustrative. Review counts 2/3 are illustrative, not a ledger. Fixture
names are readable representative English labels, not verified live localization
for those particular templates. Native icon art is darker/different from the
concept's invented blades; no HDR/color adjustment is applied to conceal that.
Obscured list background is reconstructed from reference edge colors. The 4K
projection adds no source detail; runtime sharpness and UI-scale parity remain open.

There is **no verified source asset** for the concept's exact fog/stone scene or
its Geralt pose/lighting. Native mcCharacterRenderer proves a live character
pipeline, not arbitrary world scenery behind Inventory. Future implementation
must demonstrate an authentic source-supported neutral scenic backdrop and
matching silhouette; if unavailable, return the specific asset/renderer limit
for user approval, not ship this concept PNG or a green replacement rectangle.

## Reproduce, checks and next gate

```powershell
python tools/inspect-approved-inventory.py
python tools/compose-approved-inventory.py
python -m unittest discover -s tests -p test_approved_inventory_gate1.py -v
```

Requires the private pinned v4 export, installed accepted art cache, Pillow and
the existing local Gentium font. Ten tests check reference identity, protected
pixels, row/text/icon fit, output dimensions/hashes, v4/notch pins, protected live
files and provisional policy examples. No static test establishes runtime actions,
save persistence, device transitions or flicker elimination.

Next sequence after **user visual approval**:

1. Resolve backdrop/pose feasibility and instrument real stage/row/footer bounds;
   retain visual authority. No compromise hidden inside a new build.
2. Implement one Weapons list with native ID-backed rows, localized names,
   retained icons, exact notch, native select/equip/unequip and persistent details.
   Keep native other categories/states until the narrow slice passes.
3. Verify sparse and populated screenshots, row identity/scroll after equip,
   no icon reload on selection, correct stat revision and all three devices.
4. Complete vertical rail projection and Other coverage, native auxiliary targets,
   Hoods/Roach/quickslots/drag; use verified Common script feedback bus.
5. Only then add acquisition tracking and per-item Review persistence after
   the policy/example/default-empty-state decisions and save-ID tests.
6. Isolated native compile/cook/validate/pack/metadata and one private candidate;
   manually approved cloned-profile test, never automatic deployment. Future
   rollback disables only that candidate, restoring accepted Menus v4.

All P1/P2 candidates remain historical evidence. No generated images, decoded
art, fonts, vendor movies or mod packages enter Git in this Gate 0–1 work.
