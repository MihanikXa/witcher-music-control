# Ink & Iron 0.8 integration: preserve the working stack first

> **Design policy superseded 11 October 2026:** The explicit user goal now includes **Ink & Iron's HUD appearance**, while retaining SAHUD/FriendlyHUD behavior, and allows redesign of Hoods/Outfit Wheel/Smooth Map visual components to match. The owner-preserving strategy below is a **bounded interim test/rollback plan**, not the desired finished appearance. Technical collision evidence, hashes and risks still apply. See [new visual-first authority](../design/ink-and-iron-visual-first.md).

11 October 2026. Canonical input: `reference/ink-and-iron-0.8/`, as explicitly
redirected by the user during this audit. No installation, game launch, settings
edit, script regeneration or asset modification was performed. Earlier 0.7.4
font conclusions are superseded below. This is an installation preparation,
not a runtime compatibility certificate or a menu redesign.

## Practical recommendation

Use **Fonts (Vanilla) 0.8 + the existing QuietFolio**. Keep the I&I HUD disabled.
Keep Hoods, Outfit Wheel and Smooth Map as owners of their existing movies.
Introduce the independent cosmetic modules, then I&I UI after resolving **two
common-menu script contracts**: background-image identifiers and map hint alpha.
This gets most retained menus into the I&I baseline without first merging four
compiled UI movies. Inventory/shop and the shared common/overlay styling remain
temporary exceptions. Do not describe that preservation configuration as an
unchanged, complete I&I visual installation.

The smallest additional modding task is a focused, independently authored
common-menu adapter, compiled against the exact working sources and upstream
annotations, followed by one cloned-profile smoke test. A binary merge becomes
necessary only if that test exposes a shared-renderer incompatibility, or if
the full I&I appearance must be retained in those four exceptions immediately.
Do not begin the later inventory redesign as part of this integration.

## Evidence and reproduction

The [resource matrix](ink-and-iron-0.8-audit/resources.csv) records every indexed
replacement, its hashes, existing owners/priorities, font dependencies and
decision. [Input files](ink-and-iron-0.8-audit/input-files.json) pin the extracted
containers/scripts/configuration. [Annotation inventory](ink-and-iron-0.8-audit/annotations.json)
lists every detected annotation and overlapping installed annotations.
[Summary](ink-and-iron-0.8-audit/summary.json) pins working merge inputs, actual
load order, font inputs and archive provenance. These are metadata, not mod assets.

The inventory includes POTATO70 bundle indexes, **named HCXT texture-cache
entries**, loose scripts, localization IDs/key hashes and configuration XML.
Bundle resources have decompressed SHA-256; textures have stored-stream SHA-256
plus key hashes and whole-cache input hashes. A stored texture hash is not a
decoded pixel hash. `metadata.store` is recorded as container bookkeeping, not
mistaken for an additional resource replacement. No DLC directory is supplied
by the canonical I&I extraction. No extracted standalone TTF/OTF is supplied.

