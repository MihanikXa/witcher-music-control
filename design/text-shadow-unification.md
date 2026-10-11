# Text shadow unification — use accepted NPC Shadow v1 as the visual baseline

**User direction, 11 October 2026 (verbatim):**
“I think interaction prompts should be subordinate to the names, so maybe even smaller, and I think we need that NPC Shadow v1 treatment everywhere in text where the stronger shadow was used.”

**Status:** requested design/implementation direction; *not* evidence that any
non-NPC shadows work in game. Accepted `modQuietEditorialNPCShadow` v1 is the
reference appearance and must remain unchanged.

## Design rule

Replace overly strong, wide, hard-edged **ordinary text** shadow/glow
treatments with the restrained optical treatment demonstrated by the
user-accepted NPC nameplate mod. The aim is a coherent visual language:
text feels like it belongs in the world, not thickly outlined/stickered on.

**Exact accepted NPC baseline** in the first target's PlaceObject3
DropShadowFilter:
- RGB `#141718` (charcoal), alpha `166/255`;
- blurX/blurY `2/2`, strength `1`, distance `1`;
- preserve source angle, flags, passes and composite behavior where applicable.

**This is a perceptual target, not a universal binary patch**. Some text is
currently rendered with a `GlowFilter` (including black pseudo-outlines),
some with `DropShadowFilter`, some with inherited/parent filters, some with
dynamic ActionScript/TextFormat/filter overrides, and some have **no** strong
effect. Inspect actual field/parent/runtime contracts. Converting one kind
of filter to another may require different fields/flags and must be validated
with the current compatible authoring/REDkit toolchain. Target gentle,
readable separation, not universal sameness of underlying structures.

Do **not** remove legitimately meaningful non-text effects (focus, disabled
states, warning indicators, quest/rank/rarity colors, selected menu items,
sign icons, hold-progress art, textures or cinematic emphasis). Never apply
the shadow recipe to every GlowFilter blindly. Do not add shadows to text
that has no problematic heavy effect without a separate reason.

For snowy daylight, white sky, foliage, overcast environments, bloom/fire,
dark interiors, bright menu panes and 1080p/projector viewing, compare the
NPC-strength candidate to stronger but still restrained field-local
variants if needed. Do not hide illegibility by darkening text or applying
a global dark background to all UI. Optional local backing is a separate,
deliberate accessibility/comfort decision, not the default.

## Verified starting field inventory

These are **observed direct source placement effects** already mapped in
`research/resource-map.md`; the inventory is incomplete and does **not**
certify the winning modded resource or a dynamic override. Paths are under
`gameplay/gui_new/swf/`.

| Target movie / text role | Original observed treatment | Planned handling |
| --- | --- | --- |
| `hud/hud_enemyfocus.redswf` NPC `tfName` | Former black DropShadow blur4 strength3 | **Accepted v1; no edits/rebuilds** |
| `hud/hud_interactions.redswf` `tfActionName` | Black Glow blur4 strength3 passes1 | Pair subordinate 17px Source Sans with softer NPC-family effect in independent interaction v2; possible 16px trial |
| `hud/hud_subtitles.redswf` `tfSubtitles` | Current opaque black DropShadow blur1.5 strength20 passes3 | Wave A field-local source prepared; preserve runtime `26 + SubtitleScale` and width logic; check poster/Witold routes |
| `hud/hud_dialog.redswf` `tfLine` | Opaque black Glow blur2.5 strength10 passes3 | High priority separate dialogue/movie proof |
| `hud/hud_dialog.redswf` `tfSubtitles`/`tfPreviousSubtitles` | Black shadow blur4 strength20 passes3 | Audit exact text roles and visual function; softer trial with dialogue state/timing intact |
| `hud/hud_quests.redswf` `tfQuestName`, `tfObjective`, `tfOr` | Black shadow blur2 strength20 passes3 | High priority tracked-quest text proof; retain colors/quest-icon/hiding semantics |
| `hud/hud_oneliners.redswf` ambient chatter fields | Black shadows blur2/3 strength10/4 passes2/3 | High priority separate ambient dialogue proof; SAH pool alpha/hide intact |
| `hud/hud_lootfeed.redswf` `tfQuantity` | Black shadow blur3 strength1 | Audit first; not necessarily stronger by visual appearance. `tfName` has no direct placement filter; do not invent a change. |
| `hud/hud_journalupdate.redswf` notification texts | 24 mixed text definitions/filters | Audit field/parent chain by role, patch only genuinely heavy ordinary-text effects. Preserve importance/suppression logic |
| `inventory/panel_inventory.redswf` quantity/slot text | 47 text definitions, mixed effects | Deferred until current Hoods owner is audited; do not replace it with vanilla or discard Hoods functionality |
| `mainmenu/panel_ingamemenu.redswf` text | 180 text definitions; some have no filter; `mcTitle` has **white** glow blur7 strength0.398 | Examine semantics and actual selected movie; do **not** automatically treat a white title glow as black pseudo-outline |
| Journal, bestiary, settings, map, controls, tooltips, quick-slot, radial and other used UI movies | Full inventory not yet complete | Audit actual text effects and selected resource owners, then add bounded patches where excessive text shadows really occur |

