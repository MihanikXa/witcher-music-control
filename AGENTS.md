# Codex instructions — Witcher Music Control

Read the current research reports, particularly `research/04-architecture-options.md` through `research/08-experience-led-music-policy.md`, **before** changing implementation. Earlier initial-stage prompts favoring a script-first solution were superseded by the source-backed Wwise analysis.

## Outcome and evidence discipline

Build a Remastered-compatible contextual music-control mod that **preserves the hierarchy of musical importance** rather than simply suppressing every non-cinematic cue.

Current explicit user-target defaults, as **additional gains on top of the normal Music setting**:

- generic exploration / traversal = 0%
- generic ordinary dialogue = 0%
- generic combat = 100%
- deliberately authored story / quest music during dialogue **or gameplay** = 100%
- cutscene / movie / music-only = 100% additional gain (preserve native muting/fades)

Do not promote assistant suggestions into explicit preferences. The optional intermittent/sparse exploration mode is **deferred and unapproved**; implement only when separately requested and validated. The user values Breath of the Wild (85/100) and Ghost of Tsushima (82/100) overall, but that does not independently establish endorsement of every audio technique. Film observations support score identity, perceptual pacing and meaningful contrast—not automatic preference for maximal silence or constant score prominence.

Preserve ambient effects, voices, diegetic bards, Gwent and native combat intensity until their respective policies have been established. Do not equate 100% with forced playback. Do not claim exact digital zero from a finite -96.3 dB Gain floor without measurement.

## Technical authority and current architecture

Order of technical authority:

1. installed Witcher 3 Remastered and matching REDkit 5.x scripts/assets
2. installed matching Wwise 2023.1.19 schema/project and confirmed generated bank structures
3. current compatible reference mods and empirical runtime tests
4. hypotheses, older versions, reputation or memory

For personal-preference claims, newest explicit user statements and the canonical `MihanikXa/prediction` game/film data are stronger than assistant design inference. Keep direct evidence, inference and proposal distinct.

Source-backed research found:

- `game_state` independently identifies the vanilla gameplay/cinematic context;
- `music_type` selects regional `world_music` or `quests_and_cutscenes`;
- world and quest branches normally share an ancestral Music bus;
- muting the common Music bus would also mute authored dialogue cues;
- changing `game_state` to an empty value can deselect six state-dependent quest-branch containers;
- twelve world-location quest-resource candidates merit review; twelve are **not** twelve confirmed mandatory exemptions.

**Preferred provisional architecture:** leave vanilla `game_state`, `music_type`, native events and intensity systems unchanged. Create a new `WMC_WorldMusic` bus under Music, with three RTPC-driven Gain effects whose EffectSlot.Bypass values follow the existing game_state. Route only each regional world child to the new bus. Keep quest/cutscene paths at their native mix. Later use a minimal settings-only script to write the three custom parameters. **No `SoundGameStateChange` hook is justified by current evidence.** Reassess only if actual tests falsify this design.

The mixer is supported by inspected Wwise authoring definitions, **not yet generated or validated in the game**. `research/05-wwise-mixer-proof.md` describes complete bypass truth tables, both FullBand/LFE gain and the non-linear percent-to-dB mapping. `research/06-resource-footprint.md` describes the likely Init and regional bank footprint; minimal cache packaging is unproven.

## Immediate implementation sequence

**Milestone 1 — isolated White Orchard Wwise proof (`music_prologue` bank).**

1. Copy only the required project/work units into a self-contained, isolated authoring workspace; never edit the installed REDkit/Wwise project.
2. Verify the matching Wwise version and actual object schema; author new bus, three parameters, three Gain effects and explicit state-controlled bypass gates.
3. Override only **`music_prologue/world_music`** output, targeting a **White Orchard gameplay test**, not the Kaer Morhen dream/tutorial. The prologue bank naming is technical: White Orchard village and open countryside do have exploration music in this branch. Do not alter `quests_and_cutscenes`, source audio, vanilla state enums, events or user master Music curve.
4. Exercise active and inactive parameter values (e.g. -12/-24/-6 dB), dialogue/exploration/combat/cutscene states, transitions and LFE. Test the -96.3 dB floor, bypass clicks, and native fade behavior rather than assuming perfect mute/smoothing.
5. Selectively generate `Init.bnk` and `music_prologue.bnk` into ignored `build/` outputs. Compare generated bank/HIRC/media payloads with vanilla and document unintended changes.
6. Prove a loader-compatible **minimal mod soundspc.cache** build or document the exact blocker. Do not assume that SoundBank generation implies successful packaging.
7. **Stop before installing into the live game** until explicit permission. Later stage in an isolated mod profile **in White Orchard**, using a backed-up save and comparing the exact same traversal/village dialogue/encounter before and after. Include the q001 authored tavern conversation only if replayable from an available safe save; do not force quest progress, restart playthrough, or fabricate a test. Also test crossfades, native combat variation, save/load and the game Music slider.

Then expand to the remaining seven regions, investigate *specific* world-location exceptions, and add settings UI/persistence. Sparse exploration or extra category controls are separate later experiments, not prototype #1.

**Milestone 2 — exceptions:** use `research/07-world-music-exceptions.md`; inspect intended scene/function and audible behavior. Do not use a `mus_q*`/file-name heuristic or automatically exempt every quest-named location. Exempt narrow noncombat containers/playlists when justified; exempting whole locations may disable combat-gain control.

**Milestone 3 — presentation:** test long periods of environmental audio, score entries, dramatic transitions and authored cues. Music which repeatedly declares minor actions climactic is undesirable; do not use the mod to force greater music density or intensity.

## Safety, structure and compatibility

- Third-party copies in `reference/` are read-only and Git-ignored. Do not redistribute them.
- Installed game, REDkit, Wwise and partial depot files are read-only; never alter in place.
- Do not repeat the failed 66 GB REDkit depot generation unless an actual required operation is proven impossible otherwise.
- Author our source in `src/`; helper scripts in `tools/`; notes and validation logs in `research/`; generated outputs in ignored `build/` and `deploy/`.
- Do not commit game banks, cache output, audio media, installed assets, depots, third-party files or machine-local private paths except as explicitly labeled evidence in research notes.
- Avoid indiscriminate full script replacements, unverified game hooks and periodic per-frame polling.
- Keep builds reproducible, stage artifacts outside game directories, check output destination flags, and record version/command/logs and file hashes.
- For each claim, record observed behavior, supported inference, remaining hypothesis, and a falsifying test.
- Read [research/09-white-orchard-pilot.md](research/09-white-orchard-pilot.md) for the authorized pilot geography. Do not confuse the Wwise `music_prologue` bank with a request to test the Kaer Morhen tutorial.
- Prefer preserving Wwise-authored transitions and the normal user Music volume; a category multiplier must not rewrite composition, threat weighting or scene-event sequencing.
- Conflicts with audio mods that replace Init or regional banks must be documented; do not claim automatic cache merging.
