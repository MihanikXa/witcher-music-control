# 64 вЂ” Five-cue continuous reverb-tail correction

2026-10-17. **Actual private v2 audio exists.** Conventional decay is the primary audition; freeze is optional. This completes the small corrective rendering task, not musical approval or authorization to re-render all24. No listening by Codex, game/Wwise/Vortex activity, bank generation or distribution occurred.

## Listen and decide

Open `C:\Dev\witcher-music-control\build\music-material-selection\cue-edits-v2\index.html` manually in Chrome/Edge. Order: **S05-short в†’ S11-short в†’ S12-1 в†’ S07-b в†’ S04-b**. Each card defaults to **B**, has an ending jump, Keep/Adjust/Reject, an independently chosen preferred treatment, notes and JSON export/copy fallback. Source clocks and added context are separate. The M3U fallback is beside the page.

- **A:** the existing v1 C WAV, referenced unchanged rather than re-rendered. This is the old freeze treatment, not v1's dry A.
- **B:** continuous-send natural decay, primary candidate.
- **C:** continuous-send field, actual input-closed freeze at dry stop, immediate single release.
- **B-long:** two additional natural decays, for S11-short and S07-b only.
- S07-b also offers the user's accepted **v1 conventional B**, unchanged. Accepted S05-main B is a separate comparison reference.

There are **five cue cards,12 new stereo PCM WAVs (94,236,944 bytes),18 version choices referencing six existing v1 files**, plus the S05-main reference. Longer B/C files intentionally outlast v1; player position switching keeps the same source-relative clock, not equal percentage through the file. All new files have2s leading and3s final digital silence. Longer exported length alone is not claimed as longer reverberation.

## Root cause and exact correction

The user's audible findings remain verbatim in [report62 JSON](62-user-cue-edit-decisions.json). The shared code mechanism is visible in `tools/cue_freeze_dsp.py::render_variants`: it introduced wet audio near `freeze_at`, increased it while dry faded, held an independent output envelope and then faded again. Report62 correlates S04-b's57s capture with the reported player24вЂ“25s increase. That is strong code/timing evidence, not retrospective listening by Codex.

The new `tools/cue_freeze_dsp.py::render_continuous` (line201 onward) is deliberately separate. The legacy function is unchanged for v1 reproducibility:

1. Preserve report61's resolved source ranges, entrance ramps and dry fades. Filter only the reverb send, using each source's existing high/lowpass bands; dry remains otherwise unchanged.
2. Feed the16-delay FDN with the **whole excerpt's post-fader source from its entrance**, not a late cropped prime. Wet output is audible throughout at one fixed gain. There is no late wet attack or normalization at the handoff.
3. Calibrate gain once against up to4s of **pre-fade** dry/wet RMS. Targets areв€’20 toв€’22dB wet/dry RMS. Retain original dry level; no limiter, source boost or per-ending normalization. C uses B's exact gain and pre-stop field; longer B is independently matched to the same pre-fade ratio. This controls level bias without pretending unequal decay lengths have equal perceived loudness.
4. **B:** continue feeding the fading source until actual dry stop, including causal input-filter residue, then let RT60 feedback losses dissipate energy. Wet output gain stays constant. There is **no imposed hold or separate audible output fade**.
5. **C:** retain the identical established field until actual dry stop; close new excitation and interpolate feedback losses to unity over150ms. At the same time begin one smooth log-gain release: `10**(-3*(t - 0.15*(1-exp(-t/0.15)))/rt60)`. Its initial slope is continuous, it has no hold, and it reaches roughlyв€’60dB after one RT60. It does not freeze a chord at fade start while dry harmony continues changing. Internally the field is genuinely lossless after the transition; the output releases continuously. This design intentionally avoids an exaggerated separately announced freeze layer, and may sound close to B.
6. Render at least10s or1.65Г—RT60 beyond the crop. Only the final100ms is safety-ramped, **after its unmodified signal peak is belowв€’100dBFS**. This cleanup cannot substitute for sufficient natural decay; the renderer fails if that threshold is not reached. No late boost is applied to already quiet endings.

