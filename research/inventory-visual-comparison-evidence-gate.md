# Inventory visual comparison — evidence gate before r8

**23 October 2026 · user's explicit correction.**

User says: "Okay, no. I think we need a screenshot of the game without console and reference to make judgements, some of the stuff you desribe is vague, some is overconfident, some isn't true."

## What has and has not been approved

- **Approved:** original reference composition, overall UI cohesion, proportion/position of main regions and Geralt, existing equipped notch, working Inventory functionality. Background scenery/ground/exact lighting need not match literally.
- **Source-backed:** r7 removed the known generic pending-title/hide transition, but r7 has not been game-tested. The user accepts deferring a *dedicated* r7 playtest.
- **Not established:** claims of broken visual hierarchy, inadequate background, wrong Geralt lighting, icon inaccuracies, footer problems, rarity clipping in the current capture and any priority ordering of cosmetic changes. Older diagnostic screenshots do not suffice for these claims.
- **Not authorized:** implementing the previous all-in-one r8 visual finishing handoff, making speculative aesthetic changes or changing accepted layout.

## Required clean images

1. Capture the **actual running player Inventory**, with a real selected item and its native formatted details, **F8 diagnostic overlay hidden and developer console closed**, as close to native 16:9 and original resolution as possible, uncropped and unretouched. Use the existing working build; **do not require a new install or playtest of r7 just to compare appearance**.
2. Compare with the **exact already user-supplied approved image** in `reference/inventory-design/approved-inventory-reference.png` (local ignored private copy; verify existing recorded hash when accessed). Use the image in conversation if reviewing here. Match aspect/viewport and selected context as closely as practical; differences in actual loot, font rendering and game lighting should be treated as legitimate data/context differences, not automatically defects.
3. Evaluate **one component at a time**: shared header, category rail, item rows and selected/equipped states, selected details, model positioning, background/ground treatment and footer. Give measured/visible comparisons, not generic claims that something is 'harsh', 'disconnected' or 'utilitarian' without a concrete feature. No inference that UI differences are bugs merely because reference is AI-generated.
4. Mark every proposed change as **observed difference**, **possible cause**, or **user preference requiring confirmation**. Ask the user which *specific* visible discrepancies they want altered before authoring Codex work.
5. Only then create one bounded, concrete implementation prompt; preserve native data and working input actions. Include r7 transition smoke test in eventual next full candidate, but do not claim already game-tested.

**Stop condition:** Without a clean game screenshot, do not start another visual patch, implementation or release. Historical `design/inventory-visual-finishing-after-r7.md` is no longer active authority.
