# Ink & Iron 0.8.7 menu visual completion v2

17 October 2026. Private candidate, **not yet visually accepted in-game**.
Replaces Menus v1; the accepted HUD RC2 package is unchanged. No live deployment,
settings, saves or merged scripts were modified. Inventory v2 remains deferred.

## Findings from the actual installation

The installed v1 bundle, metadata, texture cache, 13 scripts and additive options
XML **all match their released hashes**. This is not a damaged installation.
Read-only effective-owner evidence is in ignored `build/menus087-v2/ownership.json`.

| Visible discrepancy | Demonstrated cause and correction |
|---|---|
| Broad gold tabs, large XP area | `modInkIronHUDRefinementV4` **31** wins Common over `modInkIronMenus087` **32**. Effective Common SHA `d5e83c6ffa1fb1361119bf1ad60c5dc967648af3189ca5410439b12bbcfae065` contains the older TopBarNew implementation. Select the combined Common already built from upstream, with OW preserved; do not replace the HUD root. |
| Missing Quest/Alchemy/Character engravings | Same effective Common's `updateMenuBackgroundImage` only sets `imgloader.source = path`; it has no `inkart:` dispatch. UI scripts send `inkart:quests`, `inkart:alchemy`, etc., requiring the combined Common's `inkArtSet`/Loader implementation. All 24 original cache keys are deployed correctly, including these engravings. This establishes a missing handler in the winner, not a demonstrated broken cache. |
| Native Inventory arrangement | `modHoods` **11** wins Inventory over Menus **32**. Effective SHA `2a2dacc886c86d4b08fced4cdc68c7882f2017d2f9d850b41b9ef98df060c68e`. Select the combined I&I Inventory, which already contains the exact official Hoods drop/dye rule and `isDyeable` contract. Keep Hoods scripts/DLC enabled. |
| Old map appearance/control movie | Smooth Map **20** wins World Map over Menus **32**. The combined I&I/Smooth Map movie is present but shadowed. Select it, retaining the actual installed smoothing algorithm. |
| Realistic Bestiary creatures | Separate author Bestiary Art was absent. Now included unchanged, with the one Brothers in Arms correction deliberately retained as winner. |
| Missing anatomical Character reference | Upstream requires **Character screen layout: Vanilla Ironed (1)**. DX12 settings currently contain only `iiLootShowCard=true` in `InkAndIronOptions`; no saved Character override. Author default is 0, not the illustrated alternate. Select the alternate manually for screenshot comparison. |
| Incomplete auxiliary menu styling | V1 omitted the author Fonts module's **Character Perks** and **Meditation** movies. Both are now included unchanged without its IM Fell library/XML. Their paths are menu resources, not font libraries. |

The first four findings are **current installed resource ownership plus actual
source evidence**, not speculative priority changes. An ActionScript exception
has **not** been demonstrated in the new combined Common; do not attribute the
observed legacy header to one. No extra runtime diagnostic is warranted before
testing the correct winner. Visible image loading and new shared-domain behavior
still require the game test below.

## Implementation / typography

40 movies: **37 v1 movies byte-identical**, combined Common recompiled, two missing
author menu movies added. Common retains all original upstream art/layout and
26 OW methods, exports and listeners. TopBarNew uses existing public controller
clips rather than depending on RC2's missing `iaiPadIcon` method.

Only new source edit: `TopBarNew.inkTf` changes
`baseline - size * 0.93 - 2` to
`baseline - tf.getLineMetrics(0).ascent - 2` **after setting the text**. This anchors
the chosen font's real baseline instead of assuming IM Fell's ascent. The author
already fits the navigation row by measured `textWidth` at 17 down to 12 points,
with its own restrained colors, letter spacing, small icons and medallion.
Keep this authored hierarchy; do not impose RC2's old menu typography. Font
definition/import tags and Gentium/aliases are unchanged. Other menu movies keep
authored typography; no unsupported global size multiplier is applied. This is
a concrete metric correction, **not proof that every Gentium field fits**.

The full original 24-entry menu cache remains exact. The source-to-cache checks
cover every returned nonempty background key in `inkironui_bgart.ws` and its
menu-selection callback. Character alternate selection remains an author option.
No screenshot-derived decorative replacements or equipment orbit reconstruction.

### Original optional artwork

User-supplied archives are present directly under ignored `reference/`:

| Archive label | SHA-256 | Contents |
|---|---|---|
| Bestiary Art **0.8.0** | `69f341dce481f934dcfedb40212d3251cfc941d473569032884d685adc56596c` | Original metadata.store + 706-entry texture.cache, `modInkAndIronGlossary` |
| Map Inked **0.7.4** | `c457cd88c8f567794ce383340f65323f4c0ce5e2a4538f42cc9b926ef13736a1` | Original metadata.store + 2,406-entry texture.cache, `modInkAndIronMap_Inked` |

These are **archive-labelled versions**, not claimed new 0.8.7 art releases.
Both contain no scripts/UI movies. They use the author's original resource keys
and metadata byte-for-byte; no recooking or reconstructed metadata is claimed
for these already cooked author caches. Bestiary's only active mod-cache overlap
is `gameplay/gui_new/icons/monsters/bestiary_doppler.png` with Brothers in Arms:
keep **Brothers in Arms before Bestiary Art**, accepting that one corrected image
instead of the author's engraving. Map has no active mod-cache overlaps.

Map Inked also supplies **minimap tiles**. It changes map artwork, not HUD movie
geometry, behavior or glyphs. Its separate folder can be disabled independently
if that artwork is unwanted. Smooth Map operates in the combined UI movie, not
these tile textures. Bestiary/Map runtime image display is not offline-certified.

## Build and validation

Private release:
`C:\Dev\witcher-ui-overhaul\deploy\menus087-v2\Ink-Iron-0.8.7-Compatible-Menus-v2-private-test.zip`

