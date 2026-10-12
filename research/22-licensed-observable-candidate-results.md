# 22 — Licensed observable White Orchard candidate, staged for authorization

Date: 2026-10-12. **Ready for a separately authorized isolated gameplay compatibility experiment. Not runtime-validated or release-certified.** The modified regional bank passes all19 existing structural checks and byte-identical native cooker readback. Only its regional cache is staged; original Init stays native. No game launch, installation, existing-mod/config/save edit, header patch or licence-key handling occurred.

This completes the build blocked in [report21](21-stage1-observable-candidate-build.md), after the user confirmed manual licence application to its fresh project. Existing native/licensed A/B packages from [report20](20-white-orchard-bank-loading-test-plan.md) remain untouched. The specific user instruction authorizes observable candidate generation/packaging before resolving runtime ProjectID compatibility; this is an experimental acceptance boundary, **not a waiver of report17's strict native-equivalence gate**.

## Evidence paths and commands

Machine-local aliases:

- E: `C:\Dev\witcher-music-control\build\licensed-white-orchard-stage1`
- P: `E\candidate` (complete isolated project; all1,508 original work units)
- C: `E\candidate-banks-licensed-retry` (accepted experimental build output)
- B: `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline-banks`
- BP: `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline`
- K: `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit`
- G: `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3`

Selected generation:

```powershell
python tools/white_orchard_wwise.py --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' --project build/licensed-white-orchard-stage1/candidate/w3_audio.wproj --output build/licensed-white-orchard-stage1/candidate-banks-licensed-retry
```

Matching tool is Wwise2023.1.19.8928. `tools/white_orchard_wwise.py:generate` records full command array, Windows/SFX, selected `music_prologue`, isolated output/cache/metadata and disabled source-control/custom commands. No exclusions or unrelated-bank generation. C/`command.json`, `generation.log`, `result.json` and `SoundbanksInfo.xml` are retained. E/`licensed-retry-evidence.json` captures bank fields/diagnostics; E/`licensed-final-preservation.json` captures final protected-source checks. Licence application was manual; no project/licence XML was printed, inspected for keys or copied to another project.

Offline packaging (requires a **fresh absent** root):

```powershell
python tools/white_orchard_candidate_package.py --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit' --baseline build/licensed-white-orchard/baseline-banks --baseline-project build/licensed-white-orchard/baseline --candidate build/licensed-white-orchard-stage1/candidate-banks-licensed-retry --candidate-project build/licensed-white-orchard-stage1/candidate --root build/licensed-white-orchard-stage1/cooker
```

The new helper reuses `white_orchard_state_bank_audit.audit`, `white_orchard_cooker.prepare/execute`, `white_orchard_loading_package.verify` and existing bank comparators. It rejects failed generation, changed baseline warning rows, unexpected BKHD/non-State differences and failed structural checks. It never generates, installs, edits a bank or modifies the A/B helper's unmodified-input guard.

## Generation diagnostics, including the failed licensed attempt

**Observed final build:** Console exit **2**, exactly Init and music_prologue emitted, **15 warnings, zero errors/fatals**. Nine `MediaMultipleUsage`, five `MediaDuplicated`, one Wwise.dat consistency warning. The entire generation log is byte-identical to the licensed baseline's log, SHA-256 `dc3867ea2044967b9f5f22afa1c7f38a99a36f29343559ee8838053e213975cf`. The wrapper accepts2; this report explicitly records it rather than calling the build error-free. Report18 explains the same warning categories and their scope. Trial-media and Mastering Suite errors are absent, demonstrating effective coverage for this build.

**Earlier licensed attempt preserved:** E/`candidate-banks-licensed` exited1 with14 `OutputFolderCopyError` messages plus the same15 warnings. Both bank files were emitted, but were **not selected for packaging**. All14 source WEMs existed afterward;33 media files totaling150181416 bytes reached that output, while14 copies totaling79055419 bytes were absent. E/`copy-error-file-evidence.json` preserves filenames/existence/sizes. The drive showed296345600 free bytes during investigation and687448064 on a subsequent check. No evidence was deleted, no missing media was manually filled in, and no installed file or permission was changed.

**Inference, not established cause:** transient storage/resource pressure or conversion/copy timing could explain these failures; free-space fluctuations do not prove disk exhaustion at the failed copy calls. A fresh output retry, reusing converted cache, removed all copy errors. The accepted retry is the evidence for generation success, not survival of banks in the failed directory. The still-earlier pre-application licence failure remains in E/`candidate-banks` (report21).

## Structural results and dependency boundary

Evidence: E/`cooker/structural-audit.json`; `tools/white_orchard_state_bank_audit.py:audit`, `state_chunk`, `native_groups`, `header`; existing clean-authoring audit P/`state-volume-clean-authoring.json` and specification `src/wwise/white-orchard-state-volume.json`.

