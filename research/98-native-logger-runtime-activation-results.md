# 98 — Negative logger probe: native activation gate identified

2026-10-21; follows the user's negative main-menu result recorded20 October in report97. **No new retail launch, config edit, observer installation, Vortex/save action or Wwise run.**

**Result:** report96's INI-only instructions omitted a necessary native activation condition. The script-engine constructor derives the logger-disable field from a command-line search for **`-debugscripts`**. Setting `[Scripts]` keys alone cannot clear it. This is now actual instruction/data-flow evidence, not a string-name guess. Whether the user's failed run received that argument remains unknown; absence of one file does not establish permanent retail logging disablement.

Evidence: [sanitized audit](98-native-logger-activation-evidence.json), reproducer `tools/native_logger_activation_audit.py`; private disassembly/inventory under `build/native-logger-activation-v1/`. This supersedes the INI-only smoke-test recommendation in report96; do not repeat it.

## 1. Constructor → startup guard

All RVAs refer only to `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\witcher3.exe`, SHA-256 `2df765398a3d1f165db418271be7200178320a4466817379f2fa0dc0001fb101`, base `0x140000000`. Trusted installed Microsoft dumpbin used read-only; no process attachment or patch.

| Observed instruction/data flow | RVA |
|---|---|
| Engine constructor called; returned object assigned to global `0x5a7da70` | `0x1e7407d`, `0x1e74087` |
| Constructor initializes object's byte `+0x17c` to1 | `0x270f1ac` |
| Loads literal `-debugscripts` and searches the process command-line string using the reviewed narrow substring-search routine | `0x270f264`, call `0x270f26b` → `0x1a90014`; literal `0x3629800` |
| Missing substring → AL1; present → AL0; writes AL into **the same object's** `+0x17c` | `0x270f270–0x270f281` |
| Logger reads that global object's byte; nonzero branches past logger setup/file opening | `0x2287e64–0x2287e72` → `0x22880d9` |

**Verified interpretation:** a logging-disabled predicate, initially true, cleared by the native command-line substring. The search is case-sensitive substring matching, not a newly invented tokenized argument parser. Synthetic policy tests model these instructions; they do not run the game or inspect actual arguments. `IsFinalBuild()` is not the source of this field.

**Inference:** a normal launch following report96 without this argument would predictably skip the file logger regardless of the staged directory. **Unresolved:** which command line/executable actually ran in the user's test; no launch-history/account/activity logs were inspected. The expected local DX11 `bin/x64/witcher3.exe` is absent, but that alone does not prove the identity of a past process.

Core callback registration at `0x277aec0`, called at `0x270f281`, follows the field assignment unconditionally in this constructor. It must not be confused with proof that the flag starts a remote debugger. Conversely, this bounded trace is not a certification of every debugger/compiler side effect elsewhere. No flag was applied or tested.

## 2. Configuration provenance, precedence and timing

