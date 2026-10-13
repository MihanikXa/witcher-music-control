# HUD Refinement v3 — Xbox rendering correction and richer reds

13 October 2026. Private test release; no deployment performed. Runtime
acceptance is pending. V2 remains the accepted geometry/functionality rollback.

| Component | Result |
|---|---|
| Xbox glyph rendering | Corrected private movies built; visible runtime result pending. |
| Ordinary-enemy reds | Richer coordinated palette built; accepted geometry unchanged. |
| Other HUD, fonts, input and OW | Unchanged resources or exact ABC/export/font contracts verified. |
| Native resource pipeline | Cook/validate/pack passed; native metadata startup blocked, checked relocation used. |
| Installation | One private ZIP ready; no live deployment. |

## Diagnosis: confirmed evidence and remaining uncertainty

The user clarified that the controller icons are **missing**, rather than showing
the old artwork. Current deployed ownership was checked again: all 23 logical
v2 resource keys are enabled winners and match the immutable release hashes.
All 17 deployed package members also match the original ZIP. The nine glyph
movies, shared HUD/common/overlay roots and interaction movie are included.
Older combined HUD batch v1 is absent. This is not a demonstrated load-order or
deployment mismatch. No ordering changes are needed.

Local settings have bars 29, aliases 30, v2 31, SAHUD 32, Outfit Wheel 36,
NPC Colors 37, NPC Shadow 38 and Interaction 43. These are one higher than the
user's exported values, with identical relative precedence. Preserve that order.

In dialogue, Xbox sprite 168 directly places bitmap IDs 86–119; A is 118.
InputFeedbackButton selects mcIconXbox/mcIconSteam/PS/Switch from InputManager.
Gameplay controls use HintButton with the equivalent selection. These buttons
are GFx images, not font glyphs. V2 preserved their symbol IDs, frames and
bindings but redirected their DefineSubImage records to added image **65534**
and a new native texture export. Dialogue's original atlas is
`hud-dialog{1a83ca32}_i1.dds`; v2 adds `qf2-dialog{1a83ca32}_i1.dds`.
The shared HUD root also exports BitmapData classes without placing those
images on its own timeline; a timeline-only replacement would miss consumers.

The new atlas passes offline linkage, bounds, handles, pixels, CRC and native
packing checks. Those checks cannot establish that the retail image loader
actually resolves the additional atlas. Given missing icons and verified
winners/references, this added image/texture path is the leading failure
hypothesis. The exact engine rejection mechanism and live device classification
are **not confirmed**. SteamController=0 in settings does not prove Steam Input
or InputManager's runtime state. V3 removes the suspect dependency rather than
claiming offline tools reproduce the runtime failure.

## Implemented correction

Nine movies: hud, panel_common, panel_overlay, hud_controlsfeedback, hud_dialog,
hud_interactions, hud_iteminfo, hud_journalupdate and hud_radialmenu.

- Restore the pre-glyph native texture exports, handles, image definitions and
  original subimage rectangles. Eliminate v2's additional atlas/image 65534.
- Replace authored Xbox timeline bitmap placements with unexported DefineShape3
  shapes: two solid RGBA fills, no gradients or bitmap/image dependencies.
  Retain placement dimensions, matrices, depth, frames, labels and other flags;
  clear HasImage only on placements changed to shapes.
- Paint flat Xbox art into the original BC3 atlas slots as well, preserving
  BitmapData class types/IDs for shared and dynamically instantiated consumers.
  Only glyph-intersecting blocks change. Blocks touching other subimages are
  preserved verbatim; bitmap fallbacks may retain a tiny original border there.
  Timeline vectors do not sample those borders. No non-Xbox image is recolored.
- Keep all nine movies' ABC, SymbolClass and font/import tags **byte-identical
  to accepted v2**. OW exports and controller/data/listener contracts therefore
  remain exact. Existing Xbox/Steam/PS/Switch selection is retained.

Artwork reuses v2's flat ivory #EFE3CE and charcoal #141718, alpha 224 backing.
Solid vector contours use one-pixel runs at the original glyph resolution;
edge smoothness at 4K is an in-game check. This is not an Outfit Wheel redesign.
Steam/PS/Switch art is unchanged; if runtime selects a different device movie,
that surface will need the narrow device-marker diagnostic described below.

## Enemy reds only

