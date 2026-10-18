# Approved Inventory — source-to-interface implementation map

**18 October 2026 | Design-to-source planning deliverable, not a build or an in-game validation.**

## 1. Authority, exact visual reference, boundaries

The user **approved the generated concept screenshot** (conversation upload `image(20261018-163558).png`, 1672 × 941, source SHA-256 `9e7d6bdb0bad0d28b5bacfc02e8433dac177b34690303acee8af6cd03b235ac9`) and explicitly **rejected** changes to Geralt scale, details typography/hierarchy, category spacing and footer, except that equipped gear should retain **the already accepted small notch/stripe**. The user also approved an attention-filtered **Review** category as the **first** category. See `design/inventory-reference-accepted-review.md`. All P1/P2 visual layouts are rejected; their source may be inspected only as technical/negative evidence.

**Codex must have the exact screenshot locally:** put the unchanged image at **`C:\Dev\witcher-ui-overhaul\reference\inventory-design\approved-inventory-reference.png`**. This is a private, ignored reference asset, **not** a GitHub-delivered image or a license to copy fabricated mockup item stats. Verify its SHA-256 before visual work; ask the user for the file if absent. The image is available for the user to download from this conversation, but no Windows checkout transfer has been performed.

The reference shows a distinct **category rail → compact item list → selected-item details → Geralt** structure, with one slim top nav and a restrained footer. All are visible at once. Unlike earlier assistant speculation, **the approved image intentionally has a persistent full details panel**. Do not compress it into a two-line summary or turn it into a popover just because a prior assistant preferred that. The user chose this explicit composition.

### Image-bound visual geometry (orientation only, not engine pixel constants)

Image is 1672 × 941; the following are approximate reference *visual bands*, not measured SWF coordinates: shared top navigation about y=0–90; category rail around x=45–293; adjacent item list around x=314–620; details start near x=653 and occupy the central mid region; Geralt occupies roughly x=1130–1460 with substantial top/bottom breathing room; footer controls near y=845–905. At runtime, derive a single panel coordinate transform from the accepted authored 1920 × 1080 game stage, letterboxing, UI scale and actual 3D model anchor. **Do not independently alter these proportions because a proposed redesign sounds cleaner.** Use normalized positions from the actual screenshot and adjust only for real clipping/device scale.

### Visual identity to preserve

The accepted Ink & Iron slim common menu, Gentium menu typography, item artwork, neutral charcoal/ink background treatment, restrained gold selection, and game controller icons. In particular the image's scenic dark ambience is a **visual objective** but *not proof* that the game renders a 3D scene behind the menu. Trace the existing Inventory background pipeline and choose a legal, source-supported game art/scene treatment. Do not reintroduce old equipment-orbit art or create a green-black opaque `0x0C0E0C` rectangle. If the scenic backdrop cannot be realized without a major renderer/asset change, report the exact limitation and offer a bounded authentic game asset variant **for user approval**; do not invent visual substitutions.

## 2. Visual region → actual technical owners

The following is derived from the repository's accepted Menus v4 and the P2 native ownership/source audits; exact live children and selected marker asset **still need confirmation in the local decompiled v4 SWF**. Do not present this table as a live trace.

