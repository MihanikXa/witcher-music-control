# White Orchard prototype blocker review — 2026-10-11

## Outcome

**No deployment candidate.** The complete isolated source project cannot generate Init under the current licences. We have demonstrated a Wwise-native solution to the measured bypass discontinuities and a reproducible native-tool two-bank cache workflow. Those two proofs do not make the existing incomplete Init safe.

No installed game/REDkit/Wwise/reference files were edited, no software or licence was installed, no playthrough/save was changed, and no depot was regenerated. Original report 10 recordings and banks remain in `build/white-orchard/`. Follow-up experiments are separate. No settings UI, other-region routing, or WitcherScript state hook was added.

## Evidence paths

Machine-local aliases below are exact evidence paths, not distributable assets:

| Alias | Absolute path |
|---|---|
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| R | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc` |
| F | `C:\Dev\witcher-music-control\build\white-orchard-followup` |
| V | `C:\Dev\witcher-music-control\build\white-orchard-followup\validation` |
| C | `C:\Dev\witcher-music-control\build\white-orchard-followup\cooker-reproduction-2` |
| Console | `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe` |
| Cooker | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe` |
| Object definitions | `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\WObjects\WObjects.xml` |
| Helpers | `C:\Dev\witcher-music-control\tools\white_orchard_prepare.py`, `white_orchard_native_fade.py`, `white_orchard_fade_measure.py`, `white_orchard_contexts.py`, `white_orchard_cooker.py` in that same tools directory |

References like F/full-retained-banks/generation.log expand against that absolute F path. Report 10 lists the unchanged original pilot paths and object GUIDs.

## 1. Init fidelity: still blocked

### Controlled complete-project experiment

**Observed:** the source contains **1,508 .wwu files, 119,495,719 bytes**. `Prepare.prepare(..., preserve_hierarchies=True)` copies all of them recursively, byte for byte, without pruning any default ChildrenList or music/event/bank hierarchy. It copies the same 47 White Orchard originals needed for the selected bank. Project changes are restricted to isolated output/cache/originals paths, disabled external/generation commands and source control; the final control retains the original PhysicalFolderList and folder IDs. The command still selects only Windows/SFX `music_prologue`, allowing Wwise's automatic Init output.

Evidence: F/full-baseline/input-manifest.json and unchanged work-unit copies; F/full-retained-banks/command.json and generation.log. This tests unmodified **authoring definitions**, with necessary output isolation; it does not pretend the project file itself is byte-identical.

**Observed failure:** generation exits **1**, producing **no banks**. The log reports:

- Six HomeCinema errors: no Mastering Suite licence.
- Fatal trial limit: **26,218 media items, 200 permitted**, despite selecting only `music_prologue`.

The earlier first complete-copy run removed PhysicalFolderList and emitted unknown-folder warnings; that evidence remains in F/full-baseline-banks/. The final control restored that list and removed those warnings, but the same licence failures remained. Thus generation scope does not solve the project-wide media licence limit.

**Conclusion:** an unmodified isolated full hierarchy cannot generate a vanilla-equivalent Init in this environment under the current licences. Equivalence after appropriate licensing is **untested**, not guaranteed.

### What preparation explains—and what it does not

The legacy preparer empties eight default roots and removes unrelated actor/music/events/banks. That is unsafe as a basis for global Init fidelity. Keeping all project usage is the next legitimate baseline. However, every GLOBAL_CATEGORIES directory actually has all its work units at its top level: e.g. Effects 6/6, Game Parameters 11/11, Audio Devices 1/1, Master-Mixer 1/1. The top-level glob therefore drops **no nested global work unit on this machine**. It should not be blamed for every missing native object.

Source-object inventory: F/full-global-objects.json queries Bus, AuxBus, AudioDevice and Effect in the complete, matching-version WAAPI project: 56 / 41 / 4 / 357 objects. Only missing native ID **4131355637** resolves there, to `W/Effects/Factory Mastering Suite.wwu`, `HomeCinema`, GUID `{F9951DC8-664E-4B07-81CF-61716236F00A}`. The other ten missing IDs remain unnamed in this complete inventory. Possibilities include generated internal objects or differences between the available authoring project and shipped globals; neither explanation is established.

**Important correction:** native HIRC type 18 is AuxBus here, not AudioDevice. F/native-hirc-type-crosscheck.json cross-matches 56 known Bus IDs to type 8, 41 AuxBus IDs to type 18 and all four AudioDevice IDs to type 21. The reduced baseline retains those four AudioDevice HIRC records unchanged; its missing ID 4189995869 is an AuxBus. Report 10's original label has been corrected. This does not remove the missing HomeCinema effect or reduced plugin-registration problem.

