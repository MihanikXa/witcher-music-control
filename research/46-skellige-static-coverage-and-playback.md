# Skellige static coverage and playback — 2026-10-15

**Result:** complete source policy and representative Wwise playback pass, including a corrected location-primed sustained-combat control. Fresh candidate generation is blocked by its own project-local licence: exit1/no banks. No modified-bank binary gate, three-bank cache, ZIP or retail Skellige result is claimed. Report45 records the independently verified untouched licensed baseline.

## Reviewed coverage

The manifest `src/wwise/regions/skellige-v1.json` covers all23 original world location selectors and26 relevant noncombat target playlists. Recorded implementation policy decisions are separate from observed identities, parents, source fingerprints and complete consumer rows. Musical intent is inferred conservatively from selector/event/function/media evidence, never assigned automatically from a name or quest number.

| Classification | Targets | Noncombat selection rows | Share of185 rows |
|---|---:|---:|---:|
|Approved generic|12|85|45.9%|
|Verified silent|1|9|4.9%|
|Protected thematic/authored/tracking|7|52|28.1%|
|Mixed-use, retain native|1|5|2.7%|
|Unresolved, retain native|5|34|18.4%|

These185 rows are actual noncombat AudioNode consumers under the fixed nine-State review policy, not area percentages or full-game coverage.94/185 generic-plus-verified-silent rows require no audible generic score. All observed noncombat rows in this inventory have AudioNode targets; undeclared State/fallback behavior is unchanged. Six mixed/unresolved decisions remain pending.

Twelve broad regional, settlement/lift, island, cave and general-ruin playlists are approved as ordinary repeatable traversal scoring. Their exact selectors, location event IDs/actions, original Volume, physical parent, media-reuse evidence and all consumers are retained in `build/skellige-v3/manifest-source-review.json`; source identities and observed consumer rows are pinned in the manifest. Selected paths can also remain live through cutscene State changes: permanent playlist gain suppresses that continuing **generic** voice while authored sibling playback remains independent. This is not a blanket cutscene mute.

The tavern family stays native because a physical playlist is shared with minigames and related material also serves Gwent. Thematic world paths, hunting/tracking arrangements and deliberate dramatic source reuse are protected conservatively; five other theme/location-associated selections lack sufficient approval evidence and remain native. Shared audio filenames alone do not turn every reuse into a story cue. The ten source-only playlists from report45 are explicitly excluded, unchanged and not counted as suppression coverage.

## Exact source edits

Only playlist **Voice Volume (`Volume`)** becomes−200 dB on the following existing objects. No StateInfo, ancestor gain, transitions, AudioNodes, events, synchronization, threat curves, global mixer/effects/parameters or original Music control are changed.

|Playlist ShortID|Physical parent ShortID|Original Volume dB|New Volume dB|Noncombat rows|
|---|---|---:|---:|---:|
|89559491|405881864|0|−200|8|
|618480587|1035669955|-1|−200|9|
|1061684902|84399196|-4|−200|5|
|125522234|551582440|-5|−200|6|
|726745057|551582440|-3|−200|3|
|445898596|36775016|1|−200|9|
|439994516|985847750|0|−200|9|
|769524140|128344438|0|−200|9|
|173571250|969116713|0|−200|6|
|677581091|969116713|0|−200|3|
|297423389|10450794|0|−200|9|
|492969077|61839852|1|−200|9|

`regional_music.py::{plan,author,validate_source}` and `regional_music_gate.source_gate` verify complete consumer closure, protected/mixed ancestry, transition segment consumers, source restoration and fingerprints. The new optional explicit parent pins fail on any mismatch. `validate_event_directory` checks all542 event work units, including nested files outside the music Events work unit; no direct/descendant consumers of the12 targets exist. Synthetic negative tests reject a hidden event consumer and wrong parent. Original strict checks are strengthened, not bypassed.

Candidate: `C:\Dev\witcher-music-control\build\skellige-v3\candidate\w3_audio.wproj`. All1,508 WWUs remain; all1,507 nonmusic units and253 original audio inputs match installed source. Reversing only the12 Volume edits restores every original music semantic. Candidate music SHA `414dd1193433d6aaadb0fa0f27844770661fdd3d7d28c293273abd14ca56bb76`. Manifest SHA `6ba5778b1c2afbe052266a0f938d67f595831d5015834f7cfe001a0b75e55446`. Full proof: `build/skellige-v3/candidate-source-gate-all-events.json`.

The complete candidate and separate fixture use `white_orchard_prepare.py --preserve-hierarchies --regional-root music_skellige --immutable-originals build/skellige-v3/baseline`. Only253 verified original audio files are NTFS hardlinked to the canonical **build baseline**, never to installed resources. Each link is independently verified with `samefile`; source hashes must agree before linking. WWUs/projects remain independent, and no licensed project is copied. Shared originals are immutable: never overwrite/edit them in place. Negative tests reject stale pools, escaping paths, existing destinations and non-audio paths. No unnecessary multi-gigabyte audio copies.

