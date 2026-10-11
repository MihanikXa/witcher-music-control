# Music research and design decisions

The investigation phase is complete enough to attempt a one-region Wwise prototype. These reports document **observed source evidence**, bounded inference and untested build hypotheses:

1. [Reference mod audit](01-reference-audit.md): Only Story Music, Less Is More and FMC.
2. [Only Story Music differential](02-only-story-music-diff.md): how named `game_state` strings were suppressed.
3. [Current vanilla music path](03-vanilla-music-path.md): script state, independent music-type switch and Wwise routing.
4. [Architecture and revised prototype](04-architecture-options.md): why the preferred route is a world-only gain bus, not a script classifier.
5. [Wwise mixer construction](05-wwise-mixer-proof.md): matching schema, proposed Gain/State-bypass mechanism and open runtime tests.
6. [Resource footprint](06-resource-footprint.md): Init/regional soundbanks and unresolved minimal mod-cache packaging.
7. [World-music exceptions](07-world-music-exceptions.md): specific non-generic cues under world music; no automatic exemptions.
8. [Experience-led music policy](08-experience-led-music-policy.md): explicit targets versus design hypotheses, musical priorities and test order.
9. [White Orchard pilot](09-white-orchard-pilot.md): corrected test geography; `music_prologue` is the corresponding technical Wwise bank.

**Next task:** in an isolated copy of the Wwise 2023.1.19 project, implement the **White Orchard-area** mixer by modifying only `music_prologue/world_music` (technical bank name), validate state-gated gain, generate minimum banks, and investigate minimal cache packaging. Do **not** use the initial dream/tutorial as the audio test case. No installed-game changes, REDkit depot retry, user-facing sliders or sparse-exploration timing experiment are part of this step.

Do not interpret a documented authoring construction as a successful in-game test. See `AGENTS.md` for provenance and safety requirements.
