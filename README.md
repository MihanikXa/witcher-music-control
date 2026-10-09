# Witcher 3 — UI Overhaul

An independent, research-first project for refining typography, text effects, NPC nameplates and interface colors in **The Witcher 3 Remastered 5.01**.

## Visual target

Clean, light, breathable and modern, **with character**. Use *Ghost of Tsushima* as a reference for restraint, hierarchy and environmental integration, **not** for copying its Japanese visual motifs. Retain the Witcher world's distinctive texture. The user prefers the **Gentium Book** reference over the original or an undifferentiated sans-serif.

Focus on replacing thick hard-edged black text outlines, overly saturated red/green text, cramped labels and inconsistent emphasis with precise typography, a restrained palette and context-sensitive readability. Do not merely desaturate all UI elements globally.

## Project boundaries

- `main` is a **different music-control project**.
- `general-merge` is the **working compatibility project**. It contains the user's deployed Vortex Compatibility Test profile, successful analog gait integration, Seamless Adaptive HUD and FriendlyHUD. Treat it as read-only compatibility evidence.
- `ui-overhaul` develops a **separately installable UI mod**. Never merge or redeploy unrelated music, movement, combat or quest modifications.

## Workflow

1. Inspect the four local read-only references in `reference/` and current REDkit/vanilla resources.
2. Build a grounded text-surface/resource map and collision map against `general-merge`.
3. Propose and compare 2–3 precise typography/color treatments with real-game examples.
4. Prototype **one small, independently reversible NPC-nameplate treatment** first.
5. Extend incrementally to dialogue/subtitles, notifications, inventory and menus; package optional modules when feasible.
6. Validate visual contrast, clipping, localization and coexistence with current Vortex mods before any live deployment.

Codex development instructions: [AGENTS.md](AGENTS.md). Design brief: [design/brief.md](design/brief.md). Reference locations: [reference/README.md](reference/README.md).

Only original source, reports and build tools belong in Git. Never commit extracted third-party/game assets or compiled mod archives.
