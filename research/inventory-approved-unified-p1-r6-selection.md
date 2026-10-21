# Unified Inventory r6 — persistent selected-row feedback

21 October 2026. Narrow selection-presentation correction to r5.

User reports **“Much better now, almost everything works”**, but no indication
of which item is selected, only the active section. This is partial functional
feedback, not full input/visual/compatibility acceptance. The screenshot shows
Weapons active and the silver sword's actual details, but no distinct selected
row. Its overlay records focus=1 and successful details payload item 37.
Private evidence: `build/approved-inventory-r6-runtime-evidence/`;
SHA-256 `21b1507c96b029f92739c3fbc893d7d202c4c866463f4f7cac3f57aa6c9666fc`.

## Source defect and bounded correction

`SlotBase.aiPaintRow` in `src/inventory/unified/Row.asinc` used
`selected && activeSelectionEnabled` for both border and fill. Consequently a
selected row with inactive native selection is painted exactly like an unselected
row. The authored-method negative control reproduces that condition. The screenshot
does not expose the native flag or prove which native writer last changed it;
do not claim that specific runtime transition has been traced.

R6 renders selected identity independently of native active-focus feedback:

- Selected row: existing warm-gold outline and subtle brown-gold fill.
- Active selected row: stronger outline/fill using the same colors and geometry.
- Unselected row: unchanged subdued frame/fill.

This restores a persistent selected-item cue while preserving the r5 focus cues.
Native selected identity, actions, input subscription, D-pad handling, pooling,
scrolling, details, equipped notch, layout and other movies are unchanged.
No per-frame redraw, new selection model, new display objects or replacement
input actions are added. Native selected setters already invalidate row state.
Only `SlotBase` recompiles from the verified r5 resource checkpoint, whose
exact accepted Menus v4 provenance remains checked.

## Verification and limits

`python tools/verify-approved-inventory-row-selection.py` executes the actual
authored paint method against a graphics-call recorder. It proves the r5
negative control, selected active/passive differences, unchanged unselected
states, transfer of the selection appearance between rows and unchanged equipped
notch geometry. This does not execute Flash, the native game or a gamepad.

Build commands:

```powershell
python tools/build-approved-inventory-diagnostic.py prepare
python tools/build-approved-inventory-diagnostic.py package
python -m unittest discover -s tests -p test_approved_inventory_unified.py
```

All 15 targeted tests pass. The r5 annotation is byte-identical and reuses its two successful compiler
controls. Package verification checks source/movie consistency, non-code tags,
resource extraction, bundle reconstruction and protected live-file snapshots.
No native cook/validate or r6 in-game execution is claimed. Package/resource
hashes and final test count are in the r6 manifest. Known optional icon lookup
#1009, rarity clipping, Drop target/footer cleanup and item-exclusion reconciliation
remain outside this correction.

## Manual test and rollback

Close the game. In the cloned test profile, disable r5 and install only
`deploy/approved-inventory-runtime-diagnostic-r6/Approved-Inventory-P1-DIAGNOSTIC-r6-private.zip`.
It replaces the same `modApprovedInventoryUnifiedP1` subtree; preserve its
priority ahead of Menus v4. Do not enable both candidates. No automatic live
deployment, merges, settings or save changes were performed.

1. D-pad through all three weapons: exactly one row should show the gold selection
   and its name must match the middle details. Repeat with mouse/keyboard.
2. Move Left to categories and return with A; selected identity should remain
   visible. Open Details and Back; selection/scroll must stay in place.
3. Unequip/re-equip an unrestricted starter sword; selection must remain clear
   while the equipped notch and model update. Check a longer list while scrolling.

Rollback: disable r6 and restore the preserved r5 test package, or manually
redeploy accepted Menus v4. Do not reset settings or regenerate merged scripts.
