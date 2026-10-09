# Incremental analog gait test release — 9 October 2026

This update targets the already deployed Compatibility Test profile and working
6e01460 movement hotfix. The user reports successful compilation/gameplay,
keyboard gait toggling and held sprint. Those resolved issues are not reopened.
This new controller behavior has not been deployed or tested in-game by the agent.

## Cause and correction

The installed Movement Tweaks `CalculateMoveSpeed()` calls
`SetWalkToggle(false)` when `LastUsedGamepad()` is true. Thus controller movement
overrides the shared keyboard gait selection. Its normal movement calculation
also selects walk/run from the stick-magnitude threshold. Configuration alone
cannot remove either source-level behavior.

Package 04 adds one override:
`Mods/mod0000_MergedFiles/content/scripts/game/player/movement/locomotionDirectController.ws`.
The original twelve working-hotfix payloads, including `playerInput.ws` and
`r4Player.ws`, are byte-identical. Movement Tweaks itself remains installed and
unchanged. No input XML, settings, controller bindings or other package changes
are included.

During eligible ordinary on-foot exploration, the override retains
`GetIsWalkToggled()` and uses the already processed movement magnitude, bounded
to 0..1, to select `magnitude * speedWalkingMax` (0.6) or
`magnitude * speedRunning` (1.0). Selection does not depend on the last input
device. Native direction processing and deadzones remain upstream. The native
sprint calculation runs first and is retained when sprinting; the existing
hotfix restores the remembered gait after held sprint. Native sprint eligibility,
stick thresholds and release hysteresis remain in force.

The mapping is excluded during combat/combat music, swimming, vehicles, airborne
movement, player actions, scripted speed modifications, focus/fades/black screen,
disabled locomotion and disallowed run/jog contexts. The original calculation
continues in those contexts. Its temporary gamepad walk-state clearing is restored
before return so it cannot erase the user's selection. The post-calculation slow
walk, boat and other speed constraints remain unchanged. Authored turn slowdown
and native animation behavior writes are preserved.

There is one float smoothing cache, not a separate controller gait state. The
target cap changes at 3 units/second: the full walk/jog difference settles in
about 0.13 seconds. Steady walk mode never maps full stick to jogging. During
jog-to-walk deceleration, numerical speed can briefly exceed the steady walking
cap; the movement type already selects walking. This preserves speed continuity
rather than snapping the cap instantly. Actual blending, foot planting and the
native animation graph's response to low-speed `PMT_Run` still require testing.

## Private archive and dependencies

Archive:
`C:\Dev\witcher-mods-merger\audit-2026-10-08\release\witcher-compatibility\analog-gait\04-updated-merges-analog-gait.zip`

SHA-256: `fbbe3b2ecfeab77965f13b4e7386c8891167f37f8d770b20a37c7c7fd9539909`.

Thirteen real script files; standard `Mods/` install root; no extra wrapper
directory. The installed Vortex Witcher installer routes all thirteen files to
their intended paths. This replaces package 04 only. Packages 01, 02, 03 and 05,
their original disabled-package rules, and existing compatibility settings remain
unchanged. Movement Tweaks stays enabled. Standalone Responsive Movement stays
disabled; Core's modified copy stays installed. Keep the currently saved RM
locomotion effects disabled for the first test (Immediate Input off, Stop Sooner,
Transition Speed and Tighter Turns zero, Keep Running on Turns off). No additional
effect is enabled by this update.

## Update the existing Vortex profile

1. Close the game and select **Witcher Compatibility Test**. Record the current
   package 04 version and order; retain its working ZIP for rollback. Do not
   recreate the profile or reinstall the other four packages.
2. Import the new ZIP using **Install From File**, as an updated version of
   **Updated Merges** if offered. Enable this version and disable the old package
   04 version in this profile; only one package may own these merged files.
   If imported as a separate entry, name it clearly and explicitly disable the
   old entry. Do not use a conflict rule to keep both enabled.
3. Keep `mod0000_MergedFiles` at its existing priority **2**, ahead of Movement
   Tweaks (**28** in the inspected profile); lower numbers win. Preserve all
   other ordering and Core/menu conflict rules. Do not regenerate Script Merger.
4. Deploy through Vortex. Verify the new locomotion script is owned by the new
   package 04 and that the existing merged playerInput/r4Player files remain
   supplied by it. Preserve the existing merged-folder entry and priority.
5. In the game controls menu, verify **left-stick sprint is Off**. Its native
   `Controls.LeftStickSprint` mode otherwise selects different sprint dispatch
   when the last input device is a gamepad. This update uses held Ctrl instead;
   no need to implement or rebind L3. Do not replace input.settings or any full
   settings file. Preserve existing Caps Lock = WalkToggle, Ctrl = Sprint and
   X = Roach whistle bindings.

