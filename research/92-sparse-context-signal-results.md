# Contextual Sparse foundation — source audit and offline policy proof

2026-10-19. Fulfills report91. **Source inspection and simulation only: no new Wwise session, SoundBank, audio edit, game mod or retail test.**

The useful next architecture is a small contextual observer/decision layer with Wwise retaining final playback authority. The offline model demonstrates optional opportunities, time-normalized probability and composition-aware selection. It does not establish a working script-to-Wwise request gateway. In particular, exploration State is neither proof of authored-music absence nor proof that the combat outro has finished.

## Evidence and reproducibility

- [Signal catalog](92-context-signal-catalog.json): 19 ranked signal families, exact absolute paths, source SHA-256, symbols/lines, delivery limitations and proposed minimal runtime probes. All cited installed/REDkit script pairs are byte-identical.
- [Results](92-context-policy-results.json): profiles, cue identities, aggregate/per-trace measurements, artifact hashes and preservation results.
- [Synthetic timelines](92-simulated-context-traces.json): explicit simulated provenance, never presented as captured gameplay.
- Original tools: `tools/sparse_context_audit.py`, `tools/sparse_context_policy.py`, `tools/sparse_context_trial.py`; regression suite `tools/test_sparse_context_policy.py`.
- Local visual review: `C:\Dev\witcher-music-control\build\sparse-context-audit-v1\final\index.html`. Static HTML shows eligibility, native vetoes, optional windows, cue allocations and complete reason logs; no audio or server. HTML structure/escaping is tested; no actual browser session was performed.

From repository root, use fresh output names (tools refuse overwrites):

```powershell
python tools/sparse_context_trial.py --output build/sparse-context-audit-v1/replay --seeds 200
python tools/sparse_context_trial.py --output build/sparse-context-audit-v1/portable --seeds 200 --metadata-only
python -m unittest discover -s tools -p "test_*.py"
```

Default replay checks cited local source fingerprints and the three private cue payloads. Metadata-only replay explicitly skips those checks; its 4,800 mathematical result rows and representative traces matched the fully verified run exactly. Full repository suite: **268 tests passed**, including 26 new focused tests. Local logs and complete results are ignored build evidence; sanitized summary and trace inputs are committed.

## Source-grounded signal ranking

