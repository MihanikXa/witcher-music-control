# NPC shadow-only source trial: manual changed-input gate

**Changed-input save blocker:** the user created/imported/saved and observed no
assertion, but the log records exporter success followed by cancelled
overwrite/save. Checkout now exists, yet it still contains the unchanged
movie. See the [current unique-name import alternative](npc-shadow-save-blocker.md).
Only this changed candidate needs a manual action; the successful unchanged
baseline is intact. The original import instructions below are historical.

The unchanged saved Editor-output pipeline is verified offline; see
[the corrected cook/bundle evidence](editor-cli-roundtrip.md). This continuation
prepares the first original shadow-only **native SWF**, not an installable mod.
No CLI import was retried, no Editor was launched by the agent, and no installed
resource, project workspace, assertion setting or accepted v4 mod was changed.

## Implemented and verified

`tools/prepare-npc-shadow.py` exports the current native authoring source with
the local JPEXS 26.3.0, assembles unchanged and changed XML controls, and uses
only the verified changed sprite from the assembler. Whole-movie XML assembly
changes seven unrelated shape tags (22/32/2), so those bytes are discarded.
The unchanged target sprite assembles byte-identically. The changed sprite
must equal the original with exactly the approved 24-byte shadow record
substitution; all original movie bytes outside that record are retained.
This edits the standard documented SWF source, not an opaque CR2W/GFx header.
The standard compressed SWF is re-exported; its full XML must equal the original
with only the intended filter attributes changed, excluding derived file offsets.

The record layout follows the primary
[JPEXS SWFOutputStream filter serializer](https://github.com/jindrapetrik/jpexs-decompiler/blob/master/libsrc/ffdec_lib/src/com/jpexs/decompiler/flash/SWFOutputStream.java)
(RGBA, FIXED fields, UFIXED8 strength and flag bits). The transformation and
guards are original project code; no third-party mod content is copied.
The native SWF remains proprietary game-derived material and stays private.

| Property | Baseline | Trial |
| --- | --- | --- |
| Target | sprite63, character38, depth35, tfName | same |
| Shadow RGB/alpha | #000000, 255 | #141718, 166 |
| Blur X/Y | 4 / 4 | 2 / 2 |
| Strength | 3 | 1 |
| Distance | 1 | 1 |
| Angle | 0.7853851318359375 radians | unchanged |
| Passes / flags | 1 / compositeSource, outer, no knockout | unchanged |

Only **seven decompressed bytes** differ, all within the existing filter.
An independent repeat produced the identical source hash. All 32 tests pass,
including synthetic guards rejecting angle/flag/placement changes and malformed
SWF records. Accepted v4 source and archive hashes remain unchanged.
Frame header, every bitmap, font import, name text definition/bounds/size,
ActionScript, symbol, placement and other filter bytes are identical. This is
source validation, not evidence that the changed resource has been imported,
cooked or rendered. The five semantic color mappings remain solely in v4.

Input SHA-256:
`f84544e26c27b38e8b1f64ff8f77775743e1e6ecd7a4f1972fce381ed9a9e819`.
Output SHA-256:
`64ad2c80b96770ed0d09fa59f6ac4b00f5beb859276b8b0d60ace27d0a16cc17`.
JPEXS SHA-256:
`1587e60b2ec2c0e4f5721fd5f2aaaf2379f6d416569de99054b5c5d1e9ba841c`.
Full receipt/XML/assembler controls remain under `build/npc-shadow-source-v1`.

```powershell
python tools/prepare-npc-shadow.py --native build/npc-editor-run/r4data/gameplay/gui_new/swf/hud/hud_enemyfocus.swf --ffdec build/tools/ffdec/ffdec.jar --out build/npc-shadow-source-fresh
python -m unittest discover -s tests -q
```

## Shortest required manual action

Computer Use is prohibited. A changed-input official Editor import is needed;
the successfully imported unchanged controls must **not** be imported again.
Keep their existing project/workspace intact as the comparison baseline.

1. Open the **copied** Editor:
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\bin\x64_RedKit\editor.exe`.
   Create a separate new project **QuietEditorialNPCShadowTrial** under
   `C:\Dev\witcher-ui-overhaul\build\npc-editor-run\projects`.
   Use the existing `E:\TheWitcher3RMDepot\` depot; do not generate a depot or
   open the working compatibility project.
2. In Asset Browser, navigate to `gameplay/gui_new/swf/hud`. Use the same
   successful checkout workflow: first check out `hud_enemyfocus.redswf` into
   this new project's workspace. Then **Import → Flash SWF**, selecting only
   `C:\Dev\witcher-ui-overhaul\build\npc-shadow-source-v1\input\hud_enemyfocus.swf`.
   Confirm replacement/checkout into this **new project workspace**, then Save.
   Do not overwrite an installed/depot source or import Watermark again.
3. Report that it is saved (or the exact failure). If an assertion appears,
   preserve its text and stop; do not select Ignore All or disable assertions.
   Do not cook, publish, install or launch the game.

Expected output key in the new workspace:
`gameplay/gui_new/swf/hud/hud_enemyfocus.redswf`.
This import is for the changed source, not another attempt at the already
successful unchanged import. The original baseline project stays intact.

## Remaining validation and package boundary

After the user saves, compare its embedded movie against this source and the
unchanged Editor result with exactly one allowed filter change. Reuse the proven
isolated official cooker/validator and single-key bundle/metadata/re-extraction
route. Verify complete atlas metadata and all used pixels/borders, plus padding
differences, resource key and source identity. Keep assertion state unknown
unless new evidence establishes it. No ZIP until these changed-asset gates pass.

The future mod will contain only the EnemyFocus resource bundle/metadata, no
scripts or font library. v4 remains enabled separately; v2/v3 remain disabled.
Existing HUD/script hooks are preserved in source, but live health/quest icons,
targeting, damage, FriendlyHUD/SAH visibility and appearance remain untested.
Any enabled mod replacing this same resource key requires a priority/conflict
check before testing. A future one-package rollback disables/removes only the
shadow trial, retaining accepted v4 and the compatibility stack.

First visual acceptance: compare names on snow/bright sky, foliage/fire and
dark interiors/caves; switch targets, reload and toggle HUD visibility. Confirm
v4 colors remain, health/quest/targeting/damage displays work, and names remain
readable at controller distance. These are pending in-game tests, not claims.

## Track B status

English Gentium source preparation remains unchanged and separate. No font
import, cooked font resource or font ZIP was made during this shadow continuation.
