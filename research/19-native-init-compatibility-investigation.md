# Native Init compatibility investigation — 2026-10-11

## Findings and decision

**No native-Init load compatibility is certified, and no modified candidate was generated.** The licensed baseline from [report18](18-licensed-baseline-results.md) remains useful: its regional HIRC/media are native-exact, with only BKHD differences. This investigation establishes that the three missing native StateGroups have no corresponding definitions in the complete supplied authoring project. Every active source Bus, AuxBus and AudioDevice in the retained full-project object inventory is present in generated Init. The other ten native IDs cannot currently be mapped to active source definitions.

Consequently, **selective generation has not been established as the cause of those omissions**. Source/build provenance or internal generation remains unresolved. A blanket full-bank rebuild is not justified. The most efficient next experiment is a **load-only comparison of the existing unmodified licensed regional bank with shipped native Init**, through a verified independent loader, before another authoring change. No installed resource, reference mod, save, licence or binary header was changed; no new banks or runtime harness were generated/executed.

## Evidence and reviewed implementation

These are exact, explicitly machine-local evidence paths. Generated and third-party assets remain ignored.

| Alias | Absolute path |
|---|---|
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| R | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc` |
| T | `L:\Programs\Wwise_2023.1.19.8928\Authoring` |
| P | `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline` |
| B | `C:\Dev\witcher-music-control\build\licensed-white-orchard\baseline-banks` |
| V | `C:\Dev\witcher-music-control\build\licensed-white-orchard-verification` |
| E | `C:\Dev\witcher-music-control\build\licensed-white-orchard-compatibility-research` |
| F | `C:\Dev\witcher-music-control\build\white-orchard-followup` |

Relevant reports: 01/06 for reference/cache contents; 11 for isolated native cooker/bootstrap; 12 for global-object enumeration and entitlement; 13–15 for Stage1 source/serialization/fades; 16–18 for licensed baseline gates/results. Reviewed code: `tools/white_orchard_prepare.py:prepare/sanitize_project`, `white_orchard_wwise.py:generate`, `white_orchard_build_gate.py:source_control/compare_pair/baseline`, `white_orchard_compare.py:read_bank/difference`, `white_orchard_state_bank_audit.py:header/native_groups/state_chunk`, `white_orchard_state_volume_author.py:author/semantic`, `white_orchard_cooker.py:prepare/execute/verify_cache` (all under `C:\Dev\witcher-music-control\tools`). No implementation or acceptance policy was changed.

New local audits: E/source-and-global-difference-audit.json, E/reference-bank-header-audit.json, E/project-bank-diagnostic-strings.json. The source audit rehashes all **1,556 installed inputs** in P/input-manifest.json: zero changes, all1,508 source WWUs present. It also corroborates every retained WAAPI inventory GUID against the current original XML. This uses no licence property or key. Reference banks/cache are read directly, not edited or redistributed.

## 1. What is known about dwProjectID

**Verified layout:** BKHD v150 payload offset16 is a 32-bit `dwProjectID`, separate from the name-derived bank ID and 16-byte bank hash. The pinned [wwiser parser](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/parser/wparser.py#L2990), `CAkBankMgr__ProcessBankHeader`, lines3037–3047, reads that field. Its parser does not implement Wwise authoring's allocation algorithm or the Witcher loader's project-identity check. Calling the parser's function `CAkBankMgr` does not turn it into proprietary runtime source.

**Installed definitions:** T/Data/Schemas/WAAPI/ak.wwise.core.getProjectInfo.json:35–38 describes `id` as a **GUID**, not this numeric header field. T/Data/Schemas/WAAPI/ak.wwise.cli.generateSoundbank.json:24–38 documents licence inputs and :55–64 selection of one or several banks; none of those definitions exposes a `dwProjectID` override or derivation. A targeted search of installed Data XML/JSON/header/script definitions found no ProjectID-to-BKHD algorithm. No licence override was used or inspected. The matching Wwise installation contains Authoring/images, not SDK headers, libraries or Bank Manager source; the REDkit search found no matching AK SDK headers/Bank Manager source. T/x64/Release/bin/WwiseSoundEngine.dll exists, but a DLL alone is not a documented standalone SDK interface.

**Official documentation:** the [Launcher Projects guide](https://www.audiokinetic.com/en/library/edge/?id=projects&source=InstallGuide) describes a numeric applied licence ID. It does **not** specify the generator's assignment to BKHD. The [Audiokinetic REDkit setup guide](https://www.audiokinetic.com/rendertron/render/https%3A/www.audiokinetic.com/ko/blog/the-witcher-3-redkit-tutorial) documents the dedicated modding entitlement and application to the supplied game project, but supplies no numeric header compatibility rule. Its older tool-version setup must not supersede the matching local2023.1.19 build.

**Independent local observation:** FMC's loose Init and all eight cache banks also contain **17637**, despite being older v140 banks. This strongly supports treating17637 as shared modding/build provenance rather than assuming a unique ID for this user's project. It still does not prove exactly how2023.1.19 selects it. Trial0 → licensed17637 is corroborating observation, **not proof of the generation algorithm**. No licence decoding, key access, header patch or licensing experiment was attempted.

**Still unanswered:** authoritative allocation/derivation of this exact numeric field, whether the dedicated entitlement intentionally uses17637 for REDkit, and whether the shipped runtime compares it with39. A lawful matching SDK/runtime implementation or explicit Audiokinetic/CDPR confirmation is needed. No public generator/Bank Manager implementation establishing those rules was identified. Do not replace this gap with inference from licence approval.

## 2. REDkit workflow and actual runtime acceptance

The [official CDPR sound workflow](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/6327994/HOW-TO%253A%2BImplement%2Bsounds%2Band%2Buse%2BWwise) documents authoring and bringing banks into REDkit, including scene soundbank dependencies. It supports the existence of a legitimate mod-bank workflow, but does not document a17637/39 exception or prove acceptance of this replacement bank. Available documentation predates the matching current bank/tool build in places.

The [official LoadBank contract](https://www.audiokinetic.com/en/public-library/2024.1.5_8803/?id=namespace_a_k_1_1_sound_engine_a496b9917fe035f301bcff0accd61f80f.html&source=SDK) requires Init first and subsequent banks from the same project, plus registered codecs/plugins. This is an SDK contract, not an identified instruction in Witcher's shipped loader or an explicit assertion that the numeric39/17637 pair is rejected. It is insufficient to approve the pair and insufficient to claim a measured rejection. Matching the retained source project GUID likewise does not prove what this numeric field does.

E/project-bank-diagnostic-strings.json records a narrow read-only ASCII/UTF16 diagnostic search of T/x64/Release/bin/WwiseSoundEngine.dll, WwiseConsole.exe and `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe`. It found no explicit project-mismatch diagnostic/algorithm, only the unrelated media-transferred-from-authoring message. Absence of a string is **not** evidence of absence of a runtime check. No disassembly, patched executable, leaked SDK or injected runtime was used.

## 3. Native globals versus supplied source

### StateGroups: not missing through selective stripping

W/States/global_states.wwu defines only:

| Group | Numeric name hash | Source line |
|---|---:|---:|
| game_state | 766723505 | 6 |
| mixing_state | 2438777053 | 175 |
| gamepad_state | 2861987792 | 203 |

A recursive examination of every original WWU finds exactly **three StateGroup definitions**, matching generated Init. Native groups967256167,1975690400,3317025587 have **no named source match**. The lowercase FNV-1 method is corroborated by actual native/metadata game_state/Music IDs and the pinned [wwiser Fnv implementation](https://github.com/bnnm/wwiser/blob/08e937b649bc7007c234bbd59e34a41d5eef3b38/wwiser/wfnv.py#L48). This is not a guessed name recovery for those three IDs.

All three retained groups, default times and complete custom transition arrays are native-exact, including game's43 game_state transitions. STMG State sections end at native674 / generated638: missing empty groups account for **36 bytes** of the393-byte total difference. The remaining tail is native2,504 / generated2,147 bytes, another **357 bytes**; it is not decoded/certified equivalent. These latter differences cannot be explained by deleting just three groups.

### Ten HIRC objects: active source mapping absent

F/full-global-objects.json is the retained complete-project WAAPI inventory:56 Bus,41 AuxBus,4 AudioDevice,357 Effect objects. Every inventoried GUID remains in original XML; every inventoried Bus/AuxBus/AudioDevice ID is serialized in the licensed Init. Native has64 Bus/42 AuxBus/4 devices/40 type17 effects/one type16 effect; generated has56/41/4/39/one. Of357 inventoried effects,40 serialize and317 do not: unused-effect/dependency selection does occur, but none of the missing native IDs maps to that full inventory.

| Missing native ID | Kind | Body bytes | Narrow decoded native parent, where verified |
|---:|---|---:|---|
| 542827472 | Bus8 | 394 | Ambiences1017660616 |
| 890724639 | Effect17 | 201 | Not decoded |
| 1411735597 | Bus8 | 352 | Ambiences1017660616 |
| 1505802601 | Bus8 | 210 | Immerse2118946425 |
| 2041642433 | Bus8 | 389 | Ambiences1017660616 |
| 2320575434 | Bus8 | 62 | ENVIRONMENTAL Bus3600197733 |
| 3803860308 | Bus8 | 222 | Immerse2118946425 |
| 4004099879 | Bus8 | 329 | Monsters3858746980 |
| 4189995869 | AuxBus18 | 49 | Not decoded |
| 4253138028 | Bus8 | 457 | Ambiences1017660616 |

Parent reads use only the leading u32 `OverrideBusId` for type8, corroborated by the pinned parser's `CAkBus__SetInitialValues`:1759. Parent names/IDs come from F's source inventory; routing beyond that field is not guessed. No missing Bus's immediate parent is the Music bus. This does not rule out indirect effect/ducking/global relationships or establish that these objects are dispensable.

**Preset distinction:** raw XML contains42 AuxBus and368 Effect tags. The extra AuxBus is a **template** `Room Auxiliary Bus` in W/Presets/Factory Spatial Audio.wwu, not an active hierarchy object; eleven additional effects are in Presets. None of the named XML tags anywhere hashes to the missing IDs. Preset GUIDs/custom internal IDs are not necessarily name hashes; no claim is made that this alone identifies or excludes an internal/template-derived effect. Names for the ten native objects and their creation history remain unresolved.

**Conclusion:** original supplied source lacks an active-object mapping for these ten IDs and explicit definitions for the three additional native groups. Source snapshot differences are a better-supported explanation than selective omission of existing named globals. Whether native used extra source definitions, platform/build-generated objects, an internal engine pipeline or different preprocessing is **unverified**. Do not label them all internally generated or licensing side effects. Native Init already provides them in the intended Stage1 runtime.

## 4. Broader generation decision

**No broader-bank control performed.** All source buses/devices already serialize, and no source bank can be traced to the absent StateGroup definitions. There is no identified missing source object's inclusion edge to activate by adding a bank. Thus generating another region or the multi-gigabyte set would currently be an untargeted provenance search, not the smallest discriminating experiment; it would not establish39/17637 loading behavior. T's CLI schema allows multiple selected bank names, so output scope is controllable when a justified target is found.

A useful future control requires either (a) a recovered missing-object GUID/source definition with a concrete inclusion path, or (b) documented engine/generator behavior that instantiates one of these IDs when a particular bank is selected. Then select music_prologue plus **one** triggering bank into fresh ignored output with unchanged hierarchy/licensing, preserve logs/results, and compare only Init/BKHD/object sets first. Stop rather than expand if the target fails to appear. No media-pruning workaround or licence copying is justified. Full generated-Init reproduction is a separate provenance task from the Stage1 load test.

## 5. Reference evidence boundary

E/reference-bank-header-audit.json reads FMC's CS3W v2 table directly and checks payload bounds/header fields:

| Reference | Actual bank evidence | Native Init retained? |
|---|---|---|
| Only Story Music, all four variants | Script-only; no BNK/cache in extracted trees | No replacement supplied; no generated-bank identity experiment |
| Less Is More | Script/XML/localized text; no BNK/cache | No replacement supplied; no generated-bank identity experiment |
| FMC Audio Remaster | Loose Init plus8 cached banks, all v140/ProjectID17637 | **No**: loose/cache Init payloads match each other and replace native Init |

FMC cache banks are combat, generic_movement, global_doors, grunt_vo_geralt, gui, init, vo_definitions, work_voiceovers. Its Init SHA256 is `eb79f94d4e7bfa63b1752b821a1b32b606faaf9a18dda11227275b41ad6475cd`; native current Init is v150/ProjectID39. The reference can show a real alternative-ID authoring footprint, but supplies no verified mixed39/17637 load, current2023.1.19 acceptance, or preservation of native globals. No reference in this supplied set proves regional-only generated-bank compatibility. No mod was installed for testing.

## 6. Stage1 requirement and next experiment

Stage1 needs **native Init plus one modified regional bank** with existing Music inheritance/events/quest routing/media preserved and the verified world-only inline State Voice Volume change. It does not need to ship B/Init or reproduce its missing global definitions. Report15's structural experiment identifies only existing global group766723505 as the new association; report18's unmodified HIRC equality preserves the baseline reference graph. Those establish dependency evidence, not actual loader acceptance or final native-fade behavior.

The strict report17 workflow deliberately checks more than this minimal runtime requirement. Its generated-Init equality failure is not by itself proof that Stage1 cannot work; its numeric-identity failure remains unresolved. Keep the failed report intact. Do not revise the gate to pass by discarding those checks before an explicit, supported compatibility policy exists.

**Recommended independent load-only matrix, using existing banks without patches or new generation:**

1. In a fresh process, load shipped native Init39 then native music_prologue39 (control).
2. In another fresh process, load the same native Init39 then B/music_prologue17637 (test).
3. In a third, load B/Init17637 then B/music_prologue17637 (positive generated-pair control; disposable Init used only in the isolated harness).

Record actual synchronous LoadBank results or completion callback results, bank IDs, version/plugin registration diagnostics and confirmed file SHA256s. Resolve reads exclusively to the test root; disable writes/streaming outside it. Duplicate bank IDs require fresh engines, not sequential native/generated loads. Any failure needs exact failure attribution: Init initialization, missing codec/plugin, wrong version, numeric project mismatch, file I/O or dependency failure. A pass establishes **load acceptance of the unmodified baseline**, not playback/fade or future State serialization acceptance. Test the modified bank only in a separately authorized later task.

**Preferred harness:** a legitimate matching2023.1.19 native SDK host with declared plugin registration and explicit file/memory LoadBank APIs, independent of Wwise authoring. No such ready host/headers/libraries were found in the inspected installation. Do not invent a callable ABI for WwiseSoundEngine.dll, download/install another runtime automatically, or run untrusted reconstructed SDK code. Ask Audiokinetic/CDPR for the supported REDkit/native-Init test host or SDK mechanism and the numeric-ID policy; no key or licensed project needs to accompany that request.

**Existing REDkit alternative to investigate next:** the isolated `-root` bootstrap from `tools/white_orchard_cooker.py:prepare` could host a native-engine bank-load diagnostic if a supported commandlet or bank-result instrumentation is established. Require proof that it actually initializes AK and calls LoadBank on the nominated payloads. Existing `cooksounds`/`splitcache` success only proves serialization/cache-reader acceptance; neither is this load test. A zero-exit `wcc_lite help` likewise does not expose per-bank results. No verified load-only commandlet is currently identified, so this remains a proposed route, not a completed runtime harness.

T/Data/Schemas/WAAPI/ak.soundengine.loadBank.json:16–27 accepts a project bank name/GUID/ShortID, no arbitrary file pointer/path argument or raw AKRESULT. It cannot be assumed to load an independently supplied native Init without authoring-managed globals. Authoring audition remains outside this acceptance test. A REDkit editor scene test would additionally need an isolated editor project and verified asset/Init resolution; the official scene `soundbankDependency` workflow does not by itself ensure isolation or retain-native-Init semantics.

**Efficient next action:** establish this loader interface/numeric-ID policy with Audiokinetic/CDPR, then run the above **existing-bank** matrix. Do not generate a candidate, cook a release package, replace Init or widen regions until that evidence is available. The earlier licence barriers are resolved; the remaining question is source/build identity and actual native-Init load behavior.
