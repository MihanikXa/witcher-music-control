# 61 — Private source-clock cue edits and genuine freeze-tail auditions

2026-10-17. Executes report60 and the user's explicit audio-production request. **Actual private audio is rendered**, not just an editing plan. No Wwise, SoundBank, scheduler, trigger, mod packaging, retail/Vortex/save change or Music Plus bundled program was used. No subjective listening by Codex is claimed; musical resolution remains for the user to judge.

## Open the local listening pack

`C:\Dev\witcher-music-control\build\music-material-selection\cue-edits-v1\index.html`

Open in Chrome/Edge. Start with S04, S05 and S11, then S07 and S12. There are **24 individually edited excerpts /34 stereo WAV renders**, approximately274.6MiB of rendered audio. Each file contains2seconds of real leading silence and3seconds after its complete tail. Five representative excerpts offer **A dry fade / B conventional reverb decay / C genuine reverb-state freeze**, with C as the initial playback trial, not an automatically preferred verdict. Other excerpts have one provisional C render. Full original recordings remain accessible in each card; S01/S06 are uncut references. S11's full recording remains a long-piece reference, not an invented additional crop.

Use **Play from start**, **Hear ending** or the normal audio controls. Treatment switching can retain player position; every A/B/C set has identical duration/context. Changing playback treatment does **not** silently choose a favorite. Select Keep/Adjust/Reject, select the preferred treatment separately, add notes and **Export decisions JSON**. The filename includes a timestamp and does not overwrite report58. Storage is a convenience; export/copy fallback works independently of it. If local download fails, **Show/copy JSON fallback** displays the complete decisions for manual copying. `auditions.m3u8` and direct standard PCM WAV files provide a local-player listening fallback.

**Browser limitation:** browser automation rejected the `file://` URL under its protocol policy. No HTTP serving, alternate browser surface or security workaround was attempted. Actual browser playback/download is therefore **unverified**, distinct from successful independent decoding and offline client-handler/export tests. The package is intended for normal manual local opening; no server or installation is required. No browser audio was left running.

## Source and editorial authority

The unmodified `research/58-user-musical-material-audition-feedback.json` remains authoritative for titles, roles, notes and source-clock suggestions. Its exact fingerprint is pinned in [the edit plan](61-private-cue-edit-plan.json). Report59's later tentative freeze preference supplements rather than erases those instructions. Report60 defines the bounded rendering task.

Inputs are the exact full-source playback files from `build/music-material-selection/audition-v3/`, pinned by its `auditions.json` and each preview SHA256. These are the audio-file clocks the user actually heard, **not Wwise segment times**. Native base-stem previews remain base stems: no unreviewed optional-layer summation or restoration of a different in-game arrangement was performed. Music Plus additions remain private recording references. Output is48kHz/stereo/16-bit PCM WAV; the new rendering stage adds no further lossy encoding.

Every supplied explicit in/out and fade range is preserved. Mid-source entrances and unspecified fades are declared provisional choices. S05's main dry fade reaches zero at47s while its requested source range still ends47.5s. Only the expressly requested0–23.7s shorter variation was added; a23.7–47.5s remainder was **not invented**. S18's unselected gaps remain omitted. Source roles remain verbatim; per-excerpt functions from the user's notes are displayed separately, so S11's longer alternative can be atmospheric without rewriting the original source role.

**Separate clocks:** the dry source endpoint stays fixed. C's additional wet tail extends2.5–5seconds beyond it and then reaches digital silence. The player adds2seconds before the excerpt. A has no wet extension but retains the same file duration as B/C, so it is silent earlier. Tail stop and source stop are explicitly separate in the page, CSV and metadata; “stop at20s” has not silently become a longer source crop.

## Implemented edits

All times below are **original audition source-file seconds**. “End” is the actual decoded file end, not a rounded catalog duration. Full settings, provisional assumptions, raw notes and per-render hashes are in the [plan](61-private-cue-edit-plan.json), [sanitized evidence](61-private-cue-edit-evidence.json) and ignored local `renders.json`.

