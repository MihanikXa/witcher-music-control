# Codex instructions — independent Witcher 3 UI project

## Scope and authority
Work only in the `ui-overhaul` branch of `MihanikXa/witcher-music-control`. Do not alter `main` or `general-merge`. The primary authority for runtime resources is the *installed* The Witcher 3 Remastered 5.01/REDkit version; downloaded font/name-color mods are references, not guaranteed compatibility.

Do not modify the user's installed game, Vortex deployment/staging, Documents settings, saves or third-party packages without a separate, specific user authorization. Reading local files for research is permitted. Avoid blanket settings resets or regenerating the working merged scripts.

## User's visual direction
- Quiet, modern, beautiful and airy, but with character and Witcher identity; *Ghost of Tsushima* is a restraint/hierarchy reference, not a template.
- Prefer Gentium Book as a **starting taste reference** instead of a generic sans-serif. Test literary serif body styles versus a restrained serif/sans hierarchy before choosing.
- Eliminate thick black text strokes where possible; retain sufficient dynamic contrast on bright snow, overcast sky, bright UI, daylight, fire, caves and night.
- Replace excessively saturated friendly/hostile/name/highlight colors with restrained semantic colors (warm ivory, stone, sage, muted oxide and aged brass are provisional examples). Preserve hostility, focus, interactability and selection distinctions.
- Favor spacing and typographic hierarchy over boxes, ornament, clutter or indiscriminate hiding.
- Preserve practical controller readability, legibility on 1080p and 4K, English punctuation and accented names. Acceptance scope is English only; Russian/Ukrainian and Cyrillic validation are not required.

## Reference locations
The user will supply extracted mods locally under `reference/`. Read `reference/README.md`. All reference asset contents are gitignored. Use them as evidence; do not republish or edit authors' binaries. Obtain fonts under appropriate licenses and use vanilla game resources plus original modifications where feasible.

## Long-term roadmap and sequencing
Read [design/presentation-roadmap.md](design/presentation-roadmap.md) for the approved wider presentation and interaction plan. Its stages are *not* permission to implement or deploy a full overhaul immediately. Keep the current untouched-asset round-trip and NPC-nameplate proof as the first executable gate. Assess configuration-only SAHUD/FriendlyHUD opportunities before writing new logic; keep audio implementation on `main` and compatibility work on `general-merge`.

## Investigation before implementation
1. Inventory actual font, Flash/Scaleform/REDkit, menu, dialogue, subtitles, combat HUD, quest, inventory and NPC label resources used by current Remastered. Separate source-observed facts from inferences.
2. Determine exactly where typeface, weight, stroke/outline, glow/shadow, RGBA/name colors, sizes and alignment originate. Not every element shares a rendering path.
3. Map intersections with Seamless Adaptive HUD, FriendlyHUD, Mod Settings Menu Fix and compatibility package 04. Use `general-merge` only as read-only evidence; don't assume any UI asset can be replaced safely.
4. Verify any claimed technical recipe against the current installed resource format and toolchain. Never invent WitcherScript APIs, resource paths or Scaleform behavior.
5. Compare 2–3 coherent visual options. Preserve the user's Gentium preference while leaving room for licensed alternatives. Validate outlines and semantic colors independently before a global rewrite.
6. Prototype NPC nameplates as a separate Vortex mod with reversible deployment and no modification of existing managed files.
7. Check script/binary/resource priority collisions, potential font clipping, English glyph coverage, contrast, prompts and controller/keyboard input.

## Tooling, safety, and repository hygiene
Track original design documents, research findings, reproducible scripts/tests under `design/`, `research/`, `src/`, `tools/`, `tests/`. Keep generated files in ignored `build/` and `deploy/`; never force-add vendor mods, extracted game files, original game binaries, proprietary fonts or generated mod assets.

Start with an evidence-backed resource map, collision report, visual design specification and a minimal prototype plan. Do **not** begin by rebuilding the complete UI. Stop before Vortex installation and get explicit approval.

For each proposed patch, report the input resources/hashes, exact changed resource keys/paths, source provenance and license, build command, collision impact, game test criteria, and one-package rollback procedure.
