# Menus v3 — Gentium typography and original item artwork

17 October 2026. Private in-game candidate. The user reports v2's shared menu
composition/header/engravings now substantially correct. This pass retains them.
No HDR, global brightness, backdrop, Inventory layout or gameplay HUD edits.

## Source evidence and implemented roles

The read-only v2 installation verifier passed **all 40 effective movie hashes**,
deployed files and art-folder checks before this build. This is no longer v1's
shadowed Common problem. Private receipt: `build/menus087-v3/installed-v2-check.json`.

Upstream's English `$TitleFont` alias points to **IM Fell English SC**;
`$BodyFont` points to **IM Fell English**. Our accepted aliases use the same
QuietFolio/Gentium runtime family for both. V2 retained authored layouts but did
not reproduce the small-cap glyph distinction. Alchemy additionally creates its
recipe names in `$BoldFont` 17, with the availability line in `$NormalFont` 17.
These source-observed roles explain why changing a font family alone fell short.

Gentium Book 7.000 has `smcp`/`c2sc` OpenType features. However, our accepted
383-codepoint-per-style SWF library does not carry the source TTF's OpenType
substitution engine/tables or a separately addressable small-cap face. Merely
setting the alias to a nonexistent Gentium SC family is not a working solution.
This candidate **does not rebuild the global library or add a runtime font**.

The implemented alternative uses existing vector Gentium capital glyphs, with
**80% size only for originally lowercase characters**, retaining larger initials,
capitals and accents. It uses per-character TextFormat ranges and preserves the
original display source in a weak TextField dictionary. Repeated refreshes reuse
that source, avoiding conversion into uniformly large capitals or cumulative
scaling. Game item/localization/search/sort data and underlying names are untouched.

| Role | Candidate / deliberate retained behavior |
|---|---|
| Main navigation | V2 Common/TopBarNew **byte-identical**: authored slim arrangement, measured Gentium baseline and width fitting, selected-tab emphasis. No redesign. |
| Secondary/section headings | Existing Quest/Glossary `FeedbackDropdownMenuListItem.inkPaintHeader`: measured mixed-size caps at authored 25 pt. Alchemy group headings at 21 pt. |
| Selected/unselected recipe entries | Alchemy/crafting name fields switch heavy Bold 17 to Regular 18, small lowercase capitals 14.4, tracking 0.65. Existing selected `#E2C47F` / unselected `#A4997F` state hierarchy and focus remain. |
| Item/recipe titles | Alchemy card title fields, Inventory visible/docked item headings and Character information headings receive the menu-local treatment. Quest/Glossary TextArea title remains 30 pt with small lowercase caps 24. |
| Secondary category labels | Title-role fields use the same capitalization hierarchy instead of changing every string. Named prose/value/count/input fields are excluded from the tree pass. |
| Ingredient availability | List status 16 pt / small lowercase caps 12.8. Missing/insufficient state `#D9483B` → `#928B7E`; disabled code 4 `#877F71` → `#77766F`. Aggregate missing count also becomes `#928B7E`. Ready/selected state stays authored. |
| Descriptions/narrative prose | Natural case, original Body/Normal font roles, wrapping, paragraph structure and alignment retained. No blanket uppercase or global multiplier. |
| Numerical values/comparisons | Named value/count fields excluded; positive/negative comparison colors and individual missing ingredient-count warnings remain semantic. No gameplay values change. |
| Footer/controller hints | Accepted v2 renderer/layout remains exact; no attempt to restyle the shared HUD renderer through a menu copy. Glyphs, labels, spacing and hold/input behavior are preserved. |

The muted missing-ingredient label is an **intentional private departure from
0.8.7's red treatment**, not a claim that the upstream red state was a bug. The
older reference and the user's explicit restrained-status preference justify it.
Individual ingredient deficiencies still retain their warning colors.

### Implementation boundaries

**Eight movies / twelve classes** change:

- Alchemy and Crafting: `ItemCraftingModule`.
- Inventory: `MenuInventory` (including the currently docked tooltip subtree).
- Character Dupe: `MenuCharacterDupe` information/init paths.
- Quest journal, Glossary Books, Bestiary and Encyclopedia: `TextAreaModule` and
  `FeedbackDropdownMenuListItem` in each owning movie.

