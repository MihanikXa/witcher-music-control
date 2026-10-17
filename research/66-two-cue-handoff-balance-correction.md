# 66 — Two unresolved cue handoffs: v3 listening comparison

2026-10-17. User authorized proceeding after report65. **Only S05-short and S11-short are revised.** Three accepted v2 versions, all earlier audio and user feedback remain intact. No Wwise, game, Vortex, scheduler, bank, installation or distribution work occurred.

## Ready private comparison

Open `C:\Dev\witcher-music-control\build\music-material-selection\cue-edits-v3\index.html` in Chrome/Edge. Listen to **A → B → C**, optionally Dry-only, then export decisions. Use player timestamps in new notes.

- **A:** the exact rejected v2 **natural B**, unchanged. This is not v1 A or a newly processed control.
- **B:** new primary conventional reverb.
- **C:** controlled **conventional** alternative. **C does not mean freeze in this comparison.** Genuine freeze remains implemented and preserved; it is not part of this particular pre-stop correction.
- **Dry:** new B's exact source edit without additional reverb, diagnostic only.

Two cards, four new wet renders and two dry controls: **six new stereo48kHz/16-bit PCM WAVs,42,869,064 bytes**. Two older references are linked unchanged. Each excerpt includes2s leading and3s final digital silence; a full-original-source player has its original source clock instead. Ending jump, play-one-at-a-time, position-preserving switching, verdict, independent preferred treatment, notes and JSON export/copy fallback are present. An M3U fallback is beside the page.

## Findings: what is established and what is not

**User-observed:** report65 says S05-short still jumps into a tail around player25s and S11-short has a fast fade/handoff around20ish in both v2 B/C. These judgments override any earlier inference that passing post-stop measurements established audible success.

**Signal/code-observed:** v2 B/C are identical before dry stop. The original cosine dry fades force the dry/room balance to change quickly as direct music approaches zero, even while wet gain is fixed. For S05-short, measured250ms combined windows around the fade go from approximately−23.5 to−32.5 to−48.3dBFS. In S11-short the late fade moves through approximately−36.2,−42.4 and−50.9dBFS. The source itself remains substantially audible through these intervals; these are not merely already silent source endings. The wet component is around20dB below dry before fade and also loses excitation as dry fades.

**Supported explanation, not proven perceptual cause:** rapid loss of direct sound and a weak, differently colored remaining room field can be heard as switching to another source, without a numerical volume rebound. Our earlier post-stop monotonicity checks could not reject that fast *pre-stop* handoff. This accounts for a plausible mechanism and guides a test; no subjective listening by Codex or definitive root-cause claim follows.

## Bounded correction and controls

All new wet versions use an established fixed wet balance targeting **−14dB wet/dry RMS** over the original pre-fade calibration window. That is7dB stronger than v2 for S05-short and6dB stronger for S11-short. It is present throughout the excerpt, not increased at the cut. There is no dry boost, compressor, normalization or wet output attack/hold/second fade. Greater room presence could itself be undesirable; listening must assess wash and harmonic emphasis.

The new optional `send_policy='pre_ending_fade'` in `tools/cue_freeze_dsp.py::render_continuous` (line201; policy at228) separates the room excitation from the ending dry fade. Original source audio continues feeding the room until the **same source stop**, with only a20ms excitation-stop guard. The entrance ramp is retained. Causal input-filter residue and the field then decay naturally. There is no audio beyond the approved crop and no sustained/frozen gain compensation. RT60, delays, feedback, stereo matrix and input filters remain the region-independent v2 settings. Default `post_fader` is unchanged and still follows the dry fade.

| Cue | New B | New C | Preserved clocks |
|---|---|---|---|
| S05-short | Pre-ending-fade send; dry fade21.7–23.7s | Same room/send/gain; old provisional dry fade23–23.7s | Crop0–23.7s; same end |
| S11-short | Pre-ending-fade send; dry fade18–20s | Same gain, ordinary post-fader send; dry fade18–20s | Crop0–20s; exact user fade18–20s |

