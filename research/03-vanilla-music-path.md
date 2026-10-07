# Current Remastered vanilla music path

## Authoritative files inspected

The installed Remastered source is under `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts`. The matching REDkit source is under `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\scripts`. The two current `engine/sound.ws` files have the same SHA-256 (`534E267195F17F3BDDC4DDD2BE3EA1F795C1BF57264B338B90B0527B03E43AFC`). The partial depot was not needed for these conclusions.

## Script path

`engine/sound.ws` defines `ESoundGameState` and `CScriptSoundSystem` (`C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\engine\sound.ws:6-29,41-93`). The system imports the native Wwise-facing operations `SoundState`, `SoundSwitch`, `SoundEvent`, `SoundParameter`, `SoundGlobalParameter`, `SoundMusicEvent`, and `SoundEnableMusicEvents` (`sound.ws:78-88`).

The normal transition path is:

1. A caller enters or leaves an enum state with `EnterGameState` / `LeaveGameState` (`sound.ws:205-233`).
2. `SoundGameStateChange` updates `currentGameState`, handles combat start/finish callbacks, then calls `SoundState("game_state", GameStateToString(gameState))` (`sound.ws:156-190`).
3. `GameStateToString` maps the enum to the Wwise state name (`sound.ws:327-376`).
4. Default exploration/combat/underwater states are periodically selected by `exec function CollectSoundStates`, which throttles at `stateCheckCooldown`, gives explicit states priority, and selects combat or exploration from player signals (`sound.ws:557-624`). The source search found no WitcherScript caller for this `exec` function; its engine/exec integration remains unresolved.

Area music is a separate event path. `InitializeAreaMusic` sends `stop_music` and then selects `play_music_nomansgrad`, `play_music_skellige`, `play_music_kaer_morhen`, `play_music_prologue`, `play_music_wyzima_castle`, `play_music_misty_island`, `play_music_spiral`, or `play_music_toussaint` by world area (`sound.ws:279-325`). The REDkit event work unit contains corresponding `play_music_*` events and many authored `mus_q...`, `mus_cs...`, and `mus_loc...` events (`L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Events\music.wwu:216-251,252-382` and later quest/cutscene event folders). This is evidence that authored music cues and global state routing are separate layers.

## Concrete state signals

### Exploration and combat

`CollectSoundStates` calls `thePlayer.ShouldEnableCombatMusic()` and, when true, selects `ESGS_Combat` or `ESGS_CombatMonsterHunt`; otherwise it selects day/night exploration if the player is not threatened (`sound.ws:590-624`). `CR4Player.ShouldEnableCombatMusic` returns true for forced combat mode, native `IsInCombat()`, certain threatened ranged-hostile cases, existing threat plus hostile/alert conditions, finishable enemies, or a finisher (`game/player/r4Player.ws:5847-5876`). The combat-state membership used by the sound system is explicit: underwater combat, combat, monster-hunt combat, and focus-underwater combat (`r4Player.ws:8399-8419`).

**Observed fact:** this is the concrete music classifier. `IsInCombat()` alone is not the complete rule.

### Dialogue, scenes, cutscenes, and movies

`CStoryScenePlayer` pushes `Blocking`, `Cutscene`, and `Movie` states. `Blocking.OnEnterState` enters `ESGS_Dialog` or `ESGS_DialogNight`; `Cutscene.OnEnterState` enters `ESGS_Cutscene`; `Movie` enters `ESGS_Movie` (`game/scenes/scenePlayer.ws:189-218,237-261`). Movie start also enters `ESGS_MusicOnly` for a final board or `ESGS_Movie` otherwise (`scenePlayer.ws:127-138`), and movie end returns to day/night dialogue unless the state is music-only (`scenePlayer.ws:141-155`).