Formatting hooks use existing rendering/update callbacks. No added listeners,
input handlers, data mutations, public exports or native signature changes.
Only DoABC changes: every shape, font definition/import, texture, SymbolClass,
sprite, placement and other non-code SWF tag remains byte-identical. **32 other
movies**, including Common, World Map and the remaining shared menus, stay exact.
All 13 menu scripts, XML options, existing menu cache and optional art stay exact.

The helper measures `textWidth` for nonwrapping bounded headings, fitting down
only within a bounded 82–100% range. Wrapping and authored field/column/hit-area
geometry remain. The weak cache detects upstream uniform-format repainting, so
it can reapply per-character sizes without adding event listeners. The selected
color is captured before changing the display text, avoiding a default-format
color reset. No new helper is called on the accepted HUD renderer/provider.

**Offline font evidence:** private regular-face previews and widths cover recipe,
status, category, long item and accented-name strings using the preserved
QuietFolio source. The sample widths fit the modeled 480 px allowance. This is
not a GFx proof of all real field bounds, line breaks, English strings or 4K
scaling. Check long/multiline text in-game. Shared ApplicationDomain class
resolution and final runtime paint order likewise require the menu checks below.

## Icon provenance and collision resolution

Exact module `mods/modInkAndIronIcons/content/{texture.cache,metadata.store}`
is verified against pinned All-in-One 0.8.7 archive SHA
`1dbc4884fb61418af69066f972eafab61be373ed28ed1ef05c06bb091b73a56b`.
Original cache: **2,433 entries**. Not all are item icons: it also includes buffs,
HUD quest symbols, radial artwork and skills. Installing it wholesale would
expand into accepted HUD artwork, so this release uses a targeted item module.

`modInkIronMenuItemArt` exposes **2,079 inventory-item texture keys**, with all
original compressed blocks/pixels, dimensions and resource hashes retained.
The cache **index is reconstructed** by retaining original tables' selected
52-byte entries and footer count, with compressed pages and strings unchanged.
Only the observed HCXT v6, reserved-zero, no-mip-table layout is accepted.
Roundtrip lookup, offsets, every zlib stream/length and pixel sizes are tested:
2,075 selected images have BC3-sized payloads; four original 83×83 bomb images
use 27,556-byte RGBA payloads. Both original encodings are retained.
No recompression, recoloring, generated artwork or renamed texture paths.
Author's original empty metadata.store remains byte-identical; this does not
pretend that the filtered cache index was generated by a native commandlet.

Nine Brothers in Arms fixes are **absent from the new index** (seven boot keys,
one painting and one bear silver sword). Therefore those existing owners keep
their fixes regardless of new icon-module priority. Active mod caches and both
deployed DLC caches were checked. No additional item-cache collisions were found.
The full retained/excluded key/hash ledger is provided alongside the manifest.

All seven decoded source comparisons—normal red/green/blue mutagens, Alcohest,
sample weapon, armor and consumable—have different decoded payload hashes from
their located installed base-cache candidates. Private visual contact sheet:
`build/menus087-v3/icon-comparison.png`. These actual texture differences establish
the omitted Icon Pack contribution independently of screenshot HDR saturation.
No global saturation/contrast change is applied. Shared item textures can also
appear in existing quickslot/item views; their artwork changes, not HUD controls,
glyphs, bars, nameplates, typography, scripts or radial graphics.

## Reproduce, install and roll back

Private ZIP (579,604,415 bytes):
`C:\Dev\witcher-ui-overhaul\deploy\menus087-v3\Ink-Iron-0.8.7-Menus-v3-Typography-Icons-private-test.zip`

SHA-256: `919c635d37941db936ea9583a7d554baea0755daf594e07f3832228b06157965`.

**Validation:** 13 targeted tests pass. All four official native movie stages
completed with exit 0; validation reports **Errors found in 0 resources**. All
40 cooked movies are input-byte-identical and all packed entries re-extract
exactly. Every ZIP member hash and CRC is checked, ZIP generation is deterministic,
and the live snapshot is unchanged. Existing depot-directory/sound-bank startup
assertions remain recorded, as in the verified control pipeline. No native
metadata reconstruction. The separate filtered texture-cache index is explicitly
custom-built and independently checked; it is not a native cooker output.

