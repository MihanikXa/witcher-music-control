# White Orchard pilot — target location correction (2026-10-11)

## Explicit change of target

The user rejected the **opening prologue/tutorial** as the first in-game music test, because it does not offer the relevant exploration-music behavior in the segment they mean. They want the mod tested where they currently play: **White Orchard** (the user wrote "White Lotus"; interpret as White Orchard in Witcher 3 unless corrected). This is a correction to the *test geography and test cases*, not to the 0/0/100 default gains or the Wwise architecture.

**Naming trap:** the in-game region White Orchard is handled by the Wwise **`music_prologue`** regional music root/bank. That root includes named locations such as `location_prologue=village` with `village_exploration` selected during exploration and ordinary `dialog_scene`. The opening Kaer Morhen dream/tutorial and Wwise's "prologue" are not interchangeable target descriptions. The existing research (03, E:216–251 and I:122426, 124764–124835, 139679–139696) supplies exact local audio-project paths and routing evidence.

### Scope of the first prototype

- **Geographic gameplay test:** White Orchard village, surrounding countryside and accessible nearby encounters.
- **Wwise edit:** only the `world_music` child beneath `music_prologue`; attach the proposed `WMC_WorldMusic` child bus and three State-gated Gain effects. Do not change the authored `quests_and_cutscenes` sibling, generic music events, scene flags, composition/source WAV or native threat/intensity behavior.
- **Logical build outputs:** new `Init.bnk` + changed `music_prologue.bnk`; minimal mod `soundspc.cache` packaging remains unproven. Changing this Wwise root is **bank-scoped**, not geofenced: other gameplay scenes routed through that same root may also be affected. Do not claim a White Orchard-only runtime restriction without a separate location test.
- **Starting settings:** extra world gain exploration 0% intended mute, ordinary dialogue 0% intended mute, combat 100%; authored cues 100%/unity relative to normal Music volume. Confirm the finite Gain floor versus actual silence.
- **No live deployment yet:** work only in isolated Wwise project copies and ignored build outputs. No REDkit depot regeneration. Stage in-game tests only after separately authorized deployment in an isolated mod profile.

## Reproducible listening and routing matrix

For each row, capture an unmodified baseline first and note actual audible music and gameplay state; do not treat absence of an audible cue as proof of suppression.

| White Orchard situation | Baseline needed | Intended mod behavior / falsification |
| --- | --- | --- |
| Open countryside travel (one or more spots/day-night with actually audible area score) | Record that world exploration music plays; ambient SFX and weather present | Ordinary exploration music goes effectively silent; world SFX and voices unaffected. A silent starting area is **not** a valid positive result. |
| Village exploration and routine NPC dialogue | Establish baseline dialogue/area bed while speaking | Generic `dialog_scene` world branch attenuated; dialogue intelligible, authored event unaffected. |
| Standard encounter (bandits/wolves/other accessible foe) | Note encounter/combat cue and natural combat onset/exit | Combat uses unity gain and existing threat-driven timing/intensity; no spurious drop or harsh entry/exit. |
| Explicitly authored tavern conversation `mus_q001_tavern_conversation` or `mus_cs001_tavern_intro` | Available **earlier backed-up save** or Wwise authoring simulation of corresponding selector | Quest music stays at normal authored gain; no common-bus mute or destroyed world/quest crossfade. If scene cannot be replayed safely, mark in-game case **untested**, never fabricate. |
| Cutscene/movie and save/load | Baseline native playback/mute/transition | No extra attenuation on authored branch; preserve native movie mute and resume. |
| Settings / user Music volume | Baseline 100% vs reduced user setting | WMC gains remain additional; native volume still controls all music, while SFX/dialogue aren't changed. |

### Engineering validation order

1. Read reports 04–08 and this plan; use correct local installed paths (game on C:, REDkit on L:) as read-only evidence.
2. Verify the matching Wwise 2023.1.19 project and `music_prologue` hierarchy. Resolve specific White Orchard world-branch selector and audio-file/Bank ownership *before* editing.
3. In an isolated project copy, implement proposed bus/effects/state bypass. Verify inactive parameters do not attenuate any source and both FullBand/LFE paths obey selected gain.
4. Generate only matching required `Init.bnk` and `music_prologue.bnk`; compare output HIRC, media, source paths and global init objects to baseline.
5. Establish minimal cache packing and loader precedence. Wwise bank generation alone is not mod deployment.
6. Stop and report readiness; after explicit approval, test safely in White Orchard using a backed-up save and isolated mod profile. Do not restart the game or advance the story just for one quest music comparison.

### Decision

**Approved immediate prototype target:** White Orchard gameplay through the technically named `music_prologue` bank. No new music modes, no Gwent/diegetic policy change, no player-state hook and no edit to game installation were approved by this correction.
