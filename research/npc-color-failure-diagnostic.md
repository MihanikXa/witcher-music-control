# Failed v2 name recolor: bounded diagnostic — 10 October 2026

**Cause remains unconfirmed.** User reports Vesemir stays VIP green and Roach
stays neutral blue, without a compile error. These are two distinct failing
branches. The new package is a diagnostic, not a runtime-proven correction.
No installed script, settings, Vortex deployment or compatibility merge was
changed; no game was launched. Font/shadow work remains outside this task.

## User-reported in-game v3 outcome — 10 October 2026

**Explicit user feedback, preserved verbatim:**
- “Test successful”
- “Yes, and not only cyan, also whitish colors too, and stayed on these whitish didn't return”

The latter answers the question whether both Roach and Vesemir changed color during the test and whether the changes persisted. User confirms they saw the diagnostic colors (cyan followed by whitish/palette colors), which remained instead of reverting during observation. This is **user-reported live gameplay evidence**; the agent has not inspected screenshots, the numerical READ/NUMBER/UINT/PALETTE/FINAL messages, or timing details.

**What this supports:** The separately installed v3 diagnostic executes enough to alter the visible name colors for the two observed targets, and a palette-like final color is achievable/persistent over the observed interval. Thus the game can render the desired muted colors without replacing the movie, and the underlying Flash path is at least functional in this test.

**What remains inferred rather than demonstrated:** Exact source RGB returned by `GetMemberFlashNumber` versus `GetMemberFlashUInt`, whether Number setter independently succeeded, whether UInt getter / setter is the crucial v2/v3 difference, which phase caused each visual change, whether the original v2 wrapper ever ran, and persistence after target switching, HUD reload, fast travel, dialogue, or save reload. The diagnostic does not isolate those facts purely from visible colors. The strongest targeted next hypothesis is that v2's `GetMemberFlashNumber("textColor")` exact-value mapping misses the actual runtime read while v3's UInt-based path reaches a suitable RGB. Do not declare that as the confirmed root cause without exact diagnostic readings or a narrow controlled v4 comparison.

**Next step:** Implement an original, minimal production color-only v4 in a separate removable mod, preferentially using the working v3 UInt-access pattern with exact palette values and safely handling unknown color values. Preserve wrapper return/chain and all other HUD behaviour. Compile with matched no-op controls, package privately, disable both v2 and v3 before testing, and request in-game Roach/Vesemir plus rapid focus/reacquisition, HUD reload, and rollback checks. Do not prematurely claim the problem fully solved or expand scope to shadows or fonts.

## Verified evidence, in requested order

### A. Loading and execution

Read the deployed v2 file directly. SHA-256
`533d039bd5e1c44059691b69695a287a381133199d594c972d0457cf5096a260`
matches the original v2 ZIP member exactly. Current `mods.settings` enables
`modQuietEditorialNPCColors` at priority 38; SHA-256 of settings is
`42068953d6acd01ddcf17201af4c72abdbb7a395ebcf913bf49b5ee17f571423`.
Current `dx12user.settings` has `ContentManager/Mods` Enabled and EnabledLocal
true. The installed mod has the one loose WS, Vortex marker files, no info.json
opting out of loose scripts, no compiled blob and no UI movie.

These checks establish deployed input eligibility, **not** actual loader
inclusion or event execution. No available retail compile log traces this source
or its wrapper. Absence of a user-visible compile error does not prove loading.
Other current working loose mods likewise have no info.json; inventing loader
metadata as a fix is not justified by these files.

The v2 wrapper calls `wrappedMethod` once, retains its result, and performs its
read/write after that call. The current FriendlyHUD EnemyFocus source invokes
`setAttitude` when target/attitude/Axii changes; name updates are requested at
0.25-second intervals, while `UpdateName` invokes `setEnemyName` only when the
string changes. Thus v2 is textually after the original script assignment
requests. **When the native Flash invocation executes relative to a direct
member access and rendering is untraced.** Source ordering is not a live-frame
ordering proof. Current MHC supplies an existing EnemyFocus OnTick wrapper;
the current compiler accepts event annotations. Neither proves v2 execution.

### B. Exact field and color ownership

