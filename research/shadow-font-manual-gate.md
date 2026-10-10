# Shadow and English Gentium source phase — 10 October 2026

Color work is closed by user acceptance. Original v4 source and private ZIP
remain unchanged (SHA-256 `1b9d70f775ac1cf4173739fa01325d65ead2bdb9c1aeb363dac548c03f6b82b7`
and `94f39861fa552d7a3353c17831a55751171a321b3df8a73c211f995bb690036e`).
Neutral/friendly/VIP were observed; hostile/Axii were accepted without direct
observation. No new color work is required.

## Track A: manual Editor dependency, no shadow package

The existing copied Editor is `build/npc-editor-run`. Before the user's new
no-Computer-Use instruction, one supported launch call was issued and returned
without an error. No GUI input, project creation, checkout or import followed.
Subsequent process inventory showed no editor process, and no new project was
found under the intended projects directory. A successful launch call does not
prove a running Editor. No further Computer Use is permitted or proposed.

The unchanged Editor import/control, assertion comparison, cook/bundle/re-extract
and metadata/atlas gates are **unexecuted**, not passed. The earlier CLI findings
remain in [native validation](native-npc-validation.md) and
[Editor workflow](editor-workflow-bounded.md). No new CLI bootstrap variations,
opaque header edits, assertion suppression or older cooked substitute was used.

**Shortest user action, stop before cooking or deployment:**

1. Launch `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   If it requests depot generation, stop; do not Generate. Expected existing
   depot is `E:\TheWitcher3RMDepot\`. Do not open the compatibility project.
2. Create a new project named `QuietEditorialNPCShadowGate` with location
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects`.
   Verify the preview and resulting workspace stay beneath that directory.
   Do not load a world or press Play.
3. In Asset Browser (Ctrl+A), select `gameplay\gui_new\swf\hud`. Import the
   unchanged native `hud_enemyfocus.swf` from
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\r4data\gameplay\gui_new\swf\hud\`.
   The documented community menu is right-click → Import → Flash SWF;
   report actual labels if different. Confirm checkout/replacement only into
   this new project's workspace, never uncook/r4data or an existing project.
4. Import unchanged `hud_watermark.swf` from the same source folder once as the
   control. Save both resources. Note whether each operation created a fresh
   workspace resource or merely overwrote a previously loaded/checked-out one.
   Record any assertion, especially `diskFile.cpp:2633` monitor-loaded state.
5. Close the copied Editor. Send the new project/workspace path and the import
   result or exact error. Leave its logs and two workspace resources in place;
   they stay local and can be inspected directly. No cook, publishing, Vortex
   installation or game launch is requested at this stage.

If either import asserts, preserve the evidence and stop. Otherwise the agent's
next task is official isolated cook and single-key pack/re-extract, comparing
all code/symbol/timeline/placement contracts, used atlas regions/borders and
full padding differences, chunk properties/CRCs and exact resource key.
File existence or SWF parse success alone does not discharge those gates.

After passing them, the only intended changed placement is sprite 63,
character 38, depth 35, `mcNPCFocus.tfName`'s existing DROPSHADOWFILTER:
RGB `#141718`, alpha 166/255, blurX/Y 2, strength 1, distance 1. Preserve angle,
passes, flags and all other placement/filter data. No palette/AS/font/layout
change. Keep v4 enabled independently for that later test. A shadow-only
archive does not exist yet, and no shadow transformation was applied early.
Later rollback will disable only that shadow module, retaining v4.

## Track B: licensed source preparation, no font package

`tools/prepare-english-gentium.py` reads the current installed r4gui.bundle
directly, validates the EN entry, inspects DefineFont3 layout, and prepares
decomposed quadratic outline command data from independent upstream fonts.
It writes only to a fresh ignored build directory; it cannot cook or package.
Prepared data is in `build/gentium-english-source-v3`, including original
Regular/Bold/Italic TTFs, SIL OFL/copyright, FONTLOG and README, a runtime
baseline copy, per-style outline source JSON and a detailed receipt.

