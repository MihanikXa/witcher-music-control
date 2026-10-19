# 94 — Compiled observer; protected-request proof remains blocked

2026-10-19. Report93's bounded execution results. **The observer compiles. A safe external music-request gate was not established. Nothing was installed or retail-tested.**

## Results and evidence levels

| Item | Result | What this establishes |
|---|---|---|
| Original diagnostic annotations | Implemented | Log-only, three localized wrappers; no music decisions/calls |
| Native offline compilation | Exit0, candidate and matched control | Source signatures, annotation processing and bytecode generation in pristine REDkit context |
| Existing merged-mod compatibility | Not compiled as one assembly | Wrappers coexist syntactically; actual installed load/merge combination still needs user testing |
| Retail signal delivery / log destination | **Unverified** | No user gameplay trace exists; native `LogChannel` import is not a proved retail file sink |
| Selected-playlist Seek request | Authoring rejects Target reference | This primitive cannot address the proposed narrow playlist boundary |
| Parent-switch Seek variation | Seven actual authoring captures; no positive request-driven cue start | **Not a request gate**, even though native playback continued |
| Source/audio preservation | Passed | 1,508 original WWUs,542 event WWUs,47 original audio inputs and approved imported PCM exact against retained context |
| Repository tests | **281 passed** | Parser, unknown handling, lifecycle, filtering and existing regressions; not gameplay evidence |

[Sanitized evidence](94-context-observer-request-evidence.json) records exact hashes, native diagnostics and per-case profiler/PCM summaries. Full logs,50ms PCM envelopes, ancestry/RTPC records and failed attempts remain ignored under `build/sparse-live-context-pilot-v1/`. No original game/REDkit/Wwise resource, accepted cue or shipped bank was edited. All24 accepted WAVs, ten retained release/native inputs, report88 bank and report90 source pins remain exact.

## A. Small observer implementation

Original source: `src/diagnostics/wmcContextObserver.ws`. It adds unsaved diagnostic fields/methods, wrapping only:

- `CR4Player.OnSpawned`: calls original, initializes a1Hz diagnostic timer.
- `CR4Game.OnAfterLoadingScreenGameStart`: calls original, starts a new lifecycle epoch.
- `W3FastTravelEntity.OnAreaEnter`: calls original exactly once; emits discovery only on a player-entered `FirstDiscoveryTrigger`, non-hub-exit object, valid tag, previously undiscovered marker, and confirmed discovered status after the original handler.

No broad map-pin interceptor, `SoundGameStateChange` replacement, quest override, position scanner, save field, audio setter or probability model is installed. Source hooks are annotations, not replacement copies of third-party/native classes. Existing installed annotation mods and merged `r4Game.ws`/`r4Player.ws` were inspected read-only. Other wrappers on these methods can affect ordering and must remain part of the eventual user compile/load check; native-context compilation does not validate all enabled mods together.

### Source bindings and limitations

Exact installed base **G** is `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts`; corresponding inspected REDkit definitions are under `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\scripts`. Report92's catalog pins the matching source pairs.

| Recorded field | Verified binding | Limit |
|---|---|---|
| Region | G `game/commonMapManager.ws:148`, `GetCurrentArea()` | Coarse region, not current Wwise location selector |
| Logical music State | G `engine/sound.ws:235`, `GetCurrentGameState()`; enum6–29 | Public query, not audible ownership or outro completion |
| Combat/threat | G `game/player/r4Player.ws:5851,6597`, `ShouldEnableCombatMusic`/`IsThreatened` | Source-defined classification; no audio-completion inference |
| Day/night | G `game/environmentManager.ws:127`, `IsNight()` through `theGame.envMgr` | Game-time classification, not elapsed clock |
| Horse/boat | G `game/actor.ws:6431,6455`, `IsUsingHorse(true)`/`IsUsingBoat` | Horse excludes mounting-in-progress; boat occupancy is not proof of sailing |
| Scene | G `game/r4Game.ws:1329`, `IsDialogOrCutscenePlaying()` | Conservative aggregate; logical music State separately distinguishes movie/cutscene |
| Pause/loading video | G `engine/game.ws:22,31`, native pause/video queries | **Loading video=false is not loading=false**;1Hz timer may stop during pause/load and miss short transitions |
| Interior | G `game/player/r4Player.ws:433`, `IsInInterior()` | Coarse interior observation, not a biome |
| Clock/lifecycle | G `engine/game.ws:58`, engine seconds; G `game/r4Game.ws:834`, post-load callback | Monotonic within a valid epoch only; actual engine-clock pause/reset semantics remain to observe |
| Discovery | G `game/gameplay/fast_travel_entities/fastTravelEntity.ws:75–109`; G `game/commonMapManager.ws:163–184` | Narrow first player-trigger path only, not every discovery/landmark or remote quest update |
| Logging | G `core/misc.ws:9`, imported `LogChannel(channel:name,text:string)` | Compiler resolves it; physical retail destination/channel filtering remains unproved |

