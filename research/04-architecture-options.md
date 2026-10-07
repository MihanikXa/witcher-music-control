# Architecture options and prototype recommendation

## Revised requirement and conclusion

Exploration/traversal, generic dialogue, and combat music need independent multipliers, initially 0%, 0%, and 100%. Explicitly authored quest/story music during dialogue **or gameplay** must retain a 100% multiplier. Cutscene/movie/music-only music must also retain a 100% multiplier. These multipliers must sit above the user's normal music setting and preserve authored fades and native movie/loading behavior.

**Observed fact:** gameplay context and music provenance are separate selectors. `game_state` represents exploration/dialogue/combat/cutscene context; `music_type` selects regional `world_music` versus `quests_and_cutscenes`. The detailed GUID-resolved trace is in [03-vanilla-music-path.md](03-vanilla-music-path.md), including exact local paths and line references.

**Inference:** a common Music-bus dialogue mute cannot satisfy the requirement. A state-only suppression copied from Only Story Music is also insufficient: six quest-branch containers use `game_state`, so blanking exploration/dialogue can deselect intentionally authored music. The strongest structural mix boundary is the regional `world_music` ancestor, with the quest branch left intact.

## Working matrix

| Music origin / context | Default multiplier | Signal / boundary | Confidence and limitation |
|---|---:|---|---|
| World music / exploration | 0% | `music_type=world_music`, exploration/focus/boat/underwater context | Structural boundary observed; traversal policy needs tests |
| World music / generic dialogue | 0% | world branch plus `dialog_scene` / `dialog_scene_night` | Can be the same media as exploration |
| World music / combat | 100% | world branch plus combat enum membership | Use vanilla music classifier; do not replace it with only `IsInCombat` |
| Quest/story music / dialogue or gameplay | 100% | `quests_and_cutscenes` branch, regardless of gameplay enum | Strong protection boundary; not proof of audible cue activity |
| Cutscene/movie/music-only | 100% | retain native routing; no additional attenuation | Movie has native Music-bus mute; preserve it |
| Quest-specific locations within world music | preserve if explicitly authored | container/event-specific evidence still needed | Branch naming is not a perfect author-intent classification |
| Gwent / bard / diegetic | policy unresolved | Gwent state; separate emitter paths | Do not silently treat as ordinary dialogue |

