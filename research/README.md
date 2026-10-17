# Music research and design decisions

**Current reading order:** reports50–53 supersede historical prototype plans below. V4 is the completed initial regional filtering pass, not the full experience-led vision; report53 now completes the actual Music Plus archive comparison and recommends an independently designed, native-preserving sparse prototype. No new playback/deployment or runtime feature was authorized by that read-only audit.

This index includes **historical investigations** and the current Stage 1 direct-State-volume plan. Earlier reports 04–12 describe superseded or optional constructions; read 13–14 for the active engineering direction. Claims are either observed evidence, inference or untested hypotheses:

1. [Reference mod audit](01-reference-audit.md): Only Story Music, Less Is More and FMC.
2. [Only Story Music differential](02-only-story-music-diff.md): how named `game_state` strings were suppressed.
3. [Current vanilla music path](03-vanilla-music-path.md): script state, independent music-type switch and Wwise routing.
4. [Architecture and revised prototype](04-architecture-options.md): why the preferred route is a world-only gain bus, not a script classifier.
5. [Wwise mixer construction](05-wwise-mixer-proof.md): matching schema, proposed Gain/State-bypass mechanism and open runtime tests.
6. [Resource footprint](06-resource-footprint.md): Init/regional soundbanks and unresolved minimal mod-cache packaging.
7. [World-music exceptions](07-world-music-exceptions.md): specific non-generic cues under world music; no automatic exemptions.
8. [Experience-led music policy](08-experience-led-music-policy.md): explicit targets versus design hypotheses, musical priorities and test order.
9. [White Orchard pilot](09-white-orchard-pilot.md): corrected test geography; `music_prologue` is the corresponding technical Wwise bank.
10. [First instrumented Wwise prototype](10-white-orchard-prototype-results.md): original Gain bypass tests and bank/Init blockers.
11. [Fade and cooker resolution](11-white-orchard-blocker-resolution.md): smoother AuxBus experiment and native fixture packaging.
12. [Init/licensing research](12-init-entitlement-and-native-fade-plan.md): full-project trial limit, Mastering Suite and entitlement routes.
13. [Init-free direct State volume](13-world-state-volume-init-free.md): authoring-validated 0/0/100 with no new global objects, but no modified bank.
14. [Complete-context bank experiment](14-full-context-bank-experiment.md): current plan for clean local source editing without project pruning.

15. [Complete-context Stage1 result](15-full-context-stage1-results.md).
16. [Licence build gates](16-licence-pending-build-gates.md).
17. [Read-only licensed verification](17-read-only-licensed-bank-verification.md).
18. [Licensed baseline results](18-licensed-baseline-results.md): effective licence; regional ProjectID17637 versus native39.
19. [Native Init compatibility investigation](19-native-init-compatibility-investigation.md): source/reference evidence and runtime-proof limits.
20. [Unmodified regional-bank loading test](20-white-orchard-bank-loading-test-plan.md): staged A/B caches, hashes, profile isolation, rollback and load-attribution criteria.
21. [Observable Stage1 candidate build](21-stage1-observable-candidate-build.md): fresh complete edited project; generation blocked by project-local licence coverage; manual application and A/C/A audible-test plan.
22. [Licensed observable candidate results](22-licensed-observable-candidate-results.md): licensed retry, 19 structural checks, third-variant cache and pending gameplay authorization.
23. [Vortex test preparation](23-vortex-white-orchard-test-preparation.md): verified A/C archives, actual installer routing, closed-app backup, profile draft and save-isolation/approval requirements.

24. [First in-game feedback and transition defect](24-first-runtime-feedback.md): working world-only music attenuation in game; occasional one-second exploration swell during dialogue/combat entry; authored music not yet confirmed.

25. [White Orchard successful follow-up](25-white-orchard-followup-success.md): user reports that the latest tested local revision now works great; exact transition-fix artifact not yet published; next steps are preserving source/build provenance and authored-cue checks before regional expansion.

