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

**Inference:** Only Story Music is using the existing Wwise `game_state` state group as a coarse category filter. Empty strings route several enum values to the Wwise default/empty state; named strings preserve those categories. This explains why the variants can produce different category mixes without shipping audio files.

**Hypothesis to test in game:** the empty string may produce a useful “music absent” result because of the current Wwise state routing, but the exact audible result depends on the installed bank and transition rules. The diff alone does not prove that every track outside the named states is silent.

## Binary/resource conclusion

There are no binary resources to compare in this differential set. The four script hashes differ, and the path/file counts are identical. Therefore the strongest category evidence is the exact enum-to-string edit, verified against the current vanilla enum and Wwise state list in [03-vanilla-music-path.md](03-vanilla-music-path.md).