## Playback method

`regional_selector_matrix.py` consumes reviewed `src/wwise/regions/skellige-playback-v1.json` groups rather than creating another region-specific authoring script. Only a separate complete `build/skellige-v3/fixture/validation` project receives Recorder, six-channel output and silent-anchor instrumentation. No fixtures enter production source or banks. Native-reference versus manifest controls restore original playlist volumes between modes; explicit RTPC transport/global reset, threat0/Music100 and1.1s settling follow reports34–35. Profiler actual selector paths, accepted State/parameter timestamps, contributions, effective RTPCs and WAV/50ms PCM envelopes are retained. Native random/playlist history is not forced identical; wall/PCM origins differ and virtual Recorder absence is not treated as measured zero.

An initial call rejected an incorrectly assumed location event before capture. Its ignored folder remains retained; only `mus_loc_ard_skellig`, verified from actual source events, was used by accepted main captures. The fresh accepted folder is `skellige-main-outros-verified-event`. All other event identities are reviewed in the manifest evidence. The authored-direct control explicitly validates a playlist under the unedited regional quest branch; it tests that playback ancestry and Music response, not a retail quest/scene event sequence.

## Final playback and generation results


**38 captures retained:**34 native/manifest controls in the main matrix and four additional60s location-primed sustained-combat controls. Accepted profiler traces, actual selector identities, timestamps, PCM files and50ms envelopes remain under `build/skellige-v3/fixture/validation`. `completed-playback-verification.json` binds the first34 captures, and `settled-combat-outro-verification.json` binds the four stronger settlement controls. Representative cases do not imply every cue or all12 targets were individually auditioned: **four modified static targets** were directly observed (day, night, cave, settlement); all12 receive full structural/consumer/source proof. Boat selection uses the same reviewed traversal playlist without a new mix bus.

Observed results:

- Main-region combat intro stays at native−20 dB; threat0→35→100 is verified on transport object18446744073709551614, distinct from the unchanged global defaults. All three combat layers reach native−18 dB in both modes. No threat curve, native weighting or synchronization is edited.
- Core return cue remains−17 dB, completing after exploration returns13.11s/14.40s. Native/modified outro endings20.95/21.02s and22.52/22.59s.55s captures show completed endings, not truncation at transport stop. Night controls retain native transition selection; generic night gain stays below−217 dB.
- Boat→combat→boat preserves intro−20 dB, body−18 dB and outro−17 dB. Native/modified outro ends27.77/27.83s after boat returns20s. Boat↔dialogue retains generic suppression; neither boat nor dialogue unmutes the continuing traversal playlist.
-65s long-silence control starts combat35s and returns exploration42s; native/modified outro ends50.34/50.19s at−17 dB. Generic score remains suppressed through the long wait, overlap and return.
- Day/dialogue, intermediate cutscene/movie/music_only→dialogue, cave and settlement measured generic contributions remain at or below−214 dB (night/cave−217 dB). `regional_playback_review.static_voice_checks` verifies the actual−200 dB SoundBankValue on each observed playlist's full physical ancestry, not merely aggregate silence; it rejects missing gain, compensating bleed and absent voice evidence. Some voices continue virtually at inaudible levels; no mathematical-zero claim.
- Gwent remains audible at approximately−17 dB; shared minigame loop stays−23 dB in both controls. Random Gwent choices differ naturally, so byte-identical PCM is not required. The mixed physical playlist remains native.
- Protected thematic/tracking world playback remains audible at−17 dB. Direct authored-branch playlist690451412 stays−22 dB in both controls. This verifies its physical routing/ancestry, not a scene or quest event sequence. Both protected controls retain the original Music curve:100→50→100 gives RTPC contribution0→−6.0206→0 dB. See `music-master-measured-curves.json`; separate parameter samples confirm effective50/100 values.

### Settlement discrepancy and stronger control

The initial short-combat settlement pair was **not accepted as an outro-preservation comparison**: native recorded an outro, modified did not. Its event changed location *after* music had started, so native began in the previous region selector while modified began with different retained location history. Combat also returned before the long intro reliably reached the loop. No production fix was inferred from this unmatched observation.

The fixture now supports optional `prime_location`: after starting its silent transport anchor, post the verified **switch-only** location event, settle0.1s, then start music. Matching installed `WObjects.xml:3682` identifies ActionType23 as Set Switch. `primeable_location` rejects mixed/play/missing events, so this control cannot accidentally pre-play an authored event. Source production events/transitions are not edited.