**Current next task:** identify and sync the actual working local transition fix (source, validation, hashes; no game/audio binaries committed), then run bounded authored/curated music checks in White Orchard. If these pass or risks are specifically mapped, reuse the established regional-only architecture for other music banks, validating them one by one. Preserve native Init, existing Vortex archives, current save and unrelated mods. Do not infer that all authored music is safe from generic-world attenuation.

Do not rebuild the 66 GB depot or write to game paths. See `AGENTS.md` and report 14 for gates.

### Local transition evidence merged — 2026-10-13

- [25: Transition diagnosis and bounded playlist fix](25-transition-bleed-diagnosis-and-local-fix.md): native selector reproduction, five-playlist correction and retained initial licence failure.
- [26: Licensed D build and verified package](26-licensed-transition-fix-candidate.md): structural/playback checks, package hashes and approval boundary.

The source/build provenance is now preserved alongside the remote success feedback. The next evidence gap is matching the user's tested variant to these artifacts and confirming authored cues; the feedback alone does not authorize deployment or regional expansion. This updates the pre-merge next-task wording above.

### Recovery and full-game plan — 2026-10-13

27. [Working-fix recovery and provenance](27-working-fix-recovery-and-provenance.md): deployed D cache and Vortex hardlink identified, native Init/hash preservation,18 repeated gates and32 tests.
28. [White Orchard authored policy](28-white-orchard-authored-music-policy.md): explicit authored branch versus generic/winter/q505 selections, inherited-volume risks and proposed narrow exceptions.
29. [Regional comparison and scalable rollout](29-regional-comparison-and-scalable-rollout.md):106 selectors across eight banks, shared reusable inventory, mixed-target/closure differences and manifest-driven NML-first implementation plan.

Reports27–29 resolved recovery and proposed the shared implementation. The newer results below supersede their next-task instructions.


### Shared implementation — 2026-10-13

30. [Shared regional authoring](30-shared-regional-authoring.md): manifests, fail-closed source/cache gates, retained-D regression,59 tests and explicit new-bank decoder blocker.
31. [Authored-world exception proof](31-authored-world-exception-proof.md):20 native-playlist captures, q505 physical isolation, protected q001/Music/Gwent evidence and remaining intensity/policy limitations.
32. [NML scoped source results](32-nomansgrad-scoped-source-results.md): two reviewed scopes, conservative58-entry classification, six zone02 captures and fresh-baseline licensing stop.

33. [Licensed NML baseline](33-licensed-nomansgrad-baseline.md): successful selected untouched build,19 reviewed warnings, native-exact HIRC and423 streams; candidate remains ungenerated.

34. [Regional decoder and transition controls](34-regional-decoder-and-transition-controls.md): derived v150 fields,D regression,84 tests and corrected transport RTPC controls; reproduced NML combat-outro attenuation and stricter source-closure rejection.

35. [Static playlists preserve combat outros](35-static-playlists-preserve-combat-outros.md): static-only NML correction, exact consumer closure, complete native outros,59 playback captures and retained-D regression. Full corrected source passes. Candidate generation exits1/zero banks because its project-local licence is ineffective. No package or retail test.

36. [Licensed NML candidate and cooker EULA](36-licensed-nml-candidate-and-cooker-eula.md): licence effective, exit2/19 unchanged warnings; full source/decoded/media/global gates pass. Regional bank retained; cooker EULA modal blocks cache/ZIP,107 tests pass.

37. [NML offline package ready](37-nml-offline-package-ready.md): settings backed up/unchanged, confirmed native cook/split exit0, exact bank/cache/ZIP payloads and110 tests; partial regional Vortex archive ready, retail test unauthorized/unperformed.

Historical report37 next action is superseded by report38: continue offline without forced visits or custom saves; retail NML remains unconfirmed.

38. [Spoiler-free offline continuation](38-spoiler-free-offline-continuation.md): user defers NML in-game testing and refuses custom saves/spoilers; multi-bank cache proof and expansion next. NML remains runtime-unverified.

