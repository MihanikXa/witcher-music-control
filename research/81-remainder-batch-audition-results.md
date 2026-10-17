# 81 — Remaining sparse-cue batch ready for private listening

2026-10-17. Report80's preparation task is complete: **ten ordinary primary candidates, two separately restricted S14 comparisons and three controlled alternatives**. All are pending user review. The eleven accepted report79 renders, including S18-3 T3, and separate S05-main B v1 remain exact. No other cue was re-rendered.

## Listening pack

Open `C:\Dev\witcher-music-control\build\music-material-selection\remainder-batch-v1\index.html` manually in Chrome/Edge.

- **B:** new primary on every card, not an acceptance.
- **C:** optional diagnostic only on S04-a, S11-long and S12-3. All new room treatments use conventional decay; C does not mean freeze.
- **A:** unchanged earlier v1 reference on S04-a, S11-long and S07-a, linked rather than copied or replaced.
- “Entrance / full cue” and “Hear last8s + tail” cover both the original phrase and its complete ending. Players stop each other. Exact processing and original full recordings are under each card's details.
- Keep/Adjust/Reject, preferred variant, notes, local persistence when available, JSON download and copy fallback are provided. Switching a playback variant does not select a preference automatically.
- **S14 is in a separate bordered section.** Its Keep decisions export as private comparison-only, separate from ordinary decisions. Existing dedicated-authored reuse restrictions persist.

Suggested first checks: S04-a → S11-long → S07-a → quiet-end S12-4/S16-3, then the remaining cards. Export one consolidated JSON after listening. An M3U fallback is retained in the same directory; its S14 entries explicitly say comparison-only. No actual browser or subjective playback by Codex is claimed.

Every edited player includes2s leading and3s final silence. For source start `a`, `player = 2 + source − a`. “Hear last8s” starts eight seconds before the selected source stop and continues through the rendered tail. Original reference players use original source clocks.

## Source analysis and treatment choices

The local branch was `main`, matching `origin/main` after fetch. `tools/cue_remainder_batch.py::preserved_inputs` reconciles all24 report61/69 excerpt IDs: eleven report79 selections, separate S05-main, ten ordinary pending and two restricted S14 entries. It verifies32 preserved inputs, including current accepted audio, frozen prediction69 and prior source/user records.

`inspect_source` freshly decodes the exact original previews identified by `cue-edits-v1/renders.json`, checking their original SHA256 identities. It measures centered20/25/50/100ms stereo energy near each endpoint,250ms opening levels, local recoveries,30–200/200–1000/1000–4000/4000–10000Hz band trajectories, and the existing source-feature proxies. [Source observations](81-remainder-source-analysis.json) retain identities and clocks. Spectral/chroma/activity proxies do not establish chords, complete arrangements, musical endings or an identifiable original room RT60.

[Recorded plan](81-remainder-batch-plan.json) was written before DSP rendering. Frozen69 remains unchanged. Its `starting_prediction` is historical; the per-cue current reasoning/timing authority and actual DSP fields explain the reviewed choices. Exports explicitly include the current reasoning and timing authority alongside the original user wording.

