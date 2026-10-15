# HUD v4 Hotfix RC2 — shared footer correction

15 October 2026. **Implemented source correction; in-game acceptance pending.**
One clean replacement package, no new diagnostic variant or gameplay/script edits.

## Exact defect and minimal correction

The freshly extracted installed D1 HUD root matches its receipt exactly:
`01b86101bdac12fa6cc15f032159059d133282798f65d43b6d36ea64da1ebe9d`.
All 23 deployed logical resources match D1. Current effective HUD owner is
`modInkIronHUDRefinementV4`, priority **30**; preserve the actual existing order.
The prior D1 build-time 31 slot was an older snapshot. No priority was changed.

D1's runtime `FAULT AS hud footer layout` label originates in the root movie's
instrumented ModuleInputFeedback, and `renderer provider=hud` identifies its
InputFeedbackButton. Hud.configUI preloads ModuleInputFeedback and loads module
movies with ApplicationDomain.currentDomain. This is the shared provider used
while radial configUI builds its footer, rather than the radial-local class
whose bytecode RC1 had restored. Runtime presses reach the independent monitor,
but radial's native config flags remain false.

The actual installed ModuleInputFeedback.repositionButtons declares its total
width as `_loc3_`. The v4 addition instead contains:

```actionscript
this._canvas.scaleX = this._canvas.scaleY =
    this._cachedWidth > 0 && buttonsSize > this._cachedWidth
      ? this._cachedWidth / buttonsSize : 1;
buttonsSize *= this._canvas.scaleX;
```

**`buttonsSize` is not a declared local or member.** Actual FFDec P-code contains
three `getlex Multiname("buttonsSize", ...)` instructions plus `findproperty`
and `setproperty` for that name, instead of local-register reads/writes. The
conditional can attempt the missing lookup when cached width is positive; the
second statement attempts it unconditionally. The class export contains no
binding for that name. This is a real lexical-resolution defect, not the earlier
null-reference hypothesis. D1's observed #1065 in this exact method and its
propagation into radial configUI now have a concrete source/bytecode explanation.
The screenshots do not provide the exact runtime program counter; none is claimed.

Radial configUI constructs/configures its footer before dispatching OnConfigUI.
The exception aborts that dispatch, so native OnConfigUI cannot register the
ordinary radial input listeners. Restoring only radial-local DoABC in RC1 did
not repair the shared/root provider. This explains why both Tab and LB can reach
the independent monitor while the actual wheel handler remains unregistered.

The prepared `repair-ink-hud-footer.py` matches the real compiled source exactly.
RC2 applies it only to **ModuleInputFeedback in hud.redswf**, using the clean RC1
movie as the baseline. It removes those two statements, with no catch/suppression,
forced opening, binding change, or replacement of other HUD resources. The compiled
footer method is **exactly the working v3 method**, and its surrounding class
retains v4's accepted BUTTONS_PADDING=20 (v3 used 15). Alignment, glyph size, label
metrics, hold behavior and current button rendering are otherwise unchanged.
No new resolution-fit substitute is introduced. Very long/localized footer
strings must still be checked in-game; the removed fitting code never worked.

## Preserved bytes and scope

Only `gameplay/gui_new/swf/hud/hud.redswf` changes versus RC1. All other **22 logical
resources** are byte-identical, including radial, iteminfo, enemyfocus and bossfocus.
Within the changed root movie, every non-ABC definition, glyph shape, font,
SymbolClass, placement and texture tail is exact RC1. Re-exporting every class
shows that only ModuleInputFeedback.as differs, and its entire source differs by
exactly the two removed statements. Existing method/accessor declarations and
Hud/Outfit Wheel inheritance/export signatures are retained.

