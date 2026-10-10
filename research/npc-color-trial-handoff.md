# Private NPC color-only trial

## User in-game observation — 10 October 2026 (first trial)

**Explicit user report (verbatim):** “Yep, Vesimir is still bright green”. This followed installation instructions for the `QuietEditorial-NPC-Colors-private-test.zip` v2 package and the question whether the colors changed. The reported green NPC name is **not consistent with the intended VIP recolor** (`#5AFF00` to `#D5C08E`).

**Follow-up confirmation:** User confirms both the test mod is enabled in the intended Vortex profile and the deployed `Mods/modQuietEditorialNPCColors/content/scripts/local/quietEditorialNameColors.ws` path exists. These are user-reported checks, not an independent hash/loader verification. The green Vesemir label remains unchanged. Next diagnostic should distinguish whether the exact visible label belongs to EnemyFocus or Interactions and whether the OnTick wrapper loads/executes and successfully writes color. Do not change existing merge/profile settings to diagnose.

**Second explicit user observation (verbatim):** “Roach has also not changed his name, so not only vesimir”. This reports a second unchanged nameplate with the same installed trial. The user did not specify Roach's observed exact RGB here. **Inference, not established:** Roach and Vesemir may share a special/VIP category or a common renderer. These two observations do not prove all attitude categories fail. Record a hostile red-name target as a separate control only if needed; prioritize observing the live text-field route and whether the wrapper runs. No source modification or retest is claimed.

**Status: failed visual acceptance for this observed target; root cause undetermined.** Do not mark the palette runtime-valid. The report alone does not verify whether Vortex installed/enabled/deployed the correct v2 package, which profile was active at launch, whether the loose script loaded, whether `OnTick` executed, whether the actual label was `mcNPCFocus.tfName`, or whether another renderer subsequently overrode its `textColor`. The current code's exact-value mapping also ignores any variant RGB. Do not assert any of these explanations as established.

**Safe next diagnostic:** (1) confirm correct Vortex profile, mod enabled, deployed path and source hash, plus game startup/compile diagnostics; (2) if loaded, instrument the hook in a separate non-destructive build to distinguish method execution, target Flash-object path, read color, write result and subsequent resets. Avoid changing package 04, FriendlyHUD or SAH and do not rebuild Script Merger outputs. Compare another observed NPC category as a control. Disable the trial and redeploy while diagnosing if it produces no useful visual change. This report is a user observation, not an agent-run game test.


This is an original additive WitcherScript runtime experiment for English NPC
names. The movie, fonts and strong name shadow are unchanged. It does not
resolve the asset-import gate or claim completed visual acceptance.

## Local archive and verified scope

`C:\Dev\witcher-ui-overhaul\deploy\npc-colors-private-v2\QuietEditorial-NPC-Colors-private-test.zip`

ZIP SHA-256: `2ca0ca2ccded4d216aa2843021a24e570bbd959f8d2e916e79c7a5e62a69ba9d`

1,001 bytes; exactly one member:
`Mods/modQuietEditorialNPCColors/content/scripts/local/quietEditorialNameColors.ws`

Member SHA-256: `533d039bd5e1c44059691b69695a287a381133199d594c972d0457cf5096a260`.
ZIP CRC and byte-for-byte member readback pass. A second build from a fresh
output directory produces the identical ZIP SHA-256. It contains no game-derived
resource, compiled blob, third-party code, menu, settings file or compatibility
replacement. Source is original repository code; no reference author's binary
or modifications are redistributed. Generated ZIP and compilation files are
private and ignored by Git.

The installed Vortex Witcher extension **1.7.5** was inspected read-only.
Its `testSupportedTL` recognizes the `Mods` segment; `installTL` preserves the
member path, `testTL` selects type `witcher3tl` for a Mods destination, and
`getTLPath` deploys that type to the discovered game root. Therefore the archive's
explicit `Mods/` prefix routes to the intended destination. This is source-level
installer evidence, not an executed Vortex installation/preview. Extension
`index.cjs` SHA-256:
`52de6d815469d6361d72b94a11bfff79527b3846e644c2f8d471bbf2efcc3983`.
The earlier local v1 ZIP without that explicit prefix is superseded; use v2 only.

The sole annotation is `@wrapMethod(CR4HudModuleEnemyFocus)` / `OnTick`.
It calls `wrappedMethod(timeDelta)` once, preserves the Boolean event result,
then reads `GetModuleFlash().mcNPCFocus.tfName.textColor` through current imported
Flash-object methods. It writes only recognized current vanilla name RGB values.
Unknown/already mapped values are untouched. There is no target cache, alpha,
visibility, health, damage, filter, size, font or position write.

| Category | Vanilla RGB | Experimental RGB |
| --- | --- | --- |
| Neutral | `#79B8FD` | `#E9E2D2` (233,226,210) |
| Friendly | `#D3A37D` | `#B4C0A0` (180,192,160) |
| Hostile | `#FF0000` | `#D6A093` (214,160,147) |
| Axii | `#FCB549` | `#B4C2D1` (180,194,209) |
| VIP | `#5AFF00` | `#D5C08E` (213,192,142) |

These Field & Folio values are experimental. Hostility remains signaled by the
unchanged health, targeting and attitude layout as well as hue. No typography
replacement is included.

## Compilation evidence and regression criterion

Current official compiler SHA-256:
`9f448e0c8b9ea1ea803d0ae543f2fcd6e905088b8b71f54da2bff22c6cf318fc`.
All four freshly compiled cases use copies of the same known-working
`C:\REDkitProjects\witchercompatibility\compatibility-validation\analog-gait`
base/patch assembly. Each exits 0, reports successful patch compilation, emits a
nonempty blob and has zero Script/WCC errors.