| Paint | V2 | V3 |
|---|---|---|
| Ordinary-enemy health | #AA7565 | #B65348 |
| Hostile name, ghost and role | #DE9C89 | #D87566 |
| Delayed damage | #C3A18F | #C98678 |

Only four source RGB literals change in HudModuleEnemyFocus: health, delayed
damage, native hostile paint and the post-NPC-Colors-v4 synchronizer. The v4
archive/script stays intact. Native and rendered ghost/role paths share the
coordinated hostile result. Neutral/friendly/Axii/VIP and shadows are unchanged.
Health fill remains 3.8 px, compact spacing/lock/level treatment remains v2.
Boss, separate player-bars package and all other successful resources are kept.

### Investigation note — saturated pre-attack warning (13 October)

The user observed a brief **very saturated red flash/effect over ordinary enemy health/nameplate while fighting wolves** but was unsure whether it coincided with Geralt taking damage. **High-probability identification, not yet video-confirmed:** Witcher 3's enemy **dodge feedback / pre-attack telegraph**, which flashes the enemy bar/name when an enemy winds up an attack, *before Geralt is hit*. External mod evidence explicitly describes the red enemy healthbar flash before an attack (Disabled Dodge Feedback, Nexus #4867; FriendlyHUD + Enemy HUD 2.0 merge-request discussion), and combat documentation describes a counterattack window glow. The game's Seamless Adaptive HUD mod also refers to the game's red warning bar during attack windup.

**Important implementation distinction:** this is **not necessarily** the `iaiLag` delayed health-loss fill (`#C98678` in v3). Altering only the damage-lag color may leave the bright telegraph entirely unchanged. V2's `tools/refine-ink-hud-movies.py` scales the native `mcDodgeFeedback` movie clip to 80%, but does not demonstrate reducing its red flash saturation/opacity. Before fixing, trace the actual working `HudModuleEnemyFocus` clip/timeline, `mcDodgeFeedback`, any attack warning tween or effect-layer color transform, and interaction with SAHUD's configurable attack-ring/mark handling. Find the active red paint source rather than desaturate the base health fill.

Recommended future revision: retain the **timing and function** of pre-attack feedback; make the warning subtler (lower alpha and/or harmonize its red with the accepted richer bar/name palette). Preserve accepted compact enemy geometry and all boss behavior. Ask for a short combat clip or controlled wolf attack if confirming the exact rendered effect is needed. **No code or visual fix is claimed by this documentation entry.** Source pointers: https://www.nexusmods.com/witcher3/mods/4867 ; https://forums.nexusmods.com/topic/6554121-merge-request-friendly-hud-enemy-hud-20/ ; https://www.nexusmods.com/witcher3/mods/13194

## Build and validation

Run with the bundled Python environment containing Pillow, from the repository:

```powershell
& 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/build-ink-hud-v3.py --out build/ink-hud-v3-final --deploy deploy/ink-hud-refinement-v3 --runner build/ink-hud-v3-native-runner --compiled-cache build/ink-hud-v3-diagnostic-r2
& 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/validate-ink-hud-v3.py --out build/ink-hud-v3-final
& 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m unittest discover -s tests -p 'test_ink*.py'
```

Fresh destinations are required. The private native runner is a copied installed
REDkit runtime, not the game or a Vortex directory. AS cache reuse checks exact
input/edited sources and rechecks exports/contracts. WitcherScript bytes are
unchanged: v2's completed compiler controls are reused only after verifying all
55 current source inputs and output blob hashes. This is not a fresh compilation
of the seven opaque compiled mods, nor a retail multi-blob runtime proof.
No Script Merger output is regenerated.

Native cook/validate/pack, checked metadata generation, exact resource re-extraction, atlas links,
CRC checks and deterministic ZIP checks are release gates. The companion
non-asset manifest records actual results, hashes and local log paths. Independent
JPEXS XML/SVG checks verify solid shapes, bounds and absence of image/gradient
dependencies; separate checks prove non-Xbox compression blocks remain exact.
Offline validation cannot prove visibility, timing or navigation in the game.

Actual release results: native cook, 22-resource validation (zero errors) and
pack passed. V3 metadatastore waited before starting its commandlet and the
240-second launch timed out; bounded direct retries also waited. This is a tool
startup limitation, not a reported resource rejection. Metadata was generated
by `relocate-hud-metadata.py`: it first reproduces **every byte** of a second
independently native-generated control metadata file from the v2 template and
that control bundle's sizes/offsets. It then relocates the v3 bundle fields only.
The tool requires identical ordered keys, observed field multiplicities,
CSwfResource types and zero native import/buffer/dependency tables. It preserves
the native string/key/type/extent structure and updates sizes, offsets, maxima
and aligned bundle length. The release does **not** claim a successful v3 native
metadatastore invocation. Exact bundle extraction and metadata keys pass.

