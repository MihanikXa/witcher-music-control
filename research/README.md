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

**Current next task:** confirm the Vortex clone/install/deploy plan and agree a separate Windows/Documents copied-save setup (report23). ZIPs and backups are ready; no Vortex profile was created/switched and no archive installed. The licensed candidate passes offline structural/packaging checks (report22); runtime native-Init compatibility remains unproved. Existing A/B packages remain intact. Stop unrelated bank/Init regeneration; never deploy generated Init or infer acceptance from blanket silence/normal music alone.

Do not rebuild the 66 GB depot or write to game paths. See `AGENTS.md` and report 14 for gates.
