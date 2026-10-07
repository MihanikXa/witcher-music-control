# Architecture options and revised prototype recommendation

## Current conclusion

Use vanilla game_state and music_type unchanged. The concrete proposed final mixer is a new world-only child bus under Music with **three RTPC-controlled Gain effects, each State-gated by its own EffectSlot.Bypass**. An eventual settings adapter writes three GameParameters; it does not intercept SoundGameStateChange. The matching Wwise 2023.1.19 schema and plugin definitions support this construction. Runtime processing, the zero endpoint and deployment still require the deferred prototype.

Detailed proofs and limitations: [05-wwise-mixer-proof.md](05-wwise-mixer-proof.md), [06-resource-footprint.md](06-resource-footprint.md), [07-world-music-exceptions.md](07-world-music-exceptions.md). This supersedes the earlier recommendation to start by implementing a state-hook logger.

Target additional gains: exploration/traversal 0%, generic dialogue 0%, combat 100%, explicitly authored quest/story and cutscene/movie/music_only 100%. The existing user Music volume and native fades/mutes remain master controls. “100% story” means no additional attenuation; it does not override a vanilla movie mute.

**Observed:** eight regional roots select world_music and quests_and_cutscenes siblings through music_type. Six nested quest containers also select by game_state, so blanking exploration/dialogue state strings can deselect authored cues. **Inference:** neither a common Music-bus mute nor Only Story Music's state suppression meets the stronger preservation requirement. Placement below the provenance split protects the quest branch even during dialogue, gameplay and crossfades.

## Evidence anchors

- `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\engine\sound.ws:156-190`: accepted state transition sends SoundState("game_state", mappedName); :327-376 maps enum names; :82 declares native SoundGlobalParameter.
- `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Switches\switches.wwu:434-439`: music_type/world_music/quests_cutscenes.
- `...\Interactive Music Hierarchy\music.wwu:139843-139887` under that same audio root: prologue branch selection. World declaration anchors for all regions and verified bank IDs are in report 06.
- `...\Master-Mixer Hierarchy\Default Work Unit.wwu:9136-9328`: existing Music bus, native State volumes and menu_volume_music curve. :13417-13464 shows vanilla Gain usage.
- `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\Schemas\ObjectDataSchema.119.xsd:1575-1590`: EffectSlot supports StateInfo; `...\Data\WObjects\WObjects.xml:6922-6933`: Boolean Bypass. `...\x64\Release\bin\Plugins\AkGain.xml:4-36`: bus insertion and separate FullBandGain/LFEGain RTPC properties.
- `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\w3_audio.wproj:2` and installed WwiseConsole help: matching v2023.1.19/build8928. The former environment-path uncertainty is resolved.

## A. Pure WitcherScript contextual mixer

**Mechanism:** use existing script-native state/event/parameter controls without audio-resource changes.

**Evidence/context coverage:** sound.ws exposes the gameplay classifier and SoundGlobalParameter, but no verified world-only volume parameter or authored-audible-cue getter. Scene and quest helpers emit sound events (`game/scenes/scene_functions.ws:6-18`, `game/quests/quest_function.ws:1893-1905`, under the installed script root above). The gameplay enum can distinguish blocking dialogue from cutscene/movie; it cannot identify music provenance during the same dialogue state.

**Compatibility/complexity:** a small local observer may be inexpensive; a complete mixer is not established. Full vanilla engine-script replacement has merge risk. Manipulating menu_volume_music or game_state also affects authored music.

**Failure modes/unresolved questions:** common-bus attenuation leaks to story; blanked states deselect state-dependent quests; reconstructed last-event flags become stale on completion, silence, stop, unload or save replay. No API was discovered that removes those problems. This is not recommended for the final separation.

## B. Audio/Wwise mixer with hard-coded defaults

**Mechanism:** create WMC_WorldMusic below Music, three Gain effects/three GameParameters, gate individual effects using existing game_state, and explicitly route world children to it. Names are proposed, not vanilla symbols. Defaults supply mute/mute/unity without script. Protect selected world exceptions through narrower output overrides to Music.

**Evidence:** report 05 proves the concrete object/property construction. Three curves on ordinary Volume would all add; static State offsets cannot cancel arbitrary slider values. The Boolean gate is the required combination mechanism.

**Context coverage:** E/D/combat independently; cutscene/movie/music_only and unclassified states receive no added gain. quests_and_cutscenes never enters the bus. Some special locations under world require an exception policy; track provenance is not an author-intent signal.

**Compatibility/complexity:** medium authoring complexity, substantial binary conflict scope. Final rollout changes Init plus eight complete regional bank entries, carried in a mod cache; no WAV edits intended. The current cache payloads match the REDkit banks byte for byte (report 06). Other Init or regional-bank modifications need a compatible combined build.

