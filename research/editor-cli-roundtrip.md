# Saved Editor assets: CLI round-trip verification

**Watermark cooking failure resolved.** No successful imports were repeated.
No Computer Use, live game/REDkit/Vortex change, assertion suppression or
opaque-resource header edit was performed. Accepted v4 remains untouched.

## Confirmed failure mechanism and input identity

The earlier command's `-mod` enumerated the two supplied files but did not
replace the runner's active virtual-depot workspace. Its old workspace had
EnemyFocus and lacked Watermark: Watermark therefore failed to load, and the
emitted EnemyFocus hash was the **old CLI candidate**, not the Editor input.
Previous output existence was correctly not accepted as an Editor pipeline pass.

The definitive input fingerprints differ:

| Asset | Resource/texture linkage prefix |
| --- | --- |
| Old CLI import | `hud-enemyfocus{37259a9a}` |
| Saved Editor import | `hud-enemyfocus{37165933}` |
| Correct new cook | `hud-enemyfocus{37165933}` |

A new physical copy of the established expanded official tool layout places
both copied Editor resources in the runner's actual `bin/workspace`, with
configuration and GUIWithAlpha definitions preserved. `-mod` now enumerates
that same workspace. Both inputs load/cook successfully. No novel bootstrap
flags or fresh SWF import are involved. The original saved workspace is read-only.

## Assertion state: investigated, still unknown

The user does not remember an Ignore All option and did not intentionally
disable assertions. Treat that intent/state as unknown; no repeat GUI work is
requested to clarify it. The Editor log's `Asserts Disabled: ON` is evidence of
a reported runtime setting, not proof of who set it or how it affects every
assertion. Read-only searches found no assertion-disable entry in its copied
INI or config. Native binaries contain the status messages and an Enable Asserts
UI label, but strings alone do not establish defaults or control flow.

The copied CLI runs emit two ordinary assertions each (depot trailing-slash and
missing sound bank), so assertion diagnostics are visibly being delivered.
They emit **no diskFile.cpp:2633 resource-state assertion** during loading/cooking
these saved assets. This establishes a successful consumer path with active
diagnostic reporting, not that the historical fresh-creation defect was fixed
or that the Editor import was assertion-free. No suppression flag or setting
was introduced. Creation-state cause remains unresolved; saved-resource load,
cook and packaging must be assessed separately.

## Actual end-to-end checks

`build/editor-cook-resolved` contains the first corrected two-resource cook;
`build/editor-roundtrip-repeat` is an independent fresh copy/repeat made by
the new original `tools/verify-editor-assets.py`.

- Both current-version cooks exit 0. EnemyFocus output is 88,806 bytes;
  Watermark is 40,474 bytes. Official validate checks both entries and reports
  zero errors in all severity categories.
- EnemyFocus's entire non-image ordered tag stream, frame rectangle/rate/count,
  ActionScript, symbols, timelines, placements and external font imports match
  the installed runtime/native baseline. Atlas subimage placement tags match.
- Both CR2W chunks' CRCs validate. The CSwfResource/CSwfTexture linkage matches
  the Editor fingerprint. Embedded atlas is 540x64, TCM_DXTAlpha, GUIWithAlpha,
  resident index0, one mip, pitch2160, alignment16, 34,560 bytes.
- Every one of seven image footprints **and its one-pixel border** has zero
  visible RGB/alpha differences from the installed runtime. Across the complete
  atlas there are 560 alpha/visible differences outside those regions, plus
  48 transparent-RGB differences. Minimum distance from a footprint is two.
  All observed bitmap fills are clipped, and the nearest/bilinear model is
  unaffected. Actual renderer sampler state and live appearance are untested.
- Current official `pack` produces one 60,287-byte blob0.bundle with exactly
  `gameplay/gui_new/swf/hud/hud_enemyfocus.redswf`; Watermark is excluded.
  Direct index/bounds/codec checks and ZLIB re-extraction recover the exact
  88,806 cooked bytes. No stale asset, script or second UI key is bundled.
- Current official `metadatastore` reads one bundle/one entry and produces
  a 340-byte metadata.store containing that resource key and blob0.bundle.
  This checks the official producer/input inventory and expected references;
  it is **not a full independent metadata.store schema decoder** or retail
  engine loading proof. No metadata bytes were manually constructed.
- Repeat cook and pack hashes are identical. Both original Editor resource
  hashes and modification times remain unchanged. All 27 existing tests pass.

| Output | SHA-256 |
| --- | --- |
| Cooked/re-extracted EnemyFocus | `cebda92df66714090e38be95c33b5037973b0ff0c035300620c839e68b01589a` |
| Official metadata.store | `143930c12e176fb6681500c8f4cbfaee931915a377bc6817c03665c25ef1b367` |

Bundle hash, compiler hash, commands, source hashes and diagnostics are recorded
in `shadow-font-manifest.json` → `shadow.cli_roundtrip`. Full logs, cooker DB,
native/cooked assets, metadata and re-extracted binaries remain private under build.

## Reproduction and remaining gates

```powershell
python tools/verify-editor-assets.py --layout build/npc-state-expanded --workspace build/npc-editor-run/projects/quieteditorialnpcshadowgate/workspace --out build/editor-roundtrip-fresh
python tools/compare-native-npc.py --native build/npc-editor-run/r4data/gameplay/gui_new/swf/hud/hud_enemyfocus.swf --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/editor-roundtrip-fresh/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --out build/editor-roundtrip-fresh/contracts.json
python tools/analyze-npc-atlas-padding.py --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/editor-roundtrip-fresh/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --native-xml build/native-npc/native.xml --out build/editor-roundtrip-fresh/padding.json
```

The read-only chunk inspector now decodes only the known linkage String property;
Editor-only source-path Strings remain opaque bytes rather than being incorrectly
parsed as short linkage names. This is an inspector correction, not a resource edit.

**Verified scope:** repeatable offline current Editor-output load → cook →
validate → single-key bundle → metadata generation → exact re-extraction, with
the described contract/atlas comparisons. **Not verified:** Editor assertion
defaults/fresh creation, full metadata consumer behavior, live rendering or
runtime sampler behavior. No shadow filter modification or Vortex ZIP has been
made in this investigation, and no game was launched.

No user action or repeated unchanged import is needed now. The next shadow step
is an original native-SWF filter-only transformation preserving every other tag,
then validation of that changed asset through this saved-workspace route before
any private shadow archive. If its source requires Editor import, that will be
a new changed-input manual step, not a repetition of these successful controls.
