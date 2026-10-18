# Adaptive Inventory P2 — first in-game screenshot comparison

**18 October 2026.** User supplied one actual screenshot and asked **"Check repo..."**. The image is 2048×512 across the wider desktop, with an approximately 910×512 Witcher Inventory window near the center. The screenshot appears to show P2's custom composition and live selected-item summary, but **exact resource owner/installed verifier output is not supplied**. This is user-provided runtime visual evidence, **not an explicit approval or rejection**. Do not invent controller test results or treat native tests as visual acceptance.

## Build HEAD checked

- `ui-overhaul` HEAD at time of review `7009cd368e9778378c6a6cac71ae8651805897d4` — P2 implementation.
- `research/adaptive-inventory-p2-coherent-gear.md`: 13 offline tests, 24 geometry cases, native cook/validate/pack/metadata all passed, 0 native resource errors. Private P2 ZIP `deploy/adaptive-inventory-p2/Adaptive-Inventory-P2-Coherent-Gear-private.zip`, SHA-256 `0f26fea465512ca4a81c120e7e5207c014db1e912ff3e117f2bbc06518b1b415`. The shipped code reports runtime acceptance as pending.
- The screenshot itself establishes some code executing, but not exact Vortex hash or completion of all interactions.

## Directly visible progress versus rejected P1

- Slot-orbit decorations are gone from the Inventory background; global slim top navigation is unobstructed.
- Selected item **Disglair**, primary stat **Damage 99–121, +20**, and **Required Level 2** visibly populate. The selected-data/summary path therefore works at least for this one real item/state.
- No duplicate custom large rectangular buttons; a single footer hint row remains.
- Native Geralt renderer appears clean and unobstructed on the right.
- These are concrete partial improvements, not blanket design approval.

## Remaining visual and integration issues (assistant interpretation, not a user verdict)

1. **Gallery remains uncomposed:** only a few tall Gear icons are arranged in loose, lopsided clusters; items float with no perceptible scan structure or intentional relationship to the nearby summary. P2's first-fit grid is not visibly a compelling single browsable gallery. A deliberately sparse inventory is a key test, not an excuse to fill with fake items or rows of dotted empty cells.
2. **Summary is detached:** name/stat/restriction appear far to the left below the gallery rather than visually grouped with the selected slot. This is directly consistent with `p2Geometry`: gallery is **centered** inside the 57%-width content region at sparse 3 columns, but `summary.x = content.x + 20*unit`. For nominal 1920×1080: `content.width ≈1094`, 3×128 gallery width=384, left margins differ by approximately 335 authored units. Do not just scale text or move Geralt; create a single spatial anchor/container and responsive summary alignment.
3. **Secondary category navigation is tiny/low contrast:** icons under shared header are undersized and hard to interpret at screenshot scale, no explicit one-row Gear/Usables/Satchel information hierarchy. `Module.asinc` places original `mcTabList` renderers in 58% of nav width at fixed 0.62 scale; it doesn't create a more meaningful category presentation. Preserve native callbacks and selected/new state but redesign the readable affordance.
4. **Selected red X dominates artwork:** current selected sword Disglair has a huge diagonal red X. The image also shows the item requires level 2 while the save displays level 1, so this may be an authored **unusable/level gate** overlay; trace selected marker/slot art before calling it a bug or suppressing a required restriction cue. Keep meaningful disabled information, but assess how it is visually subordinate in the selected state.
5. **Footer still looks native, not P2 contextual:** visible single hint row appears to say **X Preview Item, Space Equip, R Drop, (mouse) Description size, C Player Stats**. No clear P2 Inspect or Equipment cues, despite `Footer.asinc` intending to pass composed data via `mcInpuFeedback.handleSetupButtons`. Its `p2FindCommon(stage)` requires `hasOwnProperty("mcInpuFeedback") && hasOwnProperty("mcMenuHub")` on the same display-list node; if it fails the native footer simply remains. Alternative is native feedback overwriting the temporary list. **Neither is proven**; instrument discovery, latest owner, repaint and device change (keyboard/controller) before patching.
6. **Visual cohesion:** the opaque charcoal plane successfully removes invalid old-slot ornaments, but now exposes substantial flat black negative space between actual small gallery and Geralt. Do not restore obsolete art or add gratuitous panels. Recompose scale, alignment, and sparse item grouping and optional subtle non-slot texture only where it helps.
7. **Resolution limitation:** screenshot spans 2048×512 across a wider desktop, game panel about 910×512. This establishes gross composition but cannot certify final full-screen 1080p/4K readability or real input-device transitions.

## Next bounded correction priority

**Do not start another broad Inventory rewrite or new QoL mod integration.** User requested review; these are next recommendations, not permission to deploy.

A. Verify **actual P2 Inventory winner**, and trace footer owner + prompt refresh/device transitions in game. Preserve accepted v4 when diagnosing.
B. Build a clear **sparse six-item gallery and selected-summary group**: item sizes/density, section metadata, selection geometry and summary align to **same content anchor**; keep no empty-cell wallpaper and preserve full-inventory scrolling and ID hit contracts.
C. Make category navigation **legible, distinct and single-owner**, without touching accepted global menu; preserve keyboard/pad category transitions.
D. Treat selected-item restricted/red-X state as a separate semantics audit. Don't blanket erase it.
E. Validate one keyboard and one controller shot from **normal full-screen game** plus inspect/back/equip action traces before shipping another technical candidate. No invention of gameplay tests.
F. Preserve accepted Menus v4, HUD RC2, fonts and artwork, Hoods, Smooth Map, Outfit Wheel, all local archives, release rollback. No live changes by assistant.

User screenshot remains in this conversation, not committed to the public/private Git repo.
