# Wwise mixer construction proof

## Result and limits of proof

**Observed:** the current project is Wwise `v2023.1.19`, build `8928`, schema `119` (`L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\w3_audio.wproj:2`). The matching installed authoring tool is `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe`; its help banner independently confirms that version. The older environment-variable path is not the tool used for this investigation.

**Construction supported by the installed object definitions:** three RTPC-controlled Gain effects, each independently bypassed by vanilla `game_state`. Put them on a new ordinary Audio Bus below the existing Music bus, and route only the eight regional `world_music` children to that bus. This implements a state-selected gain without changing the script classifier or quest selectors.

**Not yet proven in-game:** generation, deployment, bypass transitions, and the actual zero endpoint. Nothing was authored, generated, installed, or played in this investigation. “Proof” here means a concrete construction supported by the matching authoring schema, plugin definitions, and current project topology; it is not a claim of completed runtime validation.

## Local evidence key

These aliases resolve to exact local files; all following line references use them:

| Alias | Absolute file |
|---|---|
| I | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Interactive Music Hierarchy\music.wwu` |
| B | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Master-Mixer Hierarchy\Default Work Unit.wwu` |
| S | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\States\global_states.wwu` |
| O | `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\WObjects\WObjects.xml` |
| X | `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\Schemas\ObjectDataSchema.119.xsd` |
| G | `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\Plugins\AkGain.xml` |
| WS | `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\engine\sound.ws` |

## Why three curves on Volume do not solve it

O:151-181 declares BusVolume and audio-node Volume RTPCs as **Additive**. A state value and RTPC contributions add in dB; attaching exploration, dialogue and combat curves to one Volume property would apply all three gains simultaneously. A static state offset cannot cancel an arbitrary inactive slider value.

The RTPC object's `ControlInput` permits GameParameter, MIDI and modulators, **not State or StateGroup** (O:6817-6844). State overrides are `CustomState` property/reference lists, without an RTPC ObjectLists element (X:2402-2413). Therefore this project/schema does not establish a different RTPC curve or different RTPC binding per State. State mixing and RTPC mixing coexist; coexistence is not conditional routing. Audiokinetic's [property-combination documentation](https://www.audiokinetic.com/library/edge/?id=controlling_property_values_using_game_parameters&source=Help) describes additive and Boolean combination rules; the installed definitions, rather than a newer online version, establish the actual local property types.

## Exact proposed objects and edits

Names beginning `WMC_` below are **proposed new names**, not discovered vanilla identifiers. No GUIDs or runtime IDs have been allocated.

1. Create ordinary Audio Bus `Music/WMC_WorldMusic` under existing `Master Audio Bus/Immerse/Music` (B:9136-9328). Keep its Voice Volume and Bus Volume at 0 dB; do not copy the Music bus's -17 dB baseline or its user-volume curve onto the child.
2. Create three GameParameter objects, proposed `WMC_ExplorationGainDb`, `WMC_DialogueGainDb`, `WMC_CombatGainDb`. Use a dB domain, initially -96.3, -96.3, 0 respectively. A future settings adapter converts percentage to `20*log10(percent/100)`, bounded to the supported endpoint. Passing dB directly avoids pretending a straight line from 0% to 100% in dB is a linear-amplitude slider.
3. Insert three **non-rendered** Wwise Gain effect instances on the new bus. Proposed ShareSets `WMC_ExplorationGain`, `WMC_DialogueGain`, `WMC_CombatGain`. Each instance has base `FullBandGain=0`, `LFEGain=0`; attach identity dB RTPC curves to **both** properties from its corresponding GameParameter. G:4-36 identifies CompanyID 0 / PluginID 139, permits insertion on buses, declares both parameters Additive, and gives their supported range -96.3 to +24 dB. Controlling FullBandGain alone would leave LFE uncontrolled.
4. On each **EffectSlot**, add `StateInfo` for the existing `game_state` StateGroup, select its **Bypass** property, and author a complete Boolean truth table. Do not state-control the gain itself. X:1575-1590 explicitly permits `StateInfo` on EffectSlot; O:6903-6933 declares `Bypass`, Boolean RTPC support and engine property 48. The existing project already serializes EffectSlot StateInfo referencing game_state (B:11285-11388), although those inspected custom-state entries are empty: that example proves storage, not an already configured gate. S:6 defines the current StateGroup. Boolean bypass is a discrete gate, not a smooth volume interpolation.
5. At each regional `world_music` container in the table in report 06, set **OverrideOutput=True** and **OutputBus=WMC_WorldMusic**. Existing descendants do not enable their stored output overrides (report 03); the new explicit world override must be inherited. Leave the regional root and `quests_and_cutscenes` output routing untouched. Do not edit `music_type` entries, game_state selection entries, music transitions, sources or media.

Vanilla already uses Gain: B:13417-13464 contains a Gain instance with State-controlled FullBandGain. `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Actor-Mixer Hierarchy\generic.wwu:60688` contains another. The current generated `r4data\soundbanks\Pc\Init.bnk` INIT chunk includes plugin name `AkGain` and encoded plugin ID `0x008b0003`; the installed game cache contains identical Init bytes (report 06). This is stronger evidence for availability than merely finding an authoring DLL, but registration and processing of the proposed instances still require runtime confirmation.

## Complete gate policy

`False` means **process this effect**, `True` means bypass it. Explicitly define every current state, including None; do not rely on inherited checkbox defaults.

| Existing game_state values | Exploration slot | Dialogue slot | Combat slot |
|---|---:|---:|---:|
| exploration, exploration_night, focus_exploration, focus_exploration_night, underwater, underwater_focus, boat | False | True | True |
| dialog_scene, dialog_scene_night | True | False | True |
| combat, combat_monster_hunt, underwater_combat, underwater_combat_focus, focus_combat | True | True | False |
| cutscene, movie, music_only | True | True | True |
| None, quest, minigames, death, interior, pause, menu, gwent | True | True | True |

All names are observed in S/game_state. WS:327-376 maps script enums to most of them; `focus_combat`, `quest`, `interior`, `menu` also exist in the project but are not all emitted by that mapping. Traversal grouping and fail-open treatment of unclassified states are **proposed policy**, not vanilla author intent. No additional mixer state is needed. Native Music-bus movie mute and menu/pause attenuation remain intact (B:9173-9206).

For slot i, let `b_i(state)` be the Boolean bypass and `g_i` the slider gain. Added world gain is `sum((1-b_i)*g_i)` in dB. The table makes at most one term nonzero. Quest gain is always zero additional dB because its voices never enter this bus. During a world-to-quest crossfade, the world contribution receives its gain and the quest contribution does not; testing must confirm inherited routing during overlapping playback.

Normal user volume remains the existing `menu_volume_music` RTPC on the Music bus (B:9291-9324, endpoints 0/-200 dB and 100/0 dB). Both paths still feed that ancestor. Do not set that parameter from our settings script.

## Alternative constructions assessed

| Mechanism | Exact change | Assessment |
|---|---|---|
| State-specific RTPC curves | RTPC ControlInput or CustomState binding | **Not established/supported by the inspected schema.** State properties add values; they do not select curves. |
| State offsets + three volume curves | world Volume StateInfo + three Volume RTPCs | **Fails independence:** all RTPC gains add. |
| Three gated effects directly on world containers | Eight world MusicSwitchContainer Effects lists, three Gain EffectSlots each, same Bypass truth table | **Authorable alternative.** No new bus/rerouting, but 24 slots and effect inheritance/child OverrideEffect must be audited. Does not remove Init/new-parameter or eight-bank changes. Prefer bus for one shared gate and easier exception bypass. |
| Three serial gain buses | Create three ordinary buses below Music, each with one Gain and State-controlled Bypass | **Authorable alternative.** Same gate, more buses, same bank footprint. Individual slots on one bus are simpler. |
| State-specific nested music wrappers | Create context MusicSwitchContainer/playlist gain ancestors and change MultiSwitchEntry AudioNode targets | **Possible redesign, not a small transparent mixer.** A node has one hierarchy parent, while existing dialogue/exploration frequently select the same playlist. Duplicating/reparenting and transition identity changes must be solved; not validated here. |
| Auxiliary bus send | Add an AuxBus and sends to world nodes | **Not an exclusive dry-path multiplier:** an additional send does not by itself mute/reroute the original Music path. Would still require existing-bank changes. |
| One world-only RTPC supplied by state hook | World Volume RTPC + hook selects one saved slider | **Fallback without Gain plugin gates.** Technically simpler audio property, but requires the unwanted hook and safe ordering/loading. Not necessary if the proven authoring gate works at runtime. |
| Fixed state volume only | world container StateInfo/Volume -200 dB for E/D, 0 for combat/cinematic | **Simplest hard-coded attenuation test**, but does not prove three independent sliders. Do not confuse this with the final mechanism. |

## State hook reassessment

**Inference:** no `SoundGameStateChange` interception is required for the proposed final mechanism. Vanilla supplies the StateGroup (WS:156-190), and events supply music_type. Our settings adapter only calls the existing `SoundGlobalParameter(name,value,optional duration)` (WS:82) for three newly authored parameters; FMC provides a local menu-wrapper example (report 01). GameParameter defaults let the resource-only prototype run without any new script. Later settings persistence/reapplication is necessary, but is not a state classifier.

A hook is needed only if runtime disproves State-driven bypass, if we choose the single-RTPC fallback, or if a new classification requirement needs information not already expressed in Wwise. A script hook cannot magically distinguish author's intent in exceptional world locations. Route protected containers around the new bus instead of inventing a last-quest-event flag.

## Remaining proof obligations and smallest experiment

Recommend **one-region Wwise/deployment proof, no UI and no WitcherScript hook**. In an isolated future project copy, author the bus, three parameters/defaults and three gates, and reroute only prologue/world_music. Generate only music_prologue plus required Init; package the changed bank entries as described in report 06. Use authoring Soundcaster State/parameter controls to sweep each parameter while changing only the corresponding state. Use native music debugging in-game if available; do not add a logger interception solely to drive gain.

Test unequal values, for example -12/-24/-6 dB, as well as initial mute/mute/unity defaults. An inactive parameter must produce no level change; a quest cue must show no change for **any** parameter. Test the authored q001 tavern conversation which reuses exploration media, world/quest overlapping transitions, day/night dialogue, traversal variants, combat, cutscene, movie and save/load. These falsify gate isolation, output inheritance, parameter restoration and packaging assumptions separately.

The Gain definition's -96.3 dB minimum is a finite authored endpoint. Exact digital silence or a native minus-infinity sentinel is **not demonstrated by these XML definitions**. Verify the plugin's actual zero behavior in the future experiment; do not silently equate a finite attenuation floor with mathematical zero. Boolean bypass also needs a click/transition test. If smooth state fades are required and bypass is abrupt, the hook fallback or a different validated gain stage may be warranted; changing vanilla StateGroup transition times globally would affect unrelated audio.

The 12 concrete quest-resource cases and wider review set in report 07 prevent claiming that an unqualified world-only mute preserves every intentionally scored location. The mixer construction is implementable at the authoring-data level; the final preservation policy remains a separate routing decision.