| Cue | Exact source span | Current dry fade | Primary treatment | Observed basis / decision |
|---|---|---|---|---|
|S04-a|0–34|31–34|Post-fader room,5.5s RT60,−14dB target|Final half-second−37.6dBFS,6.7dB ending fall with local recovery. Earlier sudden ending motivates a3s **provisional** fade instead of prior2.2s. Original split stays34.|
|S11-long|0–93|90–93|Post-fader,6s,−16dB|Source remains active at−17.7dBFS. Exact user3s fade retained; old freeze handoff replaced by established natural decay.|
|S07-a|0–72.7|67–72.7|Post-fader,7s,−17dB|Stable active ending, low source spectral change. Exact user5.7s fade retained; no frozen hold or independent wet-output ending fade.|
|S12-3|35.5–48.5|46.3–48.5|Post-fader,6.5s,−14dB|−30.5dBFS ending with3.4dB local recovery. Retain the provisional2.2s fade; avoid feeding late recovery independently in the primary. Residual transition warning remains.|
|S12-4|48.5–73.045333…|Final20ms only|Original recorded release; **no added room**|Final half-second−72dBFS, source ending fall43.3dB. Preserve native dissipation rather than restoring older music with room energy. Prior1.2s fade was provisional.|
|S15-b|25.5–57.5|52–57.5|Post-fader,7s,−17dB|Exact user5.5s fade, modest local recovery. Reuses the supported S15 natural-room family while keeping its own passage and fade. Requested entrance uses the retained provisional800ms duration.|
|S16-1|0–42.3|40.1–42.3|Post-fader,6.5s,−16dB|Active−25.5dBFS ending, modest1.9dB recovery. A source-specific middle ground between the short-fade prior and accepted longer S16-2 room; parameters remain provisional.|
|S16-3|101.1–133.333333…|Final20ms only|Original recorded release; **no added room**|Final half-second−82.1dBFS, ending fall53.2dB. Retain original release; replace the provisional2.5s artificial fade with a quiet endpoint guard.|
|S18-1|0–31.7|29.5–31.7|Post-fader,5.5s,−20dB|Source already falls17dB; local recovery only1.7dB. Lighter room, no S18-3 timing transplant.|
|S18-2|61–112.7|109.9–112.7|Post-fader,6s,−20dB|Source falls22.6dB with spectral evolution. Reduce the earlier7.5s/−17dB proposal to respect existing dissipation. Exact crop and omitted gap preserved; relative-slope warning remains.|
|S14-1, restricted|0–64.5|62.3–64.5|Post-fader,5.5s,−20dB|Private comparison only. Source declines8.7dB and changes spectrum; quieter room follows the passage.|
|S14-2, restricted|64.5–132|Final20ms only|Original recorded release; **no added room**|Private comparison only. Original ending already falls29.9dB. Constant headroom attenuation described below.|

Wet targets are pre-fade calibration ratios, not post-stop normalization or promises of perceived loudness. Original levels are not boosted. Entrances from report61/69 remain unchanged; no new source start or stop was selected. Explicit fades S11-long90–93, S07-a67–72.7 and S15-b52–57.5 are pinned independently by `validate_plan`. All other ending durations in this batch are explicitly provisional engineering choices, not fabricated user instructions.

**S04-a entrance:** raw source remains near−91.7dBFS until approximately3.25s, then gradually rises through−61.9/−52.8 to about−43.2dBFS at5s. This supports the user's entrance observation without declaring a subjective threshold. The original0s boundary and opening are preserved; the edited player adds2s. No silent trim or arbitrary start-aligned alternative was made.

**Quiet endings:** `render_source_release` uses the existing stereo dry-envelope function and adds no reverberant field. The original peaks during the final20ms guards are−92.10dBFS (S12-4),−74.46 (S16-3) and−75.04 (S14-2), below the explicit−60dBFS engineering ceiling. The ceiling is not a universal human-audibility claim. Source clocks remain exact; no earlier harmony is revived.

**S18 lessons:** continuous established room, no independent late output attack/hold/fade, and source-specific send review were applied. None of these sources justified copying S18-3's local100ms phase delay/129.65s alignment. The batch gate rejects such unreviewed overrides. S18-3 itself was never generated or modified.

## Three alternatives, one variable each

1. **S04-a C:** same3s fade, RT60 and exact calibrated wet gain; change only excitation from post-fader to independent ending send. This tests whether more retained field helps its sudden ending. A relative-slope warning remains; it is not promoted over B.
2. **S11-long C:** same source, dry, room and send; increase the continuously established room target by4dB (−16→−12). Exact wet gain is primary gain ×`10^(4/20)`. This tests an approach supported by the separately accepted short excerpt, not a claim louder is better.
3. **S12-3 C:** same2.2s fade,6.5s room and exact wet gain; independent rather than post-fader ending send. Accepted S12-2 motivates the comparison, while this passage's distinct recovery motivates caution.

The send-only alternatives are sample-identical to their primaries before the ending fade. S11's wet envelopes differ only by the approved fixed scalar. No automatic tail matching, additional matrix or freeze trial was created. Three old A files are linked references, not new renders.

## Measured warnings and validation limits

