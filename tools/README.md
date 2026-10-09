# Tools

Reproducible local resource analysis, build and validation helpers belong here. No live game changes without explicit approval.

## Read-only audit

Python 3.14 was used. No external Python libraries are required. QuickBMS and its
Witcher BMS are read from the existing installed Script Merger; the helper writes
only inside this workspace's ignored build/audit. Input packages remain unchanged.

```powershell
python tools/audit-ui.py --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --redkit 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit'
python -m unittest discover -s tests -v
```

Optional deeper XML/decompilation uses [JPEXS 26.3.0](https://github.com/jindrapetrik/jpexs-decompiler/releases/tag/version26.3.0).
Download the portable author ZIP to ignored build/tools, extract into
build/tools/ffdec, and add `--ffdec build/tools/ffdec/ffdec.jar` to the audit
command. Java 8+ is required. No JPEXS or REDkit binaries are included in Git.
Original inspect logic supports both observed POTATO70 index layouts and
validated nested FWS/CWS/CFX streams, including stripped zero-glyph fonts.
It is not a cooker, CR2W writer, complete GFx decompiler or runtime validator.
Unknown formats/truncated payloads fail; JPEXS output itself stays ignored.

Outputs: reference-files.json (package hashes), references.json (payload keys,
glyphs/tag hashes), installed-bundle-index.json (resource owners, including
loose movies), baselines.json (selected current input hashes), nested gfx/,
xml/, decompiled/ and surface-facts.json. Full strings/decompiled game code
are never committed. Avoid interpreting character IDs across different movie
versions without matching sprite/linkage context.

## Licensed browser preview

```powershell
powershell -NoProfile -File tools/get-preview-fonts.ps1
```

This downloads Gentium Book 7.000 from SIL and Alegreya/Source Sans 3 from the
upstream Google Fonts repository into build/fonts, preserving licenses and
checking the inspected font hashes. It installs no system fonts. A changed
upstream font fails the hash check and requires review before updating pins.
No font binary is copied from the reference mods.

Open design/comparison.html locally. For repeatable PNGs, use Playwright with
installed Edge (headless) and a Node runtime. On this machine:

```powershell
$env:NODE_PATH='C:\Users\micha\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
& 'C:\Users\micha\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' tools/render-comparison.cjs
```

The script verifies font loading and writes scene screenshots/receipt only to
ignored build/comparison. It does not launch the game. Missing system Edge or
Playwright is an explicit environment prerequisite, not an automatic installer.

`python tools/contrast.py` reproduces the synthetic contrast table from
src/palette.json and writes build/comparison/contrast.json. It includes no game
scene measurements, black-edge contribution or HDR conversion.
