# Ink & Iron visual-first integration — current design authority

**Decision date:** 11 October 2026, after the completed 0.8 compatibility audit.  
**Status:** User-approved *design direction*, not an installed/compiled compatibility solution or authorization to alter the live game.  
**Supersedes:** The **retained-resource-owner policy** and reduced-visual-coverage *target* in [the 0.8 integration audit](../research/ink-and-iron-0.8-integration.md) and [older selective scope](ink-and-iron-scope.md). Those remain valid **technical evidence of conflicts** and a reversible *interim* fallback, not the desired finished UI.

**Latest 16 October version correction:** New **0.8.7** update is in the local reference folder, but the currently customized menu UI was **based on 0.8.0**; rebase current UI work and selected 0.8.6/Hoods improvements onto 0.8.7 **without removing any accepted prior changes**. Follow [migration handoff](../research/ink-and-iron-0.8.7-menus-migration.md). The next phase is still shared/menu integration **before Inventory v2**. The installed custom HUD v4/RC2 stays frozen. Audit 0.8.7's HUD/Buttons for useful new fixes/options and port only justified improvements into a **separate** rollbackable candidate after contract tests; never wholesale overwrite RC2.

**Earlier 16 October user sequencing update:** Before continuing Inventory v2, first establish an **Ink & Iron 0.8.6 shared/main menu baseline** with functional compatibility and the accepted HUD v4/RC2 frozen; see [latest direct user feedback](../research/ink-gear-grid-v1-user-feedback.md). The user specifically finds the old v1 top too busy and expects the full I&I menu style to improve it. Do not mistake the single movie adapted by Gear-grid v1 for comprehensive I&I menu integration. Then design a cleaner, more dominant, less dotted Inventory with larger Geralt, condensed context-sensitive descriptions/commands and an investigated translucent backdrop. The historical phase numbering below is retained as scope context, **not authoritative task order**.

**17 October user typography correction:** Preserve QuietFolio/Gentium *font faces*, NOT old menu text colors, sizes, alignment or typography hierarchy. Recreate the preferred Ink & Iron presentation using adjusted Gentium metrics, rather than defaulting to the prior font layout. Distinguish the users' exact preference from proposed optical implementation. See [latest screenshot + font follow-up](../research/menus087-runtime-visual-feedback.md).

## Explicit preference correction

The user wants more of Ink & Iron's actual visual appearance than the first integration plan retained, **including its gameplay HUD**. They value Seamless Adaptive HUD and FriendlyHUD chiefly for adaptive reveal/hide, navigation, contextual functionality and UX, **not for a requirement to retain their original visual assets**. Likewise, Hoods, Outfit Wheel and Smooth Map are eligible for targeted UI restyling or compatible resource reconstruction if their presentation conflicts with the preferred Ink & Iron style. Preserve useful behavior rather than insisting the existing resource folder/movie always wins.

**New 15 October compatibility evidence:** The official Ink & Iron 0.8.3 optional Hoods Compatibility patch explicitly restores Hoods dye handling on its Inventory. Start Inventory design against current I&I UI plus that patch, with a short read-only effective-owner/functional check; do not plan a fresh Hoods merge without demonstrated missing behavior. See [updated inventory direction](inventory-ux-direction.md).

The inventory is the major deliberate aesthetic exception: **do not preserve Ink & Iron's circular equipment constellation around Geralt.** The target is still one inventory screen, with Geralt as a clean preview, coherent grid-based browsing, clearly marked equipped items, compact accessible categories for materials/junk, usable comparisons, and intact equipment/hood/quickslot/Roach actions. See [inventory UX](inventory-ux-direction.md). Merchants and related item-grid contexts may share redesigned patterns. Other Ink & Iron menus should largely retain their visuals and structure.

Keep already accepted Gentium/QuietFolio, NPC Colors v4, NPC Shadow v1 and working movement fixes by **behavior/quality** wherever practical. Interactions v2 and Subtitle Shadow v1 have private trial status; do not present them as fully accepted without user confirmation. If a custom Ink & Iron treatment meets a preference better than an older accepted visual asset, compare the visible result rather than enforcing the older look dogmatically; do not discard accepted code or packages without consent.

## Key architectural distinction

**Appearance owner != behavior owner.** A single compiled `.redswf` movie may mix drawing, ActionScript exports, hit areas, focus and game interactions. Therefore it is **not** automatically possible to run Ink & Iron's visual movie and the old mod's logic by choosing load order. We must map visual states and functional contracts and determine for each conflicting resource whether to:

1. **Use the unchanged Ink & Iron resource** when no relevant behavioral contract is lost.
2. **Configure a native option** in an existing HUD mod when it already supports the desired style and show/hide semantics.
3. **Write an original narrowly scoped adapter/annotation** when the conflict is solely script-side and runtime ordering is testable.
4. **Create a combined resource** using an authorized I&I derivative, or independently implement a similar appearance against the modded/native runtime movie with all necessary exports and state logic retained.
5. **Redesign the conflicting mod's visible elements** (e.g. Outfit Wheel buttons or Hoods cues) to coordinate with the chosen Ink & Iron style, rather than dropping the function or accepting inconsistent visuals.
6. **Leave a documented temporary exception** only while a harder compatibility feature is unresolved; never mistake the interim appearance for the finished target.

Mod ownership priorities and same-path deploy conflict rules **cannot** merge UI movies. Avoid wholesale merging all HUD movies: first identify the minimal state/visual contracts and mod-specific features that actually overlap.

## New target decisions by system

| System | Desired appearance | Behavior/compatibility requirements | Work tier |
|---|---|---|---|
| Main menus, character, quests, alchemy, glossary, meditation, loading, etc. | Ink & Iron 0.8 as shipped, refinements only if necessary | Preserve keyboard/pad navigation, mod menus, lore and interactive functions | Low unless conflicts |
| Overall gameplay HUD | **Ink & Iron as visual model, not vanilla/SAHUD skin as default** | Preserve SAHUD context-driven module show/hide, FriendlyHUD navigation/markers, buffs, quest state, dialogue/oneliners, combat readability | High; movie and script audit required |
| NPC labels / enemy/boss UI | Integrate Ink & Iron styling with accepted restrained semantic colors and subdued outline | Preserve accepted name color categories, NPC Shadow v1 behavior and FriendlyHUD target information/quest icons | High; existing accepted baseline, careful conflicts |
| Inventory/equipment | **Custom inventory-first one-screen redesign in Ink & Iron visual language** | Hoods dye/toggle, item selection, equip/unequip, quickslots, crafting data, Roach items, player character preview | High; full architecture/layout and input contracts |
| Shops, stash, loot | Reuse successful inventory-grid grammar only where needed | Purchases, comparisons, sorting, transfers, item counts and tooltips | Medium–high |
| Outfit Wheel and shared common/overlay | Ink & Iron-compatible background/controls/glyph styling; not required to preserve current visuals | Retain OW exports, menu transitions, wheel controls/status; solve `inkart:` background protocol | Medium–high |
| Smooth Map / worldmap | Prefer I&I map styling if user prefers tested appearance; keep useful Smooth Map behavior | Routes, hints, map zoom/filter, region selection; do not hide `mcInpuFeedback` without replacement | Medium–high |
| Font aliases / typographic treatment | QuietFolio Gentium where it still meets the user's preference, with I&I Vanilla Fonts aliases | 0.8 alias/library static compatibility already supported; verify actual wrapping | Low to medium |
| Gwent, icons, bestiary, loading, dialogue | Mostly I&I unchanged | GDC, BIA texture corrections, controller glyphs and existing mod behaviors | Low to medium |

## Evidence from 0.8 audit — not a deployment certificate

- Canonical 0.8 extraction under `reference/ink-and-iron-0.8/`; 5,786 canonical resource rows, 94 annotations, with original input hashes and live mod priorities in `research/ink-and-iron-0.8-audit/`.
- Historical 0.8 audit conflict owners: Hoods `inventory/panel_inventory.redswf` (**superseded as an assumed blocker by official Ink & Iron Hoods Compatibility file added in 0.8.3; inspect current installed patch to determine the effective owner/dye behavior**); Outfit Wheel `common/panel_common.redswf`, `overlay/panel_overlay.redswf` and `hud/hud.redswf`; Smooth Map `worldmap/panel_worldmap.redswf`; SAHUD `hud/hud_wolfstatbars.redswf` etc.; accepted NPC/interaction resources `hud_enemyfocus`, `hud_interactions`; further overlaps should be enumerated per movie.
- Script-dependent `inkart:` background protocol and map hint alpha are real identified integration issues. The previously proposed small common-menu adapter is a plausible **first bridge**, not proof that the entire Ink & Iron visual design can be retained with Outfit Wheel/Smooth Map visual resources still winning.
- I&I **HUD was excluded for safety**, not because its visual design is undesirable. The new desired outcome **includes its style**. Do not enable it wholesale over SAHUD until state/menu/exports have been mapped and the combined design proved.
- I&I 0.8 Fonts (Vanilla) appears compatible with QuietFolio's English font definitions; only runtime validation establishes clipping/legibility.

## Bounded plan: move from functioning baseline to visual completeness

### Phase 0 — Preserve working state; classify the desired look