`technical` measures source/dry/wet/**actual summed** signal with20–100ms windows on source clocks, records stereo per-band trajectories, spectral distances and post-stop behavior, and distinguishes source dynamics from processing-associated slope changes. Full private curves are linked per card; [sanitized completion evidence](81-remainder-batch-evidence.json) includes representative measured windows, settings, hashes and review metrics.

- **S12-3 B:** up to2.01dB actual combined rise over100ms in the final source second; relative-to-source slope change3.62dB; wet range growth3.21dB. The independent C also carries review flags. These remain listening risks.
- **S18-2 B:** actual local rise only0.39dB/100ms, while its relative-to-source slope change is4.92dB. Room carrying the source's rapid native fall explains why a relative metric can flag without a large literal volume swell. Listen for a separate handoff rather than interpreting4.92 as an actual rise.
- **S04-a C:** a relative-slope flag remains. The primary has no threshold review flag.
- **S12-4/S16-3/S14-2:** original recorded-release warnings remind the listener that low-level numerical termination is not subjective approval.

No post-source sustained>3dB rebound or2s plateau is flagged by the existing250ms checks. That does not exclude a shorter perceptual dip, change of timbre or second-stage impression. No numerical pass establishes musical naturalness. There is no newly imposed reverb-output hold, freeze, late wet attack or second output fade: all added rooms use the existing unmodified conventional `render_continuous` path and decay internally.

## Integrity, headroom and actual test results

- All **15 new WAVs** are48kHz stereo16-bit PCM, independently decoded by the trusted existing FFmpeg and matched exactly to expected quantization. Its binary SHA256 matches report61's recorded decoder. No clipped samples, missing-material gate, wrong source frames or context-silence failure remains.
- Source frame/crop reconstruction, dry envelopes, exact explicit fades, stored PCM envelopes, source hashes and one-variable comparisons pass independent verification. Natural-tail safety cleanups start below−130.99dBFS peak or quieter, after at least10s/1.65×RT60 of rendered release. Quiet source-only candidates use their separately tested20ms low-level endpoint guards.
- **S14-2 initial headroom rejection:** source peak0.994901FS exceeded the existing `<.97` output requirement; original samples did not exceed full scale. The first file is retained privately under `failed/`, never linked for audition. The source-only helper now uses the established fixed attenuation-only headroom convention, scaling the entire cue by0.964920 (−0.31dB), retaining stereo balance. Result peak0.959961FS. No compression, gain boost or tail-specific rescaling was used.
- The main pass completed all ten ordinary cues and S14-1. An explicit identical-plan resume finished S14-2 after that headroom handling. Completed render hashes/settings were checked and skipped, not overwritten; no listening-driven parameter iteration or extra diagnostic candidate was generated.
- **215 Python tests pass**, including seven new batch/quiet-release tests: exact scope, restricted policies, explicit fades/source cuts, maximum/one-variable alternatives, quiet-only safety, recorded-release sample retention/stereo and attenuation-only headroom. Existing D/NML/Skellige/source/bank and earlier audio regressions remain in the suite.
- Offline Node player/export tests pass for the twelve-card batch and earlier six-cue/v3 pages. Tests cover storage-unavailable fallback, switching, one-player/stop handlers, JSON blob/copy output, exact user/source fields, unchanged preference on switch, and a kept S14 comparison remaining outside ordinary decisions. Real browser playback and subjective sound quality were not automated.
- All32 preserved inputs pass, including eleven current accepted hashes and separate S05-main B. All24 excerpt IDs reconcile exactly. Frozen prediction69 and report79 remain unchanged.

[Pending render manifest](81-pending-remainder-renders.json) contains all new file hashes and restrictions; it is **not** an accepted-selection manifest. The local pack's `verification.json`, `renders.json`, per-cue `analysis/` and `envelopes/` retain full private evidence. There are15 deliverable WAVs (172,695,764 bytes), three linked old references and no copied original recordings. Source/derived recordings, failed private output and preview assets stay Git-ignored; committed files contain only original tooling, tests, sanitized metadata and documentation.

Reproduce in a fresh ignored directory with the complete local references available:

```text
python tools/cue_remainder_batch.py --output build/music-material-selection/<fresh-output>
python tools/cue_remainder_batch.py --output build/music-material-selection/<completed-output> --verify
python -m unittest discover -s tools -p "test_*.py"
node tools/test_cue_edit_export.cjs build/music-material-selection/<completed-output>/index.html
```

`--resume` requires the same plan and an exact completed prefix with unchanged render hashes/settings. It never permits silent plan changes or overwrites. No software was installed; no Music Plus bundled program, Wwise, SoundBank, game, Vortex, save, scheduler or mod-packaging action occurred. No recording or derivative is distributed or approved for game reuse.

**Stop:** user listens and exports one batch decision JSON. Further correction should target only reported exceptions; no new treatment is accepted automatically and no other development follows from technical validation.
