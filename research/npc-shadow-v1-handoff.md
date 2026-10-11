# NPC shadow v1: private visual trial, offline gates passed

The unique-name official Editor import saved the correct changed movie. The
existing-resource overwrite cancellation remains unresolved, but is avoided by
creating a new test resource. The original and checked-out baseline projects
remain intact. This is a **shadow-only** package; accepted v4 remains separate
and unchanged. No game launch, deployment, Computer Use, assertion suppression
or installed-resource/settings modification was performed.

## User-reported in-game outcome — 10 October 2026

**Explicit user statement (verbatim):** “Alright, everything works, check repo, shadows work”.

**Disposition:** NPC nameplate shadow v1 is user-accepted as working in-game alongside already accepted NPC colors v4. The offline asset contract and packaging gates were documented before the test; this report adds live visual acceptance. User did not provide screenshots, color/snow stress-test details or separate reports on every HUD subsystem, so do not invent those observations or imply that unrelated subtitle/menu text shadows were changed. No further NPC shadow iterations are requested unless user reports a visual problem. Move the active milestone to independent English Gentium Book typography, maintaining separate reversible modules and the no-Computer-Use instruction.

## Exact private package and input provenance

ZIP:
`C:\Dev\witcher-ui-overhaul\deploy\npc-shadow-private-v1\QuietEditorial-NPC-Shadow-v1-private-test.zip`

Size: **60,887 bytes**. SHA-256:
`fc70ac02870ca08998c37df03215d84783a5a013e2e8ea681ba920c2a922fc51`.

| Input/output | SHA-256 |
| --- | --- |
| Current installed vanilla EnemyFocus, re-read from startup.bundle | `8b5c7cf0cb0e61fd005239689e096c9c5da9e3f1aa2182f9f88c71057903a76e` |
| Original installed native authoring SWF, copied baseline | `f84544e26c27b38e8b1f64ff8f77775743e1e6ecd7a4f1972fce381ed9a9e819` |
| Original filter-only source / unique import filename | `64ad2c80b96770ed0d09fa59f6ac4b00f5beb859276b8b0d60ace27d0a16cc17` |
| Saved Editor output (158,302 bytes) | `c331cdc12e8aae350d1dbbc1d3712df24ec0c108aa4d5544b97a8c56b1ab81ff` |
| Cooked / re-extracted resource (88,872 bytes) | `2f8e36a9d1d4e8598f889e85c3b1f9fdb28e8804e46e30ba520f0559d5c53ddd` |
| blob0.bundle | `2bb62213b08f87969a08ec49f22694feef7951ee461e85337ccbb25bcc150bfd` |
| Official metadata.store | `802d59f610cf43e096a046c6b4830f727ad84c900c1d80c09bb2075b5f0bf016` |
| Current isolated wcc_lite.exe | `9f448e0c8b9ea1ea803d0ae543f2fcd6e905088b8b71f54da2bff22c6cf318fc` |

Only these two ZIP members exist:

```text
Mods/modQuietEditorialNPCShadow/content/blob0.bundle
Mods/modQuietEditorialNPCShadow/content/metadata.store
```

The bundle has exactly one entry:
`gameplay/gui_new/swf/hud/hud_enemyfocus.redswf`.
The Editor's `hud_enemyfocus_qe_shadow_v1.redswf` is **copied into the isolated
runner at that canonical key** before cooking. The package contains neither
the unique import key nor Watermark nor scripts/fonts/configuration files.
The different internal linkage prefix is consistently
`hud-enemyfocus-qe-shadow-v1{22ca6d65}` for the movie/embedded texture references;
code, symbols and relative font imports remain identical. No opaque header or
linkage-string manipulation was used.

The transformation/tooling is original project code. Native SWF, cooked assets
and ZIP contain proprietary game-derived content and remain local/private.
No Easier to Read, Font of Life, other author binaries or third-party font
glyphs are used. Do not publish this archive as an original-source artifact.

## What is verified

- Expected-source preflight rejects an unchanged checked-out movie before
  cooking. The saved unique-name Editor result passes that gate.
- Current official cook, validate, pack and metadatastore each exit 0. Validate
  checks both the candidate and unchanged Watermark control: zero resource
  errors at every severity. Each command logs the same two ordinary startup
  assertions, with no `diskFile.cpp:2633` resource-monitor assertion.
- A complete ordered non-image tag comparison against current installed vanilla
  permits **exactly one changed sprite**, sprite63. Within it, character38,
  depth35, `mcNPCFocus.tfName` differs only by the approved shadow record.
  RGB #141718 / alpha166 / blur2x2 / strength1 / distance1; original angle,
  passes, compositeSource/inner/knockout flags remain. Every other non-image tag
  is byte-identical, including ActionScript, exports, text/font definitions,
  bounds, scale, health/quest/damage code, placement and visibility contracts.
- Frame rectangle/rate/count/version and seven atlas placement records match.
  Both resource/texture chunk CRCs validate; GUIWithAlpha/TCM_DXTAlpha, 540x64,
  resident0, one mip, pitch2160, alignment16 and 34,560-byte atlas are retained.
- All seven used image regions **and one-pixel borders** match vanilla exactly
  in visible RGB/alpha. Full atlas has 560 visible/alpha differences plus 45
  transparent-RGB differences outside those footprints, at distance >=2.
  All observed bitmap fills are clipped, and nearest/bilinear sampling is
  unaffected in the inspected model. Full-atlas byte equality is not claimed.
