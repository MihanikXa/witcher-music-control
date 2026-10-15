# Skellige pristine baseline licence gate — 2026-10-15

**Observed:** the fresh, complete, unmodified Skellige baseline reaches the project-local entitlement prerequisite. Selected generation exits1 with no banks, six Mastering Suite errors, one fatal trial-media limit (26,218/200), and ten warnings. No Skellige music edits, candidate, playback fixture or three-bank package were produced. Stop here under the user's Phase1 instruction; apply the existing approved entitlement manually to this project before continuing.

## Exact manual action

Open in Wwise2023.1.19.8928:

`C:\Dev\witcher-music-control\build\skellige-v3\baseline\w3_audio.wproj`

Use **Project → License Manager** to apply the existing approved Witcher3 REDkit entitlement and save. Do not send the key through chat or copy it to scripts/evidence. No licence field/key was inspected, extracted, transferred or logged. Other projects' successful generation does not establish licensing for this fresh project.

After confirmation, rerun selected `music_skellige` generation into a fresh `baseline-banks-licensed` directory, preserving this failed output. Establish native HIRC/media/stream/header fidelity before modifying the region. Do not regenerate White Orchard or NML.

## Complete preparation and preservation

`tools/white_orchard_prepare.py::prepare` ran with `--preserve-hierarchies --regional-root music_skellige`, using the installed read-only source `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`. Output is `build/skellige-v3/baseline`. No pruning or inclusion changes.

- All1,508 work units are preserved byte-for-byte, including original hierarchies, events, SoundBanks, transitions and globals.
-253 distinct regional audio inputs,3,093,678,926 bytes, are copied and hash-verified against installed originals. Independent copies were used for this first canonical regional baseline; no new hardlinks or modifications to shared originals.
- `input-manifest.json` records original hashes and version: schema119, `v2023.1.19`, build8928. Preparation isolates project paths/commands using the existing helper.
- `build/skellige-v3/baseline-source-preservation.json` rehashes all copied WWUs/audio and installed counterparts after generation. The original verification attempt completed input hashing but rejected a version string because it expected `2023.1.19` instead of the actual `v2023.1.19`; the initial helper is retained, and the corrected verification repeats the hashes. This was a verification-string error, not a source/version mismatch.
- Existing White Orchard D bank, NML expanded-v2 bank, consolidated-v2 ZIP and installed native Init remain at their exact report42 hashes. No installed mod, Vortex, saves, profiles or game processes were changed.

## Generation evidence

Ignored `build/skellige-v3/baseline-banks/{command.json,generation.log,result.json}` retains the actual selected Windows/SFX invocation and diagnostics. `tools/white_orchard_wwise.py::generate` uses the established isolated output/cache/metadata paths, no source exclusions and no external pre/post commands.

```powershell
python tools/white_orchard_wwise.py --console 'L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe' --project build/skellige-v3/baseline/w3_audio.wproj --bank music_skellige --output build/skellige-v3/baseline-banks
```

Exit1, zero BNKs; trial-media and six Mastering Suite failures are the concrete prerequisite. Nine MediaMultipleUsage warnings and one Wwise.dat warning remain recorded, not hidden. A successful baseline/candidate must receive its own complete diagnostic review. No native compatibility conclusion can be drawn from this failed build.

## Ten source-only playlist observations

`build/skellige-v3/source-only-reference-review.json` reuses retained inventory and `white_orchard_compare.read_bank`, then inspects actual references to each absent playlist **and its descendants** in `Interactive Music Hierarchy/music.wwu`, `Events/music.wwu` and `SoundBanks/music.wwu`. Native bank remains662,405 bytes/1,900 HIRC records, SHA `8bfa09f056045beebe51f59e19b899b370fed999a2212b1ddba7dd26af34476c`.

| Source playlist ShortID | Original source line | External reference observations in those three work units |
|---|---:|---|
|250487810|35210|None found|
|822810934|35573|None found|
|802768195|42722|None found|
|1003349432|43085|None found|
|407311040|46235|None found|
|543725422|46599|None found|
|149108804|57460|One `TransitionObjectRef` to descendant segment GUID `DFFD83C3-FC53-486A-817E-1F4C47617EC4`|
|954667010|93919|None found|
|365608565|100451|None found|
|636008624|102380|Four transition-rule `ObjectRef` references to the playlist; no inspected AudioNode selector entry|

**Inference limit:** an absent playlist container does not imply absent/unreachable descendants, and transition-rule endpoints are not the same as selector consumers. These observations do not certify runtime reachability, inclusion or deletability. In particular, the two referenced cases must not be labelled unused from the earlier AudioNode-only inventory. Licensed untouched generation and decoded transition/segment inclusion are still required. All ten remain unchanged; no inclusion flag was edited to force an object count.

## Current status and next step

Full repository suite: **115 tests pass** (`build/skellige-v3/unit-tests.log`). This turn adds documentation only; existing source/decoder tests continue passing. Working consolidated-v2 user feedback remains report43's bounded natural-play success, not a specific NML/Skellige route test.

No new classification/suppression coverage is claimed. The23 Skellige selectors and26 relevant noncombat targets from report29 remain the review scope, not approved edits. Boat, shared Gwent/minigame, protected thematic and native transition paths retain original source. No new playback measurements are claimed.

**Smallest next action:** manual entitlement application to the exact isolated baseline above, then resume pristine selected-bank verification. Once that independent baseline passes, continue complete manifest classification, source authoring, representative long-transition playback, candidate decoding and native three-bank cooking. No retail test, custom save, progression or Vortex action is needed.