39. [Build storage cleanup](39-build-storage-cleanup.md): verified original-audio hard links,12.9GiB recovered and protected artifacts preserved.
40. [Native two-bank cache proof](40-native-two-bank-cache-proof.md): real native cook/split for exact D plus NML pilot, consolidated-v1 ZIP and reviewed diagnostics.
41. [Expanded NML source/licence gate](41-expanded-nml-source-and-licence-gate.md):21 approved targets,117 selection rows, complete source and representative playback; fresh v2 entitlement application required before binary generation.

42. [Expanded NML consolidated package](42-expanded-nml-consolidated-package.md): effective entitlement,21 exact decoded playlist edits,423 preserved media payloads, unchanged globals and native two-bank v2 cache/ZIP.115 tests pass; no retail deployment.

Current next action: implement a reviewed Skellige manifest using the shared static-only authoring, consumer/transition closure, independent regional bank/media gates and representative playback; add a verified bank to a new consolidated version. Expanded NML licence gate is resolved. Preserve installed D/Vortex, saves and all rollback archives; no custom saves, spoilers or premature retail-test requirement.

43. [Consolidated v2 user feedback](43-consolidated-v2-user-feedback.md): user reports "All, works" after consolidated installation advice; current-context retail success, without specific NML-zone or hash verification. Continue Skellige and remaining regions offline, no custom saves/spoilers.

44. [Skellige pristine baseline licence gate](44-skellige-pristine-baseline-licence-gate.md): complete1,508-unit source copy and253 originals verified; selected generation exits1/no banks due to project-local licence. Preliminary absent-playlist descendant/transition references recorded, no edits or compatibility claim.115 tests pass.

Report44 baseline prerequisite is resolved by report45; report46's separate candidate prerequisite is resolved by report47.

45. [Licensed Skellige pristine reference](45-licensed-skellige-pristine-reference.md): successful untouched selected build,1,900 native-exact HIRC,253 exact native streams, reviewed16 warnings and bounded source-only playlist closure.
46. [Skellige static coverage and playback](46-skellige-static-coverage-and-playback.md):12 static generic targets/85 of185 rows, full542-event closure,38 Wwise captures and sustained/primed complete outros.139 tests and retained D/NML regressions pass; fresh candidate project licence blocks bank generation/v3 packaging.

47. [Licensed Skellige and consolidated v3](47-licensed-skellige-and-consolidated-v3.md): effective candidate licence, exactly12 decoded Volume edits,253 preserved media payloads, unchanged globals and exact retained D/NML banks. Actual native three-bank cook/split exit0, independently reviewed32/23 diagnostics, exact payload/ZIP readback and141 passing tests. V3 is ready offline, not deployed or retail-Skellige verified.

Historical next action (report47; completed by reports48–50): implement Kaer Morhen using the shared manifest, complete consumer/transition closure, independent pristine baseline and source/binary/media gates, then representative playback and a new consolidated version. Toussaint follows. Skellige licensing/cooker prerequisites are resolved; preserve accepted captures/banks, working v2, native Init and rollback archives. No custom saves, spoilers, forced travel or deployment without separate authorization.

48. [Remaining-regions batch policy](48-remaining-regions-batch-policy.md): all26 selectors/34 noncombat targets, explicit five-region manifests,11 approved static edits, shared complete-context union restoration and retained native regions. Failed XML controls lead to supported WAAPI authoring and stricter property-form tests.
49. [Batch native banks and playback](49-batch-native-banks-and-playback.md): independent native-exact baselines, exact2/9 decoded edits,62/184 preserved media, unchanged globals and58 paired captures. Complete measured combat returns and an audible long-fade control; separate named-outro audition limit stated.
50. [Consolidated v4 offline package](50-consolidated-v4-offline-package.md): exact retained three banks plus Kaer Morhen/Toussaint, real five-bank native cook/split, independently reviewed38/23 diagnostics and exact Vortex ZIP.157 tests pass; no deployment/retail launch. Settings drift is preserved without attribution or restoration.

Current next action (report50): the reviewed eight-region policy now ships five modified banks and retains three native regions intentionally. No licence/build prerequisite remains. Preserve v2/v3 and wait for separate installation authorization if desired; no forced travel or saves. Further engineering should target specific shared/unresolved paths rather than start another regional miniature project. Full generic suppression and new-region retail validation remain unclaimed.