The current installed startup.bundle entry is
`gameplay/gui_new/swf/hud/hud_enemyfocus.redswf`, uncompressed size 88,805,
packed size 60,342, codec 1. Fresh direct read/decompression has SHA-256
`8b5c7cf0cb0e61fd005239689e096c9c5da9e3f1aa2182f9f88c71057903a76e`,
matching the movie used for the prior contract/code inspection. A fresh read-only
resource scan finds no mod bundle or loose replacement of this key. The prior extracted current-runtime movie,
its code/XML and current native authoring source identify:

`HudModuleEnemyFocus.mcNPCFocus` → sprite 63 → named `tfName`, character 38,
depth 35. Runtime `setEnemyName` assigns `tfName.text`, and `setVisibility`
assigns `tfName.textColor` directly. The five observed runtime constants are
7977213 neutral, 13869949 friendly, 16711680 hostile, 16561481 Axii and 5963520
VIP. They agree with v2. All are exactly representable in a 32-bit float;
rounding is not a supported explanation for these particular constants.

Name coloring here is direct `textColor`, not name HTML/font-color markup or a
color filter. Enemy-level text uses HTML separately, and dynamically allocated
damage TextFields use their own color path. The diagnostic touches neither.
The Interactions source assigns interaction-action text to
`mcInteraction.mcActionName.tfActionName`; it does not supply the above NPC
attitude palette. This narrows the likely renderer but does not prove that the
particular visible label observed by the user is this live field.

Current `flashScriptImports.ws` explicitly supplies distinct
`GetMemberFlashNumber`/`GetMemberFlashUInt`, corresponding setters,
`GetMemberFlashObject`, `GetChildFlashSprite`, and `GetChildFlashTextField`.
The typed text-field wrapper exposes GetText/GetTextHtml/SetText/SetTextHtml;
it does **not** inherit CScriptedFlashObject's numeric-member accessors.
The old generic `GetMemberFlashObject("tfName")` path may or may not provide a
usable live object. Compilation validates signatures, not native binding
results. Likewise separate Number/UInt API names do not prove either coerces
the color's runtime representation. Both must be measured.

### C. Competing systems

Current provider hashes remain:

| Source | SHA-256 |
| --- | --- |
| FriendlyHUD EnemyFocus | `afcaea5ca80ee53b119a67190ae5af1c7c8f4b48521be3321088d89eeac23200` |
| SAH hooks | `21251f33625f039622da3fe92d1ebc23fd9b72663caaad631bd6f8cb11db4ca8` |
| MHC contract boss-bar hook | `32d4e556c05d722846eb64d3bcc8e0b45e06cc09bed9e9ebef64dc60bf8da59c` |
| Current Flash imports | `22aa58104e73265ea9897c33815588ddb40b881ad085a292c535d4be766395e4` |

FHUD supplies original category/name updates and visibility. SAH wraps HUD
OnTick, ShowDamageType and SetDodgeFeedback and applies visibility behavior.
MHC's EnemyFocus OnTick delegates the chain and adjusts only ordinary health
bar alpha for its contract boss display. The scanned enabled source hooks do
not write the same name color later or redirect the name renderer. All relevant
FHUD/SAH/MHC sources match the tested assembly after encoding/newline
normalization. An opaque compiled dependency or engine/AS update remains a
possible competing updater; there is no current same-resource path collision.

## Diagnostic strategy and preservation

New original `src/npc/quietEditorialNameProbe.ws`, separate mod ID
`modQuietEditorialNPCProbe`, must run **without v2**. The production v2 source
is retained unchanged as failed-test evidence; no unverified fix is substituted.

- HUD OnTick beacon at two seconds establishes an independent executing hook,
  reporting EnemyFocus ticks and ordinary `UpdateName` calls. A second status
  at 30 seconds also reports the actual display-target string and report count.
- EnemyFocus OnTick retains the original event result and counts executions.
  A separate UpdateName wrapper only delegates and counts calls. This separates
  ordinary method execution from event wrapping without replacing either file.
- Every five seconds, only for **Roach** or **Vesemir**, compare the generic
  object's `text` against the typed TextField's GetText and display-target name.
  `FIELD` mismatch is reported and causes **no writes**. READ also reports
  focus/text visibility and raw Number/UInt color values.
