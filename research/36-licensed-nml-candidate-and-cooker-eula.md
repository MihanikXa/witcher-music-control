# Licensed NML candidate verified; cooker EULA stop — 2026-10-14

## Verified build result

After the user confirmed manual licence application, selected `music_nomansgrad` generation succeeds with warnings in the existing complete isolated candidate. **Exit2, nineteen warnings, zero errors**, exactly two bank outputs (`music_nomansgrad.bnk`, disposable `Init.bnk`). All warning rows and counts are identical to the retained licensed baseline from report33. The former trial-media fatal error and six Mastering Suite errors are resolved. No licence key or project licensing property was read/copied; no baseline or unrelated bank was regenerated.

Matching Wwise is2023.1.19.8928, Windows/SFX. Reproducible command:

```powershell
python tools/white_orchard_wwise.py --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' --project build/regional-system/nomansgrad/candidate/w3_audio.wproj --bank music_nomansgrad --output build/regional-static-outro/candidate-banks-licensed
```

The complete context remains1,508 work units with434 original regional source files. Production changes remain the four static playlist Volume values from report35, with **no shared location State gain**. Its measured combat/outro, authored-fixture and suppression evidence is reused, not rerun or replaced here.

## Independent source and bank gates

`tools/regional_music_gate.py::{source_gate,decoded_preflight,bank_preflight}` passes against the **completed** generation output and the original native bank. An earlier source-check invocation began before generation completed; that process was stopped, and its result was not accepted. The final independent report is `C:\Dev\witcher-music-control\build\regional-static-outro\licensed-candidate-final-full-gate.json`.

- Original source inputs, all1,507 unrelated units and all434 originals remain exact; complete music semantics differ only at the four approved Volume properties. Forty mixed/unresolved decisions remain native: this is partial zone02/03 coverage.
- All3,831 HIRC objects remain. Exactly four type13 records change; no additions/removals. Static Volume insertion for719937819/946096996 adds five bytes each; replacing existing −2 dB Volume in132074504/568231384 leaves record lengths unchanged. The bank is ten bytes larger than the licensed baseline.
- `regional_music_bank.py::validate_record` derives layouts rather than reusing White Orchard offsets. Parents remain193134718 (zone02) and432285193 (zone03). State offsets move28→33 only with inserted Volume; existing33 offsets remain33. All original State bytes, other properties, selectors, transitions, RTPCs and serialized remainders are exact. No new State definitions are required.
- Embedded DIDX/DATA is exact; all423 generated media payloads, streaming/reference metadata and paths match the retained baseline. Report33 independently matched that baseline's streams to the installed native cache.
- Disposable generated Init is **byte-identical to the licensed baseline**, SHA-256 `ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01`. Thus generated HIRC, INIT plugin registrations, STMG/transitions and other global chunks gain no new dependencies. Historical native/generated Init omissions are not deployed and were not reinvestigated.
- BKHD remains v150, bank4179090583, language393239870, alignment16, Project ID17637 and bank type0. Only the expected metadata hash changes against the licensed baseline; `{F7D236E2-DC24-7047-B82A-E7E0EAB4E999}` matches the generated header. Original native Project ID39 is retained in native Init. This does **not** establish retail NML loading compatibility from the earlier White Orchard result.

| Artifact | Size / SHA-256 |
|---|---|
| Modified regional bank |1,273,141 bytes; `a90e7a986ce2ef40831bb6d2738a5ce21113a62e73cf19d1a2f545f4a4b3396d`|
| Retained licensed regional baseline |`fff351727251213bf07ecd96639d916f13e483a0d3a8efbe76ee9646ab60cfb6`|
| Clean modified music source |`ebd3d6ae95680307a6a965c07b096a02e659ccb5703981e4a27566e67d416f4f`|
| NML manifest |`ad491c8c2331b163e5683cdba8fd028a924f689f5f746d328c7e028ba8a09d22`|
| Native game Init, rechecked |`2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`|

## Packaging implementation and actual blocker

`tools/regional_music_package.py` reuses the native REDkit bootstrap/cooker and strict `regional_music_cache.verify_bytes`. Its acceptance is bounded to the measured four-target NML pilot. It requires matching full source/decoded/media/global hashes, all four decoded parents/identities,423 paired media files, exact baseline warnings, native Init provenance and all eight NML native/modified complete-outro checks. Unknown targets, missing/stale proof or the old State scopes fail. Successful cook/split must preserve exact regional payload bytes and the ZIP must contain precisely `Mods/modWMCNomansgradPilot/content/soundspc.cache`. No generated Init/WEM/source/licence material may enter it.

**107 unit tests pass** (`python -m unittest discover -s tools -p 'test_*.py'`), including nine new positive/negative package prerequisite tests. This tests gates, not a successful native cook.

Actual bootstrap: `C:\Dev\witcher-music-control\build\regional-static-outro\cooker-licensed`. Its455 read-only installed inputs and isolated native Init copies follow the already demonstrated workflow; the known unavailable startup dog bank is omitted from the isolated startup list. Only the verified regional bank is in `regional-input`.

First native `cooksounds` attempt hit the established45-second timeout, with an empty log and no cache. A single fresh-output retry used180 seconds, preserving the first result. Inspection of the **owned** `wcc_lite` process found its window title **EULA** (retained `eula-blocker.json`). The retry was explicitly terminated to avoid accepting terms or leaving an unattended dialog. Its recorded exit4294967295 is a termination result, not a bank-parser error; `timeout:false`. The actual EULA text and acceptance persistence/profile effects were not inspected. No acceptance or profile setting was written by our code.

This is an observed modal startup blocker, not evidence of incompatible HIRC or a requirement to regenerate banks/depot. No cooked cache, split readback or Vortex ZIP exists. Native-cooker success and retail loading remain separate outstanding gates. The longer optional timeout in `white_orchard_cooker.execute` preserves its45-second default and records the chosen bound; it is not an EULA bypass.

Evidence under `build\regional-static-outro` includes `licensed-diagnostics-review.json`, `licensed-build-summary.json`, final full gate, `candidate-banks-licensed/{command,result,generation.log,SoundbanksInfo.xml}`, and `cooker-licensed/{bootstrap-manifest,regional-cook-result,regional-cook-retry-result,eula-blocker}.json`. Earlier failed licence output, playback captures, retained baseline and working White Orchard A/C/D remain untouched. No game launch, Vortex deployment, save edit or binary/header patch occurred.

## Smallest next step

**Obtain authorization for a controlled manual review of the isolated cooker's EULA**, preserving relevant user settings before any acceptance. Do not accept it automatically, change EULA flags, or launch the installed editor against the original project/depot. The pending window was closed; it will need a deliberate isolated cooker relaunch for the user to review. Determine the actual settings affected before changing them; the title alone does not identify the terms or their persistence mechanism.

After that manual prerequisite is resolved, package the **existing verified bank** with a fresh cooker evidence root, for example `build/regional-static-outro/cooker-after-eula`, through `regional_music_package.py` using the retained final full-gate/playback-review files. Do not reuse/overwrite failed cook outputs. No Wwise rebuild is needed. Then verify native split/readback and archive identity and request separate authorization for a controlled NML gameplay test. Keep White Orchard D unchanged and distinguish zone02/03 pilot coverage from the unresolved remainder of Velen/Novigrad.
