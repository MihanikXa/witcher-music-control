# Load order and actual overwrite rules

**Release order:** keep mod0000_MergedFiles first (now 12 reviewed paths), then
mod0000_CompatibilityText; UPR must precede BIA, SAH must precede Bestg, and
Outfit Wheel must be explicitly enabled. The corrected complete Gwent Deck Choice
package is enabled ahead of BIA (UPR also remains ahead of BIA). Original numeric tables below
are historical; the authoritative complete reference is local
release/witcher-compatibility/load-order.json. Persist the relationships in
Vortex and inspect generated mods.settings after each deployment. See
release.md for exact steps; previous conditional trade-off gates are superseded.

## Evidence

Lower numeric Priority wins for explicitly configured Mods. This was checked against the installed Vortex Witcher plugin (ascending numbers, merged output locked at the top), primary Script Merger source (LoadOrderComparer ascending priority; explicitly configured enabled candidates preferred), and the CDPR-forum-hosted mods.settings guide. Default unset order is case-insensitive alphanumeric according to these tools; the current 5.0 engine was not launched to empirically verify unspecified/default/DLC precedence. [Script Merger source](https://github.com/IDCs/WitcherScriptMerger), [mods.settings guide](https://forums.cdprojektred.com/index.php?attachments/mods_settings-pdf.6711517/).

Priority chooses a complete resource, not a union of its changes. Annotation wrappers generally compose around a target; replacing methods and compiled script integration need semantic checks, not merely sorting folder names. DLC folders are excluded from Vortex's mods.settings generation, so assigning a DLC entry is not a verified DLC conflict solution.

## Current explicit order

All 35 recorded sections are enabled with unique priorities. Outfit Wheel is absent; Arrow's enabled entry names a folder outside the Mods search path. Local mod loading is enabled in dx12user.settings.

| Priority | Section | Effective note |
|---|---|---|
| 1 | mod0000_MergedFiles | Enabled |
| 2 | modBetterTorchesNextGen | Enabled |
| 3 | modBloodAndSteel | Enabled |
| 4 | modBloodTrails | Enabled |
| 5 | modZ_GrammarOfThePathRemastered | Enabled |
| 6 | modbrothersinarms | Enabled |
| 7 | modJumpInShallowWater | Enabled |
| 8 | modHoods | Enabled |
| 9 | modLivingCamera | Enabled |
| 10 | modLookAroundYouGeralt | Enabled |
| 11 | modzzz_sharedutils | Enabled |
| 12 | modSlimGloves | Enabled |
| 13 | modTopNotchSwordsFix | Enabled |
| 14 | modunreasonableplotredesigned | Enabled |
| 15 | modWeight | Enabled |
| 16 | modAutoApplyOilsFix | Enabled |
| 17 | modFriendlyHUD | Enabled |
| 18 | modsmoothmap | Enabled |
| 19 | modCombatSpeed | Enabled |
| 20 | modIgniWaterFx | Enabled |
| 21 | modACO-Giants | Enabled |
| 22 | modACO-Leshens | Enabled |
| 23 | modGeraltWhiteHair | Enabled |
| 24 | modHitLag | Enabled |
| 25 | modOver9000 | Enabled |
| 26 | modMovementTweaks | Enabled |
| 27 | modArrowParryManual | Absent runtime Mods folder |
| 28 | modULTRAplussVaxisBlood | Enabled |
| 29 | modBestGsSchoolStances | Enabled |
| 30 | modMonsterHuntContracts | Enabled |
| 31 | modAutoLoot | Enabled |
| 32 | modResponsiveMovement | Enabled |
| 33 | modSeamlessAdaptiveHUD | Enabled |
| 34 | modModSettingsMenuFix | Enabled |
| 35 | modEvilsOfRivia | Enabled |

## Required relationships and review candidate

mod0000_MergedFiles stays ahead of all five same-path script sources. The staged tiny AuditCompat localization patch must precede Grammar/UPR for ID 1063514. Outfit Wheel should have an explicit enabled entry; its same-path script additions already occur in merged output. Correct Arrow's layout before its priority can have an effect.

Current BIA(6) > UPR(14) hides eight UPR resources. Candidate UPR > BIA follows author guidance but has an unresolved BIA preservation gate. The full candidate renumbers all entries uniquely, keeps the existing merge first, inserts AuditCompat second, places UPR directly ahead of BIA and appends explicit Outfit Wheel. It is not approved for deployment.

Current Bestg(29) > SAH(33) selects Bestg's wolfstatbars resource. Reversing these numbers exchanges the feature loss; there is no order that retains two distinct replacements of one resource. A combined supported resource is needed for both.

Current Grammar(5) > BIA(6)/UPR(14) controls five English IDs. The tiny patch changes one winner intentionally; the other four remain unchanged, including one cosmetic overlap. BIA/UPR reordering does not solve their separate Grammar overlaps.

The existing Vortex-generated input.xml is the winner for PC controls and matches its staging hardlink. All FriendlyHUD XML Var records are retained. Other config files have independent paths/groups. Do not overwrite this managed merged file from a mod archive.

No duplicate numeric priorities were found. Existing Sharedutils/BIA dependency hooks must remain available; priority changes must not remove dependency payloads or replace script merges with partial sources. No active compatibility patch was found whose resource winner would become redundant through the safe staged one-ID localization change.

Revalidate actual deployed mods.settings after every Vortex deployment. Vortex rewrites the file from its order; a manual one-time edit is not persistent ownership-safe configuration. The candidate is a review diff, not a standalone deployment mechanism.
