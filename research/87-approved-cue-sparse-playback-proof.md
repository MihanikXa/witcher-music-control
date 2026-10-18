# 87 - Accepted S04-a in the isolated Sparse engine

2026-10-18. Report86 authoring/media/playback pilot completed. **The approved cue plays, retains its baked tail, reaches finite silence, and returns. All67 final playback gates pass.** Selected offline bank generation is blocked by the fresh project's ineffective entitlement: exit1,26,219/200 media fatal, six Mastering Suite errors, no banks. No bank, cache or release compatibility is claimed.

## Scope and exact private inputs

Repository-relative paths below resolve under `C:\Dev\witcher-music-control`. All WAVs, projects, profiler traces and banks/cache outputs are ignored. Existing releases,24 approved files, original game/REDkit files, Vortex, saves and profiles are untouched. No Music Plus code/audio was imported. S04-a is native-derived selected material; its placement in this White Orchard fixture is **not a final regional musical assignment or redistribution approval**.

- Accepted input: `build/music-material-selection/five-cue-corrections-v1/audio/S04-a-B.wav`, report85 SHA256 `2fb3282aea3474fada19b823ffb6dc6b9b794efa1f75aa347df00adf3d3cff82`.
- Private derived source: `build/sparse-approved-cue-pilot-v1/media/WMC_S04a_approved.wav`, SHA256 `5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc`.
- `tools/sparse_approved_cue.py::prepare_audio/strip_wrapper` independently reads the approved stereo48kHz PCM16:2,200,800frames/45.85s. Exactly96,000 leading frames and144,000 trailing frames are proven zero and removed. The remaining1,960,800frames/40.85s are **byte-identical PCM**, with no gain, resampling, fade, DSP or reverb alteration. Every approved selection is SHA-verified before/after.
- Only the artificial2s/3s wrapper is removed. Approved near-silent reverb samples/padding inside the retained region remain. EntryMarker0ms; dry-stop/ExitMarker30,850ms; source end40,850ms; baked post-exit allocation10,000ms. Full audible decay and allocated duration are different: last nonzero source sample is35.650604s. First nonzero is0s;50ms RMS crosses−80/−70/−60dBFS at0.15/0.20/0.30s. These are signal thresholds, not sample-exact judgments about musical onset.

Private source proof: `build/sparse-approved-cue-pilot-v1/media/audio-proof.json`. Sanitized metadata/measurement companion: `research/87-approved-cue-sparse-evidence.json`.

## Reusable implementation and source gates

Original tooling:

- `tools/sparse_approved_cue.py`: approved-source verification, exact wrapper removal, supported WAAPI import, explicit marker/clock settings, collision audit and `validate_import/check_new_fields`.
- `tools/sparse_approved_capture.py::cases`: ten matched cases using the existing report55 Recorder, native-selector initialization, scoped RTPC reset, profiler sampling and exception-safe cleanup.
- `tools/sparse_approved_review.py`: independent actual source ancestry, sample-clock PCM comparison, native rest identity, combat/intensity/outro, authored, dialogue, master and cleanup gates. It joins independently recorded case groups only with complete case coverage and byte-identical authored source fingerprints.
- `tools/test_sparse_approved_cue.py`: synthetic positive/negative source and added-node validation.
- `src/wwise/experiments/white-orchard-approved-cue-v1.json`: source hashes, marker clocks, declared semantics and current observed IDs. WAAPI creates fresh IDs on reproduction; current IDs are evidence, not a requirement to reuse collisions.

Installed API authority: `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\Schemas\WAAPI\ak.wwise.core.audio.import.json`, `ak.wwise.core.object.setProperty`, `ak.wwise.core.object.setReference`, `ak.wwise.console.project.open/close`. Matching Console/Wwise build8928/schema119 is used. Existing report55 authoring code remains unchanged; no production static-only bank gate is weakened.

