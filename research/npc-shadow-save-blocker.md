# Shadow trial Editor import: no saved candidate yet

## Current follow-up: checkout exists, replacement still cancelled

The user completed checkout/import/save and then clarified: **no
overwrite/replacement prompt appeared**. A writable 156,120-byte resource now
exists in the trial workspace, but its non-image movie tags are byte-identical
to the original native movie and differ from the shadow source. The original
black/alpha255/blur4/strength3 filter remains. File SHA-256:
`68d9ab2eb9eb65b8f935b334beb46f39d43dc05755145a2ae2ad8d60a3d41f8d`.
This is the checked-out baseline, not the successfully imported shadow trial.

The new log runs the correct changed-source exporter at 06:03:00, then repeats
the cancelled-overwrite/save warnings at 06:03:06. Filesystem read-only state
is false; the failure persists after checkout. No assertion-state change is
inferred. Absence of a user prompt does not establish who cancelled anything.

Read-only current Editor binary inspection finds the overwrite question and
error in the core resource strings, plus an embedded SaveErrorDialog whose
Overwrite button is initially hidden/disabled. These identify actual UI
resources, not the control flow invoked by this import. Reimport controls also
exist, but the checked-out resource has no decoded source-path property;
blindly asking for reimport could use the wrong source. No guessed overwrite
flag, resource-header edit, assertion suppression or UI automation was used.
Existing CLI help exposes no overwrite repair option. One `import -help`
request was rejected for missing depot path; it performed no import and supplied
no supported repair flag. Further bootstrap variations were not attempted.

The asset verifier now optionally requires `--expected-native`: it rejects this
checked-out movie **before copying tools or executing any cooker**. Synthetic
tests cover stale code/placement rejection and expected bitmap-storage changes.
All 35 tests pass. Private log/input receipt:
`build/npc-shadow-checkout-import-retry`.

### One bounded alternative: import a new resource name

To remove the existing-resource replacement condition, a byte-identical source
copy is prepared at:
`C:\Dev\witcher-ui-overhaul\build\npc-shadow-source-v1\input\hud_enemyfocus_qe_shadow_v1.swf`.
Its SHA-256 remains
`64ad2c80b96770ed0d09fa59f6ac4b00f5beb859276b8b0d60ace27d0a16cc17`.
No corresponding redswf exists in the copied r4data or generated depot. This
changes the import filename only, not symbols, code, font imports or SWF bytes.

1. Open the existing **QuietEditorialNPCShadowTrial** project. Select virtual
   `gameplay/gui_new/swf/hud` in Asset Browser.
2. Use **Import → Flash SWF** and select **hud_enemyfocus_qe_shadow_v1.swf**
   at the path above. This imports a new resource; do not check out or replace
   `hud_enemyfocus.redswf` again.
3. Save and confirm the new file exists at
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects\quieteditorialnpcshadowtrial\workspace\gameplay\gui_new\swf\hud\hud_enemyfocus_qe_shadow_v1.redswf`.
   Report completion or the precise error; if an assertion appears, stop and
   preserve it without Ignore All. No cook/publish/game installation.

This bounded alternative is **prepared, not executed or validated**. After it
saves, check the exact modified movie contracts and coherent texture linkage.
The verifier's explicit `--enemyfocus-file` stages a copy at the canonical
EnemyFocus path in a fresh isolated runner before official cooking. Preserve
the same virtual folder so relative font imports stay unchanged. A different
internal texture/export prefix must match its embedded references; do not edit
that prefix manually or assume a filename change is sufficient for runtime.
Cook/validate/bundle/re-extraction and contract/atlas gates still precede any ZIP.

Reproduction after the manual import (use a fresh output directory):

```powershell
python tools/verify-editor-assets.py --layout build/npc-state-expanded --workspace build/npc-editor-run/projects/quieteditorialnpcshadowtrial/workspace --control-workspace build/npc-editor-run/projects/quieteditorialnpcshadowgate/workspace --expected-native build/npc-shadow-source-v1/input/hud_enemyfocus_qe_shadow_v1.swf --enemyfocus-file build/npc-editor-run/projects/quieteditorialnpcshadowtrial/workspace/gameplay/gui_new/swf/hud/hud_enemyfocus_qe_shadow_v1.redswf --out build/npc-shadow-unique-cook
```

## Earlier missing-workspace attempt and superseded checkout retry

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
