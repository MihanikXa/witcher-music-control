# World-music exceptions audit

## Concrete counts and what they mean

**Observed:** the eight world branches contain **106 direct location/state selectors**: Skellige 23, prologue 9, Misty Island 1, Kaer Morhen 3, NML/Novigrad 48, Wyzima 1, Spiral 2, Toussaint 19. Twenty-four carry an explicit quest ID or “quest” in their container name. That count is not the number of authored-score exceptions.

All 106 were inspected for exploration/dialogue AudioNode targets and their actual AudioFile references. The review table below contains **55 selectors**: the 24 quest-labelled selectors, 21 additional narrative/location candidates, and 10 additions found through source inspection/comparison. The other 51 are ordinary regional, cave, settlement, town, silent, tavern or emitter-policy contexts; they are not classified as story merely because a mus_loc event exists.

There are **12 concrete quest-resource candidates** in the table (Q): **7 reuse a source also selected by an actual quest/cutscene playlist**, and 5 have quest-associated noncombat resource/variant evidence but no matched quest-branch playlist for that selected source. **11** table selectors have only verified zero-PCM sources in the four exploration/dialogue states (Z). The other **32** (L) are audible-source location/theme/reuse candidates or comparators; their author-intent policy is unresolved.

These are reproducible structural counts, not a claim that all 55 need exemption or that 12 is the exact number of intentionally scored runtime situations. A source shared with a quest cue does not make every use of that source a quest cue. **No exact all-game author-intent exception count can be proved from this Wwise project alone.** Scene/quest placement and listening are needed for that stronger assertion. The table makes the concrete attenuation risks visible instead of inventing an intent flag.

## Exact local evidence

