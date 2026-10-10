# Field & Folio interaction typography v1 — private runtime trial

## User-observed runtime result — 11 October 2026

**Explicit user reaction (verbatim):** “Yeah it works, although looks very bold and big”.

Two uploaded in-game screenshots show short `Talk` interaction action names
rendering in the movie-local sans face above the Gentium Book NPC names
`Vesemir` and `Peasant`. **Runtime selection/rendering succeeds**, but the
user considers the current typography **too bold and too large**. This is
functional proof, **not visual acceptance** or all-behavior certification:
held prompts, keyboard/controller icon transitions, bright-background
legibility, long labels and all tested resolutions remain unreported.

The modified `tfActionName` retains the authored 22px font height and the
existing opaque black GLOWFILTER with blur4/strength3/passes1. It selects
Source Sans 3 **Regular**, not Medium or Bold. The combined apparent face
size/x-height, filter and surrounding Gentium contrast plausibly explain why
`Talk` dominates the NPC name; individual causes have not been A/B verified.
The intended hierarchy is that character/name is visually primary and action
hint is secondary. Keep v1 ZIP/hashes unchanged and prepare a separate,
reversible v2 trial at ~19px with a softer field-local shadow/contrast
treatment. Maintain clear text in snow/daylight and dark interiors; do not
silently make instructions illegible. Preserve glyph and controller artwork,
text/hold state, original renderer bindings and accepted UI packages.
See [interaction v2 design gate](../design/field-folio-interactions-v2.md).

**Unchanged control and Regular candidate pass the complete official offline
pipeline. In-game font rendering works, but visual acceptance is withheld due
to excessive apparent size/weight.** User-performed imports are verified;
no installation, deployment, game launch or live settings change occurred.
Accepted QuietFolio English v1, NPC Colors v4 and NPC Shadow v1 are unchanged.

## Exact private package

`C:\Dev\witcher-ui-overhaul\deploy\field-folio-interactions-private-v1\Field-and-Folio-Interactions-v1-private-test.zip`

SHA-256: `6207bca8a9dc5b25711646ca6292f118e604d59c73fa38f299858ecfbd09e5f0`

289,768 bytes. Archive CRC, exact member bytes and Mods routing pass. Repeated
packaging uses fixed timestamps/order/permissions and identical input bytes.
This is a private game-derived test package; generated assets/ZIPs stay ignored.

```text
Mods/modFieldFolioInteractions/content/blob0.bundle
Mods/modFieldFolioInteractions/content/metadata.store
Mods/modFieldFolioInteractions/OFL-Adobe.txt
Mods/modFieldFolioInteractions/FONT-NOTICES.txt
```

The bundle owns **only**:
`gameplay/gui_new/swf/hud/hud_interactions.redswf`.
No fonts_en replacement, NPC asset, script, settings, RU/UA library or
compatibility file is included. Keep accepted QuietFolio v1 enabled: this is
an additional independent role module, not an alternative font-library owner.
Complete Adobe OFL and derivative identity notices are included outside content.

## Proven linkage and exact change

Movie-local DefineFont3 IDs **218 Regular / 219 Medium** coexist with existing
font212 and the unchanged global-font ImportAssets2. DefineEditText **215**
now uses direct **FontID218**, hasFont=true, hasFontClass=false and the original
useOutlines=true. No new `$UtilityFont`, fonts.xml entry, exported AS font class
or speculative WitcherScript call is needed.

The current official Editor importer creates three matching font descriptors:
original Times New Roman plus Quiet Folio Utility and Quiet Folio Utility
Medium. It retains both full utility font definitions and the exact selector;
the official cooker preserves them and resource validation passes. Descriptor
count/name presence is checked; this is not a complete independent decoder of
every opaque SSwfFontDesc property. Actual dynamic rendering remains a user test.

Field215 is `tfActionName`, depth1 in sprite216, used by both normal and held
interaction instances through sprite217. **Only those short action names**
select Source Sans Regular. Medium is embedded and validated for a later
weight comparison, but no visible field selects it in this v1 trial.