SHA-256: `fbd89f94bebabf2fdef9764d17d9e13048bd721a8849f880f316a10feb835bb8`.
Exact inputs, output keys/hashes, native commands/log hashes and compiler receipts:
[release manifest](menus087-visual-completion-v2-manifest.json).

All four official native stages completed with exit 0; resource validation reports
**Errors found in 0 resources**. All 40 cooked movies are input-byte-identical and
all 40 packed entries re-extract exactly. No native metadata fallback. Known
depot-directory and sound-bank startup assertions are retained in the logs and
manifest, as in the successful control pipeline. Both author art caches retain
their original metadata; these were checked/extracted, not recooked.

**25 targeted tests pass** (15 retained migration tests plus 10 visual/ownership
tests). The historical v1 freeze test now verifies its recorded build snapshot,
rather than failing merely because the user subsequently installed v1. The v2
suite separately verifies today's live files remain unchanged. The read-only
install gate was exercised against the current deployment and correctly fails
on the old Common/Inventory/Map winners and two absent auxiliary movies.

Original tools: `complete-menus-087.py`, `verify-menu-visual-install.py` and
`test_menus_087_visual.py`. Reuses the existing FFDec/REDkit and pinned inputs.
All generated/private source, binaries, logs and ZIPs remain ignored.

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/complete-menus-087.py prepare
& $py tools/complete-menus-087.py native
& $py tools/complete-menus-087.py package
& $py -m unittest discover -s tests -p test_menus_087_visual.py -v
```

Use fresh build/deploy destinations when changing source. Preparation resumes
only verified checkpoints. Native stages are bounded; native output logs and
the exact release/hash receipt are recorded separately in the release manifest.
Unchanged scripts reuse exact successful control/candidate compiler blobs and
diagnostic receipts; this pass does **not** claim a fresh script compilation.
No changes to WS inputs or merged source are required.

## Install: two different ordering systems

1. Fully exit game. Use the test profile; retain prior ZIPs and rule snapshot.
   Disable **Menus v1** and install **Menus v2** as its replacement. Do not stack
   them. Keep RC2, aliases, Gentium, Hoods, OW, Smooth Map, compatibility and all
   accepted gameplay packages. Gear-grid stays disabled.
2. In Witcher **resource load order**, move **modInkIronMenus087 before Hoods**
   (currently 11), hence also before Smooth Map (20) and RC2 (31). Lower numerical
   priority wins these resources. Keep other mods' relative order. Do not merely
   put it immediately after RC2 again. This deliberately selects combined
   Inventory/Common/Map movies; it does not merge binaries by priority.
3. Enable `modInkAndIronGlossary` and `modInkAndIronMap_Inked` from the same ZIP.
   Keep **Brothers in Arms before modInkAndIronGlossary** for its Doppler fix.
   Map artwork has no detected mod-cache collision. No upstream All-in-One,
   Fonts, HUD, Buttons root or obsolete Hoods movie is needed.
4. The physical XML file conflict is different: **Menus v2 AFTER RC2** for
   `bin/config/r4game/user_config_matrix/pc/modInkIronHUDBatch.xml`. Its additive
   options file is byte-identical to v1 and retains all accepted HUD controls.
5. After user-driven deploy, before launching, run:
   `& $py tools/verify-menu-visual-install.py`.
   It must PASS all 40 effective movie hashes and deployed files, enabled art
   folders and BIA precedence. A FAIL identifies the actual winning mod. This
   read-only gate makes no live changes and is not a visual runtime certificate.
6. Restart game; verify existing Mods > Ink & Iron options. For the anatomical
   reference set **Character screen layout: Vanilla Ironed** and reopen Character.
   Do not reset other settings. Leave Equipment First off for default comparisons.

### Short visual and functional acceptance

Compare the same menu/save at 1080p and 4K if available. Capture the header and
full composition, not just a crop of an icon:

- All major menus: slim shared text navigation, small symbols, left medallion,
  compact status; old individually highlighted gold tabs must be gone. Mouse,
  keyboard and pad tab changes, selection and long English names must fit.
- Quests: compass engraving; Alchemy/crafting: bottles/tools; Character alternate:
  anatomy. These must be visible, faint and compositionally aligned—not black.
- Glossary/Bestiary: engraved creature/character art, working entries/navigation;
  Doppler is the intentional BIA exception. Books/tutorial backgrounds and text fit.
- Inventory: authored ornamentation/context cards, equip/compare/unequip, Hoods
  dye and controls, quickslots, Roach and weight. No rejected Gear-grid presentation.
- Meditation/perks, settings/pause and secondary popups: authored typography,
  Gentium punctuation, no clipping. Check footer hints with long labels and holds.
- Map: Inked tiles, Smooth Map pan/zoom/filter/pin/fast travel and readable hints;
  minimap tiles load. Test OW transitions/sets. No input or data regressions.
- Accepted HUD remains: Tab **and LB** wheel open/select Axii/close repeatedly,
  bars/colors, quickslots, glyph letters, NPC labels/shadows, SAHUD/FHUD behavior.

Stop visual acceptance if the shared header/art are still missing despite an
install-gate PASS; then one focused runtime shared-common trace is justified.
Do not progress to Inventory v2 on compilation success alone.

### Rollback

Exit, disable v2 (all three supplied folders), re-enable the preserved v1 ZIP
and restore its prior resource ordering if reproducing the original screenshot
state. Restore the captured XML conflict rule. For the pre-menu accepted HUD,
disable the menu packages and optional art; RC2 owns Common, Hoods Inventory,
Smooth Map World Map and RC2 owns the options XML again. No saves or merges need
migration. Each art module can be disabled separately; all v1/RC2 archives remain.