**Further observed mismatch:** installed REDkit's `bin\initialdata\sound\Init.bnk` is **31,159 bytes**, SHA-256 `f4d026aeb16ee778de6a1e85ec3f7e41c68c817c3ac1066e5a27da286cfa8506`; game bootstrap, game cache and R/Init are **32,840 bytes**. The REDkit bootstrap adds one HIRC object, omits five, and changes nine compared with game Init; INIT and STMG also differ. Evidence: F/redkit-bootstrap-init-comparison.json. Merely substituting REDkit's loose bootstrap is not a native-preserving workaround.

### Best next path and acceptance

Obtain an appropriate project licence for the full source's media count **and** a matching Mastering Suite licence, then rerun the preserved complete-project control. No key was changed or activated here. Require retention of native buses/AuxBus/devices/effects, plugin registrations, game syncs, RTPC defaults, references, native Music curve and platform data; explain every non-BKHD difference before authoring the final mixer. If licensed regeneration still differs, resolve source/build provenance before proceeding.

No binary records were spliced. A byte-level augmentation remains unacceptable while global serialization, IDs/references and runtime/plugin requirements are not fully verified. None of the old generated Init files is eligible for packaging as a deployment candidate.

**Falsifier:** a successfully generated complete control retaining all native globals would clear this blocker. A clean licence log alone would not.

## 2. Transition smoothing: native alternative demonstrated

### Construction

The smallest **demonstrated** native alternative uses parallel State-volume paths. It is larger than the failed three-slot mixer; no claim is made that no smaller possible construction exists.

Retain `Music/WMC_WorldMusic` as a unity aggregate, with no State group or shipping effect. Under it create:

- `WMC_DryMuted`, ordinary Bus, base BusVolume -200 dB.
- `WMC_Fade_exploration`, `WMC_Fade_dialogue`, `WMC_Fade_combat`, AuxBus objects. Each has unity **base** BusVolume, a continuously processed Gain effect, and State BusVolume 0 dB when its category is active / -200 dB otherwise.
- `WMC_Fade_other`, AuxBus, no Gain effect. State BusVolume 0 dB for all other states / -200 dB in E/D/combat.

Route only `music_prologue/world_music`'s dry output to WMC_DryMuted. Enable its own UserAuxSend0–3, send volumes 0 dB, targeting the four AuxBuses. The added muted dry path prevents parallel unity output from doubling the original dry signal. The existing quests_and_cutscenes output remains Music, with no added sends or gains.

The three Gain effects keep FullBandGain and LFEGain bound to the existing pilot's custom **0–100 amplitude-percent** parameters and the tested `(0,-96.3)/(100,0)` curves. Gains are never bypass-switched. Numeric BusVolume States use the existing game_state's native transition timing. Neither that StateGroup nor events, switch entries, playlists, source audio or threat/intensity controls is edited.

F/prologue-native-aux-audit.json finds no stored Aux properties/references on the original world root or its descendants; the four new sends do not overwrite a discovered prologue-world send assignment. Other regions and native game-defined sends are outside this edit.

Local support: Object definitions/UserAuxSends:595 onwards declares four AuxBus references and volume properties; BusVolume is a numeric decibel property. W/States/global_states.wwu/game_state retains its existing TransitionList (including 1.5/2-second None transitions) and default timing. `tools/white_orchard_native_fade.py/run` implements this experiment; V/Master-Mixer Hierarchy/Default Work Unit.wwu and V/Interactive Music Hierarchy/music.wwu contain its saved validation graph and full 25-state table.

### Controlled measurements

V/native-fade/results.json and measured.json, produced by `white_orchard_fade_measure.py`, contain three approximately 20-second continuous 5.1 recordings: cutscene → exploration → dialog_scene → combat → cutscene, four seconds per state. Percent inputs for the unequal run were **25.118864 / 6.309573 / 50.118723**, not negative-dB parameter inputs.

| Check | Observation |
|---|---|
| Unequal levels, first full-band channel | 0 / -12.010 / -24.049 / -6.003 / 0 dB relative to protected-state unity |
| Other full-band channels and LFE | Corresponding target levels within 0.15 dB |
| Native transition peak adjacent sample changes | At most 155 counts full-band, 14 LFE; within the normal tone step range plus PCM quantization |
| Repeated original Boolean test | Up to 1,575 full-band counts, 1,265 LFE, in the broad transition windows |
| All three sliders 100% | Steady-state unity in every tested context; 100-ms envelope range approximately -0.020 to +0.018 dB across channels, without a large crossfade dip or doubling |
| Defaults 0/0/100 | Exploration and dialogue stable PCM windows zero on all six channels; combat and cutscene unity |

