# 27 вЂ” Working White Orchard fix recovered and preserved

Date: 2026-10-13. Read-only recovery after merging remote feedback (`4d94bfa`) with local implementation commits `d50d67e`, `33dc6e7` in merge `dbf4346`. No Wwise generation, licence operation, deployment, Vortex change, launch or save access. User feedback **вЂњEverything works great nowвЂќ** is accepted as satisfactory current gameplay, without extending that claim to authored cues or other regions.

## Identifying the actual installed variant

Explicit machine-local evidence paths:

- G = `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3`.
- P = `C:\Dev\witcher-music-control\build\white-orchard-transition-fix`.
- R = `C:\Dev\witcher-music-control\build\full-game-audit`.
- W = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`.

**Observed:** `G\Mods\modWMCBankLoadingTest\content\soundspc.cache` is byte-identical to `P\cooker\packages\D\modWMCBankLoadingTest\content\soundspc.cache`. The existing `tools/white_orchard_loading_package.py:verify` readback resolves its sole entry to the retained D bank, exactly 174,953 bytes at offset64; it contains no Init. `fsutil hardlink list` identifies the same file in Vortex's staging entry **WMC White Orchard вЂ” Transition Fix Test**. This identifies the currently installed variant as D from bytes and staging, rather than its name alone. R/`installed-identity.json` retains only selected hash facts; no profile database is copied to Git.

| Artifact | SHA-256 |
| --- | --- |
| Installed and staged D cache | `44a7481224be024d996b828d3bc396efacc87a5209a11db97a385ef4ad33484d` |
| Extracted D bank / P/candidate-banks-licensed/music_prologue.bnk | `925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d` |
| D production music.wwu / P/candidate/Interactive Music Hierarchy/music.wwu | `cba9ed036e94fe658ca8e506d5539e1f7139f7caea51a21cac3fadbdcebcc259` |
| D ZIP / P/cooker/archives/WMC White Orchard вЂ” Transition Fix Test.zip | `20bdfbd966aa07aa913c0ecb4694badf581082cf972a7504ef1a344ee56b3679` |
| Retained C bank | `80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698` |
| Retained C cache | `a2b8cc23285c5b6cd392b0301328d75bd545dde8d9e0c06007b674b68a14aa12` |
| Native game Init / G/bin/initialdata/sound/Init.bnk | `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277` |

**Supported inference:** current installation, retained D evidence and latest satisfactory user feedback correspond to the same working implementation. No historical launch-time manifest or captured runtime trace establishes that each earlier reported run used these exact bytes. That residual provenance limitation does not negate the user's gameplay confirmation. The former report25 feedback concern about absent local source is resolved by this merge/recovery.

## Mechanism and bounded change from C

Reports [25 diagnosis](25-transition-bleed-diagnosis-and-local-fix.md) and [26 licensed result](26-licensed-transition-fix-candidate.md) retain experiments, timings and source references. C's world State Voice Volume recovers to unity on combat entry while native beat selection/crossfades keep an exploration voice alive; a short intermediate cutscene/movie/music-only State can likewise restore world gain before dialogue returns to attenuation. Both mechanisms were reproduced with native playlists. Direct explorationв†’dialogue did not reproduce a burst. The exact State sequence of the user's original dialogue is still inferred, not traced in game.

Source: `W\States\global_states.wwu`, `game_state` default1000ms and custom transitions; `W\Interactive Music Hierarchy\music.wwu:122449`, general selector music transitions; `G\content\content0\scripts\engine\sound.ws:156`, `SoundGameStateChange` sends State independently of selector completion. Report25 distinguishes profiler wall timing from PCM timing. The approximately one-second symptom alone was not used to select a fix.

D **retains C's 25-State world table** and adds static Voice Volumeв€’200 dB to five playlist objects: 133462974 village/day, 168472101 village/night, 883068472 camp, 1049502408 cemetery, 833483595 battlefield. Their complete GUID/name/original-volume identities are in `C:\Dev\witcher-music-control\src\wwise\white-orchard-transition-fix.json`; `tools/white_orchard_transition_author.py:author` verifies 40 world-only selector consumers, no direct event targets, all1,508 work units and restoration to exact C semantics. No transition definition, selector, script, bus, effect, global State, RTPC or media asset was changed. These static gains suppress the continuing generic voices instead of changing when Wwise replaces them.

`tools/white_orchard_transition_package.py:audit` was rerun to fresh R/`D-reverified.json`: **all18 checks pass**. Exactly five existing type13 HIRC records differ from C, with only their bounded Volume property bundles changing; other485 records and world State bytes remain exact C. No added/removed IDs; DIDX/DATA and converted media preserved; BKHD identity retained, metadata hash explained. ProjectID17637 is unchanged from working C/D; original Init stays ProjectID39. Historical generated-Init equivalence is not a requirement for this regional deployment. The unchanged disposable generated Init is additional no-new-global evidence, not a shipped asset.

Native combat paths, threat layering, Music master and q001 intro/conversation playback were measured in report26. User confirms combat remains audible; intensity and specific authored cues have authoring evidence, not exhaustive in-game coverage. All nonmusic records/resources are unchanged by this regional patch; no voice/ambience/SFX gains are edited. This is structural isolation evidence, not a fresh subjective test of every sound.

## Reproducibility and retained evidence

The production sequence is preserved in source:

1. `tools/white_orchard_prepare.py --preserve-hierarchies`: fresh complete context and input hashes.
2. `tools/white_orchard_state_volume_author.py:author` with `src/wwise/white-orchard-state-volume.json`: clean local world State table.
3. `tools/white_orchard_transition_author.py:author` with transition JSON: five bounded playlist properties, no fixtures.
4. Existing `tools/white_orchard_wwise.py:generate`: selected Windows/SFX `music_prologue`, effective project-local licence manually applied by user.
5. `tools/white_orchard_transition_package.py audit`, then `package`: fail-closed comparison and isolated native cook/readback/ZIP.

Original licensed output exit **2** /15 unchanged warnings is preserved in P/`candidate-banks-licensed/{command.json,generation.log,result.json}`; this task did not regenerate it. Failed unlicensed P/`candidate-banks` remains untouched. Keep P/`licensed-D-audit.json`, `cooker/D-package-verified.json`, `final-probe-and-preservation-summary.json`; all raw native-selector captures under `build/white-orchard-transition-diagnosis/validation`; native/licensed controls from report20; C source/banks/caches and A/C ZIPs from reports22вЂ“23. Reports26/27 record exact artifact identity without redistributing binaries.

**Reproducible source and independently retained verified artifacts: yes.** Byte-for-byte fresh reproduction is not claimed for future Wwise metadata/custom source GUIDs; future builds must pass semantic/property, media, references and metadata gates. Fresh project licensing remains manual and private. **Current installed artifact: identified.** Authored exceptions and generalization: still open, addressed in reports28вЂ“29. No installation action is necessary to preserve this working version.

All **32 unit tests pass** (22 existing bank/build controls plus ten new inventory controls); negative tests intentionally emit failed-gate fixtures. Production audit passes separately. Source/build/private outputs stay ignored; only sanitized code and reports are committed/pushed.
