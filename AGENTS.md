# Codex instructions — Witcher Music Control

**Current empirical status (report 25; supersedes stale build-stage text below):** After the initial White Orchard Stage1 runtime success and transient-bleed defect (report24), the user now states **"Everything works great now"** (2026-10-13). This supports a user-perceived successful local transition correction; the exact revision, changed source, generated bank and Vortex ZIP have **not been published to this repository**, and authored/curated quest music still has no explicit in-game confirmation. First sync/preserve the actual working local fix and independent build evidence; **do not reconstruct or invent D's mechanism from this report**. Then prioritize authored-music exceptions and staged expansion to the other regions. Do not revisit ProjectID/Init licensing as an assumed blocker. See reports 24–25. Historical build instructions below remain provenance, not current go/no-go gates.

Read the current research reports, particularly `research/04-architecture-options.md` through `research/08-experience-led-music-policy.md`, **before** changing implementation. Earlier initial-stage prompts favoring a script-first solution were superseded by the source-backed Wwise analysis.

## Outcome and evidence discipline

Build a Remastered-compatible contextual music-control mod that **preserves the hierarchy of musical importance** rather than simply suppressing every non-cinematic cue.

Current explicit user-target defaults, as **additional gains on top of the normal Music setting**:

- generic exploration / traversal = 0%
- generic ordinary dialogue = 0%
- generic combat = 100%
- deliberately authored story / quest music during dialogue **or gameplay** = 100%
- cutscene / movie / music-only = 100% additional gain (preserve native muting/fades)

Do not promote assistant suggestions into explicit preferences. The optional intermittent/sparse exploration mode is **deferred and unapproved**; implement only when separately requested and validated. The user values Breath of the Wild (85/100) and Ghost of Tsushima (82/100) overall, but that does not independently establish endorsement of every audio technique. Film observations support score identity, perceptual pacing and meaningful contrast—not automatic preference for maximal silence or constant score prominence.

Preserve ambient effects, voices, diegetic bards, Gwent and native combat intensity until their respective policies have been established. Do not equate 100% with forced playback. Do not equate measured PCM silence at -200 dB (Stage 1 Voice Volume), or -96.3 dB (historical Gain prototype), with proven internal mathematical zero.

## Technical authority and current architecture

Technical authority: matching installed Remastered/REDkit resources, matching Wwise 2023.1.19 definitions and empirical playback, compatible references, then hypotheses. Current game/film preference evidence cannot be inferred solely from review/reputation.

**Operational stage 1 (reports 13–14):** retain the existing `game_state` and `music_type`; attach fixed State-driven **Voice Volume** directly to `music_prologue/world_music`. Exploration/dialogue = -200 dB; combat/other = 0 dB. The existing `quests_and_cutscenes` branch is not changed. Authoring measurements showed native State fades, combat and authored q001 preservation, and the resulting modified regional bank **now works in the user-reported in-game test (report24)**. This supersedes the older WMC custom-bus instructions for stage 1. `Init.bnk` need not receive new source-level definitions; actual candidate operation alongside shipped Init is **user-reported in-game**, while general compatibility beyond tested White Orchard contexts remains unproved.

**Operational stage 2 (deferred):** independent user sliders may require the more elaborate state-volume AuxBus mixer from reports 05, 10–12, with a properly licensed, fully faithful Init. Do not add custom buses/effects/RTPCs or a SoundGameStateChange hook to stage 1. Do not turn the optional sparse-exploration hypothesis into an approved requirement.

**Historical licence gate — now resolved for Stage1 candidate (reports18/22):** The user reports that the approved Witcher 3 REDkit modding licence has been imported into Wwise. Do not request, read, copy, echo, log or commit the key. First verify that the *isolated full-project baseline* uses an effective licence without editing the installed REDkit project. Read `research/16-licence-pending-build-gates.md` and `research/17-read-only-licensed-bank-verification.md`. Run **only the untouched full-hierarchy baseline** and review generation and strict read-only verification. If any compatibility gate fails, stop and preserve the evidence; do not proceed to the candidate or deploy. If the licence was applied only to a different Wwise project, ask for a secure project-local application rather than extracting or transferring the key yourself.

## Historical Stage1 build protocol (completed; see reports 22–24)

