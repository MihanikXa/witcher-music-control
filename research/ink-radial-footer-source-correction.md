# D1 confirmed footer exception — source-level correction candidate

**15 October 2026. Source correction prepared, NOT compiled/released/runtime-confirmed.**

Two in-game D1 screenshots show `FAULT AS hud footer layout ReferenceError: Error #1065`, propagated to `hud radialmenu configUI`; `configEnter=false configDone=false shown=false` despite independently observed RadialMenu action presses. The exact missing AVM2 symbol is not logged. See [D1 runtime evidence](ink-radial-trace-d1-runtime-feedback.md).

## Narrow correction

`tools/polish-hud-layout.py::footer` previously inserted:

```actionscript
this._canvas.scaleX = this._canvas.scaleY =
    this._cachedWidth > 0 && buttonsSize > this._cachedWidth
      ? this._cachedWidth / buttonsSize : 1;
buttonsSize *= this._canvas.scaleX;
```

This uses a name (`buttonsSize`) which the generator **never checks is a bound local** in the compiled `ModuleInputFeedback.repositionButtons` method. A runtime reference-resolution error is compatible with that, but this exact operand has **not yet been proven** as the #1065 target. V4 and RC1 already shipped with compiled code: editing their source generator alone cannot change deployed behavior.

I changed future generator output to **retain the original footer layout implementation**, keeping only the accepted 15→20 spacing change. Separately, `tools/repair-ink-hud-footer.py` provides a **fail-closed** source transform to strip precisely that two-statement v4 fit expression from a real FFDec-exported `ModuleInputFeedback.as`. It preserves the entire rest of the class byte-for-byte in source form. If FFDec renders the expression differently or it is absent, the tool raises an error rather than rewriting unrelated code.

The final-v4 `source_patches` list reflects a staged centering pass and does not necessarily list earlier compilation edits, so do **not** infer from that manifest alone that the fit code was absent from actual v4 bytes. Examine the decompiled effective provider class.

## Next local boundary (required)

1. On the local Windows checkout, verify the installed D1/RC1/accepted v4 resource winner and export **actual loaded HUD-root `ModuleInputFeedback.as`**, with its `repositionButtons` body, using FFDec. Only proceed with this candidate if the injected expression is present and the correct effective class is identified.
2. Use the helper against that class, outputting to ignored `build/` (no original asset overwritten). Diff source to prove **only** the two suspect statements disappeared. The shared HUD/root movie may be the active provider, as D1's `renderer provider=hud` suggests.
3. Recompile the one class into the working v4/RC1 HUD-root .redswf with the existing `compile_classes` path; verify DoABC-only change, unchanged glyphs/text/fonts/exports/placements, correct metadata and proper native cook/validate/pack with exact extraction. Use all original hash/contract gates. Avoid replacing radial art, iteminfo, enemyfocus, script mods, aliases or any game files.
4. Package one **private** one-mod hotfix retaining RC1's smaller A/B/X/Y letters and all accepted v4 I&I quickslots/reds/visuals. Do not stack full versions. Do not deploy automatically. Preserve explicit rollback to RC1.
5. In-game verification: footer no longer throws `#1065`, radial `OnConfigUI` enters/completes, both Tab and LB open the selection wheel, and sign selection/closing/time/movement work. Also test long menu-footer labels. If failure persists, instrument the exact expression/ABC stack before another modification.

**Scope/limitations:** Public Git contains only this original source tooling/test/research. No private SWF, third-party asset, REDkit binary or generated ZIP is available here. This static candidate is **not a proven runtime fix**; the installed user's private Windows resources are necessary to produce and test a game-ready package.
