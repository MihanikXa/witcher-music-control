# 65 — User listening results: partial v2 acceptance

2026-10-17. User supplied the five-card v2 decisions export. Its **byte-exact original** is preserved in [65-user-cue-tail-v2-decisions.json](65-user-cue-tail-v2-decisions.json), SHA-256 `7edf9dabcb766d73bfd6fd423334a1c99009de3aa1eebf60b67d434328fd3498`. Plan, feedback/source metadata, settings and all18 referenced render hashes match the retained v2 pack and actual local payloads. No audio was changed or regenerated while recording this feedback.

## Explicit decisions

| Cue | Verdict | Preferred treatment | Exact new notes |
|---|---|---|---|
| S05-short | Adjust | None selected | At 25s a sudden jump in volume to the tail in both B and C |
| S11-short | Adjust | None selected | Also sudden (more like a fast fade out into a tail this time) jump in both at 20ish seconds. |
| S12-1 | Keep | C — v2 freeze | No note supplied |
| S07-b | Keep | B — v2 natural decay, RT60 7s | No note supplied |
| S04-b | Keep | C — v2 freeze, including explicit onset repair | No note supplied |

Three Keep, two Adjust; no rejection. S07-b selects **B**, not B-long10s. S11-short has no preferred version; the export does not separately approve its9s B-long. Blank notes do not justify invented reasons for acceptance. This is private audition acceptance of specific renders, not soundtrack integration/distribution permission or approval of all cues using the same processor.

## What this changes

**Observed user evidence:** S05-short and S11-short still have an audible handoff problem despite report64's passing numerical checks. Report64's implementation and measurements remain historical facts, but are insufficient to establish successful perceptual correction for these two cues. Do not dismiss the new feedback as source dynamics solely because the whole-transition RMS resembles the dry control.

**Supported inference:** the correction works acceptably for three selected renders; it is not a universally approved processing preset. Preserve these three as accepted private audition references and keep both problematic excerpts unresolved. S04/S12 acceptance does not establish that their very quiet post-source frozen fields are what made the result convincing.

**Timing hypothesis, not confirmed clocks:** if these new notes use player time, S05-short25s corresponds to source23s, exactly the start of its700ms dry fade after2s lead. S11-short20ish corresponds to source18ish, the start of its2s fade, rather than the dry stop at player22s. Both B/C share the same audio before dry stop. This suggests the next focused comparison should inspect the *beginning and perceptual progression of the dry fade*, including spectral/direct-to-reverberant balance, not only post-stop energy. These alignments do not establish a new root cause or authorize moving user source-clock endpoints.

No new subjective listening, DSP fix, render, gameplay action or test-suite run is claimed here. Data-only validation checks the supplied decisions against retained evidence; no implementation changed.

## Smallest useful next work

Keep the accepted S12-1 C, S07-b B and S04-b C untouched. If continuing audio correction, concentrate on S05-short and S11-short only: compare their dry-source/dry-fade/reverb balance around the reported handoff, develop a bounded alternative, preserve original cut clocks, and seek listening confirmation. Do not re-render all24, ask for remaining defective v1 reviews, assume a universal B/C winner, or proceed to scheduler/game integration. This intake does not claim that a further correction is already implemented.
