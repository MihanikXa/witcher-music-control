# Isolated White Orchard mixer prototype — 2026-10-11

## Result

**Follow-up:** [11-white-orchard-blocker-resolution.md](11-white-orchard-blocker-resolution.md) retains these original tests and documents the complete-hierarchy licence failure, a measured Wwise-native smooth mixer alternative, and a reproducible two-bank native cache fixture. No deployment candidate exists yet.

**Observed:** the world-only mixer works in matching Wwise authoring playback. Three independent controls select exploration, ordinary dialogue or combat gain through the existing game_state. Both FullBand and LFE respond. The actual White Orchard village and combat selectors enter the new bus; the authored q001 tavern conversation does not, even in dialog_scene with exploration/dialogue controls at 0%.

**Not deployment-ready:** generation returned errors and the regenerated Init loses vanilla definitions. Minimal soundspc.cache packaging is unproved. Boolean bypass transitions produced abrupt waveform steps. These are remaining engineering blockers; no game installation or save was changed, no playthrough was restarted, and no depot was regenerated. No settings UI or WitcherScript hook was implemented.

The test geography is **playable White Orchard**, represented in authoring by music_prologue and its village selector. This is not a test of the opening Kaer Morhen tutorial. Some selected combat tracks happen to carry `tw3_km_*` names; their verified hierarchy/routing, rather than those names, identifies this test.

## Evidence locations

All paths below are machine-local evidence. Third-party inputs, WAV copies, WEM conversions, banks and recordings remain Git-ignored; none is added to our source tree.

| Symbol | Exact path / object |
|---|---|
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| Console | `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe` |
| Spec | `C:\Dev\witcher-music-control\src\wwise\white-orchard-mixer.json` |
| Prepare | `C:\Dev\witcher-music-control\tools\white_orchard_prepare.py`, prepare / sanitize_project / prepare_defaults |
| Author | `C:\Dev\witcher-music-control\tools\white_orchard_author.py`, author |
| Generator | `C:\Dev\witcher-music-control\tools\white_orchard_wwise.py`, generate |
| Comparator | `C:\Dev\witcher-music-control\tools\white_orchard_compare.py`, read_bank / difference / compare |
| Probe / measurement | `C:\Dev\witcher-music-control\tools\white_orchard_probe.py`, probe; `...\tools\white_orchard_measure.py`, measure / matrix |
| Context driver | `C:\Dev\witcher-music-control\tools\white_orchard_contexts.py`, run / gains / snapshot |
| Transition driver | `C:\Dev\witcher-music-control\tools\white_orchard_transitions.py`, run |
| P | `C:\Dev\witcher-music-control\build\white-orchard\prototype` |
| V | `C:\Dev\witcher-music-control\build\white-orchard\validation` |
| Generated banks | `C:\Dev\witcher-music-control\build\white-orchard\prototype-banks\Init.bnk` and `...\music_prologue.bnk` |
| Comparison | `C:\Dev\witcher-music-control\build\white-orchard\bank-comparison.json` |
| Input verification | `C:\Dev\witcher-music-control\build\white-orchard\protected-input-verification.json` |

W/w3_audio.wproj:2 declares v2023.1.19 / build 8928 / schema 119. WAAPI getInfo independently confirmed that version and WwiseConsole. Python was the existing 3.14.3 installation; only its standard library was used. P/mixer-authoring.json records the actual API version, allocated objects, project path, and complete bypass table. No additional software or licence was installed/activated.

## Isolated construction and reproducibility

Prepare copies the required global work units, retains the music_prologue subtree and its prologue events/bank, and supplies empty required default roots. It copies **47 referenced originals totalling 900,846,184 bytes**. The input manifest records 46 project/work-unit inputs plus those 47 originals. All **93 protected inputs rehashed unchanged** at completion. Output paths, cache/originals paths and external-source paths are isolated; source control and project generation commands are disabled. There are no hardlinks to installed media.

The baseline and prototype are separate self-contained authoring copies. Validation is another copy, with synthetic test audio and recorders; it is never a shipping source. Its test-only world bus configuration is explicit 5.1, and Recorder.DownmixToStereo is False. The prototype bus instead inherits its native parent channel configuration. Generator explicitly refuses the `validation` project.

Author verifies the open WAAPI project path and tool build before mutations. It creates:

