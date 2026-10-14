# Native two-bank cache proof — 2026-10-14

**Observed:** native REDkit `cooksounds` and `splitcache sounds` both exit0 and produce one cache with exactly the retained White Orchard D and NML pilot banks. Neither bank was regenerated or changed. No Init, WEMs or source audio appear in the bundle. This establishes native cache composition and readback, **not retail loading or automatic coexistence of separate mod caches**.

| Entry | Offset / bytes | Exact bank SHA-256 |
|---|---:|---|
| `music_nomansgrad.bnk` |64 /1,273,141|`a90e7a986ce2ef40831bb6d2738a5ce21113a62e73cf19d1a2f545f4a4b3396d`|
| `music_prologue.bnk` |1,273,205 /174,953|`925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`|

`regional_music_cache.verify_bytes` verifies CS3Wv2, exactly two named entries, valid index/name/payload bounds, no overlap, duplicates or missing entries, and exact input bytes. Native split repeats the check. There are zero shared HIRC IDs between these two banks; no conflicting shared serialized objects were found. Native bootstrap Init remains the original, with no generated Init in the cook input.

Cooked cache SHA `b0292e9704d734b47228f0158c6d58339b22d16019ce31054385d6ec096a8769`; native split cache SHA `7d4d144fd4deeb0b0179a85f555afb03ea79971020388cabbd740db4b38ee7b4`. Different whole-cache headers do not imply different regional payloads; no header was patched.

Consolidated offline ZIP:

`C:\Dev\witcher-music-control\build\consolidated-expansion\two-bank-pilot-v1\archives\WMC Consolidated - White Orchard D and NML Pilot v1.zip`

SHA-256 **`d5797bcbf5bebcf4ddeafe45f16e11ff0796e8d53b53879bafe836bced06641f`**. Exactly one ZIP entry: `Mods/modWMCConsolidated/content/soundspc.cache`; ZIP readback matches the cooked cache. It retains pilot coverage, not the later expanded NML policy.

## Reproducible procedure and diagnostics

`tools/regional_music_bundle.py::{verified_inputs,native,reviewed_diagnostics,stage}` consumes explicit regional paths/hashes and independent full source/decoded/media/global proof files. Unsupported names, changed hashes, duplicate/missing expected banks, failed native commands, unreviewed diagnostics or bad cache/ZIP readback fail. Future regions can be added to an explicit `regions` list only with their own passing proofs; the current spec contains two regions.

Native bootstrap and all evidence are in ignored `build/consolidated-expansion/two-bank-pilot-v1`. `bundle-cook-confirmed-result.json` and `bundle-split-result.json` retain exact commands/status; `bundle-verification.json`, `composition-diagnostics.json` and `reviewed-native-diagnostics.json` retain independent results. The input spec remains `build/consolidated-expansion/bundle-pilot-v1.json`.

The initial native cook completed but a PowerShell process-handle recording pattern returned a **null exit code**. It was rejected rather than interpreted as success. A fresh-output repeat uses the already established `Start-Process -Wait -PassThru` pattern, retains the earlier output and captures exit0. No native data was repaired/spliced.

Native diagnostics are **not error-free**: cook has29 rows versus the accepted NML single-bank26; split has the same23 startup diagnostic rows. All three additional cook rows are the expected second-bank missing split-CSV mapping, missing `.txt` file and description-load message. After replacing only timestamps, isolated roots/input names and private Documents prefixes, all inherited messages match the accepted cooker reference exactly. Both actual bank entries are nevertheless written to content0 and verified. Unchanged native media remains external, as in each accepted individual package.

Rollback: retain the individual D and NML archives and banks unchanged. No Vortex action was taken. Eventual replacement of the individual mod folders by this consolidated folder requires separate deployment authorization; do not leave multiple active variants for the same banks or assume audio mods merge. User feedback will arrive during natural play, per report38. No custom saves, forced progression or region visits are required for further offline engineering.
