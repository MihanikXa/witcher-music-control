# Clean NPC Colors v4 production trial

The user observed v3 change both Roach and Vesemir to cyan and then lighter
palette-like colors, which persisted during observation. This establishes a
working visible field/write route for those targets. No phase-specific numeric
readings were supplied. **Number-versus-UInt conversion is the leading v2
failure hypothesis, not a proven diagnosis.** The separate primitive accessors
are declared in the installed `flashScriptImports.ws`; the native implementation
and exact v2 returned values have not been traced. V3 also differed in timing,
registration and write sequence. V4 still requires its own in-game acceptance.

## Smallest original correction

`src/npc/quietEditorialNameColors.ws` now contains one additive EnemyFocus
OnTick wrapper. It delegates once and preserves the original result on every
exit. It reacquires `GetModuleFlash()` → `mcNPCFocus` → generic `tfName`, the
same field access used successfully by v3, and reads/writes `textColor` using
UInt. It skips empty text and unknown RGB values. No timers, fields, cached
targets/handles, notifications, logs, cyan override, console command or
English-name restriction remain. No HUD or UpdateName wrapper is needed.

| Category | Observed vanilla RGB | Intended RGB |
| --- | --- | --- |
| Neutral | `#79B8FD` / 7977213 | `#E9E2D2` / 15327954 |
| Friendly | `#D3A37D` / 13869949 | `#B4C0A0` / 11845792 |
| Hostile | `#FF0000` / 16711680 | `#D6A093` / 14065811 |
| Axii | `#FCB549` / 16561481 | `#B4C2D1` / 11846353 |
| VIP | `#5AFF00` / 5963520 | `#D5C08E` / 14008462 |

The current field RGB determines the mapping; no target category or old RGB
is cached. A new target/category or game-driven reset is therefore rechecked
after the normal method chain. Already-mapped RGB causes no setter call.
This uses one color read on each tick with nonempty name text, rather than
assuming all Flash resets coincide with UpdateName or target changes. Deferred
Flash assignments can still win within a frame; a subsequent tick retries if
the RGB is again vanilla. Immediate, flicker-free rendering is a runtime test.

Initialization follows the established native/FriendlyHUD EnemyFocus tick
lifecycle and its Flash bindings. Handles are reacquired after the original
method; empty text causes no write, and no unsupported Boolean/null conversion
of Flash handles is introduced. This does not independently prove native
handling of an unavailable movie before the engine delivers configured ticks.
Reload and HUD recreation are explicit acceptance checks. Hidden labels may
be recolored, but visibility is never changed or used to force the HUD open.

Only the name's `textColor` changes. The five constants are retained exactly.
Health, damage, quest icons, targeting, name strings, fonts, shadows and all
working compatibility scripts remain untouched. MHC/SAH OnTick chains are
preserved. No compiled blob or full replacement script is distributed.

## Validation and private package

Exact ZIP:
`C:\Dev\witcher-ui-overhaul\deploy\npc-colors-private-v4\QuietEditorial-NPC-Colors-v4-private-test.zip`

ZIP SHA-256: `94f39861fa552d7a3353c17831a55751171a321b3df8a73c211f995bb690036e`.
Member SHA-256: `1b9d70f775ac1cf4173739fa01325d65ead2bdb9c1aeb363dac548c03f6b82b7`.
Archive is 1,197 bytes, with one original WS member. CRC/readback pass and an
independent packaging repeat produced the identical archive hash.

All four official compiler runs exit 0, with zero Script/WCC errors and 819
warnings each. Baseline has 23,591 diagnostic assertions; both no-op controls
and candidate have 23,592, with only the shared source-metadata assertion added.
No assertions are removed and no warning delta occurs. Output blob sizes are
52,978 / 53,101 / 53,058 / 53,746 bytes respectively; blobs are not packaged.
The existing 23 tests pass. Read-only snapshot verification covers the deployed
trial scripts, FHUD/SAH/MHC sources and mods.settings; all 78 files remain unchanged.

See `research/phase2-manifest.json` → `npc_colors_v4` for exact input/source,
compiler, receipt, ZIP/member hashes and commands. Generated assets and logs
remain in ignored build/deploy directories. The source is original project
code for this private test; no third-party implementation, font or game asset
is redistributed. Reference authors' licenses are therefore not invoked.

The compiler regression criterion is the established baseline versus one no-op
EnemyFocus wrapper, one existing HUD-wrapper control, and candidate. It requires
real output blobs, zero Script/WCC errors, exactly the same single added source
metadata diagnostic, no other assertion changes and no warning delta. Current
FHUD/SAH/MHC affected source providers must match the copied tested assembly.
Seven opaque compiled mods remain outside exact retail multi-blob simulation.
Static/compiler checks do not prove in-game acceptance.

V4 has its own mod ID `modQuietEditorialNPCColorsV4`. V2 and v3 must both be
disabled; their hooks are intentionally excluded from the intended profile's
package collision check, without modifying that live profile. There is no
priority change or Script Merger regeneration required by this additive source.

## User-only installation and test

1. Exit the game. Select **Witcher Compatibility Test** in Vortex. Disable
   `modQuietEditorialNPCColors` (v2) and `modQuietEditorialNPCProbe` (v3), then
   deploy. Leave both installed but disabled. Keep compatibility packages enabled.
2. Install `deploy/npc-colors-private-v4/QuietEditorial-NPC-Colors-v4-private-test.zip`
   via **Install From File**, enable v4 and deploy. Its sole member routes to
   `Mods/modQuietEditorialNPCColorsV4/content/scripts/local/quietEditorialNameColorsV4.ws`
   below the game directory. If the preview proposes another route, replacing
   compatibility files or merging scripts, stop and report it.
3. Load the same English save. Roach should be warm ivory `#E9E2D2`; Vesemir
   should be muted brass `#D5C08E`. No cyan or diagnostic notifications should
   appear. Observe each for 20 seconds and record persistent color/flicker.
4. Switch repeatedly between them and an empty target, then reacquire each.
   Check neither retains the other's color or briefly reverts repeatedly.
5. Reload the same save; repeat both checks. Use your existing HUD hide/show
   controls and reopen the pause/menu UI, then reacquire. Names should return
   in the intended colors while FriendlyHUD/SAH visibility behaves as before.
   Check ordinary health/quest/target indicators still work. No settings changes
   or new save is needed for this test.
6. **One-mod rollback:** exit, disable v4 and deploy, leaving v2/v3 disabled.
   Reload the same save; original name colors should return. Do not manually
   delete game scripts, alter saves or regenerate compatibility merges.

## Reproduction

```powershell
python tools/compare-npc-wrapper-diagnostics.py --runtime build/native-npc-reproduce/runtime --assembly 'C:\REDkitProjects\witchercompatibility\compatibility-validation\analog-gait' --out build/npc-colors-v4-fresh
python tools/package-npc-color-trial.py --v4 --controls build/npc-colors-v4-fresh/receipt.json --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --settings 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\mods.settings' --out deploy/npc-colors-v4-fresh
```

Build tools only copy/read current inputs and write private build/deploy output.
No installation, deployment, settings write or game launch is part of the build.
