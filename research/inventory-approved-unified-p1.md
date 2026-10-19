# Approved Inventory — Unified P1

19 October 2026. Private first-playable candidate, **not runtime or visual acceptance**.
Authority: [unified scope](../design/inventory-unified-category-build-scope.md),
[approved reference](../design/inventory-reference-accepted-review.md), and the
user's attached implementation request. Review persistence remains deferred.

## Inputs, ownership and scope

Fresh read-only ownership check: `modInkIronMenus087`, priority **13**, owns
Inventory and Common. `modHoods`, priority 15, also supplies Inventory but loses
that binary resource to v4. This is a resource collision, not a merge resolved
by Vortex file rules. The candidate must own **Inventory only**; v4 retains Common.

| Input | SHA-256 |
|---|---|
| Exact accepted v4 Inventory | `a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a` |
| Installed accepted Common | `54915e76c9bea31d67d9f64ec688b268ee86939e58c6712438cbc3192c82eb8c` |
| User-authorized reference PNG, 1672×941 | `b1443ffafc009a5f123d6c971e3ea1e47572763b229595ab78d76799bde87313` |

The accepted v4 resource matches the complete `before/source.gfx` export kept
under the historical P1 build directory. That export is **v4 input**, not P1's
rejected output. The patch transforms v4 directly. All non-ABC tags, five texture
atlases/222 rectangles and original class declarations are retained. Hoods
`SlotPaperdoll`/`ItemDataStub`, `CharacterRendererController`, shared feedback
classes and every other menu/HUD resource remain byte/source exact as applicable.
Private source/assets retain their existing CDPR/Ink & Iron provenance; only
original adapters, reproducibility code, tests and this report enter Git.

## One scene and native identity model

Normal, unfiltered `IMS_Player` uses one category rail, one fixed-scale row list,
one retained native details instance and the existing live Geralt renderer.
`SetInitialTabNewFlags`/`SetInventoryState` explicitly enable the scene only for
that state. Shop, stash, horse and tag-filtered states disable it and restore
native objects before normal v4 setup. Standalone Alchemy/Crafting are untouched.

`OnApprovedRefresh` enumerates `_inv.GetAllItems`, asks the **real player component's
ShouldShowItem** across the six native filters, and restores its original filter.
Only the temporary enumeration probe ignores equipped exclusion. Native hidden,
quest, schematic, tag and forbidden-tag rules still run. Each eligible ID produces
one actual `ItemDataStub`, populated through `SetInventoryFlashObjectForItem`.
The adapter enriches localized name/category, rail group and actual equipped state;
it does not replace native quantities, slots, actions, restrictions or IDs.

| Rail | Actual source predicates, in precedence order | Authored classification cases |
|---|---|---|
| Review | Reserved, disabled, “Not enabled”; no fake count or acquisition flag | No return group 0; no click handler |
| Quest Items | Native `Quest` tag first, including otherwise-equipment/readable items | Quest sword, quest book |
| Other, horse/trophy | `IsItemHorseItem` / `IsItemTrophy` before equipment classification | Saddle, trophy |
| Pockets, dyes | Category `dye` or actual Hoods `mod_dye` tag | Native dye, Hoods dye |
| Bombs | `petard` | Bomb |
| Consumables | `potion`, `oil`, or `IsItemFood` | Potion/decoction, oil, food |
| Armor | `IsItemAnyArmor` | Armor, boots |
| Weapons | `IsItemWeapon`, `IsItemBolt`, or `crossbow` | Steel, silver, crossbow, bolt |
| Pockets | Mask/tool/usable category or native quickslot slot | Mask, quickslot item |
| Other | Remaining native-eligible IDs | Crafting material, ordinary book, unknown mod category |

Ordinary groups are disjoint and have an exhaustive final fallback. Native tab
indices are never interpreted as rail positions. The 21 fixture cases execute
the authored classifier after type erasure with mocked inventory predicates;
they do not establish membership of every installed mod's items in a real save.

Rows use real `SlotInventoryGrid` instances with native owner/listeners, data,
hit areas, actions and drag source. They are **not stretched native grid sections**.
Nine retained instances cover seven visible rows, with a one-axis viewport.
`gridSize`, slot type and original gameplay grid-position data are preserved.
Native packing, section navigation, grid reorder drops and renderer cleanup are
bypassed only while the retained list owns presentation. Equipment target drops
still use native `SlotPaperdoll`; a paperdoll-to-list drop routes native unequip,
not a fabricated row index. Manual spatial rearrangement of the former grid is
intentionally superseded by the sorted list.

Per-category state stores selected genuine ID and page. Refresh preserves existing
ID order and appends new items; explicit native sort reorders while restoring ID.
Removed IDs select a surviving nearby page item. Existing native position-index
selection callbacks cannot overwrite the row controller's identity selection.

