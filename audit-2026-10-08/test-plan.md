# Current incremental controller test

The compatibility suite is already deployed and working by user report. Do not
repeat initial installation tests as a prerequisite to this update. Follow the
seven focused analog/sprint/mixed-input and special-state cases in
[analog-gait.md](analog-gait.md), starting in Running the Walls with existing RM
locomotion effects off. Revert only package 04 if a regression appears.

# Incremental in-game acceptance tests

Use independent test saves/copies and a compatibility-test Vortex profile. Never overwrite your only campaign save. Record package toggles, load order, game build, settings and screenshots/error text for each failure.

| Stage | Setup / test | Pass condition / regression isolation |
|---|---|---|
| 1 Startup baseline | Use a new-game/pre-GDC test save; install Updated Merges first, retain originals for other mods. Test script compilation/start menu, load and save/reload; try controller dodge-to-sprint on/off, Ciri dodge/dash where an existing save permits, and auto-oils after reload. | No script errors; new sprint option works, oils respect Accessibility setting; Outfit Wheel F3, torch and inventory still work. If failure appears here, isolate Updated Merges before adding core. |
| 2 Core + profile | Replace the four originals with Core, apply the required settings, retain SAH above Bestg. Test every school, light/heavy attacks, attack→dodge/roll, interruption/hit recovery, held guard, stance changes during animation, Whirl/Rend, exploration→combat transitions and Ciri. | No stuck speed after actions/reload; Bear slower and Feline faster; damage/guard/Brawler still differ meaningfully; no doubled speed. B&S custom selectors remain off; targeting still works. Failure: revert Core as a whole with its four originals and prior settings; do not mix dependent timing files. |
| 3 HUD / helpers | Each SAH layout, vitality/stamina/toxicity/sign changes, horse/swim, cutscene and HUD recreation. Change Bestg stance, then receive a real quest popup. Check FriendlyHUD quick items and Outfit Wheel inventory/preview/close. | SAH presentation intact, no school emblem expected; independent stance popup/text and radial controls work without displacing later quest popups. Essential modules remain visible. Test AutoLoot interval, disabled/combat/dialogue/theft modes; no duplicate notifications/scans. |
| 4 Arrow | Enable Arrow Layout after previous stages pass. Test sword drawn, held guard vs fresh press, arrows inside/outside timing window, different distance/angle, reflected damage, fist/Brawler combat. | Manual sword parry obeys timing/config; fist guard/Bestg behavior unaffected. Revert only Arrow Layout and restore original package state if regression begins here. |
| 5 English / controls | Enable English Text; inspect Blood Ties letter including final signature, sylvan speaker line, threat tense, ambush subtitles and translated bracket line. Optional F8–F11 helpers, existing F3/controller bindings. | No missing IDs, doubled preceding subtitles or lost paragraphing; other languages unchanged. Revert English Text or optional settings independently. |
| 6 Quest transitions | UPR ahead of BIA: Family Matters final Baron/Uma conversation and Bog accept/decline/later-join/completion; fisherman family after completion. King's Gambit arrival/massacre/Cerys/Hjalmar and Crach Gwent. Reason of State both outcomes, warehouse exits/doors. Kaer Muire shop before/after death; Lambert/Baron/Crach cards and Collect 'Em All counters/activation. | Every branch advances and completes; NPCs/doors available; save/load before and after transitions preserves state. Stop campaign progression on a soft-lock; preserve failing and pre-transition test saves for diagnosis. |
| 7 Persistence | Save/load after combat and stance changes, travel between hubs, reload HUD, change Vortex profile and redeploy. | Required order/settings persist, no speed leak, no missing dependency or localization; Gwent Mods and paired DLC remain present and their priority persists. |

Updated Merges also needs native-update checks: ladder climb/slide/get-off with a held torch; placing/removing user pins inside/outside map bounds with FriendlyHUD zoom/filter changes; granting/looting items and learning crafting/alchemy recipes; radial potion helper plus disabled bomb slot behavior; opening graphics/telemetry menus without old marketing API errors; meditation controls feedback and Outfit Wheel cancel/save. These exercise the seven newly adapted whole-file overrides, not just the original five merges.

For a quest regression, restore the original BIA-before-UPR order and reload a **pre-transition** test save, then repeat the identical branch. This identifies the priority choice without asserting that switching order can repair an already altered save. UPR phases/scenes should move together; do not alternate individual graph files during a campaign. Restoring order requires Vortex redeployment/order verification.

For a compiler failure, capture the file/line and full message before changing anything. Compare with the stage's predecessor. Disable only the last independent package (or core plus its settings and re-enable all four originals). If startup fails before any changes, the release did not establish the baseline; investigate separately. A successful Script Merger scan does not pass quest/scene/UI acceptance.

Progression and combat acceptance remain required before calling this setup stable. No test in this checklist was executed by the agent.

## Gwent Layout acceptance step

Add package 05 as its own test stage after startup succeeds. Replace the old partial Vortex package, enable both corrected Mods/DLC, and put GDC ahead of BIA. Start a new-game test; do not use a campaign save already altered by GDC to test removal. At White Orchard's inn, talk to Aldert, run the tutorial, select each faction using separate test saves and swap factions. Verify deck-builder entries, leader selection, collection counters and save/reload. Skellige is intentionally hidden until its own menu option is enabled.

At a Velen herbalist, verify normal shop services/dialogue and Gwent. Verify first/repeat card rewards and sunrise reset, plus an expanded NPC opponent. Later test missable quest-card recovery and UPR's Lambert/Baron/Crach timing; no duplicated reward or stalled Collect 'Em All state should occur. Test NG+ and expansion-only starts separately if used.

If a regression first appears after 05, preserve the failing test save/logs, then revert to the pre-05 test save with the earlier matching package profile. Do not disable GDC and continue a save whose deck/card state it has changed. Failure before 05 implicates an earlier stage; success before 05 does not prove quest integration.


### Review regression cases

Begin on a fresh compatibility-test profile with a copied/pre-mod test save. First confirm startup compiler results; capture the full errors before changing anything. With Core + Updated Merges together, test unarmed/Brawler versus sword-ready attacks, each school, attack→dodge, repeated dodge-enable/roll changes, exploration transition→combat, Whirl/Rend exit and Ciri. Confirm no leftover speed after action end, interruption, setting disable, save/load or the 30-second fallback. Test RM swimming/climbing and HitLag separately. Verify B&S selectors remain off, signs/targeting still work and its former special-dodge flow is absent as intended. Then add Arrow, text corrections and Gwent Layout incrementally. Gwent must use its paired DLC and a suitable save. HUD: verify SAH transitions and native Bestg popup/radial selection; no stance emblem is expected. On failure revert the last independent package; Core/Merges revert as a pair. Do not overwrite campaign saves until quest-transition tests pass.
