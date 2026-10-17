# 74 — S18 dry-release listening comparison

2026-10-17. User response to report73's dry-only diagnostic:

> It does have a quick dip at the very end

This confirms that the existing dry fade contributes a perceived late dip even without added reverb. It does not establish that the dry fade is the only problem in the combined treatments. None of the failed wet corrections becomes accepted through this observation.

## One controlled change

`tools/cue_freeze_dsp.py::dry_db_release` is a separate opt-in diagnostic envelope. The legacy `dry_envelope` and every wet renderer/default remain unchanged. `tools/cue_s18_dry_release.py` creates just one new dry-only WAV, with the old dry diagnostic linked as A and the new release as B.

Both preserve source112.8–130s, entrance0.8s, ending window127.8–130s,2s leading silence and3s trailing silence. Player fade window is17–19.2s. No samples beyond the selected source endpoint enter the edit. Before the ending fade, floating-point samples are exactly equal.

The old half-cosine amplitude curve approaches zero with an increasingly steep decibel slope. B instead integrates a120ms half-cosine onset of attenuation velocity, then follows a constant decibel slope to−72dB gain. A final20ms cosine cleanup reaches digital zero from that already quiet level. No reverb, hold, normalization, source extension or tail fade is added.

**Important tradeoff:** B attenuates much earlier within the same short window. At player18s the source is−63.83dBFS rather than A's−35.73dBFS; at18.8s B is−90.33dBFS versus−53.79dBFS. This is not evidence of a superior musical release: it may feel too quick overall. The diagnostic tests whether removing the late steepening addresses the specific complaint before selecting any new dry/wet balance. We have not proven that the unchanged2.2s window is musically adequate.

## Private comparison and verification

Open `C:\Dev\witcher-music-control\build\music-material-selection\s18-dry-fade-v2\index.html`. Compare A/B using “Hear ending from16s.” Players stop one another; previous audio is linked without rewriting it. Feedback can be given in chat. No real-browser or subjective listening by Codex is claimed.

[Recorded evidence](74-s18-dry-release-evidence.json) contains exact source/control/output hashes, processing parameters and100ms source-dependent measurements. The new22.2s stereo48kHz16-bit WAV independently decodes byte-exactly to expected PCM; no clipping, peak0.13318, exact leading/trailing digital silence. SHA256 `c7b2af9e97852700ebcbdb4ed68338c559f2df9a6ba82f417b090898bb293acd`.

All204 repository Python tests pass. Three new synthetic tests check constant-dB middle slope, monotonic gain, smooth low-level cleanup, exact unchanged pre-release samples, zero after stop and invalid settings. They establish envelope behavior, not perceptual naturalness. Eleven pinned selection files and prediction69 remain exact; no accepted file or previous failed capture was replaced.

Next: user compares the dry-release slope. Do not add another wet variant or scale the library until that observation is available. If B loses level too early, revisit release duration explicitly rather than hiding the issue with another independent wet layer. No Wwise, game, scheduler, Vortex, bank, release or rights operation occurred.
