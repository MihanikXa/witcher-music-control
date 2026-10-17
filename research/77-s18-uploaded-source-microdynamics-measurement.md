# 77 — S18-3 uploaded audio: fine temporal measurement before Codex rendering — 2026-10-17

## Inputs actually analyzed

The user uploaded both **the exact full S18 audition source** (`S18-Island-alternate-pads-arrangement.opus`, SHA-256 `97663b268c063e35f0e4f6ac2f1fa3ade10289d93cf4994e46663580576ea8dc`) and **the exact old dry-only diagnostic** (`S18-3-dry-diagnostic.wav`, SHA-256 `2c4d27fb2f87c651e566e9701d0eb7acd9c843c5dbc9b05271bdd52fd5e98add`). Both SHA-256 values match prior repository evidence (report73). This is direct analysis of the original audio data, **not** a reconstruction from report73's 100ms summary. The user did not upload a combined dry+wet trial WAV; wet dynamics below come separately from prior report71–72 verified evidence and are clearly identified as such.

Both files are48kHz stereo. The full source is approximately157.01s (Opus decoder dependent end rounding). The dry diagnostic is22.2s, including2s leading and3s trailing silence. Its pre-fade active samples match the source slice `112.8–130s` at correlation>0.9999999 across test intervals with only PCM quantization differences, establishing clock alignment:

`player_time = original_source_time − 110.8 seconds`

The selected **source130.0s ending is musically correct per explicit user instruction in report76; never move it**. Original proposed S18-3 crop `112.8–130.0`, old provisional dry fade `127.8–130.0`; original preview and existing dry diagnostic are immutable references.

## Analysis method

At each original-source timestamp, calculate RMS over an **actual centered window**, average two channels' squared samples, then convert to `20 log10(RMS)` in dBFS. For source-valley robustness use window lengths20,25,50,75,100ms with10ms center increments; for the tabulation use50ms windows at5/10ms increments. Analyze the original and diagnostic dry at **the exact same source-clock centers**. Additional source-only bandpass checks use4th-order Butterworth SOS zero-phase filtering with sufficient surrounding context, approx30–200Hz,200–1000Hz,1–4kHz,4–10kHz. Channel-separated checks prevent treating stereo differences as a mono pulse.

Source Opus audio is lossy, but it is the **exact audio originally auditioned**, not a guess about the native uncompressed Wwise track. No unuploaded wet data is presented as newly measured from these attachments. The 50ms/RMS source features cannot by themselves establish phrase resolution or human auditory threshold.

## Reliable local feature: valley at source ~129.57s

| RMS window | Local near-end valley center (source) | Stereo RMS |
|---|---:|---:|
|20ms|129.570s|−32.10dBFS|
|25ms|129.5725s|−31.89dBFS|
|50ms|**129.575s**|**−31.84dBFS**|
|75ms|129.5775s|−31.38dBFS|
|100ms|129.570s|−31.06dBFS|

The local50ms minimum has a roughly**3.4dB prominence** within its neighborhood; it is a brief, real modulation, **not** a dramatic or sustained decrease of the original mix. Another weaker local valley is centered roughly**129.045s** (50ms RMS−31.02dBFS; prominence roughly2.36dB in the measured local series). Smaller stereo-level variations occur around129.32–129.46s. The most stable target for investigation is **129.55–129.60s**, equivalent to **player18.75–18.80s** (user complained at player~18.8s).

The source then **recovers and gets louder** approaching the chosen endpoint, so simply making reverb independently follow the unfaded late source is likely to generate more late energy:

| Source clock | Player clock | Original stereo RMS,50ms | Old dry diagnostic,50ms | Added dry attenuation |
|---:|---:|---:|---:|---:|
|129.450|18.650|−30.24 dBFS|−46.88 dBFS|−16.63 dB|
|**129.575**|**18.775**|**−31.84 dBFS**|**−52.78 dBFS**|**−20.95 dB**|
|129.650|18.850|−29.36 dBFS|−53.64 dBFS|−24.28 dB|
|129.750|18.950|−28.95 dBFS|−58.78 dBFS|−29.83 dB|
|129.850|19.050|−27.60 dBFS|−66.24 dBFS|−38.64 dB|
|129.950|19.150|−27.09 dBFS|−83.27 dBFS|−56.19 dB|

Values come from centered moving windows, so do not treat them as sample-accurate gain-envelope values. The original source rises roughly**4.75dB** from its129.575s valley to129.95s; the *artificial dry signal* simultaneously drops approximately**30.5dB**. These opposing trends make the handoff particularly sensitive to wet-send policy and envelope timing.

