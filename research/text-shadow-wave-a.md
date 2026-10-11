# Restrained text shadows — Wave A source implementation

11 October 2026. **Source candidates implemented and independently decoded;
manual Editor import is the next dependency. No new installable ZIP exists.**
Accepted NPC Colors v4, NPC Shadow v1, QuietFolio English v1 and archived
interaction v1 assets/packages are unchanged. No Computer Use, game launch,
deployment, installed-resource, compatibility, settings or save write occurred.

## Exact implemented changes

| Candidate | Resource key under gameplay/gui_new/swf/ | Scope |
|---|---|---|
| Field & Folio interactions v2 | `hud/hud_interactions.redswf` | DefineEditText 215: Source Sans 3 Regular ID218, 440 → **340 twips / 17px**. Its `tfActionName` PlaceObject3: sprite216, depth1, local black Glow → restrained DropShadow. |
| Subtitle shadow v1 | `hud/hud_subtitles.redswf` | Root `tfSubtitles`, character1, depth1: local black DropShadow strength20 → 1; opacity255 → 166; color → #141718; blur1.5 → 2. |

Both effects use #141718/166, blur2×2, strength1, distance1. Interaction's new
shadow angle is the accepted NPC value 51471/65536 radians; its existing passes1,
inner=false, knockout=false and compositeSource=true are retained. Subtitle's
existing angle, passes3 and compositing flags are retained. Matching the visual
language does not mean changing every surface to the same pass count.

Interaction Regular/Medium definitions218/219, their glyphs/kerning/metrics,
other fields, key/button images, both normal/held instances, animation and code
are preserved. No default foreground desaturation, width compression or y-shift
was applied. Subtitle authored size26px, bounds, leading, positioning and text
remain intact; scripts retain **26 + SubtitleScale**, HTML, centering, width
updates, alternative speaker coloring and visibility/timing.

## Current subtitle path correction

The old resource map described `witcher3/hud_subtitles.redswf`: a real but older
18px/glow5 resource. The actual installed root **modGeraltOutfitWheel** was
extracted read-only and its current `red.game.witcher3.hud.Hud` ABC independently
decompiled. It declares `m_swfPath = swf\\hud\\`, registers SubtitlesModule with
`hud_subtitles.swf`, then loads their concatenated URL. This corroborates the
current **hud** key, not the older **witcher3** key, for this HUD module.

Installed current HUD subtitle hash:
`2475d3cee55ff9846be9b2e30490cd16a67ec08283ffe3a88dd3ef2d5c3a504c`.
Its current native authoring SWF has matching movie header and all non-image
contracts. Native current HudModuleSubtitles code changes HTML text, dimensions,
position and alpha, but has no observed filter/TextFormat replacement. The
installed vanilla WS still supplies runtime size. FriendlyHUD's deployed
interaction WS uses the existing text/icon function; scripts are not patched.
These are static facts, not live frame tracing. Poster/menu subtitles are a
separate route and are not included in this one-key prototype.

An initial legacy-source candidate was prepared before the path correction;
it is retained only in ignored build output and **is not in the import handoff**.

## Source transformation and verification

`tools/prepare-text-shadow.py` accepts a pinned native SWF, unique field/name/
sprite and optional size. It refuses ambiguous placements, multiple filters,
unsupported filters or nonblack semantic effects. JPEXS serializes the approved
field/placement edits; unchanged selected tag payloads must round-trip exactly.
Only those payloads are spliced into original SWF tag streams. Variable-size
tag/sprite lengths are serialized normally; no opaque CR2W headers are edited.
All other original tags are retained, including fonts, ABC, symbols and images.
A separate final JPEXS decode must exactly match the intended XML delta, ignoring
only file offsets. This does not claim that standard SWF preparation is cooking.

Source inputs/hashes, exact changes and private import files are recorded in
[the Wave A manifest](text-shadow-wave-a-manifest.json). Both candidates pass
these source gates. All 79 tests pass, including nested variable-length splicing,
semantic-color rejection, pass/angle retention, authored parent effects and
move placements without a repeated character ID. Broad coverage tooling and
the [coverage ledger](text-shadow-coverage-ledger.md) are independent of edits.

## Minimal manual Editor dependency — three imports

This follows [AGENTS.md](../AGENTS.md): “Necessary GUI steps must be performed
manually by the user; provide exact isolated-project instructions and stop at
that dependency.” No further fresh CLI import/bootstrap experiments are needed.