Size22px, bounds400×30.2px, positioning, text color, glow, layout flags,
animations, key/button art, holds and visibility remain unchanged. Exact byte
comparison retains all ABC, SymbolClass, other fields and non-image tags.
Normal/held text setters still assign the same field's text. Existing
FriendlyHUD/SAH/compatibility scripts are not changed or regenerated.

## Validation evidence

Control receipt: `build/field-folio-control-v2/receipt.json`.
Candidate receipt: `build/field-folio-candidate-v1/receipt.json`.
Original tools: `tools/verify-field-folio-asset.py`, `tools/package-field-folio.py`.
Source preparation, code-point constructions, licenses and kerning evidence:
[phase1 report](field-folio-phase1.md).

For **both** builds, cook → validate → pack → metadatastore exit 0; each official
validator reports one file, zero resource errors. Exact independent ZLIB
re-extraction reproduces the cooked resource; official metadata inventories
one bundle/entry at the canonical interaction key. Metadata is generated by
the current official tool; a separate full metadata-store consumer is untested.

Both valid CSwfTexture chunks retain GUIWithAlpha/DXTAlpha and one complete mip,
valid CRC, dimensions, pitch/alignment, handle array and matching external-image
linkages. The **entire compressed texture payloads match installed vanilla**:

| Atlas | Dimensions | Full payload SHA-256 |
|---|---|---|
| Main icons `_i1.dds` | 1024×592 | `84966c6937e553a5674cbdd05d95b0df6aba83eaf40821852b5b5500c24c4621` |
| Scroll icon `_i3b.dds` | 40×48 | `dea625e81027822b5504e6536c52ecfdb849bbd95a4d284e21df382f97deb2af` |

Decoded BC3 comparison gives zero full-atlas, image-footprint, one-pixel border
or transparent-RGB differences. The standalone external scroll image is checked
across its full footprint even though it has no DefineSubImage tag.
Saved Editor texture bytes differ before cooking; the official cooker restores
byte-identical runtime payloads. No byte-swap, texture reconstruction or opaque
header edit was implemented to obtain this result.

Generated linkage filenames differ from vanilla because imports use unique
basenames. Resource linkage agrees with GFx ExporterInfo and both atlas links;
all character references and image rectangles remain intact. ID reassignment
is checked semantically rather than hand-patched.

All 383 points per utility weight are preserved: 381 visible nonempty glyphs
and blank space/NBSP with valid advances. Metrics 20480/6676/0; GPOS pair counts
16912/16893. JPEXS independently verifies every glyph and layout record; cooked
font payloads are byte-identical to the verified source. Tabular digits and 16
sample widths pass. Regular's longest sample 270.091px fits the authored 400px
field, without compression or size reduction. Rare glyphs, dynamically supplied
longer labels, baseline appearance and controller-distance readability remain
runtime acceptance items.

Both pipelines emit only the same two established CLI startup assertions:
depotDirectory.cpp:11 trailing slash and soundFileLoader.cpp:101 missing
ly_animal_dog bank. No fresh resource-state or additional CLI assertion occurs.
Editor assertion state remains unknown: its log says Asserts Disabled ON and
contains startup static-shader-cache/CName diagnostics before these imports.
No suppression or assertion setting change was performed. The current CLI
validation evidence does not depend on assuming a clean Editor log.

The first mount attempt hit Windows access denied while renaming an empty
private CLI workspace, before cooking. The staging helper now leaves that
empty directory in place, mounts only the requested resource key, then moves
its own staged file to the output evidence. Original file inventory is restored
and checked on success/failure. Tests cover consecutive reuse. No ACL change,
deletion, new toolchain copy, live depot change or existing project edit occurred.

70 repository tests pass, including rejected unrelated code changes, incomplete
font IDs, failed build receipts, full standalone-image footprints, transparent
pixel accounting and canonical-key staging/restoration.

## Resource hashes and collisions

