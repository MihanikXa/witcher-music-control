# 84 — Five targeted private cue corrections

2026-10-17. Report83's bounded production pass is complete: **five corrected primaries, no diagnostic alternatives**, at `build/music-material-selection/five-cue-corrections-v1/index.html`. All new renders are **pending user listening**, not accepted. Eighteen report82 selections and separate S05-main B v1 remain hash-exact. No other musical cue, original recording, historical feedback/prediction, Wwise, bank, game or Vortex resource was modified.

## Listening package

Open the local index in Chrome/Edge. B is corrected; A links the unchanged preferred report81 render (S04-a C; B on the other four). Each card includes full original source, cuts, processing, a problem-area button, measurements, Keep/Adjust/Reject, preference and notes. One export records all five. The first2s and final3s remain audition context. S04 A/B switches preserve absolute source time despite the opening trim. Turning off position retention permits a start-to-start comparison.

S14 is eligible for future Sparse consideration under the user's report82 decision. The new page does not impose the historical comparison-only exclusion. This is separate from approval of either current ending, future authored-route protection, implementation or redistribution rights. Old export flags remain unchanged.

## Source evidence and decisions

Authoritative user instructions: `research/82-user-remainder-cue-decisions.json`, five Adjust rows; timing/requirements: report83. Original report81 sources and hashes are pinned in `research/84-five-cue-correction-plan.json`. `tools/cue_five_corrections.py::measured` retains source20/25/50/100ms stereo RMS and50ms band trajectories. Frequency energy does not identify a particular instrument with certainty; the low-instrument explanation is supported by band distribution, not source separation or subjective listening.

| Cue | New source clocks | Dry release | Room | Correction |
|---|---|---|---|---|
| S04-a | **3.150–34.000s** |31–34s unchanged|Exact retained C PCM,5.5s independent-send room|Original RMS stays near−91.7dBFS until~3.25s, then rises through~5s. Remove3.15s of unused source prefix, preserving the gradual musical entrance and every later preferred C PCM frame. The standard2s lead remains.|
| S16-1 |0–**42.300s** unchanged|**35–42.3s**,7.3s half-cosine|8s RT60,−14dB target,HP190/LP3400Hz,post-fader|Source remains around−25dBFS at33–42s. Previous40.1–42.3s fade imposed a fast disappearance. Spread attenuation across an earlier audible interval; room follows the fading source with no secondary output fade.|
| S18-2 |61–**100.800s**|**97.5–100.8s**|Retained6s RT60,−20dB target,HP170/LP3900Hz,post-fader|Original declines from~−15dBFS around98s toward~−25dBFS around100s, then returns after~101s. End before that return; rejected later samples enter neither dry nor reverberation. New cut is an engineering proposal, not a user-certified cadence.|
| S14-1 |0–**64.500s** unchanged|62.3–64.5s unchanged|**8.5s RT60,−13dB target,HP80/LP3000Hz**,post-fader|Source60–64.5s30–120Hz RMS~−25.6dBFS exceeds120–250Hz~−31.8dBFS. Old HP250 attenuated this range; lower the filter and extend actual decay. Constant room level, no freeze/hold or late wet attack.|
| S14-2 |64.5–**132.000s** unchanged|Retained131.98–132s quiet guard|**9s RT60,−14dB target,HP80/LP3000Hz**,post-fader|Original falls from~−24dBFS at128s to−40dBFS at130.5s and−63dBFS at131.5s. Prior version has no room. Continuously feed this passage's own declining source into restrained low-aware room before it disappears; no earlier passage/harmony is substituted.|

Post-source dry stops occur at player32.85s,44.3s,41.8s,66.5s and69.5s respectively. S14-1's reported player65s maps to source63s; S14-2's68s maps to130.5s. The new S18-2 stop precedes the approximate player42s rejected rise; all source100.8–112.7s material is omitted. Source101s is only an approximate user clock: measured resurgence is evident around101.25–101.5s.

S14 corrections use a **fixed0.85 amplitude headroom multiplier (−1.41dB) throughout dry and room**. This replaces S14-2's previous0.964920 headroom factor, a further~1.10dB reduction. It prevents clipping without compression, tail normalization or a late level change; A is unchanged and therefore slightly louder in its dry passage. Do not infer preference from loudness alone. S04/S16/S18 have no new overall headroom scaling.

## Measured playback-file behavior

These are decoded/analysed PCM results, **not subjective listening claims**. `technical` examines original, dry, wet and actual summed signal; old wet is reconstructed from decoded A minus original dry, so contains PCM quantization residual. Corrected dry/wet come from actual DSP components. Headroom-scaled candidates are checked against the exact scaled source (multiplication order preserved); original unscaled source measurements remain separately available. Existing strict source equality was not relaxed.

S16-1 combined50ms RMS at source36/38/40/41/42s changes from approximately−26.8/−26.8/−25.7/−28.7/−47.7dBFS to **−27.5/−29.3/−38.5/−47.0/−60.4dBFS**. This is a materially earlier progressive release, not a longer blank export. Fine-window maximum extra drop changes3.77→3.59dB/100ms: natural note modulation still exists, and the metric alone does not establish musical smoothness.

