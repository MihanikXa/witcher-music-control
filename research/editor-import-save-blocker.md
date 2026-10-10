# First user-operated Editor import: save blocked

**Resolved on retry:** both workspace resources now exist at the intended
keys (EnemyFocus 156,310 bytes; Watermark 81,177 bytes). The new log records both
exporters and no overwrite/save cancellation, only failed thumbnail generation.
All non-image SWF tags in both saved files match their unchanged native inputs.
Hashes are recorded in `shadow-font-manifest.json`.

**CLI follow-up:** the failed cooker used its stale mounted workspace rather
than the supplied Editor assets. Correct isolated workspace staging now cooks
both files and verifies repeatable single-resource pack/metadata/re-extraction.
See [current evidence and limits](editor-cli-roundtrip.md). The Editor log's
`Asserts Disabled: ON` remains of unknown provenance/effect; the user did not
intentionally disable assertions. No recollection or repeated import is required.
The historical initial-failure and retry record below is superseded by the saved
outputs and CLI follow-up, not a description of the current project contents.

The user's new project exists at
`build/npc-editor-run/projects/quieteditorialnpcshadowgate/quieteditorialnpcshadowgate.w3edit`.
The copied Editor configuration selects this project and the existing uncooked
depot. Its project folder currently contains only the project file and local
string database; no workspace or saved redswf was found.

The current `build/npc-editor-run/bin/editor.log` records actual native SWF
export invocations with the current bundled `gfxexport_mult4fix.exe`:

- 05:24:24: EnemyFocus exporter invoked; 05:24:29: CFX recognized, followed by
  `Unable to save 'hud_enemyfocus.redswf' because overwriting is cancelled.`
  and `Unable to save imported 'hud_enemyfocus'`.
- 05:24:55: Watermark exporter invoked; 05:25:00: CFX recognized, followed by
  the equivalent two save failures for `hud_watermark.redswf`.

This proves attempted Editor import, **not a successful saved resource**.
"Cancelled" is the engine's wording, not evidence that the user clicked Cancel.
Whether checkout/overwrite confirmation, virtual destination selection or
another save-state issue caused it remains unresolved.

The searched log contains no `diskFile.cpp:2633` monitor assertion. However,
it also records `Asserts Disabled: ON` at 05:19:43, plus unrelated startup,
path-case and shutdown assertions. Therefore absence of the CLI assertion
cannot establish that the Editor fresh-creation issue is resolved. No assertion
state was changed by the agent; whether the logged state was a default or a
user dialog choice is unknown.

No existing r4data redswf, temporary exporter output or prior CLI artifact was
used as a substitute. Cook/bundle/re-extraction, shadow transformation and
archive generation remain blocked. Accepted v4 and font preparation are untouched.
Computer Use remains prohibited.

## Short manual retry in the same isolated project

1. Open the copied Editor and **QuietEditorialNPCShadowGate**. In Asset Browser,
   select the **virtual** `gameplay/gui_new/swf/hud` folder, not the physical
   `C:\...\r4data\...` folder in a file dialog.
2. Check out existing `hud_enemyfocus.redswf` and `hud_watermark.redswf` in that
   virtual folder. Checkout must copy each into this project's
   `workspace/gameplay/gui_new/swf/hud`, leaving r4data/uncook untouched.
   [CDPR documents this checkout behavior](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/39190599/Virtual%2Bdepot%2Band%2Bsource%2Bcontrol).
3. In the same virtual folder, import the unchanged native SWFs again. Confirm
   replacing **only those checked-out workspace resources** if prompted, then
   save. This tests the supported checkout/overwrite path; it must not be
   represented as a fresh-resource-creation test.
4. Verify these exact files exist under the project:
   `workspace/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf` and
   `workspace/gameplay/gui_new/swf/hud/hud_watermark.redswf`.
   Close the Editor and report the result. If checkout, overwrite or save
   fails, report the exact dialog text; do not change resource paths or suppress
   assertions to proceed. Do not choose Ignore All on an assertion dialog.

Assertion state is unknown; the user's clarification supersedes the earlier
request to recall Ignore All. No recollection is needed to continue validation.
Do not cook, publish, deploy or launch the game during this retry.
