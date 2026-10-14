# Static playlist correction and NML candidate licence stop — 2026-10-14

## Result

**Observed source and Wwise playback:** static-only attenuation on the four approved NML generic playlists resolves the combat-outro defect. No StateInfo is added to shared locations or playlists. Native combat intros, intensity modulation and return cues retain their original ancestry. The separate White Orchard exception fixture also passes the corrected playback tests. The installed/retained D remains unchanged.

**Generation:** corrected NML candidate exits **1**, produces **zero banks**, and reports six Mastering Suite errors plus the **26,218/200** trial-media fatal error and ten warnings. The approved entitlement is ineffective in this candidate project. Stop for manual project-local application; no candidate binary comparison, cache, ZIP or retail-game validation is claimed. The untouched licensed baseline from report33 is reused, not regenerated.

## Confirmed cause and placement

Source alias **I** is `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Interactive Music Hierarchy\music.wwu`. Original SHA-256 remains `f8184d13ea08f6bc161719884e9341bdfd3a3e7666b203c296ffae37d4e08251`.

The following playlists are physical children of their location MusicSwitchContainer, alongside exploration/combat playlists. Native `TransitionObjectRef` rules play segments inside them; the State gain on the shared location therefore affects their voices even after `game_state` returns to exploration. Report34 measured zone03's native −18 dB return cue at −218 dB under that location State gain. This is inherited attenuation, not evidence that native beat synchronization is faulty.

| Original transition playlist | GUID / ShortID | Physical parent / I declaration | Corrected treatment |
|---|---|---|---|
| zone02 `transition_cmb_to_expl` | `{3A7779C9-9DBC-4050-98CA-4C9C05DA8F7A}` /900789511 | `nml_zone_02` /193134718; I:246872 | Entirely native; no gain ancestor |
| zone03 `transition_to_cmb` | `{3416AD21-5C07-4F44-8CA3-F8020D2BF248}` /1019244598 | `nml_zone_03` /432285193; I:250760 | Entirely native; no gain ancestor |
| zone03 `transition_to_expl` | `{B362E1DD-8115-4462-997A-731E6568AF34}` /955053242 | `nml_zone_03` /432285193; I:250166 | Entirely native; no gain ancestor |

The directly referenced segment GUIDs are respectively `{79FA05C9-B0E4-4461-894B-2DDB71A86BA6}`, `{94BF0644-305E-41A3-9C43-3DF63F3F8A72}`, and `{1A957AB4-5D6E-4D18-8290-AA1E17667ABE}`. The graph resolves real objects rather than letting reference IDs shadow them. Exact closure is retained in `C:\Dev\witcher-music-control\build\regional-static-outro\native-transition-closure.json`.

**Chosen A: static-only approved generic playlists.** These selected day/night playlists already cover exploration, ordinary dialogue and overlapping generic material during intermediate States. Permanently attenuating this verified generic material avoids a gain ramp exposing it during combat entry, while native combat/transition siblings remain untouched. B/C contextual or combined-field changes are unnecessary for this pilot. No compensation gain, new bus, script hook, timing change or blanket cinematic exemption was introduced. Static suppression also applies if these same generic playlists remain selected in cutscene; intentionally authored cues on separate paths retain native treatment.

## Exact production edits

`src/wwise/regions/nomansgrad-pilot.json` now has `state_scopes: []` and four static targets. Only each playlist's existing Voice Volume (`Volume`) is set to −200 dB:

| Playlist | GUID | ShortID | Original → new | I declaration |
|---|---|---:|---:|---:|
| `expl_nml_zone_02` | `{48810350-DE09-4F69-B3DA-FCF4667EF177}` |719937819|0 → −200|245312|
| `expl_nml_zone_02_night` | `{E5564ADB-9A93-4E6A-8D72-DE209E1A1A2D}` |946096996|0 → −200|246533|
| `expl_nml_zone_03` | `{958962C3-1AC8-4C75-939C-B5EBEC3C75DD}` |132074504|−2 → −200|248313|
| `expl_nml_zone_03_night` | `{FA35E341-DB95-427A-BC50-EC2DD414DA4C}` |568231384|−2 → −200|249795|

