# UI research — 9 October 2026

## Decisions

Target English only, following the user's scope update. Recommend **Field & Folio**:
Gentium Book for literary content and a restrained auxiliary sans for practical
labels. Start with a font-independent NPC color/shadow proof, then test English
Gentium independently. Do not deploy or rebuild the complete UI.

**Do not install the supplied Alignment Fix on this build.** It is already
deployed here; recommend disabling that package only. It has no competing mod
resource owners, but replaces current glossary code with a version missing
current input/layout behavior. [Assessment and exact Vortex procedure](alignment-fix.md).

## Evidence and limits

Primary runtime: installed Steam app 292030, build **25773555**, DX12 executable
**5.0.0.1048522**, under `C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3`.
The user calls this Remastered 5.01; executable version and build ID are the
reproducible identifiers. No inference from an internal `gameVersion=29` to a
marketing release is made.

Primary authoring resources:
`L:/Games/Steam/steamapps/common/The Witcher 3 REDkit/r4data/gameplay/gui_new/`.
The regenerated `E:/TheWitcher3RMDepot` contains other uncooked content, but does
not contain `gameplay/gui_new/swf`; the installed REDkit r4data does. REDkit's
cooked UI hashes differ from installed runtime hashes. Start each runtime patch
from the installed bundle, use REDkit sources for explanation, and compare any
compiled result with that runtime baseline.

Read-only compatibility evidence is in the separate checkout
`C:/Dev/witcher-mods-merger`, branch `general-merge`, commit
`feb1e6266bb1caec2690084636412c52310da6ee` at inspection. `general-merge` is not a
local ref in this worktree's repository; no branch switch, fetch, checkout edit
or merge was needed. Current live Mods and Documents/mods.settings were read as
stronger evidence than historical tables. Alignment Fix is enabled at 38;
FriendlyHUD 19, SAH 30, Bestg 31, Mod Settings Menu Fix 35. Package 04's merged
folder is at 2, CompatibilityText at 1; their different payload types do not
justify renumbering the working profile in this task.

The audit indexed **6,375 bundled entries plus two loose redswf files** across
live Mods/DLC. All three reference bundles were extracted into ignored build/
with the installed QuickBMS/BMS tool. Six embedded resource payloads were
inspected, with sixteen selected runtime baselines, validated SWF/GFx tag
streams, font glyph tables, JPEXS XML, selected decompiled current/reference
glossary classes, current EnemyFocus class, and installed WitcherScript/REDkit
ActionScript. These are structural/source observations, not game tests.

No installed game, deployment/staging, settings, save, author package or working
merged script was changed. No game launch or asset cook was performed. The
toolchain inspection found installed GFxExport and wcc; invoking wcc help from
the isolated output directory failed because it expected `build/gameconf.cfg`.
No settings were copied or generated to work around that. A current 5.01
authoring/export/cook round trip remains a required implementation gate.

## Four reference implementations

| Reference | Actual package | Actual changes | Compatibility conclusion |
|---|---|---|---|
| Easier to Read / Gentium Book | Two files: `modTW3FontGentiumBook/content/{blob0.bundle,metadata.store}` | One resource, `gameplay/gui_new/swf/witcher3/fonts_en.redswf`; regular, bold and italic embedded glyphs under the existing PF Din binding | English font substitution is structurally plausible; no current mod overlap. Clipping and game loading untested. Does not change shadow, name colors, alignment or sizes |
| Standalone Alignment Fix | Two files: `modtw3EasierToRead-UI-Fix/content/{blob0.bundle,metadata.store}` | Two complete glossary movies, Bestiary and Encyclopedia/Characters; altered text bounds and older embedded code | No competing mod owner, but current vanilla behavior is lost at the resource level. Not recommended unchanged |
| Font of Life 1.1 | Four files: bundle, metadata, info.json and author text | Three libraries: `fonts_en`, `fonts_ru`, `fonts_ua`; customized Alegreya glyphs with the same three PF Din bindings | Author targets 5.00c; packaging advertises successful cook, not 5.01 runtime proof. English-only project would replace only EN in an independently authored build |
| Configurable Name Colors 1.0 | 24 files: two WS, one menu XML, TOML, three localization CSV and seventeen w3strings | Whole-file EnemyFocus WS plus annotated helpers; RGB sliders for six categories; direct `mcNPCFocus.tfName.textColor` assignment after attitude updates | Manifest says 4.04. Whole-file conflict with FriendlyHUD; annotations do not remove that conflict. Reference implementation must not be installed blindly |

