# Rollback and baseline guards

No deployment occurred, so there is currently nothing to roll back. Do not copy backup files into the live installation during review. The following procedures apply only to individually approved later changes.

## Before approved deployment

Run `python tools/validate-review.py` from this audit folder and require changed_live_files and patch_hash_failures to be empty. If the machine/mods were changed since this audit, refresh inventory and decisions rather than using stale rollback material. Preserve fresh independent copies of mods.settings, input.settings, dx12user.settings, MergeInventory.xml, deployment manifests, the original Arrow package/archive and the Vortex profile's order/enabled state. Capture new deployment hashes and ownership. Copies must not be hardlinks.

Existing control backups, live absolute paths and SHA-256 are in evidence/control-snapshot.json; independent copies are in private/control-snapshot. All proposed payload paths/hashes are in evidence/patch-manifest.json. All original deployed/staged source mappings are in evidence/all-deployment-link-check.json. The partial repaired Vortex DB copy is **evidence only, never a restore image**; do not replace Vortex's state.v2 with it.

## Individual change rollback

Localization patch: disable only the newly installed AuditCompat package in Vortex and redeploy. Verify its single en.w3strings no longer mounts and Grammar again wins ID 1063514. Keep the audit patch/source for review. Do not delete a shared managed deployed hardlink manually.

Arrow layout correction: disable only the new corrected package, restore the original package's enabled state/order through Vortex and redeploy. If reinstalling the original package in place was chosen, use the saved original archive and the original installer topology. Verify original managed source/destination hashes and that the earlier game/ArrowParryManual payload is restored. This intentionally restores the prior inactive behavior. No purge or bulk deletion is needed.

Priority/Outfit Wheel entry: restore the exact original Vortex order/profile enablement, redeploy, and compare mods.settings against private/control-snapshot/0-mods.settings (listed hash in control-snapshot.json). If Vortex rewrites priorities, fix its persistent order rather than copying a live file it immediately overwrites. The conditional UPR-first order has no approval now; if later deployed and rolled back, restore BIA 6 before UPR 14 with the rest of the original order.

Existing script references: these were not newly installed. If later merge regeneration is approved, preserve independent copies of all five live files and MergeInventory.xml first. Restore those exact files using the approved ownership method (the current merge folder is unowned/manual), then restore the provenance file only if its baseline still applies. The review copies under patches/verified-existing-merges and their original hashes are in installed-files.json. Do not overwrite Vortex-managed source mods to undo generated merges.

Controls: no control edits are staged. If later approved, back up each control file immediately before editing and record a per-key diff. Restore only the approved changed keys if other user changes occurred; full snapshot restore is safe only when no intervening edits occurred. Do not force-import FriendlyHUD/Hoods example bindings.

Binary quest/HUD/metadata modifications: none exist in patches; no binary rollback is needed. A future supported patch should be a separate managed package with exact bundle hashes and explicit disable/redeploy rollback, not overwritten mod originals. Vanilla metadata repair requires its own pre-change backup and supported restore workflow; no automatic Steam verification/repair is authorized here.

After rollback rerun inventory/conflict checks, verify actual overwrite winners and controls, and compare managed files to their sources. A rollback may restore the known prior conflict state; it does not establish compatibility. Saves and game binaries are never changed by these proposals.
