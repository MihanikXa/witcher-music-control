# 69 — Source-measured treatment triage and six private auditions

2026-10-17. Executes report68. **Six requested excerpts are actually rendered**; no remaining-library rollout or subjective success is claimed. Original recordings, the five accepted renders, separate S05-main reference, S14 restriction and WMC releases are preserved. No Wwise/game/Vortex/scheduler/packaging activity occurred.

## Open the trial

`C:\Dev\witcher-music-control\build\music-material-selection\treatment-trial-v1\index.html`

Listen to **B first** for S07-c, S12-2, S15-a, S16-2, S18-3 and S20-a. B is the preregistered primary. Only S07-c/S12-2 offer C, a controlled natural-reverb alternative; A on those two links an unchanged old defective version. There is no newly rendered freeze. The page shows original clocks, reasons, uncertainty, actual processing and50ms dry/wet/sum plots. A separate human form asks verdict/preference, seamless handoff, musical resolution, tail balance, artifacts and notes. Export creates a new outcome JSON with the frozen prediction and registration identity; it cannot overwrite the ledger. Copy-JSON and M3U fallbacks are present.

There are **eight new WAVs across six cards** (six primaries/two alternatives),65,251,552 bytes, plus two unchanged linked references and six full-source references. All new files are48kHz stereo16-bit PCM, with2s lead and3s final silence. Player clocks include the lead; source clocks do not. No other new excerpt is rendered.

## Registration was before treatment rendering

[Prediction ledger](69-treatment-predictions.json), source-only survey tool and five tests were committed as **`7bbb0db605510ad7c379ae61aaf40fa71bf8f1d5` before any trial rendering**. That immutable commit is authoritative; no prediction was changed after seeing output. Its Git-blob SHA-256 is `47a6e989852a126378b979a93522fd935b4fdd6e48deeaf6f55a24b9973ee026`. Windows CRLF working-file SHA-256 is `8010166243425ae68b7cf6a71433f74b88752e2f4dab090fcb65ab39b5557ebd`.

The first render command stopped **before DSP or output creation** because a raw byte comparison encountered Git's LF versus checkout CRLF. Registration now permits *only CRLF-to-LF translation*, records both hashes, and still rejects changed values or even other whitespace changes. Positive/negative tests verify that distinction. No musical setting or ledger value was changed to clear it. The ignored registration journal was written before the first successful trial DSP call. Later technical risk flags are explicitly separate from predictions and human outcomes.

## Complete survey and evidence limits

All24 report61 excerpts have a ledger entry: **five accepted, one separately accepted reference (S05-main),16 ordinary pending and two comparison-only pending S14 excerpts**. Thus18 total pending, including restricted comparisons. All18 received source features and proposed settings; only six ordinary pending entries were rendered. Ten existing verified source previews were decoded for the survey, using a small cache rather than making new source copies.

`tools/cue_treatment_predict.py::source_features` measures the original source-clock crop, not a Wwise segment clock: last8s100ms RMS, endpoint/earlier energy, source slope, positive RMS rises, spectral flux, coarse pitch-class changes, last-second spectral change/high-band energy, stereo correlation and beginning energy. It also models the existing *dry fade only*. The original notes, previous verdict/notes, provenance/IDs, arrangement caveats and restrictions remain attached.

Useful engineering observations:

- Source already below roughly−65dBFS and strongly declining should not be boosted at its endpoint merely to produce an impressive extra tail. S04-b's accepted near-silent ending supports that caution, without proving freeze was responsible.
- Active source plus a very short provisional fade risks abrupt loss of direct music. Accepted S05-short's longer fade/established room is a defensible family reference.
- Fade length and room excitation interact: post-fader sends can already be nearly drained by a long fade. Accepted S07-b does not guarantee another passage of that composition will behave the same.
- RMS rises and spectral flux help flag activity; they do **not** establish percussion, beat, cadence or suitability. Mono downmix spectral analysis can miss stereo-layer detail. Final stereo rendering is checked separately.
- Mixed recordings do not supply a known isolated excitation/response: **original room RT60 is unknown**, not estimated by fitting a music fade. Pitch-class profiles conflate harmony, instrumentation and transients; no reliable chord-resolution judgment was available. Consequently no primary freeze was justified.

Calibration is deliberately weak: the five positives are different combinations, not a fitted preference dataset. S11's accepted conventional post-fader−14dB treatment differs from S05's independent-send treatment; S07-b accepts a quieter−21dB blend. S04-b/S12-1 accept freeze files whose post-source outputs were already very quiet. The auxiliary accepted S05-main has a different historical wet-envelope architecture. None establishes a universal preset or causal parameter effect. We report **no prediction accuracy, fitted weights or probabilities**.

## Fixed rule v1

The ledger contains full executable choices/reasons for every pending cue. Thresholds are modest engineering heuristics, not learned preference thresholds:

1. Endpoint half-second below−65dBFS **and** source end falling>15dB relative to earlier ending context: natural post-fader4.5s RT60,−23dB wet/dry target; keep the original fade. Do not revive earlier harmony.
2. Active endpoint above−50dBFS with an original fade<2s: natural5.5s,−14dB established blend, independent ending send. Extend **only an earlier Codex-provisional fade** to2.2s; preserve source cut and any explicitly user-specified fade.
3. Existing fade>=3.5s: post-fader natural6s for high activity, otherwise7s. Target−20dB when source already falls>10dB; otherwise−17dB.
4. Other endings: post-fader6s/−16dB for high activity; otherwise6.5s/−17dB, or7.5s for an excerpt>45s.

“High activity” means positive100ms RMS-rise90th percentile>2dB or spectral-flux90th percentile>0.45. The45s duration modifier is an **especially weak pacing heuristic**, not evidence that long pieces require more room. Filters and entrance ramps stay per-source v1 settings. Actual RT60 feedback losses change; output length is at least10s or1.65×RT60 extra, with only sub−100dBFS final safety cleanup. No late wet normalization, wet attack, plateau, second audible output fade, dry gain boost or forced mathematical monotonicity is introduced.

## All pending predictions

Endpoint columns are original unprocessed last-half-second RMS, not rendered-tail levels. `post` follows the dry fade; `independent` continues original excitation through the ending fade with the same cut and20ms excitation guard. Wet targets are pre-fade wet/dry RMS, not absolute output dBFS.

| Pending cue | Endpoint dBFS | Predicted dry fade, source seconds | Send | Wet dB | RT60 s | Trial? |
|---|---:|---|---|---:|---:|---|
| S04-a |−37.6|31.8–34 (provisional extension)|independent|−14|5.5|No|
| S11-long |−17.7|90–93, explicit|post|−16|6|No|
| S07-a |−17.9|67–72.7, explicit|post|−17|7|No|
| S07-c |−25.4|172–176.9, explicit|post|−17|7|Yes|
| S12-2 |−33.9|33.3–35.5 (provisional extension)|independent|−14|5.5|Yes|
| S12-3 |−30.5|46.3–48.5 (provisional extension)|independent|−14|5.5|No|
| S12-4 |−72.0|71.845333–73.045333|post|−23|4.5|No|
| S15-a |−28.1|21–25.5, explicit|post|−17|7|Yes|
| S15-b |−23.4|52–57.5, explicit|post|−17|7|No|
| S16-1 |−25.5|40.1–42.3 (provisional extension)|independent|−14|5.5|No|
| S16-2 |−35.8|98.6–101.1|post|−17|7.5|Yes|
| S16-3 |−82.1|130.833333–133.333333|post|−23|4.5|No|
| S18-1 |−41.2|29.5–31.7 (provisional extension)|independent|−14|5.5|No|
| S18-2 |−40.6|109.9–112.7|post|−17|7.5|No|
| S18-3 |−28.5|127.8–130 (provisional extension)|independent|−14|5.5|Yes|
| S20-a |−21.6|38–40.8, explicit|post|−17|6.5|Yes|
| S14-1 **restricted** |−28.3|62.3–64.5 (provisional proposal)|independent|−14|5.5|Never ordinary trial|
| S14-2 **restricted** |−65.7|129.5–132|post|−23|4.5|Never ordinary trial|

No predicted edit outside the six-cue trial has been applied. Protected S14 remains private comparison-only because of dedicated-authored reuse; a numerical prediction is not integration permission.

## Why these six and their controlled alternatives

The requested set was retained, without substitution. S07-c and S12-2 carry prior negative notes (despite Unreviewed verdicts in the raw export). The other four edited passages have no previous review. All six original cuts are unchanged; S07-c/S15-a/S20-a explicit fades remain exact. S12-2 and S18-3 extend only Codex-provisional fades.

- **S07-c:** active end,4.9s explicit fade and low local flux; primary transfers the long-fade post-fader family. Preregistered C changes **only** to independent ending excitation. Earlier frozen-harmony complaint argues against recreating v1's early hold.
- **S12-2:** active end,0.7s provisional fade, high spectral activity; primary extends the fade to2.2s and uses an established independent send. C retains the old0.7s fade with identical room/send/gain, isolating fade timing.
- **S15-a:** explicit4.5s fade with source remaining active; long-fade post-fader family, no boundary change. Music Plus source; no claim about its original room impulse.
- **S16-2:**58.8s passage, moderate2.5s fade and relatively low flux; post-fader atmospheric-family7.5s. Duration-based RT60 choice remains weak, not an inferred gameplay function.
- **S18-3:** active short punctuation with1.6s provisional fade; independent-send family and2.2s provisional fade, same130s endpoint.
- **S20-a:** active source and explicit2.8s fade; moderate post-fader6.5s family, original38–40.8s fade unchanged.

S07/S12 share compositions with accepted *different passages*; they are regression/within-source transfers, not independent composition holdouts. S15/S16/S18/S20 are four sources absent from the five calibration examples, although the user previously heard their complete source auditions. Outcomes must be summarized separately for these groups. The quiet-ending family is not independently tested by these six; prior quiet calibrators do not validate it universally.

## Actual technical results — not human outcomes

