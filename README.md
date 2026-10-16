# Witcher Music Control

**Listening update (2026-10-16):** The user completed report57's21 private listening candidates, retaining12, rejecting8 and marking1 Maybe, with numerous exact passage/fade proposals. Original verbatim feedback is archived at [report58 raw JSON](research/58-user-musical-material-audition-feedback.json), with separately labeled interpretive guidance in [report58](research/58-musical-material-feedback-review.md). No edit previews, Wwise integrations, soundtrack changes or licences have yet been established.


**Private auditions ready (2026-10-16):** [Report57](research/57-sparse-musical-material-auditions.md) provides21 provisional material candidates (11 native,10 Music Plus additions),7 priority auditions and a local player with full recordings, beginning/middle/ending jumps and exportable decisions. Open build/music-material-selection/audition-v3/index.html in a browser; the first7 take about10minutes. All179 tests pass. Codex measured structure/audio but did not subjectively listen. No new scheduler, soundbank, game/Vortex change or integration. Next: listen, mark Keep/Maybe/Reject and identify3-5 worthwhile choices; Sparse implementation remains paused.


**Sparse proof completed (2026-10-16):** [Report55](research/55-white-orchard-sparse-rest-proof.md) demonstrates native audible phrases separated by two measured environmental-only rests, with native combat/intensity/complete outros, authored/Gwent controls and Music master response. The isolated candidate explicitly removes both inherited and static mutes from the permitted phrase while retaining narrow suppression elsewhere. Native location/day-night reselection can cancel a rest; combat return keeps native overlap, without persistent rest scheduling. All174 tests pass. No experimental bank, release package or deployment was made; accepted v2/v3/v4 remain intact. Next: resolve and test bounded re-entry/post-combat pacing before a reusable Sparse mode.


**Music Plus comparison (2026-10-16):** [Report53](research/53-music-plus-implementation-comparison.md) inspects the actual3.3.0 main/3.2.0 pack scripts, settings, editor and twelve soundbanks. Its track/silence scheduler and controls are real, but integral combat changes and world-thematic/global-dialogue gain caveats conflict with native-preservation goals. Recommended direction: independently develop an optional sparse mechanism on WMC's native foundation; no co-installation or third-party code/assets reuse. No new engine, playback or deployment was performed.170 tests pass, including all existing regional regressions. The proposed next step is one isolated native-only rest/interruption fixture, not another regional rebuild.

**Scope clarification (2026-10-15):** Consolidated v4 completes the *initial reviewed regional attenuation pass*, **not the full experience-led music vision**. The user reiterates an intended progression toward Breath of the Wild / Ghost of Tsushima-like sparse, deliberately paced, context-responsive musical presence rather than merely turning routine background score off. The previously explicit 0/0/100 policy remains the implemented initial baseline; details/defaults of a future Sparse mode, timing/event triggers and controls have not been approved or implemented. See [report51](research/51-broader-music-vision-reminder.md) and [original experience-led policy](research/08-experience-led-music-policy.md).


**Consolidated v4 ready offline (2026-10-15):** [Reports48–50](research/50-consolidated-v4-offline-package.md) complete a coordinated review of all five remaining regions. Kaer Morhen and Toussaint add11 approved static targets/54 noncombat rows; three regions remain native for thematic, unresolved or shared-combat reasons. The five-bank package preserves exact D/NML v2/Skellige v1. Independent native/source/decoded/media gates,58 paired Wwise captures, actual native cook/split and ZIP readback pass;157 tests pass. No deployment or new-region retail proof. Native Init remains unchanged. V4 ZIP SHA256 `b3312226b6f0b1520ed3a1d30516fe044fad900cc2508f641fe802138bc11ce3`, under `build/full-game-v4/consolidated-v4/archives/`. All eight regional policies are audited; this does not claim complete generic suppression. Mixed/unresolved paths remain native. V2/v3 rollback archives are preserved. See report50 for measured-outro limitations and a monitored mods.settings discrepancy left untouched. No licence/cooker action is pending; installation needs separate authorization and no forced game progression.

**Previous v3 milestone (superseded by v4; still retained) (2026-10-15):** [Report47](research/47-licensed-skellige-and-consolidated-v3.md) completes licensed Skellige generation and native three-bank packaging with exact retained White Orchard D and expanded NML v2. Exactly12 Skellige playlist Voice Volume fields change; all1,900 HIRC objects,253 media payloads and native global dependencies pass independent checks. Generic coverage85/185 consumer rows plus9 verified silent; protected/mixed/unresolved music stays native.38 representative Wwise captures preserve combat/intensity/complete outros, boat, authored paths, Gwent/minigames and Music master. Native cook/split exit0 and exact three-bank readback pass; actual diagnostics are explicitly reviewed. All141 tests pass. V3 ZIP SHA256 `432de7fddb522436603e88e7714b44f7e615e8cabce397bf213c59b3f746e803`. Licensing and cooker prerequisites are resolved. Nothing was deployed; retail Skellige remains untested. Current v2, native Init and rollback artifacts are unchanged. That next implementation is completed in reports48–50; no required gameplay progression.