All **28 acceptance checks** passed: six-channel steady levels, transition sample-step limits and the unity envelope. These demonstrate continuous gain transitions for the tested tone and preserve independent controls. They do not establish internal floating-point exact zero, subjective click-free native music in the game, all 25 states empirically, movie playback, save/load, or live slider-change smoothing.

**Capture pitfalls retained:** V/native-fade-base-error records the failed -200 dB **base** plus numeric State addition; active paths were still muted. V/native-fade-recorder-reset and native-fade-with-anchor retain shortened/inadequate captures. Removing stale game_state association from the aggregate bus yielded complete recordings; a silent anchor fixture keeps the recording bus active at zero gain. The anchor and Recorder are validation-only, not shipping objects. The accepted WAVs are in V/native-fade/. Do not use shortened runs as evidence of a smooth transition.

### Authored protection and master volume

V/contexts-native-fade/contexts.json again selects actual White Orchard village exploration/ordinary dialogue and the native combat layers through WMC. q001 tavern intro and conversation select their original sources with **no WMC bus in their contribution paths**. The direct conversation recording has positive PCM while exploration/dialogue parameters are 0%.

V/contexts-native-fade/protected-measured.json finds the protected synthetic path changes by at most **0.025 dB** between all-zero and all-unity contextual controls, within the 0.15 dB test tolerance. Native Music 50% produces approximately -6.00 dB. No added quest attenuation or loss of master control was measured.

The first protected synthetic run mistakenly retained the fixture's explicit AuxBus references, causing parallel playback. That failed evidence is in V/contexts-native-fade-fixture-aux-leak/. Turning off OverrideUserAuxSends alone does not discard stored sends on a root Sound directly under a WorkUnit. The corrected helper explicitly clears those four test references. No actual quest object had those fixture sends.

**Decision:** no SoundGameStateChange hook or script fade fallback is justified. The native alternative meets the tested transition requirement; game listening/transition/load tests remain future acceptance. The original shipping author recipe is retained as the failed baseline; this revised graph is currently a validation experiment, not a newly certified generated mod.

## 3. Minimal packaging: offline workflow reproduced

### Isolated root/bootstrap

`-root` works as **two arguments**, `-root <absolute-root>`, rather than the ineffective `-root=<path>` attempt. Use an isolated cwd `<root>/bin/x64`, whose parent holds gameconf.cfg. Relative config/data paths refer to that isolated root. The existing installed Cooker is executed in place; no executable/DLL is vendored.

`white_orchard_cooker.py/prepare` reproduces the successful bootstrap in C: existing config files, native dep.cache/static shader/compiled-script copies, gameplay globals CSV/XML, game/dlctable.csv, native Init and available always-loaded raw banks. It records **455 input-copy entries with hashes**. These are cooker inputs, not deployment files. The copied startup table filters the one absent `ly_animal_dog.bnk` entry and null padding **in the isolated tool root only**; it does not repair or rewrite installed resources. Source table is retained separately.

F/cooker-root/help-no-content-cache-result.json proves help exit 0 with the full game cache removed from the active root. Thus no 4.6 GB cache, partial depot or depot regeneration is needed for this demonstrated bootstrap. Preparatory attempts/logs are retained; the required Init/raw-bank directory, tooltip/economy globals and game/dlctable.csv were exposed by actual initialization failures. Nonfatal legacy config/script assertions remain in successful logs; this is a commandlet bootstrap, not a playable game clone.

### Bank-only cooking

Provide an isolated directory containing **only native fixture Init.bnk and music_prologue.bnk** via `-soundbanksdir`. No wwiseProj is supplied, no Wwise process is spawned and no banks are regenerated. Use:

```text
cooksounds -root <root> -soundbanksdir=<inputs> -outdir=<fresh-output>
           -platform=pc_dx12 -r4remastersounds
           -outsplitfile=<fresh-output>/audio-split.list -noninteractivecrash
```

Initially this reached SoundModCooker and failed on absent `soundbanks\soundsplitseed.csv`. A recursive search found no such file in installed REDkit. The supplied E: partial-depot path was unavailable in this session; no dependency or repair was inferred from that.

**Observed workaround:** a header-only `bank;chunk` CSV with **zero mappings**, created only in the isolated root, lets the native cooker use its explicit unlisted-bank **content0 fallback**. Header labels are not a verified full seed schema. Both banks receive content0 mappings. Compiled diagnostic evidence: F/sound-cooker-schema-strings.json, Cooker/soundCommandletHelper.cpp diagnostics. Runtime evidence: C/fixture-cook.log and generated audio-split.list.

Cook exits **0**, but logs missing .txt bank descriptions and absent seed mappings. Those diagnostics must not be hidden: this test intentionally includes no extra streamed WEM media. All fixture bank bytes, including their existing media references/prefetch, are native. Whether a mod's omitted streamed entries resolve from vanilla at runtime remains a live-loader acceptance test.

