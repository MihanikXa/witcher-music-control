# Adaptive Inventory P2 — coherent composition and interaction contract

**18 October 2026 · design/specification only · branch \`ui-overhaul\`.**
P1 is explicitly rejected by the user. This is a **proposed implementable next design**, not an accepted screenshot, proven live rendering contract or permission to deploy. The next implementation must obtain in-game approval before expanding to Usables/Satchel or additional third-party QoL mods.

## 0. Authority, evidence and design decisions

### Explicit user preferences and observations

- Reject the first Gear-grid v1's small/dotted grid, foot-level utility slots, oversized static details, redundant information and intrusive footer (see \`research/ink-gear-grid-v1-user-feedback.md\`).
- Keep the accepted **Ink & Iron 0.8.7 Menus v4**, Gentium/QuietFolio typography, item artwork, shared slim navigation and HUD v4/RC2.
- P1 screenshot was rejected: “No idea the fuck this is.” The user further explicitly agreed to the prior analysis and said:
  > And 6. background is a mess too, it assumes the existence of previous slots around geralt. And also doesn't seem very adaptive to controller/keyboard.
- User had approved the direction of a large, undotted item-first grid, larger **unobstructed** Geralt, contextual decision-oriented comparison, one screen, less routine material administration, and minimal context/device-sensitive controls.
- The user has **not** approved the precise P2 column ratios, tile sizes, navigation bindings or a replacement background asset. These below are design proposals requiring a runtime visual test.

### Source observations from the currently committed P1

| Surface and candidate owner | Exact evidence | Known/pending |
|---|---|---|
| Shared global top navigation | Menus v4 \`MenuCommon\` / its \`TopBarNew\` and artwork are deliberately retained; P1 screenshot shows the expected slender global row. | **Frozen**, do not edit shared global menu resource. |
| Native Inventory section/category heading and giant icons | P1 screenshot visibly shows \`EQUIPMENT\`, gears, armor/swords icons near/in the shared header. \`InventoryTabbedListModule\` and \`MenuInventory\` exist in Inventory movie. | **Actual child clip/object ownership and event handlers not established publicly**; decompile \`panel_inventory.redswf\` and trace runtime display list before hiding/relocating. Do not assume they belong to common header. |
| Inventory-specific background and decorative slot orbit | P1's \`qfAdaptiveRefresh\` hides \`iaiBg\`, \`iaiHeadSp\` and \`iaiHint\`, but **does not hide \`iaiArtHost\`**. \`ModulePaperdoll.qfGearReflow\` hides \`iaiDeco\`, \`iaiHorse\` and segment borders. Screenshot still shows faint sword/armor/bottle silhouettes where old orbit belonged. | Strong evidence of **unowned surviving art layers**; exactly which visual is \`iaiArtHost\` vs cached texture vs another clip is **unverified**. Enumerate every visible descendant and \`inkart:\` resource in private local build before removing. |
| Native items, layout and equipped marker | \`mcPlayerInventory\` -> \`InventoryTabbedListModule\` -> \`SlotsListGrid\`, \`SlotBase\`. P1 changes scale to 1.4 and viewport to 384, but retains native \`WEAPONS\`/\`ARMOR\` sections. Item count is sparse on shown level-1 save. | Scaling nine columns is **not** a unified adaptive layout. Real item IDs, ownership, filters, focus, equipped marker, tall-item footprints must remain native and functional. |
| Geralt renderer | \`mcCharacterRenderer\` and \`_rendererController.setDefaultAnchor\`; P1 places x=1060 and +12% from original. | Rendered full body in the screenshot; placement relative to the browse and summary region is disconnected. Original anchor/scale must be snapshotted and restored in other states. |
| Contextual summary | \`qfAdaptiveSummary\` is a new Sprite at (72,816), six TextFields; data comes from \`ContextInfoManager.getInstanse().iaiDockedTip()\` only when \`!isHidden()\`, then \`TooltipInventory.qfAdaptiveSummary()\` reads \`_data\`. | Blank on screen despite selected sword. **Do not assume** reason; trace selection event, tooltip instance/source, \`_data\`, visibility and formatting. Need a selected-item-based data contract that does not require a **visible** tooltip. |
| Existing input-feedback owner | Menus v4 \`MenuCommon\` owns its \`mcInpuFeedback\` subtree and footer formatting; P1 retains the native command hints. | Confirm method/interface for state-specific prompt changes on actual 5.01 movie; **no whole new footer**. |
| Added P1 input layer | \`qfAdaptiveButton\` constructs two permanent 270×38 button sprites at y=992 with hardcoded combined \`I / View\` and \`Tab / LS\`, alongside existing native hints. \`qfAdaptiveInput\` intercepts View/Select, I, Tab, LS, Esc/B through InputDelegate. | Evidenced duplicated mixed-device prompts. Actual key ownership/collisions, most recent-device API, hold/release routing and keyboard-to-controller transitions still require runtime test. |
| Native equipment targets and special features | \`ModulePaperdoll\` holds 20 native slots; Hoods \`SlotPaperdoll.canDrop\` and \`ItemDataStub.isDyeable\` retained byte/source-exact in P1; \`inkGearGrid.ws\` adds true equipped gear to grid. | Preserve all 20 native targets for drag/drop, Roach, crossbow, quickslot, Hoods dye, even if not displayed in browsing mode. |
| External mods and game states | P1 is player Gear category (4) gated and restores other native categories/shop/stash/horse. Sort Everything, Recent Loot and Junk Not Treasure were audited, **not installed**. | Keep current 5.01 merged scripts/FriendlyHUD/AutoLoot/RC2. No third-party integration in P2 structural proof. |

This table is an **ownership audit starting point**, not a claim that every display child has already been isolated. The compiled accepted movie, FFDec export and the running scene are the final sources for unknown owners.

## 1. Coherent first screen: one content plane, not two overlapping menus

### Single hierarchy

1. **Shared global navigation:** accepted MenuCommon row at the top, no Inventory-owned content overlapping it.
2. **One quiet in-Inventory category/action row below the global header:** initially a single active **Gear** context and existing native categories accessible through a compact, keyboard/controller-reachable control. No huge EQUIPMENT banner + native icon cluster in the header. The long-term Gear/Usables/Satchel grouping is a design layer over native categories, **not** fake data models or redundant top-level screens.
3. **Primary content plane:** one contiguous browse collection occupying the visually dominant left/main area, **not** separately anchored WEAPONS and ARMOR islands. Preserve native item grouping and sort/filter semantics as metadata; if their renderer creates disconnected islands, provide a source-verified reflow of real slot renderers rather than merely scaling the grouped parent. A lightweight subgroup divider is allowed when useful, never an entire fixed column with little data.
4. **Selected item information:** a restrained, always-operational **two-to-three-line summary integrated with the browse plane**: name, primary item-versus-equipped change, one contextual tradeoff/requirement if relevant. Do not expose a blank info plane when there is a selection; when the native comparison legitimately has no data, omit only the unsupported numbers and retain item name/actions. Full native tooltip/stat card opens on demand, over **the same content region**, without moving Geralt or selection.
5. **Geralt preview:** a clean, slightly prominent character within an intentionally composed neighboring region, visually anchored to the browse plane through alignment and shared negative space; no decorative equipment orbit, no unrelated controls at his feet.
6. **One quiet footer/input owner** showing the valid actions for the **current mode and active device**. Do not draw an additional row of fixed big buttons.

### Schematic only — not a replacement screenshot

\`\`\`text
┌────────────────────────────────────────────────────────────────────┐
│  ACCEPTED INK & IRON GLOBAL NAVIGATION (unchanged)                 │
├────────────────────────────────────────────────────────────────────┤
│  Gear   ·   native categories/filter/sort (one compact row)        │
│                                                                    │
│  ┌──────────────────────────────────────┐  ┌────────────────────┐ │
│  │                                      │  │                    │ │
│  │  SINGLE ITEM GALLERY                 │  │                    │ │
│  │  ▣ ▣ ▣ ▣     actual items only       │  │  GERALT            │ │
│  │  ▣ ▣ ▣ ▣     equipped marker         │  │  unoccluded        │ │
│  │                                      │  │                    │ │
│  │  Selected: name                      │  │                    │ │
│  │  +damage  | -socket | level req.     │  │                    │ │
│  └──────────────────────────────────────┘  └────────────────────┘ │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  ONE relevant set of hints, adapted to input device + mode         │
└────────────────────────────────────────────────────────────────────┘
\`\`\`

In real builds: no hardcoded \`Selected:\` placeholder, fake stat values or artificial duplicate items. There should be **one selection, one focus, one displayed equipped marker**, and no separate footer button surfaces.

### Geometry and responsive sizing (proposed, must measure native bounds)

- Use **measured native stage bounds, accepted common-header safe area and actual UI scaling**, not P1's fixed y=100/816/992 assumptions. Reserve a header band, a content rectangle and a footer safe band so rendered objects never overlap.
- Tentative **content-width ratio:** approximately 60–64% contiguous browse+inline summary, 30–34% Geralt, remainder gutter. These are adjustable starting proportions, not authoritative pixel coordinates.
- Grid cell size is governed by **available width, real item count, item aspect/tall footprints and minimum readable/icon sizes**. Do not fill empty tiles or stretch existing bitmaps to occupy space. Start with a compact well-proportioned **3–4-column gallery for a 6-item save**, and **5–7 columns** for dense equipment only if input/focus and item texture scale remain readable; refine based on rendered evidence.
- A sparse save should have **a deliberate, vertically balanced gallery plus contextual summary**; it must not collapse items to a tiny corner or float thousands of empty wells. A dense save should gain capacity and native scrolling without rearranging Geralt/footer every time the selected item changes.
- Choose density **when category/filter/content count or safe-area size changes**, not on every selection. Layout is stable during navigation/equip, with identity/scroll preservation and no animated shifting to the pointer.
- At 1649×928 capture (P1 screenshot), equivalent game virtual bounds must be measured, not inferred from pixels. Validate both 1080p and 4K, display scaling and narrower aspect ratios; no global scaling factor without bounding masks, scroll page, hit targets and rendering.

## 2. Inventory-only background artwork specification

**The user explicitly rejects the old-slot-dependent background.** The previous faint armor/sword/bottle ornaments were created for Geralt surrounded by equipment targets, not for the new browse–preview composition.

- Inventory Gear normal browse should use **quiet charcoal/ink negative space with at most a low-prominence regionally appropriate wash/texture**, never the silhouettes of vanished equipment orbit slots. Do not solve by alpha/HDR adjustment.
- Before modifying: dump the **actual Inventory movie display list** (\`iaiArtHost\`, \`iaiBg\`, \`iaiDeco\`, \`iaiHorse\`, slot segment art and any remaining original decorative clips), their parent coordinate spaces, visibility and resource/texture keys. Differentiate \`MenuCommon\` shared \`inkart:\` art from the Inventory-owned layers.
- Remove/hide/recompose only the **Inventory-specific obsolete layers in Gear mode**, with state snapshot/restore. If the offending image is sourced via a shared art cache, preserve that cache and suppress its **Inventory invocation/host only**, rather than changing the texture globally. Preserve accepted shared background art on Alchemy, Glossary, Character, Map, etc.
- If nothing tasteful can be derived from existing art without old-slot assumptions, **use simple dark canvas rather than invented decorative ornamentation**. Any world-visible transparency requires proving the game scene actually renders beneath Inventory in the user’s setup; otherwise no pretend glass effect.
- In inspect/auxiliary states, remain compositionally consistent; old art should not flash during mode transitions or focus updates.

## 3. Unified state and input contract

### UI states and return semantics

| State | Visible and focusable | Actions | Return |
|---|---|---|---|
| **Browse** (default player Gear) | gallery, selected summary, Geralt; quiet one-row categories + one native-derived footer | D-pad/arrows/wheel navigate; primary equip/unequip via native method; one explicit Inspect action; advanced equipment targeting **only on demand** | Leaving category/menu restores native/other-state UI, no leaked overlays |
| **Inspect** | same screen and Geralt; full original detail/compare content occupies browse region | Scroll long data, optional native compare control; no accidental equip/sort while scrolling | B/Esc/Back or Inspect returns to **same item ID and scroll page** |
| **Auxiliary equipment / target** | browse area temporarily hosts compact, navigable native equipment targets, without legacy slot background and without covering Geralt | Hoods dye, quickslots, crossbow/bolts, Roach, native drag/drop; ordinary weapon equip should **not** require this detour | B/Esc/Back restores gallery selection and previous subview; native cancel respected |
| **Native drag/selection** | Existing native target contract and feedback take precedence; only overlay visuals may be adapted | Native input/cancel/targets; no new global interception | Native state clears correctly; return to Browse |
| **Other inventory contexts** | Other native player categories, stash, shop, horse | Remain existing v4 until separately designed and tested | Full restoration of transforms, masks, focus, listeners, art and footer |
| **Keyboard ↔ controller transition** (orthogonal, not a new page) | Existing focus and selection remain; **only prompt language/glyphs and pointer affordance** update | Detect current input source using verified game-native APIs/events; mouse hover focus must not steal controller selection when pointer is stationary | No duplicate hints, no lost focus, no key-up ghost events |

Device switching must work inside Browse, Inspect and Auxiliary without exiting the menu. The actual current device detection source and accepted glyph API must be identified from **current MenuCommon/InputFeedback**; do not invent event names or hardcode static labels. Native gamepad prompts use the working v4 button art and actual button symbols, not text like \`I / View\` rendered for both devices. Keyboard mode uses currently bound actions; no permanent gamepad glyph row. Controller/gamepad glyphs should not claim remapping they cannot observe.

### One input-feedback owner

- **Prefer the existing \`MenuCommon.mcInpuFeedback\` provider**. Inventory reports its state/action availability to that feedback contract. If the current provider is not safely controllable, isolate it and design **one** Inventory-only row; hide the other feedback renderer *only in Inventory Gear mode*, retaining any required input listeners. No independent P1 \`qfAdaptiveButton\` strip.
- Mouse actions should appear as restrained context affordances (hover/click on real targets), not giant permanent buttons; action discoverability is addressed by tooltips/active hints, not footer duplication.
- Map each action by **semantic command**, then attach keyboard/gamepad/mouse bindings through verified existing game data. Proposed actions: Navigate/Select, Equip or Unequip, Inspect, Compare, Auxiliary/Target, Sort/Filter, Back. Exact physical keys **must be audited** against native sort, MenuCommon, FriendlyHUD/OW and RC2 before adoption.
- Separate actual **input dispatch** from **prompt rendering**. Switching device repaints hints only; it does not change or reset menu state.
- Debounce controller directional down/hold/up as proved in P1, with no input capture while native modal/drag/sorting takes precedence. Never double-dispatch a key to both native and custom handlers.

## 4. Data and visual contract for contextual summary

The blank P1 summary is a **blocking defect**. Show working real data before investing in additional category redesign.

- Single **selected item identity** from the active gallery renderer/native ID is the truth. Do not derive “selected” from hover-only tooltip display state.
- On identity change, native item update, equip/re-equip, category change: refresh summary **from an authoritative data provider** (likely existing SlotBase/ContextInfoManager/TooltipInventory payload, to be tested). If the native tooltip is hidden deliberately, **that must not invalidate the summary**. Trace creation/update of \`_data\` and \`equippedItemData\`; test tooltip-disabled settings and mouse/controller selection.
- Display **item name and one primary stat/value** when available, plus an explicit true comparison if supported. Only display genuine changes; no fabricated “best” rank. Include unmet level requirement/socket tradeoff only when meaningful and actually supplied.
- When no comparison exists, show the selected item name and relevant action, **not a blank band** or invented \`+0\`.
- Use a compact summary (2–3 optical lines) integrated within the main gallery plane. Reserve full tooltip prose/set stats for Inspect. Ensure selected item's name, contents and colors use accepted Gentium v4 styles.
- Avoid repeated per-frame rebuilding of paperdoll/tooltip TextFields. Use **dirty-state updates** for selected ID, data/equipment changes, mode, layout and device. Retain source-of-truth and stable field instances; proof must show item events actually fire.

## 5. Technical implementation decomposition and stop gates

### Gate A — cheap ownership and layout proof (before a full cook)

1. Read exact accepted v4 \`panel_inventory.redswf\`/private release and installed ownership. Reproduce P1 as the negative baseline but **do not use its movie as the new source**.
2. Export and enumerate **display-list children & art layers** for Inventory (including \`iaiArtHost\`, secondary headers and native \`MenuCommon\` boundary), with source class, local/global bounds, visibility and events. Record what survives in Gear.
3. Trace actual tooltip/selected data lifecycle, feedback owner and device detection. For unverified providers, document the missing evidence rather than silently inventing APIs.
4. Produce **two scene geometry checks** for the actual six-item early save and a larger fixture. Plot/tally real slot positions, native hit bounds, label positions, text bounds, art bounds and protected header/footer collision boxes using private inspection scripts/exports. Textual contract and private debug overlays are fine; no need to create a decorative mockup.
5. Present one stable composition that uses the measured safe area. If item reflow or summary data are impossible to prove from source, **stop** and report exact blocker instead of a fake playable package.

### Gate B — one narrow structural first-playable proof

1. Start from **accepted Menus v4**; modify only \`panel_inventory.redswf\` with targeted original code. Keep native script annotation only for already verified equipped-in-grid behavior.
2. **Suppress obsolete Inventory artwork** and duplicate native secondary header/feedback visually, preserving their needed listeners/data until equivalent navigation is wired.
3. Draw one actual continuous Gallery and properly framed Geralt; size responsively for sparse/dense; preserve grid native renderer IDs, drag and action contracts and equipped corner marks.
4. **Wire and demonstrate real selected-item summary** without hidden-tooltip dependency. If summary can't populate, this gate fails.
5. Connect to **one** context-sensitive hint owner; test device switches. No permanent double-labelled mouse/button hints or additional footer.
6. Native build/test candidate must be private and fully rollbackable. Stop after **one** in-game image + short keyboard/controller functional smoke test, rather than immediately adding Usables/Satchel/sorting/Review/cleanup.

### Gate C — only after P2 structural acceptance

- Full Equip/Unequip with selected-ID/scroll restoration, Inspect, native Auxiliary/Hoods/quickslots/Roach, shop/stash restore, advanced long text.
- Then adaptive Usables and Satchel rendering, optional Sort Everything subset.
- Then real acquisition-driven Review (Recent Loot model) and carefully isolated marked/bulk merchant cleanup (Junk Not Treasure model). No new runtime third-party mod required for Gate B.

### Required validation (do not equate native pass with UI acceptance)

- **Geometry** at 1649×928 observed capture, 1920×1080, 3840×2160 at tested UI scaling; no overlay in global header/footer, row/slot bounds and scrollbar consistent; sparse vs populated inventory.
- **Asset**: no inherited slot-orbit background shapes in Gear, no edits to shared common/art cache or other menus.
- **Selection**: real item ID throughout focus/equip/Inspect/Back, stable after refresh, native action enabled/disabled logic intact, no multi-item ghost focus.
- **Prompts**: clean footer in gamepad mode, keyboard-only hint mode, seamless device transition, no duplicated control sets, no broken pause/back/tab semantics.
- **Data**: selected item summary visible when tooltip itself hidden; correct equivalent-item comparison and graceful no-data fallback; no gameplay value fabrication.
- **Native actions**: Gear, Hoods dye, Roach, quickslots, long tooltip, sorting, mouse drag, shop/stash/horse alternate modes.
- **Safety**: 0.8.7 Menus v4, icon art, Gentium, Bestiary/Map, accepted HUD RC2, SAHUD/FHUD/OW/Smooth Map, Vortex/merged scripts unchanged; one-mod rollback. Source differences, offline/runtime outcomes and Native 5.01 validation reported separately.
- **Quality gate:** P2 is rejected unless its screenshot shows **all five**: single top hierarchy, primary item gallery, real selected summary, no obsolete orbit background, and one legible device-appropriate footer.

## 6. Files, ownership and preservation rules

This is the design specification for Codex, **not a request to install a new mod now**. No automatic Vortex deployment, input configuration changes, merged-script rebuild, save writes or bundled copyrighted upstream movie assets. Keep P1/v1 in their existing ignored private deploy directories for functional comparison, not as the visual template.

Primary sources: \`research/adaptive-inventory-v2-p1-runtime-rejection.md\`, \`research/adaptive-inventory-v2-gear-p1.md\`, \`research/menus087-v4-typography-finishing.md\`, \`src/inventory/adaptive/AdaptiveMenu.asinc\`, \`src/inventory/GearPaperdoll.asinc\`, \`tools/patch-adaptive-inventory.py\`, \`design/inventory-ux-direction.md\`, \`design/adaptive-inventory-build-plan.md\`.

**Status:** coherent proposed visual/interaction contract, backed by public repo code and user-reported P1 screenshot failure. Exact asset ancestry, native device events, tooltip data routing and layout stage extents still require the locally available private v4 movie and an in-game smoke test before implementation can be declared accepted.