| Approved region | Current native owner / evidence | Preserve | Required new display work | Risk / verification |
|---|---|---|---|---|
| Slim global nav, level, weight | `panel_common.redswf`: `MenuCommon`, `TopBarNew` | Entire accepted v4 movie, formatting, hit actions | **None** | Inventory-only child must not cover common nav |
| Left vertical categories, Review first | `InventoryTabbedListModule.mcTabList`, `mcTabListItem1..6`, `txtTitle`; real tab selection in `onTabListItemSelected`; `CR4InventoryMenu` tab filters | Native filters, tab actions, new flags, sort state and other inventory modes | One readable **vertical category rail** matching screenshot; virtual Review filter at top, then map shown groups (Weapons, Armor, Consumables, Bombs, Pockets, Quest Items, Other) to **actual** player inventory tags/categories | Native groups do not necessarily match mockup 1:1. Audit underlying tags and InventoryTab data; do not create a category that silently loses oils, mutagens, alchemy, diagrams, Roach items, quest items or books |
| Compact text-and-icon one-column item list | Native `mcPlayerInventory` → `InventoryTabbedListModule` → `mcPlayerGrid` / `SlotsListGrid`, `SlotInventoryGrid`, `SlotBase`; native ItemDataStub and per-item `id` | Authoritative IDs, native sort, state changes, selection, equip/unequip/drag, focus, existing item textures | **New item-row presentation and vertical scrolling/navigation**, using actual item icon, name/subtitle and selected line. A row is **not** an enlarged cell; avoid repainting rows every tick | Row renderer/hitbox and data-to-native-slot adapter must be source-designed; verify tall-item native footprint, density, mouse/keyboard/pad focus and long translated strings. A visual row must map 1:1 to an actual actionable native item ID |
| Equipped notch/stripe | Native `isEquipped` field/slot rendering (likely `SlotBase` art pass; source exact location **unverified**); older adapter `src/inventory/inkGearGrid.ws` exposes equipped IDs, and `InventoryRemoveItem` / `execurePrimaryAction` preserve equip/unequip | **The exact approved native notch/stripe from the user's current working design**. No new badges, dot, checkmark or separate equipped list | Reuse same existing art/symbol/semantics inside a selected or unselected item row; do not redraw by approximation unless exact symbol transfer is technically impossible and separately approved | Confirm compiled **v4 / installed accepted** movie clip and conditions, distinguish native `isEquipped`, new flags and rarity. No double renderer of equipped gear |
| Selected-item details/stat/comparison | `ContextInfoManager.dataReceiver` via native `context.tooltip.data`; `OnGetItemData` uses real item ID; `TooltipInventory`, `TooltipStatRenderer`. P2 source proved usable real name/damage/delta in one runtime screenshot | Game values, semantic colors, real comparative `equippedItemData`, warnings/required level, sockets, description; Gentium | Persistent **middle details region exactly in the reference hierarchy**, using existing tooltip content appropriately projected into the intended format, with native scrolling for longer fields. No duplicate stat block below list | P2 selected-ID `p2Payloads` adapter can be researched, but **not its old compact summary UI**. Must not depend on visual tooltip currently being visible, fabricate numbers or assume all fields exist on every item type |
| Live Geralt preview | `MenuInventory.mcCharacterRenderer`, `_rendererController`, `mcCharacterModelAnchor` | Live model, updates, character interactions; existing accepted renderer and animations | Position and mask to **approved right-side proportions** without a slot orbit or list overlap | Native anchor transform and background ownership still require runtime calibration; no independent 10%/12% scaling assumptions |
| Native special equipment + drag/drop | `ModulePaperdoll.mcPaperDollSlot1..20` / `SlotPaperdoll`, official Hoods dye `canDrop`, Roach, crossbow/bolts, potions/quickslots | All action/target contracts even when not visual in the normal list | Provide an **on-demand native equipment target mode** or contextual action, preferably through appropriate categories (Pockets/Other) without altering default screenshot composition | Confirm all 20 targets can receive drag/drop and keyboard/controller focus; no targets rendered on Geralt legs |
| Inventory-specific background | `MenuInventory.iaiArtHost`, `iaiBg`, `ModulePaperdoll.iaiDeco/iaiHorse`; common `MenuCommon.inkBgArtHost` handles `inkart:inventory` | Other menus' art caches, accepted v4 shared backgrounds, real Geralt renderer | Present a **neutral, visually coherent source-grounded Inventory-specific background** matching approved reference; suppress only art that assumes old slot constellation | Trace layer ancestry/ownership; verify whether real game world can appear behind menu, otherwise use existing game visual assets with appropriate rights/packaging. No new global HDR changes |
| Footer and key/glyph hints | Shared `MenuCommon.mcInpuFeedback` → `ModuleInputFeedback` / `InputFeedbackButton`; real `KeyBindingData`. `InputManager.isGamepad/isMouse` + `ControllerChangeEvent` known from native audit | Accepted single footer renderer/button art; device-aware formatting and input actions | Keep the mockup's restrained placement; dynamically show correct device-specific bindings and relevant state actions using **one** feedback owner | P2's attempted `p2FindCommon(stage)` interception might fail at runtime; trace actual instance and update ownership. Do not hardcode `I / View` or add duplicate button bars |
| Sort and counts | `MenuInventory.btnSort`, `btnSortChange`, native sort modal, weight field in common | Native sorting, weight/capacity, real item counts | Map actions to screenshot's unobtrusive affordance; category counts reflect underlying filtered items | Native target sort field and category-specific grouping must still be truthful; no invented counts |

