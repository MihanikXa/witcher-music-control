# Menus v4 — Typography Finishing

17 October 2026. Private candidate; runtime visual acceptance remains pending.
Based on the actual installed v3: all 40 effective resource hashes and release
files passed the read-only deployment check. No live game/Vortex/settings/save
or merge writes. The accepted HUD RC2 and previous archives remain untouched.

**Native-validation limitation:** the final candidate's WCC cook command stalled
before producing any log, twice, at the 90-second bound. Final native cook,
resource validation, packing and metadata generation therefore did **not pass**.
The private ZIP uses independently verified same-key bundle/metadata
reconstruction, not a claimed successful native run. It remains a runtime test
candidate with native validation outstanding; the recovery command below can
verify it when WCC startup works again.

## Actual row discrepancy and bounded correction

The original compiled recipe renderer sets `textField.y = 9` when it has a
secondary line. The movie's `tfSecondLine` placement is Y **849 twips = 42.45**;
both fields start at X **86**. V3 `inkOwnTF` copied these two origins independently
and merely resized/reformatted the visible clones. Therefore v3 retained a
**33.45 logical-pixel field-origin separation**. The compiled `qfCaps` did not
move either field: there is no evidence it changed their Y coordinates.
Its smaller glyphs did leave that old separation optically conspicuous.

V4 formats the two fields first, then reads their **actual line ascent/height**.
It reconstructs a compact group with **4 px optical interline clearance**, using
Gentium's measured H-cap-height/ascender ratio **1260/1940**. It retains the old
group's optical center, rather than moving the whole list or only guessing a
negative status offset. Each refresh derives positions from the untouched source
fields, not the previous visible clone positions. Multiple title lines add their
actual line heights. Ready-state lozenge and existing level tag follow their text
anchors; native level-tag fitting/data logic is unchanged.

Actual installed-font single-line model (logical coordinates):

| Field | V3 | V4 model |
|---|---:|---:|
| Name Y | 9.00 | 17.06 |
| Availability Y | 42.45 | 34.39 |
| Field-origin separation | 33.45 | 17.33 |

These are **modeled text metrics**, not pixel measurements of the user's game.
The private 2048×1152 preview shows both groups with the same 80-pixel row bounds;
it is labelled as a model. Source-native positions and actual font advances are
verified; exact reference screenshot parity still requires the game.

This applies only to `well` recipe rows (`RecipeIconListItem`, **80 px**) in
Alchemy/Crafting's shared mechanism. Inventory/enchantment-style 86/96-pixel
rows do not acquire this anchor. Selection geometry, icon transforms, hit areas,
row spacing, X positions, scrolling and controller callbacks remain original.

## Role-specific Gentium finishing

No new font face/library is installed. Gentium's TTF has `smcp`/`c2sc`, but the
accepted SWF registrations do not expose that substitution system as a separate
small-cap face. Adding a global registration is unnecessary for this bounded
finishing pass. Existing vector Regular/Bold glyphs are used with role-specific
capital proportions instead of one universal 80% rule:

| Role | V4 treatment |
|---|---|
| Recipe names | 19.5 Regular, lowercase-derived capitals 90%, tracking 0.85 |
| Availability status | 15.5 Regular, 86%, tracking 0.5 |
| Alchemy section headings | 21.5 Regular, 90%, tracking 1.1 |
| Major central item heading | 32 Bold, 92%, tracking 1.6 |
| Quest/Glossary title | 31 Bold, 92%, tracking 1.25 |
| Quest/Glossary section labels | 25 Regular, 90%, tracking 1.1 |
| Other existing menu-local caps | 88%, tracking 0.9, preserving their role size |
| Menu footer labels/hold prefix | 17 Regular, 88%, tracking 0.55 |

Explicit role parameters survive the later generic title pass through the weak
TextField record; it cannot silently reset the central title back to its default
size/weight. Source case is retained in that record. No localization, item data,
search/sort labels, gameplay values or native action strings are rewritten.