**Observed installed descriptor:** `...\bin\config\config_description.xml:3–10`, SHA `5b681e667f13fa3ce1704a29f887584f1eb70e02e03f5abaf6f7ad6f5c9be9eb`. Its PC order is code defaults → `base\` → `developer\` → `r4game\` → `platform\pc\`.

**Native source path:** boot builds the `config\` root and calls descriptor loading at `0x1e736aa` → `0x26e6090`; the loader reads `config_description.xml`/`OverrideOrder`/PC Set and ordered Path nodes. Enumeration at `0x1e736b2` → `0x26e67d0` builds `*.ini` requests and loops the configured directories (`0x26e696e`, `0x26e6b0a`). Each eligible INI goes to `0x2720560`, file-read success then generic content parser `0x2720a40`. These calls precede script-engine construction at `0x1e7407d` in the observed boot path. The filename `general.ini` is not a section-name restriction; it participates through the base-directory INI enumeration.

Thus `[Scripts]` in base/general.ini is a supported **input to the native layer**, and the registered report96 keys exist. It is not sufficient to activate the earlier constructor-controlled logger gate. The current21 INIs directly in these ordered PC directories contain **no** matching logger assignments. Native defaults/key registration must be distinguished from runtime activation.

**User-setting limit, explicitly retained:** both Windows-resolved Documents application files, `user.settings` and `dx12user.settings`, contain `DebugScriptsForceFlush=true` and **empty** `DebugScriptsLogDir`. Neither contains the probe directory. The executable also contains the `\dx12user.settings` suffix at `0x3201a00`. These observations do not by themselves prove when the user store overrides a bound native CVar at logger initialization. That part of effective-value precedence remains unresolved; no claim that an empty user value caused the failed test. I initially described these as matching probe leftovers; checking the actual values corrected that interpretation. **Do not delete them as presumed residue.**

## 3. Directory resolution and failure behavior

At `0x2287e78–0x2287ec3`, the initializer selects nonempty configured `DebugScriptsLogDir` storage, otherwise the path at `[global 0x5a5d970]+0x30`. At `0x1e73266–0x1e73276`, boot populates that field from its path-setup output. The ordinary Windows setup route `0x1e71520` uses `GetModuleFileNameW`/`GetFullPathNameW` and, for the relevant fifth output, **SHGetFolderPathW with CSIDL5** at `0x1e71967`, then formats Documents + the application-supplied directory at `0x1e71aff–0x1e71b35`. Failure of the Windows folder call takes a separate application-path fallback (`0x1e71bec` onward).

**Verified boundary:** the default is a constructed native application path, not an arbitrary working-directory guess. Windows Documents is redirected on this machine; its actual personal path remains private. Exact population of the application-name field and the actual runtime fallback result are not fully pinned. Therefore `Windows-resolved Documents/The Witcher 3/scriptslog.txt` was checked as **one source-guided candidate**, not labelled a runtime-confirmed default.

The file routine `0x2288250–0x22886b9` handles stdout/stderr special names; ordinary directory strings are normalized/appended with `scriptslog.txt`, then opened once in mode `w` at `0x2288669`. A null FILE result is stored at `0x2288688`; return is false (`0x22886ab`). There is no alternate-directory retry after this failure in the reviewed routine. The writer returns immediately on a null file pointer (`0x22880fe–0x2288108`). We found no directory-creation step in this path; pre-existing/writable directory is required. The initializer does not turn this failure into an observed user error. **No actual file-open error/permissions failure was captured.** Force-flush controls writing after open and cannot itself explain why no file was created.

## 4. Bounded local checks and restoration

- **Original general.ini restored:** current30-byte SHA `a9750eeabb62948d661a3ec785c82919eb4075dad9de6e35aaf9a4a1bc9f86b2`, exact original, distinct from staged `ec0f09...`. No modification performed.
- Configured `build/sparse-interface-prerequisites-v1/retail-logs/scriptslog.txt`: absent.
- One alternative, Windows-resolved Documents application candidate above: absent. No freshness/header result can be claimed for nonexistent files. No other personal-directory scan.
- No `smoke-check-*` output was present in the known probe root. No tool output was invented to supplement the user's report.
- Only relevant `[Scripts]` values were inspected in the two known settings files, not save files or unrelated settings/log text. No probe-directory residue found there; prior user values left alone.
- Observer source and original diagnostic ZIP still match report96 hashes, including ZIP `8cb59a83e77c328b2cd050c252411feefa21b8a257b0abd15d9a85f45ab16568`. No script adjustment/recompile or audio work was necessary.

## 5. Safe alternatives and next action

The native mechanism has a source-supported activation argument; retail effectiveness and full activation effects remain untested. Do not add it blindly to a launcher, patch the guard or repeat gameplay. The native stdout/stderr destinations are not an independently proven capture route for this GUI launch; OutputDebugString imports still do not establish message delivery.

A minimal **future visual liveness fallback** exists in installed script source: `content/content0/scripts/game/gui/r4guimanager.ws:1389–1406`, `ShowNotification`, routes text through `W3NotificationData`/`OverlayPopup`; `game/gui/popups/overlayPopup.ws:226` implements the popup side. A separately approved diagnostic could show one finite `WMCCTX1` marker, recorded manually by screenshot, without depending on the native file sink. This supports a limited liveness check, **not** a proven lossless machine-readable gameplay trace. It was not implemented, compiled or installed here. No supported arbitrary script-file writer/export bridge was established; saving messages into user configuration would violate this task's constraints.

**One recommended next user action:** tell us **which launcher was used for the failed DX12 test and whether its existing game arguments included `-debugscripts`**, without changing arguments or launching anything. This distinguishes the newly proven missing-prerequisite hypothesis before considering any further user-run probe. Keep the observer uninstalled. No other user action is requested now.

## Verification and stop

Original read-only audit and six targeted regressions added: literal byte scanning (including regex metacharacters), pinned-image rejection, constructor-gate model, substring semantics, safe descriptor paths/order and privacy-filtered empty/duplicate setting inspection. **Full repository suite:295 tests pass**; expected negative-gate diagnostics remain asserted tests. Raw disassembly/personal paths stay ignored; sanitized metadata and original tools only are committed. No installed config/game/Vortex/save change or retail launch. Unsafe MusicStinger remains rejected and disconnected. **Stop for review and launch-route information.**
