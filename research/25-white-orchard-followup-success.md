# 25 — User reports successful White Orchard transition follow-up — 2026-10-13

## Direct user report

After report24 documented a roughly one-second exploration-music bleed during dialogue and on combat entry, the user instructed Codex to investigate the transition behavior, and subsequently reported:

> "Everything works great now, what's next for us to do?"

This is a **direct subjective success report for the user's current local tested mod**, not an independently captured test, artifact-hash verification or explanation of the fix. The user has not supplied the revision identifier, the exact source edit or fresh output hashes in this message. The GitHub branch `main` still held report24 as its latest evidence before this status update; candidate D or any later local implementation must not be reconstructed from inference or falsely described as already published.

## Status supported by prior and new evidence

- In the previous explicit gameplay report, world exploration and ordinary dialogue music were suppressed, combat music played, and two brief exploration-music transient cases remained (report24).
- In the newest report, the user characterizes current operation as "works great now" after handing the transition investigation to Codex. **Interpretation (inferred):** the reported transitional defect no longer bothers the user in the current setup. **Not observed:** the exact implementation, quantitative fade trace or how comprehensively the original defect was retested.
- No new user confirmation of **authored/curated quest, cutscene, or quest-associated `world_music` music** appears in this update. Report07 already identifies specific world-container quest-associated candidates; world-only State attenuation is not a guarantee that every authored cue survives.
- No new user confirmation of expansion beyond the original `music_prologue` / White Orchard scope.

## Next work, in dependency order

1. **Preserve the working revision before further Wwise authoring.** Codex should identify the user's actual current source tree and deployed Vortex variant, compare them to last published C, report the changed mechanism and real bank/cache/ZIP hashes, and commit only sanitized source/test scripts/reports. Do not overwrite working C or local successor and do not copy protected bank binaries/licence materials to GitHub.
2. **Exercise authored scoring in the pilot region.** Verify a dedicated `quests_and_cutscenes` cue during dialogue and at least one quest-associated selection within `world_music`, if accessible to the user's current save. Check whether the intended cue remains audible. Distinguish curated cues from naturally silent/ordinary world playlists. Do not infer protection merely from unchanged Wwise sibling structure.
3. **Bound exceptions.** Use report07's concrete selectors and actual quest/scene routing before exempting material. Prefer narrow container/playlist exceptions over entire locations. Preserve combat gain control and native crossfades. In cases with no evidence of intent, record the ambiguity rather than treating a quest-like filename as sufficient.
4. **Expand by region.** Port the proven source-side State mechanism and any established transition correction to the next regional music bank (e.g. `music_nomansgrad` for Velen/Novigrad coverage), keeping each output separately auditable and reproducible. Generate selected banks with full authoring context, record effective project-local licence, compare baseline/candidate HIRC/media, package regional-only caches with native Init retained, and use Vortex for opt-in testing. Scale to remaining regions only after representative gameplay checks, not by assuming `music_prologue` transition properties/generalization.
5. **Defer independent sliders or other mixer redesign** until region coverage and exception policy are stable, unless the user explicitly reprioritizes adjustable context volumes.

## Boundaries

No additional mod/game/profile changes, Vortex actions, game launches, bank generation, source edits or production-asset commits were performed to record this feedback. Retain prior reports as the original evidence, including the historical transition defect. No claim is made that every authored cue, region, save, or desired future context-control feature now works.

## Merge reconciliation — 2026-10-13

The remote feedback commit is now merged with local commits `d50d67e` and `33dc6e7`. These preserve the actual five-playlist correction, native-playlist measurements and the licensed D build/package hashes in [transition diagnosis](25-transition-bleed-diagnosis-and-local-fix.md) and [report26](26-licensed-transition-fix-candidate.md). The earlier statements about unpublished source describe the remote branch before this merge. Both distinct report25 files are retained with descriptive filenames. No generated banks or private evidence are committed.

This reconciliation does not independently identify which artifact the user tested. Match that variant to the recorded cache/ZIP hash before treating the subjective feedback as D-specific runtime evidence. Authored-cue confirmation remains outstanding; no deployment, Vortex or save action was performed by this merge.
