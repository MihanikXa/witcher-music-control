# Controlled SWF state investigation

**Historical report at commit 33ae2f6.** The 10 October
[bounded Editor investigation](editor-workflow-bounded.md) reached project setup
but desktop input failed before import. The asset gate remains blocked. The
[color-only handoff](npc-color-trial-handoff.md) supersedes this report's fallback
packaging block: two valid no-op wrappers reproduce its single extra metadata
diagnostic without warning regressions, enabling a narrow private RGB trial.

9 October 2026; starting commit `6555e46`; English NPC typography/text styling
only. **Asset pipeline remains blocked. No bundle, ZIP or visual variants.**

The assertion is now localized to the **fresh SWF import/creation path** across
three movies, including one without bitmaps. It persists after repairing depot
attachment and most bootstrap omissions. The same generated resources load,
resave and cook without that resource-state assertion. No defect was found in
the checked serialized EnemyFocus contracts, but the root cause and full runtime
risk remain **unresolved**. A verified environment-specific toolchain defect is
not claimed without the supported complete editor initialization comparison.

## Initialization evidence and controlled cases

The installed layout is `bin/x64_RedKit/wcc_lite.exe`, `bin/gameconf.cfg`,
`bin/config`, `bin/tools/GFx4`, and root `r4data`. The earlier staging layout used
`runtime/`, adjusted relative paths and omitted important initialization inputs.
The new runner mirrors the physical installed layout and copies the unchanged
installed gameconf. It preserves `engine/textures/texturegroups.xml` throughout.

CDPR documents a virtual depot with workspace > uncook > r4data precedence;
locked source assets require checkout into the project workspace before editing.
Our minimal CLI stage was not equivalent to that initialization. The expanded
stage supplies current engine/game resources, script sources and native script
cache, GUI XML, all shipped PC sound banks and the shipped local string DB. It
does **not** clone the complete game uncooked depot or claim a fully initialized
editor. [CDPR virtual depot and source control](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/39190599/Virtual%2Bdepot%2Band%2Bsource%2Bcontrol?atl_f=content-tree)

Native inputs, untouched in every import:

| Movie | Bitmap count | Native SWF SHA-256 |
|---|---:|---|
| EnemyFocus | 7 | `f84544e26c27b38e8b1f64ff8f77775743e1e6ecd7a4f1972fce381ed9a9e819` |
| Crosshair | 2 | `5256cae12ab73aa3402152c3e3ee7967dfcc53a191939d048cfd937a018adf3a` |
| Watermark | 0 | `f4378bc7aac493950881a96625f67816613390c675a626bcbc7258baa1d8e994` |

These controls are investigation inputs only, never proposed mod replacements.

| Case | Startup assertion count | Additional diskFile assertions | Actual outcome |
|---|---:|---:|---|
| Mirrored layout, minimal data | 329 | 3, one per movie | Three fresh imports; cook/validate exit 0 |
| Expanded current bootstrap | 2 | 3, one per movie | Missing map/script-class assertions disappear; three imports/cooks |
| Expanded, explicit depot selectors | 1 | 3, one per movie | Trailing-slash depot assertion disappears; fresh outputs in isolated project workspace |
| Same explicit routing, serial execution | 1 | 3, one per movie | No port collision; same resource assertion |
| Serial, Windows depot separators | 1 | 3, one per movie | Same assertion; no cancelled overwrite |
| Load/resave generated resources, correct project root | 1 | 0 | Three loaded and resaved successfully; subsequent cook also has zero resource assertions |

The remaining startup assertion is missing `ly_animal_dog.bnk`, even with all
886 shipped PC bank files copied. Other startup diagnostics concern unavailable
legacy configuration, optional Wintab and missing Documents `base/` lookup
paths. These are retained in logs, not suppressed. The main expanded run copied
4,956 input records (3,534,989,603 bytes including duplicate ledger entries).
Input hashes/mtimes and Documents snapshots were unchanged.