No third-party processor implementation was copied. The existing original FDN/delay/filter topology is retained. No subjective claim about diffuseness, metallic coloration, harmonic resolution or optimal wetness follows from this design.

## Source clocks and tailored settings

| Cue | Original source crop | Original dry fade | Primary B RT60 | Longer B | Continuous wet/dry target |
|---|---|---|---:|---:|---:|
| S05-short |0вЂ“23.7s|23вЂ“23.7s|5.5s|вЂ”|в€’21dB|
| S11-short |0вЂ“20s|18вЂ“20s|6.5s|9s|в€’20dB|
| S12-1 |5вЂ“21s|20.4вЂ“21s|4.5s|вЂ”|в€’22dB|
| S07-b |81вЂ“115s|111вЂ“115s|7s|10s|в€’21dB|
| S04-b |34вЂ“60.757333s|59.757333вЂ“60.757333s|5s|вЂ”|в€’22dB|

These are provisional engineering settings, not ear-tuned prescriptions. All cut/fade clocks match retained v1 resolved settings; authoritative report58 wording is unchanged. Configuration and immutable historical input hashes are in [64-continuous-tail-plan.json](64-continuous-tail-plan.json).

**S04-b explicit onset edit:** keep the34s crop start, but set source34вЂ“37s to zero, then use a350ms raised-cosine entrance over37вЂ“37.35s. With2s player lead, the repaired entrance begins at player5s. This interprets the user's вЂњaround3sвЂќ as crop-relative; it is deliberately labeled provisional. It removes **all** source material in that initial3s, not a frequency-isolated note. The original interval has RMSв€’25.58dBFS/peak0.47835FS; v2 has exact zero there. Signal analysis proves removal, not subjective identification of which sound was the вЂњbleep.вЂќ No later material or endpoint moves. A and the full-source reference preserve the original entrance for comparison.

## Measured results and limits

Independent results/hashes: [64-continuous-tail-evidence.json](64-continuous-tail-evidence.json). Full local per-component50ms envelopes,250ms release measurements, internal field-energy traces, processing settings and per-file hashes are in `renders.json`; each card links a local dry/wet/combined SVG. All12 new files independently decode with trusted installed FFmpeg and match the written48kHz stereo16-bit PCM exactly.

| Cue / variant | First post-stop second RMS | Peak before final safety cleanup |
|---|---:|---:|
| S05-short B |в€’53.6dBFS|в€’148.7dBFS|
| S11-short B / B-long |в€’56.7 /в€’53.3dBFS|в€’141.7 /в€’138.2dBFS|
| S12-1 B |в€’71.8dBFS|в€’189.0dBFS|
| S07-b B / B-long |в€’68.3 /в€’60.1dBFS|в€’152.7 /в€’147.3dBFS|
| S04-b B |в€’105.0dBFS|в€’210.4dBFS|

Observed:

- No clipping; maximum new decoded peak approximately0.868FS. Source-clock cuts/dry fades and exactly zero lead/trail context pass. No dry-stop seam exceeds0.02FS sample delta; individual metrics are retained.
- All12 new post-source releases have **no sustained >3dB rebound and no detected two-second audible plateau** under the defined250ms RMS diagnostic. This does not prove that every musical or perceptual artifact is absent.
- The gain-law gate separately forbids any late wet increase before stop, any post-stop conventional output fade, and any held/rebounding freeze release. It is not dependent on naturally evolving music being monotonically quiet.
- S11-short's whole-transition diagnostic flags a rise of about3.51dB. The **dry-only** control already rises3.58dB over that region; it is not a hidden processing failure silently dismissed by relaxing a threshold. This musical-dynamics flag remains recorded for listening. Other pre-stop fluctuations are recorded too.
- Settled C internal state-energy drift stays below1eв€’10 while its external release decreases; B retains real RT60 losses. Synthetic impulse/tonal controls and original freeze tests distinguish state freeze from ordinary decay.
- S04-b is **already effectively silent at its original dry stop**; v2 does not manufacture a late held chord to make a tail appear audible. S12-1's post-stop tail is also quiet. Listen across the whole ending: whether either needs a stronger or differently colored *continuous* send is unresolved. Arbitrarily amplifying those endpoints would repeat the rejected defect.
- Longer B actually changes feedback decay, not just padding. Synthetic decay-rate tests distinguish3s from7s RT60. Real paired S11/S07 measurements show more remaining energy at source stop with the longer alternative. It may also produce more wash, requiring listening.
- All34 v1 WAV hashes and v1 metadata are preserved. Ten historical report/feedback inputs58вЂ“63 and the original source preview payloads match. No v1 source file or accepted release is rewritten by these tools.
- Independent S11-short regeneration yields byte-identical B/C/B-long. Single-cue regeneration does not require the rest of the library.

`tools/cue_tail_v2_qa.py::verify` (line15) independently decodes every linked variant, checks stored hashes/frame counts/context/levels, compares measured50ms combined envelopes to pre-quantization proof, verifies fixed source boundaries, B/C prefix equality, onset removal, freeze evidence and actual links. It fails on post-stop review flags or premature cleanup. This is deliberately an audition gate, not a claim of musical naturalness.

## Tests and interface verification

All **191 Python tests pass** with `python -m unittest discover -s tools -p "test_*.py"`, including seven new continuous-tail regression tests. They cover early active wet send, real decay, identical B/C pre-stop field, stable freeze with immediate release, zero onset interval without clock shift, invalid/unsafe render rejection, decay-rate change and deliberately defective dip/swell/hold/second-fade controls. `validate_wet_control` rejects late attacks, holds and rebound envelopes. Existing184 tests, including production bank/regional gates, continue passing.

The first attempt to invoke the new test by module path failed Python's tools import search; the repository's normal discovery invocation passed. No implementation threshold was relaxed to hide that invocation error.

Offline Node client tests pass for both the new five-card page and the old24-card page: B default selection, position switching, play/stop coordination, disabled local storage, independent preferred-treatment selection, Blob JSON export and copy fallback. No real-browser playback or subjective listening is claimed. Prior file-URL automation restrictions remain respected; no server/browser bypass was attempted. Manual Chrome/Edge opening and real listening remain user actions. The page has only local resources and16 verified audio/chart links.

The first S05 control remains in ignored `cue-edits-v2-S05-first-control/`; it preceded added control-law diagnostics. The final pack is **cue-edits-v2/**, not that control. Earlier v1 failures/evidence and24-cue pack remain intact. The old metadata snapshot inside v2 records cleanup of unused legacy DSP labels; no PCM changed during that metadata-only correction.

## Reproduce and next gate

```text
python tools/cue_tail_v2.py --output build/music-material-selection/<fresh-v2-output>
python tools/cue_tail_v2.py --output build/music-material-selection/<fresh-single-cue-output> --only S11-short
python tools/cue_tail_v2_qa.py --folder build/music-material-selection/cue-edits-v2 --output build/music-material-selection/<fresh-proof.json>
node tools/test_cue_edit_export.cjs build/music-material-selection/cue-edits-v2/index.html
python -m unittest discover -s tools -p "test_*.py"
```

No existing output directory is overwritten. Original tools, sanitized plan/evidence and this report are committed; recordings/previews remain ignored and private. No licence/rights permission for integration follows from private editing.

**Next:** user listens only to this five-cue corrective page and exports decisions. Prefer B unless the ears favor an alternative; refine an individual cue if necessary. Do not ask for remaining v1 review, propagate to all24, add gameplay triggers or integrate audio before this listening gate.
