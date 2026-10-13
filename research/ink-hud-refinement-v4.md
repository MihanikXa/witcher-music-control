# Ink & Iron HUD Refinement v4 — private visual polish

This release builds on the deployed, working v3 movies.
**Latest 13 October user in-game feedback:** v4 reds are perfect, Ink & Iron quickslots are restored, new glyph overall size/style is significantly improved; however inner button letters are too large and **LB radial sign/Axii menu no longer opens**. See [runtime feedback and regression triage](ink-hud-refinement-v4-runtime-feedback.md). Treat this as an open functional blocker; the immutable offline build manifest predates this test.
No deployment, settings,
menu registration, saves or merged scripts are changed by the builder. Runtime
acceptance remains pending; cooking does not establish in-game appearance.

## Visual cause and correction

The current ownership scan extracted all 23 packaged logical inputs from the
installed bundles: every digest matches v3. Its HUD owner is
`modInkIronHUDRefinementV3`, enabled at priority 31; aliases are enabled at 30.
The old load-order export used slots one lower. This is not an ordering defect.

V3 DefineShape3 artwork was made from horizontal runs of raster pixels. It
removed missing texture linkage but preserved stepped contours. V4 uses eight
quadratic circle arcs, rounded rectangles and original TrueType letter outlines.
No new glyph shape uses bitmap fills, gradients, bevels or gloss. Original
BitmapData exports still use their existing atlas slots, repainted with
supersampled artwork; those fallback slots remain raster, rather than being
misrepresented as resolution independent. No extra texture handle is appended.

V3 artwork occupied 40.96 pixels for circular buttons, 51.2 × 32 for triggers,
inside a 64 × 64 symbol canvas. V4 artwork is 38 pixels diameter, 40 × 28 for
triggers, with a consistent 1.25-pixel outline and centered ink bounds. Dark
backing alpha changes from 224 to 128. Static duplicate L/R hold rings are
removed; the existing functional hold indicator and timers remain.

The layout defect is separate: InputFeedbackButton used a one-unit label gap
and unscaled child viewrect widths; it positioned hold text without an explicit
extra gap. V4 caches original Xbox scale and applies 0.6875 idempotently,
measures the scaled viewrect, uses a seven-unit glyph/label gap and four-unit
hold-prefix gap, aligns text through ascent/descent metrics, and reports the
actual occupied width. HintButton receives equivalent scale and baseline work.
ModuleInputFeedback uses 20-unit command spacing (previously 15) and resets a
bounded canvas fit on each layout if the row exceeds its available width.
Keyboard and other-controller artwork are retained. Footer fitting applies to
long rows on either input device; bindings and click-height contracts survive.

The screenshot's inventory panel is owned by Hoods (priority 11), and the map
by Smooth Map (20); neither is replaced here. In the current script assembly,
menuBase.OnAppendGFxButton records bindings and forwards UpdateGFxButtons to
CR4CommonMenu. InputFeedbackManager dispatches that same event; the shared
InputFeedbackPanel / ModuleInputFeedback creates InputFeedbackButtonRef.
Thus the screenshot's footer is addressed through the working common/root/
overlay resources, without replacing the inventory layout. The movies' SWF
imports themselves only list the font library, not a fabricated common-movie
ImportAssets dependency. Exact evidence is local in
`build/ink-hud-v4-work/menu-evidence/report.json`.

## Component status

| Component | Implementation | Runtime check remaining |
|---|---|---|
| Xbox glyphs and prompt layout | Smooth paths and bounded adapters across nine provider movies | World, dialogue, footer, tabs, OW; 1080p/4K |
| Ordinary hostile palette | Coordinated native/ghost paint paths; unchanged dimensions | Daylight, snow, fire, darkness |
| Pre-attack warning | Two precisely guarded opacity edits | Repeated wolf attacks and multiple targets |
| Quickslots | Original I&I v1/0.8 movie baseline, refined glyphs/layout | Item switching, counts, hints, SAHUD fade |
| Accepted remaining HUD | Preserved inputs | Brief regression sweep |

| Paint | v3 | v4 |
|---|---|---|
| Health | #B65348 (182,83,72) | #B94A40 (185,74,64) |
| Hostile name | #D87566 (216,117,102) | #D9695A (217,105,90) |
| Delayed damage | #C98678 (201,134,120) | #C77D6E (199,125,110) |

