# Inventory QoL source findings — 17 October 2026

These are downloaded references, **not installed candidates**. No third-party
runtime code was copied into this Gear release. See the [evidence manifest](adaptive-inventory-v2-qol-manifest.json)
for exact archive/member hashes, GFx resource keys, script annotations and
installed-file hashes. Extracted files and decompilations stay in ignored
`build/adaptive-inventory-v2-p1/`.

| Supplied archive | SHA-256 | Version / target evidence |
|---|---|---|
| Sort Everything 1710 1.55 2026-10-17T06-57Z iNpQhXiL0.zip | `3dde41c51805622f268d281fa7d515f23739843b020fbb67f458190280c6e1f3` | `info.json`: 1.55, engine gameVersion 29, no declared dependencies, precompiled blob, useLooseScripts false. Annotation scripts and modern UI are supplied. This is not an independent 5.01 runtime certification. |
| RecentLootTab (5.01) 13981 1.0.0 2026-10-09T21-35Z ZqIodYbcK.zip | `ca7ef9f13e958544a94de0530c3dde9c5bdc7a201a2f3b488e8e5c0849cd3d5b` | README: 1.0.0, Remastered 5.0+, author tested 5.0.1; annotations required; 4.04 unsupported/untested. |
| JunkNotTreasure 14451 1.0.0 2026-10-16T12-53Z CvjFPsCYo.zip | `edcade7892f4bac92195bee72606fd13b5f487dd28c21f5ef004e7e063bbefb9` | Archive label 1.0.0; annotation-only sources, XML and strings, no movie/blob. No explicit engine target or independent 5.01 validation found in the archive. |

There are **three ZIPs**, not four. The supplied Sort Everything main ZIP already
contains `modSortEverything.xml` and `dx12user.settings.part.txt`. No separate
settings download is present or needed for this research.

## Feature/adoption matrix

| Feature | Evidence / current state | Decision |
|---|---|---|
| Existing native sorting, equipped markers, tooltip comparison | Accepted v4 classes and current merged Inventory; compiler control/candidate verified separately | Reuse directly; no sorting dependency in Gear P1 |
| FriendlyHUD start category and low-value new-marker suppression | Enabled 0.9.2R, priority 23. `modFriendlyHUDConfig.ws` GetDefautltInventoryTab and GetResetNewItemsInCategoriesArray; merged Inventory references these hooks | Already available in installed stack; preserve. Text settings contain no explicit fhudInventory overrides, so preset XML values are defaults, **not proof of active runtime selections** |
| Current AutoLoot | Enabled priority 44; Vortex label `01-brawler-only-core`. Installed local manager/config plus player/container/loot-popup/feed scripts | Already present; keep it. Saved DX12 options: mode 2 (single interact), PassiveHerbs true, herb/corpse/general radius 3, theft mode 1 (never steal). No second auto-looter |
| Sort Everything damage/armor and subtype sorting | `SE_SetPrimaryStatSortData`, `SE_ComparePrimaryStat`, native section/slot/category tie breakers; finite applicable-stat check; primary descending, then new/sortGroup/action/edibles/equipped/slot/category/quality/ID | Adapt later with an explicit comparator/Flash-data port. Damage mode is section-aware but **does not sort subtype before damage**; do not describe it as a quality score |
| Category-specific sorting | `inventory_sorting.ws` groups oils/potions/mutagens/bombs/other and localized name keys; `SE_ComparePotionGroups` in GFx | Useful for future Usables density/filtering |
| Selection preservation | Sort Everything GFx updateItemData/updateItems retain the native cached **index**, including its index-zero truthiness pattern; SetTabNewFlags wrapper restores current filter | Useful contract evidence; P1 independently preserves actual selected item ID/scroll on updates instead of importing this movie |
| Stash/crafting sorting | `SE_SetStashSortingMode` bridge; modes default/name/level/damage/price/weight/rarity; actual instance level, including NG+. Crafting metadata includes revision, pin, level/new flags and callbacks | Adapt in a subsequent scoped change, not this Inventory-only release |
| Recent acquisitions | OnItemGiven wrapper; saved parallel `recentLootIds`, `recentLootGains`, `recentLootSources`, saved viewed flag; loot/buy/receive contexts; horse/stash transfer suppression | Suitable later as a contextual Review data source, without the extra tab |
| Acquisition chronology and quantities | Appends actual SItemUniqueId records; newest-first population; same-batch stack gains combine; later acquisitions can retain repeated IDs in history; 99-cell trim, prune invalid IDs. Engine seconds only group events within 2 seconds | Genuine ordered history, **no saved wall-clock timestamps**. A Review display must distinguish acquisition records from unique inventory identities and clamp to currently owned quantities |
| Inspection/dismissal | Closing Inventory sets the one saved `recentLootViewed` flag; Clear removes history | No durable per-item inspected state; future Review needs its own explicit dismissal contract. Gwent identity may disappear on load, as README explains |
| Protection/sell marks | JNT_mark integer item modifier: 0 neutral, 2 sell, 1 protect; Get/SetItemModifierInt, native inventory item identity | Adapt concepts later; no new persistence in P1. No separate saved favorites registry. Modifier behavior across split/merge/new IDs still needs disposable-save tests |
| Bulk sales and dismantle | Merchant plan previews quantities/cost, excludes protected/equipped/hidden/CanDrop-failing items, respects money and rechecks price/quantity on execution. Blacksmith callbacks check displayability, marks, enchantments and scope; confirmation popup classes | Later safety phase only. Not a blanket safety certification: SalePlanRun rechecks ID/price/quantity/funds but does not itself re-evaluate every protection predicate after confirmation |
| New permanent tab, cleanup during browsing, new HUD/radial | Not needed for Gear decisions | Not useful for this release |

