# 55 — White Orchard native phrase/rest proof

2026-10-16. Implements the bounded experiment authorized in report54. **Source and Wwise authoring playback proof only:** no regional bank generation, cooker/package, retail launch, installation, save/profile change or licence access. Existing releases remain unchanged. Exact Sparse pacing and contextual triggers remain undecided.

## Result

**Observed:** a native phrase plays at native gain, completes through its native exit/tail, enters an intentional finite rest, and plays again. Two measured environmental-only intervals last approximately22 seconds each. Combat interrupts music and early/late rest, retains native threat response and completes its audible outro after exploration returns. Explicit authored playback, the separately declared technical world exception, Gwent and Music master controls pass.

**Limit:** native location/day/night reselection can cancel a rest and restart the permitted phrase. Combat return starts a new phrase using native transition overlap; it does not remember the old rest. This is a usable local scheduling mechanism, not a finished persistent or adaptive Sparse policy. No alternative architecture was needed or attempted.

## Reproducible implementation and boundaries

Repository paths below are relative to `C:\Dev\witcher-music-control`; build paths are ignored evidence, not release inputs.

- `src/wwise/experiments/white-orchard-sparse-v1.json`: pinned native identities, deterministic sequence and isolated gain scope policy.
- `tools/white_orchard_sparse.py`, `author`, `validate`, `expected_playlist`, `consumer_closure`: supported WAAPI authoring, independently reconstructed exact expected playlist, strict25-State canonical validation and complete source restoration. Production regional gates are unchanged.
- `tools/white_orchard_sparse_capture.py`, `cases`, `supplemental_cases`, `run`, `cleanup`: matched native/Minimal/Sparse captures, transport reset, location priming, accepted action times, scoped RTPCs, actual voice GUIDs/pipelines/contribution ancestry and Recorder output. A supplemental authored-during-rest test is retained separately.
- `tools/white_orchard_sparse_measure.py`, `case_summary`, `audio`: actual source-identity ancestry, profiler envelopes, 50ms PCM RMS and exact-zero intervals. `tools/white_orchard_sparse_review.py`, `review`: fail-closed measured acceptance checks with control hashes. `tools/test_white_orchard_sparse.py`: positive controls and negative gain, playlist, identity, State, event/transition consumer and cleanup tests.

Each fresh isolated control uses `white_orchard_prepare.py --preserve-hierarchies --immutable-originals build/licensed-white-orchard/baseline`: all1,508 original WWUs and47 immutable original audio inputs are preserved. Only the intended music WWU changes in Minimal/Sparse; native has no changed WWU. No source audio is edited. Installed original authoring context is read-only.

To reproduce, prepare separate fresh complete `validation` projects, start matching isolated `WwiseConsole waapi-server` instances with distinct localhost HTTP/WAMP ports, then run `white_orchard_sparse.py --project <project> --source <original authoring root> --mode native|minimal|sparse --port <port>`. Against each matching port, run `white_orchard_sparse_capture.py --project <project> --port <port> --label <fresh label>`. Run `white_orchard_sparse_measure.py --folder <capture folder>` and finally `white_orchard_sparse_review.py --native <native folder> --minimal <Minimal folder> --sparse <Sparse folder> --output <fresh ignored JSON>`. Supplement: capture with `--cases authored-rest` and a separate fresh label. Do not reuse a live project, rename a completed evidence directory or overwrite previous results. After capture cleanup, verify empty transport lists and stop only the task-owned servers. No SoundBank generation is part of this procedure.

Local projects:

| Control | Project under `build/sparse-white-orchard/` |
| --- | --- |
| Native | `native/validation/w3_audio.wproj` |
| Retained D semantics replay | `minimal/validation/w3_audio.wproj` |
| Sparse | `validation/w3_audio.wproj` |

The Minimal control is a fresh semantic replay of retained D, not a rewrite of its accepted source/bank. New local custom-State GUIDs need not equal D's GUIDs. D's pinned measured State template is verified before reuse. Original switch/event/transition/media structures restore exactly after reversing only declared edits. All542 original event WWUs are checked; no direct/descendant event or native transition target inherits a new playlist gain. All selected consumers and protected-State closure are checked.

## Exact sequence and gain mechanism

Authoritative native definitions: `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Interactive Music Hierarchy\music.wwu`, selected `MusicPlaylistContainer`133462974, GUID `{4A23933D-BE41-4C79-BED2-337D24C605EA}`, physical parent866607386 (`general`). Native decoded records are in `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc\music_prologue.bnk`.

