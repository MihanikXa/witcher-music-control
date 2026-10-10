# Bounded current Editor workflow investigation — 10 October 2026

Outcome **B**: the current copied Editor starts and accepts the existing depot,
but supported GUI project creation/import could not be operated with the
available desktop input tool. No Editor-imported SWF exists and no asset/shadow
pipeline pass is claimed. An independently removable original color-only trial
passes its own controlled compiler gate; see [handoff](npc-color-trial-handoff.md).

## Supported workflow and isolation

CDPR documents creating a new project from Welcome, with editable assets in its
`workspace` and generated publication files in `publish`. The existing valid
uncooked depot can be selected without generating another depot. The virtual
depot resolves workspace over uncook over REDkit r4data; existing source assets
are locked/read-only and checkout copies them into the project workspace.
[CDPR setup](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/6324341),
[CDPR depot/checkout](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/39190599/Virtual%2Bdepot%2Band%2Bsource%2Bcontrol?atl_f=content-tree)

The exact Flash menu sequence is described in the community UI tutorial:
Asset Browser folder, right click → Import → Flash SWF, choose SWF and confirm
replacement/checkout. This is **community documentation**, not a verified
current Editor observation here. CDPR provides a UI-mod video tutorial, but the
searched official text did not specify this menu sequence. No guessed command
flags or speculative native resource-editing API was used.
[UI import tutorial](https://redkit-resources.github.io/docs/en/en/unofficial_docs/guides/create_new_hud_medallion/),
[CDPR UI video index](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/28737537/Video%2Btutorials)

Prepared an isolated physical copy at
`C:\Dev\witcher-ui-overhaul\build\npc-editor-run` using
`tools/prepare-npc-editor.ps1`. Full bin and r4data were copied, including
texture groups, current scripts/native caches, GUI dependencies and editor data.
No junction to installed resources and no live configuration edit. Source audio
`assets/w3_audio` was omitted because no audio-authoring/import test is involved;
this is not a claim of full Wwise authoring setup.

Robocopy r4data receipt: **232,112 files, 29,810 directories, 78,024,722,648
bytes**, zero failed/mismatched/skipped files. Full-copy receipt is local;
proprietary files and logs are excluded from Git. Runtime/layout paths are kept
intact, including the correct `GUIWithAlpha` configuration. Copied Editor
SHA-256: `ed2a89f9dc05a7f75ba56caee0eb5320ca90325d03ddbbbd856dd1941d4d2b0f`.
Texture-group XML SHA-256:
`8c22259fabd1ee8e63c2df12419cbc6732cd4d3fa6dd997947a9a29cec5c3c22`.

Only the copied `bin/r4LavaEditor2.ini` was changed: clear `workspacePath` so the
working compatibility project cannot be selected automatically, retain the
game path for validation, and select existing `E:\TheWitcher3RMDepot\` as the
read-only uncooked depot. The observed [Global] keys were used rather than
invented startup flags. The first preparation had mixed line endings, causing
the depot value to swallow following keys; this original-tool bug was corrected
by normalizing the copied INI to CRLF. It was a setup error, not an SWF result.

## Actual bounded execution

1. Two supported desktop `launch_app` calls returned
   `accessibility window-opened handler did not become ready`, with no Editor
   process/window/log afterward. These failures are desktop-tool diagnostics,
   not REDkit import failures.
2. A normal process launch of the **copied** editor.exe succeeded. The Welcome
   dialog initially showed the copied INI error; closed that process before
   correcting the local INI. No Generate action was invoked.
3. Relaunched the copied Editor. Its splash explicitly identified build
   **5.0.1048625 (Oct 7 2026)**. It passed the depot setup stage automatically
   and displayed **Create project**, Name `MyProject1`, location
   `c:\redkitprojects`, and the existing compatibility project in Recent
   Projects. That existing project was never clicked/opened. The Create page
   supports the observed current setup workflow but does not prove import.
4. Attempting to set the new project name and then refresh/activate the same
   window failed with `foreground window did not report a process id`.
   Further state capture also returned that diagnostic. This prevents safely
   operating checkout/import or verifying a write destination. No custom UI
   helper, PowerShell UI Automation, suppression or editor-internal calls were
   substituted.
5. Closed only PID 33076 after confirming its executable path was the local
   copied Editor. No project was created, no world/game was started, no SWF was
   checked out/imported, and no publish/build step was executed.

The Windows [computer-use skill](C:/Users/micha/.codex/plugins/cache/openai-bundled/computer-use/26.1007.21434/skills/computer-use/SKILL.md)
was used for observed window state and supported input. Its guidance requires
fresh observations after input errors and stopping when recovery fails; this
is a tooling limitation, not an approval requirement. No user confirmation was
needed for this isolated test.

Current Editor output comparison: **unavailable**, because there is no imported
output. Its diskFile fresh-import assertion behavior remains **untested**.
The earlier three-movie CLI assertion remains an unresolved creation-state
diagnostic shared by unrelated assets; it is neither a verified EnemyFocus
resource defect nor a confirmed harmless environment defect. Successful loaded
resave/cook and matching contracts do not discharge that gate.

## Exact manual continuation, without deployment

1. Launch
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   Verify Welcome reaches Create project. If it instead requests generation,
   **do not Generate**: verify the existing depot path and copied INI first.
2. Enter name `QuietEditorialNPCProbe`. Beside **Location**, click **Browse**
   and choose `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects`.
   Before clicking **Create new project**, the preview must resolve to
   `...\projects\quieteditorialnpcprobe\quieteditorialnpcprobe.w3edit`.
   Do not open WitcherCompatibility or choose a game/REDkit/depot directory as
   the workspace. Do not load a world or press Play.
3. Open Asset Browser via View or Ctrl+A. Select
   `gameplay\gui_new\swf\hud`. Right click **Import → Flash SWF** and select
   the unchanged copied native
   `...\npc-editor-run\r4data\gameplay\gui_new\swf\hud\hud_enemyfocus.swf`.
   Confirm replacement/checkout only for the new project's workspace. If the
   menu differs, record its actual labels instead of guessing. Existing locked
   source copies must remain in uncook/r4data, untouched.
4. Repeat once for `hud_watermark.swf` as an unrelated control. Capture all
   dialogs/assertions and save the resulting workspace resource(s). Also note
   whether import overwrites a loaded checked-out resource or actually creates
   a fresh one; a no-assertion overwrite alone is not evidence about CLI fresh
   creation. Do not import a whole GUI directory or use an existing compiled
   redswf as the substitute input.
5. Preserve the copied `bin/editor.log` before/after each import and the two
   workspace redswfs, plus hashes of the unchanged input SWFs. Close the Editor.
   Stop here if either resource-state assertion occurs or required metadata is
   missing. No cook/package success claim follows from file existence.
6. Feed the **new** two-resource workspace into the same installed-current
   official cooker used in the previous controlled case, physically isolated.
   Compare native code/SymbolClass/timelines/placements, used atlas regions,
   borders, properties/linkage and CRCs to the runtime and CLI outputs with
   `tools/compare-native-npc.py` and `tools/analyze-npc-atlas-padding.py`. Review
   fresh-import, load, resave, cook and validate diagnostics separately.
7. Only if those gates pass, prove the single EnemyFocus resource bundle and
   re-extraction before styling. Current bundle/re-extraction and asset ZIP gates
   remain unexecuted. Then produce independent color/shadow movies and a combined
   proof, preserving every non-style contract. Do not use the fallback script
   simultaneously for the asset color comparison.

This is the shortest remaining shadow path: one user-operated import/control in
the already prepared current Editor. No more CLI bootstrap variations are
proposed. If the assertion also occurs there, retain the bounded two-movie
reproduction and await an actual current-tool fix; do not hand-edit headers.

## Preservation and separately testable result

The protected 41-file snapshot covers Documents game files and installed
REDkit bin configuration/log files; after the test their hashes, sizes and
timestamps match. Installed SWFs/texture configuration/current executables were
read and copied, never written. No Vortex staging/deployment operation, live
game modification, save, compatibility merge or settings change was performed.
The existing depot was selected for source reads, with no Generate/check-out
action against it. Full all-file hashing of that large depot was not performed.

The fallback now preserves the event return value as the known working Monster
Hunt wrapper does. Fresh baseline, no-op NPC, no-op HUD and RGB-hook compiles all
pass. Both no-ops reproduce the candidate's single metadata diagnostic, with
unchanged warning counters. Its separate private test archive is ready under
the documented narrow regression criterion; **only RGB is being tested**.
First runtime acceptance must establish load/reload, target-switch colors,
visibility, health/quest/damage and FHUD/SAH/MHC behavior before any visual claim.
