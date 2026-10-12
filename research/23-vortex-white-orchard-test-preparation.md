# 23 — Vortex White Orchard test archives and confirmation boundary

Date: 2026-10-12. **Both archives are prepared and verified. Nothing was installed, activated, deployed or launched.** A dedicated profile is specified in a private clone draft but has **not been created in Vortex**. Save isolation and explicit approval remain prerequisites. No native Init, existing mod configuration, save location, DLC, loader DLL, licence or authoring project was changed. No new bank generation.

## Artifacts and exact placement

Machine-local evidence root E: `C:\Dev\witcher-music-control\build\vortex-white-orchard-preparation`. Installed Vortex V: `C:\Program Files\Vortex`. Vortex data D: `C:\Users\micha\AppData\Roaming\Vortex`. Game G: `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3`.

Archives:

- `E\archives\WMC White Orchard — Vanilla Control.zip`
- `E\archives\WMC White Orchard — Music Control Test.zip`

Each has exactly one ZIP member:

```text
Mods/modWMCBankLoadingTest/content/soundspc.cache
```

No parent title folder, second Mods level, Init, WEM, script, README, Wwise project, audio source or licence information. Separately identifiable ZIP/display names deliberately share the **same destination**:

`G\Mods\modWMCBankLoadingTest\content\soundspc.cache`

| Variant | Source evidence | Cache SHA-256 | ZIP SHA-256 / bytes |
|---|---|---|---|
| A: Vanilla Control, native ProjectID39 | report20 control package | `f7a0c2c20d698d4dbb514e573c64d67df7e9c57ab854012bd0adc6b4afdde40a` | `9fd4f8776ec0a05b37e481ae59900215565054a04d17fff8571b0681ef93dddb` /87574 |
| C: Music Control Test, ProjectID17637 | report22 candidate package | `a2b8cc23285c5b6cd392b0301328d75bd545dde8d9e0c06007b674b68a14aa12` | `8e4a00259421b902e93e232149f868bd3c1008657ac933ff0d1aaa6e5c123d9a` /87617 |

Observed: source hashes match reports20/22, ZIP CRC passes and extracted bytes equal the original cache exactly. The bank payload hashes remain A=`75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912` and C=`80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698`. Existing A/B/C directories remain intact.

Reproduction: `tools/white_orchard_vortex_archive.py:archives`, run `python tools/white_orchard_vortex_archive.py archives --output build/<fresh-directory>`. Fresh output required. `E\archives\archives-verified.json` records hashes, member path and nondeployment status. ZIP contents are not committed.

## Installed installer and conflict proof

Observed Vortex version **2.9.0-beta.1**, bundled Witcher3 extension **1.7.5**. Actual installed code is `V\resources\app.asar.unpacked\bundledPlugins\game-witcher3\index.cjs` (SHA-256 `52de6d815469d6361d72b94a11bfff79527b3846e644c2f8d471bbf2efcc3983`); its matching source map and selected core sources were read/copied to ignored E/`installer-evidence`. No extension was installed/updated.

Relevant mapped sources under E/`installer-evidence/mapped-source`:

- `installers.ts:239`, `testSupportedTL`: accepts files with a Mods path segment. `installTL:250` retains root Mods when already at archive root.
- `modTypes.ts:16`, `testTL`: Mods-root copy instructions select the top-level type, barring menu patterns.
- `index.ts:245/261`: registers this installer/type. `util.ts:75`, `getTLPath`: resolves top-level deployment to the discovered game root, **not** its Mods subfolder. Default `queryModPath:211` is Mods, but that default is overridden for this archive's type.
- `common.ts:135`, `DO_NOT_DEPLOY`: excludes README/part-setting files; it does not exclude soundspc.cache.

An offline Node harness executed these installer/mod-type function bodies from the installed source map with TypeScript annotations removed and the actual common constants, using Windows path semantics. It returned one unchanged copy destination `Mods\modWMCBankLoadingTest\content\soundspc.cache`, `supported:true`, `topLevelModType:true`. E/`installer-evidence/installer-path-{harness.cjs,result.json}` records the check. This proves routing logic for the selected file list; **no full Vortex installation/deployment was invoked**. Installation must still confirm the resulting type/path in the real UI.

