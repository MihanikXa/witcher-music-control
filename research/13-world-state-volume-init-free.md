# Direct world State Voice Volume — 2026-10-11

## Result

**Authoring mechanism works; no validated bank candidate.** Existing `game_state` can directly control `music_prologue/world_music` Voice Volume. Hard-coded exploration/dialogue attenuation, normal combat, native fades, LFE and q001 protection passed the tests below. There is no demonstrated need for new global parameters, buses, effects or a state hook at the source level.

**Concrete current workflow blocker:** the installed supported bank-generation interface does not provide a verified prohibition on Init generation. The user explicitly prohibited regenerating global Init. No bank-generation operation was invoked, including in-memory generation. The available project tools parse bank chunks and opaque HIRC bodies; they cannot safely serialize the new local State data or establish its references. We did not improvise a binary patch. Consequently the alternative is **not disproved**, but cannot produce a certified regional bank under the current restriction and verified tooling. Do not confuse this blocker with the earlier full-Init licensing problem.

No licence was requested/applied; no installed resource, save, playthrough or depot was changed; nothing was deployed. Earlier reports 10–12 and their evidence remain intact. No settings UI, other region or production authoring conversion was implemented.

## Exact evidence locations

| Alias | Absolute path |
|---|---|
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| R | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc` |
| T | `L:\Programs\Wwise_2023.1.19.8928\Authoring` |
| P | `C:\Dev\witcher-music-control\build\white-orchard-state-volume` |
| V | `C:\Dev\witcher-music-control\build\white-orchard-state-volume\validation` |
| A | `C:\Dev\witcher-music-control\build\white-orchard-state-volume\validation\state-volume-anchored` |
| C | `C:\Dev\witcher-music-control\build\white-orchard-state-volume\cooker` |
| Helper | `C:\Dev\witcher-music-control\tools\white_orchard_state_volume.py`, `run` / `levels` |

## 1. Concrete construction

W/Interactive Music Hierarchy/music.wwu's `music_prologue/world_music`, GUID `{1A59CC64-141A-45A6-8374-EB823D3E9D4F}`, ShortID **1033516231**, has no existing StateInfo in the source. We used the matching Wwise 2023.1.19/build8928 localhost authoring API:

```text
setStateProperties(world, ["Volume"])
setStateGroups(world, [existing game_state GUID])
CustomState.Volume = -200 for exploration/dialogue variants; otherwise 0
```

`Volume` here is **Voice Volume**, not bus volume or a percent-input RTPC. Installed T/Data/WObjects/WObjects.xml:179–196 defines it as an additive decibel property, engine property ID **0**, default **0**, permitted range **−200 to +200 dB**. MusicSwitchContainer inherits the common music/audio-node definitions. Installed `ak.wwise.core.object.setStateProperties.json` explicitly supports Volume; the actual API accepted it on this object. Existing group GUID is `{27711515-3584-4123-9F09-B90831398B80}`.

| Category | Existing States | Added Voice Volume |
|---|---|---:|
| Exploration | exploration, exploration_night, focus_exploration, focus_exploration_night, underwater, underwater_focus, boat | −200 dB |
| Ordinary dialogue | dialog_scene, dialog_scene_night | −200 dB |
| Combat | combat, combat_monster_hunt, underwater_combat, underwater_combat_focus, focus_combat | 0 dB |
| Every other current State | Remaining eleven of the 25 | 0 dB |

V/state-volume/authoring.json records all **25** explicit values and their new **local CustomState** GUIDs. The gain adds to the native hierarchy; zero means unity additional gain, not forced playback. The native `game_state` group, transition definitions, `music_type`, location selectors, OutputBus, events, playlists, audio files and native Music processing were not changed by the proposed source edit.

P/source-audit.json compares the first pre-fixture music work unit to the previous untouched isolated baseline: removing **only world/StateInfo** restores the complete XML structure/attributes/text exactly. The original pure edit is preserved at V/state-volume/world-state-only-music.wwu. Wwise also initialized the formerly empty default Control Surface Session with authoring UI bindings; that is recorded as an unrelated authoring-only save effect, not a runtime edit. No native global work unit changed.

The later anchored run reuses the measurement workspace and contains fixture objects. Its saved work unit is **not pure shipping source**, despite the historical helper output filename. Only the first pre-fixture snapshot supplies the source-equivalence claim. This reduced authoring workspace is never a basis for regenerated Init.

## 2. Levels and native transition measurements

An imported 90-second 5.1 MusicTrack sits beneath a test MusicSegment under the **actual world container**, so the measurement exercises inherited world Voice Volume rather than a copied gate on an unrelated Sound. Distinct full-band tones plus a 60-Hz LFE use the original pilot's PCM16 amplitudes. Fixtures override Continue-to-play and capture Music at explicit 5.1; those settings are excluded from the proposed edit.

Three continuous approximately 20-second runs use cutscene → exploration → dialog_scene → combat → cutscene, four seconds per State. Baseline sets all local additions to zero; unequal uses E/D/C **−12/−24/−6 dB**; defaults uses **−200/−200/0 dB**. These are fixed State property values, not the adjustable mixer's percent RTPC inputs.

| Measurement | Observation |
|---|---|
| Baseline | All five steady windows at unity on six channels. |
| Unequal, first channel | 0 / −12.010 / −24.053 / −6.003 / 0 dB. All six channels within 0.15 dB of target. |
| Defaults | Exploration/dialogue measured steady windows contain zero PCM on all six channels; combat/cutscene unity. No claim of exact internal floating-point zero. |
| Transition adjacent-sample maxima | At most **66/88/110/14/132/154** counts across the six channels, matching the normal tone's steps; no large bypass discontinuity. |
| Baseline 100-ms envelope | Within 0.05 dB of unity. |
| Capture duration | 20.064 / 20.117 / 20.085 seconds. |

A/results.json, tone-analysis.json and acceptance.json record all **31 passing checks**: three duration guards, fifteen six-channel steady windows, twelve transition bounds and one baseline envelope. Native State timing was left intact. This proves tested authoring fades without scripting; it does not prove subjective game playback, all 25 States empirically, save/load, movie behavior or a bank loaded with native Init.

**Retained failure:** V/state-volume/defaults.wav is shortened (~8 seconds), because recording ceased while the attenuated tone was the only active source. It is not evidence of a complete transition timeline. A adds a silent, unity, direct-to-Music anchor outside world; all three captures are then complete. Anchor, Recorder, synthetic segment/track and forced channel layout are measurement fixtures only. V/state-volume-initial-save-check preserves the first overly strict save-audit failure, which revealed default Control Surface Session initialization.

## 3. White Orchard and authored protection

A/results.json's actual-selector snapshots use `play_music_prologue`, `mus_loc_prologue_village`, `game_state=exploration/dialog_scene/combat`, then `mus_cs001_tavern_intro` and `mus_q001_tavern_conversation`. Village source `tw3_prlg_village_exploration` receives the inherited attenuation (base volume below −200 dB in muted contexts). Combat layer1 is active near its native source level; layer2 remains subject to native intensity weighting. No intensity or event sequencing was rewritten. Track names containing `km` do not identify the chosen gameplay geography as the Kaer Morhen tutorial.

The intro can hold its native exit for a long time, so an event posted during it is not proof that the conversation immediately played. As in report11, the direct authored playlist `{EFA886D9-2BAD-4354-9DC3-BC08E2E75727}` isolates that cue without forcing game progress. It selects `tw3_nml_08_exploration_int1/int3` under the original authored branch, with no world gain in its contribution path.

P/protected-test.py repeats that same playlist at `dialog_scene` with the world State additions all-zero versus exploration/dialogue −200, then with native Music at 50%. A/protected-measured.json records:

- Positive stereo q001 PCM: RMS **379.326 / 383.796** in both unity and world-muted runs; measured gain change **0.000 dB** on both active channels.
- Native Music 50%: approximately **−6.030 dB** relative to world-muted/master100.
- All three protection/master checks passed. Remaining four captured channels are zero because this cue is stereo, not a six-channel authored-music test.

Source equality, routing snapshots and identical captured q001 level together support authored protection. They do not certify every quest-named world-location exception: anything under world still receives the hard-coded attenuation. Report07's exception policy is unchanged.

## 4. Init and serialized reference integrity

**Observed source-level dependency result:** the sole proposed runtime edit adds a Volume property association and local CustomStates referencing an already existing StateGroup/States. No new GameParameter, bus, AuxBus, effect, plug-in, AudioDevice or global State is authored. Native regional world selectors already use `game_state`; the user Music curve and global transition table remain the native ones.

**Supported inference:** the existing Init should provide the global definitions needed, with the new object-local property data stored in the regional bank. **Not proved:** the serializer's actual new records, their placement, numeric IDs, references, header flags or load behavior. Local CustomState GUIDs are new; they must not be mistaken for new global State enums or assumed to serialize without additional records. No edited bank exists in this task, so no claim is made that HIRC reference integrity has passed.

A real regional candidate would need:

1. A v150-aware decoder/serializer or matching Wwise output showing the complete changed world State/property data and any local records it owns.
2. Every new reference resolved to that bank or the original native Init's existing global definitions; no collisions or unexpected global additions.
3. All unchanged regional records, embedded media and stream IDs byte-equivalent; world gain content understood rather than merely allowing its whole opaque record to differ.
4. Native-Init + modified-bank loading through a matching runtime, followed by the same context/fade/protection tests. Authoring's dynamic project playback is **not this test**.

### Generation and BKHD boundary

T/Data/Schemas/WAAPI/ak.wwise.cli.generateSoundbank.json documents selected-bank output but no Init-suppression switch. `ak.wwise.core.soundbank.generate.json:100–102` exposes `rebuildInitBank`: it **forces** Init rebuilding when not using rebuildSoundBanks. Setting false does not promise that automatic generation will skip Init. `writeToDisk=false` changes output delivery, not the set of banks internally generated. Earlier selected-bank controls in reports10–12 emitted Init automatically and reported HomeCinema errors against it. There is no verified dry-run/skip-Init recipe in the inspected installed interfaces.

We therefore did **not** run those interfaces, manipulate generation caches or make Init unwritable to induce failure. A subsequent task permitting Wwise's incidental isolated Init output to be discarded could test whether direct-State regional output remains usable despite global licence errors; that is outside this turn's explicit no-regeneration restriction. Report12's successful regional emission is relevant precedent, not a test of this new State data.

Report12's E/bkhd-differences.json remains the precise caution: both previously generated bank headers differ from native at payload offset16 (**39→0**) and offsets24/28/32/36, despite equal bank version and unchanged regional media/HIRC. Those words' runtime meaning is unverified. Keeping most records or copying only a native header onto generated data would not establish compatibility. No such header transplantation or binary splice was performed.

`C:\Dev\witcher-music-control\tools\white_orchard_compare.py/read_bank` checks chunk and record lengths but deliberately leaves HIRC bodies opaque. The local helper inventory has no verified v150 State/property writer or loader test harness. Readable authoring XML is not a SoundBank schema. Only Story Music's string changes are not evidence for safely adding State property data. A compatible existing-bank editing workflow therefore remains unestablished; no software was installed to attempt one.

## 5. Init-free native cooker control

The existing native cooker bootstrap can package a **regional-only** input with no Init cache entry. P/regional-native-cook.py reproducibly uses the existing installed WCC, an ignored isolated root, original native Init copies for bootstrap, and a bank-input directory containing **only unmodified native music_prologue.bnk**. It calls `cooksounds -platform=pc_dx12 -r4remastersounds`, no wwiseProj and no Wwise process. Native Init is neither generated nor altered.

C/regional-native-verified.json records a **174,933-byte** CS3W v2 cache with exactly **one** indexed resource, music_prologue.bnk. Extracted payload is byte-identical native SHA-256 `75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912`. `splitcache sounds` exits0 through the native reader. Bootstrap Init retains native SHA-256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`.

