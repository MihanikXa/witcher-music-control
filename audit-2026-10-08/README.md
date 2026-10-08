# Witcher mod compatibility — private release ready for testing

Five installable archives contain 171 real payload files. Start with
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
Gwent Deck Choice is retained through a complete corrected-layout package. Engine compilation and
quest/combat runtime tests remain required. The live setup was not changed.

37 detected packages (36 originally audited plus one late addition), 35 Mods
folders and 6 DLC mod folders. Original 18 confirmed file/text units plus one
combat family receive mechanisms or winners. AutoLoot's semantic defect and
seven new Steam baseline incompatibilities are additionally corrected. Two
BIA/Gwent scene overlaps have deliberate Gwent winners in the corrected profile.

Git contains reports/original tooling only. Assets, tools from third parties,
private evidence and installation packages stay local/ignored. Public Git alone
cannot rebuild copyrighted payloads without the preserved local inputs.

Original inventory/resource hashes remain in inventory.md and conflicts.md; their first-pass gates are superseded by the implementation reports.