| Case | Blob bytes | Assertions | Warning markers |
| --- | ---: | ---: | ---: |
| Baseline | 52,978 | 23,591 | 819 |
| No-op EnemyFocus OnTick wrapper, return preserved | 53,101 | 23,592 | 819 |
| No-op CR4ScriptedHud OnTick wrapper | 53,058 | 23,592 | 819 |
| RGB candidate, return preserved | 53,692 | 23,592 | 819 |

In **each** added-wrapper case the exact diagnostic difference is one
`scriptCompiledCode.cpp:56 (!m_sourceFile.Empty())` assertion, with no removed
assertions and no added/removed warnings. Thus the diagnostic is reproducible
without color APIs and on a different, already wrapped HUD target. It is not
specific to this RGB implementation. Its engine-internal cause remains unknown;
this evidence supports accepting this controlled diagnostic for a private trial,
not suppressing assertions or declaring the compiler clean.

The package gate requires successful baseline and both controls and candidate,
unchanged source inputs, the exact one-diagnostic delta shared by both controls,
no warning delta and the exact candidate source hash. New compiler sites,
additional occurrences, changed warnings, errors or mismatched input hashes
fail closed. Five regression tests exercise acceptance and rejection cases.

The tested assembly includes known-working SAH annotations and Monster Hunt
Contracts' EnemyFocus OnTick wrapper. Their live sources and the FriendlyHUD
whole-file EnemyFocus provider match the compiler assembly after encoding/newline
normalization. The Monster Hunt wrapper only adjusts ordinary health alpha and
delegates/preserves the original event result; this trial delegates the complete
chain and changes only the name color. SAH's HUD OnTick/visibility, ShowDamageType
and SetDodgeFeedback hooks remain in the assembly. No merge is regenerated.

Seven enabled compiled mods are not recompiled as retail blobs:
BloodAndSteel, GwentDeckChoice, brothersinarms, sharedutils, TopNotchSwordsFix,
smoothmap and EvilsOfRivia. The working retail multi-blob stack is not exactly
simulated by this source assembly. That limitation remains an explicit first
runtime-test gate; it is not evidence that these seven mods are incompatible.
No claim of full-profile runtime validation is made. Current CDPR documentation
supports annotated events and runtime script annotations.
[CDPR changelog](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/12058625/Changelog)

Init in the live module obtains `mcNPCFocus`; native movie code exposes `tfName`
and `textColor`; all used API signatures compile. No unsupported Flash-handle
Boolean checks are used. Binding lifetime on loading, reload and HUD teardown,
actual wrapper execution order with compiled mods and AS updates between ticks
remain runtime uncertainties. Rapid target and attitude changes need testing:
the original chain runs first, the hook inspects the resulting RGB every tick,
and does not reuse a previous target classification.

## User-only installation and rollback

No installation, Vortex preview, deployment or game launch has been performed.

1. In Vortex select **The Witcher 3** and the existing **Witcher Compatibility
   Test** profile. Keep all current compatibility packages and settings enabled.
2. Use **Install From File** and select the exact ZIP above. Name it
   **Quiet Editorial NPC Colors — private test**. Inspect the installer/staging
   preview: the only game destination must be
   `Mods\modQuietEditorialNPCColors\content\scripts\local\quietEditorialNameColors.ws`.
   Stop if Vortex proposes nesting `Mods\Mods`, replacing any existing file,
   installing an asset/blob/settings file or routing to DLC.
3. Enable only this new mod and use Vortex's normal **Deploy Mods** action.
   It has a unique additive script path, so no before/after resource priority
   rule or compatibility merge is requested. Keep current priorities unchanged.
   Do not accept a request to overwrite/rebuild the functioning merged scripts;
   a reported conflict is grounds to disable this trial and investigate.
4. Launch normally as a user-controlled test. If script compilation reports any
   new error, stop and record it; do not reset settings or regenerate merges.
   Do not save over an existing save for this visual comparison.
5. Rollback: **disable this one mod**, then **Deploy Mods**. Existing scripts,
   movie and settings provide the previous appearance. Re-launch and verify.
   No compatibility package removal or manual file replacement is needed.

## First acceptance tests, in order

1. Successful script startup; load an existing save, reload, enter/leave dialogue
   and menus and travel/reload a level. Verify no new error, invalid Flash access,
   lost name, health bar or quest icon, and no HUD visibility regression.
2. Compare neutral, friendly, hostile, VIP and Axii names; rapidly switch targets,
   change attitude, lose/reacquire focus and inspect corpses, herb/quest targets,
   boss/miniboss and Monster Hunt contract health displays. No stale color.
3. Check hard lock, health/stamina/essence, damage numbers, dodge feedback,
   FriendlyHUD toggles and SAH combat/exploration fades against baseline.
4. At 1080p and 4K/controller distance compare daylight/foliage, snow/sky, bright
   walls/fire and cave/night. Keep camera, game settings and exposure comparable.
   Assess friendliness/hostility distinction and long English names. Record
   screenshots as **actual game results**, not this report's design predictions.
5. Disable/deploy this one package and verify vanilla colors return. The name
   shadow must remain unchanged in both runs; a shadow improvement is not claimed.

## Reproduction

```powershell
python tools/compare-npc-wrapper-diagnostics.py --runtime build/native-npc-reproduce/runtime --assembly 'C:\REDkitProjects\witchercompatibility\compatibility-validation\analog-gait' --out build/npc-wrapper-controls-new
python tools/package-npc-color-trial.py --controls build/npc-wrapper-controls-new/receipt.json --game 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3' --settings 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\mods.settings' --out deploy/npc-colors-private-new
```

Fresh output directories are required. The archive tool packages original loose
source only; diagnostic blobs are deliberately omitted. Local build receipts
record every compiler source hash, command, diagnostics and blob hash.
