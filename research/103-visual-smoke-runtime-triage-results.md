# 103 — Notification duration unit defect; minimal V2 correction

2026-10-23. Follow-up to the user's negative report102 test. **A concrete defect in our own diagnostic is established: `ShowNotification` durations are milliseconds, but V1 supplied4 and12, intending seconds.** This is the strongest source-supported explanation for unseen messages. Runtime hook execution still has not been observed; this is not proof that presentation is the only problem.

## Read-only deployed-stack audit

Exact installed base **G**: `C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3`.

- `G\Mods\modWMCVisualSmoke\content\scripts\local\wmcVisualSmoke.ws` exists at the correct depth and SHA256 is **`4df1b9b7d83b653ab2ef56c9535ef492ad6868bad5a85361ace51e32a15dc81b`**, exactly report101's source/archive. No stale or different payload was found.
- Current Windows-resolved Documents `The Witcher 3/mods.settings` declares that mod Enabled1, Priority52, and consolidated music Enabled1, Priority50. Current Vortex deployment manifest contains its exact relative script path. These are disk observations, not proof the failed run compiled or executed the file. No private Vortex database or unrelated history was exported.
- `mod0000_MergedFiles` is declared Enabled1/Priority2. Its `content/scripts/game/r4Game.ws:834` retains the native post-load event, and `:718` requests OverlayPopup during game initialization. FriendlyHUD's corresponding event is at`:836`. Inspected post-load annotation wrappers in `modMonsterHuntContracts/.../mhcIntroduction.ws:186–193` and `modzzz_sharedutils/.../oneliners/annotations.ws:25–29` each call `wrappedMethod()`. No demonstrated bypass of our wrapper was found in those bodies; actual wrapper composition remains unobserved.
- Merged `game/player/r4player.ws:493–605` retains `OnSpawned`, superclass initialization and repeating native CombatCheck timer setup. Installed `content/content0/scripts/engine/entity.ws:19` explicitly defines the third `AddTimer` argument as **repeats**. V1 uses that signature and a declared timer function. No blanket `RemoveTimers()` was found in the inspected merged player file. Timer delivery to an annotated timer function in this retail run remains unproved.
- V1's dependency/scene/pause/loading-video gates are legitimate source queries (report94); no source evidence establishes one as permanently true in ordinary gameplay. They can still prevent presentation, and V1 did not expose which gate blocked it.
- No deployed script override of `CR4GuiManager.ShowNotification` or the `CR4OverlayPopup` class was identified by the scoped script search. Bundled UI resource overrides and actual cached-code selection are **not** ruled out by that result. HUD script-mod Enabled flags on disk are distinct from the user's disabled HUD features; no further HUD toggles are proposed.

Preservation pins and selected Enabled/Priority values, with personal Documents path/Vortex installation identifiers omitted: [103-visual-smoke-triage-evidence.json](103-visual-smoke-triage-evidence.json). The deployed V1 hash and all audited input pins remained stable on a second read. No cache, merge, deployed script, settings, saves or music resources were changed.

## Concrete presentation defect

Exact REDkit UI source base **U**:
`L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\gameplay\gui_new\actionscript\red\game\witcher3\popups`.

| Source | Observed contract |
|---|---|
| G `content/content0/scripts/game/gui/r4guimanager.ws:1389–1406` | Duration passed to existing popup, or stored unchanged as popup initialization data. |
| G `content/content0/scripts/game/gui/popups/overlayPopup.ws:45–85,226–229` | Resolves Flash `showNotification` during `OnConfigUI`, then forwards duration as `FlashArgNumber` without scaling. |
| U `OverlayPopupMenu.as:127–145,261` | Direct and queued delivery forward `msgDuration`/stored duration unchanged to `notificationModule.show`. |
| U `NotificationModule.as:30–31,50,67–70,100–109,130–132` | Default duration4000; entrance tween0.3seconds; nonzero supplied duration used in `new Timer(_duration)`; timer expiry initiates hide tween. |
| G `content/content0/scripts/game/gui/r4guimanager.ws:897` | Vanilla explicit-duration caller passes9000, corroborating the millisecond scale. |