- `Master Audio Bus/Immerse/Music/WMC_WorldMusic`, ShortID **392010734**, Voice/Bus Volume at native new-bus unity defaults.
- `WMC_ExplorationVolume`, `WMC_DialogueVolume`, `WMC_CombatVolume`, range 0–100, initial values **0 / 0 / 100**.
- Three custom Wwise Gain instances, plugin class ID **9109507 (0x008b0003)**. Each has FullBandGain and LFEGain RTPC curves `(0,-96.3 dB)` to `(100,0 dB)`, Linear.
- Three EffectSlot.Bypass state-property tables: exploration variants enable only exploration; dialog_scene variants enable only dialogue; combat variants enable only combat; all other current states bypass all three.
- Only music_prologue/world_music (`{1A59CC64-141A-45A6-8374-EB823D3E9D4F}`, ShortID **1033516231**) gets OverrideOutput=True and OutputBus=WMC_WorldMusic.

**Concrete API detail:** setStateProperties targets each EffectSlot, selecting `Bypass`. setStateGroups must target the **owning Bus**, not the slot: the installed API rejected a direct slot call with “Please provide its owner instead.” Wwise creates the per-slot CustomState objects; Author writes their explicit Boolean values for all 25 states. Schema/API evidence: `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\Schemas\WAAPI\ak.wwise.core.object.setStateGroups.json`, `...\setStateProperties.json`, and P/Master-Mixer Hierarchy/Default Work Unit.wwu / WMC_WorldMusic / StateInfo and Effects.

**Correction to report 05's initial proposal:** the two-point identity-dB input curve did not produce an identity-dB output. A requested -12 input measured roughly -1.16 dB; -24 measured roughly -2.49 dB; -6 roughly -0.57 dB. This is consistent with interpolation of the endpoint gains in amplitude. The implemented percent-domain curve fixes this; test inputs 25.1189%, 6.30957%, 50.1187% measured about -12/-24/-6 dB. The eventual settings adapter should write percentages directly, not log-converted dB to these parameter names. This correction comes from recorded processing, rather than schema inference alone.

Authoring transport startup restores parameter defaults. Probe consequently applies global values **after** starting playback, clears transport-local overrides, and captures profiler RTPC values. Using setters before transport startup gave misleading default-level results and was corrected. The accepted matrix records both the requested dB-equivalent levels and the actual global/transport values.

## Validation results

Evidence: V/probe/matrix.json, V/probe/measured.json, and its 31 separate case WAVs. The source is a generated 6-channel tone: five full-band frequencies and a 60 Hz fourth/LFE channel. Measurement uses a stable middle-quarter PCM window; the remaining channels are not substituted for LFE.

| Check | Observed result | Limit / falsifying test |
|---|---|---|
| Exploration with controls equivalent to -12/-24/-6 | About **-12 dB** on all six channels | Wrong inactive-control multiplication would instead sum gains |
| Dialogue, same controls | About **-24 dB**, including LFE | Any quest attenuation is checked separately below |
| Combat, same controls | About **-6 dB**, including LFE | Does not force native combat layers to full intensity |
| Inactive controls at floor; active control unity | Unity in exploration, dialogue and combat | Confirms inactive sliders do not contribute |
| Cutscene / music_only and unclassified states | No added attenuation | Native parent muting/fades are still allowed |
| Exploration at 0% / Gain endpoint | All six recorded PCM channels zero | **16-bit output only**; not proof of internal float/game digital zero |
| All three controls at 0%, cutscene | Unity additional gain | Confirms cinematic bypass rather than forced playback |

All 31 recorded checks passed the 0.15 dB non-floor tolerance or the explicitly limited PCM-zero check. Movie's recorder is itself bypassed by native upstream effect-bypass behaviour after the state transition; its short recording is **not a steady-state final-output movie test**. All 25 state tables are authored/compiled, but native movie muting and real cutscene playback still need game testing.

Evidence for actual music paths: V/contexts/contexts.json includes voice GUIDs, base volumes, bus instances and voice-contribution trees; V/contexts/native_white_orchard.wav and q001_conversation_direct.wav are ignored recordings. Context driver's Event GUIDs/playlist targets resolve to W/Events/music.wwu and W/Interactive Music Hierarchy/music.wwu, also traced in reports 03 and 09.