- I = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Interactive Music Hierarchy\music.wwu`.
- E = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Events\music.wwu`.
- S = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Switches\switches.wwu`.
- O = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\Originals\SFX\`.

The audit follows each world child's ObjectLists/Entries/MultiSwitchEntry, resolves its EntryPath state GUIDs and AudioNode GUID, and reads AudioFile references **only in nodes selected by exploration, exploration_night, dialog_scene or dialog_scene_night**. It does not classify all descendants as dialogue music: those descendants also contain combat, Gwent and transition material. This distinction changes several apparent exceptions substantially.

The two silence originals, `O/music/skellige/silent_wave_10s.wav` and `O/music/toussaint/general_hub/silent_wave_10s.wav`, were inspected read-only: RIFF fmt code 1, stereo, 44,100 Hz, 16-bit PCM; each data chunk is 1,764,000 bytes, all zero. Silence below is thus established from samples, not from the filename.

## Table legend and effect of the proposed mixer

State codes are exact existing EntryPath values: E=exploration, En=exploration_night, F=focus_exploration, Fn=focus_exploration_night, D=dialog_scene, Dn=dialog_scene_night, C=cutscene, K=combat, H=combat_monster_hunt, Fk=focus_combat, U=underwater, Uf=underwater_focus, Uk=underwater_combat, Ukf=underwater_combat_focus, B=boat, G=gwent, M=minigames. The column lists the **union of mapped states**, not every state mapping to the displayed media.

Q means strong quest-resource evidence and **inferred preservation candidate**. L means location music/reuse or unresolved intent, not proven mandatory exemption. Z means no additional noncombat audible loss for the verified silent selections. With no exception routing, **every non-silent E/D selection below would receive the exploration/dialogue attenuation**, irrespective of author intent; combat remains at its configurable combat gain, C stays at unity, and G/M retain native mix. Therefore the answer “world-only protects all authored music” is false without a policy for these cases.

Displayed sources are basenames from actual AudioFile references (up to two, with remaining count). I line anchors identify the exact containing node; its descendants provide full relative media paths. Events are matched by switch GUID through the outer world location map. Absence of a matched event is reported explicitly.

| Container / quest or location and assessment | Evidence | Mapped states | Selected E/D sources | Resolved location event evidence | Class |
|---|---|---|---|---|---|
| `ice_giant_island` — Dedicated location selection; intended story exemption unverified | music_skellige; I:60936 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_skellige_ice_giant_expl_layer1.wav`, `tw3_skellige_ice_giant_expl_layer2.wav` (+1) | `mus_loc_ice_giant_island`, E:2237 | L |
| `skellige_hindarsfjall_freyas_garden` — Dedicated location selection; intended story exemption unverified | music_skellige; I:86642 | K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf | `tw3_skl_16_freyas_garden_expl.wav` | `mus_loc_hindarsfjall_freyas_garden`, E:2465 | L |
| `skellige_ard_skellig_cataclysm_place` — Dedicated location selection; intended story exemption unverified | music_skellige; I:88982 | K,H,C,D,Dn,E,En,F,Fn,G,U,Ukf | `tw3_bad_news_ahead_full_with_brass.wav` | `mus_loc_ard_skellig_cataclysm`, E:2119 | L |
| `nilfgaard_camp_q501` — q501 camp; ordinary prologue camp-source reuse | music_skellige; I:91185 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_prlg_02_expl_14.07.16.wav` | `mus_loc_ice_giant_q501_nilfgaard_camp`, E:2275 | L |
| `skellige_ard_skellig_yennefers_room` — Yennefer room; q309 harp love-theme cue source | music_skellige; I:93190 | K,H,C,D,Dn,E,En,F,Fn,G,U | `tw3_love_theme_short_harp_only.wav` | `mus_loc_ard_skellig_yennefers_room`, E:2157 | Q |
| `skellige_hindarsfjall_burned_village_q205` — q205 burned village; q203 examination cue source | music_skellige; I:96977 | K,H,C,D,Dn,E,En,F,Fn,G,U,Ukf | `tw3_q203_09_examine_elf_corpse_full.wav` | `mus_loc_hindarsfjall_burned_village_q205`, E:2503 | Q |
| `skellige_ard_skellig_berserkers_village` — Berserkers village; Freya garden-source reuse | music_skellige; I:99706 | K,H,C,D,Dn,E,En,F,Fn,G,U,Ukf | `tw3_skl_16_freyas_garden_expl.wav` | `mus_loc_ard_skellig_berserkers_village`, E:2195 | L |
| `emhyrs_fleet_q210` — q210 fleet; camp-source reuse; return event selects quests | music_skellige; I:104062 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_prlg_02_expl_14.07.16.wav` | `mus_loc_emhyrs_fleet`, E:2313 | L |
| `skellige_spikeroog_hims_house` — Dedicated location selection; intended story exemption unverified | music_skellige; I:110289 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_ambient01_hims_house_mix.wav` | `mus_loc_spikeroog_hims_house`, E:2583 | L |
| `village_q505` — q505 village; q302 inquisition cue source | music_prologue; I:137817 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `Novi_Inquisition_ThemeV3_NoChoirPerc_NoSoloVlnBrs_bip.wav` | `mus_loc_prologue_village_q505`, E:558 | Q |
| `mi_general` — Isle of Mists region; regional score, quest intent unresolved | music_misty_island; I:140157 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_isle_of_mists_expl_full_bip.wav` | `mus_loc_isle_of_mists`, E:6240 | L |
| `nml_barons_castle` — Dedicated location selection; intended story exemption unverified | music_nomansgrad; I:251967 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_03_exploration_int1.wav`, `tw3_nml_03_exploration_int2.wav` (+2) | `mus_loc_nml_barons_castle`, E:8203 | L |
| `nml_mice_island` — Dedicated location selection; intended story exemption unverified | music_nomansgrad; I:255274 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_06_exploration_day_int1.wav`, `tw3_nml_06_exploration_day_int2.wav` (+3) | `mus_loc_nml_mice_island`, E:8217 | L |
| `nml_swamps_witches_village` — Dedicated location selection; intended story exemption unverified | music_nomansgrad; I:269640 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_05_witches_village_exploration_with_rebec_14.02.21.wav`, `silent_wave_10s.wav` | `mus_loc_nml_swamps_witches_village`, E:8259 | L |
| `nml_ghost_forest` — Ghost forest; silent noncombat despite tree-cave sibling | music_nomansgrad; I:271881 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_ghost_forest`, E:8273 | Z |
| `nml_ghost_forest_tree_cave` — Dedicated location selection; intended story exemption unverified | music_nomansgrad; I:273902 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_10_ghost_forest_exploration_mixed_14.02.19.wav` | `mus_loc_nml_ghost_forest_tree_cave`, E:8287 | L |
| `nml_mice_island_popiel_tower` — Dedicated location selection; intended story exemption unverified | music_nomansgrad; I:305884 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_06_exploration_day_int1.wav`, `tw3_nml_06_exploration_day_int2.wav` (+2) | `mus_loc_nml_mice_island_popiel_tower`, E:8859 | L |
| `novi_radovid_ship` — Dedicated location selection; intended story exemption unverified | music_nomansgrad; I:319660 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `Novi_Inquisition_ThemeV3_StrAndWW_bip.wav` | `mus_loc_novi_radovid_ship`, E:9049 | L |
| `novi_inquisitors_house` — Named house events target Radovid ship instead | music_nomansgrad; I:322704 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `Novi_Inquisition_ThemeV3_NoChoirPerc_NoSoloVlnBrs_bip.wav` | No matched outer entry/event | L |
| `nml_village_burned_q101` — q101 burned village; same q203 cue | music_nomansgrad; I:325746 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_q203_09_examine_elf_corpse_full.wav` | `mus_loc_nml_village_burned_q101`, E:9125 | Q |
| `novi_haunted_house_q301` — q301 house; dialogue ambient01 | music_nomansgrad; I:328001 | K,H,C,D,Dn,E,En,F,Fn,G,U | `tw3_dialog_ambient01.wav` | `mus_loc_novi_haunted_house_q301`, E:9163 | L |
| `novi_nilfgaard_embassy` — Novigrad embassy; q002 emperor-conversation source | music_nomansgrad; I:331050 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `q002_geralt_talks_to_emperor_Full.wav` | `mus_loc_novi_nilfgaard_embassy`, E:9239 | Q |
| `dawn_estate_sq301` — sq301 estate; tavern-arrangement reuse | music_nomansgrad; I:334107 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `skl_11_tavern02_arranged.wav` | `mus_loc_dawn_estate`, E:9277 | L |
| `novi_crime_scenes_q308` — q308 crime scenes; ambient03 also used in combat | music_nomansgrad; I:336585 | K,H,C,D,Dn,E,En,F,Fn,G,U,Ukf | `tw3_dialog_ambient03.wav` | `mus_loc_novi_crime_scenes_q308`, E:9315 | L |
| `novi_golden_sturgeon_dreamers_house_q301` — q301 dreamer's house; ambient02 | music_nomansgrad; I:337747 | K,H,C,D,Dn,E,En,F,Fn,G,U | `tw3_dialog_ambient02.wav` | `mus_loc_novi_golden_sturgeon_dreamers_house_q301`, E:9353 | L |
| `nml_zone_04_roche_camp` — Roche camp; Assassins theme used interactively | music_nomansgrad; I:344122 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_assassins_of_kings_theme_expl_p1_MASTER_15.02.12.wav`, `tw3_assassins_of_kings_theme_expl_p2_MASTER_15.02.12.wav` | `mus_loc_roche_camp`, E:9201 | L |
| `nml_zone_01_nilfgaard_warcamp` — Warcamp; emperor theme/day, ordinary NML night | music_nomansgrad; I:346699 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_main_themes_nilfgaard_emperor_theme_12.09.26.wav`, `tw3_nml_04_exploration_night_int1.wav` (+2) | `mus_loc_nml_zone_01_nilfgaard_warcamp`, E:9501 | L |
| `nml_zone_04_novigrad_outskirts_ep1_poi_lovers_spot` — EP1 lovers POI; q309 goodbye/love-theme sources | music_nomansgrad; I:350359 | B,K,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_q309_08a_goodbyePT2_Full.wav`, `tw3_q309_08a_goodbye_Full.wav` | `mus_loc_nml_ep1_lovers_spot`, E:9553 | Q |
| `nml_zone_04_novigrad_outskirts_ep1_poi_leshy_forest` — EP1 Leshy forest; Hym-house ambient reuse | music_nomansgrad; I:353124 | B,K,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_ambient01_hims_house_mix.wav` | `mus_loc_nml_ep1_leshy_forest`, E:9539 | L |
| `nml_mansion_garden_q604` — q604 garden; same noncombat source as generic caves | music_nomansgrad; I:355530 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_10_ghost_forest_exploration_mixed_14.02.19.wav` | `mus_loc_nml_mansion_q604`, E:9567 | L |
| `nml_mansion_paint_q604` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:357619 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_mansion_paint_q604`, E:9605 | Z |
| `nml_olgierd_house_q601` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:359037 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_olgierd_house_q601`, E:9643 | Z |
| `nml_mansion_paint_winter_q604` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:361616 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_mansion_paint_winter_q604`, E:9681 | Z |
| `nml_auction_house_q603` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:363023 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_auction_house_q603`, E:9719 | Z |
| `nml_everect_crypt_q602` — q602 crypt; same noncombat source as generic caves | music_nomansgrad; I:366088 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `tw3_nml_10_ghost_forest_exploration_mixed_14.02.19.wav` | `mus_loc_nml_everect_crypt_q602`, E:9757 | L |
| `nml_wedding_q602` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:368470 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_wedding_q602`, E:9795 | Z |
| `nml_occultist_house_q605` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:369839 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_occultist_house_q605`, E:9871 | Z |
| `nml_final_tavern_q605` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:372901 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_final_tavern_q605`, E:9833 | Z |
| `nml_final_shani_house_q605` — Quest/location-labelled selector; E/D verified silent | music_nomansgrad; I:375964 | B,K,H,C,D,Dn,E,En,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_nml_final_shani_house_q605`, E:9909 | Z |
| `devils_pit_exterior_(states)` — Devil's Pit; mq1060 original source path | music_nomansgrad; I:379027 | K,H,C,D,Dn,E,En,Fk,F,Fn | `tw3_devpit_01_amb_settlement.wav` | `mus_loc_nml_devils_pit`, E:9947 | Q |
| `wyzima_castle` — Wyzima castle; same q002 source as embassy | music_wyzima_castle; I:383446 | K,C,D,Dn,E,En,F,Fn,G | `q002_geralt_talks_to_emperor_Full.wav` | `mus_loc_wyzima_castle`, E:18689 | Q |
| `spiral_general` — Spiral region; interactive regional score | music_spiral; I:384784 | B,K,H,C,D,Dn,E,En,F,Fn,U,Uk,Ukf,Uf | `tw3_spiral_01_exploration_int1.wav`, `tw3_spiral_01_exploration_int2.wav` | `mus_loc_spiral`, E:19129 | L |
| `spiral_castle` — Spiral castle; q101 dialogue-cue source also used in combat | music_spiral; I:386109 | B,K,H,C,D,Dn,E,En,F,Fn,U,Uk,Uf | `q101_04b_talk_with_survivor_Full_VerA.wav` | `mus_loc_spiral_castle`, E:19167 | Q |
| `regis_cemetery` — Dedicated location selection; intended story exemption unverified | music_toussaint; I:404200 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_bob_15_expl_cemetery_alt_loop.wav`, `tw3_bob_15_expl_cemetery_main_loop.wav` | `mus_loc_toussaint_cemetery`, E:19581 | L |
| `tournament_quest` — Tournament quest; q701/sq701 variants alongside generic versions | music_toussaint; I:411392 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_q701_tournament_meadows_expl_Day_generic_expl.wav`, `tw3_q701_tournament_meadows_expl_Day_q701_sq701.wav` (+2) | `mus_loc_toussaint_tournament_quest`, E:19657 | Q |
| `tournament_general` — Ordinary tournament comparator; generic day/night sources | music_toussaint; I:414142 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_q701_tournament_meadows_expl_Day_generic_expl.wav`, `tw3_q701_tournament_meadows_expl_Night_generic_expl.wav` | `mus_loc_toussaint_tournament_general`, E:19643 | L |
| `regis_cemetery_workshop` — Regis workshop; silent noncombat | music_toussaint; I:418757 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | `mus_loc_toussaint_cemetery_workshop`, E:19733 | Z |
| `q702_wights_lair` — q702 lair; shared dialogue ambient | music_toussaint; I:423484 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_bob_16_amb_01_MASTER.wav` | `mus_loc_q702_wights_lair`, E:19809 | L |
| `sq703_photos_exhibition` — sq703 exhibition; Gwent-media reuse during noncombat/minigames | music_toussaint; I:425116 | K,H,C,D,Dn,E,En,F,Fn,G,M | `tw3_bob_12_tavern_01_loop_MASTER.wav`, `tw3_bob_13_tavern_02_MASTER.wav` | `mus_loc_sq703_photos_exhibition`, E:19847 | L |
| `q705_prison` — q705 prison; silent noncombat, no outer location entry resolved | music_toussaint; I:427232 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `silent_wave_10s.wav` | No matched outer entry/event | Z |
| `poi_gor_a_10` — POI gor_a_10; shared ambient, quest ID not established | music_toussaint; I:429759 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_bob_16_amb_01_MASTER.wav` | `mus_loc_poi_gor_a_10`, E:19923 | L |
| `mq7023_laboratory` — mq7023 laboratory; q702 music-box source, diegetic policy unresolved | music_toussaint; I:432172 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_q702_toy_storage_music_box.wav` | `mus_loc_mq7023_laboratory`, E:19961 | Q |
| `fairy_tale_main` — Fairy-tale land; dedicated q705 original plus silent intervals | music_toussaint; I:434346 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_q705_fairy_tale_land.wav`, `silent_wave_10s.wav` | `mus_loc_toussaint_fairy_tale_main`, E:20037 | Q |
| `fairy_tale_intro` — Dedicated location selection; intended story exemption unverified | music_toussaint; I:436231 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_bob_22_expl_amb_02.wav`, `silent_wave_10s.wav` | `mus_loc_toussaint_fairy_tale_intro`, E:19999 | L |
| `unseen_cave` — Dedicated location selection; intended story exemption unverified | music_toussaint; I:438133 | B,K,H,C,D,Dn,E,En,Fk,F,Fn,G,U,Uk,Ukf,Uf | `tw3_dialog_ambient01.wav` | `mus_loc_toussaint_unseen_cave`, E:20113 | L |