Consequently zone03's additional attenuation is 198 dB, not 200; this is perceptual suppression, not a mathematical-zero claim. Compared with the rejected report32/34 pilot, both location State tables are absent; the same four static values remain. Original selectors, playlists, transitions, events, RTPCs and sources are unchanged.

The clean existing complete candidate was restored to pristine source before shared authoring. Its former music source, manifest, audit and snapshot remain under `build\regional-static-outro\previous-nml-candidate`; no project/licence file was read or copied. Other prior captures and D/A/C artifacts remain in place. Reuse avoided another multi-gigabyte project/media copy.

Candidate music source SHA-256: `ebd3d6ae95680307a6a965c07b096a02e659ccb5703981e4a27566e67d416f4f`. NML manifest SHA-256: `ad491c8c2331b163e5683cdba8fd028a924f689f5f746d328c7e028ba8a09d22`.

## Fail-closed gates

`tools/regional_music.py::{plan,validate_events,validate_source}` supports an exact `static_consumer_paths` allowlist: selector GUID, ShortID and complete State path for every selector consumer. A newly added/missing consumer, altered selector identity, combat/Gwent use, outside-world routing, direct event to a target **or any descendant**, unapproved/mixed target or native transition inheriting gain fails. The prior reviewed-scope checks still apply when no explicit consumer closure is supplied. Source fingerprint pins and exact semantic restoration checks remain.

The new manifests preserve all prior classifications: NML has four approved generic, eleven verified-silent, three conservative protected, four mixed and36 unresolved entries. Forty mixed/unresolved decisions remain native. `shipping_policy_complete: false` explicitly means partial coverage, not permission to mute those paths. White Orchard q505 remains **technical-fixture-only**, with winter/tavern questions unresolved.

`NML-source-gate.json` proves complete1,508 work units, unchanged original434 audio files, unchanged all1,507 nonmusic units/global definitions, and only the four approved music properties changed. The post-generation gate repeats those checks. `tools/regional_music_bank.py` already decodes static insertion/replacement with derived layouts, exact parent/property/rest-of-record checks; **no speculative combined-field decoder was added**. Synthetic static-only record tests reject accidental location States and preserve untouched transition records. Candidate binary/media/BKHD checks cannot run without generated output; they have not been weakened.

Retained D passes `build\regional-static-outro\D-regression.json`: full source, derived six-record bank field checks, native-exact baseline comparison, unchanged disposable generated global data, and47 paired media payloads. D bank SHA remains `925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`. Native Init remains `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`.

**98 unit tests pass** with `python -m unittest discover -s tools -p 'test_*.py'`. New positive/negative tests cover static-only source and serialized-record edits, exact consumer identity/closure, combat mixed use, direct event descendants, native outro siblings, accidental location-State changes, missing/attenuated/truncated outro captures and duplicate controls. The printed false-gate JSON lines are expected negative-test evidence, not suite failures.

## Real playback evidence

`tools/regional_outro_probe.py` runs native-reference versus manifest in the existing complete isolated fixtures. `white_orchard_transition_probe.py` retains transport/global RTPC resets, verified effective threat0/Music100, 1.1s settling, native play/location events, and profiler contributions. Combat starts at6 or7.3s; exploration returns at13 or14.3s. Extended35s captures observe completion rather than stopping during the outro. Original native timing/transition rules are unedited. `regional_playback_review.py` rejects missing, attenuated or capture-truncated outro evidence.

**57 matrix captures plus two fresh-process threat captures** are preserved. All12 phase-paired outro checks pass (native/modified × two entry phases × three tested locations). Selected measured return-cue results:

| Location / cue | Native peak | Static-only peak | Static-only observed interval, after exploration return |
|---|---:|---:|---|
| zone02 outro, entry6s |−16 dB|−16 dB|14.25–19.42s; no outro voices remaining by35s|
| zone02 outro, entry7.3s |−16|−16|15.54–20.75s|
| zone03 outro L1, entry6s |−18|−18|13.88–19.02s|
| zone03 giant outro, entry6s |−18|−18|16.01–21.71s|
| zone03 outro L1, entry7.3s |−18|−18|14.69–19.78s|
| zone03 giant outro, entry7.3s |−18|−18|16.85–22.47s|
| White Orchard outro, entry6s /7.3s |−19|−19|14.21–19.17s /15.27–20.16s|