**Failure modes/unresolved questions:** wrong bus override/inheritance; omitted regions; abrupt Boolean bypass; finite gain floor mistaken for digital silence; regeneration alters unrelated media/structures; cache precedence/bootstrap Init mismatch; overbroad exemption also removes combat control. Selective Wwise generation is supported; minimal REDkit cache packaging is not yet demonstrated.

## C. Wwise mixer plus settings-only WitcherScript adapter

**Mechanism:** architecture B plus a small settings adapter writing the three proposed global dB parameters through SoundGlobalParameter. Vanilla supplies all state transitions and music_type selections. No SoundGameStateChange interception, no per-frame polling, no authored-cue-active flag.

**Evidence:** native setter sound.ws:82; FMC's `C:\Dev\witcher-music-control\reference\fmc-audio-remaster\mods\modFMCAudioRemaster\content\scripts\local\FMCAudio.ws:15-17,151-164,327-338` demonstrates local menu-wrapper parameter writes. Its resource banks are older-format and do not prove our routing or deployment.

**Context coverage:** identical to B. Slider changes update effect parameters even when their slots are bypassed, so values are ready when that context becomes active. Stored defaults handle the first resource test.

**Compatibility/complexity:** preferred eventual architecture. Small settings/persistence script, same audio conflict footprint as B. Local settings callback support and save/load initialization must be verified when implementation is authorized.

**Failure modes/unresolved questions:** missing initialization/reapplication, wrong units, LFE omitted, parameter names not matching generated definitions, settings adapter accidentally changing master volume. A state hook is only a fallback if State-gated effect bypass fails runtime validation or another context needs a signal absent from Wwise.

## Exception policy and preservation limit

The 106 world location selectors include 24 quest-labelled names. Report 07 audits 55 candidates/comparators: 12 with concrete quest-resource evidence (7 proven shared authored-cue sources, 5 further associated cases), 11 whose noncombat sources are verified zero PCM, and 32 other location/theme candidates. These are structural counts, not an exact count of author-intended story moments.

The strongest counterexamples include Yennefer's room selecting a love-theme source also used by actual quest playlists, Spiral castle selecting q101 dialogue-cue media, and tournament_quest containing quest variants alongside generic variants. Conversely, several q604/q605/q603 locations select silence despite plausible playlist names.

**Inference:** a world-only mixer can satisfy branch isolation, but cannot guarantee preservation of every intentionally scored world location without justified exceptions. Exempt a noncombat playlist through an output override to Music when appropriate; exempting its entire location would also bypass independent combat control. This is container-level policy, not a primary track list. A state hook adds no missing intent information.

## Proposed final signal/routing graph

```text
vanilla sound classifier -> game_state -----------------> 3 EffectSlot.Bypass gates
vanilla sound events ----> music_type -> regional MusicSwitchContainer
                                         |
                    +--------------------+--------------------+
                    |                                         |
                 world_music                         quests_and_cutscenes
                    |                                         |
           ordinary descendants                      existing inherited Music
                    |
            WMC_WorldMusic [new child of Music]
              Gain exploration <- exploration dB parameter
              Gain dialogue    <- dialogue dB parameter
              Gain combat      <- combat dB parameter
                    |
                Music <- existing menu_volume_music/master mix
                    |
              Immerse / Master Audio Bus

protected world noncombat containers -> explicit output override -> Music
future settings adapter -> 3 global dB parameters; no state hook
```

Only one effect is processed in exploration/dialogue/combat respectively; all are bypassed for cutscene/movie/music_only and fail-open special states. Native parent volumes/fades remain. During a world/quest crossfade only world voices take the new gain.

## Prototype #1: one-region mixer and deployment proof

**Recommendation:** a resource-only prologue experiment proving state-gated gain selection and minimal packaging, with no UI, no new source script and no state interception. This advances beyond the earlier state logger because vanilla already carries the necessary state.

Future authoring changes in an isolated copy:

1. Master-Mixer work unit: new child bus with three embedded Gain instances/EffectSlots and complete existing-state Bypass tables.
2. New Game Parameters work unit: three dB parameters/defaults, initially mute/mute/unity.
3. Interactive Music music work unit: only prologue/world_music OverrideOutput/OutputBus change.

Future logical generated minimum: **Init.bnk and music_prologue.bnk**. Candidate install footprint: **one matching loose bootstrap Init.bnk plus one mod soundspc.cache containing the changed prologue and matching Init entries**. Cache packaging/loader behavior remains to be proved; no claim that loose regional banks are supported. No Events, Switches, States, source WAV, quest-branch or SoundBank-inclusion edits are needed for this experiment. A full rollout would extend the same routing to the other seven regional banks.

Acceptance: independently vary unequal gains in authoring; inactive sliders have no effect; q001 authored tavern conversation survives exploration/dialogue suppression, including crossfade overlap; combat is independently adjustable; cinematic states add no gain; master Music volume still works; startup/save/load are consistent. Observe/debug rather than adding a hook to drive the mix. Verify actual zero and bypass transitions before committing to final smoothing behavior.

Nothing was implemented or generated. Only research reports were changed.
