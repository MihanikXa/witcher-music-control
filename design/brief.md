# Design brief — Quiet Editorial

## Target
Make The Witcher 3's interface feel lighter, modern, spacious and deliberately designed while retaining warmth and literary texture.

References:
- The restraint, hierarchy, scene integration and subtle material character in *Ghost of Tsushima*.
- Gentium Book from the user's *Easier to Read* font mod as the primary **taste reference**.
- The vanilla Witcher UI for its grounded universe-specific visual cues, **not** its harsh text outlines or neon semantic colors.

## Typographic hierarchy (provisional)
1. **Display / chapter / location:** characterful literary face, lightly weighted; restrained tracking.
2. **NPC names / dialogues / subtitles:** comfortable readable type with minimal or no hard stroke, clear separation from the scene, normal-case labels unless authored otherwise.
3. **Gameplay instructions / small labels / menu controls:** simple supporting family or weights; avoid cramped decorative small caps.
4. **Numbers, controller hints and alerts:** high legibility, tabular figures where helpful, no extraneous boxes.

Do not choose a font solely because it is serif or sans. Compare sizing, weight, spacing, glyph coverage, readability and in-game placement.

## Semantics (illustrative, not hardcoded globals)
- Primary: soft warm ivory.
- Secondary: slightly cooler stone.
- Friendly / ally: muted light sage.
- Hostile / danger: warm low-chroma oxide/brick.
- Selected / interactable: quiet old brass, with complementary position/shape signals.
- Disabled / background: low emphasis without becoming invisible.

Check semantic distinguishability and contrast across backgrounds and color-vision profiles; saturated colors should be reduced by targeted rules, not by a universal filter.

## Rendering treatments
Reduce thick solid black strokes. Prefer subtle shadow or small translucent backing only where dynamic scene brightness needs it. Account for varied resolution/HDR and bloom. Avoid relying on CSS-like controls unless verified in Scaleform or WitcherScript.

## First visual proof
The floating NPC nameplate shown in the user's Yennefer screenshot: muted color, less outlined, smaller/airier proportions, readable against dark interiors and bright daylight. Compare neutral, friendly, hostile and special targets using the same system. Preserve targeting and interaction cues.

## Validation before rollout
Character names; hostile targets; quests; dialogue choices; subtitle sequences; inventory; item rarity; loot names; skill screens; Gwent; options menus; day/night/snow; native language and Cyrillic glyph coverage; 1080p vs 4K; current Seamless Adaptive HUD/FriendlyHUD coexistence.
