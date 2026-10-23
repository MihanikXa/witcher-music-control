# Codex instructions — independent Witcher 3 UI project

## 23 October r7 — pending runtime transition verification

R6 user confirms previous functional faults work; r7 removes the separate generic
pending title and retains the formatted tooltip until a current-ID/current-serial
payload commits. Duplicate/zero-ID replies are rejected; Browse focus return no
longer forces unchanged details. Only MenuInventory/TooltipInventory change;
actions, selected row/notch and r6 input remain intact. See
[r7 transition receipt](research/inventory-approved-unified-p1-r7-details-transition.md).
Sixteen offline tests and controlled reconstruction are not native rendering or
flicker acceptance. Next: same-save rapid-selection 60fps recording, equip and
category/Details round-trip. Visual finishing is a [separate plan](design/inventory-visual-finishing-after-r7.md),
not implemented in r7. No live install/settings/save/merge edits.

## Latest user-confirmed functionality; details transition flicker — 22 October 2026

User now says **"Everything that was faulty works now"**, and provides two
consecutive item-selection frames. The **only reported remaining functional
problem** is a several-frame transition where the middle details panel becomes
a plain large white title with no stats, then snaps into correctly formatted
native details. They also explicitly say **the appearance remains far from
the approved concept**. See
[22 October source-grounded report](research/inventory-approved-unified-p1-r6-runtime-feedback.md).

**Confirmed code cause:** `Scene.asinc::aiSelectData` displays generic
`aiPendingName`, calls `TooltipInventory.aiPending` which hides the real
tooltip on new ID, then native async `OnApprovedDetails` later returns;
`aiPresent` validates and reveals the formatted details and clears the
placeholder. This is the user's two screenshot states. Fix with a stable
formatted presenter, no generic pending title/hide state, one current-ID+
serial-validated commit. Test rapid controller scrolling and stale payloads,
consider bounded caching only if runtime latency warrants it.

After this small stability fix, perform a **separate reference-fidelity finish
pass**: cohesive neutral background/grounding/lighting (not pixel-identical
scenery), refined item/details typography and category symbols, appropriate
footer restraint. Preserve the approved rail/list/details/Geralt proportions,
existing gold equipped marker, current functional category actions and input.
Do not restart a broad rewrite or Review implementation. All visual fixes
need in-game screenshot acceptance. Diagnostics overlay is not final UI.
No automatic installed game/Vortex/save/merge changes.

## Scope and authority

**21 October r5 runtime / r6 selected-row correction:** user reports much better,
almost everything works, but no visible selected item. Screenshot details still
follow real selection at focus=1. R5 paint made selected+inactive identical to
unselected; r6 keeps a visible selected-row border/fill independent of native
active-focus gating, with stronger active emphasis. Only SlotBase changes from
r5; no input/action/layout changes. See [r6 selection receipt](research/inventory-approved-unified-p1-r6-selection.md).
Offline paint regression is not runtime acceptance. Next: D-pad/mouse selection
matches details, category/Details round-trip and starter-sword equip retention.

**21 October gamepad failure / r5 correction:** user confirms equip/unequip
generally but explicitly says gamepad cannot equip/unequip, navigation/focus is
confusing and contextual actions fail. The stats screenshot's white block matches
the detached custom mask Shape. See [r5 input stability](research/inventory-approved-unified-p1-r5-input-stability.md).
R5 corrects native tracker priority, D-pad/arrow ownership, projection-based module
eligibility, late list focus, visible active-region cues and stats mask lifetime.
Native actions/modals are preserved. Offline tests/compiler controls are not
gamepad acceptance; next is the short native action/navigation/stats return test.

**20 October r4 actual runtime evidence:** real rows/details now display in
Weapons and Other. User overlay shows owned=50, published=38, binding=38,
equipped=9, restored Weapons filter and probe=false. Both equipped starter
swords plus Disglair are visible with correct notches/native comparison and
level restriction. See [runtime proof](research/inventory-approved-unified-p1-r4-runtime-proof.md).
This establishes the data/row/details bridge, NOT equip/unequip, full parity,
flicker-free input or visual acceptance. Twelve exclusions need ID reconciliation.
Next is one permitted starter-sword unequip/re-equip + selection/model/marker
check and Inspect/Back. Do not build another package or expand features merely
to respond to these screenshots. Remaining visible defects: optional lookup
#1009, clipped rarity label, lingering Drop target and contextual footer cleanup.

