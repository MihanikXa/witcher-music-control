# 96 — Native logger path and rejected Stinger request gateway

2026-10-19. Implements the bounded report95 investigation. **No observer installation yet. First perform the logger-only, main-menu smoke test below.** Source ZIP compilation is retained; retail capture and the full enabled-mod assembly remain unverified. A Trigger/MusicStinger positively starts the approved S04-a, but fails protection, request lifetime and cancellation. It must not be connected to the contextual model.

## Evidence levels and outcome

| Question | Result | Evidence level |
|---|---|---|
| Does retail contain a native LogChannel sink? | Yes: script registration → writable callback → native file logger → configured directory/scriptslog.txt | Read-only executable tracing; not observed retail output |
| Does this installation activate/configure it correctly? | Unknown; startup has a conditional guard and configuration must reach it | Requires one user main-menu probe |
| Is observer source ready? | Existing source compiles; unchanged exact source ZIP retained | Previous native compiler evidence rechecked, not recompiled this task |
| Is it ready for unconditional installation? | **No. Confirm the sink first.** | No retail WMCCTX1 rows exist yet |
| Can an external Trigger cause actual S04-a playback? | Yes, complete approved stereo PCM and baked tail | Wwise 2023.1.19.8928 profiler plus Recorder PCM |
| Is the tested request protected? | **No. Combat/outro overlap, stale dialogue request, ineffective cancellation** | Counterexamples below |
| Did anything ship/install? | No | No bank generation, game launch, installed config change, Vortex/save change or audio distribution |

