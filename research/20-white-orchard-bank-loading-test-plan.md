# 20 — Unmodified regional-bank loading test: staged, not deployed

Date: 2026-10-11. Scope: **runtime compatibility experiment**, not a release candidate or modified music policy. The user explicitly superseded further native-Init reconstruction and unrelated-bank generation. No Wwise generation, licence operation, header patch, installed-resource edit, game launch or save modification occurred.

## Result and evidence locations

**Observed:** both A/B caches were built and read back by the installed native cooker, with exact bank-payload preservation. Neither contains Init or media files. Packaging is technically ready. **Actual mixed-ProjectID loading remains unproved**; profile isolation and convincing load attribution are launch prerequisites, not results of these offline tests.

Repository root `R = C:\Dev\witcher-music-control`. Installed game `G = C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3`. Installed REDkit `K = L:\Games\Steam\steamapps\common\The Witcher 3 REDkit`. Ignored evidence root `E = R\build\white-orchard-bank-loading-test`. These are machine-local evidence paths, not portable dependencies.

Exact package files:

- A: `E\packages\control\modWMCBankLoadingTest\content\soundspc.cache`
- B: `E\packages\licensed\modWMCBankLoadingTest\content\soundspc.cache`

Each mod folder contains **only that file**. Use one variant at a time under the same mod name; do not deploy two competing variants. The future destination would be `G\Mods\modWMCBankLoadingTest\content\soundspc.cache`, but nothing was copied there.

Evidence: `E\{control,licensed}-verified.json`, `E\{control,licensed}-{cook,split}-result.json`, four corresponding `.log` files, `E\installed-inputs-recheck.json`, and `E\bootstrap-manifest.json`. Reproducible helper: `R\tools\white_orchard_loading_package.py`, functions `stage` and `verify`; existing cooker/bootstrap implementation: `R\tools\white_orchard_cooker.py`, `prepare` and `execute`. Reports [18](18-licensed-baseline-results.md) and [19](19-native-init-compatibility-investigation.md) retain the generation and failed strict-gate evidence. This packaging helper **does not waive or alter that gate**.

## 1. What is known about resolution

**Observed installed resources:** reading only the index and selected payloads of `G\content\content0\soundspc.cache` found 2,174 entries. `music_prologue.bnk` is at offset 534457179, length 174826; `init.bnk` is at offset 370791266, length 32840. Their hashes match the REDkit native copies. The cached Init and `G\bin\initialdata\sound\Init.bnk` are byte-identical. Thus both identified native Init sources supply ProjectID39; this experiment need not determine which identical copy wins in order to preserve its content.

**Observed static evidence:** `G\bin\x64_dx12\witcher3.exe` contains `bin\\initialdata\\sound\\`, `Init.bnk`, `gameplay\\globals\\soundbanks_always_load.csv`, `SoundLoadBank`, `SoundUnloadBank` and decorated AK `LoadBankMemoryCopy`/`LoadBankMemoryView` names. Selected strings are recorded in `R\build\white-orchard-test-preparation-evidence\retail-loader-strings.json`. These show integration vocabulary, **not a verified call chain, exported callable API, search order or successful return value**.

**Official workflow evidence:** CDPR documents per-mod enablement/priority through Documents' `The Witcher 3\mods.settings` in [Managing mods](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/36339714/Managing%2Bmods). The older CDPR [sound-tool workflow](https://forums.cdprojektred.com/index.php?threads%2Ftool-sound-editing-tools-for-the-witcher-3.121192%2F=) places `soundspc.cache` in `Mods\<mod>\content`. That older workflow is evidence for placement, not proof of modern BKHD compatibility. Current Remastered cache-format evidence is our matching cooker/readback, using `-platform=pc_dx12 -r4remastersounds`.

**Reference boundary:** report19 §5, `reference\fmc-audio-remaster` supplies Init and cached banks together (v140/ProjectID17637). It is useful evidence for audio-mod packaging, **not** a known-working native39/generated17637 mixture. Only Story Music and Less Is More contain no generated banks and cannot settle this question. No inspected reference establishes mixed-ID loading.