Zone03's standalone combat-entry transition peaks at native −17 dB in both designs. Zone02 combat-intro L1 peaks at −13 dB, later main-combat L1 at −14 dB. Zone03 combat L1 remains −18 dB. Generic day exploration peaks at −219 dB in zone02 and −217 dB in zone03; it stays suppressed during overlap, dialogue, and cutscene/movie/music_only→dialogue. Night variants also remain suppressed. These are actual voice contributions, not assumptions from State labels.

Transport RTPC observations show exactly threat0→35→100 and Music100. Zone02 intro L2 and White Orchard L2 become audible at35 and remain at100 (−15 and−19 dB respectively). Zone03 has distinct native intro/main-loop curves: intro L2 is audible at35 (−18 dB); main-loop L2 remains below threshold at35 and reaches −18 at100. The first A/B matrix chose different native playlist segments. Fresh-process repeats reversed that choice; matching-segment observations across both runs preserve those distinct thresholds. Do not misreport unlike segments as an intensity regression. Playlist history/random selection and phase cause differences in chosen segment/timing; source checks preserve the actual playlists and native RTPC curves.

In the corrected White Orchard technical fixture, q505's thematic path measures −17 dB during exploration and median −18 dB in the sampled dialogue window, matching native. D-reference remains approximately −232/−218 dB in those windows. q001 intro/conversation stay audible; direct conversation intensity3 responds Music100→50→100 as −22→−28.02→−22 dB in both native/modified. Gwent remains audible at −17 dB with different native random tracks; source routing is exact. None of this approves q505 intent or alters deployed D.

Recorder files include50ms PCM envelopes where the Music bus is active. For purely suppressed runs the virtual/inaudible bus sometimes emits no WAV; this is **not measured zero PCM**. Profiler envelopes and constant approved −200 dB playlist contributions provide the suppression evidence. Wall-clock profiler and PCM origins are not sample-aligned. The first native trials also retain brief previous default-location material (caves/battlefield) before location selection settles; those outside-pilot paths are not claimed suppressed. Subsequent selected-location trials and all manifest overlap results are explicitly identified in traces.

Evidence roots (all ignored/private locally):

- `build\regional-system\nomansgrad\fixture\validation\static-outro-35-zone{02,03}-{outro,contexts}`.
- `build\regional-system\exception\validation\static-outro-35-{village-outro,village-contexts,village-authored,q505}`.
- NML fixture `static-outro-fresh-{native,manifest}-threat`.
- `build\regional-static-outro\{playback-review,fresh-process-threat-review,native-transition-closure,NML-source-gate,D-regression,generation-diagnostic-review}.json` and generation command/log/result. Pre-start connection refusal in the first fresh-native attempt occurred before any capture; retry used the same unused fresh output name.

## Generation prerequisite and smallest next action

User opens **`C:\Dev\witcher-music-control\build\regional-system\nomansgrad\candidate\w3_audio.wproj`** and applies the already approved REDkit entitlement through **Project → License Manager**, then saves/closes Wwise. Do not provide the key to Codex. Only this candidate needs application; baseline remains verified.

After confirmation, re-run selected `music_nomansgrad` Windows/SFX generation to a **new** ignored output directory using `white_orchard_wwise.py` (for example `build/regional-static-outro/candidate-banks-licensed`). Reuse `baseline-banks-licensed`, run the full decoded gate with `game-state-sync-identities.json`, review all diagnostics against the report33 baseline, verify all media/global metadata, then use the existing native cooker and exact payload readback for a regional-only experimental Vortex ZIP. Package no Init or WEMs. No new bank/source changes or broad investigation is needed before that build.

NML runtime compatibility remains untested; source, authoring playback and future binary verification are distinct gates. Eventual retail test needs separate authorization. Current NML design covers zone02/03 approved day/night selections only. No package/hash exists yet; game, Vortex, saves and native Init were never changed.
