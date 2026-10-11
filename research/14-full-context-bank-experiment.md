# Complete-context State-volume bank experiment — 2026-10-11

**Executed:** [report 15](15-full-context-stage1-results.md) records complete-context paired builds and supported Inclusion controls. The intended inline State data serialized with unchanged media/non-world HIRC and no Init additions. Generation still exits 1; numeric BKHD project identity differs from native. No compatible package or game test is certified.

## Decision

**Do not equate the smallest patch with the smallest authoring project.** Retain the complete Wwise source hierarchy in an isolated workspace, apply the already-measured direct State Voice Volume change locally to White Orchard `music_prologue/world_music`, and let supported generation determine what banks are needed. Start by selecting `music_prologue` for a controlled comparison, but do not prune or reconstruct the source project merely to limit output. White Orchard remains the first *gameplay* test, not a restriction on work-unit scope.

**Objective:** obtain and assess a modified regional bank that reuses vanilla Init, without custom buses, effects, parameters or global State definitions. If necessary, Wwise may incidentally emit an experimental Init *inside ignored build output*; never substitute it for the original installed game Init or package it into a mod.

## Existing evidence versus hypothesis

- **Observed, report 13:** Wwise authoring applies local State Voice Volume to `music_prologue/world_music`; 31 checks passed, including voice attenuation, native transitions and direct q001 authored playlist protection. This does **not** prove generated SoundBank serialization or actual game runtime behavior.
- **Observed, reports 11–12:** complete source retains 1,508 work units; full project generation currently fails a 26,218/200 trial-media limit plus six HomeCinema/Mastering Suite errors. Omitting unselected SoundBank media inclusion alone does not fix it. Excluding file-backed leaves outside `music_prologue` clears the media-count error, but still produces an incomplete Init and a generation exit 1; the modified State world object has not been generated under those conditions.
- **Observed, report 13:** an unmodified native `music_prologue.bnk` can be packed into a *single-entry regional-only* CS3W v2 `soundspc.cache` using the native cooker. This proves packaging/readback of vanilla data, **not** runtime loading of a modified regional bank.
- **Unresolved:** BKHD offsets 16/24/28/32/36 differ between native and isolated generated banks even with identical unmodified HIRC/media; their semantics and potential loader effect remain unknown. Native Init currently differs from the attempted regenerated controls. A readable Wwise XML StateInfo does not guarantee an appropriate v150 HIRC encoding.

## Immediate experiment

1. Prepare **two** fresh, complete isolated copies of the Wwise 2023.1.19/build8928 project using `white_orchard_prepare.py --preserve-hierarchies`: untouched control and Stage 1 candidate. Preserve full default hierarchies and all 1,508 work units. Do not edit the installed Wwise project or game.
2. On the candidate only, use `tools/white_orchard_state_volume_author.py --project <candidate>/w3_audio.wproj` after starting a localhost WAAPI server for that exact project. This clean helper applies the 25 local Voice Volume State values and does not import any test audio or change native global definitions. Verify its audit, independent of the instrumented test scripts.
3. Attempt selected-bank generation for the pristine and modified copies into **separate fresh** ignored output paths. It is permissible for Wwise to generate an incidental isolated `Init.bnk`; that file is **disposable comparison evidence**, not a deployable artifact. Capture command, full exit code, plugin/license/media diagnostics, produced-file hashes and HIRC/DIDX/DATA/INIT/STMG differences.
4. First compare full-hierarchy selected-bank results without source exclusion. If blocked by the documented trial limit, repeat as a **controlled pair** using the supported file-leaf inclusion reduction from report 12, applied equivalently to both workspaces. This is experimental dependency pruning, not evidence that the output preserves every original global registration. Preserve separate unmodified controls. Never suppress licence errors or assume a bank emitted during a failed run is valid.
5. Decode/validate the changed regional State Voice Volume serialization, including all new local IDs and references to native global StateGroup/State IDs, preserved non-world HIRC, unchanged media/streamed resources and original native Music routing. The existing comparator treats HIRC bodies as opaque; it is **insufficient by itself**. Check BKHD semantics using source-backed parsers, Wwise tools or validated runtime behavior; do not blindly copy original headers or splice opaque bytes.
6. If *and only if* a soundbank is valid and dependency-complete, pack **only** the required modified regional bank(s) using the tested isolated REDkit cooker, and check payload readback. A native-only fixture is not acceptance of a mod. No game installation, save changes or live-loader tests without separate authorization.

## Minimal project vs minimal output — decision rules

- The project's complete hierarchy and original work-unit IDs are higher priority than a small source workspace. White Orchard uses `music_prologue`, but the compilation may depend on definitions elsewhere.
- Start with selected regional output because it supports clear diffs; **do not insist on it if generation itself proves dependent on broader scope**. If multiple regional banks are needed, justify the dependency and produce/compare them. All eight regional banks are small in total, but shipping more banks increases audio-mod conflict scope, so avoid unnecessary replacements.
- A generated Init in a temporary folder is acceptable; **deploying or modifying native Init is not**. Full/project-wide generation may still require Audiokinetic's REDkit modding entitlement; changing the number of generated banks does not bypass licensing.
- If dependency-complete regional-only generation remains blocked, state the blocker precisely and recommend the documented *official modding entitlement request* as a user action, not an automatic purchase or proof that commercial licensing is required.
- Stage 1 remains fixed 0/0/100. Stage 2 independent sliders are deferred. No source WAV redistribution, deep binary splice, 66 GB depot regeneration or live deployment.

## Stop conditions and evidence expected

A successful result is an inspectable regional candidate with the intended local State changes, no unexplained global dependencies, untouched native Init, provenance for any compiler warnings, and an independently verified cooker package **ready for separately authorized in-game testing**. Otherwise retain the exact failure report, baseline/candidate comparison and a justified next route; never label a failed build as deployable.

**Tooling note:** `tools/white_orchard_state_volume_author.py` is newly written clean authoring source. It has not been exercised against the installed Windows Wwise environment; Codex must review and verify its API calls, project/work-unit checks and saved outputs when running the next experiment.