The exact startup selectors `-uncookDir` and `-workspaceDir` were recovered from
the **installed current WCC binary** beside its startup/log options. They are
not invented commandlet flags or asserted to appear in public SWF documentation.
A bounded help probe and actual import verified acceptance: a local uncook root
and project root ending in backslashes remove the depot assertion; generated
files land in `<project-root>/workspace/<resource-key>`. Passing the physical
workspace instead of its project root misroutes the virtual depot.

An overlapping help/compiler probe reported port binding failures. It was not
used to infer the assertion's cause. The subsequent serial import listened on
37000/37010 normally and reproduced all three resource assertions.

Official current `resave` help supplies `-tmpdir`, `-path`, `-ext` and
`-ignorefileversion`. Forward-slash `-path` was rejected by directory.cpp 83/132;
the Windows-separator attempt with the physical workspace could not find the
base directory. Correct Windows path plus the **project root** loaded all three
resources and reported three successes, zero failed/unloadable resources and
three copied to the isolated depot. This was a real load/save control, not an
overwrite cancellation. It still logs empty-filename read failures; no clean
all-diagnostics toolchain pass is claimed. No streaming reset, version patch,
assertion toggle, guessed header or older compiled movie was used.

## Serialized contracts and atlas visibility risk

Expanded EnemyFocus cook and the post-resave cook retain byte-identical ordered
non-image tags, including full ABC, symbols, nested timelines, placements, shapes,
text definitions and font imports; movie header/frame data also matches runtime.
Both chunks' CRCs validate, one texture handle resolves to the embedded atlas,
and external-image linkage names match their texture linkage. The atlas retains
540 × 64, GUIWithAlpha/TCM_DXTAlpha, resident index 0 and one 34,560-byte mip.

Every used subimage and its one-pixel border matches runtime alpha and visible
RGB exactly. Expanded cook has 560 differing alpha texels and 26 transparent-RGB
differences outside those footprints; post-resave cook has 609 and 46. Different
linkage strings and unused atlas data preclude byte-deterministic output claims.