## Presentation and details

Logical v4 authoring space remains 1920×1080, inheriting the game's UI transform:
rail `(52,174.5,274,721.04)`, rows `(365,200,338,726)`, details `(747,190,464,730)`.
Row pitch 105.6, row 338×90. These reproduce Gate 1's approximately 294×78 rows at
1672×941; sparse content leaves intentional space. Names ellipsize, subtitles and
native quantities/charges stay subordinate. Icons use the accepted native loader,
aspect-preserving 53×80 maximum; no enlarged low-resolution equipment tiles.

The equipped notch is the accepted v4 `SlotInventoryGrid.iaiFlags` flag **4**
(`data.isEquipped`) and `SlotBase.iaiDrawLess` triangle: `(3,3) → (12,3) → (3,12)`,
color **#B48C44**, alpha **0.9**, native concatenated-scale compensation `k`.
The same mark is translated to the row icon well `(22,5)`. The old `equipedIcon`
remains alpha zero. No new badge or equipped sidebar.

Rail silhouettes are drawn once from actual native paperdoll default icons at
4× display resolution (steel/armor/potion/bomb/pocket); remaining groups reuse
native tab artwork. No target clip is reparented. These are native glyphs, not an
assertion of pixel-identical generated-reference pictograms.

Persistent details use a single actual `ItemTooltipRef_mouse` / `TooltipInventory`.
Selection requests `OnApprovedDetails(actualID, serial)`, which invokes the same
`W3TooltipComponent.GetTooltipData` provider as native `ShowItemTooltip`, including
`equippedItemData`. The resulting `context.tooltip.data` payload carries the request
serial. `ContextInfoManager` routes it **before** visibility-dependent native
tooltip display. Only matching ID **and serial** populate the retained card.
Mouse/native-hover unnumbered or old-revision responses cannot overwrite it.
Name appears immediately for a newly selected ID; previous item's stats are never
relabelled. Same-ID equipment refresh keeps the existing card until new data arrives.

The original v4 item requirements, damage/armor, signed comparisons, properties,
descriptions, sockets, sets and advanced content remain native; long content scrolls
instead of shrinking to fit. The large duplicate header icon/plate is suppressed
inside this owned card. This is real native information, not a universal quality
score or a hand-written sword-only summary. Exact vertical text hierarchy and
long-content fit still require the first in-game screenshot.

Geralt remains the original live renderer: scale 1.05, texture anchor centered
around logical `(1510,528)` using its measured `(481,485)` origin. Its controller,
render target and equipment updates are retained. Only Inventory's `iaiArtHost`,
old-slot background and paperdoll decorations are suppressed. An Inventory-local
neutral charcoal gradient and understated ground shadow replace the obsolete orbit.
No shared texture cache, HDR, global exposure, navigation or other menu art changes.
The scene is explicitly below the live renderer in display order; a separate
preview mask `(1245,120,630,810)` prevents its texture rectangle crossing the
details/header/footer safe areas, and restores the original mask on leaving.
Runtime model/camera framing and native lighting are explicitly unverified.

## Inputs and preserved actions

One footer: the real **Common script bus**, `UpdateGFxButtons` plus native context
bindings → `common.input.feedback.setup`. No stage search, foreign movie objects,
permanent command rectangles, or mixed-device labels. Common's accepted glyphs and
InputManager/controller-change handling own device presentation.

| State/action | Contract |
|---|---|
| Browse | Up/down native row movement; left rail, right details. Mouse hover/click uses actual row ID. |
| Rail | Up/down category; right returns to list; Review is skipped/disabled. |
| Details | I / native View (`back`) toggles focus, wheel/Page/up/down/right-stick scroll; Back returns to list. |
| Auxiliary | Tab / native L3 (`gamepad_L3`) shows retained native targets; Back returns to list. |
| Native equip/use/read | Native E/A/action context remains the owner. Only already-equipped armor/weapons adapt primary action to native `OnUnequipItem`. |
| Compare | Existing Shift/LT and native `equippedItemData`/tooltip comparison. Native context supplies applicable compare hint. |
| Sort | Q quick sort; F/native right-stick sorting modal; existing sort implementation, ID restored. |
| Modal/drag/stats | Native handlers take priority; stable scene is suspended rather than destroyed. Mode restoration preserves item/page. |

Oil/upgrade target selection, food/potion consume/assign, bomb charges, quest/read
and drop restrictions, crossbow/bolt, Roach, Hoods dye and special mod actions still
run their original context/provider/target methods. They are **source retained and
compile checked**, not all runtime tested. No generic “equip everything” adapter.
Quickslot/radial/HUD resources, Outfit Wheel, FriendlyHUD, AutoLoot and Smooth Map
receive no changes. Full native target access is on demand, not an equipment orbit
in normal browsing.

