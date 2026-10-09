# Native NPC SWF import investigation — 2026-10-09

**Status: blocked; no ZIP and no visual variants.** The native authoring route
fixes the missing texture array. A missing official texture-group definition
caused a second, independently reproduced texture-cooking failure. Including
that definition restores the vanilla embedded-mip structure. The resource-state
assertion remains, so an unchanged end-to-end build is not accepted.

Scope is English typography, NPC text colors and text rendering only. The later
presentation roadmap is untouched. No game launch, deployment, installed asset,
Vortex, merged-script, settings or save modification was performed. The fresh
runner's before/after hashes and mtimes of all files under the current Documents
game directory match. This is a filesystem snapshot, not a system-wide write trace.

## Primary inputs and observed comparison

Installed REDkit source:
`L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\gameplay\gui_new\swf\hud\hud_enemyfocus.swf`.
Runtime source: installed `content/content0/bundles/startup.bundle`, resource
`gameplay/gui_new/swf/hud/hud_enemyfocus.redswf`; read-only extraction under build.

| Input/output | Bytes | SHA-256 |
|---|---:|---|
| Installed native CWS authoring SWF | 66,944 | `f84544e26c27b38e8b1f64ff8f77775743e1e6ecd7a4f1972fce381ed9a9e819` |
| Installed runtime CR2W/CFX resource | 88,805 | `8b5c7cf0cb0e61fd005239689e096c9c5da9e3f1aa2182f9f88c71057903a76e` |
| Fresh native import, uncooked | See manifest | `80cc3441a6f6839e94f1cf38d600c3dd929e4daf2c39c23cf3eac0b74f4405fa` |
| Fresh native cook with texture-group config | 88,805 | `c3b9949c0c31481263a57185bde84c0161590d345f22561d5a0888af7b29dd92` |

The fresh result is a diagnostic artifact, **not an installable asset**. Hashes
are exact run receipts, not promises of byte-deterministic rebuilds; exporter
linkage identifiers depend on the input path and atlas padding differs.

Native source has 73 tags; runtime and cooked movies have 75. Excluding bitmap
storage/export tags 36, 1000, 1008 and 1009, the entire ordered tag streams are
byte-identical, before and after the official import/cook. This includes ABC
(82), SymbolClass (76), external font imports (71), all nested sprite timelines
(39), placements (26), shapes, text definitions and export records. Flash
version, frame rectangle, frame rate and frame count match too. No ActionScript
was recompiled or taken from a reference mod.

Native seven DefineBitsLossless2 bitmaps use format 5, with validated decompressed
32-bit pixel lengths. The official exporter packs them into one DXT5 atlas:

| Character | Native size | Runtime/cooked atlas rectangle (exclusive end) |
|---:|---|---|
| 6 | 40 × 39 | 247,0 → 287,39 |
| 10 | 124 × 7 | 289,0 → 413,7 |
| 13 | 124 × 7 | 415,0 → 539,7 |
| 32 | 64 × 64 | 0,0 → 64,64 |
| 35 | 47 × 44 | 198,0 → 245,44 |
| 56 | 64 × 64 | 66,0 → 130,64 |
| 59 | 64 × 64 | 132,0 → 196,64 |

All seven subimage tags are byte-identical. Both resource files have a
CSwfResource with one embedded texture handle to a child CSwfTexture. Both
chunks' recorded CRCs match their contents. Texture properties match:
540 × 64, TCM_DXTAlpha, GUIWithAlpha; resident index 0, one embedded mip,
pitch 2160, alignment 16 and 34,560 DXT5 bytes. No separate streamed atlas is
required by this observed texture structure.

BC3 decoding finds **zero alpha/visible-RGB differences in each subimage and its
one-pixel border**. Across the whole atlas there are 555 alpha/visible-RGB
differences outside those footprints, plus 21 transparent-RGB differences.
Therefore the entire atlas is not pixel-identical. Filtering beyond the measured
border and live rendering have not been validated. Raw atlas hashes are in the
manifest. The inspector checks this limited observed structure; it is not a
complete v164 CR2W decoder or proof of runtime behavior.

## Texture failure isolated and corrected

The first native import restored the texture object, but cooking with the old
minimal staging data produced 55,038 bytes, missing the compression property,
residentMipIndex 4 and a ten-mip payload rather than the embedded full atlas.
The DX12 cook behaved the same. `buildcache textures -platform=pc_dx12` found
zero resources and wrote an empty cache. That route was not accepted.

Installed `r4data/engine/textures/texturegroups.xml`, group GUIWithAlpha, explicitly
sets TCM_DXTAlpha, streamable=0, resizable=0, maxsize=2048 and hasmips=0.
The installed cooker refers to this exact configuration path. Copying that
unchanged file into the isolated data directory and repeating a fresh import
and cook restores the full 88,805-byte embedded texture structure. This input
is now mandatory in the original reproducible probe. No resource header,
compression enum, mip field or binary tail was hand-edited.

## Concrete blocker: importer state assertion

Fresh imports, including the corrected configuration and a separately staged
reproduction, report:

```text
diskFile.cpp:2633 (m_monitorData->m_isLoaded == 1)
Corrupted internal flag state for resource
'gameplay\gui_new\swf\hud\hud_enemyfocus.redswf'
```

