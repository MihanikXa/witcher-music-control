# 25 — Transition bleed reproduced; local playlist fix measured; D licence pending

Date: 2026-10-12. Started from `main` at `c6c1092`, fetched origin and verified no divergence. No game launch, deployment, Vortex change, save modification, installed-resource edit, licence transfer or unrelated-bank generation.

**Later follow-up:** after the user manually applied the licence, [report 26](26-licensed-transition-fix-candidate.md) records successful licensed generation, structural/playback validation and the D package. The failed generation and evidence below remain preserved as historical results. D still awaits separate deployment authorization and gameplay validation.

**Result:** the isolated authoring tests reproduce exploration score becoming audible during combat entry and through short intermediate scene states. A bounded playlist-level correction suppresses those continuing generic voices while preserving native combat and q001 voices in the tested sequences. Clean D authoring source is prepared, but its fresh project lacks effective licence coverage. Generation exited **1 and produced no banks**. Therefore there is **no D bank, cache, Vortex ZIP, package hash or runtime compatibility claim**. Manual project-local licence application is the next prerequisite.

## Evidence paths

These are explicitly labelled machine-local build evidence, retained outside Git:

| Alias | Exact path |
| --- | --- |
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| G | `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3` |
| T | `L:\Programs\Wwise_2023.1.19.8928\Authoring` |
| V | `C:\Dev\witcher-music-control\build\white-orchard-transition-diagnosis\validation` |
| P | `C:\Dev\witcher-music-control\build\white-orchard-transition-fix` |
| C source | `C:\Dev\witcher-music-control\build\licensed-white-orchard-stage1\candidate` |

Raw profiler paths, accepted State/event wall timestamps and voice contributions: `V\native-transitions\results.json` (14 control/C cases), `V\pinned-playlist-transitions\results.json` (seven corrected cases). Each directory has `transition-measurements.json`, generated read-only by `C:\Dev\witcher-music-control\tools\white_orchard_transition_measure.py:measure`, plus available six-channel PCM16 recordings. `P\target-consumers.json` records selector consumers; `P\preservation-and-diagnostics.json` records provenance and diagnostic counts. No older test evidence was overwritten.

## Actual mechanism and source evidence

**Observed source:** `G\content\content0\scripts\engine\sound.ws:156–190`, `CScriptSoundSystem.SoundGameStateChange`, submits `SoundState("game_state", GameStateToString(gameState))` after combat callbacks. It does not wait for a music segment to change. The periodic classifier and priority handling are at `sound.ws:557–624`; `game/player/r4Player.ws:5847–5876`, `ShouldEnableCombatMusic`, supplies combat selection. No script interception is introduced.

**Observed native data:** `G\bin\initialdata\sound\Init.bnk`, STMG group `766723505`, has default transition **1000 ms** and 43 custom transitions, parsed with existing `white_orchard_state_bank_audit.py:native_groups`. `W\States\global_states.wwu:138–176` explicitly gives exploration/day/night→dialogue and exploration→cutscene **two seconds**, not one second. These files remain unchanged.

**Observed music rules:** `W\Interactive Music Hierarchy\music.wwu:122301`, world GUID `{1A59CC64-141A-45A6-8374-EB823D3E9D4F}`, selects regional locations. Under `general`, the transition rules around `:122449–122549` retain source exploration while scheduling combat and fading the two paths. Exploration→combat specifies `ExitSourceAt=3` and four-second source/destination fades; combat→exploration retains its authored combat outro. Matching `T\Data\WObjects\WObjects.xml:2494–2508` defines **3 = Next Beat**, **2 = Next Bar**. Destination synchronization definitions are at `:2532–2544`. Thus selection and gain have different clocks; the numeric enums were verified locally rather than guessed.

**Observed measurement, combat:** C accepted combat at wall time **6.022 s**. The still-playing `tw3_prlg_village_exploration` voice rose to approximately −32 dB at 6.27 s and **−19 dB** at 7.02 s, including Music master and native fades. At 7.02 s its contributions show Music = −17 dB, world_music = 0 dB. The first sampled audible `tw3_km_01_combat_layer1` appears around **7.38 s**; exploration continues fading beside it. A second change at 7.3 s reproduces the exposure at a different musical phase. This directly establishes gain reopening a continuing exploration voice, with switch synchronization/overlap prolonging it. It is not an attribution based on the user's approximate duration.

