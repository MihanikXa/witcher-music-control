# Expanded NML source and licensing gate — 2026-10-14

## Status and coverage

**Implemented:** versioned `src/wwise/regions/nomansgrad-expanded-v2.json`, shared authoring and full source validation in a fresh complete isolated project. **21 static targets, up from four**, with17 newly approved playlists. No shared location State gains, global effects, script hooks or sliders were added. The original four-target manifest, licensed pilot bank and individual/consolidated-v1 archives remain preserved.

**Measured consumer coverage**, not guessed map area or track count:

| Nine-State noncombat selection rows | Pilot | Expanded v2 |
|---|---:|---:|
| Approved generic, suppressed |18|117|
| Verified silent, unchanged |99|99|
| Protected/likely authored, unchanged |27|27|
| Mixed combat/Gwent/minigame, unchanged |30|30|
| Ambiguous, unchanged |245|146|
| Total |419|419|

Generic suppression coverage is6.5× the pilot, from4.3% to27.9% of all419 rows (5.6%→36.6% of320 nonsilent rows). Suppressed-or-already-silent rows total216/419,51.6%. These are selector rows, not geographic-area percentages or confirmed musical intent. Twenty-one generic, eleven silent, three protected, four mixed and nineteen ambiguous playlist decisions cover the complete58-target inventory. The remaining23 mixed/ambiguous decisions stay native. Core traversal and city scoring were substantively reviewed; coverage is still incomplete.

**Generation stop:** fresh expanded project licence is ineffective. Selected NML generation exits1 with zero banks, six Mastering Suite errors, one fatal26,218/200 trial-media-limit error and ten warnings. No candidate binary/media verification or updated consolidated-v2 package is claimed. The independent licensed NML baseline was reused for source/layout comparison, never regenerated. Report40's two-bank bundle contains the earlier verified pilot, not v2.

## Source-backed classification and exact edits

Source is installed read-only REDkit `assets/w3_audio`, specifically `Interactive Music Hierarchy/music.wwu`, `Events/music.wwu`, `States/global_states.wwu` and report29's complete inventory. The music fingerprint stays `f8184d13ea08f6bc161719884e9341bdfd3a3e7666b203c296ffae37d4e08251`. `regional_music_review.py::review` records all58 physical parents, original values, full selector/State consumers, location-switch values and actual event actions, media/quest-branch reuse, direct audio events and native transition segments. Full raw technical details are in ignored `build/consolidated-expansion/expanded-source-event-evidence.json`; user-facing tables use numeric identities to avoid narrative spoilers.

The approved additional families comprise ordinary regional day/night traversal, adaptive city ambient score and repeatable underground ambience. This is an **approved inferred generic policy**, not a claim to have read an author's intent. Supporting evidence is the combination of repeatable world-location switch events/return actions, separate noncombat versus combat/Gwent mappings, adaptive/variant source structures, complete physical ancestry and absence of explicit audio-event or transition-material consumers. No classifier uses quest-number, filename or genre heuristics. The day/night adaptive families reuse only the previously verified silence source with the authored branch. Underground ambience has real source reuse with other contexts; its different playlist/parent identity is crucial: suppressing this generic path does not suppress identical media through other protected/mixed paths. Fixed thematic and exceptional context selections remain protected/ambiguous rather than automatically generic.

Each reviewed selector has actual location-setting event actions in the source (two per new selector family); the pilot zone02 has three. Event names alone were not treated as branch/cue proof. A first ad-hoc audit incorrectly counted referenced global IDs inside a playlist as physical descendants; the corrected audit excludes reference nodes and the existing strict `graph`/`validate_events` independently checks real ancestry. Actual direct audio-event consumers are zero for all21 targets. Transition descendants are also zero. All complete consumer lists are pinned in the new manifest, and combat/Gwent/minigame or outside-world consumers fail closed. Related native intro/outro playlists remain sibling objects without attenuated ancestors.

Only playlist **Voice Volume (`Volume`) becomes −200 dB**. Existing values differ; the additional gain is not uniformly−200 dB and is not mathematical zero. The exact changes, including the four retained pilot targets, are:

| Playlist ShortID | Original parent ShortID | Original Volume dB |
|---:|---:|---:|
|212262762|387415965|0|
|658433984|24105830|3|
|619624006|101254717|−4|
|557630169|430000258|0|
|932329779|903258976|0|
|719937819|193134718|0|
|517264825|387415965|1|
|844878119|1039349895|−1|
|939329143|1039349895|−3|
|132074504|432285193|−2|
|591906274|24105830|−6|
|815747428|903258976|0|
|284863188|71417542|1|
|1041422844|600355437|0|
|1042184487|781069643|−3|
|946096996|193134718|0|
|715939731|600355437|1|
|265482033|781069643|−7|
|652104057|923976362|−3|
|568231384|432285193|−2|
|878261688|817752635|−7|

