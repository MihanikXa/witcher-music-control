# English Gentium Book v1 private trial — 10 October 2026

**Offline validation passed; in-game acceptance is pending.** No installation,
deployment, game launch or live settings change was performed. NPC Colors v4
and NPC Shadow v1 source/package hashes remain unchanged.

## Package and exact scope

`C:\Dev\witcher-ui-overhaul\deploy\gentium-english-private-v1\QuietFolio-English-Gentium-Book-v1-private-test.zip`

SHA-256: `220a4d1427544567210e66d55a797cd909fd0d337a1fc7c7e4ef78ad114f37da`

196,881 bytes. Two independent packaging runs produce identical archive hashes;
ZIP timestamps, member order and permissions are fixed. CRC and every member's
bytes were checked. This game-derived package is for private testing only.

The archive contains exactly:

```text
Mods/modQuietFolioEnglish/content/blob0.bundle
Mods/modQuietFolioEnglish/content/metadata.store
Mods/modQuietFolioEnglish/OFL-SIL.txt
Mods/modQuietFolioEnglish/OFL-Noto.txt
Mods/modQuietFolioEnglish/FONT-NOTICES.txt
```

The bundle contains exactly one resource:
`gameplay/gui_new/swf/witcher3/fonts_en.redswf`.
There is no loose fonts_en.redswf, Russian/Ukrainian library, NPC asset, script,
settings file or compatibility patch in the ZIP. Installed Mods/DLC scan:
32 bundles, zero English-font owners; loose English-resource scan also clear.
This is a file/resource collision check, not proof of all runtime interactions.

## Implemented and verified

Only DefineFont3 IDs **1 Regular / 3 Italic / 5 Bold** change relative to the
installed movie, apart from official regenerated ExporterInfo. Runtime aliases,
style/language flags, font-registration descriptors, movie bounds/rate/frames,
all other movie tags and default empty texture state are preserved. No UI
geometry, text sizes or subtitle scaling were changed.

Independent SIL Gentium Book 7.000 outlines retain natural proportions. The
six missing points are independently constructed/licensed as documented in
[the conversion report](gentium-implementation.md). Every style retains all
383 mappings: 381 visible nonempty glyphs and correctly blank space/NBSP with
positive advances. No PF Din or reference-mod outline was used.

JPEXS independently decoded geometry, bounds, offsets, advances and kerning.
The imported and cooked DefineFont3 payloads remain byte-identical to this
verified source. Metrics are ascent/descent/leading 19400/5500/0 in all styles;
GPOS-derived pair counts are 6775/7057/6775. All 18 sample strings match
full-run kern-only HarfBuzz widths; digits are tabular. SWF does not provide
general OpenType contextual/mark shaping. Renderer behavior remains untested.

Derivative source fonts are named **Quiet Folio Book**, complying with Gentium
and SIL reserved names. The required game lookup alias remains
`PF Din Text Cond Pro`; it is a binding, not the derivative family name.
**Official GFx import strips all three DefineFontName attribution tags** from
the prepared SWF. This was checked across source, saved import and cooked
output; font payloads do not change. Both complete OFL notices and derivative
attribution therefore ship externally in the mod root. No resource header was
edited to retain those optional tags.

## Official pipeline evidence

Unchanged control:
`build/gentium-editor-control-v2/receipt.json`.
Candidate:
`build/gentium-candidate-v1/receipt.json`.

Both complete cook → validate → pack → metadatastore → independent ZLIB
re-extraction successfully. Four exit codes are 0 for each. Official validator
reports one file and zero resource errors. Chunk CRC is valid; the candidate
has one CSwfResource, no bitmap dependencies and intact registration data.
Re-extraction exactly reproduces cooked bytes. Official linkage and its GFx
ExporterInfo agree; generated linkage differs from vanilla by the unique
authoring filename and is recorded, not hand-patched.

Each CLI command emits only the same two established startup assertions as
the unchanged control: depotDirectory.cpp:11 trailing slash and
soundFileLoader.cpp:101 missing ly_animal_dog bank. No fresh resource-state
assertion occurs. Editor log still reports `Asserts Disabled: ON`; its origin
and diagnostic effect remain unknown. No zero-assertion Editor claim is made,
and no assertion settings were modified. Independent CLI evidence is the gate.

Metadata is produced by the official current tool, with a single bundle/entry
and the canonical English key. An independent complete metadata-store consumer
decoder was not implemented; actual game loading is part of acceptance.