Both hostile paint paths change together; accepted NPC Colors v4 is neither
modified nor replaced. Neutral/friendly/Axii/VIP treatments, enemy geometry,
lock/level placement and boss resources remain unchanged.

The warning is conclusively separate from iaiLag: HudModuleEnemyFocus's
setDodgeFeedback and UpdateVisibility control mcDodgeFeedback, character 30
inside mcNPCFocus (sprite 63). Its shape 29 has an opaque pure-red 215-twip
stroke; the parent placement adds a pure-red glow (25 × 25, strength 3).
V4 changes the red stroke and red glow alpha from 255 to 179 (70.2% each).
Hue, stroke geometry, glow radius/strength, frame count, trigger and duration
are unchanged. These are independent source layers; their combined optical
intensity is not claimed to be exactly 70%. No animated clip alpha is assigned,
so native/adaptive fades remain proportional and repeated attacks cannot
accumulate an opacity multiplier. SAHUD's existing direct child lookup and
visibility policy survive. Its CNewNPC.SetDodgeFeedback hook identifies attack
wind-up start/end; FriendlyHUD's SetDodgeFeedback forwards the target state.
The pure-red cue remains more chromatic than the ordinary bar; verify the
perceived hierarchy in-game.

## Build and validation

Original tools: `smooth-xbox.py`, `polish-hud-layout.py`,
`build-ink-hud-v4.py`; private dependencies/font are not committed.
Install fonttools 4.60.1 under `build/hud-v4-python` using the bundled Python.
The source font is the existing local Segoe UI, pinned in the manifest;
converted outlines and previews remain private. Existing I&I/REDkit assets
retain their original provenance and are used only for this personal build.

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/build-ink-hud-v4.py --out build/ink-hud-v4-final7 --deploy deploy/ink-hud-refinement-v4-release
& $py tools/build-ink-hud-v4.py --out build/ink-hud-v4-final7 --deploy deploy/ink-hud-refinement-v4-release --finish
& $py -m unittest discover -s tests -p 'test_ink_hud*.py'
```

Use a fresh output/deploy pair for reproduction. `--resume` verifies completed
movie checkpoints and continues after a failed source-contract edit; incomplete
private working directories are retained with an attempt suffix. No relaxed
contract or fake successful cook is permitted. The existing owner extraction
and exact deployed-input snapshot are mandatory build inputs, not vanilla.

The release manifest records hashes, changed keys, original declarations,
listener/controller/data sites, font/import/exports, atlas and CRC checks,
unchanged resources, native commands and compiler controls. Independent FFDec
parses and actual GFx shape PNG exports at 0.6875, 1.375 and 4 times canvas size
are retained locally. Accepted script control blobs/providers are rehashed;
packaged WitcherScript must match v3 byte-for-byte. No fresh compilation is
claimed for unchanged scripts or the seven opaque compiled mods.

The final build was assembled from validated private movie checkpoints, with a final artwork-only correction preserving ABC/fonts/exports/placements exactly. `rebuild-hud-v4-art.py --cache build/ink-hud-v4-final4 --out build/ink-hud-v4-final5` records that step; the native gates then run against the final bytes. All D-pad directions and the double-up marker have distinct definitions. Release hash and final native results are recorded below.
Native metadata startup has previously timed out. The builder attempts the
native command first, then explicitly records independently verified table
relocation if required. That fallback reproduces a separate successful native
control byte-for-byte, requires identical ordered resource keys and rejects
native imports/buffers/dependency tables. It is not a successful native metadata
commandlet run. Native cook, resource validation and packing remain separate
mandatory gates, followed by exact bundle re-extraction and deterministic ZIP
checks.

## Install, test and rollback

1. Exit the game. In the isolated test profile, disable **HUD Refinement v3**
   (and v2/batch v1 if present). Install the single v4 ZIP. Keep the aliases
   folder enabled once; its bytes are unchanged.
2. Use v3's exact priority slot (31 locally / 30 in the earlier export), with
   the same file-conflict rules. V4 owns its packaged HUD/common/overlay keys.
   Keep bars, SAHUD, FriendlyHUD, NPC Colors v4/Shadow v1, QuietFolio, interaction/
   subtitle trials, OW/Hoods, Smooth Map and compatibility/movement/combat mods.
   Keep Over 9000 disabled. No priority experiment or merge regeneration.
3. Reuse the already registered modInkIronHUDBatch.xml filename. V4 restores
   the original iiShowQuickSlotKeys option for the restored I&I quickslots;
   it does not write settings or registration automatically. Deploy manually.
4. Check A Talk relative to NPC name/action text; footer A/B, LT/RT and long
   L [Hold] labels, tab changes, focus, timed choices, haggling and controller/
   keyboard switching. Check holds complete/cancel correctly, including OW.
   Compare at 1080p and 4K: sharpness, baseline, gaps, no clipped long labels.
5. Check I&I quickslots, consumable counts/switching/key hints and contextual
   SAHUD fade. Check radial input; only its button provider/style is refined.
6. Fight ordinary wolves repeatedly and with several visible enemies. Compare
   health, delayed loss and incoming-attack cue; cue must remain obvious and
   clear after attack/cancel. Check hostile/role names and unchanged non-hostile
   semantics, daylight/snow/fire/darkness. Confirm thin geometry and boss/player
   bars, subtitle shadows, dialogue sizing and FHUD navigation are retained.

Complete rollback: disable v4 and re-enable the untouched v3 ZIP in the same
slot, restore v3's menu XML through the mod manager, manually deploy and restart.
V2 is also retained as an older alternative; its glyphs may be missing and its
quickslots are retail. Do not enable duplicate annotation packages together.
Resource rollback is a rebuilt coherent package: restore hud_enemyfocus from
v3 for the palette/warning, hud_iteminfo from v3 for retail quickslots, or the
nine controller-provider movies from v3 for buttons/layout. Keep the other v4
keys. Re-run native pack/metadata/extraction gates; never edit live bundles or
stack full v3 and v4 packages merely to roll back one resource.

A reproducible component rollback builder is provided. Example (enemy only):

```powershell
& $py tools/build-hud-resource-rollback.py --base build/ink-hud-v4-final7 --restore build/ink-hud-v3-final --group enemy --out build/ink-hud-v4-rollback-enemy --deploy deploy/ink-hud-v4-rollback-enemy
```

Groups are `enemy`, `quickslots`, and `buttons`. The button group also restores
v3 iteminfo; restoring a whole compiled provider includes its associated layout.
The builder pins both release archives, preserves all other input bytes and
runs native/resource/package gates. Its rollback ZIP replaces v4 in the same
slot; disable the main v4 package first. These optional rollback outputs have
not been generated or runtime-tested during this release.

Final centering uses y = glyphCenter − 2 − (ascent + descent)/2, with hold-prefix ascent aligned to the same baseline. `correct-hud-v4-centering.py --cache build/ink-hud-v4-final5 --out build/ink-hud-v4-final7` performs the final guarded metric correction. It independently decompiles the modified classes; unmodified class sources are reused from the previously checked checkpoint, explicitly recorded in the manifest. The final XML parse and native gates operate on the complete final movies.

## Final release evidence

`deploy/ink-hud-refinement-v4-release/Ink-Iron-HUD-Refinement-v4-private-test.zip`: 10,994,697 bytes, SHA-256 `83d4482b6e65a1a72bfdf7d377ed1d7782594e5fd415227aa4057f49f4a46747`.

The final native cook, 22-resource validation (zero resource errors), pack and **native metadata generation** all passed. No metadata relocation fallback was used for this release. The established depot-path and absent-sound-bank startup assertions match the accepted controls; no new assertions were allowed.

All 13 unchanged logical resources remain byte-identical to v3, including boss bars, oneliner shadows, buffs, minimap, quest tracker and horse/companion indicators. Ordinary subtitles continue under their existing separate trial owner; v4 does not package hud_subtitles. Player bars are still supplied by the separate accepted package. All packaged WitcherScript files match v3, with baseline/no-op/candidate compiler-control blobs and current source-provider hashes revalidated. All changed native resources pass header/chunk CRC, font/import/export, atlas, existing function signature and listener/controller/data checks.

59 HUD regression tests pass, including curve geometry, solid fills without gradients, distinct D-pad directions, palette, idempotent scaling, baseline/hold alignment, bounded footer fitting and exactly two warning-opacity payload-byte edits. Actual GFx previews at three scales are under `build/ink-hud-v4-final7/previews`. Exact resource extraction, metadata keys and deterministic ZIP content are verified. Live input snapshots match before/after. No in-game validation or deployment is claimed.
