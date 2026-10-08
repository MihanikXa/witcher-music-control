# Validation results and limits

## Passed static/non-destructive checks

All 30 mod bundles indexed without format/offset errors (both legacy 0x140 and remastered 0x130 entry layouts). Thirty-one vanilla bundles indexed, 365,866 entries, with no parser errors. QuickBMS bounded extraction succeeded for the ten colliding resource paths across nine owners and thirteen relevant baseline/XML extractions. Extracted sizes equal table sizes; actual decompressed SHA-256 is recorded rather than treating compressed bytes/header hashes as content equality.

Installed Steam depot manifests were decoded and 1,926 official files checked: 1,904 hashes match, 20 zero-length tombstone/placeholder files match the expected empty/no-content-hash form, 2 differ. No installed-depot manifest was missing. About 69.76 GB was read; no game file was repaired. All vanilla scripts used in merges and game executables match the installed cached manifest. This verifies local installed-version consistency; it is not a fresh Steam server authenticity check.

Thirteen source-contribution three-way checks across five merged scripts exited 0 and made no change to the normalized current merged output. This establishes source-change inclusion against the current baseline; it is not a full semantic proof or a compiler pass. No new unrelated duplicate type or paired replacement of the same target was identified in scanned loose sources.

All 229 installed .w3strings index structures parse; overlapping English IDs were decoded with the installed author helper. The one-ID English patch roundtrips exactly, contains only ID 1063514 and no keys, and retains UPR's expansion. The Arrow layout adds no string-ID or named script-symbol overlap with scanned installed loose sources. It shares only the intentional “Mods” root localization key in translated languages. New patch paths do not replace existing runtime Mods files: 20 projected files in the Arrow/localization packages, including one intended existing-ID localization override. Arrow's menu XML already exists and is unchanged.

Twenty-nine config XMLs parse. Every FriendlyHUD input Var attribute record survives the Vortex input.xml merge. Missing custom shortcut actions are documented in conflicts.md rather than importing conflicting defaults.

All 644 deployment records are present hardlinks to corresponding staging sources. Final validation rehashed 1,148 installed mod/other/control files and found no content changes; all 29 staged review files match patch-manifest.json and proposed priorities are unique. Exact results: evidence/review-validation.json. Full extra-file inventory is evidence/all-extra-game-files.json.

## Compiler/resource tooling limitation

An isolated copy of REDkit wcc/DLLs was run with private config/tool data. Initial missing-config diagnostics were corrected only in the audit workspace. Initialization then failed with an access violation (0xC0000005) and missing depot/resource/language/sound inputs. An earlier hung audit-owned wcc process was stopped. The installed game and REDkit files were not used as write targets; no depot was generated.

No supported script compilation, quest graph export/recompile or combined redswf generation succeeded. QuickBMS extraction is not semantic merging. Legacy tools are not assumed capable of correctly compiling remastered annotations. Binary caches/precompiled scripts and native DLL combinations remain runtime/semantic uncertainties.

The modern Script Merger UI was not launched for a rescan: it could write state or operate on the live path. The independent bundle, loose-script, annotation, localization, XML, Steam-baseline and staged-path scans supply broader static coverage. A later copied-workspace Script Merger scan can supplement these results but cannot close binary compatibility gaps.

## Audit write boundary

Reports, extracted resources, baseline copies, tool copies, repaired database copy and proposed patches were written only under this audit folder. Loading the installed SAH Python helper initially created one __pycache__/w3s.cpython-314.pyc file beside that helper. Only that audit-generated cache and its empty directory were removed; bytecode writes are disabled in the staging tool now. No mod content or managed payload was changed. No launch/deployment/save edit occurred.

## Required tests after separate approval

1. Compiler/startup: validate current 5.0 scripts and compiled blob integration with supported tooling; verify expected signatures and wrapper chains. Stop on errors, do not work around them by discarding mods.
2. Quest graphs: compare current vanilla/BIA/UPR graph nodes and scene transitions before accepting priority. Test Family Matters/Baron optional quest handoff, delayed Return to Crookback Bog activation and later joining; Reason of State conclusion/warehouse doors/Dijkstra aftermath; King’s Gambit massacre/attack, Crach Gwent timing and Birna/Svanrige conversation; Kaer Muire blacksmith shop/Gwent cooldown; Collect ’Em All/Lambert/Baron/Crach card timing. Test both intended optional paths, save/reload and leaving/returning to the area. Historical purpose mapping is not sufficient to predict all failures.
3. HUD: SAH artwork styles and transitions, health/stamina/toxicity/sign/medallion, Bestg stance display, Ciri, HUD recreation, saving/loading, marker/quest visibility with FriendlyHUD/Monster Hunt.
4. Combat: speed multipliers start/end, dodges, lunge/targeting, heavy attacks, HitLag damage feedback and Evils AI with BloodAndSteel/Bestg/Combat Speed. Require matching compiled sources where needed.
5. Controls: existing F3 Outfit Wheel behavior; Arrow tap/hold/no-block timing; Hoods toggle and approved FriendlyHUD hotkeys in every configured context. Preserve current controls.
6. Localization: expanded Blood Ties letter and remaining BIA/Grammar dialogue IDs aligned with voices and scene segmentation; verify applicable language behavior.
7. Integrity: determine metadata.store origin and supported lifecycle before restoration/rebuild; monitor new compiler/resource errors after any approved deployment.

## Play safety

**The installation cannot be certified mutually compatible or safe for progression from these results.** Eight quest resources currently shadow UPR changes; preservation after reversal is unverified. HUD artwork contracts conflict; combat speed behavior overlaps; metadata.store differs without known provenance. These establish feature-loss and compatibility risks, not proof that a quest is presently broken or that the game will crash. Do not call warning disappearance a successful fix. Until the unresolved gates are closed, continuing important quest progression is not recommended as a validated outcome.
