# Witcher Music Control

A Witcher 3 Remastered mod project for context-aware music volume control.

## Target behaviour

The intended end state is independent control over music in contexts such as:

- exploration / traversal
- ordinary dialogue
- combat
- cinematic / important story moments
- optionally Gwent, taverns / diegetic music, and other scripted states

The first prototype should keep the behaviour simple and hard-coded:

- Exploration: 0%
- Ordinary dialogue: 0%
- Combat: 100%
- Cinematic / story: 100%

Once state detection is reliable, expose those values as user-facing sliders.

## Repository layout

```text
.
├── AGENTS.md
├── src/                          # Our mod source only
├── reference/                    # Local research copies; extracted files ignored by Git
│   ├── only-story-music/
│   │   ├── story-only/
│   │   ├── story-gwent-tavern/
│   │   ├── story-combat/
│   │   └── story-exploration/
│   ├── less-is-more/
│   └── fmc-audio-remaster/
├── research/                     # Tracing notes, findings, hypotheses, symbol maps
├── tools/                        # Project-local helper scripts
├── build/                        # Generated build output; ignored by Git
└── deploy/                       # Generated ready-to-install output; ignored by Git
```

## Reference mods

Download the reference archives manually and extract each archive into its matching folder while preserving the archive's internal hierarchy.

### Only Story Music

Download all four current Remastered variants and keep them separate:

1. `reference/only-story-music/story-only/`
   - Baseline: story music only.
2. `reference/only-story-music/story-gwent-tavern/`
   - Diff against the baseline to isolate Gwent/tavern-specific changes.
3. `reference/only-story-music/story-combat/`
   - Diff against the baseline to isolate combat-specific changes.
4. `reference/only-story-music/story-exploration/`
   - Diff against the baseline to isolate exploration-specific changes.

The four-way comparison is especially useful because it turns the mod into a controlled differential reference: files/settings that differ between the baseline and one variant are evidence for that music category.

### Other references

- `reference/less-is-more/`
  - Primary reference for runtime state handling in Remastered.
- `reference/fmc-audio-remaster/`
  - Reference for contextual exploration/combat/dialogue volume controls.

Third-party extracted files are intentionally ignored by Git. Only the small guidance READMEs are tracked.

## Toolchain

Expected local tools:

- The Witcher 3 Remastered
- The Witcher 3 REDkit 5.x
- Wwise 2023
- Script Merger - Remastered
- Git
- Codex

## First development phase

Do not begin by implementing sliders.

First trace the current Remastered music-control path:

```text
game state
    -> exploration / dialogue / combat / cinematic detection
    -> music manager / script hooks
    -> Wwise events, states, switches or RTPCs
    -> actual music-volume behaviour
```

Use the current REDkit/vanilla scripts as the authority. The reference mods are supporting evidence, not a substitute for tracing current Remastered behaviour.

The preferred architecture is a small script-driven mod using Remastered scope-based/local overrides. Only move into Wwise asset modification if the script layer cannot provide the required separation.