This preserves the exact accepted reds (#B94A40 / #D9695A / #C77D6E), attack-warning
alpha, nameplate geometry, I&I quickslots, smaller RC1 A/B/X/Y interiors, outer
button sizes, dialogue, shadows, SAHUD/FriendlyHUD and other compatibility support.
All existing RC1 ZIP members outside the root bundle/metadata pair are exact.
D1's diagnostic script, observers, ledger and instrumented movies are absent.

Input provenance is the installed personal I&I/OW/compatibility stack, RC1 and
working v3. Third-party resources/derivatives remain private and gitignored;
only original tooling, tests and non-asset evidence are committed. Author assets
are not redistributed. No game, settings, staging/profile, save or merge output
is modified. Old v4, RC1 and D1 archives remain intact.

## Reproduce

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/build-ink-hud-footer-hotfix.py --out build/ink-hud-v4-hotfix-rc2-footer --deploy deploy/ink-hud-v4-hotfix-rc2
& $py -m unittest discover -s tests -p 'test_ink*.py'
```

Use fresh ignored output directories. The builder pins installed D1 inputs and
immutable RC1 inputs, exports/recompiles/re-exports the one class, checks actual
P-code, and requires equality with the working v3 method. Successful exact-source
WitcherScript controls are reused only after rechecking their provider/input and
compiled-blob hashes; no WitcherScript changes are made. Opaque mod dependencies
are outside source recompilation. Native stages have one bounded 90-second
attempt each; no repeated blind startup retries. Any reconstruction is explicitly
recorded separately from native success. Local logs/exports/receipt stay under
the selected build directory. Public hashes and stage results are in
`research/ink-hud-v4-hotfix-rc2-manifest.json`.

## Install and runtime acceptance

1. Exit the game completely. In the isolated test profile, disable/remove D1 and
   replace it with the RC2 ZIP. It deliberately uses the same
   `modInkIronHUDRefinementV4` folder. Do not stack v4, RC1, D1 and RC2. Preserve
   the existing priority/rules and aliases; do not regenerate Script Merger or
   menu registration. Verify no residual `inkRadialDiagnostic.ws` remains from
   D1's package through Vortex's file/deployment view.
2. Restart, load the usual Geralt test save outside dialogue/cutscene, wait for
   HUD setup. The diagnostic ledger is intentionally gone. Offline removal of
   the bad lexical references is established; runtime absence of #1065 and native
   listener registration must not be claimed merely from successful cooking.
3. Press **Tab**, select Axii and another sign with mouse/keyboard, close, check
   gameplay input/time, and repeat. Then test **LB**, analog selection, closing
   and repeat independently. Opening/selection is the functional evidence that
   initialization and the ordinary listener path complete.
4. Repeat after a normal menu transition and combat. Check the restored I&I
   quickslots, hints and switching; ordinary footer Select/Back, hold descriptions
   and LT/RT tabs; long labels at the user's normal resolution/UI scale.
5. Check the accepted enemy reds/geometry/warning, player/boss bars and text
   presentation. These resources are exact RC1 bytes, but runtime remains the
   final acceptance gate. Do not create campaign saves just for this test.
6. Report separately whether Tab opens, LB opens, Axii/other signs select, closing
   restores input/time, and whether footer fit/alignment remains acceptable.
   If either input still fails, report the observable response; do not reorder mods.

## Rollback

Exit the game. Disable/remove RC2 and reinstall the preserved RC1 ZIP in the same
slot; do not stack them. RC1 is the accepted visual baseline (with its known wheel
failure), and original v4 is also preserved. D1 can be restored solely to recover
its existing trace if needed. No save migration, settings reset or merge rebuild
is involved. The only logical resource altered by RC2 is the shared HUD root;
whole-package replacement keeps the matching bundle/metadata pair coherent.

## Build results

Private ZIP:
`C:\Dev\witcher-ui-overhaul\deploy\ink-hud-v4-hotfix-rc2\Ink-Iron-HUD-v4-Hotfix-RC2-footer-private-test.zip`
(10,995,164 bytes). SHA-256:

`9cbc759c9002f11af32d43d69566ef6563fc66dfd1a2939cab23878777aa46c3`

**All native stages passed:** cook, validate (22 resources, zero resource errors),
pack and metadatastore exited 0. Cooked bytes equal their prepared inputs. All 22
native packaged resources re-extract exactly, and metadata contains their keys.
The alias-only XML remains in its original separate alias bundle; native packing
uses only the 22 movie inputs. **No bundle or metadata reconstruction was used.**
The two established depot-path/sound-bank startup assertions are present and
explicitly retained in the manifest; these are not new resource-validation errors.
Native logs and per-stage command lines/hashes are retained locally.

**90 regression tests pass.** New tests cover the actual installed unresolved
lexical bytecode, its absence from RC2, exact equality to the working v3 method,
retention of 20-pixel spacing, all other class-source equality, and preservation
of every RC1 ZIP support member and unaffected resource. Root class-contract
checks retain 3,580 method/accessor declarations. ZIP CRC/extraction and two
identical deterministic ZIP generations pass. The public manifest records exact
resource, package, source and native-log hashes. Runtime wheel operation through
Tab/LB, sign selection and footer fit remain **unverified until the user's test**.
