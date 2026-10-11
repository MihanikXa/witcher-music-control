# Complete-context White Orchard State-volume build — 2026-10-11

## Decision

**The local State edit serializes correctly, but no deployment candidate is certified.** Complete-context selected generation fails the trial-media gate. Supported file-leaf exclusion clears that gate and emits a regional bank whose only HIRC change is the intended inline world Voice Volume data. Both reduced-media builds still exit **1** with six Mastering Suite errors. Generated bank project identity is **0**, versus native **39**; loading this regional bank with native Init has not been demonstrated. No header was patched and no failed output was packaged.

This advances [report 14](14-full-context-bank-experiment.md): bank serialization is now measured, rather than a hypothetical authoring-to-runtime step. It does not invalidate report 13's playback/fade evidence or establish in-game behavior. The target remains playable **White Orchard**, technically `music_prologue`, with fixed exploration/dialogue suppression and combat/other unity. No sliders, state hook, other-region edits, deployment, save changes, licence application or depot generation occurred.

## Evidence paths

All aliases below resolve to exact local paths. Generated banks and original source/media are ignored evidence, not committed or distributable assets.

| Alias | Absolute path |
|---|---|
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| R | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc` |
| T | `L:\Programs\Wwise_2023.1.19.8928\Authoring` |
| P | `C:\Dev\witcher-music-control\build\white-orchard-full-context-stage1` |
| Clean author | `C:\Dev\witcher-music-control\tools\white_orchard_state_volume_author.py`, `author` / `semantic` |
| Bank audit | `C:\Dev\witcher-music-control\tools\white_orchard_state_bank_audit.py`, `audit` / `state_chunk` / `native_groups` / `header` |

P contains complete `baseline`/`candidate` and fresh complete `leaf-baseline`/`leaf-candidate` controls. Each retains **1,508 original work units**, with 47 referenced originals totaling 900,846,184 bytes. Installed input provenance is recorded in each `input-manifest.json`. Project paths/commands are isolated by `white_orchard_prepare.py --preserve-hierarchies`; no regional hierarchy was removed.

## 1. Clean helper review and source acceptance

The helper targets existing GUID `{1A59CC64-141A-45A6-8374-EB823D3E9D4F}`, ShortID **1033516231**, and existing `game_state` GUID `{27711515-3584-4123-9F09-B90831398B80}`. It checks project path/build8928, complete manifest, absence of prior world StateInfo, existing group/name/count, and disjoint category membership. It calls only `setStateProperties`, `setStateGroups`, `setProperty`, and `project.save`; no fixture, audio, bus, effect, parameter or global State is created.

Added audit guards read back all **25** saved local values and global State references, reject added/deleted work units, and compare the music XML after removing **only world/StateInfo**. P/candidate/state-volume-clean-authoring.json passed: only `Interactive Music Hierarchy/music.wwu` changed, unrelated work-unit list empty, all units retained, source semantics restored exactly.

**Observed save normalization in the inclusion control:** its first strict XML audit failed because Wwise moved experimental Inclusion properties within PropertyList and converted shorthand `Value="False"` to a single default `ValueList/Value`. Values and platform qualifiers did not change. P/leaf-source-semantic-differences.json records **zero** differences after normalizing only property-list order and that equivalent single-default serialization. The first failed authoring audit remains intact. Bank audit independently confirms all source semantics differ only by world StateInfo. The helper now performs that normalization; it never ignores child/container order, platform-qualified values or property names/types.

The new source has no altered quest branch, user Music curve, event, switch, global transition or audio source. All clean controls are separate from report 13's Recorder/tone workspace.

**Fresh verification repeat:** P/leaf-candidate-repeat is another complete copy prepared from installed read-only inputs, with the same leaf exclusion. The revised helper passed all source guards, including the normalized semantic comparison. Its generation still exits1 with the same six errors, but reproduces **exactly the same regional and disposable Init SHA256s** as the first candidate. It did not enable the optional readable setting. P/repeat-state-bank-audit.json passes all **19 structural/source/media checks**, as does the first candidate's final audit. This validates the helper fix and binary reproducibility without reusing an authored or instrumented project.

## 2. Controlled generation

Exact Console argument arrays, complete logs and exit/results are P/<output>/command.json, generation.log and result.json. Console is T/x64/Release/bin/WwiseConsole.exe, **v2023.1.19/build8928**. All output/cache directories are inside P. The selected command uses Windows/SFX `--bank music_prologue`, no source control, no decode, no wwise.dat writing, and empty custom opening/closing/pre/post commands. No licence override or error suppression was supplied.

| Output directory | Input | Exit | Banks emitted | Blocking diagnostics |
|---|---|---:|---|---|
| `full-baseline-banks` | Complete untouched hierarchy | 1 | None | Trial media 26,218/200; HomeCinema licence errors |
| `full-candidate-banks` | Complete hierarchy + local State volumes | 1 | None | Same media limit and licence errors |
| `leaf-baseline-banks` | Complete hierarchy + controlled leaf Inclusion | 1 | Init, music_prologue | Six HomeCinema/Mastering Suite errors; media-limit fatal absent |
| `leaf-candidate-banks` | Equivalent Inclusion + local State volumes | 1 | Init, music_prologue | Same six errors; media-limit fatal absent |

`white_orchard_init_audit.py --exclude-file-leaves` records **41,429 excluded AudioFileSource instances**, **133 retained prologue instances**, every edited ID/previous value, and unchanged global work-unit hashes. This disables file-backed Sound/MusicTrack leaves outside Prologue; it does not delete nodes, work units, source plug-ins, events, banks or dependencies. It is an experimental compiler-usage reduction, not a shipping project policy.

The six licence errors explicitly name **Init / HomeCinema**, not music_prologue. They do not by themselves prove that the emitted regional structure is corrupt or that a licence is inevitably required for this Init-free design. The observed job fails; regional/native-Init compatibility must be established independently before accepting its emitted file.

An optional, symmetric `SoundBankGenerateReadableFile=True` project setting was also tested on the leaf pair. The installed definition is T/Data/WObjects/WObjects.xml:6185. It emitted two-byte `[]` .rbnk files, supplying **no useful structural decoding**. P/readable.py and each leaf/readable-option-audit.json preserve this exact metadata-only change. The useful generated files are SoundbanksInfo.xml and bank bytes; the decoder below does not rely on empty readable output.

P/bank-comparison.json and P/state-bank-audit.json establish:

| Regional component | Native / untouched control | Modified control | Result |
|---|---:|---:|---|
| Bank size | 174,826 | 174,943 | +117 bytes |
| HIRC payload | 60,274 | 60,391 | Only world ShortID1033516231 changes |
| World body | 430 | 547 | Inline State block replaces empty block |
| DIDX / DATA | 84 / 114,384 | Same | Byte-identical to native |
| Added / removed HIRC IDs | 0 / 0 | 0 / 0 | No new local/runtime object definitions |
| All non-world HIRC bodies | Native | Exact native match | Events, actions, quest structures, tracks and streaming references preserved |

All **47 converted .wem files** under the two authoring `.cache` directories also match by relative path and SHA256. Those are paired conversion checks, not a claim that every generated stream was independently compared with the installed game. Existing native stream references remain exact and no new streamed media would ship. The shared chunk/HIRC reader now rejects truncated headers/records, duplicate chunk tags and duplicate HIRC IDs instead of silently accepting dictionary replacement.

Native regional SHA256: `75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912`.
Untouched leaf control: `6f12d7d1322532d14af097c02dd024dcceb5b8a5664f38add85b44dd9b3611c9`.
Modified leaf control: `bfb418033c0bacc261e787747551800f4eae19997f3e71f64f313da172d60edf`.

**Disposable Init:** both leaf outputs are byte-identical, 29,332 bytes/SHA256 `f0297a4166ac8618a0ea036bde0f8e3feb8e2eb554d2fa37a8bd7fbae55f3476`. They retain the report12 omissions: eleven native HIRC records, two plug-in registrations and non-equivalent STMG. No surviving Init HIRC record changes. This proves the local State addition did not change the experimental global output; it does **not** make that Init usable. Native Init remains 32,840 bytes/SHA256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` and is the only intended runtime Init.

