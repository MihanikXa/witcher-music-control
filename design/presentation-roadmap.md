# Presentation & interaction roadmap — Witcher 3 Remastered

**Status:** Approved direction / future implementation plan, **not built or deployed**.  
**Date:** 9 October 2026.  
**Owner:** `ui-overhaul`. This expands the long-term design remit beyond typography while retaining the existing NPC-nameplate proof as the immediate task.

## Goal and design mechanism

Make Witcher 3 feel **lighter, more coherent, more spacious and more immersive**, with a literary identity rather than a generic flat minimalist skin. The comparison points are the user's Ghost of Tsushima equipment/techniques screenshots and Breath of the Wild inventory screenshot. These are **design references, not assets to copy**.

The relevant mechanism is **low competition for attention**, not simply fewer icons or less information:

- Ghost of Tsushima's equipment composition makes the character the center and places important functions in distinct regions. The techniques screen concentrates high chroma in one selected area, leaving other elements quiet.
- Breath of the Wild's inventory is fairly dense; it remains legible because object icons, category groupings, selection, descriptions and the game world follow one consistent grammar.
- Witcher 3 should retain necessary RPG complexity, quest information and world specificity, while avoiding simultaneous demands from labels, markers, pop-ups, minimap routes, redundant prompts and saturated effects.

Design principles:
1. **World first.** Show information when it helps the current activity, not permanently.
2. **Progressive disclosure.** Ordinary items/actions are quiet; focused or high-consequence details are explicit and easy to request.
3. **One visual grammar.** Typography, focus treatments, icon shape, highlight colors, timing and transitions communicate consistent roles.
4. **Composed screens.** Distinct visual regions and meaningful negative space, not merely fewer items.
5. **Character without ornament overload.** A restrained, literary Witcher expression (Gentium Book a starting reference), not a Tsushima clone.
6. **Preserve agency and clarity.** Removing guidance must not produce repeated menu-opening, missed objectives, failed controller navigation or unreadable bright-background text.
7. **Reduce redundant friction.** The game's authored dialogue/story structure is a strength; reduce administrative interruptions, not story payload.

## Prioritized opportunities

These are feasibility **hypotheses** to validate against current 5.01 source assets and the installed mod stack, not verified implementation claims.

| Workstream | Intended change and reason | Potential experiential impact | Expected effort / primary risk |
|---|---|---|---|
| Context-sensitive exploration HUD | HUD recedes when exploring; combat info comes back in danger; on-demand navigation and markers during Witcher Senses or user input | Very high | Low–moderate with existing SAHUD/FriendlyHUD; overlapping state ownership |
| Navigation/discovery hierarchy | Prioritize selected goal, seen landmarks and user markers; reduce undiscovered ? checklist and always-on GPS; preserve an optional precise route | Very high | Moderate; some quests require explicit waypoints |
| Typography/text rendering/color | Refine font hierarchy, soften heavy outlines, mute bright friendly/hostile labels while preserving semantic recognition; NPC labels first | High | Moderate–hard; GFx assets and readability in snow/fire/night |
| Menu composition | Focused equipment/character presentation, grouped satchel and details on request; consistent high-contrast selection and controller focus | Very high | Hard; complex movies, resource collisions, input/focus |
| Notifications and interaction feedback | Group routine loot/XP, reduce redundant prompts; reserve distinct moments for consequential quest/progression updates | High | Moderate; scripted triggers and missed state changes |
| Camera/presentation continuity | Stable framing, restrained shake/zoom/sway, gentle changes that don't fight input; test current Living Camera first | Medium–high | Moderate; gameplay readability and motion jitter |
| Music/ambience negative space | Quiet traversal when appropriate; retain bespoke story and combat cues; promote environmental sound as scene detail | Very high | Separate `main` music-control project; Wwise routing/quest exceptions |
| Scene-specific color/exposure | Reduce disruptive UI effects, excessive sharpening or bloom selectively; preserve the environment's region-specific colors | Medium | Moderate; no indiscriminate global desaturation |
| Fundamental world/quest simulation | More systemic discovery, traversal and quest guidance | Potentially transformative | Very hard, likely outside scope; Witcher 3 is an authored RPG |

