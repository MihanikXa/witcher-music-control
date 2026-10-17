# 68 — Remaining sparse-cue ending selection: preregistered six-cue trial — 2026-10-17

## Authority and task

The user explicitly agreed to hand off the next step: **determine how well we can choose endings for the rest without individually hand-tuning each one**. The assistant's proposed workflow was: analyze the unapproved excerpts and their endings; derive a provisional selection rule from the **five accepted exact renders**; freeze choices **before** evaluation; make **six diverse playable examples**; assess the fit once the user listens, then consider scaling. This specification authorizes research, local private audio/metadata rendering and testing, **not** a universal production preset or full library rollout.

Start with `AGENTS.md` and reports 58, 61–67. Explicit musical timings/roles in `research/58-user-musical-material-audition-feedback.json` and later user corrections prevail over inferred design rules. `research/67-accepted-private-cue-selections.json` pins the five accepted exact private WAVs and hashes; `research/65-user-cue-tail-v2-decisions.json` and report66 contain rejection/acceptance and measurement controls. `research/61-private-cue-edit-plan.json` enumerates all 24 source-clock edited excerpts, including two restricted comparative S14 excerpts. **S05-main B v1** was a separately accepted reference; do not treat it as one of the five report67 items or a new holdout. Label explicitly previously approved, previous negative, unknown and restricted cases.

## Goal

Build a reproducible and *modest* rules-based **treatment triage** for the unapproved passage endings, followed by a **preregistered six-cue out-of-sample audition**. Optimize for a natural perceptual transition from music into quiet. Prevent known wet-level jumps, double fades, overly fast direct-to-room transitions, unnatural held harmony and overly conspicuous effects. Maintain musical usefulness over purely monotonic waveform metrics. There is insufficient evidence to learn numerical preference weights or claim accuracy from the five positives.

## Phase A: source measurement across all remaining cues

Recover every source identity and source-clock cut and user note without rewriting report58. Do not decode or copy all proprietary audio multiple times needlessly; use existing locally verified private source previews, FFT/PCM analysis tools and provenance fingerprints. Record a per-cue table with:
- cue ID; original/MP pool and context; source in/out, dry fade, optional base stem/arrangement caveat, authored reuse/rights flag, user's source notes, previous v1 feedback status;
- source RMS and short-window envelope leading into cut; original already-natural decay or endpoint near silence; local dynamic slope, transient and spectral changes; potential start silence/bleep; original source tail and potential note/chord shifts (if meaningful and supported by actual analysis);
- simulated/reconstructed dry/wet/total curves for provisional choices, including room-send policy, onset timing, fade slope, actual RT60, wet/dry calibration window and ratio, frozen state release policy, tail audibility and end safety; measure perceptually salient jumps, gaps, rebounds, held-energy vs audible output and tail termination;
- derived classification such as 'already near-silent', 'abrupt cutoff with sustained harmony', 'busy transient/percussive', 'slow evolving atmospheric', 'long fade with harmonically changing end'; mark uncertain classifications as uncertain, never assume a file title proves mechanics.

For machine features, describe threshold choices as heuristics/sanity gates, not fitted preference models. A narrow peak/RMS check cannot prove harmonic closure or subjective naturalness. Source-file timing **must not be silently substituted with Wwise segment timing**.

## Phase B: transparent treatment policy and predictions

Using the five accepted report67 WAVs as **examples**, derive a small readable decision tree or rules table with explicit mechanism and exception flags—not a pseudo-scientific numeric scoring function. Broad prior: **continuously established, longer naturally decaying conventional reverb is the usual starting candidate**, based on the user's latest report63 statement. Choose send policy (normal post-fader or independent pre-ending fade), wet gain, dry fade behavior, RT60, sufficient rendered tail and optional freeze. Do not infer that S12-1/S04-b *won because of freeze* when their post-stop tails measured near silence; accepted cases are entire combinations, not controlled causal evidence.

- Avoid copy-pasting S05's 2-second fade, S11's post-fader policy, or S07's 7-second RT60 to unrelated source material.
- If cut/fade was **explicitly user specified**, preserve it. Only revise prior Codex-provisional cuts/fades where the plan says they were provisional, and document both versions.
- Keep the five accepted hashes/audio unchanged and preserve S05-main B v1.
- Avoid v1's late wet onset/plateau/two-stage fade. If attempting freeze, use report64's continuous established field and immediate smooth output release, not the old late attack and held wet layer.
- Preserve S14's authored-route restriction and MP/private-rights restriction throughout.

