# Field & Folio — selective English utility typography (next phase)

**Status:** approved direction to continue font replacement work, 10 October
2026. QuietFolio Gentium Book v1 is already user-accepted working in-game.
This is a **new limited typography prototype**, not authority to overhaul all UI.

## Current implementation gate

Movie-local Source Sans 3 Regular/Medium conversion and the exact action-field
font-ID selector are implemented and independently validated. Official GFx
export preserves both fonts and the selector. This leaves the accepted English
Gentium library unchanged. User-performed unchanged/control and Regular candidate
Editor imports are complete. Unchanged and Regular candidate cook, validation,
bundle, metadata and exact re-extraction pass; both full atlases match vanilla
byte-for-byte. A private interaction-only v1 ZIP exists.
See [the validated trial handoff](../research/field-folio-v1-handoff.md).
Runtime font rendering is now confirmed by the user, who reports the v1 action names look “very bold and big.” This is functional success but not aesthetic acceptance. The next bounded task is a quieter ~19px interaction v2 with softer field-local text treatment; see [v2 design gate](field-folio-interactions-v2.md). No further Editor action is needed to reproduce v1; v2 may require a separate manual import.

## Design intent

Keep the accepted independently licensed Quiet Folio Book (Gentium Book
derivative) as the **literary family** for NPC names, dialogue, subtitles,
quest prose, narrative reading and characterful major headings. Investigate
independently licensed **Source Sans 3** as a quieter, more compact family for
selected high-density **utility roles**: short action/interaction prompts,
controller/keyboard hint text where actual text glyphs are used, small menu
settings labels, quantities and compact numerical/statistical labels.

Maintain the restrained *Ghost of Tsushima*–inspired hierarchy without
removing The Witcher's own identity. This is about **role separation**, not
using a sans-serif everywhere or producing another font that merely changes
the three universal normal/bold/italic aliases. Preserve existing icon
glyphs, controller key art, symbol lookup, hint behavior, text positions,
focus and dynamic text/color/visibility contracts.

## Current verified baseline

- Installed English font library key:
  `gameplay/gui_new/swf/witcher3/fonts_en.redswf`.
  Accepted QuietFolio v1 mod replaces this one library, with three
  `DefineFont3` IDs 1 Regular / 3 Italic / 5 Bold and retains all 383
  original code points per style, runtime `PF Din Text Cond Pro` lookup
  binding, and complete supporting license notices.
  [User-accepted handoff](../research/gentium-v1-handoff.md).
- `design/visual-spec.md` already recommends **Field & Folio** as the
  longer-term *two-family* option; this was **not** implemented by the
  accepted single-library QuietFolio swap.
- Runtime font aliases `$NormalFont`, `$BoldFont`, `$ItalicFont`
  resolve through the installed fonts configuration. Simply changing the
  existing three aliases a second time would remove Gentium from narrative
  text; it would not establish role-based font selection.
- The installed resource map records
  `gameplay/gui_new/swf/hud/hud_interactions.redswf` as a prospective
  low-collision first utility movie; it includes `tfActionName` and
  controller/key art driven by the current `hudModuleInteractions.ws`.
  This is a **candidate**, not a proven independent font registration path.
  Its original field has a text-effect/filter and authored sizing; changing
  the face must not change these or the binding behavior.
- The accepted NPC nameplate shadow asset
  `hud_enemyfocus.redswf` and color v4 WitcherScript remain separate.
  Hoods owns inventory, SAH owns wolf HUD, Outfit Wheel owns root/common/
  overlay, other menu/script owners are listed in
  [resource map](../research/resource-map.md) and
  [collision map](../research/collisions.md).

## Gate 1 — prove two-family linkage, before changing utility text

1. Audit current installed 5.01 files, accepted QuietFolio cooked source and
   installed `fonts.xml`. Enumerate the actual embedded font registration
   tags, mappings, `DefineFont3` IDs, internal font lookup strings, dynamic
   text binding behavior, `ImportAssets2`/symbol paths, importer rewriting
   and renderer/Flash constraints. Do **not** claim a new alias/API works
   based only on SWF specification or source comments.
2. Obtain Source Sans 3 (Regular and Medium initially) independently under
   its OFL 1.1 license. Preserve copyright and reserved font-name rules;
   use a derivative name if transformed and avoid representing it as the
   game's proprietary PF Din or as unmodified Source Sans.
   Check EN glyph coverage, punctuation/diacritics, sign/number symbols,
   em metrics, kerning, tabular figures, actual legibility and widths.