The game-level boolean `IsDialogOrCutscenePlaying` intentionally combines dialogue and cutscene (`game/r4Game.ws:1238-1334`). Therefore it is not sufficient for category-specific mixing, while the scene-player state and `CScriptSoundSystem` enum are separate. Ordinary authored blocking scenes and cutscene/movie phases are distinguishable at this script layer. Dialogue while the player retains control, scripted walks, and scenes that use quest-level state calls still require in-game trace validation.

### Explicit special states

Gwent enters/leaves `ESGS_Gwent` from `gwintGameMenu.ws` and `deckBuilderMenu.ws` (for example `game/gui/menus/gwintGameMenu.ws:98-101,134-137` and `deckBuilderMenu.ws:47-50,88-92`). A quest helper can enter an arbitrary `ESoundGameState` (`game/quests/quest_function.ws:4521-4524`). This means quest music can override the default classifier and is a known ambiguity.

Loading-screen initialization enters `ESGS_Movie` when a loading video is playing, and post-load leaves it and sends `system_resume` (`game/r4Game.ws:722-727,836-847`). Black-screen handlers temporarily use `ESGS_MusicOnly` (`engine/sound.ws:95-114`). Paused/constrained and stopped/resumed paths are handled in `CollectSoundStates` (`sound.ws:561-580,583-586`).

## Wwise evidence

The current REDkit project provides text Wwise work units under `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`:

- `States/global_states.wwu:1-32` defines state group `game_state` with `combat`, `combat_monster_hunt`, `exploration`, `exploration_night`, `dialog_scene`, `dialog_scene_night`, `cutscene`, `movie`, `music_only`, `gwent`, underwater/focus states, and others. There is no `story` state.
- `Game Parameters/music.wwu:1-24` defines `intensity`, `threat_rating`, and interactive-music parameters. `threat_rating` is the concrete existing game parameter used by `SoundParameter`/`SendThreatRating`; no exploration-volume, combat-volume, or dialogue-volume game parameter appears in this work unit.
- `Master-Mixer Hierarchy/Default Work Unit.wwu:9136-9328` contains the `Music` bus. Its `StateInfo` references `game_state`; the bus has explicit state overrides for `movie` (`BusVolume=-96`), `dialog_scene` and `dialog_scene_night` (`-1`), focus states (`-6`), and other state entries. The same bus has an RTPC named `menu_volume_music` controlling `Volume` (`:9291-9324`).
- `SoundBanks/music.wwu` lists area music banks such as `music_shared`, `music_prologue`, `music_nomansgrad`, `music_skellige`, and other region banks. This supports the script's area-event path but does not turn authored cue names into runtime categories.

**Inference:** Wwise receives a concrete coarse gameplay-context signal through `game_state` and supports state-specific bus volumes. Runtime classification reliability still needs tests. Context alone does not identify the origin of the music; see the separate `music_type` path below. Arbitrary independent contextual multipliers require either a suitable existing parameter or a resource-side addition. The vanilla project exposes `menu_volume_music`, but not a verified generic-only contextual volume mechanism.

## Answers to the investigation questions

