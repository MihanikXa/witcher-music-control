# Proposed resolutions — review required

No live installation changes are authorized by this audit's first-pass scope. All payloads are private local review artifacts. Six file/text conflict units are covered: five existing script merges plus one newly staged English localization merge. One additional installation correction is staged. Twelve confirmed conflicts plus one combat overlap remain unresolved; eight have a conditional priority proposal, which is not a merged quest patch.

## Safe/reversible review packages

S1–S5: retain current mod0000_MergedFiles. The 13 installed source contributions were replayed using current Steam-verified vanilla in three-way merges; every result was conflict-free and identical to the current merged text after line-ending normalization. Reference copies are under patches/verified-existing-merges. They are not new replacements and need not be deployed. Function signatures/imports remain as in the current merged files; compiler validation is still required.

L1063514: patches/localization/Mods/mod0000_AuditCompat/content/en.w3strings contains only the Blood Ties letter ID. It preserves UPR's full added paragraph while fixing “born” to “borne”, joining clauses with “but”, removing a double space and correcting “as a I write”. It has no localization key records or other IDs. Author helper write/read roundtrip passed. Preview: patches/localization/letter-before-after.md. Put this small patch ahead of Grammar and UPR, below the existing merge; English only. Readability and runtime string winner must be checked after separately approved deployment.

O1: patches/arrow-deflection-layout contains the existing script, 18 translations and the existing menu XML at the correct archive root. Content is copied without alteration and without Vortex markers. Import/reinstall through Vortex with a corrected installer topology; do not edit the current hardlinks or create two active copies. The existing wrong-root payload is inert and must not be purged during this review. After deployment approval, retain its files until the Vortex-managed replacement and rollback path are verified.

O2: make Outfit Wheel explicitly enabled in the approved Vortex/persistent priority scheme. The complete candidate is patches/load-order/mods.settings.proposed, but it also contains the conditional quest reordering; do not install it wholesale as a “safe-only” change.

## Quest resources Q1–Q8

Minimum candidate: UPR before BIA, as UPR's author instructs. This restores UPR's overlapping behavior but may hide BIA changes if UPR's resource does not incorporate the installed BIA version. It is **not independently verified to preserve all features**. The staged load-order file is clearly labelled conditional and must not be deployed until reviewed.

For a feature-preserving resource patch: obtain compatible original mod source/quest graphs for the installed versions; export both plus current 5.0 vanilla through supported REDkit resource tooling; compare changed nodes/links, facts, conditions, action points and scene choice transitions; combine independent changes; validate reference dependencies and recook a dedicated small patch bundle. Test the exact quest paths on disposable test saves after approval. Where nodes implement contradictory quest design, present the exact mutually exclusive behavior for user choice. Current tooling cannot supply that graph diff; no fabricated binary patch is included.

Known gaps: exact BIA shop and q206 attack changes; exact mapping of q107 phase changes; whether UPR incorporates BIA 4.0.3. Historical author documentation helps identify risk but cannot close these gaps. Priority alone is acceptable only if incorporation or an explicitly accepted loss is proven.

## HUD H1

Use supported Flash source tooling to retain SAH artwork clips/timelines and transplant Bestg's mcWolfsHead.BG2_SetStance contract into a single resource, then export/package it with a compatible REDkit pipeline. Keep both script implementations. Validate all SAH styles, health/stamina/toxicity/sign states, stance updates, Ciri, save/reload and recreated HUDs. No source FLA or verified existing combined resource was available. Giving either original resource priority loses the other's resource-level changes; stop for an explicit decision if source integration is unavailable.

## Remaining localization and combat

L1092187/L1130095/L391138: choose the intended noun, tense and dialogue segmentation using voice/dialogue context, then extend the one-ID patch only for approved text. Do not duplicate both strings under one ID or silently prefer an editorial version. L558403 is cosmetic and can remain Grammar-first.

C1: obtain BloodAndSteel's matching compiled source or author compatibility guidance and unify speed multiplier ownership/reset semantics with Bestg/Combat Speed. Until that is possible, no automatic removal or speed-disabling settings are applied. Current test-build notes increase uncertainty. Any “choose one speed controller” approach requires user acceptance of the precise feature loss.

O4: identify why metadata.store was regenerated/modified (existing logs/stamp/tool history), then use a supported metadata rebuild or verified restore only if justified and separately approved. Steam verification would also affect managed input.xml, so blind repair is inappropriate.

O5/O6: retain current input.settings; propose unused context-specific bindings for the missing FriendlyHUD and Hoods actions, with collision checks. Binding the two defaults to IK_9 would discard one intended action. No mass import of sample controls/preferences is staged.

## Review and deployment sequence

1. Review conflicts.md, the proposed letter, and this file. Approve individual packages and explicitly state whether deployment and subsequent game launch/test are permitted; these are separate approvals.
2. Before live deployment, rerun tools/validate-review.py, inspect Vortex profile/order and make fresh independent backups of the original Arrow package, controls, deployment manifests and affected Vortex metadata. Stop if hashes differ from the audited baseline.
3. Import the approved tiny localization package through Vortex. Correct Arrow's package root using Vortex's installer/reinstall workflow or a separately named corrected local package with the original package disabled only after explicit approval; preserve the original package for rollback. Require Mods/modArrowParryManual to exist and share identity with its corrected managed source.
4. Set only approved priority relationships in Vortex and persist them. Keep the current quest ordering unless the conditional UPR-first change has explicit preservation evidence or an accepted trade-off. Do not blindly copy the whole candidate mods.settings because Vortex rewrites it and it includes unresolved choices.
5. Deploy only approved changes through Vortex. Recheck deployment identity, actual mods.settings, new string IDs/resource winners and compiler result. Do not regenerate the five current merges without reviewing a copy first.
6. Launch only with separate permission. Test combat/dodge, both HUDs, Outfit Wheel F3, Arrow timing, Hoods/FriendlyHUD shortcuts and quest cases listed in validation.md. No save edits; use disposable test saves or independent copies, never overwrite a sole existing save.

Approval of the staged localization/Arrow packages does not approve binary quest/HUD edits, disabling combat mods, control reassignment, Steam repair or a game launch.
