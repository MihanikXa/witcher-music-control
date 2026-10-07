# Architecture options and prototype recommendation

## Evidence boundary

The current Remastered script already classifies several contexts and sends a Wwise `game_state`. The current REDkit Wwise project has state-specific Music-bus volume overrides, but no exposed vanilla contextual volume parameters. The two reference styles therefore demonstrate different layers:

- Only Story Music and Less Is More alter `engine/sound.ws` state-to-string behaviour.
- FMC uses local menu wrappers plus custom Wwise resources and global parameters.

Claims below are labelled by evidence. “Observed” means directly present in the cited local files; “inference” connects those facts; “hypothesis” requires runtime/compiler testing.

## Working state matrix

| Context | Desired prototype volume | Observed engine signal | Reference evidence | Confidence / open problem |
|---|---:|---|---|---|
| Exploration / traversal | 0% | `ESGS_Exploration` / `ESGS_ExplorationNight` from `CollectSoundStates` | Only Story Music exploration variant; Less Is More | High signal confidence; volume routing still unverified |
| Ordinary dialogue | 0% | `ESGS_Dialog` / `ESGS_DialogNight` from `CStoryScenePlayer.Blocking` | Only Story Music exploration variant; vanilla scene player | High for authored blocking scenes; player-control dialogue needs trace |
| Cinematic / story | 100% | `ESGS_Cutscene`, `ESGS_Movie`, or `ESGS_MusicOnly` | vanilla scene player and Wwise state group | High state separation; authored quest music outside scenes remains open |
| Combat | 100% | `ShouldEnableCombatMusic()` → combat enum | vanilla `r4Player.ws`; Only Story Music combat variant | High classifier evidence; scripted combat precedence needs trace |
| Quest gameplay / scripted sequence | TBD | explicit `EnterGameState(soundState)` is available | `quest_function.ws:4521-4524` | Low until representative quests are traced |
| Tavern / bard / diegetic | TBD | emitter/entity and bank path, not necessarily global state | Less Is More inn/bard scan; REDkit music emitters | Low; must keep separate from global interactive music |
| Gwent | TBD | explicit `ESGS_Gwent` | `gwintGameMenu.ws`, `deckBuilderMenu.ws`, Wwise `game_state` | High signal confidence; desired policy not chosen |

## A. Pure WitcherScript contextual mixer

**Mechanism:** observe accepted `ESoundGameState` transitions at the central sound-system path and apply hard-coded or configurable values through existing script calls, while leaving banks/assets unchanged. Candidate observation points are `SoundGameStateChange`, `EnterGameState`, and `GameStateToString` in `engine/sound.ws`.

**Supporting evidence:** `SoundGameStateChange` is the central function that calls `SoundState("game_state", ...)` (`C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\engine\sound.ws:156-190`). The enum already separates exploration, combat, dialog, cutscene, movie, Gwent, and underwater states (`sound.ws:6-29`). FMC shows that `SoundGlobalParameter` calls are available from local script (`reference/fmc-audio-remaster/mods/modFMCAudioRemaster/content/scripts/local/FMCAudio.ws:15-18`).

**Contexts:** strong for the existing global states; weaker for diegetic tavern/bard music, quest-specific cues, and dialogue that does not create a blocking scene state.

**Compatibility/conflict risk:** low only if a narrow local override is supported. High if it requires replacing `engine/sound.ws`, as in Only Story Music and Less Is More. Calling a nonexistent global parameter would fail silently or do nothing; vanilla does not expose contextual volume parameters.

**Complexity:** low for a logger; medium for a working mixer; high if a new native/Wwise parameter is assumed without resource support.

**Failure modes:** misclassifying threat as combat; suppressing authored quest music; losing state after load/black screen; overriding movie/music-only transitions; changing a global state without changing the Music-bus volume.

**Unresolved:** whether Remastered scope/local syntax can wrap the private transition method; whether an existing native global parameter can be repurposed safely; whether `SoundGlobalParameter` affects the vanilla Music bus without a custom bank.

## B. Audio/Wwise-resource approach

