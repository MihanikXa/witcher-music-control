# 60 — Authorized private cue-edit / freeze-tail comparison — 2026-10-17

## User decision and scope

After report58's full 21-source audition and report59's tentative preference for reverb-freeze fading at most/possibly all new cue endings, the user asks to **prepare a Codex handoff and prompt**. This authorizes preparing **private offline auditory prototypes** of their chosen passages, not a game integration, release, universal freeze preset, or changes to WMC source/gameplay behavior.

**Input authority**:
1. `research/58-user-musical-material-audition-feedback.json` is the unedited canonical user feedback. Take source-file (audition preview) timestamps literally and preserve original titles and roles; do not rewrite them as Wwise segment-clock offsets.
2. `research/59-provisional-freeze-tail-preference.md` records later preference to try genuine reverb-freeze+fade on most cue endings (not just S11), still subject to audition.
3. `research/57-sparse-musical-material-auditions.md`, `research/57-music-material-shortlist.json`, `research/57-music-material-evidence.json` and the ignored existing `build/music-material-selection/audition-v3/` are the source/format/provenance authority. Reports53,55 explain input/architecture constraints.
4. Do **not** assume an excerpt is ready or musically resolved merely because user proposed a cut. Treat cuts, fades, split points, apparent silences and functions as provisional listener-directed designs.

## Objective

Turn the user's exact Keep candidates and concrete edit proposals into **private, playable, compared excerpt renders**. The important test is how each candidate sounds in isolation: clean opening, phrase development, cut, convincing tail and genuine environmental silence afterwards. Prefer true reverb-freeze tails with smooth fade for many or most proposed cue endings, but include limited matched ordinary reverb decay and dry-fade references to falsify whether freeze is an improvement. Do **not** make every source share the same tail length or processing.

## Work order and bounded rollout

**First complete a production/QA vertical slice of S04, S05 and S11** (native source, Music Plus source, simple/complex split, S11 explicit freeze request), including trusted playback files, audio assertions and a working local HTML A/B review page. Fix problems before scaling to S07 and S12. These five IDs are the first full user-audition set. If sound processing and export work reliably, extend the same verified path to the other detailed Keep edits (S14 comparison-only; S15, S16, S18, S20); S01/S06 can remain full-source reference listens with a short contextual gap. Do not pad output with invented section timings or multiple arbitrary DSP permutations. If the full set would require significant new architecture, stop at five fully usable cases and report the planned expansion.

**Traceable excerpt plans, subject to exact user JSON, not a replacement for it**:
- S04: two pieces split near 0:34 source clock, including the later piece's proper start/end.
- S05: primary up to about 0:47.5 (dry reduction 0:42–0:47); alternate first break at 23.7s, then only explicitly supported remainder.
- S07: ~0–72.7s (fade ~67–72.7); second ~81–115s (fade-in at 81, fade-out ~111–115); third ~156–176.9s (fade ~172–176.9).
- S11: ~0–20s (fade ~18–20, preference for freeze), alternate long opening ~0–93s (fade ~90–93); full recording as reference option.
- S12: ~5–21, 21.5–35.5, 35.5–48.5, 48.5–end seconds, with careful independent beginnings/endings.
- S14: ~0–64.5 and64.5–end (comparative listening only due verified dedicated-authored source reuse).
- S15: ~0–25.5 (fade ~21–25.5); ~25.5–57.5 (fade ~52–57.5 and possible new entrance ramp).
- S16: split near42.3 and101.1 seconds into three sections.
- S18: ~0–31.7, 61–112.7 and112.8–130 seconds.
- S20: ~0–40.8 (fade ~38–40.8).
- S01/S06: user did not specify new cuts; preserve full-source audition as reference unless there's a clear required comparison. S19 is Maybe, not automatically a render.
- Revisit exact user text for ambiguous “fade from... stop...”; distinguish dry fades, reverb freeze start, overall tail stop, possible extra tail after endpoint.

## Reverb freeze technical specification

