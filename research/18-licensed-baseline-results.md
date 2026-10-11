# Licensed unmodified White Orchard baseline — 2026-10-11

## Decision

**Effective build coverage is demonstrated, but native compatibility is not certified.** The complete untouched baseline emits `Init.bnk` and `music_prologue.bnk` with exit **2**, 15 warnings, zero errors/fatals, and no trial-media or Mastering Suite licence errors. The strict baseline validator exits **1**. Its failures are generation acceptance, Init fidelity, regional fidelity and complete STMG equivalence. No candidate, cooker package, deployment, licence transfer, binary patch or save modification was performed.

The important new difference is **generated BKHD Project ID 17637 versus native 39**, replacing the earlier trial output's 0. The regional bank otherwise preserves every native HIRC record and embedded media chunk. Generated Init now includes native HomeCinema and all 18 plugin registrations, but still lacks ten native HIRC objects and some global data. Licence approval/application alone does not solve native identity or source provenance.

## Reproduction and evidence

Exact paths below are explicitly machine-local evidence; generated/licensed assets remain ignored and are not committed.

| Alias | Absolute path |
|---|---|
| P | `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline` |
| B | `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline-banks` |
| V | `C:\Dev\witcher-music-control\build\licensed-white-orchard-verification` |
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| R | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc` |
| G | `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\initialdata\sound\Init.bnk` |
| Console | `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe` |

The previously prepared P exists, so it was reused without copying its project/licence. `tools/white_orchard_build_gate.py:source_control` passes before and after generation: **1,508 original WWU paths/hashes**, schema119, v2023.1.19/build8928, 47 unchanged copied originals, no inclusion experiment. All **1,556 recorded W inputs** were rehashed before and after: zero changes. V/post-build-source-and-diagnostics.json records the final check. Validator inputs also remain unchanged. No licence property, credential or key was inspected, extracted or transferred; effective coverage was tested only through generation results.

Generation command (B was absent before execution):

```powershell
python tools/white_orchard_wwise.py `
  --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' `
  --project build/licensed-white-orchard/baseline/w3_audio.wproj `
  --output build/licensed-white-orchard/baseline-banks
```

`tools/white_orchard_wwise.py:generate` selects only `music_prologue`, Windows/SFX, isolated cache/output/metadata, no source control/decode/Wwise.dat writes and empty custom commands. B/command.json preserves exact arguments; B/result.json preserves actual Console exit **2** (the wrapper itself accepts 2). B/generation.log SHA256 is `dc3867ea2044967b9f5f22afa1c7f38a99a36f29343559ee8838053e213975cf`. No leaf exclusion or hierarchy pruning was used.

The report17 baseline command was run unchanged with P/B/R/G and output V/baseline.json. That strict validator rejects exit2/warnings rather than silently accepting them. Its detailed comparisons are preserved. The 14 synthetic verification-tool unit tests pass; their intentionally failed fixture reports are expected tests, not build evidence.

## Generation diagnostics

**Observed:** B/generation.log, `SoundBankGeneration` diagnostics:

| Diagnostic | Count | Assessment |
|---|---:|---|
| Trial 26,218/200 / media-limit fatal | 0 | Previous blocker resolved for this complete selected-bank build; no sources excluded. |
| HomeCinema / Mastering Suite licence error | 0 | Previous six errors resolved; native HomeCinema record4131355637 now exists unchanged. |
| Other errors / fatal errors | 0 / 0 | No further manual licence application is indicated by this build. This is not a general entitlement/expiry audit. |
| MediaMultipleUsage | 9 | Inconsistent streaming/memory configuration for q703 torture scene, q106 ectoplasma and Dettlaff swarm source instances. Full-project diagnostics outside the selected region; regional record/media equality shows no resulting difference in this baseline bank. |
| MediaDuplicated | 5 | q301 opening and four dialogue ambient media shared across music banks. Sharing does not itself establish corruption; emitted regional embedded media remains native-exact. |
| Uncategorized Wwise.dat consistency warning | 1 | Log reports consistency files could not be written. Command explicitly requests `--no-wwise-dat`; cache permission failure is not established from the warning alone. No permission change was attempted. |

**Supported inference:** the licence is effective for the requested isolated build, including the previous media/plugin barriers. Exit2 plus warnings is a more permissive result than the strict gate accepts; it is not evidence of an error-free build. A future explicit warning policy could distinguish these known diagnostics from errors, but no gate was changed or bypassed here.

## Bank comparisons

Evidence: V/baseline.json, `baseline.banks`, `plugin_registration_differences`, `stmg`; parsers `tools/white_orchard_compare.py:read_bank/difference` and `tools/white_orchard_state_bank_audit.py:header/native_groups`.