## Strong cases traced beyond media naming

The following **7** Q cases were resolved to a selected source shared with an actual playlist under quests_and_cutscenes. This proves the source has both world and authored-cue uses; preserving the cue does not automatically preserve its world use.

| World selector | Actual quest playlist using identical AudioFile reference |
|---|---|
| skellige_ard_skellig_yennefers_room | q309_love_theme (I:184714), q301_love_theme (I:191661), cs_sq301_geralt_triss_kiss (I:193861), sq101_love_theme and sq303_dandelion_about_priscilla |
| skellige_hindarsfjall_burned_village_q205 | tw3_q203_09_examine_elf_corpse_full (I:11122) |
| village_q505 | q302_radovid_dlg (I:194844) and q303_inquisitors_theme (I:199479) |
| nml_village_burned_q101 | tw3_q203_09_examine_elf_corpse_full (I:11122) |
| nml_zone_04_novigrad_outskirts_ep1_poi_lovers_spot | q309_08a_goodbye (I:184194) / q309_08a_goodbye_pt2, q605_dialogue_with_shani (I:235527) and other love-theme playlists |
| spiral_castle | q101_04b_talk_with_survivor (I:168213) |
| mq7023_laboratory | q702_toy_storage_amb (I:453920), tw3_q703_shieeeet (I:460299) and q704_bedroom (I:465919) |

