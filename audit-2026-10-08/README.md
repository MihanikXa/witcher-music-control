# Witcher mod compatibility — private release ready for testing

Four installable archives contain 144 real payload files. Start with
[release.md](release.md) for installation/hashes, [decisions.md](decisions.md)
for trade-offs, [implementation.md](implementation.md) for actual changes, and
[test-plan.md](test-plan.md). validation.md and rollback.md contain current
results and exact recovery steps.

Target: Steam 25773555 / 5.0.0.1048522 after an update during this work.
Two existing merges and seven independent overrides were adapted to current
vanilla; three existing merges remain byte-identical. Eight UPR quest resources
and SAH's wolf HUD are deliberate winners, not binary merges. Bestg timing is
unified through Combat Speed; AutoLoot's duplicate scheduler is corrected.
B&S custom animation selectors and Bestg's wolf emblem are sacrificed; the
late partial Gwent Deck Choice package is excluded. Engine compilation and
quest/combat runtime tests remain required. The live setup was not changed.

37 detected packages (36 originally audited plus one late addition), 35 Mods
folders and 6 DLC mod folders. Original 18 confirmed file/text units plus one
combat family receive mechanisms or winners. AutoLoot's semantic defect and
seven new Steam baseline incompatibilities are additionally corrected. Two
potential BIA/Gwent scene overlaps stay excluded with that incomplete package.

Git contains reports/original tooling only. Assets, tools from third parties,
private evidence and installation packages stay local/ignored. Public Git alone
cannot rebuild copyrighted payloads without the preserved local inputs.

Original inventory/resource hashes remain in inventory.md and conflicts.md; their first-pass gates are superseded by the implementation reports.
