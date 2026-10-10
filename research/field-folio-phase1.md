# Field & Folio phase 1 — interaction-only source prototype

**Implemented and independently validated authoring SWFs; official GFx export
passed. Manual Editor import is the current dependency. No installable ZIP.**
QuietFolio English v1, NPC Colors v4 and Shadow v1 are user-accepted and unchanged.
Only the new interaction font experiment is active. No installed game, REDkit,
Vortex, settings, saves or compatibility scripts were modified or launched.

## Exact role separation and evidence

Installed `fonts.xml` maps Normal/Bold/Italic/Credits to the language font library.
The current EN family is PF Din's runtime lookup alias, now backed by accepted
QuietFolio glyphs. An arbitrary new `$UtilityFont` alias is **not** established.
Appending a font to that library alone would not select its use in prompts.

Current REDkit libraries demonstrate family coexistence: fonts_ar contains
Arial IDs 1/4 and PF Din ID 6; fonts_zh contains Noto ID 1 and PF Din ID 5.
These were read as technical evidence only; no non-English resource was edited.
The existing ingame-menu movie embeds seven Times New Roman glyphs in Font3
ID 510, referenced by a static TEXTRECORD. Interactions already contains a
local empty Font3 ID 212 and a separate dynamic field 213 bound by FontID.
That empty font is **not** evidence of successful dynamic outline rendering.

The narrower selected route is **movie-local embedding**:

- Add DefineFont3 IDs **218 Regular** / **219 Medium**, independent family
  strings **Quiet Folio Utility** / **Quiet Folio Utility Medium**.
- Change only DefineEditText **215** from `hasFontClass=$NormalFont` to
  `hasFont=true, FontID=218`, retaining `useOutlines=true`.
- Preserve the existing `gfxfontlib.swf` ImportAssets2 (empty symbol lists),
  original Font3 212, all ABC/SymbolClass, shapes, images, placements and timelines.
  Direct FontID selection requires no new exported font class or script/API.

The installed GFx 4.01 / SDK 4.3.27 exporter retains both full Font3 payloads
and the direct field binding **byte-identically**. This verifies serialization
and importer-stage GFx acceptance, **not yet REDkit resource registration,
cooked game loading or rendered runtime resolution**. Those require the next
manual import and eventual in-game trial. No untested new alias is claimed.

Intended single resource key:
`gameplay/gui_new/swf/hud/hud_interactions.redswf`.
**fonts_en.redswf is unchanged.** The eventual role module can coexist with
accepted QuietFolio v1; it is not a competing English-library replacement.

## Exact action field and preserved behavior

Field 215 is placed as `tfActionName`, depth1, sprite216. That action sprite
is `mcActionName` at depth56 within sprite217. Sprite217 is instantiated as
both `mcInteraction` and `mcHoldInteraction`: this one field definition changes
short regular **and held** action names, not key/button labels.

Current native/runtime ABC match. `HudModuleInteractions.SetInteractionText`
assigns `mcInteraction.mcActionName.tfActionName.text`; `handleHoldInput` assigns
the hold instance's text. Neither observed path sets a font or TextFormat.
The installed FriendlyHUD `hudModuleInteractions.ws` invokes the same
`SetInteractionKeyIconAndText` contract and has no font-setting call.
No WS hook is introduced; SAH/FriendlyHUD visibility/input paths remain intact.

Original authored size22px, bounds400×30.2px, color, centered alignment,
leading, HTML settings and opaque black glow (blur4/strength3/passes1) remain
unchanged. Font selection is the only field payload change. Health, NPC names,
dialogue, subtitles and narrative text are outside this resource.

## Independent source and glyph validation