The tested recovery sequence after that startup timeout was:

```powershell
& 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/build-ink-hud-v3.py --out build/ink-hud-v3-final --deploy deploy/ink-hud-refinement-v3-verified --finish-package --prepare-resume
& 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/build-ink-hud-v3.py --out build/ink-hud-v3-final --deploy deploy/ink-hud-refinement-v3-verified --finish-package --relocate-metadata
```

Preparation reproduces all nine modified movie bytes and verifies the four
enemy source literal changes. Finish calls the relocation tool and records its
real subprocess result separately from the native stages. The original direct
metadata trials are retained in local logs; no receipt invents native success.
For future key/dependency changes this bounded relocator refuses to proceed.

Release: `deploy/ink-hud-refinement-v3-release/Ink-Iron-HUD-Refinement-v3-private-test.zip`,
11,027,604 bytes, SHA-256
`6a5d5d41fa8139b339ff4aa779d4181cfbfeadc88077302e57d0ea364fa60671`.
Three separate packaging runs produce that same digest. 58 regression tests pass.
263 independently defined vector shapes serve 297 timeline placements, with
all 306 bitmap exports supported in original slots. Twelve native HUD movies
and fonts.xml remain byte-identical to v2. Detailed input/output hashes and
component checks are in `ink-hud-refinement-v3-manifest.json`.

## Install and test

1. Exit the game. In the isolated test profile, disable **HUD Refinement v2**.
   Install the single v3 private ZIP. It supplies modInkIronHUDRefinementV3 and
   the unchanged alias folder. Never enable v2 and v3 annotations together.
2. Put v3 in v2's exact existing priority slot: 30 in the export, 31 in the
   current local settings. Keep every other order/rule unchanged. Let v3 own
   its packaged resources. Keep bars, SAHUD/FHUD, OW/Hoods, Smooth Map,
   QuietFolio, NPC Colors/Shadow, interaction/subtitle trials and compatibility
   packages enabled as before. Keep Over 9000 disabled.
3. Reuse the existing modInkIronHUDBatch.xml menu registration; bytes/options
   are unchanged. Do not regenerate merges. Deploy manually and restart.
4. Activate Xbox input. Check gameplay Jump/A and other bottom-right hints,
   A interaction, dialogue A/B and timed/long choices, radial menu and quickslot
   shoulder/D-pad hints, journal notifications, pause/shared menus and Outfit
   Wheel. Verify visible flat glyphs, correct letters/directions, holds, focus,
   switching and actions. Screens outside these shared movies remain outside
   this correction's proven coverage.
5. Fight ordinary enemies in daylight, snow, fire and darkness. Compare richer
   bar/name reds, delayed damage, role text, Axii/friendly/neutral/VIP, lock-on
   and narrow geometry. Confirm boss/player bars, restored quickslots, subtitle
   shadows, dialogue sizes, adaptive fading and FHUD navigation remain accepted.

If icons remain missing, capture the exact affected surface and device setup.
The retained diagnostic builder can insert a small magenta Xbox / cyan Steam /
yellow other-device vector marker into HintButton and InputFeedbackButton,
with paired original/private A atlas probes. It is a fallback tool, **not the
released v3 artwork**. Do not change order or deploy another blind glyph batch.

## Rollback and provenance

Complete rollback: disable v3, re-enable the unchanged v2 release in its former
slot, retain aliases and all other mods, deploy manually and restart. No settings,
save migration or merge regeneration is required. V1 and accepted bars remain
unchanged. Individual resources are identified and hashed in the manifest;
a component rollback should rebuild one coherent package from the verified v2
input for that key, rather than enable duplicate annotation packages.

Enemy palette rollback replaces only hud_enemyfocus with v2. Glyph rollback
replaces the nine listed movies as a group, or a specific affected movie with
its v2 input; the original missing-art issue can return on that surface. Native
pack/metadata/extraction gates must run for any rollback ZIP. Do not edit live
bundles. All third-party code, source movies, font rasterization intermediates,
cooked resources, private derivatives and archives stay ignored under build/deploy.
Public Git contains only original tooling/tests and non-asset evidence.
