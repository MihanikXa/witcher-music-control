# 21 — Observable Stage1 candidate: source prepared, fresh-project licence blocker

Date: 2026-10-11. **Not ready for gameplay testing.** The fresh complete project has the requested clean State edit, but generation exits1 with no banks because the approved entitlement is not effective in this newly prepared project. Existing licensed baseline and A/B packages remain byte-identical. No licence/key was read, transferred or applied; no installation, game launch, existing-mod/config edit or save modification occurred.

**Subsequent result:** after manual application, [report22](22-licensed-observable-candidate-results.md) records the licensed retry and staged third variant. The failure evidence below remains unchanged as the historical pre-application result.

The latest user instruction explicitly authorizes generating/packaging an observable Stage1 candidate before the mixed-ProjectID runtime question is resolved. This supersedes earlier instructions to stop after the unmodified baseline, but does not authorize licence-key handling, deployment, binary patching or a compatibility claim.

## Exact workspace and evidence

Machine-local paths, all outputs ignored:

| Alias | Absolute path |
|---|---|
| P | `C:\Dev\witcher-music-control\build\licensed-white-orchard-stage1\candidate` |
| E | `C:\Dev\witcher-music-control\build\licensed-white-orchard-stage1` |
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| B | `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline-banks` |
| BP | `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline` |
| A/B packages | `C:\Dev\witcher-music-control\build\white-orchard-bank-loading-test\packages` |
| Console | `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe` |

**Project to open manually:** `C:\Dev\witcher-music-control\build\licensed-white-orchard-stage1\candidate\w3_audio.wproj`.

Evidence: P/`input-manifest.json`, P/`state-volume-clean-authoring.json`, E/`source-and-build-verification.json`, E/`waapi-{stdout,stderr}.log`, and E/`candidate-banks/{command.json,result.json,generation.log}`. No generated/licensed asset is committed. Existing helpers were reused without relaxing the strict report17 gate.

## Executed preparation and source validation

```powershell
python tools/white_orchard_prepare.py --audio-project 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio' --output build/licensed-white-orchard-stage1/candidate --preserve-hierarchies
```

**Observed:** fresh copy retains all1,508 original `.wwu` paths and all default hierarchy contents. Its47 copied source-audio files total900846184 bytes. The helper isolates project output/cache/Originals paths, source control and custom commands, without pruning hierarchies or applying Inclusion controls. All1,556 recorded installed inputs (1,509 project/work-unit inputs plus47 audio originals) were rehashed after the experiment: none changed; copied originals also remain byte-identical.

A local Console WAAPI server for this exact project was launched with `waapi-server <P/w3_audio.wproj> --http-port 18090 --wamp-port 18080 --allowed-addr 127.0.0.1 --no-source-control`. The first helper call reached the server before project loading completed and failed connection establishment without an edit. After readiness, this succeeded:

```powershell
python tools/white_orchard_state_volume_author.py --project build/licensed-white-orchard-stage1/candidate/w3_audio.wproj
```

Authority: `tools/white_orchard_state_volume_author.py:author`, `src/wwise/white-orchard-state-volume.json`, and its retained clean-authoring audit. World GUID`{1A59CC64-141A-45A6-8374-EB823D3E9D4F}`, ShortID1033516231; existing `game_state` GUID`{27711515-3584-4123-9F09-B90831398B80}`. All25 local State values were saved/verified; removing world `StateInfo` restores the original music-work-unit semantics. Only `Interactive Music Hierarchy/music.wwu` differs from the licensed baseline's1,508 work units. No test audio, buses, effects, parameters, global States or script hook was added.

| Category | Existing State names | Voice Volume |
|---|---|---:|
| Exploration | exploration, exploration_night, focus_exploration, focus_exploration_night, underwater, underwater_focus, boat | −200 dB |
| Generic dialogue | dialog_scene, dialog_scene_night | −200 dB |
| Combat | combat, combat_monster_hunt, underwater_combat, underwater_combat_focus, focus_combat | 0 dB |
| Other | Remaining11 existing States | 0 dB |

The unchanged sibling `quests_and_cutscenes` retains authored routing. This is a verified **source edit**, not new runtime evidence of attenuation/fades/protection. Prior authoring measurements remain in report13. −200 dB is not claimed to be internal mathematical zero.

After the saved edit, an attempted `ak.wwise.core.project.close` call returned unknown-procedure; the started Console server was then stopped by its recorded PID before generation. No save was pending, and subsequent work-unit checks passed. No user's Wwise session was terminated.

## Generation: precise failure, no candidate bank

