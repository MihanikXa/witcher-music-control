# Adaptive Inventory P2 — Gate A ownership

18 October 2026. Source verification for the bounded structural candidate; no
in-game display-list capture or visual acceptance is claimed. Primary design:
[P2 contract](../design/adaptive-inventory-p2-composition-contract.md).

## Pinned source and installed ownership

Resource: `gameplay/gui_new/swf/inventory/panel_inventory.redswf`, accepted
Menus v4 SHA-256
`a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a`.
The existing private `adaptive-inventory-v2-p1/before` export was checked
byte-for-byte against **this v4 resource**, not against the rejected P1 output.
Original AS additions are under `src/inventory/p2/`; compiled vendor sources,
movie XML, textures and binaries stay ignored.

Read-only installed audit found enabled Inventory owners: P1 at priority **11**,
Menus v4 at **14**, Hoods at **16**. Thus rejected P1 currently wins. Common
owners: Menus v4 at **14**, HUD refinement at **36**, Outfit Wheel at **41**;
v4 wins. Lower numeric priority wins in this measured stack. This is binary
resource selection, not method merging. The P2 combined Inventory must precede
v4 and Hoods; disable P1/v1, retaining the accepted packages. No deployment was
performed. Exact owner hashes are private `build/adaptive-inventory-p2/installed-owners.json`.

## Visible object → owner → behavior → disposition

| Object | Compiled owner | Contract and P2 treatment |
|---|---|---|
| Global slim navigation | `panel_common`, `MenuCommon` / `TopBarNew` | **Keep exact**; no common movie edit. |
| Equipment state banner / auxiliary labels | Inventory `ModulePaperdoll.tfCurrentState`, `tfPotions/Pockets/Petards/Masks` | **Suppress** in Gear; snapshot/restore outside Gear. |
| Category icons/new markers | Inventory `InventoryTabbedListModule`, `mcTabList`, `mcTabListItem1..6` | **Reflow same renderers** into one row; retain selection callbacks. |
| Active category text / section headings | `InventoryTabbedListModule.txtTitle`, `_sectionTitlesContainer` | **Suppress** redundant Gear headings; retain provider metadata. |
| Sort controls | `MenuInventory.btnSort`, `btnSortChange`, native sorting modal | **Reflow** to reserved right side of category row; native Q/F/R3/held-stick handlers remain. |
| Real item slots | `mcPlayerInventory.mcPlayerGrid`, `SlotsListGrid` / `SlotInventoryGrid` / `SlotBase` | **Replace packing**, not identities: one row-major lattice across former section columns, native sort order, tall footprints, masks, scrolling, actions and drag listeners. |
| Empty wells | `SlotBase.iaiDrawLess` | **Suppress painting** only for empty unselected non-target cells. Keep targets/hit contracts. |
| Equipped marker | Native slot data `isEquipped` | **Keep**; original annotation adds real equipped weapon/armor IDs to normal listing without bypassing other filters. |
| Geralt | `MenuInventory.mcCharacterRenderer`, `_rendererController` | **Reframe** live renderer in adjacent aligned preview, snapshot anchor/scale/mask. |
| 20 equipment targets | `ModulePaperdoll.mcPaperDollSlot1..20`, `SlotPaperdoll` | **Subordinate** in Browse; compact 5×4 alternate target state inside browse plane; native drop/equip events and Hoods class unchanged. |
| Paperdoll decorations | `iaiDeco`, `iaiHorse`, `mcSegmentBorder*` | **Suppress** for P2 states; snapshot/restore. |
| Local obsolete backdrop | `MenuInventory.iaiArtHost`, inventory/inventory_ef artwork | **Suppress local host** only. |
| Common's Inventory art | `MenuCommon.inkBgArtHost` under `mcMenuBackgroundContainer`; `inkart:inventory` | **Cover within Inventory content** with a quiet opaque charcoal canvas. Do not change common host, shared cache or other menu invocations. |
| Tooltip backing/header strip | Inventory `iaiBg`, `iaiHeadSp`, `iaiHint`, `TooltipInventory.iaiStrip` | **Suppress** redundant browse surfaces; restore on leaving Gear. `iaiBg` alone does not own all orbit artwork. |
| Compact summary | P2 stable fields under `MenuInventory` | **Replace** P1 visibility-dependent strip with selected-ID data binding, three lines below gallery. |
| Original full details | `TooltipInventory`, actual symbol `ItemTooltipRef_mouse` | **Keep native content**; explicit Inspect mode, native scrolling/comparison, return to same ID/page. |
| Footer/glyphs | Common `mcInpuFeedback` → `ModuleInputFeedback` → `InputFeedbackButton` | **Reuse same provider**, scope bindings by mode, restore on leaving; no second footer sprite or mixed-device literal labels. |

