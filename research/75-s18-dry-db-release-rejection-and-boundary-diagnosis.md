# 75 — User rejects S18 constant-dB release; revisit musical exit — 2026-10-17

## Latest explicit feedback

> B is ten time worse Worse in the dip, it much more sudden now. What is up with that one?

This refers to report74's S18-3 **B dry-only constant-dB release**, `s18-dry-fade-v2/index.html`, compared with original A dry-only cosine release. **B is rejected as substantially worse / much more sudden.** Do not record B as an approval or ask the user to audition it again. The user has not supplied a new approved v4 alternative. Preserve report70's qualified S18-3 Keep/B, all exact historical WAVs and the other ten selected files.

## Code- and data-grounded explanation (not new subjective listening)

Report74's function `tools/cue_freeze_dsp.py::dry_db_release` attenuates **72 dB over an unchanged2.2-second fade** (2s leading silence → player17–19.2s), with a0.12s ramp to nearly constant decibel slope and20ms cleanup. It was devised to avoid A's steeper *late* decibel slope, but its sustained steep attenuation instead makes the passage disappear **too early**. Readback from report74:

| Player second | Original dry A | New dry B |
|---|---:|---:|
|17.0|−30.65 dBFS|−31.11 dBFS|
|17.5|−32.99|−48.05|
|18.0|−35.73|−63.83|
|18.8|−53.79|−90.33|

These are source-conditioned100ms RMS measurements, not arbitrary gain-envelope labels. B is already ~28 dB lower than A at18s, effectively silent by18.8s. A constant dB-per-second slope in this short window does **not** establish a perceptually smooth decay; the very large target attenuation made the early loss overwhelming. The newly tested release was a poor proposal despite clean PCM, valid math and204 passing tests.

The stronger structural problem: report73 showed the **unfaded musical source remains active and slightly rises** around player18.3–19.1s (approximately−29 to−27dBFS), while *both* proposed fades must reduce it to digital zero by source130s. The user previously heard a dip even in the dry-only original. Report57's S18 full recording lasts **157.01s**, so the requested S18-3 punctuation ends roughly27 seconds *before the original recording ends*, without source evidence that130s is a natural musical cadence. The report57 native authored exit is around152.667s but may not map directly to the source audition clock; do not invent a resolved cadence/usable endpoint. This supports a **musical-cut constraint hypothesis**: the release may remain artificial because it suppresses ongoing, nonresolving material. It does not establish that all fade shapes are impossible, or authorize shifting the explicit user cut without approval.

## Correct next decision — no more unbounded DSP taper attempts

1. Stop trying new constant-dB targets, wet-send exponent sweeps, or declaring success from envelope smoothness alone. Report71–74 have already shown multiple technical gates that missed the perceptual defect.
2. Inspect actual original **S18 full source around the proposed130s stop and after it** (e.g. original125–157s), existing sections, possible natural rests/phrase cadences and stereo/layer structure; separate what can be measured from what only a listener can decide. Identify one or two source-clock **musically defensible alternate endpoints**, if any, *without silently replacing the user's proposed130s ending*.
3. Present a clearly labeled private comparison of original context versus the **130s user-proposed cut**, and proposed alternative source interval(s) **only if separately requested/approved**. Optionally discuss musical edit/extension rather than pure DSP as a potential way to retain the intended duration.
4. No new audio, game/Wwise integration, full-cue batch or numerical-accuracy claims follow from the rejection. Any later sound change must receive its own audition, with accepted files and unmodified preregistered report69 predictions retained.

This is a feedback/status/intake document, not a finished correction.

## Superseded diagnosis — report76

The **newest explicit user statement** confirms that source130s is a musically good ending; report75's alternate-endpoint hypothesis and suggestion to investigate longer source continuations are **not active directions**. See [report76](76-s18-local-dry-wet-fade-alignment.md) for the corrected, authoritative focus on a narrowly timed fade and dry/reverb crossover. The rejection of report74 B remains valid.