**Latest retail feedback (2026-10-14):** Following installation advice for the consolidated White Orchard D + expanded Velen/Novigrad v2 archive, the user reports **"All, works"**. This supports successful consolidated operation in their current play, without establishing which NML selectors have been exercised. Exact installed-cache hashes were not independently checked in this report; individual NML locations remain untested. Next: continue spoiler-free offline work on Skellige and additional regions. See [report43](research/43-consolidated-v2-user-feedback.md).

**Testing decision (2026-10-14):** Develop further regions offline without custom saves, spoilers or rushed game progression. NML pilot remains untested in retail and provisionally accepted only for continuing engineering. User will report any issue encountered naturally. Verify a native two-bank D+NML cache and expand generic music coverage conservatively, preserving working D installation. See [report38](research/38-spoiler-free-offline-continuation.md).

**Current status (2026-10-13):** User reports satisfactory White Orchard gameplay. [Report27](research/27-working-fix-recovery-and-provenance.md) now identifies the deployed Vortex cache as the verified D Transition Fix Test, preserves source/build provenance and reconfirms native Init. All18 structural checks and32 tests pass. No new bank, deployment or save change was made during recovery.

**Shared implementation (2026-10-14):** [Report35](research/35-static-playlists-preserve-combat-outros.md) resolves the NML combat-outro defect using static attenuation on four approved generic playlists, with no shared location State gains. Full source checks and59 real Wwise captures preserve native combat/outros and White Orchard technical authored/Music/Gwent regressions. Retained D remains unchanged and decoded-bank verified. Exact consumer pins and strict source/bank gates remain. **Licensed NML candidate now passes full source and binary gates** ([report36](research/36-licensed-nml-candidate-and-cooker-eula.md)): exit2/19 unchanged warnings, exactly four playlist records changed,423 media payloads exact and native Init preserved. [Report37](research/37-nml-offline-package-ready.md) completes native cooker/split and Vortex ZIP readback after authorized settings preservation/relaunch. Both commands exit0; known bootstrap diagnostics match retained D. The experimental regional-only ZIP is verified,110 tests pass, and no Init/WEM/licence material ships. No NML deployment or retail test has occurred. That historical immediate-testing recommendation is superseded by report38: continue offline and await natural-playthrough feedback. Zone02/03 is partial coverage; unresolved/mixed paths stay native. Reports30–34 preserve earlier implementations and failed scope evidence.

**Current consolidation (2026-10-14):** [Report42](research/42-expanded-nml-consolidated-package.md) completes the expanded NML v2 bank and native consolidated cache/ZIP with unchanged White Orchard D. Generation exits2/19 baseline-identical warnings/zero errors; full source,21 decoded playlist edits,423 exact media payloads, unchanged globals and native cook/split readback pass. All115 tests pass. Generic noncombat coverage increases18→117 of419 selection rows, plus99 verified silent; unresolved/mixed material stays native. [Report41](research/41-expanded-nml-source-and-licence-gate.md) preserves classification and30 representative playback captures; its licence gate is now resolved. [Report40](research/40-native-two-bank-cache-proof.md) and all individual/v1 packages remain preserved. Expanded-v2 is ready offline, **not deployed or retail NML verified**. Next: reviewed Skellige manifest, independent validation and a new consolidated version. Natural-playthrough feedback continues under [report38](research/38-spoiler-free-offline-continuation.md); no custom saves or rushed travel. Shared source audio remains immutable after [verified deduplication](research/39-build-storage-cleanup.md).

A Witcher 3 Remastered mod project for **context-aware music gain**: reduce routine scoring without removing deliberately authored dramatic music or disturbing the game's native soundtrack transitions.

## Current target policy

These are **additional gain multipliers relative to the player's normal Music setting**, not absolute output-volume commands.

| Source / context | Initial target | Status |
| --- | ---: | --- |
| Generic world music during exploration / traversal | 0% | Explicit user target |
| Generic world music during ordinary dialogue | 0% | Explicit user target |
| Generic world music during combat | 100% | Explicit user target; retain vanilla combat/intensity behavior |
| Explicitly authored quest/story music, including gameplay and dialogue | 100% | No added attenuation; preserve authored fades and dynamics |
| Cutscene / movie / music-only cues | 100% | No added attenuation; do not defeat native movie mutes |
| Gwent, bards/taverns and other diegetic music | TBD | Preserve existing behavior until a separate policy is established |

"100%" means **unity additional gain**, not forced playback or an override of the player's Music slider. Working Stage1 uses Voice Volume−200 dB for perceptual suppression; measured silence is not proof of mathematical zero. The −96.3 dB Gain-plugin experiment belongs to the historical, deferred mixer.