**Frequency/stereo qualification:** In the original source, energy is heavily concentrated around**200–1000Hz**. This band's50ms RMS is roughly−33.5dBFS at129.575s and−27.6dBFS at129.95s, explaining much of the late recovery. Left/right energy evolves differently; a coherent stereo fade is preferable to independent channel-by-channel pumping. This does not prove any specific chord, cadence, reverberation RT60, timbral perception or best crossover.

## What existing *separate* wet evidence establishes

From reports71–72, not uploaded wet WAVs:
- The selected independent-send reverb keeps receiving relatively strong source energy while dry attenuates. Report71 reconstructs wet rising from around−46.6dBFS at player18.6 to−36.9dBFS by19.1, creating a measured bump in the combined signal. The report71 post-fader fix depleted the room and the user heard a strong dip.
- In report72 partial-send B, dry/wet energies become comparable at player**18.6s** (source**129.4s**; both around−46.6dBFS), *before* the original source's strongest measured valley at player18.775. Its wet then rises several dB, explaining a plausible separate 'dry drop → wet takeover/plateau' perceptual structure. Partial-send C avoids the larger rebound but was still not accepted as fixing the audible handoff.
- In report74's rejected72dB/2.2s dry-only control, the apparent final dip worsened because dry disappeared too early (original/dry−35.7 versus control−63.8dBFS at player18s). Do not reuse constant-dB forced deep attenuation here.

Thus the issue is **not** evidence that130s is a poor musical endpoint. The measured micro-dip near129.575 together with the dry attenuation and wet field behavior can explain the reported timing. These are mechanism hypotheses; no candidate has been heard or approved yet.

## Implementation-ready bounded experiment

**Keep source crop112.8–130.0s and final original-source stop130.0s fixed.** Modify **only S18-3** and keep the selected report70 B, old dry diagnostic and rejected reports71–74 WAVs unchanged.

1. In Codex's local full-source preview, reproduce this50ms measurement and report any discrepancies. Examine20/25/50ms stereo RMS/bands and the ***actual*** dry/wet/combined curves (user did not upload wet here) over **source129.25–130.0s**. Inspect wet-field lag/correlation and whether it swells after the natural valley. Use equivalent player/source clock labels to prevent old off-by2s errors.
2. Tune the **local fade knee / dry-to-wet crossover alignment**, not a fixed entire0.5s fade and not a new musical ending. Three defensible provisional center times for the crossover are**129.45**, **129.575**, **129.65** source seconds (player18.65,18.775,18.85 respectively). Search only roughly**129.35–129.8s** initially; the middle target is a measured valley, outer times bracket it. A crossover center is **not** an instruction for the wet level to surge suddenly at that timestamp. Compare narrow, smoothly evolving controls, not a discontinuous preset switch. Do not assume the 'correct' point from the energy plot alone.
3. Keep a suitably long, musically gentle dry attenuation ahead of that local zone where appropriate; adjust local shape so the existing ~3dB dip is **not multiplied into a sudden ~20dB perceived hole**. Preserve stereo coherence. Let the **already-established reverb** fill gradually without a positive late wet swell, artificial hold, stepped direct-to-room change or second fade. If the wet field retains too much energy from the source's rise after129.6s, taper/stop its new excitation at a musically suitable moment while allowing the previously built diffuse state to decay, rather than abruptly turning down the wet output.
4. Render **at most three distinct handoff-timing trials** with identical fixed source cut/endpoint, plus unchanged trial B as A reference. No huge matrix of fade lengths × RT60 × gains. Include dry-only *diagnostic* components if useful, with selected wet-in-context versions clearly labeled; align candidate audio and plots on source/player clocks.
5. Measure25/50ms source/dry/wet/sum envelopes, per-band behavior, gain-law transitions and post-stop decay. Verify no clipping, new excitation discontinuity, wet rebound, double fade, changed original source material, shifted endpoint or source-clock drift. Highlight cases where source continues to rise at129.95 but the output is supposed to vanish musically. Numerical monotonicity is **not** a guarantee of perceived quality.
6. Stop for user listening verdict. Do not propagate across other pieces, modify the five+five other accepted renders, rewrite the frozen report69 prediction, or touch Wwise, game, Vortex, SoundBanks or any commercial source music rights.

**Measured conclusion:** strong near-end local valley129.57s plus opposing rebound of source and heavy imposed dry attenuation; likely useful alignment investigation within a few tenths of a second. **Not proven:** exact optimal fade curve, ideal RT60, phase/color behavior of the wet field, or an approved new ending. Keep those for the small Codex audition.
