# Music research and design decisions

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

Decoder/control work is complete. Next narrow gain ancestry to approved generic playlists outside native transition paths, validate any joint State/static changes, then repeat outro/q505/q001 controls before candidate generation. The baseline licensing step remains complete. Do not deploy fixtures, bulk-mute unresolved locations or replace working D.
