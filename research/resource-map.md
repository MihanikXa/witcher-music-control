# Verified UI resource map

**11 October 2026 runtime and active work update:** The Field & Folio
interaction v1 movie-local Source Sans Regular selector is user-observed
**working in-game**, but `Talk` is too large/heavy, so visual acceptance is
withheld. The requested v2 tests a subordinate 17px hint and a soft local
shadow. The user now requests that overly strong ordinary-text effects
throughout the UI match the accepted NPC shadow's restrained appearance.
The full surface/parent/filter audit and staged implementation criteria are
in [text shadow unification](../design/text-shadow-unification.md).
These new work items are **not implemented** yet.

Current verified follow-ups supersede the historical build gate below:
[accepted English Gentium v1](gentium-v1-handoff.md) and
[Field & Folio interaction v1 offline handoff](field-folio-v1-handoff.md). The
English font pipeline passed and v1 is user-accepted. The new interaction-local
family passes serialization/GFx export, user-performed Editor import and the
official cook/validate/bundle/metadata pipeline. Both full atlases match vanilla;
exact bundle re-extraction passes. Runtime font resolution is now positively observed in-game for the interaction
field, but the size/heaviness is rejected; other dynamic input/prompt cases
remain untested. No global auxiliary alias is assumed.

**NPC live-binding update:** the authored `mcNPCFocus.tfName` hierarchy is
verified. The user observed the generic field accessor with UInt writes working
in v3 and accepted all v4 mappings (three categories directly observed). Color
work is closed; Number-versus-UInt remains the leading, unproven v2 failure
hypothesis. See the [v4 evidence](npc-colors-v4-handoff.md) and independent
[shadow-only v1 trial](npc-shadow-v1-handoff.md), now user-accepted in-game.

Paths below `gameplay/gui_new/swf/` are observed runtime keys, not filesystem
guesses. `content/content0/bundles/startup.bundle` owns the selected HUD modules
and inventory; `r4gui.bundle` owns the font libraries, glossary, subtitle movie,
quest journal and ingame settings panel. WitcherScript paths below are relative
to installed `content/content0/scripts/`. A loaded root/resource connection is
inferred from names/contracts unless corroborated by a bound module; no live
frame tracing or engine instrumentation was performed.

