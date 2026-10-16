# 53 — Music Plus 3.3.0: actual implementation and direction — 2026-10-16

## Decision

**Recommend an independently designed hybrid: retain WMC's native combat/story foundation and develop optional sparse exploration using selected ideas demonstrated by Music Plus. Do not combine the installed mods.** Music Plus is a substantially more configurable whole-track soundtrack replacement, with a real working-data design for track-boundary rests and location carryover. It is not merely a description of a possible scheduler. However, its combat redesign is integral to the shipped banks, its optional dialogue lowering operates on the global Music parameter, and its exploration controls also encompass world-selected thematic score. Those differences conflict with our preservation requirements. Turning off added tracks does not reverse them.

This verdict follows static inspection of both actual archives, all twelve replacement banks, the editor's data and code, and the shipped WitcherScript. **No Music Plus program, script, editor, server, Wwise session or retail game was executed.** Runtime sound, performance, compilation, transition-rule precedence and long-session reliability are not newly measured here. Existing WMC playback and retail results retain their original scope: v4 is offline verified; the latest user-confirmed installed configuration was v2, with specifically successful White Orchard testing (reports35,43,49–51).

## A. Inputs, method and evidence addresses

Exact original archives under `C:\Dev\witcher-music-control\reference\music-plus\`:

|File|Bytes|SHA-256|
|---|---:|---|
|`Music Plus MAIN FILES 3.3.0 Remastered 13818 3.3.0 2026-10-15T20-23Z Q81OXmQZ0.zip`|21,479,021|`2327d3895d63dc24141e78ae7ab1e953b22234f624dd6a1cbff870c10e3a94a7`|
|`Music Plus Music Pack 3.2.0 13818 1 2026-10-15T20-10Z 5sT4Vv5b8.zip`|930,980,232|`e36bf00ab035e01d3208e1b08bc2d4bcbdb57249b72585164185aa4e9b004636`|

The pack is actually labeled **3.2.0**, including the main archive's `musicpack.txt`; do not relabel it 3.3. The author's [3.3 changelog](https://www.nexusmods.com/witcher3/mods/13818) says the existing pack remains usable. Local required-file enumeration independently matches all275 pack entries.

The complete member inventory, per-file sizes/hashes, per-bank hashes/counts and compact derived results are committed in [53-music-plus-archive-evidence.json](53-music-plus-archive-evidence.json). This contains metadata, not third-party source/audio. Original ZIPs remain untouched. Extraction into fresh ignored analysis directories rejected absolute/traversal/duplicate/link members, read ZIP members with CRC verification and checked extracted sizes. Main:41 files/106,593,304 expanded bytes; pack:one930,980,054-byte cache. Nothing was installed.

Local aliases below expand to these exact paths:

- **A** = `C:\Dev\witcher-music-control\build\music-plus-audit`.
- **M** = `A\main`; **P** = `A\pack`.
- **S** = `M\mods\modMusicPlus\content\scripts\local\musicPlus.ws`.
- **X** = `M\bin\config\r4game\user_config_matrix\pc\modMusicPlus.xml`; **CFG** = `M\bin\config\base\modMusicPlus.ini`.
- **J** = `M\mods\modMusicPlus\editor\index.json` (JSON pointers identify entries below).
- **H** = `M\mods\modMusicPlus\editor\editor.html`.
- **B** = `M\MusicPlus-Playlist-Editor.bat` (read as text only).
- **MP banks** = `A\banks\<bank>.bnk`, extracted from the verified main-cache index.
- **N** = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc`.
- **W** = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`; **I**=`W\Interactive Music Hierarchy\music.wwu`, **E**=`W\Events\music.wwu`.
- **V** = `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts\engine\sound.ws`.

Relevant contents: one28,245-byte WitcherScript file, X/CFG,18 localized string files, a84,703,633-byte bank cache, H (34,331 bytes), J (11,042,657 bytes), pack manifest, three BAT tools, and bundled vgmstream executable/DLLs/COPYING. The930MB pack cache has exactly275 WEM entries and **no banks**. The main cache has exactly12 banks and **no Init or WEM entries**. No authoring WWUs/project or complete bank-build source accompanies them. B mentions private build-tool names; those comments do not supply those missing implementations.

### Independent binary inspection

`tools/music_plus_audit.py` reuses the native cache reader and bounded bank reader; it checks extracted bank-set/payload identity before comparing native banks. New `tools/music_comparison_decode.py` independently decodes v150 music prefixes, RTPCs, children, meters, stingers, transition rules, decision trees, playlist items, segments and non-switch tracks. Layout reference is the pinned primary [wwiser parser](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/parser/wparser.py), associated enums in its [wdefs.py](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/parser/wdefs.py). These are reverse-engineered format references, not proprietary runtime authority. They were read, not installed/imported/executed. Production WMC decoders/gates remain unchanged.

**Observed:** all251,721 music segment/switch/playlist records and246,705 music tracks decode completely without unexplained tails. All12 banks use v150; **only HIRC differs from native**. BKHD is byte-identical, including native Project ID39; DIDX/DATA are exact wherever present. This establishes serialized differences, not the original mod author's build method or runtime compatibility certification.

|Bank basename|Native HIRC|Music Plus HIRC|Added / removed / changed native records|
|---|---:|---:|---:|
|music_prologue|490|37,029|36,548 /9 /59|
|music_nomansgrad|3,831|278,000|274,217 /48 /407|
|music_skellige|1,900|74,827|72,950 /23 /276|
|music_kaer_morhen|440|13,197|12,760 /3 /22|
|music_toussaint|1,804|83,990|82,204 /18 /189|
|music_wyzima_castle|97|4,992|4,896 /1 /6|
|music_misty_island|70|5,332|5,263 /1 /9|
|music_spiral|33|4,490|4,459 /2 /9|
|music_em_bard_groups|27|35|8 /0 /2|
|amb_dyn_bob_music_em_bard_group|37|53|16 /0 /4|
|amb_dyn_bob_music_em_mandragora_bards|13|17|4 /0 /1|
|music_em_ep1_wedding_bards|23|27|4 /0 /1|

Evidence: `A\architecture-final.json`, `banks/<name>`, bank-local HIRC IDs in `differences`. Across the12 banks,818 native event records and2,083 native action records remain exact (counts are bank-local, not claimed unique IDs). Regional event targets keep their identities while their downstream music graphs are rebuilt. Native Init SHA remains `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`.

### Actual controller and graph

```text
native location/music_type events ──> regional MusicSwitch root
                                      ├─ authored branch: native present records exact
                                      └─ world branch: flattened location × game_state × extra switches
                                           ├─ exploration/tavern scheduler copies
                                           ├─ combat scheduler copies
                                           └─ Gwent/minigame selections
