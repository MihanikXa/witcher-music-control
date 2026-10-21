# 100 — Verify the final game process before another logger diagnosis

2026-10-21. Read-only follow-up to report99. **The next discriminating measurement is actual game argv, not another blind logger test.** No game, Vortex, configuration, save, observer or audio changes were made. Main was fetched and matched origin/main before work.

## Observed local state

- Installed `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\config\base\general.ini` is currently the **staged** logger configuration: SHA256 `ec0f09b06fd74984017ad27acbc3564705d0244c7af388e6415f9267a2ecfa4f`, not the original 30-byte file. Lines6–8 enable logging/flush and specify the report96 private build folder. It was left untouched. This establishes current disk state, not what the second launch read.
- `build/sparse-interface-prerequisites-v1/retail-logs/` exists. ACL metadata includes inherited allow/Modify entries; this is **not a successful effective-token write test**. No test file was created.
- Neither `scriptslog.txt` in that configured folder nor the single Windows-resolved Documents application candidate exists. No broad file search was performed. The exact runtime default suffix and effective CVar/user-store precedence remain qualified as in report98.
- Both known user-settings files still have an **empty** `DebugScriptsLogDir`; no keys were removed. DX11's expected executable remains absent. The read-only process witness returned **NotRunning**, so no actual argv was observed.

Reproduction: `python tools/native_logger_activation_audit.py --output build/<fresh-output>.json`. Sanitized snapshot: [100-logger-argv-evidence.json](100-logger-argv-evidence.json). Native constructor and file callback findings remain those of reports96/98; no unrelated executable analysis was repeated.

## What installed Vortex actually implements

Installed Vortex executable FileVersion is2.9.0; bundled Witcher extension is1.7.5. Inspected **current installed** `C:\Program Files\Vortex\resources\app.asar.unpacked\bundledPlugins\game-witcher3\index.cjs.map` (SHA in evidence), not merely the report23 retained copy. Relevant original sources were extracted as data into ignored `build/logger-argv-witness-v1/vortex-source/`; no bundled code was executed.

| Source inside installed package | Verified behavior |
|---|---|
| Extension `index.ts:85–103` | Separate DX11 and DX12 tools; DX12 executable is `bin/x64_DX12/witcher3.exe`. |
| Extension `edition.ts:107–108`, `util.ts:340–351` | Default executable resolution prefers existing DX12, otherwise DX11. |
| Extension `index.ts:204–234` | Game registration uses that resolver. No `requiresLauncher` is declared here; Steam app metadata is not itself a launcher requirement. |
| `C:\Program Files\Vortex\resources\app.asar`, `/renderer.js.map`, `src/util/StarterInfo.ts:488–510` | Main game uses `gameDiscovery.parameters`; a tool uses its own `toolDiscovery.parameters` (with respective defaults). Editing one entry does not establish the other entry's parameters. |
| Same core source `:135–136, 289–295, 383–395` | Direct path passes `info.exePath, info.commandLine` to `api.runExecutable`. A required-launcher path calls the launcher's `launchGame(infoObj, api)` instead; no equivalent unconditional argument forwarding is shown there. |

**Inference:** this extension's ordinary default is direct executable launch, not an obligatory REDlauncher hop. **Not established:** the entry actually clicked, current user overrides, downstream launch hooks, or final child argv in either failed run. Current per-entry state is in Vortex's private LevelDB; it was not opened with a writable database API, copied wholesale, or exported. Static default code is not a substitute for the final-process witness.

## One-shot privacy-filtered witness

[`tools/Get-WmcGameArguments.ps1`](../tools/Get-WmcGameArguments.ps1) issues only:

```powershell
Get-CimInstance -ClassName Win32_Process -Filter "Name='witcher3.exe'" -ErrorAction Stop
```

It emits a status plus **only executable path and nullable flag boolean per matching game process**. No full argv, PID, parent process, other processes, exception text or disk log is emitted. Detection deliberately matches report98's native **case-sensitive substring** search; it does not pretend to validate token syntax. A null/unreadable command line means unknown, never false. Multiple processes are explicitly ambiguous. The script neither launches nor changes anything.

Six regression tests exercise the actual PowerShell function with mocked CIM responses: exact scope, privacy, case/substrings, absent process, unreadable fields, sanitized errors and multiple games. A real one-shot read returned NotRunning. This is not evidence of flag delivery.

## Fallback decision

The conditional prerequisite **“logging fails despite verified actual arguments” has not been met**. Consequently no new diagnostic was compiled, packaged or installed in this task. This is a deliberate conditional deferral, not a claim that the existing observer is capture-ready.

The bounded alternative remains source-supported: installed `content/content0/scripts/game/gui/r4guimanager.ws:1389–1406`, `CR4GuiManager.ShowNotification(messageText:string, optional duration:float, optional queue:bool):void`, creates notification data/requests OverlayPopup or forwards to its existing popup. If actual argv is confirmed and the sink still fails, the next implementation is a separate two-message, finite liveness/snapshot diagnostic, compiled in pristine and matched-control contexts before any opt-in installation. It would provide visual evidence, **not** the replayable machine-readable context stream. No native file-writer or safe Wwise request gateway is asserted. The rejected Stinger stays disconnected.

## Validation outcome

The six new PowerShell-backed regression tests pass. Full repository discovery ran301 tests: **23 errors**:21 NumPy allocation failures in existing audio tests (including1–3MiB allocations), plus two PowerShell subprocess nonzero exits in the new witness tests. Those six witness tests passed in the earlier standalone run; their two full-suite subprocess errors are not explained by that pass and remain recorded. No assertion failures. The full suite therefore did **not** pass. Private complete output is retained at `build/logger-argv-witness-v1/tests.txt`. No audio/DSP implementation was changed to hide these environment failures.

## Exactly one next user action

**During your next user-operated Vortex launch, stay at the main menu and run the following in PowerShell, then send its small JSON result:**

```powershell
powershell.exe -NoProfile -File "C:\Dev\witcher-music-control\tools\Get-WmcGameArguments.ps1"
```

No save load or observer installation is needed; do not change settings for this check. `Observed` plus the expected DX12 path and `true` proves the currently running final process contains the flag. `false` identifies argument delivery as a problem; `Unreadable`, `QueryFailed`, `NotRunning` or multiple processes are inconclusive. This is an argv-delivery measurement, not a request to repeat the earlier blind logfile experiment. If script execution is blocked, report that error rather than changing execution policy.

Stop for that result. Current staged INI is explicitly documented above; this task has not restored or changed it, the user's graphics settings, or the working music installation.