1. **Normal gameplay music component:** `CScriptSoundSystem` controls the `game_state` Wwise state and emits area music events; Wwise's `Music` bus and music banks perform the resulting routing.
2. **Combat signal:** `CollectSoundStates` uses `CR4Player.ShouldEnableCombatMusic`, which combines native `IsInCombat`, threat, force-combat, hostile/alert, finishable-enemy, and finisher signals.
3. **Dialogue/scene signal:** `CStoryScenePlayer` enters `ESGS_Dialog`/`ESGS_DialogNight` for `Blocking` scenes; the state is sent through `SoundGameStateChange`.
4. **Ordinary dialogue vs authored cinematic:** yes at the scene-player/sound-state layer (`dialog_scene` vs `cutscene`/`movie`), although the general game boolean combines dialogue and cutscene.
5. **Story music runtime state:** no `story` enum or Wwise state was found. Only Story Music changes existing enum-to-string mappings; its effect is resource/state routing, not a new story state.
6. **Independent exploration/combat volume without replacing music assets:** the state layer can distinguish them, and Wwise can apply state-specific bus volumes. A script-only arbitrary multiplier is not proven by vanilla data because no contextual volume RTPC is exposed; FMC demonstrates the resource-backed approach.
7. **Independent generic dialogue volume:** a `dialog_scene` multiplier on the common Music bus is insufficient: it would also affect authored cues during dialogue. The follow-up trace below finds a structural `world_music` / `quests_and_cutscenes` separation suitable for applying generic-only multipliers. No existing vanilla parameter implementing that policy has been established.
8. **Cinematic/story override:** the scene player separates cutscene/movie phases, but authored story music can also play during an ordinary `dialog_scene` or exploration state. Preserve the authored branch independently of `game_state`; a cinematic-state exception alone is insufficient.
9. **Reusable mechanism:** `SoundState("game_state", ...)`, `SoundParameter`/`SoundGlobalParameter`, `SoundMusicEvent`, existing `game_state`/`mixing_state` groups, `threat_rating`, and `menu_volume_music` are all present. No vanilla contextual music-volume global parameter was found.
10. **Remastered scope/local overrides:** FMC proves local script wrappers work for `CR4IngameMenu`; the references do not prove a local wrapper for private `CScriptSoundSystem.SoundGameStateChange`. A full engine-file replacement works in the references but has high conflict risk. Compiler/runtime validation is required before choosing an override form.
11. **Narrowest stable hook:** `SoundGameStateChange` is a central hook for gameplay context, but does not observe music-branch selection. The narrowest structural mix boundary found is the regional `world_music` container below each `music_type` selector. Authored-event diagnostics additionally need the event/switch path; local override and native-event coverage remain unverified.
12. **Ambiguous cases:** gameplay dialogue with control and scripted walks may use blocking scene states but need trace confirmation; quest music can call `EnterGameState` directly; combat during a quest competes with explicit state priority; Gwent has an explicit state; tavern/bard music is also represented by diegetic emitter/bank assets and is not equivalent to global gameplay music; menus, loading videos, black screens, pause, and save/load transitions have separate states/resume paths.

## Follow-up: generic area music versus explicitly authored cues

This section supersedes any implication above that a dialogue/cutscene enum alone identifies the provenance of the music. The target now preserves explicitly authored quest/story music at a multiplier of 100% even during `dialog_scene` or exploration, while generic exploration/dialogue default to 0% and combat defaults to 100%. A multiplier of 100% means preserving the user's normal music setting and authored mix, not overriding the user's volume or the game's movie mute.

### Evidence paths and method