**Mechanism:** add or edit Wwise state/bus/RTPC routing so the existing `game_state` values drive contextual volume, or add global parameters such as FMC's `fmc_explorationMusic`, `fmc_combatMusic`, and `fmc_dialogueMusic`.

**Supporting evidence:** `States/global_states.wwu` defines the state group and transitions; `Master-Mixer Hierarchy/Default Work Unit.wwu:9136-9328` shows the Music bus with state-specific volume overrides and `menu_volume_music` RTPC; FMC ships a replacement `Init.bnk` and `soundspc.cache` and sets its custom global parameters from script.

**Contexts:** strong for every context represented by `game_state`; can preserve cinematic overrides and support independent multipliers. It still cannot automatically classify a diegetic bard or authored quest cue unless those resources/events are separately routed.

**Compatibility/conflict risk:** high. A custom `Init.bnk`/cache or Wwise project change can conflict with other audio mods and game updates. The reference FMC replacement demonstrates the footprint.

**Complexity:** high: resource authoring, bank/cache generation, packaging, and version compatibility are required.

**Failure modes:** wrong bank/platform, missing IDs, stale cache, state transitions with no corresponding routing, volume affecting dialogue/ambience through an incorrectly placed bus, or conflict with another Init/bank replacement.

**Unresolved:** whether the available REDkit can safely build only the needed routing; whether the user's target install accepts a minimal bank/cache delta; exact runtime semantics of the custom FMC parameters.

## C. Hybrid approach

**Mechanism:** use a narrow WitcherScript hook only to observe/normalize context and set a small number of Wwise global parameters; keep state selection and smooth volume curves in Wwise. Preserve explicit `cutscene`, `movie`, `music_only`, Gwent, and quest states as higher-priority cases.

**Supporting evidence:** the script already provides the context signal and event boundary; Wwise already provides state transitions and state-specific bus volumes; FMC proves the script-to-global-parameter call pattern and resource-backed parameter names.

**Contexts:** best coverage for exploration, combat, ordinary dialogue, and cinematic overrides; can explicitly log and later handle Gwent and quest states. Diegetic music still needs a separate policy.

**Compatibility/conflict risk:** medium. It avoids replacing the full sound script but still needs a compatible Wwise resource mechanism. If an existing parameter cannot be reused, the resource footprint becomes closer to option B.

**Complexity:** medium to high, but separable: first validate state detection and hook scope, then validate one parameter and one bus route.

**Failure modes:** incorrect priority between script parameters and Wwise states; stale parameter values after loading; a parameter routed to the wrong bus; local override not accepted for the sound-system class.

**Unresolved:** the exact supported Remastered override syntax for `CScriptSoundSystem`; whether a parameter can be added without replacing `Init.bnk`; and which Wwise bus receives only interactive music rather than diegetic emitters.

## Recommendation

Recommend option C as the target architecture, but prototype only its diagnostic half first. Prototype #1 should be a no-UI, no-bank, no-asset diagnostic logger that observes every sound-state transition at the narrowest hook that the Remastered compiler accepts. It should record the enum, mapped Wwise string, previous/current state, whether the state is one of the combat states, whether the game reports a combined dialog/cutscene flag, and the reason for explicit transitions where available. It should not change volume yet.

The prototype test matrix must cover: free exploration day/night; combat start/end and monster hunt; ordinary blocking dialogue with and without player control; scripted walks; authored cutscene; movie/loading screen; combat entered during a quest scene; Gwent; tavern/bard music; pause/menu; black screen; and save/load while a special state is active. The expected result is a transition log that shows whether the global state is stable and whether ordinary dialogue and cinematics are reliably separated.

Only after that log is stable should prototype #2 apply the requested hard-coded levels (exploration/dialogue 0%, combat/cinematic 100%) through the smallest proven routing mechanism. UI sliders and broader special-case support should wait until the signal and Wwise routing are demonstrated.

The biggest unresolved implementation issue is not state discovery; it is whether a Remastered-compatible local/scope override can observe `CScriptSoundSystem.SoundGameStateChange` without replacing the whole engine sound script, and whether the vanilla bank exposes a safe contextual volume parameter. The reports intentionally stop before implementing or altering any source.