Weather is omitted from this first diagnostic rather than adding another untested callback. Exact music location, reviewed selector, authored owner and outro completion are explicitly unknown. Region/interior provide limited location context, not fabricated access to native music-location Switches.

At most600 records per lifecycle,32 discovery identities and15minutes of timer sampling. Changed snapshots plus a30s heartbeat are logged; no high-frequency movement scan. Local discovery tags are retained only in bounded unsaved memory; output uses per-epoch ordinal IDs, not quest names, coordinates or native location strings. A spawn followed by post-load initialization can produce two epochs; this is an explicit reset, not proof of two world loads. No diagnostic object availability means an unavailable snapshot, not stale positive eligibility.

`WMCCTX1|epoch=...|seq=...|t=...|snapshot|...` is versioned and bounded. `tools/sparse_observer_trace.py` rejects reversed/malformed records, unfiltered discoveries, duplicate identities, invented ownership and unknown enum encodings. It preserves observed provenance separately from policy inference. Epoch gaps are unknown and compacted only for offline ordering; they cannot calibrate real elapsed silence. Replay through the existing policy leaves native owner/selector/outro/loading unknown and therefore produces **no fabricated eligibility**. Synthetic parser fixtures are not retail logs.

### Compiler evidence, including failures

Compiler: installed native `bin/x64_RedKit/wcc_lite.exe`, log version5.0.1048625 / P4CL13413172, built2026-10-07. Installed retail executable reports5.0.0.1048522. These are actual local metadata, not a claim of identical binaries; the relevant installed/REDkit script definitions match, and the compiler accepts the annotations/API calls. No retail executable was launched.

`tools/sparse_observer_build.py` creates a private complete script context, native runtime/config/bootstrap copies and a private product title. Compiler assets never replace installed files. The native tool creates an empty task-title `gamesaves` directory outside the repository; no real game save/profile or Vortex setting is targeted. The private title is not the live game's profile. Original runtime DLL hardlinks used in this run were hash-matched to installed REDkit files and never edited; the reproducible preparation helper copies native assets.

Preserved attempts:

1. Initial relative data-root error: native bootstrap assertion, task-owned process stopped; no script result.
2. Incomplete bootstrap: access-violation exit3221225477, missing resource definitions and commit-memory1455 messages. Not a script compile result; all retained.
3. Absolute data path trial: this compiler prefixes its root even to that config value; rejected bootstrap, stopped. The final helper uses the observed relative base-directory convention.
4. Empty patch baseline: exit1, **No script files found in patch source directory**. A single original empty control class provides a valid patch baseline.
5. Final baseline, real observer and matched-declaration/API control: all exit0, successful `blob.rsblob` outputs, zero `[Error][Script]`/`[Error][WCC]` diagnostics.

Native diagnostics are **not clean**: baseline20,893 assertion entries; candidate20,901. The only diagnostic delta is8 occurrences of `scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())`. An initial eight-empty-function control did **not** reproduce the delta; no simplistic per-function explanation is accepted. The final control retains the exact annotations, fields, wrapped calls and native queries, changing only the logged payload to a constant. Its complete diagnostic counter matches the observer exactly. All other warning/error counters match baseline. This supports code generation and separates trace formatting from native metadata assertions; it does not prove assertions harmless in retail. We neither removed source nor hid diagnostics to obtain exit0.

Reproduction (fresh root; no parallel native-tool startup):

```powershell
python tools/sparse_observer_build.py --root build/sparse-live-context-replay/observer --prepare --label baseline
python tools/sparse_observer_build.py --root build/sparse-live-context-replay/observer --label candidate --candidate
python tools/sparse_observer_build.py --root build/sparse-live-context-replay/observer --label matched-control --assertion-control
```

The stored review helper uses this run's named evidence directories. Compiler artifacts stay ignored; the manual source-only diagnostic is separate from the compiler's complete native script context/blob.