## Geometry and data contracts

Authored stage is **38400×21600 twips = 1920×1080 logical units**. Authored
common footer is near y=1023; global top navigation occupies approximately
y=0–100. Reserve header through 118 and footer from 994 in this coordinate
space. Native grid cells are 64×64, tall footprints two cells; original grid is
9 columns ×10 visible rows with section padding. The grid mask is an authored
off-center shape (approximately x=-348..460, y=0..642). P2 resizes it and then
corrects position using `getBounds`, together with native page/scroll dimensions.

P2 derives its content rectangles from current stage-to-menu coordinates, not
the capture pixel count. Browse occupies 57% of width, preview 33%, with a
gutter. Sparse density uses 3 columns/4 rows at up to 128 units; populated
density uses 6–7 columns/6 rows at up to 96. Density changes only at content-count
bands or viewport changes. Six conservative two-cell items fit without scroll.
Selection changes update text, not scene geometry. Real live transformed bounds,
UI-scale behavior, long text, 3D framing and glyph width still need the first
runtime screenshot. Offline geometry is a bound calculation, not a rendered
screenshot test.

`SlotsListGrid.populateData` contains the former weapons/armor column partition.
P2 removes that layout restriction only while player Gear is active, retaining
section IDs as metadata and the native sorting comparator. Live renderer data
is authoritative after incremental updates; full populate uses its actual data
provider. Identity deduplication and selected-ID/scroll restoration occur after
native updates. Gallery coordinates are not persisted as native saved positions.

Selection is `getSelectedRenderer().data.id`. Native selection sends
`OnSelectInventoryItem`; P2 explicitly requests verified `OnGetItemData` for the
selected ID and revision. The effective merged `CR4InventoryMenu.ShowItemTooltip`
calls the existing provider and publishes **`context.tooltip.data`**.
`ContextInfoManager.initialize` registers `dataReceiver` for that binding.
The installed provider emits **`ItemId`**, `ItemName`, `PrimaryStatValue`,
`PrimaryStatDelta`, `PrimaryStatDiffStr`, requirements and `equippedItemData`.
Its primary-stat comparison uses the relevant actual equipped slot; P2 retains
the native difference string/colors and socket-count tradeoff, with no score.
`equippedItemData` is freshly created by `GetTooltipData` where comparable.

P2 caches this payload by **ItemId before any tooltip access** and raises a dirty
event. Hidden/nonexistent tooltip presentation cannot block it. While awaiting
the payload, native stub name/category remains available; unsupported numbers
are omitted. A Node test executes this actual receiver branch with a tooltip
getter that throws. This establishes source/data routing, not successful live
Flash delivery. First screenshot must show the real selected item's name/stat.

## Verified input owner and state model

Native `InputManager.isGamepad()/isMouse()` and
`ControllerChangeEvent.CONTROLLER_CHANGE` (`controller_change`) drive the
unchanged footer's glyph repaint. Its public `handleSetupButtons(Array)` takes
`KeyBindingData`; its buttons expose `getBindingData`, click emulation and native
input routing. P2 locates the actual common instance by its public traits in
the stage display list; actual discovery and device transitions require runtime
confirmation. A trace records the discovered owner. Bindings repaint on dirty
mode/device/native-hint changes, not every frame.

| State | Routing |
|---|---|
| Browse | Native select/equip/unequip, category/sort/drag. Inspect I/View, equipment targets Tab/L3 reuse verified input events; native footer renders one device at a time. |
| Inspect | Native full card within browse region; Shift/LT compares, wheel/arrows/right-stick scroll; Esc/B or Inspect returns to saved item ID/page. |
| Auxiliary | Native paperdoll focus/targets inside browse region; native tooltips beside targets; Esc/B returns to Browse. |
| Native modal/drag | Native modal/cancel takes priority; custom interception yields. |
| Other categories/shop/stash/horse | Leave P2, restore native v4 masks/transforms/footer/art. |

The two P2 commands use audited physical input codes; arbitrary user remaps of
I/Tab are not discovered. Primary/sort action availability comes from native
binding data. D-pad down/hold/up gating reuses the proven v1 mechanism, while
mode actions occur once on release. Device switching only dirties prompts;
stationary mouse hover cannot steal gamepad focus. Full gamepad, mouse click
emulation, Hoods, Roach and shop/stash behavior remain runtime acceptance tests.