**Supported inference to test:** the mod cache supplies a resource override for the canonical `music_prologue.bnk` name, while unlisted banks/media remain supplied by native resources. The cache is an indexed set of bank/media entries, not an entire replacement of all native sound resources. Offline selective cooking confirms its structure; **runtime duplicate-name precedence, fallback and acceptance are still the experiment's subject**. Generic mod priority documentation alone does not prove sound-cache arbitration. The single-active-test-mod procedure avoids competing audio caches without assuming a numerical priority direction.

Wwise's [SoundBank loading contract](https://www.audiokinetic.com/library/edge/?id=soundengine_banks_general.html&source=SDK) separates Init/global initialization from content-bank loading. It does not establish Witcher 3's cache precedence or prove that its integration accepts differing ProjectIDs. No new Init definition is introduced by either package.

## 2. Exact A/B inputs and packaging results

| Item | Bytes | ProjectID | SHA-256 |
|---|---:|---:|---|
| Retained native Init, loose and cached | 32840 | 39 | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |
| A native regional bank | 174826 | 39 | `75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912` |
| B existing licensed unmodified bank | 174826 | 17637 | `5b28f4ee5f286ec46a80120ea632c1d2ca715c0e2b05fb90ddd411f16e9a953a` |
| A staged cache | 174933 | — | `f7a0c2c20d698d4dbb514e573c64d67df7e9c57ab854012bd0adc6b4afdde40a` |
| B staged cache | 174933 | — | `00a87a4e337ed6758e4a54c27e0e32de36cfdf7fc50b118778a66de13bfd8c78` |

A input: `K\r4data\soundbanks\Pc\music_prologue.bnk`. B input: `R\build\licensed-white-orchard\baseline-banks\music_prologue.bnk`. Both use v150, bankID3228744150, language393239870, alignment16, bank type0. Existing comparison tools confirm no HIRC objects added/removed/changed and no non-BKHD chunk difference. B is **unmodified**, not the older trial output or a Stage1 State-volume candidate.

All four native cooker operations exited **0**, without timeout. Direct caches are CS3W v2, one `music_prologue.bnk` entry at offset64, length174826; exact payload comparison succeeds. Native `splitcache sounds` reads each and writes a one-entry content0 cache whose bank payload is also byte-identical. The split-cache hashes differ from direct caches because cache wrapper layout differs; that is not a bank change. A split hash: `debf91472db31824283b86bc9098523bbadd752e9a0ee19b470a80ac305e0eaa`; B split hash: `b748368a3283e8f206969cbc387b18a620bb3657968591340e9c0d4693e4b2a6`. Packages retain the direct cooked cache.

**Diagnostics preserved, not described as error-free:** cooker bootstrap emits missing legacy config/profile-base, localization/sqlite and Wintab messages, a depot-path assertion, and missing map-manager script/component assertions. The cook summary reports one bank absent from the header-only split seed (assigned to content0), one missing text description, zero missing WEM files and zero WEM mapping conflicts. These match the isolated bootstrap limitations; successful exit and exact payload/readback establish packaging only, not retail loading. Logs preserve every message. No full depot is required by this operation.

After packaging, all **455 installed bootstrap source inputs** were rehashed against the preparation manifest; none changed. Native Init hashes remained identical. The source bank is never rewritten; the helper rejects inputs other than the two recorded unmodified hashes, requires native bootstrap Init, and refuses existing operation outputs.

Reproduce with a fresh ignored root (do not overwrite this evidence):

```powershell
python tools/white_orchard_loading_package.py prepare --root build/white-orchard-bank-loading-test-repeat --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit'
python tools/white_orchard_loading_package.py control --root build/white-orchard-bank-loading-test-repeat --bank 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc\music_prologue.bnk'
python tools/white_orchard_loading_package.py licensed --root build/white-orchard-bank-loading-test-repeat --bank build/licensed-white-orchard/baseline-banks/music_prologue.bnk
```

`white_orchard_cooker.execute` records full argument arrays, working directory, exit code and timeout. Its isolated `-root` prevents cooking against installed data. No Wwise command is involved.

Verification-tool regression suite: `python -m unittest discover -s tools -p test_white_orchard_build_gate.py -v` — **14 passed**. Its intentionally failing synthetic fixtures print failure JSON as expected; they are not new licensed-build results. `python -m py_compile tools/white_orchard_loading_package.py` and `git diff --check` also passed. Banks, caches, profile backups and unsanitized tool logs remain ignored; only the helper/documentation are repository changes.

