# Authored-world isolation proof — 2026-10-13

Observed supported mechanism: relocate the existing 25-State Voice Volume policy from the shared world ancestor onto approved physical generic subtrees. An authored child cannot escape D simply by removing its static attenuation. No child compensation, bus override, global mute or script hook was used.

## Exact scope

`src/wwise/regions/white-orchard-exception-proof.json` pins the original world/quest identities and six generic State scopes: general, tavern, camp, cemetery, battlefield and silent selections. The original five D static playlist attenuations remain. `village_q505/expl_prologue_inquisitors` (playlist ShortID 589261176) remains outside attenuated ancestry; protecting it is **technical-fixture-only**, not musical-intent approval. Winter village/tavern selections remain unresolved and native in this proof, so this is not a replacement production policy. Exact GUIDs, original gains, consumers and evidence are in the manifest; `tools/regional_music.py::plan` verifies ancestry and consumers before editing.

Original authoring material: `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Interactive Music Hierarchy\music.wwu`; events `Events\music.wwu`; global States `States\global_states.wwu`. Fixtures use `C:\Dev\witcher-music-control\build\regional-system\exception\validation\w3_audio.wproj`. Original 1,508 units and 47 regional source files were preserved before instrumentation. Initial supported author passed all source checks; final recovered clean source also passes six scopes/five static changes and exact remaining music semantics (`final-source-semantic-audit.json`).

## Measured tests

Shared `tools/white_orchard_transition_probe.py::run` uses actual native play/location events, MusicSwitchContainer selection and profiler voice contributions plus Music-bus Recorder PCM. Only the separate fixture contains Recorder/anchor instrumentation. D-reference recreates D in that fixture; manifest mode applies relocation. Native playlist synchronization and global fades are retained.

20 captures are retained under fixture `q505-isolation`, `generic-regression`, `extra-preservation`, each with `results.json`, `transition-measurements.json` and WAVs. Sequences include exploration→combat→exploration, ordinary dialogue, cutscene→dialogue 400 ms later, movie/music-only intermediate States, native q001 intro/conversation events, threat changes, Music 100→50→100 and Gwent.

| Observation | D reference | Relocated proof |
|---|---:|---:|
| q505 exploration voice peak, 1–5 s | −234.38 dB | −17.00 dB |
| q505 dialogue peak, 7–9 s | −217.84 dB | −17.51 dB |
| Generic exploration during combat-entry test | −217.18 dB | −217.00 dB |
| Combat layer 1 | −17 dB | −17 dB |
| q001 direct Music 100→50→100 | −22→−28.02→−22 dB | same |
| Gwent | −17 dB | −17 dB |

Generic dialogue remained strongly attenuated (−417 dB contribution in both fixture modes); intermediate-scene generic peaks stayed below −224 dB in the measured captures. q001 authored voices remained audible, approximately −18 dB during the routed intro/conversation test. Threat layer 2 settled to −19 dB at threat 35/100 in both modes.

**Limitation:** early layer-2 onset at 7–10 seconds differed between paired threat captures (D approximately −786 dB versus relocated approximately −22 dB). Native RTPC/source relationships are unchanged, but playback phase/reset history has not been experimentally isolated; this is not proof of identical intensity onset. Require a paired explicit-threat-zero reset repeat before production promotion. Profiler pathless contributions are excluded from path peaks. Recorder durations vary with active bus/voices; missing/truncated recording is not mathematical-zero proof or a time-aligned runtime trace.

## Failures and interpretation

An initial attempt to recover clean fixture source failed State serialization because unsaved WAAPI gain changes had not reached disk. Explicit fixture save, removal of the fixture-only empty world StateInfo, and full semantic verification produced `recovered-clean-source.wwu` outside the project. No gate was weakened. An evidence snapshot with `.wwu` extension elsewhere initially caused a 1,509-unit failure; snapshots now use `.xml` and the 1,508 gate is unchanged.

Supported inference: physical relocation is a viable bounded exception mechanism and preserves measured suppression, q001 and Music master behavior. No generated exception bank or in-game exception confirmation exists. q505 intent still requires the short placement/listening test from report28; winter/tavern remain unresolved. D remains the working game version. Next production work must resolve the threat-repeat limitation and obtain decoded bank validation, not deploy this fixture.