### Output and native reader check

`C/native-fixture-cooked/CookedPC/soundspc.cache` is **207,806 bytes**, CS3W v2, exactly two indexed resources and no indexed WEMs:

| Entry | Offset | Bytes | SHA-256 |
|---|---:|---:|---|
| init.bnk | 64 | 32,840 | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |
| music_prologue.bnk | 32,904 | 174,826 | `75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912` |

Both extracted payloads equal the inputs byte for byte. `splitcache sounds` exits 0, reads both entries through the native cache reader and rewrites content0 with the same two payloads. C/fixture-verified.json records hashes and exact commands/logs; this full helper run used a fresh bootstrap with **no copied game cache**. The earlier manual fixture/reproduction attempts remain in F/cooker-root/ and cooker-reproduction/.

**Header caution:** the splitter rewrites bytes at header +28/+29 without changing the indexed resources or payloads. Their meaning is unverified; do not treat +28 as a Remastered streamed-media count or manually zero/splice it. Prefer the direct `cooksounds -r4remastersounds` output as the future bank-only mod cache; split output is a native-reader check, not required for a single content chunk. Native game index classification is actually **740 .bnk + 1,434 .wem = 2,174 resources**, not 2,174 banks (F/cache-entry-classification.json). Legacy FMC layout must not be assumed identical merely because it also says CS3W v2.

**Proof boundary:** native-tool serialization and offline native-reader acceptance are demonstrated. Actual game mod-cache precedence, omitted-media fallback and bootstrap Init replacement are **not live-tested**. The fixtures contain vanilla banks, not the WMC mixer. They are not a deployment candidate.

## Proposed final graph and next build

```text
vanilla game_state ──► numeric State BusVolume gates on four AuxBuses
vanilla music_type ─► unchanged music_prologue world/quest selection
future settings only ─► E / D / combat global amplitude percentages (0–100)

world_music ── dry ──► WMC_DryMuted (-200 dB) ────────────────────┐
      ├─ user send 0 ► exploration State gate + continuous Gain(E)│
      ├─ user send 1 ► dialogue State gate + continuous Gain(D)   ├► WMC_WorldMusic
      ├─ user send 2 ► combat State gate + continuous Gain(C)     │   (unity aggregate)
      └─ user send 3 ► other-State unity gate ────────────────────┘          │
quests_and_cutscenes ───────────────────────────────────────────────────► Music
                                                    native volume/fades/muting │
                                                                      native output
```

The next substantive build starts with the **licensed complete-project Init control**, not another reduced Init or a binary splice. Once native equivalence is established, adapt the existing author recipe to the measured parallel graph, excluding all test sounds/anchor/recorders, then selectively generate only Init.bnk and music_prologue.bnk and compare every unrelated record/media payload. Do not introduce scripts to solve an Init licensing problem.

Minimum proposed deployment remains a matching loose bootstrap **Init.bnk** plus `mod…/content/soundspc.cache` containing those two complete bank entries; no new source audio, streamed WEM, UI, script or other regional replacement. Cache generation/helper metadata and 143,258,312 bytes of bootstrap input copies are **not** deployment content. Confirm native-media fallback and Init/cache precedence during a later explicitly authorized isolated White Orchard test. This remains bank-scoped, not a White Orchard geofence; world-location exceptions remain the separate later milestone in report 07.

## Final verification

F/protected-input-verification.json rehashes the original pilot's 93 inputs, complete-project control's 1,556 inputs and cooker reproduction's 455 copy entries against their installed read-only sources: **zero changes**. Python compilation and `git diff --check` passed. The original pilot bank/recording workspace was not overwritten. New failed runs are retained separately with descriptive names. Task-owned Wwise/WCC processes were stopped; no live deployment occurred.

## Reproduction

Use fresh output roots to retain all evidence:

```powershell
python tools/white_orchard_prepare.py --audio-project 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio' --output build/<fresh>/full-baseline --preserve-hierarchies
python tools/white_orchard_wwise.py --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' --project build/<fresh>/full-baseline/w3_audio.wproj --output build/<fresh>/baseline-banks
```

The second command currently fails on the two licence conditions; do not package any incomplete output. For the cache fixture independently:

```powershell
python tools/white_orchard_cooker.py prepare --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit' --root build/<fresh>/cooker
python tools/white_orchard_cooker.py native-fixture --root build/<fresh>/cooker
```

For smoothing, copy the original isolated prototype to a fresh `validation` directory, open that copy in matching localhost WAAPI, run the existing Probe/Contexts/Transitions first, then NativeFade and FadeMeasure. NativeFade refuses an existing output folder. Sources/commands are in the named helpers and the preserved F workspaces. All test calls use amplitude percentages, with dB values only as measured/expected output levels.
