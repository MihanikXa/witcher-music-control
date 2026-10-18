# Accepted visual direction — category → item → decision + Review

**18 October 2026.** User supplied a concept image with a slim accepted-style Witcher top navigation, dark neutral subtly textured backdrop, slim **vertical category rail on left**, compact **text-and-icon item list** in adjacent column, one persistent **selected-item details/stat region**, full-body Geralt at right, and one restrained bottom hint row. It is in the conversation as an uploaded image; the image itself is **not in this repository**. Existing P1 and P2 code and layouts were explicitly rejected and cannot be used as visual references.

## Latest explicit user corrections

User: **"I like this concept though that I got from my own prompt"**.
After the assistant proposed shrinking Geralt, changing detail hierarchy, compressing the category rail and revising footer, user clarified verbatim:

> I disagree with all your refinement notes, except for equipped state maybe. And I would add recent category as the first one, or not recent but the one we planned where I can look what's new that is important but not 100th material picked up or something, or whatever our concept was.

**Binding design direction:**
- **Preserve the concept as shown.** Do not independently shrink Geralt, adjust density/spacing of the rail, alter mid-panel hierarchy or rework footer. The screenshot is a user-selected *visual reference*; it is not proof of technical viability or pixel-exact approved asset coordinates.
- Do **not** revert to the large tile-based Inventory Grid/Gear gallery or Gear/Usables/Satchel-only category strip. The reference prefers **a one-column item list** with contained icon, name, concise subtitle and a distinct selected-item details panel.
- **Add a first category above Weapons** to handle actionable newly acquired items, provisionally titled **Review** or **To Review**. This is NOT an unfiltered Recent tab, nor every item that acquired the vanilla 'new' flag.
- Equipped state is **settled**: reuse the exact small notch/stripe already present in the user's accepted current design. Confirm its actual implementation ownership before porting it. Do not invent alternative badges, an equipment orbit, a second equipped sidebar or a competing item collection.
- Don't make unsolicited changes to typography, button footer, Geralt proportion, background or global menu while implementing this direction.

## Final explicit user approval — 18 October 2026

The user confirms, verbatim:

> Equipped is easy, just a small notch/stripe that we already have in our approved implemented design rn. And I agree on review addition and design.

**Decisions finalized:**
- Reuse **the exact existing, user-approved small equipped-item notch/stripe from the accepted current Inventory implementation**. Do not invent a new badge, prominent marker, second equipment rail or other state treatment. Find and preserve its exact source/movie ownership from Menus v4/current approved installed resource; the earlier P1/P2 rendering implementations are rejected even where they incidentally use native markers.
- The **selected concept's overall visual composition and the first-category Review attention model are approved**. Do not revisit proportions, typography, category density or footer without new user feedback.
- **Review is not Recent:** noteworthy newly acquired items enter a persistent, dismissible review list; routine repeated materials do not. The high-level principle is approved, while specific eligibility thresholds, edge cases and persistence choices remain engineering details to substantiate before shipping.
- Next step is a source-mapped implementation plan based on the approved reference, not more speculative visual alternatives or resurrecting P1/P2 layout.

## Review — approved principle; detailed eligibility policy still to verify

Purpose: surface newly acquired things that plausibly require **a decision**; ordinary accumulated materials should not generate inspection chores. The first category lives within the same Inventory view and uses the **same item list, selected-item details and Geralt placement**. A small count of pending items may appear beside Review; no separate popup or intrusive alerts.

Candidate inclusions for first pass (need user signoff on policy): newly obtained weapons/armor worth at least a glance (without assuming higher damage means better); new usable recipes/diagrams or distinct actionable items; unusual/unique nonroutine loot if native metadata can support it. Candidate exclusions: every repeated herb, ore, common monster material, mundane stack quantity increase, book already read, redundant consumable replenishment. User's 'not 100th material' explicitly rules out a chronological firehose.