Corrected post-source whole-second stereo RMS:

| Cue | First second | Second | Third | Fourth | Fifth |
|---|---:|---:|---:|---:|---:|
| S04-a |−57.1|−68.7|−81.1|−91.3|−102.5|
| S16-1 |−66.4|−73.9|−81.3|−88.7|−95.4|
| S18-2 |−57.3|−67.6|−77.5|−86.7|−96.0|
| S14-1 |**−51.3**|−58.6|−65.3|−72.7|−79.4|
| S14-2 |**−61.2**|−68.0|−74.5|−80.8|−88.0|

S14 low/mid-low energy persists after source stop: corrected30–120Hz50ms samples at stop/+1/+2s are~−55.1/−64.4/−70.0dBFS (S14-1) and−68.3/−75.0/−85.2dBFS (S14-2). Its120–250Hz samples are~−51.5/−57.8/−65.1 and−58.1/−64.8/−73.0dBFS. These demonstrate nonzero decaying musical-band energy, not guaranteed perceptual audibility or identification of an isolated instrument. Full relevant bands and fine envelopes are linked per card and preserved privately.

No post-source broad-window rebound/plateau flags arose. S16-1/S18-2/S14-1 have no threshold review warnings. **S04-a retains C's existing relative-slope warning** (ending intentionally unchanged). **S14-2 retains a relative-slope warning** where room carries the rapid source decline; measured actual local summed rise is1.56dB/100ms, not the larger source-relative slope. Listen for an unwanted separate tail; it has not been declared fixed by metrics. All remaining warnings are exported and in the sanitized evidence.

## Validation and reproduction

- **222 Python tests pass**, including seven new focused tests. Tests cover exact preferred stereo PCM crop, unchanged endpoint/policy rejection, rejection of the old short S16 release, low-band filter behavior, and poisoned post-cut source samples producing identical dry/room output.
- Independent FFmpeg PCM readback,48kHz stereo, exact durations/context, clipping/headroom and original source hashes pass. All five originals and historical A references remain exact. S04's entire post-trim PCM suffix matches preferred C frame-for-frame.
- Existing DSP source reconstruction, explicit dry-stop bounds,50ms actual decoded sum against render proof and quiet termination pass. Safety cleanup starts below−137dBFS peak on all new room renders (S04 retained C below−151dBFS). All19 accepted payload hashes pass before/after.
- Offline Node VM export/client tests pass for this five-cue page and retained remainder/trial/v3 pages: optional storage, source-aware switching, play/stop, five decisions, S14 eligibility and JSON blob/copy export. **No actual browser/audio listening was performed by the assistant**; this does not claim real-browser playback testing.

Original tools: `tools/cue_five_corrections.py`; tests: `tools/test_cue_five_corrections.py` and `tools/test_cue_edit_export.cjs`. DSP architecture `tools/cue_freeze_dsp.py` is unchanged. No freeze alternatives were needed. Per-cue settings, exact sources, gains and source analysis are in plan84; pending file hashes are in `research/84-pending-corrected-cue-renders.json`; actual transition evidence is in `research/84-five-cue-correction-evidence.json` and private analysis files.

Reproduce into a fresh ignored output with `python tools/cue_five_corrections.py --output build/music-material-selection/<fresh-directory>`; default executes one fresh Python worker per cue to bound memory. `--resume` requires exact plan, completed-prefix settings and hashes, never overwrites completed audio. `--verify` performs readback/preservation gates. `--plan` is only for initial plan creation and refuses an existing plan. No input audio is modified.

## Preserved implementation failures

The initial in-process batch completed three cues then hit Windows memory allocation during S14-1; fresh-process workers resolve retained-array peak memory. Initial S14-1 room exceeded existing0.96 safety gate, with no file written; add fixed headroom only for the two not-yet-rendered S14 cues. Earlier plan and completed-prefix metadata remain ignored beside the final output, with logs. A temporary metadata reserialization used the Windows default encoding and failed exact-settings resume; restored the original UTF-8 prefix, with no audio change. Strict floating-point source equality exposed different multiplication association under fixed headroom; diagnostics now receive the exact scaled input without relaxing the established gate. An already-written deterministic S14-1 file was verified byte-equivalent to rerendered quantized samples and retained, not overwritten. Final console JSON initially failed Windows codepage encoding after all five outputs and verification had completed; ASCII-safe console JSON fixes that exit-only error. A new synthetic test initially lacked required pre-fade calibration duration; corrected fixture and full222-test run pass. All failed logs remain ignored. No extra musical alternatives or hidden retuning rounds were created.

## Stop and next action

Listen to these five corrections and export one verdict file. No new render is accepted, no accepted S18-3 adjustment is proposed, and no scheduler or game integration follows automatically. Musical resolution of the proposed earlier S18-2 cut and perceived continuity/room coloration of both S14 endings are the principal listening decisions.