Sanitized measurements and local artifact fingerprints: [96 evidence](96-interface-prerequisites-evidence.json). Private raw evidence is under `C:\Dev\witcher-music-control\build\sparse-interface-prerequisites-v1\`. All timings below are measured authoring wall clocks unless expressly identified as PCM sample clocks.

## A. Native logging — trace the callback, not just its initial pointer

Inspected **only as data**: `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\witcher3.exe`, SHA-256 `2df765398a3d1f165db418271be7200178320a4466817379f2fa0dc0001fb101`, image base `0x140000000`. RVAs below are relative to that image, not reusable offsets for another executable. Trusted installed Microsoft VS dumpbin disassembly is retained privately; original read-only reproducer is `tools/observer_native_log_audit.py`. No debugger attachment, binary patch, licence inspection or bundled third-party program was used.

| Verified object/path | Native evidence |
|---|---|
| Script LogChannel binding | name RVA `0x362ed68`; registration LEA `0x2745b9b`; handler `0x2745340–0x274541a` |
| Indirect log dispatch | call `0x27453fa` through writable `.data` slot `0x405baa0` |
| Initial fallback | pointer to `0x27454d0`, `ret 0`; **not evidence that logging is permanently disabled** |
| Actual startup rebinding | initializer `0x2287e60`, called at `0x2286703`; assignment `0x2287e95` replaces the slot with callback `0x22880f0` |
| File formatter | `0x22880f0–0x228823b`, FILE pointer `0x5c92b18`; writes `[channel] text` plus newline, with a force-flush branch at `0x2288213` |
| Filename and opening | filename literal `scriptslog.txt` at `0x35c78f8`; path appends at `0x2288553`/`0x2288620`; native file-open call `0x2288669` to `0x1aa6b20`, mode `w` at `0x35c7908` |
| Native startup marker | `Debugging scripts for ` emitted by the file logger initialization |

The executable **registers these exact configuration keys in group `Scripts`**:

- `LogDebugScripts`: node `0x5149218`, value `0x5149248`; constructor sets its initial value to true. The key's exact influence on the startup guard is not established, so it is not described as a proven enable switch by itself.
- `DebugScriptsForceFlush`: node `0x5149250`, value `0x5149280`, directly read by the formatter's flush branch.
- `DebugScriptsLogDir`: node `0x5c05f80`, string storage `0x5c05fb8`; initialized in code `0x1cd3ca–0x1cd42c`, not a prepopulated on-disk BSS pointer. Native logger chooses the configured directory when nonempty and appends the filename. Default directory was not resolved or guessed.

**Remaining runtime uncertainty:** startup skips the logger when the engine-global byte at offset `+0x17c` is nonzero. Its semantic name and retail value are not established. `CGame.IsFinalBuild` returning true is a separate fact, not proof of what this byte means. Configuration delivery, file permissions and whether initialization occurs at this user's main menu still need actual observation. OutputDebugString imports and a `-debugscripts` string do not establish this log route; neither DebugView nor that flag is recommended. No new software is needed.

The initial return-only callback was an investigative false lead; tracing the **writers of the writable slot** corrected it. The audit explicitly fails on an unreviewed image or changed registration/config/file-open layout. It does not pretend to be a general-purpose disassembler.

## B. Exact staged smoke test and rollback

Prepared locally, **not installed**:

`C:\Dev\witcher-music-control\build\sparse-interface-prerequisites-v1\manual-logger-probe\`

Contains `READ-ME-FIRST.md`, staged `general.ini`, exact `general.ini.original` rollback and a manifest. Original `bin\config\base\general.ini` is 30 bytes, SHA-256 `a9750eeabb62948d661a3ec785c82919eb4075dad9de6e35aaf9a4a1bc9f86b2`. The staged copy preserves those bytes and appends:

```ini
[Scripts]
LogDebugScripts=true
DebugScriptsForceFlush=true
DebugScriptsLogDir=C:/Dev/witcher-music-control/build/sparse-interface-prerequisites-v1/retail-logs/
```

Staged SHA-256: `ec0f09b06fd74984017ad27acbc3564705d0244c7af388e6415f9267a2ecfa4f`. This is a **reversible optional user config experiment**, not an assertion of observed retail activation. Using an existing config file avoids assuming an arbitrary newly named INI is discovered. Installed files remain unchanged.

**User's next action, in order:**

1. Close the game. Open the staged folder in Explorer and inspect `general.ini` in Notepad. Check the installed original hash above. If different, stop for a fresh merge; do not overwrite intervening configuration.
2. Manually copy only the staged `general.ini` to `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\config\base\general.ini`. Keep the exact original rollback. **Do not install the observer or change Vortex yet.**
3. Record UTC time (`(Get-Date).ToUniversalTime().ToString("o")` in PowerShell). Launch by the usual **DX12** route. Stay at the **main menu only**, at most 60 seconds, then quit. Do not load a save/start a game.
4. Open `C:\Dev\witcher-music-control\build\sparse-interface-prerequisites-v1\retail-logs\scriptslog.txt` in Notepad. Expect a **fresh** file with `Debugging scripts for `. WMCCTX1 is not expected without the observer. Missing file/header: stop and report just that outcome. No extra flags, DLLs, install or longer gameplay.
5. With the game closed, restore the original `general.ini` and verify its original SHA. Restore only if the installed copy is still this test's staged hash; otherwise review intervening edits. Preserve the log before another launch: native mode `w` truncates it each startup.

Optional read-only check from repository PowerShell, substituting the actual pre-launch time:

```powershell
python tools/observer_log_smoke.py check --log build/sparse-interface-prerequisites-v1/retail-logs/scriptslog.txt --started "2026-10-19T15:30:00Z" --output build/sparse-interface-prerequisites-v1/smoke-check-1
```

The checker rejects stale/oversized files, reports header/marker counts, saves only WMCCTX1 rows privately and uses the unchanged strict parser. It does not print other mods' log text. Synthetic tests are not runtime log evidence. Report only fresh-header success, no file, or no header; do not upload the full potentially private script log.

### Later observer test, conditional on the sink result

The unchanged source-only ZIP remains:

`C:\Dev\witcher-music-control\build\sparse-live-context-pilot-v1\observer\manual\WMC Context Observer - Diagnostic Source.zip`

SHA-256 `8cb59a83e77c328b2cd050c252411feefa21b8a257b0abd15d9a85f45ab16568`. Observer source SHA `8c78e5fa5b95390364e72a55ed5db73b19215ecf7c55b852c2fe89b053069acc`. No logger adapter/recompile was necessary; previous compiler blobs/counters were revalidated. No claims of a newly compiled or fully merged retail assembly.

Only **after confirming logger output**: use report94's manual Vortex procedure, record enabled/merged state, add only this source diagnostic under `Mods/modWMCContextObserver/content/scripts/local/wmcContextObserver.ws`, and review compilation. No audio-priority change or replacement core scripts. On an error disable only the diagnostic and retain error text privately; do not remove the existing merged folder. A subsequent separately user-run brief ordinary-save load should emit `[WMCContext] WMCCTX1|epoch=...|seq=...|t=...|begin|origin=load_or_spawn` and a `snapshot` within 60 seconds. Missing marker: quit/stop; absence of output is not absence of gameplay events. No forced discovery, progression or custom save. Revert just the diagnostic and this logging config through the user's usual workflow.

### Compatibility review

Read-only installed `Mods` scan retained privately as `installed-hook-review.txt`. Relevant observed overlaps include:

- `modbrothersinarms/content/scripts/local/bia_modMenu.ws:13`: wraps `CR4Player.OnSpawned`.
- `modHoods/content/scripts/local/mod__hoods_Annotations.ws:8`: same wrapper.
- `modzzz_sharedutils/content/scripts/local/sharedutils/oneliners/annotations.ws:25–29`: wraps `CR4Game.OnAfterLoadingScreenGameStart`, calls original then initializes its manager.
- `modMonsterHuntContracts/content/scripts/local/mhcIntroduction.ws:175,187`: corresponding player/load hooks; existing hook order matters.
- `modMovementTweaks/content/scripts/annot.ws:13–19` wraps the derived `W3PlayerWitcher`, not a conflicting new copy of CR4Player. HUD `sah_hooks.ws:433–434` wraps **W3SettlementTrigger**, not the diagnostic's W3FastTravelEntity.

These are compatibility considerations, not proof of a collision. Annotations and `wrappedMethod` avoid wholesale core-script replacement, and the diagnostic calls original once in each wrapper. The native-context compile is not a compile of every current enabled mod. No new source change or merge was made; real annotation ordering/error check remains the manual prerequisite. The logging config does not replace other mods' scripts or install a DLL.

## C. One request hypothesis: existing Trigger + local MusicStinger

Source support: `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\WObjects\WObjects.xml`, `MusicStinger` at line2747, common `Stingers` list line2441, Action35 Trigger line3683 and Action2 Stop line3647. Supported properties allow a Trigger to request a Segment as a stinger, with synchronization/advance/cooldown. They do not supply an expiring request identity or an authored-owner/outro-completion condition.

Fresh complete isolated project: `build/sparse-interface-prerequisites-v1/wwise/candidate/validation/w3_audio.wproj`. `tools/sparse_stinger_probe.py` first verifies exact report90B source, then removes **only its automatic cue playlist reference** `{E628DC21-010A-49FB-BA2F-DDB4B588857B}`. All original objects remain. Selected playlist `{4A23933D-BE41-4C79-BED2-337D24C605EA}`, ShortID133462974, now loops the retained native rest rather than eventually starting the cue automatically. Source restoration proves exact original semantics after reinserting that reference. This supplies an honest no-request silence control.

In-memory-only additions:

- A local MusicStinger attached to that playlist, referencing existing approved segment `{22B6E6E1-528D-47DD-98F1-C1B3C1AD800A}` /1029261546. Track499024852 and source remain unchanged.
- Existing Trigger `{90730515-839D-472E-BE48-C0B95033193D}`, `TEMP_cmb_prototype_attack_special01`, from `Triggers/music.wwu:6`. Only its source definition was found in the reviewed WWUs; this **does not exclude hidden native producers**. Private reuse tests the mechanism without editing global definitions; it is not approved as a production control or proven compatible generated-bank dependency.
- `PlaySegmentAt=0` Immediate, `NumSegmentAdvance=0`, `DontPlayAgainTime=45s` as technical fixture cooldown, **not** a TTL, request identity or final default.
- Event `WMC_Private_Request_Stinger`, Action35 Trigger; no direct child Play. Follow-up cancellation Event `WMC_Private_Cancel_Stinger`, Action2 Stop targeting this cue segment only; no global Stop/mute.

Existing gains, States, native selectors/fades/transitions, combat definitions, authored branch, Music master and global definitions are unchanged. Additions are discarded at process close, not bank-generated. The fixture is a rejected hypothesis, not a production source extension.

## D. Actual authoring results

15 cases across fresh `stinger-captures`, `stinger-followup`, `stinger-expiry` directories; profiler paths, settled State observations, RTPC values, action acceptance clocks and 50ms PCM envelopes retained. Immediate State reads can be stale; combat was independently settled by the **later request event** and actual combat voices. A pipeline may exist while virtual/muted; audibility below distinguishes this.

| Test | Observed result | Interpretation |
|---|---|---|
| No request,55s | PCM peak0; repeated native rests, no S04-a pipeline | Genuine off-policy silence |
| Valid request ~6s | Cue audible6.309–47.061s | Positive request-driven start |
| Duplicate at6/12s | One cue pipeline6.451–47.047s | Cooldown suppresses tested duplicate, not general idempotency |
| Combat4s; request6s | Settled combat State; cue audible6.575s while combat continues; native outro24.767–29.555s | **Protection failure**; outgoing rest still lives until8.381s |
| Request25s during return | No cue in this capture; native outro25.413–30.317s | Early negative observation does not prove complete-outro protection |
| Request28s during return | Cue audible28.579s, native outro25.628–30.500s | **~1.92s measured overlap with complete native outro** |
| Dialogue4s; request9s; exploration18s | Cue pipeline9.279s, audible only18.292s onward | **Stale/ineligible request survives to a later context**, not an audible dialogue success |
| Active cue then combat12s | Cue remains audible through46.984s; native outro32.733–37.613s | **No native preemption guarantee** |
| Active cue then authored event12.1s + dialogue12s | Cue becomes inaudible after14.058s; authored score is audible | Native/dialogue attenuation observed, not proof of cancellation/expiry |
| Authored request, wrong-location→return, Gwent request | No new cue observed in these cases; protected material present where applicable | Negative controls only; no safety claim |
| Cancel active cue at12s | Cue still audible through25s end of capture | Targeted Stop action does not cancel this stinger instance in tested configuration |
| Dialogue request9s; cancel12s; return18s | Cue still becomes audible18.204s | Cancellation also fails to invalidate the latent cue |
| Music100→50→100 | Effective cue gain−18.9966→−25.0206→−18.9966dB | Native master remains functional |

**Important negative-test limitation:** the 45s stinger cooldown/history was not independently reset between every case inside a server. It can confound negative interpretations. We do not use those negatives as ownership proofs. It cannot explain away the positive unsafe starts, stale playback or failed cancellation. Server/transport and RTPC setup, initial selectors and actual voice ancestry are in the raw records. No second architecture was implemented merely to mask these counterexamples.

### PCM identity and native behavior

Independent `tools/sparse_interface_review.py` aligns the valid-request Recorder clock to the entire approved PCM by correlation, then checks all1,960,800 stereo frames at native gain. Recorder offset4.253333s is **not** the wall-clock request time. Source40.85s including the baked tail is preserved; maximum quantization difference0.989845 PCM16 units, RMS0.488662; extra Recorder channels and post-tail rest exactly zero. Original dry-stop/Exit30.85s, baked tail through40.85s unchanged. All captures decode as validated48kHz Recorder PCM; maximum observed peak5991/32768, no clipping.

Combat layer1/layer2 and threat0/35/100 remain in profiler traces; native outro reaches its original gain (~−19dB) and full transition span. The failure is **additional generic playback over them**, not a repaired/muted/shortened combat structure. No subjective listening or retail playback is claimed.

## E. Why not call this a gateway or force another workaround?

Observed: the MusicStinger can launch alongside an outgoing generic node, persists across combat, and can be inaudible in dialogue then become audible later. Source detail: selected playlist133462974 retains base Voice Volume-2dB; exploration CustomState967536041 and combat385219422 have no additional Volume override, while dialogue251479027 adds-200dB. These unchanged per-playlist gains are not an admission/cancellation gate. The outgoing native rest remains alive through8.381s after combat was requested around4.136s, so a Trigger near6s still finds the local node. A dialogue-created voice continues virtually/muted and later becomes audible mid-cue; this is not proof that a new start was queued at return. Its cooldown is unrelated to an opportunity's lifetime. No successful cancellation/commit acknowledgment has been established. Therefore it does **not** provide the required transaction: validate current eligible owner → accept exactly one live request → preserve complete native outro → acknowledge start/completion/cancel.

Source/schema review of a normal MusicSwitch/playlist transition is not a second passing mechanism. Native rules respond to selector changes and defined musical boundaries; the reviewed hierarchy exposes no safe external one-shot playlist-advance command (report94 Seek was not one). Adding a persistent selector or changing vanilla game_state/music_type to force a transition would evade the constraints, not solve priority. We stopped after **one** justified approach rather than implementing an unsafe second.

Smallest feasible interim alternative: keep report90B's already verified **native rest-first automatic playlist** as the playback control and use the observer/model only for diagnostic decisions, with no audio connection. For genuinely contextual positive requests, a separately authorized **local one-shot gateway/acknowledgment design** is required: request generation+deadline, admission only after verified native outgoing playback has relinquished ownership (not exploration State alone), and actual started/stopped/cancel completion. Script signals in report92 do not expose those facts. Merely adding a new Trigger or a longer arbitrary cooldown is insufficient. Any new scoped control definition/native callback bridge must be explicitly evaluated for Init and cancellation compatibility before implementation; none is silently assumed available here.

## F. Preservation, tests, process cleanup and stopping point

- All1,508 original WWUs retained;542 Event WWUs/global WWUs byte-exact on disk;47 original regional audio inputs exact; approved engine WAV SHA `5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc`.
- New isolated music source SHA `1a148316567f90233926e66499b3f321308b38f1c6d0f070bd05aef0cc9ac230`. Restoring the single removed reference restores report90B semantics exactly; unrelated source changes rejected.
- All24 accepted cues, ten retained release/native inputs (including native Init), report88 bank, report90 source snapshots and68 native compiler runtime inputs independently rechecked against report94 retained pins. Installed REDkit source also checked against input fingerprints. No licensed project/key was read/copied/transferred.
- Full repository Python suite: **289 tests pass**, including8 new synthetic source-restoration, unrelated-edit rejection, read-only log filtering/freshness, malformed-marker, config-merge refusal PE bounds/version and audible-versus-virtual overlap checks. Expected negative-gate diagnostics in the test log are asserted test cases, not hidden failures.
- Existing observer pristine/matched-control compile evidence remains exit0, native assertions20,893 baseline vs20,901 candidate/control; no Script/WCC errors. Full merged-mod compile and runtime remain pending.
- All three authoring sessions/captures exit their Python runners0, no cleanup errors; WwiseConsole exit1 follows explicit project close, as in previous fixtures. No generation diagnostics exist because no banks were generated. Task-owned authoring processes stopped.

**Stop:** both investigations are complete to the authorized boundary. The observer is compiled and packaged, but **not ready for unconditional install until the logger smoke test passes**. Your exact next action is the reversible **logger-only main-menu test** in sectionB; leave the observer ZIP and current audio installation alone, then report only whether the fresh native header appeared. The contextual model must remain disconnected from this failed request primitive.
