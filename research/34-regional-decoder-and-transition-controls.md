# Regional decoder and transition controls — 2026-10-13

## Result and stop decision

Implemented a bounds-checked read-only regional decoder and completed the missing controls. **84 tests pass**; retained D passes full source/decoded-bank regression without regeneration. Corrected transport-scoped threat tests reproduce native intensity response. However, the current NML location-level State scopes attenuate the native zone03 combat outro on return to exploration. Source review also uncovered transition consumers absent from the former switch-entry-only coverage gate. New authoring now fails closed on these consumers, including the current NML pilot and White Orchard exception fixture specification. No new candidate bank or package was generated. Working D remains unchanged.

Reports30–33's source/playback results remain historical evidence, not current authoring acceptance for the two exception/pilot manifests. Physical authored-path isolation still works in measured fixtures; the proposed scope placement is incomplete for preserving combat transition cues.

## Decoder implementation and evidence

`tools/regional_music_bank.py::{Reader,decode,states,validate_record,record_gate}` parses the actual v150 MusicNode prefix for numeric HIRC types12/13: FX/metadata arrays, bus/direct parent, variable property bundles/ranges, supported positioning, aux/advanced settings, then inline State data. Offsets derive from fields rather than White Orchard constants. Unsupported listener-relative/spatial layouts, truncation, impossible/duplicate counts, bad varints and nonfinite State values fail. Exact source parent and independently captured global State GUID/ShortID mappings are mandatory. Repeated SoundbanksInfo StateGroup definitions must all agree with the original 25-State enum.

Format provenance: [pinned wwiser primary parser](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/parser/wparser.py), `CAkMusicNode__SetMusicNodeParams` (1912), `CAkParameterNodeBase__SetNodeBaseParams` (620), parameter/position/aux/advanced helpers, `CAkStateAware__ReadStateChunk` (462), inline short-property bundle (57). This reverse-engineered implementation is a format reference, not proprietary runtime authority; our decoder is independently implemented and cross-checked against local source and bytes.

`build/regional-system/nomansgrad/measured-baseline-layouts.json` verifies native-exact baseline objects against actual source parents: State offset28 for zone02/03 selectors and zone02 day/night playlists, **33** for zone03 day/night playlists whose existing Volume is −2 dB. `game-state-sync-identities.json` captures only 26 WAAPI object identities (group plus25 States), not project/licence material. Native STMG supplies group766723505 and original transitions.

Field gate permits only the exact nine nonzero inline States (Volume0/additive2/inDb1, existing group, Immediate synchronization, −200 dB) or an approved static Volume replacement/insertion. All other bytes, record types/sets and opaque music/RTPC tails must remain exact. `regional_music_gate.py::decoded_preflight` additionally requires full source proof, native-exact baseline HIRC/nonheader chunks, identical generated global chunks outside BKHD, and paired exact media bytes/reference/streaming metadata. Existing header/media/chunk checks remain. Generation-warning review, playback and cooker readback are independent required gates; `packaging_allowed` stays false. Combined State plus static edits on one record are currently rejected and require a dedicated tested extension if used in the next correction.

Real regression: `build/regional-system/D-full-decoder-source-regression.json` passes all source and decoded checks: 1,508 units,25 States/five static targets, six changed records only, unchanged global generated data and47 paired media payloads. D SHA remains `925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`; source `cba9ed036e94fe658ca8e506d5539e1f7139f7caea51a21cac3fadbdcebcc259`. The measured field gate now verifies those changes independently of the old pinned-D hash adapter.

Synthetic tests in `test_regional_music_bank.py` cover valid dynamic layouts, volume insertion/replacement, strict State values, parents/tails/types, malformed counts/varints, nonfinite values, metadata/global disagreement and extra/unchanged records. Two additional source tests verify native transition review enforcement. First synthetic transition tests exposed reference nodes overwriting real objects in `graph`; references now cannot shadow their targets. First metadata regression rejected repeated per-bank enums; the corrected gate verifies every occurrence instead of trusting just one. All84 tests subsequently pass.

## Playback controls and measured outcomes