**Observed scene source:** `G\content\content0\scripts\game\scenes\scenePlayer.ws:127–155,189–261`, `CStoryScenePlayer`, enters movie/music-only, blocking dialogue and cutscene states, and returns from those states. This proves such states are available in scene sequencing. It does **not** prove which states the user's particular conversation traversed.

**Observed measurement, dialogue:** direct exploration→dialog_scene→exploration never reopened the generic voice in C. Exploration→cutscene for 400 ms→dialog_scene did reopen it, then return to attenuation. Movie/music-only intermediates also produced a brief recorded swell under the simulated timing. These are demonstrated mechanisms consistent with the reported dialogue symptom; the exact in-game conversation sequence remains an **inference**, not a captured runtime fact. A clip identifying the NPC, dialogue entry/exit and location would falsify or refine that inference if D does not solve it.

## Reproduction and measurement

`C:\Dev\witcher-music-control\tools\white_orchard_transition_probe.py:run` prepares measurement fixtures **only** in a guarded `validation` project. Fresh preparation retained all **1,508** work units and 47 regional originals (900,846,184 bytes). Wwise reports build **8928**. No measurement fixture enters production source.

The control is unity State gain in the same instrumented complete project, not a newly generated licensed baseline bank. C uses its existing 25-State table; the corrected probe uses the same table plus the five local properties below. Tests play actual `play_music_prologue`/`mus_loc_prologue_village` events and native playlists. These are not the previous sustained-tone tests. Each case runs 19 seconds, changes State after six seconds (also 7.3 seconds for an offset combat case), and retains native transition and threat curves.

| Sequence | C peak generic voice contribution after transition | Corrected probe peak | Result |
| --- | ---: | ---: | --- |
| Exploration→combat at 6 s; combat→exploration at 13 s | −19.00 dB | ≤−217.44 dB | C exposes old exploration; corrected path stays attenuated; combat remains audible |
| Exploration→combat at 7.3 s | −20.06 dB | ≤−217.76 dB | Reproduced at another musical phase |
| Exploration→dialogue at 6 s; dialogue→exploration at 10 s | ≤−219.03 dB | ≤−417 dB | No direct-transition burst reproduced |
| Exploration→cutscene→dialogue, intermediate 400 ms | −32.32 dB | ≤−232.28 dB | C swell removed in corrected profiler path |
| Exploration→movie→dialogue, intermediate 400 ms | −31.32 dB | ≤−230.25 dB | C recorded swell; corrected voice remains attenuated |
| Exploration→music_only→dialogue, intermediate 400 ms | −26.49 dB | ≤−227.15 dB | Same result |
| Exploration→cutscene + `mus_cs001_tavern_intro`; dialogue + `mus_q001_tavern_conversation` | Generic predecessor briefly exposed | Generic predecessor attenuated | Protected authored voices remain audible |

Table generic peaks use contribution totals in the 6.1–12 s wall-time window; quantities are gain contributions, not sound-pressure measurements. Combat layer1 reaches **−17 dB** in the corrected runs. The original outro and layering paths are still present. For the authored case both C and corrected probe reach **−18 dB** for `tw3_cs001_tavern_intro` and **−22 dB** for the conversation's `tw3_nml_08_exploration_int3`; its `int1` voice reaches about −22.12 dB. Profiler ancestry places them under `quests_and_cutscenes/q001_beginning`, outside the edited paths. This is positive authoring evidence for both intro and conversation, not in-game confirmation.

PCM envelopes are measured at **50 ms** intervals. Profiler sampling median is 109–125 ms, maximum below 195 ms, so this is not a sample-exact voice onset measurement. Recorder audio and wall-clock origins differ; the analyzer explicitly does not align them sample-for-sample. Native transport playback did not keep the separate silent anchor active throughout every run. C's fully attenuated direct-dialogue case and corrected silent scene cases emitted **no recorder file**. That absence is not labelled measured zero PCM; the contribution traces demonstrate attenuation. Other captures contain actual audio, including C's intermediate-state swells and corrected combat/authored cues. Do not infer internal mathematical zero from these tests.

