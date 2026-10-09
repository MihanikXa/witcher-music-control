# Private installable release

Location: `C:\Dev\witcher-mods-merger\audit-2026-10-08\release\witcher-compatibility\`.

Target: Steam **25773555**, executable **5.0.0.1048522**, current installed mod versions from inventory.md plus its late-update note. Five archives passed CRC, per-file SHA-256, root-layout and repeat-build checks. Official compiler results and their scope are recorded in validation.md; deployment and runtime compatibility remain untested. These are private personal integration packages containing third-party/game payloads; do not upload them to GitHub.

| Archive | Files | Bytes | SHA-256 |
|---|---:|---:|---|
| 01-core-replacements.zip | 111 | 1181797 | 0e63fc2f62fc73d3e325e4f698e62735cbaa12bf8977ce136676a48d547950f9 |
| 02-localization.zip | 1 | 1223 | 98abf4fee35cf97f2f5ceb2f5fa38b2ca760a875ed95f04c1c8b4828666f19d1 |
| 03-arrow-layout.zip | 20 | 19487 | ceb701c5677f618a2d2e9890b8cda5ded7ffe69d34b51310d077dab24290f8bd |
| 04-updated-merges.zip | 12 | 324521 | 49220f25110566c6355e19be9464822ef47d0bf12a43b31d209e8d3ef151813a |
| 05-gwent-deck-choice-layout.zip | 27 | 501310 | c4c935765b417894869119469a683fbe25960bc1d62e2016d23a04601c82ae45 |

## Vortex installation, performed by the user

1. Close the game. Preserve a rollback profile and independent copies of current document settings, the entire existing manual `Mods/mod0000_MergedFiles` folder, Script Merger's MergeInventory.xml, current Vortex order, and the affected original package archives. Use a separate compatibility-test profile. Replace the wrongly laid-out Gwent package with Gwent Layout in step 3; retain its functionality. Use a new-game test or pre-GDC save: the author warns uninstalling GDC from a changed playthrough can break decks. Do not purge Vortex.
2. Import the five ZIPs with **Mods РІвЂ ’ Install From File**, or drag them onto the Mods drop area. Name them clearly (Compatibility Core, English Text, Arrow Layout, Updated Merges, Gwent Layout). Inspect installation previews: core has four original Mods folders plus bin; localization has one Mods folder; Arrow has Mods plus bin; merges has Mods/mod0000_MergedFiles; Gwent Layout has Mods/mod_GwentDeckChoice, DLC/dlcGwentDeckChoice and bin menu XML. Installed Vortex's root/menu and top-level installers preserve these layouts; no wrapper directory belongs in the game root.
3. Before enabling core, disable the original **Bestg School Stances, Combat Speed, AutoLoot, Responsive Movement** Vortex packages. Core replaces them using identical folder names; enabling both copies would undermine ownership and annotation checks. Keep B&S, SAH, UPR, BIA, Sharedutils (including DLC), FriendlyHUD, Outfit Wheel and all other retained mods enabled. Disable the original mislaid Arrow package before enabling Arrow Layout. Disable the original incorrectly packaged Gwent Deck Choice Vortex package, then enable Gwent Layout in the same planned deployment. Both Mods and DLC must be present; do not install the Gwent My Way alternative. Keep originals installed for rollback. Set the Vortex file conflict rule so Compatibility Core's `modBloodAndSteel.xml` wins over the original B&S menu XML.
4. To avoid an unmanaged/generated-file overwrite prompt, move the backed-up existing **manual** mod0000_MergedFiles folder outside the game's Mods tree before enabling Updated Merges. Do not move any managed hardlinks or other folders. Let Updated Merges supply the five existing plus seven newly adapted script paths. Vortex's merged/manual-prefix lock keeps that section at the top. Avoid running Script Merger's automatic regeneration over these reviewed outputs; its previous inventory was empty despite five live merges. A future regeneration must be reviewed against these scripts in a copy.
5. In **Vortex's Witcher load-order page**, persist: mod0000_MergedFiles first; mod0000_CompatibilityText next; UPR ahead of BIA; mod_GwentDeckChoice ahead of BIA; SAH ahead of modBestGsSchoolStances; Outfit Wheel explicitly enabled. Core's four component entries retain their existing relative positions. Use local load-order.json as the complete reference (38 enabled sections), with unique ascending priorities. **Lower number wins.** File conflict rules and resource priorities are separate. Do not just copy mods.settings: Vortex rewrites it on deployment/profile changes.
6. Review `prepared-settings/dx12user.settings.diff` and apply its narrow profile changes to the current Documents settings (or use mod menus for exactly those values). Current prepared copies are based on this machine's settings. If preferences changed, regenerate below and review again. The original B&S values must be set off even with new XML defaults; saved settings override defaults. Verify in-game that custom attack/dodge selectors remain off and CSM additive layers/finishers remain off. Optional input.settings changes use F8 Hood, F9 potions, F10 bombs, F11 oils across eight contexts; apply only if wanted. Existing keys are preserved.
7. Deploy through Vortex. Review external-change prompts individually; do not accept deletion of unowned files blindly. Inspect actual Mods paths, deployed menu XML, file ownership and generated Documents/mods.settings. Confirm all required priority relationships after every deployment. Check that GwentDeckChoice.xml is registered in the applicable menu file list by Vortex and the Gwent menu is visible; preserve all other menu entries. If not registered, add that single XML entry using the installed menu-filelist workflow, never replace the complete list. If the new merged package's section is missing or disabled, correct it in Vortex before launch. Follow test-plan.md incrementally; keep normal campaign saves untouched until progression tests pass.

Prerequisites: the retained installed B&S/BIA/UPR/SAH/Sharedutils/FriendlyHUD/Outfit Wheel dependencies and paired DLC; this release is not a standalone mod collection. Arrow uses the existing guard control, so no new essential parry binding is needed. No game binaries, complete vanilla resources, global input.xml or saves are replaced by these packages.

## Regenerate personal offline settings

Run from the release directory. Outputs stay under that directory; the helper never overwrites its input.

```powershell
C:\Python314\python.exe .\prepare-settings.py --input 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\dx12user.settings' --delta .\settings-profile.json --output .\prepared-settings\dx12user.settings
C:\Python314\python.exe .\prepare-settings.py --input 'C:\Users\micha\OneDrive - hull.ac.uk\Documents\The Witcher 3\input.settings' --delta .\optional-controls.json --output .\prepared-settings\input.settings
```

Review the resulting diffs, back up live originals, then apply only approved differences while game is closed. Occupied IK_ keys are never replaced, duplicate target keys cause refusal. Vortex menu deployment does not substitute for these saved document settings. Do not install the settings copies as game-root ZIP payloads.

After approval and personal testing, retain the generated hashes/order/configuration alongside the profile. No agent deployment is required: all installable archives are already available locally.


## Review acceptance gate

The five rebuilt ZIPs pass archive/static checks; only Core and Updated Merges payloads changed in this review. Vanilla, the focused school timing overlay and Gwent hook sources compile with current official wcc. A broad source assembly returns success with many assertions; the exact full annotation/opaque-blob deployment context is **not** cleanly compiled. See validation.md before testing. No compiled test artifact is part of these ZIPs. Current binaries remain the selected authors' originals; no additional quest/HUD binary merge was produced. Use a disposable test profile/save first, not an established campaign.