### Gentium

Three DefineFont3 tags: IDs 1/3/5, regular/bold/italic; each **1,557 glyph entries**,
including 528 code points in U+0020–U+024F and 171 in U+0400–U+052F. These counts
describe the embedded table, not a complete language-coverage certification.
The embedded family string remains `PF Din Text Cond Pro`, allowing existing
font aliases to resolve. The supplied bytes do not prove the exact upstream
Gentium version or all glyph provenance; identification as Gentium is the
reference's supplied identity and author credit. Do not reuse its glyph assets.

Current vanilla EN has 383 entries per style (329 in that Latin range; zero in
that Cyrillic range). Replacing only EN does not replace RU/UA libraries even
when the EN glyph table contains Cyrillic. This is now informational; English
is the only acceptance target. Audit English punctuation, accented proper
names, replacement glyphs, normal/bold/italic, numbers and controller glyphs.

### Font of Life

Three resources, not the single-resource simplification in the author's text.
RU and UA are byte-identical. All three contain the same three modified font
tag payloads, with **1,171 glyph entries per style** (406 in the Latin range;
145 in the Cyrillic range). Author text identifies Alegreya, condensation,
small-cap bold and hanging figures. The payload audit confirms replacement
font tables but does not independently measure every outline, transformation,
small-cap substitution or figure shape. Italic is included despite limited
author testing. No outline/color/layout controls are delivered by this package.

### Configurable Name Colors

`local/cnc.ws` adds fields and methods, wraps `OnConfigUI`, caches the
`tfName` object and reads `ConfigurableNameColors` settings. RGB is packed as
`R*65536 + G*256 + B`. The modified full `hudModuleEnemyFocus.ws` writes
`textColor` after `setAttitude`, and updates it on changed slider values.
It covers actors, VIP/Axii states and non-actor herb labels; it does not control
subtitle color, health bars, effect filters or a text RGBA value.

**Semantic pitfall:** helper comments/settings label 0 Friendly and 1 Neutral.
Current runtime `getFrameByAttitude` maps **0 neutral, 1 friendly, 2 enemy,
3 axii**, with 4 routed to VIP by `setAttitude`. Defaults for the misleadingly
named groups preserve the renderer's blue/ochre colors, but the slider labels
operate on the opposite categories. Use observed current mappings and actor
behavior, never this comment as an enum authority.

XML has eighteen integer RGB sliders, six headings and one preset. Its RGB
slider label strings are themselves saturated red/green/blue. Seventeen
language containers do not certify seventeen translated menus: supplied text
sources exist for EN/IT/RU only. No fonts or keyboard bindings ship. Menu XML
registration is an additional installation concern; it is unnecessary for a
fixed-palette first proof.

## Permissions and independent reproduction

Author pages checked 9 October: [Easier to Read](https://www.nexusmods.com/witcher3/mods/11657),
[Configurable Name Colors](https://www.nexusmods.com/witcher3/mods/11614),
[Font of Life](https://www.nexusmods.com/witcher3/mods/13507).
Each forbids uploading its files elsewhere and requires permission for modifying
or using its assets. Font of Life also identifies other-author assets.
No redistribution license was supplied inside the Gentium, Alignment or CNC
packages. Read-only examination is not permission to fork their binaries or
publish their scripts. Preserve them unchanged; cite techniques as observations.

Independently obtainable fonts: [SIL Gentium Book 7.000](https://software.sil.org/gentium/download/),
[Alegreya upstream license](https://raw.githubusercontent.com/google/fonts/main/ofl/alegreya/OFL.txt),
[Source Sans 3 upstream license](https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/OFL.txt).
They use OFL 1.1. Preserve copyright/license notices with embedded font derivatives;
review reserved-name requirements when modifying/naming them. Gentium reserves
Gentium/SIL and Source Sans reserves Source. Use an original project name for a
modified font; internal legacy binding names are a separate integration issue.
The mod authors' restrictive package terms do not grant or remove rights in
separately obtained upstream fonts. Game-derived UI remains governed by the
installed REDkit/game terms; no public redistribution decision is made here.

Reproducible inspection: [tools guide](../tools/README.md).
Proprietary dumps, downloaded fonts, tool binaries and rendered PNGs stay in
ignored build/. Original reports, HTML, inspection tools and tests are committed.
