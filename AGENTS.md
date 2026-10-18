# Codex instructions — independent Witcher 3 UI project

## Scope and authority
Work only in the `ui-overhaul` branch of `MihanikXa/witcher-music-control`. Do not alter `main` or `general-merge`. The primary authority for runtime resources is the *installed* The Witcher 3 Remastered 5.01/REDkit version; downloaded font/name-color mods are references, not guaranteed compatibility.

Do not modify the user's installed game, Vortex deployment/staging, Documents settings, saves or third-party packages without a separate, specific user authorization. Reading local files for research is permitted. Avoid blanket settings resets or regenerating the working merged scripts.

## Latest user corrections to rejected Inventory P1 — 18 October 2026

The user agrees P1 failed and adds two **explicit** defects:
(1) its Inventory background/engraving composition assumes the old equipment
slots around Geralt; (2) the interface is not convincingly adaptive to
controller versus keyboard. See
[direct user correction and scoped requirements](research/adaptive-inventory-v2-p1-runtime-rejection.md).
The next Inventory design must remove/recompose **slot-dependent background
art only within Inventory**, retaining accepted art elsewhere, and own one
context/device-sensitive prompt system rather than hardcoded mixed I/View,
Tab/LS labels plus a second native footer. Verify live input-device changes,
controller focus and prompt transitions. These are independent of the already
listed layout, summary and empty-space failures. P1 remains rejected; do not
proceed by coordinate-only patches or misleading static UI proofs.

## Prior P1 in-game rejection — user explicit (17 October 2026)

The first **Adaptive Inventory v2 Gear Prototype 1** has now been shown in-game
and the user's exact response is: **"No idea the fuck this is"**.
Treat the **visual/UX candidate as rejected**, NOT as accepted because 16 tests
and native compile passed. Save the private P1 files only as functional
reference; recommend switching the test profile back to accepted Menus v4
Inventory until a new candidate. The screenshot and evidence are described in
[the P1 rejection report](research/adaptive-inventory-v2-p1-runtime-rejection.md).

Do **not** iterate by moving the existing native section groups, scaling the grid
again, adding another detached tooltip strip or another footer button row. The
user wanted an integrated adaptive item-driven composition; P1 displays
WEAPONS/ARMOR tiny clusters in the upper left, giant dead space, a disconnected
Geralt far right, native subnavigation/category icons colliding with Ink & Iron
header, duplicate bottom control systems and **no selected-item contextual
summary**. These are screenshot observations/assistant interpretation, while
the user quote above is direct evidence.

Next work is **diagnosis and a materially different design/architecture**,
including runtime tracing of the missing summary and explicit shared-header/
native-category/footer ownership, then a cohesive state-driven first screen
that handles very sparse **and** full inventories. Preserve Gentium/Menus v4,
item art, HUD RC2, Hoods, input contracts and manual rollback. No broad mod/QoL
installation or automatic live changes. Require visual geometry and functional
proof before declaring the next candidate done.

## Prior user completion and earlier inventory plan — 17 October 2026

The user said **"Alright, all done. Let's continue to the next task"**
following Menus v4 Typography Finishing. Treat the menu appearance work as
**accepted/closed by the user** and leave it alone unless they report a new
problem. This is a broad user completion statement, **not** a case-by-case
functional test report. The v4 native cook/validate commandlet stalled; its
source verified fallback built the release and 13 targeted tests passed.
See [v4 receipt](research/menus087-v4-typography-finishing.md). Native
verification may be done as a separate housekeeping check if tool startup
recovers; it must not drive further visual modifications or block new work.

