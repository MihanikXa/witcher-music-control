# Field & Folio interaction v2 — correct oversized/heavy action names

## User feedback and success criterion

11 October 2026 explicit result: **“Yeah it works, although looks very bold and big”**. Subsequently the user explicitly clarified: **“I think interaction prompts should be subordinate to the names, so maybe even smaller, and I think we need that NPC Shadow v1 treatment everywhere in text where the stronger shadow was used.”** The priority is now an **unambiguous hierarchy**, rather than a mildly smaller alternative.
Screenshots: `Talk` in utility sans visually dominates `Vesemir` and
`Peasant` in accepted QuietFolio Gentium Book. Interaction font linkage and
in-game rendering are therefore successful, but **visual hierarchy is not**
user-accepted. v1 is a **functionally working baseline** and its archived
package/hash must remain unchanged. See
[documented in-game observation](../research/field-folio-v1-handoff.md).

Desired behavior: NPC name remains the principal text; the nearby `Talk`
action is noticeably smaller, lighter and secondary without becoming
illegible. The bold look was **not a Bold/Medium face mistake**: DefineEditText
215 selects FontID 218, Source Sans 3 Regular. Apparent heaviness can result
from the unchanged opaque black GLOWFILTER blur4/strength3/passes1 and large
22px original fontHeight, as well as the larger sans x-height relative to
Gentium. Do not assert which cause dominates until comparing variants.

## Candidate for the next manual runtime test

Start with **17px Source Sans 3 Regular**, with a separate 16px source candidate if needed for an even quieter result. This is a visual trial, not a presumption that any fixed pixel target equals a specific apparent size. Aim for approximately 70–80% of the **perceived prominence** of the NPC name without sacrificing readability. Keep the accepted 20px Gentium NPC name unchanged. No artificial width scaling or font-weight change. The authored field height is 30.2px, field width400px,
centered horizontal alignment; preserve semantic positioning and text setters.
If fontHeight is encoded as 440 twips at 22px, verify new size through an
independent decoder (target 340 twips for 17px, 320 twips for 16px). Changing font height can alter
vertical baseline: check it in the authored movie and then game, and apply
only a demonstrably needed narrow y-offset if evidence requires it.

Replace the **field-local heavy black glow** on the relevant named
`tfActionName` placement (not globally) with a soft, restrained shadow
treatment. Reuse the accepted NPC shadow design as an aesthetic *reference*,
not a blind copied filter binary: alpha≈166/255, blur2, strength1, distance1,
near-charcoal #141718 are candidate values. First inspect exact filter type,
character/placement path, fields and the control source; preserve all flags,
angle, passes and unrelated filters unless explicitly part of this patch.
This is a design candidate, not a proven bright-snow contrast solution. The same accepted NPC-shadow **visual language** is now the broader cross-UI goal, detailed in [text shadow unification](text-shadow-unification.md). Keep the interaction v2 prototype one resource and one affected field; do not put global patches inside it.

If the combined size/effect change becomes too small to read, test 18px or a slightly firmer local shadow; if still too dominant, test the separately prepared 16px source candidate. Distinguish size from shadow effects with independent checks where practical. Do **not** darken/grey/desaturate the
foreground text by default to reduce prominence: background contrast varies.
Do not hide interaction text as a means of 'fixing' its appearance.

## Technical boundaries and safety

- Work on **`ui-overhaul`** only; Blood and Steel/Brawler stays on
  `general-merge`, audio stays on `main`.
- Modify only the interaction movie
  `gameplay/gui_new/swf/hud/hud_interactions.redswf`.
  Preserve movie-local Source Sans 3 Regular/Medium IDs 218/219, 383-point
  coverage, license/derivative attribution and existing QuietFolio independent
  English library. Keep all accepted NPC color/shadow/font packages unchanged.
- Isolate exactly field 215 `tfActionName`, corresponding PlaceObject3
  filter if present in relevant sprite/placement, and any minimal vertical
  offset necessary to maintain alignment. Verify that normal and held
  instances are affected as intended; no other field or interaction icon.
- No Flash ActionScript/ABC, scripts, SymbolClass, timelines, texture atlas
  pixels, interaction key icons, hold/completion/visibility behavior, root
  menu, player controls, input mapping, NPC names, dialogues/subtitles, or
  gameplay values may change.
- Develop a deterministic parametric/source transform from v1's pinned
  authoring source, with robust structural parsing of the text-field, filter
  and placement. Do not use byte-offset guesses for a movie or rewrite
  native REDkit/CR2W headers manually.
- First verify source-level SWF delta, glyph bindings, textHeight and exact
  filter scopes. Then independently import via verified supported tooling,
  cook/validate/pack/metadata/re-extract and compare both complete atlases
  with current installed vanilla, plus v1 contract preservation. No
  assertion suppression or unverified binary modification.
- If an Editor import/save must be performed manually, stop and give user
  exactly the bounded unique-file steps; **never use Computer Use or
  desktop automation**. Reuse existing private CLI runner for the rest.
- No edits to live Mods, Vortex, saves, user settings, or controller software.
  Build separate v2 package with its own manifest/ZIP hash and reversible
  ownership. v1 and v2 may **not** be enabled simultaneously because both
  own the interaction movie; keep v1 available for rollback. Keep accepted
  QuietFolio, NPC colors/shadows enabled.

## Bounded runtime acceptance

Compare the same `Talk` over Vesemir and `Talk` over Peasant views with v1
at unchanged display scale. Confirm clearly subordinate, smaller and softer action label, NPC name
visually dominant, no overlap with yellow quest icon, no baseline shift or
unintended second line. Confirm a held prompt, longer interaction, gamepad
key-art/hide/show and snow/sky or other bright background along with dark
interior. Test at the user's actual resolution/viewing distance. On issue,
disable v2 and re-enable preserved v1 through Vortex; no other mod change.

## Codex output

Commit original parameterized transform and tests/reports, not game
assets/font binaries/third-party files. Report exact tag/filter/placement
identifiers, changed bytes/contracts, unchanged resources, control/candidate
cooking receipts, v2 private ZIP/hash and risks. **Do not reopen the
successful Gentium v1, color or shadow work.**