## Stability checks and honest limits

The rejected P1/P2 display architecture is absent: no sectioned gallery, P2
geometry/footer/summary controller, per-frame reflow, full-list cleanup or repeated
model creation. Only original pad repeat gating and native-target snapshot/restore
ideas are reused. Competing v4 equipment-first presentation is bypassed while the
unified scene owns the player screen, then restored at the special-state boundary.

`verify-approved-inventory.py` executes the authored AS list and repeat bodies
after type erasure in Node, mocking Flash display/events. Cases include two-item
sparse view, 180-item list/scroll, repeated same-ID refresh, equip-state change,
selected-ID deletion, empty list, bounded allocation, native-property restore,
D-pad down/up and held repeat. **Nine allocations; zero unchanged-icon reloads**
in those mocked runs. They do not execute Scaleform or establish visible continuity.
Geometry projections cover 1649×928, 1672×941, 1080p and 4K within header/footer bounds.

`approvedInventoryTrace(true)` in an already available game console enables
non-saved diagnostic state; reopen Inventory to start traces. `false` disables it.
The code emits ordered, millisecond-stamped Scaleform trace events for scene entry,
row create/destroy/bind, icon loads/stale completions, selected ID/request serial,
payload, category, focus, device and visibility-state transitions. It writes no
save/settings/debug file. Capture using an existing debug trace setup; no automatic
configuration changes. A screen recording is still needed to judge flashing.

Known unverified areas: real controller/device transitions, all heterogeneous
actions/modded tags, native modal/target mouse hit-testing, model framing, exact
details styling, 4K/HDR rendering and actual flicker. Review is deliberately
unavailable, with no persistence/ledger/count. No claim of final functional or
visual acceptance follows from compilation/offline tests.

The rail filters the exhaustive item projection locally. Native tutorial progress
that depends specifically on old tab-click indices is **not remapped**. Forced,
tag-filtered Inventory states stay native, but ordinary Inventory tutorial tab
progress needs an explicit early-game check. Native item eligibility, quest/drop
restrictions and actual item actions remain delegated to their original handlers.
Diagnostics become active on data refresh; first-entry pool creation can precede
the first enabled trace event.

## Exact surface and reproduction

Only resource: `gameplay/gui_new/swf/inventory/panel_inventory.redswf`.
Changed classes: `MenuInventory`, `InventoryTabbedListModule`, `SlotsListBase`,
`SlotsListGrid`, `SlotBase`, `SlotInventoryGrid`, `ModulePaperdoll`,
`ContextInfoManager`, `TooltipInventory`.
Original annotation file: `src/inventory/unified/approvedInventory.ws` adds scoped
CR4InventoryMenu/player-component/context adapters and the opt-in trace flag.
New Flash callbacks: `approvedEnabled`, `approvedDiagnostics`; script requests:
`OnApprovedRefresh`, `OnApprovedMode`, `OnApprovedDetails`; binding:
`inventory.approved.items`. All original public interfaces remain.

```powershell
python tools/compile-ink-gear-grid.py --out build/approved-inventory-unified-scripts-final --source src/inventory/unified/approvedInventory.ws --disabled-assignment 'aiApprovedActive = on;'
python tools/build-approved-inventory.py prepare
python tools/verify-approved-inventory.py
python -m unittest discover -s tests -p test_approved_inventory_unified.py -v
python tools/build-approved-inventory.py native
python tools/build-approved-inventory.py package
```

Compiler output must be fresh; use a new path and update the builder pin for a new
script revision. Movie compile checkpoints/native prior logs remain private.
Packaging rejects source/compiled mismatches, changed protected installed inputs,
unexpected resource keys or failed exact bundle extraction. Private manifest and
native commands/logs are under `build/approved-inventory-unified-p1/`.

## Release validation and private artifact

ZIP: `C:\Dev\witcher-ui-overhaul\deploy\approved-inventory-unified-p1\Approved-Inventory-Unified-P1-private.zip`

SHA-256: `9f3a0592704f1dc632ade76a0ce755849155b89e234bf6e8d43932b40d0c69f3`.

Released Inventory resource SHA-256:
`8a61619d9439887c72142c95e43430db3be8ed56f294ae364d4bcb5183478436`.
Released original annotation SHA-256:
`3e081eb6506d60776c5082a2254affc8bf3f1d70a9160e96d605a14dac727740`.
The annotation source is byte-identical to the successful API-control/candidate
compiler receipt in `build/approved-inventory-unified-scripts-final/receipt.json`;
both compiled blobs are checked by hash again during packaging. Later stalled
compiler attempts are retained separately and are not passed off as success.