3. Establish one minimal reproducible two-family proof: either append new
   independently licensed font definition(s) to the **single canonical
   English font library** while retaining all accepted QuietFolio Gentium
   definitions, or another verified renderer-supported registration path.
   Do not edit or overwrite v1 in place. If the supported importer strips or
   breaks registrations, record the failure and select a smaller documented
   alternative, such as movie-local font embedding, only if actually supported.
4. Validate unchanged controls, serialized font geometry/metrics, symbol and
   alias references, exact non-font resource contracts, official Editor/CLI
   round-trip, metadata generation and clean re-extraction. Check for
   duplicate resource owners and font IDs. No opaque CR2W edits or assertion
   suppression. Use the successful source-to-Editor-to-cook gates from
   `research/gentium-v1-handoff.md`.

**Important deployment rule:** Any revised `fonts_en.redswf` is an
**alternative version/replacement of QuietFolio**. Never enable two
independent mods owning this same canonical English resource simultaneously.
Keep the original v1 package/hash recoverable as the known-good rollback.

## Gate 2 — first practical text-role slice

- Choose exactly **one bounded utility surface** after mapping its actual
  TextField/ActionScript/runtime font resolution. Preferred candidate:
  `hud_interactions.redswf`, **only short action-prompt text** such as
  `tfActionName` if the field and renderer can be switched independently.
  Preserve icon artwork, hold progress, key bindings, positioning,
  action text, prompts, controller/keyboard switching, visibility and
  existing filters/colors initially.
- Compare no-change imported movie against current installed runtime; then
  change only the chosen field/font registration reference. Audit symbolic
  code and font-linkage differences. Do not change colors/shadows, tracking,
  global scale or broader HUD styling as part of this font test.
- Pair the edited utility movie with the canonical revised library in the
  smallest **single private Vortex package** if both are needed, or justify
  a separate role module only if it references a font without a resource
  collision. Do not package an unverified two-family design.
- Validate string lengths, wrapping/ellipsis, accents, a long localized
  action name, normal/held interactions, gamepad button hints, prompts
  hidden by FriendlyHUD/SAH and normal gameplay reloading.
  Readability at 1080p, 4K and the user's projector distance matters;
  don't assert success from desktop SWF previews alone.
- User performs runtime installation/testing manually after Codex supplies
  a private checked archive. Retain reversible v1 option.

## Gate 3 — extend *only* after the first slice is successful

Candidate additions, prioritized by interface benefit and evidence, not
blanket replacement: select compact utility text fields within
`hud_lootfeed.redswf` (e.g., counts), dialogue-choice control hints,
safe settings labels in `panel_ingamemenu.redswf` and only later
inventory/tooltips (Hoods currently owns the inventory resource).
Each surface needs its own exact field/linkage/collision audit and
user-approved trial before a broad roll-out.

If `Source Sans 3` is not actually visually preferable in-game, keep
accepted all-Gentium QuietFolio v1. Font hierarchy is an experiment,
not a mandatory migration.

## Non-goals / safety

- No RU/UA libraries. Do not add generic sans to narrative subtitles,
  dialogue, NPC names or quest reading by default.
- No global replacing `$NormalFont` with Source Sans.
- No automatic text size reduction or artificial font condensation to fit
  denser layouts; assess clipping and layout per selected field.
- Do not merge with existing Brawler/Blood and Steel `general-merge` work,
  music `main`, or rebuild accepted NPC Colors v4 / Shadow v1 assets.
- No Computer Use or GUI automation; ask for exact minimal user-operated
  REDkit import instructions if needed. Codex uses CLI/code otherwise.
- No live Vortex, game install, Documents settings or saves changes.
- No Git commits of downloaded font files, proprietary cooked game data,
  other mod authors' assets or generated ZIPs; original tooling,
  manifests, validation/tests and reproducibility records only.

## Next Codex deliverable

First produce a **specific technical feasibility result** for adding and
binding a second font family, citing real resource/source records. Then,
if safe, proceed immediately to a private **one-surface Field & Folio v1**
prototype with a verified package and clear game test/rollback directions.
Stop only at a concrete unsupported binary/API step or required manual
Editor action; do not open a new broad exploratory UI rewrite.

At handoff report input hashes, font provenance/license, resource key(s),
font IDs and linkage, exact changed field(s), control-vs-candidate
comparisons, official cook/bundle receipts, collision owner review,
archive path and SHA-256 (if validated), and explicit unknowns.
