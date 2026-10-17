# 83 — Five user-directed Sparse cue corrections, one private pass — 2026-10-17

## Current authorization and immutable history

User agreed to the **single five-cue corrective pass** proposed after report82: “Okay, let's do it.” This authorizes local private rendering, examination, tests and a new audition/feedback package, **not** permanent acceptance, audio distribution, Wwise, soundbank, game integration, scheduler edits, or changes to approved audio.

Read `AGENTS.md`, reports58/61/69/70/77–82 and current `research/82-accepted-private-cue-selections.json` before work. In report82 **18 current exact renders** are accepted plus separately accepted **S05-main B v1** (19 in all). All 19 must remain bit-identical. Reports69 (frozen predictions), 81 (render plan and source analysis), 82 (exact user verdicts), selected manifests and historical adjusted WAVs are immutable. Do not call any Adjust row accepted just because user preferred its old B/C as the basis for correction.

The exact five outstanding user-feedback entries from report82 are:
- `S04-a` — **Adjust/C**: “The first 4 seconds are complete silence.”
- `S16-1` — **Adjust**, preferred unspecified: “Way too sudden drop. This should be very gradual volume reduction.”
- `S18-2` — **Adjust/B**: “I would rather cut and fade it out before 42s volume rise, musically the 42s-50s section doesn't work, so let's remove it and make the phrase end sooner.”
- `S14-1` — **Adjust/B**: “Would like a longer tail after 1:05, so the low instrument doesn't drop as suddenly, but fades out with a tail gradually”
- `S14-2` — **Adjust/B**: “Would like a longer tail after 1:08, drops too suddenly”

These are **five different mechanisms**; do not solve them by imposing one fade-length/reverb preset. Do not re-render the other 19 selected excerpts or re-open accepted S18-3 T3.

## Clock discipline

Current listening files have **2s of leading silence**, and for source start `a`, `player = 2 + source - a`. Original recordings' clock is authoritative for cuts. Never confuse player and source:
- `S04-a`: source0–34, standard player intro2s; user reports4s total early silence, and report81 observes original source near−91.7dBFS until around source3.25s, gaining audible energy through source5s. The observed silence is **both** wrapper lead and source opening; measure before changing.
- `S16-1`: source0–42.3, old provisional dry fade40.1–42.3.
- `S18-2`: source61–112.7, old provisional fade109.9–112.7. **Player42s maps to source101s**; user rejects the subsequent player42–50s passage (source~101–109s). This supersedes prior full112.7 endpoint for **S18-2 only**. It does not choose an exact new end. Source S18-3 starts112.8 and its accepted source130 end **must not change**.
- `S14-1`: source0–64.5, current fade62.3–64.5, player1:05 maps to **source63.0**.
- `S14-2`: source64.5–132.0, player1:08 maps to **source130.5**; raw original drops near source end. Old primary is dry-only with a20ms quiet end guard and fixed attenuation ~−0.31dB for headroom. There is *no added reverb* to extend its low-instrument decay.

Only the user explicitly requests a different **musical end** for `S18-2`. Retain the other four excerpt endpoints unless source evidence strongly requires a narrowly explained private comparison and the user's request supports it. Every alteration to a user-expressed clock should be justified and transparent.

## Five-target investigation and implementation

### S04-a — remove unnecessary opening silence, keep preferred C ending

Reference `build/music-material-selection/remainder-batch-v1/audio/S04-a-C.wav` (independent `pre_ending_fade` conventional room) is user-preferred but **Adjust**, not selected.

Inspect actual source 0–6s with 20/50/100ms stereo and bands. Locate the first *musically useful* audible onset rather than cutting at a fixed−60dB threshold, rushing entrance ambience, or treating2s audition lead as source content. Propose one minimal **source-relative opening trim/offset or entrance change** around the unused near-silent source prefix while **maintaining the musical split at source34s** and the preferred C ending DSP. Record the actual source start chosen and any effect on total clip duration. Keep standardized2s lead for like-for-like audition, but clearly label it **listening context, not part of musical entrance**; distinguish the revised music start from the unchanged lead. Preserve the old C as an A reference so the user can verify nothing desirable was cut. Do not simply hide long source silence behind yet more silence.

### S16-1 — genuinely gradual audible release

Reference `remainder-batch-v1/audio/S16-1-B.wav`; source0–42.3 and current provisional fade40.1–42.3, RT60 6.5s,−16dB pre-fade wet, post-fader.

Measure original/dry/wet/combined through at least the final8s at 20/50/100ms. Locate the actual audible abrupt decline (time and band); assess whether source itself changes dynamics, direct dry fades too quickly, or room loses energy prematurely. Re-shape attenuation across a **meaningfully longer audible interval** (candidate onset earlier than40.1, if compatible with composition), and coordinate established wet room so the perceived loudness becomes progressively quieter through note decay rather than a steep direct-to-room handoff. Preserve endpoint42.3; do **not** simply append blank export seconds, normalize the tail, create a conspicuous wet hold/second fade or reuse the report74 failed72dB/2.2s constant-dB release. Original fade start was provisional, not user-specified. Evaluate the release during playback, not just no clipping/plateau after dry stop.

