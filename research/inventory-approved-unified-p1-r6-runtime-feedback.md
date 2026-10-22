# Unified Inventory r6 — user runtime acceptance of functionality, remaining details flash and visual gap

**22 October 2026.** The user supplied two screenshots and reports:

> Everything that was faulty works now, the only issue is this when I scroll the item doesn't switch the details seamlessly but with a couple of frames of how the image 1 is (basically different font, always white and without anything) so it creates a weird effect when scrolling through the items. Visually it is obviously quite far away from the concept.

**Authority:** This is positive user runtime feedback that prior reported **functional defects now work**. It is **not** a complete item-parity audit, compatibility certification, acceptance of the overall visuals, or proof that every special-mode action was tested. The visible row gold selection and matching full second-frame details strongly support the r6 selected-row correction in game. Exact deployed package hash is not supplied in this message. Screenshots live in the conversation, not this repository.

## Direct screenshot difference

- **Frame A / intermediate:** "Witcher's steel sword" appears as a plain large white title in the middle column, with no typed subtitle or detailed stats. Item row selection and Geralt remain.
- **Frame B / completed:** same selected row, now the native rich details field: all-caps steel sword item name and subtitle, damage 22–26, armor piercing +25, weight 1.74, durability 92%, price 32, required level 1. The title's font/weight/casing and the presence of stats change suddenly on scroll.
- Both shots still have a large centered diagnostic overlay, so evaluate the non-diagnostic interface without this before final visual acceptance. Existing left category rail and right live Geralt are visible. The current scene/background is much plainer/darker than the approved concept and the character is harshly lit relative to the surrounding UI. Original approved composition remains the user's visual authority; do not infer permission to shrink Geralt or overhaul layout.

## Source-confirmed cause of transient text flicker

In `src/inventory/unified/Scene.asinc`:

- `aiEnter` creates `aiPendingName=aiText(aiScene,"",761,228,435,32,0xD7D0C2)`, a **separate generic text field**, not the formatted native tooltip presentation.
- `aiSelectData` on selection or forced refresh sets `aiPendingName.text=...`, then calls `aiTip.aiPending(aiCurrentID,...)` and dispatches the native async `OnApprovedDetails` event with `++aiRequestSerial`.
- `src/inventory/unified/Details.asinc::aiPending` executes `if(aiItem!=id){visible=false;iaiScr=0;}`. Thus the real persistent tooltip **disappears** for a changed ID while waiting for the new payload.
- `aiPayloadApply` checks actual `ItemId` and request serial, runs `aiTip.aiPresent(payload,aiDetailsRect)`, then clears `aiPendingName.text=""`; `aiPresent` sets the native tooltip data, validates, and makes it visible.
- The source therefore deliberately creates precisely the two visually different states the user photographed. This is **source-confirmed design behavior**, not necessarily a font asset or race condition. Async timing determines how many frames the user sees the placeholder. A separate inherited native-tooltip field formatting/validation issue could exist but is not required to explain these images.

### Preferred bounded correction

1. **Never display `aiPendingName` while ordinary item selection is pending.** Remove/suppress that separate placeholder in browsing; reuse normal formatted details only. Do not replace it with a new temporary title of a matching font.
2. Keep a **stable mounted details presenter**. During a new item request, keep the *previous fully formatted panel* visually stable until a matching current-ID/current-serial payload is ready, then swap/update as one visual commit. No hide/show intermediate, field-by-field global font resetting, disappearing text, or layout motion.
3. A previous-item panel is temporarily **stale** while fetching. Do not dispatch actions using its old ID and do not misrepresent stale data as current; keep logical selection authoritative. If visible latency becomes substantial, investigate a **small bounded item-ID+revision cache or prefetch** (adjacent visible items only) to avoid repeated waits; invalidate on equip, item update and ownership/quality change. Never eagerly fetch every item/full tooltip in a huge inventory.
4. Determine if `TooltipInventory.data=value; validateNow(); visible=true` actually produces one visually atomic update at runtime; if it internally tears down content over multiple frames, consider an invisible back buffer / native tooltip clone with **single frame swap** after validation. Do not implement heavy double tooltip infrastructure unless the simple keep-and-commit approach is empirically insufficient.
5. Add a test reproducing selection A→B with delayed native response, including duplicate/stale events and controller rapid scroll. Assert no temporary generic title, no disappearing entire panel, no stale-response override and stable layout. Then verify with a short video or two-frame comparison in game. Do not assert offline static passing proves a flicker-free render.

## Separate visual gap relative to the user-approved concept

User explicitly says visuals are **still far from the reference**. Treat this as a second scope, **after details transition is corrected**:

- The approved category rail/list/details/Geralt relationship should remain, as should the accepted notch and current functioning interactions. Avoid random proportional redesign.
- Restore **cohesion**: accepted reference uses integrated neutral charcoal texture/lighting and subtle character grounding. Current inherited black canvas and hard-lit bright Geralt feel detached. Scenic 1:1 replication is explicitly unnecessary; a simplified appropriate treatment is allowed. Don't return to flat green/grey opaque panels or equipment-orbit ornaments.
- Refine **visual styling toward the reference**: classic Gentium hierarchy and consistent item names/secondary text, readable persistent details, restrained selection/gold accents, category-row presentation/icons, and context-sensitive non-overcrowded footer, without altering the user's previously approved region proportions and character prominence.
- Existing optional rail icon lookup fault TypeError #1009, rarity text clipping and overlong native footer remain known technical/presentation issues (unless newer running state proves they are fixed). Use correct runtime symbols and app owners, not guessed asset calls.
- Do one **visual finish pass** after settling the transition, with before/after screenshot review against the exact approved reference at the same resolution and input mode. Don't implement Review acquisition persistence, merchant/stash changes or new QoL modifications in this pass.

## Next scope and safety

The old show-stopping "no data/rows/interaction" bugs are no longer the top priority on user's current test. Prioritize **details transition, then reference fidelity**, preserve the now-working runtime behavior. Keep diagnostic overlays off for aesthetic comparisons. Offline tests and controlled reconstruction are still not native validation; no future success claim without in-game evidence. Do not automatically edit working game/Vortex/settings/saves; package only a rollbackable candidate for manual testing. Keep all vendor assets and images private/gitignored.