## 3. Decoded HIRC State serialization and dependencies

The read-only audit validates the measured v150 world layout against actual bytes, clean XML and Wwise metadata. Parser-author primary code was consulted without installing/executing it: [wwiser wparser.py, pinned commit](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/parser/wparser.py), functions `CAkStateAware__ReadStateChunk`, `AkPropBundle_float_unsigned_short___SetInitialParams`, `CAkBankMgr__ProcessBankHeader`, `CAkBankMgr__ProcessGlobalSettingsChunk`; associated enums are in [wdefs.py](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/parser/wdefs.py). This is a reverse-engineered parser's primary implementation, **not Audiokinetic SDK authority**. Local byte/metadata cross-checks are recorded in P/state-bank-audit.json; provenance is P/parser-source-provenance.json.

World's numeric HIRC type is **12** in this bank; prior notes loosely calling it type13 should not guide parsing. Source object remains MusicSwitchContainer. At body offset **28**, an empty two-byte State block becomes 119 bytes. Prefix [0,28) and suffix after the respective State block ends are exact native matches. The new block contains one property **0 / additive2 / inDb1**, one group **766723505 / sync0 (Immediate)**, and nine inline one-property float bundles. Each value is −200. No local CustomState ShortID is serialized and no type1 State record is added. Sixteen zero additions are omitted.