| Check | Observed result |
|---|---|
| Source context | All1,508 WWU paths retained; only `Interactive Music Hierarchy/music.wwu` differs from BP. Removing world StateInfo restores original semantics. All25 source State overrides retain the requested values. |
| Changed regional object | Only type12 world_music1033516231 changes; no HIRC IDs added/removed. Total regional size174943 versus baseline174826, **+117 bytes**. |
| Local serialization | Additive dB Voice Volume property0; one immediate existing StateGroup766723505; exactly nine attenuated States at−200 dB (seven traversal variants and two dialogue variants). Combat/other0 dB values remain the default, without redundant serialized attenuation. |
| World outside State block | Prefix and suffix byte-exact; composition, threat/intensity, switch routing and other properties preserved. |
| Non-world HIRC | Every non-world record remains native-exact, including events/actions, authored quest/cutscene routing, sources and streaming references. |
| Media | DIDX/DATA native-exact; all47 converted WEM paths/hashes match the licensed baseline. No replacement music assets. |
| Global dependencies | No new serialized HIRC IDs; local authoring CustomState IDs do not become HIRC dependencies. Existing global State source unchanged. Native Init contains the referenced game_state group, default1000ms and43 custom transitions. |
| Disposable Init | Candidate and licensed baseline byte-identical (`ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01`), including INIT plugin registrations and STMG. Never packaged. Existing native-source discrepancies are not repaired or re-investigated. |
| BKHD | v150, bankID3228744150, language393239870, alignment16, type0 and padding match baseline. **ProjectID17637** matches licensed baseline; native remains39. Candidate content hash matches metadata GUID `{CE2EC172-CD88-8256-670E-D3CC4F02E817}` in bank byte order. No header edits. |

All19 audit checks pass. The packaging helper additionally compares header fields other than the expected content hash and limits differing chunks to BKHD/HIRC. **Supported inference:** the delta needs no additional global definitions beyond existing native State support; exact surviving references/media and identical generated Init bound the change. **Unresolved runtime hypothesis:** native Init39 can accept this regional17637 bank and apply the State gains/fades. Offline structure and authoring playback cannot prove that; the staged audible test is the falsifying experiment.

## Third variant and hashes

**Exact C package:**

`C:\Dev\witcher-music-control\build\licensed-white-orchard-stage1\cooker\packages\candidate\modWMCBankLoadingTest\content\soundspc.cache`

Only this cache is in the mod folder. It contains one indexed `music_prologue.bnk` entry, offset64, length174943. No Init, WEM, script, menu or configuration file. All three variants use the same mod directory name; **only one may be installed at a time**, never coexisting caches.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| C regional bank | 174943 | `80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698` |
| C direct cooked/staged cache | 175050 | `a2b8cc23285c5b6cd392b0301328d75bd545dde8d9e0c06007b674b68a14aa12` |
| C native splitcache readback cache | 175050 | `ebcf23a12398f34d74f2687b0d2b576bd3c5e6ff187d635ce04b479baea3812c` |
| Edited music.wwu | — | `3a4f0ecf86c5edb6a0079eccc341251d0147645f66c3fa3c4b6a24212be43ce2` |
| User-licensed isolated project file | — | `c4b79397f261bd5fa11232b4a708252f49811a109ce78e3605470a79f4bc55ea` |
| Retained native Init | 32840 | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |

Both `cooksounds` and `splitcache sounds` exited0. Direct and readback payloads are byte-identical to C; wrapper hashes differ because cache layout differs, as in report20. Full logs/argument arrays are E/`cooker/candidate-{cook,split}.{log}` and corresponding `-result.json`; E/`cooker/candidate-verified.json` records payload identity. Bootstrap uses native Init only, with the known isolated startup CSV filtering of missing `ly_animal_dog.bnk`. Bootstrap legacy/localization/script assertions and seed/text-description messages remain in the logs; they are not described as an error-free game environment. Exit0 plus exact readback establishes packaging only.

Final rechecks: all1,556 installed source inputs and455 installed cooker-bootstrap inputs unchanged; native Init, licensed baseline banks and A/B package hashes unchanged. A remains `build/white-orchard-bank-loading-test/packages/control/...`; B remains `.../packages/licensed/...`, with hashes from report20. No installed Mods/configuration or saves were edited. Fourteen existing verification tests pass; new helper compiles and `git diff --check` passes. Banks/media/cache/project/licence and private evidence remain ignored.

## Authorized-test proposal and pass criteria

Use report21's minimally invasive **A → C → A** procedure: keep existing mod/DLC/loader configuration identical, temporarily add only the one test-cache mod, and use a separately verified test Documents/profile location containing a copy of an existing user-selected White Orchard save. Keep cloud synchronization and automatic saves confined away from live saves; refresh backups first. Do not invent a user-directory switch or restart the playthrough. Recheck for competing audio caches/hooks before launch; if isolation or save dependencies cannot be made safe, stop before installing/launching. Optional B is retained as the unmodified licensed control.

Each variant requires a fully new process and the same initial copied save, route, nonzero normal Music setting and audio settings. First establish audible A exploration and reachable combat. C should suppress generic exploration after native fades, keep combat music audible, then attenuate traversal again on return. Repeat A to confirm exploration restores. Use routine village dialogue only where A has confirmed generic world music; deliberately authored dialogue score is expected to remain audible. Test a protected authored cue already accessible in the copied save; mark unavailable cue coverage incomplete, without advancing live quests. White Orchard, not the opening Kaer Morhen tutorial, is the region under test.

**Positive behavioral attribution:** repeatable selective C exploration/dialogue attenuation with intact combat/authored audio, reversed by A, demonstrates the edited bank's effect in these contexts. Native random musical gaps require repetition; a moment of silence is insufficient. **Inconclusive:** normal music everywhere (fallback/wrong context/competing override remain alternatives), naturally silent A, or blanket C silence. **Failure investigation:** C-attributable crashes, loss of combat/authored cues, broken fade/resume or altered Init/config. A successful route would establish this bank's runtime compatibility, not every region/quest or slider architecture.

The remaining gate is **explicit user authorization** for temporary installation of these hashed A/C caches, an agreed isolated copied-save/profile setup, matched launches and rollback. Keep original Init and existing mod configuration intact, remove only the temporary test-mod afterward, and verify restoration. No deployment or launch is authorized by the licence confirmation or by “Continue.”