Evidence root for Wwise citations below: `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\`. Script citations use `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\`.

## A. Pure WitcherScript contextual mixer

**Mechanism:** observe gameplay sound-state changes and use only existing native script controls, with no audio-resource changes.

**Supporting evidence:** `engine/sound.ws:156-190` centrally maps an accepted enum transition to `SoundState("game_state", ...)`; `:78-93` exposes event, switch, parameter, save, and debug operations. Only Story Music demonstrates state-string filtering. `SoundEventScene` and `SoundEventQuest` dispatch separate events (`game/scenes/scene_functions.ws:6-18`, `game/quests/quest_function.ws:1893-1905`).

**Contexts it can distinguish:** the gameplay enum distinguishes ordinary blocking dialogue from cutscene/movie, but cannot distinguish generic and authored music when both play during dialogue. An event log can recognize requests by resolved switch targets; it cannot establish actual current playback without further native information.

**Compatibility/conflict risk:** a local context logger could have a small footprint if wrapping is supported. A full engine-script replacement has high merge risk. Manipulating the global game state affects six authored quest selectors. Applying `menu_volume_music` globally would attenuate both branches.

**Complexity:** low for diagnostics; unresolved for a complete mixer. No existing script-visible authored-cue-active getter or generic-only volume control was verified.

**Failure modes:** authored cues muted during dialogue; state-dependent quest cues deselected; last-event flags stale after silent cues, cue completion, root stops, native dispatch, or save replay. Prefixes misclassify return/location events.

**Unresolved questions:** local wrapper support for private/imported sound methods; complete event interception; availability of a generic-only native parameter or a playback query. A pure script solution is not established for the revised requirement.

## B. Audio/Wwise-resource approach

**Mechanism:** leave both selectors unchanged. Apply configurable gain to the eight regional `world_music` ancestors through a container-level RTPC or a correctly routed dedicated generic-music bus. Use gameplay state only inside that branch to select exploration/dialogue/combat gains. Leave `quests_and_cutscenes` at multiplier 100%.

**Supporting evidence:** `Switches/switches.wwu:434-439` supplies the music-type split; prologue root entries at `Interactive Music Hierarchy/music.wwu:139843-139887` select sibling world/quest branches. An XML-wide GUID audit resolves 1,630 world AudioNode entries within the world branch and 734 quest entries within the quest branch. The generic prologue and NML selectors map dialogue and exploration to the same playlist (`:124764-124835`, `:269387-269440`). The existing Music bus at `Master-Mixer Hierarchy/Default Work Unit.wwu:9136-9328` has state volumes and the user-volume RTPC.

**Contexts it can distinguish:** the structural split protects quest cues during any gameplay context, including the six state-dependent quest containers. It can independently attenuate generic dialogue and exploration without listing individual media. It cannot automatically decide author intent for special quest/location music routed under world music.

**Compatibility/conflict risk:** resource generation/packaging may conflict with other audio mods. Container-level gain avoids rerouting buses but still changes bank content; a new bus requires explicit correct output overrides. Neither path has been built or verified.

**Complexity:** medium to high. Identify a minimal resource delta, validate inherited gain and transitions, and establish compatible deployment without replacing audio media.

**Failure modes:** modifying the common Music bus; changing root state mappings; overwriting user volume; incorrect output inheritance; generic gain applied to authored cue crossfades; omitted regional roots; stale or overly broad bank/cache replacements.

**Unresolved questions:** minimal bank/init/cache footprint; whether state volume properties suffice for future sliders or a new parameter is necessary; exceptional world-branch quest music; exact movie/main-menu routing. Existing `Master Audio Bus` references inside children must not be mistaken for enabled bus overrides.

## C. Hybrid approach

**Mechanism:** a small script hook supplies contextual gain to a Wwise parameter attached **only** within the world branches. Vanilla events continue selecting quest/cutscene cues. The script does not need an authored-cue-active boolean to protect the quest branch. Keep authored quest gains at 100% and do not blank gameplay-state strings.

**Supporting evidence:** native `SoundGlobalParameter(parameterName, value, optional duration)` exists (`engine/sound.ws:82`). FMC calls custom parameters from local menu wrappers (`C:\Dev\witcher-music-control\reference\fmc-audio-remaster\mods\modFMCAudioRemaster\content\scripts\local\FMCAudio.ws:15-17,151-164`). Current Wwise has the required world/quest topology, but FMC's binaries do not establish that its dialogue parameter protects authored cues.

**Contexts it can distinguish:** exploration/dialogue/combat are classified by the existing sound state; branch placement supplies provenance. The authored conversation event can select exploration-named media, so keep provenance separate from track labels. Cutscene/movie/music-only receive no added attenuation, while retaining native fades/mutes.

**Compatibility/conflict risk:** smaller script scope than the full replacements, but resource conflicts remain until a minimal routing delta is verified. Local override support for the selected method remains unknown.

**Complexity:** medium to high, split into independent context diagnostics and resource gain validation. No UI is needed first.

**Failure modes:** wrong hook ordering; using combined dialogue/cutscene boolean as the whole classifier; gain leaking above the world ancestor; parameter not initialized after load; unsupported wrapper; confusing event request with playing music.

**Unresolved questions:** supported local hook; safe generated routing footprint; branch-level inheritance in runtime; author-intent exceptions within world music. No parameter name or new API should be assumed until authored and verified.

## Robustness of an authored-cue-active signal

`music_type=quests_cutscenes` is a real selected-branch signal. It is not equivalent to audible music: a selected cue can be silent, finished, faded, stopped, or unloaded. The inspected script exposes setters/events/debugging, not a getter for that switch or a current-segment/playing-ID/completion callback. Native `EnableMusicDebug` exists; the content of its output has not been observed.

A logger around the scene/quest helpers would cover those script requests only. The helpers do not establish coverage of native scene events, restoration, or other direct event calls. Reconstructing a cue-active boolean from prefixes or a fixed timer is therefore not recommended. For volume isolation, a structural branch multiplier is stronger than an unverified boolean.

## Recommended prototype #1 — diagnostic only

Recommend the hybrid architecture provisionally, with a **two-selector diagnostic investigation** first. The earlier state-only logger recommendation is insufficient for the stronger requirement.

1. Validate a minimal Remastered local hook for gameplay transitions and log the old/new sound enum and mapped Wwise state without changing them.
2. Exercise the existing native music-debug facility and determine whether it exposes regional root, `music_type`, quest/cue selectors, or current segment. Do not assume its output format.
3. Correlate gameplay-state transitions with event requests from the verified scene/quest dispatch paths. Resolve event targets to switch groups in the project data; do not use `mus_q*` or `mus_loc*` prefixes as an authoritative classifier.
4. Compare ordinary area dialogue, the explicit tavern conversation, and the six quest selectors that also depend on gameplay states. Record unknown native dispatch and save replay as unknown, not inactive.
5. Apply no volume changes, no sliders, and no bank edits in prototype #1.

The next gain experiment should attenuate a **generic branch**, never the global dialogue state or common Music bus. Test simultaneous source/destination crossfades, an authored conversation reusing exploration media, a state-dependent quest cue, and save/load restoration before extending it to all regions.

Acceptance criterion: generic dialogue at 0% leaves explicitly authored story cues at their normal authored/user-volume mix even while both share `dialog_scene`. Authored gameplay cues must also survive exploration at 0%. A recorded `dialog_scene` transition alone cannot establish either result.

## What would falsify this architecture?

- A resolved ordinary quest cue runs outside the protected quest branch and is attenuated by the proposed world gain.
- Child playback fails to inherit the proposed container gain, or an output override changes its scope.
- A world-to-quest crossfade keeps both voices subject to a global/script-only gain.
- A native music event changes provenance without any diagnostic coverage and the design relies on a script flag for protection.
- Save/load resets parameter state or restores an authored cue through an unobserved path.

These are future validation requirements. This task changed research reports only.
