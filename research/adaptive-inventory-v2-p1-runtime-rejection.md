# Adaptive Inventory v2 P1 — first runtime screenshot rejection

**17 October 2026.** User-provided actual 1649×928 Inventory screenshot of the
private P1 running over Menus v4. The user directly stated, verbatim:

> No idea the fuck this is

**Status: explicitly rejected as a visual/UX result.** This screenshot confirms
that at least some P1 visual and layout code ran, but does not establish every
input interaction or which specific settings/controls succeed. Compilation and
the 16 static/native tests were successful **but do not override in-game
reception**. Do not present P1 as user-accepted.

## Directly visible defects (assistant observations, not further user quotes)

1. The screen resembles a damaged **juxtaposition of two menu systems**:
   inherited Inventory/Equipment secondary icons and central EQUIPMENT label
   compete and overlap the accepted Ink & Iron shared horizontal top menu.
   The new code did not design one unified header/subnav.
2. Only two weapons and four armor pieces form isolated clusters at the top left.
   Despite a 9-column/6-row scaled grid, **visual browsing is small,
   fragmented and uncomposed**, with vast unused black space. Simple
   scale and x/y changes do not solve native section-based grid reflow.
   A sparse level-1 inventory is an essential design case, not a screenshot
   to discount.
3. Geralt is large and visible but floats as a **disconnected right-hand
   mannequin**, with no coherent relationship between current selection,
   context/action and character.
4. The lower item-summary zone is **blank** despite a selected sword.
   This fails the central premise of immediate meaningful comparison.
5. Two chunky custom Inspect/Equipment rectangles at bottom are present
   together with the untouched dense native input-feedback footer.
   Commands overlap and repeat, especially at the 928px screenshot output.
6. Ambient Ink & Iron engravings remain but do not fix hierarchy.
   Existing v4 art and layout outside Inventory should remain frozen.

## Source-grounded contributors (do not claim verified runtime root causes)

- `src/inventory/adaptive/AdaptiveMenu.asinc::qfAdaptiveRefresh` assigns
  fixed grid x=72/y=100 and scale 1.4, a fixed Geralt x=1060 and +12% scale,
  and summary x=72/y=816 plus buttons y=992. It moves native grid rather than
  implementing item-responsive placement and does not show a working top-level
  composition contract for the native Equipment bar and icons.
- `tools/patch-adaptive-inventory.py` preserves native section grouping in
  InventoryTabbedListModule/SlotsListGrid, so a nine-column grid does not
  guarantee the sparse items visually occupy the intended browse area.
- `qfAdaptiveRefresh` populates summary text only if
  `tip && !ContextInfoManager.getInstanse().isHidden()`, and obtains
  `tip` via `iaiDockedTip()`. The screenshot establishes blank display,
  **not** which condition failed; trace selected-item event, payload, movie
  visibility, TextField font and display order under the real runtime.
- `qfAdaptiveButton` draws separate 270x38 buttons at y=992; no corresponding
  native menu input-feedback cancellation/replacement is demonstrated.
  The duplicate footer visible in screenshot matches that code behavior.
- Static suite `tests/test_adaptive_inventory.py` checks compilation,
  presence/translation of helper behavior, retained interfaces and archive
  hashes but not GUI overlay bounds, real-time payload availability, 928p
  screenshots or usability.

## Decision and next gate

**Do not try to rescue P1 by moving a few native elements.** Fall back to
Menus v4 for normal game use in the test profile: fully exit game; disable only
`modAdaptiveInventoryV2GearP1`, keep Menus v4 and its art modules/HUD RC2.
Do not change saves/merge/settings. Preserve P1 ZIP/src/tests as an
unaccepted functional experiment.

Next: redesign from one actual scene hierarchy with **one header layer,
one category strategy, primary item browsing, a visible contextual summary
and a modest unoccluded Geralt preview**, with no duplicate footer. Build a
sparse and populated inventory plan **before** running another expensive
native pass. Use actual native component ownership/masks/bounds and
disambiguate whether top native controls must be hidden or relocated in Gear
only, preserving their functional callbacks. Make the summary's tooltip-data
binding operational (trace, not a fake preview); ensure responsive coordinates
at 1080p/4K and current controller/input scaling. Check Shop/Stash mode
restore and Hoods quickslot/secondary equipment access.

Only progress after acceptance based on in-game **image and functional
interaction**, not checksums. No new permanent tabs/animated dashboards/
inventory QoL additions required in this rescue.

User screenshot is in conversation attachment, not in public repo.
