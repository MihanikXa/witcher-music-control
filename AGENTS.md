# Codex project instructions

## Goal

Build a Witcher 3 Remastered mod that gives the player independent control over music volume by gameplay context.

Primary target contexts:

- exploration / traversal
- ordinary dialogue
- combat
- cinematic / important story moments

Potential later contexts:

- Gwent
- tavern / bard / diegetic music
- quest gameplay / scripted sequences
- other special states discovered during tracing

The desired first prototype is intentionally hard-coded:

- exploration = 0%
- ordinary dialogue = 0%
- combat = 100%
- cinematic / story = 100%

Do not implement sliders until contextual state detection is shown to be reliable.

## Authority order

When sources disagree, use this order:

1. current Witcher 3 Remastered / REDkit 5.x vanilla scripts and resources
2. current Remastered-compatible reference mods
3. older Next-Gen reference implementations
4. assumptions or memory

Never invent WitcherScript APIs, event names, RTPC names, Wwise states, file paths, or engine behaviour. Search for them in the available sources.

## Investigation order

Before substantial implementation:

1. Trace where Remastered detects or represents exploration, dialogue, combat and cinematic states.
2. Trace the path from those states into music control.
3. Identify music-related WitcherScript managers, events, callbacks and native calls.
4. Identify relevant Wwise events, states, switches and RTPCs if exposed.
5. Compare the three reference mods and record which layer each one modifies.
6. Determine the smallest stable hook point for contextual volume multipliers.
7. Only then implement a minimal prototype.

Record findings under `research/` with exact file paths, class/function names, and enough context to reproduce the conclusion.

## Architecture constraints

Prefer:

- Remastered scope-based/local WitcherScript overrides
- small, isolated hooks
- contextual multipliers on top of the user's normal music volume
- event/state transitions rather than constant per-frame polling where possible
- smooth transitions/fades where the engine already supports them
- logging during the prototype so misclassified states can be observed

Avoid unless demonstrated necessary:

- replacing entire vanilla script files
- large copied chunks of vanilla code
- modifying music assets themselves
- editing Wwise banks/projects
- hard-coding track lists as the primary classification mechanism
- adding dependencies merely to create the settings UI
- touching unrelated gameplay systems

If script-level control cannot produce the required separation, document why before moving to Wwise-level work.

## Reference material

Third-party reference files live under `reference/` and are intentionally ignored by Git.

Treat them as read-only evidence. Do not edit them, redistribute their files, or copy large bodies of their code into this repository. When useful, describe mechanisms and cite exact local paths/symbols in research notes.

Reference roles:

- `reference/only-story-music/`: strongest reference for ordinary vs story/quest music separation
- `reference/less-is-more/`: strongest reference for runtime state handling in Remastered
- `reference/fmc-audio-remaster/`: reference for separate exploration/combat/dialogue volume controls

## Repository hygiene

- Our source belongs in `src/`.
- Investigation notes belong in `research/`.
- Helper scripts belong in `tools/`.
- Generated intermediate output belongs in `build/`.
- Ready-to-install generated output belongs in `deploy/`.
- Do not commit REDkit depots, game files, Wwise installations, downloaded reference mods, archives, or generated build output.
- Do not put machine-specific absolute paths into tracked source/config unless they are examples clearly marked as such.

## Testing discipline

For every state classifier or hook, note:

- what signal is being used
- why it should represent the intended context
- known ambiguous cases
- what in-game situation would falsify the assumption

Important edge cases include:

- dialogue while retaining player control
- scripted walks
- cutscenes vs ordinary dialogue scenes
- combat entered/exited during quest scripts
- tavern/bard music
- Gwent
- races and minigames
- quest-specific music outside cinematics
- loading/menu transitions
- save/load while a special state is active

Keep the first implementation observable and easy to revert.