Long one-line major titles fit within the original bounds down to 18 at a 32
base. Below that, the text field alone can wrap within its **existing height**;
if necessary it receives a display-only ellipsis. Original wrap flags/source
text are restored on the next refresh/selection. Tracking scales with the fitted
glyphs. No text-field/panel enlargement. The long-title model verifies two lines
within the original 48-pixel title height at the narrow 320-pixel allowance.

### Secondary colors

The central ingredient **name** and **required count** now use missing-state
`#928B7E`, matching the already muted list status. Available names stay
`#A4997F`; available counts/selected names retain authored `#E2C47F`. Disabled
status remains `#77766F`. Actual level warnings, positive/negative stat comparisons,
icon colors, selection shapes and every gameplay HUD palette remain unchanged.
This is a targeted recipe status preference, not global removal of warnings.

### Short item prose

The **actual installed** QuietFolio English resource is SHA
`9bc41144a3fcfc32377b41bebf9698ac8c80ebaee0f621fc64f22a8ed16a0e9e`.
The native Alchemy description field is **475.45 px**, about **471.45 usable**.
Its accepted SWF advances measure the quoted mutagen sentence at **500.47 px**
at 19. Thus wrapping is expected; it is not evidence the whole column is wrong.

V4 probes the real runtime font for single-paragraph item descriptions of at most
100 characters, testing 19 down to **17.5**, in 0.25 steps. The offline installed-
font model fits the sentence at **17.75 / 467.54 px**. It does not force all prose
onto one line or shrink long narrative passages. Natural case, inline semantic
colors, paragraph content and column width remain; short-item fitting runs before
Alchemy's existing card height/layout measurement. The equivalent menu-local
item-description field is also eligible in Inventory/Character information trees.
Quest/Bestiary narrative bodies are not selected by that item-field rule.

### Footer ownership and preservation

Only `MenuCommon`'s **own `mcInpuFeedback` subtree** is styled, from its existing
`inkArtFrame` callback. No new listeners, shared renderer overrides, input or
initialization adapters. The hint letters are smaller/literary and muted; gold
emphasis and red warning labels are preserved. Label vertical centers are cached
against the current native renderer position, preventing drift. Visible hold
prefixes share the new baseline and a measured 4-pixel text gap. Button containers,
glyphs, command widths, hit areas and input listeners are not resized/replaced.

The original `TopBarNew`, `InputFeedbackButton` and `ModuleInputFeedback` classes
in Common were independently decompiled again and remain **source-identical**.
OW methods and Common initialization/art-dispatch contracts are retained. The
HUD's renderer/package is never edited. Input-device changes and late rendering
order still need the game checks below.

## Build and isolation

Private candidate ZIP, **579,612,087 bytes**:
`C:\Dev\witcher-ui-overhaul\deploy\menus087-v4\Ink-Iron-0.8.7-Menus-v4-Typography-Finishing-private-test.zip`

SHA-256: `4566e39878e234f3f4d96bece03804a625f0338f8d2cb7680c9627b044bf44d0`.

**13 targeted offline tests pass**: compiled role/row/prose/footer contracts,
retained native interfaces/listeners, original common renderer/header classes,
unchanged non-code tags/art/scripts/options, actual font fitting, native-control
reconstruction checks, exact extraction, ZIP CRC/member hashes and the live-file
freeze. This is **not** a native resource validation pass or runtime acceptance.
[Exact release manifest](menus087-v4-typography-finishing-manifest.json).

**9 movies / 13 classes** change: v3's eight typography movies/classes plus
`MenuCommon` for footer paint. Every non-DoABC SWF tag remains exact, including
font definitions/imports, symbols, shapes, sprites, placements and glyph artwork.
**31 movies remain byte-identical**. All existing scripts/options, the complete
v3 item-art cache, Bestiary Art, Map Inked and menu-art cache remain exact.
Main navigation geometry and drawing code, Smooth Map and Hoods/OW behavior are
preserved. No Inventory v2, HDR or backdrop work.

Private source, compiled resources and full logs live under ignored
`build/menus087-v4-final/`. Earlier `build/menus087-v4/` is superseded fitting-study
output, **not a release input**. An early model caught a narrow long-title clip;
the final source adds bounded wrap/ellipsis. That superseded native metadata
attempt also timed out and is not represented as successful final validation.