The selected generic day playlist keeps its original−2dB Volume. Its existing continuous-sequence root `{253E9486-0F36-409E-8BE8-9496DE42FD8D}` loops indefinitely. The first existing item still selects native segment319905093 once; the second selects existing native silence segment4111369 for exactly three10-second loops. Only the prior nested randomized playlist-item group is removed; its audio segments/tracks remain. No composition, segment timing, stream, exit marker or outer transition rule changes. This repeats the same eligible native composition on successive instances; it does not introduce a second composition.

Native segment319905093 exits at140,000ms with an8,000ms post-exit tail (decoded duration148,000ms). Silence segment4111369 uses native source16708307, previously verified zero PCM. Thus the30-second rest begins at the exit while the original tail completes; approximately22seconds are environmental-only. This interval is an engineering choice, not a proposed user default.

**Both D mutes are explicitly resolved:** Sparse is authored from pristine source, with no shared `world_music` StateInfo. Four other approved generic playlists retain static−200dB. The selected day playlist gets a local25-State Voice Volume table with exploration0dB, generic dialogue/focus/other previously muted noncombat States−200dB, and native-unity other States. Three other noncombat playlists receive local25-State copies of D's policy, retaining D treatment without newly classifying their musical intent:

| Local scope | ShortID | Extra gain policy |
| --- | ---: | --- |
| Selected day playlist |133462974| D policy except exploration is audible |
| Other world selection |251819879| D policy retained |
| Other world selection |531434506| D policy retained |
| Technical thematic selection |589261176| D policy retained by default |

These are100 local custom-State objects, existing native `game_state` references and no new global definitions. No compensating gain, bus, production effect, script hook or Init change is used. Combat, Gwent and transition playlists are outside these local scopes. Dedicated authored routing remains exact. **The proof does change gain placement beyond the selected branch** to avoid releasing other material when D's ancestor mute is absent. This is an experimental candidate, not a production D patch.

## Measured controls

Wwise2023.1.19.8928, nine cases per control plus one authored-rest supplement per control (30 matched captures total), and an initial20-second Gwent instrumentation smoke. Full matrices are retained under each project's `matrix-v1/`; `results.json` includes exact accepted times, profiler paths, effective RTPC values and raw voice identities. `sparse-measurements.json` contains50ms PCM envelopes; `authored-music.xml` is the pre-Recorder source snapshot. `final-source-gates.json`, `full-consumer-closure.json`, `acceptance-review-v2.json` and `final-preservation.json` retain independent checks. Sanitized numerical results and hashes: [evidence](55-white-orchard-sparse-evidence.json).

| Measurement | Native | Minimal replay | Sparse |
| --- | ---: | ---: | ---: |
| Selected initial phrase contribution |−19dB|−417dB|−19dB|
| Music100→50→100 |−19→−25.02→−19dB| Muted generic control |−19→−25.02→−19dB|
| Two intentional quiet windows, PCM clock | Native sequence | Generic suppressed |148.05–169.95s;318.05–339.95s|
| Threat0/35/100, combat layer1 |−17/−17/−17dB| Original curve |−17/−17/−17dB|
| Threat0/35/100, combat layer2 |−783.62/−19/−19dB| Original curve |−783.62/−19/−19dB|

The measured transport scope18446744073709551614 actually receives threat0/35/100; a separate default scope is not substituted for it. Native layer2 saturates by35 in this material:100 does not demonstrate an additional intensity layer. The normal voice gain includes the native Music bus contribution; these are not only source Volume values.

Intentional rest is established by actual voice ancestry through rest segment4111369 under the selected playlist, its native zero-PCM source, finite loop count and subsequent audible phrase—not an empty Recorder file. Recorder is not a continuous wall-clock guarantee: several muted/context-switch captures retain only later output (for example, the105-second Sparse mixed case has approximately20seconds of Recorder output). Recorder reopening/virtualization is a possible explanation, not independently proven here. Their WAV duration is **not** used to measure State acceptance, interruption latency or silence length. The uninterrupted cycle PCM and matching profiler selections support the two quiet intervals. Profiler sampling is approximately0.2seconds, with occasional query gaps; intervals are not sample-accurate voice termination measurements.

### Combat interruption and complete return

Actual native outro segment800050000, parent playlist626252931, is followed after accepted exploration. Native decoded segment duration is approximately5.10seconds; sampled voice spans are approximately4.7–4.9seconds. Capture continues well beyond each tail.

| Entry condition | Native combat response | Sparse response | Native/Sparse outro span | Native/Sparse middle gain |
| --- | ---: | ---: | ---: | ---: |
| During phrase |1.35s|1.52s|4.84/4.82s|−19/−19dB|
| Early rest |1.48s|1.08s|4.84/4.75s|−19/−19dB|
| Late rest |1.30s|0.87s|4.75/4.93s|−19/−19dB|