[Sanitized evidence](69-treatment-trial-evidence.json) records registration, hashes, PCM gates, source controls, technical warnings and single-primary regeneration. Full local data are in `renders.json`, `final-readback.json`, `spectral-source-review.json` and `tail-audibility-and-peak-estimates.json`.

| Cue | Primary max250ms handoff decline | First post-stop second dBFS | Last post-stop50ms RMS window above−75dBFS ends at | Spectral-distance proxy |
|---|---:|---:|---:|---:|
| S07-c |8.79dB|−72.8|0.65s|0.32|
| S12-2 |4.04dB|−48.8|2.80s|0.89|
| S15-a |4.32dB|−67.7|1.20s|0.53|
| S16-2 |6.21dB|−60.6|2.30s|0.28|
| S18-3 |4.55dB|−41.3|3.30s|0.37|
| S20-a |5.71dB|−53.9|2.90s|0.49|

The−75dBFS threshold describes signal level, **not proven human audibility**. Rendered tail length and physically specified RT60 do not equal perceptual tail duration. This is particularly important for S07-c's mostly drained primary room field.

**Safety/source gates pass:** correct source/frame/fade reconstruction; valid non-silent stereo PCM; independent FFmpeg readback; original context zeros; no clipped samples; no premature termination; no forbidden control-envelope attack/hold/double fade; no detected sustained post-stop rebound/plateau. All22 pinned source/feedback/accepted inputs, plus original source catalog/feedback fingerprints, match. Eight new payloads are verified. Four-times resampling peak estimates remain below1FS (maximum approximately0.9603); this is not a certified true-peak-meter claim.

**Remaining objective warnings are not concealed or retuned:**

- S07-c primary's8.79dB handoff is steep and its post-stop tail weak. C changes the room excitation and measures3.44dB, with first post-stop RMS−52.2dBFS. C has more retained energy despite identical pre-fade gain; “louder tail” is not automatically better. **Primary remains B as preregistered.**
- S16-2 primary's6.21dB decline merits listening for an abrupt room reveal. No alternate was added after seeing this result.
- S12-2 primary has lower loudness-knee magnitude than v1 B (4.04 versus12.02dB), but **greater spectral change** than the unfaded source control (0.89 versus0.62). C measures8.43dB/approximately0.65. This may be a processing-induced timbre/masking problem; it must not be dismissed as native source dynamics or called solved because RMS is smoother.

For review,>6dB adjacent250ms decline and>0.65 spectral distance are conservative **post-render diagnostic thresholds**, not preregistered preference rules, tuned acceptance gates or predicted accuracy. They flag three primaries and the S12 alternative. Page annotations clearly separate these measured watches from frozen reasoning. Spectral changes can still be musical; source controls do not establish subjective acceptability.

The source/dry/combined envelopes are measured over the entire ending, not solely after dry stop. Real v1 wet envelopes for the two known-problem examples were reconstructed from their retained parameters and are rejected by the new gain-law gate for late wet arrival. This demonstrates detection of the old architecture, not proof that all new perceptual handoff problems are solved. No numerical safety threshold was relaxed to improve the trial's apparent outcome.

## Verification, reproducibility and scope

All **200 Python tests pass**: previous193 plus five source/rule tests and two registration/scope tests. New tests cover source coordinates/known signal level, explicit versus provisional timing, quiet endpoints, activity branch, bad source ranges, six-only/S14 exclusion, unchanged committed content and LF/CRLF-only conversion. Existing DSP positive/negative tests retain late attack, rebound, plateau and truncation rejection. Offline Node tests pass for the six-card page, human evaluation fields, frozen prediction export, disabled storage, Blob/copy fallback and all-cue prediction preservation; the prior v3 page also passes after the client-test extension.

S12-2 B independently regenerated from the frozen settings with byte-identical SHA-256 `1df4cf103ee2854b38b9460ebbb9a344cbae347650932751ce85b8c9a9d32451`. No post-generation parameter tuning occurred. No real-browser playback or subjective listening by Codex is claimed. Browser file-URL automation restrictions were respected without a server/alternate-surface workaround.

```text
# Survey is archival/one-shot: it refuses to overwrite the registered ledger.
python tools/cue_treatment_predict.py
# Render into a fresh ignored directory, using the committed ledger unchanged:
python tools/cue_treatment_trial.py --output build/music-material-selection/<fresh-trial>
python tools/cue_treatment_trial.py --verify --output build/music-material-selection/<completed-trial>
node tools/test_cue_edit_export.cjs build/music-material-selection/<completed-trial>/index.html
python -m unittest discover -s tools -p "test_*.py"
```

All original/converted audio remains private and ignored. There is no soundtrack reuse/distribution permission, game integration or release implied by this trial.

**Conclusion:** source features can automate reproducible triage and expose engineering risks, but this trial already shows that they do not guarantee a perceptually good choice. The primary predictions are frozen, and human outcomes are still empty. Next: user auditions the six, exports separate feedback, then assesses the four fresh cases separately from two regressions. Only afterward version/simplify the rule or process another bounded group. Do not automatically render the remaining library.
