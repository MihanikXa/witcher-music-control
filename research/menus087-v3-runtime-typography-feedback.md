# Menus v3 — user runtime typography follow-up (17 October 2026)

## Direct statement

> Much better but not quite it, is it

Two 2048x1152 screenshots accompany this statement: current Menus v3 Alchemy/Greater Blue Mutagen, followed by the Ink & Iron mod-page Alchemy/Greater Blue Mutagen reference. User explicitly signals **substantial improvement but remaining dissatisfaction**. Screenshot images are conversation attachments, not included in Git. Do not infer acceptance of non-Alchemy menus or full functional regression from this sentence.

## Assistant observations (inferred, not quoted user requirements)

The two captures now show closely corresponding blue mutagen/item art, selected row ornaments, compact top bar, three-column Alchemy composition and background bottles. **Do not reopen the now-close item art or common geometry based solely on the reference capture's HDR/contrast.**

**Remaining source-grounded visual differences at the identical resolution:**

1. **Typography shape and scale:** The current selected recipe list is narrower/lighter than the reference's engraved-looking letterforms; Alchemy group heading is narrower; the prominent center `GREATER BLUE MUTAGEN` occupies visibly less horizontal width. The reference has stronger relative heading emphasis and wider tracking. Current implementation in `tools/refine-menu-typography.py::qfCaps` converts display strings to uppercase Gentium and sets per-character size to 0.80 for originally lowercase characters. This is a **simulation**, not OpenType small-cap glyphs. The upstream reference uses IM Fell English SC; the user's accepted constraint is to **keep Gentium family**, not old sizes/colors/alignments. It is not physically possible to reproduce IM Fell's glyph shapes exactly while remaining Gentium; improve visual hierarchy and weight/spacing within the chosen family.
2. **Central ingredient warnings remain vivid red:** `Blue mutagen` and `0 / 3` directly below the ingredient icon remain red, whereas the reference shows subdued grey. V3 deliberately muted **list row `Ingredients missing`** but retained individual ingredient warnings as red. This is the strongest unfinished color-role inconsistency. Adjust only the targeted recipe/ingredient text role if user confirms reference treatment; do not globally remove meaningful warning states.
3. **Right body text wraps differently:** Current `Can be used to enhance Abilities or create mutagen decoctions.` wraps to two lines; reference fits on one. Current code preserves prose font/format and column geometry. Compare actual font widths and TextField bounds/size/spacing; a bounded **menu-local body-text typography fit** may solve it without a panel reshuffle. Check long multilingual/localized strings before compressing fields.
4. **Right stat row alignment/order may differ:** Current screenshot puts `Sign intensity` at the left and right-aligns values to the far right; reference visually groups the base value + label + green delta near the left side. This might stem from upstream version, option or item-widget implementation differences, not simply font metrics. Check source/selected-state settings before attempting geometry correction.
5. **Footer hints remain conventional title-case Gentium:** V3 explicitly retains the accepted v2 footer, while the reference has smaller/literary small-caps. Scope changes to menu footer text only; do not touch the shared HUD glyphs, hit areas or controller actions.
6. **Text styling remains inconsistent across roles:** Body prose, selected titles, category heads, labels and hint text do not yet have the same coherent contrast/size/weight rhythm visible in the reference. Do not solve with blanket uppercase, one font-size multiplier or global palette shifts.

## Recommended next narrow task

**Menus v4 typography finishing only**, with one **Alchemy pilot** then applying validated formatting to other menus. Inspect actual decompiled TextFields/TextFormats and small-cap substitutes. Prefer **role-based typography**: calibrated true/simulated small capitals where supported, stronger/wider large titles, more restrained minor labels, menu-local prose metric refinement, consistent disabled/ingredient state palette, subtle footer. Keep appropriate semantic color distinctions. Preserve current item icon module, all original item textures, Bestiary/Map art, common header, background engravings and layout, Hoods/OW/Smooth Map bridges, RC2 HUD and rollback untouched. Before release, compare the exact same recipe at 2048x1152 and test long text, pad/keyboard, scrolling. **No new download or global saturation/HDR tuning indicated by this comparison.**

**Status:** in-game visually much improved, not yet accepted as final. Treat table row size/color suggestions as assistant hypotheses pending review, not independently confirmed user specifications.
