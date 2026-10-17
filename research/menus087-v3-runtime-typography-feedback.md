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

## New direct user alignment correction — 17 October 2026

Two new tightly cropped current/reference Alchemy ingredient-list screenshots were supplied, and the user explicitly says:

> I agree with those: I would now leave the icons, navigation, layout and background entirely alone. Focus on better small-cap proportions and heading emphasis, consistent secondary-text coloring, prose sizing, and menu-footer typography. We can get closer to the reference, although retaining Gentium means the exact letterforms will necessarily differ from IM Fell. But also pay attention to these. The alignment is different.

**Direct requirements:** (a) preserve icons, header/navigation, overall layout and background; (b) complete the Gentium-small-cap/prose/color/footer finishing; (c) **correct text alignment** as a first-class typography task. These outrank the earlier assistant-only description of an isolated style mismatch.

**Screenshot-grounded alignment interpretation (assistant analysis, not user quote):** The selected row's box, icon and title appear close in relative placement after allowing for different crop/scaling; the subordinate `Ingredients missing` line sits **much farther below the name** in our version than in the mod-page reference, nearly touching the bottom selection border. Both the selected and unselected rows appear to have excessive title-to-status vertical distance. Horizontal left edges for title/status are comparatively close to reference after normalizing crop scale. This is **an internal two-line group vertical-alignment and baseline/line-height defect**, not evidence that the entire list or icon grid needs translating.

**Diagnosis boundary:** V3 `tools/refine-menu-typography.py` applies per-character uppercase+size changes via `qfCaps()` / `setTextFormat`, while its build report says no SWF display-list position/shape tags changed. An existing `inkOwnTF` row positioning assumption may be incompatible with changed glyph ascent/textHeight; alternatively, explicit dynamic row label/status `y`, `height`, `autoSize`, TextField vertical alignment or selection bounds may be responsible. **Do not claim a specific operation caused the misalignment until measured from the decompiled live `ItemCraftingModule` and compiled movie.** Merely changing `size * 0.80` or blanket moving every text field up may not resolve it and risks other list elements.

**Next bounded correction:** Measure the label, secondary status and icon bounds relative to each actual row and selection rectangle for both normal/selected states at 2048x1152; compare source `inkRow`/`inkOwnTF` field positions/textFormat and calculated line metrics against reference geometry. Make **the smallest menu-local change to the secondary-label text-field baseline/anchoring** to re-form the intended compact two-line group. Apply the same pattern to Crafting and similar list rows **only where the same contract is verified**. Preserve arrow, selection outline, icon, hit areas, row height and scrolling/keyboard/controller navigation. Then tune small-cap proportions/heading weight/tracking and remaining color/body/footer styles without moving global menu columns or changing art/HDR. Add tests for title/status relative geometry if accessible and require a screenshot/repeated selection in-game.

