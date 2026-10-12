# Ink & Iron 0.8 HUD batch — private v1

12 October 2026. This implements the user's combined-HUD milestone. The accepted
[player-bars v1](ink-hud-bars-v1-runtime-feedback.md) package remains unchanged.
The batch adds the remaining 17 HUD-module movies and the Dialogue module's HUD
movie. Inventory, Shop, full-screen World Map and Outfit Wheel's root movie are
outside this build. No game/Vortex/settings/merge/save deployment is performed.

**Ready for isolated in-game testing:**
`deploy/ink-hud-batch-private-v1-final/Ink-Iron-HUD-Batch-v1-private-test.zip`
(8,915,063 bytes), SHA-256
`f976a2e5b5d9a3a6a4c0610415214341605df3687aa810e0eddaeb83f1dc9b4d`.
One ZIP contains the main HUD folder and the separate alias-only folder. Enable
the previously accepted bars v1 package alongside it; its ZIP/hash are unchanged.

## Implementation and compatibility

`gameplay/gui_new/swf/hud/` is the common resource prefix below. Matching callbacks
prove a callable contract, not correct live timing, layout or controller behavior.
The installed FriendlyHUD/merged 5.01 scripts remain the data/input providers;
SAHUD's existing module policies remain the visibility/fade providers.