**S05-short timing qualification:** its original700ms fade was our report61 fallback; the user specified the23.7s split, not that700ms fade. The new B provisionally begins fading1.3s earlier, with the same ending/crop. The page makes this explicit; C retains the old timing. This does not alter S05-main's user-specified42–47s fade or any accepted render.

Both new variants are calibrated once against the same original source context and use the **same exact wet gain**, not independently normalized tails. S05 B/C therefore isolate the dry-fade shape/duration; their wet field is identical. S11 B/C isolate whether room excitation follows the ending dry fade. They are sample-identical up to the respective comparison start. Against A, however, both new treatments intentionally have more room presence. A favorable comparison against A alone would not establish that timing rather than louder reverb was responsible.

No additional freeze render is useful for isolating a defect shared before v2's B/C divergence. This is a bounded choice for these two unresolved cues, not deletion of freeze or a universal conventional-reverb policy.

## Measured results

`tools/cue_handoff_v3.py::handoff_metrics` (line21) measures **fixed player-clock**250ms windows spanning the complete handoff. These metrics compare engineered changes, not musical quality. The windows are23–26.5s for S05 and19–23s for S11, with identical alignment for all compared versions.

| Cue | Largest adjacent250ms decline: A v2 | New B | New C |
|---|---:|---:|---:|
| S05-short |15.87dB|5.35dB|8.95dB|
| S11-short |8.45dB|4.22dB|5.41dB|

This is an improvement in measured handoff steepness, **not proof that an audible jump is solved**. Native source dynamics and any remaining perceived timbre jump still require listening. Dry-only eventually reaches exact silence, so its floor-related dB differences are not meaningful tail-quality comparisons.

Independent readback gate `tools/cue_handoff_v3.py::verify` (line117) checks all payload hashes, exact frame counts, stereo PCM, context zeros, source-cut/user-wording preservation, decoded50ms RMS against stored pre-quantization proofs, per-variant policies/fades, common gain, unchanged RT60, B/C prefix identity, dry-stop seams, decay completion and no post-stop sustained-rebound/plateau flags. It checks all **51 retained input fingerprints**, including34 v1 and12 v2 WAVs, metadata and feedback. The three accepted versions are among those unchanged v2 payloads.

Observed maximum dry-stop sample deltas: approximately0.00190FS for S05 and0.00711FS for S11. Peaks at the final100ms safety cleanup are below−138.96 and−126.27dBFS respectively, before any cleanup ramp. No clipping or missing/silent active passage was found. These checks do not certify absence of every audible artifact.

Fresh independent regeneration reproduces all six new WAV hashes exactly. Full50ms dry/wet/sum envelopes, energy traces, actual gains and output hashes remain in ignored `renders.json`. [Sanitized evidence](66-handoff-balance-evidence.json) retains measured readback windows, hashes, seams and regeneration results; [plan](66-handoff-balance-plan.json) pins all approved changes and immutable inputs.

## Tests, reproduction and limits

All **193 Python tests pass**, including two new regression tests for pre-ending send: dry/cut and pre-fade prefix preservation, increased remaining natural field energy, safe completion, unsupported policy/onset/guard rejection. All previous191 tests continue passing. Offline client tests pass for the two-card player, B default, independent preferred selection, playback coordination, position changes, export Blob and disabled-storage copy fallback.

No real-browser playback or subjective listening was performed. Existing file-URL browser restrictions were respected; no localhost or alternate-browser workaround was used. Manual opening remains the supported user action. No software installed or third-party processor code used.

```text
python tools/cue_handoff_v3.py --output build/music-material-selection/<fresh-v3-folder>
python tools/cue_handoff_v3.py --verify --output build/music-material-selection/<completed-v3-folder>
node tools/test_cue_edit_export.cjs build/music-material-selection/<completed-v3-folder>/index.html
python -m unittest discover -s tools -p "test_*.py"
```

**Next:** user auditions these two cards and exports the result. Preserve accepted S12-1 C, S07-b B and S04-b C. Do not propagate a preset to all24 or claim either new ending is approved. If B still sounds wrong, the smallest further correction should follow the specific variant/time feedback, rather than another unbounded tail matrix or gameplay integration.
