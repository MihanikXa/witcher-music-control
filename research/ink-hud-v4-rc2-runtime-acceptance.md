# HUD v4 RC2 — user runtime acceptance and next phase

**15 October 2026, user report.** Latest explicit user statement:

> Check repo. Everything works now. Time to move on to next tasks.

The statement follows local Codex's `6a246f5` RC2 shared HUD footer fix, which removed the unbound `buttonsSize` lexicals. It is **in-game user acceptance**, not an additional repository-run runtime test. The user does not separately enumerate every specialized edge-case in this sentence; don't fabricate case-by-case pass logs or re-label immutable RC2 build `runtime_tested=false` receipts as having performed runtime tests.

## Accepted current baseline

- Treat RC2 as working and **freeze** the previously user-accepted v4 visual choices: enemy health `#B94A40`, hostile name `#D9695A`, lag `#C77D6E`, subdued-but-contrasting attack warning, compact geometry, Ink & Iron quickslots, reduced circular button letters, glyph outer scale, dialogue/shadows, and coexistence with SAHUD/FriendlyHUD/OW/Hoods and existing UI stack.
- The previously broken Tab/LB circular radial sign/quick access selection no longer requires an active debugging workstream; user reports **everything works**. The exact offending `buttonsSize` was verified from actual installed P-code by Codex; RC2 removed only two offending statements in one HUD root class, all other packaged HUD resources exact versus RC1.
- Keep intact RC2 private ZIP and its hashes/receipts/rollback; no global toolchain optimisation, redesign of accepted HUD, repeated diagnostic packages, or unrequested live deployment.

## Next unfinished workstream

Continue the approved one-screen **Inventory vertical slice** in `design/inventory-ux-direction.md` and `design/ink-and-iron-visual-first.md`; the repo contains the user-approved specification but no corresponding implemented prototype at this revision. First read-only map the **effective Hoods-owned** `inventory/panel_inventory.redswf` and Ink & Iron version; identify equip/unequip, previews, Roach/hoods, quickslots, sorting, stats, comparison and keyboard/controller interfaces, then propose/implement **one bounded functional Gear grid** within the same screen and reversible private package. Character Geralt stays a preview; equipped items get clear grid markers, no orbit/radial constellation, details/comparisons in one focused region. Do not replace whole interface or build shop/map changes until a working inventory prototype has been validated. Respect actual installed ownership and private assets.
