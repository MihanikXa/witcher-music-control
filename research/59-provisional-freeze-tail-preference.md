# 59 — Provisional freeze-tail preference for sparse cue edits — 2026-10-16

## New explicit user statement (after report58)

> "Is freeze tail reverb with a fade out for all of them essentially I think, or at least most difficult to do for codex?"

Read in its conversational context, this indicates the user is considering a **reverb-freeze tail with a fade-out for most or potentially all proposed sparse musical cue endings**, broadening report58's S11-specific reverb-freeze suggestion. The statement is tentative, not an exact confirmed global default: no decay time, processor, wet/dry mix, reverb character, freeze instant, eligible track list, or detailed audio specification was supplied. Do not treat all individual timestamp edits in report58 as withdrawn; the preference is a proposed finishing treatment on top of them. Do not infer one identical tail length for all passages.

## Technical distinction and recommended audition-only action

A regular fade reduces the source recording; a conventional reverb tail lets reverberation decay after source cutoff; a **true reverb freeze** sustains the reverberant state of a musical moment (or an intentionally approximated held texture) until a separate gain envelope fades that tail away. A long echo/reverb setting alone does not prove a real freeze. True freeze must avoid metallic repetition, unstable high-feedback, artificial harmonic sustain, clicks, and poor boundaries, especially with rhythmic/bright signals.

For next private audition renders, preserve exact source-clock cuts and split candidates in report58, while testing wet-tail freeze+fade as a **provisional preferred option**, particularly on otherwise unresolved ends. Include standard/natural-tail or simple reverb+fade comparisons on a small representative subset to establish whether freeze genuinely improves musical resolution. Tune freeze point, fade-in/out, wet level and hold/decay by ear rather than hard-coding a global 3-second or similar preset.

Offline pre-rendering using trusted tools / custom signal-processing is in scope of a separately authorized render handoff; deploying a runtime Wwise freeze or modifying/supplying third-party music is a different task and needs proper provenance and permissions. A standalone frozen tail is not proof that the underlying phrase resolves harmonically.

Original raw 21 audition responses are immutable in `58-user-musical-material-audition-feedback.json`; this note is the later user consideration, not an edit to earlier statements.