```powershell
python tools/white_orchard_wwise.py --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' --project build/licensed-white-orchard-stage1/candidate/w3_audio.wproj --output build/licensed-white-orchard-stage1/candidate-banks
```

`tools/white_orchard_wwise.py:generate` records the exact command array: selected `music_prologue`, Windows/SFX, isolated cache/metadata/output, no source control/decode/Wwise.dat and empty custom commands. No exclusion, licence override or header patch was used.

| Observed diagnostic | Count / result |
|---|---|
| Console exit | **1**; wrapper also fails |
| Produced BNK files | **None**; no regional bank or disposable Init |
| Fatal media limit | 1:26,218 items versus200 permitted |
| Mastering Suite licence errors | 6, naming HomeCinema / Init |
| MediaMultipleUsage warnings | 9: the same q703/q106/Dettlaff source configuration categories described in report18 |
| Wwise.dat consistency warning | 1; retained, not treated as a licence fix |
| MediaDuplicated warnings | 0 emitted in this failed run; do not assume the successful retry will omit baseline's5 |

**Observed contrast:** the retained BP/B licensed baseline generated with exit2 and effective coverage (report18); this fresh project encounters the original licence barriers. **Supported inference:** coverage does not carry automatically into this newly prepared isolated source copy in the current setup. It is not evidence that approval was revoked or the approved key is invalid. No licence internals were inspected to determine storage/application scope.

No BKHD ProjectID or candidate bank hash exists to record, since no bank was emitted. Native39 and licensed baseline17637 remain known; **do not assign17637 to a nonexistent candidate**. Structural bank comparison and cache packaging therefore did not run. The third test variant has not been fabricated from failed/older trial output.

## Hashes and preservation

| Evidence | SHA-256 |
|---|---|
| Installed original music.wwu | `f8184d13ea08f6bc161719884e9341bdfd3a3e7666b203c296ffae37d4e08251` |
| Clean edited music.wwu | `3a4f0ecf86c5edb6a0079eccc341251d0147645f66c3fa3c4b6a24212be43ce2` |
| Fresh project before manual licence application | `ee58c0318791dad924b9b175e327c53a26fdd24c2b31db8e4d36a52fa0b781c5` |
| Clean-authoring audit | `4792352bfc52bcf2d97aa7d9cdd46540b9da6f9bf65e31dfe5d0898f263cb957` |
| Failed generation log | `ea05cafb8b9df6d50e2904321f4a91c00c3b652817aa4cf9f2102818e3888789` |
| Retained game Init | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |
| Retained licensed baseline regional bank | `5b28f4ee5f286ec46a80120ea632c1d2ca715c0e2b05fb90ddd411f16e9a953a` |
| Retained A native-cache package | `f7a0c2c20d698d4dbb514e573c64d67df7e9c57ab854012bd0adc6b4afdde40a` |
| Retained B licensed-cache package | `00a87a4e337ed6758e4a54c27e0e32de36cfdf7fc50b118778a66de13bfd8c78` |

All retained hashes were checked, including baseline's disposable Init (`ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01`). No existing A/B or baseline evidence was overwritten. Source/project hashes are pre-licence-application evidence; a legitimate GUI application may change the isolated project file. Never publish that file or its licence contents.

## Necessary next action and remaining gates

The user must open **P/w3_audio.wproj** in the matching Wwise2023.1.19.8928 and use **Project → License Manager** to apply the already approved Witcher3 REDkit modding licence to **this isolated project**, then save/close it. Do not send the key in chat. No new licence request or paid purchase is indicated. The prior licence-handling restriction requires this manual action; copying the baseline project/licence to avoid it is not authorized.

After the user's confirmation, retry into a **fresh** output such as `E/candidate-banks-licensed`; preserve the failed directory. Reuse the existing edited work units, verify their hashes, and generate only `music_prologue`. Record actual exit/status/all diagnostics; expected baseline exit2 warnings must be disclosed and reviewed, not converted to0. Any licence/error/fatal or new unrelated change stops the build.

Then reuse `tools/white_orchard_state_bank_audit.py:audit` with native bank folder, BP/B and P/new candidate output. Require exactly world1033516231 changed, no HIRC additions/removals, the verified inline additive dB Volume block on existing group766723505, nine attenuated State values, unchanged world prefix/suffix, all non-world records/media/stream references unchanged, metadata hash consistent with BKHD, and identical generated baseline/candidate Init (including INIT/STMG). New local authoring GUIDs must not create runtime object dependencies. Source global States must remain unchanged and native Init must supply the referenced existing group/transitions. These checks establish structural suitability for an experiment, **not proven native39/generated17637 runtime acceptance**. Investigate rather than weaken an unexplained failure.

