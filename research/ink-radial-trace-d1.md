# Radial opening trace D1 — one instrumented private package

**14 October 2026. Not a fix.** RC1 failed through both Tab and LB. D1 instruments
that failed installation instead of guessing another radial-button replacement.
The actual runtime stopping point remains unknown until its checkpoints are read.

## Verified starting point and narrowed findings

All 23 deployed logical resources were re-extracted: they match RC1 exactly.
The effective HUD owner is `modInkIronHUDRefinementV4`, priority **31**; aliases
are at **30** in the current settings. Preserve those existing slots. The previous
scan's 30/29 values were an earlier snapshot, not permission to reorder mods.
Bindings still map IK_Tab and IK_Pad_LeftShoulder to RadialMenu. No settings,
Vortex deployment, saves, merged outputs or reference packages were changed.

The actual loose-script owners are merged files (priority 2) for HUD/root and
radial, and FriendlyHUD (19) for iteminfo. All three texts match the previously
verified 5.01 compiler assembly exactly. Its other current provider hashes are
also pinned. Seven opaque compiled dependencies remain outside source recompilation.

The **complete tag-level movie comparison**, including non-ABC definitions,
shows:

| Movie | v3 → v4 GFx differences | v4 → RC1 GFx differences |
|---|---|---|
| HUD root | DoABC | none (glyph changes are in native atlas slots) |
| Radial | Shape3 and DoABC | Shape3 and DoABC |
| Iteminfo | Shape3 and DoABC | Shape3 |
| Common / overlay | Shape3 and DoABC | Shape3 |

Counts and payloads of other tag types—including sprites, placements, fonts,
imports and SymbolClass—are equal. Native texture tails do change for glyph
painting; they were compared separately, not silently treated as DoABC.
RC1 radial matches working v3's DoABC, sprites, placements and font/export
records but retains new shapes and atlas artwork. Thus the next useful evidence
is **initialization/dispatch**, not another unproven button-bytecode fix.

The HUD loads movies with **LoaderContext(false, ApplicationDomain.currentDomain)**.
Its startup also constructs bare InputFeedbackButton, HintButton, HudModuleBase,
W3ScrollingList and ModuleInputFeedback instances. Shared definitions already
loaded in the parent domain can affect renderer resolution; restoring one child
movie's bytecode does not prove its local definitions execute. D1 reports the
actual renderer provider when accessible, with a guarded fallback if an older
shared definition lacks the diagnostic method. It does not add a new missing-
method failure to the original initialization chain.

No source/runtime evidence yet proves that the unsafe nullable Xbox predicate,
a root constructor, a load error, an input gate or iteminfo is **the** cause.
The original optional quickslot annotation omission is still a configuration
mismatch, but its direct radial call is behind the disabled developer test flag.
D1 does not restore that unrelated script section or swap retail quickslots.

## What D1 observes

The failed RC1 resource is the base for all instrumentation. Three movie bytecode
payloads change: HUD root, radial and I&I iteminfo. **Every non-ABC definition and
native texture payload remains exact**, including the perfect buttons and 80%
A/B/X/Y lettering. Twenty logical resources remain byte-identical to RC1:
enemyfocus/colors/warning, bosses, minimap, common/overlay, other HUD and aliases.

- Root configUI entry/exit; before/after each bare class preload; module request,
  load completion and load errors. Original exceptions are logged and **rethrown**.
- Radial/iteminfo configUI; footer renderer construction/provider and layout;
  InputFeedbackButton construction/update/setup; radial ShowElementFromState
  requested visibility, block/stick flags and errors; iteminfo setRadialMenuOn.
- Native HUD/radial OnConfigUI entry/exit. Radial completion flags show whether
  its existing listener setup returned.
- A separate HUD observer for the same RadialMenu action reports presses even
  when the radial's own listener is absent. It returns **false**, does not open
  the wheel, change input context or consume the action. An earlier consuming
  handler may prevent later observers; absence alone is not a conclusive trace.
- Native OnRadialMenu press and existing early gates: already shown, action
  disallowed, dialogue/cutscene, blackscreen/fade and denied input.
- Native ShowRadialMenu entry/exit (m_shown), OnRadialOpened and radial state
  rendering. Original wrapped methods execute once with their original return.
