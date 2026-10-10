# Witcher 3 — UI Overhaul

An independent, research-first project for refining typography, text effects, NPC nameplates and interface colors in **The Witcher 3 Remastered 5.01**.

The saved Editor assets now pass a reproducible [offline cook/bundle round trip](research/editor-cli-roundtrip.md).
The Watermark failure was a stale workspace resolution issue. Editor assertion
state remains unknown; no successful imports need repeating. Computer Use is
prohibited. Independent SIL Gentium Book 7.000 English font conversion now has a validated private
QuietFolio v1 archive, and the user reports that QuietFolio works in-game. The [private shadow-only v1 trial](research/npc-shadow-v1-handoff.md)
passed offline cook/validate/bundle/atlas/ZIP gates and is now reported working
in-game by the user, alongside accepted NPC colors v4. Its unique-name Editor import resolved the save dependency; no
successful imports need repeating. Keep accepted v4 unchanged.

Current scope: **English only**, per the user's 9 October 2026 update. Phase 1
research is in [research/findings.md](research/findings.md). The supplied
Alignment Fix is not recommended unchanged for this runtime; see its
[assessment](research/alignment-fix.md). Explore the original
[typography comparison](design/comparison.html) and
[prototype plan](design/implementation-plan.md). No asset overhaul package is built
or deployed yet. The private v2 color-only trial failed for both Roach (neutral)
and Vesemir (VIP). The user then observed both names change and persist in the
[v3 diagnostic](research/npc-color-failure-diagnostic.md). The current
[clean v4 UInt color trial](research/npc-colors-v4-handoff.md) removes all diagnostic
instrumentation. The user directly observed neutral, friendly and VIP colors working and
explicitly accepted all five categories for now, including hostile/Axii not personally
observed. Color is a closed milestone by user acceptance; shadow and typography are next.
Keep v2 and v3 disabled, and preserve working v4 separately.
The native REDkit SWF now cooks with its embedded atlas after
including the official texture-group configuration. The importer still emits a
resource-state assertion, shared by unrelated controls. Saved Editor outputs
now load, cook, validate, pack and re-extract reproducibly without that assertion;
the cause and runtime risk of fresh creation remain unresolved. The additive color fallback
now compiles in the known source assembly. Its single added metadata assertion
also occurs with two no-op wrappers, with no warning or other diagnostic delta.
Full retail multi-blob coverage remains incomplete. The v2 visual failure is
recorded in the [historical trial handoff](research/npc-color-trial-handoff.md);
v4 has been observed working in three categories and accepted in all five by the user.
The exact v2 failure mechanism remains inferred.
See the current [controlled investigation](research/swf-state-investigation.md),
[bounded Editor test and manual import steps](research/editor-workflow-bounded.md),
[native NPC validation](research/native-npc-validation.md) and earlier
[Phase 2 investigation](research/phase2-validation.md). The private shadow v1 ZIP
is available locally and user-reported working in-game; evidence for individual
stress-test and other HUD surfaces remains limited.

**Next typography phase:** [Field & Folio selective utility typography](design/field-and-folio-typography-phase.md). QuietFolio already supplies the shared English literary font; the next prototype investigates an additional Source Sans 3 utility role in one safe UI movie, not a second global font replacement. The accepted v1 remains a separate rollback package.

**New text-effect direction (11 October 2026):** Interaction names must be unequivocally subordinate to NPC names (trial 17px Source Sans Regular, optional 16px), and heavy ordinary-text glows/shadows throughout the in-use UI should be audited and softened toward the accepted NPC Shadow v1 appearance. See [interaction v2](design/field-folio-interactions-v2.md) and [text-shadow unification](design/text-shadow-unification.md). This does not change installed assets or mean all text filters are equivalent.

## Current user acceptance — 10 October 2026

NPC Colors v4, NPC Shadow v1 and English Gentium Book v1 (QuietFolio) are
all user-accepted working in-game. Acceptance is a positive user report, not
independent confirmation of every glyph, scene or resolution. Preserve these
three independently reversible mods and their recorded hashes. Further UI
improvements are separate work, not automatic edits to accepted packages.

## Visual target

Clean, light, breathable and modern, **with character**. Use *Ghost of Tsushima* as a reference for restraint, hierarchy and environmental integration, **not** for copying its Japanese visual motifs. Retain the Witcher world's distinctive texture. The user prefers the **Gentium Book** reference over the original or an undifferentiated sans-serif.

Focus on replacing thick hard-edged black text outlines, overly saturated red/green text, cramped labels and inconsistent emphasis with precise typography, a restrained palette and context-sensitive readability. Do not merely desaturate all UI elements globally.

## Broader presentation roadmap

The project also has an accepted longer-term [presentation and interaction roadmap](design/presentation-roadmap.md): contextual exploration information, navigation/discovery, menu composition, notification restraint, camera/audio coordination and unified UI polish. This extends the **long-term design target**, not the immediate implementation authorization. Finish the existing NPC-nameplate and typography build gates first.

## Project boundaries

- `main` is a **different music-control project**.
- `general-merge` is the **working compatibility project**. It contains the user's deployed Vortex Compatibility Test profile, successful analog gait integration, Seamless Adaptive HUD and FriendlyHUD. Treat it as read-only compatibility evidence.
- `ui-overhaul` develops a **separately installable UI mod**. Never merge or redeploy unrelated music, movement, combat or quest modifications.

## Workflow

1. Inspect the four local read-only references in `reference/` and current REDkit/vanilla resources.
2. Build a grounded text-surface/resource map and collision map against `general-merge`.
3. Propose and compare 2–3 precise typography/color treatments with real-game examples.
4. Prototype **one small, independently reversible NPC-nameplate treatment** first.
5. Extend incrementally to dialogue/subtitles, notifications, inventory and menus; package optional modules when feasible.
6. Validate visual contrast, clipping, English text coverage and coexistence with current Vortex mods before any live deployment.

Codex development instructions: [AGENTS.md](AGENTS.md). Design brief: [design/brief.md](design/brief.md). Reference locations: [reference/README.md](reference/README.md).

Only original source, reports and build tools belong in Git. Never commit extracted third-party/game assets or compiled mod archives.