| Surface | Runtime resource | Script/source contract | Modification and known intersection |
|---|---|---|---|
| NPC/target names; target health/stamina/level | `hud/hud_enemyfocus.redswf` | `game/gui/hud/modules/hudModuleEnemyFocus.ws`: `OnConfigUI`, `OnTick`, `UpdateName`, `ShowDamageType`; binds `setEnemyName`, `setAttitude`, `setEnemyHealth`, `setEnemyLevel`; actual runtime AS `HudModuleEnemyFocus` | Named `mcNPCFocus.tfName`; field 38, centered, `$NormalFont`, height 400 twips = 20 logical px, leading 40 = 2 px, multiline/wordWrap. Color assigned by `setVisibility`. FLA/PlaceObject filter for shadow. Full WS conflicts with FriendlyHUD; SAH wraps damage/dodge methods and controls visibility. No installed movie competitor |
| Cinematic dialogue choices/previous sentence/skip prompts | `hud/hud_dialog.redswf` | `hudModuleDialog.ws`: `SentenceSet`, `PreviousSentenceSet`, `ChoiceTimeoutSet`, `SkipConfirmShow`, `setAlternativeDialogOptionView`; REDkit `HudModuleDialog.as` | Movie text fields/renderers and script-supplied localized text, selection/timing state; FriendlyHUD replaces this WS, Monster Hunt/Sharedutils wrap choice callbacks. No movie owner collision seen. Direct choice/sentence filters are enumerated below; live renderer state remains to validate |
| Cinematic subtitles/speaker | `witcher3/hud_subtitles.redswf` | `hudModuleSubtitles.ws`: `OnSubtitleAdded`, `addSubtitle`, `removeSubtitle`, `updateWidth`; REDkit `HudModuleSubtitles.as` | `tfSubtitles`, field 1, centered/wordWrap, authored 18 px but WS injects **26 + SubtitleScale**; alternative Witold text injects `#5ACCF6`. Movie/HTML/WS contributions must be treated independently. Poster subtitle route duplicates behavior; don't assume one movie covers every subtitle |
| Ambient NPC chatter | `hud/hud_oneliners.redswf` | `hudModuleOneliners.ws`: `OnCreateOneliner`, `CreateOneliner`, pooled `mcOneliner<ID>`; SAH restoration helper | Different movie/pool from subtitle/nameplate. Native positioning/visibility and SAH pooled alpha handling; FriendlyHUD same-path source replacement. Direct authored variants are enumerated below; pool-specific runtime behavior remains to validate |
| World interaction prompts/hold icons | `hud/hud_interactions.redswf` | `hudModuleInteractions.ws` binds `SetInteractionKey`, `SetInteractionKeyIconAndText`, `SetHoldDuration`, `SetVisibilityEx`, `SetPositions`; REDkit `HudModuleInteractions.as` | Text/art/key-code path and world placement; preserve controller/keyboard selection and hold timing. FriendlyHUD owns script variant; no movie collision. Direct action field size/filter is enumerated below; no guessed global text setter |
| Active quest/objectives | `hud/hud_quests.redswf` | `hudModuleQuests.ws`: `ShowTrackedQuest`, `SetSystemQuestInfo`, `SendObjectives`, storage `hud.quest.system.objectives`, `GetColorByQuestType` | Script sets Story `#FFCC00`, Chapter `#BB8237`, side/hunt/treasure `#C0C0C0`; movie styles/highlights separate. FriendlyHUD replacement plus SAH/Monster Hunt wrappers on SendObjectives. Change selected color rules without rewriting tracking/visibility |
| Quest/item/level notifications | `hud/hud_journalupdate.redswf`; `hud/hud_lootfeed.redswf` | `hudModuleJournalUpdate.ws`, `AddNewJournalUpdate`; `HudLootFeedShower.as` sets `tfName.text = data.name` | Queue behavior and artwork differ from objectives. SAH may suppress notices; preserve it. FriendlyHUD scripts intersect; mixed direct filters are inventoried below; runtime queues require tests |
| Quest journal | `journal/panel_journal_quests.redswf` | Current menu/script data and REDkit journal AS | Independent panel text/layout. No scanned bundle collision; full renderer state/path audit remains pending |
| Inventory/item names/tooltips | `inventory/panel_inventory.redswf`; `inventory/panel_inventorysockets.redswf` | `game/gui/menus/inventoryMenu.ws`; REDkit `slots/SlotBase.as` passes item quality to `mcColorBackground.setByItemQuality`; tooltip classes format label/text | Hoods replaces inventory movie. Item rarity/background/icon is not synonymous with NPC attitude; retain rarity semantics. Tooltip font/HTML/format needs deeper per-renderer inspection. Hoods/BIA script wrappers on inventory component also intersect |
| Settings/ingame menu | `mainmenu/panel_ingamemenu.redswf` | `game/gui/main_menu/ingameMenu.ws`, `ingamemenu/igmOptions.ws`; XML groups/Vars specify settings rows | Mod Settings Menu Fix and Better IGNI menu hooks, SAH options handling, Sharedutils; merged package04 sources preserve these. Text layout/style belongs in movie/renderers; XML is not a general font/stroke stylesheet |
| Bestiary/Characters | `glossary/panel_glossary_bestiary.redswf`, `glossary/panel_glossary_encyclopedia.redswf` | Current extracted `GlossaryBestiaryMenu`, `GlossaryEncyclopediaMenu`, `W3ScrollingList` | Alignment Fix whole-resource winner. See separate assessment; geometry, imported image IDs and embedded code all need current-baseline preservation |
| Player stat bars/buffs/radial | `hud/hud_wolfstatbars.redswf`, `hud/hud_buffs.redswf`, `hud/hud_radialmenu.redswf` | Existing HUD/stance functions, Bestg `BG2_SetStance`, SAH movie contracts | Wolf bars already have SAH vs Bestg overlap with SAH selected. No typography patch here in first proof; broad library changes still affect text indirectly |
| Root/common/overlay and map | `hud/hud.redswf`, `common/panel_common.redswf`, `overlay/panel_overlay.redswf`, `worldmap/panel_worldmap.redswf` | Root module imports/shared UI; Outfit Wheel and Smooth Map | Outfit Wheel owns the first three; Smooth Map owns map. Never replace root HUD simply to change one nameplate |

## Exact nameplate and subtitle effects

Additional direct XML observations from the installed runtime (all sizes are
authored logical sizes; script/HTML can override them):

| Movie / named field | Definition ID / size | Direct placement effect |
|---|---|---|
| hud_dialog / tfLine | 213 /23 px | Opaque black glow, blur2.5, strength10, passes3 |
| hud_dialog / tfSubtitles, tfPreviousSubtitles | 236/237 /27 px | Opaque black shadow, blur4, strength20, distance0, passes3 |
| hud_interactions / tfActionName | 215 /22 px | Opaque black glow, blur4, strength3, passes1 |
| hud_quests / tfQuestName | 4 /20 px, leading−2.5 px | Opaque black shadow, blur2, strength20, distance0, passes3 |
| hud_quests / tfObjective, tfOr | 18/20 /19 px | Same strong shadow as quest title; leading2 px |
| hud_oneliners / textField variants | 1/2 /25/24 px | Black shadows: blur2/3, strength10/4, distance0, passes2/3 |
| hud_lootfeed / tfQuantity, tfName | 21/22 /22/24 px | Quantity black shadow blur3/strength1; name has no direct placement filter |
| panel_inventory / tfSlotName variants | 236/273 /18/17 px | No direct filter; latter leading−5 px |
| panel_inventory / tfQuantity variants | 70/211/274 /24/23/23 px | Mixed shadow/glow definitions; cannot treat every quantity identically |
| panel_ingamemenu / mcTitle | 81 /30 px | **White** glow blur7, strength0.3984375; not a black stroke |
| panel_ingamemenu / tfName | 378 /14 px | No direct placement filter |