| Check | Observed result |
|---|---|
| Regional size / HIRC | 174,826 bytes; 490 records; no added, removed or changed HIRC IDs/bodies. Entire 60,274-byte HIRC chunk matches native, including events, world and authored quest routing. |
| Regional embedded media | DIDX84 / DATA114,384 bytes, both native-exact. Existing media/stream reference fields in HIRC unchanged. This does not independently compare every streamed WEM with the installed cache. |
| Regional differences | Only BKHD differs. Generated SHA256 `5b28f4ee5f286ec46a80120ea632c1d2ca715c0e2b05fb90ddd411f16e9a953a`; native `75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912`. |
| BKHD identity, both banks | v150, native bank IDs, SFX language393239870, alignment16, type0 and padding match. **Only compared identity field difference: Project ID17637 versus39.** |
| BKHD hash | Generated 16-byte hashes match the respective B/SoundbanksInfo.xml `SoundBank/Hash` GUIDs in GUID byte order. Native hashes differ. Hash differences alone are already separated from identity failure by the validator. |
| Init | Native32,840 bytes/151 HIRC records; generated29,692 bytes/141 records. Ten removed, none added, no surviving body changed. Generated SHA256 `ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01`. |
| Plugin registrations | All18 native INIT IDs/names match, including MasteringSuite12189699 and AkMotion26804226; entire INIT277-byte chunk matches. |
| Audio devices / HomeCinema | No type21 AudioDevice removed or changed; HomeCinema4131355637/type16 now preserved. |
| Other Init chunks | ENVS168 and PLAT8 match; differences limited to BKHD, HIRC and STMG. |
| Native Init provenance | R/Init matches G, SHA256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`; never replaced. |

Removed native Init HIRC objects:

| ID | Type, cross-checked in report12's retained type audit |
|---:|---|
| 542827472 | 8 Bus |
| 890724639 | 17 Effect |
| 1411735597 | 8 Bus |
| 1505802601 | 8 Bus |
| 2041642433 | 8 Bus |
| 2320575434 | 8 Bus |
| 3803860308 | 8 Bus |
| 4004099879 | 8 Bus |
| 4189995869 | 18 AuxBus |
| 4253138028 | 8 Bus |

These are the prior unexplained ten omissions, now separated from the resolved HomeCinema licence omission. No reliable source names/dependency explanation was established; do not attribute them all to licensing or selected-bank stripping. Report12's retained `C:\Dev\witcher-music-control\build\white-orchard-followup\native-hirc-type-crosscheck.json` supports the type mapping.

STMG is **native3,178 versus generated2,785 bytes**, with differing SHA256s recorded in V. Decoded headers match (threshold−96.300003, max voices256, virtual50). Native has six StateGroups; generated retains three. Missing groups are **967256167, 1975690400, 3317025587**, each native default transition1000ms and no custom transitions. Existing `game_state`766723505—including default1000ms and all43 custom transitions—matches exactly. Groups2438777053 and2861987792 remain. The undecoded STMG tail is not certified equivalent; the size difference cannot safely be attributed solely to the three missing groups.

## Dependency problem versus conservative equivalence

**Observed:** the strict gates failed exactly `baseline.generation_success`, `baseline.init_native_fidelity`, `baseline.regional_native_fidelity`, `baseline.complete_stmg_exact`. Source, native reference provenance, native IDs, plugin registrations and read-only checks pass. An unmodified baseline adds no local State Voice Volume, so this run does not test its future serialization.

**Supported inference:** the Init differences are real global-definition differences, not merely a byte-order/hash complaint. This Init is unsuitable as an unexplained vanilla replacement. However, Stage1 intends to retain native Init; requiring a disposable Init to reproduce every native object may be stronger than that regional-only design needs. The native-exact regional graph establishes that this unmodified bank introduces no new serialized HIRC/media dependencies. It does not prove a future edited bank loads, or that generated/native project identities can coexist.

**Unresolved hypothesis:** Project ID17637 may reflect the approved modding entitlement while39 reflects the shipped game's project. The change from trial0 is correlated with licence application; no licence internals were inspected and no mapping was proven. The [official SDK bank overview](https://www.audiokinetic.com/library/edge/?id=soundengine_banks_general.html&source=SDK) requires Init/content banks from the same project, but does not establish this Remastered runtime's treatment of these numeric header IDs or modding entitlements. Neither rejection nor permissive loading has been measured. This is a genuine unresolved compatibility condition, not an established runtime failure or a justified gate waiver.

**Recommended next action:** obtain Audiokinetic/CDPR guidance on generating/loading REDkit-modding-licensed banks (ProjectID17637) alongside shipped native Init(ProjectID39), and whether selected generation/source provenance explains the ten Init omissions and STMG differences. Supply sanitized IDs/hashes and commands, not keys or licensed project files. Do not request another licence or generate the candidate yet. A supported native-Init bank-load compatibility test or documented runtime policy would falsify the identity blocker; an error specifically rejecting differing project IDs would confirm it. If supported compatibility is established, review the disposable-Init and known-warning requirements explicitly before revising the acceptance policy. No opaque header rewriting is justified.

Installed resources, original source hierarchy, prior experimental evidence and saves remain unchanged. Stage1 candidate generation is **not cleared** by this run.
