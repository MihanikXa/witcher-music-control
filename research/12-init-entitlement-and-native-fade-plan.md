# Init entitlement and production native-fade plan — 2026-10-11

## Decision and scope

No native-compatible deployment Init is certified. The legitimate next step is to request the dedicated **Witcher 3 - REDKit Modding** entitlement, with Windows / Wwise **2023.1.19.8928** and the native plug-ins covered. A paid unrestricted commercial licence has **not** been demonstrated necessary. Request/approval/application is a separate user action: nothing was activated, purchased, installed or submitted here.

This report supplements [10](10-white-orchard-prototype-results.md) and [11](11-white-orchard-blocker-resolution.md). It preserves their recordings, failed controls and comparisons. No game, REDkit, installed Wwise, reference mod, save or depot was modified. No source mixer or settings implementation was changed; the production conversion below is a proposal.

## Evidence locations

These aliases designate exact, machine-local evidence, not distributable assets.

| Alias | Absolute path |
|---|---|
| W | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio` |
| R | `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc` |
| T | `L:\Programs\Wwise_2023.1.19.8928\Authoring` |
| F | `C:\Dev\witcher-music-control\build\white-orchard-followup` |
| E | `C:\Dev\witcher-music-control\build\white-orchard-init-entitlement` |
| Audit helper | `C:\Dev\witcher-music-control\tools\white_orchard_init_audit.py`, `run` / `exclude_leaves` |

## 1. Effective local entitlement

**Observed:** W/w3_audio.wproj has an empty `LicenseKey` property. The fresh isolated complete copy has the same empty property. E/local-license-status.json records **only property name and nonempty=False**, without a key, identity or account data. No Launcher credential cache, customer account, activation endpoint or unrelated licence was inspected. An empty project field cannot establish whether the user has an approved but unapplied entitlement online.

**Observed effective generation status:** F/full-retained-banks/generation.log reports trial **26,218 / 200** and six `HomeCinema` Mastering Suite licence errors. E's fresh controls provide current corroboration below. No currently effective unrestricted or Mastering Suite evaluation entitlement is demonstrated for this project. The logs do not distinguish never requested, unapplied, expired or version/platform-incompatible entitlements. Do not invent an expiry date or infer eligibility from installed plug-in DLLs.

The local generator error specifically directs the user to a **free** Mastering Suite licence. The plug-in definition is W/Effects/Factory Mastering Suite.wwu, `HomeCinema`, GUID `{F9951DC8-664E-4B07-81CF-61716236F00A}`, CompanyID 0, PluginID 186, PluginType 3. W/Audio Devices/Default Work Unit.wwu:51 and :112 reference it from `System` and `System_Immerse_on`. Native Init contains its ShareSet ID **4131355637**. Removing or disabling it would change native output processing rather than solve entitlement.

## 2. Legitimate options and costs

| Route | Official support | Assessment |
|---|---|---|
| Dedicated REDkit modding entitlement | Audiokinetic's setup guide directs users to Customer Profile → Wwise Modding Projects → **Witcher 3 - REDKit Modding** → request access; then approval and project licence application. It describes generating all project assets and plug-ins. | Preferred, specific to the supplied game project. Confirm current 2023.1/Windows coverage and native plug-ins with Audiokinetic if the offered key is older. No account request was made. |
| Free unrestricted non-commercial project licence | Audiokinetic's licensing FAQ explicitly offers this for projects exceeding the free trial's 200-media limit. | A legitimate fallback request for this non-commercial mod; register its actual purpose, not a fictional new game. Plug-in coverage must be checked separately. |
| Mastering Suite entitlement | Generator provides a free-licence request URL; Audiokinetic's price table lists Mastering Suite as free across game tiers. | Zero advertised plug-in price does not mean activation-free. Ask for coverage on this project and tool version. |
| Evaluation entitlement | Audiokinetic describes requesting premium plug-in evaluation for a registered/approved project via Developer Relations; evaluation expiry can exclude plug-ins from built banks. | Possible temporary offline proof route if granted; not a presumed perpetual publishing licence. No active evaluation or its duration is locally established. |
| Trial with genuinely reduced media | Supported bank filters and node Inclusion controls were tested below. | Does not remove the independent Mastering Suite requirement; Init equivalence remains mandatory. |

Sources: [Audiokinetic REDkit setup guide, “Getting the Wwise License”](https://www.audiokinetic.com/en/blog/the-witcher-3-redkit-tutorial/), [licensing FAQ: trial / non-commercial / plug-in evaluation](https://www.audiokinetic.com/en/products/licensing/?asia_=%2F), [official Mastering Suite price table](https://www.audiokinetic.com/pricing/for-games/?asia=). Checked 2026-10-11 through indexed official text; direct page opens sometimes returned 403. These support a legitimate no-commercial-purchase route, **not an already granted entitlement**. Recommended first expenditure: **$0 licence request**, subject to Audiokinetic approval and confirmed coverage. No reason to buy a Pro/Platinum licence has been established.

**Version caution:** the 2025 Audiokinetic guide names Wwise 2021.1.7 for the older game. Use its entitlement process, not its version/depot/conversion instructions. [Current official REDkit changelog](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/12058625/Changelog) requires Wwise 2023 with Mastering Suite and Motion; installed W/w3_audio.wproj:2 confirms 2023.1.19/build 8928/schema119. [CDPR's sound workflow](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/6327994/HOW-TO%253A%2BImplement%2Bsounds%2Band%2Buse%2BWwise) directs modders to a Wwise licence and `_Mod`/selected-bank publishing. Its older “250” figure is superseded here by the actual **200** limit. `_Mod` publishing does not prove an additive global-Init mechanism.

## 3. What may be omitted, and what must remain

[Official SDK bank documentation](https://www.audiokinetic.com/library/edge/?id=soundengine_banks_general.html&source=SDK) separates Init's bus hierarchy, game syncs, RTPCs and bus effects from regional banks' events, playable structures and media. Audio Devices are also automatically included in Init ([official Audio tab documentation](https://www.audiokinetic.com/en/public-library/2024.1.5_8803/?id=audio_tab&source=Help)). Loading requires registered source/effect/codec plug-ins and compatible project globals. Those documentation versions explain roles; the actual installed schema and native banks remain technical authority.

| Data | Treatment for this pilot | Verification required |
|---|---|---|
| Native bus/AuxBus hierarchy, Audio Devices, attached effects/ShareSets, IDs, routing and references | Keep; including unused-looking native output branches. | Every native HIRC record retained and unchanged, plus understood generated/internal objects. |
| States/Switches, group defaults/transitions, RTPC definitions/defaults/curves, ENVS and platform data | Keep all native global data. | Compare STMG/ENVS/PLAT and relevant HIRC bodies; preserve native Music curve. |
| Source/effect/codec/device plug-in usage and Init registration data | Keep complete dependency closure, not only visible bus definitions. | Native INIT entries and runtime availability retained. File-presence or matching names are insufficient. |
| Unselected regional events, source media and playable structures | Do not ship their regenerated banks. Their authoring definitions may still inform global dependency serialization. | Selected-bank generation already avoids outputting them; removing definitions cannot be presumed safe. |
| White Orchard media and quest/world structures | Preserve byte-equivalent regional content except the specified world routing. | DIDX/DATA and every non-world HIRC record unchanged; native streamed-media references retained. |
| Audio originals from other banks | Need not copy for the already attempted selected-bank control. | Missing originals alone did **not** reduce trial count; full control still counted 26,218. |

The native target R/Init.bnk is **32,840 bytes**, SHA-256 `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`, matching the previously extracted installed-game Init. Legacy reduced Init has eleven missing native records, nine rather than eighteen registrations and a smaller STMG. F/native-hirc-type-crosscheck.json identifies type8 Bus, type18 AuxBus, type21 AudioDevice. F/missing-native-source-map.json resolves only HomeCinema among those eleven. The other ten omissions remain a source/build-provenance or generation-dependency question, not proven licence side effects. Even a successful free entitlement would **not automatically clear that fidelity issue**.

## 4. Controlled media reduction

All controls use 1,508 complete work units, the same 47 distinct White Orchard originals, unchanged native object IDs and the matching Console. They select only Windows/SFX `music_prologue`; no licence override is supplied. Logs, command arrays, output/result records and input hashes remain under E.

### Bank-media filters: supported, but insufficient

`Audit.run` uses installed `T/Data/Schemas/WAAPI/ak.wwise.core.soundbank.getInclusions.json` and `...setInclusions.json`. The latter explicitly supports independent `events`, `structures`, `media` filters and includes an example omitting media. Through that API, the control removes **only `media`** from the inclusion entries of **738 unselected banks**; `music_prologue` is unchanged. All sources, events, structure inclusions, banks, globals and references remain present.

E/media-filter-control/media-filter-audit.json records before/after lists for all changes. Wwise saved 380 SoundBanks work units; **every non-SoundBanks work unit remains byte-identical**. E/media-filter-banks/generation.log still reports **26,218 / 200**, the six HomeCinema errors, and many `MediaNotFound` diagnostics for the now-unassigned unselected media. Exit **1**, **no banks**. Therefore independent media packaging flags do not reduce this build's trial count. They are not a valid generation recipe.

### Node Inclusion control

`Audit.exclude_leaves` uses the installed `WObjects.xml` Inclusion property (definition :50–52; Sound :5904–5905; MusicTrack :6117 and its Common_AudioNode base). It retains every object/source/reference/event/bank, but adds `Inclusion=False` to file-backed Sound/MusicTrack leaves outside the `music_prologue` subtree. Non-file source plug-ins are retained. E/leaf-inclusion-control/leaf-inclusion-audit.json records **41,429 excluded AudioFileSource instances**, **133 retained prologue instances** (47 distinct copied files; instances are not unique licensed-media count), previous Inclusion values, IDs and complete unchanged-global-work-unit hashes.

This is a supported exclusion experiment, **not** an assertion that disabled nodes preserve compiler global usage. Init comparison is required even if the media gate clears. No source file, custom effect, output device or vanilla bus is removed to silence an error.

**Observed:** E/leaf-inclusion-banks/generation.log has **no media-limit fatal error**, and emits only Init.bnk and music_prologue.bnk. It still reports six HomeCinema licence errors and exits **1**; the generator correctly rejects it. No exact new licensed-media count is printed, so report only that this control passed that gate. This proves a below-limit generation control is feasible without deleting native global definitions, **not** that its dependencies are native-complete.

E/leaf-bank-comparison.json compares the emitted banks to R and the original reduced baseline:

| Component | Native | Node-exclusion control | Meaning |
|---|---:|---:|---|
| Init bytes | 32,840 | 29,332 | SHA-256 `f0297a4166ac8618a0ea036bde0f8e3feb8e2eb554d2fa37a8bd7fbae55f3476`; rejected output. |
| HIRC payload bytes | 29,113 | 26,030 | Same eleven missing records as report10; no added records, no changed surviving record. HIRC equals the original reduced baseline. |
| STMG bytes | 3,178 | 2,785 | Equals original reduced baseline; native global differences remain unexplained. |
| INIT registration entries / bytes | 18 / 277 | 16 / 245 | Improved from old 9 / 129, but two required native registrations still absent. |
| ENVS / PLAT | Native | Byte-identical | No differences observed in these chunks. |
| music_prologue HIRC / DIDX / DATA | Native | Byte-identical | Only BKHD differs. No mixer was authored in this control. |

E/plugin-registration-comparison.json records the read-only native/control INIT entries. They parse completely as a count followed by repeated 32-bit plugin IDs and null-terminated names; the parser checks the final offset equals the chunk length. The only missing pairs are **12189699 / MasteringSuite** and **26804226 / AkMotion**; no extra registrations. Installed `T/x64/Release/bin/Plugins/AkMotionSource.xml:4` identifies CompanyID0, PluginID409 and EngineDllName `AkMotion`; source instances remain in W/Actor-Mixer Hierarchy/motion.wwu:43 onwards. Merely retaining those source objects did not ensure registration in the selected output. The four AudioDevice records still survive unchanged; this is not evidence that Motion source registration is dispensable.

All unrelated differences are accounted for at the **comparison** level: BKHD metadata, eleven absent HIRC objects, the non-equivalent STMG and two absent plug-in registrations; no other changed chunks/records. E/bkhd-differences.json records every changed 32-bit header word: payload offset16 is native39/control0 in both banks; offsets24/28/32/36 also differ. Their semantic meaning is not established here, so they are not certified harmless. HomeCinema omission is supported by the explicit licence errors; the ten remaining objects and STMG cannot yet be explained. The missing IDs/types are **542827472/8, 890724639/17, 1411735597/8, 1505802601/8, 2041642433/8, 2320575434/8, 3803860308/8, 4004099879/8, 4131355637/16, 4189995869/18, 4253138028/8**. Do not certify this control, equate all eleven with licensing, or splice their bytes from vanilla.

**Conclusion:** the conservative bank-filter route fails the count gate; the supported leaf-exclusion route clears it but fails global/runtime equivalence and Mastering Suite entitlement. It has not been proved impossible to construct a dependency-complete small project, but no such project is demonstrated. Further pruning offers no justified advantage over the official free entitlement route. Keep the complete project for the next baseline and investigate native source/build provenance if missing data persists after licensing.

Reproduction (fresh output folders; open the full copy in matching localhost WAAPI only for the first filter operation):

```powershell
python tools/white_orchard_prepare.py --audio-project '<W>' --output build/<fresh>/media-filter-control --preserve-hierarchies
python tools/white_orchard_init_audit.py --project build/<fresh>/media-filter-control/w3_audio.wproj
# Stop the task-owned WAAPI server before selective generation.
python tools/white_orchard_wwise.py --console '<T>/x64/Release/bin/WwiseConsole.exe' --project build/<fresh>/media-filter-control/w3_audio.wproj --output build/<fresh>/media-filter-banks

