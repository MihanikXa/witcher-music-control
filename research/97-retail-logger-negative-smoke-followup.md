# 97 — Negative main-menu logger smoke test: isolate actual activation failure

2026-10-20. **User-reported outcome:** "The logger main-menu test produced no scriptslog.txt." This follows report96's **manual DX12 main-menu only native logger probe**, which staged changes to \`bin/config/base/general.ini\` to request the native \`LogChannel\` file logger. The user did not provide a runtime log, screenshots, actual file hashes, CLI output, launcher executable evidence or confirmation of config restoration. **Do not infer** that there was no file anywhere, that \`LogChannel\` is permanently disabled, that the source observer was tested, or that the startup guard alone caused it. The observer was **not installed** for this smoke test.

The assistant advised **restore original \`general.ini\` if not already done, do not install the observer and do not launch the game again until a new evidence-based test exists**. This is a narrow operational checkpoint; report96 and its local offline authoring proof are otherwise unmodified.

## Known original experiment and evidence (report96)

- Original \`C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\config\base\general.ini\` (30 bytes) SHA256 \`a9750eeabb62948d661a3ec785c82919eb4075dad9de6e35aaf9a4a1bc9f86b2\`.
- Staged \`general.ini\` SHA256 \`ec0f09b06fd74984017ad27acbc3564705d0244c7af388e6415f9267a2ecfa4f\`. It appended \`[Scripts]\`, \`LogDebugScripts=true\`, \`DebugScriptsForceFlush=true\`, \`DebugScriptsLogDir=C:/Dev/witcher-music-control/build/sparse-interface-prerequisites-v1/retail-logs/\`.
- Target file \`C:\Dev\witcher-music-control\build\sparse-interface-prerequisites-v1\retail-logs\scriptslog.txt\`. A fresh log was expected to include \`Debugging scripts for \`; no \`WMCCTX1\` lines were expected because the observer was not installed.
- Report96 **static DX12 executable disassembly**, SHA256 \`2df765398a3d1f165db418271be7200178320a4466817379f2fa0dc0001fb101\`, found the script \`LogChannel\` registration, no-op initial callback, conditional startup rebinding to a native file callback, the \`Scripts\` config keys, append-path to \`scriptslog.txt\` and fopen mode \`w\`. Native logger initializer at RVA \`0x2287e60\`, assignment to callback at \`0x2287e95\`, called at \`0x2286703\`. The initializer skips on engine-global byte at \`+0x17c\` being nonzero; this byte's identity/value was **not established**. This static chain proves one possible mechanism but not actual activation or config delivery. See \`tools/observer_native_log_audit.py\` and \`research/96-interface-prerequisites-results.md\`.
- Observer compilation remains report94's pristine-script result, not full merged-mod or retail evidence. Its unchanged source-only diagnostic ZIP is not yet capture-ready. Report96's Trigger/MusicStinger does start S04-a but fails combat/outro ownership and cancellation, therefore is **rejected** as a protected cue-request gateway; do not let logger triage accidentally resume or install it.

## Next Codex task: *read-only diagnostic investigation first*, no random repeat gameplay test

Goal: determine which **specific source-verified preconditions** must be true for this retail build to write the file and where the file *actually* goes, then recommend **one bounded discriminating test only if necessary**.

### 1. Reconstruct actual configuration provenance and precedence

Using native DX12 executable disassembly and the installed on-disk configuration files as **read-only data**, trace:
- How \`Scripts/LogDebugScripts\`, \`DebugScriptsForceFlush\`, and \`DebugScriptsLogDir\` get bound, read, overridden, or ignored; identify exact consumer(s), constructor/default, config load timing, precedence of \`bin/config/base/general.ini\` vs user settings/other INIs and possible DX12-vs-DX11 paths. A constructor with a default true value alone does **not** prove the runtime guard.
- Whether the staged \`general.ini\` syntax/group can be parsed by the installed config loader at the logger-init moment. Distinguish proven config parser behavior from mere string matches.
- Whether the field and path ever influence the verified logger initialization; whether empty directory falls back, whether the slash/style is interpreted correctly, whether directories are created or must preexist, whether denied path/write access suppresses startup or only file-open, and where the *default* log would be written. Do not claim a guessed Documents or game-root path.
- Trace engine-global \`+0x17c\` provenance and **every relevant assignment/use**, giving disassembly addresses and confidence. Do not equate \`IsFinalBuild()\` or \`-debugscripts\` strings with this byte without actual data flow.

### 2. Check actual local read-only installation state

- Recheck the **present** SHA256 of installed \`general.ini\` to see if original was restored, without changing it. If it differs from expected original or staged SHA, record only drift and ask before suggesting a merge, never overwrite.
- Read known installed release/launcher metadata (DX12 exe version/hash, DX11 path if relevant). Do not assume which executable user launched; derive if any running/last-launch artifact can establish it **without looking at private saves, browser/account data or user activity logs**, or mark unknown.
- Check whether a fresh \`scriptslog.txt\` exists in the explicitly configured test folder or **one or two source-derived alternative candidate directories**, with timestamps and *header-only* check. No broad system scans, no printing other mods' logs or contents, no process attachment/monitor injection.
- Audit \`build/sparse-interface-prerequisites-v1/manual-logger-probe\` and any smoke checker outputs if present; do not invent terminal output or file evidence.

### 3. Provide a decision tree, not blind toggles

Possible outcomes:
- **Proven config wasn't loaded**: explain actual source-derived expected config origin and prepare **non-installed** staged alternative + byte-preserving backup and hash/preflight, then ask user to approve a tiny second main-menu test.
- **Configured output path differs**: report true native path resolution and prepare a read-only checker for that path; avoid replay if a fresh file is already present.
- **Initialization is gated off on retail**: identify exact guarded condition, reject untrusted bypasses/flags, and evaluate a *separately verified, non-invasive* diagnostic sink option. Prefer supported in-game/public APIs, not game executable patches, injected DLLs, arbitrary debuggers or global game overrides.
- **Mechanism remains uncertain**: disclose what code proves and doesn't prove; propose at most one discriminating, safe and user-operated main-menu test with an exact expected marker, bounded stop, rollback and no observer install, **or say no safe probe exists**.

Do not bypass or patch the engine guard, hook/inject into the retail executable, install third-party logging tools, modify installed config/files, launch the game, switch Vortex, deploy the observer, alter saves, run private gameplay, or add audio/script calls. No new full Wwise experiment is part of this checkpoint.

### 4. Result and stop condition

Commit original read-only inspection tooling/tests only if needed, plus a concise numbered result report \`research/98-native-logger-runtime-activation-results.md\` (or next free), sanitized evidence and a **precise next user action**. Keep full executable disassembly, raw private logs/config copies and user-specific paths or telemetry in ignored \`build/native-logger-activation-v1/\`. In Git, cite known source IDs, important RVAs and SHA256, not copyrighted binary/code dumps or private runtime logs.

Do not claim that the reported absence of the configured file proves \`LogChannel\` has no retail sink. The goal is to distinguish: **configuration not read, wrong output path, logger initialization disabled, or an unresolved condition**.

**Stop before another user gameplay test.** Ask the user only for the minimal action that the source audit can justify. Report tests/pass counts as run, not assumed.