**Next active workstream: Inventory v2**. Read
[inventory phase transition](research/inventory-v2-phase-transition.md),
[user's explicit v1 feedback](research/ink-gear-grid-v1-user-feedback.md), and
[current inventory UX direction](design/inventory-ux-direction.md). Start from
the **working 0.8.7 Menus v4 inventory resource/compatibility stack**, not the
old 0.8.6 prototype SWF as a replacement. Reuse v1 only for functional ideas/
proven code contracts; do not carry forward its visually rejected arrangement.
Preserve approved Menus v4, Item Art, Bestiary Art, Map Inked, and HUD RC2.
No automatic Vortex/game/live save or merge changes.

## Historical explicit correction — menu row internal alignment (17 October)

User approves the previous typography/secondary-color/prose/footer finishing
scope **but adds alignment**. Cropped current-vs-reference Alchemy row screenshots
show the `Ingredients missing` secondary label **too low and detached from its
recipe title** even when the row border, icon and title are close. Preserve
icons, menu layout/geometry, navigation and background as user requests.
Inspect actual `ItemCraftingModule` row placement and `qfCaps` field metrics;
fix only internal two-line label positioning with selected/unselected and
controller navigation checks, NOT entire list geometry. Details:
[menu row alignment correction](research/menus087-v3-runtime-typography-feedback.md).

## Prior v3 typography runtime comparison (17 October)

User reports v3 "Much better but not quite it" with current versus
reference **same Greater Blue Mutagen** screenshots. The icon art,
shared slim topbar and Alchemy composition now appear substantially aligned.
Main remaining visual differences: synthetic Gentium small caps are
lighter/narrower than the authored IM Fell SC reference; center
heading lacks width/tracking; center recipe ingredient warning is red
while reference is neutral; prose wraps to two lines versus one; menu
footer lettering is still conventional. Read
[Menus v3 runtime follow-up](research/menus087-v3-runtime-typography-feedback.md).
Do not recook icons or change HDR/background/layout on these screenshots.
Use a bounded Alchemy-first font styling pass, then other menu roles,
without changing the accepted RC2 HUD. This review is not a user-approved
line-by-line typography specification.

## Prior v2 in-game styling priorities — user explicit (17 October)

The common Ink & Iron 0.8.7 layout/engraving/header now looks substantially
right. The user's **main remaining concern is typography and text color**;
item **icons also look wrong**. They suspect photo/screenshot saturation and
contrast differences are **HDR**, so **do not tune global brightness/saturation,
background contrast or HUD palette on that evidence**.
Read [latest explicit clarification](research/menus087-v2-runtime-comparison.md).
Next, target **menu-local Gentium hierarchy, small-cap treatment, sizes,
alignment and text colors**, plus provenance/texture-owner checks for the
**Icon Pack** already supplied in the 0.8.7 All-in-One but omitted from v2.
Preserve shared layout, accepted HUD RC2 and functional integrations. Do not
continue Gear-grid v2 until common menu fidelity is accepted.

## Latest typography directive — user explicit (17 October)

Keep QuietFolio/Gentium's font family/library, **not** current menu typography
color, size, positioning, alignment, spacing or hierarchy. These are editable
toward the Ink & Iron mod-page reference with font-aware measurements. Read
[latest runtime feedback + reference acquisition](research/menus087-runtime-visual-feedback.md).
Bestiary Art is a separate optional source to acquire; Map Inked is separate and
optional for map visuals. Other menu engravings/top-bar artwork should already
be in the shipped 0.8.7 UI/24-entry cache, and need runtime diagnosis rather
than a speculative addon.

## Latest user runtime feedback — visual baseline NOT accepted (17 October)

Read [Ink & Iron 0.8.7 visual runtime mismatch](research/menus087-runtime-visual-feedback.md) first. The first five in-game screens lack the slim shared top bar and many mod-page engravings. The user calls the result "half-cooked." Before Inventory v2, identify current **effective `panel_common` owner**, new TopBarNew initialization and `inkart:` texture runtime, compare optional Bestiary Art / IM Fell / Character layout presets, and correct the actual integration gap. Package/native/15 tests did not test screenshot parity. Preserve custom HUD RC2, existing visual work and the source/ZIP rollback. Do not update live Vortex automatically.

## Prior active work — 0.8.7 menu migration with 0.8.0 preservation (16 October)

The user added a **0.8.7** update under the private local `reference/` and says their
existing UI was based on **0.8.0**. 0.8.7 lacks the separately obtained Hoods
compatibility patch and our private 0.8.6 work. **Read
[0.8.7 migration handoff](research/ink-and-iron-0.8.7-menus-migration.md) first.**
Locally pin the new source, compare **upstream 0.8.0 → customized installed UI
→ interim 0.8.6/official Hoods compatibility → upstream 0.8.7**, rebase only
missing changes without removing accepted custom modifications, and build a
private compatible shared-menu baseline. The installed accepted custom HUD v4/RC2 is frozen. **Audit 0.8.7 HUD/Buttons for useful missing upstream changes; optionally prepare separately testable selective ports without replacing or regressing RC2.**
Do not import the rejected Gear-grid v1 presentation into the baseline. Other
older integration/audit documents are historical, not authority to overwrite
current code. No live Vortex/settings/merge modifications without approval.

## Prior work: Ink & Iron 0.8.6 Inventory (superseded by latest 0.8.7 menu phase)

The user confirms custom HUD v4/RC2 works and has moved on. **Freeze it.**
Next task is one functional **one-screen Gear-grid Inventory** prototype using
actual **0.8.6 UI plus official optional Hoods Compatibility** as version-pinned
local source. **Read [0.8.6 Inventory handoff](research/ink-and-iron-0.8.6-inventory-handoff.md) first.**
The old `reference/ink-and-iron-0.8/` and audit are **0.8.0 historical**;
they cannot stand in for missing 0.8.6 archives. No automatic live deployment,
no update of custom HUD, and no broad UI redesign in this slice.

## Historical sequence correction — 16 October user Inventory feedback (now targets 0.8.7)

The user supplied explicit v1 screenshot criticism and proposes integrating the
**complete Ink & Iron 0.8.6 menu UI baseline before Gear-grid v2**. This now
takes precedence over immediately implementing a second Inventory layout pass.
Read [explicit feedback](research/ink-gear-grid-v1-user-feedback.md) and the
revised [Inventory direction](design/inventory-ux-direction.md). Use modular
0.8.6 menu UI/compatibility assets, **not a blind All-in-One replacement**.
Freeze the accepted HUD RC2; preserve Outfit Wheel, Smooth Map, Hoods/official
patch, QuietFolio and existing merges. Old 0.8.0 audit is historical. Source
archives for 0.8.6 are pinned locally in the v1 prototype docs. Do not
deploy live or overwrite the working prototype without specific approval.

## User's visual direction
- Quiet, modern, beautiful and airy, but with character and Witcher identity; *Ghost of Tsushima* is a restraint/hierarchy reference, not a template.
- Prefer Gentium Book as a **starting taste reference** instead of a generic sans-serif. Test literary serif body styles versus a restrained serif/sans hierarchy before choosing.
- Eliminate thick black text strokes where possible; retain sufficient dynamic contrast on bright snow, overcast sky, bright UI, daylight, fire, caves and night.
- Replace excessively saturated friendly/hostile/name/highlight colors with restrained semantic colors (warm ivory, stone, sage, muted oxide and aged brass are provisional examples). Preserve hostility, focus, interactability and selection distinctions.
- Favor spacing and typographic hierarchy over boxes, ornament, clutter or indiscriminate hiding.
- Preserve practical controller readability, legibility on 1080p and 4K, English punctuation and accented names. Acceptance scope is English only; Russian/Ukrainian and Cyrillic validation are not required.

## Reference locations
The user will supply extracted mods locally under `reference/`. Read `reference/README.md`. All reference asset contents are gitignored. Use them as evidence; do not republish authors' binaries. **For this strictly personal, non-distributed mod project, local edits and private builds of the extracted Ink & Iron assets are allowed by the user; do not impose an author's permission request as a prerequisite.** Keep modified third-party resources and packages gitignored. Preserve exact provenance/hashes and do not publish or redistribute them.

## Newest explicit scope authority — visuals and behavior (11 October 2026)

**Read first:** [design/ink-and-iron-visual-first.md](design/ink-and-iron-visual-first.md). User prefers Ink & Iron's visual design **including its HUD**. Preserve SAHUD/FriendlyHUD/Hoods/Outfit Wheel/Smooth Map **functionality**, not necessarily each mod's original appearance or movie resource priority. The older 0.8 auditor's "keep I&I HUD disabled; old owners win" is a safe **interim rollout**, **not** the final UI target. Existing conflicting mods' visible components are eligible for redesign or compatible merged resources after real contract mapping and isolated build/validation checks. Never blindly enable overlapping compiled movies; see current canonical plan for gates and sequencing. The inventory still needs a one-screen non-radial layout with equipped-item markers.

## Latest inventory and installation decisions (11 October 2026)

**Read these first:** [design/inventory-ux-direction.md](design/inventory-ux-direction.md) and [research/ink-and-iron-integration-plan.md](research/ink-and-iron-integration-plan.md). Keep Inventory as **one screen**; user dislikes the **entire circle-based equipment constellation around Geralt**, not just the grid. Geralt becomes a preview, equipped items gain grid markers, and lower-value inventory clutter is reduced by filters/information architecture, without losing actual resources. Shop and related item grids are additional candidates. Keep other Ink & Iron menus largely as published. First run a local exact resource-owner/Fonts-bridge/annotation audit, then install in a cloned profile with user approval. No All-in-One over existing Vortex profile; protect accepted font/NPC/HUD/movement features.

## Newest scope correction: selective Ink & Iron refinement

Read [design/ink-and-iron-scope.md](design/ink-and-iron-scope.md) **before** interpreting the older broad redesign roadmap. User wants to keep Ink & Iron for nearly all screens; mainly consider serious redesign of inventory/shop/other grids and player-stats readability. Preserve its coherent dark literary identity, and don't impose sweeping sans typography, brighter backgrounds or a full menu rebuild. Test whether screenshot text compression is real at 1080p/4K. The user explicitly authorizes local personal modifications of extracted Ink & Iron assets and has no distribution plans. Do not require author-contact or licensing clearance as a gate for local private work; do not publish or redistribute modified assets. Treat installed-mod collisions as real binary resource ownership conflicts. Keep accepted user packages and pending interaction/subtitle trials intact.

## Long-term roadmap and sequencing
Read [design/presentation-roadmap.md](design/presentation-roadmap.md) for the approved wider presentation and interaction plan. Its stages are *not* permission to implement or deploy a full overhaul immediately. Keep the current untouched-asset round-trip and NPC-nameplate proof as the first executable gate. Assess configuration-only SAHUD/FriendlyHUD opportunities before writing new logic; keep audio implementation on `main` and compatibility work on `general-merge`.

## Investigation before implementation
1. Inventory actual font, Flash/Scaleform/REDkit, menu, dialogue, subtitles, combat HUD, quest, inventory and NPC label resources used by current Remastered. Separate source-observed facts from inferences.
2. Determine exactly where typeface, weight, stroke/outline, glow/shadow, RGBA/name colors, sizes and alignment originate. Not every element shares a rendering path.
3. Map intersections with Seamless Adaptive HUD, FriendlyHUD, Mod Settings Menu Fix and compatibility package 04. Use `general-merge` only as read-only evidence; don't assume any UI asset can be replaced safely.
4. Verify any claimed technical recipe against the current installed resource format and toolchain. Never invent WitcherScript APIs, resource paths or Scaleform behavior.
5. Compare 2–3 coherent visual options. Preserve the user's Gentium preference while leaving room for licensed alternatives. Validate outlines and semantic colors independently before a global rewrite.
6. Prototype NPC nameplates as a separate Vortex mod with reversible deployment and no modification of existing managed files.
7. Check script/binary/resource priority collisions, potential font clipping, English glyph coverage, contrast, prompts and controller/keyboard input.

## Tooling, safety, and repository hygiene
Do not use Computer Use under any circumstances, per the user's explicit
instruction. Necessary GUI steps must be performed manually by the user;
provide exact isolated-project instructions and stop at that dependency.

Track original design documents, research findings, reproducible scripts/tests under `design/`, `research/`, `src/`, `tools/`, `tests/`. Keep generated files in ignored `build/` and `deploy/`; never force-add vendor mods, extracted game files, original game binaries, proprietary fonts or generated mod assets.

Start with an evidence-backed resource map, collision report, visual design specification and a minimal prototype plan. Do **not** begin by rebuilding the complete UI. Stop before Vortex installation and get explicit approval.

For each proposed patch, report the input resources/hashes, exact changed resource keys/paths, source provenance and license, build command, collision impact, game test criteria, and one-package rollback procedure.
