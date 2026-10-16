# Gear-grid v1 — first screenshot design review (assistant observations)

**16 October 2026.** Based on two user-supplied in-game screenshots, both approximately 1646x927: Gear/Equipment with a selected Hunting Trousers item, and Alchemy/Crafting with a selected yellow flower. This is an **assistant interpretation**, **not user-authored feedback** or confirmation of functional tests. Screenshots remain chat attachments, not published repo assets. Implementation reviewed at `f623e90719060d5f9fbed847e6f0bf438eeb811a`.

## Bottom line

**Real functional prototype, but incomplete spatial and information design.** Three visual islands—left native category grids, center Geralt plus moved auxiliary paperdoll slots, and right tooltip panel—still behave independently. Retain Ink & Iron's dark literary language, item icons, header, gold semantic accents and full game systems. Do not accept the current geometry as the requested complete one-screen Gear redesign.

## Visible observations and actual source links

| Observation | Source evidence and likely next intervention |
|---|---|
| Fixed "GEAR" title overlaps the native "ALCHEMY AND CRAFTING" in non-Gear screenshot | `src/inventory/GearMenu.asinc`: `qfGearLabel("GEAR",23,48,105,620)` creates a permanent field in `qfGearRefresh()` for the whole unfiltered player inventory; no native tab-boundary/title switching or contextual visibility check. Remove redundant custom title or bind it to the actual selected category; do not hardcode another fixed position. |
| Weapons and armor are two small columns at top left, underused very large blank grid | `GearMenu.asinc` sets `mcPlayerInventory.x=48,y=186,scale=1.05` while retaining upstream native sectional grouping. The save has only two swords/four armor pieces, so scarcity partly reflects **actual early-game inventory**, not a broken item predicate. Need compositional response to low item counts, e.g. compact card groups/real adjustable grid viewport and coherent selection navigation; don't fabricate items or hide native categories. |
| Auxiliary quickslot/Hoods/Roach objects scattered over Geralt's shins/feet, tiny captions and dense double row | `src/inventory/GearPaperdoll.asinc` repositions 14 utility/native slots to x=786+66-column increments at y=798+78-row, using original art/hit areas. `GearMenu.asinc` labels at x756,y744 "Quickslots / Hoods / Roach [Tab / LS] Focus"; visible lower-middle overlap and old equipment-system visual residue. Keep all functionality but place controls in a discrete secondary region/palette or on-demand focus panel away from the character preview. No hiding functional targets without safe access and navigation. |
| Right-side Hunting Trousers stats readable but isolated; alchemy material selected while right side blank | `src/inventory/GearMenu.asinc` forces Geralt anchor x610; `tools/patch-ink-gear-grid.py` docks `TooltipInventory.iaiDock=new Rectangle(1280,166,600,720)`. Verify selected/hovered item actual tooltip state and the no-description setting before assuming a broken contract. The next version needs a coherent details/compare region or intentional context-specific adaptive placement, not arbitrary empty third of the screen. |
| Header hierarchy duplicated: Inventory top nav, Gear, Equipment, Weapons/Armor, and secondary auxiliary prompt | The extra custom `qfGearTitle` and `qfGearAuxTitle` are scripted additions, while native category headings and icon row remain. Prune duplicate labels and show status/action hints only in their relevant context. |
| Buttons and item icons visually subordinate/quiet, attractive restrained dark Ink & Iron styling | Preserve upstream styling, typography, header, icons and accepted gameplay HUD. Avoid color/font overhaul as a response to the more fundamental layout issue. |

## What v2 should target

First make a **single coherent three-region design for Gear** (grid/browse; clean Geralt preview; selected-item details+comparison) with all three regions aligned on the same vertical hierarchy. Make grid content organization respond sensibly to a 2-sword/4-armor early save as well as a heavily populated save. Equipped markers and selected-state borders should remain distinguishable in brighter and darker backgrounds.

Move quickslots/Hoods/Roach and dye/drop targets into a compact **on-demand auxiliary inventory section or distinct footer zone**, invoked through existing Tab / LS focus logic. Do not place them against the Geralt model or make them disappear from keyboard/gamepad/mouse access. Preserve slot indices, equipment actions, drag/drop hit areas and all 20 native slots.

Ensure layout state reacts to the **actual category**. In Alchemy/Crafting and other non-Gear tabs, no "GEAR" label; no hardcoded Gear details position producing unaccounted blank regions. Dynamic collapse/expand of item groups and content-aware stats/description display should be tested rather than presumed. Keep one Inventory screen with in-screen categories, not separate main-menu routes.

Make one targeted v2 revision against v1's now-grounded movie/ActionScript paths, inspect actual movie dimensions and owner. **No blind reshuffle or broad new art assets**. Test source and compiled contracts, and check in-game: early-game sparse grid, large inventory scrolling, category switching/title, detail visibility, Geralt unobstructed, native item actions, equip and comparison, dye, quickslots, Roach, controller+keyboard and 0.8.6 D-pad behavior. These remain **unverified functional behaviors** unless directly observed; static v1 tests are not proof.

Do not edit or redeploy accepted HUD v4/RC2, live profile, merges or saves automatically. Preserve original v1 private archive and rollback.

## Open question for user

This document records an assistant design assessment; it does **not** assume the user accepts the current layout or all proposed v2 changes. User may decide whether quickslots should be permanently visible in a separate clean region or on demand. A reversible one-pass proposal can default to on-demand without losing accessibility.
