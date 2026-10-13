# HUD Refinement v4 — user in-game acceptance and radial-menu regression

**Report:** 13 October 2026. **Authority:** the direct, newest user feedback below. This report was received after v4 packaging; leave original static build receipts as snapshots of their creation time.

> Check the repo. The reds are perfect, the quickslots are back, the buttons are the right size and looking much better, but the letters inside are filling the circle a bit too much (are too big), and the circle/axi/lb selection menu was broken and doesn't open, the rest is fine.

## Scope and status

| Surface | Latest user status | Change permission |
|---|---|---|
| Ordinary enemy health/name reds | **Accepted: perfect** | **Freeze v4 palette** (`#B94A40` health; `#D9695A` hostile name; `#C77D6E` lag), along with accepted other semantic colors |
| Compact enemy overhead and pre-attack warning | No new objection; previously requested design | Preserve existing v4 behavior/geometry and warning-alpha adjustment; no reason for another broad enemy change |
| Ink & Iron bottom-left quickslots | **Accepted/restored** | Keep I&I quickslot styling and function; **do not revert to vanilla/retail** to paper over radial problem |
| Controller glyph outer design/scale | **Accepted: correct size, much better** | Keep outer circular/capsule art, vector smoothness, existing overall prompt spacing/layout unless a specific defect is demonstrated |
| Letters inside circular Xbox button symbols | **Too large** | Reduce **inner letterform size** only, e.g. A/B/X/Y to approximately 75–85% of current *letter* scale as an initial visual trial; center optically, maintain clear ring padding; leave outer ring and actual prompt sizing unchanged. Percentage is an assistant design proposal, not an explicit user number. Avoid shrinking LT/RT typography unless visibly needed |
| LB radial menu for signs/Axii (and possibly other quick selection) | **BROKEN: menu does not open** | **Highest priority functional regression.** Correct and verify before declaring v4 acceptable. This means the controller-operated circular quick-access/sign selection wheel, **not the controller button glyph itself**. The report does not establish whether the same radial menu opens by keyboard or which internal component fails |
| All other HUD functionality/appearance | Working/acceptable | Preserve, with no broad redesign |

## Investigate actual v4 regression, do not infer a root cause from passing offline tests

User reports v4 radial menu does not open, although v3 user tests previously found everything functional before the restored I&I iteminfo and v4 glyph/layout changes. `research/ink-hud-refinement-v4.md` explicitly says "check radial input" but marks runtime as pending. Its 59 synthetic tests check structural invariants, not the in-game LB path.

Concrete v4 differences to trace:

1. `hud_iteminfo.redswf`: restored **I&I v1** native movie over the earlier v3 retail iteminfo. The `hud_radialmenu.redswf` movie and `hud.redswf` also changed with smooth Xbox glyphs and layout adapters.
2. `InputFeedbackButton` source was patched in `hud_radialmenu`, `hud_iteminfo`, and several shared movies. `HintButton` was patched in `hud.redswf` and controls feedback. All function exports and listeners being present does **not** establish that runtime rendering/opening succeeds.
3. **Potential script/resource mismatch to audit:** v4's builder keeps v3 **WitcherScript bytes unchanged**, while restoring I&I `iteminfo` and the `iiShowQuickSlotKeys` option. V3's selected `inkIronNpcPlate` source had previously removed the I&I-only key-hint annotation section. This is a demonstrable packaging decision, **not yet proven to be the reason LB does not open**. Compare v1 scripts, v3/v4 scripts and current I&I iteminfo/radial contracts before applying any script fix.

### Recommended diagnostic sequence

- First read effective mod resource winners, current `mods.settings`, and active binding of **LB to Quick Access/Radial Menu** (without modifying settings). Determine whether LB input is received and whether the same wheel opens through keyboard alternative. Distinguish input mapping/dispatch, GFx create/show/open callback, Flash ActionScript exception/abort, `hud_radialmenu` paint and `hud_iteminfo` state interaction.
- Inspect exactly how `CR4HudModuleRadialMenu` and `CR4HudModuleItemInfo` interact with the root movie and annotations; diff **v3 working vs v4** byte/source changes. Check new `InputFeedbackButton` code for unsafe null/hitArea/viewrect/scale assumptions during radial initialization.
- If offline tracing cannot decisively locate the cause, construct **small private coherent package variants** which each replace **one suspect resource group** from v4 with verified v3 or v1 input (e.g. radial movie; iteminfo movie; shared root/prompt adapter), with unambiguous hash checks. Test the single most informative variant first; never enable two full HUD packages simultaneously, and don't conflate a retail quickslot regression test with an acceptable final user design.
- If necessary add targeted logging/runtime diagnostics rather than doing a broad HUD rewrite. Correct the actual bug with I&I quickslots preserved and the accepted v4 palette, size and typography frozen. Include a real LB-to-wheel in-game verification step in the handoff; offline compilation is insufficient.

## Next deliverable

A bounded **v4 hotfix**, no broad redesign: working LB radial quick-access/sign/Axii menu with I&I quickslots, and smaller central Xbox glyph letters while keeping the approved ring size and overall UI proportions. Preserve remaining v4 contents and support rollback to v4. Run native/GFx/script gates and report genuine runtime uncertainty. Private binaries and author assets remain ignored; public Git contains only first-party tools and evidence. Never alter user Vortex profiles, saves or merges automatically.
