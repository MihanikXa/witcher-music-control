# Ink & Iron–first, selective UI refinement scope

> **Updated visual ownership policy:** See [Ink & Iron visual-first authority](ink-and-iron-visual-first.md). The user explicitly wants Ink & Iron's HUD visuals, with SAHUD/FriendlyHUD's behavior preserved and conflicting visual assets eligible for redesign. Older "preserve original HUD look" implications below are superseded.

**Decision recorded:** 11 October 2026. This is the user's newer, explicit design preference and supersedes the **scope and priority** of a from-scratch, complete menu/visual-system rebuild in [presentation-roadmap.md](presentation-roadmap.md). The older roadmap and master UI inventory remain coverage/reference documents, **not** a commitment to implement every screen.

**User's position:** They like Ink & Iron's cohesive near-black, parchment/gold, relatively minimal style in screenshots. They are not willing to pursue a labor-intensive redesign across every screen. They propose keeping Ink & Iron for nearly all screens with only selective shared styling changes (font, background and perhaps colors), **except inventory grids/shops and related interfaces**, where a more substantive redesign may be worthwhile. Compressed-looking text in screenshots is a *concern to test in-game*, not a confirmed failure of the shipped assets.

## Actual desired target

**Default: retain Ink & Iron's screen compositions, artwork and styling** unless an actual in-game test demonstrates a meaningful problem. Its dark look should not be automatically replaced by pale or translucent backgrounds. The new target is *coherence, readability and useful breathing space* with a literary identity—not making all screens bright or turning the game into Tsushima.

### Decision matrix (screen-level hypotheses)

| Screen / system | Initial decision | Intended changes / limits |
|---|---|---|
| Character, skills/mutations | KEEP | Prefer existing organization/tree/equipped slots; test tiny labels and low contrast only |
| Journal, quests | KEEP | Preserve list + objectives + lore columns; modest font size/leading, selected emphasis if needed |
| Alchemy | KEEP | Preserve item/list + ingredients + details layout; only typography/spacing/contrast where necessary |
| Glossary, bestiary, books/tutorials | KEEP | Preserve engraved illustrations and reading layout; refine readability if required |
| Pause menu | KEEP | The world-continuity background, restrained labels and selection look good |
| Main menu, meditation, loading, Gwent, noticeboards, other minor screens | RETAIN selectively | Don't redesign just for completeness; evaluate user-visible defects |
| Inventory + equipment | REDESIGN selectively | Preserve character preview and strong circular equipment grouping; reconsider sparse/difficult left inventory grid, information density, comparison position and selected-item readability |
| Merchant/shop | REDESIGN | Correct overly tiny/dense merchant item cluster, huge unused surrounding area and scattered compare info; preserve buy/sell, selection and relevant merchant functionality |
| Stash, loot, crafting or other inventory-grid variants | REUSE only proven new grid pattern | Audit each first; don't automatically rewrite all crafting/alchemy just because it has lists |
| Player statistics | REFACTOR for readability | Preserve depth/data and character view, but improve the tiny cramped three-column statistics presentation; do not hide advanced stats |
| Gameplay HUD | SELECTIVE / preserve existing baseline | Do not blanket-install Ink & Iron HUD over SAHUD/FriendlyHUD/accepted NPC labels, interactions and subtitles |
| Map / minimap | SELECTIVE | Maintain Smooth Map + SAHUD functionality; any Ink & Iron style is optional and needs a concrete resource-owner check |
| Global font, text shadows, color, background | ADJUST minimally | Gentium Book is already user-accepted; preserve NPC Colors v4 and NPC Shadow v1, and the pending interaction-v2/subtitle-v1 runtime test path. Try Ink & Iron's defaults at real 1080p/4K before replacing. Avoid cross-menu restyling unless one problem recurs |

## Screenshot-grounded observations (hypotheses)

User examples: Ink & Iron inventory, character, journal, alchemy, shop, character stats, glossary, paused-world and HUD details.

- **Keep:** character/skills, journal, alchemy, glossary and pause show distinctive regions, clear selected states and strong visual coherence; do not redesign out of principle.
- **Inventory:** the paper doll / circular equipment identity is successful, but the left item area is visually sparse and small; selected-item details occupy a third competing column. Investigate denser or better-clustered *usable* inventory hierarchy.
- **Shop:** merchant item thumbnails are very small and dense while the rest has a lot of empty area. Prioritize scannable grids and direct item comparisons rather than another visual skin.
- **Statistics:** very fine, tight text may be hard to read at viewing distance despite useful separation into categories. Grouping/scale first, not loss of information.
- **Typography:** screenshots can be scaled/compressed; evaluate actual text at the user's 1080p projector and 4K monitor. Do not mistake downscaled screenshots for asset resolution or prescribe a global font switch in advance.
- **Background:** near-black / gold may be a positive feature. Test contrast and fatigue, not arbitrary brightening.