**20 October r3 runtime / r4 diagnostic:** the user's screenshot shows the
custom scene owns browsing (old tabs/dots/orbit removed), but every visited
category has zero rows. Optional fault is `1 lookup #1009`. See
[r4 data-boundary receipt](research/inventory-approved-unified-p1-r4-data-boundary.md).
The three custom Flash callbacks were plain functions rather than the native
script event contract. R4 corrects them and pins sent/ack/owned/published/binding
counters without console setup. Compilation is not proof of native dispatch;
actual r4 row/details/action results remain pending. Do not expand features.
Work only in the `ui-overhaul` branch of `MihanikXa/witcher-music-control`. Do not alter `main` or `general-merge`. The primary authority for runtime resources is the *installed* The Witcher 3 Remastered 5.01/REDkit version; downloaded font/name-color mods are references, not guaranteed compatibility.

**20 October diagnostic receipt:** see
[bounded Unified P1 diagnosis](research/inventory-approved-unified-p1-diagnosis.md).
Released rail validation on an unattached native tab reproduces a null-stage
failure in the authored-method negative control. The user's r2 screenshot now
confirms `rail.icons.begin → TypeError #1009`, before module/list setup; it does
not identify the exact operation inside that method. R3 adds per-operation
evidence and isolates optional icon failures so functional setup can continue;
the first optional fault remains visible in the overlay. Native category renderers are confirmed
external siblings (`InventoryGridRef` / `CoreList`), so hiding `mcTabList` alone
was also insufficient. The private diagnostic fixes those boundaries, uses the
native runtime tooltip asset provider, gates the inherited subdata alpha/data
writer and records real item/selection/action evidence. No runtime acceptance
or item parity is claimed. Do not expand features or redesign composition;
next step is the user's short diagnostic smoke procedure. No automatic live
installation, settings, merge or save edits.

Do not modify the user's installed game, Vortex deployment/staging, Documents settings, saves or third-party packages without a separate, specific user authorization. Reading local files for research is permitted. Avoid blanket settings resets or regenerating the working merged scripts.

## Most recent Unified P1 user correction — 19 October 2026

The user confirms Unified P1 is **NOT FUNCTIONAL**, not merely visually
overlapped. The surviving **original dotted grid displays only one sword**,
suggesting a separate item enumeration/filter/display regression, **not proof
of data loss**. The screenshot's **flat grey charcoal background rectangle,
hard bottom cutoff and disconnected ground/Geralt treatment** are also
explicitly rejected; prior report overlooked this. Read
[Unified P1 revised runtime failure](research/inventory-approved-unified-p1-runtime-failure.md).
The user's feedback supersedes the earlier milder visual-only review.

Next work MUST be narrow, read-only runtime diagnosis: same-save Menus v4
baseline comparison, owned IDs/native filter counts, annotation script load,
GetAllItems → ShouldShowItem → flash publisher → binding → aiData → real row →
real details, old UI visibility writers and actual action dispatch. Examine
aiScene's authored fixed 1920x850 nearly opaque gradient for the hard cutoff;
do not rescue it with cosmetic alpha or position tweaks. No full new candidate,
Review acquisition code or other UI work before native item parity + working
interactions + single scene can be established. Disable rejected candidate
manually for regular play. No automatic Vortex, game or save changes.

## Previous Unified P1 runtime screenshot — FAILED (19 October 2026)

The user supplied the first real in-game screenshot and responded **"No idea
wtf this is."** Unified Inventory P1 **fails basic visual/runtime integration**:
its new left rail draws, but the old Inventory category bar, WEAPONS/ARMOR
dotted grid and 20-slot paperdoll equipment orbit remain; horizontal item
rows and middle selected-item details are missing. Read the
[first Unified P1 runtime failure report](research/inventory-approved-unified-p1-runtime-failure.md)
before further work. **Do not recommend cosmetic tuning, a P2 rebuild, Review
features or another full category implementation until the live runtime
display-owner/data-binding failure is diagnosed.** Inspect active resource owner
and native annotation, then trace the exact event chain
`aiEnter → aiArrange/aiEnable → OnApprovedRefresh → aiData → row paint →
OnApprovedDetails → aiPayload`, and which native lifecycle methods reactivate
old UI layers. Original P1 final native cook timed out; controlled packaging
passed but native candidate not validated. All offline mocked tests were
insufficient to detect this. Leave working Menus v4/HUD RC2 untouched; advise
manual disabling of P1 in cloned profile for rollback. No automatic live edits.

## Previous implementation-scope correction — 18 October 2026

**19 October implementation receipt:** the private unified first-playable
candidate is now documented in
[Approved Inventory Unified P1](research/inventory-approved-unified-p1.md).
Source is `src/inventory/unified/`; reproducible entry point is
`tools/build-approved-inventory.py`. It transforms exact accepted v4, uses one
retained row/controller/details scene across ordinary player categories and
reserves disabled Review first. **Not yet visually/functionally accepted in game.**
Final native cook hit a blank startup timeout; released bundle/metadata use
independently controlled reconstruction. Exact released annotations match the
successful compiler controls. Eight targeted tests pass, not runtime acceptance.
Check native tutorial-tab progression, model/details framing, all heterogeneous
actions, device switching and zero flicker in the user's first test. No live
installation/settings/merge/save changes were made. Do not start Review ledger,
bulk cleanup or another composition redesign before this candidate is evaluated.