Flash timer delay is in milliseconds. V1's4/12 therefore request **4ms/12ms**, not4s/12s; nonzero values also bypass the4000ms default. Hide can start long before the300ms entrance tween completes and removes that entrance tween. Actual runtime frame/timer quantization and the exact active retail UI asset were not measured; do not claim a precisely4ms visible period or prove callback execution from this source finding.

**Diagnosis ranking:** D/presentation has a demonstrated unit error; A/script loading, B/callback execution and C/timer/readiness remain possible additional failures. Source compilation alone cannot eliminate them. Full enabled-mod assembly/cached retail scripts were not reconstructed or compiled in this task; neither priority assumptions nor pristine REDkit compilation are being presented as that proof. With a concrete local defect found, report102's minimal-correction branch is appropriate; a new multi-hook/multi-output probe would change more variables unnecessarily.

## Smallest correction and validation

V1 and its accepted archive remain unchanged. Separate original `src/diagnostics/wmcVisualSmokeV2.ws` changes only:

- Display durations **4→4000**, **12→12000**.
- Versioned field/method/timer identifiers and visible markers `WMCVIS1→WMCVIS2`.
- One unit-explanation comment.

Callback, timer interval, message spacing, bounds, readiness tests, context queries and native-method forwarding are otherwise exact. No new checkpoint, hook, global definition, audio call, saved field or settings dependency was added. `tools/visual_smoke_triage.py` rejects any extra source change and audits the local forwarding/timer contract; it makes no writes to installed files. `tools/visual_smoke_build.py` now accepts a versioned variant and preserves the actual duration in its constant-payload control.

Reproduce in a **fresh ignored** directory:

```powershell
python tools/visual_smoke_build.py --root build/<fresh-directory> --variant milliseconds-v2
```

Completed evidence: `build/visual-smoke-triage-v1/` (triage JSON, baseline/control/candidate blobs/results/stdout/full logs, complete tests).

- Pristine baseline, matched control and candidate all exit0 and produce blobs, with zero Script/WCC errors.
- Baseline20,893 native assertions; control/candidate20,897. Complete candidate/control diagnostic counters match. All share784 warnings plus15 Core/3 Engine errors; these inherited engine diagnostics are retained, not suppressed.
- All pinned installed compiler inputs unchanged; exact source-only ZIP readback passes.
- Four new tests cover source restoration, unchanged timer seconds, corrected UI milliseconds, control preservation and rejection of unknown contracts. **All309 repository tests pass.**
- No retail launch or actual UI delivery is claimed. No full enabled-mod compatibility proof. No new logger test, Wwise action, soundtrack edit or deployment.

## One precise next user action

**Perform one Vortex-managed replacement smoke test of this duration correction:** with the game closed, disable only old **WMC Visual Smoke**, install/enable the following distinct V2 ZIP, and deploy without changing the music mod or unrelated priorities:

`C:\Dev\witcher-music-control\build\visual-smoke-triage-v1\manual\WMC Visual Smoke V2 - Millisecond Fix.zip`

ZIP SHA256: `ad8753381fdfd35a8cf1c59e779f6de248d6cc3ce0bc3bc31f106edbdcca28e0`

Only member: `modWMCVisualSmokeV2/content/scripts/local/wmcVisualSmokeV2.ws`

Source SHA256: `969cb74af8b970f989fc60ec95d5ed05152e672ce0ee80a64c133de12d0a2a9f`

Load an existing current-region save, remain stationary outside dialogue for about30 unpaused seconds, and report/screenshot **`WMCVIS2 begin`** and **`WMCVIS2 snapshot`**, or the exact compile/no-message result. Nothing is expected at the main menu. No HUD/INI/argument changes, quest progress or deliberate save are needed; normal game autosave behavior remains outside this diagnostic's control. Stop on compilation conflicts rather than editing merges or priorities.

Rollback with the game closed: disable/remove **only V2** in Vortex and deploy that removal; keep V1 disabled and preserve the working music configuration. If V2 also produces no messages, the unit bug remains a proven defect but is insufficient to explain retail reachability; do not automatically request another unchanged run or revert to native logger experiments. Stop for review.
