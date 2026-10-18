# Adaptive Inventory P2 — Coherent Gear Prototype

18 October 2026 · private structural candidate · **awaiting in-game screenshot
and interaction acceptance**. P1 remains rejected. No live deployment.

## Implementation

[Gate A ownership and evidence](adaptive-inventory-p2-ownership.md) records the
accepted v4 input, actual owners, native selection/data/footer contracts and
remaining runtime unknowns. P2 starts from that v4 movie, never P1's compiled
output. Only Inventory changes; common navigation, HUD, art caches, Hoods movie
methods, other menus and current merged scripts are retained.

The former native section-column layout is bypassed in player Gear only. Real
native slots now use one first-fit gallery with native sorting, two-cell item
footprints, actual equipped identities/markers, scrolling and drag/action
contracts. Sparse six-item content uses three columns, populated content six
or seven. Packing is refreshed on item-data changes; selection alone never
rebuilds the scene. Native grid position persistence is suppressed for this
temporary display layout. Selected identity and scroll position survive updates
where the item still exists.

A single geometry function allocates category row, gallery, three-line summary
and adjacent live Geralt preview inside reserved header/footer bands. The
original category renderers remain interactive; their redundant title and
weapons/armor headings are hidden. Native sort controls occupy the row's right
side. Orbit artwork is removed from the content by local suppression plus an
Inventory-only dark canvas. The native character renderer remains live and is
masked/reanchored in the preview. Twenty native equipment targets are available
in an explicit Auxiliary mode in the browse region, never around Geralt's feet.

The summary reads the selected renderer's ID and requests native `OnGetItemData`.
`ContextInfoManager.dataReceiver` caches `context.tooltip.data` by its real
`ItemId` before any presentation logic. It no longer asks whether a tooltip is
visible. Stable fields show the native name, damage range/armor and supplied
colored primary difference, then requirements/warnings or socket tradeoff. No
universal quality score, synthetic comparison or acquisition history is added.
Native full content remains available in Inspect, including native comparison
and scrolling, with identity/page restoration on return.

Browse, Inspect and Auxiliary share **the existing common footer instance**.
Native device detection and its unchanged glyph renderer choose keyboard or
controller hints; there are no added button sprites or combined-device labels.
Native primary/sort bindings retain their availability. Device changes dirty
prompts without changing focus. Native sorting, dragging, selection modals and
advanced character controls retain priority. Other Inventory modes restore v4.

## Exact scope and reproduction

Changed resource: `gameplay/gui_new/swf/inventory/panel_inventory.redswf`.
Changed classes: `MenuInventory`, `InventoryTabbedListModule`, `SlotsListGrid`,
`SlotsListBase`, `SlotBase`, `ModulePaperdoll`, `ContextInfoManager`,
`TooltipInventory`. All original public/protected declarations survive. Original
equipped-in-grid annotations remain `src/inventory/inkGearGrid.ws`; no new
WitcherScript API/provider, saved fields or QoL dependency is introduced.

Original additions: `src/inventory/p2/*.asinc`, `tools/patch-inventory-p2.py`,
`tools/verify-inventory-p2.py`, `tools/build-inventory-p2.py`,
`tests/test_inventory_p2.py`. Vendor sources/binaries remain private/ignored;
personal modification authority is documented in AGENTS.md. Original third-party
archives, P1/v1, Menus v4 and RC2 release packages remain intact.

With the pinned local v4 exports and tools available:

```powershell
python tools/build-inventory-p2.py inspect
python tools/compile-ink-gear-grid.py --out build/adaptive-inventory-p2-scripts
python tools/build-inventory-p2.py prepare
python -m unittest discover -s tests -p test_inventory_p2.py -v
python tools/build-inventory-p2.py native
python tools/build-inventory-p2.py package
python -m unittest discover -s tests -p test_inventory_p2.py -v
```

Compiler/deploy destinations must be fresh. Compiled checkpoints resume only
with identical movie and AS inputs. Native stages use an isolated local runner,
not installed game files; metadata startup timeouts can be retried separately
after verifying exact cooked/packed content. Logs retain failed attempts.

If metadata alone remains unavailable after a blank startup timeout, the explicit
`metadata-fallback` stage can invoke the existing native-control-verified codec;
that outcome must be labelled reconstructed, never native metadata success.

## Private release result

ZIP: `deploy/adaptive-inventory-p2/Adaptive-Inventory-P2-Coherent-Gear-private.zip`.
SHA-256: `0f26fea465512ca4a81c120e7e5207c014db1e912ff3e117f2bbc06518b1b415`.
Machine-readable [release receipt](adaptive-inventory-p2-release-manifest.json).

**Final candidate:** 13 targeted tests passed, zero skipped; 24 geometry cases.
Native **cook, validate, pack and metadata all completed** with exit code 0.
Validation found one file and zero erroneous resources (zero major/minor/tiny
errors). No reconstruction fallback was used. Prepared bytes, cooked bytes and
exact single-key bundle extraction match. All original 4,269 public/protected
declarations, non-code tags, texture tails and protected live inputs passed.

