# Ink & Iron HUD refinement v2 — private test build

12 October 2026. A targeted successor to the user's functioning HUD batch v1.
**13 October user runtime feedback:** v2 works and the slimmer enemy overhead geometry is liked; the **red health bar and hostile name remain too pale**, while the new flat controller button art is **not observed**. See [runtime feedback and glyph diagnosis](ink-hud-refinement-v2-runtime-feedback.md). Build-time `runtime_tested: false` refers to the time of packaging, not this later report.
This preserves accepted player-bars v1, boss presentation and all unrelated HUD
logic. Author assets, private ActionScript derivatives, native binaries and ZIPs
remain in ignored build/deploy directories. No live deployment is performed.

## Component status

| Requested area | Status and implementation | In-game acceptance still needed |
|---|---|---|
| Complete ordinary-enemy overhead composition | Completed offline. Slim rectangular health/damage fill; remove sawtooth/notches and decorative frame; smaller lock ring, level backing/text, quest/dodge icons; smaller name and tighter name/bar gap. Friendly/ghost role rules and lozenge removed, role data retained. | Long names, levels/skulls, lock/unlock and reduced lock scale, damage lag, stamina, status/quest/dodge feedback, rapid target changes and SAHUD hide/fade. |
| Balanced semantic colors | Completed offline. New private movie palette; repair accepted-v4 RGB when necessary in the existing post-SAHUD sync. Native name, role and ghost fields share coordinated colors. Accepted Colors v4 remains enabled and untouched. | Neutral/friendly/hostile/Axii/VIP distinction, merchant roles, fast target/category changes, bright snow, fire and dark interiors. |
| Previous bottom-left quickslots | Completed offline. Restore the actual installed 5.01 retail movie previously behind v1. Only its Xbox image references/art change. Remove the author annotation's I&I-only quickslot section and its unused option. Keep radial menu. | Consumables, depletion, item/sword switching, normal/minimal SAHUD display, native keyboard hints and controller prompts. |
| Flat controller glyphs | Completed offline. 34 Xbox identities per relevant movie, including dialogue, interactions, controls feedback, quickslots, radial, journal notifications, shared common/overlay and Outfit Wheel HUD root. Separate embedded atlas, flat ivory geometry/letters, alpha-only edge antialiasing; no baked gradient/bevel/gloss. Original glyph IDs, dimensions, frames and OW contracts retained. | A/B/X/Y, bumpers/triggers, sticks/directions/hold/scroll/tabs, D-pad, menu/back; input-device changes; dialogue skip/hold, radial navigation and Outfit Wheel actions. |
| Bottom-screen text shadows | Completed offline. Replace heavy authored dialogue current/previous/choice and both ambient-bark text placements; remove dynamic option-text double shadow/glow and soften its text action label. Ordinary subtitle trial already wins with charcoal/166-alpha/blur2/strength1/distance1; retain it without a duplicate replacement. | Ordinary subtitles, current/previous dialogue, ambient barks, long/wrapped lines and bright backgrounds. FriendlyHUD also uses ambient label instances for markers: check those markers and their visibility. |
| Smaller dialogue options | Completed offline. Effective normal English option target 26 → 21 px; action text 15 → 13 px; row step 40 → 36, extra-line step 35 → 29. Retain 35 px minimum hit height and wider multiline hits. Spoken subtitle sizes unchanged. | Selected/disabled/read/timed options, seven-plus choices/scrolling, long multiline text, mouse/touch/controller focus and haggling. |

All six areas have implementation or verified retained coverage. This is an
offline-validated test candidate, not a claim of visual acceptance in-game.
PlayStation/Switch/Steam-specific glyphs and full-screen Inventory/Shop/World Map
glyph copies are outside this Xbox HUD iteration. No boss movie edits are made.

## Exact visual changes and ownership

| Measurement | V1 | V2 |
|---|---:|---:|
| Health fill height | 6 px | 3.8 px (36.7% thinner) |
| Health outer height, including frame/backing | 9 px | 4.8 px |
| Hostile name | 21 px | 19 px |
| Name/bar gap used in ascent positioning | 10 px | 5 px |
| Lock radius | 19.5 px | 13 px |
| Level framed backing | 27 × 21 px | 20 × 16 px; frame removed |
| Level text | 20 px authored | 16 px applied during drawing |
| Supporting quest/dodge clip scale | Existing scale | 80% of existing scale |
| Friendly name / role | 22 / 15 px | 20 / 14 px |

The complete screen footprint depends on name wrapping, projected position and
runtime scale; these are authored measurements, not measured game screenshots.
Health data, the 0.8-second delayed-damage tween, stamina and native visibility
proxies are retained. Boss/dead guards remain. The successful bars adapter and
the batch's original script bridge are unchanged.

| Category | Accepted v4 | V2 name/role palette |
|---|---|---|
| Neutral | `#E9E2D2` | `#EEE3CF` |
| Friendly | `#B4C0A0` | `#AEC795` |
| Hostile | `#D6A093` | `#DE9C89` |
| Axii | `#B4C2D1` | `#A8C5DF` |
| VIP | `#D5C08E` | `#DFC183` |

