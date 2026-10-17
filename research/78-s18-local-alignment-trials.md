# 78 — S18 local dry/reverb alignment trials

2026-10-17. Three final private comparisons implement report76–77's source-centered timing experiment. They preserve source112.8–130.0s and the explicitly confirmed130.0s musical endpoint. None is accepted yet. Report74 B remains rejected: the user said its dip was much more sudden. No other excerpt was rendered or altered.

## Audition

Open `C:\Dev\witcher-music-control\build\music-material-selection\s18-local-alignment-final\index.html` manually in Chrome/Edge. A links the exact qualified report70 selection. T1/T2/T3 are the earlier, natural-dip-aligned and later trials. “Hear from17.5s” gives context before the disputed handoff and continues through the complete tail; full-cue playback is available. Expand the references to compare the original full recording or the unchanged dry diagnostic. Only one player runs at a time.

The correct clock relation remains `player = source −110.8s`; source130.0s is player19.2s. The32.2s files include2s lead,17.2s source,10s natural-tail rendering and3s final context silence. No subjective listening or actual browser playback by Codex is claimed. The useful listening decision is which, if any, avoids the dip/room-takeover/second-fade impression. No candidate is automatically preferred from the measurements.

## Reproduced source and reference evidence

`tools/cue_s18_alignment.py` uses the original audition Opus, SHA256 `97663b268c063e35f0e4f6ac2f1fa3ade10289d93cf4994e46663580576ea8dc`, decoded with the trusted installed FFmpeg to48kHz stereo. It reconstructs the old selected combined WAV and existing dry-only diagnostic **exactly at quantized PCM level** before evaluating components. It never substitutes a different composition or source clock.

Centered stereo RMS averages both channels' squared samples; it does not sum channels to mono. The local scan uses2.5ms center spacing over129.50–129.65s:

| Window | Measured minimum source center | dBFS |
|---:|---:|---:|
|20ms|129.5725|−32.11|
|25ms|129.5700|−32.09|
|50ms|129.5750|−31.84|
|75ms|129.5800|−31.40|
|100ms|129.5725|−31.11|

The50ms result matches report77. Fine-window minimum timestamps differ by a few milliseconds and the25ms minimum is about0.2dB lower than its earlier table. The exact cause of those small analysis differences is not established; they do not change the stable local-valley finding. The source recovers from−31.836dBFS at129.575 to−27.088 at129.95: **4.748dB**. Its200–1000Hz band recovers from−33.50 to−27.62dBFS, whereas1–4kHz changes only from−37.67 to−37.02. The recovery is frequency dependent.

The actual old16-bit dry WAV measures−52.785dBFS at129.575 and−83.275 at129.95, confirming about20.95/56.19dB added attenuation. Floating-point reconstruction is about0.08dB quieter at the latter near-quantization-floor measurement; the decoded original dry PCM remains exact. [Full evidence](78-s18-local-alignment-evidence.json) records20/25/50/100ms source, actual dry, reconstructed dry/wet/sum and per-band trajectories.

The reference wet field continues rising while the direct source disappears. A200–1000Hz20ms-energy-envelope lag search over0–1000ms has only weak maximum correlation0.281 at0ms. It does not identify a useful single modulation lag and must not be described as a measured acoustic delay. The causal, diffuse field retains earlier excitation; source modulation and wet energy cannot be aligned by assuming one fixed offset.

## Exact local construction

All three trials retain the existing127.8–130s ending-fade window,0.8s entrance,5.5s conventional RT60,170–3900Hz input filtering, fixed wet gain `0.1981443461969509`, original FDN/stereo behavior and constant wet-output gain. They change two local controls around one common center:

| Trial | Center, source/player | Local support / reverb-input taper, source |
|---|---|---|
|T1 Earlier|129.450 /18.650|129.200–129.700|
|T2 Natural-dip aligned|129.575 /18.775|129.325–129.825|
|T3 Later|129.650 /18.850|129.400–129.900|

1. **Direct gain:** `cue_freeze_dsp.py::aligned_dry_envelope` delays the *progress of the existing fade* by at most100ms under a compact raised-cosine bell of width500ms. This alters only the gain trajectory, not waveform timing or pitch. The original sampled cosine curve is retained exactly outside that local support. Both endpoints remain fixed; gain stays bounded and decreases without a hold or reversal. The100ms offset is a provisional engineering choice, not a fitted optimal musical setting or an inverse-source-envelope gain correction.
2. **Reverb excitation:** the already-established independent send tapers smoothly from1 to0 across the same500ms support. No new source excitation follows its end; causal input-filter residue and the existing field decay normally. Wet output is not turned up, held, gated or given a new ending fade. Thus the source's late recovery cannot feed the room indefinitely while direct sound vanishes.