### Important code reuse boundaries

**Reusable functional evidence**, not visual source: `src/inventory/inkGearGrid.ws` (equipped ID inclusion and equip/unequip), existing Focus/D-pad debounce contracts, native `OnGetItemData` → `ContextInfoManager.dataReceiver` data projection demonstrated by P2, Hoods `isDyeable/canDrop`, and accepted v4 `TooltipInventory`. The scene should use stable retained display instances updated by item-ID/data revision rather than `cleanUpRenderers()` + re-creation on every equip/focus update.

**Rejected visual code**: `src/inventory/GearMenu.asinc`, `GearPaperdoll.asinc` layouts, `src/inventory/adaptive/AdaptiveMenu.asinc`, all P2 `Geometry.asinc`, `Gallery.asinc`, `Module.asinc` coordinates/packing, `Menu.asinc` opaque canvas, footer injection. Do not migrate those arrangements, even if they compiled.

## 3. Native inventory-category and input model (mandatory source audit)

The screenshot's rail displays **Weapons, Armor, Consumables, Bombs, Pockets, Quest Items, Other**, with **Review inserted first**. These are **presentation categories**, not necessarily game-native data classes. Before implementation, produce a row for every existing vanilla/I&I native Inventory tab/tag and subtype with: native game type/filter, where it appears in the approved rail, sorting, stock/equipped semantics, merchant/stash behavior and cross-mode state. Explicitly account for *steel/silver swords, chest/boots/gloves/trousers, ranged gear, bolts, oils, potions, decoctions, bombs, mutagens, crafting and alchemy resources, food, Roach gear, books, diagrams, quest objects and miscellaneous items*. **Nothing gets silently hidden.**

At any time there is **one currently selected item ID**, one currently selected category, one scroll offset per applicable category, one authoritative active input device, and one current interaction state. Suggested internal modes: **Browse** (rail, item list, details, Geralt), **Details/scroll** (same composition with focus in the middle), **Auxiliary/target** (temporary native equipment target controls), and **native modal/shop/stash** (restore accepted v4 behavior until tested). Switching categories retains contextual selection when valid; mouse movement does not steal gamepad focus when pointer is stationary. Controller/keyboard switch repaints prompts, not layout, selected ID, state or model.

Existing renderers are scaleform ActionScript and support many native callbacks. **Do not invent exact method names, category indices or remap-safe key codes**; get the actual compiled class and provider signatures on local Codex Windows before modifying them.

## 4. Build sequence and hard gates

**Gate 0 — immutable visual & baseline receipt (read-only).**
- Put verified screenshot in ignored reference path above; store path/hash in build receipt, do not embed in the released mod.
- Verify the effective **accepted v4** `panel_inventory.redswf` against release manifest (historically SHA `a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a`). Re-check actual live owner with `mods.settings` and Vortex. Disable rejected P1/P2 **only manually in a cloned profile**.
- Decompile/inspect exact current `SlotBase` equipped **notch/stripe** and its semantic state, plus native rail/category providers, item data row path, text-format aliases, Geralt anchor, background and footer. No native build until the reference and current owner are verified.
- Pin a **source ownership mapping** with actual class/function and display symbol; do not mistake old prototype methods for existing accepted v4 behavior.