- Bundle bounds/codec/key are checked, with ZLIB re-extraction recovering the
  exact cooked bytes. Official metadata generation reports one bundle/one key,
  with expected key references. ZIP members are reopened, checked byte-for-byte
  and CRC-tested. Repeat packaging has the identical ZIP hash.
- A fresh read-only scan covers all 31 installed mod/DLC bundles, including
  disabled owners, and loose EnemyFocus files: **no competing resource owner**.
  V4 source/archive hashes remain unchanged. All 39 tests pass.

The Editor log records the unique-name exporter at 06:09:03 and a saved resource
at 06:09:09, without that attempt's overwrite/save cancellation. Thumbnail
generation warnings and missing dependency-index entries occur; later saved-file
loading, cooking and official resource validation succeed. Historical cancelled
attempts remain in the same log and must not be confused with this import.
Editor assertion state still reads `Asserts Disabled: ON`; its provenance and
full effect remain **unknown**, and fresh creation is not claimed assertion-free.
This package is supported by the saved-output consumer checks, not assertion
absence alone. No settings or suppression flags were changed.

## Reproduction

Original source preparation is in [source handoff](npc-shadow-source-handoff.md).
The unique SWF is a byte-identical copy under a new filename; only the user
operates the Editor import. Build from the already saved resource, using a fresh
output directory:

```powershell
python tools/verify-editor-assets.py --layout build/npc-state-expanded --workspace build/npc-editor-run/projects/quieteditorialnpcshadowtrial/workspace --control-workspace build/npc-editor-run/projects/quieteditorialnpcshadowgate/workspace --expected-native build/npc-shadow-source-v1/input/hud_enemyfocus_qe_shadow_v1.swf --enemyfocus-file build/npc-editor-run/projects/quieteditorialnpcshadowtrial/workspace/gameplay/gui_new/swf/hud/hud_enemyfocus_qe_shadow_v1.redswf --out build/npc-shadow-rebuild
python tools/compare-native-npc.py --native build/npc-shadow-source-v1/input/hud_enemyfocus.swf --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/npc-shadow-rebuild/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --out build/npc-shadow-rebuild/contracts.json
python tools/analyze-npc-atlas-padding.py --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/npc-shadow-rebuild/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --native-xml build/npc-shadow-source-v1/verified.xml --out build/npc-shadow-rebuild/padding.json
python tools/package-npc-shadow.py --build build/npc-shadow-rebuild --game "C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3" --out deploy/npc-shadow-rebuild
python -m unittest discover -s tests -q
```

The generic texture comparer reports non-image equality false because it does
not exempt a style edit; that is expected here. The packaging gate independently
requires precisely the approved filter delta and rejects any extra code/tag
change. No WitcherScript compilation is required: the archive has no script and
does not regenerate the working compatibility assembly.

## User-only installation and first acceptance test

1. Exit the game. In Vortex select **Witcher Compatibility Test**. Keep v4
   `modQuietEditorialNPCColorsV4`, FriendlyHUD, SAH and compatibility packages
   enabled; keep v2/v3 disabled.
2. **Install From File** using the exact ZIP above. Enable only this new shadow
   mod and Deploy. Confirm its two files route to:
   `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\Mods\modQuietEditorialNPCShadow\content\blob0.bundle`
   and the sibling `metadata.store`. No new scripts should be deployed or merged.
   No resource-priority adjustment is indicated by the current collision scan.
   If Vortex proposes a same-file conflict, different routing or compatibility
   replacement, stop and report it rather than choosing an arbitrary winner.
3. Load the same English save. Observe Roach and Vesemir at controller distance:
   their accepted v4 colors should remain, with a softer, lighter name shadow.
   Verify the font, size, position and labels are unchanged. Switch targets and
   reacquire them; reload the same save and repeat.
4. Use existing FriendlyHUD/SAH HUD hide/show controls. Check health/stamina,
   targeting, quest icons and damage displays where available. Hidden labels
   should remain hidden under the existing settings.
5. Compare bright snow/sky (first readability priority), foliage/fire and a dark
   interior/cave as convenient. Capture same-position before/after views by
   disabling/re-enabling **only** the shadow mod between fully exited sessions.
   Report missing UI, clipping, flicker, color changes or inadequate contrast.

This package has now been accepted by the user as visually working in-game. The detailed stress-test and compatibility coverage limitations described here remain distinct from that acceptance. Native sampler
state, full independent metadata-store consumer decoding and retail resolution
of the new internal linkage prefix are unverified; the static contracts and
official producer checks support testing, not certainty of runtime behavior.
FriendlyHUD/SAH/MHC compatibility is preserved structurally by unchanged scripts
and all non-style movie contracts; live integration needs the checks above.

## One-package rollback

Exit the game, disable **modQuietEditorialNPCShadow** in Vortex and Deploy.
Optionally remove that shadow mod from Vortex afterward. Keep v4 and all working
compatibility mods enabled. Its removal restores vanilla EnemyFocus shadow through
resource selection; no saves, settings or compatibility merges need restoring.

## Independent typography status

QuietFolio English Gentium v1 is now separately user-accepted in-game; its
package remains unchanged. NPC Shadow v1 remains the accepted visual baseline.
The active bounded extension is interaction v2 plus current HUD subtitle
shadows; see [Wave A source implementation](text-shadow-wave-a.md).
This does not authorize rebuilding accepted packages or broader roadmap work.
