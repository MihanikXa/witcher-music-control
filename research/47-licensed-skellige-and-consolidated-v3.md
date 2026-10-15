# Licensed Skellige and consolidated v3 — 2026-10-15

**Result:** licensed Skellige candidate generation, full source/decoded/media/global gates, native three-bank cooking/split readback and Vortex ZIP validation all pass. V3 contains the **exact retained White Orchard D and expanded NML v2 banks**, plus the verified Skellige candidate. No game launch, Vortex deployment, save/profile change or Init replacement. Skellige/v3 retail behavior remains unconfirmed; reports38/43 authorize continued offline development and natural-play feedback.

## Licensed candidate

The user confirmed manual application to `C:\Dev\witcher-music-control\build\skellige-v3\candidate\w3_audio.wproj`. No key/licence field was accessed or transferred. Only selected `music_skellige`, Windows/SFX, was generated with matching Wwise2023.1.19.8928. `build/skellige-v3/candidate-banks-licensed/{command.json,generation.log,result.json}` records **exit2**, exactly regional bank plus disposable Init, **16 baseline-identical warnings and zero errors/fatals**. Old failed `candidate-banks` is retained. No baseline, D or NML bank was regenerated.

`licensed-candidate-diagnostic-review.json` uses `white_orchard_candidate_package.diagnostics` to compare exact Counters with Skellige's own accepted baseline. Trial-media/Mastering Suite failures are resolved. Exit2 warnings remain visible, not described as exit0 or error-free output.

`licensed-candidate-full-gate.json`, using `regional_music_gate::{source_gate,decoded_preflight,bank_preflight}` and `regional_music_bank.record_gate`, verifies:

- Complete1,508-WWU context; all1,507 unrelated work units, original253 audio inputs and installed source hashes unchanged; all542 event units reviewed. Source music remains SHA `414dd1193433d6aaadb0fa0f27844770661fdd3d7d28c293273abd14ca56bb76`, manifest SHA `6ba5778b1c2afbe052266a0f938d67f595831d5015834f7cfe001a0b75e55446`.
- Exactly12 existing type13 playlist records change;1,900 HIRC objects retained, no additions/removals and1,888 unrelated records exact. Actual original properties/parents and−200 dB Volume changes are decoded, including six inserted Volume properties and six replacements. Remaining properties, State chunks, RTPC tails, selectors, transition/source relationships and references restore exactly to baseline.
- All253 media payloads, streaming identities and metadata/reference rows match the pristine licensed baseline, whose original-game cache equivalence is independently established in report45. Embedded-media/non-HIRC chunks remain unchanged.
- Generated Init non-BKHD data is baseline-exact, preserving existing global definitions, State transitions and plugin registrations. No new globals/dependencies. Generated Init is not staged or shipped.
- BKHD version150, bank1324662489, language393239870, alignment16, Project ID17637, type0 and eight zero padding bytes match the licensed baseline. Updated hash `{D3BB521D-76B6-7098-D1CB-AD7ECEDA5F1D}` agrees with metadata. Only BKHD/HIRC chunks differ; no header patching.

Candidate `music_skellige.bnk`: **662,435 bytes**, SHA **`4c6ea268545a02248dd2fad146d9c625e23d479f7e4fccf40fee34c6acacfc27`**.

The12 identities, original values and physical parents are tabulated in report46 and pinned in `src/wwise/regions/skellige-v1.json`. Their native combat and authored siblings remain outside attenuation ancestry. All ten source-only playlists/descendants remain omitted exactly as in the untouched native/ licensed reference; no inclusion repair or regeneration of unrelated banks.

## Coverage and accepted playback

Reuse report46's **38 native/manifest Wwise captures**; the bank is independently checked against that exact authored source. No unnecessary playback repeat.12 generic targets cover85/185 noncombat selection rows (45.9%); one verified-silent target covers9 rows (4.9%). Seven protected targets/52 rows, one mixed target/5 rows and five unresolved targets/34 rows remain native. These are selector-consumer counts, not geographic percentages or blanket Skellige coverage.

Four modified targets were directly observed across representative day/night, dialogue/intermediate-State, boat, cave and settlement groups; all12 receive source/consumer/binary proof. Generic measured contributions stay at/below−214 dB, with explicit−200 dB properties verified. Combat intensity retains effective threat0/35/100 and native layer levels. Main−17 dB outros finish after exploration returns; boat and65s long-return controls preserve full endings. Protected thematic/world and direct authored-branch music remain audible, shared Gwent/minigame score stays native, and Music100→50→100 retains0→−6.0206→0 dB master response. This does not certify every authored cue or a retail scene sequence.

The initially unmatched short settlement capture remains rejected evidence. The stronger location-primed,20s-combat/60s-capture controls verify the same initial selector and complete−17 dB outros at both phases: native/modified endings36.52/36.48s and37.33/37.44s. Production source was not changed to hide a fixture discrepancy. Native fades/beat timing are unedited.

## Native cooker startup and actual diagnostic review

The first two **hidden** isolated launches produced no log/cache and remained idle; both were explicitly stopped, with failed results/stopped-launch receipts preserved in `build/skellige-v3/{consolidated-v3,consolidated-v3-retry}`. These are not successful native builds. A previously authorized visible relaunch in `consolidated-v3-visible` exposed an **EULA** dialog, confirmed through the native process title. Codex requested manual review; the user replied “done”, after which cooking proceeded. Codex clicked no acceptance control and edited no acceptance flag. The exact cause of differing historical launcher behavior remains unresolved; this observation identifies the current waiting dialog, not a Wwise bank incompatibility.