| Authoring simulation | Actual active music source(s) | Route with E/D at 0%, C at 100% |
|---|---|---|
| mus_loc_prologue_village + exploration | tw3_prlg_village_exploration | WMC_WorldMusic → Music |
| Same village + dialog_scene | tw3_prlg_village_exploration | WMC_WorldMusic → Music |
| Village + combat | tw3_km_01_combat_layer1 / layer2 | WMC_WorldMusic → Music; native layer weighting remains |
| mus_cs001_tavern_intro | tw3_cs001_tavern_intro | Music; WMC bus absent after transition |
| mus_q001_tavern_conversation + dialog_scene | tw3_nml_08_exploration_int1 / int3 | Music; WMC bus absent |
| Direct q001 conversation playlist `{EFA886D9-2BAD-4354-9DC3-BC08E2E75727}` + dialog_scene | Same two authored-selected layers | Music; positive recorded PCM with dialogue 0% |

The tavern cue's exploration-named source files do **not** make it generic exploration: the posted quest selector and verified quests_and_cutscenes playlist govern its routing. Generic village dialogue and that authored conversation receive different gains without track enumeration.

Native event transitions can remain pending: one short initial sequence still played the 82.667-second tavern intro when the conversation event had already been posted. The later accepted event simulation selected the conversation sources; an independent direct-playlist case also verifies their protected path. Event posting alone is not proof that a requested cue is the current audible voice. No in-game availability of an earlier q001 save was assumed or tested.

**Protected-path/master test:** synthetic audio routed directly to Music changed by only about **0.015 dB or less** when all three contextual controls changed from 0 to 100%. Setting vanilla menu_volume_music to 50 produced about **-6.023 dB** versus 100%. Evidence: V/contexts/protected_all_zero.wav, protected_all_unity.wav, protected_music_half.wav and contexts.json. The normal Music control remains an additional master in the authoring graph; actual game-menu/save-load behaviour is untested.

### Transition test: a remaining failure mode

V/transitions/world-gates.wav records a continuous tone through cutscene → exploration → dialogue → combat → cutscene with the -12/-24/-6 dB-equivalent controls. V/transitions/transitions.json records calls; measured.json records PCM adjacent-sample steps in approximate transition windows.

The unchanging full-level probe's normal adjacent steps were 66–154 counts on full-band channels and 14 on LFE. Gate changes produced steps up to **1,376 full-band counts and 1,507 LFE counts** in the examined windows. **Observed:** abrupt discontinuities exist. **Inference:** Boolean switching is click-prone and cannot be advertised as a smooth contextual fade. These numeric measurements are not a listening verdict, nor proof of a particular perceived severity in native music. Existing authored transition HIRC bodies remain byte-identical, but that does not remove discontinuities introduced by our gain gates.

**Next falsifying/acceptance test:** establish a transition-safe Wwise construction or measured mitigation, then repeat sustained-tone and actual village dialogue/combat transitions. Do not change vanilla state timing, threat weighting or scene events to disguise this issue. A state-hook fallback remains unimplemented and unapproved; the present steady-state mechanism needs none.

## Generated banks and global Init blocker

Generator's command.json, generation.log and result.json are in `C:\Dev\witcher-music-control\build\white-orchard\baseline-banks` and prototype-banks. Both runs explicitly selected **--bank music_prologue --platform Windows --language SFX**, isolated SoundBank/cache/root-output paths, and disabled generation hooks/source control. Wwise automatically generates Init alongside the selected bank. There were **two .bnk outputs in each run**, plus metadata and 47 conversion WEMs; no other regional bank was generated.

| Final experimental output | Bytes | SHA-256 |
|---|---:|---|
| Init.bnk | 30,277 | `377e410b6ffca6aea0648798c3de057e896e0da1bec33b32586ac0e81cc0d427` |
| music_prologue.bnk | 174,826 | `cdb142b9acfb323a47a4842f34223284464b984252421ea51532b73024f974bd` |

Both BKHD versions are 150. Generation returned **exit 1**, with six “No license for Mastering Suite” errors for HomeCinema in Init. The generator treats this as failure; files existing is not a successful build. The earlier isolated project verification succeeded after supplying required empty defaults; final verification is separately recorded below.

