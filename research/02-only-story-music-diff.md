# Only Story Music controlled diff

## Method

`story-only` is the baseline. Each comparison has the same relative path set and no binary resources. Text was diffed directly. The implementation file is `modOnlyStoryMusic/content/scripts/engine/sound.ws` in each variant.

## Results

| Comparison | Files changed | Semantic change in `GameStateToString` |
|---|---:|---|
| baseline → `story-gwent-tavern` | 1 | `ESGS_Gwent`: `""` → `"gwent"` |
| baseline → `story-combat` | 1 | `ESGS_Combat`: `""` → `"combat"`; `ESGS_CombatMonsterHunt`: `""` → `"combat_monster_hunt"`; `ESGS_UnderwaterCombat`: `""` → `"underwater_combat"`; `ESGS_FocusUnderwater`: `""` → `"underwater_combat_focus"`; `ESGS_Gwent`: `""` → `"gwent"` |
| baseline → `story-exploration` | 1 | `ESGS_Exploration`: `""` → `"exploration"`; `ESGS_ExplorationNight`: `""` → `"exploration_night"`; `ESGS_Focus`: `""` → `"focus_exploration"`; `ESGS_FocusNight`: `""` → `"focus_exploration_night"`; `ESGS_Dialog`: `""` → `"dialog_scene"`; `ESGS_DialogNight`: `""` → `"dialog_scene_night"`; `ESGS_Boat`: `""` → `"boat"`; `ESGS_Underwater`: `""` → `"underwater"`; `ESGS_FocusUnderwater`: `""` → `"underwater_focus"`; `ESGS_Gwent`: `""` → `"gwent"` |

The baseline retains the mappings for `cutscene`, `movie`, and `music_only` (`reference/only-story-music/story-only/modOnlyStoryMusic/content/scripts/engine/sound.ws:327-376`). The exploration variant restores the ordinary gameplay and dialogue strings while leaving `cutscene`, `movie`, and `music_only` intact (`reference/only-story-music/story-exploration/modOnlyStoryMusic/content/scripts/engine/sound.ws:327-376`).

## What this proves

**Observed fact:** the variants only change which existing `game_state` string is sent to Wwise. No event, bank, asset, RTPC, or state-group resource changes are present in the variant trees.

**Inference:** Only Story Music uses the existing Wwise `game_state` selection as a coarse filter. The script sends empty strings for suppressed categories; the native normalization of that string is not exposed in the inspected source. The world-music containers lack a `None` playlist entry, supporting the expected suppression when named state selection is removed.

**Hypothesis to test in game:** the empty string may produce a useful “music absent” result because of the current Wwise state routing, but the exact audible result depends on the installed bank and transition rules. The diff alone does not prove that every track outside the named states is silent.

## Binary/resource conclusion

There are no binary resources to compare in this differential set. The four script hashes differ, and the path/file counts are identical. Therefore the strongest category evidence is the exact enum-to-string edit, verified against the current vanilla enum and Wwise state list in [03-vanilla-music-path.md](03-vanilla-music-path.md).

## Follow-up: why authored dialogue can survive, and where it does not

**Observed fact:** the REDkit project has a separate SwitchGroup `music_type` (`L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Switches\switches.wwu:434-439`). Regional root containers choose between `world_music` and `quests_and_cutscenes` using its values. This switch remains untouched by Only Story Music.

Generic dialogue in the prologue village chooses `village_exploration` through `game_state=dialog_scene`; exploration chooses the same playlist (`Interactive Music Hierarchy/music.wwu:124764-124835`, relative to the Wwise root above). Explicit `mus_q001_tavern_conversation` instead sets three Switch values selecting the quest branch and a dedicated conversation playlist (`Events/music.wwu:180-213`; `Interactive Music Hierarchy/music.wwu:115509-115526`). That path does not require `dialog_scene`. **Inference:** it can keep playing when the mod removes the named dialogue state, because the mod suppresses the world branch's selection rather than globally muting the Music bus.

**Observed counterexamples:** six quest-branch MusicSwitchContainers also select by `game_state`. `q103_poroniec_all` requires named dialogue/exploration entries (I:172941-172976), and `q705_followup_regis` has a named dialogue entry (I:471930-471947), with no `None` entry in either. **Inference:** Only Story Music can suppress these authored cues too. Its name and successful preservation of many switch-only cues are not proof of complete story preservation.

The stronger requirement is therefore to preserve vanilla state routing and attenuate generic music within `world_music` only. Muting the common Music bus during dialogue would also attenuate authored conversation music, and retaining `cutscene` alone cannot protect story music played during `dialog_scene` or gameplay. Full event/container/bus traces and falsification cases are recorded in [03-vanilla-music-path.md](03-vanilla-music-path.md).