### S18-2 — an earlier musical cut before the rejected rise

Reference old `remainder-batch-v1/audio/S18-2-B.wav`, source61–112.7, current fade109.9–112.7.

Analyze the original source around **98–103s** and, for context, a few seconds earlier, with finer RMS/spectral/phrase features. Mark the onset of the rejected player42s rise (approximately source101s). Find a musically defensible earlier phrase termination **before that rise**, with adequate time for the dry release. Record *proposed new exact source fade start and stop* (tentative, not user-specified), and explain why the edited sound does not contain the rejected player42–50 section. Keep source start61s, the earlier entrance and its spatial character where possible. The low-key reverb should decay naturally; don't accidentally leak rejected later source samples into room excitation, or leave a wet field surging on source material the user wanted excluded. Do not claim the earlier new end was explicitly chosen by the user.

### S14-1 — preserve the low instrument into a longer diffuse tail

Reference `remainder-batch-v1/audio/S14-1-B.wav`, source0–64.5 with current fade62.3–64.5 (player64.3–66.5), post-fader RT60 5.5s,−20dB wet, **high-pass250Hz** on room send. The current room input bandwidth may suppress the low instrument; **measure rather than assume** which frequency bands contain it. Measure low-band30–120/120–250/250–500Hz behavior around source61–64.5 and actual room energy after player65s/source63s. If low note fundamentals/overtones fall below existing HP, adjust send filtering/balance or apply a restrained frequency-dependent room tail so its decay is carried beyond the direct stop. A longer *actual audible* LF/mid-low release is the goal, not longer silent PCM, excessive sub-bass, a sudden wet gain jump, reverb-state plateau or an obvious new note. Preserve the musical source split at64.5 unless user evidence says otherwise.

### S14-2 — actually introduce a controlled tail at the quiet end

Reference `remainder-batch-v1/audio/S14-2-B.wav`, source64.5–132.0, output with **no room** (original recorded release and20ms quiet guard). The user requests a longer tail after player68s (= source130.5s), so another source-only silence extension cannot address it. Measure the last *audibly meaningful* low-frequency passage, including source128–132s, against the original global decline. Design a restrained natural low-aware reverberant or similar diffused decay fed from audible material **before** it becomes nearly silent, so a continuous tail persists beyond the abrupt perceived dropout. This must not suddenly reanimate earlier harmony, boost source silence, produce a long artificial freeze/hold, or feed samples beyond the source132s endpoint. Preserve the established fixed headroom-only reduction (or document justified equivalent safe headroom), source clock64.5–132 and the original existing output for comparison.

## One corrected audition pack, not a preset matrix

Produce **one principal correction for each of the five**, plus **no more than two total controlled alternatives** only if actual analysis leaves a consequential one-variable uncertainty. Reuse existing `tools/cue_remainder_batch.py`, room DSP and offline client infrastructure where possible. Do not independently produce serial mini-packs.

Fresh ignored output folder:
`build/music-material-selection/five-cue-corrections-v1/`

Offer exactly five clear comparison cards (original A + corrected B, optional C), explicit **source vs player times**, source ending/fade and wet behavior, audible last~8s and full-cue playback; S04-a needs opening playback as well. Use Keep/Adjust/Reject, preference and free notes with one combined JSON export/copy fallback. S14 **should now be eligible for *future* Sparse consideration according to the user's new explicit statement**; DO NOT perpetuate the old blanket comparison-only ban in the new evaluation status. Its actual cue renders remain unaccepted until the user reviews these fixes, and existing authored event/routing/media protection and rights/distribution limits still apply. Preserve historical `comparison_only` metadata exactly where it was originally recorded; update only the *new* pack's current policy metadata with provenance.

## QA and stop gates

Verify source identities against original private WAV/Opus and pinned input hashes; preserve 18 report82 accepted SHA-256 payloads **plus separate S05-main B v1**. Do not alter earlier report81 output, failed experiments, report82 feedback, report69 preregistered predictions or S18-3 T3. Reconcile all 24 report61 IDs: 19 accepted total (including S05-main), 5 Adjust pending. Use source-time evidence for exact edited boundaries. Inspect 20/25/50/100ms stereo source/dry/wet/combined envelope, relevant low/mid bands, onset/termination/spectral continuity, audible level after drop, no dry-to-wet holes/rebounds/plateaus/double fades, actual decoded PCM/clipping/headroom and below-audibility final safety cleanup. Ensure true audible progress rather than extra silent time; use negative regression checks for old poor S16/S14 behavior. Link correctly to old versions, preserve accepted outputs bitwise.

Run all current Python + offline client/export tests (report81 counted215 Python; this is not a promise of current count). Commit only original code/tests, a sanitized source-measurement/parameter ledger, output hash manifest **pending user approval**, and numbered completion report84 or next appropriate number. Keep copyrighted audio files out of Git.

**Stop after one private pack**; do not silently mark corrected versions accepted or launch Wwise/SoundBank/Vortex/game/scheduler work. The user's next action is one consolidated listening verdict for these five fixes.
