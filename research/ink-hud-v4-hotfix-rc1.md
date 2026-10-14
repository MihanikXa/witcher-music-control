# HUD v4 hotfix RC1 — radial-code isolation and face-letter sizing

**Status: technically validated private diagnostic/recovery candidate; the actual
runtime stopping point is not confirmed.** This is one replacement package,
not a stack of experimental HUD mods. User acceptance freezes v4's enemy reds,
warning, quickslots and overall glyph size. No live deployment occurred.

## Confirmed evidence and remaining uncertainty

The 14 October ownership scan re-extracted all 23 logical resources. Every
winner matches the tested v4 hash: `modInkIronHUDRefinementV4` priority **30**,
with the unchanged aliases at **29**. No priority changes are proposed.
Current input.settings contains both `IK_Tab=(Action=RadialMenu)` and
`IK_Pad_LeftShoulder=(Action=RadialMenu)` in BASE_SHOW_RADIAL_MENU. Both inputs
failing is direct user evidence, not proof of a specific Flash exception.

The opening chain observed in current 5.01 sources is:

1. Radial GFx configUI initializes fields and appends its meditation/exit footer
   buttons, then dispatches **OnConfigUI**. The footer creates
   InputFeedbackButtonRef, applies data, and validates/layouts its renderers.
2. Native CR4HudModuleRadialMenu.OnConfigUI binds Flash functions and registers
   RadialMenu, CloseRadialMenu and ConfirmRadialMenuSelection listeners.
3. OnRadialMenu checks press/action/dialogue/input gates, then ShowRadialMenu
   stores the radial context, forces analog UI, plays the opening sound, updates
   items, slows time through FriendlyHUD and marks m_shown.
4. CR4ScriptedHud.OnRadialOpened forces HVS_RadialMenu. The HUD root's
   RadialMenu state shows RadialMenuModule, BuffsModule and ItemInfoModule.
5. GFx ShowElementFromState handles radial visibility/alpha, mouse handlers,
   input blocking, selected items and timers. Closing restores the context and
   normal control. ItemInfo.RadialMenuOn forwards setRadialMenuOn to quickslots.
   SAHUD observes the radial state and honors its fade/quiet interval.

**Important negative evidence:** ShowRadialMenu's empty Flash stub is also empty
in working v1/v3; it is not a newly broken implementation. The active rendering
path is ShowElementFromState. The full decompiled radial classes differ between
v3 and v4 only in **InputFeedbackButton** and **ModuleInputFeedback**. The actual
HudModuleRadialMenu show/hide/selection class is unchanged. Signatures passing
therefore cannot establish that the prerequisite footer setup completed.

The v4 InputFeedbackButton adds an unsafe expression:
`_gpadIcon == mcIconXbox && _gpadIcon.visible`. When both references are null,
that equality is true and the dereference is unsafe. Its new hold-gap predicate
also considers null-equality to be an Xbox match. This is a confirmed code
hazard, **not a confirmed live exception**: authored radial button timelines do
contain mcIconXbox, and no runtime trace establishes whether bindings are absent
at the failing call. The footer constructor creates _canvas; its simple absence
is not established. Do not label any of these hypotheses as the actual cause.

Restored I&I iteminfo does retain the **iaiKeyHints** export while the v4 script
package omits the optional key-hint annotation section. That is a real optional
configuration mismatch. The original section sends hint data; its only
RadialMenuOn call is inside iaiQsTestOn(), which always returns false in release.
Its omission cannot directly toggle the wheel. No speculative script restoration
is bundled into this isolation test. Existing quickslot behavior stays as v4.

**Why a runtime test is indispensable:** no game/Flash runtime exception trace
or successful wheel opening is available to this offline build. Cooking parses
resources; it does not exercise constructor timing, input dispatch or state
transitions. Restoring the verified working radial bytecode is the smallest
single-resource isolation of the leading local difference. No retail iteminfo
swap, root-code rollback or second variant is built blindly.

## Implemented candidate

- Replace **only hud_radialmenu's DoABC records** with exact bytes from the
  verified, working v3 package. Keep v4's smooth shapes, authored sprites,
  placements, fonts, imports, symbol mappings and texture linkage. This removes
  the v4 local prompt adapters from the wheel. **Wheel footer layout temporarily
  follows working v3**, including its local icon scaling; this is intentional
  diagnostic scope. All accepted v4 layouts outside the wheel stay unchanged.
- Reduce only A/B/X/Y interior contours to **80%** about their existing optical
  center: 21 → **16.8** canvas units. Circle diameter **38**, outline **1.25**,
  backing RGBA, 64 × 64 canvas, other symbols and outer art remain unchanged.
  Apply the same letter treatment to existing native bitmap fallback slots.
  No gradients, new texture handles or font-library changes.