- A confirmed field receives cyan `#00FFFF` once via the Number setter; its
  immediate Number/UInt readbacks are reported. Five seconds later report its
  retained value and test the UInt setter with the same cyan. This bypasses
  the five-color switch completely.
- After another five seconds, report the delayed UInt result and try the
  existing palette once through UInt, then report FINAL five seconds later.
  Initial RGB comes from UInt when plausible, otherwise Number. If neither
  yields a restorable nonzero 24-bit RGB, report READ and skip writes rather
  than guess a color or restore black. Unknown valid RGB maps back to itself.
- Automatic reporting has a hard limit of **ten NPC reports plus two HUD
  notices** per module/HUD lifetime. Target changes restart the sequence but
  cannot evade the cap. Stop/restore after the cap; completed targets receive
  no more samples. Full per-frame Flash reads/writes are not used. Counters
  and diagnostic timers are temporary; this is not the final recolor lifecycle.
- Supported `Log` mirrors the few notices if existing logging captures them;
  no logging settings are changed and no retail log destination is promised.
  Notifications use the same supported GUI ShowNotification method used by
  existing mods. Optional console command `qeprobe` proves source registration
  independently of either event, if an existing console is already available.
  It does not enable a console or alter settings.

Only name `textColor` is written, after matching the field and target. No alpha,
name string, scale, health/damage, targeting, quest icon, visibility, font,
shadow or gameplay write occurs. UpdateName and both OnTick wrappers delegate
exactly once; the two OnTick event results are preserved. Diagnostic messages
are temporary overlay notifications and may be replaced by another notification;
no existing notification queue is cleared or disabled. Do not save this session.

## Interpreting the next runtime evidence

| Observation | Supported conclusion / next investigation |
| --- | --- |
| `qeprobe` recognized | Source/exec registered; absence of NPC counter increments is not simply a missing source |
| HUD beacon, ticks=0 but name calls grow | NPC class method chain runs, but OnTick annotation is not executing; investigate event wrapping/dispatch |
| HUD beacon, ticks>0 | NPC wrapper executes; investigate field and access results |
| No beacon and no usable console | Loader/HUD wrapper/notification delivery remain indistinguishable; do not label this definitive non-loading |
| Console reports source loaded but no HUD/module | Loading succeeds; module/lifecycle selection is wrong or unavailable |
| FIELD typed name correct, object text empty/different | Generic object access fails to identify the typed name field; replace that access path only after a supported alternative is validated |
| Both field texts differ from target | Wrong live field, stale target or different renderer; no recolor attempted |
| Matching name but hidden focus/text, visible name unchanged | Investigate the visible renderer/visibility path; not a resource-file collision |
| READ N differs from U; U is vanilla RGB | Number read/type conversion explains why the exact-value switch misses; test supported UInt correction |
| READ both values are other valid RGB | Exact-value mapping misses the actual color; inspect observed state rather than guessing constants |
| Immediate readbacks never show 65535 | That setter/object path is ineffective or asynchronous; no immediate-write success proved |
| Immediate 65535 but next delayed value reverts | Property write succeeds but a later update resets it; trace that update before changing lifecycle |
| Number fails, UInt succeeds and persists | A narrowly supported UInt-access correction is justified by runtime evidence |
| Readbacks stay 65535, actual visible name never cyan | The edited object may be a non-visible label, or another presentation/text-format path controls output |
| PALETTE and FINAL match expected RGB, visible name changes | This diagnostic's trial write works; production correction still needs the observed safe lifecycle |

Possible AS/native deferred execution means immediate failure is not alone proof
of a broken setter. Compare both immediate **and delayed** values and the visible
color. This protocol does not promise every absent notification is diagnostic;
the optional independent exec and counters resolve those cases where available.

## Compilation and package handoff

Exact package path:
`C:\Dev\witcher-ui-overhaul\deploy\npc-nameprobe-v3\QuietEditorial-NPC-NameProbe-private-test.zip`

ZIP SHA-256: `3d6803e582227c3d967bf189c1465b71df3523a541ba65ee6edc4fcd1540326b`

2,514 bytes; one original member:
`Mods/modQuietEditorialNPCProbe/content/scripts/local/quietEditorialNameProbe.ws`