| Serialized State | Existing numeric State ID | Voice Volume dB |
|---|---:|---:|
| dialog_scene_night | 360867343 | -200 |
| focus_exploration_night | 1432638110 | -200 |
| boat | 1795056175 | -200 |
| underwater | 2213237662 | -200 |
| exploration | 2582085496 | -200 |
| underwater_focus | 3708995963 | -200 |
| dialog_scene | 3757878140 | -200 |
| exploration_night | 3817056875 | -200 |
| focus_exploration | 3985602033 | -200 |

Group/State IDs match P/leaf-candidate-banks/SoundbanksInfo.xml's `StateGroups/game_state`; source States/global_states.wwu is unchanged. R/Init.bnk's decoded STMG already contains group766723505 and the native transition table. `focus_exploration_night` and `underwater_focus` have no custom-transition entry there; STMG's transition list is not an exhaustive State enumeration. The initial overstrict transition-membership check is preserved in P/state-bank-audit-first-check.json and corrected explicitly, rather than interpreted as missing runtime objects.

**Supported inference:** this serialized edit requires no new global bus/effect/parameter/plugin or local State record in Init. Existing native group transitions can drive the additive property, consistent with report13's native fades. Actual bank-loaded fade/playback acceptance is still required. Unchanged complete non-world HIRC and exact world prefix/suffix preserve existing output inheritance, Music master, threat/intensity structures, decision tree and quest routing, including q001 conversation/intro. Authoring audio evidence remains report13; no new claim of in-game q001 playback is made.

## 4. BKHD differences: identified versus unresolved

All three regional banks are version150, bankID3228744150, languageID393239870, alignment flags16 and bank type0, with identical padding. Based on the pinned parser, offset16 is **dwProjectID**, not an audio-gain property. Native is **39**, both generated controls **0**. This remains an unresolved loader-compatibility condition, not a measured rejection: no game or separate native-Init runtime was exercised.

Offsets24–39 form the 16-byte bank hash. Generated bytes exactly match each `SoundBank Hash` GUID in SoundbanksInfo.xml using GUID byte order. Thus offsets24/28/32/36 are **one hash**, not four unexplained routing/dependency IDs. The modified hash differs from the untouched control as expected. The untouched hash also differs from native despite identical playable data; the exact hashing inputs/project provenance are not established, and no native metadata hash was available for an independent native cross-check.