Create a **preregistered per-cue prediction ledger** before generating/listening to six final trial renders. For each of the 24 plan cues record accepted/auxiliary accepted/pending/comparison-only as appropriate. For each pending cue list source features with confidence/unknowns, predicted preferred treatment and concrete parameter values, technical risk and audible failure hypothesis, plus alternative if uncertain. Freeze the ledger by committing it or storing a fingerprinted immutable snapshot **before the trial renders**. Do not backfill expected success after observations. Distinguish technical safety checks from *predicted subjective fit*; don't invent fitted probabilities.

## Phase C: six-cue representative test

Prefer these **six distinct source compositions / roles** for an informative trial, unless measurements reveal a compelling coverage issue (document substitutions *before* rendering):
- **S07-c**: prior user complaint that freeze was too early; compare later/normal reverb in a dramatically changing piece.
- **S12-2**: earlier user note reports sudden conventional wet entry despite 'Unreviewed' verdict; short native cut.
- **S15-a**: previously unreviewed Music Plus excerpt with explicit user fade.
- **S16-2**: previously unreviewed longer, native otherworldly atmospheric section.
- **S18-3**: previously unreviewed shorter native isolated punctuation with mid-source entrance.
- **S20-a**: previously unreviewed native city-night atmospheric/punctuation with specified fade.

These are **two known-problem regression probes and four not-yet-reviewed excerpts**, across six sources and multiple durations/context types. If these fail to span meaningful measured categories, adjust the selection *before* looking at results, explicitly record why. S14 is comparison-only, should not occupy an ordinary rollout probe; previously accepted cases are calibrators, not holdouts. Cases drawn from sources with already accepted *different passages* are not independent material generalization; label this limit. S04-a / S11-long may be useful follow-on exceptions but don't silently expand this trial.

Create exactly **one principal predicted version per selected cue**. Where justified, offer **one controlled fallback on at most two high-risk cues** for diagnosis; don't create three to five variants everywhere, don't add a universal frozen alternative out of habit. Keep original full-source references available without copying more source files unnecessarily.

## Phase D: outputs and verification

Generate fresh ignored `build/music-material-selection/treatment-trial-v1/` including a local HTML listening index with source and cue ID, all rendered paths, cut/fade values, selected treatment, short *precommitted* explanation/uncertainty, v1 reference only when it helps, play-end control, keep/adjust/reject, optional variant preference, human notes and reliable JSON export/copy fallback. Keep ~2s lead and quiet final context, label player/source/fade clocks separately. No audio in Git.

Add a clearly separated **human evaluation form** showing the original predicted treatment and recorded user outcome. Recording an actual outcome must be append-only or in a separate file, never rewrite the prediction. Focus on 'seamless handoff?', 'musical resolution?', 'tail too intrusive/too short?', 'unexpected audible artifact?'—not blanket opinions or invented objective ratings.

Code/tests must verify source fingerprints and original cut coordinates, cue starts, dry/wet/sum 50/250ms windows, no imposed late wet attack / hold / double fade, clipping/headroom, actual output silence, valid PCM and browser links, and unchanged five accepted WAV hashes. Compare against known defective examples to ensure regression gates would catch v1 failures. A declining RMS envelope alone does not guarantee natural timbre; no subjective verdict by Codex.

Run existing Python and offline client tests (latest known 193 Python). If local audio/source references are unavailable, report blocker rather than create synthetic 'finished' outputs. Commit only original code/tests, sanitized evidence, frozen ledger and a new numbered completion report. **Do not** regenerate the entire remaining 19, touch Witcher 3/Wwise/Vortex, alter accepted releases or distribute Music Plus material.

## Decision after user feedback

**Stop after six playable cases.** No automatic full-library propagation in this handoff. Present concise results and the JSON export workflow. After the user listens, evaluate prediction-versus-feedback for the four fresh cases separately from the two known-defect regression cases, including failures and alternative explanations. Revise the rule only after observing outcomes, versioning rather than rewriting the preregistered predictions. If the trial underperforms, simplify to a natural-reverb baseline or use small specialist families rather than pretending a five-example system has generalized.

**Success:** a traceable triage of remaining material + a preregistered, technically audited six-cue listening trial that can actually test whether predictive treatment selection reduces subjective hand-tuning. It is not a finished soundtrack or game integration.