All real bitmap fill references observed in native XML resolve to those seven
subimages. Fill types are 65 (smoothed clipped bitmap) or 67 (non-smoothed clipped
bitmap), not repeating fills; these type constants and the ignored 65535 marker
are cross-checked against [JPEXS FILLSTYLE source](https://github.com/jindrapetrik/jpexs-decompiler/blob/master/libsrc/ffdec_lib/src/com/jpexs/decompiler/flash/types/FILLSTYLE.java).
Every visible difference is at least two texels
outside the exclusive subimage rectangles. Therefore the differences cannot
affect the **stated clipped nearest/bilinear, single-mip sampling model**. The
actual runtime sampler/driver path has not been captured: this is a conditional
rendering assessment, not in-game proof or a claim that every possible filter is
safe. No manual padding sanitization was performed.

The observed defect boundary is fresh creation versus loaded serialization,
not EnemyFocus, image count, mip configuration, slash spelling or the removed
depot assertion. The likely explanation is monitor-state handling in the fresh
import path; that is an **inference**, not a source-confirmed engine diagnosis.
Structural integrity after loaded resave is encouraging but cannot prove that
the original assertion has no lifecycle or rendering consequences. The remaining
incomplete initialization is a real limit on classification.

## Script fallback: source scope and real compiler correction

The original failed staging loaded whole-file AutoLoot overrides into the base
while `local/modAutoLootConfig.ws`, defining SAutoLootFeedItem, remained in the
patch applied later. This is a forward-type/scope setup problem. The known
successful general-merge source assembly places dependencies in the base; a
copied baseline now compiles without SAutoLootFeedItem errors. No working script
was rewritten or moved in the actual profile.

The read-only reference is
`C:\REDkitProjects\witchercompatibility\compatibility-validation\analog-gait`.
Its EnemyFocus text matches the current FriendlyHUD provider after newline
normalization. Staged copies contain 1,708 base files and three pre-existing patch
files. Compiler output and all source hashes remain in ignored build.

The candidate initially failed three `void` → `Bool` conversions: Flash handles
do not support the proposed `if (!handle)` guards. Those unsupported guards were
removed from **our original hook only**. It follows the module's existing
initialized OnTick lifecycle, delegates wrappedMethod first, then uses current
GetModuleFlash/GetChildFlashSprite/GetMemberFlashObject/GetMemberFlashNumber/
SetMemberFlashNumber signatures. Both copied baseline and corrected candidate
now pass the official current compiler with real nonempty blobs and zero WCC
script errors. This validates event wrapping and those API signatures in this
source assembly, not live binding lifetime or complete deployed compatibility.
Both logs contain 819 warning markers. Baseline has 23,591 assertion markers;
candidate has 23,592. The added assertion is
`scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())`, a source-metadata diagnostic
whose cause is not resolved here. These are **compiler success receipts, not
clean assertion-free compilation**; the extra assertion is another explicit
reason not to package. Output blobs are 52,978 and 53,657 bytes respectively.
The current release documents support for annotated events.
[CDPR current commandlet/script changelog](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/12058625/Changelog)

Seven enabled opaque compiled mods remain outside exact compilation coverage;
the assembly is not an exact retail multi-blob load-order reproduction. The
wrapper's initialization/teardown, target switching and coexistence with those
blobs remain tests. No fallback ZIP is produced. Palette and shadow specifications
remain unchanged; Gentium and broader UI work are deferred.

## Reproduction and stopping point

Run CLI engines serially because they share service ports. These diagnostic
tools cannot pack, deploy or claim a verified pipeline:

```powershell
python tools/investigate-swf-state.py --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit' --settings-directory 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3' --out build/npc-state-fresh --bootstrap expanded --attach-depots --resave-control
python tools/compare-native-npc.py --native build/npc-state-fresh/input/hud_enemyfocus.swf --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/npc-state-fresh/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --out build/npc-state-fresh/contracts.json
python tools/analyze-npc-atlas-padding.py --vanilla build/audit/vanilla/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --cooked build/npc-state-fresh/cooked/gameplay/gui_new/swf/hud/hud_enemyfocus.redswf --native-xml build/native-npc/native.xml --out build/npc-state-fresh/padding.json
python tools/check-npc-fallback.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --settings 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\mods.settings' --runtime build/native-npc-reproduce/runtime --assembly 'C:\REDkitProjects\witchercompatibility\compatibility-validation\analog-gait' --out build/npc-fallback-fresh
python -m unittest discover -s tests -v
```

Fresh output directories are required. Local actual receipts are under
`build/npc-state-layout`, `build/npc-state-expanded` and
`build/npc-fallback-assembly-fixed`. The current manifest retains earlier
investigations and records these cases, hashes and limits. Fourteen synthetic
inspection/diagnostic tests pass; they are not engine or Vortex tests.

**Shortest asset next step:** one supported Editor Flash import/checkout in a
new isolated project, using the already generated current uncooked depot
read-only, with EnemyFocus and Watermark as controls. Compare its new-resource
state and outputs to this CLI case before doing any styling. This requires a
demonstrably isolated editor configuration; do not launch against the working
compatibility project or regenerate the depot. If the same assertion occurs,
prepare the current-version three-movie reproduction for a confirmed CDPR fix;
do not keep changing unrelated bootstrap files.

**Shortest fallback next step:** establish exact compiled-dependency/annotation
coverage for the live profile or a supported equivalent compiler assembly and
resolve the candidate's additional source-metadata assertion before packaging
the now compiling hook. Do not mistake a source-only pass for that
coverage and do not rewrite compatibility scripts to achieve it.

Generated ZIP path: **none**. Installation/rollback handoff is deferred because
neither package gate passed. First eventual game tests remain unchanged control,
name/health/quest/target behavior, FriendlyHUD and SAH visibility/fades, then
separate color/shadow comparisons in daylight/snow/bright interiors/caves at
1080p/4K and controller distance. For the fallback also test HUD initialization,
reload, teardown and rapid category changes. No installed game/REDkit asset,
Vortex deployment, Documents settings or save was modified; no game/editor
launch or installation occurred.
