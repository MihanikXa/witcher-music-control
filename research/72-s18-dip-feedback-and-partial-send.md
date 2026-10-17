# 72 — S18-3: reported dip and partial-send follow-up

2026-10-17. Exact new user feedback on report71:

> Now there is a strong dip at 18.8s or so

**Report71's full post-fader correction is not accepted.** Its numerical monotonic decline did not establish perceptual continuity. The original report70 Keep/B-with-qualification remains preserved, as do all other selected renders. No new treatment is marked accepted.

## Private comparison

Open `C:\Dev\witcher-music-control\build\music-material-selection\s18-correction-v2\index.html`.

- **A:** unchanged report71 full-post-fader correction, with the reported dip.
- **B:** fuller partial send taper, exponent0.25.
- **C:** more restrained partial send taper, exponent0.5.

Both new options use natural reverb. Listen around player18–20s: does B still rise/reveal the room, and is C still too quiet? Record verdict, preference and notes/export. Two new WAVs only; no other excerpt is rendered. Original audition/release evidence stays intact. No subjective listening by Codex or actual browser playback test is claimed.

## What went wrong with the first correction

The original independent send let the room build while dry faded, causing a measured rise near player19s. Report71 then made room excitation follow the *entire* dry fade, removing too much room energy: post-source first-second RMS dropped roughly20dB. Around player18.5–18.8s the correction fell from−43.39 to−49.17dBFS combined. The user hears a strong dip. This supports rejecting that specific correction; declining RMS alone is not a perceptual success criterion.

This follow-up keeps the same source112.8–130s, dry fade127.8–130s, entrance0.8s, RT60 5.5s,170–3900Hz input filters and exact wet gain0.1981443461969509. Only the **ending send taper** changes. No dry boost, normalization, late output attack, hold, new freeze or second wet-output fade is added.

`tools/cue_freeze_dsp.py::render_continuous` adds an explicitly selected `tapered_ending` policy: the ending's existing raised-cosine dry envelope is raised to a fractional power **for excitation only**. The original entrance and final20ms excitation guard remain. Power0.25 keeps more room excitation;0.5 supplies less; full-post uses the unmodified dry envelope, while the earlier independent send did not follow that envelope at all. Invalid/missing powers are rejected. Existing send defaults, original dry samples, feedback, stereo structure and accepted waveforms are unchanged.

This is a continuous signal-dependent taper from an existing musical fade, not a separate audible wet gain envelope. The natural field still dissipates after the same source stop. It may nevertheless sound like a plateau, timbre handoff or excessive room; numerical construction cannot settle that.

## Measured trade-off retained, not hidden

Combined100ms RMS, dBFS (values rounded):

| Player | A full-post correction | B fuller taper | C restrained taper |
|---:|---:|---:|---:|
|18.6s|−46.61|−44.5|−45.7|
|18.7s|−48.56|−44.0|−46.0|
|18.8s|−49.17|−43.4|−46.0|
|18.9s|−50.90|−43.0|−46.5|
|19.0s|−52.64|−42.7|−47.2|
|19.1s|−56.84|−43.9|−49.7|
|19.2s|−56.86|−45.1|−50.9|

B fills the reported region more, but retains an approximately1.8dB late rise over18.6–19s. C avoids that rise in these windows, but is more restrained and has a brief near-level crossing. **Neither is declared fixed.** There is no imposed constant-level hold, but the balance may still be artistically wrong.

First post-source second: original report70 selection−41.27dBFS; rejected report71−61.26; new B−49.05; C−54.87. These intermediate levels are consequences of excitation tapering, not independent tail loudness matching. Both new versions have identical dry and pre-fade signal and the same fixed wet gain; this is one controlled parameter comparison.

## Verification and preservation

[Plan and exact user feedback](72-s18-partial-send-plan.json) and [sanitized evidence](72-s18-partial-send-evidence.json) retain powers, actual gains,100ms component curves, hashes and safety checks. All18 pinned prior inputs—including eleven cumulative selections, S05-main, original trial, rejected correction and immutable prediction69—match before/after rendering. No global rule is rewritten from this failure.

New stereo48kHz/16-bit PCM independently decodes exactly, context zeros and headroom pass. Dry/pre-fade identity pass; cleanup begins below−143dBFS peak for both; dry-stop seam limits and post-source decay gates pass. Full original source references remain available. Local HTML/export and position switching pass offline tests. The script reconstructs its comparison from pinned source/settings and refuses an existing output directory.

All **201 Python tests pass**, including a new synthetic fractional-taper regression for unchanged dry/pre-fade samples, retained natural tail energy, safe end decay and invalid power rejection. No software installation, Wwise, game/Vortex/save operation, SoundBank, scheduler or distribution occurred. Audio stays private/ignored.

```text
python tools/cue_s18_taper.py --output build/music-material-selection/<fresh-s18-taper-output>
node tools/test_cue_edit_export.cjs build/music-material-selection/<completed-output>/index.html
python -m unittest discover -s tools -p "test_*.py"
```

**Next:** user listens to this one-cue comparison. Preserve both prior failures and the qualified original. Do not scale these settings to other cues or mark this ending accepted before the user's verdict.
