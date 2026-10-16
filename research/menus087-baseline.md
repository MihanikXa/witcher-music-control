# Ink & Iron 0.8.7 compatible menus — private baseline v1

16 October 2026. Implemented menu baseline, pending isolated in-game acceptance.
This replaces neither the accepted RC2 HUD package nor its gameplay resources.
Gear-grid v1 is preserved as an independent experiment; Inventory v2 is deferred.

## Evidence and migration decisions

Official user-supplied archive, pinned under ignored `reference/ink-and-iron-0.8.7/archives`:
`Ink and Iron - All in One 13111 0.8.7 2026-10-16T15-39Z lPL5EVl9W.zip`.
SHA-256 `1dbc4884fb61418af69066f972eafab61be373ed28ed1ef05c06bb091b73a56b`.
All **84 supplied extracted files** match their archive members. The package is
assembled from selected modules, not the All-in-One installer.

The [per-resource matrix](menus087-migration-matrix.csv) compares actual 0.8.0,
installed winners, 0.8.6 and 0.8.7 hashes. Important correction: **all 26 UI keys
in 0.8.7 equal 0.8.6 byte-for-byte**, as do all 15 Buttons keys. Thus the Inventory
source is exactly the version already examined for v1, but its rejected custom
layout is not transferred. The full UI was never established by that one movie.

Current actual mod owners at audit time: Gear-grid prototype owns Inventory at
11; Smooth Map owns World Map at 22; RC2 owns common/overlay and gameplay HUD
movies at 32; Adaptive Bars owns player bars at 30; aliases at 31 and QuietFolio
English at 40. These numbers describe the snapshot, not proposed new priorities.
No supplied menu key has a same-key DLC bundle owner. All deployed mod source,
bundle/cache/store and order inputs are hashed before/after. Full evidence stays
in ignored `reference/ink-and-iron-0.8.7/migration-evidence/` and `build/`.

| Feature / actual changed implementation | Decision |
|---|---|
| Shared MenuCommon background selection, Inventory/Equipment First art boxes and supplementary bands; pause OptionListModule art handling | Adopt 0.8.7, including its `inkart:` protocol and 24-entry UI texture cache. Preserve OW logic rather than retain the old plain common movie. |
| Inventory ContextInfoManager, SlotBase, TooltipInventory/TooltipStatRenderer, MenuInventory/ModulePaperdoll | Adopt upstream contextual card/comparison and browsing implementation. Preserve 0.8.5 hide-connector option and 0.8.6 Equipment First debounce. No v1 grid title, focus overrides, hidden gear slots, auxiliary cluster or fixed card dock. |
| Hoods compatibility | Transfer exact official 0.8.4 `SlotPaperdoll.canDrop` body plus `ItemDataStub.isDyeable`; retain installed Hoods scripts/DLC and all native slots/actions. No older whole-movie replacement. |
| Alchemy/crafting ItemCraftingModule | Adopt improved stat-value columns, wrapping and comparison alignment observed since 0.8.0. |
| Blacksmith ModuleBlacksmithGrid / SlotBase; TransmogMenu; item-selection popup | Adopt upstream rarity/slot changes and menu annotation feeds. |
| Map StaticMapPinData / StaticMapPinDescribed | Adopt optional quest-level data/labels. Default remains off; FriendlyHUD and native quest selection stay present. |
| World Map panning/zoom | Combine I&I rendering/hint copy with the **installed Smooth Map timer body**, mapped to upstream's existing timer fields. Retain installed show delay and texture fade constants. No second smoothing loop or duplicate fields/listeners. |
| Controller artwork and layout | Reapply accepted direct vector paths and bitmap fallbacks, 0.6875 icon scale, label metrics/gap, footer spacing, and RC1/RC2's 20% smaller A/B/X/Y interiors. Preserve upstream-only renderer helpers and older secondary-movie renderer APIs. |
| Quests, glossary/bestiary, character/skills, meditation, noticeboard, loot and remaining UI movies unchanged since 0.8.0 | Use upstream menu assets with the accepted controller treatment. Existing functional mod scripts remain. |
| RC2 panel_overlay | Retain byte-identical existing combined OW/glyph movie: upstream overlay itself has not changed since 0.8.0. No duplicate replacement. |
| QuietFolio / aliases | Retain installed English library and Vanilla-style Title/Body aliases pointing to the PF-family name supplied by QuietFolio. The upstream All-in-One instead maps Title/Body to IM Fell; that alternative is intentionally excluded. The English library path and alias keys remain compatible. Do not ship upstream font libraries or its two auxiliary font-module movies. Typography/wrapping still needs runtime checks. |
| Character-lighting environment | Defer this unchanged upstream optional override: the native cooker rewrites it and isolated validation reports one resource error. Keep the current game lighting. |
| Gear-grid v1 | Preserve source, ZIP and implementation history; disable it only in the new menu test profile. No retirement or overwrite of its archive. |
| Animated title scenes, loading art, icon pack, Gwent and dialogue modules | No blind update. Existing owners remain; unchanged optional animated title scenes are not a menu compatibility dependency. Accepted dialogue sizing/shadows and Gwent Deck Choice remain untouched. The Buttons loading movie only changes prompts, not the loading art module. |