## 3. Profile isolation, backup and rollback

**Observed preflight:** game process was absent. Current `G\Mods` has41 directories, and the real Documents profile's `mods.settings` has41 enabled entries. No loose BNK or `soundspc.cache` was found under current Mods/custom DLC, and searched mod scripts contain no `SoundGlobalParameter`, `SoundGameStateChange`, `GameStateToString` or `CollectSoundStates` match. This is a resource/text audit, not proof that scripts or bundled content cannot affect sound.

Custom DLC includes BloodAndSteel, BrothersInArms, GwentDeckChoice, Hoods, MonsterHuntContracts and sharedutils. `G\bin\x64_dx12` also contains `dsound.dll`, `dxgi.dll`, `w3loadfix.dll` and other addons. `w3loadfix.ini` documents `Enabled=false` as a feature-disable option. None was changed. Decompression/loader modifications are especially relevant to attributing failures. Merely disabling audio-named mods would not create a clean test environment.

The Windows Documents known-folder resolves to a OneDrive-redirected directory, **not** necessarily `%USERPROFILE%\Documents`. A byte-verified offline backup of that entire existing `The Witcher 3` profile was created at `E\private-profile-backup`:35 files,2756112 bytes, including25 save-related files. Original files were rehashed during copying and remained unchanged. The private manifest is `E\private-profile-backup-manifest.json`; save names/account metadata remain ignored and are not published. This is a preflight snapshot, **refresh it immediately before any authorized change**, with game/cloud synchronization stopped.

**Recommended isolation:** a separate Windows test account/profile with a verified separate Documents known-folder, cloud synchronization disabled for the test, and **a copy of an existing user-selected White Orchard save**. No new playthrough is required. Account creation/setup is a future manual or separately authorized action. No alternative-user-directory launch switch has been verified; do not invent one. A separate Windows profile alone does not isolate the shared installation's Mods, custom DLC or DLLs.

Before launch, inventory/hash active Mods, custom DLC and relevant DLL/config files. Temporarily move user-installed mod directories/custom DLC and third-party loader files into explicit, backed-up quarantine outside the game tree, only with separate authorization and after checking dependencies; preserve official content. Use the same clean arrangement in A and B. Do not uninstall software or overwrite binaries. If the copied save requires removed quest mods, fails to load, or produces broken world state, **stop** and choose a suitable existing save; do not save/repair/reset the live playthrough. If isolation cannot be made safe, report that prerequisite instead of improvising on the live profile.

Rollback plan: close the game fully; remove only the newly added test-mod directory after verifying its exact resolved path/name; restore quarantined folders/files to their recorded original paths and verify hashes; restore configuration bytes and original enablement; verify native Init again. Preserve test-profile autosaves/diagnostics separately or discard that test profile with authorization. Never copy its saves over live saves. Re-enable cloud sync only after confirming the live profile/save manifest is intact. Keep the preflight backup until the user accepts restoration. None of these installed-directory/profile mutations has been performed.

## 4. Controlled run sequence — requires authorization

1. Finish the isolation/diagnostic preflight above, choose the copied White Orchard save and establish a repeatable audible route. Confirm normal Music volume is nonzero and identical for both trials. Verify native Init hash39 and absence of any other mod audio cache/Init. Capture file manifests/configuration and diagnostic capability before launch.
2. Optional A0: run without the test mod, on the isolated copied save, to confirm the route is audible and clean-profile operation is healthy. This is a sanity check, not the packaged A control.
3. A: install **only** the staged control cache under the proposed test-mod name; verify its hash. Start a fresh process, load the fixed save, capture diagnostics and exercise White Orchard exploration, a routine village conversation, reachable combat and an available authored cue. Record route/events/settings and quit fully. If A fails, do not interpret B or proceed.
4. Restore the test save copy to its initial snapshot, keeping any automatic writes confined to the test profile. With the process stopped, swap only the test cache for B, verify its hash, and repeat the same route/settings/capture. Do not rely on in-session bank reload or cached memory. Neither run adds Init.
5. Optionally repeat A after B if a discrepancy appears, to separate reproducible B behavior from timing/route effects. Stop on crashes, load errors or save-isolation failures. Restore the installation/profile configuration as above and preserve trial evidence.

