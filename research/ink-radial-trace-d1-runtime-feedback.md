# Radial trace D1 — first actual in-game findings

**15 October 2026.** Two in-game screenshots supplied by user. **This runtime evidence supersedes D1's earlier statement that the stopping point was unknown.** The user asks whether it gives a clear picture of what is going wrong. Screenshot pixels remain in the chat, not this public Git repository. No generated package or immutable manifest has been changed.

## Direct observations from the trace screenshots

Shared core lines (screenshot transcription):
```text
QFR TRACE D1 (diagnostic, not a fix)
FAULT AS hud footer layout ReferenceError: Error #1065
FAULT AS hud radialmenu configUI ReferenceError: Error #1065
AS hud createButton enter
AS hud renderer provider=hud
FAULT AS hud footer layout ReferenceError: Error #1065
WS radial status configEnter=false configDone=false shown=false
WS input RadialMenu pressed (independent monitor)
WS radial status configEnter=false configDone=false shown=false
```

The screens also show repeated `AS hud SetupGamepadIcon enter/exit` and `AS hud HintButton alignIcons enter/exit`. The same footer layout fault occurs both before and after some setup messages. The separate native input monitor receives RadialMenu action presses, but the radial's own native OnConfigUI entry/completion flags remain false. No `OnRadialMenu`, `ShowRadialMenu` or `OnRadialOpened` checkpoint appears in the displayed lines. The second screenshot shows the same faults and `configEnter=false configDone=false shown=false` before input.

**High-confidence causal chain:** Shared HUD footer layout throws `ReferenceError #1065` while radial `configUI` prepares prompt controls; the exception propagates/aborts that method before the native `OnConfigUI` event that normally registers radial listeners. Physical Tab/LB input dispatch still works (independent monitor sees the action). Consequently the regular handler never receives the action and the wheel stays closed. This is much stronger evidence than previous load-order, button sprite and input-binding guesses.

**Important distinctions:** The exact missing/unresolved ActionScript name/property behind #1065 is **not** present in the ledger; do not pretend it is known. A standard `ReferenceError #1065` denotes name/variable resolution, and is not proof of the previous `_gpadIcon.visible` null-dereference theory (which normally raises a different error). A fault at `hud footer layout` is more specifically within `ModuleInputFeedback.repositionButtons` than an arbitrary radial show/hide animation. `renderer provider=hud` indicates the active InputFeedbackButton comes from the shared HUD provider. The D1 repo's ApplicationDomain.currentDomain loading makes class provider/source ownership material. RC1 swapped only local radial DoABC, so it need not affect a shared/root `ModuleInputFeedback` class.

## Most relevant v4 source edit

`tools/polish-hud-layout.py::footer` modifies `ModuleInputFeedback` by increasing `BUTTONS_PADDING` 15→20 and injecting before the alignment switch:
```actionscript
this._canvas.scaleX = this._canvas.scaleY =
   this._cachedWidth > 0 && buttonsSize > this._cachedWidth
     ? this._cachedWidth / buttonsSize : 1;
buttonsSize *= this._canvas.scaleX;
```
This new canvas-fit logic is a prime **candidate**, not yet a confirmed exact #1065 expression. Verify compiled `repositionButtons` source/bytecode, actual variable and symbol resolution, and the earlier working v3 version rather than guessing that a particular identifier is absent. InputFeedbackButton's null-safe guard is a separate issue and not demonstrated as the current fault.

## Minimum next fix / proof strategy

1. Inspect **the actual loaded shared HUD `ModuleInputFeedback.repositionButtons`** and compare exact v3→v4 differences. Establish which compiled method/provider throws; use a temporary checkpoint around the new scale/fit expression or guarded `getStackTrace()`, including the unresolved QName if recoverable. Error #1065 alone does not identify the symbol.
2. Prefer the smallest **shared HUD footer-only** revert (e.g. remove only new v4 canvas-fit math, preserve style, glyphs and size, spacing and unaffected layout). Build one pinned, private coherent test ZIP that leaves I&I iteminfo, radial resource/code, and v4 enemyfocus exact. Avoid swapping out accepted quickslots or changing load order.
3. Runtime-check whether (a) the footer no longer faults, (b) radial `OnConfigUI` enters and completes, (c) the actual handler receives Tab and LB, (d) the wheel opens, sign selection works and close returns input/time normally. Verify footer long-label fit and other visible prompts after any layout rollback.
4. Once confirmed, rebuild a clean nondiagnostic hotfix and retain the RC1 small A/B/X/Y lettering, accepted glyph outer dimensions, enemy palette `#B94A40` / `#D9695A` / `#C77D6E`, 179-alpha attack warning, I&I quickslots and all other accepted v4 resources. Do not call it resolved before that runtime observation.

**Diagnostic conclusion:** The footer layout exception is **confirmed**; that it interrupts radial config is strongly supported by trace ordering and config flags. The exact opcode/expression causing #1065 remains to be isolated.