Added `combat-threat` and `q001-direct`/Music-slider probes are ready in the helper but were **not executed** after the fresh production project hit its licence stop. The existing threat curves and Music slider are structurally untouched; a fresh intensity sweep and slider measurement remain pre-packaging checks. Night/camp/cemetery/battlefield playback and long virtual-voice recovery also remain coverage gaps. Playlist randomness and differing initial fades preclude claiming sample-identical control/C audio.

## Smallest supported correction

Keep C's world State table. Set static **Voice Volume = −200 dB** on five existing generic noncombat playlist containers. Their own continuing voices then cannot be exposed merely because their parent State gain returns to unity. No change to synchronization, transition durations, events, threat weighting, Music master or new global definitions is needed.

Exact targets in `W\Interactive Music Hierarchy\music.wwu` and `C:\Dev\witcher-music-control\src\wwise\white-orchard-transition-fix.json`:

| Playlist | Existing ShortID | Previous static volume | D volume |
| --- | ---: | ---: | ---: |
| `general/village_exploration` (`:122550`) | 133462974 | −2 dB | −200 dB |
| `general/expl_nml_zone_01_PROLOGUE_NIGHT` (`:124140`) | 168472101 | 0 dB | −200 dB |
| `nilfgaard_camp/expl_nilfgaard_camp` | 883068472 | 0 dB | −200 dB |
| `cemetery/expl_cemetery` | 1049502408 | +1 dB | −200 dB |
| `battlefield/expl_battlefield` | 833483595 | +1 dB | −200 dB |

GUIDs and expected original values are pinned in the specification. All **40 AudioNode consumers** of these five objects are inside White Orchard world_music; no Events work unit directly references those playlist GUIDs. Transition endpoint references also exist, and are preserved. This is object/routing evidence, not a filename heuristic. A source-equivalent correction was exercised in the separate fixture before clean D was authored.

`C:\Dev\witcher-music-control\tools\white_orchard_transition_author.py:author` requires the existing clean State-authoring proof, checks identities, parentage, original properties, complete work units and consumer scope, applies supported WAAPI `setProperty(..., "Volume", -200)`, and fails unless restoring just those five properties makes the music work unit semantically identical. Production run proved **only five static volumes changed**, the C-stage State table/native transitions preserved, no unrelated WWU changed and all 1,508 retained. Consumer checks added to the reusable helper were independently evaluated against the same source: 40 world-only consumers, zero direct-event references.

Only `Interactive Music Hierarchy/music.wwu` differs from original input, containing C StateInfo plus these five properties. D source SHA-256: `cba9ed036e94fe658ca8e506d5539e1f7139f7caea51a21cac3fadbdcebcc259`. `P\candidate\transition-clean-authoring.json` retains the clean source audit. Fresh locally generated CustomState GUIDs may differ from C source; their **State meanings/values** are unchanged. Future generated-bank comparison must require the world HIRC body to equal C, not infer serialization from XML.

**Authored-music boundary/risk:** `general_winter`, `tavern_winter`, `village_q505`, combat, Gwent and `quests_and_cutscenes` are unmodified. Report07's quest-themed world exception is not permanently muted. The five ordinary playlists are now attenuated even when selected/continuing during cutscene/movie/music_only. Deliberately authored sibling cues retain native gain and transitions. Source routing cannot establish author intent for every use of an ordinary playlist during a scene; game validation must check available authored cues. The correction intentionally does not promise to remove a burst from an unclassified winter/quest-themed world playlist. It also retains C's existing combat→exploration root gain fade, rather than redesigning that policy.

## Alternatives assessed

