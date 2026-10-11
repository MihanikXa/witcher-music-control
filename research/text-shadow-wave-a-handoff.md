# Wave A private trials — offline validated, runtime acceptance pending

11 October 2026. User-performed imports are complete. The current official
5.01 cooker, validator, packer and metadata producer pass for interaction v2,
the unchanged current-HUD subtitle control and its shadow-only candidate.
No installation, deployment, game launch, live resource/settings/save change or
Computer Use occurred. Accepted font/NPC packages and archived interaction v1
remain unchanged. The broader UI shadow rollout is still deferred.

## Exact private archives and routing

**Interaction v2**, 289,751 bytes:

`C:\Dev\witcher-ui-overhaul\deploy\field-folio-interactions-private-v2\Field-and-Folio-Interactions-v2-private-test.zip`

SHA-256: `b9e5b84d9d10b98e2d2818ff538cc0ad210f5922bbe7798862de5f4c455b3a2d`

```text
Mods/modFieldFolioInteractionsV2/content/blob0.bundle
Mods/modFieldFolioInteractionsV2/content/metadata.store
Mods/modFieldFolioInteractionsV2/OFL-Adobe.txt
Mods/modFieldFolioInteractionsV2/FONT-NOTICES.txt
```

Its bundle owns only `gameplay/gui_new/swf/hud/hud_interactions.redswf`.
Source Sans 3 Regular remains selected by direct FontID218; both independently
licensed utility definitions 218/219 retain their original glyph records.
DefineEditText 215 is now 340 twips/17px. Only its `tfActionName` placement,
sprite216/depth1, converts the heavy black glow to #141718/166, blur2,
strength1, distance1, NPC angle 51471/65536, passes1 with original compositing.
Text bounds, foreground colors, matrix, icons, normal/held instances, code,
timelines, visibility and hold/key/controller behavior remain unchanged.
Adobe OFL and derivative identity notices are unchanged and included.

**Subtitle shadow v1**, 43,962 bytes:

`C:\Dev\witcher-ui-overhaul\deploy\subtitle-shadow-private-v1\QuietEditorial-Subtitle-Shadow-v1-private-test.zip`

SHA-256: `6eb5afeb0459b29a545c29637651d0deb5f4488170c560162d9579c24e1951f3`

```text
Mods/modQuietEditorialSubtitleShadow/content/blob0.bundle
Mods/modQuietEditorialSubtitleShadow/content/metadata.store
```

Its bundle owns only **`gameplay/gui_new/swf/hud/hud_subtitles.redswf`**, the
current root loader path corroborated by installed Outfit Wheel ABC. The older
`witcher3` subtitle movie is not replaced. Root `tfSubtitles`, character1/depth1,
retains its existing DropShadow type, angle and passes3, with #141718/166,
blur2, strength1 and distance1. Authored 26px, runtime **26 + SubtitleScale**,
font aliases, HTML, wrapping, width, position and subtitle behavior are intact.
No fonts, textures, scripts, settings, NPC asset or other movie is packaged.
Poster subtitles and separate dialogue-choice/previous-line movies are not
covered by this subtitle module.

## Verification evidence

| Build | Cooked resource SHA-256 |
|---|---|
| Interaction v2 | `35baf8d672112e3fbc693419d432d3a15d9909f6c3b20c58b855689f01f67a31` |
| Subtitle v1 | `b010c79c9e9e067cdbee8512e1676bc5c407d3b68b43ccf7d989ca7ab7d885e4` |

Detailed input, saved-asset, bundle, metadata and archive member hashes are in
[the manifest](text-shadow-wave-a-manifest.json). Original source proofs and
provenance are in [the source implementation report](text-shadow-wave-a.md).

- Saved imports match the pinned independently decoded source contracts.
- Successful official commands each exit 0; resource validation reports one
  file and zero resource errors. Only the two established CLI startup assertion
  sites, depotDirectory.cpp:11 and soundFileLoader.cpp:101, occur. No diskFile
  resource-state assertion occurs in these successful saved-resource builds.
- All source font/code/symbol/timeline contracts remain exact. Interaction's
  two **complete compressed atlas payloads**, dimensions, handles, linkages and
  used regions match vanilla; transparent pixels also match. Subtitle has one
  valid CSwfResource, no bitmap dependencies, empty/absent font/texture arrays,
  consistent official ExporterInfo linkage and valid CRC.
- Both bundles contain exactly their intended one resource. Official metadata
  inventories one bundle/entry with the canonical key; independent ZLIB
  extraction reproduces the cooked bytes. Metadata was not hand-written.
- ZIP CRC, exact members, full readback and Mods routing pass. Each module's
  second independent packaging run reproduces its archive hash.
- Current read-only ownership scan finds only archived/deployed interaction v1
  on the interaction key, an intentional replacement. Subtitle has no deployed
  movie owner. Unexpected owners fail packaging; no priority winner is guessed.
- **83 tests pass**, including guards rejecting stray subtitle texture/font
  dependencies, bad linkage/CRC and changed source-transformation inputs.

Full independent metadata-store consumption and every opaque font-descriptor
field are not separately decoded. The official producers/consumers, exact
movie/font/atlas comparisons and prior working family linkage support private
runtime tests; they do not prove game appearance or all compatibility states.

## Bounded failures retained, not bypassed

The first interaction cook failed during startup, exit 0x80000003, with logged
Windows **1455** commit-page failures; PowerShell also reported out-of-memory.
A subsequent read-only memory snapshot showed availability recovered to about
7.1GiB of commit and 16.4GiB physical, with no Editor/WCC process active. One
fresh retry using unchanged inputs, compiler and command succeeded. This
supports an environmental startup failure, without proving every causal detail.
The failed output/logs remain local in `build/interactions-v2-candidate`.

