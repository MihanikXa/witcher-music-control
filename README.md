# Witcher Music Control

**Testing decision (2026-10-14):** Develop further regions offline without custom saves, spoilers or rushed game progression. NML pilot remains untested in retail and provisionally accepted only for continuing engineering. User will report any issue encountered naturally. Verify a native two-bank D+NML cache and expand generic music coverage conservatively, preserving working D installation. See [report38](research/38-spoiler-free-offline-continuation.md).

**Current status (2026-10-13):** User reports satisfactory White Orchard gameplay. [Report27](research/27-working-fix-recovery-and-provenance.md) now identifies the deployed Vortex cache as the verified D Transition Fix Test, preserves source/build provenance and reconfirms native Init. All18 structural checks and32 tests pass. No new bank, deployment or save change was made during recovery.

**Shared implementation (2026-10-14):** [Report35](research/35-static-playlists-preserve-combat-outros.md) resolves the NML combat-outro defect using static attenuation on four approved generic playlists, with no shared location State gains. Full source checks and59 real Wwise captures preserve native combat/outros and White Orchard technical authored/Music/Gwent regressions. Retained D remains unchanged and decoded-bank verified. Exact consumer pins and strict source/bank gates remain. **Licensed NML candidate now passes full source and binary gates** ([report36](research/36-licensed-nml-candidate-and-cooker-eula.md)): exit2/19 unchanged warnings, exactly four playlist records changed,423 media payloads exact and native Init preserved. [Report37](research/37-nml-offline-package-ready.md) completes native cooker/split and Vortex ZIP readback after authorized settings preservation/relaunch. Both commands exit0; known bootstrap diagnostics match retained D. The experimental regional-only ZIP is verified,110 tests pass, and no Init/WEM/licence material ships. No NML deployment or retail test has occurred. The next step is a separately authorized Vortex off/pilot/off test with an established zone02/03 route. Zone02/03 is partial coverage; unresolved/mixed paths stay native. Reports30–34 preserve earlier implementations and failed scope evidence.

**Current consolidation (2026-10-14):** [Report40](research/40-native-two-bank-cache-proof.md) proves a native two-bank cache and consolidated D+NML-pilot ZIP. [Report41](research/41-expanded-nml-source-and-licence-gate.md) expands approved generic coverage to21 playlists and117 noncombat consumer rows; full source and representative playback pass. Fresh v2 generation is blocked by project-local licensing. Apply the approved entitlement manually to `build/consolidated-expansion/nml-v2/candidate/w3_audio.wproj`, then resume strict binary/package gates without regenerating the baseline. Combined-v1 is ready offline; expanded-v2 has no bank/ZIP yet. Retail NML remains unconfirmed and will be assessed during natural play, without spoilers/custom saves, per [report38](research/38-spoiler-free-offline-continuation.md). Shared source audio is immutable after [verified deduplication](research/39-build-storage-cleanup.md).

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

## Historical White Orchard build protocol (completed; current next action is report35)

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
