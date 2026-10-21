# 101 — Finite visual context diagnostic ready for an optional manual smoke test

2026-10-21. The user supplied report100 witness output: **Observed**, installed DX12 `witcher3.exe`, `DebugScriptsSubstringPresent: true`, then authorized proceeding. This establishes actual argument delivery for that observed process, not native logger activation or a fresh same-run logfile check. Given the two negative logger probes, this task prepares the bounded visual alternative rather than more undocumented logger toggles.

## Implementation and scope

Original source: `src/diagnostics/wmcVisualSmoke.ws`. Separate from the unchanged log observer. One `@wrapMethod(CR4Game)` on `OnAfterLoadingScreenGameStart` calls `wrappedMethod()` exactly once and schedules a short player timer. No polling until a save has loaded; **nothing is expected at the main menu**.

At most two notification calls per `CR4Game` instance:

1. `WMCVIS1 begin - diagnostic active` (4-second display).
2. `WMCVIS1 snapshot | region=… | state=… | combat=… | night=… | travel=… | owner/outro=unknown` (12-second display).

The first is attempted after three timer ticks and availability checks. The second is at least seven further timer ticks later. Pause, dialogue/cutscene and loading-video conditions defer presentation. Missing dependencies also defer it. Each wait has a finite counter; resetting that counter once after the first message bounds the whole attempt to at most58 one-second timer callbacks. Timers may pause with the game; this is **not** a wall-clock guarantee. Subsequent load callbacks can retry an unfinished attempt; after two calls they do nothing. Fields are unsaved; no cross-session persistence is claimed.

Bindings verified against installed sources under `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts`:

| API | Source |
|---|---|
| `CR4Game.OnAfterLoadingScreenGameStart` | `game/r4Game.ws:834` |
| `GetGuiManager(): CR4GuiManager` | `game/r4Game.ws:232` |
| `CR4GuiManager.ShowNotification(string, optional float, optional bool)` | `game/gui/r4guimanager.ws:1389–1406`; existing/new OverlayPopup handling |
| Region, logical State, combat, night, travel, scene/pause/loading-video queries | Exact original bindings already catalogued in report94's source table; same queries reused here |

The snapshot is a small visual liveness/API observation, **not** a timeline, discovery observer, authored-owner signal, outro-completion acknowledgement or safe audio request. It does not enable eligibility in report92's policy. It contains no coordinates, quest/location names, probabilities, music setters or file writes. Unsafe Stinger remains rejected and disconnected.

## Compilation and evidence

`python tools/visual_smoke_build.py --root build/<fresh-isolated-directory>` reuses the established compiler-preparation and compile helpers. Copies complete pristine REDkit script context and private compiler runtime; no installed source/config is edited. Builds baseline, constant-payload matched control and candidate. Packages only after compile, exact control-diagnostic and installed-input hash gates pass. ZIP readback must contain exactly the original diagnostic source.

First attempt, retained at `build/visual-smoke-v1/`, failed with `Left hand side is const` on field assignments through global `theGame`/`thePlayer` receivers. No package was produced. Corrected source performs assignments inside methods on the owning object. A delayed begin also resets the local timer counter so the snapshot cannot immediately replace it.

Accepted build evidence: `build/visual-smoke-v2/visual-proof.json`, individual `.result.json`, `.full.log`, `.stdout.log` and script blobs; sanitized summary: [101-visual-smoke-compile-evidence.json](101-visual-smoke-compile-evidence.json).

| Check | Pristine baseline | Matched control | Candidate |
|---|---:|---:|---:|
| Native compiler exit / blob produced | 0 / yes | 0 / yes | 0 / yes |
| Script / WCC errors | 0 / 0 | 0 / 0 | 0 / 0 |
| Native assertions | 20,893 | 20,897 | 20,897 |
| Warnings | 784 | 784 | 784 |
| Other native Core / Engine errors | 15 / 3 | 15 / 3 | 15 / 3 |

Candidate/control **complete diagnostic counters match exactly**. Native assertions/warnings/errors are retained, not concealed as a clean engine startup. All pinned installed inputs hash unchanged. No task-owned compiler remains running. The original observer and soundtrack artifacts were not changed.

Four new focused tests cover constant-control equivalence, finite/no-audio source constraints, exact one-source ZIP readback and refusal to package unexplained diagnostic differences. **All305 repository tests pass** in this run (`build/visual-smoke-v2/tests.txt`). This does not rewrite report100's historical failed run. Initial targeted test invocation used the wrong module search root; the corrected `unittest discover -s tools` invocation passes.

## Package and compatibility limits

Private manual archive:

`C:\Dev\witcher-music-control\build\visual-smoke-v2\manual\WMC Visual Smoke - Diagnostic.zip`

SHA256: `7d7215b4bf5eea0fc025802ccb1fb379312a4f74ed6f2c063c96ecbf427f6dfc`

Only member: `modWMCVisualSmoke/content/scripts/local/wmcVisualSmoke.ws`

Source SHA256: `4df1b9b7d83b653ab2ef56c9535ef492ad6868bad5a85361ace51e32a15dc81b`

No compiled blob, native source, configuration, bank, audio or licence is distributed in it. No existing music package needs disabling. The diagnostic has no overlapping sound cache.

Read-only installed-mod scan found no existing `WMCVisualSmoke` identifiers, but did find the callback in merged/FriendlyHUD game source and annotation wrappers in `modMonsterHuntContracts/.../mhcIntroduction.ws:186–193` and `modzzz_sharedutils/.../annotations.ws:25–29`. Wrapper composition is preferable to a replacement; **the complete enabled-mod assembly has not been compiled here**. Pristine REDkit compilation proves API/type resolution in that context only. If retail compilation reports a conflict, stop and report it; do not overwrite merges or change priorities to force it through.

## One optional user-operated test, and rollback

The diagnostic is **ready to install for a bounded manual smoke test**, not runtime-proven. This preparation does not install it or authorize automatic launch.

1. With the game closed, use Vortex **Install From File** for the exact ZIP above; enable only this new diagnostic, keeping the existing music setup and mod priorities unchanged. Do **not** install the earlier context-log observer alongside it. Intended installed file is `Mods/modWMCVisualSmoke/content/scripts/local/wmcVisualSmoke.ws` with no extra directory layer. Review deployment and stop on unexpected conflicts.
2. Launch normally. If script compilation fails, stop, disable the diagnostic and share the error. Otherwise load an **existing save in your current region**, remain stationary outside dialogue, and allow roughly30 unpaused seconds. No special arguments, INI changes, quests, travel, progression or new save are required. Main-menu-only testing cannot trigger this post-load diagnostic.
3. Capture the `WMCVIS1` marker and snapshot if shown. If neither appears, report that exact observation; it is not proof every context API is broken. Exit without deliberately saving or progressing. Normal game autosave behavior is not controlled by this script; if zero save writes are required, defer the test until save isolation is separately approved.
4. With the game closed, disable/remove **only WMC Visual Smoke** in Vortex and deploy that removal. Do not remove or reorder the working music mod. No logger/graphics configuration restoration is performed by this package.

Return the snapshot (or compilation/no-message result). That is the next decision point. No full observer/controller, Wwise changes or further deployment follows automatically.
