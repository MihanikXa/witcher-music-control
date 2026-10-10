# Modular implementation plan — no deployment

Current English font implementation: all 383 mappings per style are converted
and independently decoded. Unchanged and modified resources pass official
cook, validation, bundle, metadata and exact re-extraction. The separate English
v1 private ZIP is ready for user runtime acceptance; no deployment occurred.
See [current package and handoff](../research/gentium-v1-handoff.md).
Accepted NPC Colors v4 and NPC Shadow v1 remain unchanged.

Current Phase 2 update: importing the installed native authoring SWF restores
the texture array. Including the official GUIWithAlpha texture-group definition
also restores the full embedded mip structure. The resource-state assertion
persists across EnemyFocus and unrelated controls after bootstrap/depot repairs.
Loaded resave/cook succeeds, but fresh import risk remains unresolved. The
corrected additive script fallback compiles in the known source assembly;
exact deployed compiled-mod coverage remains incomplete. A private color-only
loose-script ZIP passed controlled no-op/compiler and current source
intersection checks but failed the user's Roach neutral and Vesemir VIP test.
The user observed the diagnostic change both names and retain palette-like colors.
The clean v4 UInt trial preserves the event result and five mappings without
diagnostic state; the user reported neutral/friendly/VIP working, and explicitly
accepted all five mappings (including unobserved hostile/Axii) as confirmed for
now. Color work is closed by user decision, not by five observed category tests.
Keep v4 unchanged and in its separate mod. Next active work: shadow and English
typography, with the existing isolated Editor/SWF pipeline constraints.
See the [v4 handoff](../research/npc-colors-v4-handoff.md).
The shadow-only v1 candidate is now packaged privately. The user created
the isolated project and saved EnemyFocus and Watermark. Corrected workspace
resolution now proves repeated offline cook/validate/pack/metadata/re-extraction;
see [current verification and limits](../research/editor-cli-roundtrip.md).
Editor assertion state and live rendering remain unverified. See the historical
[Editor outcome/manual steps](../research/editor-workflow-bounded.md),
[color-only test handoff](../research/npc-color-trial-handoff.md),
[controlled investigation](../research/swf-state-investigation.md),
[native validation](../research/native-npc-validation.md) and earlier
[reconstruction investigation](../research/phase2-validation.md).
The package boundaries and first-proof specification below remain proposals.

## Current next milestone — English typography (active)

The user explicitly accepted all five colors, with neutral/friendly/VIP observed
in-game. The user also explicitly reported NPC shadow v1 working in-game on 10
October 2026. The current NPC nameplate color-and-shadow proof is therefore
closed by user acceptance. Preserve both independent Vortex modules, and do not
replace the script palette in the edited SWF. No screenshots, all-scene contrast
tests or universal HUD compatibility claims were supplied.

**Next action:** user tests the standalone English v1 package. Regular/Italic/Bold
conversion, all six missing points, GPOS pair kerning and official build gates
are complete. Preserve existing text bounds, subtitle scaling and accepted NPC
mods. Wider metrics, wrapping, quest-icon spacing and vertical clipping remain
in-game acceptance risks. No further UI development is authorized by this gate.

No Computer Use or desktop automation. If a supported isolated Editor
import step is needed, provide the smallest manual user action and wait.
Preserve main/general-merge, existing working Vortex mods, accepted v4 and
shadow v1; keep any generated archive private until static validation gates pass.
Other surface-specific shadows (subtitles, quest labels, dialogue) remain later
independent work, not part of the completed NPC proof.

## Package boundaries

1. **NPC presentation proof:** one current `hud_enemyfocus.redswf` replacement;
   its named text-field shadow only. Keep all movie color constants unchanged;
   the accepted separate v4 script handles semantic colors. No global
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
| Color changes | None in the movie; preserve all five original constants and branch logic. Keep the accepted v4 script separately enabled |
| Filter change | Sprite 63 / named tfName placement / character 38 / depth 35: existing DROPSHADOWFILTER RGB141718, alpha166/255, blurX/Y2, strength1, distance1; preserve angle/passes/flags; do not edit level/damage filters |
| Unchanged first proof | Font family, text box/leading/position, SetScaleFromWS, exports/imports, timers, bars, quest icons, lock/dodge/stamina/essence and damage colors |
| Source provenance | Current installed vanilla/native payload; original filter transform only. No Alignment/Gentium/FoL/CNC asset copied |
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

The original additive color wrapper is a separately gated fallback. The earlier
loot-feed failure is a base/patch type-order problem: the known working source
assembly resolves it. Baseline and corrected candidate now compile in copied
assembly sources, including the OnTick wrapper and current Flash APIs. Seven
opaque compiled mods and exact deployed load order remain outside that proof.
Do not alter working merges to bridge this gap. No existing REDkit project is
modified. The next asset comparison is one supported Editor import in a new
isolated project; repeated CLI bootstrap changes have reached their useful limit.

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

Current narrow fallback handoff: [clean NPC Colors v4](../research/npc-colors-v4-handoff.md).
The [v2 color-only trial](../research/npc-color-trial-handoff.md) is failed-test history.
The controlled no-op diagnostic criterion replaces the earlier blanket
zero-additional-assertion/full-opaque-recompile packaging block for this original
loose-script experiment. It does not validate the asset pipeline or retail runtime.

After the unchanged asset gate succeeds, produce separate color-only and shadow-only
trial outputs for private comparison, then one combined movie. Preserve the
existing WS. Only after baseline and combined prototype differences have been
reviewed should an asset Vortex archive be prepared. These asset changes remain
gated; the separate original color-only script archive has its own handoff and
does not resolve shadows. Installation remains user-only.

## English font trial inputs

Input current EN library SHA-256:
`a1223e1a26e0c541a69cb1c6ad8bffbd70c074f1d4603193758b2bf220e95f81`,
from `content/content0/bundles/r4gui.bundle`;
key `gameplay/gui_new/swf/witcher3/fonts_en.redswf`.
Replace only glyph shapes/code/advance/layout metrics for three style records
after compiling static regular/bold/italic upstream Gentium. Preserve alias
resolution; inspect reserved-name and internal-binding distinction. The 383-point subset per style and current-toolchain gates are verified;
see the v1 handoff for exact commands and output hashes.
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
