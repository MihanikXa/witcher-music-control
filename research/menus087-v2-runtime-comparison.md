# 0.8.7 Menus v2 — first visual runtime comparison

**17 October 2026.** Two images supplied by the user: (A) current Alchemy/Blue Mutagen and (B) mod-page Alchemy/Greater Blue Mutagen reference. Both 2048 × 1152. Images stay in the conversation; this note contains only observations. The two captures depict **different saves/item selections** (level 1 Blue Mutagen vs level 2 Greater Blue Mutagen), so numerical differences and recipe contents are NOT parity defects.

**User's explicit statement (verbatim):**
> It looks substantially right now, except for some stuff, can you identify what and why that might be

This is **positive partial visual feedback** after v2; user has not approved every element or confirmed controls/Hoods/Map/HUD regression checks. Distinguish it from previous v1's major rejection.

## Observed improvements and remaining differences

- The slim unified navigation with medallion, compact stats, subtle highlighted current tab and background Alchemy bottle engraving **now visibly render**. This is strong evidence that v1's shadowed shared `panel_common` / `inkart:` issue has been addressed in the current screenshot, **not proof of every other menu's effective owner**.
- The actual three-column Alchemy composition, selection frame and recipe structure closely match the reference. Do not reopen a wholesale Alchemy geometry rewrite.
- **Small-caps and typographic role mismatch:** in A recipe names and "Ingredients missing" labels use ordinary mixed-case Gentium and are heavier/less restrained; reference B has distinctive IM Fell English SC-style small capitals, finer secondary labels and more articulated hierarchy. Header/item-list labels and footer have similar treatment difference. The accepted Gentium library is deliberately retained: v2 applied a **TopBarNew ascent-based metric correction only**, not a role-based menu typography pass. A future implementation should preserve Gentium glyph family while changing *menu-local* case, size, weight, tracking, alignment and color—possibly using a verified Gentium-derived small-cap treatment or safe text styling. Do not silently swap in IM Fell or globally uppercase source strings that are used outside display text. Test lengths and clipping.
- **Icon appearance:** vivid blue/green/red mutagens in A versus muted, engraved-looking ingredients in B. The v2 release explicitly left the optional **Ink & Iron Icon Pack** out, and current v2 added **Bestiary Art and Map Inked**, not the Icon Pack. This is a strong likely source of missing icon art; confirm exact current texture owners, the original icon pack's resource keys and conflicts (especially Brothers in Arms or other installed item icon mods) before a new private candidate.
- **Missing-ingredient palette:** A displays vivid red `Ingredients missing`, while B shows muted grey small-cap text. This alone is not proof of a broken current UI. The author's 0.7 changelog (Nexus mod 13111) **explicitly introduced red missing-ingredient labels**. The reference gallery may be from an earlier version. Choose muted grey only after explicit user preference; record it as a custom styling choice rather than a missing upstream fix.
- **Background tone:** A's empty near-black fields visibly darker than B; sampled representative empty-background RGB medians on a 2048×1152 comparison approx A 5/5/5 vs B 10/10/10; reference has a more perceptible Alchemy etching. This could reflect menu backdrop alpha/color, brightness/gamma or reference screenshot processing; image comparison does not identify the runtime cause. Avoid blindly brightening all UI; inspect source menu/background layers and actual in-game option state.
- **Header size/weight and line spacing:** the authored top-bar placement is now present, but letterform widths and apparent weight differ with Gentium vs IM Fell; likely typographic adaptation task, not old top-bar resource still winning.
- **Do not compare item value, recipe ingredient ratio, gold/level, or exact selected-row scroll offset as styling defects** because the screenshots are not state-matched.

## Latest user clarification — 17 October 2026 (explicit; supersedes inferred priorities)

> I think saturation and contrast is probably hdr, the main problem is typography and text color. And the icons don't look right too.

**Explicit user evidence/preferences:** The user identifies **typography and text color** as the primary remaining visual problem; **icons** also look wrong. They think capture/HDR explains apparent saturation and contrast differences. These are user judgments and a plausible capture hypothesis, **not confirmation of a measured HDR transfer function**. Do **not** initiate background brightening, global saturation changes or contrast adjustment simply to match the two differently captured screenshots.

**Next task order (assistant interpretation of user priorities):** (1) Menu-local typography system with retained Gentium/QuietFolio font family but source/reference-driven size, hierarchy, small-caps treatment, tracking, alignment, secondary text color, focus/disabled states and footer; (2) exact original 0.8.7 All-in-One **Icon Pack** provenance and effective texture ownership, with an optional art-only private integration preserving meaningful correction mods; (3) any contrast/HDR tuning only after a controlled SDR/HDR apples-to-apples comparison and a separate user request. Do not reopen fixed shared header/Alchemy geometry. Keep accepted HUD RC2 and independent art/Map fixes unchanged.

**Validation:** Prefer matched item/recipe, same display settings and image output for visual comparison; inspect compiled TextField/TextFormat/AS formatting rather than treating missing IM Fell SC as a license to replace the chosen Gentium family. Avoid blanket uppercasing localized data and check long labels. Ask user to review an in-game typography + icon candidate rather than claiming screenshot parity from static tests.

## Previous assistant narrow scope (superseded where priorities conflict)

1. Preserve the now-functional shared 0.8.7 menu/header/engraving integration and frozen accepted HUD RC2.
2. Audit the separate original upstream **Icon Pack inside the pinned 0.8.7 All-in-One** against currently installed icons, and a BIA/other corrected texture collision ledger. Build one optional, reversible art-only candidate if it gives closer reference fidelity without overwriting accepted repairs.
3. Perform a **menu-only typography pass** informed by the author's role-based IM Fell / IM Fell SC distinction while preserving QuietFolio/Gentium as the font family. Compare screenshots at identical resolution, selected item and settings where possible; adjust font weights/size/smallcap treatment/line metrics/secondary color/focus contrast. No universal `fonts_en` replacement or gameplay HUD change.
4. Inspect menu background color/alpha independently to understand the measured brightness delta; don't assume current black is a broken artwork load.
5. Run focused visual tests in Alchemy, Glossary/Bestiary, Quests, Character, Inventory and shared navigation; manual game test remains necessary.

**Status:** v2 visually much closer per user; exact typography/icon/background finishing remains to be accepted. This feedback is not authorization to auto-deploy or edit live Vortex.
