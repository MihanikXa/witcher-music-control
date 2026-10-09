# Modular implementation plan — no deployment

Current Phase 2 update: importing the installed native authoring SWF restores
the texture array. Including the official GUIWithAlpha texture-group definition
also restores the full embedded mip structure. The resource-state assertion
persists, and the additive script fallback has no compiler acceptance. The gate
remains failed; no visual variants or ZIP exist. See the current
[native validation](../research/native-npc-validation.md) and earlier
[reconstruction investigation](../research/phase2-validation.md).
The package boundaries and first-proof specification below remain proposals.

## Package boundaries

1. **NPC presentation proof:** one current `hud_enemyfocus.redswf` replacement;
   target-name color constants and its named text-field shadow only. No global
   font, name/health visibility, input mapping, movement or combat change.
2. **English literary font trial:** one `fonts_en.redswf` library, independently
   obtained Gentium Book glyphs/metrics. Normal/bold/italic bindings and other
   libraries preserved. Test against unmodified presentation first, then combine.
3. **Speech:** small set of dialogue/subtitle/oneliner movies only after their
   renderers are mapped. Preserve poster/special dialogue and script size paths.
4. **Prompts and quest notifications:** separate movies and narrow original
   script hooks only if those are needed for script-owned semantic colors.
5. **Menus/inventory:** defer until Hoods/common/root renderer dependencies are
   resolved. Hoods inventory and any SAH/Bestg/Outfit Wheel movie changes require
   one supported combined variant per overlapping resource; priority is no merge.
6. **Role-based two-family option:** extra licensed embedded family and selected
   field bindings. Does not fit a three-alias global font swap. Prove family
   import/fallback first; do not mislabel option01 as implemented option02.

Author original transformations/manifests in src/; read input copies only;
retain dumps, generated GFx/CR2W, cooked metadata, bundle and archives in build/
and deploy/. Separate module IDs, input/output hashes and receipts; an aggregate
package may combine modules that touch the same movie, never two competing
versions. Public Git contains original scripts/plans, no cooked/game/author data.

## First proof manifest (proposed, not built)

| Field | Exact value/status |
|---|---|
| Runtime input | `content/content0/bundles/startup.bundle` → `gameplay/gui_new/swf/hud/hud_enemyfocus.redswf` |
| Input payload SHA-256 | `8b5c7cf0cb0e61fd005239689e096c9c5da9e3f1aa2182f9f88c71057903a76e` |
| Target resource key | Same `gameplay/gui_new/swf/hud/hud_enemyfocus.redswf` only |
| Color changes | Current runtime `HudModuleEnemyFocus.setVisibility`: neutral0 → ivory, friendly1 → sage, enemy2 → oxide, axii3 → slate, vip4 → brass. Retain the branch visibility logic and all function signatures |
| Filter change | Sprite 63 / named tfName placement / character 38 / depth 35: existing DROPSHADOWFILTER color, alpha, blurX/Y, strength only as trial in visual-spec; do not edit level/damage filters |
| Unchanged first proof | Font family, text box/leading/position, SetScaleFromWS, exports/imports, timers, bars, quest icons, lock/dodge/stamina/essence and damage colors |
| Source provenance | Current installed vanilla payload; original semantic mapping/filter transform. No Alignment/Gentium/FoL/CNC asset copied |
| License | Game-derived resource subject to installed game/REDkit terms; private test package only until redistribution terms reviewed. Original code/design belongs in repository. No proprietary PF Din font redistribution |
| Expected packaged layout | `Mods/modQuietEditorialNPC/content/blob0.bundle` and tool-generated `metadata.store`; exact current cook output must be confirmed before writing archive |
| Collision impact | No existing movie owner; behavior depends on FriendlyHUD and SAH contracts. Do not alter package04 or introduce duplicate whole-file WS |
| Build command | Native import/cook diagnostic commands are reproduced in native validation; an accepted assertion-free end-to-end bundle build is not established |
| One-package rollback | Disable only modQuietEditorialNPC in Vortex and deploy; inspect absent payload/winner. Vanilla movie restores. Other modules and existing profile stay enabled |

## Precise next step: prove an unchanged round trip