White Orchard is the playable region for `music_prologue`; the musicless opening Kaer Morhen tutorial is not a useful control. Both variants retain normal music; this test does **not** assess suppression, sliders, State fades or quest protection of a modified candidate. Available authored cues depend on the existing save; do not advance irreversible quests on live saves to obtain them.

## 5. Proving loading versus fallback

**Critical limitation:** A and B have the same events, HIRC, media and bankID. Hearing music, seeing `music_prologue` in a bank list, or opening the mod cache is insufficient to distinguish them. No marker sound, header patch or modified candidate is authorized.

Prefer supported diagnostics in this order:

| Evidence | What it proves / limit |
|---|---|
| Game/Wwise diagnostic identifying B's actual resource/buffer and a completed successful bank load, correlated to the native Init and playback | Strong acceptance evidence. The return/callback result must be completion, not only a scheduled request. Same bank name/ID alone is insufficient. |
| Wwise remote profiler, **Profile Only**, if this game build exposes communication | Can reveal load errors and loaded banks/events. Source identity must still be correlated to B. Do not synchronize authoring data into the game or use authoring playback as evidence. Availability is not established. |
| Windows file-I/O trace showing reads covering B cache's bank payload (offset64..174889 inclusive) and subsequent normal events/playback | Establishes B resource consumption, stronger than an open/index scan. Does not by itself prove AK acceptance or rule out fallback after rejection. Native-cache streaming-media reads are expected, not evidence of bank fallback. |
| Exact B BKHD/buffer bytes observed through separately approved read-only runtime inspection, paired with a successful load result | Strongest attribution if supported logs fail; no current harness or verified retail call-site inspection exists. A buffer merely present in memory is not a successful load. |
| Audible normal music/crash-free play without attributable load diagnostics | Smoke-test result only; record **inconclusive compatibility**, not success. |

Official [Wwise profiling guidance](https://www.audiokinetic.com/en/public-library/2024.1.8_8893/?id=profiling&source=Help) excludes Release-configuration profiling. [Advanced Profiler](https://www.audiokinetic.com/en/library/edge/?id=game_profiler_advanced_profiler&source=Help) documents bank/media views; neither establishes that retail Witcher3 exposes them. Installed exe strings `-debugscripts` and `DebugScriptsLogDir` do not prove audio-load logging. No verified supported retail flag has been found that reports bank ProjectID/hash and completed AK result.

Built-in `C:\Windows\System32\wpr.exe` and `logman.exe` are present. No Procmon/debugger installation is proposed. An authorized diagnostic preflight must verify an available file-I/O trace profile/provider and inspect its actual payload/read coverage; don't assume a generic WPR recording includes all required offsets or bank-return results. Traces can contain private paths and stay ignored. Do not attach a debugger, inject hooks or change executable behavior as an unannounced workaround.

**Pass criterion:** B is attributable as the loaded content bank, with no bank-load failure/fallback, native Init retained, and the matched audible route works. This establishes compatibility for **this unmodified bank, current executable and tested contexts**, not every regional bank or future State edit. **Fail:** reproducible B-attributable rejection/crash/missing music with successful matched A. **Inconclusive:** diagnostic attribution unavailable, A fails, profile differs, or route has no audible music. A mixed-ID successful load would falsify the hypothesis that differing ProjectIDs are universally rejected; it would not explain all generated-Init differences.

## 6. Readiness and requested authorization boundary

**Ready:** exact one-entry A/B packages, native cooker readback, reproducible commands, hashes, original-input rechecks, private profile backup and concrete rollback/run criteria. **Still required before a decisive result:** isolated profile/save selection, safe quarantine/dependency review, and a verified diagnostic route that can attribute B acceptance. An initial diagnostic preflight/smoke test can establish which instrumentation is available, but may remain inconclusive.

The next authorization must explicitly cover: temporarily installing the staged A/B cache one at a time; temporarily isolating and restoring the enumerated existing mods/custom DLC/third-party loaders; using a separate test profile and copied, user-selected White Orchard save (automatic writes only there); launching/quitting the game for the matched controls; collecting supported loader/profiler/file-I/O diagnostics; and completing rollback. Cloud/account setup may require user action. **No authorization is presumed** for deployment, modifying live saves, replacing Init, instrumentation that changes the executable, or generating a modified candidate. If supported diagnostics cannot establish attribution, stop and propose a separate bounded read-only instrumentation investigation.
