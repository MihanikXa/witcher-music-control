# Witcher Music Control

A Witcher 3 Remastered mod project for **context-aware music gain**: reduce routine scoring without removing deliberately authored dramatic music or disturbing the game's native soundtrack transitions.

## Current target policy

These are **additional gain multipliers relative to the player's normal Music setting**, not absolute output-volume commands.

| Source / context | Initial target | Status |
| --- | ---: | --- |
| Generic world music during exploration / traversal | 0% | Explicit user target |
| Generic world music during ordinary dialogue | 0% | Explicit user target |
| Generic world music during combat | 100% | Explicit user target; retain vanilla combat/intensity behavior |
| Explicitly authored quest/story music, including gameplay and dialogue | 100% | No added attenuation; preserve authored fades and dynamics |
| Cutscene / movie / music-only cues | 100% | No added attenuation; do not defeat native movie mutes |
| Gwent, bards/taverns and other diegetic music | TBD | Preserve existing behavior until a separate policy is established |

"100%" means **unity gain**, not force playback or override the player's master Music slider. The 0% requirement is an intended perceptual mute: the proposed Wwise Gain plugin has a finite -96.3 dB floor, so exact silence remains a prototype test.

**Design principle:** preserve contrast and authored musical meaning. Do not interpret the goal as "minimize all music." A future optional sparse-exploration mode may use intermittent musical punctuation, inspired by Breath of the Wild and Ghost of Tsushima, but this is a **design hypothesis**, not an approved replacement for the 0% default and not something a static volume slider alone can deliver. Details: [experience-led music policy](research/08-experience-led-music-policy.md).

## What the research established

Current Witcher 3 / Wwise uses two different selectors:

- `game_state` distinguishes exploration, ordinary dialogue, combat, cutscene, etc.
- `music_type` selects `world_music` versus `quests_and_cutscenes` inside eight regional music roots.

Some important authored cues play **during** ordinary dialogue or gameplay, so a global dialogue mute would also mute story music. Conversely, six quest-branch containers still depend on `game_state`, so copying Only Story Music's empty-state strategy can suppress authored cues.

The proposed, **not yet runtime-validated**, solution is a child bus under the existing Music bus containing three state-gated Gain effects. Only the regional `world_music` children route through that bus; the quest/cutscene branch retains vanilla routing. User settings eventually set the three gains without intercepting `SoundGameStateChange`. Some quest-relevant location music lives under `world_music` and requires careful exceptions rather than blanket rules.

Read the evidence and outstanding validation conditions:

- [Architecture and prototype](research/04-architecture-options.md)
- [Wwise mixer construction](research/05-wwise-mixer-proof.md)
- [SoundBank/cache footprint](research/06-resource-footprint.md)
- [World-music exceptions](research/07-world-music-exceptions.md)
- [Experience-led target policy and test order](research/08-experience-led-music-policy.md)

## Next milestone — White Orchard proof (Wwise `music_prologue`)

1. In an **isolated copy** of the matching Wwise 2023.1.19 project, construct the proposed bus, three Gain instances/RTPCs and state-controlled bypass tables.
2. Route **`music_prologue/world_music` only** to the new bus, and perform the in-game test **in White Orchard** (village, open countryside, encounters), not in the Kaer Morhen dream/tutorial. The Wwise bank name `music_prologue` includes White Orchard exploration music; it is not a requirement to test a musicless introduction. Do not change quest/cutscene routing, player Music volume, media or native events.
3. Validate gains, state gates, crossfades and sound routing in authoring; then selectively generate `Init.bnk` and `music_prologue.bnk` to ignored build output.
4. Establish a **minimal mod `soundspc.cache` packaging and load test** before any game deployment. Selective bank generation alone does not prove that a mod cache will load.
5. Only after successful packaging and user approval: test on a backed-up White Orchard save in an isolated mod profile, compare unmodded/modded exploration and dialogue, test combat and accessible authored scenes; then expand other regions, decide exception policy and add settings UI. See [White Orchard pilot](research/09-white-orchard-pilot.md).

The REDkit 5.x depot-generation attempt failed during finalization. **Do not re-generate the 66 GB depot as a prerequisite** for this Wwise proof; re-evaluate only if a demonstrable build dependency requires it.

## Repository layout

- `AGENTS.md` — Codex conventions, authority and non-destructive work rules
- `research/` — source-backed investigations and design decisions
- `src/` — our future authored mod source
- `tools/` — reproducible helper scripts
- `build/`, `deploy/` — ignored generated output
- `reference/` — local, Git-ignored third-party references (Only Story Music variants, Less Is More, FMC Audio Remaster)

Game installations, REDkit installations, original Wwise resources and third-party mod payloads are **read-only evidence**, never committed or modified in place. The music-control project is on `main`; `general-merge` is an independent compatibility-audit branch.