**True freeze** = a sustained, decoupled reverberant state after new dry excitation stops, followed by a controlled gain envelope to silence. Ordinary reverb with an elongated decay, delay echo or a repeated short dry recording is **not** automatically a true freeze. A stable digital reverb feedback network with feedback frozen at/near unity (plus controlled energy/damping), or an accurately documented equivalent reverb-state hold/synthesis, is acceptable. Prefer trusted local DSP implementations or a small independently implemented, tested, appropriately cited offline effect; no copying third-party proprietary algorithms. Record the effect design, tail start/fade times, damping, wet/dry balance, stereo coherence and headroom, and explicitly label an approximation if freeze cannot be verified.

At excerpt boundaries, stop/fade the dry signal as the user suggested. Capture/hold a late musically coherent reverb field so the tail doesn't hold percussion transients, click, ring or collapse into an obviously repeated pattern; fade the held texture smoothly over an auditioned, **per-cue** duration. Tail may extend past the source stop where musically appropriate, but label dry-stop versus final-silence timestamps separately and do not silently shift the source-cut plan. Where a natural ending already works, compare with minimal wet treatment or no freeze.

**Comparisons**: for at least three diverse excerpts spanning short/percussive/sustained material, render matched dry fade, standard reverb-decay fade and freeze+fade. Keep source levels intact; level-match the A/B tail appropriately so “louder/longer” is not the only difference. Do not apply blanket LUFS normalization or compress each source flat. Inspect PCM at boundaries for clicks, hard clipping, unstable growth, hard silence discontinuities and duration/clock drift. Human musical improvement cannot be concluded from RMS, metadata or file decoding alone.

## Audition deliverables

Create **fresh ignored** `build/music-material-selection/cue-edits-v1/` with:
- local `index.html`: arranged by source and excerpt; clear IDs, source ID/title, original source-clock in/out, dry fade, freeze start/length/fade, total output length, DSP variant; HTML audio controls; play-one-at-a-time and global stop; verdict (Keep/Adjust/Reject), notes; **Export decisions JSON** that doesn't overwrite earlier feedback;
- private `audio/` render files suitable for Chrome/Edge; listener can compare A/B without searching folders;
- `renders.json`, `renders.csv`, a simple playlist fallback, waveform/PCM QA if useful, and a reproducible provenance + integrity manifest;
- intro/outro listening context that includes an optional few seconds of actual silence around clips (not embedded in a misleading source timeline). Separate playback files from original reports.

Accept soft local storage as a convenience only; export must work without it. If `file://` browser audio controls or JSON export cannot be verified, provide a robust documented fallback. Avoid running unsafe bundled Music Plus software; use trusted existing FFmpeg or transparent local DSP, no auto install without justification.

## Hard boundaries

No Wwise authoring, SoundBank generation, mod ZIP, new regional music policy, schedule/control scripts, game launch, Vortex/saves change, web distribution or changes to accepted v2/v3/v4. Keep original audio archives and full-source previews untouched; do not commit copyrighted audio, code or rendered excerpts. For Music Plus additions, copied/modified recordings stay only in private local audition. No permission to include those recordings in any distributed WMC mod is inferred from local analysis; recording/music rights and mod-page conditions need independent clearance before game integration or release.

## Completion criteria and stop conditions

Ship a **working private audition pack**, not just a rendering script or a table. Run relevant tests plus all existing regression tests; verify each preview is independently playable, the crop actually corresponds to the exact input/source-clock ranges, the effect behaves as claimed, natural tail→silence does not click and quiet gaps remain real. For tricky cuts, make an A/B choice instead of claiming arbitrary slices are already compositionally convincing. Save exact cut/variant parameters per render for later reproducibility. Commit only sanitized metadata, code, tests and a new numbered report. State limitations candidly where subjective judgments or true freeze verification remain unresolved.

**Success**: the user can audition independently edited punctuations, hear a plausible frozen-reverb fade rather than a raw truncation, compare simpler alternative tails, record Keep/Adjust/Reject, and return JSON for the next refinement round. No new WMC gameplay feature is part of this milestone.