Thirteen relevant settings files were fingerprinted **before** any cooker launch, then compared after manual review/cooking: **all13 unchanged** (`pre-cook-settings-fingerprints.json`, `post-cook-settings-fingerprints.json`). This does not claim registry-wide or all-application-state equivalence. All455 installed bootstrap inputs rehash exactly, and both isolated bootstrap Init copies retain the original native hash. No installed resources were edited.

Actual `bundle-cook-result.json` and `bundle-split-result.json` record **exit0**. Archive creation initially stops at the deliberately fail-closed new-bank diagnostic gate after actual cook/split and payload readback, preserving completed output. The wrapper's resulting failure is not confused with native command status.

`actual-three-bank-diagnostic-delta.json` compares observed normalized output with retained consolidated-v2:

- **32** cook diagnostic rows: all29 accepted v2 rows remain; exactly three additional messages concern Skellige's missing initial split-CSV mapping (native content0 fallback), missing `.txt` description and failed description load. No inherited messages disappear.
- **23** split diagnostic rows, exact Counter match with v2; no added/removed messages.
- No new WEM entries, missing expected bank payloads or changed regional bytes. Native bootstrap diagnostics remain known limitations, not a claim of warning/error-free cooking. Minimal-bank packaging deliberately retains original installed streaming media rather than shipping replacement WEMs.

Only **after observing/reviewing this actual output**, `src/wwise/cooker/three-region-v3-diagnostics.json` records the exact independently reviewed32/23 rows and explicit bank set. It is not generated by renaming NML expectations. `regional_music_bundle.diagnostic_rows` uses only established timestamp/root/input/Documents normalization. Missing profile, different bank set or any changed diagnostic fails closed. The previous two-bank profile remains bounded and passes its retained-output regression.

`--finalize-existing` then revalidates successful exit status, no timeout, exact command arguments, empty stderr, all independent input proofs/definitions, staged-file set, both native cache payloads, original Init and installed bootstrap fingerprints. It creates the ZIP **without recooking or weakening any gate**. Conflicting resume modes, failed/stale native output and existing approved bundles are rejected; ZIP creation uses exclusive mode. Positive/negative tests cover profile scope/content and native completion/status/argument/stderr binding. The explicit `--visible` option is for authorized manual dialog review only; hidden remains default and no automatic EULA action exists.

## Three-bank cache and ZIP

Build spec `build/skellige-v3/bundle-v3-reviewed.json` references the exact D/NML source+binary+media proofs retained in report46 and the new licensed Skellige proof. Final evidence: `build/skellige-v3/consolidated-v3-visible/bundle-verification.json`. All three bank IDs are distinct, with **zero shared serialized HIRC definitions**. Shared references to native globals/media are intentional and independently preserved.

| Cache entry | Offset / bytes | Exact SHA-256 |
|---|---:|---|
|`music_nomansgrad.bnk`|64 /1,273,166|`7317029446858ddf5fa1958ecab6021263c62b097ea0b28218505f591a60bb78`|
|`music_prologue.bnk`|1,273,230 /174,953|`925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`|
|`music_skellige.bnk`|1,448,183 /662,435|`4c6ea268545a02248dd2fad146d9c625e23d479f7e4fccf40fee34c6acacfc27`|

The2,110,749-byte cooked cache has exactly three names/entries, valid index/table bounds, no duplicates/overlaps and exact expected bank bytes. Native splitter readback repeats all three exact payload checks. No Init, WEM, source audio, project, licence or extra entry is packaged.

- Cooked cache: `build/skellige-v3/consolidated-v3-visible/bundle-cooked/CookedPC/soundspc.cache`, SHA `517829f02d170505ff4101398b4c7fb8f4ad506051f9d90934fc7b504034608f`.
- Native split cache: `build/skellige-v3/consolidated-v3-visible/bundle-split/content0/soundspc.cache`, SHA `4d071c325bca642504783f50a299ec3df26da27c4306db5169a46de6ce30b011`. Header differences are native output, not manually repaired; payloads are identical.
- ZIP,1,109,946 bytes:

`C:\Dev\witcher-music-control\build\skellige-v3\consolidated-v3-visible\archives\WMC Consolidated v3 - White Orchard, Velen Novigrad, Skellige.zip`

SHA-256 **`432de7fddb522436603e88e7714b44f7e615e8cabce397bf213c59b3f746e803`**.

Exactly one ZIP entry: `Mods/modWMCConsolidated/content/soundspc.cache`. ZIP CRC/readback equals the cooked cache. It retains the established Vortex root with no extra nesting.

## Final status and next implementation

**141 tests pass** (`unit-tests-v3-profile.log`). `v3-final-preservation.json` verifies seven original bank/archive/Init hashes, including the working v2 archive, and a read-only retained two-bank diagnostic regression. D/NML are unchanged, native Init stays SHA `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`. All earlier individual/consolidated rollback artifacts remain intact. No licensing or cooker prerequisite remains for this built package.

V3 is **offline verified and ready for separately authorized installation**, not deployed or retail-Skellige verified. No required retail trip, imported save or progression manipulation. If installation is later requested, replace the overlapping active consolidated variant through Vortex; do not leave multiple cache variants enabled for the same banks. Preserve v2 for rollback and keep native Init. Current installed configuration remains untouched by this task.

Next valuable regional implementation: **Kaer Morhen**, using the shared complete-context/static-only manifest, all-consumer review, pristine regional baseline, independent decoded/media gates and representative playback before adding its verified bank to a new consolidated version. It is a small remaining main-game region; preserve its authored branch and verify silent/generic classifications. Toussaint follows for broader coverage. No other regional bank was authored or generated here.