| Input/output | SHA-256 |
|---|---|
| Installed runtime English resource | `a1223e1a26e0c541a69cb1c6ad8bffbd70c074f1d4603193758b2bf220e95f81` |
| Prepared candidate SWF | `4d7964fe5679bbd69fddb7d5ab8cd5ee8a7b41e4701f832c9fc0aab0962674c3` |
| User-saved candidate | `80dbe1de28645d7100f14b497b7e2ad6dc4fa8eda6e4e5e4d6c47113b1bb10c1` |
| Cooked candidate / re-extraction | `9bc41144a3fcfc32377b41bebf9698ac8c80ebaee0f621fc64f22a8ed16a0e9e` |
| blob0.bundle | `17f82a1af81221ba41742edd0f1e3130b2fc00054454b9e8305f9d43a38ff9af` |
| metadata.store | `fad0e235232f60fac4c5fd95bba9bfbde0aa1e0879e99f96e97bc5ca07be68d1` |
| Current wcc_lite.exe | `9f448e0c8b9ea1ea803d0ae543f2fcd6e905088b8b71f54da2bff22c6cf318fc` |

56 repository tests pass, including packaging rejection of changed non-font
tags, movie geometry, code mappings and missing styles. See the original
[package tool](../tools/package-english-gentium.py) and
[regression tests](../tests/test_gentium_package.py).

The build reuses the retained private CLI runner and restores its original
workspace by checked hash inventory. No toolchain/depot copy was created.
Editor log snapshot is local `build/gentium-candidate-import-evidence/editor.log`.
The preserved saved project resource and final SWF are the necessary inputs;
the large Editor depot copy is not a package dependency.

### Reproduce from the saved input

Choose unused output directory names:

```powershell
& build/font-preparation-venv/Scripts/python.exe tools/verify-font-asset.py --resource build/npc-editor-run/projects/quietfolioenglishtrial/workspace/gameplay/gui_new/swf/witcher3/fonts_en_qf_book_v1.redswf --expected-swf build/gentium-font-source-final/input/fonts_en_qf_book_v1.swf --out build/gentium-candidate-repeat
& build/font-preparation-venv/Scripts/python.exe tools/package-english-gentium.py --build build/gentium-candidate-repeat --game 'C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3' --out deploy/gentium-english-repeat
```

Packaging determinism is verified for unchanged cooked/metadata inputs. Fresh
official cooking's absolute-path/linkage dependence is not claimed universally
deterministic across different authoring filenames or tool installations.

## User installation and first acceptance test

1. Close the game. Select Vortex **Witcher Compatibility Test** profile.
   Keep accepted Colors v4 and Shadow v1 enabled. Keep old overlapping color
   v2/v3 hooks disabled. Do not regenerate merges or change settings.
2. Use **Install From File** with the exact ZIP above. Check routing to
   `Mods/modQuietFolioEnglish`, with the two content files and three notices.
   Enable this one font mod and deploy through Vortex. If a conflict with
   another English font mod appears, stop and report it; do not blindly assign
   priorities. The current scan found none, so no priority change is required.
3. Verify deployed files under
   `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\Mods\modQuietFolioEnglish`.
   The English resource lives inside blob0.bundle, not as a loose file.
4. Launch manually in English. Confirm main-menu text visibly changes. Check
   regular body text, bold labels and italic text where naturally present.
5. Load a save: inspect Roach/Vesemir and one longer name with a quest icon.
   Confirm accepted colors/shadow, health, targeting and HUD toggles still work.
   Change targets and reload. Check names do not clip or collide with icons.
6. Check a long dialogue/subtitle, settings labels/descriptions and aligned
   numbers. Look for extra wrapping, missing accented characters/punctuation,
   clipped ascenders/descenders and differences between styles. Keep subtitle
   scale unchanged. Check practical controller distance on bright snow/sky and
   dark interiors at the resolution you actually use; report that resolution.

Regular sampled names are 16–25% wider, though the eight checked names fit
the authored NPC bounds. Quest-icon spacing and dynamic bounds remain
runtime risks. Long dialogue/menu labels may wrap earlier; accented forms
can exceed natural vertical metrics by up to approximately 1.57px at 20px.
No global shrinking or condensation was applied to conceal these risks.

**One-mod rollback:** close the game; disable or uninstall only
`modQuietFolioEnglish` in this profile and redeploy. Keep Colors v4, Shadow v1
and compatibility packages enabled. No saves or settings need restoration.
The next required user action is this reversible in-game trial; no further
manual Editor import is needed.