Reproduce with the pinned private toolchain/assets (fresh native/deploy paths):

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/build-menu-finishing.py prepare
& build/font-preparation-venv/Scripts/python.exe tools/preview-menu-finishing.py
& $py tools/build-menu-finishing.py native
& $py tools/build-menu-finishing.py package
& $py -m unittest discover -s tests -p test_menu_finishing.py -v
```

For this release, after the two recorded blank-log cook timeouts, the bounded
fallback was `& $py tools/reconstruct-menu-finishing.py`, then `package`. It accepts
only the same 40 keys/self-contained resources and must reproduce both native
v2/v3 control bundles **and** their metadata byte-for-byte, including an independent
v2 → v3 changed-content reconstruction. All candidate resources are re-extracted
exactly. It refuses native resource-error diagnostics, unknown tables, new keys,
imports/buffers, missing controls or nonzero logs; it does not bypass an observed
candidate resource validation error. No further unchanged native retries were run.

When the external startup problem is resolved, the isolated follow-up command is
`& $py tools/build-menu-finishing.py verify-native`. It uses a fresh ignored
`native-verification` directory and compares native bundle/metadata bytes with
this release, without deploying anything. Its success has **not** been claimed.

The release manifest records all changed classes/input-output hashes, native
commands/log hashes, font/width/row evidence, archive and targeted test results.
There is no new WitcherScript source: v3's verified compiled inputs are carried
byte-for-byte; no merge or campaign-save migration is required.

## User installation and rollback

Exit game. In the test profile disable **Menus v3**, install v4 as its replacement,
and retain the **working v3 resource order and XML conflict rule**. Keep the four
existing folders enabled: Menus, Item Art, Bestiary Art and Map Inked. Do not stack
v3/v4 or install upstream whole Fonts/HUD packages. Keep RC2, aliases/Gentium,
Hoods, OW, Smooth Map, SAHUD/FHUD and compatibility/gameplay mods unchanged.

Read-only check after the user-driven deployment:

```powershell
& $py tools/verify-menu-visual-install.py --release build/menus087-v4-final/receipt.json --report build/menus087-v4-final/installed-check.json
```

Require PASS before comparing typography. No settings reset or automatic deploy.
Rollback: exit, disable v4 and restore the preserved **Menus v3 ZIP** and its
unchanged rules/order. All four art modules/options match v3; RC2 is untouched.

## Focused in-game acceptance (pending)

Use **Greater Blue Mutagen**, equivalent display settings and a 2048×1152 capture:

- **Alchemy:** compact two-line selected/unselected label groups, status clear of
  lower border, same icon/border/list placement. Scroll repeatedly; short/long
  names and ready/missing/disabled states must not drift or collide with level tags.
- Central title: fuller/wider capitals without clipping. Test a very long title,
  then a short one; wrap/ellipsis must clear normally. Ingredient name/count grey,
  selected/available gold retained, stat comparison warnings unchanged.
- Mutagen sentence should fit on one line where the actual font probe allows it.
  Long descriptions and accents remain readable, with natural paragraphs.
- **Crafting:** same recipe-row grouping, levels, ingredients and controller focus.
  No altered item icon, row size or navigation; test long names beside level badges.
- **Quest/Glossary/Bestiary:** title/section hierarchy, long titles, prose/scrolling,
  accents and selection. Open these in different orders after fresh launches.
- **Inventory/Character:** item/skill headings and short descriptions; long prose,
  comparisons, equipment, Hoods dye and existing actions remain functional.
- **Footers:** controller and keyboard hints, hold prefixes, selected/disabled
  actions, mouse hit areas, long labels, baseline alignment at 1080p/4K. The top
  navigation, glyphs, item/map/bestiary art and background must look unchanged.
- Brief unchanged-feature check: Tab/LB radial, accepted bars/quickslots, OW,
  SAHUD/FHUD, Smooth Map. These are regression checks, not claimed runtime passes.

This is a playable typography candidate, not a claim of IM Fell glyph identity
or exact screenshot parity from native compilation alone.