**Gate 1 — static reference-faithful region proof (before expensive native cook).**
- Produce **a visual arrangement test** at 1672×941 screenshot aspect, 1920×1080 and 3840×2160, anchored to the screenshot's areas. Use real source item images at their actual in-game display scale, no forced 2× upscaling. Both six-item and populated data must preserve **the same rail/list/details/Geralt proportions**.
- Use an extracted screenshot composite or authored nonshipping UI test with **real reference-specific proportions**. Do not substitute a generic grid wireframe or include fabricated game attributes in shipping.
- Verify category rail size, item row height/icon quality, aligned details and character, footer readability and scrollbar; prevent region collisions and prevent transformed hit bounds from diverging from visuals.
- This is a **visual gate**: report a contact sheet or two screenshots to the user before implementation, without another uncontrolled P1/P2 binary.

**Gate 2 — functional row renderer and detail contract.**
- Against accepted v4 and no optional runtime QoL mods, implement the actual single-column item row renderer and rail; use native provider items and stable real ID mapping. Initially **one category with a selection**; no altered equipped/inventory game data.
- Implement correct native selection, equip/unequip, selected detail data (the **full reference-style panel**), single footer and model scene. Stable display objects, dirty-on-data updates, frame/visibility diagnostics for flicker.
- Preserve native model, item events, drag/drop, equipped notch, Hoods, and character interactions. Test input for mouse/keyboard/controller and modal states.
- Stop after **one private, rollbackable screenshot candidate**. Require user's visual acceptance of sparse case and a dense scrolling test. Avoid spending hours implementing all rail groups before proving quality.

**Gate 3 — completeness and category parity.**
- Add all rail categories with a documented exhaustive native-tag mapping, category-specific row subtitles and sort, persistent selection/scroll; support both equipment and consumables/materials/quest objects correctly.
- Route Pockets/Roach/Hoods/accessory/auxiliary equipment through native functions without restoring orbit background. Keep Shop/Stash/horse screens at native v4 behavior until separately verified.
- Ensure correct device-adaptive footer and full detail formatting/scrolling with no overlaps or wrong controls. No renderer disappearance or flashes during equip/sort/filter/category transitions.
- Finish after user accepts visual+functional cross-category results.

**Gate 4 — approved Review as FIRST rail category.**
- Implement the **separate saved acquisition-aware Review model** described in `design/inventory-review-behavior-contract.md`. Add its rail count, filtered item rows, data flow, inspect/dismiss and a no-spam policy.
- Integrate `Recent Loot Tab`'s **concept** of real acquisition-event capture only after exact annotation/provider collision review; do not install its overlapping movie wholesale. Ensure no duplicate records and no damage to accepted FriendlyHUD/AutoLoot behavior.
- Validate persistence and effects on actual save state in a disposable/cloned test save. No silent sale/dismantle/disappearance of base-category items.

**Gate 5 — separate QoL features after visual acceptance.**
- Evaluate `Sort Everything` subset and `Junk Not Treasure` protection/bulk flow after deterministic row/category behavior, with script-method collision checks. Do not introduce optional dependencies early just because their archives are available.

### Mandatory anti-repeat checks

- No native grid scaling to fill emptiness; item icon art stays crisp and stable regardless of inventory count.
- No native category topbar competing with accepted shared header; one left vertical rail.
- No background assumption of slots orbiting Geralt, and no invented green-black opaque canvas.
- No hidden-tooltip visibility gate suppressing selected details.
- No tearing down/recreating list renderers during routine selection or equip; instrument real state changes and **reject flashing**.
- No duplicate footer, static mixed controller+keyboard labels or focus-stealing device transitions.
- No altered active HUD/RC2, shared `panel_common`, accepted fonts/icon atlas, movies outside Inventory, Vortex or saves automatically.
- Native cook/validate/pack/metadata and offline tests are **necessary but insufficient**; screen captures and user acceptance are mandatory.

## 5. Next handoff and immediate deliverable

The next Codex run should be a **bounded Gate 0–1** exercise: establish current v4/native item-row interfaces, original approved notch and actual background/footer ownership, then produce **visually faithful sparse and populated layout proofs** grounded in the user's *exact* screenshot. Do **not** build a new large runtime release in that same speculative run. Once the visual proof is accepted, commission Gate 2's first single-category functional implementation.

This staged plan deliberately spends a short visual/source checkpoint before another long native cook, because both earlier P1 and P2 were technically validated but decisively failed user perception and stability.
