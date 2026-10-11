# Resource footprint and deployment boundaries

## Result

**Latest engineering result:** [report 11](11-white-orchard-blocker-resolution.md) proves native `cooksounds -soundbanksdir` can package only Init/music_prologue into a 207,806-byte cache and native `splitcache sounds` reads both payloads unchanged. The reproducible isolated bootstrap needs no full game cache or regenerated depot. These are vanilla bank fixtures: a deployment candidate still requires native-preserving mixer Init, which the complete hierarchy cannot generate with the current trial and Mastering Suite licences. The revised smooth mixer retains the same logical bank/cache footprint, with four auxiliary paths and a muted dry path instead of bypass-gated effects.

**Observed bank ownership:** all eight world roots are serialized in eight corresponding regional banks. **Proposed full bus mixer:** change those eight bank structures and Init.bnk; no new audio media is required. **One-region generation now observed:** music_prologue.bnk (174,826 bytes) plus Init.bnk (30,277 bytes). Both are version 150, but generation exits with errors and regenerated Init drops vanilla definitions. They are quarantined build artifacts, not approved deployment outputs. See [pilot results](10-white-orchard-prototype-results.md).

The game distributes these banks through `soundspc.cache`, and also has a loose bootstrap Init. A practical candidate distribution is one mod cache containing the changed bank entries plus the replacement bootstrap Init. This is a small **entry set**, not a binary patch to a bank, and not a copy of the vanilla multi-gigabyte cache.

## Exact bank trace

Local roots:

- W = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio\`
- R = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc\`
- C = `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\soundspc.cache`

Three independent checks: resolve SoundBank ObjectInclusionList GUIDs to Events/music.wwu folders and their Play actions; resolve Interactive Music root/child ShortIDs to HIRC records; read the installed cache's bank index and compare its bank payload bytes with R. HIRC parsing used chunk headers `(four-byte tag, u32 length)`, then HIRC object records `(u8 type,u32 length,u32 ID,body)`. No semantic decoding of unrelated object bodies was needed.

| Regional root | world declaration in W/Interactive Music Hierarchy/music.wwu | world ShortID | Bank / current bytes | SoundBanks/music.wwu inclusion lines | C payload offset |
|---|---:|---:|---|---:|---:|
| music_skellige | 33614 | 655655590 | music_skellige.bnk / 662,405 | 6-8 | 534633303 |
| music_prologue | 122301 | 1033516231 | music_prologue.bnk / 174,826 | 13-15 | 534457179 |
| music_misty_island | 140132 | 1037750256 | music_misty_island.bnk / 54,244 | 27-29 | 533129804 |
| music_kaer_morhen | 155258 | 105784741 | music_kaer_morhen.bnk / 326,697 | 41-43 | 532627342 |
| music_nomansgrad | 244033 | 492774600 | music_nomansgrad.bnk / 1,273,131 | 34-36 | 533184048 |
| music_wyzima_castle | 383421 | 361704319 | music_wyzima_castle.bnk / 82,481 | 48-50 | 535978040 |
| music_spiral | 384734 | 577841188 | music_spiral.bnk / 3,904 | 55-57 | 535295708 |
| music_toussaint | 393835 | 680115949 | music_toussaint.bnk / 678,428 | 69-71 | 535299612 |

Each world ShortID appears as HIRC type 12 in its listed bank. The full scan of R/*.bnk found no second owner for these eight IDs. Corresponding regional root IDs are respectively 953773349, 287204113, 20329317, 240585186, 976763369, 857873235, 554357235, 788238583. `music_shared.bnk` has no such world/root definition. Shared stop events reference regions; a reference alone does not imply duplicated regional HIRC ownership.

All table payloads are **byte-identical** to R copies and use BKHD version 150. The eight current banks total 3,256,116 bytes, before modifications/container overhead. They include some DIDX/DATA prefetch audio: replacing a whole bank does not mean all its bytes are purely routing. Reuse unchanged media/prefetch and conversion settings; do not claim generation will necessarily leave every DATA byte unchanged without comparing it.

## Cache and Init evidence

C is 4,633,638,076 bytes, header `CS3W`, version 2. Its resource-name block starts at byte 4,633,548,803, length 37,097, with 2,174 entries: **740 .bnk and 1,434 .wem**, verified by the follow-up's cache-entry-classification.json. For this observed format, header +24 is the u32 indexed-resource count; +32 is the u64 name-block offset; +40 is the u32 name-block length. Immediately after names, each 24-byte entry gives `(u64 name-relative-offset, u64 payload-offset, u64 payload-length)`. Resolving these entries yields the offsets above and verifies the bank payloads start with BKHD. This layout is an **observed decoding of these files**, not a promised public cache-writing API. Header +28 must not be assumed to be a Remastered streamed-media count; native split rewrites that uninterpreted field, while keeping the same indexed resources.

The cache also contains `init.bnk` at offset 370,791,266, length 32,840. It matches R/Init.bnk and `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\initialdata\sound\Init.bnk`, SHA-256 `2DCB418B9F96389A57341A49E86CDCB0C18D95552A0E17DCCF10D4DF1D54D277`. Init chunks are BKHD/INIT/STMG/HIRC/ENVS/PLAT; regional banks have HIRC and sometimes media chunks, not STMG.

**Init required:** the proposed mixer adds a bus, GameParameters, bus effects and state gating. These are initialization/global definitions. Audiokinetic's [SoundBank general information](https://www.audiokinetic.com/library/edge/?id=soundengine_banks_general.html&source=SDK) identifies bus hierarchy, game syncs, RTPCs and bus effects in Init. Local Init has the global chunks and existing AkGain registration. A new content bank does not replace the bootstrap Init or extend its bus hierarchy automatically.

The installed REDkit deployment script `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\bin\tools\cooker\toolchain\_step_deploy_common.bat:44` copies loose `bin\initialdata\sound\Init.bnk`; :69 has a commented-out loose SoundBank copy. `...\local_tests\soundbank_cooking\wcc_cooksounds.cmd:7` invokes cooksounds, and `wcc_splitcache_sounds.cmd:7` splits a cooked soundspc.cache. None of those commands was run.

FMC supplies both `C:\Dev\witcher-music-control\reference\fmc-audio-remaster\bin\initialdata\sound\Init.bnk` and `...\mods\modFMCAudioRemaster\content\soundspc.cache`. Its cache contains exactly eight indexed banks: combat, generic_movement, global_doors, grunt_vo_geralt, gui, init, vo_definitions, work_voiceovers. The embedded Init is 38,007 bytes and matches its loose Init. **It contains no regional music bank.** Thus FMC is not evidence that our regional changes can avoid those banks. Its examined bank headers use version 140, versus current vanilla 150: do not use its generated resources as a current-build template without validation.

**soundspc.cache required?** It is the evidenced shipping container for regional banks. No supported loose-mod .bnk lookup was found. Therefore budget a mod cache for the changed banks, and a matching loose bootstrap Init. Whether embedded Init must also be included is unresolved loader behavior; the conservative proposed package includes it, matching the local reference/deployment pattern. An Init-only state test would not require regional replacements, but cannot isolate world from quests at their current common bus.

## Can an auxiliary bank avoid replacements?

**No demonstrated additive mechanism.** Existing world nodes inherit Music and contain no reference to a proposed bus/RTPC/effect. Loading a new bank cannot make those nodes acquire such references. A new bus requires existing OutputBus overrides; direct world gain requires existing Effects/RTPC edits. Global Music-bus attenuation would affect quests. An AuxBus send adds a path without removing the dry path.

Attempting to redefine existing world IDs in a supplementary bank is not an established merge/override contract. It risks duplicate object ownership and load-order-dependent behavior. It also does not solve Init/global definitions. Prefer complete replacements of affected bank entries, preserving IDs and untouched content, rather than assuming engine-level HIRC patches.

All eight regional banks need replacements for complete geographic coverage. A prologue-only proof changes one. Exception routing within these regions adds object changes to the **same** eight bank entries, not a bank per exception. `music_shared`, menu/credits, bard/emitter and unrelated audio banks need not change on the traced ownership evidence.

## Selective generation versus delta deployment

**Observed supported authoring operation:** matching `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin\WwiseConsole.exe generate-soundbank --help` supports `--bank`, `--platform`, `--soundbank-path`, `--cache`, `--root-output-path` and disabling custom pre/post commands. Help was queried without a project argument; no project was opened or generation run. Selected-bank generation is available. It produces complete banks plus global outputs, not serialized patches to selected HIRC records.

Current `W/w3_audio.wproj:64-75` points Windows SoundBank output at the REDkit r4data tree; :45 has an external-source developer output path, and later project settings include generation commands. A future build must use an isolated project copy and explicitly isolated outputs/cache; it must not run the project defaults against the read-only installation.

**Original pilot limitation, now partly resolved:** report 10's bounded help attempts failed during engine/root initialization. Report 11 establishes the supported separate-argument `-root` override and a reproducible isolated commandlet bootstrap. `cooksounds -soundbanksdir` packages only two native fixture banks, without Wwise generation or a copied game cache, and `splitcache sounds` reads them back. No depot repair/regeneration was needed. **Still unproved:** a native-preserving generated mixer Init and live mod-cache precedence/vanilla-streamed-media fallback. Keep the direct Remastered cooker output; the splitter changes an uninterpreted header field. Do not equate successful native serialization with game deployment acceptance.

## Compatibility and expected generated changes

| Item | Expected change / reason | Conflict boundary |
|---|---|---|
| Init.bnk | New bus/three parameters/effects/global mix data | Global replacement; conflicts with other Init modifications, including FMC |
| Eight regional .bnk entries | New world output override (or direct gain alternative); chosen exception overrides | Bank-entry granularity; conflicts with regional audio/event/routing mods even when their media is unchanged |
| mod soundspc.cache | Carrier of changed bank entries, possibly matching embedded Init | Do not assume two mod caches with overlapping entries merge; loader precedence requires proof |
| .wem / originals | No intended source/conversion change | No new streamed media intended; hash after future generation |
| SoundBanksInfo / project metadata | May be emitted by generator | Build evidence; not demonstrated required for game deployment |
| WitcherScript/menu files | None in prototype #1; settings adapter later | No state hook or full vanilla script replacement proposed |

Bank regeneration can alter more than the intended property if project/platform/conversion/global settings differ. Preserve object IDs and compare HIRC, DATA/DIDX, event actions, transitions, state groups and user-volume curves. Exact future filenames beyond these required logical outputs cannot be certified without the deferred generation. A compatible combined audio build may be necessary where another mod owns Init or an affected regional bank.

## Minimum prototype #1 footprint

**White Orchard target clarification (2026-10-11):** White Orchard's region-specific exploration and dialogue music is inside the Wwise `music_prologue` hierarchy, as traced in report 03 (the `location_prologue=village` and `village_exploration` path). Therefore user-requested **White Orchard** testing still requires the same logical bank pair: `Init.bnk` and `music_prologue.bnk`. This does **not** mean the first in-game test should take place in the opening Kaer Morhen dream/tutorial. Audio-mapping validation in the game is still required; do not assert all White Orchard subareas have constant music.

Future isolated authoring edits: a copy of `Master-Mixer Hierarchy/Default Work Unit.wwu` (new bus with custom Gain instances/slots), a new Game Parameters work unit (three proposed definitions), and `Interactive Music Hierarchy/music.wwu` (only prologue/world output override). Existing SoundBank inclusion definitions suffice; no Events, Switches, States, source WAV or quest-branch edits are required. Custom effects can be embedded on the bus so a separate Effects work unit is optional.

Future generated logical outputs: **Init.bnk + music_prologue.bnk**. Proposed install outputs: **matching bootstrap Init.bnk + one minimal mod soundspc.cache containing music_prologue and matching Init entries**. No source script, UI or hook is needed to test hard-coded defaults. Cache packaging and loader precedence remain acceptance tests, not claimed accomplished work.

### Measured generation footprint and acceptance failure

`C:\Dev\witcher-music-control\build\white-orchard\bank-comparison.json` records the controlled comparison. The regional bank retains every vanilla HIRC object; only world_music ID 1033516231 changes. DIDX/DATA are identical to vanilla. No quest/event/transition or source-media change is needed for the mixer. Wwise also converts 47 WEMs while generating these banks; unchanged existing media IDs/content references mean those conversion outputs are not an additional proposed shipping set.

Relative to the isolated baseline, prototype Init adds one Bus and three custom Gain records, with no changed or removed existing HIRC records. However, **the baseline itself** omits eight vanilla Bus records, one custom effect, HomeCinema's Effect ShareSet and one AuxBus, and its INIT plugin-registration count falls from 18 to 9. STMG also differs before our edits. The console reports missing Mastering Suite licences, but the other omissions must not all be attributed to licensing without proof. A licence alone has not been demonstrated to restore a vanilla-equivalent global Init from this reduced project. Restore/verify global fidelity before any packaging/deployment candidate; do not replace the native Init with the present generated file.