The user questions the earlier **Weapons-only playable slice**, explicitly
reasoning that once Inventory logic/layout are redesigned, implementing all
ordinary categories under one system could be simpler than combining two
incompatible logic/layout systems. This is a valid architectural change.
Read [unified player Inventory scope](design/inventory-unified-category-build-scope.md).

**Next first-playable candidate should target one shared player-Inventory UI
framework across the normal categories** (Weapons, Armor, Consumables, Bombs,
Pockets, Quest Items, Other), using the exact user-approved category rail,
one retained horizontal row renderer/list controller, persistent middle details,
Geralt, subdued cohesive background and one device-adaptive footer. Category
variation belongs in data projection, sorting and native actions, NOT separate
visual layouts. Test each type incrementally, but avoid a shipped
"redesigned Weapons vs old vanilla other categories" hybrid if practical.

This expands the previous Gate 2 scope, not authorization for a monolithic
new acquisition ledger, merchant/stash/horse redesign or other QoL add-ons.
**Review remains first in the approved rail**; its genuine saved acquisition
ledger is a separate, later gated source integration unless independently
proved safe. Do not show fake counts, inert buttons or pretend Review works.
Preserve all items/tags, special Hoods/OW/Roach/quickslot native actions, and
test intermediate exceptions before deciding a fallback is necessary.
User in-game acceptance and anti-flicker behavior remain required; no
automatic Vortex/game/save modifications.

## Previous acceptance and background flexibility — 18 October 2026

The user **agrees with the Gate 0–1 visual proofs and technical findings** and
clarifies explicitly that the scenery, ground and lighting may be substantially
simplified; **the whole UI's cohesion, analogous approved layout and aesthetic
quality** matter more than matching the generated backdrop 1:1. See
[visual reference acceptance](design/inventory-reference-accepted-review.md).
This supersedes earlier notes that reproducing the exact backdrop/pose/lighting
must block a functional Weapons slice. Preserve the approved rail, native-scale
rows, persistent middle details, Geralt's relative placement/proportions,
accepted equipped notch, one footer and user-approved visual hierarchy.
A neutral charcoal/ink background, understated ground/shadow and simplified
lighting are acceptable if Geralt and all regions feel deliberately integrated;
do not reintroduce green opaque fill, disconnected black voids or old-slot
engravings. Avoid gratuitous design changes to anything except environmental
treatment. **Next task can be a tightly bounded first playable Weapons slice**,
with real background/model tests and flicker instrumentation; no need for
pixel-identical scenery reconstruction. Review remains approved as first rail
category, but persistent acquisition integration follows the foundational
list implementation. No automatic Vortex/game/settings/save changes.

## Prior Inventory implementation route — 18 October 2026

The user-approved 1672x941 screenshot is **the visual authority**:
vertical category rail → compact one-column text/icon item list →
persistent middle details → right-side Geralt. No redesign of its proportions,
typographic hierarchy, character size or footer. Reuse the approved existing
**equipped notch/stripe**. The new **Review** category appears FIRST and
filters genuine significant acquisitions, not routine repeated materials.

**Read before another Codex implementation**:
- [Native source-to-screen map](design/inventory-approved-implementation-map.md)
- [Review acquisition/state contract](design/inventory-review-behavior-contract.md)
- [User-approved visual reference](design/inventory-reference-accepted-review.md)

The screenshot is NOT committed to Git; place the unchanged original in the
ignored local `reference/inventory-design/approved-inventory-reference.png`.
Verify SHA-256 `9e7d6bdb0bad0d28b5bacfc02e8433dac177b34690303acee8af6cd03b235ac9`.
If absent, ask user for file; do not infer visual target from P1/P2.

**Gate 0 local-copy authorization (18 October):** the supplied local PNG is
1672×941 but hashes to
`b1443ffafc009a5f123d6c971e3ea1e47572763b229595ab78d76799bde87313`.
After the mismatch was reported, the user explicitly replied **“Use the current
local image”**. This copy is now authorized; retain the historical hash as
provenance, not a reason to request the same confirmation again. Gate 0–1
findings/proofs are recorded in
[the source and visual receipt](research/inventory-approved-gate0-1.md).
**Proof approval remains pending; no native build is authorized by this receipt.**