### HUD / Buttons changes reviewed, not silently installed

All non-HUD Buttons keys are unchanged upstream from 0.8.0 through 0.8.7. They
receive our accepted artwork/layout; upstream `hud.redswf` is excluded entirely.

0.8.6 adds adrenaline arc/diamond handling to HudModuleWolfHead. 0.8.7 additionally
adds XP-bar and medallion styles (`iaiSetXpStyle`, `iaiSetMedStyle`, `iaiApplyMed`,
`iaiHeadDone`). These change the accepted Adaptive Bars rendering, not a demonstrated
missing functional contract: **defer**, no player-bar port included.

Journal updates gain vanilla/layout alternatives by 0.8.6 and `iaiSetQuestType`
in 0.8.7; QuestFinishedWindow adds layout positioning. **Defer cosmetic/options
ports** rather than introduce unsupported HUD settings into the menu release.
The radial movie adds `iaiFitIcon` after 0.8.0, already present by 0.8.6. It is
an icon-fit change, not evidence of a Tab/LB opening fix. **Retain working RC2**.
All remaining supplied upstream HUD movies equal 0.8.0. New HUD script/option
sections are not installed. No optional HUD port was justified for this baseline.

## Implementation and validation boundaries

One resource mod combines UI movies (except the unchanged retained overlay) and the
non-HUD Buttons movies. Only source-backed compatibility changes are applied:

- MenuCommon receives all 26 actual OW methods, its private state and required
  imports from the currently effective common movie. Upstream art is retained.
- Inventory receives only the author's Hoods rule/data field, controller artwork
  and renderer spacing. Its upstream composition and equipment behavior remain.
- HubMap receives the installed smoothing timer body with explicit field-name
  mapping; its rendering and map hint bridge remain upstream. The native common
  row is hidden via alpha on the map, keeping its input listeners active; the
  copied map row is display-only.
- InputFeedbackButton, HintButton where present and ModuleInputFeedback preserve
  original public/protected interfaces. The faulty `buttonsSize` footer injection
  is absent. Older secondary renderer variants receive bounded equivalent edits;
  no wholesale class replacement drops newer upstream helper functions.
- TopBarNew uses a small public-icon resolver instead of requiring `iaiPadIcon()`
  on the renderer. This is necessary because the shared ApplicationDomain can
  supply RC2's accepted HUD renderer, which does not define that upstream helper.
  The HUD and overlay do not define TopBarNew, so the adapted common-menu provider
  owns this header logic without replacing RC2's input renderer.

The common menu retains upstream's context-specific 0.8 hint-canvas scale; the
glyph paths, local scale, interior letter size and custom spacing remain ours.
Gameplay HUD glyph sizing is untouched. A legitimate declared `buttonsSize`
local exists in several upstream footers; it is not the RC1 unresolved lexical
reference. Tests check the declaration and absence of the faulty fit expression.

The original Hoods patch SHA is
`617f6d37d94158d751b3a3e6c3c0c5308e567f65ec74e007a967108d1a56802c`;
its movie SHA is
`90905cebbaac7b0a0f18671d32549e663b7aff67314334d9663e350c32e01a10`.
The 0.8.7 Inventory input SHA is
`10c63da7879ed48779c7e68c4cae8efaf17b71b83c2521f4fe1bc6825f3de9bd`.
Inputs are third-party author assets, locally adapted under the user's private-use
authorization; no assets or copied source bodies are published in Git.

**Environment exception:** the first 39-resource native batch reported one uber
resource error despite commandlet exit 0. The unmodified `.env` was the sole
cooked input whose bytes changed (41,014 to 40,963). A separate one-resource
upstream control also reports exactly one resource error. It is excluded rather
than treating exit 0 as successful resource validation. This establishes a native
validation limitation for that supplied asset, not proof of an in-game crash or
an identified bad environment property. Inventory camera hooks remain upstream;
the optional lighting resource does not ship. Full control logs/hashes are private
and its summary is in the release manifest.

The release manifest records exact output hashes, exports, atlas checks, native
commands, compiler control and diagnostics. Offline checks cannot prove game
initialization, focus, visible typography, OW operation, dyeing or map feel.
Seven opaque gameplay dependencies remain outside source recompilation, as in
the established verified compiler assembly. No Script Merger output is generated.
The target assembly omits Gear-grid v1's annotations, matching the required
disabled prototype in the new test profile; the current merged source is retained.

The settings supplement appends nine menu controls to the **actual current**
`modInkIronHUDBatch.xml`. Every existing HUD Var subtree is unchanged. It reuses
the installed page filename rather than adding another options page. This
is an intentional **physical file conflict**, unlike same-key movies in different
mod folders. The old page is retained by RC2 for rollback. Normal upstream
first-use default writes occur only when the user later runs the game; no settings
are edited during this build.