- Two-second native status: module absent, or config-enter/config-complete/shown.
  Raw UI Tab/LB events are supplementary; gameplay input need not arrive as a
  Scaleform stage event, so their absence does not mean the physical input failed.

The on-screen **QFR TRACE D1** ledger is a mouse-disabled, non-selectable text
field attached to the **stage**, not the HUD. That preserves HUD child counts
used by CheckModulesDepth. It retains the latest 25 messages and pins up to five
faults. Constructor logging runs **after super()**; an exception in super is
instead caught by the root's surrounding preload checkpoint. Diagnostic reporting
errors are contained; original gameplay exceptions are not swallowed. Repeated
child setup messages are deduplicated to avoid frame-by-frame flooding.

The native script also calls existing LogChannel('GWINT_AI',...). Persistent
retail log output depends on the game's existing logging configuration. **No log
file is promised or logging setting enabled.** The primary retrievable output is
the on-screen ledger captured manually. If no ledger appears, that is diagnostic
failure/incomplete activation, not proof that the radial failed at a named step.

## Exact test and output retrieval

1. **Exit the game completely.** In the isolated test profile, replace/disable
   RC1 and install this one D1 ZIP. It deliberately uses the same
   modInkIronHUDRefinementV4 folder and existing 31 slot; keep aliases at 30 and
   every other rule/mod unchanged. Do not stack original v4, RC1 and D1. No
   menu registration or Script Merger regeneration is required.
2. Restart and load the usual Geralt test save outside a dialogue/cutscene.
   Do not create a campaign save while diagnosing. Wait 2–3 seconds.
3. **Before pressing anything**, capture a screenshot of the QFR TRACE D1 ledger
   and any pinned FAULT. This preserves setup output before later input messages.
4. Press **Tab once**, wait about a second, and capture another screenshot.
   Record whether the wheel, sound, slowdown or input capture occurs.
5. Press **LB once**, independently, and capture the resulting ledger. Repeat
   once only if necessary to read the last checkpoint. Do not change bindings.
6. Return these three captures (startup, Tab, LB), or transcribe all FAULT lines
   and the last checkpoint lines exactly. ShareX/ordinary screenshot capture is
   sufficient; no console command, native log setting or computer automation is
   needed. If the ledger is absent, report that and any game script-compilation
   error. Do not assume a lack of trace is a successful negative measurement.
7. If the wheel unexpectedly opens, check Axii/another sign, analog and mouse/
   keyboard selection, close/return of time and movement, and one repeat of each
   input. **Instrumentation changing timing is possible; do not call it fixed.**
8. Exit and restore RC1 after collecting evidence. Original v4 is also retained,
   but RC1 is the preferred visual rollback because its buttons are accepted.

Interpret the trace conservatively:

| Observation | What it narrows |
|---|---|
| Root preload FAULT with before but no after | Specific shared constructor failed |
| Request but loadError FAULT | Resource/loader path failure, URL/event shown |
| Radial configUI enter + FAULT, no native completion | Initialization aborted at named checkpoint |
| Native monitor ready + press, configDone=false | Input reaches native route; radial setup did not finish |
| OnRadialMenu press + gate | Named native early-return condition |
| ShowRadialMenu + OnRadialOpened, no rendered state | Shared state-to-GFx dispatch/rendering path |
| Render state + blocked/stick flags or FAULT | Radial visibility/state handling |
| No ledger/native readiness | Diagnostic activation or root trace route unresolved |

The captured stopping point will determine the **smallest correction**. No second
blind isolation package is included. Restoring a full v3 radial resource remains
an option only if these observations cannot be collected usefully.

## Reproducible tooling and validation

Original sources: src/hud/inkRadialDiagnostic.ws,
tools/instrument-radial-movies.py, tools/build-ink-radial-trace.py and
tools/compile-radial-trace.py. tools/audit-radial-trace-inputs.py reproduces the
read-only installed-resource snapshot into a fresh ignored destination.
Third-party classes, binaries, cooked files and
archives remain ignored. Current extraction/snapshot evidence is local under
build/ink-radial-trace-work, with complete-definition comparison JSON.

