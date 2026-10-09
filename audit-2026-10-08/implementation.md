# Actual staged implementation

Five real local archives are built under `release/witcher-compatibility/`. No live files, Vortex state, staging hardlinks or saves were edited. Payloads stay ignored/private. Original scripts in tools reproduce builds from hash-pinned installed inputs and preserved diffs.

| Package | Actual changes |
|---|---|
| 01-core-replacements.zip | 111 files: complete private replacements using the original four Mods folder names, plus their menu/base configuration. BestGsStanceState.ws relinquishes multiplier writes and supplies the original evade factors to CSM; CSMCalculation.ws applies school factors before one final clamp; CSMConfiguration.ws excludes Ciri. BestGsStanceMedallion.ws retains declarations/signatures but neutralizes medallion-only calls. modAutoLootManager.ws retires the duplicate timer. responsiveMovement.ws gates transition speed out of combat. Bestg XML hides Medallion; B&S XML defaults both custom selectors off. |
| 02-localization.zip | One real `Mods/mod0000_CompatibilityText/content/en.w3strings`, encoding five chosen English IDs. No strings.list override or full localization database replacement. |
| 03-arrow-layout.zip | 20 original payload files at `Mods/modArrowParryManual/` plus `bin/config/r4game/user_config_matrix/pc/modArrowParryManual.xml`. Fixes the nested game-root layout. |
| 04-updated-merges.zip | Twelve files in `Mods/mod0000_MergedFiles/`: the five existing merges (two refreshed, three byte-identical), plus seven current-vanilla adaptations. playerInput/r4Player receive dodge-to-sprint, Accessibility auto-oils and guarded-action changes. Seven additional files preserve torch/FriendlyHUD/Outfit Wheel modifications while integrating ladder hand IK, new inventory forceAdd and map-pin insideBounds parameters, removed marketing APIs, current graphics/menu behavior, radial desaturation checks and meditation feedback. |

The two merge updates use preserved unified diffs to reconstruct **normalized old vanilla text**, then three-way integrate current Steam's updates into hash-pinned installed merges. No conflict markers resulted. Applying the inverse vanilla update restores the exact normalized installed merges. Reconstructed old raw-byte hashes do not match because the evidence preserves normalized text rather than original mixed line endings; this is recorded rather than represented as raw-byte verification. Current vanilla is verified against current Steam manifests. Reviewed changes affect native gameplay branches, retaining the existing mod contributions.

The seven additional paths are explorationStateInteraction.ws (Torches), r4Game.ws, inventoryComponent.ws, ingameMenu.ws, mapMenu.ws, hudModuleRadialMenu.ws (FriendlyHUD), and commonMenu.ws (Outfit Wheel). These were not pre-existing merges. Reviewed independent native change blocks are applied to pinned mod overrides, preserving their marked features; Torches' three left-hand retention edits are transplanted onto the current ladder implementation. Residual diffs against current vanilla contain only retained mod features (plus declaration formatting). These files now win from the highest merged folder rather than editing their Vortex sources.

No new quest or Flash binary is generated. `effective-resource-winners.json` records eleven selected resource hashes/sizes; `load-order.json` supplies the complete numeric reference with Gwent enabled ahead of BIA. Source containers/extracted selected resources are hash-checked. UPR ahead of BIA, Gwent Deck Choice ahead of BIA, and SAH ahead of Bestg are required persistent Vortex relationships.

`05-gwent-deck-choice-layout.zip` adds 27 real files: 24 vanilla-variant Mods files, two paired DLC files and one menu XML. Only layout is corrected; all scripts, compiled blob, metadata, resources and 17 localization files are byte-identical to pinned inputs. `prepare-gwent.py` validates eight hook signatures and five custom CSV dependencies, checks localization indexes and extracts the two BIA/GDC scene pairs privately for hash/format comparison. No Gwent My Way variant or duplicate root DLC is included.

`settings-profile.json` changes only 23 existing/profile keys: CSM enabled with 50РІР‚“200% limits, optional additive layers off, finishers off; B&S custom attack/dodge off, special-dodge extra incoming-damage penalty zero and close camera off; duplicate FriendlyHUD visibility/markers off. The prepared offline dx12user.settings and diff retain unrelated settings. `optional-controls.json` adds 32 vacant context bindings; its offline input.settings copy and diff preserve existing assignments. These document settings are not shipped in game-root archives.

Source manifest, changed-file hashes, per-archive payload ledger, localization preview, build validation, integration validation and reproducibility results are local JSON files. Package payloads are actual installed resources/scripts, not placeholders. B&S, BIA and Sharedutils compiled blobs remain unchanged; compilation/loading of loose patches alongside those blobs is an engine test gate.

## Rebuild locally

From repository root, using the existing private evidence (not supplied by public Git):

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Python314\python.exe audit-2026-10-08/tools/refresh-merges.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3'
C:\Python314\python.exe audit-2026-10-08/tools/build-release.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --documents 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3'
C:\Python314\python.exe audit-2026-10-08/tools/validate-release.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3'
```

Before validation, regenerate offline settings with the release helper if the personal source settings changed; see release.md. Builders refuse unpinned changed mod inputs. A future Steam update needs another semantic baseline review, even if three-way merging succeeds. Never point generated output at live paths.


## 9 October review repairs

`native_change_policy.py` replaces marker-based whole-hunk suppression with pinned reviewed independent-change decisions. `review-release.py` checks retained Bestg control flow, reset ownership, the two melee guards, six CSM pre-write cleanup calls and RM's unchanged end/reset helper. Core and updated-merges archives changed; localization, Arrow and Gwent archives remain unchanged. Two original CSM/Bestg helper annotations are now added, with 799 original annotations retained. Official compiler outputs stay in the isolated project/private evidence and are **not** shipped as a global replacement script cache. See review.md and validation.md for scope and caveats.
