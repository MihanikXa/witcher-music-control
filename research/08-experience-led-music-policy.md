# Experience-led music policy — 2026-10-11

**Scope:** Witcher Music Control design target. This is a specification update, **not** evidence that the mod has been authored, generated, installed or user-tested. Technical architecture still lives in reports 04–07.

## Why this document exists

The original 0/0/100 exploration/dialogue/combat idea is useful but incomplete. Film and game calibration suggests the underlying goal is **perceptual contrast**: leave room for the environment and for gameplay to breathe, while retaining consciously authored musical interventions that do something specific. We must not mistake this for a generic desire to eliminate music or to maximize score prominence.

Evidence is explicitly distinguished:

| Evidence | Status | Design implication |
| --- | --- | --- |
| User's Witcher request: mute routine traversal/most generic dialogue, retain combat and chosen story/cutscene cues | **Explicit** | Keep current 0% / 0% / 100% targets. Never move the defaults based only on analogies. |
| Canonical Game calibration: Breath of the Wild 85/100 (player trust, wonder, low friction) and Ghost of Tsushima 82/100 (combat feel, beauty/progression) | **Explicit whole-game scores** | These games are strong *design references*, but scores do not prove a specific soundtrack setting was preferred. |
| Film reaction to Vice, Don't Look Up (84/100) and Requiem for a Dream: strong original score as an active, compositionally distinct part of audiovisual form; not mere needle-drop collage | **Explicit mechanism/reception** | Preserve deliberate, independently meaningful scoring and transitions, even inside playable sequences. Original-score status alone does not suffice. |
| Negative reactions to ZeroZeroZero pilot (repetitive underlying synth drone) and Renegade Immortal E1 (continuous epic climax scoring) | **Explicit reactions to limited material** | Avoid perpetual dramatic assertion, generic harmonic wallpaper and climax saturation. Do not generalize pilot reactions into ratings of whole series. |
| Optional intermittent exploration punctuation model, by analogy with Breath of the Wild / Tsushima | **Assistant proposal only** | Research later; do not replace current 0% default or claim this is a confirmed user request. |

