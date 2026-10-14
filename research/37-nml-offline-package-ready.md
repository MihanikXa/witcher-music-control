# NML regional pilot package ready — 2026-10-14

## Outcome and authorization

The user authorized settings backup and an isolated cooker relaunch for manual EULA review. **Thirteen relevant settings/config files were copied and hash-verified into ignored private build output. No saves were copied.** All thirteen remained byte-identical after the cooker operations. The backup includes game/editor settings; this is not a claim that all registry or other application state was audited. Private paths/profile files are not committed.

The previously observed EULA modal did not remain pending on relaunch. No acceptance control was clicked or acceptance flag edited by Codex. The relaunch completed and emitted a cache; its process exit code was not retained, so that first output was used only as payload evidence. A fresh confirmed cook and native split were then run with `Start-Process -WindowStyle Normal -Wait -PassThru`, capturing **exit0 for both**. This differs from the earlier noninteractive Python launches which stalled. The reason for the changed EULA behavior is **unresolved**; do not infer automatic acceptance, a missing commercial entitlement or a bank compatibility defect from it.

The confirmed cook, native split readback and archive verification now pass. **No game launch, Vortex installation/deployment, save edit or native Init replacement occurred.** The candidate has offline verification; NML retail-game compatibility remains untested.

Final preservation checks rehash all455 installed bootstrap inputs without changes. Native game Init remains `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`; retained White Orchard D ZIP remains `20bdfbd966aa07aa913c0ecb4694badf581082cf972a7504ef1a344ee56b3679`. `final-preservation-check.json` records these independent checks.

## Package and exact payload

Archive:

`C:\Dev\witcher-music-control\build\regional-static-outro\cooker-licensed\archives\WMC Velen Novigrad — Zone 02-03 Combat Outro Test.zip`

| Artifact | Size / SHA-256 |
|---|---|
| Vortex ZIP |677,022 bytes; `44b3188e54eea49cdec30ad479c7d77e3c58a6a639f59df63918004a7919392f`|
| Packaged cooked cache |1,273,250 bytes; `73ceb20769da30685a0e2e986aa4044c619ba4ebc112c4bb64334cdf41cef932`|
| Native split/readback cache |1,273,250 bytes; `d2f33e267dcd802384d1fd6ac0e0f22ad28d2d5b9490f775e17f1a8b915d078c`|
| Exact regional bank payload |1,273,141 bytes; `a90e7a986ce2ef40831bb6d2738a5ce21113a62e73cf19d1a2f545f4a4b3396d`|

ZIP has precisely one file:

```text
Mods/modWMCNomansgradPilot/content/soundspc.cache
```

No extra nesting, generated Init, WEMs, source audio, project/licence material or settings backups are included. ZIP readback matches the packaged cache; both native caches index exactly `music_nomansgrad.bnk` at offset64 and contain the exact verified bank bytes. Whole-cache hashes differ because the native splitter changed only bytes28/29: the header uint32 at28 changes0→445. Its semantic meaning remains uninterpreted; neither bank nor cache header was manually patched. Entry name, payload, index and all other cache bytes match. The ZIP uses the original cooked cache, consistent with the retained White Orchard packaging workflow.

## Gates and native diagnostics

Report36's complete source/decoded bank proof is retained, SHA-256 `956fa9760f142a2f8e6a5b512bec4a6279c0ddb031793e35a706389f8ee6a1aa`. The source remains `ebd3d6ae95680307a6a965c07b096a02e659ccb5703981e4a27566e67d416f4f`; unchanged manifest `ad491c8c2331b163e5683cdba8fd028a924f689f5f746d328c7e028ba8a09d22`. Selected Wwise generation remains **exit2 with19 baseline-identical warnings**, zero errors. No bank regeneration was needed for packaging.

