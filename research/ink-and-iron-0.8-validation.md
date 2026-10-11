# Focused test and rollback — Ink & Iron 0.8

User-run checks, after the installation gates in the
[integration report](ink-and-iron-0.8-integration.md). None were game-tested by
the agent. Record pass/fail, resolution, input device, current winners and a
capture/diagnostic for each failure. Compare to **Witcher Compatibility Test**
using the same location/save. English only; test at real 1080p and 4K viewing
distance, without treating downscaled screenshot text as a rendering defect.

| Surface | Focused check | Failure means |
|---|---|---|
| Startup | Start DX12 normally; no new script compile errors, blank startup text or missing modules; load a disposable existing test save | Roll back last module stage; don't regenerate merges |
| Gentium / aliases | Existing HUD remains Gentium; I&I titles/body/italic/bold resolve; names with accents, apostrophes, curly quotes, en/em dashes and ellipses display; long labels wrap/clip acceptably | Inspect actual fonts.xml + EN-library winner; keep IM Fell disabled |
| Inventory/equipment | Hoods movie remains owner; select/equip/unequip, sort/filter, compare, tooltip, quickslot assignments, Roach preview/reset and weight/crowns; experimental equipment-first stays off | Stop UI stage; inspect shared components and camera wrappers |
| Hoods | Existing keyboard/controller hood toggle works and hint remains; dye equipped hood/Quickslot2 through existing supported workflow; preserve color through toggle | Inventory replacement or annotation regression; retain Hoods owner |
| Shop/stash/loot | Buy/sell one disposable item; controller and mouse selected-item cards/comparison update for both inventories; stash retrieval, loot scrolling and close/back work | Check I&I tooltip fallback with retained inventory, not just movie owner |
| Outfit Wheel | Open/select/cancel/save/wear in gameplay, common menu and overlay; controller stick/release, keyboard, equipment availability/messages still work | Verify all three GOW movies retained and OW exports bind |
| Character/skills/stats | Navigate trees/mutations/equipped slots, spend no permanent point initially; inspect names, requirements and stats; keep all data; readability at distance | Record specific text problem for later scope; no redesign in this task |
| Quest journal | Switch/select/scroll, track a quest and return; long objectives and lore visible | Shared movie/script font/input regression |
| Alchemy/crafting | Recipe filters, ingredient names, craftability/missing ingredient and item tooltip; craft only disposable item after navigation succeeds | I&I annotations/data contract or focus regression |
| Glossary/bestiary | Characters, bestiary, books/tutorials, animated entries, scrolling and return; doppler BIA art remains deliberate exception | Texture owner or common background callback failure |
| Meditation | Clock/time navigation, accept/back, no clipping or missing title; no campaign overwrite | Alias/layout regression |
| Pause/main | Resume/reopen; each owned DLC main scene; mod.io submenu visible and scene returns after closing it | MainMenu/ingame combined wrapper or overlay conflict |
| Save/load UI | Browse/back first; only after other checks pass create and overwrite a separate disposable test slot; return and navigate with pad/keys | I&I OnInkSaveOverwrite/ForceSetIgnoreInput path; never test on campaign slot |
| Loading | Region title/panorama/medallion at several regional loads; no blank title or missing localization | Title alias, region movie or loading string failure |
| Gwent | Existing GDC selection/mod settings, vanilla deck builder and one disposable match: turn/score/pass/round/end and return; board/cards/faction symbols readable | Behavior conflict despite no detected same-key overlap; disable board only |
| Settings/mod menus | More than ten existing Mods entries remain accessible; scrolling, select/back and long names; all existing menus still present | Preserve Mod Settings Menu Fix and package04; XML registration issue |
| Map | Smooth Map pan/zoom/filter/region switching, correct button hints and bindings including holds; common hints return after closing map | Common-menu adapter/order failure; stop UI stage |
| Existing HUD | SAHUD hide/show/combat modes; FriendlyHUD visibility/markers/oneliners, quests, buffs, stats/minimap; no forced visibility | Do not enable any I&I HUD module; check shared root/library effects |
| NPC / trials | Accepted hostile/friendly/neutral/focus colors and NPC shadow; quest icon spacing; preserve deployed interaction/subtitle trial look/status | Resource or font regression; trial presence is not acceptance |
| Controller/navigation | Focus and LB/RB, A/B/X/Y prompts, mouse/pad switch, scroll, holds, accept/cancel and return across tested menus | Priorities do not prove contracts; preserve captures and exact state |
| Movement/combat | Analog Walk/Jog thresholds, held sprint/release, left-stick behavior and keyboard gait match original; basic weapon/unarmed combat and parry unchanged | Stop clone trial; confirm package04/core/controls unchanged |

For a later optional HUD cosmetic test, audit and package one movie/script pair
separately, obtain approval and give it an independent rollback. This checklist
does not authorize that expansion. Interaction V2 and Subtitle Shadow V1 remain
private trials, even though current settings show their folders enabled.

## Rollback

Close the game. For a single independent cosmetic stage, disable only the newly
enabled I&I module and redeploy the clone. For the UI stage, disable I&I UI and
its new compatibility adapter together. Keep Vanilla Fonts while other active
I&I modules require the aliases. For a font-only rollback with those dependents
disabled, disable I&I Fonts; leave QuietFolio enabled throughout.

For complete rollback, select **Witcher Compatibility Test**, redeploy and verify
the original resource owners/order, menus, Gentium, NPC effects, movement and
combat. Confirm I&I folders/resources and new menu registrations are no longer
deployed, without manually deleting managed hardlinks. Restore only settings
entries actually changed during the approved test from the recorded backup;
Vortex profile switching does not guarantee every Documents setting is restored.
Keep both trial archives and accepted packages. Never re-enable Over 9000.

If Vortex presents external-change prompts or a retained owner/hash differs from
the snapshot, inspect that precise difference before proceeding. Do not purge,
reset complete settings, regenerate merges or overwrite saves. Keep the original
working profile and independently preserved package04/archive as the reference.