| Cue | Source in–out | Dry fade | Freeze capture | Extra wet tail | Versions |
| --- | --- | --- | ---: | ---: | --- |
| S04-a |0–34|33–34, provisional|33|3.2s|A/B/C|
| S04-b |34–60.757333|Last1s, provisional|57|3.0s|C|
| S05-main |0–47.5|**42–47**|42|4.0s|A/B/C|
| S05-short |0–23.7|23–23.7, provisional|23|2.8s|C|
| S11-short |0–20|**18–20**|18|4.5s|A/B/C|
| S11-long |0–93|**90–93**|90|5.0s|C|
| S07-a |0–72.7|**67–72.7**|67|4.5s|C|
| S07-b |81–115|**111–115**|111|3.5s|A/B/C|
| S07-c |156–176.9|**172–176.9**|172|4.2s|C|
| S12-1 |**5–21**|20.4–21, provisional|20.4|2.5s|C|
| S12-2 |**21.5–35.5**|34.8–35.5, provisional|34.8|2.8s|A/B/C|
| S12-3 |**35.5–48.5**|47.7–48.5, provisional|47.7|3.0s|C|
| S12-4 |**48.5–73.045333**|Last1.2s, provisional|69|3.5s|C|
| S15-a |0–25.5|**21–25.5**|21|3.8s|C|
| S15-b |**25.5–57.5**|**52–57.5**|52|3.8s|C|
| S16-1 |0–**42.3**|40.5–42.3, provisional|40.5|4.0s|C|
| S16-2 |**42.3–101.1**|98.6–101.1, provisional|98.6|4.8s|C|
| S16-3 |**101.1–133.333333**|Last2.5s, provisional|130.833333|3.8s|C|
| S18-1 |0–**31.7**|30.1–31.7, provisional|30.1|3.5s|C|
| S18-2 |**61–112.7**|109.9–112.7, provisional|109.9|4.5s|C|
| S18-3 |**112.8–130**|128.4–130, provisional|128.4|3.2s|C|
| S20-a |0–40.8|**38–40.8**|38|4.3s|C|
| S14-1 — comparison only |0–**64.5**|63–64.5, provisional|63|4.2s|C|
| S14-2 — comparison only |**64.5–132**|Last2.5s, provisional|129.5|4.2s|C|

Entrance ramps are0.35s for S12's mid-source pieces,0.5s for S04-b,1.1/1.2s for S07-b/c,0.8s for S15-b,1s for later S16 sections,1.3/0.8s for S18's later sections, and0.9s for S14-2. Source-start excerpts use a20ms safety ramp. These were unspecified details, not new user preferences. No low-energy detector moved any musical boundary.

S14 is a **restricted comparative audition** because report57 verified dedicated-authored source reuse. Its positive rating does not approve generic repurposing. S19 remains Maybe with no new cut or render. Rejected sources were not edited. Twelve Keep sources are represented through ten edited sources plus two uncut references.

## Actual DSP mechanism — and why this is freeze

`tools/cue_freeze_dsp.py` is an independent numerical implementation, not Music Plus, a proprietary plugin or copied third-party DSP code. It uses16 unequal odd delays (997–4111samples at48kHz) and a normalized Hadamard feedback matrix. Orthogonality gives an energy-preserving delay-state update when feedback gains are unity and input is zero. General authority: Julius O. Smith's [Feedback Delay Networks](https://www.dsprelated.com/freebooks/pasp/Feedback_Delay_Networks_FDN.html) and [lossless feedback matrices](https://www.dsprelated.com/freebooks/pasp/Most_General_Lossless_Feedback.html). The implementation and tests are original; no external implementation is imported.