### A. Exploration HUD policy — configure before coding

Aim for:
- Ordinary exploration: world dominant; no permanently bright objective stack, inventory counters or unnecessary markers.
- User request / Witcher Senses: useful navigation and relevant nearby information appears, then recedes.
- Combat/danger: health, selected tools, target feedback and other high-value combat elements return reliably.
- Navigation: one active objective plus deliberately chosen waypoints; minimize merchant/herb/POI saturation and long-range icon noise.
- Avoid blindly disabling every minimap feature: if actual quest directions are insufficient, keep on-demand precise guidance.

**First implementation route:** audit existing Seamless Adaptive HUD and FriendlyHUD options in the working Vortex test profile and document a reversible configuration baseline. Only propose new logic when a concrete missing behavior is reproduced.

### B. Map, exploration and discovery

- Audit the difference between discovered locations, player-marked places, available quests and auto-revealed question marks.
- Test filtering *undiscovered* marker clutter without concealing essential narrative leads.
- Prefer environmental landmarks and optional proximity cues to constant breadcrumb/GPS paths.
- Preserve a one-action way to request explicit routing, since Witcher 3 quest design is not always spatially self-describing.
- Score success by actual exploration flow and fewer compulsory map reopenings, not by the smallest visible marker count.

### C. Text and visual language — the active short-term track

- Start with the current `hud_enemyfocus.redswf` unchanged round-trip gate, then NPC nameplate color-only/shadow-only trials and a reversible combined prototype; see [existing implementation plan](implementation-plan.md).
- Next validate a licensed Gentium-style font trial independently. Wider menu text, letter metrics, subtitle clipping and contrast need actual in-game checks.
- Extend to dialogue, subtitles, interaction prompts, quest updates and menus only after identifying each distinct renderer.
- Proposed palette: ivory/stone primary/secondary; sage friendly; oxide hostile; aged brass selected. Treat all as provisional, not global blind replacements.
- Replace thick hard-edged strokes with restrained shadows/backing *only if legible* on bright snow, daylight sky, fire/bloom, overcast fields and dark interiors.

### D. Menu composition — prototype one screen, then expand

**First candidate: Inventory.** The user-supplied Ghost of Tsushima equipment and Breath of the Wild inventory references suggest:
- Distinct spatial roles for equipped items, Geralt preview, grouped satchel items and focused details.
- One readable selection focus; non-selected controls recede without disappearing.
- Item imagery and consistent grids carry identification; avoid duplicating the same information in labels, badges and notifications.
- Full descriptions, comparisons and advanced RPG information remain available on request.
- Preserve quick controller traversal, scrolling, search/filter/sort and item management. Avoid expensive animated transitions that create delay.

A visually attractive static mockup is **not** adequate. Prove actual input focus, controller and keyboard paths, item interactions and preserved original functions. Audit Hoods, SAHUD, Bestg and Geralt Outfit Wheel resource ownership before replacing any menu movie. Inventory first; map/journal/skills only after an approved operational prototype.

### E. Notifications / low-value feedback

| Event | Desired treatment |
|---|---|
| Routine herb/loot pickup | Brief grouped line or optionally silent; avoid overlapping announcements |
| Minor XP / trivial counters | No prominent toast unless explicitly requested |
| Important quest development | One clear, restrained and readable announcement |
| Major skill/progression change | Distinct but short emphasis, appropriate to significance |
| Nearby NPC labels | Show through proximity/focus/interaction, not always over every character |
| Ongoing objective | Compact or temporarily hidden with an easy reveal |

Review FriendlyHUD/SAHUD controls and notification assets first; preserve information that cannot be recovered later.

### F. Presentation outside the UI

- **Audio:** maintain a separate music-control project on `main`; context-specific quiet exploration and authored cues, with ambient-world audibility. Do not change audio banks in `ui-overhaul`.
- **Camera:** first tune existing Living Camera without reintroducing the user's observed movement jitter. Prioritize stability and input authority over cinematic sway.
- **World colors:** do not uniformly desaturate Witcher 3. Preserve warm sunlight, cold mist, dark foliage and region identity. Audit only disruptive sharpening/bloom/HUD visual effects.
- **Game-system boundary:** Witcher 3's authored quest structure, traversal limits and limited systemic physics cannot be converted into Breath of the Wild through UI alone. Do not degrade narrative staging to imitate a sandbox.