Only reused isolated `build/regional-system/{exception/validation,nomansgrad/fixture/validation}` projects received fixture operations; no production authoring source was altered. Initial connection-refused attempts happened before WAAPI startup; no captures were claimed until servers were ready.

`white_orchard_transition_probe.py --explicit-threat-zero` adds preplay threat0/Music100, 1.1s settling, scoped RTPC reset and active profiler RTPC observations. Installed matching definitions `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\Schemas\WAAPI\ak.soundengine.{setRTPCValue,resetRTPCValue}.json` explicitly document omitted `gameObject` as **transport scope**; `ak.wwise.core.profiler.getRTPCs.json` exposes effective values/scopes. Original probe behavior without the new flag remains unchanged.

First controls (`threat-zero-repeat`, `zone03-threat-zero`, eight captures) explicitly set global0 but scheduled global35/100 did not yield the expected voice response. They remain retained failures, not evidence of a production intensity defect. Corrected transport-scoped runs reset transport/global history and apply all scheduled values to the same documented transport scope. `threat-zero-transport` and `zone03-transport` retain six additional captures with RTPC observations, voice envelopes and PCM; all combat-threat cases show actual **0,35,100**.

| Measured path/window | Reference | Relocated manifest |
|---|---:|---:|
| White Orchard layer2, threat0 (7–9.8s) | below −786 dB | below −786 dB |
| White Orchard layer2, threat35/100 | −19 dB | −19 dB |
| NML zone03 layer2, threat100 (15–18.5s) | −18 dB | −18 dB |
| NML zone03 native combat outro layer1, after exploration return | −18 dB | **−218 dB** |

Ordinary zone03 exploration remained strongly attenuated, including cutscene→dialogue and combat entry. The latest paired run reproduces the outro loss while retaining combat intensity response. State-entry playlist phase differed between runs, so no sample-exact envelope equivalence is claimed. Extremely negative profiler contributions are not proof of mathematical zero. Recorder and profiler have different time origins.

Supported inference: the earlier White Orchard intensity-onset ambiguity was caused by inadequately controlled RTPC scope/history in the fixture; it is resolved by the observed scoped values/response. Independent measured issue: zone03's native transition playlist continues after exploration State enters, so location-ancestor State attenuation applies during that continuation. No filename-only musical-intent classification is needed for this observation: actual native playback/routing proves it is the combat return cue.

## Source closure defect and precise blocker

Original `Interactive Music Hierarchy/music.wwu` under installed REDkit contains three affected NML transition playlist consumers:

| Selector | Playlist GUID / ShortID | Result |
|---|---|---|
| zone02 | `transition_cmb_to_expl` / `{3A7779C9-9DBC-4050-98CA-4C9C05DA8F7A}` /900789511 | Unreviewed State-gain ancestry; no new listening claim |
| zone03 | `transition_to_cmb` / `{3416AD21-5C07-4F44-8CA3-F8020D2BF248}` /1019244598 | Unreviewed transition ancestry |
| zone03 | `transition_to_expl` / `{B362E1DD-8115-4462-997A-731E6568AF34}` /955053242 | Outro attenuation reproduced |

`regional_music.py::{graph,plan}` now traces `TransitionObjectRef` to the real segment and physical playlist ancestors. Attenuated transition consumers need explicit generic classification, approved policy and independent `transition_attenuation_approved`/`transition_evidence`; names alone cannot approve them. No such approval was invented. `transition-consumer-source-gate.json` records current NML/White Orchard exception manifests rejected, retained-D replay accepted. The known-D regression exception preserves historical behavior; it cannot be used to approve a new manifest. Six White Orchard transition playlists also need scope review before exception production promotion.

**Smallest next implementation:** narrow the exception/NML attenuation ancestry to the already-approved generic playlists, leaving native combat intro/outro/transition paths outside it. If a playlist receives both State and static Volume edits, implement a tested joint field allowlist first. Then repeat the same native route/RTPC/outro controls and the protected q505/q001 cases. Do not simply approve attenuating the combat outro to clear the guard. Generate the NML candidate only after that source/playback correction passes; its licence remains independently untested. No additional regions, settings, global mixer or live-game operation is needed.
