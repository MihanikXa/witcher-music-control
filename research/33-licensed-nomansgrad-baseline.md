# Licensed NML baseline — 2026-10-13

After the user confirmed manual application, the **existing untouched isolated NML baseline** generated successfully with warnings. This resolves report32's project-local baseline licence blocker. No key/project licence property was read, copied or transferred; effectiveness was established solely through generation diagnostics. The modified candidate was not generated, packaged or deployed.

## Reproduction and retained evidence

Project: `C:\Dev\witcher-music-control\build\regional-system\nomansgrad\baseline\w3_audio.wproj`. Original project/source remains the installed REDkit `assets\w3_audio`. The wrapper command was:

```powershell
python tools/white_orchard_wwise.py --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' --project build/regional-system/nomansgrad/baseline/w3_audio.wproj --bank music_nomansgrad --output build/regional-system/nomansgrad/baseline-banks-licensed
```

This selected only NML, Windows/SFX, complete context, no source exclusions, fresh ignored output and isolated cache/metadata. Previous failed `baseline-banks` remains preserved. Disposable Init was incidentally generated; it must never be packaged.

Evidence under `C:\Dev\witcher-music-control\build\regional-system\nomansgrad`:

- `baseline-prelicensed-recheck.json`: pre-build original source fingerprints, complete 1,508 units and 434 regional originals pass.
- `baseline-banks-licensed/{command.json,result.json,generation.log,SoundbanksInfo.xml}`: actual command, diagnostics, metadata and binaries.
- `licensed-baseline-native-comparison.json`: reused `white_orchard_compare::{read_bank,difference}`, `white_orchard_state_bank_audit::{header,native_groups}` and `white_orchard_build_gate::plugins`.
- `licensed-baseline-media-source-recheck.json`: post-build full source rehash passes; initial loose-media lookup incorrectly searched the bank directory itself.
- `licensed-baseline-streamed-media-corrected.json`: corrected loose lookup under native `Pc\Media` finds only three of the 423 streams; those three match. Absence of other loose files is not a media mismatch.
- `licensed-baseline-native-cache-media.json`: bounded read-only CS3W index/payload reads from installed `content\content0\soundspc.cache` resolve **all 423** streams and match every generated payload hash. No extraction/deployment was performed.
- `licensed-baseline-warning-review.json`: explicit review versus retained licensed White Orchard baseline diagnostics.

A metadata-preview attempt used a nonexistent older-schema `ReferencedStreamedFiles` node and failed after successfully writing the bank comparison. Correct current metadata uses `SoundBank/Media/File` (`Id`, `Streaming`, `Location`, `Path`, `CachePath`). The subsequent media checks use that actual structure. Failed lookups/previews are preserved and do not substitute for completed checks.

## Build and bank results

**Observed:** Console v2023.1.19, build8928; exit **2**; exactly `Init.bnk` and `music_nomansgrad.bnk`; **19 warnings, zero errors/fatals**. Previous trial 26,218/200 limit and six Mastering Suite errors are absent. The wrapper accepts exit2 as evidence production, not as automatic candidate approval.

| Resource | Bytes / SHA-256 |
|---|---|
| Native NML bank | 1,273,131 / `09c570e4117c70e601c80757fb1df42debf8ce1f078b9a8ca26ce0935092b251` |
| Generated untouched NML | 1,273,131 / `fff351727251213bf07ecd96639d916f13e483a0d3a8efbe76ee9646ab60cfb6` |
| Disposable generated Init | 29,692 / `ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01` |
| Generation log | `f397104c992dd06d242bd3e4f18113507a7c1b37314e61c0b3ffb5366fde2341` |
| Installed original Init | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |

Regional **all 3,831 HIRC records and embedded DIDX/DATA are native-exact**; no record added, removed or changed; only BKHD differs. Header v150, bank4179090583, language393239870, alignment16, bank type0 and padding remain native. Project ID is17637 versus native39; generated hash bytes correspond exactly to generated metadata GUID `{BF9FBE05-D34E-C9C3-3895-F1CD1E117AC8}`. No header was patched. Installed cache's NML payload also matches the native bank hash. Existing White Orchard runtime success informs this identity difference but does not certify NML loading in game.

Native source/selection/media relationships are preserved by byte-exact HIRC, unchanged source and **423/423** streamed payload equality. Every recorded original WWU and regional audio input in installed REDkit and isolated baseline still matches before/after generation. No fresh global definitions were authored.

Disposable Init has the already observed ten missing native HIRC objects and three missing StateGroups (967256167,1975690400,3317025587); surviving HIRC and existing StateGroup transitions match native. All18 INIT plugin registrations match exactly. These historical Init omissions are recorded, not repaired or accepted for deployment. Original native Init remains the production design.

## Explicit warnings review and remaining gates

Nine `MediaMultipleUsage` streaming/memory consistency warnings are inherited from original full-project definitions; nine `MediaDuplicated` warnings concern existing shared music. Fifteen warning messages match the retained White Orchard licensed baseline exactly. Four additional duplication messages concern the two EP1 credits pieces shared with `music_main_menu_credits`, cs210 Ciri lab and cs203 Udalryk shared with `music_skellige`. Exact native HIRC and all stream hashes corroborate unchanged configuration/content; these are reviewed **untouched-baseline** warnings, not automatically approved future candidate differences. The remaining warning concerns Wwise.dat consistency output; the wrapper uses `--no-wwise-dat`, as in earlier builds, and the bank/metadata artifacts exist. Full log retained; no warning hidden. Old strict exit0/native-Init-equivalence gates were not altered or bypassed.

59 existing unit tests pass again. No source/test logic changed in this follow-up. The new-bank fail-closed preflight still requires a measured regional record decoder; this baseline is now a trustworthy comparison input, **not a deployable NML candidate**. Also outstanding: explicit-threat-zero paired control and zone03 playback from reports31–32. Candidate project's licence effectiveness has not been tested and must not be inferred or copied from baseline.

Smallest next implementation: implement a bounds-checked v150 regional State/Voice Volume decoder against this preserved native-exact baseline and existing source identities, with synthetic malformed/negative cases; complete the two playback controls before candidate approval. Then test candidate project-local licensing through its own authorized generation workflow, stopping for manual application if necessary. No broad Init investigation, D regeneration, unrelated bank generation or live-game change is needed.