Exact GUIDs, source names, original fingerprints and all consumer paths are preserved in the versioned manifest. Source-semantic restoration removes only these21 changes and matches the entire original music hierarchy. Every one of1,508 units remains; all1,507 nonmusic work units,434 originals, global definitions, events, transitions and authored routing pass their hash/semantic checks. Clean music source SHA `815c3288d958e42fe4532bfb3ebafedc976e753b898670900027bbc0ffa44250`; manifest SHA `44ff812bfb51abce8105157f6c857092ca806534d16458cb4e97c4b97ff4eab5`.

All21 pristine licensed-baseline records were decoded with their exact source parent. Measured State offsets are28/33; none requires an unsupported or combined State/static layout. This is **baseline layout evidence**, not verification of a nonexistent v2 bank. After successful generation, the existing independent `record_gate` must verify the exact21 changed records, all other HIRC, media/streams, globals/Init registrations, STMG and BKHD metadata. No binary checks were relaxed.

## Representative Wwise regressions

Thirty native-reference versus expanded-manifest captures completed in a separate complete fixture: sixteen countryside cases, four extended city combat-return cases and ten city/context/protected-master cases. Explicit threat0/Music100, transport/global resets,1.1s settling and profiler RTPC observations reuse report34's corrected method. The first countryside attempt timed out at `getInfo` before capture; its directory remains retained, and only the fresh retry is accepted.

Grouping uses common static-only separation and native selector roles rather than testing every target combinatorially. A new countryside selector tests layered day/reduced night scoring, while an adaptive city selector tests a different original volume and playlist family. Source closure for **every** target prevents combat/transition gain inheritance; exact unchanged native selection/transition semantics support those mechanical guarantees. Untested locations are not claimed individually auditioned. Original zone02/03 pilot and White Orchard D remain source/bank regression references.

Observed paired results:

- Countryside combat intro/return transition peaks at native−17 dB in both designs. For entry6s, native outro ends21.86s, expanded21.79s after exploration returns13s. Entry7.3s: native23.21s, expanded23.16s after return14.3s.35s captures show complete endings, not capture truncation.
- City return cue peaks at native−13 dB in both designs; native/expanded endings22.04/22.01s and23.53/23.52s for the two entry phases. Native timing/selection rules are not altered.
- Generic countryside peaks remain below−206 dB through ordinary dialogue and intermediate cutscene/movie/music_only→dialogue; city dialogue/movie overlap peaks at−217 dB. Night and combat-entry overlaps remain suppressed.
- Effective RTPC values0→35→100 are captured on the transport. Countryside combat layers retain their native−18 dB peaks; city threat/intensity follows the unchanged source curves. Random/playlist phase differences are not treated as identity regressions.
- Protected direct q001 conversation, whose media is available in this full fixture, keeps Music100→50→100 response at−22→−28.02→−22 dB in both controls. This is a known early-cue regression; no later narrative scene or retail quest was visited. All NML protected paths also retain original source ancestry/properties. Gwent/mixed paths are unedited and remain covered by strict source closure; earlier dedicated Gwent evidence is retained.

Raw profiler identities, timestamps and50ms PCM summaries remain in `build/regional-system/nomansgrad/fixture/validation/{expanded-zone01-v2-retry,expanded-city-outros-v2,expanded-city-contexts-v2}`. Summaries are under `build/consolidated-expansion`. Virtual/inaudible Recorder absence is not measured zero PCM; wall and PCM origins are not sample-exact. No retail test, custom saves, forced visits or progression changes occurred.

## Precise prerequisite and scaling

User must manually apply the existing approved entitlement via **Project → License Manager** to:

`C:\Dev\witcher-music-control\build\consolidated-expansion\nml-v2\candidate\w3_audio.wproj`

Do not send/copy the key. This is a fresh source project, not a copied licensed project. Source and playback are complete; do not repeat them or rebuild the untouched baseline unnecessarily. After application, generate only selected NML to a fresh output, run the full decoded/media/global/diagnostic gate against the retained licensed baseline, then make a separately versioned consolidated-v2 cache with the exact retained D bank. The generation failure and earlier successful pilot proofs are preserved.

Next substantial region is Skellige after v2's binary/package gates pass: reuse complete-source preparation, explicit per-path policy, all-consumer review, representative selector grouping, regional decoder and multi-bank bundle writer. Report29's unreachable/absent native playlist observations require separate structural handling, not arbitrary edits or extra-bank regeneration. Subsequent regions can enter the bundle only with independent passing proofs. No bulk authoring of the remaining six banks has begun. Offline acceptance continues under report38; it is not retail compatibility confirmation.
