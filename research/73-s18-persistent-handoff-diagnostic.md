# 73 — S18 persistent handoff failure: isolate before further tuning

2026-10-17. Exact user feedback on the latest comparison:

> There still that dip that 18.8s, then constant volume then fade effect that we tried to correct for a long time

No new version is accepted. The message does not specify which partial-taper variant was heard; do not invent separate B/C verdicts. Reports71–72 did not establish perceptual success and their safety/monotonicity metrics must not be presented as solving the complaint.

## Finding and limit

The same ending dry fade was retained throughout the send changes. At the disputed cue time it sharply removes direct sound while the remaining field follows another trajectory. Actual unfaded source and dry-only100ms RMS illustrate this:

| Cue player time | Unfaded original source dBFS | Existing dry edit dBFS |
|---:|---:|---:|
|18.3s|−29.31|−39.06|
|18.6s|−30.20|−46.76|
|18.8s|−29.56|−53.79|
|19.0s|−27.52|−65.66|
|19.1s|−26.88|−79.98|

The original source does not show a comparable energy collapse. It does **not** follow that its harmony/timbre is subjectively ideal or that the dry fade is the sole audible cause. Changing the send moved the dry/room crossover: report72 B retained a dip/rebound, while C produced a near-level crossing before continuing decay. Those are the very behaviors the user rejects. Continuing to alter send exponents without isolating the perceived handoff would repeat the same uncertain exercise.

**No new reverb “fix” is rendered in this turn.** A diagnostic asks whether the dry fade alone already has the objectionable impression, or whether that impression emerges upon adding the room. This is missing listening evidence, not a permission requirement or a new approval round for another claimed correction.

## Private diagnostic

Open `C:\Dev\witcher-music-control\build\music-material-selection\s18-handoff-diagnostic\index.html`.

It provides:

- **Dry-only control:** exact existing source112.8–130s, entrance0.8s and dry fade127.8–130s; no added reverb. Same2s lead; source stop at player19.2s;3s final digital silence. One new diagnostic WAV, not an alternative cue ending.
- **Unfaded full original:** existing source reference, with a button to source128.8s (equivalent to cue18s). No new source crop or original-recording change.
- **Latest rejected/unsuccessful partial C reference:** existing file, with a button to cue18s. This is a diagnostic reference, not a claim the user specifically selected C in the latest feedback.

Playback is one at a time. No existing preview was edited, no new wet treatment or output-gain shaping was produced, and no original source endpoint was moved. The useful human observation is: **does the dry-only control have that same objectionable dip near18.8s?** If yes, the next correction must revisit the dry-release shape/timing; if no, room coloration/crossover remains the target. That fork is conditional, not a proven diagnosis.

## Verification and preservation

`tools/cue_s18_diagnose.py` reconstructs the exact dry envelope from the selected trial's settings, independently writes/decodes stereo48kHz16-bit PCM, checks quiet context/headroom, records source hash, verifies eleven selected hashes before/after and leaves prediction69 unchanged. [Diagnostic evidence](73-s18-diagnostic-evidence.json) preserves the exact user message and source/dry measurements. No algorithmic preference score or new approval is assigned.

All201 existing Python tests pass. One empty measurement window at the exact dry-stop endpoint was removed from the diagnostic table; strict finite JSON serialization now rejects such data. The audio was unaffected. No new DSP mechanism is introduced. No real-browser or subjective playback by Codex is claimed. The diagnostic is a simple local player rather than the previous verdict/export client; replies can be made directly in chat.

All recordings remain private/ignored. No Wwise, game, Vortex, save, scheduler, mod packaging or library rollout operation occurred. All previously accepted cues and failed S18 evidence remain intact.

**Next:** obtain the single dry-only listening distinction before generating another correction. Stop repeating taper variants or calling a smooth numeric curve a musical solution.