All controls/workers retain1,508 original WWUs and47 immutable original audio inputs. Preparation uses `white_orchard_prepare.py --preserve-hierarchies --immutable-originals build/licensed-white-orchard/baseline`. New work units are not added. Original audio hardlinks are immutable; the new WAV is a separate file. Final full-context source audits cover native, Minimal, Sparse, two identical Sparse workers and clean generation context. Native has no changed WWU; each other context changes **only** `Interactive Music Hierarchy/music.wwu`. All1,509 installed authoring inputs plus47 installed original WAVs are rehashed unchanged. Native game Init equals the pinned REDkit Init, SHA256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`; ten retained release/native inputs also remain exact.

The original Sparse pre-import source passes report55's exact restoration and canonical25-State rules, including542 event-work-unit consumer closure. The new gate permits exactly one new segment/track/source/clip subtree and the selected phrase item's changed Segment reference. It checks new layout tags/properties, source WAV hash/language, exact source duration/markers, zero added gain/RTPC/effect processing, existing conversion and bus references, physical parent, complete clip/source linkage, and restores all old music semantics exactly. Unknown fields/tags or unrelated source edits fail. Collision audit covers all1,508 original WWUs and739 native banks: new GUIDs, segment/track ShortIDs and media ID do not collide. Original selectors, event actions, native segments, combat transition references, fades, RTPC curves and global definitions remain unchanged.

## Actual graph and clock correction

```
play_music_prologue -> existing music_type/world_music -> existing location/game_state
    -> generic village/day playlist133462974 (native Volume -2dB)
        -> approved S04-a segment1029261546 -> track499024852 -> media383927916
           Entry0; Exit30.85s; baked source/tail end40.85s
        -> native silence segment4111369 / source16708307, three10s loops
        -> same eligible approved cue again