Paths below are relative to **G** = `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts`. **W** = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`. Full paths and fingerprints are in the catalog. A means a strong source-defined input/routing candidate; B requires filtering or delivery verification; C is an unsafe proxy or an unresolved interface. **None of these mod hooks was newly retail-tested.**

| Signal | Rank | Concrete source and useful behavior | Boundary |
|---|---|---|---|
| Region | A | G `game/commonMapManager.ws:148`, `GetCurrentArea`; G `engine/sound.ws:279`, `InitializeAreaMusic` stops/starts regional playback | Coarse area, not biome or meaningful arrival |
| Music location | A | W `Switches/switches.wwu:1183`, location_prologue `{3139B245-58B7-4C39-9BE9-414395307E75}`; W `Events/music.wwu:254`, village event `{DA48339C-9810-491C-A4A4-24CAF7811E13}` sets Switch | Exact Wwise selector exists; complete script-side producer coverage not established; duplicates are not arrivals |
| Logical sound State | A | G `engine/sound.ws:235`, public `GetCurrentGameState`; `CollectSoundStates:557` prioritizes explicit States and native combat classifier | Public query avoids private-state interception; not audio voice ownership/timing |
| Day/night | A | G `game/environmentManager.ws:127`, `IsNight`; G `game/player/r4Player.ws:15076`, `CheckDayNightCycle` and day/night notifications | Game-time jumps must not advance an elapsed opportunity clock |
| Weather | B | G `engine/environment.ws:35,53`, rain/weather queries; G `engine/world.ws:101`, `OnWeatherChange` forwards player callback | Weather commentary filtering in `r4Player.ws:1510` is not event availability; callback mod delivery untested |
| First discovery | B | G `game/gameplay/fast_travel_entities/fastTravelEntity.ws:75`, player guard, first-discovery trigger disabled before discovery call; map wrapper `commonMapManager.ws:163` checks prior discovery | Strong local path, not a universal discovery bus; remote quest/inventory/debug discovery calls must be excluded |
| General map-pin change | C | G `game/commonMapManager.ws:158`, `OnMapPinChanged`; G `game/globalEventsScriptsDisptacher.ws:174`, listener registration | Broad mutation notification has no discovery identity/type payload; cannot trigger music indiscriminately |
| Location-area entry | B | G `game/gameplay/gameplay_triggers/locationArea.ws:17`, entry/HUD/reward logic | No player guard in that handler; saved discovery depends on reward path; repeated entry needs filtering |
| Journal subarea | B | G `game/commonMapManager.ws:341`, `GetCurrentJournalAreaByPosition` | Region/position-derived label, not biome or emotional significance |
| Travel mode | A | G `game/actor.ws:6431,6455`, `IsUsingHorse`/`IsUsingBoat`; G `game/player/player.ws:2466`, `IsSailing` | Mount-in-progress differs from mounted; being on a boat differs from sailing |
| Movement/activity | B | G `game/components/movingAgentComponent.ws:81,110`, speed/velocity; G `game/player/player.ws:1380`, sprint query | Velocity is not discovery, vista or importance; useful suitability/veto input only |
| Interior | B | G `game/player/r4Player.ws:433`, `IsInInterior`; G `game/components/interiorArea.ws:34`, entry | `isCave` at line16 is a postprocessing setting, not a universal cave/music taxonomy |
| Combat/hostility | A | G `game/player/r4Player.ws:5851`, `ShouldEnableCombatMusic`; threat query6597; G `engine/sound.ws:156`, `SoundGameStateChange` | Native classifier combines threats/force/finishers; do not replace it with one boolean |
| Combat outro completion | C | G `engine/sound.ws:173`, `OnCombatFinished` precedes actual outro completion; W music WWU rule `{A79AC940-BEEA-48E2-81EA-BD307F4771D4}` at122504; measured report90 | No complete script completion callback established; must remain audio-side arbitration, not inferred from exploration State |
| Authored ownership | C | W `Switches/switches.wwu:434`, music_type `{2076AA35-8BFD-4069-A941-1D9625ADD8F0}`; W authored event `{52B7971D-0DD6-40FA-9275-8236C5EFC3B0}` at180 has three SetSwitch actions | Precise native ownership exists in Wwise; no complete script getter/interceptor established; world branch also contains authored exceptions |
| Dialogue/cinematic | A | G `game/scenes/scenePlayer.ws:127,189,237`, movie/blocking/cutscene paths; G `game/r4Game.ws:1329`, `IsDialogOrCutscenePlaying` | Useful conservative veto, not proof of which cue owns music; typo `OnEnterSate` is not callback-delivery evidence |
| Lifecycle/UI | A | G `engine/game.ws:19–28`, active/pause/stopped; G `game/r4Game.ws:834`, loading-screen completion | Need tested lifecycle epochs; engine time58 and game time82 have distinct meanings, pause/load elapsed behavior unproven |
| Quest facts | C | Explicit fact/event call sites cataloged | Per-fact interpretation is bespoke and potentially spoiler-sensitive; not a general musical-importance detector |
| Biome/vista | C | G `engine/environment.ws:39`, `AreaIsCold` is hardcoded region proxy; G `engine/world.ws:74`, navigation elevation | No general biome/vista/discovery signal established by this bounded search |

Bounded negatives: 44 installed engine `.ws` files contain no matching `GetMusicPosition|GetMusicState|OnMusicFinished|OnMusicEnded`, nor `GetBiome|OnVista|OnLandmarkDiscovered`. This is not proof that no native engine facility exists anywhere. Existing global `rain_intensity`, `wind_intensity` and ambient `time` RTPC definitions have zero ObjectRef uses in the inspected Music WWU. Their native feed/effective values remain untested; weather-sensitive Wwise behavior is plausible, not already available in this music graph.

The `.15` cooldown in G `engine/sound.ws:67` is a throttle, not a verified calling frequency. Likewise, an imported script sound-event API does not prove all engine/quest-authored sound events pass through a hook on that API. No exhaustive authored interception is proposed.

## Bounded model

**Observed inputs:** 24 approved files SHA-verified, PCM16/stereo/48kHz; mapped to ten source-recording keys. Same-recording excerpts share a composition key. Cross-recording arrangements/remixes may still be the same composition and need alias review before a full palette; this is not a completed musicological taxonomy.

Only three approved excerpts illustrate selection:

| Cue | Model duration | Source family | Demonstration role |
|---|---:|---|---|
| S04-a | 40.85s | native:263850977 | Punctuation, day/night, foot/horse |
| S04-b | 36.757333s | Same as S04-a | Alternative excerpt, cannot evade family cooldown |
| S16-2 | 71.175s | native:626459345 | Atmospheric, night/foot hypothesis |

Durations subtract only the standard 2s+3s audition wrapper; internal silence and baked tails remain. S04-a's engine derivation was separately demonstrated in report87; no new engine import of the other two occurred. User role notes/native night ancestry support exploring the atmospheric role; exact foot/night restrictions and weights are editorial simulation hypotheses, **not approved regional assignments or verified musical suitability**.

The decision stages in `sparse_context_policy.py` are:

1. Positive hard eligibility: known generic owner, reviewed selector, region/location, exploration, no scene/hostility/pause/load, supported activity/environment, confirmed completed outro. Unknown blocks.
2. Stable context and quiet/recovery floors. These prevent immediate starts but never compel a later one.
3. Suitable palette and hard excerpt/family cooldown, plus a softer last-family penalty. If nothing qualifies, stay quiet; no inappropriate fallback.
4. Continuous hazard: `P(start during interval) = 1 - exp(-integral(lambda(t) dt))`. One exponential timing budget is consumed by the integrated eligible rate, with separate seeded cue-choice RNG. Baseline ramps after quiet time; optional first-discovery/arrival/weather windows contribute the **maximum** active boost, not additive event spam.
5. Windows can expire unused. Duplicate IDs do not renew TTL or spend more RNG; remote/non-first discoveries are rejected. Opportunities during native veto/playback are not saved as a sticky backlog. Seen IDs/windows/history are bounded.
6. Commit one whole cue allocation. Window expiry does not cut the phrase. Native priority withdraws allocation; load generations discard stale inputs. Combat epochs require the matching simulated outro completion before recovery. Exploration alone cannot clear that gate.

Two experimental profiles contrast baseline rates1/900 and1/450 per second, opportunity boosts1/180 and1/100, 60s windows, 8s context stability, 30s quiet floor, 120s ramp, 420s excerpt gap, 240s family gap and45s post-outro recovery. These illustrate behavior; none is a default recommendation. Source events are normalized into synthetic inputs rather than pretending imported function names directly deliver this schema.

**Unimplemented contracts:** `native_owner`, reviewed-selector identity and actual `outro_end` are simulated oracle observations. Commit is assumed immediately accepted; completion uses cue duration, not a proved playback callback. Simulation interruption/pause withdraws the allocation; this does not demonstrate native pause/resume semantics, audio fades or baked-tail continuity. Actual combat/quest sound remains the responsibility of unchanged native routing. No new audio proof is claimed.

## Comparison and failure evidence

Six synthetic timelines cover an hour of stable exploration, optional events, native priority, missing outro acknowledgement, duplicate/boundary/load events and a limited palette. 200 seeds × six timelines × two profiles × two approaches = **4,800 runs**. The randomized control retains the same hard native vetoes, but uses constant hazard/uniform cue selection without repeat/suitability policy.

| Profile / approach | Mean starts per trace | Mean allocated fraction | Zero-start traces /1200 | Recent family repeats | Editorial mismatches | Expired windows |
|---|---:|---:|---:|---:|---:|---:|
| Restrained randomized | 2.111 | 4.48% | 309 | 336 | 540 | 0 |
| Restrained contextual | 1.438 | 2.87% | 388 | 0 | 0 | 1257 |
| Contrast randomized | 3.753 | 8.07% | 179 | 1015 | 974 | 0 |
| Contrast contextual | 2.363 | 4.75% | 254 | 0 | 0 | 1083 |

Different rate budgets mean this is **not an equal-rate superiority experiment**. Zero repeats/mismatches demonstrate enforced constraints, not learned accuracy, natural musical placement or subjective quality. Allocation includes internal silence/tails and is not measured audible duty. Interruptions still occur when native priority arrives, as intended (restrained contextual131, contrast237 across1200 runs each).

Stable one-hour exploration averages3.29/5.28 starts under restrained/contrast; median longest no-Sparse gaps are approximately27/18 minutes. Long silence remains possible, not forcibly repaired. Missing-outro traces deliberately stay blocked:177/200 restrained and160/200 contrast traces produce no cue at all. This preserves priority but exposes why a missing completion contract cannot be concealed with a timer. No-Sparse intervals can contain native combat/quest music; they are not necessarily silent gameplay.

Independent checks cover full allocations, no overlaps, natural-duration completion and no continuation across external native vetoes. Focused tests verify identical cue/start results at0.25s and1s polling, rate-CDF behavior on synthetic data, exact-timestamp native-veto precedence, stale epochs, duplicate completion, optional expiry, composition cooldown and bounded memory. All pass. The fixed public seed7 representatives were retained for review rather than selecting favorable runs.

## Practical architecture and next pilot

Wwise already has native music_type, game_state, location/day-night routing, synchronized transitions and musical endings. It remains the right playback authority. Its existing source graph does not establish richer discovery/location significance or cross-recording history. A thin script context adapter is therefore useful for optional windows and selection, rather than replacing native combat/story scoring. Existing weather RTPCs may reduce adapter work if their feed is later verified.

Proposed flow (interfaces still to prove):

```text
verified public context + filtered local opportunities
    -> eligibility / seeded hazard / palette / composition history
    -> expiring request with lifecycle identity
    -> reviewed generic-selector Wwise request/commit gate
         native music_type + game_state + complete outro veto
    -> accepted phrase -> native ending/baked tail -> quiet