python tools/white_orchard_prepare.py --audio-project '<W>' --output build/<fresh>/leaf-inclusion-control --preserve-hierarchies
python tools/white_orchard_init_audit.py --project build/<fresh>/leaf-inclusion-control/w3_audio.wproj --exclude-file-leaves
python tools/white_orchard_wwise.py --console '<T>/x64/Release/bin/WwiseConsole.exe' --project build/<fresh>/leaf-inclusion-control/w3_audio.wproj --output build/<fresh>/leaf-inclusion-banks
```

Both generation commands are expected to fail under the current entitlements. The incomplete node-control output remains isolated evidence only. Compare using `white_orchard_compare.read_bank` / `difference`; do not package either control.

## 5. Incorporating the measured native fades into the production recipe

**Proposal, not implemented:** after an accepted native-equivalent control, adapt `C:\Dev\witcher-music-control\tools\white_orchard_author.py/author` using the routing/state-construction portion of `...\tools\white_orchard_native_fade.py/run`. Start from a fresh complete dependency-preserving baseline, never the instrumented `validation` project.

1. Retain existing path/build guards; also assert the Music parent, world GUID `{1A59CC64-141A-45A6-8374-EB823D3E9D4F}`, game_state GUID `{27711515-3584-4123-9F09-B90831398B80}` and native source Aux audit. Fail if unanticipated user sends exist. Re-run the existing 25-state coverage/disjointness check rather than assuming future States belong to the correct category.
2. Create a unity `Music/WMC_WorldMusic` aggregate, with **no effect or State association**. For conversion of a previous isolated recipe, explicitly clear its old `StateGroups`, `StateProperties` and three bypass effects; stale association truncated the earlier capture. Do not delete any native object. Prefer fresh construction over migration.
3. Create ordinary Bus `WMC_DryMuted` with base BusVolume **-200 dB**, plus four child AuxBuses `WMC_Fade_exploration`, `WMC_Fade_dialogue`, `WMC_Fade_combat`, `WMC_Fade_other`, all with base BusVolume **0 dB**. Numeric State gain adds to base; inactive base -200 on those AuxBuses was a demonstrated error.
4. Keep three **0–100 amplitude-percentage** GameParameters with defaults **0/0/100**. Put one continuous Wwise Gain (class **9109507**) on each E/D/C AuxBus, binding **both FullBandGain and LFEGain** through the measured `(0,-96.3)/(100,0)` Linear curves. Other gets no Gain. Do not state-switch effect bypass.
5. On each AuxBus select `BusVolume` via `setStateProperties`, associate existing game_state via `setStateGroups`, save and fill its generated CustomState IDs: **0 dB active / -200 dB inactive**. Other is active for every state outside E/D/C. Assert all **25** current States have exactly one active path. Leave vanilla StateGroup TransitionList/default timings untouched.
6. Change only prologue/world's dry OutputBus to DryMuted and its `OverrideUserAuxSends=True`, four `UserAuxSend0..3` references and corresponding send levels **0 dB**. Maintain existing parent Music processing and quest/cutscene routing; no new sends on authored branches. Save an object/parameter/State/routing manifest and audit all unrelated authoring definitions.
7. Exclude every validation fixture: test tone, Recorder, anchor, fixture transports and forced 5.1 BusConfig. Inherit native channel layout. Repeat the continuous-tone/protected/master tests in a separate validation copy; shipping generation must reject it.
8. Generate only Init/music_prologue. Extend the regional comparator to verify the world routing's expected output/send fields (record length can change), not merely accept any body change with that ID. Require every other regional record and media payload unchanged. For Init require every vanilla global record/reference/registration unchanged plus only the documented new buses, AuxBuses, Gain instances, parameters and their State data. Explain every unrelated serialized difference before eligibility.
9. Then use `white_orchard_cooker.py`'s already demonstrated isolated root and `cooksounds -r4remastersounds` bank-only workflow with **accepted** banks. Offline native-reader readback must equal inputs. The prior vanilla fixture is not a mixer build; game cache precedence and omitted-media fallback still require later authorized live testing.

No `SoundGameStateChange` hook is needed by the tested graph. No settings UI, other region, world-location exemption or new sparse mode belongs to this conversion. Native slider-update smoothing and real-game listening remain distinct tests from the measured native State transitions.

```text
vanilla game_state ─► four AuxBus numeric State-volume gates (native fades)
future settings ────► E/D/C amplitude-percent RTPCs ─► three continuous Gains
vanilla music_type ─► unchanged regional world / quest selection