```powershell
$py = 'C:/Users/micha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py tools/compile-radial-trace.py --out build/ink-radial-trace-script-full-control
& $py tools/build-ink-radial-trace.py --out build/ink-radial-trace-d1-release-final --deploy deploy/ink-radial-trace-d1 --runner build/ink-radial-trace-native-runner
& $py tools/build-ink-radial-trace.py --out build/ink-radial-trace-d1-release-final --deploy deploy/ink-radial-trace-d1 --finish --runner build/ink-radial-trace-native-runner
```

Use fresh ignored paths to reproduce and adjust the pinned compiler-cache path
when making a fresh compiler run. --resume validates prepared resource checkpoints;
it does not invent native receipts. The API/declaration control makes the same
native calls with a constant report payload; it is **not a runtime no-op**.
Both it and the real diagnostic pass with identical warnings and assertions.
The native-source-file assertion scriptCompiledCode.cpp:56 occurs in both controls
and is explicitly recorded, not misreported as a new clean baseline. No script
errors occur. Existing provider hashes and the actual merged radial/HUD and
FriendlyHUD iteminfo sources are verified before source assembly use.

Final native stages, hashes and extraction evidence are recorded below after
packaging. A native startup timeout with empty logs is not resource validation.
The guarded metadata fallback must reproduce a separate successful
native control exactly and is labeled separately. No cooking result is claimed
to prove listener registration or wheel functionality.

### Delivered artifact and explicit native limitation

Private ZIP: `deploy/ink-radial-trace-d1/Ink-Iron-HUD-Radial-Trace-D1-private-test.zip`
(10,998,790 bytes), SHA-256:
`cb207b36e68debb00152e8c023013e30c58a730e516349257d2606d8de7dea52`.
Exact input/output hashes, effective owners, preserved support members and
validation controls are in `research/ink-radial-trace-d1-manifest.json`.

**Final D1 has not completed native cook/validate/pack or native metadata generation.**
An earlier instrumented revision passed all three initial native stages (22
resources, zero validation errors). Its later guarded shared-provider query
changed two movies; that final candidate repeatedly stalled before commandlet
startup, with empty logs. One clone attempt lacked depot configuration and is
excluded as resource evidence. Completing that private clone and isolating TEMP/TMP
still timed out; the previously successful native/compiler runtime also stalled.
No resource rejection, successful final native stage or native metadata run is
inferred from these timeouts. Native-control logs stay local under
`build/ink-radial-trace-d1-final`; final attempts under
`build/ink-radial-trace-d1-release-final`.

To deliver the requested single diagnostic without unsafe unguarded reporting,
`tools/reconstruct-radial-trace-bundle.py` uses only the observed 22-key native
table, existing key order, CRC32, ZLIB level 9 and 16-byte payload alignment.
It first reconstructs **three independently native-produced bundles byte for
byte** (v2, v3 diagnostic, initial D1). It refuses extra keys, other codecs,
unknown tables, imports/buffers/dependency tables and opaque payload gaps.
Final GFx definitions also independently parse/export through FFDec. Existing
non-ABC tags and texture tails are exact RC1 bytes. Final metadata is independently
relocated from a native table after reproducing a separate native control exactly.
These are independently checked reconstruction stages, **not native commandlet successes**.
The manifest deliberately records `official_cook_validated=false`.

The explicit fallback commands, after a failed native stage and with no existing
packed output or deploy directory, are:

```powershell
& $py tools/reconstruct-radial-trace-bundle.py --out build/ink-radial-trace-d1-release-final
& $py tools/build-ink-radial-trace.py --out build/ink-radial-trace-d1-release-final --deploy deploy/ink-radial-trace-d1 --finish --diagnostic-reconstruction --runner build/ink-radial-trace-native-runner
```

**82 tests pass**, including native-control byte reproduction, unchanged visual
definitions/textures, non-consuming observer behavior and RC1 support/ZIP checks.
All 22 packaged native resources re-extract exactly; ZIP CRC and deterministic
generation pass. Three movies contain diagnostic bytecode; the other **20 logical
resources**, existing scripts, aliases, menu XML and supporting package files
are unchanged. Nothing was deployed. D1 is temporary instrumentation, with final
native acceptance and actual runtime observation still outstanding. It is not a
corrected HUD release; both Tab and LB remain runtime acceptance gates.