Health changes from `#8E1914` to `#AA7565`, with muted `#C3A18F` damage lag.
Name shadows retain the accepted restrained treatment. Only known accepted-v4
colors are remapped after script processing; unknown colors are untouched.
The accepted script remaps vanilla colors only, so it does not undo the v2 RGB.

The installed Outfit Wheel root loads `swf\hud\hud_enemyfocus.swf` separately
from bossfocus. Enemyfocus owns the custom health/level/ring/name layers; the
author NPC annotation supplies roles/ghost placement and positions interactions
using `iaiPlateBottom`. FriendlyHUD's independent 3D navigation markers use
oneliner label instances; their sizes and data are preserved. These markers
should not be mistaken for additional enemy health geometry.

Pre-batch iteminfo is the actual current `content/content0/bundles/startup.bundle`
resource, SHA-256 `a83eaafda5dc2f6b33b3d69c34962922bceef6b44f01650aa9afd5475cf77f00`.
No other enabled mod owns that key behind the batch. A full installed bundle
lookup established the retail owner; subsequent builds read and hash-pin that
container. Retaining a glyph-only derivative is necessary for consistent Xbox
art; excluding the I&I movie alone would restore its old controller artwork too.

## Reproducible private build and validation

Use the desktop's bundled Python with Pillow, or an equivalent environment:

```powershell
$hudPython = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $hudPython tools/build-ink-hud-refinement.py --out build/ink-hud-refinement-repeat --deploy deploy/ink-hud-refinement-repeat
python -m unittest discover -s tests -p 'test_ink*.py'
```

The builder requires the verified v1 receipt/archive and current deployed v1
resource winners for a fresh build. It verifies canonical inputs, gathers actual
owners/priorities and current merged/SAHUD/FHUD script providers, stages private
source controls, cooks, validates, packs, creates metadata, re-extracts every key
and verifies deterministic ZIP bytes. It writes no game/Vortex/setting/save file.
The native runner's private workspace is restored after each stage. If a native
metadata launch times out after cook/validate/pack have completed, use:

```powershell
& $hudPython tools/build-ink-hud-refinement.py --finish-package --out build/ink-hud-refinement-repeat --deploy deploy/ink-hud-refinement-repeat
```

This verifies current inputs, candidate/compiler pins and completed native
controls, retries only metadata if necessary, then performs all bundle/ZIP gates.
Run only one native build/resume at a time because the runner uses one workspace.


Controller replacement appends a separate CSWFTexture export, extends the
resource's texture handle array and redirects only the 34 existing Xbox image
rectangles. All original atlas chunks stay byte-identical. This avoids altering
neighbouring images that share BC3 blocks. The new atlas uses flat ivory marks on a flat charcoal matte (alpha 224),
without lighting or gradients. RGB565 quantizes requested `#EFE3CE` to `#EEE2CD`
and `#141718` to `#101418`; alpha supplies edge antialiasing. Segoe UI supplies tiny button letters from the user's Windows font,
with its exact input hash recorded privately; no font binary is packaged.

The current oneliner GFx has a declared End boundary followed by 2,173 opaque
trailing bytes in an 81,920-byte decompressed allocation (exporter allocation padding is an inference). The writer retains
that tail verbatim and changes only approved text filter records. ActionScript
and playback contracts remain byte-identical. Dynamic dialogue formatting is
changed explicitly so it cannot repaint the original heavy option glow.

See the release manifest for exact input/output hashes, native logs/commands,
resource-key inventory, atlas checks, signature/listener evidence and script
diagnostic controls. Opaque compiled mods retain the established limitation:
source-assembly regression does not reproduce retail multi-blob compilation.
Native/resource checks do not prove live contrast, focus or frame ordering.


## Validated release

Private ZIP: `deploy/ink-hud-refinement-v2-release-final/Ink-Iron-HUD-Refinement-v2-private-test.zip`

SHA-256: `fa9e05bf961c64ad3e1b06578fc62761d818845abffa805b20e928cc3ee36ee9`.
Size: 11081264 bytes. Exact hashes/owners are in
[the original non-asset manifest](ink-hud-refinement-v2-manifest.json).
Detailed private source edits, atlas rectangles, exported contract evidence and
receipts are in `build/ink-hud-refinement-v2-release-final/`.

- 45 automated tests passed. All 22 native movies cooked unchanged, validated
  with zero resource errors, packed and re-extracted byte-for-byte. The alias
  adds one logical fonts.xml key using its unchanged original container.
- Nine new atlases contain 306 Xbox glyph instances. Original texture chunks,
  font definitions/imports, dictionary IDs and required controller/data/listener
  sites are retained. Shared roots keep byte-identical ActionScript, including
  Outfit Wheel's OWOpen/OWClose/OWAxis/OWRelease/OWSetSlot/OWSetItem/OWStatus.
