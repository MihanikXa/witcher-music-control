# 62 — Cue-tail audible handoff defect: user feedback and corrective direction — 2026-10-17

## User evidence and status

The user listened to some of report61's private cue edits and uploaded the exported JSON. Their complete **verbatim** 24-cue feedback (with exact source-clock ranges, render hashes, selected versions, notes and parameters) is preserved in [62-user-cue-edit-decisions.json](62-user-cue-edit-decisions.json). Count: **8 Adjust, 2 Keep, 14 Unreviewed**. One Unreviewed entry, S12-2, nevertheless has a substantive note. User explicitly considers it unproductive to audit the remaining clips because the same problem recurs. **No rejection or approval is imputed to unreviewed cues**; stop asking for further v1 listening.

Important examples (exact quotes remain in raw file):
- S04-a: B and C too sudden; B more natural; audible content begins about5s after the preview starts.
- S04-b: initial bleep unwanted; desired start around3s into crop; audible jump at24–25s; freeze holds after early fade, then separately fades.
- S05-main **Keep, B**; S07-b **Keep, B** but user requests **longer reverb decay**.
- S05-short, S11-short, S11-long: distinct jump into frozen tail, followed by another fade.
- S07-a: held tail too constant with late sudden fade. S07-c: freeze captured too early; longer conventional reverb requested.
- S12-1: dip then freeze reappears; S12-2: same issue and sudden B reverb entrance.
- User picked C on some Adjust cases as a relative preferred variant, **not** approval of the processing defect.

## Cause: code-supported diagnosis, not an audition of local WAVs

The shared algorithm in `tools/cue_freeze_dsp.py::render_variants`:
1. Sets the dry fade using `dry_envelope`.
2. Begins audible wet processing only at `freeze_at`, usually exactly the start of the dry fade.
3. Uses `tail_env[:wet_attack]=ramp(...)` to **raise** the wet component while the dry component is fading down.
4. Holds the wet envelope at **full gain until after dry end + hold_after_dry**, then starts **another separate** output fade.
5. For C, `Field.process(freeze=True)` transitions to lossless feedback, leaving underlying state energy constant until externally faded.

This architecture directly permits the perceived **dip → wet swell/re-entry → constant-level plateau → later second fade** across unrelated sources. For S04-b, source `freeze_at=57s` minus `source_in=34s` gives wet entrance23s after crop onset; add2s preview lead silence and the player shows about25s, consistent with the reported24–25s jump. This alignment strengthens but does not itself prove waveform causation. Current QA checks sample continuity, no clipping, fade-boundary values and internal freeze-energy conservation, not perceived combined-gain evolution. No source WAVs were provided for a new acoustic test in this turn.

Variant B also begins its wet output through a late attack; it is not a continuously present standard reverb send. Hence S12-2 can experience a jump even in B. Do **not** solve this by making tail_extra larger, changing one wet_db_relative parameter, or lengthening C's hold.

## Recommended small corrective test (before full rerender)

1. Preserve report61/v1 renders, report58 musical material directions, the uploaded raw JSON and existing WMC releases untouched. Do not reprocess all24.
2. Compare representative v2 material: **S05-short, S11-short, S12-1, S07-b** (and S04-b as a focused onset/24–25s regression). Keep the original source selection/timestamps. Adjust S04-b's initial bleep according to the user's note using a safe boundary after audition; the user's “3s” is a source-relative observation, not yet a fixed crossfade command. S04-a's initial5s may be pre-roll or intended silence; don't trim silently.
3. Build a low-level, continuously audible conventional reverb **send before the dry fade**, rather than introducing wet at the cut. Let B receive ordinary fading excitation and decay smoothly; test genuinely longer ordinary decay on S07-b and some other cases. Source/tail levels need an integrated, matched time-domain envelope, not merely RMS matching of initial ungated wet fields.
4. If testing freeze C, transition an **already-active wet field** smoothly into an internally frozen state. Remove the independent post-dry constant-level hold, and use a **single continuously decreasing release envelope** across the dry-to-tail region. Let per-cue DSP tune wet mix and capture moment. Never claim a late-onset gated reverb with lossless feedback is a pleasant fade just because the state energy is conserved.
5. Run objective checks around entire dry+wet RMS envelopes for gaps, rises, plateaus and double-fade geometry using 50–100ms windows, test source endings and onset clicks, and compare A/B/C at controlled levels. DSP checks are necessary but cannot replace subjective listening.
6. Generate a **tiny private A/B comparison index only for the revised controls**; user only needs to review a few corrected examples before authorizing a full24-cue batch. If B is better, prioritize B; optional freeze is not the goal in itself.
7. Keep no game/Wwise/scheduler/bank/Vortex action, no reused third-party code, no source asset distribution, and no licensing assumption. Commit only original tools/tests/sanitized report/metadata after independent pass.

This report records the new user correction and a proposed bounded next engineering step. It does not claim a v2 algorithm, audio render or Wwise integration was completed.