JournalUpdate contains 24 text definitions with mixed shadows/glows; Inventory 47;
IngameMenu 180. Their repeated names are per-sprite, not unique global selectors.
A missing direct placement filter does not rule out a parent filter or runtime
effect. These observations narrow the editing targets; parent-chain and runtime
state inspection is still required before a patch.

Current NPC `PlaceObject3` named **tfName**, character 38, depth 35, inside
mcNPCFocus's sprite 63, carries **DROPSHADOWFILTER**: black RGBA `(0,0,0,255)`,
blurX/Y 4, strength 3, distance 1, angle 0.785385 radians (~45°), passes 1,
compositeSource true, innerShadow/knockout false. The wide, strong shadow explains
the apparent outline here; a Stroke property is not required to reproduce it.

Current subtitles `PlaceObject3` named **tfSubtitles**, character1, depth1,
carry **GLOWFILTER**: black RGBA `(0,0,0,255)`, blurX/Y5, strength1, passes3,
compositeSource true, innerGlow/knockout false. This is an independently editable
authored filter. Do not globally delete all GlowFilters (many represent focus).

**`DefineEditText.useOutlines=true` means render embedded font glyph outlines;
it is not the black text-border setting.** Toggling it is not an outline fix.
Likewise the NPC's authored ivory is overwritten by runtime attitude color;
editing only its initial textColor will not desaturate target names in gameplay.

Runtime NPC palette confirmed by decompilation:

| Numeric input | Renderer frame | Actual name color |
|---|---|---|
| 0 | neutral | `#79B8FD` |
| 1 | friendly | `#D3A37D` |
| 2 | enemy | `#FF0000` |
| 3 | axii | `#FCB549` |
| 4 | vip (special route) | `#5AFF00` |

Preserve the visibility decisions in `setVisibility`, bars, quest icon, hard
lock, level and dodge/essence paths when changing colors. `setNPCQuestIcon` and
`setEnemyName` position the quest icon using `tfName.textWidth`; a wider font
therefore changes more than appearance. `SetScaleFromWS` is a no-op in runtime
EnemyFocus; do not assume the global HUD scale slider sizes its name text.

Damage numbers are dynamically allocated TextFields (`$NormalFont`, size24,
centered). `ShowDamageType` in current WS selects saturated DoT red `#FF0000`
and heal green `#00FF00`, among other values, and invokes `setDamageText`.
Name field changes do not automatically change those colors or new text fields.

## Font pipeline and unresolved packaging gate

Installed REDkit `fonts.xml` maps `$NormalFont`, `$BoldFont`, `$ItalicFont` and
credits to PF Din, with bold/italic flags. It selects EN/RU/UA/AR/ZH/CN/JP/KR
libraries separately and Latin-language aliases reference EN. Only EN is in
this project's proposed replacement scope.

Font library SWF contains glyph shapes/advances/metrics. UI movies contain
TextField/font-class references, bounds, margins, alignment/leading, filters,
placement and embedded ActionScript. WS supplies text, state, some colors and
HTML font sizing; user config supplies scale/preferences. These layers are
verified; no universal RGBA or outline setting is established.

Installed `bin/tools/GFx4/gfxexport_mult4fix.exe` exists; current resource formats
include CR2W with nested **CFX** and reference Gentium **FWS**. Bundle magic is
POTATO70; current/reference indexes exercise 0x130 and 0x140 record layouts.
JPEXS 26.3.0 reads the extracted payloads and exports XML/decompiled scripts.
Compression/header length and CR2W wrapper sizes vary: font payload offsets
601 vanilla, 622 Gentium, 630/644 Font of Life; NPC offset 592. Thus the Font of
Life text's fixed 601-byte wrapper recipe is not a universal technical method.

The supplied REDkit FLA files begin with ZIP entries, but Python zipfile rejects
their central directories. They were not repaired or treated as ready-editable
source. Direct GFx inspection is available; authoring FLA suitability remains
unresolved. The official exporter/cooker invocation and a current-version
round-trip are **not yet verified**. No mod build command is claimed to work.
See the [prototype gates](../design/implementation-plan.md) for the exact next
step. A browser's CSS shadow/font spacing is a visual proposal, not an asserted
Scaleform API or in-game result.
