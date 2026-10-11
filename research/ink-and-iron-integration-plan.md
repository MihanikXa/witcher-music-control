# Ink & Iron modular baseline — integration and installation gate

**Superseded installation audit:** the user switched the canonical input to
`reference/ink-and-iron-0.8/` during the 11 October audit. Use the
[0.8 evidence and installation strategy](ink-and-iron-0.8-integration.md), its
per-resource matrix and validation checklist. In particular, the 0.8 Vanilla
Fonts package is alias-only and does not replace QuietFolio's English library.
The older acquisition map below remains historical planning, not deployment
instructions.

**11 October 2026; planning only, NOT installed or verified against user's local archives.** User explicitly wants to **adopt almost all of Ink & Iron 0.7.4 as the baseline** for retained interfaces and build only the needed exceptions on top. This document establishes how to do that without overwriting the working mod profile.

Reference: [Ink & Iron v0.7.4 on Nexus](https://www.nexusmods.com/witcher3/mods/13111?tab=files), last updated 10 Oct 2026, by WinterElfeas. Current description says 5.0/Remastered only; same-file `.redswf`, `.env`, `fonts.xml` conflicts cannot be merged by Script Merger. Read-only description evidence is *not* a local installed-file manifest.

## Desired final outcome

- Published Ink & Iron structure/style unchanged in character/skills, quests/journal, alchemy, glossary/bestiary, crafting, meditation, pause, settings, most popups and secondary screens.
- Inventory and merchant/shop are explicit exceptions; overhaul the composition and browsing/management experience, not just item icons. See [inventory direction](../design/inventory-ux-direction.md).
- Player statistics: improve legibility as needed, retain every stat.
- Shared typography/background/semantic colors: keep Ink & Iron defaults except deficiencies observed in the actual game; do not reflexively change the dark palette. Preserve user-accepted Gentium/QuietFolio, NPC Colors v4 and NPC Shadow v1 if technically possible.
- Existing SAHUD/FriendlyHUD, Hoods, Geralt Outfit Wheel, Smooth Map, current movement compatibility package and any accepted UI addons: **protect their functionality**, not merely their folder names.
- Interaction v2 / subtitle shadow v1 remain private trials pending user approval, not automatically part of this baseline.

## Modular acquisition map — v0.7.4

| Nexus module | Intent | Installation decision |
|---|---|---|
| **UI** | Main source of retained menu layouts; includes Inventory/Shop to replace later | **Core target; audit first.** Full-file collisions with Hoods inventory, Outfit Wheel common/overlay and Smooth Map world-map movie |
| **Fonts (Vanilla)** | Required Ink & Iron font support without its visual IM Fell replacement | **Required dependency candidate.** Still check aliases/`fonts.xml` and `fonts_en` collision with accepted QuietFolio. Do not activate both blindly |
| Fonts (IM Fell) | Alternative typography | Reference only initially; do not activate alongside Fonts (Vanilla) |
| Dialogue Choices | Literary styled choice list | Keep if compatible with FriendlyHUD dialogue hooks and current font aliases; requires Fonts |
| Controller Buttons | Ink-style button glyphs outside UI/HUD | Optional, contingent on user/controller artwork compatibility |
| Icon Pack | Item/skill icon styling | Optional keep; verify collisions with icon replacements and legibility |
| Bestiary Art | Engraved portraits | Likely safe candidate, but audit resource ownership and game metadata |
| Animated Main Menu | Etched main-menu scenes | Optional; decide in-game |
| Loading Screens | Panorama/loading art | Optional; decide in-game |
| Gwent Board | Board and tags (cards/deck builder remain vanilla) | Optional; verify Gwent Deck Choice patch resource paths |
| **HUD** | Minimap, enemy name, status bars, quests, quickslots | **DEFER** until exact SAHUD/FriendlyHUD/NPC movie merge/compatibility plan; enabling wholesale risks accepted functionality |
| World Map tile variants (Inked/Charcoal/Parchment/Shadow) | Full map+minimap tile visual styles | **DEFER**: existing Smooth Map. One variant only if deliberately chosen |

The author says **UI/HUD depend on a Fonts module**, and Dialogue requires it too. The Fonts (Vanilla) alternative is **not a guarantee of coexistence with QuietFolio**, because resource ownership and special font aliases need inspection. The description recommends updating UI/HUD/Buttons together; identify **which files actually depend on the paired versions**, rather than inventing a safe partial split. No All-in-One install.

## Known baseline collisions to verify before enabling UI

| Resource/feature | Current installed owner/role | Ink & Iron risk |
|---|---|---|
| `inventory/panel_inventory.redswf` | `modHoods` | whole-resource winner replaces inventory features |
| `common/panel_common.redswf`, `overlay/panel_overlay.redswf`, root/import contracts | `modGeraltOutfitWheel` | scene/menu/prompt integration can regress |
| `worldmap/panel_worldmap.redswf` | `modsmoothmap` | whole-resource collision; tile pack distinction matters |
| `hud/hud_enemyfocus.redswf` | accepted NPC Colors/Shadow movies; SAHUD/FriendlyHUD script contracts | enabling I&I HUD overrides accepted name effects |
| `hud/hud_wolfstatbars.redswf`, `hud/hud_minimap2.redswf` | Seamless Adaptive HUD | cannot resolve by blind Vortex priority |
| `witcher3/fonts_en.redswf` and `fonts.xml` | `modQuietFolioEnglish` and current game/other mods | missing aliases or fonts overriding accepted Gentium |
| `gwint/gwint_game.redswf` and card-choice/menu resources | Gwent Deck Choice layout replacement and current native/modded game | feature collision requires file/path inspection, not assumptions |
| menu component/option/annotation scripts | Compatibility Test profile (package 04, Mod Settings Menu Fix, others) | Ink & Iron annotation stacking is advertised, not a guarantee |

These are *known risk targets* from current repo's [resource map](resource-map.md) and author's disclosed module file list; the **precise installed winners still need actual archive manifest comparison**.

## Safe experiment: preserve working profile, introduce Ink & Iron in stages

**Stage 0 — local read-only audit (Codex):**

1. Download each desired current **separate Nexus module**. Extract untouched packages under `reference/ink-and-iron/v0.7.4/<module>/` in the local `ui-overhaul` worktree; this directory is gitignored.
2. Produce machine-readable resource-key / same-filename / native script annotation and texture-cache inventories, with archive hashes, provenance and version.
3. Compare against user-selected **deployed** profile and compatibility release, not just vanilla or Vortex staging archives.
4. Classify every owned resource: KEEP AS IS / SAFE OPTIONAL / COLLISION REQUIRES MERGE / DELIBERATELY EXCLUDE / UNKNOWN. Name exact dependency between main UI and fonts, HUD, buttons.
5. Offer a verified recommended *module subset and file-level precedence*, explaining any loss of features. Do not claim Vortex priority merges bytecode or SWFs.

**Stage 1 — isolated, reversible baseline test (user, after Stage 0):**

1. Vortex: clone **Witcher Compatibility Test** into a separate named **Ink & Iron Integration Test** profile. Ensure saves/settings or live-game deployment can be rolled back. Switching profile re-deploys the same game folder; do not install two conflicting profiles simultaneously.
2. Preserve current original profile as untouched baseline and keep all installed mod archives/backup merged folder. Install modules through Vortex **separately**, not All-in-One and not manual game-folder extraction.
3. First test only optional, conflict-checked cosmetics (Bestiary Art, Animated Main Menu, Loading, Icon Pack, Gwent Board, Controller Buttons as relevant). Confirm real changes; don't assume conflict-free from module names.
4. Then enable **UI + one compatible Fonts bridge** according to the *actual audit*, handling Hoods, Outfit Wheel and Smooth Map overlaps intentionally. Do not disable these mods or choose winner reflexively just to make UI show. If not safely compatible, report blocker and implement a supported combined asset/alternative strategy *before* deployment.
5. Initially keep **Ink & Iron HUD disabled** so accepted NPC and SAHUD effects remain; confirm whether UI or optional modules **require** HUD and how Ink & Iron options are surfaced.
6. Restart game when font modules change, then test menu hub, inventory, player stats, character, quests, alchemy, glossary, merchant/shop, pause, settings and mod menus; verify keyboard/controller navigation and current accepted movement, HUD, fonts.
7. Record captures at actual 1080p/4K, menu font readability, encountered collisions and Vortex winners, live broken/missing behaviours, not just startup success.

**Rollback:** close game, switch to original Compatibility Test profile, redeploy, verify game. Do not regenerate compatibility merges, overwrite backups or modify saves. Keep optional test modules isolated.

## Permission boundary

The Nexus author explicitly requires permission to modify or reuse Ink & Iron files/assets; upload to other sites forbidden. The user may install the original packages for personal play. Before preparing any modified derivative **from author assets**, seek permission. Without it, retain upstream packages unchanged and make independent original modifications to current vanilla game assets instead. Do not publish/repackage vendor compiled payloads in this GitHub repo.

## Immediate action requested from Codex after references arrive

Perform **Stage 0 only**, report an exact package-level and per-key compatibility plan, and draft a one-screen inventory-grid prototype feasibility report. Stop before touching installed game, Vortex, user settings and saves. Continue parallel accepted interaction/subtitle tests separately.

**Do not present module acquisition as proof of safety**; the goal is to install the retained Ink & Iron baseline after a short, focused compatibility audit, not to restart a massive UI redesign.