All Wwise paths in this section are relative to the exact read-only evidence root `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\`:

| Alias | Exact relative file |
|---|---|
| E | `Events/music.wwu` |
| I | `Interactive Music Hierarchy/music.wwu` |
| S | `Switches/switches.wwu` |
| B | `Master-Mixer Hierarchy/Default Work Unit.wwu` |

The XML was parsed in memory with the already installed Python standard library. Event target GUIDs were resolved against Switch objects, then container Arguments and MultiSwitchEntry EntryPath/AudioNode references were followed. Counts below cover these work units, not every event in the entire project. No Wwise application, generation, or game execution was used. Raw `ActionType` numbers are recorded because a local enum definition was not found; the inferred switch-setting meaning comes from the targets resolving to Switch values, not their filenames.

### Two independent selectors

**Observed fact:** S:434-439 defines a SwitchGroup `music_type` with values `world_music` and `quests_cutscenes`. This is separate from the StateGroup `game_state` in `States/global_states.wwu`.

**Observed fact:** the eight regional root MusicSwitchContainers (`music_skellige`, `music_prologue`, `music_misty_island`, `music_kaer_morhen`, `music_nomansgrad`, `music_wyzima_castle`, `music_spiral`, `music_toussaint`) use `music_type` as an Argument. For prologue, the root is I:113621 and its Argument and entries are I:139843-139887: `world_music` selects its `world_music` child; `quests_cutscenes` selects its `quests_and_cutscenes` child. These are two children of the same root playback hierarchy, rather than separate event-started area and quest tracks.

### A. Generic area music during dialogue

The concrete prologue path is:

`play_music_prologue` → `music_prologue` → (`music_type=world_music`) `world_music` → (`location_prologue=village`) `general` → (`game_state=dialog_scene`) `village_exploration`.

**Observed facts:** E:216-251 contains a root-target action with omitted/default ActionType, an ActionType 3 action with the prologue root as an exception, and an ActionType 23 targeting the `world_music` Switch GUID. I:139679-139696 maps location `village` to `general`. The general container (I:122426) uses `game_state`; its entries select `village_exploration` for both exploration (I:124764-124781) and dialogue (I:124818-124835), and also for cutscene (I:124800-124817). No `None` entry is present in its entry list. The NML `nml_zone_01` container repeats this pattern: exploration and dialogue select `expl_nml_zone_01` (I:269387-269440).

**Inference:** generic dialogue can simply be the regional exploration playlist selected while the game is in dialogue. It need not have a distinct dialogue track or a dialogue-prefixed event. The area-root event initializes playback; later state changes select its active child.

### B. Explicitly authored conversation/cutscene music

The concrete conversation path is:

`mus_q001_tavern_conversation` → Switch values (`music_type=quests_cutscenes`, `quests_prologue=q001_begining`, `q001_begining=mus_q001_tavern_conversation`) → already-started `music_prologue` → `quests_and_cutscenes` → `q001_beginning` → `q001_tavern_conversation` playlist → `mus_q001_tavern_conversation` segment → two music tracks.

**Observed facts:** E:180-213 contains three ActionType 23 actions whose GUIDs resolve to those exact Switch values (S:1196-1218; S:434-439). The regional quest selector maps `q001_begining` to container `q001_beginning` (I:122174-122191); that container maps the cue Switch to `q001_tavern_conversation` (I:115509-115526). Its playlist is at I:114768, segment at I:114820, and tracks at I:114833 and I:114935. This selector chain has no `game_state` Argument. `mus_cs001_tavern_intro` follows the same structure with a different cue Switch and playlist (E:146-179; I:115491-115508; playlist I:114621).

Crucially, the authored conversation uses sources `music\nomansgrad\section_02\tw3_nml_08_exploration_int1_14.02.21.wav` and `tw3_nml_08_exploration_int3_14.02.21.wav` beneath those tracks. **Observed fact:** an explicitly selected conversation cue can reuse exploration-named media. Track-name filtering cannot represent the required distinction.

### Replace, pause, bypass, or coexist?

**Observed facts:** the conversation and cutscene events above contain Switch-target actions, not root Play/Stop/Pause target actions. The regional root has transition rules between world and quest objects. For example, I:113664-113691 describes `village_exploration` → `cs001_tavern_intro` with source fade-out enabled and FadeTime 2; I:113692-113729 describes `cs001_tavern_intro` → `q001_tavern_conversation` with source/destination fades and FadeTime 4. I:113789-113816 describes `q001_tavern_conversation` → `expl_silent` with source fade-out FadeTime 6. `mus_loc_prologue_tavern` only sets the location Switch (E:292-305); `mus_loc_prologue_tavern_cs_to_gmpl` sets that location and `music_type=world_music` (E:306-329).

**Inference:** the normal mechanism replaces the selected branch of an ongoing regional music root. It bypasses the world branch's `game_state` selection, rather than bypassing all music mixing or pausing a separately launched area stream. Source and destination can overlap during authored crossfades; the data does not establish indefinite parallel playback. A normal location update can coexist with the selected quest branch as stored selector state without audibly switching back; explicit return events restore `world_music`. The exact sample timing and pause/resume cursor semantics need runtime observation.

**Observed fact:** `stop_music` is different: E:5891 onward contains ActionType 2 root-target actions, with FadeTime 4 on several regional roots. Do not treat every music event as a cue start or every `*_stop` name as a root Stop action.

### Container routing versus bus routing

**Observed facts:** regional roots explicitly reference OutputBus `Music` (e.g. I:113626-113628). In B, that bus is under `Master Audio Bus/Immerse/Music` (Music begins B:9136). The quest/world children often contain stored OutputBus references to `Master Audio Bus` (e.g. I:114185-114187 and I:122431-122433), but the inspected ordinary descendants do not enable `OverrideOutput`. An XML-wide search found no `OverrideOutput=True` under `world_music`. Under `quests_and_cutscenes`, the eight enabled overrides found are localized Toussaint main-menu tracks, mostly targeting `Ambient_BKG` (e.g. I:477236); these are special cases.

**Inference:** normal world and authored quest music inherit the regional root's Music bus; the presence of a stored Master Audio Bus reference without an enabled output override is not evidence of an authored-music bypass. This interpretation should be checked in Wwise/profiling before resource generation. No ordinary dedicated story bus was identified in this trace.

B:9188-9206 applies a -1 dialogue-state adjustment at the common Music bus; B:9291-9324 applies `menu_volume_music`. A new 0% dialogue multiplier here would affect both branches that use the bus. It cannot satisfy authored-story preservation merely by allowing `cutscene`.

### Why Only Story Music often preserves authored cues

**Observed facts:** the mod suppresses exploration/dialogue state strings in `GameStateToString` but does not modify these music events or the `music_type` Switch (`C:\Dev\witcher-music-control\reference\only-story-music\story-only\modOnlyStoryMusic\content\scripts\engine\sound.ws:327-376`). The world path above needs a named `game_state` entry to select its playlist; the authored conversation path only needs music-type/quest/cue Switch values.

**Inference:** suppressing named game-state selection can remove the generic area playlist while leaving a switch-selected authored conversation audible. This is a selection filter, not a global music-volume mute. The native normalization of `SoundState("game_state", "")` to an empty/default state is not available as source; the absence of a `None` world entry supports the mechanism but audible silence is still a runtime assertion.

**Important counterexample:** Only Story Music does not guarantee preservation of all authored music. Across I, there are 106 nested world MusicSwitchContainers, all using `game_state`, and 105 nested quest MusicSwitchContainers, six of which also use `game_state`:

| Quest-branch container | Declaration | Relevant dependence |
|---|---:|---|
| `q103_daughter/q103_poroniec_all` | I:170892 | dialogue/exploration select `q103_poroniec`; no `None` entry (I:172941-172976) |
| `q106_tower/q106_investigation` | I:175992 | combat/exploration/dialogue selection; no `None` entry |
| `novi_sewers` | I:188977, under `music_nomansgrad/quests_and_cutscenes` | world-like `game_state` selector despite quest-branch placement |
| `novi_fight_club` | I:209556, under the same quest branch | world-like `game_state` selector |
| `q705/q705_followup_regis` | I:470422 | dialogue/exploration select the Regis cue; no `None` entry (I:471930-471947) |
| `mq7023/caves` | I:473413, under `music_toussaint/quests_and_cutscenes` | state-based cave exploration/combat selection |

**Inference:** blanking dialogue/exploration globally can also deselect these authored/state-dependent cues. This falsifies a universal claim that Only Story Music preserves every authored quest cue.

### Event-family audit and exceptions

Resolved against S by GUID, E contains:

| Event prefix | Count | `music_type=quests_cutscenes` targets | `music_type=world_music` targets |
|---|---:|---:|---:|
| `mus_q*` | 260 | 259 | 1 |
| `mus_cs*` | 152 | 152 | 0 |
| `mus_loc*` | 212 | 3 | 103 |
| `play_music_*` | 9 | 0 | 8 |

The remaining location events generally update location selection without changing music type. Two `mus_q*` actions also have ActionType 38; they are not decoded here. This is not a universal prefix classifier: `mus_q102_villagers_flee_stop` returns to world music (E:10523); `mus_loc_novi_sewers` and `mus_loc_novi_fight_club` select the quest branch (E:8987 for sewers), as does `mus_loc_emhyrs_fleet_cs_to_gmpl`. `play_music_main_menu` uses a different main-menu selector instead of `music_type`. Follow GUID targets, not prefixes.

### Is there a robust authored-cue-active signal?

**Observed fact:** `music_type=quests_cutscenes` is a concrete structural signal for the selected branch. It is not itself proof of audible authored music: a branch may select silence, have completed, be stopped/unloaded, be transitioning, or contain generic-looking shared material. Event receipt records a request, not playback completion.

The installed script exposes `SoundEvent`, `SoundMusicEvent`, `SoundSwitch`, `SoundEventAddToSave`, `SoundEventClearSaved`, and `EnableMusicDebug` (`C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\engine\sound.ws:78-93,681-688`). No getter for `music_type`, current music segment/playing ID, or music completion callback was found in that script/API trace. `GetCurrentGameState` only returns the gameplay enum. A stale Wwise SDK environment path was found, but its directory does not exist; no SDK query/callback API is assumed here.

Authored event dispatch is partly visible: `SoundEventScene` calls `theSound.SoundEvent(eventName)` and optionally saves/clears the event (`game/scenes/scene_functions.ws:6-18`); `SoundEventQuest` does the same (`game/quests/quest_function.ws:1893-1905`). Both paths can change the music selectors without calling `SoundGameStateChange`. Native scene/resource event dispatch and save replay may bypass wrappers around these helpers; complete coverage is unproven. A script-side last-event flag or prefix test is not a robust active-cue detector.

**Recommendation/inference:** apply generic multipliers structurally below `world_music`, where they cannot reach the authored branch, rather than requiring an audible-cue boolean to protect every quest. Playback diagnostics remain useful, but preservation can follow hierarchy membership without tracking individual tracks.

### Can the volumes be separated without a track list?

**Inference supported by the topology:** yes at the Wwise-container level. Keep vanilla `game_state` and `music_type` routing intact. Attach a contextual multiplier only to the eight regional `world_music` ancestors, or route those branches through a dedicated generic-music bus with correct output overrides. Exploration/dialogue/combat receive separate levels there; `quests_and_cutscenes` receives no additional attenuation. Crossfade overlap then receives the correct gain per branch. The XML audit resolved all 1,630 AudioNode entries within world-branch selectors to world-branch objects, and all 734 quest-branch entries to quest-branch objects, supporting this boundary without individual media enumeration.

This is a resource-routing design, not a proven vanilla script API. The exact additional parameter names, generation scope, packaging, and inheritance behavior are unresolved. A pure gameplay-state multiplier on the common Music bus, or copying Only Story Music's empty-state strategy, does not meet the new requirement. Explicitly quest-related location music routed under `world_music` remains a semantic exception: a selector branch encodes the engine's category, not a perfect author-intent label. Such cases require source-grounded container-level exceptions or a stronger runtime signal before claiming complete coverage.

### Falsification tests for a future diagnostic session

- Compare ordinary area dialogue with `mus_q001_tavern_conversation` while both report `dialog_scene`; the branch must differ even though the gameplay enum matches.
- Enter `q103_poroniec_all` and `q705_followup_regis` during dialogue/gameplay: a preservation strategy must retain their named states, rather than reproduce Only Story Music's empty-state failure.
- Trigger normal location changes while a quest cue is selected, then an explicit return event: verify that location changes do not prematurely replace the authored cue.
- Observe crossfades, silent quest selections, stopped roots, cue completion, save/load, and native scene events. These can falsify a last-event-based active-cue flag.
- Set a generic-branch test attenuation and verify that authored cues, including reused exploration media, retain their authored mix. Any authored attenuation indicates an incorrect inheritance/routing boundary.