This narrows the prospective minimum deployment to **one mod content/soundspc.cache with a regional-bank entry**, keeping installed Init entirely untouched. It proves serialization/readback of the native control; **modified-bank packaging and game mod-cache/media-fallback behavior remain untested**. Successful logs retain missing bank-text/seed-mapping warnings and bootstrap diagnostics; zero exit is not a live-loader test.

## 6. What is lost versus the adjustable mixer

| Capability | Direct State Voice Volume | Parallel adjustable AuxBus mixer |
|---|---|---|
| Hard-coded 0/0/100 policy | Demonstrated in authoring | Demonstrated in authoring |
| Native State fades / quest sibling protection | Demonstrated for tested tone/q001 | Demonstrated for tested tone/q001 |
| Three independent user sliders | **Lost.** Fixed E/D/C values compiled into the regional bank. New presets require rebuilding/editing banks. | Three independent 0–100 amplitude-percent RTPC inputs. |
| Native Music master | Retained in measured q001 test | Retained in prior measurements |
| Global Init edits | No source-level additions needed; actual serialized reuse unproved | New buses/effects/parameters require a complete compatible Init |
| Routing changes | Existing native routing retained | Four user sends, muted dry bus, aggregate and AuxBuses |
| Voice behavior | Gain is before output mixing; retain native virtual/threshold policy and verify game resume/overlap behavior | Gain is in downstream effects; voice/mixing behavior also needs game testing |
| Media assets / native intensity | No intended changes | No intended changes |
| Regions / world exceptions | Still only music_prologue; world exceptions still attenuated | Same pilot scope and exception limitation |
| Audio-mod conflicts | Replaces regional bank/cache entry; no intended Init conflict | Regional conflict plus global Init conflict |