Native logs contain the already tolerated isolated-runner depot-directory and
missing dog soundbank assertions; no new assertion type was accepted. Script
control/candidate compilations passed with matching existing diagnostics. Earlier
pre-correction metadata attempts timed out three times at blank startup; their
logs are preserved under private `before-loop-fix`. The corrected source was
freshly cooked/validated/packed and metadata completed normally. V4's historical
fallback is separate from these final P2 native results.

## Validation and limits

Executable geometry covers the observed six-item count with conservative tall
footprints and synthetic 24/80-item fixtures at 1649×928, 1080p, 4K and 2560×1080.
Both authored 16:9 fit and viewport-aspect logical coordinate policies are
checked: **24 cases**, disjoint gallery/summary/preview/header/footer rectangles,
sparse content fitting and dense last rows reachable. This does not read a save
or establish the game's actual runtime UI scaling. Native item art/hit bounds,
font metrics, mouse/controller changes and 3D framing need runtime confirmation.

Tests execute the actual patched native placement check, the identity-keyed
receiver with tooltip access prohibited, and the actual summary method with two
distinct fixture IDs/native-formatted delta. They also verify compiled scope,
original declarations, unchanged artwork/atlas, Hoods and footer classes, exact
package extraction and protected live-file hashes. Fixture values are test-only;
no fixture items or statistics are embedded into the release.

Known limits: custom Inspect/Equipment use audited I/View and Tab/L3 codes;
arbitrary remapped I/Tab bindings are not discovered. The actual common-instance
discovery, live Flash payload arrival, footer transitions, drag focus, long-name
clipping and renderer framing are **not established by offline tests**. On absent
native comparison only supported information is shown. Pending provider data
uses the native stub name/category; a category-only persistent fallback fails
runtime acceptance and should be reported. Existing native full details remain
the complete statistics surface. No new work on Usables/Satchel/Review/cleanup.

## Manual test installation and one-package rollback

1. Exit the game. In a cloned test profile disable rejected
   `modAdaptiveInventoryV2GearP1` and old Gear-grid v1, if enabled. Keep accepted
   Menus v4, Gentium, item/Bestiary/Map art, HUD RC2, Hoods, Outfit Wheel, Smooth
   Map, FriendlyHUD and working merges enabled.
2. Install the private P2 ZIP from the companion release manifest. It contains
   only `Mods/modAdaptiveInventoryP2/content/{blob0.bundle,metadata.store}` and
   original `content/scripts/local/inkGearGrid.ws`. Set P2 to own Inventory
   **before** `modInkIronMenus087` (currently 14) and `modHoods` (16), using relative
   Vortex rules. Do not enable both candidate annotation packages. No binary
   load-order rule merges their methods; P2 already includes v4/Hoods contracts.
3. Deploy manually. Do not reset settings, regenerate merges, replace working
   merged Inventory scripts, install reference QoL mods or change HUD/art packages.
4. Run the read-only ownership gate before judging the UI:

   ```powershell
   python tools/build-inventory-p2.py verify-installed
   ```

   It must confirm P2 Inventory, all other accepted v4 movies, packaged members
   and protected HUD/merge inputs. It does not change priorities or deploy files.
5. Open player Equipment on the sparse level-1 save. First capture the whole
   screen with an actual item selected. Stop at the screenshot/short smoke gate
   before expanding the design.

**Rollback:** exit; disable/remove only `modAdaptiveInventoryP2` and redeploy the
test profile. Leave P1/v1 disabled so accepted Menus v4 owns Inventory again.
Keep existing accepted packages/order. No save migration, cache deletion,
settings reset or merge regeneration is needed.

## Prioritized runtime gate

1. Whole sparse screen: one navigation hierarchy, one contiguous item-first
   gallery, selected item's actual name/stat, integrated unobstructed Geralt,
   no orbit engraving and exactly one appropriate footer. If any fail, stop and
   report the image/device/state; native build success does not overrule it.
2. Change mouse → keyboard → controller in Browse, Inspect and Auxiliary;
   glyphs/hints change without focus loss. Ten D-pad taps, then hold/release.
3. Compare three swords consecutively; equip/unequip; item identity, marker,
   stat/comparison and page remain correct. Inspect I/View, scroll, Shift/LT,
   Back/Esc/B returns to the same selection. Repeat armor and no-comparison item.
4. Tab/L3/click Equipment; test native Hoods dye, Roach, crossbow/bolts,
   quickslots and drag targets. Back restores Browse; category/return works.
5. Populated inventory scrolling/sorting, long names/details, repeated open/close,
   1080p and 4K; then shop/stash/horse and accepted common menus/HUD/radial/OW.

Next work is **P2 runtime evaluation and correction only**. Adaptive categories
are the next design phase after structural acceptance; acquisition Review and
safe cleanup remain later phases.
