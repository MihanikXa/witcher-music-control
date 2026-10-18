# P2 runtime rejection — 18 October 2026

Direct user feedback:
> Looks and feels awful ngl. Detached huge low-res icons, with small by comparison also detached geralt, dark green background that looks completely off, confusing layout, inefficient use of space. Nothing works here ngl. The thing also flashes a lot, with like little dissapear appear when doing some actions.

**Status: explicitly rejected.** Earlier screenshot review (research/adaptive-inventory-p2-runtime-first-screenshot.md) was too optimistic. P2 is not the next visual baseline. Preserve the candidate only as test and compatibility evidence.

## Source-supported hypotheses, NOT verified causes

- Geometry.asinc scales sparse items to 128 units vs native 64; Gallery.asinc scales existing slot renderers, plausibly explaining the large blurry art.
- Menu.asinc uses opaque green-tinted fill 0x0C0E0C; user dislikes its appearance.
- The character scales only 1.10 relative to baseline; there is no integrated visual relationship between Geralt, gallery and selected-item details.
- Gallery.asinc p2Populate tears down and reconstructs renderers on some item updates; Menu.asinc p2Tick repeatedly manipulates visibility, target states and layout. These are possible flashing mechanisms but **no runtime root cause is established**. Need frame/event/visibility traces when selecting, equipping, inspecting and switching input.
- Native test/cook success and real tooltip data do not establish acceptable UX.

## New sequence

1. In a cloned test Vortex profile, exit and disable modAdaptiveInventoryP2 (and keep P1/v1 off), restoring accepted Menus v4 as Inventory owner. Don't change other working packages, saves or merges.
2. **Stop patching P2 geometry.** Before coding again, create a static full-size visual composition using actual appropriately scaled Witcher items/Geralt, two representative inventories (6 items and populated), shared header and legible responsive category/footer. Seek explicit user visual approval.
3. Prioritize **predictable native-resolution item scale**, stable spatial structure regardless of inventory count, integrated selected details, larger purposeful character presentation, no old slot-orbit decorations and no green canvas.
4. Diagnose and eliminate flashing with live reproduction/instrumentation, not guesses from source. Do not mask the problem by reducing animation timing.
5. Then implement one narrowly gated prototype with visual and input regression checks. Defer additional QoL mods, materials and cleanup until visually accepted.

Explicit user complaints outrank all prior assistant-inferred recommendations to treat P2 as promising.