`tools/regional_music_package.py::{require_proofs,validate_native_result,stage}` requires the independent complete source, four decoded HIRC records/parents, unchanged423 media/reference payloads, unchanged globals, exact generation warnings, native Init provenance and report35's complete-outro playback evidence. New completed-command mode accepts both recorded native commands/results and outputs only when all arguments match the expected isolated cook/split paths and both commands exit0. Incomplete evidence, failed status, wrong root/output or stale bank/source hashes fail. Exact CS3W payload, native split and ZIP readback checks remain mandatory. The original normal-cook workflow remains available.

Native cooker logs are **not error-free** despite exit0. Confirmed cook has26 diagnostic rows, split23. They include minimal-bootstrap missing legacy configs/language/sqlite data and script assertions. Cook also logs `[Error][SoundModCooker] Can't load description file ... music_nomansgrad.txt` and missing split-CSV mapping, followed by explicit addition of the bank to content0. These are the same diagnostics as the retained D cooker, after replacing only timestamps, isolated roots/input-folder names, private Documents prefix and regional bank name. `native-diagnostics-review.json` records exact normalized multiset equality, with no added/missing rows. Missing descriptions explain why the summary's `banks processed` counter is0 while its actual cache contains one bank; no media descriptions/WEMs were provided. This bank-only packaging relies on existing native streams, whose423 payloads were independently preserved against the licensed/native baseline in reports33/36. Retail resolution still needs the game test.

**110 tests pass** with `python -m unittest discover -s tools -p 'test_*.py'`, including new completed-command positive/negative checks. Tests, source validation, Wwise playback, binary checks and native cache serialization remain distinct evidence layers.

## Retained local evidence and reproduction

Under `C:\Dev\witcher-music-control\build\regional-static-outro\cooker-licensed`:

- `regional-cook-confirmed-{result.json,stderr.log}` and `regional-cook-confirmed.log`: exact command/status and diagnostics.
- `regional-cooked-confirmed/{audio-split.list,CookedPC/soundspc.cache}`.
- `regional-split-confirmed-{result.json,stderr.log}` and `regional-split-confirmed.log`; `regional-split-confirmed/content0/soundspc.cache`.
- `regional-package-verified.json`, `native-diagnostics-review.json`, `post-manual-settings-check.json`, and `package/Mods/modWMCNomansgradPilot/content/soundspc.cache`.
- Prior45s timeout,180s retry/termination and first manual output remain preserved; they were not accepted as successful command-status proof.

Private backups/session manifest remain in ignored build output; they must never be committed or distributed. Restore a backed-up settings file only if necessary and separately authorized; currently no restoration is needed because all thirteen hashes match.

The verified completed outputs can be passed through the shared packaging CLI with the usual baseline/candidate/project/manifest/proof/playback/root arguments plus `--completed-cook-output`, `--completed-cook-result`, `--completed-split-output`, `--completed-split-result`. Use the corresponding paths above. Archive creation fails if it already exists; preserve this accepted archive rather than rerunning into it. A future fresh cook uses the same native arguments/isolated bootstrap and keeps generated Init out of the input bank directory.

## Smallest next step: separately authorized Vortex gameplay test

Do **not** deploy as part of this completed preparation. Next obtain explicit authorization for an isolated Vortex **off→pilot→off** test using the same copied save, route, settings and fresh game process each time. Preserve the current working White Orchard D and primary profile. The new mod folder differs from D's folder and its cache indexes a different regional bank; nevertheless other mods replacing `music_nomansgrad.bnk` require conflict review before deployment. Do not claim automatic audio-cache merging.

Test only a route established to select `mus_loc_nml_zone_02` or `mus_loc_nml_zone_03`. The archive is **not full Velen/Novigrad suppression**: only four approved day/night generic playlists change; forty mixed/unresolved decisions remain native. A reliable retail geographic route for these selector IDs has not been established by these authoring tests; confirm it in the test preparation rather than guessing from playlist names.

Listen for generic exploration/dialogue suppression, combat entry at different phases, threat/intensity response and a **complete audible combat outro after exploration returns**, with no generic overlap burst. Check available authored cues and Music-slider behavior. Restored control must bring the same generic cue back, allowing for native soundtrack gaps. Wwise evidence already supports these musical mechanisms, but a successful NML game test is required before claiming regional runtime compatibility.