Each field is primed from2.2–4seconds of the existing late musical material, with per-cue high-pass170–260Hz and low-pass3–4.4kHz filtering. This reduces bass buildup and sharp-transient sustain in the wet field without filtering the dry passage. Stereo excitation and diffuse stereo output use different mixing vectors with a shared component; the dry left/right samples remain unchanged before the declared fades/wet entry. This is not repetition of a cut dry phrase or a single long feedback echo.

- **A:** the user's dry fade, plus only declared entrance/endpoint assumptions and matched silent context.
- **B:** ordinary RT60 decay (2.8 or3.6seconds), with normal post-fader input continuing through the dry fade/cut and its causal filter tail. Its reverberant state loses energy after input ends.
- **C:** new excitation closes at the listed capture point; feedback losses smoothly reach unity over100ms. The reverberant field evolves without energy decay. A separate wet envelope enters over0.8–1s, holds until dry end+0.2–0.4s, then smoothly fades the **output** to zero. It does not accomplish “freeze” by merely lengthening a decaying echo.

Wet entrance calibration matches B/C's initial **ungated**400ms field RMS relative to the same late source level; both then use the same wet output envelope and total file length. Wet targets range−13 to−17dB relative to the local musical context. This is not blanket LUFS normalization or a claim of equal perceived loudness throughout different tails. A stable hold will intentionally sustain longer than an ordinary decay; that alone does not make it artistically better.

No compression or gain boost is applied to dry passages. A common linear headroom reduction is used only if necessary across a cue's variants. All comparative sets needed0dB reduction; S14-2's sole C render needed approximately−0.310dB. Existing full originals remain untouched.

## Production progression and rejected controls

1. S04/S05/S11 completed as a six-cue/twelve-render vertical slice, including PCM assertions and offline export/switching tests.
2. S07/S12 brought the core to thirteen cues/twenty-three renders. The same tests passed before expansion.
3. The remaining concrete Keep edits added eleven cues, including restricted S14 comparisons:24cues/34renders in the final index.

Failed/earlier evidence remains ignored and is not marked final:

- An initial stereo-injection matrix shape error was fixed before usable output; synthetic tests now exercise that operation.
- Initial S04-b capture at its nearly silent source endpoint failed the **−72dBFS post-dry audible-tail floor**. Earlier57s field capture fixes that without moving the34s split, final source endpoint or dry fade. The failed WAV is retained under `cue-edits-v1-failed-endpoint-capture/`. S12-4 similarly uses an explicitly recorded69s field capture ahead of its quiet original ending; this is a provisional musical choice.
- Early B controls stopped excitation at the same early capture point as C. This was a real decaying field but an unnecessarily weak conventional-reverb comparison for long dry fades. Those captures remain under `cue-edits-v1-early-input-decay-control/`; final B continues the ordinary fading send through the dry cut.
- A wet attack ending exactly where its smooth output fade starts was initially rejected by an overly strict scheduling assertion. The valid touching-envelope case now has a specific positive regression test. No audio safety threshold was relaxed.

These are technical corrections, not claims of subjective improvement. No effect was tuned “by ear” by Codex. All per-cue character/capture/hold choices remain provisional for the user's listening.

## Verification and remaining listening risks

`tools/cue_edit_render.py` pins the report58 feedback, report57 metadata and exact preview payload hashes. Source ranges use rounded48kHz frame indices. The declared dry crop/fades and pre-wet source samples are checked against the decoded input; every rendered WAV is independently decoded by trusted installed FFmpeg and compared to the expected quantized PCM. `tools/cue_edit_qa.py` independently rechecks all declared fields, input fingerprints, crop prefixes, frame counts, layout, silence, payload hashes, closed-input freeze evidence and local links. It does not weaken any WMC production bank gate.

Observed final results, recorded in [sanitized evidence](61-private-cue-edit-evidence.json):