- **Shorten/remove the State fade:** rejected without implementation. It would reopen the old exploration voice sooner and disturb native gain behavior; it does not address voice provenance.
- **Mute all intermediate states or global Music:** rejected without implementation. It would suppress authored branch/music-only content rather than isolate the continuing generic voice.
- **Force immediate playlist switches/stop voices:** rejected without implementation. It removes native beat synchronization, overlap or outro behavior instead of preserving them.
- **Script-assisted delayed combat unmute:** not necessary for the reproduced local mechanism; adds timing and hook risks and could truncate early combat music. Not implemented.
- **Five static generic-playlist properties:** tested successfully for the village/day transition matrix; chosen for bounded source preparation. Other location/intensity/slider checks and generated-bank validation remain outstanding.

## Build stop, preservation and next gate

Fresh production project prepared with `white_orchard_prepare.py --preserve-hierarchies` at:

`C:\Dev\witcher-music-control\build\white-orchard-transition-fix\candidate\w3_audio.wproj`

Existing clean State helper then transition helper were run through matching isolated WAAPI. No key was inspected, requested, copied, transferred or logged. Selected generation used the existing `white_orchard_wwise.py` Windows/SFX/music_prologue workflow into `P\candidate-banks`; exact command, log and result are retained there. **Exit 1**, no `.bnk` output: six HomeCinema/Mastering Suite licence errors, one fatal **26,218/200** trial-media error, nine MediaMultipleUsage warnings and one Wwise.dat consistency warning. These failures are recorded rather than hidden or relabelled exit-code2 success. No inclusion experiment, header patch, bank splicing or cooker invocation followed.

Because no D bank exists, D BKHD ProjectID, HIRC fidelity, streamed/embedded media preservation, Init dependency serialization, cooker identity and ZIP validation are **not yet established**. Source scope adds no global object, but that is not a substitute for those bank checks.

Original installed REDkit inputs and copied regional source media match the fresh input manifest. C source/bank/cache and both A/C archives still match reports22–24. Game loose Init is unchanged at SHA-256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`. C bank remains `80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698`; C ZIP remains `8e4a00259421b902e93e232149f868bd3c1008657ac933ff0d1aaa6e5c123d9a`. All started Console processes were stopped. Existing verification-tool unit tests: **14 passed**; new helpers compile. No licensed binaries or private profiles are committed.

**Next user action:** open the exact isolated D project above in Wwise 2023.1.19.8928, apply the already-approved entitlement through **Project → License Manager**, and save. Do not send the key to Codex. Then authorize continuation of local build/verification. Retain failed build evidence and use a fresh output folder for the licensed retry.

Before packaging: finish preservation/intensity/slider probes, generate selected bank, explain diagnostics including exit-code2 warnings, compare D against retained C and licensed baseline. Allow only the five existing playlist property changes relative to C; require world State data byte-identical, all other HIRC/media/references unchanged, unchanged global dependencies/disposable Init and explained BKHD metadata. The original C-only gate must not be weakened to accept arbitrary extra HIRC changes. Use the native cooker and exact readback, then produce **WMC White Orchard — Transition Fix Test.zip** with the same exclusive mod/content cache path and no Init/media/project payloads. No archive is available now.

## Later C → D → C game checklist (requires separate deployment authorization)

After D passes all pending checks, retain C ZIP and the report23 profile/save rollback plan. With game closed, enable only C or D in the existing isolated Vortex test profile; the two variants target the same `Mods/modWMCBankLoadingTest/content/soundspc.cache`. Verify the deployed hash and that no second variant remains active. Do not change other mods or Music settings between variants.

For each fresh game process, load the same copied White Orchard save and repeat the same village dialogue and combat encounter. Record dialogue entry **and exit**, combat entry, intensity progression and combat→exploration. C should reproduce the burst on the selected route; D should keep generic exploration inaudible until the combat cue itself starts, retain combat/outro continuity and preserve available authored q001/quest cues. Return to C to confirm the difference. Avoid quickloading an advanced save or interpreting a natural soundtrack gap as proof. Check native Music-slider behavior and long silence recovery; note any scene score lost under D. If a burst persists, supply a short clip and NPC/location/day-night context before broadening the fix. Do not label D successful in game from these authoring results.
