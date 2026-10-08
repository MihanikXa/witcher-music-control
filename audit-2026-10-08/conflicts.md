# Conflict matrix

**Historical first-pass matrix.** Exact paths/hashes remain valid for unchanged
original mod payloads. decisions.md and implementation.md give current status:
all original units have mechanisms or deliberate winners. AutoLoot's duplicate
scheduler and seven additional Steam-update override incompatibilities are
also corrected. The late Gwent package is excluded; two potential BIA scene
overlaps are documented in decisions.md. Earlier preservation/permission gates
below were superseded by the user's qualitative implementation authorization.

## Counting and confidence

**18 confirmed file/text conflict units plus 1 combat-behavior overlap requiring validation: 19 review units.** These comprise 5 same-path script conflicts, 8 quest/scene resource conflicts, 1 HUD resource conflict, 4 meaningful English string-ID conflicts, and 1 combat-behavior family. The combat family's three shared annotation targets are counted once to avoid inflating the total; its incompatible runtime outcome is not proven. Five script conflicts are covered by existing merges; one English string conflict has a staged patch; 12 confirmed conflicts and the combat overlap remain unresolved for preservation. “Covered” does not mean compiled or game-tested.

This is a complete matrix of detected file/resource collisions in the scanned loose payloads and bundle indexes, plus source-level annotations and localization IDs. It is **not a certification of all quest graphs, compiled scripts, cache semantics or runtime behaviors**. Further unknown interactions remain possible. Operational installation/control issues below are counted separately.

Current winners use explicit mods.settings priorities and the lower-number-first rule described in load-order.md. They are configured/predicted winners, not observed game-runtime results. Wrappers normally compose; they do not follow a single-file winner rule. DLC ordering and container-local cache behavior were not independently runtime-verified.

## Same-path WitcherScript

| ID | Path | Source mods | Winner | Classification / result |
|---|---|---|---|---|
| S1 | content/scripts/game/player/playerinput.ws | modBetterTorchesNextGen, modFriendlyHUD, modMovementTweaks | mod0000_MergedFiles (1) | Mergeable; existing merge preserves installed source changes; compile unverified |
| S2 | content/scripts/game/player/playerwitcher.ws | modAutoLoot, modFriendlyHUD, modGeraltOutfitWheel | mod0000_MergedFiles (1) | Mergeable; existing merge preserves installed source changes; compile unverified |
| S3 | content/scripts/game/player/r4player.ws | modBetterTorchesNextGen, modFriendlyHUD, modJumpInShallowWater | mod0000_MergedFiles (1) | Mergeable; existing merge preserves installed source changes; compile unverified |
| S4 | content/scripts/game/gui/hud/hud.ws | modFriendlyHUD, modGeraltOutfitWheel | mod0000_MergedFiles (1) | Mergeable; existing merge preserves installed source changes; compile unverified |
| S5 | content/scripts/game/gui/menus/inventorymenu.ws | modFriendlyHUD, modGeraltOutfitWheel | mod0000_MergedFiles (1) | Mergeable; existing merge preserves installed source changes; compile unverified |

## Bundled quests/scenes — high preservation risk

All eight pairs have different decompressed SHA-256 hashes, including the equally sized q103 phase. Neither hash equality nor byte size proves semantic compatibility; both versions also differ from the current vanilla baseline. All currently prefer **BIA priority 6 over UPR priority 14**, so UPR's overlapping modifications are shadowed.

