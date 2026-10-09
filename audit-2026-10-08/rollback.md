# Analog gait update rollback

For this incremental test, close the game, disable the new analog-gait package
04 and re-enable the retained 6e01460 movement-hotfix version in the existing
Compatibility Test profile. Deploy with Vortex; preserve packages 01/02/03/05,
their settings and priorities. Verify Vortex withdraws the added merged
locomotion override. Do not manually delete managed files or follow historical
whole-suite rollback steps below. Exact archive/hash and optional setting
restoration: [analog-gait.md](analog-gait.md).

# Exact rollback procedure

Nothing was deployed by the agent. Before installing, create fresh backups from the **current** live settings and five merged scripts, not the older first-pass snapshot: Steam changed the baseline. Preserve original Vortex package archives/state/order and create a separate test profile. Do not rely solely on profile switching to back up unmanaged files.

| Modification | Undo through Vortex / offline settings |
|---|---|
| Core replacements | Disable Compatibility Core. Re-enable the original four Bestg, Combat Speed, AutoLoot and Responsive Movement packages together. Restore original B&S menu XML winner. Deploy normally; check old component paths/ownership. Restore only the changed profile settings from your fresh settings backup/diff. Do not restore an entire stale settings file over subsequent unrelated preferences. |
| Updated Merges | Disable Updated Merges and deploy to withdraw its managed files. Restore the independently backed-up manual Mods/mod0000_MergedFiles folder only after confirming Vortex no longer owns those paths. Restore original Script Merger inventory if you changed it. Keep generated merged section first. This restores the pre-release installation, whose two scripts are stale against current Steam; prefer a corrected forward fix after isolating a regression. |
| English Text | Disable its Vortex package and deploy. Original localization databases then supply those five IDs according to the original relative priorities. No text database rebuild is required. |
| Arrow Layout | Disable corrected Arrow package, re-enable the original package only if returning to its exact prior state, and deploy. Its old layout was inactive; this intentionally loses functioning Arrow Deflection. No other guard binding was changed. |
| UPR/BIA priority | Restore BIA-before-UPR in Vortex's load-order page and deploy/recheck mods.settings. Reload a pre-transition test save. Switching priorities is not guaranteed to repair quest state already stored in a save. |
| SAH/Bestg priority | Restore original Bestg-before-SAH relationship only with original Bestg scripts/core reverted, then deploy/recheck. This restores the prior wolf asset and can shadow SAH presentation. |
| Required saved profile | Review prepared-settings/dx12user.settings.diff and restore previous values for those 23 keys from your current backup. Remove a newly added key only if absent before installation. Keep unrelated preferences and the game's new native options. |
| Optional controls | Reverse only the added F8–F11 bindings in the named eight sections, using the diff/fresh backup. Do not touch occupied keys or F3. Re-run the offline helper for a newer source copy rather than applying a stale full input.settings. |
| Gwent Layout | Before any GDC gameplay has changed a save, disable Gwent Layout and restore the prior profile/package/order through Vortex. The old package restores the prior partial layout, not a recommended working setup. After deck selection/rewards, return to the matching pre-GDC test save and profile; do not continue the changed save with GDC removed. If already using GDC in a campaign, retain the complete mod while investigating regressions. Never remove only its Mods or DLC half. |

After rollback, verify Vortex enabled states and actual priorities, retain Sharedutils/other dependencies, and load the same independent pre-test save. No purge, uninstall, save editing, Steam blanket repair or deletion of staging hardlinks is necessary. Do not mix a partially reverted timing controller with the remaining core changes.

For a regression, first revert the last independent package/stage using test-plan.md. Core's Bestg/CSM timing files are coupled and must revert together. Keep error messages and test saves; report which package/stage first failed. Private original payloads and first-pass snapshots remain under audit private storage, but fresh user backups take precedence over older machine-state evidence.


### Reviewed release rollback dependency

Treat Compatibility Core and Updated Merges as one tested rollback unit: disable both, restore the backed-up manual merged folder only after Vortex ownership is removed, re-enable original four component packages, and restore the saved profile settings/order. Do not roll back by copying over managed hardlinks. Arrow and localization can revert independently. Gwent Mods/DLC must revert together and only with a matching pre-GDC/new-game test save; removing it from a changed campaign may invalidate decks. Keep the previous ZIPs outside Vortex deployment for version rollback.
