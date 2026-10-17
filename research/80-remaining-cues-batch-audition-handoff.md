# 80 — Finish the remaining sparse-cue private audition batch — 2026-10-17

## User direction and authority

User: **"Done, check repo, let's now get to the rest of them"** immediately following their explicit report79 acceptance **"T3 is good enough"** for S18-3. Proceed to prepare all **remaining private** source-selected cue treatments efficiently in **one bounded batch**, rather than another six-cue calibration cycle or prolonged 2–3-item experiments. This authorizes local private audition preparation and engineering validation, not new Wwise/game/scheduler integration or public distribution.

The latest explicit acceptance is recorded by **report79**, `research/79-accepted-private-cue-selections.json`; its S18-3 T3 hash supersedes the older qualified report70 selection. There are **24** report61 excerpt IDs total: **11** currently selected in report79, **1** earlier separately accepted `S05-main` v1 conventional B (do not re-render or count as pending), **10** ordinary pending excerpts, and **2** restricted comparison-only `S14` excerpts. Never silently promote S14 to normal exploration/music deployment: report57 found reuse in dedicated-authored paths.

New treatments are predictions, not accepted cue versions. Preserve report69's preregistered predictions unchanged, user wording from report58, reports62/65/70 corrections, all original/accepted audio files and private material licensing boundaries.

## Ordinary pending: render all ten in one run

| Cue | Original source span (seconds) | Original user constraints / earlier user feedback | Starting family from frozen report69 (not a guaranteed preset) |
|---|---|---|---|
| **S04-a** |0–34|First punctuation split at34; v1 B more natural than C but both too sudden; user notes audible start ~5s (observation, *not* permission to shift source start silently)|Independent established natural room; provisional dry fade31.8–34, RT60 5.5, wet target−14dB|
| **S11-long** |0–93|Explicit fade90–93; v1 freeze handoff/second fade disliked; distinct from approved S11-short C v3|Post-fader natural, RT60 6,−16dB|
| **S07-a** |0–72.7|Explicit fade67–72.7; old freeze plateau and sudden final fade disliked; different from accepted S07-b/c|Post-fader natural, RT60 7,−17dB|
| **S12-3** |35.5–48.5|Exact user slice; original short fade47.7–48.5 was *Codex-provisional*; S12-2's longer fade succeeded|Independent established natural, provisional fade46.3–48.5, RT60 5.5,−14dB|
| **S12-4** |48.5–73.045333|Last original section through natural source end; quiet endpoint; **do not revive a nearly silent ending or impose needless tail**|Post-fader subtle natural, RT60 4.5,−23dB, provisional fade71.845–73.045|
| **S15-b** |25.5–57.5|Exact user fade52–57.5, new segment entrance timing provisional; compare approved S15-a without copying preset blindly|Post-fader natural, RT60 7,−17dB|
| **S16-1** |0–42.3|User split42.3; provisional fade and entrance; compare approved S16-2 but segment differs|Independent natural, provisional fade40.1–42.3, RT60 5.5,−14dB|
| **S16-3** |101.1–133.333333|Last native section through original end, already very quiet; do not artificially bring back earlier harmony|Post-fader subtle natural, RT60 4.5,−23dB, provisional fade130.833–133.333|
| **S18-1** |0–31.7|User first punctuation ends31.7; provisional fade; same source as S18-3 but **do not automatically transplant T3's unique valley alignment**|Independent natural, provisional fade29.5–31.7, RT60 5.5,−14dB|
| **S18-2** |61–112.7|User atmospheric development61–112.7; provisional fade; retain omitted intermediate gap|Post-fader natural, RT60 7.5,−17dB, provisional fade109.9–112.7|

**Time values above are starting inputs based on the source-clock ledger; use report69/61 resolved machine data for exact frame coordinates.** The user's explicit source cuts and fade times always outrank provisional model choices. Per-cue higher-resolution analysis should validate choices before rendering; report69 parameters are archived hypotheses rather than newly confirmed approvals. Avoid applying T3 everywhere simply because it helped S18-3.

**Prior-feedback labels:** S04-a, S11-long, S07-a had concrete audible complaints. The other seven were unreviewed for final edit quality; user Keep on a *full source* in report58 does not imply the newly processed excerpt was auditioned and approved.

## Two restricted comparison-only excerpts

