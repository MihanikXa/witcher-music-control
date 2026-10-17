# 63 — Longer natural reverb decay for most sparse cues — 2026-10-17

## New user correction (latest explicit statement)

> "A longer conventional reverb decay I recon would be helpful for most too."

This applies broadly to the private cue edits, **not just S07-b**. User favors trying a longer, natural conventional reverb decay for **most** clips, after hearing widespread unpleasant late wet arrivals / freeze plateaus / second fades (see report62 and its verbatim JSON). "Most" does not establish that every cue requires reverb or an identical reverb time. This statement changes our **next audition priority**: treat continuous-send **B (conventional decay)** with appropriate longer tails as the primary experimental treatment, and **C (freeze)** as an optional contrasting effect, not the automatic default. Do not erase previous freeze-tail interest (report59); later user feedback and the specific approved B selections in report62 outrank an earlier tentative preference to freeze most cues.

## Engineering implications — proposed, not validated

- Reverb must be present continuously at an appropriately subtle wet level **before** the original musical fade begins, so an audible new wet attack is not introduced at the boundary. After the dry source stops, allow the reverberant state to decay smoothly and organically toward silence. Avoid gate/hold/second envelope or an abruptly truncated tail. A conventional decaying wet signal does not need a separate imposed loudness plateau or artificial end fade.
- Longer **RT60** and longer **render window** are different controls: extending the exported audio alone does not produce a longer decay. Provide enough render length for the actual wet decay to become inaudible; if finite length requires cleanup, use a near-silent final safety fade rather than a second perceptible fade.
- Tune RT60, wet mix, pre-delay/filtering, exact cut point and total tail **per cue**. Provide a couple of meaningfully different longer-decay B examples, controlled at comparable initial loudness, not a large indiscriminate matrix. Avoid excessive wash, lingering incorrect harmony, bass/metallic build-up or masking. Preserve source clocks and original user's cut decisions.
- Test only small representative v2 controls first (report62's S05-short, S11-short, S12-1, S07-b, with S04-b as specific onset repair), including v1 comparisons, independent dry/wet/sum envelope analysis and a short local private listening page. Optional C controls can remain for useful contrasts, but do not prioritize additional freeze complexity unless a seamless natural decay is first demonstrated.
- Do not reprocess all24 v1 files, restart full listening, edit game assets, build Wwise banks or assume licensing/redistribution rights. Reports58,61,62 and source audio are immutable historical inputs.

**Completion criterion for the next run:** a few playable continuous conventional reverb treatments that decay naturally without the audible dip / swell / plateau / double fade; user approval still depends on listening, not numerical QA.