Both mod entries would collide on the same file. With the observed **hardlink_activator**, Vortex controls which staged payload supplies that target; changing that file manually could also change a staged hardlink. Therefore use Vortex enable/disable/deploy, never edit the deployed cache. Do **not** depend on a before/after rule with both entries enabled: it can hide a wrong winner. No persistent conflict rule is needed when only one is enabled. If a conflict prompt appears with both enabled, cancel/review and correct exclusivity. File merging is neither requested nor claimed.

## Current setup, isolation and backups

Read-only profile-state inspection plus the closed-state write batches identifies four Witcher3 profiles: **Default** (two distinct profile records), **Witcher Compatibility Test**, and **Ink & Iron Integration Test**. Active/last-active is **Witcher Compatibility Test**,41 enabled mod entries. Staging is `D\witcher3\mods`; method `hardlink_activator` is corroborated by `G\Mods\vortex.deployment.json` and its recorded target/staging fields. Existing staging examples use `Mods/...` (some also bin), matching the top-level archive convention.

Private evidence: E/`private/{selected-state.json,closed-state-reference.json,profile-summary.json,proposed-profile.json}`. No state database was edited. The draft specifies **White Orchard Music Test**, cloned from the active compatible configuration; it is not an actual installed Vortex profile.

Actual clone UI source: E/`installer-evidence/core-source/renderer.js.map-19-ProfileItem.tsx:206` exposes **Clone**; `renderer.js.map-20-ProfileView.tsx:345` copies profile/mod-state properties and stored profile files, adds a new ID and opens Edit without itself activating it. **Separate per-profile load-order state is not proved copied by this function.** Compare the new Load Order against the recorded original before first deployment; do not accept unrelated reordering or automatically sort/remerge the41 mods to accommodate a cache-only test. Inherit current feature choices rather than inventing new ones.

Audio audit: no loose `.bnk` or soundspc.cache in installed G/Mods or G/DLC, and none in current Vortex staging. Searched staged `.ws/.xml/.ini/.settings` files have no main `SoundGameStateChange`, `SoundGlobalParameter`, `GameStateToString`, `CollectSoundStates` or dialogue-state hook matches. This is a bounded resource/symbol check, not proof against every bundled/script audio behavior. Keep existing gameplay mods, custom DLC, W3LoadFix/ReShade/other loaders identical A/C/A. A specific newly discovered conflict requires review; no broad removal is proposed.

