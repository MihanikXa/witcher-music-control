# Gear-grid v1 — explicit user visual feedback and sequencing correction

**16 October 2026.** This file contains the user's newest explicit response to the first Gear-grid screenshots, followed by distinctly labeled assistant interpretation. It supersedes earlier assistant-only design proposals where they conflict.

## Direct user statement (verbatim)

> I'll tell you my thoughts and you tell me how congruent they are with what you already said. I think grid looks too visually busy with too many individual dots, and simulteneously too small and secondary on the side, geralt could be a bit bigger, too much text and detail everywhere, too many button hints at the bottom, too visually intrusive, the background, which we might change anyways when work more on the rest of the menus, is too intrusive too, I would like very clean, maybe even slightly transparent background for immersion. Obvious stuff like bottom item slots and details problems + other stuff I agree with you. The top is also too busy but ink and iron fixes it pretty well already, we just haven't implemented it yet, maybe we should first implement the whole menus ink and iron base and then do the rest of inventory?

## Explicit preferences (not assistant extrapolations)

- Grid dots/placeholders are too numerous and visually busy.
- The browse area feels too small, pushed to the side and visually secondary.
- Geralt could be larger.
- Too much persistent text/details and footer input hints; the whole UI competes for attention.
- The backdrop is visually intrusive; desire an extremely clean, possibly slightly translucent background, with greater immersion.
- Top navigation still looks too busy, but user expects Ink & Iron's **complete** menu baseline to resolve much of that. This baseline has not yet been implemented across menus.
- Previous objections to auxiliary slots beneath Geralt, disconnected right-side item details and other screenshot-review issues are agreed with.
- User proposes **first completing the Ink & Iron menu baseline, then returning to Inventory design**. This is an explicit sequencing proposal, accepted as the next working plan below.

## Assistant interpretation / proposed mechanisms — not direct user specifications

1. Reduce persistent grid decoration; allow actual item art, spacing and a single selected state to define the browse area. Preserve underlying hit areas/selection contracts. Do not solve the density complaint merely by shrinking dots.
2. Give the Inventory grid dominant functional/visual weight; raise Geralt's visual scale modestly only after creating an uncluttered preview region. Adapt the layout to few versus many items.
3. Condense duplicate headings. Show descriptions, comparisons and command hints **when relevant**, without losing access. Reduce permanently displayed bottom hint count.
4. Test a clean backdrop/controlled translucency. **Verify that the game world actually renders behind the menu before promising any immersion benefit**; alpha alone may reveal a static/black scene or compromise text contrast.
5. Establish the actual **Ink & Iron 0.8.6 shared menu baseline** first, before v2; do not fabricate a comprehensive all-in-one setup from the single Inventory movie now used by the v1 prototype. Current build report says 0.8.6 was used as Inventory input, while the upstream **I&I UI/official Hoods patch did not own deployed Inventory** before the prototype.
6. This is a **menu integration phase**, not permission to enable whole All-in-One, replace the accepted custom HUD, alter the existing movie priorities blindly or replace the working 0.8.6 Gear v1 candidate automatically. Use the modular 0.8.6 UI/menu sources with targeted compatibility checks: common/overlay `inkart:` backgrounds and Outfit Wheel exports; Smooth Map hint ownership; Fonts (Vanilla)/QuietFolio; Hoods dye patch/current Gear prototype precedence. Test actual new version; historical 0.8.0 audit hashes are informative, not release authority.
7. Preserve one isolated reversible v1 reference. After shared menu styling is accepted, do a genuinely redesigned Inventory composition, not merely a rearrangement of all 20 paperdoll slots.

## Immediate workstream gate

**First:** Version-pinned 0.8.6 menu/UI module inventory and collision-aware integration in a cloned Vortex profile, with one private modular baseline and exact rollback. Preserve every accepted custom HUD v4/RC2 resource, behavior and existing mods. Test shared nav/header/background across Glossary, Alchemy, Quests, Character, Meditation, Inventory and one context using common/overlay/map. No automatic install.

**Then:** Reopen the one-screen Inventory redesign with user-driven requirements above; consider deeper changes only after the shared baseline is visible and accepted. Avoid another quick v2 reshuffle that still has fixed small side grid, dotted clutter, huge footer, and feet-level slot cluster.

User statements remain attributable to the user; layout strategies here are assistant hypotheses.
