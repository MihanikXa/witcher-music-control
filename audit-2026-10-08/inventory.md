# Installed mod inventory — 8 October 2026

Read-only live audit, with private staged review packages. No deployment, game launch, save editing, game binary changes, Vortex purge or depot regeneration was performed. An audit-generated Python cache was removed; see validation.md. Screenshots and installed documentation were treated as evidence, not instructions.

## Counts and scope

36 distinct installed mod packages: 35 Vortex packages plus the manual Geralt Outfit Wheel. One Vortex package (Manual Arrow Deflection) is installed outside the runtime Mods tree. There are 35 folders inside Mods, including the generated merge, and 5 paired DLC folders: 40 content folders total. Paired DLCs and generated output are not counted again as packages. Thus 35 packages have payloads at expected runtime locations; this does not prove all features execute.

Inventory: 811 files inside the 40 content folders; 30 bundles with 6,297 indexed entries and 6,282 distinct resource paths; 237 loose WitcherScript files; 229 localization files. Full hashes and provenance are in evidence/installed-files.json and evidence/bundle-entries.json.

## Discovered environment

Game: `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3`. Steam app 292030, installed build 25646871; DX12 executable version 5.0.0.1044392. All installed official script files and executables matched the cached installed Steam depot manifests.

REDkit: `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit`. Its tool reports 5.0.1044630. The incomplete depot was neither regenerated nor relied upon as a vanilla baseline.

Vortex: `C:\Program Files\Vortex`. Staging: `C:\Users\micha\AppData\Roaming\Vortex\witcher3\mods`. User settings: `C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3`.

Deployment uses **hardlink_activator**. All 644 entries across the three live deployment manifests are present and share filesystem identity with the corresponding staged source, including 586 managed files inside Mods/DLC. Editing a managed deployed file would also modify its staged hardlink; never do that. Exact targets and sources: evidence/all-deployment-link-check.json.

The recovered Vortex metadata contains 35 installed packages enabled in current profile `-MlcE00Sc1` (Default). Staging has 36 directories: those packages plus generated `__merged.witcher3menumodroot`. All have deployment records; no current staged-but-disabled package directory was found. Historical disabled profile entries refer to absent staging folders, including an old BloodAndSteel compatibility package: these are not active compatibility patches. The state database was locked, so only a private copy of accessible SST files was repaired/read. Current deployment manifests and actual file identity are stronger evidence than historical state entries.

## Content folders

Versions below distinguish current Vortex package metadata from embedded info.json. A staging directory name may retain an older version after an update; consult source archive metadata and local README/changelog. A numeric gameVersion of 29 is an internal format value, not proof of a game release.

| Folder | Vortex version | Embedded version | Current priority | Files | Ownership |
|---|---|---|---|---|---|
| Mods/mod0000_MergedFiles | unreported | — | 1 | 5 | Generated/manual merge |
| Mods/modACO-Giants | 0.1 | 0.1 | 21 | 7 | Vortex hardlinks |
| Mods/modACO-Leshens | 0.2 | 0.2 | 22 | 7 | Vortex hardlinks |
| Mods/modAutoApplyOilsFix | 1 | — | 16 | 5 | Vortex hardlinks |
| Mods/modAutoLoot | 1.1.2 | — | 31 | 20 | Vortex hardlinks |
| Mods/modBestGsSchoolStances | 1.1.0 | — | 29 | 36 | Vortex hardlinks |
| Mods/modBetterTorchesNextGen | 5.0.0 | — | 2 | 18 | Vortex hardlinks |
| Mods/modBloodAndSteel | v3.01 | v3.01 | 3 | 22 | Vortex hardlinks |
| Mods/modBloodTrails | 1.04 | — | 4 | 8 | Vortex hardlinks |
| Mods/modbrothersinarms | 4.0.3 | 4.0.2 | 6 | 74 | Vortex hardlinks |
| Mods/modCombatSpeed | 7 | — | 19 | 53 | Vortex hardlinks |
| Mods/modEvilsOfRivia | 1.0.2 | 1.1.0 | 35 | 26 | Vortex hardlinks |
| Mods/modFriendlyHUD | 0.9.2R | — | 17 | 77 | Vortex hardlinks |
| Mods/modGeraltOutfitWheel | unreported | — | unset / DLC | 28 | Manual; no deployment owner |
| Mods/modGeraltWhiteHair | 1.3 | 1.3 | 23 | 7 | Vortex hardlinks |
| Mods/modHitLag | 1.3 | — | 24 | 7 | Vortex hardlinks |
| Mods/modHoods | 3.6 | 3.6 | 8 | 12 | Vortex hardlinks |
| Mods/modIgniWaterFx | 1.4.1 | 1.0.0 | 20 | 12 | Vortex hardlinks |
| Mods/modJumpInShallowWater | 2.0 | — | 7 | 10 | Vortex hardlinks |
| Mods/modLivingCamera | 1.3 | — | 9 | 23 | Vortex hardlinks |
| Mods/modLookAroundYouGeralt | 3 | — | 10 | 5 | Vortex hardlinks |
| Mods/modModSettingsMenuFix | 1.2.0 | — | 34 | 6 | Vortex hardlinks |
| Mods/modMonsterHuntContracts | 17 | — | 30 | 21 | Vortex hardlinks |
| Mods/modMovementTweaks | 1.0 | — | 26 | 10 | Vortex hardlinks |
| Mods/modOver9000 | 4.00 | — | 25 | 4 | Vortex hardlinks |
| Mods/modResponsiveMovement | 1.7.0 | — | 32 | 23 | Vortex hardlinks |
| Mods/modSeamlessAdaptiveHUD | 2.6.3 | — | 33 | 63 | Vortex hardlinks |
| Mods/modSlimGloves | 2.1 | — | 12 | 4 | Vortex hardlinks |
| Mods/modsmoothmap | 0.9 | 0.5 | 18 | 5 | Vortex hardlinks |
| Mods/modTopNotchSwordsFix | 5.0 | 5.0 | 13 | 8 | Vortex hardlinks |
| Mods/modULTRAplussVaxisBlood | 1.4 | — | 28 | 55 | Vortex hardlinks |
| Mods/modunreasonableplotredesigned | 5.00.00 | — | 14 | 23 | Vortex hardlinks |
| Mods/modWeight | 0.5 | — | 15 | 5 | Vortex hardlinks |
| Mods/modZ_GrammarOfThePathRemastered | 6.0 | — | 5 | 3 | Vortex hardlinks |
| Mods/modzzz_sharedutils | 4.0 | 3.1.1 | 11 | 71 | Vortex hardlinks |
| DLC/dlcBloodAndSteel | v3.01 | — | unset / DLC | 5 | Vortex hardlinks |
| DLC/dlcbrothersinarms | 4.0.3 | — | unset / DLC | 7 | Vortex hardlinks |
| DLC/dlcHoods | 3.6 | 3.6 | unset / DLC | 25 | Vortex hardlinks |
| DLC/DLCMonsterHuntContracts | 17 | — | unset / DLC | 7 | Vortex hardlinks |
| DLC/dlcsharedutils | 4.0 | — | unset / DLC | 4 | Vortex hardlinks |