51. [Broader music vision reminder](51-broader-music-vision-reminder.md): user correction distinguishes completed all-region static gain filtering from the unimplemented sparse, context-responsive exploration scoring ambition; original 0/0/100 baseline remains, exact Sparse-mode behavior unapproved.

52. [Music Plus architectural comparison intake](52-music-plus-archive-comparison-intake.md): 3.3.0 publicly documented sparse track/silence and playlist control; direct Nexus archive not yet acquired, definitive bank/script parity pending read-only main+pack inspection. Compare design not reputation, preserve vanilla combat/cue grammar and protected-world exceptions.

53. [Music Plus implementation comparison](53-music-plus-implementation-comparison.md): actual3.3.0 main/3.2.0 pack, twelve decoded banks, weighted gap profiles, native event/authored-subtree equality with parent/world/global-volume qualifications, redesigned combat paths, controls/editor persistence and native-preserving hybrid recommendation. [Sanitized archive/bank metadata](53-music-plus-archive-evidence.json).170 tests pass; no bundled execution, playback, new mod implementation or deployment.

54. [White Orchard sparse-rest prototype authorization](54-white-orchard-sparse-prototype-authorization.md): user-approved narrow offline feasibility fixture, with explicit retained-D inherited/static-gain issue, native music/rest/combat-outro/author protection gates and no deployment or user-facing mode defaults.

55. [White Orchard native phrase/rest proof](55-white-orchard-sparse-rest-proof.md): complete-context native/D/Sparse controls, explicit dual-mute resolution, two measured finite rests, native combat/outros and authored/Music/Gwent controls. Native reselection cancels rest; D replay outro attenuation recorded without changing releases.174 tests pass; no bank generation, package or deployment. [Sanitized evidence](55-white-orchard-sparse-evidence.json).

56. [Sparse musical-material selection plan](56-musical-material-selection-plan.md): Music Plus and native originals material audit, provenance-aware 15–25 cue audition shortlist and 5–8 priority picks, offline private previews, no integration or scheduler work.

57. [Sparse musical-material auditions](57-sparse-musical-material-auditions.md):21 local playable candidates,7 priority auditions, exact native/MP joins, independent Opus packet-preserving private conversion, stereo measurements and authored-reuse cautions.179 tests pass; no subjective listening or gameplay implementation. [Shortlist](57-music-material-shortlist.json), [sanitized evidence](57-music-material-evidence.json).

58. [User musical-material feedback](58-musical-material-feedback-review.md) and [unaltered user audition JSON](58-user-musical-material-audition-feedback.json): 12 Keep / 8 Reject / 1 Maybe, source-clock cut/fade proposals, distinctions between user instructions and technical inferences; no audio work or integration yet.

59. [Provisional reverb-freeze ending preference](59-provisional-freeze-tail-preference.md): a subsequent user consideration to apply wet freeze-tail and fade to most/possibly all extracted punctuations, pending listening; preserves exact report58 notes and distinguishes true freeze from ordinary reverb decay.

60. [Private cue edits and freeze-tail handoff](60-private-cue-edit-and-freeze-tail-handoff.md): next authorized Codex work, source-clock cuts, true freeze vs conventional reverb/dry A/B listening, local ignored HTML player and feedback export; no Wwise/game integration or audio redistribution.

61. [Private cue edits and freeze auditions](61-private-cue-edits-and-freeze-auditions.md):24 user-directed source-clock excerpts,34 actual PCM previews, five dry/decay/freeze comparisons, independently implemented lossless FDN, exact crop/silence/headroom checks, offline export test and single-cue regeneration.184 tests pass; actual browser/subjective listening unverified. [Plan](61-private-cue-edit-plan.json), [sanitized evidence](61-private-cue-edit-evidence.json).

62. [Cue-tail audible handoff defect and small v2 plan](62-cue-tail-handoff-defect-review.md); [verbatim export](62-user-cue-edit-decisions.json). Broad dry/wet dip, plateau and separate end fade; preserve v1, stop unnecessary listening, first try continuous reverb and coherent release on a few controls.
