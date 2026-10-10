# English Gentium implementation — 10 October 2026

**SWF source implemented; unchanged Editor/CLI round trip verified; modified
Gentium SWF awaits manual Editor import. No installable font mod yet.**
See the [current control proof and import handoff](gentium-editor-control.md).
NPC Colors v4 and NPC Shadow v1 are accepted and unchanged. This work targets
only `gameplay/gui_new/swf/witcher3/fonts_en.redswf`. No installation, game
launch, live settings changes, compatibility merge, RU/UA font change or other
UI work occurred.

## Implemented conversion

`tools/build-gentium-swf.py` reads the current installed r4gui.bundle EN entry,
requiring SHA-256 `a1223e1a26e0c541a69cb1c6ad8bffbd70c074f1d4603193758b2bf220e95f81`.
It converts independently obtained SIL Gentium Book 7.000 Regular/Italic/Bold
into IDs 1/3/5. The required `PF Din Text Cond Pro` lookup string, style flags,
language byte, stage bounds, frame rate/count and all non-font tags remain
unchanged. This alias is a runtime binding, not a claim of PF Din authorship.
No game/reference font outlines are used in candidate glyphs.

Original serialization implements DefineFont3 wide offsets/codes, quadratic
and straight SHAPE records, initial fill style selection, closed contours,
rounded 20x-em coordinates, actual quadratic-extrema bounds, advances, layout
metrics and pair kerning. Out-of-range fields fail rather than truncate.
SIL UPEM 2048 is converted to the SWF 20480 coordinate scale with inverted Y.
Natural proportions are retained; no global compression or font-size change.

The current runtime has no alignment-zone tags. None are copied from the
native PF Din authoring SWF, where their old hints would be inappropriate.
Three dependent DefineFontName records identify the derivative as **Quiet
Folio Book** and retain attribution. Standard SWF output omits GFx ExporterInfo;
the official importer must regenerate it. No CR2W writer/header patch exists.

All 383 original mappings per style are retained. All **381 visible characters**
have nonempty outlines and valid bounds; U+0020/U+00A0 are correctly blank spaces
with positive advances. Giving spaces visible outlines would damage text layout.
The six upstream omissions are resolved in every style:

| Point | Independently implemented source |
|---|---|
| U+0149 | Gentium modifier apostrophe U+02BC + n, compatibility composition |
| U+2103 | Gentium degree + C |
| U+2105 | Original diagonal c/o construction from Gentium c, slash, o |
| U+2109 | Gentium degree + F |
| U+212B | Canonically equivalent Gentium Å U+00C5 |
| U+212E | Noto Sans estimated symbol from the corresponding style, same-em conversion |

Noto is used for this one conventional symbol only; this is not an auxiliary
sans family or Source Sans trial. The pinned upstream commit, URLs and hashes
are in `src/fonts/noto-estimated-source.json`. Both sources use SIL OFL 1.1.
The Gentium/SIL reserved font names are not used as the derivative family or
PostScript/unique ID. Upstream copyright/license attribution remains. Any final
private package must carry **both complete OFL notices**; none exists yet.

