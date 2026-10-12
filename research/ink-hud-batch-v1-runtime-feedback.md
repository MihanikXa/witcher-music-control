# Ink & Iron HUD batch v1 — user runtime acceptance and visual corrections

**Feedback:** 12 October 2026. **User reports full combined batch functioning in-game**, but does not accept every visual treatment. This is a user report, not a complete itemized acceptance test; do not rewrite immutable offline release receipts or claim every edge case was separately tested.

## Direct user statements (verbatim)

> Everything works, although I am not a fan of enemy bars, it's just a bit too much, I would like it to be more minimalistic, the boss is fine and quick slots I preferred the ones I had earlier too, the rest is good. Also, not a fan of controller buttons, the vanilla is even worse, but I would love it if they were very minimalistic and modern without any gradients

> hud_iteminfo is just quickslots in the left bottom corner? Enemy bars I agree with your direction but maybe also make them thinner overall, they are too tall.

## Accepted / needs revision

- **Functionality:** overall batch reported working. Other HUD appearance is acceptable **as currently observed**, excluding the listed visual problems. Preserve the successful adaptive bars v1 and existing SAHUD/FHUD functionality.
- **Enemy bar `hud_enemyfocus.redswf`:** too visually busy and specifically **too tall**. Prioritize **reducing height / thickness**, not only removing ornament. Design hypothesis: start by testing about **30–40% less vertical bar height** while retaining approximate width; this numerical range is an **assistant proposal, not a user-specified dimension**. Reduce decoration, extraneous framing, vertical spacing and excessive visual weight. Preserve target legibility, lock/health feedback, NPC semantic colors and subdued shadow. **Do not modify bossfocus**: the user explicitly likes the boss presentation.
- **Quick slots:** the user prefers the **pre-batch quickslot appearance**. Existing evidence identifies `hud_iteminfo.redswf` as the bottom-left quick-access item cluster, with potion/item slots, icons, hints, radial-return, switches and visibility callbacks. `hud_radialmenu.redswf` is **separate**. First produce an isolated batch variant **excluding `iteminfo`** so the original installed owner wins, and check visually and functionally; do not remove the radial menu or unrelated HUD components by mistake. If the left-bottom cluster is influenced by additional shared/root widgets, identify them precisely. Retain batch iteminfo only if actual before/after feedback warrants it.
- **Controller buttons:** neither vanilla nor current Ink & Iron buttons are visually preferred. Desired target is **very minimal, modern, flat, without gradients**. Audit the actual prompt/button glyph owners (including common/root resources, Outfit Wheel and controlsfeedback) and build a compatible flat style, with clear Xbox labels and interaction/hold legibility; do not replace input or event handling.
- **Other components:** retain the currently working Ink & Iron bars, buffs, quests, minimap, dialogue, notifications, etc. Avoid a fresh global HUD redesign.

## Next development scope

One **combined targeted refinement iteration**: narrower enemyfocus drawing, prior quickslot look restored in the combined build, and flat controller-button glyph prototype. Retain component-level rollback. Build only necessary visual patches. Keep third-party assets and compiled private releases out of Git; live Vortex deployment is user-controlled. Use the [batch implementation and rollback tooling](ink-hud-batch-v1.md) as the technical base.

**Current released bundle remains a valid working functional baseline**, but the final aesthetics of enemy bars, iteminfo and controller glyphs are not accepted.
