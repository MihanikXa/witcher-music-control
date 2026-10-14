# Expanded NML consolidated package — 2026-10-14

**Observed:** after the user manually applied the approved entitlement to the fresh expanded project, selected `music_nomansgrad` generation succeeds with exit **2**,19 baseline-identical warnings and zero errors. Full source, decoded bank, media, generated-global and native cooker/readback gates pass. The new consolidated-v2 ZIP contains the exact retained White Orchard D bank plus expanded NML v2. Nothing was deployed. NML and combined-cache retail loading remain unconfirmed; report38 authorizes continued offline engineering without custom saves, spoilers or forced visits.

This completes report41's project-local licensing prerequisite. Its failed trial generation remains preserved; no key was inspected, copied or transferred. Reports40–41 retain the packaging implementation, source classification and completed playback evidence rather than repeating them here.

## Build and structural evidence

All evidence paths below are relative to `C:\Dev\witcher-music-control`; generated outputs are ignored. Installed original source remains `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`.

- Project: `build/consolidated-expansion/nml-v2/candidate/w3_audio.wproj`.
- Generated output: `build/consolidated-expansion/nml-v2/candidate-banks-licensed`.
- `command.json`, `result.json` and `generation.log` record Wwise2023.1.19.8928, selected NML, Windows/SFX, exit2 and exactly `music_nomansgrad.bnk` plus disposable `Init.bnk`. No exclusions or unrelated regional generation.
- `reviewed-generation-diagnostics.json`: `white_orchard_candidate_package.diagnostics` compares exact warning Counters against retained `build/regional-system/nomansgrad/baseline-banks-licensed`: nine MediaMultipleUsage, nine MediaDuplicated and one Wwise.dat warning. No new warnings or errors. Exit2 is not concealed or described as error-free generation.
- `licensed-full-gate.json`: `regional_music_gate::{source_gate,decoded_preflight,bank_preflight}` passes with1,508 work units,434 original audio inputs unchanged, all1,507 unrelated work units exact, and restoration of approved edits reproducing all original music semantics. Installed inputs are rehashed against the complete preparation manifest.
- Exactly21 existing type13 playlist records change; all3,831 HIRC objects remain, no additions/removals. `regional_music_bank.record_gate` checks each actual parent, original Volume, approved−200 dB value and variable-layout offsets; remaining fields, State data, RTPCs, serialized tails, selection and transition relationships are exact. Seven originally absent Volume properties insert five bytes each; other approved records replace existing values. No contextual State scope is added.
- All423 generated media payloads, identities, streaming metadata and references equal the retained licensed baseline. Embedded-media chunks remain exact. Baseline non-BKHD chunks/HIRC remain native-exact under the independent retained-baseline check.
- Generated Init non-BKHD chunks are baseline-exact, including global definitions, plugin registrations and State transitions. No new global dependency is introduced. Disposable Init remains evidence only; full native Init equivalence is not a shipping requirement.
- BKHD version150, bank4179090583, Windows/SFX language393239870, alignment16, Project ID17637 and bank type0 match the licensed baseline. Updated bank hash `{393A2104-2AF3-7055-542A-46200CA0460E}` agrees with generated metadata; only BKHD/HIRC chunks change. No header patching.

Source manifest: `src/wwise/regions/nomansgrad-expanded-v2.json`, SHA `44ff812bfb51abce8105157f6c857092ca806534d16458cb4e97c4b97ff4eab5`.
Authored `Interactive Music Hierarchy/music.wwu` SHA `815c3288d958e42fe4532bfb3ebafedc976e753b898670900027bbc0ffa44250`.
Regional bank1,273,166 bytes, SHA **`7317029446858ddf5fa1958ecab6021263c62b097ea0b28218505f591a60bb78`**.

The21 changed ShortIDs are `132074504, 212262762, 265482033, 284863188, 517264825, 557630169, 568231384, 591906274, 619624006, 652104057, 658433984, 715939731, 719937819, 815747428, 844878119, 878261688, 932329779, 939329143, 946096996, 1041422844, 1042184487`. Exact GUIDs, parents, original values and approved complete consumer paths are pinned in the manifest and decoded proof. Report41 explains the source-backed policy decisions. These are playlist-local static Volume edits, not location or world-ancestor gains.

## Native combined package

`tools/regional_music_bundle.py::{verified_inputs,native,reviewed_diagnostics,stage}` consumes `build/consolidated-expansion/bundle-expanded-v2.json`. Independent full regional proofs and exact hashes are mandatory; its preflight's `packaging_allowed:false` remains unchanged because diagnostics, playback and native readback are separate gates.