Flydigi assignments are external: M1 sends Ctrl key-down while held and key-up
on release; M2 sends one Caps Lock keypress per press, without turbo/repeat;
front C/Z sends X. Keep the stick as analog XInput, not WASD emulation.
No hardware mapping is committed or installed. Source checks establish that the
new mapping does not reset gait on device switching and the existing on-foot
action handlers accept these keyboard actions. They do not prove that the
controller software delivers simultaneous keyboard/XInput events. Prompt/device
switching and camera behavior must be checked in-game.

## Focused in-game acceptance tests

Use the Running the Walls tutorial or an equivalent unrestricted on-foot area.
Begin with the current saved RM locomotion effects off; keep a clean test save.

1. Select walk with physical Caps Lock while holding the stick fully tilted.
   After the short deceleration, full deflection must stay walking. Sweep through
   roughly 25%, 50%, 75% and full tilt; speed must rise smoothly without jogging.
2. Select jog without releasing the stick. Full tilt must jog; repeat the sweep
   and cross the former magnitude threshold repeatedly. Check foot planting,
   direction changes and absence of sudden speed jumps.
3. Toggle both ways at full tilt and during gradual stick motion. Selection must
   respond on the next update, with a short smooth acceleration/deceleration.
   Check for flicker, snapping or RM-style jitter.
4. In each selected mode, hold physical Ctrl with full stick, then release it.
   Sprint must override and release must restore the chosen gait. Repeat with M1
   and M2 emulation. Test M2 while already fully tilted, and sprint/toggle while
   steering the camera with the right stick. Check interactions, prompts, X
   whistle and Photo Mode. A rear-button failure when physical keys work points
   to event delivery/mapping, not proof that the gait script is wrong.
5. Release the stick; verify stationary behavior and normal deadzone response.
   Repeat keyboard Caps Lock, held Ctrl and Movement Tweaks slow-walk C tests.
6. Save/reload and repeat selection/sprint. Test combat entry/exit, Bestg stance,
   dodge/roll, horse steering/gaits, swim, jump/climb and a scripted movement
   section. Native restrictions remain authoritative; do not expect exploration
   caps in those excluded contexts.
7. Only after these pass, try wanted RM options one at a time. If jitter appears,
   restore that option to its prior disabled value and repeat the same route.
   The update does not certify newly enabled RM effects.

If a test fails, record the mode, stick deflection, physical versus emulated
button, LeftStickSprint setting and enabled RM effects; capture a short video
and exact compilation message/log if present. Stop before using campaign saves
if startup, special movement or combat regresses.

## Rollback

Close the game. Disable this analog-gait package 04 version; re-enable the saved
working movement-hotfix version and deploy through Vortex. Keep all other
packages and priorities unchanged. Confirm the added merged locomotion override
is withdrawn and Movement Tweaks supplies its original path again. Never delete
managed files manually. No saves were migrated. Restore only the left-stick
sprint option if you changed it and want the previous setting; external Flydigi
assignments are independent.

Working rollback ZIP:
`release/witcher-compatibility/movement-fix/04-updated-merges-movement-fix.zip`,
SHA-256 `6ce762947cfbc02223ac50e635277065df65962f233909acb7a7950398b990d3`.
It has not been overwritten.

## Build and validation evidence

`tools/build-analog-gait.py --game <installation>` pins the original Movement
Tweaks source and working package 04 hashes, checks the deployed twelve-member
baseline, and assembles the private replacement. Every controlled function-body
edit reverses exactly to the original body; other methods are unchanged.
`--compile` additionally creates a fresh isolated REDkit
`compatibility-validation/analog-gait` workspace from the preserved working source
assembly. For a repeat compiler run, preserve the previous isolated result under
another name first; the builder refuses to overwrite that directory.

The official `wcc_lite compilescripts` run succeeded (exit 0, patch blob produced).
Its 379 warnings and 23,591 diagnostic assertions match the working assembled
source baseline. This is real compilation of that assembly, including the new
override and preserved annotation patch, not a delimiter check or full validation
of opaque third-party compiled blobs. Blob SHA-256:
`e04822ba441925a481c5f8575b23f3239d7447466a33f7527965cbbd8270d243`.
Private log: `C:\REDkitProjects\WitcherCompatibility\compatibility-validation\analog-gait\compiler.log`.

Run `node tools/test-analog-gait.cjs <generated-locomotion.ws> <receipt.json>`
against the private payload. It executes the generated mapping fragment with a
numeric fixture: 2,002 proportional samples, threshold continuity, bounded gait
transitions, native sprint output, excluded-context output and turn slowdown pass.
This fixture does not emulate the engine, action dispatch or animation graph.
CRC, thirteen-file topology, twelve-member identity and deterministic rebuild
checks pass. The original five archives and working hotfix remain unchanged.
Protected deployed scripts and Documents settings match their pre-task hashes.
No agent deployment, game launch, save edit or Vortex mutation occurred.
