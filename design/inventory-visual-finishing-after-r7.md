# Inventory reference-fidelity finishing — separate from r7

23 October 2026. Plan only; implement after the user verifies r7 transitions.
Keep rail/list/details/Geralt proportions and working interactions. No new
concept, Review ledger, merchant/stash changes or global HDR/lighting adjustments.

## Evidence and comparison

Visual authority: unchanged authorized local PNG,
`reference/inventory-design/approved-inventory-reference.png` (1672×941,
SHA-256 `b1443ffafc009a5f123d6c971e3ea1e47572763b229595ab78d76799bde87313`).
Private sparse/populated proofs: `build/inventory-approved-gate1/`. Proofs contain
reference scenery/illustrative details; they are not runtime assets or validation.

The r6 user's two-frame observations are recorded in
`research/inventory-approved-unified-p1-r6-runtime-feedback.md`: gold row selection
works; full formatted native sword details return after a plain title; environment
remains black and character is harshly lit. The prior locally retained r5 screenshot
is useful for unchanged region/background/footer ownership only, not r6 selection
acceptance. Capture r7 with overlay off at the same resolution/device as the
reference comparison before implementing the finishing candidate.

| Priority / owner | Approved reference | Current game evidence | Smallest proposed finishing change |
|---|---|---|---|
| Essential: Inventory background, `aiScene` / `iaiArtHost` | Neutral charcoal atmosphere connects information regions and character, soft tonal transitions and understated ground | Near-black empty field and bright model feel disconnected; earlier rectangle explicitly rejected | One Inventory-only, stage-sized, softly feathered neutral tonal/texture treatment behind all four regions; validate alpha/masks against footer and safe areas. No independently boxed panels, orbit art or global texture-cache replacement. Reuse accepted private texture only if appropriate; otherwise original understated procedural treatment. |
| Essential: native tooltip hierarchy, `TooltipInventory.iaiStyleDocked` / `iaiDecorate` and field bounds | Clearly separated name, type, rarity, short prose, primary stats and quiet secondary properties | Native all-caps heading/type, clipped rarity (“Maste”), dense/uneven vertical gaps, harsh white emphasis | Measure real Gentium fields; correct rarity width/wrapping and internal title/type/rarity spacing, then align native stat/comparison columns. Preserve all real properties, restrictions, set bonuses and persistent panel. No invented descriptive prose or altered item values. |
| Essential: category art, `aiConfigureRailIcons` | A small readable symbol aligned with each category label | Some native symbols absent or inconsistent; optional `1 lookup #1009` remains | Resolve exact post-population source slot/map or attached native tab symbols; extract/reuse accepted silhouettes at small sharp size. Do not guess label/slot keys or force early validation. Keep text-only fallback and optional failure isolation. |
| Essential: footer, `OnApprovedMode` / native context bindings / `MenuCommon` | Restrained device-specific hints and selected-item action emphasis | Native Drop, Preview, description size, sort, quick sort, equipment, details, stats can crowd one line; lingering Drop target | Audit IDs and owning handlers per Browse/Rail/Details/Aux and item category. Keep primary action, Back and current-mode hints readily visible; expose secondary native actions through an existing deliberate details/equipment context before suppressing any hints. Keep all bindings/actions reachable and native glyph switching. Trace Drop owner separately; hide it only when not an active drag/equipment target. |
| Essential: row typography, `SlotBase.aiFormatRow` | Compact name/subtitle hierarchy, quiet borders and contained sharp icons | Core proportions now analogous, but current text weight/casing/line spacing and repetitive borders feel heavier | Font-aware measurement of name/subtitle baseline and tone; adjust only internal text styles and border emphasis. Preserve row size, one-column list, pool and exact equipped notch. Test long names and current 1080p/4K readable scale. |
| Secondary: Geralt grounding, `aiModelMask`, native anchor/controller | Prominent Geralt belongs to surrounding atmosphere and ground | Model prominence retained, but hard light against black and weak grounding | First judge model against cohesive background. Add only restrained soft ground shadow/tonal falloff aligned with feet; preserve anchor/size/mask and stats transition. Investigate actual menu-scoped lighting API/settings read-only; do not promise a light change without a verified owner or alter global HDR. |
| Optional: scenic fog, ground texture, subtle highlights | Cinematic reference scenery | Functional simplified environment | Omit unless essential treatments still fail cohesion. Exact scenery, pose and lighting replication were explicitly waived. No new ornament or screenshot collage in runtime. |

## Icon dependency to establish before editing

The known optional fault occurs during `source=mcPaperDollModule.mcPaperdoll.getRendererForSlotType(...)`
before silhouette copying. `SlotsListPaperdoll.getRendererForSlotType` depends on `_slotTypeToIndexMap` populated
by native data, while unified scene startup calls the optional icon routine early.
The operation-level trace proves lookup fails, not its exact null member. Next
trace map readiness and actual slot-type keys after native population, or reuse
verified attached `TabListItemRef.mcIcon` symbols. Keep these symbols owned by
their proper library/timeline; do not move a live functional equipment target
into the rail. No full Inventory replacement resource from a QoL mod.

## Implementation order and review gate

1. Accept r7 with a rapid-selection recording; keep its source/resource baseline.
   Capture controller and mouse screenshots with diagnostic overlay off. Do not
   conceal a remaining transition behind typography changes.
2. Produce one measured comparison at 1672×941 or proportional 1080p/4K, using
   both sparse save and populated fixture; freeze outer region bounds. Record
   typography/rarity and background corrections as concrete source owners.
3. Implement essential background cohesion plus internal text/rarity fixes in a
   private finishing candidate; preserve input, actions and native data byte paths.
   Verify no hard edge, clipped text, lost stats or Stats-mask regression.
4. Resolve icon readiness and footer/action visibility as small independently
   tested ownership changes within that pass. Test both devices and every hidden
   hint's access path. Do not delete native functions to simplify presentation.
5. User screenshot review against approved sparse/populated proofs, followed by
   device switching/equip/Details/Stats and anti-flicker checks. Optional grounding
   embellishments follow only if still needed. Do not enlarge scope to Review.

The current user's appearance complaint remains open. This plan preserves the
approved composition and explicitly does not declare current visuals accepted.
