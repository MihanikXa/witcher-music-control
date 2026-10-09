# Phase 2 — unchanged resource gate failed

9 October 2026. Branch `ui-overhaul`; research baseline `7a25630`.
English-only acceptance scope. **No variants, bundles or ZIP generated.**

The installed current tools import and cook a `CSwfResource`, but the attempted
runtime extraction → XML → SWF → official GFx import → PC cook does not preserve
the vanilla movie's complete rendering dependencies. Do not install this output.

| Gate | Observed result |
|---|---|
| Current input | Runtime startup.bundle resource; pinned SHA-256 in manifest |
| Inner reassembly | 75 tags; byte-identical ABC, symbols, imports, text, placements and sprite timelines |
| Shapes | Seven tags re-encoded; zero-value bit widths normalized; derived ABC XML file offsets shift three bytes |
| Official GFxExport | Runs, but processes zero images from stripped runtime payload |
| Import | Writes resource; reports `Corrupted internal flag state` for that resource |
| PC cook | Reports one cooked CSwfResource; cook.db and 53,858-byte output |
| Official validator | Zero resource errors; insufficient to establish visual completeness |
| Texture contract | **Failed:** vanilla has an embedded CSwfTexture array; rebuilt resource lacks it |
| Export metadata | Additional ExporterInfo; existing external-image reference survives |
| Bundle/Vortex | Not reached; failed gate prohibits packaging |
| Game/HUD integration | Not tested |

The vanilla GFx movie references `hud-enemyfocus{576aea93}_i6.dds` through
DefineExternalImage2, target size 540 × 64. Its texture is represented inside
the outer game resource. Extracting only CFX does not export that texture.
Vanilla contains `textures`, `array:2,0,handle:CSwfTexture`, `CSwfTexture`, width,
height and compression properties; the rebuilt cooked file lacks them. The
official importer processes no images and creates no texture array. A parse,
successful cook and clean validator therefore cannot establish full round-trip
success. No guessed CR2W writer or old compiled replacement was used.

Two isolated imports reproduce the texture loss and resource-state assertion.
The minimal depot also emits unrelated startup warnings/assertions for absent
scripts/data. These are distinct from the resource-specific assertion, which
remains unresolved. Exit code zero is not a build acceptance criterion.

## Current source lead and precise next step

Read-only inspection of installed REDkit's
`r4data/gameplay/gui_new/swf/hud/hud_enemyfocus.swf` finds a CWS movie with seven
DefineBitsLossless2 bitmap tags. Its ABC and SymbolClass tags match current
runtime byte-for-byte. This is a promising **current source candidate**, not a
verified replacement: complete bitmap/shape/placement equivalence, atlas pixels,
texture properties and packing options still require comparison.

Next: compare that native SWF's full functional/visual contracts with runtime,
then establish an isolated supported import preserving its seven bitmaps as
the correct embedded atlas. Resolve the import assertion and verify the full
cooked resource with the current tools. Only after these pass, pack an unchanged
single-key bundle, re-extract and hash-check it, and validate its Vortex layout.
No authoring-source cook is claimed here. Do not substitute it merely because
its code matches, or advance to visual variations from the inner movie alone.

## Reproduction and evidence

```powershell
python tools/probe-enemyfocus.py --ffdec build/tools/ffdec/ffdec.jar --resource build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --out build/phase2/probe
python tools/probe-redkit-ui.py --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit' --probe build/phase2/probe --out build/phase2-fresh
```

The second command needs a fresh output directory and deliberately exits
nonzero; it has no pack/ZIP operation. Installed tools/config/startup files are
copied to ignored build; config adaptations occur locally. The importer needs
`tools/GFx4` relative to its local base. TEMP/TMP are redirected locally.
The engine still attempts to read Documents settings. Observed root settings
timestamps predate these probes; no settings edit/save was requested. Generic
`Saving configuration` logging does not prove either isolation or a live-file
write. External-write monitoring remains a requirement for a reusable runner.

Local logs/receipts:

- `build/phase2/probe/receipt.json`: current input and inner tag checks.
- `build/phase2/probe/import2-full.log`, `cook-full.log`, `validate-full.log`.
- `build/phase2-reproduce/official-receipt.json`: exact commands and copied input hashes.
- `build/phase2-reproduce/import.full.log`, `cook.full.log`, `validate.full.log`.

XML/code/assets remain ignored. The committed manifest contains metadata only.
Five existing inspector tests pass. No pack, Vortex deployment or game launch
was performed. Exploratory dumpfile commands produced no usable resource dump;
no full CR2W schema validation is claimed from them.

## Deferred transformations

After unchanged acceptance, generate color-only, shadow-only and combined tests.
These original specifications were **not executed**:

- Change only the five name-color constants in current
  HudModuleEnemyFocus.setVisibility: neutral `#E9E2D2`, friendly `#B4C0A0`,
  hostile `#D6A093`, Axii `#B4C2D1`, VIP `#D5C08E`.
- Change only tfName's existing drop shadow (character 38, depth 35 in sprite
  63): initial trial RGB 20/23/24, alpha 166, blur X/Y 2, strength 1, distance 1;
  preserve angle, passes and compositing flags.
- Preserve font, bounds, positions, all callbacks, quest-icon width measurement,
  visibility/health logic, targeting, damage numbers and dodge feedback.
- Snow/bright readability remains a game-test question. Retain a dark edge;
  tune the candidate only against actual game comparisons.
- One EnemyFocus key; no scripts/fonts/settings/input files. Gentium and dual
  family typography remain separate subsequent work. Private game-derived
  assets only, original transformations tracked; no reference-mod asset reuse.

Phase 1 found no live owner of the EnemyFocus movie. FriendlyHUD's whole-file
EnemyFocus script and SAH hooks are preserved integration contracts. Recheck the
live collision inventory before packaging; the old inventory cannot certify a
changed profile. Compatibility package 04 and existing merges remain untouched.

## Installation and rollback

**Generated ZIP path: none. Do not install anything from these build folders.**
An exact installable package or priority recommendation depends on the failed
asset gate being resolved.

Future verified ZIP procedure: select Witcher Compatibility Test in Vortex,
Install From File, enable just one test variant, review conflicts and deploy.
Stop if the archive includes scripts/settings/fonts or keys beyond EnemyFocus.
Do not regenerate merged scripts. Use the refreshed collision receipt to set
priority. Rollback: disable that one test mod, deploy, confirm its override is
removed and the previous provider wins. Never manually edit managed game files.
These are future instructions; no current deployment is authorized.

First game tests once a valid package exists:

1. Unchanged control first: friendly/neutral/hostile, VIP/Axii transitions, normal
   and boss health/levels, quest icons, target switching and long names.
2. SAH exploration/combat hide/show/fade; FriendlyHUD distance/name visibility;
   damage numbers and dodge feedback.
3. Compare color-only, shadow-only, combined on daylight, snow/sky, bright walls,
   fire, cave/night; 1080p/4K and controller viewing distance.
4. English accents/punctuation, icon overlap, save reload, UI scale/resolution
   changes and return-to-vanilla rollback, using a disposable test save.