Fresh root: `build/consolidated-expansion/two-bank-expanded-v2`. Native `bundle-cook-result.json` and `bundle-split-result.json` record exit0. `bundle-verification.json` confirms exactly two entries, valid names/index bounds/offsets, no overlaps/duplicates, and byte-identical bank payloads before and after native split:

| Bank | Offset / bytes | SHA-256 |
|---|---:|---|
| `music_nomansgrad.bnk` |64 /1,273,166|`7317029446858ddf5fa1958ecab6021263c62b097ea0b28218505f591a60bb78`|
| `music_prologue.bnk` |1,273,230 /174,953|`925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`|

There are zero shared HIRC IDs between these banks (`nml-v2/preservation-and-composition.json`). Cooker bootstrap uses original native Init; both bootstrap copies are hash-checked. No generated Init, WEM, source audio, project or licence files ship.

Native cook has29 diagnostic rows; split23. They exactly match report40's reviewed two-bank normalization of the accepted single-bank reference: three additional second-bank missing-description/split-mapping rows, with inherited minimal-bootstrap diagnostics unchanged. Both commands succeed and readback verifies the actual written entries. This does not claim diagnostic-free cooking or retail cache-merging behavior.

Cooked cache SHA `17e2ad8db3c32c69e214b6b66dc81f4064cc3ea446b37c1d70a6f3e141b96e8b`.
Split cache SHA `cf4adfc2a6034a7a0e347d32b25313a387d4c38c443620bb6f576ab7c87aa67a`.

Vortex archive:

`C:\Dev\witcher-music-control\build\consolidated-expansion\two-bank-expanded-v2\archives\WMC Consolidated - White Orchard D and Expanded NML v2.zip`

SHA-256 **`6478460bf8c4dc0f68b24464503808852a9bb65b921a6f84e9909c245da1f512`**.
Exactly one ZIP entry: `Mods/modWMCConsolidated/content/soundspc.cache`; extracted bytes equal the cooked cache. Not installed or deployed.

## Coverage and playback retained

Report41's already completed30 native/reference Wwise captures remain accepted; the generated bank is verified against that exact authored source. No unnecessary repeat or baseline regeneration occurred. Generic coverage increases18→117 of419 noncombat selection/consumer rows,4→21 playlists. Including99 verified-silent rows,216/419 rows require no audible generic score. These counts are selection coverage, not geography or full NML coverage. Protected27, mixed30 and unresolved146 rows retain native behavior;23 mixed/ambiguous playlist decisions remain native. Permanent suppression is approved only for generic-only consumer closures.

Observed playback from report41: countryside combat intro/outro native−17 dB, city outro−13 dB, including complete endings after exploration returns. Paired outro endpoints are21.86/21.79s and23.21/23.16s countryside;22.04/22.01s and23.53/23.52s city. Day/night, threat0→35→100 and different entry phases preserve native combat/intensity. Generic dialogue/intermediate-state overlap peaks stay below−206 dB countryside and−217 dB city. Protected direct early conversation retains Music100→50→100 at−22→−28.02→−22 dB. Native transitions/beat synchronization are unedited. Not every expanded target was individually auditioned; every target receives exact source-consumer and binary-field checks. Ambiguous authored material is preserved, not assumed generic.

Final tests: `python -m unittest discover -s tools -p 'test_*.py'` — **115 passed**, log `build/consolidated-expansion/nml-v2/unit-tests-final.log`. Six preservation hashes pass for retained D/pilot banks, their individual ZIPs, combined-v1 ZIP and installed native Init. Native Init SHA remains `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`. Working White Orchard D and all rollback artifacts remain usable and unchanged.

## Next substantial implementation step

Implement a reviewed **Skellige static-only manifest** with complete consumer/transition closure, reuse the licensed-baseline/decoded-media gates and representative native-selector playback, and add that independently verified bank to a new versioned consolidated bundle. First resolve that region's specific absent/unreachable selector targets from report29; do not authorize them by naming convention or generate unrelated banks. There is no current NML licensing/tooling blocker.

The v2 bundle is ready offline for eventual separately authorized natural-playthrough testing. Do not alter the current installed D or Vortex to make that test happen. If deployment is later requested, only one consolidated/individual variant for each overlapping regional bank may remain active; preserve the individual archives for rollback. Retail NML compatibility and unobserved authored cues remain uncertainties, not prerequisites for further offline development under report38.