Primary format reference: [Adobe SWF 19 specification](https://open-flash.github.io/mirrors/swf-spec-19.pdf).
Independent sources: [SIL Gentium Book 7.000](https://software.sil.org/downloads/r/gentium/GentiumBook-7.000.zip)
and [pinned Noto source tree](https://github.com/notofonts/noto-fonts/tree/ffebf8c1ee449e544955a7e813c54f9b73848eac/hinted/ttf/NotoSans).

## Verification and layout limits

JPEXS 26.3.0 independently decodes all emitted outlines, code mappings,
advances, bounds, metrics, aliases/style flags and every kerning record.
Regular/Italic/Bold ascent/descent/leading are **19400/5500/0**, taken from
the source hhea metrics. The renderer's use of those metrics is untested.

HarfBuzz 0.56.3 evaluates every two-character combination with GPOS `kern`
enabled and substitution/other positioning features disabled. Conversion
rejects substitutions or placement adjustments that a SWF pair cannot express.
It emits **6,775 / 7,057 / 6,775** records. This includes class/context-sensitive
GPOS observed for two-character runs, not just a legacy kern table. All 18
sample strings match full-run kern-only shaping exactly in each style.
Longer-context positioning and mark shaping cannot generally be represented
by DefineFont3 pair tables; this is not a claim of full OpenType shaping.
Default digits have equal advances in all three styles; punctuation separators
and any numeric pair adjustments are retained in the width checks.

`tools/check-gentium-layout.py` covers names, accents, quotes/apostrophes,
dashes/ellipsis, numbers, menu labels/descriptions, subtitle/dialogue strings
and the six constructed symbols. Regular sampled names are 16–25% wider than
vanilla. All eight sampled names fit the observed NPC field's 625.05px authored
width at the existing 20px size; longest sample is 335.13px. This does **not**
prove adjacent quest-icon placement or dynamically shortened bounds are safe.

Individual gameplay risks, requiring observation rather than global shrinking:

- NPC names: quest-icon spacing, runtime textWidth calculations, unusually long
  localized/procedural names and controller distance.
- Dialogue/subtitles: earlier wrapping and extra lines in long sentences; keep
  existing script-controlled subtitle scale and bounds. No renderer screenshot
  or actual multiline layout has been accepted.
- Menus/settings: long labels and descriptions may wrap or clip; test these
  individually before proposing any geometry change.
- Accent clipping: U+013A extends above natural ascent by 1220/950/1610 SWF
  units in Regular/Italic/Bold (maximum 1.57px at 20px). U+0125 also overshoots;
  several cedilla/comma forms and inverted punctuation exceed descent slightly.
  Stored bounds include these outlines, but runtime masking remains untested.

Private preview `build/gentium-font-source-final/decoded-swf-preview.png` uses
JPEXS-exported fonts. It demonstrates decoded glyph appearance at an enlarged
size, **not in-game rendering**. JPEXS's preview TTF exporter adds a head-table
trailing-byte warning; those TTFs are never production inputs.
51 synthetic repository tests pass. Repeated complete source conversions
produce identical candidate/control SWF hashes; packaging determinism is not
claimed because packaging has not passed its gates.

## Earlier official asset control and metadata stall (historical)

The existing current REDkit `r4data/.../fonts_en.redswf` has the same movie
contracts as the installed resource. Its saved-file SHA-256 is
`4fb81854fc73ce254d1b5e1a5ef2f559e8b87e0205e3314ff87c909d30d7093b`.
A fresh private runner `build/gentium-unchanged-control-v2` staged only this
resource under canonical bin/workspace. Official cook, validate and pack all
returned 0. Validator reported **one file, zero resource errors**. Each logged
only the established depot-trailing-slash and missing ly_animal_dog bank
assertions; none logged the fresh diskFile resource-state assertion.
The official cooker omits the default empty texture-array property; accepting
that omission corrects our inspector, without changing a resource.

Cooked output is byte-identical to installed runtime SHA-256 above. It has one
CSwfResource with valid observed chunk CRC, no bitmap dependency tags, intact
font and non-font contracts including movie header. The ZLIB bundle contains
exactly the EN key; independent decompression reproduces that cooked resource.
Bundle SHA-256:
`2c3282eaac39b36e422ea26ac47b5e47fac16be7ba8f90e42255920bb747a6e1`.

**`metadatastore` stalled before emitting stdout or any wcc.log content.** The
first invocation timed out at 60 seconds; a direct retry was stopped after
about three minutes. One bounded comparison using the previously successful
private shadow runner, against the same new font bundle, also stalled before
logging and was stopped after about a minute. No metadata.store was generated.
This does not establish whether the input, process startup or environment is
responsible. It is not an observed resource-state assertion, nor evidence that
assertions are disabled. No assertion suppression, settings reset or opaque
header workaround was attempted. Only our launched processes were stopped.
No NPC resource was imported, cooked or packaged during that comparison.

At that earlier stopping point the unchanged pipeline did not pass. The candidate
exists as a structurally verified SWF only: no official candidate import/cook,
metadata, Vortex ZIP, deployed path or in-game acceptance is claimed.
Reading 32 currently installed Mod/DLC bundles plus loose font resources found
no competing EN resource owners. Recheck immediately before eventual packaging.
The accepted NPC packages use different resource/script paths and remain intact.

## Reproduction and bounded continuation

Existing source preparation is reused. In the local venv, install pinned
`fonttools==4.60.1 uharfbuzz==0.56.3 Pillow==12.3.0`; no global Python changes.
For an independent fresh reproduction (choose unused output directories):

```powershell
& build/font-preparation-venv/Scripts/python.exe tools/fetch-estimated-glyph-source.py --out build/noto-estimated-fresh
& build/font-preparation-venv/Scripts/python.exe tools/build-gentium-swf.py --game 'C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3' --sources build/gentium-english-source-verified --noto build/noto-estimated-fresh --ffdec build/tools/ffdec/ffdec.jar --out build/gentium-font-fresh
& build/font-preparation-venv/Scripts/python.exe tools/check-gentium-layout.py --build build/gentium-font-fresh
& build/font-preparation-venv/Scripts/python.exe -m unittest discover -s tests
```

`tools/verify-font-asset.py` verifies an officially saved resource against an
expected SWF, then performs cook/validate/pack/metadatastore and exact
re-extraction. It now reuses `build/npc-state-expanded` instead of copying the
toolchain, temporarily mounts only the input, and restores the original runner
workspace on success/failure. New outputs and logs remain separate. Command
outcomes/timeouts are journaled incrementally. The metadata retry and the
subsequent newly imported control both succeeded; the earlier stall's cause is
still unknown. No metadata was fabricated or borrowed from another resource.

Fresh CLI SWF creation still has the previously documented unresolved resource
monitor assertion. Editor import is the established supported route. Computer
Use is prohibited by the user and AGENTS.md: any necessary import must be manual.
The unchanged English-font import and complete round trip are now verified.
The **next manual action is the modified Gentium SWF import**:

1. Launch `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   If it requests depot generation, stop; do not Generate or alter the depot.
2. Open the existing **QuietFolioEnglishTrial** project under
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects\quietfolioenglishtrial`.
   Do not open the compatibility/NPC projects, load a world or press Play.
3. In Asset Browser (Ctrl+A), select `gameplay\gui_new\swf\witcher3`.
   Right-click → Import → Flash SWF; choose exactly
   `C:\Dev\witcher-ui-overhaul\build\gentium-font-source-final\input\fonts_en_qf_book_v1.swf`.
   This unique basename creates a new resource; do not replace depot fonts_en.
4. Save into the new project's workspace, close the Editor, and report the
   saved result and any dialog/assertion. Do not choose Ignore/Ignore All.
   Expected output ends in
   `quietfolioenglishtrial\workspace\gameplay\gui_new\swf\witcher3\fonts_en_qf_book_v1.redswf`.

Leave that resource and logs in place. Do not repeat the unchanged import.
The agent stages saved output at the canonical key in a fresh private runner;
the user need not rename resources or cook/build/install anything manually.

Only after candidate official validation, metadata, exact re-extraction and
collision recheck may a deterministic ZIP be produced, with precisely
`Mods/modQuietFolioEnglish/content/{blob0.bundle,metadata.store}` plus both
license notices outside content. The bundle must own only fonts_en.redswf.
Eventual rollback is disabling that one font mod and redeploying; leave accepted
Colors v4 and Shadow v1 enabled. **No archive is currently approved to install.**
