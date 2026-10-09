# Research validation and remaining gates

This records Phase 1. Phase 2 resolved local tool initialization and reached
import/cooking, but failed texture preservation; current status is in
[phase2-validation.md](phase2-validation.md). The full asset gate remains closed.

9 October 2026; English-only acceptance scope.

## Completed

- Correct branch ui-overhaul and intended repository remote checked; initial
  worktree clean. Separate general-merge checkout read only.
- Four supplied references inspected by file inventory and SHA-256; three
  bundles extracted locally, six resource payloads and font tables inspected.
- Actual Mods/DLC bundle indexes and loose movie paths scanned; selected current
  runtime resources extracted from r4gui/startup. Reference Alignment Fix's two
  deployed files match the supplied files byte-for-byte.
- JPEXS read/XML/decompilation successful for current/reference glossary and
  current EnemyFocus; eight more selected movies had direct named text/filter
  observations recorded. Current code omissions identified separately from
  decompiler variable-name/debug differences.
- Five inspector tests pass: both index layouts/invalid bounds, nested
  standard/GFx payloads, missing End rejection, zero-glyph fonts, unknown format.
- Browser comparison rendered with installed Edge through Playwright; all
  upstream fonts loaded. Five synthetic backgrounds plus hostile backing and
  narrow1080-wide view generated. Daylight, snow-backing and narrow views
  visually inspected; no column overlap or header clipping observed.
- Contrast table reproduced numerically; all generated artifacts stay ignored.
- git diff whitespace check passes. No deployment or game launch performed.

## Explicit limits

No actual in-game screenshots or readability results were generated. Synthetic
backgrounds and browser rasterization cannot certify Scaleform/HDR/motion or
controller distance. No current-version asset build, engine load or full mod
compatibility test passes are claimed.

Isolated wcc help failed because it requested an absent build/gameconf.cfg.
Installed REDkit FLA central directories are rejected by Python zipfile. Neither
issue was repaired through installed-file changes. The next phase must verify
an isolated current-toolchain unchanged round trip before authoring/packaging a
binary patch. No guessed cooker arguments or fixed CR2W-header recipe is used.

Direct field filters were inspected; parent filters and dynamic changes remain
per-surface implementation checks. Some compiled mod integration/cache behavior
remains opaque. Reference glyph-code inclusion is verified; shape attribution,
all metrics and game clipping are not fully characterized.

Public licensing for game-derived resource redistribution remains a separate
decision. The first proposed archive is private, from current vanilla plus
original transformations. Reference authors' package permissions do not allow
copying their modified assets/scripts into this repository.
