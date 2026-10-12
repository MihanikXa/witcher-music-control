# Ink & Iron HUD implementation — private bars proof

11 October 2026. **Built and offline validated; user-reported successful in-game test on 12 October 2026.**
See [runtime feedback](ink-hud-bars-v1-runtime-feedback.md). The original manifest's `runtime_tested: false` is the **immutable build-time snapshot**, not the current later user observation.
This implements the visual-first direction; the earlier HUD exclusion is no
longer the target. No live installation, profile, settings, merged scripts or
saves were changed. No Inventory work was performed.

The private package combines **the unchanged Ink & Iron 0.8 player-bars movie**
with an original SAHUD settings adapter. A compiled-movie merge is unnecessary
for this first configuration. The official cooker accepts the author's existing
resource directly; no new SWF import or GUI step was required.

## Visual versus functional component matrix

Observed evidence: JPEXS 26.3.0 exports of actual 0.8 GFx payloads; current
deployed FriendlyHUD module scripts, SAHUD scripts and 13 merged source inputs;
resource ownership from installed bundles and loose files. Exact signatures,
SymbolClass IDs, ABC hashes and imports are in [contracts](ink-hud-contracts.json).
The earlier [complete inventory](ink-and-iron-0.8-audit/resources.csv) remains the
resource map. Matching exports establish a callable interface, not runtime correctness.

All six examined movies import `gfxfontlib.swf`. This is the existing font-library
contract; the proof does not install a new font library or replace QuietFolio.
Movie-class exports were inspected without fetching external SWFs. Nested
renderers/data listeners remain additional validation surfaces.

| Component / resource suffix under `gameplay/gui_new/swf/hud/` | Visual rendering | Visibility / contextual behavior | Data / input contracts | Integration result |
|---|---|---|---|---|
| Player status: `hud_wolfstatbars.redswf` | I&I draws health, segmented stamina, toxicity, XP and adrenaline in `iaiBars:Shape`; disc/sign ornament is added separately. One embedded 1024×184 DXT5 atlas. | SAHUD looks up `WolfHeadModule`, drives module alpha/visibility and `SetMaxOpacity`. Native `SetEnabled`, `ShowElement`, `SetState`, timer and scale methods remain. SAHUD alternate themes and `ToxicSplit` manipulate native children, which I&I sets to alpha zero. | All **18** current FHUD-bound functions are present, including vitality/stamina/toxicity, sign, focus, Ciri, coat of arms, level and mutation feedback. Gesture handler remains in the author movie. | **Implemented:** author movie + original in-memory adapter selecting original appearance and combined toxicity. Adaptive module fade works through the unchanged contracts, pending game test. Independent toxicity-only reveal requires separating I&I drawing layers or a new opacity export. |
| Buffs: `hud_buffs.redswf` | I&I `iaiRow` groups compact buff renderers and overflow; expanded grid retained; custom scale pivot via `iaiSetHudK(Number,Number,Number)`. | SAHUD module fade is separate from optional buff restyling, expiration-flash suppression and placement (`BuffsStyle`, `BuffsLayout`). | All **3** FHUD-bound functions exist: `setViewMode`, `setPercent`, `showBuffUpdateFx`; data storage/renderer contracts also matter. I&I native scaling helper is in `inkIronHudScale.ws`. | Next low-cost proof: retain I&I renderer/layout, disable the secondary SAHUD painter, test expiration flash and placement against actual renderer children. No evidence yet that a wholesale movie merge is needed. |
| Quest tracker: `hud_quests.redswf` | I&I tracker text/layout; distinct from journal-update banners. | SAHUD tracks `QuestsModule` and wraps current objective delivery; FriendlyHUD retains tracker policies. | All **5** FHUD-bound functions exist, including `SetSystemQuestInfo` and objective counter/highlight controls. Objective storage listeners need testing. `inkIronQuest.ws` actually targets **journalupdate**, not this tracker movie. | Candidate unchanged I&I tracker with existing behavior; compile any selected banner annotations separately. Do not merge these two surfaces merely because both are quests. |
| Minimap: `hud_minimap2.redswf` | I&I frame, rim clock/weather glyphs; retains `mcCommonMap`, hub/interior maps, masks, player/camera markers and distances. | SAHUD `Minimap2Module` fade, compass substitution and zoom logic remain script-side; FHUD navigation/marker logic remains. | All **13** FHUD-bound functions exist. Added `iaiSetHour` / `iaiShowClock` need I&I `inkIronMinimapClock.ws` for clock functionality. | Candidate unchanged movie + narrow clock annotation; test zoom, compass substitution, interiors, marker/distance data and scale. No resource owner collision with SAHUD's minimap skin, but script behavior still intersects. Smooth Map's full-screen movie is separate. |
| Enemy/nameplate: `hud_enemyfocus.redswf` | I&I replaces visible bars with `iaiBar:Shape`, sets native bar alpha zero, reformats `mcNPCFocus.tfName`, and creates **additional ghost name/role fields**. | SAHUD controls enemy children such as `mcHealthBar`, stamina/delay, level, lock and dodge feedback. Those handles no longer necessarily control the visible I&I drawing. | All **15** FHUD-bound functions exist; NPC-role annotation passes `Name|Role`. Accepted NPC Colors v4 targets the original name field, while the new ghost field uses I&I's own formatting. | **Real combined-resource work needed** for full accepted semantic colors/shadows and granular enemy visibility. Apply the accepted treatment to every new name field and bridge the visible bar/lock layers. Keep NPC Shadow v1 owner during this bars proof. Matching function names alone is insufficient here. |
| Interaction: `hud_interactions.redswf` | I&I changes name/prompt typography, key positioning and NPC feedback rows. | SAHUD `InteractionsModule` policy and FHUD positioning/visibility logic are separate. | All **14** FHUD-bound functions exist, including key/icon/text, hold duration, positions and visibility contracts. | Keep deployed **Interaction v2 private trial** unchanged now. Later combine its font/shadow treatment with I&I layout; verify hold/key glyph and dynamic text routes. Existing v2 acceptance status is unchanged. |