- 24 requested excerpts,34 renders; all declared source/fade settings match the plan;10edited source-preview hashes match.
- All files are48kHz/two-channel/16-bit PCM with exact expected frame counts. No missing passages or all-silent active excerpts pass the gate.
- Zero clipped samples. Maximum decoded sample peak0.959961FS. Maximum measured dry-stop seam sample delta0.008972FS; first/final active samples and all context samples are exactly zero. These do not certify inaudibility of every possible artifact, but reject hard boundary truncation.
- The closed-input frozen network's maximum settled relative state-energy range is approximately7.65×10⁻¹⁶. Ordinary-loss controls decay. The external fade reaches actual digital silence, while the internally held state remains lossless until processing stops.
- Measured tail channel correlations range approximately0.259–0.910. The dry prefix's stereo relationship remains exact. This is not a subjective guarantee of ideal spatial presentation.
- S07-c has the highest20–150Hz fraction of post-dry spectral energy, approximately25.3%; other tails are below9%. No state-energy growth occurs, but **listen for heavy held bass in S07-c**. This is a review flag, not an automatic EQ or source-boundary change.
- All50 local audio links resolve; the page uses no external resources. Offline Node tests execute the original generated client handlers against a small fake DOM: play/stop coordination, A/B switching, explicit favorite preservation, source-clock export, disabled-storage handling, Blob JSON content and copy fallback pass. **No real-browser or subjective listening claim follows from that test.**
- Regenerating only S11-short in a fresh ignored subdirectory produces all three identical PCM hashes. An individual cue can be revised/re-rendered without processing the library.
- All184 Python repository tests pass, including all previous regional regressions and five new synthetic DSP/clock/feedback/energy/envelope tests. The Node client test passes separately. No packages were installed; existing NumPy2.4.3, SciPy1.17.1 and trusted installed FFmpeg were used.
- All21 old full-source previews and10 retained release/native artifact fingerprints remain exact, including native Init and accepted banks/archives. The authoritative report58 JSON is unchanged.

Source timbre, harmonic closure, percussion smear, metallic resonance, a wrong held chord, loss of momentum or excessive tail length remain **listening decisions**. An output that meets these gates is a technically valid audition, not an artistically approved cue. In particular, freezing at fade start may hold harmony while the remaining dry music changes; if it clashes, request a later/earlier capture or choose B/A. A fade can hide a cut without resolving the composition.

## Reproduction and next action

Original tools: `tools/cue_freeze_dsp.py`, `tools/cue_edit_render.py`, `tools/cue_edit_qa.py`, `tools/test_cue_freeze.py`, `tools/test_cue_edit_export.cjs`. Configuration: `research/61-private-cue-edit-plan.json`; no recordings, reference code, projects or binaries are committed.

```text
python tools/cue_edit_render.py --plan research/61-private-cue-edit-plan.json --output build/music-material-selection/<fresh-output> --max-stage 1
# Review/verify first slice, then --max-stage 2, then 3 in that same output.
python tools/cue_edit_qa.py --folder <completed-output> --plan research/61-private-cue-edit-plan.json --output <fresh-ignored-proof.json>
node tools/test_cue_edit_export.cjs <completed-output>/index.html
python tools/cue_edit_render.py --plan research/61-private-cue-edit-plan.json --output <fresh-ignored-single-cue-output> --only S11-short
```

Revised parameters require a fresh output directory; existing renders are never silently overwritten. Final local authoritative checks are `validation/final-proof-v2.json`, `final-export-logic-v2.json`, `individual-regeneration.json` and `preservation.json`. Earlier stage snapshots are historical controls. `renders.json`, `renders.csv` and the per-cue plan contain all clocks, filters, wet calibration, delay/matrix specification, envelopes, headroom and hashes needed to regenerate.

**Next:** audition S04-a/S05-main/S11-short first, then S07/S12; compare C against B/A without assuming the longer hold wins. Export Keep/Adjust/Reject, preferred treatment and specific timing/wet/tonal corrections. Refine those private passages next. No gameplay trigger, scheduler, soundbank integration, release or underlying music-rights permission is authorized by this audition milestone.