Data model/technical care:
1. Base on *real acquisition events*, not a reused new-item flag or invented acquisition timestamp. The supplied `Recent Loot Tab` reference tracks `OnItemGiven` with saved item IDs, quantities/sources, but has only one aggregate saved `recentLootViewed` flag (see `research/adaptive-inventory-v2-qol.md`). Do not naively reuse that as per-item dismissal or assume IDs persist unchanged across stacking/transfers.
2. Need saved per-item **pending/reviewed/dismissed** states and the ability to review/dismiss without removing or selling an item. Review should survive reopening and loading until legitimately cleared; do not clear everything merely when Inventory closes or focus passes over an item.
3. Items always remain accessible in their ordinary category, including materials suppressed from Review. An overrestrictive filter must not hide valuable gear; demonstrate inclusion/exclusion cases on sample acquisitions and consider a restrained policy configuration later.
4. Ordinary equip/inspect may count as deliberate review; non-actionable list items can be dismissed with a low-friction explicit gesture. If Review is empty, don't force the player to stare at an empty first page; a suggested default is last-used category, though actual behavior needs user agreement.
5. Don't add automatic sell/dismantle or destructive cleanup to Review. It's an **attention filter**, not an item deletion or quality ranking engine.

## Integration and future work

- The **visual direction is now settled provisionally by the user's preference for this screenshot**. Next practical step is to inspect a selected reference screenshot and map visible sections to available 5.01 native Inventory components, then design a faithful implementation plan in phases.
- Implement and test the approved **category → item list → details → Geralt** arrangement first, with stable native-size icon art, native equip/tooltip/Hoods/Roach/quickslot functionality and keyboard/controller behavior. **No dynamic icon doubling, opaque green backgrounds, orbit art or renderer teardown flicker.**
- The Review data model may be developed in parallel as isolated source/test work, but don't make it a blocking dependency for first visual correctness.
- Respect Menus v4/Gentium/item art/HUD RC2 and all source ownership constraints.
- The image example displays populated list rows and stats, but static generated image values are **illustrative**, not validated in-game item data.

This document supersedes earlier assistant-proposed Gear gallery, small-item grid and layout tuning; preserve historical implementation notes as rejected experimental evidence.

## Current source map and staged route — 18 October 2026

The approved screenshot is mapped to Witcher 3 owners and source boundaries in
[the implementation map](inventory-approved-implementation-map.md), with
[Review behavior](inventory-review-behavior-contract.md).
These are planning specifications, not a compiled candidate or permission to
change the live game. The exact screenshot must also be copied to the ignored
local `reference/inventory-design/` checkout for Codex; do not visually
approximate using P1/P2 source.


## Latest user acceptance — 18 October 2026: layout approved, environmental treatment flexible

The user reviewed Codex's sparse/populated Gate 1 visual proofs and replied:

> Agree on all, and by the way we can for sure, simplify the background and ground substantially and don't have to reproduce the lighting 1 to 1 either, but the cohesion of the whole ui and layout should be analogous, as well as being aesthetically pleasant.

This is explicit approval of the **current source/visual direction** and a
constraint correction, **not** acceptance of a playable implementation.
Keep the selected concept's structural hierarchy, rail and row scale, details
placement, Geralt's relative composition, typography, approved equipped notch,
and footer. However, exact background scenery, fog, stone ground, pose-specific
lighting and promotional scene matching are **not hard requirements**. An
appropriately simplified **neutral dark, ink/charcoal background and subtle
grounding/shadow** are acceptable if they retain deliberate visual cohesion
and aesthetic quality. Do not interpret simplification as approval for the
flat green-black P2 panel, ungrounded Geralt or a visually disconnected void.

This approval unblocks **a narrowly scoped playable Weapons slice**. A
realistic live Geralt renderer and source-supported simplified atmosphere are
appropriate; make exact scenic replication a non-blocking optional improvement.
User in-game visual and interaction acceptance remain separate gates.