Current same-key movie owners are SAHUD for bars/buffs, NPC Shadow v1 for
enemyfocus, Interaction v2 for interactions. Quests/minimap have no installed
mod movie competitor in the completed resource inventory. They still have
FriendlyHUD/SAHUD script consumers. Root `hud.redswf` remains Outfit Wheel's
owner; this proof never replaces it. All 18 bar callbacks were checked against
the current installed FHUD script, not an older vanilla API list.

## Implemented adapter and its limits

[Original source](../src/hud/inkIronBarsBridge.ws) wraps **`SahSettings.Load()`**,
calls the existing method, then sets `hudStyle=0`, `hudMinimal=false`, and
`toxicMode=0` in memory. Existing policies, hold/fade times, health triggers,
Witcher Senses/radial rules, quickslot settings and data callbacks are retained.
Reloading settings after leaving a menu reapplies the constraint. It writes no
configuration file and adds no replacement native/merged script.

The working profile currently already stores original appearance and combined
toxicity (`sahHudAppearance=0`, `sahToxicMode=0`). Therefore the proof retains
its current choices. While enabled, the adapter also prevents choosing SAHUD's
alternate health/buff theme painters or toxicity-only mode; the menu may still
display the saved selection even though these runtime values are constrained.
SAHUD quickslot minimal styling remains governed by its separate setting.
This is an explicit v1 limitation, not a claim of every SAHUD option supported.

I&I's one composite Shape cannot follow separate health/toxicity alpha handles.
Load-order changes cannot fix that. If separate toxicity is wanted, the smallest
follow-up derivative splits the draw output into addressable health/toxicity
sprites and forwards SAHUD's existing alpha values to them; no complete HUD
rewrite is justified. Preserve the original health-damage lag tween when doing so.

## Build and technical evidence

Private ZIP: `deploy/ink-hud-bars-private-v1/Ink-Iron-Adaptive-Bars-v1-private-test.zip`
(108,969 bytes), SHA-256
`4e138f392d24c7475a7c49249214d1aaa6f3439f650a89a5ff17c4b50170db67`.

Its three members are only:

- `Mods/modInkIronAdaptiveBarsTest/content/blob0.bundle`
- `Mods/modInkIronAdaptiveBarsTest/content/metadata.store`
- `Mods/modInkIronAdaptiveBarsTest/content/scripts/local/inkIronBarsBridge.ws`

The bundle has exactly **one** resource key: `gameplay/gui_new/swf/hud/hud_wolfstatbars.redswf`.
No HUD root, buffs, fonts, NPC/interaction movies, textures outside the embedded
atlas, I&I HUD annotations, menu XML, localization or merged blob is packaged.
There is no hard dependency on another I&I module for this bars resource.
SAHUD and the existing FHUD/data/root providers must remain enabled.

Source and cooked resource SHA-256 are identical:
`7f6b35cc88602523561dd588a24ac725219976c8309370374b8011f91f8c32c1`.
The deployed SAHUD loose and bundled bars both hash to
`98ca8a2c197b65cc4df11ee387f14519a529f231114d02c7ec0ffce816daa9a7`.
The [manifest](ink-hud-bars-v1-manifest.json) pins author container, compiler,
original adapter, bundle/metadata/ZIP members, current source providers and logs.
All third-party payloads, source extracts, generated blobs and ZIPs stay ignored.
Author/game provenance is unchanged; local use is explicitly user-authorized.

Validation completed:

- Official **baseline, declaration-matched no-op and candidate** script compiler runs: exit 0, no Script/WCC errors, 819 warnings and 337 diagnostic assertions each; identical diagnostic multisets. Real output blobs produced, never packaged.
- The 54 required source pins include every deployed merged `.ws`, SAHUD implementation, affected FHUD module/helper sources and accepted NPC v4. Radial uses the current merged winner. A read-only, previously validated compatibility assembly supplies the rest. Seven opaque compiled mods are outside exact retail multi-blob simulation; this is a bounded compiler regression check.
- Official **cook → validate → pack → metadatastore**, each exit 0. Validation reports one resource and zero resource errors. The cooker emits only the two known runner startup assertions (`depotDirectory.cpp:11`, `soundFileLoader.cpp:101`); no new/resource-state assertion.
- CR2W chunk CRCs and atlas structure pass; whole cooked resource equals the author input byte-for-byte. Thus ActionScript, signatures, symbols, imports, timelines, layout, exporter linkage and compressed atlas remain exactly the author's resource.
- Single bundle key, exact independent ZLIB re-extraction, official metadata key, ZIP routing/readback/CRC and repeated deterministic ZIP encoding pass.
- Deployed script/container fingerprints and `mods.settings` match the before-build snapshot. Private runner workspace is restored. Seven synthetic fail-closed tests pass.

Logs and receipts: `build/ink-hud-bars-v1c/` (resource logs at its root; compiler
logs/receipt under `scripts/`). Preliminary failed runs `v1`/`v1b` stopped during
owner auditing because the helper initially assumed ZLIB; the final helper also
handles the installed raw owner codec. No compiler/cooker workaround was used.
The unchanged-resource control is `build/ink-hud-cook-control/`.

Rebuild into fresh ignored directories:

```powershell
python tools/build-ink-hud-bars.py --game "C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3" --settings "C:/Users/micha/OneDrive - hull.ac.uk/Documents/The Witcher 3/mods.settings" --assembly "C:/REDkitProjects/witchercompatibility/compatibility-validation/analog-gait" --out build/ink-hud-bars-repeat --deploy deploy/ink-hud-bars-repeat
python -m unittest discover -s tests -p "test_ink*.py"
```

The helper fails if canonical pins, affected current sources or resource owners
change. It requires the existing isolated runners and ignored audited extraction;
it does not fetch or publish author assets. Source-assembly/retail compilation,
physical file ownership and in-game visibility are different checks.

To reproduce the contract inventory from the existing private audit payloads:

```powershell
$components = @{bars='wolfstatbars'; buffs='buffs'; quests='quests'; minimap2='minimap2'; enemyfocus='enemyfocus'; interactions='interactions'}
foreach ($component in $components.Keys) {
    java -jar build/tools/ffdec/ffdec.jar -selectclass 'red.game.witcher3.hud.modules.*' -export script "build/ink-hud-probe/ink-$component" "build/ink-and-iron-0.8-audit/payloads/modInkAndIronHUD/gameplay/gui_new/swf/hud/hud_$($components[$component]).gfx"
}
python tools/audit-hud-contracts.py --game "C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3" --out build/ink-hud-probe/contracts-repeat.json
```

The committed contract manifest retains only bound/bridge signatures plus
symbol/import/hash metadata. Full decompiled author implementation stays private.

## Isolated installation and rollback

1. Exit the game. In Vortex, clone **Witcher Compatibility Test** as **Ink & Iron Integration Test**. Keep the original profile available. Back up the clone's profile settings before deployment; keep existing saves untouched and test from an existing save without saving campaign progress.
2. Install the ZIP above with **Install From File**, enable it **only in the clone**, and verify the preview routes the three members to the exact `Mods/modInkIronAdaptiveBarsTest/` paths. Do not enable the whole I&I HUD or All-in-One archive for this proof.
3. Keep SAHUD, FHUD, all five working compatibility packages, Movement Tweaks/analog gait, Hoods, Outfit Wheel, Smooth Map, GDC, Mod Settings Menu Fix, QuietFolio, NPC Colors v4 and NPC Shadow v1 enabled. Keep Interaction v2 and Subtitle Shadow v1 at their existing private-trial status. Leave Over 9000 disabled; do not restore VGXWalk or replace the working core package variants.
4. **Witcher resource precedence:** place `modInkIronAdaptiveBarsTest` immediately before `modSeamlessAdaptiveHUD` (lower numeric priority loads first). With the recorded order, insert the test at **29**, move SAHUD and following entries down by one **in the clone only**, preserving their relative order and keeping merged/compatibility packages first. Verify the resulting test priority is lower than SAHUD's. Both SAHUD's loose and bundled copies must lose this one resource key to the test mod; do not disable SAHUD itself.
5. **Vortex file rules:** none expected between these differently named mod directories. A `blob0.bundle` basename alone is not a file conflict across mod folders. If Vortex reports an unexpected same-destination rule, stop and inspect it. Engine same-key priority selects the movie; it does not merge resources.
6. Deploy the clone manually. **Do not rerun Script Merger or overwrite `mod0000_MergedFiles`.** The adapter is additive and compiled against existing SAHUD; no REDkit GUI operation is required. Launch and run the checklist below. An unexpected compile failure is a rollback condition, not permission to regenerate the stack.
7. Roll back by disabling only **Ink Iron Adaptive Bars Test** and redeploying the clone, then restart the game. SAHUD's original movie wins again, and its saved options reload because the adapter is absent. Alternatively return to **Witcher Compatibility Test** and deploy. No settings reset, save restore or compatibility ZIP regeneration is needed.

