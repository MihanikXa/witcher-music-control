# Exact input and resource inventory — 0.8.0 (historical snapshot)

**Version gate (16 October 2026):** These hashes, 83-file input inventory and installation priorities describe the **11 October 0.8.0 snapshot**, not upstream **0.8.6**. Preserve unchanged for reproducibility. New Inventory source must be separately obtained, hashed and audited using the [0.8.6 handoff](../ink-and-iron-0.8.6-inventory-handoff.md). Do not overwrite this snapshot.

Canonical extraction: `reference/ink-and-iron-0.8/`. 83 files, 11 mod folders,
one shared configuration XML, no DLC folders. 5,786 canonical resource rows;
the CSV additionally includes seven original IM Fell alternative rows from the
unmodified All-in-One archive. The duplicate Vanilla archive verification is
excluded from the published CSV. Archive/member hashes establish provenance:
every canonical All-in-One member matches except the two Fonts container files,
which match the separate 0.8 Vanilla archive instead.

| Module | Bundle resources | Texture-cache entries | Loose runtime files |
|---|---:|---:|---:|
| UI | 26 (25 movies + one environment) | 21 | 12 annotation scripts |
| Fonts (Vanilla) | 1 (fonts.xml only) | 0 | 0 |
| Dialogue | 1 | 0 | 0 |
| Buttons | 16 | 0 | 0 |
| Glossary / Bestiary Art | 0 | 706 | 0 |
| Gwent | 1 | 10 | 0 |
| HUD | 18 | 59 | 7 scripts + 18 localization files |
| Icons | 0 | 2,433 | 0 |
| Loading | 11 | 0 | 18 localization files |
| Main Menu | 3 | 17 | 1 script |
| Map Inked | 0 | 2,406 | 0 |
| Shared configuration | 0 | 0 | 1 XML |
| IM Fell alternative (archive research only) | 7 | 0 | 0 runtime files; three OFL notices recorded separately |

All `.bundle`, `.cache`, `.store`, `.ws`, `.w3strings` and configuration-file
hashes are in [input-files.json](input-files.json). Compiled `.redswf`, fonts.xml,
`.env`, texture names and annotation-script keys are in [resources.csv](resources.csv).
No supplied format was silently treated as mergeable text. No archive/DLC/mod
directory name was inferred from an older roadmap.

CSV columns distinguish decompressed resource SHA-256 from stored-stream
SHA-256, existing mod owners from vanilla presence, and observed overlap from
the proposed decision. Categories correspond to the user's six cases:

1. No detected owner (new resource or no indexed replacement).
2. Vanilla replacement candidate; runtime verification still required.
3. Dependency/configuration requirement (aliases, local scripts/art); combined
   with 1/2 where applicable.
4. Presentation overlap, retaining the existing BIA correction.
5. Replacing a functionality-bearing owner, deliberately deferred.
6. Combined resource or compatibility solution required, or retained-owner
   exception with an adapter gate. This does not certify that solution exists.

Rows for an excluded HUD remain excluded even if a particular movie has no
same-path competitor. A lack of key overlap does not certify compatible
runtime exports, shared definitions, annotation order or cached font resolution.
Distinct en.w3strings filenames are compared by IDs/key hashes, not declared
conflicts merely because their filenames match.
The known installed English XOR index scheme is normalized before comparison
with I&I's unencrypted v164 indexes. Other languages are inventoried without
claiming the English normalization or Cyrillic runtime acceptance.

[annotations.json](annotations.json) contains 94 annotations (addField,
addMethod and wrapMethod; no replaceMethod detected). Four target rows have
external annotation overlaps: SAHUD SnapToAnchorPosition; Hoods/BIA item data;
Hoods paperdoll input and hints. Source filename collisions are absent.
Native same-path replacements/merged implementations and internal UI/MainMenu
wrappers still participate in the final compiler/runtime context; four does
not mean only four possible behavioral interactions.

The earlier 0.7.4 comparison stays private. In 0.8 the Vanilla font library
collision disappears; item-selection and transmog movies move from Buttons to
UI; journal-update moves from Buttons to HUD; HUD gains companion, boss,
crosshair, damaged-gear resources and its artwork/scripts. No old package
selection is silently reused.

[summary.json](summary.json) records the final 41-section load-order snapshot,
13 working merge-source hashes, fresh owner movie/font hashes, both original
0.8 archive hashes and provenance comparisons. Resource owners were read from
the live game Mods/DLC trees, with vanilla bundle/cache indexes checked too.
The game version designation is the user's installed 5.01 baseline; this audit
does not replace its runtime or launch it. Original reports and helpers are
tracked; extracted payloads, font glyphs, author source and texture pixels are not.

For actionable installation gates, dependencies, permissions and rollback,
read [the integration report](../ink-and-iron-0.8-integration.md) and
[validation checklist](../ink-and-iron-0.8-validation.md).