`build\white-orchard\verification.json` and baseline-verify.log / prototype-verify.log record final **exit 0** for both project verifications; prototype used `--abort-on-load-issues --verbose`. Baseline emits the non-failing ModifiedSharedProperties update message. The verify operation does not support `--no-source-control`; an initial unsupported-option invocation is retained separately and the corrected invocation passed. This verifies project/reference loading, not licensing, generated-bank loading or game behaviour. Python compilation and `git diff --check` also passed.

Comparison's HIRC records are decoded only as type/ID/opaque body; it does not infer undocumented body semantics. Against vanilla, baseline music_prologue has identical HIRC, DIDX and DATA, differing only in BKHD. Prototype changes **one HIRC record**, world_music ID 1033516231, of unchanged length 430 bytes; all other regional records and all embedded media remain identical. Existing events, quest/cutscene containers, combat composition and authored transition records are therefore unchanged in this bank. Streamed media references in their unchanged bodies remain unchanged; converted WEMs are not proposed as extra mod media.

Against the isolated baseline, prototype Init adds one Bus (392010734) and three custom Gain records (151295419, 352367310, 966399932); **no existing HIRC record changes or disappears**. STMG adds the new controls. However, the baseline already differs from native Init:

| Missing native HIRC type | IDs |
|---|---|
| Bus, type 8 (eight records) | 542827472, 1411735597, 1505802601, 2041642433, 2320575434, 3803860308, 4004099879, 4253138028 |
| Custom effect, type 17 | 890724639 |
| Effect ShareSet, type 16 | 4131355637 — HomeCinema |
| AuxBus, type 18 | 4189995869 |

**Type correction from follow-up evidence:** this row was originally labelled AudioDevice. Cross-matching the complete project's WAAPI objects with native HIRC verifies 41 AuxBus objects as type 18 and all four AudioDevices as type 21. The four AudioDevice records are retained unchanged in the reduced baseline; the missing record is an auxiliary bus. See follow-up/native-hirc-type-crosscheck.json at the absolute build root in report 11. The omitted IDs themselves have not changed.

Native INIT registers **18 plugins**, reduced baseline/prototype INIT **9**; baseline STMG also differs from native. HomeCinema is verified at W/Effects/Factory Mastering Suite.wwu / `{F9951DC8-664E-4B07-81CF-61716236F00A}` and referenced by W/Audio Devices/Default Work Unit.wwu's System and System_Immerse_on effect slots. The other ten omissions were not resolved to named source objects; do not attribute all differences solely to the reported licence error. Reduced project/plugin inclusion and source-versus-shipped global differences remain possibilities.

**Blocker:** obtain a generated or otherwise rigorously verified augmentation of native Init that retains unrelated global records, registrations and definitions while adding this mixer. Resolving the licence message alone has not been proved sufficient. No global-effect removal, unverified binary splice or replacement native Init was used as a workaround.

## Minimal soundspc.cache packaging investigation

`C:\Dev\witcher-music-control\build\white-orchard\cache-audit.json` rechecks the installed game's CS3W v2 cache. Its 2,174-resource index resolves native Init (32,840 bytes) and music_prologue (174,826 bytes), version 150, with the hashes already recorded in report 06. Follow-up classification finds 740 .bnk and 1,434 .wem entries; the original description of all 2,174 as banks was incorrect. This is read-only parsing, not a cache writer or loader test.

Installed command evidence remains `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\bin\tools\cooker\local_tests\soundbank_cooking\wcc_cooksounds.cmd:7` and wcc_splitcache_sounds.cmd:7. The executable contains cooksounds/soundbanksdir/wwiseProj/outdir options and Wwise selected-bank command fragments. Those strings establish available concepts, not a proven minimal packing invocation.

Bounded attempts used the existing `...\bin\x64_RedKit\wcc_lite.exe help cooksounds -noninteractivecrash`, with working/output logs in ignored build directories. Evidence:

- `build\white-orchard\wcc-cooksounds-help.log` / wcc-help-result.json: 2 GiB commit allocation failed, exit 3; also missing local gameconf.
- `...\wcc-cooksounds-help-configured.log` / wcc-help-configured-result.json: copied isolated gameconf, then depot-path assertion and missing always-loaded ly_animal_dog bank; bounded termination at 30 seconds.
- `...\wcc-cooksounds-help-isolated-root.log` / wcc-help-isolated-root-result.json: attempted isolated data path, but engine prefixed that absolute value with the REDkit installation root, producing an invalid path; bounded termination at 18 seconds, before command execution.