- Keep I&I iteminfo's **v4 bytecode exactly**, including its functional
  quickslot renderer. Its only changes are A/B/X/Y art. Shared HUD/OW bytecode
  is also exactly v4. Every other changed provider differs only in face art.
- Freeze enemyfocus **byte-for-byte**: health #B94A40, name #D9695A, lag #C77D6E,
  geometry and 179-alpha pre-attack warning. Fourteen logical resources remain
  exactly v4, including bosses, other HUD indicators and aliases.

This is **RC1**, not a claim that the wheel is fixed in-game. If it works with
I&I quickslots retained, the fault is narrowed to the removed radial-local
bytecode/adapters or their recompilation. It still does not identify the exact
instruction. A final layout-preserving correction can then be confined to those
two classes. If it fails identically, the local-bytecode hypothesis is rejected;
next inspect runtime root/state and iteminfo interaction, retaining this single
clear result rather than generating several simultaneous guesses.

## Build evidence and reproduction

`tools/build-ink-hud-v4-hotfix.py` performs pinned-input checks, exact tag-level
change whitelisting, CRC/atlas checks, independent complete GFx XML parses,
native cook/validate/pack/metadata, extraction and deterministic ZIP verification.
Private inputs are deployed v4, accepted v3 radial bytes and the verified I&I
iteminfo glyph map. All derivatives, previews and packages stay ignored.

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/build-ink-hud-v4-hotfix.py --out build/ink-hud-v4-hotfix-rc1-final --deploy deploy/ink-hud-v4-hotfix-rc1
& $py tools/build-ink-hud-v4-hotfix.py --out build/ink-hud-v4-hotfix-rc1-final --deploy deploy/ink-hud-v4-hotfix-rc1 --finish
& $py -m unittest discover -s tests -p 'test_ink_hud*.py'
```

Use fresh ignored output paths to reproduce. The current owner extraction and
live-input snapshot under build/ink-hud-v4-hotfix-work are mandatory evidence.
Segoe UI input is pinned to the accepted v4 hash; fonttools 4.60.1 remains local.
No third-party assets or code are committed. The release manifest records exact
source/output hashes and provenance, native logs, unchanged keys and limits.
Native metadata fallback, if needed, is separately labeled and requires the
existing independent native control; no fallback is represented as native.
WitcherScript and menu XML must be byte-identical to v4. Existing compiler
baseline/no-op/candidate blobs and their actual provider hashes are revalidated;
no fresh script compilation is claimed for unchanged sources or opaque mods.

## One installation and decisive game test

1. Exit the game. In the isolated profile **replace/disable the original v4
   package**, then install RC1. It deliberately uses the same mod folder
   `modInkIronHUDRefinementV4`, so retain its current **30** slot and all existing
   rules. Keep aliases at 29, existing bars/SAHUD/FHUD/OW/Hoods/Smooth Map,
   QuietFolio, NPC patches, movement/combat and compatibility packages unchanged.
   No menu registration or Script Merger regeneration; menu XML is unchanged.
   Do not enable two v4 packages simultaneously. Over 9000 stays disabled.
2. Start a normal Geralt save, outside a conversation/cutscene. **Press Tab**.
   Record whether the wheel opens. If it does not, record whether the wheel
   sound occurs, time slows or movement becomes blocked: that distinguishes
   native dispatch/state transition from failure before registration.
3. **Press controller LB independently**, without changing input bindings.
   Perform the same observation. Do not infer controller success from Tab.
4. If open: navigate signs with analog stick and mouse/keyboard, choose **Axii**
   and another sign, confirm selection, close and regain normal movement/time.
   Check relevant quick-access items, meditation/exit prompts and FHUD extras.
5. Repeat both input routes several times, after combat and after opening and
   closing a normal menu. Confirm no stuck slowdown, input blocker or invisible
   wheel. Check I&I quickslot display, consumables and controller hints.
6. Confirm A/B/X/Y have more breathing room in world prompts, dialogue, footer,
   quickslots and OW; outer sizes/layout remain v4 outside the diagnostic wheel.
   Briefly verify unchanged perfect reds, warning, boss/player bars and shadows.

**Return the two input outcomes and sound/slowdown observation.** No further
variant is required before that result. This is the remaining runtime gate.

Rollback: disable/remove RC1, reinstall or re-enable the untouched original
v4 ZIP in the same folder/slot, manually deploy and restart. Restore its exact
bundle/metadata together; no settings, saves or merged scripts need changes.
Original v4 SHA-256: `83d4482b6e65a1a72bfdf7d377ed1d7782594e5fd415227aa4057f49f4a46747`.
This rollback preserves accepted visuals but brings back the reported wheel
regression. Earlier v3/v2 archives remain available; they are not the proposed
final configuration because I&I quickslots must stay.

## Release result

Private ZIP: `deploy/ink-hud-v4-hotfix-rc1/Ink-Iron-HUD-v4-Hotfix-RC1-radial-isolation-private-test.zip`, 10,995,070 bytes. SHA-256: `16520f81637acb86e423a4384e6187ed9b45c56683a8056e791b627b47cbefbb`.

Native cook, 22-resource validation (zero resource errors) and pack passed. Native metadata startup timed out at 240 seconds without passing the commandlet. The independently verified native-control table relocation passed, reproducing its control byte-for-byte and rejecting changed key order/import/buffer/dependency tables. This release uses **fallback metadata**, not a successful native metadata command. Exact bundle extraction, metadata keys, deterministic ZIP, all unchanged component hashes, script/menu equality and live snapshot checks passed. Known depot-path and absent-sound-bank startup assertions match accepted controls; no new assertions were allowed.

65 HUD regression tests passed. Actual final GFx A/B/X/Y exports were inspected at 0.6875, 1.375 and 4 times canvas scale. These prove definitions and smooth shape construction; they do not prove the radial opens in-game. The six hotfix tests cover letter-only scaling, other art equality, exact working radial ABC, frozen components, unchanged iteminfo/root code and the nullable equality hazard as a model, explicitly not a captured runtime exception.

## Additional user observation — 14 October 2026

Asked whether the failed v4 Tab/LB attempt produces the opening sound, slowed
time or blocked movement, the user answered: **"Nothing happens."** This is
feedback about the original v4 failure, not a test result for hotfix RC1.

The lack of perceived opening effects supports a failure before the native
ShowRadialMenu sequence reaches sound/time/context changes. Early native action
gates or missing input-listener registration remain possible; it does not
prove an ActionScript null exception. In the observed source chain, radial
footer setup occurs before GFx dispatches OnConfigUI, which registers those
listeners. The existing RC1 radial-bytecode isolation therefore remains the
first test. An invisible successfully opened wheel is less supported by this
observation. No second variant or package change is justified before RC1 results.

## RC1 in-game result — 14 October 2026

**User statement, verbatim:** "Still doesn't open or do anything when I press the buttons".

This follows the requested private RC1 test of keyboard Tab and controller LB. **RC1 FAILED TO RESTORE THE RADIAL WHEEL.** No wheel or observable response was reported. The statement does not independently prove absence of every subtle sound/time/input effect, although earlier the user said nothing happened with original v4. **This supersedes pre-test RC1 status** elsewhere in this report.

**Updated diagnosis:** Exact working v3 DoABC inside the v4 radial movie was **not sufficient** to restore radial operation. The removed v4 radial-local ABC changes alone cannot be considered a complete fix. This does not isolate whether surrounding v4 radial sprites/placements, root or shared GFx initialization, iteminfo/I&I quickslot state, v3 WitcherScript, other enabled mods, or native input gates prevent the opening action. The nullable Xbox icon expression is a possible hazard in other movies, not a confirmed runtime exception.

**Next efficient action:** Instrument or decisively isolate the common opening chain before producing another normal HUD hotfix:
1. Verify installed candidate SHA, effective resource ownership and input bindings read-only. Installation was user-reported but not independently inspected here.
2. Compare complete v3/v4/RC1 GFx trees and script/export setup, including HUD root, shared panel_common / panel_overlay initialization, and I&I hud_iteminfo. Test whether footer initialization can abort OnConfigUI before input-listener registration.
3. Prefer a small private trace build logging checkpoints: native/shared HUD readiness; radial GFx configUI/OnConfigUI completion; native OnRadialMenu entry and gate outcome; ShowRadialMenu and ShowElementFromState. Guard logging and give a reproducible path to retrieve evidence after pressing Tab/LB. Do not equate absence of a sound with proof of a specific failing function.
4. If tracing is infeasible, try ONE pinned, coherent, complete v3 radial movie isolation while retaining v4 iteminfo/colors and other accepted resources. This differs from RC1's bytecode-only isolation and can discriminate non-ABC radial resource effects. Avoid multiple blind variants.
5. Fix the established cause with I&I quickslots and accepted v4 palette, geometry, warning and smaller letters preserved; run offline checks and require real Tab/LB runtime verification before calling it fixed.

**Release status: RC1 rejected as a functional fix, but remains a reproducible diagnostic.** Its smaller-letter change may be reused. Do not rewrite the original static RC1 manifest or immutable ZIP hash.