Member SHA-256:
`0d3cff26d1188c8a523fb4a108f51149b17e118b06ae157334e473dc5075600a`.
ZIP CRC/readback pass; a second packaging run produced the identical ZIP hash.
Explicit Mods/ routing uses the already inspected Vortex
1.7.5 witcher3tl installer and game-root mod type. No installed Vortex preview
has been executed. No binaries/blobs/reference code or game resource is included.

Fresh official baseline / declaration-matched no-op / diagnostic compile in the
known-working copied assembly. All exit 0, emit real nonempty blobs, have zero
Script/WCC errors and identical warning counters (819). Baseline has 23,591
diagnostic assertions; both no-op and candidate have 23,597. Generated blobs
are respectively 52,978, 53,731 and 58,113 bytes. Private receipt
`build/npc-nameprobe-safe-controls/receipt.json` SHA-256 is
`0ada08e0bc72ed1e7cf3dc0513f15a35f0c2ceb26209444a0dcf722105848abd`.
The no-op retains all
declarations and six nonempty function bodies, removes instrumentation/member
writes, and delegates the three wrapped methods. Both control and diagnostic
produce exactly six extra `scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())`
assertions relative to baseline, no other assertion change or warning delta.
The package gate compares that exact control delta, candidate hash, unchanged
compiler and assembly inputs, and current affected source-provider coverage.
Early controls with empty helper bodies had fewer diagnostics; they were not
accepted as matched controls or packaged. The control was corrected to retain
nonempty bodies before accepting the comparison. This is compilation evidence,
not an assertion-free compiler or full retail multi-blob simulation.

Seven enabled compiled mods remain outside exact retail multi-blob reproduction.
Existing FHUD/SAH/MHC code is preserved. Runtime native binding/annotation order,
notification delivery and the visible field remain acceptance risks.
The 23-test suite passes, including control-declaration preservation and gates
rejecting mismatched/extra diagnostics and source changes. Compiler logs and
all intermediate diagnostic resources remain ignored/private.

### Smallest useful user test

1. Exit the game. In **Witcher Compatibility Test**, **disable v2**
   `modQuietEditorialNPCColors` and deploy. Uninstalling it is unnecessary;
   leave it disabled. Do not run both packages, rebuild merges, change priorities
   or disable compatibility packages.
2. Install the exact new ZIP via **Install From File**, enable only the new
   diagnostic and deploy. Verify its sole destination is
   `Mods\modQuietEditorialNPCProbe\content\scripts\local\quietEditorialNameProbe.ws`.
   Stop if routing differs or a merge/overwrite is proposed.
3. Load the same existing English save; **do not save**. Record the HUD beacon.
   Face **Roach**, keep the same visible target for **30 seconds**, and record
   READ → NUMBER → UINT → PALETTE → FINAL plus whether the name becomes cyan
   after each setter. Expected neutral baseline U is 7977213; palette 15327954
   (`#E9E2D2`). Report the actual numbers, including zeros, not just unchanged.
4. Face **Vesemir** and hold for **30 seconds**, recording the same five notices
   and visible color. Expected VIP baseline U is 5963520; palette 14008462
   (`#D5C08E`). If FIELD or writes-skipped appears, report that exact message;
   no further target categories are required. A fresh reload restarts the cap
   if a target change interrupted the sequence.
5. If no notices appear, use `qeprobe` only if your console is already available;
   record recognized/unknown and its message. Do not enable a console or edit
   logging settings solely for this test. Report absent notices explicitly.
6. Exit, **disable the one diagnostic mod and deploy**. Keep failed v2 disabled.
   Reload to restore the current vanilla appearance. No manual game-file edits,
   settings reset or compatibility removal is needed. This is one-mod rollback.

Until these observations arrive, neither UInt access nor another lifecycle is
declared the confirmed fix. The next correction will use the result of this
single bounded test rather than add another broad investigation.

### Reproduction

```powershell
python tools/compare-npc-wrapper-diagnostics.py --runtime build/native-npc-reproduce/runtime --assembly 'C:\REDkitProjects\witchercompatibility\compatibility-validation\analog-gait' --candidate src/npc/quietEditorialNameProbe.ws --out build/npc-nameprobe-fresh
python tools/package-npc-color-trial.py --probe --controls build/npc-nameprobe-fresh/receipt.json --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --settings 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\mods.settings' --out deploy/npc-nameprobe-fresh
```