- **S14-1:** original0–64.5s, user atmospheric split64.5, other clocks from report69/61.
- **S14-2:** original64.5s to source end (~132s), from same source.

If source/rights evidence remains consistent, prepare a **separate, clearly labeled private-only comparison panel** for these two in the same processing run (or document any access blocker). Preserve S14 `comparison_only=true`; do not place either in the ordinary "ready to use" selection manifest or imply availability for public redistribution/game repurposing. They are not part of the 10 ordinary final edits.

## Execution sequence (single engineering pass)

1. Verify HEAD, reports58–79, source identities/hashes, report79's **11 accepted exact renders** plus the separately accepted S05-main v1 B, report69 frozen ledger and historical feedback. Reconcile24 IDs precisely; do not silently lose any.
2. Analyze all **10 ordinary pending** from local private sources with source-clock 20–100ms stereo RMS, band envelope near endings, source natural fade/valleys, dry/wet combined handoff and tail audibility. Identify high-risk artificial cutoff, entrance bleep, late reverb buildup, quiet tail, overlap/crossover problems. Numeric diagnostics are gates/flags, not guarantees of musical taste.
3. Select *one best-supported primary* for each of the ten. Conventional continuously present natural reverb is the starting default given report63 and the six-cue experiment, but choose post-fader/independent send, RT60, wet level and fade shape **by individual source**. Use the simple report69 parameters as priors and newer corrections when they explicitly apply; preserve any user-specified fade and all source cuts. For S04-a, optionally provide a start-aligned comparison only if it genuinely improves the user-mentioned5s onset; do not silently change source boundaries. For S18-1/2, examine local dynamics separately and use report78 T3-style local alignment **only if the new source actually shows the same failure**.
4. Deliver **ten primary, non-redundant private renders together**, not serial mini-packs. Add **up to three diagnostic alternatives total** across all ten only for genuinely flagged risks, with one controlled variable per comparison. S14's two separately restricted comparisons may also be rendered; don't count them as ordinary primaries. Avoid a combinatorial multi-preset matrix, old v1 late wet attacks/holds/second fades or the rejected 72dB/2.2s dry curve.
5. Build `build/music-material-selection/remainder-batch-v1/index.html` with ten obvious named cards, source cut/fade clocks (source and player distinguished), intro + 'hear last 6–8s' buttons, user-feedback Keep/Adjust/Reject, preferred variant, notes, JSON export/copy fallback, links to dry/wet/sum envelopes, original references and any relevant v1 defective reference (without defaulting to it). Separate `S14-comparison-only` page/section explicitly with restriction. Keep each excerpt's current status **pending review**, never mark machine passes as user-approved.
6. Verify 48kHz stereo readback, trusted FFmpeg exact hash/source identity, boundary/entrance correctness, no clipping/truncation, safe tail near silence, continuously established reverb, 20/25/50/100ms dry/wet/sum trajectories, no rapid late independent-send room buildup, gaps, rebounds, prolonged plateaus or audible extra fade; record review flags even where no strict technical gate fails. Validate user-clock constraints and no change to accepted hashes; run all existing Python and offline interface/export tests (**last reported208**).
7. Commit original renderer/tests, sanitized per-cue settings/measurement report **81** (or next appropriate number), input references and manifest of **pending** generated files. No third-party raw/derived audio in Git. Generated local previews go under ignored build directory. If blocked by missing local audio source, skip honestly and list exact blockers; do not fabricate usable files or pretend measured clean results.

## Boundaries and stop

The deliverable is one **batch audition** of the rest, not a complete game mod. **Stop after rendering and validating the ten ordinary candidates plus separately restricted S14 references**. User then listens, preferably starting with known-risk S04-a/S11-long/S07-a and quiet-end S12-4/S16-3, and exports one consolidated outcome JSON; follow-up correction only for genuinely flagged exceptions. Preserve all earlier accepted files including S18-3 T3. Do not modify Wwise, SoundBanks, Witcher 3, Vortex, saves, scheduler or previously successful world-music attenuation. No undocumented rights assumption for native or Music Plus material.

**Success condition:** all ordinary pending edits have a plausible, reproducible, source-specific private candidate and straightforward single-page feedback, with any S14 comparative files clearly segregated; accepted entries stay unchanged; minimal need for serial rework. Successful technical QA is *not* user musical approval.