Use a cloned Vortex profile. Keep original compatibility profile plus accepted packages unchanged. Obtain **real screenshots from I&I 0.8** (reference screenshots are sufficient only for preliminary look, not proof of runtime fidelity). For HUD, identify *exactly* which I&I elements are preferred: bars, shapes, sizes, colors, map frame, combat indicators, tracking text, radial UI, etc. Don't assume all HUD movie replacements must follow wholesale.

Produce a per-movie table with: **I&I visual target, current functionality provider, ActionScript/symbol imports/exports, scripts depending on each, risk, integration technique, success checks**.

### Phase 1 — Early safe visual baseline

Validate original separate modular archives and the static Fonts (Vanilla)+QuietFolio pairing. Install only collision-checked independent I&I cosmetic/menu parts in an isolated clone. Keep full I&I HUD/main UI pending verified adapter/resource integration. The purpose is to measure the preferred styling at actual resolution, **not** to accept the interim mixed-skin state as final.

### Phase 2 — Targeted common-menu + HUD proof

1. Implement the **small common-menu behavior adapter** (InkArt backgrounds, Smooth Map hints) if it genuinely reduces obstacles; compile with exact current annotations/merge inputs and prove wrapper ordering. The adapter is not the final treatment if retained movies look inconsistent.
2. Prototype **one representative I&I HUD visual component** combined with SAHUD/FriendlyHUD behavioral contracts, including visibility transitions and relevant exports. Start with a resource having a clear owner and reliable reversible tests; select the first resource *after* inspecting dependency/complexity, not by a guessed priority.
3. The user has explicitly approved **private, personal modification of the extracted Ink & Iron resources**, without intending redistribution. Use them directly for local experiments and integration when technically appropriate. Keep third-party binaries, source extracts, cooked resources and private ZIPs out of public Git; commit only original tools, manifests and non-asset documentation.

**Gate:** complete in-game show/hide, combat activation, target text, icon prompts, map hints, joystick/keyboard, menu transition regression checks. Successful compilation is necessary but not sufficient.

### Phase 3 — Consolidate visual HUD and conflicting elements

Apply the proven technique to only the required HUD movies. Where GOW controls/Outfit Wheel, Hoods buttons or Smooth Map cues visually disagree, restyle their **visible components** or create verified functional combined assets. Do not silently forfeit their features. Keep a resource-by-resource manifest and rollback. Avoid conflating I&I map *tile textures* with the *worldmap UI movie* and navigation controls.

### Phase 4 — One-screen inventory redesign

Retain the desired Ink & Iron design language, **not its radial equipment layout**. Create one Inventory functional vertical slice before shops: item grid with equipped markers, clean character preview, item details/comparison, currently equipped identification, keyboard/mouse/controller traversal, Hoods dye/hood, quickslots/Roach gear. Reuse the design for merchant, stash and loot if it clearly improves those workflows. No new top-level equipment menu.

### Phase 5 — Acceptance / clean baseline

Compile/cook/bundle/validate affected assets against 5.01; test in cloned profile then, after explicit user choice, move the accepted modules to the main compatibility profile. Record which areas intentionally retain vanilla/other appearance, rather than implying all surfaces are I&I. Later universal typography/color/shadow changes only if in-game testing warrants them.

## Scope, effort, and practical boundaries

- This is **more work than the prior preservation plan**, because maintaining SAHUD/FriendlyHUD features while adopting I&I compiled HUD visuals may require reverse-engineering/rebuilding several UI movies. There is no honest guarantee of an easy whole-HUD merge.
- **Functionality is a constraint, visual ownership is negotiable.** Hard constraints: no lost basic UI actions, broken focus, missing quest/interaction cues, broken mod menu, movement/quest regressions or invisible map hints.
- Keep the already accepted QoL and controller/locomotion changes intact; no mass Script Merger rerun or live installed-file overwrite.
- **Personal-use scope:** no author-permission gate for local changes/testing; no distribution or publication of modified third-party assets. Preserve original author provenance, mod archives and reversible test packages outside Git.
- Separate test ZIPs and exact rollback. No Computer Use.
- Codex may research and build isolated original adapters with local assets/tools, but **must not deploy** before an explicit user-run test procedure and approval.

## Immediate new Codex request

Update the previous binary-owner matrix into a **visual target vs functional contract** integration matrix across I&I HUD, common/overlay, worldmap, Hoods/inventory and accepted NPC components. Identify the **smallest actionable first combination** and whether the common-menu adapter should precede or follow that prototype. Keep the older audit as technical evidence. Deliver a concrete implementation order, private-asset boundaries, acceptance tests and isolated build instructions. **Do not yet rewrite every conflicting mod or overwrite Vortex.**