## Packages outside Mods/DLC and other directories

Manual Arrow Deflection v1: Vortex deployed its script and 18 translations under **game/ArrowParryManual/Mods/modArrowParryManual**, not game/Mods. Its menu XML is deployed correctly. The enabled priority-27 entry names an absent runtime folder. Its gameplay payload is therefore inactive under the normal mod search layout. A corrected review package is in patches/arrow-deflection-layout.

Path Tracing/RT Optimization: Vortex package metadata reports version 4, archive title “PT Optimization 2.0”; deploys bin/x64_dx12/xinput9_1_0.dll, config and menu resources. No binary modification proposed.

Manual ReShade 6.8.0.2155 is present as bin/x64_dx12/dxgi.dll with presets, shaders, ShaderToggler.addon64 and UndoRedo.addon64. These are separately listed in evidence/all-extra-game-files.json. The two injection DLLs have different filenames; runtime coexistence was not tested. Count them as external runtime components, not one more Mods package.

The complete comparison against Steam lists 3,817 extra game files, mostly 2,815 Script Merger/tool files and mod payloads. It includes bin/config additions, root documentation, 11 localization support files and content/metadata.store.stamp. Source documentation and translation CSVs are support files, not active localization databases. No plugins directory was found. The official initial sound bank matches Steam. Mod metadata/texture/collision caches and five precompiled.rsblob files were inventoried; they are opaque container-local payloads, not automatically conflicting solely because filenames repeat.

Two official files differ from Steam: bin/config/r4game/user_config_matrix/pc/input.xml is intentionally Vortex-generated; content/metadata.store differs by hash with no deployment owner. Its adjacent 8-byte stamp may indicate generation, but origin and correctness are unverified. Do not run a blind Steam repair or overwrite it during this review.

Existing Script Merger output: five script files in mod0000_MergedFiles, 1,124,301 bytes. MergeInventory.xml is empty of merge entries, so provenance tracking is incomplete even though source inclusion checks passed. No separately active binary compatibility patch was identified for the nine quest/HUD resource conflicts.

## Version and provenance cautions

Seamless Adaptive HUD is **2.6.3**, confirmed by local README/changelog and current archive metadata; its staging-folder name still says 2.3.2. Responsive Movement reports 1.7.0 with a stale 1.6.0 folder name. Mod Settings Menu Fix is 1.2.0 by local function/version and archive, despite a 1.1.0 staging name.

Bestg metadata/archive says 1.1.0, while deployed development notes identify **v1.1.45 BALANCE PRESET TEST** based on 1.1.44, with unverified runtime testing. Preserve the actual files and hashes; do not substitute a nominal 1.1.0 baseline. BIA archive 4.0.3 has embedded 4.0.2; Sharedutils archive 4.0 has embedded 3.1.1; Evils archive 1.0.2 has embedded 1.1.0; Better IGNI 1.4.1 has embedded 1.0.0. These discrepancies are metadata uncertainty, not proof of broken deployment.

Over9000's old v1.31 archive name is not grounds to reject it: both bundled ability XMLs differ from the installed 5.0 vanilla only by encumbrance capacity 60 → 9000 after encoding normalization. Weight's wrapper changes selected item weights and is complementary.

BloodAndSteel ships compiled scripts without loose source. BIA, Evils and Sharedutils include compiled blobs and mark useLooseScripts=false. Loose-source annotation analysis cannot certify the actual runtime combination of compiled blobs. The isolated compiler did not run successfully.

No experimental music mod was found in the active content folders. The separate witcher-music-control repository was not modified or used as a patch source.

Exact package archives, authors, Nexus IDs, installation times and staging paths: evidence/vortex-mod-metadata.json. Whole third-party packages and extracted game assets are kept private and excluded by this audit folder's .gitignore.