```

Do not send a direct Play to a child and assume ancestor switch selection protects it: that can bypass selection arbitration. The request must be accepted only within the reviewed generic path, expire without backlog and remain cancellable at native priority. No such gateway or unchanged-Init compatibility is established by this simulation. Do not substitute `exploration == safe`, global Music muting, an estimated outro timer or a private `SoundGameStateChange` interceptor.

**Smallest next implementation pilot:** a log-only thin observer in the already visited region, after separate authorization. Read public region/day-night/logical sound State, observe a narrowly filtered first-discovery path, and log actual lifecycle/deduplication behavior. No audio setters, forced travel, custom saves or per-frame scanning. Initially report authored ownership/outro as unknown rather than fabricate them. Replay the captured trace through this model, then prove a source-scoped request/commit gate using the existing single S04-a Wwise fixture before allowing any audible controller request. S04-b and S16-2 remain illustrative alternatives, not an expansion mandate. This is a small integration test, not another regional-bank rebuild or full24 scheduler.

All24 approved audio hashes, ten retained release/source pins, report88 bank, five report90 source pins and original native Init remain exact. No game/Wwise process was launched. Existing v2 retail confirmation, later offline packages and authoring-only Sparse proofs retain their separate evidence levels. **Stop for review; no controller, bank or deployment follows automatically.**