| Verification | Actual result |
|---|---|
| Final v4 → candidate ActionScript compile/export | Passed; nine intended classes, **4,269** original declarations retained |
| Art/fonts/symbols/resource integrity | Non-code tags/atlases exact, CRC/atlas checks pass; frozen Hoods/controller/feedback classes exact |
| Targeted test suite | **8 passed**, including 12 authored list/repeat scenarios, **21** classifier cases and four geometry projections |
| Final native cook attempt | **90-second blank startup timeout**; final candidate was not natively cooked/validated |
| Earlier private intermediates | One completed all four stages; another completed cook/validate/pack before metadata startup timed out. These are not final-candidate validation |
| Released bundle/metadata | Controlled reconstruction, exact one-key extraction and ZIP member hashes passed |
| Protected installed inputs | Unchanged, checked again at packaging |
| In-game visuals/actions/flicker | **Not tested or accepted**; manual user gate remains |

Reconstruction retains two byte-identical native bundle controls, five native
metadata identity controls and independent changed-bundle/metadata controls.
It uses the original one-resource **container** templates, not an old Inventory
movie/layout. The payload is exclusively the newly transformed accepted v4 movie.
`tools/native-zlib-control.py` uses the local Git standard zlib 1.3.1 DLL,
SHA-256 `cb7ab3788d10940df874acd97b1821bbb5ee4a91f3eec11982bb5bf7a3c96443`.
System Python uses zlib-ng and Node uses a different zlib fork; neither reproduced
the native compression streams, so their failed controls were not relaxed.
The standard DLL passed the full native controls before release. Override its
location with `INVENTORY_ZLIB_DLL` only if the same identity controls pass.

If reproducing the same **blank startup timeout**, run
`python tools/build-approved-inventory.py reconstruct` before `package`.
That path refuses nonblank native diagnostics and requires every reconstruction
control. It does not claim native candidate validation. Commandlet startup logs
on successful intermediates contain the already-known depot-directory and missing
`ly_animal_dog.bnk` assertions; resource validation itself reported zero errors.

## Manual installation and rollback

1. Keep the accepted v4/HUD setup and a known save. Use a cloned Vortex test profile.
   Disable any old Gear-grid, Adaptive P1/P2 or prior Inventory candidate there.
2. Add **only** `deploy/approved-inventory-unified-p1/Approved-Inventory-Unified-P1-private.zip`
   to Vortex. Its sole mod is `modApprovedInventoryUnifiedP1` (one movie + original
   annotation file). Leave Menus v4, its fonts/item art and existing integrations enabled.
3. Manually give this candidate a lower numeric resource priority than Menus v4
   (e.g. **12** if v4 remains **13**). Merely ordering ZIP installation is insufficient
   for internal bundle-key ownership. Do not overwrite v4 or Hoods packages.
4. Deploy manually. The new `.ws` uses native annotations; no replacement merged
   inventory script is shipped. If the current stack reports script errors, stop
   and retain the compiler message; do not regenerate the working merged scripts.
5. Manual alternative: with the game closed, extract the ZIP's single `Mods/`
   subtree into the game root, preserving its unique mod directory; manually set
   only the candidate priority as above. Do not combine manual and Vortex installs.

Rollback: close the game; disable/remove **only this candidate** from the test
profile and manually redeploy (or remove its unique manually installed mod folder
and candidate settings entry). Menus v4 becomes Inventory owner again at 13;
Common/HUD were never replaced. No save conversion or blanket settings reset.
No installation, Vortex action, settings/merge/save edit was performed by this run.

## Prioritized user acceptance

1. First screenshot: sparse Weapons then Armor; approved rail/rows/details/Geralt,
   correct item scale/notch, no orbit art, no duplicate footer or missing selection.
2. Move between all seven ordinary groups; check known food/potion/oil, bomb,
   pocket/dye, quest/book and material/Roach items. Review should explicitly say
   “Not enabled” and have no click/count.
3. Compare several swords; equip/unequip, continue browsing; I/View → Back and
   Tab/L3 → Back must preserve ID/page. Record any flashes/stale details.
4. Use/assign consumables/bombs/pockets; dye/Hoods/quickslots and actual equipment
   drag targets; read quest/books; verify quest restrictions, tutorial tab progress
   and the native sort modal.
5. Switch mouse/keyboard/controller, single D-pad taps/held repeat, long Other
   scroll; enter/exit shop/stash/stats and reopen repeatedly at 1080p/4K.
6. Confirm shared v4 menus and accepted HUD/radial/glyphs/quickslots are unchanged.

Next stage: correct only demonstrated runtime/parity defects first. Add the
acquisition-aware Review ledger after this shared foundation is accepted; do not
start bulk cleanup or another composition redesign.