## Manual observer test and rollback

Prepared locally: `build/sparse-live-context-pilot-v1/observer/manual/WMC Context Observer - Diagnostic Source.zip`. It contains only original diagnostic source at:

```text
Mods/modWMCContextObserver/content/scripts/local/wmcContextObserver.ws
```

ZIP SHA256: `8cb59a83e77c328b2cd050c252411feefa21b8a257b0abd15d9a85f45ab16568`.

The `Mods/mod.../content` root matches the previously verified Vortex archives. No generated scripts blob, native scripts, DLL, music, bank, cache, project or licence ships in this diagnostic. Exact ZIP readback/hash is in the evidence JSON.

**Capture prerequisite remains unresolved.** Local evidence verifies a native script logging API and native compiler logs, not a retail script-log file. The installed retail binary contains the `LogChannel` binding and imports OutputDebugStringA/W; that is static evidence only, not proof the binding forwards these records there. Do not invent a `wcc.log` destination, enable flags, install a logger/DLL or assume normal gameplay writes these records. This package is **compiled source ready for a controlled manual sink probe, not a verified capture-ready diagnostic**. If no already working native `LogChannel` capture route is available, stop before installation and resolve that narrow prerequisite first.

Once a capture route is established, user-operated steps are:

1. Close the game. Record enabled mods/merge state before adding this optional diagnostic. Preserve the current consolidated audio mod and its priority.
2. Import the ZIP into Vortex and inspect the destination above. Enable only this additional source mod; no audio replacement or profile/save switch. Review Vortex/Script Merger messages. Do not overwrite a merged core script with an entire vanilla file. Annotation processing and the user's complete load order require the first retail compilation check; if it errors, disable the diagnostic and retain the error text privately.
3. In a fresh user-launched game process, load the user's normal existing save. A short ordinary walk, a mount/dismount if already available and an ordinary menu/scene are sufficient initial observations. Natural combat or an accessible genuinely undiscovered marker are optional, never prerequisites. No forced travel, quest advancement, custom save or discovery manipulation. The diagnostic writes no saved variables; normal game autosaving is the game's existing behavior.
4. First verify that a `WMCCTX1` begin/snapshot arrives at the established sink. If none arrives, stop; do not interpret lack of logs as lack of gameplay events or play for15minutes blindly. Return the sink/probe result before larger capture.
5. Capture only a few minutes, extracting WMCCTX1 lines into an ignored local file. Review them before sharing; originals remain private. Normalize with:

   ```powershell
   python tools/sparse_observer_trace.py build/sparse-live-context-pilot-v1/observer/logs/raw.txt --output build/sparse-live-context-pilot-v1/observer/logs/normalized.json
   ```

6. Quit normally. Disable/remove only `modWMCContextObserver` through Vortex, redeploy the prior configuration and review only affected merge outputs. If a merger changed files, restore/rebuild from the recorded pre-test state using the user's normal workflow. No save rollback or WMC audio reinstallation is required by this source-only diagnostic. Never delete the existing merged-mod folder wholesale.

Codex performed none of these retail/Vortex actions. No discovered-event delivery, logger sink or runtime compatibility is marked passed.

## B. Protected Wwise request experiment

Fresh ignored complete-context clone: `build/sparse-live-context-pilot-v1/wwise-request/candidate/validation/w3_audio.wproj`. Exact retained report90B rest-first music source SHA256 `a5c759d7d4ccd2d182ce28398f634d9dc8095a6aba804b1e46f6c96decc7530a`; all1,508 WWUs retained. The accepted S04-a engine PCM SHA256 remains `5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc`. Original markers, source track, baked tail, native transitions/events, combat/outro, globals and Music master are unchanged.

**Candidate1:** an Event with only Seek action36, targeting the reviewed selected playlist `{4A23933D-BE41-4C79-BED2-337D24C605EA}` / ShortID133462974. Wwise2023.1.19.8928 itself rejected the Target reference (`ak.wwise.invalid_reference`). There was no playback success to measure.

**Candidate2, justified by that rejection:** same Seek action at existing parent MusicSwitch `{00F2D643-114B-46E4-B5EB-4B78ED19D3A6}`, percent99.9, marker snapping false. No direct Play, new globals, effects or imported media. Event/Action objects existed only in task-owned authoring memory; all work units are byte-exact to their retained inputs afterward. The intention was to test whether an already selected rest could yield to the cue without starting an inactive branch. **It did not establish that behavior.**