Next is **Gate 0–1 only**: inspect accepted Menus v4 native resource owners,
exact equipped notch, item row/data/actions, background/footer and produce
sparse+dense visual proofs against reference. Obtain user visual approval
before native binary build. P1/P2 layout and flicker are rejected; use only
their functional source evidence. Review exact policy thresholds are examples,
not explicit user choices. No automatic Vortex, game, merge or save changes.

## Historical approval note — equipped marker and Review — 18 October 2026

User confirms the small **equipped notch/stripe already exists and is accepted**
in their current working Inventory design; reuse it **exactly**, no new marker
concept or separate equipment display. User explicitly agrees to the
selected concept composition **and Review as the first attention-filtered
category**. See
[final user approval](design/inventory-reference-accepted-review.md).
High-level Review inclusion/exclusion is approved; exact item-rule corner
cases and persistence semantics need implementation verification.
P1/P2 visual layouts remain rejected. Next work is source-mapping/plan for
faithful approved reference, not another unconstrained speculative redesign.

## Earlier visual direction and Review (18 October 2026)

The user chose a **specific generated concept screenshot** as the preferred
Inventory layout: one vertical category rail, adjacent **compact one-column
item list**, middle selected-item details, and Geralt on the right with a
quiet footer/background. Read
[accepted reference and explicit correction](design/inventory-reference-accepted-review.md).
The user **rejects ALL assistant refinements** to Geralt size, detail
hierarchy, category rail spacing and footer, except equipped-state marking
may warrant a subtle solution. **Add Review as the FIRST category**, for
noteworthy newly acquired items (not every herb/duplicate material), rather
than a raw Recent tab. Real acquisition history and durable per-item
dismissal must underpin Review; initial eligibility rules are candidates,
not user-approved scores. The user's visual direction supersedes the prior
Gear grid/gallery, P1/P2 plans. Do not do another experimental native build
or alter accepted Menus v4/HUD RC2 without a reviewed source/visual plan.
The reference image exists in conversation, not repo; do not claim pixel-level
specification from the source code alone.

## Historical user authority — P2 rejected (18 October 2026)

P2 is **explicitly rejected** for giant low-resolution detached item icons,
small/disconnected Geralt, off-style green-black canvas, disorganized/wasteful
screen and flashes/disappearing-reappearing elements during actions. Read
[direct P2 rejection](research/adaptive-inventory-p2-user-rejection.md).
This supersedes the previous recommendation to do a bounded P2 refinement.
Preserve P2 as code/diagnostic evidence only. Next: revert the test profile
to Menus v4 manually; get explicit user acceptance of a real-scale static
sparse+dense visual composition *before any further native Inventory build*.
Trace P2 flicker separately, without asserting a root cause; preserve HUD RC2,
the accepted menu baseline and existing working mods. No automatic live edits.

## Historical P2 first runtime screenshot — 18 October 2026

The user supplied a **first in-game P2 screenshot** and asked to check the
repository. See [P2 first runtime review](research/adaptive-inventory-p2-runtime-first-screenshot.md).
Do **not** classify it as user approval or explicit rejection. Observed partial
success: obsolete orbit engravings removed; clean shared header; native
Disglair item summary now displays actual name, damage/+20 and level 2
requirement; duplicate button rectangles gone. Remaining deficiencies:
the sparse first-fit item gallery still looks visually fragmented; summary is
anchored far to the left of a centered gallery by `p2Geometry()`; category
icons are tiny and low-legibility; footer still appears to be **native hints**
despite P2's attempted native-feedback override; red-X selected item is likely
a native required-level restriction and must be traced, not blindly erased.
Next action is a **bounded source/runtime correction of gallery+summary cohesion,
navigation legibility and footer owner**, not a third unbounded rewrite or QoL
feature import. Test both KB and pad, preserve v4/HUD RC2.
The image shows the game within a roughly 910×512 desktop window; don't claim
full-screen 1080p/4K or device-transition acceptance.

## Prior P2 composition contract (18 October 2026)

User agreed to **prepare the source-grounded visual/interaction specification
before another expensive full Inventory build**. Read
[Adaptive Inventory P2 composition/interaction contract](design/adaptive-inventory-p2-composition-contract.md)
first. This document is a proposed design, **not an accepted P2 implementation**.
Major requirements: one quiet common navigation, reflow the actual native item
slots into a cohesive gallery, selected-item summary must genuinely populate,
Geralt integrated, remove obsolete **Inventory-specific old-slot background**,
one device- and mode-sensitive footer provider, proper sparse/dense geometry.
Distinguish compiled source observations from unknown actual movie child
ownership and current input-device API. First build is a bounded structural
proof with a user screenshot gate, **not** another whole adaptive QoL rollout.
Preserve accepted Menus v4/Gentium/art, HUD RC2, v1/P1 rollback and no live
deployment.

## Prior user corrections to rejected Inventory P1 — 18 October 2026

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