1. Read reports **13 and 14** first; reports 04–12 are historical evidence and may contain superseded prototype recommendations. White Orchard is the in-game target; the matching Wwise bank is named `music_prologue`. Never test the musicless Kaer Morhen opening as evidence of exploration suppression.
2. Use a *fresh complete isolated copy* of the original Wwise project, including all 1,508 original `.wwu` work units and default hierarchies. `white_orchard_prepare.py --preserve-hierarchies` is the existing setup. Do **not** prune regional branches simply to make the patch small. The project's output paths, source control and commands must be isolated and original input hashes verified.
3. Apply only the local State Voice Volume change with `tools/white_orchard_state_volume_author.py`. Confirm world object GUID/ShortID, existing game_state group, 25 disjoint State entries and that all unrelated work units remain unchanged. Do not use the fixture-containing `white_orchard_state_volume.py` output as shipping source.
4. Use selected `music_prologue` generation as the **first test**, not an artificial limit. Full-source generation was blocked by Wwise's 200-media trial limit and Mastering Suite licence; supported exclusion controls were explored in report 12. Record every warning/error/exit status. If Wwise automatically emits an `Init.bnk` into ignored build output, that is permitted **as disposable build evidence only**. Never use it to replace installed native Init.
5. Compare baseline and modified regional banks with native. Inspect the new local State/Voice Volume serialization and all new IDs/references; preserve vanilla events, non-world HIRC, media, streamed references and Music master. BKHD header differences are still unexplained. A file produced during a failed generation is **not** automatically an acceptable bank.
6. The existing REDkit cooker can create and read a **regional-only cache from a vanilla bank** (report 13). That is not a validated modified-bank deployment. Only use the cooker for a release candidate after bank validity and native Init dependencies are established. Package the minimum *changed, compatible* banks; allow multiple banks if necessary, not project pruning to achieve minimal output.
7. Stop before live-game installation or save modification. Once a safe package exists, request separate authorization for an isolated, backed-up White Orchard test with actual audible exploration, routine conversation, combat and available authored scenes.

**Decision gates:** if generating the new regional bank remains blocked despite complete context and supported inclusion settings, document exactly which build action fails. A dedicated **free-request** Witcher 3 REDkit Wwise entitlement is documented (report 12); do not claim it has been granted or install/activate a licence. If an Init-free build proves impossible, explain why before returning to a global mixer. Do not manually splice opaque HIRC/BKHD fields or reconstruct audio semantics by filename.

**Milestone 2 — exceptions:** use `research/07-world-music-exceptions.md`; inspect intended scene/function and audible behavior. Do not use a `mus_q*`/file-name heuristic or automatically exempt every quest-named location. Exempt narrow noncombat containers/playlists when justified; exempting whole locations may disable combat-gain control.

**Milestone 3 — presentation:** test long periods of environmental audio, score entries, dramatic transitions and authored cues. Music which repeatedly declares minor actions climactic is undesirable; do not use the mod to force greater music density or intensity.

## Safety, structure and compatibility

- Third-party copies in `reference/` are read-only and Git-ignored. Do not redistribute them.
- Installed game, REDkit, Wwise and partial depot files are read-only; never alter in place.
- Do not repeat the failed 66 GB REDkit depot generation unless an actual required operation is proven impossible otherwise.
- Author our source in `src/`; helper scripts in `tools/`; notes and validation logs in `research/`; generated outputs in ignored `build/` and `deploy/`.
- Do not commit game banks, cache output, audio media, installed assets, depots, third-party files or machine-local private paths except as explicitly labeled evidence in research notes.
- Avoid indiscriminate full script replacements, unverified game hooks and periodic per-frame polling.
- Keep builds reproducible, stage artifacts outside game directories, check output destination flags, and record version/command/logs and file hashes.
- For each claim, record observed behavior, supported inference, remaining hypothesis, and a falsifying test.
- Read [research/09-white-orchard-pilot.md](research/09-white-orchard-pilot.md) for the authorized pilot geography. Do not confuse the Wwise `music_prologue` bank with a request to test the Kaer Morhen tutorial.
- Prefer preserving Wwise-authored transitions and the normal user Music volume; a category multiplier must not rewrite composition, threat weighting or scene-event sequencing.
- Conflicts with audio mods that replace Init or regional banks must be documented; do not claim automatic cache merging.