Installed definitions: `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\WObjects\WObjects.xml`, ActionType Seek36, SeekType/SeekPercent/Target; `Html/en/SeekPercent.html` explains seeking relative to MusicSegment Entry/Exit, not a command to advance playlist sequence items. The proposed use is not equivalent to a playlist advance/commit API. Returning successfully from `postEvent` is only API acceptance, not cue acceptance.

| Measured case | Actual result |
|---|---|
| Rest control18s | Native silence segment pipelines; Recorder all-zero over16.213s actually written |
| Request at6s | Same rest selection, no cue pipeline; all-zero16.096s; no request-driven start demonstrated |
| Requests at6/9s | Rest continues, no cue pipeline; all-zero21.152s actually written; duplicate identity/cancellation semantics unproved |
| Combat→exploration control | Exploration accepted24s; native outro voiced24.74–29.45s, peak−19dB; cue enters46.69s on original sequence |
| Same return with request24.3s | Outro24.82–29.52s at−19dB; cue46.58s on original sequence, not at request; no premature cue overlap observed |
| Authored interruption + request | Actual authored voice ancestry audible; no imported-cue pipeline; because positive acceptance failed, this is not proof of a functioning ownership veto |
| Wrong location + request | Other native selection remains attenuated (~−217dB), no imported cue; Recorder wrote only0.096s, **not a full-duration PCM silence proof** |

Times are profiler samples, approximately0.2s resolution, not sample-exact acceptance/completion timestamps. Effective threat RTPC on transport game object was0→35→100; Music100. Combat layers remain at native measured gains (−19/−17dB peaks); complete native outro remains audible in both new matched return cases. Recorder return captures are48.11/48.07s, peak5923PCM16, no clipping. Full ancestry, RTPC values and50ms envelopes remain private.

No new complete S04-a phrase/tail audition is claimed: return captures end while its later automatically scheduled phrase is still playing. Report87/90's complete phrase/PCM/master/native/Minimal controls are retained and source-identical, not relabeled as new request tests. The new wrong-location PCM truncation and WAMP port-bind diagnostic are retained. HTTP API project/version were checked; WAMP subscriptions were not used. Explicit project.close caused WwiseConsole exit1; the capture script completed0 and cleanup/source preservation passed. All task-owned servers/transports stopped.

### Why this is a blocker, and what was not tested

Neither candidate supplies **one cue per accepted request**. Without a positive commit primitive, a no-cue result in combat/authored contexts cannot validate protected gating. New request-specific dialogue/movie/Gwent/loading, TTL, stale context and cancellation proofs therefore remain **not passed**; we stopped after the meaningful primitive failure rather than growing an unsafe matrix. This does not prove Wwise can never implement a gate.

The preserved native graph also shows the deeper timing problem: generic rest can already be selected around24.8s while the original outro remains audible until29.5s. Thus even a future trigger attached to that active generic container must not assume "selected generic = outro finished." Native music_type protects dedicated authored routing but is not a blanket classification of every world selection. Direct Play of the child, a sticky request Switch, a fixed estimated outro timer or muting Music would not satisfy the requirement.

A local stinger/Trigger was inspected in installed WObjects definitions (`MusicStinger`, `NumSegmentAdvance`, `DontPlayAgainTime`, Trigger/Segment references), **not implemented as an untested third candidate**. Its cooldown is not per-request identity/expiry, and its ability to remain queued into a later segment and overlap native return material would need independent proof. No new global Trigger/State/RTPC or Init dependency has been approved/generated here.

## Handoff

The two missing contracts remain concrete:

1. **Telemetry capture:** actual retail delivery/sink of the compiled source-defined records. First manual test should be a short logger/compilation probe, not soundtrack playback or forced progression.
2. **Audio commit:** a source-scoped native primitive that accepts an expiring request only when the reviewed generic leg may start, positively acknowledges that start, survives duplicate/cancellation checks and defers/rejects through the complete native outro. The tested Seek mechanism does not provide it. A future narrowly scoped trigger/transition proof needs its own ownership/outro and lifetime design; it must not be wired to the probability model yet.

The next practical step is to establish the observer's retail log capture route while reviewing the failed request evidence. Do not connect the report92 model to audio, expand cues, generate banks or install anything automatically. The current implementation remains a compiled diagnostic plus a measured **negative** request experiment, not an end-to-end contextual soundtrack controller. Stop for review.
