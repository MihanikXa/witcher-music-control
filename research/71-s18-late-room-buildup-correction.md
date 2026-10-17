# 71 — S18-3 only: correct late room buildup

2026-10-17. User authorized “Sure, do a correction” after report70 identified S18-3's qualified Keep: not seamless, intrusive tail and a slight bump around player19s. **One corrected private WAV is rendered.** No other cue, original recording, frozen prediction, WMC release or game resource changed. Approval of this new file remains pending.

## Audition

Open `C:\Dev\witcher-music-control\build\music-material-selection\s18-correction-v1\index.html` manually in Chrome/Edge.

- **A:** exact original selected S18-3 trial B, linked unchanged.
- **B:** corrected natural reverb send, default audition.

Use “Hear around the bump,” compare A/B, then export Keep/Adjust/Reject, preferred version and notes. Both retain the same source/player clocks. Listen especially for an overcorrection: the new tail is much quieter and may feel too dry. No subjective listening by Codex or claim of musical success is made. M3U/copy-JSON fallbacks remain available; browser playback was not automated.

## Measured mechanism

Player19s maps to source129.8s, shortly before the dry stop at source130s/player19.2s. Reconstruction from the retained settings reproduces the selected WAV's PCM exactly. Around the reported event,100ms windows show:

| Player time | Original dry dBFS | Original wet dBFS | Original sum dBFS | Corrected sum dBFS |
|---:|---:|---:|---:|---:|
|18.6s|−46.76|−43.89|−42.73|−46.61|
|18.7s|−50.53|−42.85|−41.38|−48.56|
|18.8s|−53.79|−41.00|−40.19|−49.17|
|18.9s|−58.48|−39.31|−38.81|−50.90|
|19.0s|−65.66|−37.53|−37.32|−52.64|
|19.1s|−79.98|−36.89|−36.86|−56.84|
|19.2s|Digital zero|−37.47|−37.47|−56.86|

**Observed:** while dry fades down, the independent reverb excitation continues unfaded. Wet grows approximately7dB and the sum rebounds approximately5.9dB over18.6–19.1s. This is a pre-stop component interaction, not v1's late output-envelope attack. Post-source monotonicity checks could not catch it because it occurs before dry stop. The100ms inspection explains an actual measurable bump in the reported region; human perception of the entire correction still needs listening.

**Controlled correction:** make the existing reverb send follow the dry fade (`pre_ending_fade` → `post_fader`). Dry is unchanged, and all audio before the fade begins is sample-identical. The resulting combined signal decreases throughout the reported100ms window sequence. No general decision-rule changes or retrospective edits to report69 were made; independent sends remain appropriate in other accepted cues.

## Exact change and preservation

Only the send policy changes. Preserve:

- source112.8–130s; dry fade127.8–130s; entrance0.8s;
- natural RT60 5.5s; wet input170–3900Hz;
- **exact original wet gain0.1981443461969509**, without recalibration or normalization;
- existing FDN delays/feedback/stereo, natural release and final below−100dBFS cleanup;
-2s lead/3s final context and the original trial file.

The first post-source second falls from−41.27 to−61.26dBFS, approximately20dB quieter. This results from **less room excitation during the fade**, not an extra wet-output fade, gate, limiter or shortened RT60. It may be a larger perceptual reduction than necessary. A simple lower fixed wet mix was considered insufficient by itself: it cannot prevent continued unfaded excitation from rebuilding the field. No extra parameter matrix or alternate source cuts were produced.

New WAV: `build/music-material-selection/s18-correction-v1/audio/S18-3-B.wav`

SHA-256: `6a585f0406e9303451c9f33ef857cdb96f069d11bf1e2c2578d081bcb5e09c98`.

[Plan](71-s18-send-correction-plan.json) pins16 immutable inputs: all eleven cumulative selected files (including qualified original S18), separate S05-main B, trial metadata, user outcomes and prediction/selection records. Original source-preview identity is additionally checked. [Sanitized evidence](71-s18-send-correction-evidence.json) retains100ms dry/wet/sum measurements, hashes and verification. Full local settings/QA remain in `renders.json` and `verification.json`. The corrected candidate is **not** added to accepted selections before user approval.

## Validation

- Original reconstruction exactly matches its decoded quantized PCM.
- Dry component is exact across the full excerpt; combined pre-fade signal is identical through player17s/source127.8s.
- New48kHz stereo16-bit PCM independently decodes exactly; no clipped samples, missing material or changed context zeros.
- Post-source sustained rebound/plateau flags are absent. Dry-stop sample delta approximately0.000514FS; final cleanup begins below−154.1dBFS peak.
- All16 immutable inputs remain exact before and after rendering; all linked local files resolve. No generated audio or third-party asset enters Git.
- All **200 existing Python tests pass**. No new DSP law was introduced; the existing tested post-fader mechanism is reused. Offline page/export, storage-failure and A/B handlers pass. Actual browser playback and subjective quality remain unverified by Codex.

```text
python tools/cue_s18_correction.py --output build/music-material-selection/<fresh-s18-output>
node tools/test_cue_edit_export.cjs build/music-material-selection/<completed-s18-output>/index.html
python -m unittest discover -s tools -p "test_*.py"
```

The helper rejects another cue ID or existing output directory. It does not regenerate other trial cues, change report69 predictions, touch Wwise/Vortex/saves, or broaden copyrighted-audio permissions.

**Next:** user listens only to this A/B correction and exports a verdict. Preserve both files. If B is too quiet, that is specific new feedback for a bounded follow-up, not authorization to retune the rest of the library.