| Movie suffix / component | Implementation | Preserved functional contract / runtime checks |
|---|---|---|
| `wolfstatbars` | Existing accepted v1 dependency; no duplicate replacement | Existing SAHUD in-memory appearance/combined-toxicity adapter remains. Its optional-theme/toxicity-only limitations are unchanged. |
| `buffs` | Private derivative: public `sahRefreshCells`, 16 renderer handles/count, `expireTween`, renderer identity and tween ownership flag | Three native callbacks and original timers/percent/data listeners survive. SAHUD can suppress expiration alpha flashing and release its own pause. Native renderers stay I&I; secondary SAHUD themes stay constrained by bars v1. Test renewal/expiration, overflow/expanded view, anchors/scaling and menu transitions. |
| `minimap2` | Unchanged I&I movie + author clock annotation | 13 callbacks, navigation/markers/hub/interior map remain; module fade, SAHUD compass/zoom policies and FHUD navigation remain script-side. Test time/weather, zoom, interiors, custom markers, compass substitution and return from Smooth Map. |
| `quests` | Unchanged I&I tracker | Five native callbacks; objective/counter/highlight listeners retained. Test tracked/untracked/optional objectives and contextual hide. |
| `journalupdate` | Unchanged I&I movie + author quest-banner annotation/art | Six callbacks; quest completion/new/update and XP delivery retained. Color/XP-style options require HUD settings XML/localization/cache. |
| `enemyfocus` | Private derivative + original post-SAHUD state bridge + author NPC protocol | 15 callbacks retained. Visible I&I composite bar follows native health/stamina visibility; custom lock ring follows native visibility/scale. V4 semantic colors and v1 subdued shadow reach native name, friendly role and ghost text. Test combat/dead/boss transitions, hostility/Axii, merchants/craftsmen, focus-marker 100%/60%/hidden, hide-bars/level and dodge feedback. |
| `bossfocus` | Unchanged I&I movie | Three callbacks; boss data and module policies retained. Test boss health and entry/exit transitions separately from enemyfocus. |
| `interactions` | Private derivative retaining I&I layout and trial utility face/shadow | 14 callbacks, hold-duration, key/icon/positions/listeners retained. Embedded utility font copied from exact currently deployed Interaction v2; prompt + dynamic NPC row use it at 17px. Trial status remains unaccepted. Test hold, mount/talk/loot, busy NPC, controller/keyboard switching and layered prompts. |
| `iteminfo` | Unchanged I&I quickslots + key-hints portion of NPC annotation | Eight callbacks; slot data, potion/oil/sword indicators and input changes retained. SAHUD's independent minimal-slot option remains enabled as currently configured. Test radial return, depleted items, oil hints, quickslot keys and switching input device. |
| `radialmenu` | Unchanged I&I movie + colored-sign annotation | 14 callbacks checked against deployed merged winner; input dispatch/listeners retained. Test signs, bombs/oils, axes, navigation/back, keyboard/pad and existing combat actions. |
| `controlsfeedback` | Unchanged I&I movie | Native feedback callback and original button/input listeners retained; root glyph system remains Outfit Wheel's. |
| `hud.redswf` (Buttons module's HUD root) | **Isolated exception: deployed Outfit Wheel root retained** | I&I's replacement lacks GOW's `OWOpen/OWClose/OWAxis/OWRelease/OWSetSlot/OWSetItem/OWStatus` contract. Do not overwrite it with load order. Root-dependent glyph appearance is not fully I&I yet; port the wheel class/data/input exports into the I&I root as the next shared-resource transformation. |
| `damageditems` | Unchanged I&I movie + gear annotation/art | Native callback retained; durability/gear-style options. Test broken/repaired sword and armor. |
| `horsepanicbar`, `horsestaminabar` | Unchanged paired movies + author horse forwarding | Native callbacks retained; I&I combined fear/stamina presentation receives panic data. Test fear, gallop exhaustion/recovery and dismount. |
| `oxygenbar` | Unchanged I&I movie | Native oxygen callback + module policy; test dive/surface and depletion/recovery. |
| `companion` | Unchanged I&I movie | Six callbacks retained; test companion vitality and party changes where available. |
| `crosshair` | Unchanged I&I movie | No literal native function binding in its WS; inherited module lifecycle and original input/event sites retained. Test aiming, bombs/crossbow and Witcher Senses. |
| `timelapse` | Unchanged I&I movie + shared HUD scale helper | Three callbacks; native progress and inherited module lifecycle remain. Test visible time/progress contexts and scale. |
| `dialog` | Unchanged I&I Dialogue HUD movie | 11 callbacks, dialogue choices, spoken-line fields, skip/timer/haggling controls retained. This is distinct from `hud_subtitles`; subtitle-shadow v1's resource is untouched. Test timed/disabled/previous choices, controller focus, skip and bargaining. |
| Loot feed, oneliners, gameplay subtitles, other unsupplied HUD movies | Existing owners retained | The selected 0.8 modules supply no replacement for these keys. Do not claim their appearance is newly I&I. Existing notification queues and subtitle trial stay intact. |

The native module source for every movie is selected from the deployed merged
winner first, FriendlyHUD second, then the verified installed compatibility
source assembly. All **106 literal native function bindings** resolve through
the movie root's public inheritance chain. Original root signatures,
SymbolClass IDs, imported libraries, data/event/controller source sites and
non-ABC tags are checked before/after. These checks do not simulate Flash frames.

The enemy movie keeps I&I's original single composite health/stamina Shape.
SAHUD's hide-bars policy hides both native handles, which now hides that Shape.
Independent health-versus-stamina rendering is not added. Lock-ring baseline
scale is captured once, so changing its gold option cannot recapture SAHUD's
already-reduced marker scale. Accepted colors are mapped at the actual render
sites, including the new ghost name/role fields, rather than relying solely on
the old hidden name field. The accepted color script remains enabled.

Buff export work includes **declared** `sahRendererId` on the renderer and
`sahExpiryOwned` on GTween: AS3 sealed classes cannot safely receive arbitrary
new properties. Only the expiration-tween ownership flag is added; native
percent rings, data, timers, event callbacks and tween implementation remain.

## Build and evidence

Original implementation: [restricted movie patcher](../tools/patch-ink-hud-movies.py),
[batch builder/rollback utility](../tools/build-ink-hud-batch.py),
[state adapter](../src/hud/inkIronHUDStateBridge.ws),
[fail-closed tests](../tests/test_ink_hud_batch.py).
Full decompiled author sources and edited AS stay private under `build/`;
the tracked patcher records the reproducible transformations without vendoring
the original classes. Asset input/output hashes and exact ownership are in the
[non-asset release manifest](ink-hud-batch-v1-manifest.json).

The bounded CR2W edit replaces the framed compressed GFx stream, adjusts export
sizes/offsets, chunk/export-table CRCs, file lengths and header CRC. Properties,
tables, linkage names and embedded atlas bytes survive. It rejects unsupported
tables/buffers and bad CRCs. Header CRC layout is corroborated against
[WolvenKit-7 CR2WFile.cs](https://github.com/WolvenKit/WolvenKit-7/blob/main/WolvenKit.CR2W/CR2W/CR2WFile.cs);
that reader's older supported versions are not proof of v164 support. Actual
v164 input checks and the installed native cooker/validator provide that gate.
JPEXS AS compilation is experimental; re-export/signature/listener checks and
native validation bound its use, but in-game testing remains essential.

Only three movies have ABC edits. Interactions additionally adds the trial font
(new unused ID 60000 before its text field), rebinds field 215 and replaces its
authored action-name filter. The trial's glyph payload is preserved. Other
non-ABC tags, embedded texture pixels and exporter/atlas linkage are retained.
All atlases have checked native mip sizes, handle arrays, external-image names,
logical/BC3-padded dimensions and image rectangles.

The main native bundle contains only selected HUD `.redswf` keys. Font support
uses the **unchanged alias-only 0.8 Fonts (Vanilla) bundle and metadata** in a
second identifiable mod folder within the same ZIP. It supplies `fonts.xml`
TitleFont/BodyFont aliases, **no font library**. English resolves to the accepted
QuietFolio family; IM Fell is not included. This avoids treating raw alias XML
as a native resource during metadata generation. No global Gentium package is
rewritten. Only the trial's local utility face remains specific to interactions.

HUD texture.cache is immutable and contains exactly 59 gear/quest art entries;
no menu art is carried. English HUD localization contains two settings labels.
The seven HUD author annotations and a filtered seven-variable HUD XML are
included privately. No full I&I options/UI module, input settings, merged blob,
generic glyph/root movie, inventory or world-map resource is packaged.

Rebuild (existing local toolchain and audited extractions required):

```powershell
python tools/build-ink-hud-batch.py --out build/ink-hud-batch-repeat --deploy deploy/ink-hud-batch-repeat
python -m unittest discover -s tests -p "test_ink*.py"
```

The helper verifies the `ui-overhaul` branch, author pins, deployed affected
source coverage and before/after live resource fingerprints. It copies the
read-only compatibility source assembly into a private compile workspace;
baseline/no-op/candidate compile controls produce private blobs, never packaged.
Seven currently enabled opaque compiled mods are outside this source-assembly
regression; retail multi-blob compilation and live frame timing remain runtime
checks. Resource commands use only the isolated runner, restored afterward.

Final offline results (`build/ink-hud-batch-private-v1-final/`):

- Baseline, declaration-matched no-op and candidate script compiles: exit 0,
  no Script/WCC errors, **819 warnings / 337 assertions each**, identical
  diagnostic multisets. All 55 required current source/archive pins match;
  accepted bars is read from its hash-pinned release because the refreshed live
  profile has returned to a configuration without it deployed.
- Native **cook → validate → pack → metadatastore**: exit 0 at every stage;
  **18 resources, zero resource-validation errors**. Only the two established
  private-runner startup assertions occur (`depotDirectory.cpp:11`,
  `soundFileLoader.cpp:101`); no new resource-state assertion. The runner/compiler
  hash equals the currently installed REDkit compiler.
- **15 entire resources are byte-identical to their I&I inputs; three are scoped
  derivatives.** All 106 native callbacks resolve; 21,613 original class method/
  accessor declarations and data/event/controller source sites survive. Every
  atlas's mip/handle/image/rectangle checks pass. The added utility font has an
  unused definition ID, its glyph payload is identical to the deployed trial,
  and its definition precedes its bound text field.
- Main bundle has exactly 18 native keys; independent re-extraction matches
  every cooked input. Official metadata contains every key. Original alias
  bundle has exactly one key and re-extracts to the audited `fonts.xml`.
  ZIP CRC/readback/routing and deterministic ZIP encoding pass (17 members).
- Before/after deployed resource/source/settings fingerprints match. All
  extracted/modified assets, compile blobs, native logs and ZIPs remain ignored.
  **32 synthetic tests** pass; no runtime scenario is claimed tested for this batch.
- A real rollback variant removing the NPC/interaction pair was built and
  checked: **16 native keys**, NPC annotation/state bridge absent, official pack/
  metadata/extraction and ZIP checks pass. Its private receipt is under
  `build/ink-hud-batch-rollback-npc-check/`.

Preliminary runs stopped on export-directory/encoding checks and packaging
timeouts; they are not release evidence. The final run uses fresh outputs,
native-only metadata inputs and the original built alias container. Its final
post-pack check was corrected to match metadata's actual single backslash path
separators, then resumed against already completed native output and independently
re-extracted every key. No asset or cooker success was fabricated. Current-source
checks were refreshed after an overnight user-side profile switch; VGXWalk and
an audio test cache present in that newer profile are preserved as found.

## Install once and test — user action only

1. Close the game. Clone **Witcher Compatibility Test** to **Ink & Iron HUD Batch Test**,
   or use the existing isolated I&I test clone. Preserve the original profile,
   current order, private release archives and settings backups. Profiles share
   the deployed game directory; cloning does not create a separate installation.
2. Install the release ZIP identified in the manifest with Vortex **Install From File**
   and enable it only in the test clone. Verify both folders:
   `modInkIronHUDBatchTest` and `modInkIronHUDAliasesTest`. Enable the already
   accepted `modInkIronAdaptiveBarsTest` v1 package as its dependency; the refreshed
   working-profile snapshot currently has it undeployed. Its existing release ZIP
   remains unchanged. Do not enable the full original
   I&I HUD, Dialogue, Fonts, Buttons or All-in-One alongside this curated batch.
3. Keep all five working compatibility packages, merged scripts, SAHUD, FriendlyHUD,
   QuietFolio, NPC Colors v4, NPC Shadow v1, Interaction v2, Subtitle Shadow v1,
   Outfit Wheel, Hoods/DLC, Smooth Map, Mod Settings Menu Fix and existing
   movement/combat configuration enabled. Leave Over 9000 disabled. The trial
   packages stay available as fallbacks; this does not promote their status.
4. Engine order: the main batch must precede SAHUD (buffs), NPC Shadow
   (enemyfocus), and Interaction v2 (interactions), with lower numeric priority.
   The refreshed working-profile order is SAHUD 29, NPC Shadow 35, interactions 40;
   bars v1 is currently not deployed. In the clone, insert **batch 29, accepted bars
   30, alias-only folder 31**, then SAHUD 32. Shift existing entries at/after 29
   down three, preserving their relative order (Shadow 38, interactions 43).
   If the clone already has bars enabled, insert only the two new folders and
   preserve the same relative ordering. The alias-only folder has no current
   same-key mod competitor; keep it before any future conflicting `fonts.xml`
   owner. Keep merged/compatibility packages ahead.
   Verify relative precedence, not stale absolute numbers. This selects already
   combined resources; it does not use priority to merge movies.
5. No same-destination Vortex file rules are expected for distinct mod folders.
   The optional XML routes to
   `bin/config/r4game/user_config_matrix/pc/modInkIronHUDBatch.xml`. Use Vortex's
   menu-file handling and verify **Mods > Ink & Iron** appears; never replace a
   whole menu file list. Current inspected installation has no dx11/dx12 filelists;
   do not create legacy lists blindly. Do not register both this filtered XML and
   the author's full `modInkAndIron.xml`. Defaults work without changing any HUD
   options; check clock, gear/banner style, colored signs and key hints separately.
6. Deploy the clone manually. **Do not regenerate Script Merger outputs.** Launch
   and check retail script compilation first; an error is a rollback condition.
   Test using an existing save without saving campaign progress. No REDkit GUI
   import is required by this pipeline.
7. Use the matrix above for component tests, then check the whole stack: accepted
   player bars, SAHUD contextual show/hide/hold/fade, Witcher Senses and dialogue
   transitions, menu/fast-travel reload, FriendlyHUD markers/quest navigation,
   Outfit Wheel/Hoods, Smooth Map, Gentium punctuation/accented names, combat,
   walk/jog/run analog gait and stick/controller input. Check 1080p/4K if available
   and names/prompts against snow, daylight, fire, caves and night. Report the
   failing component and trigger; offline validation cannot establish visual
   contrast, clipping, frame ordering or live device focus.

## Roll back a component without discarding the batch

Exit the game first. Generate a new ZIP from the **final verified build** (path
recorded in the release manifest), removing named movie suffixes:

```powershell
python tools/build-ink-hud-batch.py --reuse build/ink-hud-batch-private-v1-final --exclude minimap2 --out build/ink-hud-without-minimap --deploy deploy/ink-hud-without-minimap
python tools/build-ink-hud-batch.py --reuse build/ink-hud-batch-private-v1-final --exclude enemyfocus --out build/ink-hud-without-npc --deploy deploy/ink-hud-without-npc
```

Disable the previous batch release in the clone and install/enable the variant;
both use the same mod-folder names, so do not enable two versions simultaneously.
Keep its winning precedence. The utility verifies cached hashes, removes dependent
annotations, re-packs the remaining cooked resources, generates official metadata
and verifies extraction/ZIP routing. It does not deploy or regenerate scripts.

Any single listed suffix may be removed, **except** enemyfocus/interactions and
the two horse movies are atomic pairs. The NPC Name|Role and placement protocol
requires both movies; removing either removes both and `inkIronNpcPlate.ws`
(also losing optional I&I quickslot key hints). Existing NPC Shadow/Interaction
v2 owners then return. Horse panic forwarding similarly needs both horse movies.
Buff/timelapse scaling helper remains while either component is retained.
Other scoped gear/clock/banner/sign helpers follow their own movies. Alias support
is retained because remaining I&I movies still use it. Full rollback disables
both batch folders only, preserving accepted bars v1 and all original providers;
Vortex removes the optional XML when the release is disabled. Restart after
redeployment. No settings reset or campaign-save restoration is needed.

## Remaining work

There is no planned whole-HUD rewrite or Inventory work in this iteration.
**All 18 selected module movies pass the offline build gate.** The Buttons
module's shared HUD root remains isolated because its missing Outfit Wheel
exports would remove functionality; that is a real remaining integration task,
not a native cooker failure or permission gate. Root/glyph presentation is the
principal supplied-resource exception in this release.
The next gate is comprehensive user testing of this combined build. Correct
specific visible failures first, especially custom enemy layers and interaction
placement under rapidly changing targets/policies. Optional SAHUD alternate
themes and independent toxicity presentation retain the bars-v1 limitations.
Unsupplied loot/oneliner/subtitle/root visuals remain existing-owner exceptions.

Then integrate shared common-menu exports into I&I's own movies for Hoods and
Outfit Wheel, preserving GOW root exports and input behavior; adapt Smooth Map
controls/navigation to an I&I world-map movie as a separate compatibility build.
Finally implement the approved one-screen inventory/equipment redesign, keeping
equipped-grid markers, clean Geralt preview and materials/junk hierarchy. These
systems' visible assets may change; their useful functions remain the constraint.
