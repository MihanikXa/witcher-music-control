# 90 — Single-cue Sparse rest and re-entry: Wwise-only results

2026-10-18. Report89's bounded experiment is complete: **two source-scoped candidates, 193 final review checks and 242 repository tests pass**. Redundant selections already continue; local day/night history can resume rest; nested location returns do not reliably retain it. A conservative rest-first sequence prevents generic music from overlapping the complete native combat outro in the tested cases.

This is **reversible source and measured Wwise authoring proof**, not a new bank, release, approved pacing default or retail test. No controller, SoundBank generation, cooker, installation, game/Vortex/save change or licence operation occurred. All24 approved cues, accepted releases, native Init and the report88 bank remain exact. No WwiseConsole process remains.

## Inputs and source scope

Private root: `C:\Dev\witcher-music-control\build\sparse-reentry-pilot-v1\`. Three baseline workers and two candidates each retain1,508 work units,47 immutable original audio inputs and the exact additional S04-a source. Audio links to the existing build pool are verified NTFS hard links, never edited in place. WWUs are independent copies. No licence data was copied/read.

| Input | SHA-256 |
|---|---|
| Accepted `build/music-material-selection/five-cue-corrections-v1/audio/S04-a-B.wav` | `2fb3282aea3474fada19b823ffb6dc6b9b794efa1f75aa347df00adf3d3cff82` |
| Derived `build/sparse-approved-cue-pilot-v1/media/WMC_S04a_approved.wav` | `5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc` |
| Prior `generation/Interactive Music Hierarchy/music.wwu` | `a0beae9fbf32d55054c2cb8ea10a2cc8f0034b699d9c921fef1e1351075b53ff` |
| Candidate A music WWU | `752b340a9f74f6f3588d0b771ac9169ca97d23fdda9351215ffb4382c486ad66` |
| Candidate B music WWU | `a5c759d7d4ccd2d182ce28398f634d9dc8095a6aba804b1e46f6c96decc7530a` |
| Preserved report88 `generated-banks-licensed/music_prologue.bnk` | `4759b863ac1e2700627811922d3f07b17397635b03a97af212e8657d33fb27bc` |
| Installed native `bin/initialdata/sound/Init.bnk` | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |

The approved source stays stereo48kHz/40.85s: Entry0, ExitMarker30.85s, baked-tail allocation through40.85s, native60BPM/4/4. Segment`1029261546`, track`499024852`, media`383927916` remain report87 identities. No DSP/sample/marker change.

Complete source reconstruction (`tools/sparse_reentry_source.py`, `verify`) checks all five contexts,542 event work units,24 approved WAVs, ten retained release/native inputs, original audio hashes/link identity and the report88 bank/native Init. It reruns the existing Sparse and approved-import restoration gates. Reversing only declared re-entry edits restores the exact approved-cue semantics. Other regional work units, events, combat/outro, global definitions, master, RTPCs and original media remain unchanged. This proves source scope, not new serialized-bank compatibility.

## Native mechanism and baseline observations

Read-only installed project: `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\`.

- `Events/music.wwu`, `mus_loc_prologue_village` and alternate-location control: `ActionType=23`, Set Switch, not Play/restart. Installed `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\WObjects\WObjects.xml`, ActionType enum, verifies that mapping.
- That schema, lines1449 and2532–2590, defines MusicSwitchContainer `ContinuePlay`, Last Played Segment and Last Exit Position. Loaded WAAPI reads confirm unchanged `ContinuePlay=true` on regional root`287204113`, world`1033516231` and general`866607386`.
- `Interactive Music Hierarchy/music.wwu`, general combat-return transition`{A79AC940-BEEA-48E2-81EA-BD307F4771D4}`: native Next Beat source synchronization and transition segment`800050000`. Both candidates retain its source sync, transition audio and original fades/curves. A pipeline's lifetime is not necessarily its audible interval or a restart from source time zero.

| Approved-cue Sparse baseline | Observed behavior |
|---|---|
| Same location event at6/44/57s | Same cue/rest cadence; next cue~62.92s. Independent valid PCM confirmation. |
| Same exploration State at6/44/57s | Same cue pipeline/cadence (~60.85s); no reset. |
| Actual location/day-night return during music,6→12s | New pipeline can re-enter partway through the composition while retaining its old exit/rest boundary. Not necessarily a full-track restart. |
| Early-rest location return~48s | New cue~49.78s, before uninterrupted~63s deadline: rest cancelled. |
| Early-rest day/night return~48s | New cue~49.31s: rest cancelled. |
| Late-rest returns~60s | New cues~62.53/~62.26s. Nearness to old deadline is not proof of persistence. |
| Combat from music/early/late rest | Complete native outro~4.72–4.96s at −19dB, but generic cue returns~0.82–1.28s after exploration, overlapping it. |

**Inference:** redundant effective selections are not the demonstrated reset mechanism. Genuine hierarchical selections can lose/reinitialize local history. Native Same Time entry also explains why a new pipeline need not mean a new musical beginning. Actual retail event cadence was not measured.

## Two bounded candidates

Implementation/allowlist: `tools/sparse_reentry_author.py`, `build()`/`validate()`. Selected playlist is`{4A23933D-BE41-4C79-BED2-337D24C605EA}`/`133462974`.

### A — local history and targeted combat-rest entry

Two new local rules request `DestinationPlaylistJumpTo=2` (Last Played Segment), `DestinationJumpPositionPreset=4` (Last Exit Position): one inside general targeting the selected playlist, one cloned from applicable native regional return rule`{23D85023-3E0B-42E8-AC78-6B23436B4635}`. Native explicit combat-return priority remains.

On that existing combat-return rule, only destination entry changes to Specific Playlist Item/Entry Cue, pointing at existing rest item`{42F12789-7847-4193-AF93-64D2FEB84C2C}`. No native fades, sync, outro or combat definition changes. Six collision-checked local rule/fade GUIDs, no new audio/event/State/RTPC/global object.

**Measured:** nested location early-rest return still starts cue~49.69s: cross-location persistence fails. Day/night late return resumes a rest fragment~62.06–67.88s, cue~68.09s. Early return resumes two rest pipelines~49.43–57.15/57.35–67.06s, cue~67.27s, about4.18s beyond uninterrupted deadline~63.09s. Both support local cursor/remaining-loop continuation consistent with the4s departure being paused, **not a wall-clock countdown across contexts**.

Targeted combat return passes one probe: native outro~30.61–35.48s at −19dB, generic cue~62.20s. Wider A regression coverage is not claimed.

### B — fresh rest when the selected sequence reinitializes

Only reorder the selected root's existing children `[Music, Rest]`→`[Rest, Music]`. Music item`{E628DC21-010A-49FB-BA2F-DDB4B588857B}` and rest item above retain all properties: three finite native10s silence loops, infinite outer sequence, unchanged approved phrase/tail. **No new GUID or transition rule.**

Initial entry and tested location/day-night/combat reinitializations get fresh rest, not the old deadline. If the same playlist remains selected, it can continue instead: dialogue mutes/unmutes the existing timeline rather than restarting it. Thirty seconds is a fixture, not an approved mode default. Native Same Time can shorten the first rest loop; actual measured delay matters. Repeated true departures can keep deferring music, an explicit policy tradeoff.

Early-rest location return~10.08s→cue~42.05s; late-rest day/night return~30.12s→cue~62.04s. Both enter a fresh bounded rest, not remaining elapsed rest.

## Playback and audio verification

[Sanitized evidence](90-sparse-rest-reentry-evidence.json) fingerprints34 complete behavior-capture rows (13 baseline,4 A,17 B), plus a separate22s State-settling control. One initial invalid baseline WAV is explicitly rejected and independently repeated. All17 B behavior files are valid. Raw profiler identities, actual RTPCs, timestamps and50ms Music-bus PCM envelopes remain ignored/private.

| B combat probe | Exploration API acceptance | Native outro sampled interval | Next generic cue | Gap after outro |
|---|---:|---:|---:|---:|
| During phrase |60.160s|61.379–66.394s|89.117s|22.724s|
| Early rest |30.047s|30.911–35.903s|58.599s|22.696s|
| Late rest |50.021s|51.260–55.777s|78.628s|22.851s|
| Rapid combat, final return |42.045s|42.788–47.622s|65.677s|18.055s|

Every outro middle is −19dB; rapid combat also retains the complete20.668–25.593s first outro, no generic overlap. Entry latencies~0.75–1.32s retain native synchronization. Rapid return delay23.632s versus~28.55–28.96s in other probes demonstrates **bounded quiet, not an exact30s timer**. Do not substitute one rest loop without retesting this guard.

- **Exact approved PCM:** first/second Recorder starts30.005333/90.855333s, cadence60.85s. Full second40.85s stereo phrase/tail matches the reference scaled by native gain within0.990 PCM16 units; other four channels zero. Initial30s and over15s conservatively tested after allocated tail are exact-zero Music-bus PCM. No DSP/re-render. This fixture does not audition actual environmental ambience.
- **Intensity:** actual transport object`18446744073709551614` reports0/35/100. Layer1 reaches −17dB at35/100; layer2 below −200 at0 and −19 at35/100. Original entry crossfade remains, including its ramp in the threat-zero measurement window.
- **Music master:**50/100 gives −25.0206/−19dB on the cue; protected-world technical control gives −23.0206/−17dB. No master changes.
- **Authored:** q001 control reaches native −22dB from phrase, rest and postcombat recovery; no later generic cue competes under that authored selection. q505 technical-isolation control remains native −17dB. Its existing temporary authoring overrides are restored; this is not a new production exception approval.
- **Gwent:** native −17dB, no definitions edited.
- **Dialogue:** installed `States/global_states.wwu`, lines161–166, explicitly sets exploration→dialogue to2s. Measured cue reaches −220dB by~2.15s after API acceptance. Its timeline continues silently and returns under the existing exploration gain policy; not a new start. Dialogue during rest also leaves finite rest running.
- **Intermediate States:** cutscene/movie/music-only retain existing Sparse behavior. An already-running cue can become audible again under movie/music-only; this is not universal silence in those States. The scene probe does not start an additional cue before the existing sequence boundary. Only tested authored routing is certified; not every cinematic path.

Native/Minimal report87 traces are reused, not regenerated or relabelled: `build/sparse-approved-cue-pilot-v1/{native,minimal}/validation/matrix-v1/approved-cue-measurements.json`. The historical Minimal replay attenuates its outro; this experiment retains the native-gain Sparse outro and leaves installed D/releases untouched. B timings shift to its initial-rest/phrase categories, not identical native wall clocks. Exact source restoration and actual profiler/PCM checks complement, rather than replace, one another.

## Failures, measurement corrections and uncertainty

All failed outputs are retained; no binary/header/audio repair or production-gate relaxation.

1. Two initial parallel baseline servers exited`3221225477` at transport creation, before playback. Cause unproven. All subsequent playback is sequential/task-owned.
2. First redundant-event WAV has unfinished RIFF/data lengths and incomplete frame. Rejected, not interpreted as silence; new `event-confirmation-v1` is valid. Recorder can retain only its last portion after routing changes, so valid-file duration may be shorter than capture wall time. Audio/profiler clocks stay separate.
3. A's initial preparations failed XML child order, then a transition reference to its owning switch. Corrected reference ordering and real-descendant contexts are now source-checked and live-read through WAAPI. These are failed preparations of A, not extra candidate designs. Failed WWU snapshots were moved byte-identically outside active project roots after the strict1,508-WWU gate caught them.
4. Old A discriminator lifecycle has a false `source_exact=false`: hash variable shadowed by transition settings. Its recorded source hash equals snapshot/current source and independent complete reconstruction. Raw flag remains, explanation/fingerprint is exported. Fixed later A capture reports source exact; no raw record rewritten.
5. Installed Recorder uses extensible PCM subtype,16-bit containers, `validBits=0`, mask1551. New format check initially assumed16 in that field. It now accepts only this observed6ch/48kHz zero-valid-bits layout or explicit supported PCM16, checks subtype/block/byte-rate/chunk bounds, rejects unknown layouts. Exact reference PCM comparison independently verifies interpretation; no header patched.
6. First aggregate `final-review-v1.json` falsely required an immediate getter to equal requested State and assumed1.2s dialogue attenuation. Installed `Authoring/Data/Schemas/WAAPI/ak.soundengine.getState.json` advises a short delay, but here old State remains at14–18ms; a separate unchanged-source probe sees requested State at the next66–72ms sample for all four changes. Not a universal latency bound. API acceptance is not sound-engine application. Corrected review preserves immediate observations, rejects unknown snapshots, requires settled control and derives2s dialogue fade from unchanged source. Historical12 baseline rows precede getter instrumentation; they have API acknowledgements/profiler only. Coverage is explicit, not manufactured retroactively.

Profiler polling~0.2–0.3s provides sampled bounds; PCM uses50ms windows. Voice gain/identity is not subjective musical judgment. Interrupted phrases follow unchanged native fades; only uninterrupted controls establish complete baked-tail waveform identity. No retail, new encoded-media decode or new bank proof is claimed. Report88's binary remains valid for its old source only.

## Wwise-only verdict and next step

**Works:** redundant selections continue without a script; local day/night history can retain remaining quiet cursor/loops; targeted native combat-return entry can choose rest; the conservative rest-first sequence provides bounded return silence through the complete native outro in all tested cases.

**Not established:** exact remaining-rest deadlines across nested locations, authored ownership changes, region stop/reload and save/load. A failed at nested location return. This limits the tested hierarchy, not every conceivable Wwise design. B deliberately starts fresh rest on reinitialization and adds initial-entry rest; it is not an exact persistent clock.

**Recommendation:** retain B as the smaller Wwise-only foundation if fresh-rest-on-reinitialization is acceptable. Decide that policy versus a genuinely exact remaining deadline before adding cues. If immediate first entry is required, A's narrower combat-only rule is proven, but a combined alternative needs a separate bounded test; none was silently built here. Keep fixture durations provisional. No controller is currently necessary for the demonstrated guard.

If exact cross-context timing is required, a future controller needs eligibility/deadline state, lifecycle/context-generation invalidation and a trustworthy cue/rest boundary clock or acknowledgement. Exploration/combat alone cannot reconstruct an unknown playlist cursor. Installed `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\scripts\engine\sound.ws`, `CScriptSoundSystem`, imports78–90 expose setters/events/bank status, no established playlist-position getter. `SoundGameStateChange`156–190 and `CollectSoundStates`557–624 provide the native music-combat classifier; `InitializeAreaMusic`279–325 can stop/restart region playback. Authoring WAAPI getters do not establish WitcherScript getters. Any future eligibility control must stay local to generic music, not delay native `game_state` or globally disable authored music events. **No script implementation.**

## Reproduction and retained evidence

Tools: `tools/sparse_reentry_{author,pilot,source,measure,review,pcm,evidence}.py`; tests `tools/test_sparse_reentry.py`. Existing capturer only adds an optional observer, preserving old callers.242 tests pass, including malformed/unknown PCM, exact waveform, source scope, invalid transition context, finite return, complete/muted/cropped outro, RTPC/master and stale-getter tests.

```powershell
python tools/sparse_reentry_author.py --name fresh-rest-proof --mode rest-first
python tools/sparse_reentry_pilot.py --project build/sparse-reentry-pilot-v1/fresh-rest-proof/validation/w3_audio.wproj --port 18414 --label proof-v1 --cases cycles-master combat-early combat-late authored-music authored-rest dialogue-music gwent
python tools/sparse_reentry_measure.py --folder build/sparse-reentry-pilot-v1/fresh-rest-proof/validation/proof-v1 --output build/sparse-reentry-pilot-v1/fresh-rest-proof/validation/proof-v1/measurements.json
python -m unittest discover -s tools -p 'test_*.py'
```

Use fresh ignored names, one server at a time. Recorded complete source audit pins these five workers; an extra reproduction needs its own explicit inclusion rather than weakening context membership. Source gates `source-gate-final-v3.json`, waveform `candidate-b-pcm-proof.json`, final aggregate `final-review-v2.json` and `tests-complete.log` remain private. Raw diagnosis/discriminator/regression/dialogue/history/settling folders retain original files and failed evidence. All successful task-owned servers stop/destroy transports and close their exact projects; process termination status is separate from playback gates. No packaging or deployment is authorized by this report.
