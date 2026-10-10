# Shadow trial Editor import: no saved candidate yet

The user reports creating/importing/saving **QuietEditorialNPCShadowTrial**
without observing an assertion. CLI inspection confirms its project file exists,
but its directory contains only that file and the local string database: there
is no workspace `hud_enemyfocus.redswf` anywhere under the trial project.

The copied Editor log records:

- 05:56:58: exporter invoked on the correct prepared shadow source
  `build/npc-shadow-source-v1/input/hud_enemyfocus.swf`.
- 05:57:04: CFX recognized, then
  `Unable to save 'hud_enemyfocus.redswf' because overwriting is cancelled.`
  and `Unable to save imported 'hud_enemyfocus'`.

"Cancelled" is the engine's wording, not evidence of a user Cancel action.
This is the same save-state failure previously resolved for the unchanged
controls by explicit checkout followed by import. The exact underlying dialog
state is not established by CLI evidence. No assertion was observed by the user;
the log again reports `Asserts Disabled: ON`, whose provenance/effect stays
unknown. No suppression or setting change was made. Unrelated shutdown GPU
assertions are also present; they do not establish an EnemyFocus import defect.

A bounded asset-verifier invocation stopped at the missing source-file copy,
**before any cook/validate/pack/metadata command executed**. Its private
staging directory is `build/npc-shadow-cook-v1`. No old baseline or temporary
exporter output was substituted, and no test ZIP exists. The verifier now checks
all saved inputs before copying the tool layout and supports a separate unchanged
Watermark workspace so that control need not be imported again.

Log and missing-output receipt are preserved privately under
`build/npc-shadow-editor-save-blocker`. The unchanged baseline EnemyFocus remains
SHA-256 `08c9576c3b7398b8ffe3613d416d58a67629bed8326e1a5a8eebdf47585cf791`;
v4 source/archive and the prepared shadow source remain unchanged. All 32 tests
pass. No Computer Use, game launch, installation or working project change occurred.

## Minimal manual retry: changed EnemyFocus only

The prior handoff should have explicitly required checkout before this new
project's first replacement import. This correction keeps the unchanged project
and installed/depot resources intact.

1. Open **QuietEditorialNPCShadowTrial** in the copied Editor. In Asset Browser,
   select the virtual `gameplay/gui_new/swf/hud` folder. Check out the existing
   **hud_enemyfocus.redswf** into this project's workspace.
2. In that same virtual folder use **Import → Flash SWF** with
   `C:\Dev\witcher-ui-overhaul\build\npc-shadow-source-v1\input\hud_enemyfocus.swf`.
   Confirm replacement of the checked-out **project workspace** resource, then Save.
3. Confirm this actual file exists:
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects\quieteditorialnpcshadowtrial\workspace\gameplay\gui_new\swf\hud\hud_enemyfocus.redswf`.
   Report completion or the precise checkout/save dialog text.

Do not repeat Watermark or unchanged EnemyFocus imports, generate depots, cook,
publish or install. If an assertion appears, preserve its text and stop without
Ignore All. This is an overwrite of a checked-out test resource, not proof of
assertion-free fresh creation. Once the changed candidate is saved, offline
contract/atlas checks and the isolated cook/bundle gates can proceed.