MusicPlus WitcherScript ──> custom SetSwitch events + category RTPC values
menu/persistence ─────────> script; editor ──> on-disk bank weights/rules
pack cache ──────────────>275 additional streamed media sources
```

Concrete example: MP `music_prologue.bnk` root287204113 still selects world1033516231 versus authored323955723 using music_type884382085. World originally had location_prologue alone; now arguments are205934134 (teleport switch),3512909160 (location),766723505 (native game_state),764195689 (combat-as-exploration switch). The nine original location containers are removed; their playlist-level material is reparented beneath world. Its transition rules grow3→56; root rules19→23. NML world492774600 similarly combines location964668249 with these extra controls. This is a rebuilt decision system, not a volume patch (`architecture-final.json/changed_native_music_nodes`).

S:32–98 chooses eight start/skip variants; `mod_music_next_v0` event483684750 references action728917564. Its exact bounded17-byte action is SetSwitch(global), group3826109949, value172378896. Exploration schedulers additionally use pause-chance group1992375827 and pause-length1909588031; combat uses variant1941480456 and mute2375221010. Actions are verified from serialized fields, not guessed from names. No shipped bank has STMG/INIT chunks or new buses/effect/plugin-registration records. Custom RTPC/switch **references** are present; this archive uses native Init rather than shipping global authoring definitions. That is valuable evidence for a potential Init-free control design, not our own retail proof of arbitrary new parameter names/defaults.

## Sparse playback: what it really schedules

**Observed graph:** exploration target719937819 in NML is now a MusicSwitch (type12), with variant/chance/length arguments and528 decision rows. Variant0/chance1/length0 selects playlist1413886368. Its continuous sequence runs: first weighted track group → weighted gap → infinite sequence of weighted track group/gap pairs. Tracks use their segment entry/exit markers; playlist transition sync is ExitMarker, with zero internal fades in this example. Random groups are StepRandom; the repeated music pool has avoid-repeat2. Initial disjoint groups support a different first piece for skip variants. These are authored playlist copies, not a script timer waking to start every track (`A\reproducible-pause-profiles.json`; J `/playlists/13/{pools,first}`; H:460–518).

The24 explicitly resolved profiles demonstrate:

|Pause length index|Long-gap choices, seconds|
|---|---|
|0|10,20,30,45,60|
|1|30,60,120,180|
|2|60,120,180,240,300|
|3|120,240,360,480,600|

For chance indices1/2/3, these long-gap alternatives receive total25/50/75% weight, with the remainder assigned to a **one-second silent segment**, not literal zero delay. Index4 always selects a long gap; index0 has no gap stage. Five-second silent segments are looped to construct the long durations. Representative silent segment746491802 and track source16708307 resolve to the existing native silent material established in report07: `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline-banks\SoundbanksInfo.xml:60208–60211` independently maps16708307 to the verified original silent source. The archive's chance5 selects a looping silence profile1763123210 when ExplorationVolume=0. These are discrete weighted durations, not uniform continuous sampling across the menu's ranges (`S:176–201`, decoded profiles).

**Consequences and limits:**

|Question|Implementation-backed answer|
|---|---|
|Only after complete tracks?|Normal rest insertion follows a selected segment/group's exit marker. Combat, skip, fast travel, immediate locations and setting-profile changes can interrupt it; no universal promise to finish every composition. Some native tracks are multi-layer/grouped material, not one WEM per composition.|
|Random or context-driven?|Weighted Wwise track/gap choices. No discovery, vista, narrative salience or weather-triggered entrance logic appears in S or the scheduler arguments. Horse/boat/underwater controls are volume context, not meaningful-moment composition selection.|
|Location/day-night changes?|World rules can defer to ExitMarker. J `/zones/keep` is `[7,0,0]`; `/zones/cut` is `[0,3000,3000]`. H:240–253,514–518 rewrites sync/fades for instant-place options. Ordinary places default deferred; some tavern/silent contexts immediate. Thus a piece or scheduled silence can carry over until its exit; exact nested-loop exit handling still needs playback, not an invented timer result.|
|Weather?|No explicit MP weather scheduler. This does not claim the entire game's weather/audio system is absent.|
|Combat during silence?|New world rules select combat with Immediate sync, source fade2s/destination1s, rather than waiting for the exploration track boundary. Structural path exists; actual response latency was not measured here.|
|Quest cue priority?|Original authored event/actions and music_type selection remain; the scheduler is below world. An authored branch can replace world without waiting for its gap. Native event priority/actual runtime timing is not newly auditioned; parent rules and global script controls qualify the preservation claim below.|
|After combat?|S:280–343 draws a fresh exploration variant after a four-second combat hold. This is a new start selection, not an implemented resume-position store.|
|After authored scene?|Unchanged explicit return-to-world events and root rules resume selection. There is no script scene-end scheduler checkpoint/resume. At least some native SameTime entry rules change to EntryMarker, so do not promise native position continuity.|
|Natural completion?|Ordinary playlist progression/location carryover uses musical exit points; interruptions use designed crossfades. This offers phrase completion in some paths, not uniformly native phrasing.|

This is **sparse whole-piece rotation**, with basic state/location responsiveness. It is not demonstrated short musical punctuation or context-sensitive dramatic entrances. “50% chance of a pause” is not50% elapsed silence. For illustration, a hypothetical180s piece followed by the decoded chance2/length0 distribution has an expected17s gap, or roughly91% musical occupancy before interruptions. This is an illustrative model, not a measured playlist/session average; track weights, repetition and interruptions matter. “Sparse” alone does not establish environmental dominance.

## Combat: substantial, partly configurable redesign

S:246–343 implements a fixed4s postcombat tail. On land combat→exploration, it updates logical currentGameState/callbacks but **does not post the new Wwise game_state**. A later SetDefaultGameState invocation releases it. Consecutive land-combat/monster-hunt transitions can return without posting a new state. Native V:156–190 posts accepted state changes directly; V:557–624 invokes default-state selection, with0.15s cooldown and stopped/menu/loading branches. Therefore S's comment “every frame” is not a guarantee of four-second wall-clock accuracy while stopped/paused. The delay and state sequencing differ materially from native.

Binary proof goes beyond descriptions: the known NML transition playlists900789511,1019244598 and955053242 remain in MP, with their segments458178455,757873925 and303498338. Their properties/segments largely persist, but their physical parents move to world492774600. **None of those six IDs is reachable from the MP regional root through a conservative playback closure** (all selector alternatives, even zero-weight playlist leaves, transition segments and stingers included). Source/destination rule conditions are not playback edges. An arbitrary direct external event is outside this bounded closure; native event/action comparison finds no changed event that restores these normal paths. Retained records do not mean retained normal combat intros/outros (`A\native-transition-comparison.json`, `conservative-playback-closure.json`; original ancestry proven report34).

The MP world/root rules add immediate exploration→combat2s/1s fades, combat→exploration4s/6s fades, and combat→combat5s/5s ExitMarker crossfades (White Orchard root287204113 appended rules19–22; corresponding NML world rules339–341). With S's4s hold, a short fight can retain the selected combat body before the return fade; it does not play the original outro simply because the body stays audible. Native bridge/outro timing and destination phrase alignment are replaced on these paths.

Native intensity/threat mechanisms are **not all removed**: decoded MP music tracks retain9,992 intensity and2,229 threat_rating curves across duplicated records; e.g. native-source layered tracks190472864/1963456447 retain intensity gain curves. Other added music is full-mix Opus media. Curve presence/count does not establish equivalent intensity progression for every randomized alternative, and counts are inflated by copies. No new combat audition was performed. It would be wrong to say MP has no adaptation, or that its original dynamic combat is preserved wholesale.

CombatVolume and track/source weights are configurable. `CombatExploration` optionally routes combat to day/night exploration copies while keeping authored siblings separate (`S:346–374`, X). **There is no exposed native-combat-structure toggle**, intro/outro restoration switch or four-second-tail setting. Turning all non-Vanilla editor sources off leaves the new sequence graph, transitions and script hold. This may be a desirable soundtrack redesign for other listeners; it does not meet our original-combat criterion.

## Authored cues, dialogue and special music

### Strong protection, with important qualifications

Observed dedicated-branch results, native-present HIRC records exact: prologue118, NML1,075, Skellige436, Kaer Morhen164, Toussaint611, Wyzima34, Misty14, Spiral1; total2,453. This covers records actually present in each native bank, not missing source-only objects. The alternative `quests_cutscenes` spelling is resolved by original source identity. All818 native bank-local events and2,083 actions also remain exact. MP prologue authored conversation playlist933909186 remains reachable in the conservative root closure, outside exploration-volume RTPC ancestry. E's explicit q001 intro/conversation events still select authored music_type2578615350 and the existing cue switches (E:146,180; I object933909186; report28).

But the parent root is changed. In MP prologue root287204113, original rules4/12 change destination133462974 from SameTime(entry1) to EntryMarker(entry0); NML root976763369 has analogous changes in rules6/77/92. Native fades for those specific rules remain while return-entry behavior changes. S's held **global** game_state can also affect state-sensitive authored paths during overlap: decoded authored switches199043280,979178121,992398107,177877874 in NML and11423262,847555167 in Toussaint explicitly consume group766723505. This is a concrete dependency risk, not a newly observed mistimed cue (`A\authored-game-state-consumers.json`). Dedicated-branch records being exact supports asset/inner-graph preservation, not exact end-to-end timing.

Most importantly, S:490–524 writes `menu_volume_music = Audio.MusicVolume × contextPercent /100`. Optional `DialogLower` applies during dialog_scene/day-night and remains latched through a nested cutscene; `CutsceneLower` shares DialogVolume. This affects intentionally authored dialogue/cutscene score under Music too. It cannot identify “generic music during dialogue.” Defaults leave those toggles off; independent exploration-volume routing can suppress world dialogue, but the dialogue slider itself is not the required provenance-aware control. q001's separate route survives exploration mute, yet not a global dialogue mute.

### World-selected authored/thematic paths

No universal authored-intent signal is added. MP replaces many selections WMC deliberately preserves or leaves unresolved. Representative exact comparisons:

|Native object/role|MP evidence|WMC v4 comparison|
|---|---|---|
|Prologue589261176, `village_q505` noncombat theme|Converted playlist→scheduler switch; exploration attenuation/boost RTPCs3792101544/1055534981. J `/playlists/65` contains18 track alternatives. Reachable through flattened world, not dedicated authored branch.|D also mutes this probable exception through inherited State gain; **neither currently guarantees the desired treatment**. Report35's separate static-only exception fixture protects it technically, but is not shipped D or approval of intent.|
|NML world thematic candidates719937819-style routing, plus embassy/lovers/source-reuse cases in report07|J `/playlists/9,10,22,23,33` supplies replacement pools to original world paths. These are affected by exploration control, not protected by shared media with an authored cue.|WMC's pending/protected world decisions retain native behavior instead of treating every world route as disposable. Exact IDs/policies in `src/wwise/regions/nomansgrad-expanded-v2.json`.|
|Skellige448669660,159808125,883058634,112225352,899457248 and1014924209|All changed scheduler objects carry exploration RTPCs3792101544/1055534981 (`architecture-final.json`, those IDs).|WMC manifest classifies these native paths protected; static targets exclude them. No narrative names are needed to establish the technical difference.|
|Toussaint262644476,688195063,1005715432,952228266,817517040|Changed schedulers with exploration controls; J includes exceptional-location alternatives as well as general score.|WMC's five protected world selections remain native (`toussaint-v1.json`).|
|Wyzima361704319 world branch; Misty world regional selection; Spiral shared native music|MP provides separate exploration/combat pools, including J `/playlists/126–131`.|WMC deliberately ships none of these banks: thematic, unresolved, or shared-combat risks. More coverage in MP is not evidence of better authored preservation.|
|Native-silent NML selection|World492774600, location2877259110, exploration2582085496 selects scheduler861605735; variant0/no-pause playlist914259787 has positive-weight references to six added WEM sources instead of the verified silent original. J `/playlists/32` identifies their track roles (`A\native-silent-location-replacement.json`).|MP can select additional score where native/WMC permit silence. This is a verified reference/selection change, not a new audibility measurement.|

These classifications concern routing and policy, not a spoiler-bearing assertion about what a particular quest means. Soundtrack authorship cannot be inferred from reused source names. The selected original track can remain one of many choices without remaining guaranteed at the intended moment.

### Gwent, taverns, minigames and emitters

MP changes Gwent pools (J `/playlists/132,133`, ten alternatives each), and all four listed bard banks. Bard random-container prefix128625140, for example, adds bards RTPCs1463848559/1186105402 while retaining original native controls; seven other changed bard containers show the same category controls (`A\bard-control-prefixes.json`). Full random-container tails were **not** decoded by the new music-tail decoder; do not turn prefix evidence into a complete emitter-behavior certification.

Skellige shared object196982704 receives **tavern**, not exploration, volume controls2548973979/4294848228. Its ordinary dialogue/exploration, cutscene and minigames consumers still select that same object. Thus separating tavern gain is useful, but setting it to zero also affects that minigame use; there is no separate minigame-volume setting. Gwent has its own other choices. Bards are actual emitter banks; world tavern score is a distinct mechanism. WMC intentionally leaves mixed-use playlists and these emitters unchanged. Neither approach has a verified universal “all diegetic music” classifier.

## Settings, editor, persistence and operational quality

|Control|Actual mechanism / scope|Evidence|
|---|---|---|
|Exploration, combat, Gwent, bards, tavern volume|Five independent0–200 inputs; attenuation/boost RTPC pair per kind;0 exploration additionally chooses looping-silence profile,0 combat selects mute switch. Existing Music master remains above regional score.|S:106–201; X; decoded curves on589261176,970815018 and bard128625140. Raw scaled curve endpoints are not asserted to be−200dB or mathematical zero.|
|Dialogue/cutscene/main-menu/manual reduction|Global Music parameter; dialog/cutscene share percentage. Manual toggle uses minimum of applicable reductions.1s reduction/1.5s restoration. MainMenuVolume separately selects percentage of normal Music option.|S:490–550; X/CFG. Does not save a replacement Audio.MusicVolume.|
|Horse/boat/underwater|Priority underwater→boat→horse context percent, multiplied into exploration/combat/tavern gains,2s fade; no Gwent/bard factor.|S:143–172. A volume change is not a musical entrance decision.|
|Pause chance/duration|Discrete scheduler switches, not continuous volume; six internal chance profiles including mute, four length sets.|S:176–201, decoded24 profiles.|
|Skip|Next exploration/combat variant; disjoint first groups then ordinary weighted cycle; exploration skip temporarily releases teleport-switch2 after1.5s.|S:32–98,394–414. Gwent/bard editor pools lack first-variant groups; do not promise a universal skip/restart button. No independent “resume prior position” control.|
|Track/source filtering|Editor0–300% weights,5% steps; alternates default0; normal tracks100 relative to built weights. Source toggles adjust every matching track. Nonempty-pool validation or supported silent substitution.|H:132–150,240–410,460–546; J exact pool IDs/field offsets. Vanilla-only filtering does not recover native graph.|
|Location entry policy|Per-playlist immediate/deferred checkbox rewrites selected transition sync/fade fields; not merely a gain setting.|H:240–253,514–518; J `/zones/rules`, keep/cut triples above.|
|Settings persistence|In-game config wrapper with defaults/migration; editor saves one JSON document of weights/cut choices, with restore-after-update banner. No named preset library in shipped UI.|S:451–467,592–620; H:152–195,520–546; B:211–214,432–487.|

J contains **138 editor playlist entries**,2,187 track placements and309 distinct(source,name) labels. There are35 distinct labels under Vanilla and274 under other sources. These are metadata labels, not an independently established count of compositions. Actual additional media is275 WEM sources; all are referenced by the modified bank source set, with none missing from the supplied pack. Native-source set875→MP1,150; all275 additions match pack IDs. Do not substitute the public description's older playlist/track counts for these facts (`A\media-reference-closure.json`).

S:207–229 wraps SetDefaultGameState: checks tail/teleport deadlines whenever invoked, context every0.25s and configuration every1s. Hooks also cover area initialization, same-world fast travel, player input, menu open/close/config events and focus return. Area initialization redraws exploration/combat starts before native area playback; local travel enters silence until observed loading/fade ends or a5s fallback, then restarts a random exploration piece (S:384–449). Clock-reset guards are present. These are thoughtful load/skip mitigations, not demonstrated robustness across every save/scene/mod combination.

Current installed source has the relevant sound-system methods (V:156,240,279,557), `game/commonMapManager.ws:690`, and GUI callbacks `game/gui/main_menu/ingameMenu.ws:1859` / `game/gui/menus/menuBase.ws:473`. That supports hook-name compatibility, **not compilation or mod-order proof**; native callbacks are events and the shipped script uses annotations. No script compiler/game was launched. Wrappers can coexist or conflict depending on other mods' transformations, and the partially reimplemented native state method increases maintenance exposure relative to WMC's script-free v4.

B:201–487 statically contains a loopback-only TCP server on a random port, audio-preview subprocess calls to bundled vgmstream, `/peek`, and `/apply`. Apply checks game process/cache size/stored header checksum, writes supplied2/4-byte fields directly into the installed bank cache, and saves `Documents\The Witcher 3\musicplus_playlists.json`. It is **an offline bank patch editor**, not a Wwise generator or runtime scheduler. Size/header checksum checking is not independent per-record semantic validation. The key installer backs up then edits input.xml/input.settings; common pack code can strip old bank-index entries from a legacy combined cache. The uninstaller removes bindings/settings/mod files. None was run. These are explicit side effects to review before any separate execution authorization; this report is not an executable-security audit.

Performance inference: MP's501,989 total HIRC records/84.7MB bank cache plus931MB media are much larger than WMC v4's3.1MB five-bank cache. This suggests higher bank-object/memory/loading costs, **not a measured FPS regression**. Wwise schedules tracks natively; script polling is bounded but adds work/hooks that WMC v4 lacks. No CPU, memory or disk-stream benchmark was performed.

## B. Side-by-side architecture

|Aspect|Native|WMC v4|Music Plus3.3|Desired future WMC (proposal)|
|---|---|---|---|---|
|Exploration|Regional authored interactive score, including some silence|Reviewed generic playlists−200dB; D also ancestor State policy; ambiguous/shared paths remain|Weighted original+added whole-piece pools, selectable rests/category gain; some native-silent contexts gain music|Minimal remains baseline; opt-in sparse/native-only mode and eventually justified entrances|
|Ordinary dialogue|World or explicit authored event depending provenance|Generic suppression; dedicated authored untouched; D world-exception gap acknowledged|World follows exploration/tavern controls; optional dialogue slider also lowers authored Music|Provenance-aware control, no global dialogue mute|
|Combat|Native intro/body/intensity/outro and synchronization|Native graph/fades/RTPCs retained; measured offline; White Orchard retail success|Randomized bodies/new entry/return rules,4s hold; some native dynamic layers retained, native transitions not restored by settings|Retain native composition/response; interrupts optional rests safely|
|Authored dedicated score|Explicit events/music_type|Original branch/event/parent routing retained|Branch records/events exact; parent rules and global state/volume behavior differ|Protect cue selection, gain **and** entrance/return timing|
|Authored world score|Mixed with background routing|Conservative reviewed exceptions; not complete|Many thematic paths enter exploration scheduler/gain|Explicit reviewed origin-based exceptions; uncertainty stays native|
|Gwent/diegetic|Native choices/emitter routing|Preserved mixed paths and emitters|Expanded Gwent/bard pools; separate controls but shared minigame caveat|Native default; independent optional policy only after isolation|
|Transitions|Per-region beat/phrase/fade rules|Existing transitions retained, static mute prevents bleed|Exit-marker carryover plus new immediate/fixed crossfades|Retain native rules except narrowly proved rest-specific behavior|
|Sparsity|Existing score-specific silences|Continuous generic suppression, no rest scheduler|Real whole-track/gap scheduling; not salience-driven punctuation|Substantial space, deliberate presence; exact triggers/defaults unapproved|
|Controls|Music master|Master only; no WMC sliders|Broad in-game gain/context controls and offline weighted editor|Optional Minimal/Sparse/Low-background controls, implementation deferred|

## C–D. Mechanism-level merits and adoption options

**MP demonstrably does more today:** editable weighted pools, anti-repeat/start variants, real track-boundary rests, user-selectable location carryover, per-category gains, movement-related gain factors, load/skip handling and an editor that persists customization. Those are useful engineering mechanisms. More tracks, added score in silent locations, full-piece randomization and replacing combat bridges are different musical design choices, not objective improvements for this user.

**WMC demonstrably does better for the specified preservation policy:** minimal reviewed HIRC edits; unchanged media, native combat intros/outros/intensity/transitions; conservative handling of thematic/shared world paths; no script hooks or editor mutation of deployed files. Existing paired playback proves specific behaviors. It is not a sparse/adaptive engine and has no comparable controls; D's inherited world-exception attenuation is an acknowledged weakness, not a solved shipped feature.

**Neither currently supplies the whole desired experience:** a verified meaningful-context entrance policy, composed short punctuation vocabulary, demonstrated dramatic salience, or perfect authored-intent classification. Do not attribute precise algorithms to the two inspirational games from this audit. Random gaps can reduce repetition but cannot make an arbitrary long piece appropriate to a particular moment.

|Mechanism / choice|Value, effort and dependencies|Decision|
|---|---|---|
|Replace WMC entirely with MP|Immediately obtains many controls and track rotation; trades away unchanged native combat/transition behavior and conservative world-cue protection. Would require separately authorized installation/compilation/listening.|Reject as current default; viable if the user deliberately relaxes those preservation priorities.|
|MP plus WMC simultaneously|All five WMC regional bank names/IDs overlap MP; full banks compete, not merge. MP-script-only with WMC banks lacks its custom events/scheduler/RTPC consumers but retains script state changes.|Reject ordinary co-installation. Cache priority does not create a hybrid.|
|Independent category RTPC curves on approved generic objects|Potentially modest local-bank change with settings adapter; MP demonstrates references without shipped Init/global buses. Needs isolated authoring and actual API/native-Init validation; cannot assume a custom RTPC requires rebuilding Init solely from old mixer reports.|Worth a bounded future proof; preserve native Music master and avoid shared/authored ancestry. No new slider code in this task.|
|Native-only track-boundary rest scheduler|Moderate regional authoring/verification work; optional scheduler replaces only generic playlist internals. Must preserve native combat entry/outro, immediate rest interruption, original cue origin and carryover behavior. New scheduler objects need explicit gates rather than weakening static-only checks.|Best first independent hybrid prototype.|
|Weighted editor/source packs|High graph/UI/version-migration/testing cost; added audio has permission/distribution constraints. Native-only choices avoid adopting MP assets. Its precompiled-copy strategy explains graph growth; not the only possible scheduler design.|Defer until pacing earns its complexity. Do not copy editor or bank-patching implementation.|
|Location carryover / anti-repeat|Good principle, moderate testing: track ending versus place identity, silence exit and authored interruption need explicit policy. Do not simply wait indefinitely in every silent location.|Reuse idea independently and test representative transitions.|
|MP combat rewrite/fixed tail|Conflicts with native intro/outro timing and state-sensitive cue protection; no independent off switch in shipped controls.|Do not adopt.|
|Global dialogue duck / blanket movement factors|Easy to implement, but dialogue affects authored music and context percentage is not an entrance policy.|Reject global dialogue mechanism; defer movement factors pending user policy.|
|Meaningful-context punctuation|Requires approved context vocabulary, reliable signals and musically suitable phrases/markers/assets. It is not delivered by either current bank design.|Separate longer-term work after the small cadence/interrupt proof; no speculative quest hooks now.|

An independent hybrid would change the **future optional generic-playlist architecture**, not require replacing native combat, global Music buses or shipping MP's audio. Keep v4 Minimal and its exact rollback banks separately available. Story/world exceptions must be explicit; a playlist called exploration is not sufficient authorization. Production source/bank gates would need new bounded structural specifications for added scheduler nodes; current Volume-only allowlists should continue rejecting them until then.

The [author's published permissions](https://www.nexusmods.com/witcher3/mods/13818) require permission for modification/asset reuse and forbid unauthorized redistribution. This audit copies no MP implementation into WMC. Independently designing the general scheduling/control ideas is distinct from reusing their code, banks or packaged recordings. Execution of the editor or a MP listening test would need a separate request; neither is necessary to choose the preservation-first direction now.

## E–F. Concrete next step and falsifying test

**Next authorized development task to propose: one isolated, native-only White Orchard sparse-playlist fixture**, alongside retained D, with no UI, added audio, retail deployment or global mixer. One already approved generic selection should play its native musical material to the existing exit marker, enter a bounded rest, and permit native combat/authored selectors to interrupt. Keep original combat intro/body/intensity/outro, dedicated authored paths and Music master exact. Use the report35 authored-isolation fixture as a protected-world control, without changing shipped D or deciding q505's musical intent.

Measure ordinary progression, location/day-night change during a piece **and** rest, combat during each rest phase, return through the complete native outro, an authored interruption, and the normal Music master. The narrow question is whether **sparse cadence can be isolated to generic playback while native entry/return grammar remains intact**. Compare native/D controls using existing selector/profiler/PCM infrastructure. This is a technical discrimination experiment, not approval of MP's exact probabilities or a new user default. If rests require disabling native combat transitions or expose generic bleed, reject that construction rather than promote it to production.

Do not begin with all-region generation, an external editor, new soundtrack packs, broad state interception or dozens of context triggers. Once the isolated proof passes, choose sparse pacing/eligibility rules with the user; meaningful-context punctuation still needs a separately specified and validated signal/phrase experiment. There is no evidence-based reason to stop WMC entirely, and no need to re-run solved Project ID/licence/cooker work.

## Verification, preservation and reproducibility

Command (existing extracted inputs; writes fresh ignored evidence):

```powershell
python tools/music_plus_audit.py --main build/music-plus-audit/main --banks build/music-plus-audit/banks --native 'L:/Games/Steam/steamapps/common/The Witcher 3 REDkit/r4data/soundbanks/Pc' --source 'L:/Games/Steam/steamapps/common/The Witcher 3 REDkit/assets/w3_audio' --output build/music-plus-audit/architecture-final.json --profile-bank music_nomansgrad.bnk --profile-target 719937819
python -m unittest discover -s tools -p 'test_*.py'
```

The audit refuses an existing output path.13 new synthetic tests exercise valid segment/switch/playlist/track layouts, complete truncation, bad tree/playlist closure, unsupported versions/automation, trailing bytes, nonfinite duration and strict switch-action decoding. **170 tests pass**, including all existing157. Independent cross-checking also matches the production prefix decoder for all1,301 supported native switch/playlist records; the new inspector separately decodes the eight listener-relative regional roots that the production edit gate intentionally rejects (`A\decoder-crosscheck.json`). Expected failing-gate JSON printed by negative regression cases is not a failed test. New inspection code never writes a bank or relaxes production validation.

Ignored local evidence includes exact archive/extracted inventories, cache and payload hashes, `architecture-final.json`,24 decoded pause profiles, conservative playback closure, parent-rule differences, bard prefix controls and media-reference closure. Known limits: no new MP compilation/audition, no exhaustive runtime event/state sequencing proof, no full bard-tail decoder and no performance benchmark. Claims about naturalness remain design inferences pending listening; static choices/record equality are observed facts.

Original MP ZIPs, WMC v2/v3/v4 ZIPs and the five accepted WMC bank payloads are rehashed after inspection; exact results remain in `A\preservation.json`. No generated Wwise project, licence, source audio, bank/cache/ZIP, third-party script or private profile file enters Git. No installation, Vortex, save/profile, licence or playback command was issued. This report supersedes report52's archive-unavailable boundary; it does not change WMC's current runtime behavior.