Native `G\bin\initialdata\sound\Init.bnk` remains SHA-256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`. `modWMCBankLoadingTest` does not currently exist in the game.

After the user closed Vortex/game, **55 files /5614120 bytes** were copied to E/`private/rollback-backup`, including Vortex state database/profile/snapshot data, relevant deployment manifests/staging metadata, current Documents settings/save files and native Init. All source/copy hashes match;25 save-related files preserved. E/`private/rollback-manifest.json` records exact source/backup paths, bytes/hashes and original active profile; refresh this snapshot immediately before authorized mutations. Private backup/state files must never be committed or redistributed. Do not restore a live Vortex database while the app is running.

## Save isolation: Vortex does not provide it for Witcher3 here

Observed installed code: game extension `index.ts:313` registers **Profile Data** (`local_merges`), described as merged scripts/load order; `mergeBackup.ts:45` gates that behavior and `util.ts:63` resolves game settings to the Windows Documents known-folder. It does not register a Witcher3 save feature or profile-dependent save path.

Actual Save Games feature comes from installed `bundledPlugins/gamebryo-savegame-management/index.cjs` in the ASAR. Its `local_saves` registration uses predicate `P(gameId)`, backed by the Gamebryo dictionary `M`; Witcher3 is absent. Its Saves/<profileID> logic applies to those supported games. Empty Witcher3 profile directories and a Vortex **snapshot** containing Documents gamesaves are not evidence of save redirection. **Do not treat snapshots or Profile Data as isolated saves.**

Verified alternative mechanism: Windows provides a separate Documents known-folder for a separate user, while this game uses `The Witcher 3\gamesaves` within Documents (actual current profile and saved-game files observed). The current account's Documents is OneDrive-redirected; hardcoding `%USERPROFILE%\Documents` is unsafe. Use a separate existing/test Windows account with a verified separate Documents path, copy one user-selected existing White Orchard save and its companion files there, and keep Steam/OneDrive sync from writing across profiles. These account/path/Steam-launch prerequisites **have not been configured or launch-tested**. Verify the known-folder in that account and actual game write location before interpreting gameplay. No unsupported launch flag, junction/symlink or live-save-directory swap is proposed.

Vortex should continue managing the shared installation from its existing account/state. Do not start another independent Vortex instance under the test Windows account against the same installation. User may need to prepare Steam access in the test account manually. If that setup is impractical, stop and agree an explicit backed-up save-isolation alternative; do not silently fall back to the live save directory. No restart or new playthrough is required.

## Exact proposed Vortex workflow — await approval

1. Confirm the copied White Orchard save/test Windows Documents setup and refresh closed-app backups. Open existing Vortex, Witcher3 → **Profiles**, use **Clone** on **Witcher Compatibility Test**, name it **White Orchard Music Test**. Compare enabled mods/features/load order; preserve all existing unrelated mods. Activating this clone requires explicit authorization because it can redeploy/shared settings.
2. On the authorized test profile, use **Install From File** for both ZIPs. Keep them as **two separate mod entries**, named exactly as archive titles. If Vortex offers to replace an existing WMC variant, cancel that choice and retain separate entries; neither existing mod should be replaced. Confirm both installer outputs use top-level Witcher3 type and the intended path, without `Mods\Mods` or a title wrapper. Do not change unrelated deployment rules.
3. **A:** disable Music Control Test, enable Vanilla Control, deploy via Vortex. Both must not be enabled. Verify actual deployed bytes and native Init before launch (command below). Record profile ID/enabled statuses, deployed hash and any Vortex warnings. If additional audio caches appear or a load-order/merge change is unexplained, stop. No new scripts require merging for these archives.
4. Exit the game fully. **C:** disable Vanilla Control, enable Music Control Test, deploy; verify C bytes. Use the same initial copied save/settings/route in a fresh game process. Do not launch before save isolation is verified.
5. Exit fully. **A again:** reverse the two statuses, redeploy and verify A. Restore the initial test-save copy only within the isolated test profile; live saves remain untouched.

Read-only verifier, after each **authorized** deployment:

```powershell
python tools/white_orchard_vortex_archive.py verify-installed --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --variant A
# Use --variant C for the middle run.
```

`installed` checks native Init, sole correctly placed mod/DLC audio cache, no loose mod banks and the intended cache hash. A shared target cannot reveal whether both Vortex entries are enabled; also inspect the two UI statuses. Offline fixtures passed: valid A accepted, wrong variant/competing cache/altered Init rejected. Helper compilation and `git diff --check` pass. No fixture wrote to the installed game.

## Checklist and rollback

- Confirm **audible generic exploration under A**; natural gaps are inconclusive. Same White Orchard area/time/route and nonzero normal Music setting throughout.
- Under C, hear exploration attenuation, reachable combat music and native combat→exploration transition back to attenuation. Ambient sound/voices remain normal.
- Test ordinary village dialogue only if a genuinely generic score is audible under A; explicitly authored quest/dialogue music should remain. Use only protected cues accessible in the copied save; missing cue coverage remains an open item.
- Restored A must restore generic music. Repeatable selective A/C/A differences support candidate loading; all-normal or blanket-silent results remain inconclusive. Startup alone is not compatibility proof.
- Record route/timing, variant/deployed hashes, expected/actual audio and errors. Fully quit between runs; test autosaves stay outside the live profile.

Rollback through Vortex: disable **both** test entries on the test profile, deploy to remove the shared test cache, then restore **Witcher Compatibility Test** and its recorded enabled set/load order. Ensure both tests are disabled there and in the primary profile. Verify the test cache is absent, native Init matches and existing settings/mod deployment are restored. Existing41 mods/custom DLC/loaders remain present. Keep installed ZIP entries disabled or uninstall **only these two** through Vortex with approval; don't manually purge the staging tree. Preserve private test diagnostics and do not copy test saves over live saves. Re-enable sync only after verifying live saves/settings intact. Use the closed-app rollback backup for recovery if Vortex's normal restoration fails; don't blindly overwrite current database/deployment files.

**Stop point:** ZIPs, installer-path proof, backup, clone draft and procedure are ready. Actual clone creation, activation, installation/deployment, Windows/save setup and launches remain pending. The next confirmation should authorize profile clone/activation plus separate ZIP installation and A/C/A deployment **only after save isolation is agreed**, with restoration afterward. Licence confirmation/earlier “Continue” does not authorize those actions. Runtime compatibility remains unproved.