Exit code is zero despite that assertion. Re-importing an existing output omits
the resource assertion but says overwriting is cancelled and fails to save;
that does not resolve it. The currently installed `swfimport` help exposes only
fromAbsPath and toDepotPath. Generic `import` lists texture and mesh importers,
not SWF; it is not an evidenced substitute. `resave` offers no supported recipe
to repair this importer monitor state. No invented overwrite flags or custom
resource writer were used.

The isolated minimal runtime also emits startup assertions, including missing
script classes/sound banks and depotDirectory's trailing-slash assertion.
Adding a trailing slash to the staged data path did not eliminate the latter.
The new resource assertion is additional to that startup baseline; its cause
is not proven to be independent of the incomplete isolated startup environment.
These logs are not clean toolchain acceptance. Official `validate` reports zero
resource errors but cannot certify the importer or live HUD contracts.

Next asset step: establish a supported, complete isolated REDkit initialization
and reproduce/import this unchanged SWF without the monitor-state assertion,
or obtain a confirmed current-tool fix. Retain the exact input and compare the
same contracts. Do not suppress the assertion or repurpose an older compiled
movie. Packing, bundle re-extraction, metadata verification and Vortex ZIP
validation remain downstream gates; no single-resource package is claimed yet.

The refreshed installed Mods/DLC bundle and loose-resource inventory finds no
EnemyFocus movie override. This removes a known asset collision, not the need
to validate FriendlyHUD and SAH behavior against their unchanged scripts.

## Narrow script fallback, also unvalidated

Original `src/npc/quietEditorialNameColors.ws` is an experimental additive
OnTick wrapper. It delegates the existing method, follows the observed
mcNPCFocus.tfName Flash member path, and remaps only the five exact vanilla
textColor values through installed Get/SetMemberFlashNumber APIs. It does not
replace the EnemyFocus movie or copy a third-party implementation. Proposed
neutral/friendly/hostile/Axii/VIP values remain #E9E2D2, #B4C0A0, #D6A093,
#B4C2D1, #D5C08E. It cannot provide the requested shadow-only trial.

`tools/check-npc-fallback.py` stages a read-only approximation of enabled loose
scripts and whole-file priority winners, then compiles baseline and candidate
separately. FriendlyHUD owns EnemyFocus.ws (priority 19); SAH priority 30 and
compatibility merges remain unchanged. Both runs fail before candidate checking:

```text
Unknown type 'array:2,0,SAutoLootFeedItem' for property 'm_feedQueue'
Unknown type 'SAutoLootFeedItem' for property 'feedItem'
Could not start a scripting system update
```

This diagnoses the staged compiler context, not a defect in the working game
profile or proof that the wrapper works. Seven enabled compiled-script mods
also prevent claiming complete profile coverage: BloodAndSteel, GwentDeckChoice,
brothersinarms, sharedutils, TopNotchSwordsFix, smoothmap and EvilsOfRivia (exact
folder IDs in manifest). Do not rewrite working merges to accommodate this
diagnostic. The fallback has no package, no compilation acceptance and no
in-game acceptance. Resolve the isolated baseline/opaque-script coverage before
considering it an alternative test ZIP.

## Reproduce, delivery and eventual acceptance

```powershell
python tools/probe-redkit-ui.py --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit' --native --resource build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --settings-directory 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3' --out build/native-npc-fresh
python tools/compare-native-npc.py --native build/native-npc-fresh/input/hud_enemyfocus.swf --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/native-npc-fresh/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --out build/native-npc-fresh/contracts.json
python tools/check-npc-fallback.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --settings 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\mods.settings' --runtime build/native-npc-fresh/runtime --out build/npc-fallback-fresh
python -m unittest discover -s tests -v
```

Use fresh output directories. Both diagnostic runners deliberately fail closed;
neither packs or deploys. Local actual receipts/logs are under
`build/native-npc-reproduce/`, early contrast runs under `build/native-npc/`, and
script comparison under `build/npc-color-fallback/`. The committed manifest
contains hashes/metadata, never asset contents. Ten synthetic inspector tests
pass; those tests validate inspection, not the game or cooking pipeline.

**Generated ZIP path: none. Installation: none. Rollback: unnecessary because
nothing was installed.** Once all unchanged gates pass, build an unchanged
single-key control first, then independent color/shadow/combined trials. The
shadow proposal remains RGB 20/23/24, alpha 166, blur 2, strength 1, distance 1
on tfName only; it has not been executed. Gentium remains a later separate test.

For a future accepted ZIP: select Witcher Compatibility Test in Vortex, Install
From File, enable only one trial, inspect conflicts and deploy. Expect only the
EnemyFocus key and official generated package metadata; refresh live ownership
before deciding priority. Do not regenerate merges. Roll back by disabling that
one test mod and deploying, then confirming its override is absent.

First game acceptance: unchanged control with friendly/neutral/hostile and
Axii/VIP transitions; normal/boss health, levels, quest icons, target switching,
damage and dodge feedback; FriendlyHUD distance/name behavior and SAH
exploration/combat hide/show/fades. Then compare individual visual trials on
snow/sky, bright daylight/walls, fire, caves/night at 1080p/4K/controller distance,
long English names, UI scale changes and save reload. Check rollback last. No
runtime acceptance is claimed by matching ABC or successful file validation.
