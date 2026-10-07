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

**Inference:** Wwise already receives a reliable coarse context through `game_state` and already supports state-specific bus volumes. Arbitrary independent contextual multipliers require either a suitable existing parameter or a resource-side addition. The vanilla project exposes `menu_volume_music`, but not the three requested contextual volume parameters.

## Answers to the investigation questions

1. **Normal gameplay music component:** `CScriptSoundSystem` controls the `game_state` Wwise state and emits area music events; Wwise's `Music` bus and music banks perform the resulting routing.
2. **Combat signal:** `CollectSoundStates` uses `CR4Player.ShouldEnableCombatMusic`, which combines native `IsInCombat`, threat, force-combat, hostile/alert, finishable-enemy, and finisher signals.
3. **Dialogue/scene signal:** `CStoryScenePlayer` enters `ESGS_Dialog`/`ESGS_DialogNight` for `Blocking` scenes; the state is sent through `SoundGameStateChange`.
4. **Ordinary dialogue vs authored cinematic:** yes at the scene-player/sound-state layer (`dialog_scene` vs `cutscene`/`movie`), although the general game boolean combines dialogue and cutscene.
5. **Story music runtime state:** no `story` enum or Wwise state was found. Only Story Music changes existing enum-to-string mappings; its effect is resource/state routing, not a new story state.
6. **Independent exploration/combat volume without replacing music assets:** the state layer can distinguish them, and Wwise can apply state-specific bus volumes. A script-only arbitrary multiplier is not proven by vanilla data because no contextual volume RTPC is exposed; FMC demonstrates the resource-backed approach.
7. **Independent dialogue volume:** same answer. `dialog_scene` and `dialog_scene_night` are distinct Wwise states with state-specific Music-bus entries, but a new adjustable dialogue multiplier is not present in vanilla.
8. **Cinematic/story override:** yes, the scene player pushes `cutscene`/`movie` over blocking dialogue, and Wwise has distinct states and transitions. Exact precedence during unusual nested scenes needs gameplay tracing.
9. **Reusable mechanism:** `SoundState("game_state", ...)`, `SoundParameter`/`SoundGlobalParameter`, `SoundMusicEvent`, existing `game_state`/`mixing_state` groups, `threat_rating`, and `menu_volume_music` are all present. No vanilla contextual music-volume global parameter was found.
10. **Remastered scope/local overrides:** FMC proves local script wrappers work for `CR4IngameMenu`; the references do not prove a local wrapper for private `CScriptSoundSystem.SoundGameStateChange`. A full engine-file replacement works in the references but has high conflict risk. Compiler/runtime validation is required before choosing an override form.
11. **Narrowest stable hook:** semantically, `CScriptSoundSystem.SoundGameStateChange` is the narrowest central transition point because it receives every accepted enum transition and performs the Wwise state call. Its private-method override feasibility is the largest implementation question. `EnterGameState`/`SetDefaultGameState` are the next public candidates.
12. **Ambiguous cases:** gameplay dialogue with control and scripted walks may use blocking scene states but need trace confirmation; quest music can call `EnterGameState` directly; combat during a quest competes with explicit state priority; Gwent has an explicit state; tavern/bard music is also represented by diegetic emitter/bank assets and is not equivalent to global gameplay music; menus, loading videos, black screens, pause, and save/load transitions have separate states/resume paths.