The reader is based on the existing installed-format bundle auditor and the
[upstream cache implementation](https://github.com/Systemcluster/w3edit/blob/main/src/texture_cache.rs),
validated against local v6 entries. It reads source files; extraction is into
ignored `build/` only. Unknown formats fail or are recorded, never interpreted
as a successful compatibility result. The deployed UPR texture cache is a
**zero-byte placeholder**, recorded as an unparseable empty file; it supplies
no inspectable texture entry. Nonempty inspected caches parse successfully.

```powershell
python tools/audit-ink-and-iron.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --mods-settings 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\mods.settings' --vanilla-fonts-archive 'C:\Users\micha\Downloads\Ink and Iron - Fonts (Vanilla) 13111 0.8.0 2026-10-11T16-27Z Q81OXm5Yf.zip' --all-in-one-archive 'C:\Users\micha\Downloads\Ink and Iron - All in One 13111 0.8.0 2026-10-11T16-27Z sedaZoAhj.zip'
python tools/report-ink-and-iron.py
python -m unittest discover -s tests -p test_ink_and_iron_audit.py -v
```

The All-in-One argument is **read-only provenance and IM Fell research**, never
a deployment instruction. Public files contain no source bodies, glyphs or
textures. Native/AS decompilation remains private in `build/`. The `general-merge`
remote-tracking snapshot was read at `12739d3a906ae13b023b606ff1ef89cd230c76a1`;
its release/movement documents are historical evidence, while live Mods/DLC
indexes and `mods.settings` determine this report's current owner candidates.

## Actual modules and selection

Use the **0.8.0** files under the exact published package labels below, with the
listed folder in the installer preview. The [author's file list](https://www.nexusmods.com/witcher3/mods/13111?tab=files)
is the source for package labels and update recommendations; local hashes are
the authority for the audited payload. The author's alphabetical-priority
suggestion does not replace this installation's explicit `mods.settings` order.

| Published package | Exact folder | First test decision | Conditions / preserved features |
|---|---|---|---|
| Ink and Iron - Fonts (Vanilla) | `modInkAndIronFonts` | ENABLE | 0.8 alias-only XML; keep QuietFolio enabled; restart game |
| Ink and Iron - Fonts (required), IM Fell | same folder | DISABLE alternative | Audited from original All-in-One; would replace the accepted English font library and additional movies |
| Ink and Iron - UI | `modInkAndIronUI` | DEFER until adapter, then ENABLE | Hoods/GOW/Smooth Map win four listed movies; preserve all 12 I&I scripts unless an author-approved alternative is obtained |
| Ink and Iron - Dialogue Choices | `modInkAndIronDialogue` | ENABLE after Fonts | Independent dialog movie; retain FriendlyHUD/Monster Hunt/Sharedutils scripts and test timed choices/subtitles |
| Ink and Iron - Controller Buttons | `modInkAndIronButtons` | ENABLE with GOW ahead | Root HUD remains GOW; other supplied movies can be candidates; some root glyph styling intentionally lost |
| Ink and Iron - Icon Pack | `modInkAndIronIcons` | ENABLE with BIA ahead | Nine BIA icon corrections retain ownership; remaining icons use I&I |
| Ink and Iron - Bestiary Art | `modInkAndIronGlossary` | ENABLE with BIA ahead | Retain BIA doppler image; other art is I&I |
| Ink and Iron - Animated Main Menu | `modInkAndIronMainMenu` | ENABLE | Three movies, own artwork and one annotation script; verify mod.io submenu returns correctly |
| Ink and Iron - Loading Screens | `modInkAndIronLoading` | ENABLE after Fonts | Region movies use TitleFont; own English string ID has no detected installed overlap |
| Ink and Iron - Gwent Board | `modInkAndIronGwent` | ENABLE as isolated stage | Board movie and ten textures do not collide with current GDC resources; keep package 05 + its DLC |
| Ink and Iron - HUD | `modInkAndIronHUD` | DISABLE | Protect SAHUD/FriendlyHUD, NPC effects and deployed private trials; do not enable for settings labels |
| Ink and Iron - Map Inked | `modInkAndIronMap_Inked` | DEFER optional | Tile-only cache; no detected Smooth Map key collision; map appearance changes world map and minimap together |
| Map Charcoal / Parchment / Shadow; HUD Layout EXPERIMENTAL | absent | DEFER / not audited | Not necessary for requested baseline; do not infer contents from another variant |

The two exact original archives present locally are:

- `Ink and Iron - All in One 13111 0.8.0 2026-10-11T16-27Z sedaZoAhj.zip`
- `Ink and Iron - Fonts (Vanilla) 13111 0.8.0 2026-10-11T16-27Z Q81OXm5Yf.zip`

Their hashes and member comparison are in summary.json. The canonical extraction
combines the All-in-One's other modules with the Vanilla replacement of its
Fonts folder. Individual modular ZIP filenames/hashes are **not locally
available**; don't invent them. Before installation, obtain the separate official
0.8 packages bearing the labels above and verify their contents against the
canonical manifest. This is an acquisition step, not another research project.
Do not install All-in-One then rely on package-wide enable/disable to isolate its
modules. Do not repackage the author's extracted files without authorization.

## Font finding: the 0.8 change matters

The old local 0.7.4 Vanilla package shipped EN/RU/UA libraries and mapped BodyFont
to `PF Din Body`, absent from QuietFolio. **Do not use that old archive.**
The canonical 0.8 Vanilla bundle owns only `gameplay/gui_new/fonts.xml`.
Its EN Normal/Italic/Bold/Credits/Title/Body entries all use `PF Din Text Cond Pro`;
italic and bold retain their flags. The English library path stays
`gameplay/gui_new/swf/witcher3/fonts_en.redswf`.

QuietFolio's deployed library supplies three font definitions under that same
family name with the appropriate flags, each with 383 glyphs and the accepted
Gentium outlines. Thus **static alias/library coverage passes**: I&I Vanilla
can supply the added aliases while QuietFolio supplies their glyphs. There is
no same-key EN-library collision in this chosen pair, and no extra bridge build
is needed. English punctuation/accented names and actual wrapping still need
1080p/4K runtime checks. Cyrillic validation remains out of scope.

The alternative IM Fell folder actually supplies EN, RU, UA and gfxfontlib
movies, `character/panel_character_perks.redswf`,
`meditation/panel_meditation.redswf` and fonts.xml. Its font/license definitions
are separate inventory rows. The source includes OFL notices for IM Fell and
Cormorant. Neither its library nor those alternate menu resources are required
for the selected Vanilla path. Whole upstream UI/texture assets remain subject
to the author's permissions regardless of font license.

## Exact conflicts and smallest resolutions

Keys below are relative to `gameplay/gui_new/swf/` unless stated otherwise.
Existing priorities are the read-only current snapshot; lower numbers win.
These are configured owner predictions, not observed live renderer selection.

| Key / contract | Existing owner | Resolution / consequence |
|---|---|---|
| `inventory/panel_inventory.redswf` | Hoods (11) | Keep Hoods for first baseline. Its SlotPaperdoll accepts dye on Quickslot2 and honors `isDyeable`; I&I is not assumed to preserve that extension. Inventory and shop retain the current movie, rather than losing hood dye/drop behavior. A later combined inventory resource must retain that condition and X toggle/input bindings. |
| `common/panel_common.redswf` | Outfit Wheel (33) | Keep GOW; its `OWOpen/OWClose/OWAxis/OWRelease/OWSetSlot/OWSetItem/OWStatus` exports are required by outfitWheel.ws and absent from I&I's replacement. I&I shared frame/background appearance is deferred. |
| `overlay/panel_overlay.redswf` | Outfit Wheel (33) | Keep GOW and its wheel context; do not treat an overlay as decoration only. Imported/duplicated shared classes still require smoke testing against I&I componentslib. |
| `worldmap/panel_worldmap.redswf` | Smooth Map (20) | Keep Smooth Map. I&I's `inkironui_map.ws` hides common `mcInpuFeedback` with alpha 0, expecting its own movie's `inkiron.map.hints` listener; Smooth Map lacks it. Restore the retained common hint row through an independently authored, correctly ordered adapter before enabling UI. |
| `hud/hud.redswf` in Buttons | Outfit Wheel (33) | GOW wins. Buttons' root lacks OW exports. Most other button movies can still be installed unchanged. |
| `hud/hud_enemyfocus.redswf` | NPC Shadow (35), NPC Colors via WS | Leave I&I HUD off; retain both accepted packages and SAHUD/FriendlyHUD behavior. |
| `hud/hud_wolfstatbars.redswf`, `hud/hud_buffs.redswf` | SAHUD (29), bundled + loose copies | Leave I&I HUD off. Duplicate same-owner loose/bundled candidates are reported, not counted as different mods. |
| `hud/hud_interactions.redswf` | deployed Interaction V2 (40) | Leave I&I HUD off; preserve deployed trial and its unapproved acceptance status. Subtitle Shadow (41) has no direct I&I key collision. |
| Nine inventory icons; one bestiary doppler texture | BIA (9) | Keep BIA ahead of Icons/Glossary. Exact ten texture keys and stream hashes are in resources.csv. Cosmetic mismatch is preferable to discarding current corrected art. |

**Second common-menu contract:** I&I `inkironui_bgart.ws` sends `inkart:<key>`
to `updateMenuBackgroundImage`. The I&I movie recognizes this protocol; GOW's
movie assigns it directly to `W3UILoader.source`. A higher movie priority alone
would therefore cause invalid background loads. The preservation adapter must
restore the normal background via the observed `CR4CommonMenu.SetMenuBackground`
path after these notifications (including glossary/close notifications), or
suppress the I&I-only protocol without suppressing existing menu behavior.
Do not ship a guessed wrapper order. Verify the actual annotation chain in an
isolated compiler assembly, then test the resulting calls in the clone.

Keeping the four original owners is a **deliberate temporary exception**, with
named lost styling, rather than claiming the collision has been merged. If the
adapter cannot reliably run after the upstream senders, stop at that gate:
request an author-approved script variant or combine the two shared movies.
Adding OW exports to I&I common/overlay is a real binary modification requiring
permission and a cook/round-trip test, not Script Merger. The existing FFDec/GFx
and official REDkit pipeline can inspect/prototype it; no successful combined
resource or GUI-free import is claimed. Any necessary REDkit GUI step belongs
to the user in an isolated project.

Permission must cover I&I assets and any other author's code/art reused in a
combined movie. No derivative payload was produced by this audit.

### Scripts, dependencies and configuration

UI supplies annotations only, not replacement native script paths. Its
equipment-first wrappers overlap Hoods' paperdoll feedback and Hoods/BIA item
serialization. They are not automatically resolved by Script Merger. Keep
`iiEquipFirstInventory` **off**: it is an upstream alternative, not the approved
one-screen inventory direction. The existing scripts remain installed unchanged;
compile and test the combined annotations. UI's own character-layout/background,
rarity, shop-tooltip and save-overwrite methods are coupled to its movies.
Guarded missing Flash functions are not evidence of complete compatibility.

HUD's SnapToAnchorPosition wrapper overlaps SAHUD; additional 0.8 gear and quest
scripts depend on I&I functions in their matching movies. No cosmetic HUD
subselection is recommended yet, even where a movie has no same-path owner:
behavior intersections remain through visibility, pooling and script-supplied
data. The 0.8 quest-update movie moved into HUD; excluding HUD intentionally
retains the working quest-update presentation.

UI/MainMenu both wrap `CR4IngameMenu.ChildRequestCloseMenu` for distinct guarded
purposes. This internal same-target composition is separate from the external
annotation overlaps. The full annotations JSON supplies names and paths for
review; the audit is not a compiler. Keep package 04's thirteen scripts intact.

Hard observed dependencies: Title/Body aliases in UI/Dialogue/loading movies;
module-local custom Flash setters/listeners and supporting scripts/art;
Fonts IM Fell's own alternate library/movies if that alternative were selected.
The author recommends updating UI/HUD/Buttons together; this is a version
alignment recommendation, **not evidence that the UI requires the HUD module**.
Fonts (Vanilla) has no script dependency on HUD.

`bin/config/r4game/user_config_matrix/pc/modInkAndIron.xml` defines shared options.
Its page name and Gold Lock label rely on two string keys supplied in HUD's
English w3strings. Other options use literal labels. Loading's one English ID
and HUD's two IDs/key hashes have no detected installed conflicts. Shared
`en.w3strings` filenames alone are not resource collisions.

For the minimal HUD-free baseline, retain UI defaults and defer the I&I options
page if those localization labels are unavailable. Alternatively create an
original English label-only supplement; do not enable the entire HUD merely
to get its labels. Mod Settings Menu Fix stays enabled. Register only the new
XML entry through Vortex's menu workflow; never replace a complete file list.

## Installation sequence — user only, after adapter and explicit approval

1. Close the game. In Vortex clone **Witcher Compatibility Test** to
   **Ink & Iron Integration Test**. Preserve the original profile, current order,
   menu-file lists, Documents settings, MergeInventory.xml, managed package
   archives and private trial releases. Profiles redeploy into the same game
   directory; cloning alone is not an independent game installation.
2. Keep all five working compatibility packages, their existing original-package
   replacement choices, Movement Tweaks, analog gait, SAHUD, FriendlyHUD, Hoods
   + DLC, Outfit Wheel, Smooth Map, GDC + DLC, Mod Settings Menu Fix, QuietFolio,
   NPC Colors/Shadow and other working mods. **Over 9000 stays disabled.**
   `modWeight` is a different currently enabled package; don't disable/re-enable
   it based on the Over 9000 incident. Keep combat/core state as found. A separate
   user-side redeployment removed VGXWalk during this audit; the final snapshot
   has 41 entries. Do not restore that trial as part of I&I installation.
3. Import the separate unchanged 0.8 packages. Check roots/folder names against
   the table. Never import both font alternatives: they use the same mod folder.
   Keep All-in-One disabled. Preserve the trial release archives and current
   profile state without converting them into accepted releases.
4. Enable Vanilla Fonts first. The installed QuietFolio EN movie remains its sole
   mod owner; I&I owns only fonts.xml. Restart and verify Gentium in existing
   menus. Then stage Icons + Bestiary Art, Animated Main Menu, Loading, Gwent and
   Dialogue separately, smoke testing after each stage.
5. Enable Controller Buttons with GOW retaining the root movie. File-conflict
   rules apply only to the **same deployed physical file**. The distinct I&I,
   GOW/Hoods/Smooth Map/BIA folders have no Vortex same-destination file conflicts;
   use Witcher resource priorities for the intentional retained winners below.
   Do not create fictitious bundle-file conflicts across different folders.
6. Once the common-menu adapter has passed isolated compilation and its expected
   execution order is demonstrated, install that independently packaged adapter,
   then enable I&I UI. Do not regenerate Script Merger output. If startup reports
   a script failure, disable this stage and preserve the existing merges; capture
   the exact diagnostic. A native same-path script replacement is not part of
   the proposed adapter. Its precise priority is to be pinned by that follow-up's
   compiler evidence, not guessed here.
7. In Vortex's Witcher load-order page preserve every existing relative position
   and append the unchanged enabled I&I modules **after the current 41 entries**:
   Fonts 42, Icons 43, Glossary 44, MainMenu 45, Loading 46, Gwent 47,
   Dialogue 48, Buttons 49, UI 50. Use these numbers only if the current snapshot
   still has 41 entries; otherwise append in that sequence after the retained
   maximum. Disabled/deferred modules get no required priority.
8. Confirm the generated order after deployment: Hoods before UI; GOW before UI
   and Buttons; Smooth Map before UI; BIA before Icons and Glossary; GDC before
   BIA; SAHUD before BestGs; accepted font/NPC and trial state retained. These
   resource choices preserve functionality; they do not merge code or determine
   annotation wrapper execution order. No other original package is disabled.
9. Use [the test checklist](ink-and-iron-0.8-validation.md). Treat I&I fonts,
   common library and retained movie imports as a combined runtime test.
   Stop on invisible hints, lost dyeing, missing wheel functions, broken
   comparison/navigation or settings regressions. Do not save over campaign
   slots during the initial test.

No deployment is authorized by this report. No Vortex profile was created by
the agent. The acquisition and adapter gates make the later approval concrete;
they are not permission to deploy now.

## Follow-up package specification

One original adapter, provisionally
`Mods/modQuietInkCompatibility/content/scripts/local/quietInkCompatibility.ws`.
Inputs: canonical UI scripts in input-files.json, installed GOW/Smooth Map
movies and working commonMenu.ws hashes in summary.json. Changes: only the
two common-menu presentation contracts described above; no movement/combat
or inventory-layout changes. Source: independently written from observed
contracts; do not copy/repackage I&I code or author movies.

Build: first use the existing isolated official-script compiler workflow with
the exact native/merged sources and upstream annotations; a new reproducible
build command and hashes must accompany the implementation. **No adapter build
command or working patch is claimed in this audit.** Test controller map hints,
all common-menu transitions/glossary closures, backgrounds, Outfit Wheel in
gameplay/menu/overlay, Hoods dyeing and retained fonts. Rollback that candidate
by disabling only its Vortex package and I&I UI, then redeploying the clone.

If exact shared-library/embedded-class behavior defeats this small adapter,
the next minimal work is an author-approved combined common/overlay pair, not
a global redesign. Hoods inventory and Smooth Map can remain retained owners
until their respective deliberate improvements are actually required.