The UPR author states BIA compatibility and requires UPR to take priority. That supports a candidate order, but does not establish which BIA 4.0.3 changes are retained in the installed UPR resource. No verified installed merged binary patch was found. The BIA public detailed sheet is v3.0, so its purpose mapping is historical context, not an exact 4.0.3 graph diff. Paths mapped to UPR features below are explicitly inferences where an exact author file-to-node mapping is unavailable. [UPR author page](https://www.nexusmods.com/witcher3/mods/12988), [BIA author page](https://www.nexusmods.com/witcher3/mods/11260), [BIA detailed changelog](https://docs.google.com/spreadsheets/d/1f5MsivPkYdr8_KLTLG2u2E2Jzjc7Mhaaffc1KT0B9LE/edit).

| ID | Exact resource path | Affected quest/system | Purpose evidence | Status |
|---|---|---|---|---|
| Q1 | gameplay/community/shops_and_craftsmen/skellige_shops_and_craftsmen.w2phase | Skellige shop/NPC community setup | UPR changes Kaer Muire blacksmith/Gwent timing; exact BIA node modification not mapped in available historical changelog. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q2 | quests/generic_quests/card_minigame_all_hubs/cg_card_minigame_meta.w2phase | Collect ’Em All / Gwent quest timing | UPR adjusts Gwent availability; historical BIA changelog prevents an automatically awarded Roach card starting the quest prematurely. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q3 | quests/minor_quests/novigrad/quest_files/mq3035_emhyr/phases/mq3035_wrap_up.w2phase | Reason of State wrap-up | UPR revises Dijkstra/Philippa aftermath; historical BIA changelog fixes missing warehouse doors after the quest. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q4 | quests/part_1/q103_daughter.w2phase | Family Matters | UPR changes optional Return to Crookback Bog handoff; historical BIA changelog restores fisherman-family action points after quest completion. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q5 | quests/part_1/quest_files/q103_daughter/scenes/q103_27_baron_final_talk.w2scene | Baron final conversation | UPR optional quest/dialogue transition; historical BIA changelog fixes optional-choice highlighting after Uma interrupts. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q6 | quests/part_2/q107_swamps.w2phase | Return to Crookback Bog | UPR delays/hides activation while preserving a later join path; historical BIA fixes involve dialogue/action points across this quest, exact phase-node correspondence unverified. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q7 | quests/part_2/q206_berserkers.w2phase | King’s Gambit | UPR changes Crach Gwent timing after massacre; historical BIA optional-content sheet restores Birna/Svanrige gameplay conversation on arrival at Kaer Trolde. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |
| Q8 | quests/part_2/quest_files/q206_berserkers/phases/q206_berserkers_attack.w2phase | King’s Gambit attack sequence | UPR Gwent/quest state timing inferred from quest and author description; exact BIA change not isolated in available source evidence. | Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only |

## Decompressed bundled hashes and sizes

### strings.list

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modACO-Giants | Mods\modACO-Giants\content\blob0.bundle | 3147 | 240144277fe02bc9a332912d26ff0ee38a7050a5eef1b0729a791c8e3f233958 |
| modACO-Leshens | Mods\modACO-Leshens\content\blob0.bundle | 2776 | 65441359a1497905044404642dada3b55337e7619dc7918bb525a333c0176f6a |
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 1059647 | 559aa80054ed7068dd346911f2f933a4e5fb01e6bbc06d493f57c16a46c2fee1 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 5040 | 28649bff2c2ec085e05dd2555748a4a9d5a5402c1c8db51e001ab1bc6297cf97 |
| dlcBloodAndSteel | DLC\dlcBloodAndSteel\content\blob0.bundle | 19 | dd7f21788e0936078538f5f3fa8c759b5811876455aaf1bb613ae0bf2ab75008 |
| dlcHoods | DLC\dlcHoods\content\blob0.bundle | 1403 | ec887544c2afa42daf0c8eda1369df6c3c3a0c1cef6152ea1bfbc42fd2d96e8f |
| dlcsharedutils | DLC\dlcsharedutils\content\blob0.bundle | 19 | dd7f21788e0936078538f5f3fa8c759b5811876455aaf1bb613ae0bf2ab75008 |

### gameplay/gui_new/swf/hud/hud_wolfstatbars.redswf

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modBestGsSchoolStances | Mods\modBestGsSchoolStances\content\bundles\bestgs_stance_hud.bundle | 512202 | f56fa177adfaf6775b4b2ef32c69fe4ba2a02d82f8f9c1d3c2e4e065fbddf302 |
| modSeamlessAdaptiveHUD | Mods\modSeamlessAdaptiveHUD\content\blob0.bundle | 1040303 | 98ca8a2c197b65cc4df11ee387f14519a529f231114d02c7ec0ffce816daa9a7 |

### gameplay/community/shops_and_craftsmen/skellige_shops_and_craftsmen.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 78469 | be23d5e145b590af8dfde5ca5233d259d2557acf137f2114668119af1e9c8363 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 79973 | 332d57bced7a3f2e5392af3ad691fdd5158a3c9b2a83229b32afc299a0e06168 |

### quests/generic_quests/card_minigame_all_hubs/cg_card_minigame_meta.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 68864 | db93c20dfc58f8057ae156652f1eb2522033aa7a85a23646e9662d49df17ef24 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 69013 | 99eb4bbb307fa1bf6397a66a7fe3c6d65f02ec52d0163d28aa0f10da113c6626 |

### quests/minor_quests/novigrad/quest_files/mq3035_emhyr/phases/mq3035_wrap_up.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 45063 | 7b6a63b4fa0b2f25f28c9e362875cac51df850e8ed92414ec5bfdec432f47a2d |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 50440 | 21c659469d0f0a75f25514ccf283eeeb8b46bade18acf1b7ed3088df029f5394 |

### quests/part_1/q103_daughter.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 861792 | b6bb7d8193fe4317089f1329d701f42c46e4afe78061c629353e7307ebc8532b |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 861792 | dc6a82582f437ef190e480b36554a53bd0e7a9f692f256a7cc551cec227fdde8 |

### quests/part_1/quest_files/q103_daughter/scenes/q103_27_baron_final_talk.w2scene

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 413564 | 59bb8bb25b5b7bb5a886c284aac47c672a7a3c8d0911391c20589bea1ee68cf7 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 413726 | 2cfc93ad4567639c793a9e20f6d496f94372f238233c8423a22e787b1d669627 |

### quests/part_2/q107_swamps.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 152053 | 882b1aefa25ed14cfa0440ea6aa9b584e64e957762b3f7b92e1cc9dae1ff0386 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 154087 | 894970a9fdcf0fabdc5287af46b6316b839e7e76212522b3368ef7ee650d2304 |

### quests/part_2/q206_berserkers.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 271776 | 0e56432c134c98b1a6719b366e8e852455b449aaac953444262eccc6f64aa164 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 271917 | 47cbfc06c58445558fd9ead1628728c05e0fa72f472eb396433b38c63a045303 |

### quests/part_2/quest_files/q206_berserkers/phases/q206_berserkers_attack.w2phase

| Owner | Bundle | Bytes | SHA-256 |
|---|---|---|---|
| modbrothersinarms | Mods\modbrothersinarms\content\blob0.bundle | 93123 | 0ef2967f03d21028d032dae2a7bef7a616de6641588268f60e09147159aeef72 |
| modunreasonableplotredesigned | Mods\modunreasonableplotredesigned\content\blob0.bundle | 93086 | 714f78a870efb9b4e2be804f06b42eec5b1dcc3c5c87570f9d05affc5614a127 |

## H1 — Wolf HUD Flash resource

modBestGsSchoolStances (priority 29) wins over modSeamlessAdaptiveHUD (33) for gameplay/gui_new/swf/hud/hud_wolfstatbars.redswf. Bestg requires mcWolfsHead.BG2_SetStance to display the selected school stance. SAH requires its artwork timelines and clips for custom health/stamina/toxicity/sign/medallion presentation. Its loose wolfstatbars copy is byte-identical to its bundled copy, so it does not supply a combined variant. The independent hud_buffs resource does not resolve the wolfstatbars collision.

Giving SAH priority can lose Bestg's stance display/function; leaving Bestg first can lose SAH artwork/timeline behavior. Source checks establish different resource contracts, not a proven crash. This requires a combined Flash resource or an explicit feature trade-off. No verified compatibility patch was found in the installed payload or author material consulted. A supported Flash source/export pipeline and CR2W packaging are needed; extraction alone is insufficient. [Bestg author page](https://www.nexusmods.com/witcher3/mods/13595), [SAH author page](https://www.nexusmods.com/witcher3/mods/13194).

## English localization IDs

Grammar of the Path (5) currently wins all five repeated IDs over BIA (6) or UPR (14). The .w3strings indexes share the relevant English language key pair. Four differences alter text meaning/content; one is whitespace only.

| ID | Owners | Difference / feature loss | Status |
|---|---|---|---|
| L1092187 | modbrothersinarms, modZ_GrammarOfThePathRemastered | BIA: “a sylvan”; Grammar: “Allgod”. Naming/content choice; cannot retain two replacements of one line. | Unresolved decision |
| L1130095 | modbrothersinarms, modZ_GrammarOfThePathRemastered | BIA: future threat “will be”; Grammar: present “is”. Editorial decision. | Unresolved decision |
| L391138 | modbrothersinarms, modZ_GrammarOfThePathRemastered | Grammar adds the preceding Fayrlund casualty sentence to BIA’s ambush line. Verify dialogue/audio/subtitle segmentation before choosing. | Unresolved decision |
| L558403 | modbrothersinarms, modZ_GrammarOfThePathRemastered | Only removes a space before a closing brace; harmless cosmetic overlap. | Harmless |
| L1063514 | modunreasonableplotredesigned, modZ_GrammarOfThePathRemastered | Grammar hides UPR’s expanded Blood Ties letter. One-ID staged patch preserves the expansion and corrects four grammar/spacing issues. | Staged |

The remaining 18 language-key overlaps are the shared “Mods” menu-root key 0x4d5f8b0c, an intentional common label, not 18 independent functionality losses. No repeated string IDs were found outside the five English IDs among installed Mods/DLC localization indexes. Text decoding was performed for the overlapping English IDs, not every translated string.

strings.list is REDkit-generated JSON bookkeeping (file/string ID lists), not the .w3strings runtime text database. Its seven owners are listed with hashes above; the BloodAndSteel/sharedutils DLC copies are identical. Treat the Script Merger warning as harmless bookkeeping overlap, not a seven-way localization merge request. DLC's single strings.list winner is not established and is immaterial to runtime text. This interpretation is supported by its content and mod-developer guidance; do not delete it merely to hide warnings. [Developer guidance](https://www.nexusmods.com/witcher3/mods/7175?tab=posts).

## C1 — Combat speed / stance / animation behavior

Bestg, Combat Speed and BloodAndSteel modify combat animation/timing behavior. Bestg and Combat Speed share OnCombatActionStart, OnCombatActionEnd and SetIsCurrentlyDodging; Combat Speed replaces the last method while Bestg wraps it. Separate multipliers and resets can compose incorrectly even if compilation succeeds. Bestg's author discourages combining animation-speed overhauls. BloodAndSteel's relevant code is compiled-only here, so the full interaction cannot be patched reliably from available loose sources.

Classification: overlapping behavior requiring supported sources/compatibility patch or an explicit choice of intended behavior. This is one conflict family, not three additional file conflicts. It may cause timing, dodge, targeting or responsiveness defects; a crash was not demonstrated. Do not disable any mod or sacrifice animations automatically.

## Shared annotation targets — full matrix

23 target methods have multiple owners. An annotation collision alone is not a duplicate definition: wrappers generally call the chain and Sharedutils intentionally provides dependency methods. No pair of replaceMethod annotations targets the same method in the scanned loose source. No unrelated-file duplicate class/struct/enum was established; repeated vanilla declarations are covered by same-path winners.

| Target | Owners / annotation / source line | Assessment |
|---|---|---|
| CR4PlayerStateCombat.OnComboAttackCallback | modBestGsSchoolStances: wrapMethod @ 55; modResponsiveMovement: wrapMethod @ 857 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| W3DamageManager.ProcessAction | modBestGsSchoolStances: wrapMethod @ 120; modHitLag: wrapMethod @ 6 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CPlayerInput.Initialize | modBestGsSchoolStances: wrapMethod @ 7; modbrothersinarms: wrapMethod @ 65 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4Player.OnCombatActionStart | modBestGsSchoolStances: wrapMethod @ 122; modCombatSpeed: wrapMethod @ 204 | C1 speed/reset interaction |
| CR4Player.OnCombatActionEnd | modBestGsSchoolStances: wrapMethod @ 143; modCombatSpeed: wrapMethod @ 211 | C1 speed/reset interaction |
| CR4Player.SetIsCurrentlyDodging | modBestGsSchoolStances: wrapMethod @ 154; modCombatSpeed: replaceMethod @ 4 | C1 speed/reset interaction |
| W3PlayerWitcher.DrinkPreparedPotion | modBestGsSchoolStances: wrapMethod @ 99; modbrothersinarms: wrapMethod @ 50 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4Player.OnSpawned | modbrothersinarms: wrapMethod @ 1; modbrothersinarms: wrapMethod @ 13; modCombatSpeed: wrapMethod @ 28; modHoods: wrapMethod @ 8; modMonsterHuntContracts: wrapMethod @ 174 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4IngameMenu.SU_onMenuEntered | modbrothersinarms: wrapMethod @ 153; modzzz_sharedutils: addMethod @ 23 | Intentional Sharedutils dependency / wrapper composition; runtime unverified |
| CR4GlossaryBooksMenu.PopulateListData | modbrothersinarms: wrapMethod @ 9; modzzz_sharedutils: wrapMethod @ 27 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| W3GuiBaseInventoryComponent.SetInventoryFlashObjectForItem | modbrothersinarms: wrapMethod @ 1; modHoods: wrapMethod @ 33 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CEntity.PlayEffectSingle | modbrothersinarms: wrapMethod @ 17; modULTRAplussVaxisBlood: wrapMethod @ 1463 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| W3PlayerWitcher.OnSpawned | modIgniWaterFx: wrapMethod @ 26; modMovementTweaks: wrapMethod @ 13 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4IngameMenu.showOptionsPanel | modIgniWaterFx: wrapMethod @ 34; modSeamlessAdaptiveHUD: wrapMethod @ 125 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4IngameMenu.ShowDeveloperMode | modIgniWaterFx: wrapMethod @ 191; modModSettingsMenuFix: wrapMethod @ 199 | Better IGNI and Menu Fix both repair menu rows; redundant repair, idempotence needs UI testing |
| CR4HudModuleQuests.SendObjectives | modMonsterHuntContracts: wrapMethod @ 627; modSeamlessAdaptiveHUD: wrapMethod @ 178 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4HudModuleMinimap2.OnConfigUI | modMonsterHuntContracts: wrapMethod @ 805; modzzz_sharedutils: wrapMethod @ 33 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4Game.OnAfterLoadingScreenGameStart | modMonsterHuntContracts: wrapMethod @ 186; modzzz_sharedutils: wrapMethod @ 25 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4HudModuleDialog.OnDialogOptionSelected | modMonsterHuntContracts: wrapMethod @ 525; modzzz_sharedutils: wrapMethod @ 4 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4HudModuleDialog.OnDialogOptionAccepted | modMonsterHuntContracts: wrapMethod @ 543; modzzz_sharedutils: wrapMethod @ 10 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4MapMenu.UpdateUserMapPins | modMonsterHuntContracts: wrapMethod @ 906; modzzz_sharedutils: wrapMethod @ 15 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4LocomotionPlayerControllerScript.UpdateLocomotion | modMovementTweaks: wrapMethod @ 23; modResponsiveMovement: wrapMethod @ 497 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |
| CR4IngameMenu.OnOptionValueChanged | modSeamlessAdaptiveHUD: wrapMethod @ 132; modzzz_sharedutils: wrapMethod @ 148 | Wrapper overlap; no proven source-level incompatibility; runtime chain unverified |

## Configuration, dependencies and operational findings (separate from 19)

O1, medium: Arrow Deflection is misdeployed; corrected layout staged, runtime validation pending.

O2, medium: manual Outfit Wheel has no mods.settings entry. Its existing merge is present and F3 OWToggle bindings exist, but relying on implicit order is avoidable. Explicit entry staged as a proposal.

O3, medium: empty Script Merger MergeInventory.xml does not track the five live merges. Rebuild provenance on a copy with current sources; do not regenerate live output blindly.

O4, high uncertainty: unowned vanilla content/metadata.store differs from Steam. Source and semantic correctness unresolved; not classified as a confirmed mod collision or repaired.

O5/O6, functionality: FriendlyHUD's sample input fragment contains 32 actions absent from live input.settings (2 sample actions are present); Hoods' ToggleArdHood action is absent. This means the documented custom shortcuts are not configured, even though scripts/menu resources exist. Sample IK_9 also conflicts between FriendlyHUD's item shortcut and Hoods' toggle; controller bindings may overlap. Defaults are examples, not permission to overwrite the user's controls. A binding plan requires selection of keys/context and checking every existing assignment. Missing saved FriendlyHUD preference keys may simply use script defaults and are not independently a fault. Evidence: input-action-check.json and input-fragment-check.json.

29 installed config XML files parse correctly. Vortex's merged input.xml retains all FriendlyHUD input Var attributes; duplicate Group id Hidden in input.xml/hidden.xml is a shared grouping, not an identified lost variable. Other mod menu groups have no cross-file repeated IDs. No new gameplay XML collision was found between mod bundles; Over9000 replaces vanilla abilities intentionally, and Weight is complementary.

FriendlyHUD and SAH both control HUD visibility/markers; Movement Tweaks and Responsive Movement both influence locomotion. Their source hooks can compose, but desired visual/feel behavior needs game testing. Monster Hunt/Sharedutils hooks are intentional dependency overlap. Existing DLC resources and caches need runtime mounting checks; no extra cross-mod bundled collision beyond the ten indexed paths was detected. Bundled references, precompiled blobs and native injection behavior have not been fully semantically decoded.

4542 distinct mod resource paths override vanilla assets; these are intentional replacements unless another installed mod replaces the same resource. This count is not added to functional conflicts. See evidence/vanilla-mod-overrides.json and vanilla-collision-baselines.json for exact resources/current baselines.