- Current script controls all exit 0: baseline 819 warnings / 23,593 assertions;
  no-op and candidate each 819 / 23,620. Their diagnostic multisets match;
  all 55 current source/archive provider pins pass. These established native
  source-assembly assertions are not retail runtime acceptance. Seven opaque
  compiled mods cannot be recompiled from missing source.
- Native cook/validate/pack/metadata each exit 0 with only the two established
  depot-path/sound-bank startup assertions. An earlier candidate metadata launch stalled;
  its bounded metadata-only retry succeeded. The final corrected-art build
  completed all four native stages normally.
  `commands.json` and stage logs contain the successful release evidence.
  Preliminary compiler memory/relative-path failures are not release evidence.
- ZIP encoding repeated identically; every ZIP member passed CRC and readback.
  Game/settings snapshots match before/after. Accepted v1 HUD ZIP and player
  bars ZIP remain unchanged. New in-game acceptance is still pending.

No GUI or additional modding blocker remains for this candidate. PS/Switch/Steam
glyph art and full-screen menu copies remain outside this Xbox HUD scope.

## Isolated installation and gameplay check

1. Exit the game and select/clone the isolated I&I HUD test profile. Preserve
   the original Witcher Compatibility Test profile and both accepted v1 ZIPs.
2. Disable the **combined HUD batch v1 package** before enabling v2. Its author
   annotations must not coexist with v2 copies. Install the new private ZIP once.
   Expect `modInkIronHUDRefinementV2` and unchanged `modInkIronHUDAliasesTest`.
   Keep accepted `modInkIronAdaptiveBarsTest` v1 enabled separately.
3. Keep SAHUD, FriendlyHUD, QuietFolio/Gentium, Colors v4, Shadow v1, Interaction
   v2, Subtitle Shadow v1, Outfit Wheel, Hoods, Smooth Map, compatibility/merged
   packages and movement/combat mods enabled. Keep Over 9000 disabled.
4. Use the disabled v1 main folder's priority slot **31** for the refined folder
   in the inspected profile. Alias remains **29**. It must precede SAHUD **32**,
   Outfit Wheel **36**, NPC Shadow **38** and Interaction v2 **43** by lower number.
   Preserve all other relative order, including accepted bars. These priorities
   choose already combined movies; they do not merge binaries. Recheck actual
   clone order if it differs. Keep merged compatibility providers ahead.
5. With v1 disabled, no active same-file conflict should remain. The alias
   folder and optional `modInkIronHUDBatch.xml` are intentionally the same routes
   as v1. Register only the filtered v2 XML; use Vortex menu-file handling and
   do not replace a menu file list or regenerate Script Merger outputs.
6. Deploy the clone manually. Check retail script compilation/startup first.
   Test the six rows above without saving campaign progress. Compare the same
   enemies/NPCs, time of day and backgrounds; take before/after captures if useful.
   Verify boss bars and accepted player bars are unchanged, then minimap, quests,
   buffs, notifications, HUD fades, Hoods/Outfit Wheel, Smooth Map and analog gait.

## Component and complete rollback

Exit the game. A verified release caches its original base resources for
rollback after v2 is deployed. The builder still checks current script providers
and performs native/script/package gates, without deploying. For example:

```powershell
& $hudPython tools/build-ink-hud-refinement.py --reuse build/ink-hud-refinement-v2-release-final --rollback enemy --out build/ink-hud-v2-without-enemy --deploy deploy/ink-hud-v2-without-enemy
```

A glyph-only rollback variant was built and validated through native cooking,
zero-error validation, packing, metadata, exact re-extraction and ZIP checks:
`deploy/ink-hud-refinement-v2-rollback-glyphs/Ink-Iron-HUD-Refinement-v2-private-test.zip`.
It contains 18 native movie keys; original shared roots and retail quickslots
become owners again. SHA-256:
`23e6ee7bc085bec1d3e504a072d2ea217f3328852c9e0a6b62d48424d084dc20`.
Its metadata startup was stopped before the next build used the shared runner;
the guarded `--finish-package` resume completed it successfully. Other rollback
switches are implemented but have not each been independently built in this pass.

Valid independent switches (multiple may be supplied):

- `enemy`: restore v1 enemy composition and palette together.
- `quickslots`: restore I&I v1 iteminfo and its author key-hint section/option.
- `glyphs`: restore original Xbox artwork across all changed movies; original
  Outfit Wheel/shared roots become their resource owners again.
- `shadows`: restore v1 dialogue effects and the prior oneliner owner; preserve
  smaller choices unless `dialogue` is also supplied. The separate subtitle trial
  stays unchanged in either variant.
- `dialogue`: restore v1 choice sizes/spacing while preserving softer effects.

Disable the prior v2 package before enabling a variant; both have the same mod
folder identities. Do not enable two versions together. For **complete rollback**,
disable v2 and re-enable the immutable combined batch v1 ZIP at its prior order;
accepted bars and original providers stay enabled. Vortex removes/replaces the
optional XML as appropriate. Restart after redeployment. No settings reset,
merged-script regeneration or save restoration is required.