Reproduce by comparing the table's selected AudioFile strings with AudioFile strings under each quests_and_cutscenes playlist in I; GUID-resolved playlist ancestry is the discriminator. For example the Spiral castle world node selects `music/nomansgrad/q101/q101_04b_talk_with_survivor_Full_VerA.wav` (I:386109 and descendants), while the authored playlist q101_04b_talk_with_survivor uses that same file. A shared source is evidence against track-list provenance classification.

The other **5** Q cases are novi_nilfgaard_embassy and wyzima_castle (both select the q002 emperor-conversation source), devils_pit_exterior_(states) (mq1060 source references), tournament_quest (separate q701/sq701 exploration variants), and fairy_tale_main (dedicated fairy-tale source). Their association is **observed metadata/routing**; important-story interpretation is an inference. Do not assign quest titles from memory. The table reports project quest IDs and location labels.

Tournament is the strongest controlled special-location comparison: tournament_general (I:414142) selects only generic day/night originals, while tournament_quest (I:411392) includes those plus q701/sq701 variants. Both are under world_music. Rerouting all of tournament_general as story would exceed the available evidence.

## Important corrections to a filename-only audit

- The q604 painted mansion and winter selectors, q601 Olgierd house, q603 auction house, q602 wedding and three q605 houses select verified silence for noncombat. Some playlists have exploration/oxenfurt-style names despite containing only the silent WAV. Combat/Gwent remain separate selections. Quest labels do not prove suppressed audible quest music.
- nml_mansion_garden_q604 and nml_everect_crypt_q602 reuse the ordinary cave/ghost-forest noncombat source. That is thematic location routing; distinct intent remains unverified.
- novi_crime_scenes_q308 maps combat as well as exploration/dialogue/cutscene to dialog_ambient_03 (I:336585 and entries following I:337540). The combat slider is state-based, not a “combat-sounding track” detector.
- sq703_photos_exhibition selects Gwent-media resources during exploration/dialogue/minigames. Treating media filenames as Gwent-only would misclassify it.
- mus_loc_emhyrs_fleet_cs_to_gmpl (E:2327-2350) selects music_type=quests_cutscenes. Its name does not guarantee return to world. The plain location event can update the location while leaving branch choice untouched.
- mus_loc_novi_inquisitors_house and its return event target the **novi_radovid_ship switch** (E:9087-9124), not the similarly named world container. No direct matching event was found for the inquisitor-house location-map value. Do not assume the house container is active from the event name.
- q705_prison exists as a world child, but the inspected outer world entries do not resolve a location entry to that container. Its named events set location_toussaint/q705_prison (E:19885-19922). Actual selected behavior/default resolution is unresolved, so the table counts a present selector, not a proven playable exception.
- A cue-return event such as mus_q102_villagers_flee_stop (E:10523) restores world and Baron's castle. It does not make that area's entire interactive score an explicitly active quest cue.

## Routing policy implied by this audit

A generic mixer cannot recover intent from game_state, music_type or a source filename. Both world and quest use some identical originals. There is no verified universal “explicit authored cue audible now” signal in the inspected script API (report 03). Static world-container exceptions can be routed directly to Music with OverrideOutput=True, leaving their state/music transitions intact and receiving none of the new gains. This uses **containers/contexts, not an enumeration of individual tracks**, but still requires a finite, justified exception policy.

A blanket override at the whole location protects its combat and Gwent descendants too; that would remove their independent combat control. If only an authored noncombat playlist is exempt, put the output override on that playlist and leave sibling combat routing through WMC_WorldMusic. During crossfades this isolates voices by routing rather than by a last-event flag. Check child output inheritance and transition material before choosing granularity.

Recommend proving the core mixer in prologue before authoring any exemption list. For the final behavior, prioritize the 7 proven shared-cue-resource cases and 5 associated Q cases for quest-placement/listening verification, and decide separately whether location themes, regional story-only worlds, music-box material and quest ambience should be preserved. A generic dialogue mute applied without that decision would suppress some intentionally selected location score. A SoundGameStateChange hook supplies no missing author-intent information and is not a solution to this exception problem.
