# Unchanged English-font control verified — 10 October 2026

The user saved `fonts_en_qf_unchanged.redswf` in the isolated
QuietFolioEnglishTrial project. We verified it and completed official cook,
validate, pack, metadatastore and exact re-extraction. **The unchanged asset
pipeline passes offline. The modified Gentium font is not cooked or installable.**

## Evidence

- Saved input: `build/npc-editor-run/projects/quietfolioenglishtrial/workspace/gameplay/gui_new/swf/witcher3/fonts_en_qf_unchanged.redswf`
- Input SHA-256: `cf4d0cccdf06e9278714e9d4ff95dc22ee4264250db66b742faee52d51256531`.
- Movie version, stage bounds, frame rate/count, all three font records and all
  non-font tags match the installed baseline, excluding regenerated GFx
  ExporterInfo. No proprietary outlines were modified in this control.
- Editor exporter/save is recorded in the private snapshot
  `build/gentium-editor-control-evidence/editor.log`. No fresh diskFile resource
  monitor assertion is logged. The Editor also logs `Asserts Disabled: ON`;
  its cause/effect remains unknown, so absence of an Editor assertion alone is
  not our validation criterion. No setting was changed to suppress assertions.
- Current official compiler SHA-256:
  `9f448e0c8b9ea1ea803d0ae543f2fcd6e905088b8b71f54da2bff22c6cf318fc`.
- All four CLI commands returned **0**. Resource validator found **one file,
  zero errors**. Each command logged only the two established startup assertions
  (depot trailing slash and missing ly_animal_dog bank); no fresh resource-state
  assertion occurred. None was suppressed.
- One CSwfResource, valid observed chunk CRC, no bitmap dependency tags or
  populated textures. The font-registration `fonts` property is byte-identical
  to the runtime baseline, preserving names/style descriptors.
- Generated linkage `fonts-en-qf-unchanged{cc7f3e7d}.gfx` differs from the vanilla
  export name and agrees with this movie's official ExporterInfo. This is a
  recorded metadata difference, not silently treated as byte-identical vanilla.
  No opaque resource header or property was manually patched. Runtime loading
  and visual behavior still need the eventual in-game trial.
- Bundle owns **only** `gameplay/gui_new/swf/witcher3/fonts_en.redswf`.
  Re-extraction reproduces the cooked resource exactly; official metadata
  describes one bundle/one entry and contains that canonical key.
  Metadata validation uses the official producer and inventory/key checks,
  not a complete independent consumer-schema decoder.

| Output | SHA-256 |
|---|---|
| Cooked control | `9f73b3132161957b61397c3b250833d32fc5e932d261cf7b1ca1e40d24e0538c` |
| Single-resource bundle | `eedfdfe2eeb4f9608432c3da9de8ca32b3ea997853c03620f5417aedbd5642a3` |
| Official metadata.store | `060ec79608514c5fd5b0a6259a9786f9d85b83e89cdbc2319a0acb026414a459` |

The earlier stalled metadata command also succeeded on retry without changing
its invocation. Its original cause remains unknown. The complete newly
imported control independently confirms current success; it does not prove the
earlier stalls harmless or justify replacing assertions with a zero-total rule.

## Storage and reproducibility

The earlier failed runner-copy attempt exhausted C: before cooking. The user
removed redundant generated runtime/depot copies while retaining source,
projects, evidence and packages. Their removal does not invalidate recorded
hashes; historical command executable paths may no longer exist.

`tools/verify-font-asset.py` now reuses the retained private CLI runner
`build/npc-state-expanded`. It temporarily parks the runner's workspace, stages
only this font resource at the canonical key, writes new outputs/logs separately,
and restores the original workspace with file-hash checks even after failures.
Staged input is retained as evidence, not deleted. No installation/depot copying
is performed. The complete control run occupies **1.22 MiB**. The compiler hash,
path boundaries, unsafe links, concurrent backup mounts and low free space are
checked. All **51 repository tests** pass, including restoration on exceptions.

```powershell
& build/font-preparation-venv/Scripts/python.exe tools/verify-font-asset.py --runner build/npc-state-expanded --resource build/npc-editor-run/projects/quietfolioenglishtrial/workspace/gameplay/gui_new/swf/witcher3/fonts_en_qf_unchanged.redswf --expected-swf build/gentium-font-source-final/input/fonts_en_qf_unchanged.swf --out build/gentium-editor-control-fresh
```

The saved control/expected source are unchanged. Colors v4 original source and
ZIP and Shadow v1 ZIP retain their accepted hashes. No live game, installed
REDkit, Vortex, saves, Documents settings or compatibility scripts were edited.

## Next manual action: modified Gentium import only

Computer Use remains prohibited. Fresh CLI resource creation has the previously
unresolved monitor assertion, so the established manual Editor import route is
required. Do not repeat the successful unchanged import.

1. Launch `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   Open the existing project:
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects\quietfolioenglishtrial\quietfolioenglishtrial.w3edit`.
2. In Asset Browser, select `gameplay\gui_new\swf\witcher3`.
   Right-click **Import → Flash SWF**, and select:
   `C:\Dev\witcher-ui-overhaul\build\gentium-font-source-final\input\fonts_en_qf_book_v1.swf`.
3. Save the newly named resource in this project's workspace and close the
   Editor. Report any assertion/dialog; do not choose Ignore/Ignore All.
   Expected output ends in `workspace\gameplay\gui_new\swf\witcher3\fonts_en_qf_book_v1.redswf`.

Candidate SWF SHA-256:
`4d7964fe5679bbd69fddb7d5ab8cd5ee8a7b41e4701f832c9fc0aab0962674c3`.
All 383 mappings per style and the three style bindings are source-verified,
including the six independently constructed/sourced additions. Full geometry,
advances, metrics and GPOS-derived kerning checks are in
[the conversion report](gentium-implementation.md).

Leave the Editor data copy until this import succeeds and its saved resource/log
are verified. No world loading, Play, manual cooking, game launch or deployment
is requested. Next the agent compares the candidate, cooks with the reused
runner, checks descriptors/non-font contracts and packages only after its own
gates pass. No font Vortex ZIP exists at this dependency.