The subtitle control's first metadata stage exceeded its 60-second budget during
script initialization, before bundle processing. Its successful cook/validate/
pack stages were retained and rechecked; a **single metadata-stage resume**
with a 120-second Python process timeout succeeded. Original failure commands
and stdout are retained as `.first-timeout` files. Candidate metadata uses the
same bounded 120-second timeout and succeeds. No REDkit command flags, assertion
settings, installed files, opaque headers or earlier compiled assets were
changed to bypass either failure.

The Editor log reports **Asserts Disabled: ON / Data Asserts Disabled: OFF**;
their provenance/effect remain unknown. During shutdown, after “Shutting down
game engine” and while collecting unreachables, it logs diskFile.cpp:2633 for
**all three** new resources, including the unchanged subtitle control. Later
saved-resource loads/cooks/validation succeed without that assertion. The
monitor-state cause remains unresolved; this is not an assertion-free Editor
claim or a proved serialized-resource defect. No suppression was performed.
Raw evidence is private at `build/text-shadow-wave-a-editor-evidence/editor.log`.

## Exact user installation and first tests

1. Close the game; select **Witcher Compatibility Test** in Vortex.
2. **Disable interaction v1** (`modFieldFolioInteractions`) but keep its archive
   and installation available. Install interaction v2 via **Install From File**
   using the exact v2 ZIP above, enable v2 and deploy manually. Never enable
   v1 and v2 together: both own the same movie despite different mod folders.
3. Keep **QuietFolio English v1, NPC Colors v4, NPC Shadow v1, FriendlyHUD,
   Seamless Adaptive HUD, Hoods and the compatibility stack** unchanged/enabled.
   Do not regenerate merges or adjust subtitle settings just for installation.
4. Check the same Talk-over-Vesemir and Talk-over-Peasant views. Action text
   should be clearly subordinate to NPC names. Verify long/held prompts,
   keyboard/controller art, hold completion/cancel, target switching and HUD
   hide/show. Check baseline alignment, clipping and no quest-icon overlap.
5. Separately install the exact subtitle ZIP via **Install From File**, enable
   and deploy manually. Check speaker/body text, ordinary cinematic dialogue,
   wrapped lines and current subtitle scaling. Test hide/show, reload and the
   alternative speaker route when available. Poster/choice text can remain
   unchanged because they use separate resources.
6. For each module compare bright snow/sky, foliage/fire and caves/interiors at
   actual resolution/viewing distance. Report readability, baseline shift,
   missing hints or other UI regression. Do not infer acceptance from parsing.

Deployed files belong under
`C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\Mods`, in the
exact mod folders above. Movies reside inside their bundles, not loose redswf
files. Unexpected conflicts beyond disabled interaction v1 require reporting
the owner, rather than assigning arbitrary resource priorities.

**Independent rollback:** close the game, disable/uninstall only
`modFieldFolioInteractionsV2`, re-enable preserved `modFieldFolioInteractions`
and deploy. Subtitle rollback: disable/uninstall only
`modQuietEditorialSubtitleShadow` and deploy. Keep accepted font/NPC packages
enabled; no save, settings or compatibility restoration is necessary.

## Remaining surfaces

Accepted NPC shadow is complete. Interaction/subtitle are offline-complete
private trials awaiting visual acceptance. Dialogue variants, quests and
oneliners are Wave B; notifications, menus, inventory, map and remaining
semantic/owned surfaces are Wave C. The [coverage ledger](text-shadow-coverage-ledger.md)
records them individually. Gwent's bounded XML export remains a static audit
blocker. No other surface has been changed or silently declared complete.

## Reproduce

Use fresh build/deploy output paths and the existing private runner. Run WCC
jobs sequentially; no additional imports are needed for these saved assets.

```powershell
python tools/verify-field-folio-asset.py --resource build/npc-editor-run/projects/quiettextshadowwavea/workspace/gameplay/gui_new/swf/hud/hud_interactions_ff_v2_17.redswf --expected-swf build/text-shadow-wave-a/input/hud_interactions_ff_v2_17.swf --baseline build/field-folio-source-v2/runtime.redswf --out build/interactions-v2-fresh
python tools/verify-subtitle-shadow-asset.py --resource build/npc-editor-run/projects/quiettextshadowwavea/workspace/gameplay/gui_new/swf/hud/hud_subtitles_qs_unchanged.redswf --expected-swf build/text-shadow-wave-a/input/hud_subtitles_qs_unchanged.swf --baseline build/text-shadow-source-v1/runtime-hud.redswf --control --metadata-timeout 120 --out build/subtitle-control-fresh
python tools/verify-subtitle-shadow-asset.py --resource build/npc-editor-run/projects/quiettextshadowwavea/workspace/gameplay/gui_new/swf/hud/hud_subtitles_qs_v1.redswf --expected-swf build/text-shadow-wave-a/input/hud_subtitles_qs_v1.swf --baseline build/subtitle-control-fresh/cooked/gameplay/gui_new/swf/hud/hud_subtitles.redswf --metadata-timeout 120 --out build/subtitle-candidate-fresh
python tools/package-text-shadow-wave-a.py --module interactions --candidate build/interactions-v2-fresh --control build/field-folio-control-v2 --game "C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3" --out deploy/interactions-v2-fresh
python tools/package-text-shadow-wave-a.py --module subtitles --candidate build/subtitle-candidate-fresh --control build/subtitle-control-fresh --game "C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3" --out deploy/subtitle-v1-fresh
```