1. Open the existing isolated Editor:
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   Create a **new QuietTextShadowWaveA** project under
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects`.
   Do not open or change earlier working projects. If depot generation is
   requested, stop and report it; do not recreate the deleted full depot.
2. Asset Browser **Ctrl+A**, select `gameplay\gui_new\swf\hud`.
   Right-click → **Import → Flash SWF**, and import these three unique files:

   ```text
   C:\Dev\witcher-ui-overhaul\build\text-shadow-wave-a\input\hud_interactions_ff_v2_17.swf
   C:\Dev\witcher-ui-overhaul\build\text-shadow-wave-a\input\hud_subtitles_qs_unchanged.swf
   C:\Dev\witcher-ui-overhaul\build\text-shadow-wave-a\input\hud_subtitles_qs_v1.swf
   ```

3. Save all three to this new project's workspace, keeping their unique
   basenames. Close the Editor and report any dialogs/assertions. Do not choose
   assertion suppression, overwrite depot resources, cook/deploy or launch game.

The existing successful interaction unchanged control is reused. The subtitle
is a newly targeted resource, so its unchanged control is necessary. Existing
NPC/Gentium imports are not repeated.

## Remaining gates and eventual test/rollback

After saved files exist, verify their code/style deltas, current official
cook → validate → bundle → metadata → exact re-extraction. Require precisely
the intended keys, complete texture/metadata contracts and independently
verified source font records. Recheck live deployed ownership before packaging.
The prior interaction packager intentionally rejects these new size/filter
deltas; extend its narrowly scoped gate rather than treating old receipts as
proof of this build. Subtitle needs its own no-image resource control.

**ZIP paths/hashes: none for either new trial at this gate.** No offline cook,
metadata, Vortex routing or runtime pass is claimed for the new candidates.

Eventually v2 must replace/disable interaction v1, never run alongside it.
Keep Gentium, NPC Colors and NPC Shadow enabled. Rollback interaction by
disabling v2 and re-enabling archived v1; roll back subtitle by disabling only
its separate new module. No settings or compatibility merges need restoration.

First user checks: same Talk-over-Vesemir/Peasant scene with NPC name dominant;
held/long action, key/controller art, hold/cancel, target switching and hide/show.
For subtitles test normal cinematic dialogue, speaker labels, longer wrapped
lines, subtitle scaling, alternative speaker route if available, and save reload.
Compare snow/sky, foliage/fire, caves/interiors at actual viewing distance.
Poster subtitles and dialogue-choice text remain separate later targets.

## Coverage disposition

- **Complete milestone, preserve:** accepted NPC name shadow/color and Gentium.
- **Implemented source, blocked on manual import:** interaction v2 and current
  HUD subtitle v1. Their final game contrast and hierarchy remain untested.
- **Wave B deferred until these proofs pass:** dialogue choices/previous sentence,
  quest tracker and ambient chatter; exact authored effects are in the ledger.
- **Wave C deferred:** notifications, remaining menus, inventory/tooltips, journal,
  map, controls, radial/quick slots, rewards/tutorials and other visible text.
  Inspect semantic states and runtime setters individually; occupied Hoods,
  Outfit Wheel, Alignment Fix and SAH/Bestg movies require selected-owner care.
- **Explicit audit blockers/limits:** see ledger. No claim of exhaustive live
  runtime use or dynamic-filter coverage, and no blind replacement of glows.

## Audit totals and reproduction

The read-only catalogue covers **116 distinct UI keys, 118 owner/movie records
and 1,703 authored text placements/states**. Relevant deployed mod owners are
enabled in current mods.settings; enabled flags/priorities were read only,
not changed. Duplicate base loading-movie copies have byte-identical hashes.
Current native-AS/installed-WS scanning finds style setters in 48 source files;
these are static candidate references, not proof of per-frame overrides.
Hoods and Smooth Map codec5 movies were decoded with the existing verified
QuickBMS extractor into ignored output. Gwent game XML export exceeded the
bounded 60-second budget and remains a precise static audit blocker; it is
unmodified and deferred, rather than presumed shadow-free.

Reproduce preparation with fresh output paths (existing pinned v1 source reused):

```powershell
python tools/prepare-text-shadow.py --source build/field-folio-source-v2/input/hud_interactions_ff_regular.swf --sha256 f24e345a29be63ed19d3c414e34f9147d5b03a8bc741f80daf0de23ff341f2d4 --ffdec build/tools/ffdec/ffdec.jar --out build/interactions-v2-fresh --field 215 --name tfActionName --sprite 216 --height 17
python tools/prepare-text-shadow.py --source "L:/Games/Steam/steamapps/common/The Witcher 3 REDkit/r4data/gameplay/gui_new/swf/hud/hud_subtitles.swf" --sha256 28758214e28e36cf91b9084983edeaa4c0bfa5a683bb395d58285250bb2dd776 --ffdec build/tools/ffdec/ffdec.jar --out build/subtitles-shadow-fresh --field 1 --name tfSubtitles --sprite 0
python tools/audit-text-shadows.py --game "C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3" --redkit "L:/Games/Steam/steamapps/common/The Witcher 3 REDkit" --ffdec build/tools/ffdec/ffdec.jar --mods-settings "C:/Users/micha/OneDrive - hull.ac.uk/Documents/The Witcher 3/mods.settings" --out build/text-shadow-audit-fresh
python tools/report-text-shadow-coverage.py --audit build/text-shadow-audit-fresh/coverage.json --out research/text-shadow-coverage-ledger
```

Final generation includes codec5 support; the first bounded audit used two
read-only codec5 follow-ups for Hoods and Smooth Map, without repeating any
Editor import. Source candidates each reproduced the exact hash in a second
independent preparation run. No official cook result is inferred from this.