## Focused in-game checklist

Record resolution, HUD size, input device and pass/fail; offline checks do not
prove any of these. Test 1080p and 4K where available, Small/Large HUD size,
controller and keyboard, and at least a bright outdoor and dark scene.

| Test | Required result |
|---|---|
| Startup/script compilation | No new errors; normal save load. Existing mod settings remain accessible. |
| Player bars | I&I health/stamina/toxicity/XP/adrenaline visuals; correct values after damage, healing, potion toxicity and sign use; health loss lag settles; no double bars. |
| Adaptive behavior | Existing idle/exploration hide and combat/low-health reveal; configured hold/fade duration, manual reveal, Witcher Senses and radial transitions; no ghost bars or flicker after closing menus. |
| Data and control | Sign selection/dimming, insufficient stamina feedback, adrenaline changes, level/XP, mutation feedback and Ciri when accessible; selected sign hide option; mouse/pad gesture feedback. |
| Scale/layout | HUD option changes and resolution changes preserve anchor placement; bars do not overlap current buffs or clip the edge. |
| Other HUD | Buff timers, tracker objectives, minimap/compass/markers, enemy bars and interaction hold prompts behave as before; prove the single-resource scope in play. |
| Accepted typography/NPC | Gentium text still resolves; NPC semantic colors and shadows unchanged; Interaction v2 and Subtitle Shadow v1 remain separate trials. |
| Existing menus | Inventory/equipment and Hoods toggle/dye, shop, skills, journal, alchemy/crafting, bestiary, pause/main menu, Gwent, settings/mod menus open and navigate as before. |
| Existing gameplay | Analog walking/running transition, sprint, jump, movement/combat controls, Outfit Wheel selection and Smooth Map controls still work. No weight-mod or merged-script change. |
| Rollback | Disable the test, restart: original SAHUD movie and saved appearance/toxicity options return. |

## Remaining implementation order

1. **Completed by user report:** First isolated adaptive bars test works in-game; preserve the accepted package and its reproducible build receipt. Per-scenario runtime coverage remains unspecified. See [runtime feedback](ink-hud-bars-v1-runtime-feedback.md).
2. **Next: implement I&I buffs as a standalone private prototype**, then minimap and quest tracker as separate tested resource increments; preserve FHUD data listeners, SAHUD fading and navigation, and only the necessary I&I annotations. Check renderer paths before retaining SAHUD fine-grained cosmetic controls. Add separate toxicity rendering only if that option is required.
3. Combine enemy/nameplate drawing with accepted colors/shadows, including I&I ghost fields and SAHUD child-level alpha/lock/dodge controls. Then combine interaction v2 treatment with I&I key/hold/NPC feedback. These have demonstrated rendering-handle conflicts.
4. Port Outfit Wheel's `OWOpen/Close/Axis/Release/SetSlot/SetItem/Status` contracts into I&I common/overlay/root movies while retaining the `inkart:` background protocol and I&I glyph/layout vocabulary. Preserve current wheel callbacks. The older two-function bridge can be a diagnostic fallback; it is not the final visual plan.
5. Compare Smooth Map's actual zoom/filter/input handlers with I&I `MapMenu`; port useful controls into the I&I movie and keep the `inkiron.map.hints` replacement visible when common `mcInpuFeedback` is hidden. Map tile cosmetics can remain independent. No new worldmap asset was built here.
6. Implement the subsequent **one-screen Inventory** milestone in I&I's visual language: replace the entire equipment-circle arrangement, retain grid equipment markers, Hoods Quickslot2/isDyeable behavior, preview/input/equip/Roach contracts and better material/junk organization. Do not solve its architecture as part of the bars patch.

Only the composite-layer/child-handle cases currently demonstrate a need for
new movie exports or rendering changes. There is no evidence that all HUD
modules or all native callbacks must be rewritten. Future edited native movies
may need a manual Editor import/save; the proven bars path does not establish
that every future derivative can bypass that step.