prologue/world ─dry─► DryMuted ───────────────────────────────────────┐
              ├send► E gate + Gain(E) ────────────────────────────────┤
              ├send► D gate + Gain(D) ────────────────────────────────┤► WMC unity
              ├send► C gate + Gain(C) ────────────────────────────────┤   aggregate
              └send► other gate / unity ─────────────────────────────┘       │
prologue/quests_and_cutscenes ──────────────────────────────────────────► native Music
                                                          master/fades/mutes ► output
```

Minimum prospective deployment remains accepted loose bootstrap Init plus the two-entry mod soundspc.cache. The extra authoring objects live in those same Init/regional banks; no test audio, new WEM, script hook or UI is required by this graph. None has been packaged as a deployment candidate here.

## Acceptance and least-cost next action

Request the dedicated modding entitlement for the **actual 2023.1 Windows project**, explicitly covering the full supplied media count, Mastering Suite/HomeCinema and native plug-in use (including Motion). If that route cannot grant current-version coverage, ask Developer Relations for the free unrestricted non-commercial project entitlement plus the free Mastering Suite licence, or an authorized evaluation for the baseline proof. Confirm permitted publishing use and validity rather than treating trial output as licensed deployment.

Once the user applies an approved entitlement to an isolated project (or later authorizes a nonpersistent Console `--license-file` invocation), rerun the **unmodified complete hierarchy** control from report11 first. The installed `T/Data/Schemas/WAAPI/ak.wwise.cli.generateSoundbank.json:25–36` documents `--license` / `--license-file` without saving the key in the project; this was inspected but never invoked. Avoid command-line key text or logging key contents. Do not modify installed W/w3_audio.wproj.

If the licensed full control differs from native Init, stop and request matching source/build guidance from CDPR/Audiokinetic with the existing ID/chunk comparison. No binary splice, older Wwise downgrade, unlicensed HomeCinema removal, fresh empty-project Init or incomplete deployment is an accepted workaround. A free entitlement is the best supported next step; **native fidelity remains a separate mandatory test**.

## Final verification

E/protected-input-verification.json rehashes **1,556 protected installed inputs per control**, with zero changes. Native banks were read only. All generation/WAAPI processes owned by this investigation finished or were stopped; no WwiseConsole remains running at final inspection. Python compilation and `git diff --check` passed. Existing report10/11 test outputs were not overwritten. The old 28-check native-fade proof is retained, not presented as a new runtime test. No cache was cooked from either rejected Init and nothing was deployed.