The latter logs are initialization/rooting failures, not evidence that the partial depot is defective or needs regeneration. No installed config was edited, no actual cooksounds/export batch was executed, and no cache was generated. **Exact remaining packaging blocker:** establish the supported isolated cooker root/bootstrap configuration and required read-only bank inputs, or a verified independent entry-level writer. The observed bank index alone does not establish the streamed-media/hash/header serialization or loader precedence needed to certify a new cache.

**Minimum candidate deployment footprint remains:** a matching native-preserving bootstrap Init plus a minimal mod soundspc.cache containing music_prologue and, conservatively, matching Init entries. No new soundtrack media, script, UI, other regional banks or depot should be necessary for this one-bank proof. This is a proposed entry set, not a loader-compatible package already delivered. The current experimental Init must not be used for it.

## Signal graph and next step

```text
vanilla game_state ─────► three EffectSlot.Bypass gates
vanilla music_type ─────► music_prologue's existing world/quest selection

future settings only ───► WMC_ExplorationVolume / DialogueVolume / CombatVolume
                         (global amplitude percentages, defaults 0 / 0 / 100)
                                  │
music_prologue/world_music ─► WMC_WorldMusic [three Gain slots] ─► Music
music_prologue/quests_and_cutscenes ────────────────────────────► Music
                                                               │
                              native Music volume/state/fades ──┴─► native output
```

Current prototype source is the Spec plus our authoring/build/probe helpers. Current generated bank set is exactly Init.bnk and music_prologue.bnk. **Stop here before live deployment.** Next work should address native-preserving Init generation, a demonstrated minimal cache path, and smooth state-gain transitions. Only after those pass should a separately authorized isolated mod profile test the same White Orchard traversal, village dialogue and encounter with a backed-up save. Real save/load, game Music UI, long listening, native combat intensity and safely replayable q001 scenes remain untested. Exceptions such as other quest-relevant world locations remain report 07's later milestone; this is bank-scoped, not a White Orchard geofence.

## Reproduction commands

These paths document this run. Prepare refuses existing destinations; use fresh isolated output directories for a new run rather than overwriting the evidence. Commands/flags for the actual generation are also preserved verbatim as JSON alongside each bank set.

```powershell
$wmcAudio = 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio'
$wmcConsole = 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe'
python tools/white_orchard_prepare.py --audio-project $wmcAudio --output build/white-orchard/baseline
python tools/white_orchard_prepare.py --audio-project $wmcAudio --output build/white-orchard/prototype
python tools/white_orchard_wwise.py --console $wmcConsole --project build/white-orchard/baseline/w3_audio.wproj --output build/white-orchard/baseline-banks
```

Start the local prototype WAAPI server in a separate shell (no GUI needed), then run Author from the repository shell. Never point this server/Author at the installed project.

```powershell
& $wmcConsole waapi-server 'C:\Dev\witcher-music-control\build\white-orchard\prototype\w3_audio.wproj' --http-port 18090 --wamp-port 18080 --allowed-addr 127.0.0.1 --no-source-control
```

```powershell
python tools/white_orchard_author.py --project build/white-orchard/prototype/w3_audio.wproj
python tools/white_orchard_wwise.py --console $wmcConsole --project build/white-orchard/prototype/w3_audio.wproj --output build/white-orchard/prototype-banks
python tools/white_orchard_compare.py --vanilla 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc' --baseline build/white-orchard/baseline-banks --prototype build/white-orchard/prototype-banks --output build/white-orchard/bank-comparison.json
```

Stop that server; copy the isolated prototype project/work units/originals into a separate `build/white-orchard/validation` workspace. Run a server against that validation project instead, then:

```powershell
python tools/white_orchard_probe.py --project build/white-orchard/validation/w3_audio.wproj
python tools/white_orchard_measure.py --folder build/white-orchard/validation/probe
python tools/white_orchard_contexts.py --project build/white-orchard/validation/w3_audio.wproj
python tools/white_orchard_transitions.py --project build/white-orchard/validation/w3_audio.wproj
python tools/white_orchard_measure.py --folder build/white-orchard/validation/probe
```

The last measure checks that the retained matrix recordings still pass after other simulations. Stop the validation server when finished. All task-owned Wwise/WCC processes were stopped at completion. No deployment command exists in these helpers.