Upstream is [SIL Gentium Book 7.000](https://software.sil.org/gentium/download/),
downloaded freshly with normal Windows TLS validation. Python urllib rejected
the site's certificate as expired; no TLS validation was bypassed. Windows
Invoke-WebRequest succeeded, and its ZIP hash exactly matches the previously
obtained independent SIL cache:
`fa4e35bcea62dd68befabf4bb7c2765aacd2691f51ec8ae008f5f913ef49f419`.
No reference mod glyphs or assets were read/copied for this preparation.

Current installed EN resource SHA-256:
`a1223e1a26e0c541a69cb1c6ad8bffbd70c074f1d4603193758b2bf220e95f81`.
All three records retain the internal `PF Din Text Cond Pro` lookup string;
current fonts.xml routes Normal/Credits, Italic and Bold aliases via this
family and style flags. **Verified order is ID1 Regular, ID3 Italic, ID5 Bold**,
not the earlier shorthand regular/bold/italic ordering. Each has 383 entries.
The first source-preparation attempt rejected that wrong style assumption;
no output was accepted until flags were read and corrected.

SIL input TTF hashes match the earlier independent upstream evidence:

| Style | SHA-256 |
| --- | --- |
| Regular | `2027f6a864e5a9907c113438969d1d03fa91dfdd1a3885fa0fdeb496f0f682e4` |
| Italic | `ed128fd9370533c796219d48aaf17b55d0562791f8cc49e83a6c607c5680bea2` |
| Bold | `ed788447ea4298dd44ac62034b9a6849003bdfea256757cb4a5d599c8b09a365` |

Each supplies 377 of those 383 baseline code points. Missing in all three:
U+0149 (deprecated apostrophe-n), U+2103 (Celsius), U+2105 (care of), U+2109
(Fahrenheit), U+212B (Angstrom), U+212E (estimated symbol). Do not silently drop
them or copy proprietary PF Din glyphs. Canonical Å for Angstrom and original
compositions from licensed component glyphs are candidates, not implemented
coverage. Complete source coverage is an additional font gate.

The prepared outlines use decomposed TrueType pen commands, normalized from
2048 UPEM to 20480-unit EM with inverted Y. Adobe's
[SWF specification, DefineFont3](https://open-flash.github.io/mirrors/swf-spec-19.pdf)
specifies twentyfold glyph-coordinate resolution. This is **source geometry
preparation**, not SWF SHAPE serialization. Implied quadratic on-curve points,
integer rounding, contour fill/winding, per-glyph bounds, kerning conversion
and align-zone regeneration remain unvalidated. Do not preserve PF Din's
alignment zones blindly for new outlines.

Observed baseline ascender/descent/leading values:
Regular 18100/4240/1860; Italic 18440/4240/2200; Bold 18900/4400/2820.
Gentium hhea metrics are 1940/-550/0 at 2048 UPEM for each style. These are
different vertical proportions; translating source metrics without testing can
change clipping and baseline placement. Current TextField bounds/sizes/leading
and script subtitle size `26 + SubtitleScale` must remain unchanged.

Baseline regular/italic have 809/706 kerning records, bold zero. Upstream has
GPOS kern/mark/mkmk, no legacy kern table. GPOS class/pair adjustments cannot be
replaced with the assumption that a missing legacy table means no kerning.
Conversion must enumerate relevant BMP pairs and respect supported lookup
types; advanced combining-mark shaping is not established for this renderer.
Keep precomposed accents and test apostrophes, quotes, dashes, ellipsis and names.

Unkerned equal-EM width comparisons are source estimates, not live textWidth:
Regular Roach +16.9%, Vesemir +19.4%, Kaer Morhen +19.9%, digit string +9.3%.
Italic names are about +5.9–8.3%; bold names about +14.4–16.3% for these samples.
Default digits are tabular within each upstream style (986/859/1061 units).
This preserves within-style numeric alignment, not existing cross-style widths.
Wider names can move quest icons positioned using tfName.textWidth; menus and
subtitles can wrap sooner even when their geometry is unchanged. Controller
distance, 1080p/4K legibility and dynamic wrapping still require a real trial.

Preserve the runtime library's non-font contracts and regular/italic/bold
bindings. Controller icons may use other libraries; coverage of this EN table
alone is not proof of every input icon. No Source Sans, RU/UA or new family
architecture is introduced. Full OFL notices stay beside private prepared
fonts. A derived distributable font must comply with the OFL and its reserved
Gentium/SIL names; distinguish the mandatory game lookup string from upstream
family identity and never represent derived outlines as proprietary PF Din.
See [OFL requirements](https://openfontlicense.org/ofl-faq/).

Font import/cook is not tested or installable. **No user font action is needed
yet:** first provide Track A's two unchanged Editor imports. Then continue the
font conversion/coverage gate in isolation and validate unchanged fonts_en
import/cook before a separate EN-only module.

## Reproduction and repository boundary

```powershell
python -m venv build/font-preparation-venv
& build/font-preparation-venv/Scripts/python.exe -m pip install fonttools==4.60.1
Invoke-WebRequest -Uri 'https://software.sil.org/downloads/r/gentium/GentiumBook-7.000.zip' -OutFile build/GentiumBook-7.000-reverified.zip
& build/font-preparation-venv/Scripts/python.exe tools/prepare-english-gentium.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --archive build/GentiumBook-7.000-reverified.zip --out build/gentium-english-fresh
```

Original tooling, synthetic bounds tests, reports and hash/metric summaries
belong in Git. Proprietary baselines, open-font binaries/outline dumps, logs,
venv and generated resources remain private/ignored. Neither shadow nor font
has a private Vortex ZIP. Installed game/REDkit/Vortex/compatibility/saves/settings
were not modified. No game was launched.