Differences are not treated as a speed improvement: native phase/beat synchronization and sampling explain these sub-second variations. Rest voices are active before both rest interruptions. No audible generic prelude appears between those combat acceptances and combat entry. All original transition rules and native combat ancestry remain exact.

**New observation about retained D semantics:** the replay's world State gain reduces the outro's middle contribution to−219dB after exploration returns; its initial peak is approximately−29 to−32dB before further attenuation. Sparse retains−19dB throughout the sampled middle. This does not contradict the user's satisfactory retail feedback; that feedback never established these exact outro tails. It does not authorize changing accepted D or the consolidated releases.

After combat, Sparse starts the selected phrase with the same native fade/overlap grammar as pristine. The native outro remains audible alongside this native return overlap; the scheduler does not wait for an extra independently invented boundary. A future experience policy may want an additional post-combat rest, but this experiment does not claim to implement one.

### Context changes and protected controls

- During phrase, day/night switches preserve native fades. The night and other-location generic playlists stay below−190dB additional-path contribution. Returning to the permitted day selection restarts an audible phrase using native transitions.
- During rest, night151s→day154s restarts the day phrase around155.77s wall time, before its nominal rest end. Location reselection behaves similarly. A rest does not persist across context re-entry.
- Ordinary dialogue attenuates the permitted generic path to approximately−219dB. Intermediate cutscene/movie/music-only changes preserve the declared native-unity policy: the permitted phrase can return during unity States. This is not proof of a universal contextual music-only exception.
- Explicit native authored event `mus_q001_tavern_conversation` is accepted and its actual authored voice933909186 is audible at native gain, including Music master control. The mixed case retains native authored-entry timing rather than forcing immediate replacement.
- The separate authored-rest supplement confirms rest segment4111369 active before the event at151.20s, followed by actual authored voice933909186 at156.12s and steady−22dB, matching native at156.12s/−22dB. The approximately4.9s acceptance-to-voice interval is native cue timing, not a scheduler-enforced wait until the nominal170s rest end. All three supplemental captures finish with no cleanup errors. `white_orchard_sparse_review.py --authored-rest` reproduces this separate comparison using the supplement folders.
- The protected-world control uses the separately declared report35 technical gain-isolation override for playlist589261176. Its local gain is temporarily unity only for that capture, then restored. Native-level playback proves technical isolation, **not** that normal candidate policy exempts it or that its musical intent has been resolved.
- Gwent remains audible at native gain. No new diegetic, voice, ambience or sound-effect routing is authored; those categories were not individually auditioned by this fixture.

## Verification, cleanup and next step

All174 repository tests pass, including prior regional bank regressions and new synthetic negative cases. Expected `passed:false` messages from existing negative tests are not suite failures. Complete musical source restoration, exact local State fields, no extra playlist fields/IDs, preserved original input hashes and all unrelated WWUs pass. This is **not** a generated candidate HIRC/media gate: no experimental bank was generated, and no claim of retail Sparse compatibility is made.

Original music source SHA256 remains `f8184d13ea08f6bc161719884e9341bdfd3a3e7666b203c296ffae37d4e08251`. Sparse source snapshot SHA256 `848ff8dc4cee8a6f868dd276a22ac70757a6df58e4eab22622bd985af664264a`; fresh D semantics replay `e1c658d22d6901d169afc243f2c615a6f0d83df7867ee54fef0ce52d30cbf3da`. Retained accepted D source/bank, native Init and v2/v3/v4 archives retain their prior hashes.

Recorder/channel/anchor instrumentation is validation-only, removed/restored in `finally`. Transport/capture/RTPC cleanup continues after errors; negative cleanup tests cover that path. Completed matrices and supplements have no cleanup errors. Empty transport lists were verified before stopping the three exact task-owned Console processes in both capture sessions; no unrelated program is terminated. An initial supplemental API connection attempt before server readiness failed without starting playback and is not passing evidence.

**Recommendation:** proceed with a bounded reusable Sparse prototype, preserving this local native-sequence approach. The smallest next step is explicit re-entry/post-combat rest semantics: choose whether native reselection may restart a phrase or a rest must survive it, then implement/test only that behavior. This proof does not yet deliver contextual punctuation or adaptive composition choice. Before any future release, add explicit generated-bank structural/dependency gates for the playlist edits and local States, then seek separate retail authorization. Do not copy the old static-only bank allowlist onto these structural edits.