Only on a structural pass: use a fresh isolated native cooker root and add C at `packages/candidate/modWMCBankLoadingTest/content/soundspc.cache`, preserving A/B. Cache contains only the modified regional bank; no Init/WEM. Reuse native `cooksounds -platform=pc_dx12 -r4remastersounds` and `splitcache sounds`; require exact original-bank versus direct-cache versus readback payload equality and record hashes. Report20's helper intentionally accepts only unmodified A/B inputs: **do not defeat its hash guard** to package C. Add a separate candidate path gated by the structural audit, or invoke the existing cooker/verification primitives explicitly after acceptance.

## Practical observable gameplay test — proposed, not executed

This supersedes report20's need to prove loading through identical A/B playback alone. A staged candidate may provide **behavioral attribution** when the expected selective pattern occurs reproducibly; silence alone remains ambiguous.

Minimize changes: keep the user's existing mod enablement, custom DLC and loader configuration **identical across controls**, adding only one temporary test-cache mod. Report20 found no other loose BNK/cache under installed Mods/custom DLC and no matches for the main music-state symbols in searched scripts; recheck before a run. This preserves the heavily modded save's dependencies and avoids wholesale quarantine for the first controlled observable experiment. If a competing audio resource/hook is discovered or A is broken, stop for a separately agreed isolation plan. Keeping other mods fixed controls A/C differences, but does not establish broad compatibility with every mod.

Protect live saves with a separately verified Windows test profile/Documents location and a copy of a user-selected existing **White Orchard** save. Copy existing mod settings to that profile rather than altering the live settings; keep cloud sync out of the test profile. No unverified `--userdir` switch, live-profile save swap or restarted playthrough. Automatic writes must be confined to test-profile saves. Confirm these prerequisites with the user before launching; refresh the report20 backup before any installation. Existing normal Music volume must be nonzero and consistent.

Recommended order: **A → C → A**, with full process exit between variants and the same initial copied save/route each time. B remains an optional unchanged licensed control. Only one cache under `modWMCBankLoadingTest` is active; record its exact hash. Preserve original Init39 throughout.

| White Orchard observation | A, native regional bank | C, intended edited bank | Interpretation |
|---|---|---|---|
| Previously confirmed audible generic exploration/traversal | Normal native music | Exploration score attenuated after native fade; voices/ambient effects intact | Repeatable A/C/A difference is observable edit attribution |
| Routine village conversation with confirmed generic world score | Normal native music | Generic world score attenuated | Avoid assuming every dialogue is generic; authored quest score is a protected case |
| Reachable combat from the same route | Normal native combat cue | Combat cue audible at native additional gain | Distinguishes selective suppression from a failed/silent entire bank; observe fade/resume |
| Available authored quest/scene cue on protected branch | Audible when normally triggered | Remains audible | Supports protected routing for that cue, not every possible quest |
| Return from combat/dialogue to traversal | Normal native exploration behavior | Returns to attenuated world exploration | Check state change, delayed entry and eventual resume rather than one instant |

First identify a route with **audible A exploration**; native random spacing/silence makes a musicless baseline inconclusive. Allow native fades/entries and repeat the same area/time/event where practical. Confirm an A combat cue and at least one available protected cue without advancing live quests. The Kaer Morhen tutorial is not evidence. If the save cannot provide a protected cue, mark that coverage incomplete rather than restarting or manufacturing a cinematic.

**Positive behavioral result:** C repeatedly suppresses only established generic contexts while combat/protected music still works, and restoring A restores generic music. This would demonstrate use of the edited bank in the tested runtime without depending on a ProjectID log. **Inconclusive:** all music remains normal (fallback, another override, wrong state/area, or failed attenuation remain alternatives), A is naturally silent, or all C music disappears. **Failure investigation:** crashes, blanket silence, missing combat/authored cues, disrupted native fades/resume or changed Init/config. Optional supported traces supplement these observations; no injected instrumentation is needed merely to hear the selective pattern.

After a future run, fully exit, remove only the temporary test-mod directory, verify original Init and existing mod/config hashes, retain private recordings/logs and keep test autosaves out of the live profile. No profile/mod/DLL changes are currently authorized. Before actual deployment, request explicit approval for the final hashed C package, chosen test profile/copied save, temporary A/C/A installs and launches, and rollback. **Current stop is earlier: manual licence application is required; there is no candidate package to authorize yet.**