Continue from the native authoring SWF, not the texture-stripped runtime
reconstruction. Establish complete supported isolated REDkit initialization
and eliminate the importer monitor-state assertion while retaining the official
texture-group definition. The native source, cooked non-image tags and seven
atlas footprints now match the runtime evidence; whole-atlas differences and
runtime behavior remain unaccepted. Then pack one unchanged resource with the
current official tool, re-extract it, check exact keys/hashes/metadata and validate
Vortex layout before any color/shadow variation. No older movie or guessed
header is an acceptable workaround. See native validation for exact commands.

The original additive color wrapper is a separately gated fallback. Its staged
baseline and candidate both fail on an existing loot-feed struct before testing
the wrapper, with seven opaque compiled-script mods omitted. Do not alter working
merges to make that diagnostic pass. No existing REDkit project is modified.

Verified inspection command:

```powershell
python tools/audit-ui.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit' --ffdec build/tools/ffdec/ffdec.jar
```

Read-only JPEXS commands already verified on extracted local payloads:

```powershell
java -jar build/tools/ffdec/ffdec.jar -swf2xml INPUT.gfx OUTPUT.xml
java -jar build/tools/ffdec/ffdec.jar -selectclass red.game.witcher3.hud.modules.HudModuleEnemyFocus -export script OUTPUT_DIRECTORY INPUT.gfx
```

INPUT/OUTPUT stand for ignored workspace paths, not installed assets. A future
build script must refuse wrong input hashes, unknown CR2W/bundle layout, output
outside build/deploy, unexpected extra resource keys and changed exported
contracts. Do not use the fixed 601-byte font-header recipe for an NPC movie.
If a current-tool round trip cannot be verified, stop before packaging and
consider a narrowly original RGB-only script proof; its wrapper/compiler
compatibility with FriendlyHUD must be demonstrated before calling it viable.

After the unchanged gate succeeds, produce separate color-only and shadow-only
trial outputs for private comparison, then one combined movie. Preserve the
existing WS. Only after baseline and combined prototype differences have been
reviewed should a single Vortex archive be prepared for approval. This research
turn stops before those changes, archive generation or installation.

## Future English font trial manifest

Input current EN library SHA-256:
`a1223e1a26e0c541a69cb1c6ad8bffbd70c074f1d4603193758b2bf220e95f81`,
from `content/content0/bundles/r4gui.bundle`;
key `gameplay/gui_new/swf/witcher3/fonts_en.redswf`.
Replace only glyph shapes/code/advance/layout metrics for three style records
after compiling static regular/bold/italic upstream Gentium. Preserve alias
resolution; inspect reserved-name and internal-binding distinction. Exact
glyph subset and build command await the current-toolchain gate.
Upstream GentiumBook-Regular SHA-256:
`2027f6a864e5a9907c113438969d1d03fa91dfdd1a3885fa0fdeb496f0f682e4`;
Bold `ed788447ea4298dd44ac62034b9a6849003bdfea256757cb4a5d599c8b09a365`;
Italic `ed128fd9370533c796219d48aaf17b55d0562791f8cc49e83a6c607c5680bea2`.
License OFL 1.1, sourced directly from SIL 7.000. Runtime glyph subset must include
all vanilla English points plus required names/punctuation; upstream coverage
alone does not certify embedded output. It competes with any other EN font
replacement and changes all aliased UI text. Rollback: disable that one font
module and deploy. No RU/UA modification or test requirement.

## Game acceptance criteria for the first proof

- Current test profile with package04 analog gait, SAH/FriendlyHUD settings
  unchanged; name display enabled only through existing user preferences.
- Neutral/friendly/hostile/VIP/Axii targets verified against actual behavior;
  never use CNC's swapped category labels. Quest and herb targets, corpses,
  boss/miniboss, hard lock, health/stamina/essence and dodge feedback preserved.
- Long English names, apostrophes, accented names, rapid target changes and
  quest icon placement; check no clipping or stale color after target changes.
- Daylight foliage, snow/sky, cave/night, fire/bloom and bright walls at 1080p
  and 4K; fixed settings and matching camera/save for baseline and candidates.
  Compare still and moving camera/controller distance, SDR and user's HDR
  setting if active. Record actual settings rather than guessing pixel scaling.
- Keyboard/mouse and controller talk/loot/target/hold/back/accept behavior;
  dialogue, HUD hiding and quest notifications unchanged outside modified field.
- Inspect archive CRC, output hashes, exact single resource key, current bundle
  format, Vortex installation preview and enabled winner before launch.
- Rollback test restores the current vanilla appearance with one package
  disabled. User performs deployment only after explicit approval of the
  concrete archive and change manifest.
