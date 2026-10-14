# HUD Refinement v4 — user in-game acceptance and radial-menu regression

**Report:** 13 October 2026. **Authority:** the direct, newest user feedback below. This report was received after v4 packaging; leave original static build receipts as snapshots of their creation time.

> Check the repo. The reds are perfect, the quickslots are back, the buttons are the right size and looking much better, but the letters inside are filling the circle a bit too much (are too big), and the circle/axi/lb selection menu was broken and doesn't open, the rest is fine.

> Nope, tab is just as broken

## Scope and status

| Surface | Latest user status | Change permission |
|---|---|---|
| Ordinary enemy health/name reds | **Accepted: perfect** | **Freeze v4 palette** (`#B94A40` health; `#D9695A` hostile name; `#C77D6E` lag), along with accepted other semantic colors |
| Compact enemy overhead and pre-attack warning | No new objection; previously requested design | Preserve existing v4 behavior/geometry and warning-alpha adjustment; no reason for another broad enemy change |
| Ink & Iron bottom-left quickslots | **Accepted/restored** | Keep I&I quickslot styling and function; **do not revert to vanilla/retail** to paper over radial problem |
| Controller glyph outer design/scale | **Accepted: correct size, much better** | Keep outer circular/capsule art, vector smoothness, existing overall prompt spacing/layout unless a specific defect is demonstrated |
| Letters inside circular Xbox button symbols | **Too large** | Reduce **inner letterform size** only, e.g. A/B/X/Y to approximately 75–85% of current *letter* scale as an initial visual trial; center optically, maintain clear ring padding; leave outer ring and actual prompt sizing unchanged. Percentage is an assistant design proposal, not an explicit user number. Avoid shrinking LT/RT typography unless visibly needed |
| Quick-access radial menu for signs/Axii | **BROKEN through both LB (controller) and Tab (keyboard)**; wheel does not open | **Highest priority functional regression.** Because two distinct inputs fail, prioritize shared radial initialization/show/open path and v4's combined movie/script state rather than controller icon styling or LB binding alone. The precise failing stage remains unproven. |
| All other HUD functionality/appearance | Working/acceptable | Preserve, with no broad redesign |

## Investigate actual v4 regression, do not infer a root cause from passing offline tests

User reports v4 radial menu does not open, although v3 user tests previously found everything functional before the restored I&I iteminfo and v4 glyph/layout changes. `research/ink-hud-refinement-v4.md` explicitly says "check radial input" but marks runtime as pending. Its 59 synthetic tests check structural invariants, not the in-game LB path.

Concrete v4 differences to trace:

1. `hud_iteminfo.redswf`: restored **I&I v1** native movie over the earlier v3 retail iteminfo. The `hud_radialmenu.redswf` movie and `hud.redswf` also changed with smooth Xbox glyphs and layout adapters.
2. `InputFeedbackButton` source was patched in `hud_radialmenu`, `hud_iteminfo`, and several shared movies. `HintButton` was patched in `hud.redswf` and controls feedback. All function exports and listeners being present does **not** establish that runtime rendering/opening succeeds.
3. **Potential script/resource mismatch to audit:** v4's builder keeps v3 **WitcherScript bytes unchanged**, while restoring I&I `iteminfo` and the `iiShowQuickSlotKeys` option. V3's selected `inkIronNpcPlate` source had previously removed the I&I-only key-hint annotation section. This is a demonstrable packaging decision, **not yet proven to be the reason LB does not open**. Compare v1 scripts, v3/v4 scripts and current I&I iteminfo/radial contracts before applying any script fix.

### Recommended diagnostic sequence

- First read effective mod resource winners, current `mods.settings`, and active binding of **LB to Quick Access/Radial Menu** (without modifying settings). The user confirms **both LB and Tab fail**. Do not request a redundant keyboard check or focus on controller binding remapping without new evidence. Confirm the dispatched common radial open action and isolate whether module initialization, GFx show/open, AS exception, visibility or shared quickslot state fails. Distinguish input mapping/dispatch, GFx create/show/open callback, Flash ActionScript exception/abort, `hud_radialmenu` paint and `hud_iteminfo` state interaction.
- Inspect exactly how `CR4HudModuleRadialMenu` and `CR4HudModuleItemInfo` interact with the root movie and annotations; diff **v3 working vs v4** byte/source changes. Check new `InputFeedbackButton` code for unsafe null/hitArea/viewrect/scale assumptions during radial initialization.
- If offline tracing cannot decisively locate the cause, construct **small private coherent package variants** which each replace **one suspect resource group** from v4 with verified v3 or v1 input (e.g. radial movie; iteminfo movie; shared root/prompt adapter), with unambiguous hash checks. Test the single most informative variant first; never enable two full HUD packages simultaneously, and don't conflate a retail quickslot regression test with an acceptable final user design.
- If necessary add targeted logging/runtime diagnostics rather than doing a broad HUD rewrite. Correct the actual bug with I&I quickslots preserved and the accepted v4 palette, size and typography frozen. Include **both Tab-to-wheel and LB-to-wheel** in-game verification steps in the handoff; offline compilation is insufficient.

### New inference from dual-input failure

This report eliminates the hypothesis that *only* the Xbox LB binding/icon causes the problem. Both default input routes fail, which makes shared state, radial module resource contracts, the newly restored I&I iteminfo movie, root-to-radial GFx wiring or common show/hide logic better first hypotheses. It does **not** prove which one. First compare the **working v3 radial behavior** with v4 and test a coherent v4 package using **v3 radial movie only** while retaining v4 iteminfo, glyphs and palette; follow with a v3 iteminfo swap *solely as a diagnostic* if necessary. Do not ship reverted retail quickslots as the preferred fix. If the wheel responds to neither input but action dispatch is confirmed, instrument the earliest shared initialization or show call. All experiments should preserve known-working Vortex profiles; no automatic deployment.

## Next deliverable

A bounded **v4 hotfix**, no broad redesign: working LB radial quick-access/sign/Axii menu with I&I quickslots, and smaller central Xbox glyph letters while keeping the approved ring size and overall UI proportions. Preserve remaining v4 contents and support rollback to v4. Run native/GFx/script gates and report genuine runtime uncertainty. Private binaries and author assets remain ignored; public Git contains only first-party tools and evidence. Never alter user Vortex profiles, saves or merges automatically.

## Additional user observation — 14 October 2026

Asked whether the failed v4 Tab/LB attempt produces the opening sound, slowed
time or blocked movement, the user answered: **"Nothing happens."** This is
feedback about the original v4 failure, not a test result for hotfix RC1.

The lack of perceived opening effects supports a failure before the native
ShowRadialMenu sequence reaches sound/time/context changes. Early native action
gates or missing input-listener registration remain possible; it does not
prove an ActionScript null exception. In the observed source chain, radial
footer setup occurs before GFx dispatches OnConfigUI, which registers those
listeners. The existing RC1 radial-bytecode isolation therefore remains the
first test. An invisible successfully opened wheel is less supported by this
observation. No second variant or package change is justified before RC1 results.
