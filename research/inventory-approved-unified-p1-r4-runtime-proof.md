# Unified P1 r4 — user runtime data/row/details proof

20 October 2026. **Data/rendering smoke gate demonstrated; equip/action,
full item parity, stability and visual acceptance remain pending.**
Follow-up to [r4 data-boundary correction](inventory-approved-unified-p1-r4-data-boundary.md).
This records the user's actual game images, not agent execution or a reconstruction.

## Evidence

All images are 3840×2160. Unchanged private copies and receipt:
`build/approved-inventory-r4-runtime-evidence/`. No images/assets enter Git.

| User file | SHA-256 | Observation |
|---|---|---|
| `witcher3_GpcV2al8uX.jpg` | `ccb3284961d6978d4c1ff55f0b8f28e32695efc3b25160f5f154a84a4d9fa5ba` | Other rows, selected Diamond dust and corresponding native properties |
| `witcher3_HpSle4IH1s.jpg` | `147347e76e1edda07a17ef0f666f77e9eb585d0398f77c72be129987b21f90da` | All three shown swords, two equipped marks, selected Disglair and real comparison |
| `witcher3_hCWd79qkLA.jpg` | `e2256ae40d4bbb72d7257308213bdb808d5506fbb52e3265a88d4bdf7f1a2109` | Same weapon scene with pinned script/binding counters and pooled-row snapshot |

Visible diagnostic values:

```text
FIRST OPTIONAL ICON FAULT: 1 lookup TypeError #1009 Error #1009
REFRESH SENT=2 SCRIPT=refresh.request active=true busy=false
owned=50 filter.before=IFT_Weapons
publish=38 equipped=9 filter.restored=IFT_Weapons probe=false
BINDING=38
```

These establish actual refresh dispatch, native script execution, owned-item
enumeration, publication, binding delivery and subsequent item rendering.
Publication and binding counts match; this is not the earlier zero-row scene.
The native filter/probe restoration is also observed. The native C++ dispatch
was exercised by the user's game, not by the offline compiler/tests.

## Visible item/selection/detail contracts

- Weapons shows **3**: Witcher's silver sword, Witcher's steel sword and Disglair.
  Both starter weapons carry the accepted small gold equipped corner notch.
  The previously absent equipped swords are now included in the shown projection.
- Selected Disglair has an actual persistent native details payload: damage
  **99–121**, native comparison **+20**, bleeding **+4%**, weight **1.03**,
  durability **100%**, price **155**, compared equipped silver sword **81–99**,
  and **Required Level 2**. The red restriction mark is appropriate for the
  level-1 character; do not erase it to make this item appear equippable.
- Other shows named/art-backed rows, with selected **Diamond dust** and matching
  middle-panel name, crafting-component type, weight **0**, price **150** and
  actual crafting description. Distinct category payloads use the same scene.
- Rail counts: Weapons 3 + Armor 4 + Consumables 6 + Pockets 1 + Other 24 = **38**.
  Bombs/Quest show no count. Review remains explicitly disabled.
- The snapshot's `v=false` entries can represent unused retained pool instances
  carrying previous-category IDs. `aiPaint` intentionally hides pool entries not
  chosen for the current category. These lines alone do not prove missing items;
  the current screenshot visibly has three weapon rows. Full pool identity and
  scroll verification remains a separate test.

The r3→r4 result supports the event-declaration correction in practice: r3 could
enter but had no projection; r4 exposes the three native event handlers and now
receives real items/details. The earlier rail exception and callback-contract
mismatch were separate failures. Do not reinterpret prior compilation success
as evidence that either path had been working.

## What is NOT established

The difference **50 owned → 38 projected** is not evidence of data loss and is
not automatically an accepted exclusion policy. Native filters exclude some
owned objects; the twelve excluded IDs still need the per-item/native-filter
audit against the same unmodified source save before claiming complete parity.
The screenshots do not supply those identities or exclusion reasons.

No screenshot proves equip/unequip dispatch, updated marker/model after an action,
selection retention through that action, Inspect/Back restoration, all-category
actions, controller/mouse parity, held repeat, shop/stash/Hoods/quickslots,
continuous scrolling or absence of flashing. Do not mark these passed.
User visual approval of this implementation has not been stated.

## Remaining visible defects, bounded follow-up

1. Optional rail-art lookup still throws #1009 but no longer aborts initialization.
   Native paperdoll lookup map initialization is a source-supported timing cause,
   not yet an exact observed null-member trace. Repair without delaying item data.
2. Rarity line is visibly truncated to **“Maste”** in both details examples.
   Source owner is retained `TooltipInventory.tfItemRarity` and its native/v4
   format/width/decorate lifecycle. The exact clipping writer is not established.
3. Native circular **Drop** target remains beside the list. Its input contract
   must survive while ordinary browsing presentation is subordinated correctly.
4. Footer now receives the custom Equipment/Details/Quick Sort prompts, confirming
   further bridge progress. Native Description size/Sort/Stats are also present;
   contextual cleanup and device switching still need testing. This is not proof
   of two separate footer renderers, nor approval to redesign the accepted footer.

Do not make another package solely because these images arrived. The next gate
is **one ordinary reversible equipment action**: select an unrestricted starter
sword, unequip and re-equip it, then confirm it stays selected, the notch/model
update, and browsing continues. Disglair cannot be used for an unrestricted-equip
test at level 1. Capture a short sequence/recording to assess flashing and focus.
Then test Inspect/Back on the same item before expanding scope or visual work.

No new binary build, native cook, live deployment, settings, merge or save edits
were made for this evidence review. Original r4 package remains the candidate;
rollback is still disabling it and manually redeploying accepted Menus v4.