`src/wwise/regions/skellige-playback-settled-v1.json` repeats both phases with combat held20s and60s captures. Actual first-two-second profiler paths verify **the same settlement selector405881864** in all four controls. Combat body enters about15.6/15.7s and remains at native−17 dB; it is not masked by an intro-only test. Exploration returns26.06/26.05s;−17 dB outro ends36.52/36.48s. Offset controls return27.34/27.44s and outro ends37.33/37.44s. Every outro finishes well before capture stop, and continuing generic score remains−214 dB. Native beat alignment explains some delay between State return and cue entry; no fades were shortened.

**Demonstrated conclusion:** the static-only design preserves sustained settlement combat and its complete audible outro under matched starting selection, including two entry phases. **Inference:** earlier missing-outro evidence was confounded by location/playlist history and short combat, rather than an attenuation defect. The two influences were corrected together; their individual causal shares are not isolated. Retain the first comparison as rejected evidence, not a passing gate or proven game regression. No speculative production correction was made.

## Candidate generation prerequisite and packaging boundary

Candidate source is concrete and validated, but its freshly prepared project has not inherited baseline entitlement. Selected `music_skellige` Windows/SFX generation into `build/skellige-v3/candidate-banks` exits **1**, produces **zero banks**, with **six Mastering Suite errors, one fatal trial26,218/200 limit and ten warnings**. Full `command.json`, `result.json`, `generation.log` and sanitized `candidate-generation-blocker.json` are retained. No candidate licence fields/key were read, copied or transferred. Failed generation does not supply a package.

User must manually open:

`C:\Dev\witcher-music-control\build\skellige-v3\candidate\w3_audio.wproj`

Apply the **existing approved Witcher3 REDkit entitlement** through **Project → License Manager**, then save. Do not send the key. This is the remaining manual prerequisite; no new entitlement request or purchase is needed. Reuse the now-verified licensed baseline; do not regenerate it.

After confirmation, generate only selected Skellige into fresh `candidate-banks-licensed`, review warnings against its16-warning regional baseline, and run `regional_music_gate.py` with the retained baseline, actual native bank, final manifest and unchanged global State identity table. Baseline type13 layouts and physical parents have been measured for all12 targets (`approved-baseline-layouts.json`); the existing variable-layout decoder supports them. **Actual modified HIRC/media/BKHD/global validation remains pending a successful bank**. Require exactly12 approved Volume records, no additions/removals, unchanged serialized tails/RTPC/selector/transition data and253 exact media payloads. Generated Init must remain nonshipping and introduce no changed globals versus this pristine baseline.

The existing bundle interface accepts an explicit three-region list and requires each independent source/binary/media proof. New `audit_bank_identities` rejects duplicate bank IDs or overlapping HIRC definitions before preparation/cooking; real retained D+NML+untouched-Skellige references pass with zero shared definitions. Shared references to original globals/media are intentional, not duplicate definitions. This is **not** a native three-bank cook or a modified-candidate proof.

The two-bank diagnostic profile is explicitly bounded: `reviewed_diagnostics` now rejects a new bank set rather than extrapolating NML messages to Skellige. Only after successful candidate gates should the native cooker produce actual three-bank output; independently review those diagnostics and implement its observed exact profile before allowing archive finalization. No Skellige diagnostic expectations have been fabricated and no v3 archive exists yet. Preserve all individual/v1/v2 rollback packages. No Init, WEMs, project, source audio or licence material may ship.

## Regressions, retained evidence and next action

- `D-regression-full.json`: retained White Orchard D passes full source/decoded/media/global checks and all542 event-work-unit closure; same bank hash `925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`.
- `NML-v2-regression-full.json`: expanded NML passes unchanged21-record/423-media proof and new event closure; same hash `7317029446858ddf5fa1958ecab6021263c62b097ea0b28218505f591a60bb78`.
- Existing consolidated-v2 ZIP remains SHA `6478460bf8c4dc0f68b24464503808852a9bb65b921a6f84e9909c245da1f512`. Original native Init remains SHA `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`. Neither bank was regenerated, and Vortex/installed configuration/saves were not changed.
- **139 tests pass** (`unit-tests-final.log`). `post-generation-source-gate.json` passes all source/audio/event checks after the failed generation; `final-retained-artifact-preservation.json` verifies seven retained bank/archive/Init hashes under `build/skellige-v3`; source/authoring, binary, native-cache and retail results remain distinct. All raw evidence is ignored; committed files are sanitized helpers, tests, manifests and documentation only.

**Smallest next action:** manually apply entitlement to the exact candidate above, then resume selected generation, strict binary/media/global gates and actual native three-bank diagnostic review/cooking. Source policy and measured playback do not need to be restarted. Retail play remains deferred per reports38/43. After v3 is complete, Kaer Morhen's small main-game region is the next efficient manifest/source/bank implementation, then broader Toussaint coverage; no other regional bank has been authored or generated here.