Game system source: [Game calibration](https://github.com/MihanikXa/prediction/blob/main/systems/game/calibration.md). Film source examples: [Don't Look Up reaction](https://github.com/MihanikXa/prediction/blob/main/data/screen/reactions/don-t-look-up-2021.md), [ZeroZeroZero observation](https://github.com/MihanikXa/prediction/blob/main/data/screen/reactions/zerozerozero-2019.md), [Renegade Immortal E1 observation](https://github.com/MihanikXa/prediction/blob/main/data/screen/reactions/renegade-immortal-2023-e01.md). These preferences inform design; they do not establish Witcher engine capabilities.

## Design hierarchy

1. **Environmental sound is first-class.** Silence from the *music* channel is not silence from the world: leave weather, wildlife, room tone, footsteps, effects, spoken dialogue and normal diegetic sources alone.
2. **Routine scoring may recede.** Exploration and ordinary dialogue are the main targets for default 0% generic music; this creates a baseline from which select musical events can matter.
3. **Preserve deliberate authored cues regardless of game_state.** A cue may be explicitly selected for a dramatic dialogue, quest walk, reveal, memorable location or playable story moment. A plain dialogue/exploration enum does not make that cue generic.
4. **Combat remains reactive, not uniformly epic.** The 100% combat target means retain native combat music and threat/intensity modulation at unity gain. It does not force a cue, raise intensity or turn every skirmish into a climax.
5. **Respect authored transition grammar.** Crossfades, cue endings, source/destination overlap and intentional silence are meaningful. A clean mixer must avoid audible gate clicks, score resets or flattening those transitions.
6. **Retain normal player volume authority.** Extra gains multiply the native Music setting and never override the game's cinematic/movie mute or master mix.

This does **not** mean that all music flagged as 'quest' is inherently exceptional, or that all world-location music is expendable. Importance is a listening/scene-function judgement, not an automatic filename classification.

## Why the current Wwise architecture is still the right first step

Vanilla separates `game_state` from `music_type` and commonly routes two sibling music branches per region:

```text
regional root
  music_type
    world_music          -> [proposed WMC_WorldMusic contextual gain]
    quests_and_cutscenes -> [existing Music mix, untouched]
```

Generic dialogue often selects normal regional world music; an authored conversation can select the quest branch even while `game_state=dialog_scene`. Six quest-branch selectors themselves still use `game_state`, so we must **not** blank those states like Only Story Music. Context and music provenance are separate mechanisms.

The proposed mixer uses three RTPC-driven Gain effects, each State-gated by EffectSlot.Bypass, on a bus carrying world branches only. Prologue-first bank generation and cache packaging are **not yet runtime proven** (reports 05–06). Exact 0% may require more than the finite -96.3 dB plugin minimum. Do not state that a volume-only mixer changes the frequency or rhythmic placement of original composition cues.

## Explicit first milestone (no new mode yet)

Keep the current hard-coded defaults: **exploration 0%, ordinary dialogue 0%, combat 100%, authored music unity**.

Prologue-only acceptance cases:

- Ordinary prologue exploration and village dialogue: only generic world music attenuated; environment and voices intact.
- `mus_q001_tavern_conversation` and `mus_cs001_tavern_intro`: authored branch unaffected by exploration/dialogue gain, including transition overlaps.
- Day/night, focus/boat/underwater groupings and combat: correct effect enabled while other two are bypassed, without perceptible gate clicks. Test unequal gains to expose leakage.
- Cutscene/movie/music-only, pause/Gwent and loading: no unexpected new attenuation, playback or cancellation of native states.
- Native Music slider still changes both branches; no change to sound effects, speech or diegetic sources.
- Save/load and crossfades do not leave a stale gain or a branch on the wrong output path.
- Successful generated `Init.bnk` + `music_prologue.bnk` is not sufficient: minimal mod cache and loader precedence require independent validation.
- Test true silence separately from '-96.3 dB sounds silent'; report what was measured.

Do **not** modify installed game directories or retry full REDkit depot generation to perform this initial isolated authoring proof.

## Deferred ideas and decisions

### Optional sparse exploration (proposal, not a default change)

High-level inspiration from Breath of the Wild's restrained, discontinuous exploration scoring and Ghost of Tsushima's mixture of ambient spaces, adaptive combat and authored playable moments.

A future experiment could allow *selected intermittent musical punctuation* while suppressing routine continuous world beds. That is a **timing/event policy**, not a third volume value. Verify whether current Witcher music containers provide acceptable transition/sequence and silence control or whether modifying the event schedule would destroy authored phrasing. Less Is More may help as a reference but its random play/mute intervals are not automatically equivalent to compositional punctuation.

Possible comparison after first prototype: existing **Minimal** preset (0/0/100), a **Sparse** mode using documented event/timing rules, and a **Low-background** option with adjustable nonzero gain. None should be hard-coded as a user preference from overall game ratings alone.

### Selectively preserve important world-location score

Report 07 identifies 106 world selectors, 55 reviewed candidates and 12 concrete quest-resource candidates; these are **not** 12 verified author-intent exceptions. Before adding exemption routes, test representative story situations and source-level routing. Prefer narrowly exempted noncombat playlists/containers to exempting entire location branches, which would also bypass combat-gain control. Treat diegetic music boxes and bards separately from nondiegetic score.

### Later user controls

Three independent sliders and save/load persistence after successful authoring/deployment. Keep Gwent, tavern/bard and other categories in 'preserve vanilla / undecided' state until explicitly requested. Avoid adding complicated UI or classification logic as a prerequisite for a proof-of-function.

## Decision log

- **Confirmed target retained:** 0/0/100 and authored unity.
- **Design clarification:** preserve dynamic range of musical importance, not silence for its own sake.
- **Architecture retained:** Wwise-only context selection at world-music bus, no sound-state script hook without evidence.
- **Not yet decided:** sparse exploration mode, default nonzero background volume, exact world-location exemptions, separate Gwent/diegetic policies.
- **Next required action:** isolated prologue-only Wwise authoring + bank/cache packaging proof, then controlled in-game test with explicit permission.