## The most important technical constraints

**Current installed baseline:** `general-merge` working compatibility setup, Hoods inventory, Geralt Outfit Wheel (common/root/overlay), Smooth Map worldmap, SAHUD and FriendlyHUD, movement patch, plus `ui-overhaul` user-accepted font/NPC modules. Preserve exact working packages and record winners before changing any loaded resource.

At inspection time, Ink & Iron's **0.7.4** modular distribution (Nexus #13111) includes: UI, HUD, Fonts (or alternative Fonts_Vanilla), Dialogue, Buttons, Icons, Glossary, MainMenu, Gwent, Loading and selectable Map styles. It explicitly notes:
- UI/HUD have a font-module dependency, including a published vanilla-font alternative;
- the **whole-file** `.redswf`, `.env` and `fonts.xml` replacements cannot be resolved by Script Merger;
- UI includes `panel_inventory`, `panel_common`, `panel_overlay`, `panel_worldmap` etc.; HUD includes `hud_enemyfocus`, `hud_wolfstatbars`, `hud_minimap2`; these overlap the working mod stack;
- some blacksmith/armorer/enchantment UIs are only partly restyled and the beta has limited tested surfaces;
- the author restricts redistribution and reuse outside private play. **Newest explicit user direction permits local, personal modification of extracted assets; do not require permission before private prototyping.** Do not publish or redistribute modified third-party payloads.

**Do not assume 'use Ink & Iron as the base' means that All-in-One can be deployed safely.** Layout/asset research can use its unpacked files read-only; an installable version must respect published module dependencies, real file collisions and the user's accepted patches. Vortex load order is not a true binary merge.

## Reduced-work execution plan

1. **Stop the global rebuild plan.** Keep ongoing, already-built accepted work untouched. Interaction v2 and subtitle shadow v1 are offline-built private trials pending visual runtime acceptance, not release-ready by assumption.
2. **Acquire current Ink & Iron modular reference archives** into a local, ignored reference folder, with version + source manifest. Audit modified resource keys and actual layout behaviors against active mods; preserve original game and Vortex install.
3. **Optional reversible install test** in a separate cloned Vortex profile, *only after the owner/dependency audit*. Compare untouched official Ink & Iron at real viewing distance. Do not install All-in-One over the active Compatibility Test profile or disable existing user-accepted patches to chase aesthetics.
4. **Document exceptions** from screenshots and in-game operation: one Inventory case, one Shop case, one player-stats case, and any genuinely illegible repeated typography. Do not broaden automatically.
5. **Build one focused vertical slice** of Inventory/grid+item details based on actual input resources and working controller, mouse, item selection, comparison, equip, filter, sort and merchant behavior. Preserve Hoods and Outfit Wheel features or document irreducible conflict.
6. **Reuse only successful patterns** in Shop / Stash / Loot and similar grid-heavy variants. Keep others as published when satisfactory; cosmetics only when actually needed.
7. **Build private personal-use adaptations when useful.** Do not commit or redistribute Ink & Iron asset copies or adapted binaries; keep generated/private resources gitignored and record one-resource manifests and rollback.
8. **Consider optional visual unification** only after real in-game comparison—Gentium, color, backdrop, and subdued shadow should be tuned for legibility but need not override cohesive Ink & Iron styling.

### Acceptance criteria

- Retained screens feel like Ink & Iron, not an unrelated second skin.
- Inventory/shop readability, density, and task completion are meaningfully better, not just prettier.
- Real 1080p and 4K viewing-distance typography is comfortable; no unverified screenshot-compression assumptions.
- Gamepad focus, keyboard/mouse, prompts, scroll, loot, equip, sorting, shop buy/sell, stats and mod menu work.
- No regression to user-accepted NPC colors, shadow, English Gentium or working analog gait/HUD functions.
- No unapproved installs or wholesale changes, no redistribution of unlicensed mod assets.

### Immediate Codex task

**Audit rather than implement:** inspect local Ink & Iron UI, Fonts and relevant HUD modules, identify exact collisions/feature dependencies with the current installation, and produce a concise `KEEP / MODIFY / EXCLUDE / CONFLICT` map. Compare on-screen actual behavior at 1080p and 4K through user-provided captures where possible. Propose the narrowest safe installation experiment and one concrete inventory-grid vertical slice. Stop before deployment or large menu rewrites.
