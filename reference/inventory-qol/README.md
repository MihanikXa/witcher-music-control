# Inventory QoL reference archives — Codex source input only

These are local, private third-party source/reference downloads for the adaptive Inventory project. **Do not install or enable them in Vortex yet.** `reference/` binary contents are ignored by Git. Do not commit copied author assets, archives or extracted scripts.

Put the **original downloaded archives without renaming or extracting** in the following local folders under `C:\Dev\witcher-ui-overhaul`:

```text
reference/inventory-qol/
  sort-everything/archives/
    <Sort Everything main Remastered v1.55 archive>
    <Sort Everything - Menu and user settings archive>
  recent-loot-tab/archives/
    <RecentLootTab (5.01) v1.0.0 archive>
  junk-not-treasure/archives/
    <JunkNotTreasure v1.0.0 archive>
```

Original download pages:

- Sort Everything: https://www.nexusmods.com/witcher3/mods/1710?tab=files — choose 17 Oct 2026 main Remastered file, not old 4.x/More Quick Slots variant; additionally get `Sort Everything - Menu and user settings` from Miscellaneous.
- Recent Loot Tab: https://www.nexusmods.com/witcher3/mods/13981?tab=files — main `RecentLootTab (5.01)`.
- Junk Not Treasure: https://www.nexusmods.com/witcher3/mods/14451?tab=files — main `JunkNotTreasure`.

Optional later, not needed for first Gear candidate: Quick Surplus Seller https://www.nexusmods.com/witcher3/mods/14170?tab=files . If requested, put original archive in `reference/inventory-qol/quick-surplus-seller/archives/`.

Codex should verify archive names, file hashes, scripts, packaged cooked movie keys and installed resource owners read-only. Check compatibility with the accepted Menus v4, FriendlyHUD, Hoods, Outfit Wheel, accepted RC2 HUD and current Script Merger. Borrow functional design ideas, but do not blindly stack whole UI replacements. First playable Gear should have no new external runtime dependency; provenance and feature-contract reports are the first use of these archives.

Document any dependencies in `design/adaptive-inventory-build-plan.md`; do not use these local reference archives as proof the mods are enabled in the game.
