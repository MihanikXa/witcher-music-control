# Ink & Iron 0.8.6 Gear-grid prototype v1

16 October 2026. First **implemented, privately installable** Inventory slice;
not an in-game acceptance claim. HUD v4/RC2 is frozen and untouched.

## Inputs and actual ownership

The existing checkout was already at a9aab65. The official Nexus
[files](https://www.nexusmods.com/witcher3/mods/13111?tab=files) and
[changelog](https://www.nexusmods.com/witcher3/mods/13111?tab=logs) identify 0.8.6
and the separate Hoods optional file. We use the **UI module inside the supplied
official 0.8.6 All-in-One**, not an invented standalone UI ZIP or the old 0.8.0
snapshot. No All-in-One deployment is proposed.

| Local original archive | SHA-256 |
|---|---|
| Ink and Iron - All in One 13111 0.8.6 2026-10-15T18-45Z z2QRfnz9T.zip | 2beb77716b6b5b5e8acf7d2c5ea65ba950ed9726d0c0e0cb5e40e1ce407d6e00 |
| Ink and Iron - Hoods Compatibility 13111 0.8.4 2026-10-13T15-59Z mlFpu6vCy.zip | 617f6d37d94158d751b3a3e6c3c0c5308e567f65ec74e007a967108d1a56802c |

Pinned original archives are in ignored `reference/ink-and-iron-0.8.6/archives`;
UI members match the existing extraction exactly. The patch is also pinned under
that versioned folder's `hoods-compat`. Source payloads/exports and their manifest
are under `inventory-source`. All vendor assets remain private and gitignored.

Both inputs replace `gameplay/gui_new/swf/inventory/panel_inventory.redswf`:
UI **10c63da7879ed48779c7e68c4cae8efaf17b71b83c2521f4fe1bc6825f3de9bd**;
Hoods patch **90905cebbaac7b0a0f18671d32549e663b7aff67314334d9663e350c32e01a10**.
The patch contains only that movie, metadata and readme, no scripts/DLC. It is
labeled **0.8.4**, not 0.8.6. Its inventory lacks the later debounce and connector
option. Taking it wholesale would regress those changes. We instead reuse its
**exact canDrop method** and isDyeable data field in 0.8.6. This is the author's
existing compatibility rule, not a replacement Hoods implementation.

Actual deployed Inventory owner before this prototype: **modHoods, priority 11**,
resource **2a2dacc886c86d4b08fced4cdc68c7882f2017d2f9d850b41b9ef98df060c68e**.
No I&I UI/official patch owns the live Inventory in this snapshot. Desired new
owner is the explicitly combined prototype. The accepted HUD root remains owned
by modInkIronHUDRefinementV4 at 31; its bundle/metadata and the merged Inventory
script were hashed before/after and remain exact. The RC2 private ZIP still hashes
**9cbc759c9002f11af32d43d69566ef6563fc66dfd1a2939cab23878777aa46c3**.

## Compact functional map

| Surface | Implementation / preserved contract |
|---|---|
| Gear grid | Existing InventoryTabbedListModule + SlotsListGrid and real item IDs. Native weapon/armor category (tab 4); 1.05 scale at x48/y186. Existing categories, section layout, sorting, scrolling and filters remain. |
| Equipped items | Native ShouldShowItem still runs every tag/quest/category filter. A scoped query flag suppresses only its equipped-gear exclusion. Real isEquipped state is supplied separately, driving I&I's existing corner marker/sort. No cloned IDs or shadow inventory. |
| Equip / unequip | Existing grid context equips; equipped gear's primary action calls native OnUnequipItem. Labels become Unequip. Native combat/tutorial gates remain. Post-equip removal becomes an item refresh only for valid equipped weapons/armor. |
| Character / slots | Six weapon/armor paperdoll targets leave the orbit and are normally hidden; equipped gear is browsed in the main grid. All 20 native slot objects, indices, listeners and hit areas remain. Auxiliary controls form a rectangular strip below the clean preview. |
| Dye / sockets / drag | Native selection mode or any drag reveals all original equipment targets in a compact rectangular target palette. Hoods Quickslot2 dye rule is exact official code; installed customDyeing.ws supplies isDyeable. |
| Details / comparison | 0.8.4+ TooltipInventory stats/comparison/scroll logic remains; card is docked to x1280/y166, 600x720 logical region. Connector is suppressed by the fixed-card path; upstream option setter remains intact. Shift / LT comparison stays native. |
| Navigation | Native grid input preserved, with per-key duplicate-down suppression and 400ms hold delay / 110ms repeat. Tab / left-stick click transfers focus between grid and auxiliary controls; normal actions/back/tab-category controls remain. |
| Shared menus / fonts | All 72 public exports from the actual installed Hoods Inventory retained; 4,266 original method/accessor declarations retained. gfxfontlib.swf import and atlas/fonts unchanged. Existing Gentium aliases/libraries remain enabled. |

This is a composed Gear-first grid, not the upstream Equipment First preset. That
preset is not enabled or packaged. Its 0.8.6 fix and the 0.8.5 setter remain exact.
FHUD's configured starting category is honored; select Equipment/Weapons for the
Gear test if its preference opens another tab. Other categories remain accessible;
there is no invented Recent tracking or removed crafting/quest data.

Only eight classes change: MenuInventory, ModulePaperdoll, SlotBase, SlotsListBase,
SlotPaperdoll, ItemDataStub, ContextInfoManager and TooltipInventory. There are no
new movie definitions, glyphs, fonts, atlas pixels or shared HUD/common/overlay
replacements. Auxiliary-slot geometry scales the actual native clips/hit areas;
drag targets are resolved by the existing topmost-entity path. All other class
sources are unchanged. Four FFDec double-negation literal renderings were
normalized to valid equivalent AS; original P-code confirms push-negative/negate.
After reflow, a saved paperdoll selection pointing to a hidden gear slot returns
focus to the live grid. Visible auxiliary targets and dye/drag selection retain
their focus; this prevents starting navigation on the removed equipment orbit.

The game shares this movie with Shop/Stash/Horse. Our custom layout/data inclusion
is gated to unfiltered player Inventory and restores on state changes. Those other
states retain **upstream 0.8.6** presentation, not the pre-prototype retail movie.
No custom Shop/Stash redesign or separate menu resource was implemented. Their
runtime behavior is not newly certified by this Gear slice.

## Build and validation

Original code: `src/inventory/`, plus prepare/patch/build/compiler/atlas/metadata
tools. Reproduce with fresh ignored destinations (compiler cache location is
SCRIPTS in the builder):

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/prepare-ink-gear-source.py
& $py tools/compile-ink-gear-grid.py --out build/ink-gear-grid-v1-scripts-final
& $py tools/build-ink-gear-grid.py --out build/ink-gear-grid-v1-focus --deploy deploy/ink-gear-grid-v1-release --stage prepare
& $py tools/build-ink-gear-grid.py --out build/ink-gear-grid-v1-focus --deploy deploy/ink-gear-grid-v1-release --stage native
# Only if native metadata startup fails; do not regenerate an existing store:
& $py tools/relocate-inventory-metadata.py --out build/ink-gear-grid-v1-focus
& $py tools/build-ink-gear-grid.py --out build/ink-gear-grid-v1-focus --deploy deploy/ink-gear-grid-v1-release --stage package
& $py -m unittest discover -s tests -p test_ink_gear_grid.py
```

**Passed:** exact-source script candidate and matched API/declaration control,
with identical diagnostics and no script errors; actual merged 5.01 Inventory and
Hoods dye sources verified in the assembly. Seven opaque dependencies remain
outside source recompilation. This is not a new Script Merger output or a runtime
no-op control. Native cook, one-resource validation (**zero resource errors**) and
native pack passed; cooked bytes equal prepared bytes. Five BC1/BC3 atlases, 222
rectangles, image handles, exports and native CRCs check. ZIP CRC, deterministic
ZIP generation and exact resource re-extraction pass. **11 targeted tests pass**;
the source-predicate input test does not execute Scaleform or prove game focus.
No broad HUD regression/performance suite was run.

**Final candidate native metadata passed:** cook, validate, pack and metadatastore
all returned exit 0. No reconstructed metadata is shipped. An earlier pre-focus
candidate hit startup timeouts; the independently tested single-key metadata
converter remains available as a fail-closed fallback tool, but was not used for
this release. Native command arguments, baseline depot-path/sound-bank assertions
and log hashes are recorded in the manifest; full logs remain in the ignored
build folder. Those baseline assertions did not report Inventory resource errors.

## Install, test and rollback

Private ZIP: `deploy/ink-gear-grid-v1-release/Ink-Iron-0.8.6-Gear-Grid-v1-private-test.zip`
(**1,112,198 bytes**), SHA-256:
`69fe187a267670a9477652693c0662a53cf8827c9b6594bf831efd89a60c9239`.
Exact hashes, owners and logs are in `research/ink-gear-grid-v1-manifest.json`.

1. Exit the game and use a cloned test profile retaining the accepted RC2 HUD.
   Install **only this ZIP**, creating modInkIronGearGridPrototype. Place it
   immediately **before modHoods** in resource load order; if an I&I UI/official
   patch is later present, the prototype must also own Inventory above those.
   Existing priority 10 belongs to JumpInShallowWater, so do not overwrite its
   setting or use a guessed priority. Preserve all existing relative ordering.
   This chooses an already combined resource; load order is not merging movies.
2. Keep Hoods, RC2 HUD, adaptive bars, aliases/Gentium, SAHUD, FHUD, OW, Smooth Map,
   NPC and compatibility/movement mods enabled. Do not enable the All-in-One,
   replace fonts/HUD, or enable the older official Hoods movie over this one.
   No menu registration, settings reset or Script Merger regeneration is needed;
   the one original annotation script compiles normally at game startup.
3. Load a normal Geralt save outside combat/dialogue. Open Inventory, choose the
   native Equipment/Weapons tab. Verify real swords/armor, equipped corner marks,
   Geralt preview, fixed details and weight; all other categories remain reachable.
4. Tap D-pad each direction ten times, releasing between presses: one focus move
   per tap, no early hold repeat. Then test held navigation, keyboard and mouse,
   scrolling, sort, and Tab / left-stick click to/from auxiliary controls.
5. Equip another sword and armor with A / Space and mouse double-click; marker,
   preview, weight/stats and grid membership must refresh. Unequip the selected
   equipped item and re-equip. Check Shift / LT comparison and long/set descriptions.
6. Test Hoods dye on a hood/cloak in quickslot 2, through native use/selection and
   drag/drop. Verify the compact target palette, native cancel/back, quickslot
   assignments/consumables, crossbow/bolts and Roach gear. Close/reopen and repeat.
7. Check 1080p/4K at normal UI scale for clipping, hit accuracy, scroll and comparison
   fit. Check ordinary menu transitions and the frozen HUD/OW/radial behavior.
   These are **pending runtime checks**, not claimed passes. Avoid campaign saves
   during the prototype test. Treat non-player shared-movie states as a smoke-test
   dependency before relying on them for ordinary item management.
8. Roll back by exiting, disabling only modInkIronGearGridPrototype and redeploying
   the cloned profile. Hoods resumes its original Inventory owner automatically.
   Leave RC2 and every accepted package enabled; no settings/merge/save migration.

No missing 0.8.6 source or Hoods implementation blocker remains. All four native
stages passed for the final candidate. Actual game initialization, focus,
equip/dye behavior and optical layout still need the user's first isolated test.