[Release manifest](menus087-v3-typography-icons-manifest.json) records movie/class
hashes, native commands/log hashes, tested font metrics/coverage, exact item-art
provenance, initial installed v2 owners and test results. The [texture ledger](menus087-v3-item-textures.csv)
lists every upstream key, its inclusion/exclusion decision and original compressed
block hash. Original v2/RC2 archives remain unchanged. Final visual acceptance and
runtime class-provider behavior are still pending the user's game test.

Original scripts: `refine-menu-typography.py`, `build-menu-typography.py`,
`preview-menu-refinement.py`; targeted suite `test_menu_typography.py`.
All vendor code/assets, private derivatives and previews remain ignored.

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/build-menu-typography.py prepare
& build/font-preparation-venv/Scripts/python.exe tools/preview-menu-refinement.py
& $py tools/build-menu-typography.py native
& $py tools/build-menu-typography.py package
& $py -m unittest discover -s tests -p test_menu_typography.py -v
```

To regenerate the public manifest/ledger after capturing the successful test
output in ignored `build/menus087-v3/tests.log`, run
`& $py tools/build-menu-typography.py report`.

Fresh native/deploy directories are required; source-matched compile checkpoints
can resume preparation. The private receipts distinguish native movie stages
from the custom item-cache index. No new WitcherScript compilation is necessary:
all script bytes are unchanged from v2's verified source assembly/compile inputs.

1. Exit game; preserve the v2 archive/profile/rules. Disable **Menus v2**, install
   v3 as its replacement. Do not stack them. The same menu/art folders are kept,
   plus new `modInkIronMenuItemArt`. Leave Hoods, OW, Smooth Map, aliases/Gentium,
   SAHUD/FHUD, accepted HUD RC2 and all working compatibility/gameplay mods active.
2. Retain the **working v2 resource ordering**: Menus wins Common/Inventory/Map
   before Hoods, Smooth Map and RC2. Keep Brothers in Arms before Bestiary Art.
   The new item module has no remaining active mod/DLC cache collisions; no
   speculative changes to existing relative order are needed.
3. Keep the **Menus-after-RC2 physical XML rule**. The options file is unchanged.
   Enable the new item-art folder; do not also install upstream whole Icons/HUD
   or Fonts packages. No settings reset or Script Merger regeneration.
4. Read-only post-deploy check:
   `& $py tools/verify-menu-visual-install.py --release build/menus087-v3/receipt.json --report build/menus087-v3/installed-check.json`
   Require PASS before testing. It checks v3 effective movie hashes, release files
   and enabled folders. It is not a visual runtime test.
5. Full rollback: exit, disable v3/new item-art folder, restore preserved v2 and
   its rules/order. The accepted HUD package never changes. For typography-only
   isolation, keep the new item-art module disabled; for a clean v2 baseline,
   restore the entire v2 package. No save, font-library or merge migration.

## In-game comparison checklist (not yet passed)

Use the same item/save/recipe and display settings. Do not compare Blue Mutagen
with Greater Blue Mutagen when judging recipe contents or numerical differences.

- **Alchemy:** mixed-size small caps on recipe names, muted missing-status labels,
  selected/unselected hierarchy, correct three mutagen artworks. Check changing
  selection, crafting, filters, scrolling, long labels and multiline descriptions.
  Individual missing ingredient counts must remain distinguishable. Footer/hold
  prompts keep accepted size and spacing; no missing actions.
- **Quest/Glossary:** heading/section caps, selected-entry distinction, natural
  narrative paragraphs, accents and long titles. Test Quest-first and Glossary-
  first opening after separate fresh game launches to catch provider-order issues.
- **Inventory:** item and docked tooltip titles, stats/comparison signs/colors,
  item images and long labels. Equip/unequip, Hoods dye, quickslots and Roach
  actions; layout, selection and hit areas must be unchanged.
- **Character:** category/skill information title hierarchy, readable body/state
  colors, normal focus and navigation. No category/layout rearrangement.
- **Shared:** slim header, medallion, background art, long tab labels and footer
  alignment unchanged at 1080p/4K. Map/BIA/Bestiary appearance remains as v2.
- Brief unchanged-HUD check: Tab/LB wheel opens/selects/closes, RC2 bars/colors,
  quickslots, SAHUD/FHUD and OW. No new HUD asset or script is supplied.

If a specific heading remains ordinary mixed case, report the menu, field and
opening order; do not infer every menu failed or restack upstream whole packages.
Native validation does not establish rendered typography or final class ownership.