Adobe [Source Sans 3 release 3.052R](https://github.com/adobe-fonts/source-sans/releases/tag/3.052R),
pinned binary-source commit `87b37a2daaed80fcb8e8ccb0085c4d72ddade12e`.
Complete URL/hash pins: `src/fonts/source-sans-3-source.json`.
OFL 1.1, copyright 2010–2024 Adobe; reserved font name **Source**.
Derived identities use Quiet Folio Utility and retain Adobe notices.
Source fonts, derivatives and complete OFL remain private ignored build files.
No reference-mod glyphs or proprietary font outlines are used.

Both weights preserve all **383** baseline English mappings: 381 visible
nonempty glyphs plus correctly blank space/NBSP with positive advances.
Four upstream omissions are resolved: U+2103 degree+C, U+2109 degree+F,
U+212B canonical Å, U+215F superscript1+fraction slash. Components come from
the corresponding independently licensed Source Sans style. No global
condensation, shrinkage or synthetic bold is applied. Medium uses a distinct
face name because SWF only has bold/italic style bits, not a Medium weight bit.

Reused original DefineFont3 converter verifies quadratic outlines, wide offset
and code tables, advances, exact curve bounds and pair kerning. Independent
JPEXS XML checks every serialized glyph, advance, bound and kerning record in
both candidate variants. New IDs do not collide with existing definitions.
Ascent/descent/leading: **20480/6676/0** for both weights. Kerning counts:
**16912 Regular / 16893 Medium**, derived from GPOS through HarfBuzz.

16 prompt/punctuation/accent/numeric samples match full-run kern-only shaping
within per-coordinate rounding (<0.02px at22px). Digits are tabular. The
longest checked phrase fits400px (Regular270.091px, Medium274.203px).
No runtime clipping, long mod-supplied prompt, auto-size, baseline, keyboard/
controller or projector-distance acceptance is claimed.

## Controls, atlas evidence and remaining build gates

Installed runtime SHA-256:
`5e1ce7d3be052cea8a0ea9d1d744a3fe059fd367bc4bd7ed951fa76d599780e9`.
Native/unchanged SWF:
`075e0cf4fa94ea293ad50d8528d0dc0778546794f53a07655885a6156dc4f03d`.
Regular candidate:
`f24e345a29be63ed19d3c414e34f9147d5b03a8bc741f80daf0de23ff341f2d4`.
Medium comparison source:
`ae6e7a961b6784f0440d1c061d62e343407faace66cb04e44d19d7e3c7ac77b1`.

Native vs installed non-image contracts match byte-for-byte; GFx import changes
bitmap tags35/36 into atlas tags1008/1009 and strips old alignment zones73.
Source transformations preserve all original tags exactly except the approved
field binding and appended font definitions/optional attribution tags.
The copied native SWF and fonts.xml were rechecked against the installed REDkit
and have identical hashes. Two complete source preparations reproduce identical
candidate hashes. **64 repository tests pass**, including field isolation,
duplicate font IDs, atlas reference reassignment and invalid geometry rejection.

Both unchanged and Regular official exporter commands return0. Their141
subimages have identical character IDs, bounds and semantic atlas descriptors.
The exporter assigns the main atlas ID0 vs1; every subimage reference follows
that assignment consistently. This is checked semantically, not patched.
The two atlas records match after ID normalization. `-ne`, observed in the
existing official Editor command, does not emit texture pixels in this probe.
**Pixels and full cooked texture metadata remain unverified.** No raw GFx is
packaged. Editor import must reconstruct actual CSwfTexture data, followed by
control/candidate cooking, atlas pixel checks, validation, metadata and exact
single-resource re-extraction before a ZIP may be produced.

Read-only current Mods/DLC scan:32 bundles and loose resource scan; zero
interaction-movie collisions. FriendlyHUD owns its WS implementation, not this
movie. Accepted font/color/shadow packages have different resource/script keys.
This does not establish all runtime compatibility.

## Minimal manual dependency — perform once

1. Start the existing isolated Editor:
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   Create a **new** project named **QuietFolioUtilityTrial** inside
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects`.
   Do not open/change the accepted font/NPC projects or generate another depot.
   If depot generation is requested, stop and report it.
2. Asset Browser (Ctrl+A): select `gameplay\gui_new\swf\hud`.
   Right-click → Import → Flash SWF; import **both** of these unique sources:

   ```text
   C:\Dev\witcher-ui-overhaul\build\field-folio-source-v2\input\hud_interactions_ff_unchanged.swf
   C:\Dev\witcher-ui-overhaul\build\field-folio-source-v2\input\hud_interactions_ff_regular.swf
   ```

3. Save both to the **new project's workspace**, close the Editor and report
   any dialogs/assertions. Do not overwrite depot hud_interactions, choose
   Ignore/Ignore All, cook manually, install a mod or launch the game.
   Outputs should retain the unique basenames under that workspace's
   `gameplay\gui_new\swf\hud` directory.

Medium is prepared and decoded for later comparison; **do not import it now**.
Two files are the complete next action: unchanged control and Regular candidate.

This dependency follows [AGENTS.md](../AGENTS.md): “Necessary GUI steps must
be performed manually by the user; provide exact isolated-project instructions
and stop at that dependency.” Computer Use/GUI automation is prohibited.

After those files exist, the agent will reuse the small existing CLI runner,
check unchanged/candidate contracts and both texture atlases, then run official
cook → validate → pack → metadatastore → exact re-extraction. No toolchain or
full depot copy is needed. **No ZIP currently exists or is approved to install.**

Once packaged, the first user test will compare Talk/Loot/Open/held prompts,
keyboard and controller hints, hold progress, reload and HUD visibility while
NPC names/dialogue/subtitles remain Gentium. Keep Colors v4 and Shadow v1 enabled.
Rollback will disable only the new interaction-role module and redeploy;
known-good QuietFolio v1 remains enabled and recoverable without rebuilding it.

## Reproduction

```powershell
& build/font-preparation-venv/Scripts/python.exe tools/fetch-source-sans-3.py --out build/source-sans-fresh
& build/font-preparation-venv/Scripts/python.exe tools/prepare-field-folio.py --game 'C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3' --native build/npc-editor-run/r4data/gameplay/gui_new/swf/hud/hud_interactions.swf --sources build/source-sans-fresh --ffdec build/tools/ffdec/ffdec.jar --out build/field-folio-fresh
& build/font-preparation-venv/Scripts/python.exe tools/check-field-folio-layout.py --build build/field-folio-fresh
& build/font-preparation-venv/Scripts/python.exe tools/probe-field-folio-export.py --source build/field-folio-fresh --exporter build/npc-editor-run/bin/tools/GFx4/gfxexport_mult4fix.exe --out build/field-folio-export-fresh
& build/font-preparation-venv/Scripts/python.exe -m unittest discover -s tests
```

Choose unused output folders. Source SWF determinism is checked independently;
official cooked/package determinism cannot be claimed before the manual gate.