## Exact collision boundaries

Sort Everything's bundle owns **seven paired redswf/swf menus**: Inventory,
Alchemy, Crafting, Bestiary, Books, Tutorials and Quests. Recent Loot owns
Inventory, Alchemy, Crafting and `gwint/deck_builder.redswf`. Their Inventory
`MenuInventory` / `InventoryTabbedListModule` / `SlotsListGrid` implementations
cannot coexist with v4/P1 by ordering whole movies. Sort's extra ItemDataStub
fields and `SE_SetDamageArmorContext` / `SE_SetStashSortingMode` bridge callbacks
also require the matching data producers. Recent Loot adds tab 5, jump/clear
callbacks and recipe/deck bridge behavior. A future port must reconcile those
methods with our code, Hoods `SlotPaperdoll.canDrop` and v4 typography.

Script intersections are explicit in the manifest. Sort wraps Inventory
OnConfigUI, SetInitialTabNewFlags, PopulateTabData, PopulateDataForTab,
SetTabNewFlags and base SetInventoryFlashObjectForItem. Recent Loot wraps
SetInitialTabNewFlags, InventoryUpdateItem(s), OnMoveItem(s), PopulateTabData,
OnConfigUI/OnClosingMenu and loot/buy/horse acquisition paths. These overlap
our wrappers and the existing merged Inventory/FriendlyHUD data paths.

JNT has no binary movie collision, but it wraps Inventory primary feedback,
SetInventoryFlashObjectForItem, OnSelectInventoryItem, sale/drop/transfer,
OnSellAllJunk and blacksmith actions. Its Z/controller-back marking input must
be reconciled with P1's View/Select Inspect binding before any adoption. Its
copyright header reserves reuse/redistribution; this report analyzes behavior
and copies none of its implementation. None of these archives is Git payload.

The installed AutoLoot is a locally labeled core variant, not a version inferred
from a current public mod page. Its enabled status/configuration and source are
observed; this run does not independently establish every existing feature's
in-game working state. Its source replacement paths are another reason to
retain current merged scripts rather than install acquisition wrappers blindly.

Reproduce evidence: `python tools/research-inventory-qol.py`.