[Audiokinetic LoadBank documentation](https://www.audiokinetic.com/en/public-library/2024.1.5_8803/?id=namespace_a_k_1_1_sound_engine_a496b9917fe035f301bcff0accd61f80f.html&source=SDK) requires content and initialization banks from the same project. This supports treating the identity difference seriously; it does not establish the Remastered runtime's comparison rules or whether zero is specially handled. Source project GUID is preserved, but that GUID is not the observed numeric BKHD field. No supported editable `dwProjectID` authoring property was found in installed WObjects/project XML. Licence-derived numeric identity is a **hypothesis**, not a verified licence-to-ID mapping.

Installed T/Data/Schemas/WAAPI/ak.soundengine.loadBank.json exposes a bank name/GUID/ShortID, not an independent arbitrary-file native-Init harness. Authoring playback with dynamically supplied project objects would not certify the original Init/regional pair. No extra SDK/tool was installed to invent such a test, and no opaque BKHD/HIRC splicing was attempted.

## 5. Packaging gate and least-cost next step

**Not cooked:** the acceptance gate in report14/AGENTS requires a compatible bank first. A native cooker cache readback would preserve the current questionable bank bytes; it would not resolve project identity or turn exit1 into successful generation. The already-proven regional-only cooker control from report13 remains applicable once this gate passes; no full depot or additional bank generation is indicated by the measured local-State dependencies.

The narrow intended future footprint is **one mod soundspc.cache entry, music_prologue.bnk**, retaining the installed game's original Init and streamed media. No loose/bootstrap Init, no Init cache entry, no source WAV, no other regional bank or script is justified by this experiment. This is a proposed footprint, **not a produced package**. Audio mods replacing music_prologue require a combined bank build; automatic cache merging is not claimed.

**Exact next blocker resolution:** first seek supported confirmation of native-Init compatibility for the generated projectID0 regional bank versus native39, using this paired evidence. If official guidance or an existing independent bank-loading harness establishes it, the regional-only approach can advance without replacing Init; neither has been demonstrated here. The documented generation remedy is the official Witcher 3 REDkit modding entitlement for 2023.1.19/Windows and HomeCinema/Mastering Suite, followed by comparable complete-context controls without leaf exclusion. Confirm generated numeric project identity compatibility before approving packaging. The [official REDkit Wwise guide](https://www.audiokinetic.com/en/blog/the-witcher-3-redkit-tutorial/) describes requesting **Witcher 3 - REDKit Modding** access for project assets/plug-ins. Report12 documents the free-request route; a paid commercial licence has not been shown necessary. No request, account access, activation or purchase was performed here.

If that entitlement still emits projectID0 or licence errors, provide these paired commands/logs and header values to Audiokinetic/CDPR. Request native-compatible bank-generation guidance rather than altering the game's Init. If successful generation still changes unrelated regional HIRC/media, investigate those differences before cooking. There is no evidence that generating all eight regional banks would fix either current blocker.

## Reproduction and preservation

Use fresh complete workspace paths and the tracked clean helper after the exact matching localhost WAAPI server reports ready. Stop that task-owned server before offline exclusion or generation. First generate the unexcluded pair; if the media gate fails, prepare another full pair, apply `--exclude-file-leaves` equally, and author only its candidate. Commands and exact isolated options are preserved in P's command.json files. The read-only audit can be repeated with:

```powershell
python tools/white_orchard_state_bank_audit.py `
  --native 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc' `
  --baseline build/white-orchard-full-context-stage1/leaf-baseline-banks `
  --candidate build/white-orchard-full-context-stage1/leaf-candidate-banks `
  --baseline-project build/white-orchard-full-context-stage1/leaf-baseline `
  --candidate-project build/white-orchard-full-context-stage1/leaf-candidate `
  --output build/white-orchard-full-context-stage1/state-bank-audit.json
```

P/final-input-verification.json rehashes **1,556 installed authoring inputs**, finding zero changes, and confirms R's two native bank hashes plus the game's loose Init. No installed resource, save, reference mod or depot was written. All prior recordings/audits remain; failed controls and initial overly strict audit results are retained. Generated Init files remain quarantined evidence inside P.

One initial leaf authoring call was made before its WAAPI server reported ready and failed with ConnectionRefused before mutation; the ready-server retry produced the retained audit. Python compilation of the changed helpers and `git diff --check` pass. Task-owned WwiseConsole servers were stopped after saving, before offline generation; none remains running at completion.
