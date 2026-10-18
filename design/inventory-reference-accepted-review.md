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
- Equipped state is the only design element the user suggested might merit refinement: subtle but unambiguous native equipped badge/corner marker in item list and accurate compare/equip actions. Do not add an equipment orbit, a second equipped sidebar or another competing item collection.
- Don't make unsolicited changes to typography, button footer, Geralt proportion, background or global menu while implementing this direction.

## Review — proposed behavioral contract, not final user-approved eligibility algorithm

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