Voice Volume range −200 differs from Gain's −96.3 floor. PCM-zero measurements do not imply an exact mathematical mute or altered playback scheduling. Neither design is an intermittent/sparse music policy. Adding adjustable context gains later would need new controls/routing or another proved construction; vanilla master Music cannot supply three independent contextual sliders.

## Stop decision and next demonstrated boundary

The proposed graph is now:

```text
vanilla game_state ─► existing world_music local State Voice Volume
                     exploration/dialogue −200 dB; combat/other 0 dB
vanilla music_type ─► unchanged world / authored selection
world_music ────────► unchanged native Music hierarchy/master/output
quests_and_cutscenes ► unchanged native Music hierarchy/master/output
```

Stop with an **authoring-proven Init-free design, bank-construction/compatibility blocker**, not a deployment candidate and not a finding that direct State volume cannot work. No licence is needed for the demonstrated authoring/cooker controls. The smallest remaining experiment requires either a verified regional-only generation mechanism, authorization for incidental isolated Init generation **solely to obtain regional output while retaining native Init**, or a verified existing-bank State serializer. Any resulting bank still needs the explicit BKHD/reference/native-Init load checks above. Do not request a licence as a prerequisite for this alternative merely because the adjustable design needed one.

P/final-verification.json rehashes **93 authoring inputs and 455 cooker inputs**, with zero installed-input changes. Both Init files anywhere beneath P are exact native bootstrap copies; no generated Init exists there. The split cache's sole regional payload is also verified byte-identical. Python compilation and `git diff --check` passed. Task-owned Wwise playback/server was stopped. The new ignored evidence, source snapshots and failed recordings are preserved; no deployment file was staged.