See `research/resource-map.md`, `research/collisions.md`,
`design/visual-spec.md`, and accepted
`research/npc-shadow-v1-handoff.md` for concrete source observations,
existing compatibility risks, exact NPC filter and established toolchain.

## Work plan

### 1. One evidence-backed comprehensive audit

Create original tooling that enumerates **all installed, currently selected
English-gameplay UI movies in scope** and identifies text definitions,
Placements, parent-chain filters, resource key, source package/winning mod,
current filter parameters, original/v1 expected appearance and any relevant
dynamic script filter setters. Do not limit the audit to the table above:
look for other strong text treatments in quest rewards, dialogue controls,
status notifications, signs, menu categories, tutorials, location cards,
inventory, map, journal and other actually visible surfaces.

Classify each field, with exact evidence:
- **Strong ordinary-text effect → modify.**
- **Already subtle / none → leave unchanged.**
- **Semantic highlight, active focus, accessibility or non-text filter → leave unchanged.**
- **Owner/renderer unresolved → defer with precise dependency.**

Separate mere filter strength numbers from the actual rendered appearance
(e.g. blur5 and strength1 vs shadow strength20); use code plus sensible
visual stress tests, not thresholds alone. A background or parent filter may
alter appearance. Distinguish verified static style from inferred runtime style.

### 2. Define a shared shadow treatment, with field-level evidence

Use one parameterized, tested, reusable SWF transform for ordinary text
filters, with explicit per-field/per-movie allowlists and source hashes.
Support both softening DropShadow and the GlowFilter pseudo-outline paths,
without rewriting unrelated tags. Preserve movie timeline/ABC, import/export,
texture atlas/source mip, text sizing, colors, alignment, auto-size,
dynamic text and explicit semantics. Source no external reference-mod asset
for the effect; operate only from installed compatible resource versions.

Where no visual-preserving conversion is yet proven, build a small
single-field proof and compare. Do not silently change a different
filter type or produce a resource with broken rendering.

### 3. Incremental build waves, not a single risky universal overwrite

- **Wave A:** Interaction v2 and one independent **subtitle or dialogue**
  shadow module as the first strong-effect proof.
- **Wave B:** dialogue/previous sentence, quest tracker and ambient oneliners,
  then other low-collision ordinary text roles.
- **Wave C:** notifications, specialized text and inventory/menu/journal/map
  after verifying the *selected currently modded* resource owner and any
  supported merge path. Hoods inventory, Alignment Fix glossary, Outfit Wheel
  root/overlay, SAH wolf HUD and other occupied resources cannot be casually
  overwritten.
- Keep separate modules when resource keys differ, or deliberately combine
  changes touching the same key in one tested movie/module. If a multi-resource
  package is sensible **after** per-surface validation, its inventory and
  single-package rollback must remain explicit.
- Audit currently enabled FriendlyHUD/SAH controls so hidden UI stays hidden;
  do not enable prompts/trackers or suppress vital warnings to achieve
  a cleaner look.
- **Font-family changes remain independent**: keep accepted Gentium library
  and accepted NPC color/shadow mods intact. Source Sans is only used
  where chosen and validated; this shadow pass must not silently replace
  every font with Source Sans.

### 4. Verification and release gates for each wave

Do read-only inventory against actual game/REDkit version and active mod
resources, verify hashes, input code/placements, licenses/provenance,
collision owners. Use saved unique-name manual Editor imports only when
required (user performs GUI work). Official cook → validate → pack →
metadatastore → re-extract, verify code/style contract, exact resource
key(s), atlases including transparent pixels, independently reproducible
private ZIP and complete one-mod rollback. No guessed binary headers,
suppressed assertions, unsafe asset merging, arbitrary priority winners,
changes to merged script bundles or Vortex installation by Codex.

**Runtime test:** compare before/after on bright snow/sky, fire, foliage,
dark caves, dialogue and controller/projector distance. Confirm text still
legible, no lost high-importance event, proper quest state, keyboard/
controller hint behavior, names, HUD visibility and genuine eye-comfort
improvement. User acceptance applies only to tested modules, not all
rendering systems.

## Completion definition

Declare the broad shadow job done only after:
1. Every relevant **in-use**, user-visible text surface is catalogued,
   including inheritance/dynamic overrides.
2. Every stronger, nonsemantic ordinary-text effect is either replaced by
   a field-validated restrained effect **or explicitly documented as
   blocked/deferred**, with reason.
3. Runtime and fallback coverage is evaluated per affected module.
4. No accepted feature or accessibility/semantic meaning is lost.

The accepted NPC Shadow v1 is a reference and rollback anchor, not evidence
the same filter automatically works everywhere.

## Current Wave A gate

Current installed Outfit Wheel root ABC corroborates `swf\\hud\\` plus
`hud_subtitles.swf`; the earlier `witcher3` subtitle glow entry was stale for
the current HUD route. Source candidates are prepared and independently
decoded; manual Editor imports are the next dependency. See
[Wave A implementation and manual handoff](../research/text-shadow-wave-a.md).