**Design principle:** preserve contrast and authored musical meaning. Do not interpret the goal as "minimize all music." A future optional sparse-exploration mode may use intermittent musical punctuation, inspired by Breath of the Wild and Ghost of Tsushima, but this is a **design hypothesis**, not an approved replacement for the 0% default and not something a static volume slider alone can deliver. Details: [experience-led music policy](research/08-experience-led-music-policy.md).

## Historical licence/build notes (2026-10-11; superseded by reports22–35)

The user reports **approval and local import** of the Witcher 3 REDkit Wwise modding licence. **Effective coverage for this isolated Wwise project, successful generation, plug-in support and bank compatibility are still unverified**. Run the untouched complete-project licensed baseline first. A user-reported import is not a bank-generation result. Do not claim that a licence is installed or that this clears the observed project-ID difference. Before another bank-generation experiment, use the controlled post-approval protocol in [research/16-licence-pending-build-gates.md](research/16-licence-pending-build-gates.md). Keep all licence keys out of Git and logs.

## Historical engineering choice (2026-10-11)

**Complete-context build result:** [report 15](research/15-full-context-stage1-results.md) verifies the intended regional State serialization (+117 bytes, unchanged media and quest/event records, no new runtime IDs or Init changes). Full copies hit the trial-media limit; supported inclusion controls emit banks but still fail Mastering Suite licensing. Generated BKHD project identity is 0 versus native 39; compatibility with original Init remains unproved. No package was cooked or deployed.

**Stage 1: direct, fixed State Voice Volume on the existing `music_prologue/world_music` object.** This was demonstrated in Wwise authoring (report 13): exploration and generic dialogue -200 dB, combat/other states 0 dB, native State fades, and authored q001 quest music on its unchanged sibling branch. A playable soundbank is **not** yet established. There are no new buses, effects, GameParameters or modified global States in this design.

**Do not confuse the build input with the output.** The preferred next experiment preserves all 1,508 Wwise source work units in a fresh isolated copy, rather than pruning the project to one region. Modify only the existing `world_music` object for White Orchard, then attempt selective regional-bank generation. The experiment may let Wwise incidentally generate an isolated `Init.bnk`; that output must be discarded, not packaged or installed. The native game's Init stays untouched.

Preserving complete authoring context might reduce missing dependencies but **does not cure the existing 26,218/200 media trial limit or Mastering Suite licence errors** (report 12). If full-source generation fails, use controlled, supported inclusion tests and compare untouched versus modified outputs; do not call a failed build successful. If valid selected-bank output remains impossible, the official REDkit modding entitlement is the supported no-commercial-purchase request route, requiring separate user action.

**Stage 2 (deferred):** independent live sliders. Reports 05, 10 and 11 demonstrated a more involved mixer in authoring, but its new global objects create an Init-fidelity and licensing problem. Do not reintroduce this architecture during Stage 1.

Historical research 04–12 documents the earlier mixer, audio exceptions, licence investigations and successful *vanilla-fixture* cache cooking. Current operational decisions are in [13: direct State volume](research/13-world-state-volume-init-free.md) and [14: full-context build experiment](research/14-full-context-bank-experiment.md).

## Historical White Orchard build protocol (completed; current status is report47)

1. Prepare a **complete**, separate copy of the existing Wwise 2023.1.19 project using `white_orchard_prepare.py --preserve-hierarchies`. Never write to installed game, REDkit or Wwise files.
2. Apply only the existing world's 25 State Voice Volume values using the clean author-only helper `tools/white_orchard_state_volume_author.py`. Do not use the test-tone/Recorder workspace as production source.
3. Select `music_prologue` for the initial bank-generation test, but **do not prune the project or require single-bank generation if it is the blocker**. Allow an incidental isolated Init output solely as evidence; never deploy it.
4. Compare modified and pristine regional output against each other and vanilla, including BKHD, HIRC State serialization, global references, event/media/stream equivalence and actual Wwise generation errors. No invented binary splice.
5. Once a valid regional bank is established, use the proven isolated REDkit cooker workflow to package only required changed banks. Validate cache readback, then separately request authorization for an isolated, backed-up White Orchard game test.

Project-size minimization is secondary to reliable output. Shipping all eight regional banks is **not** a requirement or a solution to licensing, but may be accepted later if simpler and compatible. No REDkit 66 GB depot rebuild is authorized.

## Repository layout

- `AGENTS.md` — Codex conventions, authority and non-destructive work rules
- `research/` — source-backed investigations and design decisions
- `src/` — our future authored mod source
- `tools/` — reproducible helper scripts
- `build/`, `deploy/` — ignored generated output
- `reference/` — local, Git-ignored third-party references (Only Story Music variants, Less Is More, FMC Audio Remaster)

Game installations, REDkit installations, original Wwise resources and third-party mod payloads are **read-only evidence**, never committed or modified in place. The music-control project is on `main`; `general-merge` is an independent compatibility-audit branch.