Reproduce locally with the existing private toolchain and pinned references:

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/audit-menu-migration.py
& $py tools/build-menus-087.py prepare
& $py tools/compile-menus-087.py
& $py tools/build-menus-087.py native
& $py tools/build-menus-087.py package
& $py -m unittest discover -s tests -p test_menus_087.py -v
& $py tools/report-menu-migration.py
```

Use fresh destinations for new releases. Prepare can resume exact verified movie
checkpoints; compilation can finish settings verification from exact previously
successful control/candidate sources with `--finish-existing`. Neither option
changes the live installation. Failed pre-release scratch files remain ignored.

## User installation and rollback

Private ZIP: `deploy/menus087-v1/Ink-Iron-0.8.7-Compatible-Menus-v1-private-test.zip`
(62,022,110 bytes), SHA-256:
`c7b5829f4cdae538a1b657424702e2e6c05d835aa9ae1ed2d255b32d22ec9ed0`.
[Release manifest](menus087-release-manifest.json) includes source/output hashes,
script deltas, native commands/log hashes and the isolated environment result.

**Final release checks passed:** 38 movies cooked byte-identically, native
validation reports zero resource errors, pack and metadatastore exit 0, exact
bundle re-extraction, deterministic ZIP generation/CRC and **15 targeted tests**.
All 13 menu annotation scripts compile against the verified current merged/modded
assembly with identical control diagnostics. The 24-entry texture cache has no
active mod cache collisions. No metadata reconstruction is used. Full native logs
and compiler output remain private. Baseline depot-directory/sound-bank assertions
are retained in the evidence, not omitted. Runtime acceptance is still pending.

1. Exit the game. Clone the working test profile, preserving its current package
   and file-conflict rules. Install the private Menus v1 ZIP. **Disable Gear-grid
   v1 in this clone**, keeping its package and source. Do not install All-in-One,
   upstream HUD, upstream Buttons root or IM Fell font replacements.
   Profiles redeploy into the same game directory; keep the original profile as
   the rollback reference. Do not stack a separate old/new modInkAndIronUI script
   package alongside this combined release.
2. Give `modInkIronMenus087` resource ownership **before Hoods, Smooth Map and RC2**.
   Preserve the relative order of all existing mods. These are intentional combined
   Inventory/Map/Common movies, not an assumption that load order merges binaries.
   RC2 must still own every gameplay HUD key and panel_overlay. Keep Hoods, OW,
   Smooth Map, SAHUD, FriendlyHUD, QuietFolio/aliases, NPC patches, compatibility,
   movement/combat and Gwent Deck Choice enabled. Over 9000 stays disabled.
3. For the one physical `bin/.../pc/modInkIronHUDBatch.xml` conflict, choose the
   **Menus package's additive file after RC2** in Vortex's file-conflict rules.
   This is separate from the resource ordering above. Reuse the existing Vortex
   menu-file workflow and verify Mods > Ink & Iron appears. The inspected 5.01
   install has no dx11/dx12 filelists: do not create legacy lists blindly, replace
   whole lists or register a second page. No merge regeneration/settings reset.
4. For upstream-default Inventory testing leave Equipment First off. Existing
   menu choices are honored; no Gear-grid preset is forced. Do not change campaign
   saves as part of UI testing.
5. Roll back: exit, disable only Menus v1, restore RC2 as the physical XML winner
   and redeploy the clone. Re-enable Gear-grid v1 only if returning to that saved
   experiment; otherwise Hoods resumes Inventory, Smooth Map resumes Map, and RC2
   resumes Common. No save or merge migration. Original private ZIPs remain intact.

### Short in-game acceptance checklist

- Startup: no script/UI error; mod options open, including >10 mod entries. Check
  old HUD options and nine new menu controls without changing unrelated settings.
- Open/close navigation and pause/settings, Inventory, Character/skills/mutations,
  Alchemy/crafting/runewright, quests, glossary/books/bestiary/tutorials, meditation,
  noticeboard and loot. Verify backgrounds/transitions, tab changes and back.
- Controller, keyboard and mouse: focus, hold/release, category changes, long
  labels, footer alignment at 1080p/4K and 21:9 where applicable. No missing glyphs.
- Inventory: native equip/unequip, compare, sockets, quickslots/consumables, Roach,
  weight, Hoods toggles and dyeing on Quickslot2. D-pad one step per tap in both
  upstream normal mode and optional Equipment First if tested. Shop/Stash return
  paths and selected/mouse tooltips must work.
- Map: smooth mouse/pad/keyboard pan/zoom; pins, quest/filter navigation, hints,
  long-press user pins, fast travel and return. Try optional quest levels off/on.
- Outfit Wheel: open/use/close in gameplay and relevant menus; restore focus and
  backgrounds, save/wear sets. Hoods and movement/combat still behave normally.
- Confirm Gentium, punctuation/accents, dialogue sizing and text shadows. Check
  accepted player/enemy/boss bars/colors, quickslots, adaptive visibility and
  **Tab and LB radial opening**, sign selection/close. These are regression checks,
  not claimed runtime passes from cooking.

No Inventory v2 layout, translucency experiment, shop redesign or HUD update is
included. Any runtime fault should be reported with menu, input device and exact
action; disable this one package to isolate it without discarding accepted RC2.
