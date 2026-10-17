# Remainder listening decisions and S14 policy clarification

2026-10-17. The latest user export is preserved byte-for-byte in `research/82-user-remainder-cue-decisions.json` (SHA-256 `22bd01ef7cb1e2b092bfe10ba76ce7e1800ec050b97341bad00de614a1487375`). All twelve cue identities and three registration fingerprints match the retained report81 private render manifest. Every referenced render hash was checked against its local audio. The eleven previously accepted report79 renders remain exact.

## Listening results

| Cue | Decision | Preferred | User note / implication |
|---|---|---|---|
| S04-a | Adjust | C | “The first 4 seconds are complete silence.” |
| S11-long | Keep | C | No additional note. |
| S07-a | Keep | B | No additional note. |
| S12-3 | Keep | C | No additional note. |
| S12-4 | Keep | B | No additional note. |
| S15-b | Keep | B | No additional note. |
| S16-1 | Adjust | Unspecified | “Way too sudden drop. This should be very gradual volume reduction.” |
| S16-3 | Keep | B | No additional note. |
| S18-1 | Keep | B | No additional note. |
| S18-2 | Adjust | B | End earlier, cutting/fading before the playback42s volume rise; user rejects the42–50s musical section. |
| S14-1 | Adjust | B | Longer gradual tail after playback1:05, particularly the low instrument. |
| S14-2 | Adjust | B | Longer tail after playback1:08; current drop too sudden. |

Seven new exact selections join the existing eleven in `research/82-accepted-private-cue-selections.json`. S05-main B v1 remains a separate accepted reference: nineteen accepted excerpts overall, five requiring adjustment. Preferred versions on Adjust rows are not accepted renders.

## S14 policy supersession

After the source-reuse explanation, the user explicitly states: “I think we can use them, inspect my latest export though”. This permits considering S14 for future Sparse use; supersedes the earlier comparison-only policy as a blanket exclusion. It does not accept either current ending, authorize game integration, or grant distribution rights. Preserve historical exports and their `comparison_only` fields unchanged: those describe the interface policy at export time, not the newest user decision.

Observed: report57 identifies the same native source in eight dedicated authored segment/track paths across six banks (`research/57-music-material-evidence.json`, S14 identity/authored_reuse). Inference: repeated generic reuse could dilute its dramatic association; no exclusive narrative association or technical ban was established. Any eventual new playback path must preserve existing authored events, routing and media behavior. No such integration is implemented here.

## Correction handoff

Five remaining adjustments only. Preserve all accepted files, especially S18-3 T3. For S04-a distinguish the intentional2s audition lead from additional original-source near-silence (report81 source onset evidence); do not silently remove the standard listening context or assume an exact trim. For S18-2 the new request overrides the prior112.7s endpoint for this excerpt only: assuming the exported player clock with2s lead, player42s maps to source101s (source61 +42−2). The instruction is to finish before the rise, not an approved exact new endpoint. Verify local dynamics before editing. S14 timestamps similarly refer to playback, not source clocks. S16-1 needs a genuinely gradual release, not just a longer silent export.

No renders, DSP, source recordings, historical predictions, game or Wwise resources changed. This is a feedback/provenance update; no new processing tests required or musical quality inferred from measurements.