## Phasing and gates

| Stage | Deliverable | Gate before next stage |
|---|---|---|
| **0 — Existing active work** | Verify current-version UI asset round-trip; separate and combined NPC nameplate prototypes | Unchanged GFx/CR2W contracts, reproducible build, no HUD/script conflicts, explicit Vortex approval |
| **1 — Text foundation** | Independently removable typeface trial, text-outline/color treatments and text surface validation | Real-game legibility, glyph coverage, long strings, bright/dark environments, original menus unaffected |
| **2 — Exploration & information audit** | Inventory what current SAHUD/FriendlyHUD can already do, propose profile settings and identify missing capabilities; no unnecessary new UI hooks | User tests one walk/combat/quest/navigation route and confirms improved flow |
| **3 — Menu vertical slice** | Full Inventory interaction prototype with comparison recordings and original resource ownership accounted for | Controller/keyboard focus, equipment changes, scrolling and descriptions all functional; safe rollback |
| **4 — Broader polish** | Extend verified patterns to map, journal, quests, notifications, prompts, menu transitions | No regressions in story/quest/loot/targeting; portable modular install |
| **5 — Cross-project integration** | Coordinate music/ambience and camera/visual setting recommendations without merging unrelated branches | Compare user experience across uninterrupted travel/combat/story sessions |

**Do not parallelize disruptive large UI rewrites with the stage-0 NPC proof.** Research and interaction inventory may proceed in parallel, but preserve clear package/resource ownership and don't change the active build target without authorization.

## Acceptance and failure criteria

Success means **less attention competition and friction while keeping information discoverable**, not an empty or uniformly beige screen. Test at 1080p and 4K, controller and keyboard, daylight/snow/fire/night, exploration/combat/dialogue/inventory/Gwent, long names and current English localization.

Measure through concrete before/after scenarios:
- Can the player travel and orient without persistent route clutter or constant map reopening?
- Can a player learn a hostile/friendly target's status instantly in bright and dark scenes?
- Can the player access an item, equipment comparison or relevant quest fact with as few or fewer actions as before?
- Do HUD modules appear reliably when needed and recede promptly after the action?
- Do scene transitions, notifications and camera changes avoid unwanted interruption or jitter?
- Can each new module be disabled without altering the five deployed compatibility packages?

Failure signs: illegible low-chroma labels in daylight, missing combat state, buried item details, more menu visits, damaged quest navigation, janky focus/animations, lost mod functionality or a generic visual skin with no Witcher identity.

## Safety and project boundaries

- The existing `general-merge` profile is a **known-working user-reported baseline**, including its analog gait patch. Inspect it read-only; don't accidentally rebuild its scripts, reset HUD settings or enable the broken Over 9000 mod.
- Respect Vortex ownership: new test packages are separately installable/rollbackable and don't modify existing hardlinked deployed files.
- `main` owns the music/WWise work. This branch can document cross-project integration but must not modify audio banks.
- Use English-only font target for the current phase; do not silently introduce a multi-language implementation dependency.
- Treat third-party mod packages and copyrighted game assets as local read-only references; commit only original research/source/build tooling.
- Where resource overlap prevents safe independent replacement, document the combined-asset requirement explicitly instead of declaring load-order priority a merge.
- Every actual implementation needs hashes, resource-key manifest, compilation/cook proof, in-game validation steps and rollback.
- This roadmap is **scope direction**, not blanket permission to edit/deploy/overwrite the live game.

## Next action after this document

Continue the **already planned unchanged asset round-trip and NPC-nameplate prototype**. Separately commission a focused **information-hierarchy inventory** of the current Witcher 3 gameplay HUD, Inventory, Map and Journal, grounded in the user's screenshots, current UI assets and deployed mod features. That audit should report overlaps, missing configuration capabilities and one proposed Inventory vertical slice; **do not begin the full inventory rewrite yet**.