| Resource/input | SHA-256 |
|---|---|
| Installed vanilla | `5e1ce7d3be052cea8a0ea9d1d744a3fe059fd367bc4bd7ed951fa76d599780e9` |
| Saved unchanged import | `b18f8cfda71aaec3687570d17d8dd729958b399b73b6e695737cd981fe7d63d4` |
| Saved Regular import | `fb70d185ad41ba8d6b2f6a6095e795ba9e0ca00c2049b0ac01008698e93e75a4` |
| Regular source SWF | `f24e345a29be63ed19d3c414e34f9147d5b03a8bc741f80daf0de23ff341f2d4` |
| Cooked control | `fa1ceebb34bcbfe463409c898ce89072c7e9ddb213cdf15c8a280d213638508a` |
| Cooked candidate/re-extraction | `317b4e960a33f8048ba66fa345986d5dcc945ad482b61622f2cb7c878cf3dcaa` |
| Candidate bundle | `fecfbc474f1a9a60b22cffece76e28743669357540b483b94d260983aba1eb62` |
| Official metadata | `2a5edf2a4dc53ac94f525c0f78635914a196a4e4f7641a50094dda79677268e4` |

Current read-only Mods/DLC scan: 32 bundles plus loose interactions resources,
zero owners of this movie. The packager re-reads current installed vanilla and
verifies the accepted v1/v4/shadow ZIP hashes. No load-order override is needed
for this trial based on that scan. This does not certify arbitrary future UI
mods or unobserved runtime formatting/visibility changes.

## User installation and smallest useful test

1. Close the game. Select Vortex **Witcher Compatibility Test**.
2. **Install From File** the exact ZIP above. Check routing to
   `Mods/modFieldFolioInteractions`, enable it and deploy. If Vortex reports an
   interaction-movie resource conflict, stop and report the owner; do not assign
   arbitrary priorities or merge/rebuild scripts.
3. Keep **QuietFolio English v1, NPC Colors v4 and NPC Shadow v1 enabled**.
   Do not change FriendlyHUD/SAH, compatibility packages or subtitle settings.
4. Expected deployed files are under
   `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\Mods\modFieldFolioInteractions`.
   The movie is inside `content/blob0.bundle`, not a loose redswf file.
5. Launch manually. Inspect **Talk**, **Loot/Open**, and one **held** prompt.
   Action names should look sans-serif; NPC names, dialogue and subtitles
   should remain Gentium. Check clipping, baseline/centering and readability
   at normal play distance, including a longer available action label.
6. Switch keyboard/controller if available; verify glyph art, key hint, hold
   progress, completion/cancellation, target changes and HUD hiding/showing.
   Reload a save and confirm the selected face remains. Inspect at least one
   bright background and dark interior. Report actual resolution and any issue.

**One-module rollback:** close the game, disable/uninstall only
`modFieldFolioInteractions` and redeploy. Leave all three accepted mods enabled.
The previous all-Gentium interaction appearance returns using known-good
QuietFolio v1. No settings, saves, compatibility merge or font rebuild needed.

## Reproduce without another import

Choose fresh build/deploy output paths; reuse saved resources and the existing
small CLI runner. Do not run builds concurrently against that runner.

```powershell
& build/font-preparation-venv/Scripts/python.exe tools/verify-field-folio-asset.py --resource build/npc-editor-run/projects/quietfolioutilitytrial/workspace/gameplay/gui_new/swf/hud/hud_interactions_ff_unchanged.redswf --expected-swf build/field-folio-source-v2/input/hud_interactions_ff_unchanged.swf --baseline build/field-folio-source-v2/runtime.redswf --out build/ff-control-fresh
& build/font-preparation-venv/Scripts/python.exe tools/verify-field-folio-asset.py --resource build/npc-editor-run/projects/quietfolioutilitytrial/workspace/gameplay/gui_new/swf/hud/hud_interactions_ff_regular.redswf --expected-swf build/field-folio-source-v2/input/hud_interactions_ff_regular.swf --baseline build/ff-control-fresh/cooked/gameplay/gui_new/swf/hud/hud_interactions.redswf --out build/ff-candidate-fresh
& build/font-preparation-venv/Scripts/python.exe tools/package-field-folio.py --control build/ff-control-fresh --candidate build/ff-candidate-fresh --game 'C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3' --out deploy/ff-trial-fresh
```

No further Editor action is required for v1. Subsequent scope is gated on the
user's visual/functional report; no other utility surface was modified.