This is an opt-in local envelope experiment within the existing conventional-reverb architecture. Legacy defaults remain unchanged. It does not reuse the rejected constant-decibel release, move the130s endpoint, freeze a changing chord or apply inverse-envelope pumping. The original dry samples **after** the local window are exact again, so any improvement near the stop relies on the altered room history rather than extending the source.

## Actual combined behavior and remaining risks

Centered50ms combined RMS, dBFS:

| Source / player | A unchanged | T1 Earlier | T2 Dip aligned | T3 Later |
|---|---:|---:|---:|---:|
|129.450 /18.650|−42.99|−42.33|−42.54|−42.90|
|129.575 /18.775|−41.34|−42.88|−41.42|−41.16|
|129.650 /18.850|−39.82|−43.01|−40.78|−39.91|
|129.750 /18.950|−38.77|−45.24|−42.64|−40.91|
|129.850 /19.050|−37.54|−47.77|−44.83|−42.70|
|129.950 /19.150|−37.03|−50.94|−47.05|−44.73|

At the source valley the direct component is−50.89/−49.29/−49.96dBFS in T1/T2/T3, compared with old−52.78. Local imposed attenuation is reduced by roughly1.9–3.5dB, not cancelled or boosted away. T1 avoids the reference's strong post-valley rise in this table, but has a briefly near-level region and a quieter final tail. T2/T3 still rise about0.64/1.25dB between129.575 and129.65. Those small dynamics and the changing direct/room spectrum may still be audible. **No clean perceptual result is asserted.** None is accepted merely because the post-stop checks pass.

The band tables show actual source/dry/wet/combined evolution, not a guarantee of timbral seamlessness. No new filter switch exists, but the established band-limited room can still sound perceptually separate from the direct source. That remains a listening risk alongside an overly quiet T1 ending or residual T2/T3 swell.

## Verification, reproducibility and preservation

All208 repository Python tests pass, including four new local-envelope/send tests. They check exact gain restoration outside the support, monotonic bounded gain, rejected invalid/reversing layouts and smooth excitation closure. The legacy rejected curve still has archival technical tests; their passing does not approve it musically. The authoring helper additionally proves exact pre-window combined audio, exact post-window direct audio, zero further new excitation after the local send window and exact baseline/dry reference PCM reconstruction.

All three stereo48kHz16-bit WAVs independently decode to the expected PCM. No clipped samples; shared peak0.133423FS. Final safety cleanup begins below−142.9dBFS peak (T1−147.5,T2−144.6,T3−143.0); no natural tail is cut at an audible level. Existing250ms post-stop checks flag no sustained>3dB rebound or2s plateau. They do **not** rule out the short local perceptual defects described above. HTML JavaScript syntax and all six local audio links pass static checks; actual browser/audio listening remains untested by Codex.

Eleven pinned selections, the separate S05-main reference, frozen prediction69, user outcomes and original trial metadata are preserved through the16-input hash gate before/after rendering. No acceptance record is rewritten. Original source/audio, failed captures and accepted WMC packages remain ignored and untouched.

Final new WAV hashes:

- T1: `f7b2b7cc6f9ed1b9ab1f14edf0a8546981ed96bd54e939bc9827cc3f01440003`
- T2: `3a199b2b6b2a1cb5525ef90e1007006b826b9e5fa5d00b286714a1f53a7c2139`
- T3: `5951314953b4df6708fc761d11624a239a44c25e0404dc6b353f8074330083dd`

Run the helper with a **fresh** ignored output directory to reproduce the three final candidates:

```text
python tools/cue_s18_alignment.py --output build/music-material-selection/<fresh-output>
python -m unittest discover -s tools -p "test_*.py"
```

Bring-up evidence is retained under ignored `s18-alignment-v*` directories. Some attempts stopped on bounds/reference checks; a component-array clock-index mistake was corrected before final measurement, and a failed exact-restoration test found tiny changes outside the intended local region. These checks were fixed rather than relaxed. Superseded internal send-only and Gaussian-shape controls were also rendered, exceeding the intended three-render limit during bring-up; they are not delivered as additional listening choices. The delivered set is exactly the three final compact-support trials plus the unchanged A. No further variants are generated in this task.

**Next:** user listens only to this local comparison and reports a preference or rejects all three. Keep130s fixed. No other cues, Wwise, game, Vortex, SoundBanks, scheduler, packaging or distribution operation occurred.