existing authored event -> unchanged authored sibling
existing combat/Gwent/native transition objects -> unchanged native paths
existing menu_volume_music -> unchanged Music master -> all normal music playback
```

The report55 gain isolation resolves **both** D suppression layers: no broad world ancestor StateInfo; selected static-200dB removed, restoring native-2dB playlist gain. Selected local25-State policy permits exploration and suppresses ordinary dialogue/focus as before. Four other approved generic static mutes remain; three other local playlist State scopes retain report55's D policy. Existing global game_state and its transitions are reused. No boost, new global mixer, bus, effect, RTPC, WitcherScript or Init replacement is used. Dedicated authored/combat/outro/Gwent paths do not inherit these local generic gains.

**Important measured correction:** default import created a120BPM segment without a clock override. Native selected phrase explicitly uses60BPM/4-4 with OverrideClockSettings. Initial default-clock captures are preserved as exploratory, not final timing evidence. The final tool explicitly sets the new segment to native60BPM with override and4-4 inherited meter. Exit timing remains30.85s. All final Sparse cases were repeated after this correction. No native clock, beat/transition rule or composition was changed.

## Measured engine playback

Thirty final matched captures:10 native,10 Minimal replay,10 clock-pinned Sparse; plus10 earlier default-clock Sparse captures retained separately. To bound elapsed time, the final Sparse matrix is split across three complete workers with identical authored music XML. Cases never run against different selector source semantics. Existing controls and all earlier evidence remain intact.

Private folders: `native/validation/matrix-v1`, `minimal/validation/matrix-v1`, and `sparse`, `sparse-b`, `sparse-c` each under `validation/matrix-native-clock`, all beneath `build/sparse-approved-cue-pilot-v1`. `results.json` retains accepted actions, actual voice GUIDs/contribution ancestry and effective RTPC scopes; `approved-cue-measurements.json` retains50ms PCM envelopes and summary intervals. `playback-review.json` has67 passing gates.

### Cue, approved tail, silence and recurrence

Native generic contribution peaks at−19dB, Minimal at−417dB, new Sparse cue at−19dB. Sparse Music100/50/100 changes−19/−25.02/−19dB. This proves the imported source is not hidden under D's mutes.

In uninterrupted final Sparse PCM, cue1 starts at sample256 (5.333ms); cue2 starts at2,921,056 (60.855333s), a60.85s cycle. Source end/dry stop and30s rest overlap exactly as intended: the silent segment begins at the30.85s Exit while the approved post-exit tail is still allowed to run through40.85s. Nominal allocated music-free rest is20s, not30s after the full tail. Actual exact-zero50ms PCM windows are33.40–60.90s and94.25–121.75s; the quiet source/normal bus gain reaches PCM16 zero before its allocated40.85s end. First/last threshold windows are not sample-exact silence boundaries.

**Strong waveform proof:** the second complete40.85s stereo phrase/tail matches the approved wrapper-stripped PCM at the measured native gain, with maximum output difference **0.990 PCM16 sample units**, RMS0.489. All extra Recorder channels are zero. The baked tail is included in this full-length comparison, not merely its filename or segment metadata. The first phrase's20–25s and30.85–40.85s comparisons also pass. No second room processing is introduced.

Recorder uses six-channel validation routing, but only the original L/R carry this cue. This validation-only channel layout is removed/restored afterward. Sound source entry, Recorder sample clock and profiler/action wall time are distinguished: native/Minimal/Sparse first profiler voice samples occur around2.15/2.22/2.11s, while the cue's Recorder source alignment is5.333ms. Similar native startup timing and the sample-exact stripped source show this is not an imported2s wrapper. Recorder file duration/offset is **not** used as action-interruption latency.

The early PCM test window4–7s initially crossed the intentional master50 transition (around source6s on Recorder clock); it is retained as failed comparison registration, not a source defect. The final identity proof independently aligns the entire steady-master second phrase with the same native-gain/PCM tolerance. No tolerance was loosened. Actual nonzero audio/voice ancestry, known rest identity, finite loops and subsequent matching phrase establish the rest; an empty Recorder alone is never treated as proof.

### Combat and complete outros

| Entry condition | Native response | Sparse response | Native/Sparse sampled outro span | Sparse middle gain |
|---|---:|---:|---:|---:|
| During cue |1.130s|1.363s|4.996/4.802s|−19dB|
| Early rest |1.299s|0.740s|4.888/4.906s|−19dB|
| Late rest |1.297s|0.675s|4.896/4.784s|−19dB|

Latency is accepted-State-to-actual-combat-voice profiler time. Sampling/beat phase varies; differences are not evidence of a speed improvement. Both rest cases show native rest voice active before combat. Native outro segment800050000/playlist626252931 remains audible after exploration returns and completes before capture ends; original decoded~5.1s source duration/tails are unchanged. Sampled spans are not sample-exact durations. Minimal replay still demonstrates its historical inherited-outro attenuation (−219dB); final Sparse does not inherit that defect. Retained production D is untouched.

Effective threat values on the actual transport game object are0/35/100 in every control. Layer1 is−17/−17/−17dB; layer2 is approximately−783.62/−19/−19dB in native, Minimal and Sparse. Layer2 saturating by35 is native behavior, not a new added layer at100. Original combat intro/body/RTPC/transition source and media remain exact. Native return starts the eligible cue with the existing outro overlap; **it does not resume the interrupted rest or implement a postcombat quiet lockout**.

### Other contexts and limits

- Explicit authored cue interrupts phrase and rest at native timing/−22dB; it does not wait for the nominal rest to finish. Rest control event accepted around44.1s and authored voices begin around49.11s (native timing comparable). Dedicated authored definitions/events are unchanged.
- The existing technical protected-world control and Gwent are audible at native peak gain; Music master remains authoritative. Technical world override is temporary and restored. It is **not** a new production exemption/classification for that selection.
- Ordinary dialogue suppresses the imported generic cue after the existing State fade. Cutscene/movie/music-only sequences retain native bus/selector behavior; no blanket scene exemption is introduced.
- Location and day/night reselection remain native: night/camp generic selections are suppressed and returning to the selected day leg can restart the cue, cancelling a rest. Final rest-reselection capture shows cue restarting around49.3s after day selection rather than waiting for the original~62.9s wall-clock boundary. **Persistent rests/adaptive re-entry remain unimplemented.**
- No environmental ambience was synthesized by the music-only fixture. “Environmental rest” here means verified zero Music output with the native rest transport active, leaving actual game environmental audio routing unchanged by source construction. Retail playback, mod loading and subjective musical appropriateness have not been tested by this task.

## Clean bank-generation attempt and precise blocker

Clean project: `C:\Dev\witcher-music-control\build\sparse-approved-cue-pilot-v1\generation\w3_audio.wproj`. It is separately prepared from original source with complete hierarchy, then receives only the source-gated final music XML and exact derived WAV. No Recorder/anchor/effects or validation project licence files are copied.

Selected command uses existing `tools/white_orchard_wwise.py::generate`, matching Wwise2023.1.19.8928, only `music_prologue`, Windows/SFX, fresh `generated-banks/`, isolated cache, no hooks/source-control/Wwise.dat/decode. Actual command and full diagnostics are retained privately. **Exit1; no .bnk files.** Diagnostics: one trial fatal26,219/200, six Mastering Suite licence errors, ten warnings. Nine warnings are existing inconsistent media-use rows and one is the Wwise.dat consistency-file warning; all ten match exact retained licensed baseline warning rows (hashes in evidence). No leaf exclusions, licence copying, binary patches, pruning or global regeneration workaround was attempted.

The WAAPI converted-file property supplied a potential WEM path, but no physical converted WEM was present there. Do not treat that property as encoded-media proof. New DIDX/DATA/stream content, generated HIRC/additions, BKHD identity and generated Init/plugin/STMG comparisons remain **unverified because generation emitted no bank**. Current native Init remains exact and is not a replacement target. Existing D runtime compatibility does not certify this new-media bank.

**Minimum prerequisite:** user manually applies the existing approved REDkit entitlement to the clean generation project through Wwise Project → License Manager, then closes it. Assistant did not inspect, request, copy or log a key. Re-run selected generation into another fresh output and require both media-limit and plugin errors to clear. Then independently decode/verify the declared new segment/track/playlist/local State data and media against retained licensed/native references; unexplained membership/dependency changes must fail. No cooker/package or retail step is authorized by this report.

## Tests, cleanup, preservation and reproduction

All226 Python tests pass, including four new test methods with positive and multiple negative mutations: wrapper channels/nonzero/bounds, exact restored source, wrong exit/tail, gain, RTPC/unknown-layout injection, changed native object, clock120 and ShortID collision. Existing D/NML/Skellige/static bank decoders remain unchanged. New playback review has67 actual gates. No subjective listening by the assistant is claimed.

Capture `finally` stops transports/profiler, resets RTPCs, destroys transports, removes Recorder/anchor and restores channels even on errors. All final captures have no cleanup errors. Empty transport lists were checked before closing each task-owned project; exact task-owned Console PIDs were stopped. No orphaned audio/server remains. A subsequent project save had reformatted two global WWUs; their parsed semantics were **exactly** original. Those format-only versions were backed up and original bytes restored in the isolated primary after closing it. Clean generation and both additional workers already retained exact global bytes. Final source gates require exact other-WWU bytes; no global-field equivalence was silently substituted for that check.

Earlier failed server-readiness/source-order attempts, initial import XML, default-clock captures, first PCM comparison window and generation failure logs remain ignored. Tool preflight now checks the original Sparse gate before importing; it pins native clock and current authored-source fingerprint before capture. The successful controls and24 approved audio files were not overwritten.

To reproduce in a fresh ignored root, prepare native/Minimal/Sparse complete `validation` projects with the existing helper and author the report55 modes using their matching WAAPI ports. Run `sparse_approved_cue.py --root <fresh-root> --audio`, then `--root <fresh-root> --project <sparse-validation.wproj> --port <port>`. Run its `--collision-banks <native-bank-directory>` audit. Capture via `sparse_approved_capture.py` with a fresh label, using the declared case groups and complete identical source copies for parallel workers (never copy licences). `sparse_approved_review.py --root <fresh-root> --label <label>` reviews native/Minimal `matrix-v1` plus the three clock-pinned workers. Source snapshots and clean-generation copying are independent from instrumentation. Preserve fresh-port readiness checks, final source/media/Init hashes and task-owned cleanup. Pacing, probabilities and cue geography remain test-only/undecided.

## Result and next step

**Working foundation demonstrated:** accepted source → exact stripped PCM → collision-free new Wwise cue → native-gain phrase/approved baked tail → genuine finite music-free rest → next phrase, with native combat/intensity/full outro and protected interruption paths preserved at the authoring level. No full24 scheduler, deployment, release or new aesthetic default is implemented.

Next smallest step is the manual entitlement prerequisite for the clean generation project and a bounded **single-cue generated-bank/new-media verification**. After that, choose explicit rest/re-entry behavior before extending cue count. Do not redo accepted edits or broad licence/Project-ID research, and do not assume reselection persistence has been solved.
