# HUD refinement v2 — user runtime feedback and glyph diagnostic

**Report date:** 13 October 2026. **Status:** v2 functional and visual shape improvement confirmed by user; Xbox button glyph visibility unresolved; red palette not accepted. Distinguish reported observations from hypotheses. Do not rewrite the immutable v2 build receipt's `runtime_tested: false` snapshot.

## Direct user statement (verbatim)

> Everything works well, but I don't see the new buttons, might be something to do with my order, check, but might be not. Also, the red colour is still too pale on the enemy bars and name, but the narrowness and how it is less bulky is great

## Explicit acceptance and corrections

- **Accepted: functionality and enemy overhead *geometry*.** Keep current thin health bars, reduced total overhead bulk, font sizes, spacing, lock-ring and indicator hierarchy unless a separately demonstrated bug requires change. Boss bars were accepted previously and must remain unchanged.
- **Rejected: red palette is still too pale.** In v2 the ordinary enemy fill is `#AA7565` and hostile name `#DE9C89`. Increase **saturation/depth** for the red bar and hostile name together; target richer, clearer red while avoiding vanilla neon/aggression. Do **not** undo the accepted shape/size changes or blindly raise all semantic colors. Neutral/friendly/Axii/VIP mappings are not rejected by this report. Treat any specific candidate RGB as a proposed visual trial, not an inferred exact user preference. Coordinate native name, ghost name/role and accepted Colors v4 script paths so paint sources cannot fight.
- **Unresolved: new controller buttons not observed.** The user says "I don't see the new buttons", **not** that button input is broken, and does not specify whether old artwork remains or icons are absent. Ask only if needed after read-only diagnosis.

## Why priority alone is not enough

The **12 October build-time** resource-owner audit recorded `modInkIronHUDRefinementV2` intended at priority 31, SAHUD 32, Outfit Wheel 36, NPC Shadow 38 and interaction v2 43. Lower numeric wins. The v2 bundle includes glyph-patched `hud.redswf`, `panel_common.redswf`, `panel_overlay.redswf`, plus other movies. **These values describe the archived build/test profile plan, not an inspection of the user's current Vortex deployed order on 13 October.** The user's report of the slimmer overhead enemy UI supports *some* v2 resource winning, but does **not** prove the shared HUD root/common/overlay winner or actual icon lookup path.

The current `tools/refine-ink-hud-movies.py` patches the `ICO_Xbox_*` SymbolClass/1008 external image rectangles to a new atlas while preserving symbol IDs. The v2 build has **306 identities across nine movies** and passed static packaging/resource checks. This establishes resource content, not that the *runtime buttons* use these icon definitions. It may be a wrong surface, competing owner, different input-device path, or a runtime texture/layout issue. No single cause has yet been demonstrated.

## 13 October 2026 — user-provided Vortex load-order export checked

User supplied `loadordenow.json`: **45 unique mods, all enabled, 0–44 unique contiguous numeric prefixes**. This is a user-provided *load-order export*, not independent live inspection of bundle bytes, actual `mods.settings` on disk, game resource winner or UI textures. It supersedes the old **assumed** build-time priority numbers for evaluating the ordering question.

| Prefix (lower wins) | Enabled mod |
| ---: | --- |
| 10 | `modHoods` |
| 18 | `modFriendlyHUD` |
| 28 | `modInkIronAdaptiveBarsTest` |
| 29 | `modInkIronHUDAliasesTest` |
| **30** | **`modInkIronHUDRefinementV2`** |
| 31 | `modSeamlessAdaptiveHUD` |
| 35 | `modGeraltOutfitWheel` |
| 36 | `modQuietEditorialNPCColorsV4` |
| 37 | `modQuietEditorialNPCShadow` |
| 42 | `modFieldFolioInteractionsV2` |
| 43 | `modQuietEditorialSubtitleShadow` |

The older `modInkIronHUDBatchTest` **is not listed**. The intended v2, accepted bars and alias folders are enabled. In the exported order, v2 outranks the SAHUD and Outfit Wheel UI resources where they conflict. Therefore **do not prescribe a blanket Vortex sort/priorities change**: nothing in this list identifies a priority fault causing unchanged/missing modern controller glyphs. Earlier candidate 31 / wheel 36 numbers were merely a different profile snapshot; relative precedence is unchanged.

**Next diagnostic:** verify deployment and runtime selected resource hashes for representative **shared HUD root `hud.redswf`**, `panel_common.redswf` and `panel_overlay.redswf`, plus actual in-game HUD/dialogue glyph movie. Then trace whether the displayed controller icons consume patched `ICO_Xbox_*` character IDs/1008 image rectangles or a separate provider (e.g., actual selected input-device art). Differentiate old artwork still rendered, missing art, and art not updated only in menus outside v2's declared coverage. Only create a minimal visibly distinctive private probe if needed. Existing v2 geometry is accepted and must not be changed for this investigation.

## Next read-only local diagnostic before rewriting glyph art

1. Read the **actual current** installed `mods.settings` and Vortex clone deployment; enumerate every enabled same-resource bundle/loose movie owner for `hud.redswf`, `common/panel_common.redswf`, `overlay/panel_overlay.redswf`, `hud_controlsfeedback.redswf`, `hud_iteminfo.redswf`, `hud_dialog.redswf` and any shown button owner. Report exact priorities, selected resource SHA-256 and whether the current v2 22-key ZIP is installed/enabled as intended. Do **not** assume priorities from the old receipt.
2. If v2 wins the actual button-bearing movies, trace the *visible* glyph widget: its active input-device variant (Xbox vs PlayStation/keyboard), `ICO_Xbox_*` linkage, GFx frame/texture use and whether another separate font/library/atlas or a different menu movie paints the user's button. Distinguish **old appearance persists** from **icon absent** before concluding.
3. Prefer a **temporary private, single-surface, unmistakably distinct diagnostic glyph** with a known trigger only if resource-winner tracing cannot prove runtime use. Keep diagnostic art local and out of release; record in-game observed outcome. Avoid global blind priority shifts and mass replacements.
4. If a precise fault is established, repair the smallest necessary resource(s) and run official cook/validate/pack, contract, script and exact extraction gates. Retain Outfit Wheel's `OW*` exports, all button inputs and accepted HUD logic.
5. Independently prepare a richer-red candidate for the ordinary enemy bar and hostile names with unchanged geometry and full palette ownership verification; photograph/compare in the same lighting as v2 before accepting.

No private assets, generated ZIPs or modified third-party movies belong in public Git. Do not alter game, Vortex, settings, merges or saves automatically. The accepted v2 geometry and v1 fallback remain preserved.
