# Complete Witcher 3 settings audit and optimization — 21 October 2026

**User request:** Delegate full settings configuration to local Codex because installed mods use distinct storage and routing. The earlier ChatGPT-made 4K ZIP is **partial**, not an authoritative, comprehensive preset. This plan supersedes wholesale application of that ZIP.

## Objective

Audit the **actual, currently active** Witcher 3 DX12 installation, installed
Vortex deployment/profile, base game configurations, enabled mod schemas and
all supported settings storage routes. Produce an evidence-backed,
low-friction, restrained, performant **reviewable offline configuration
package**, not an unverified stack of guessed settings. Account for all
enabled mods with configurable behavior, including mods without visible
dx12user.settings sections.

Hardware/visual priorities given by the user:
RTX 3070 Ti, Ryzen 5 2600X, 32 GB RAM, 4K display/output.
Prefer responsive, coherent, smooth-frame-time gameplay and restrained Witcher
atmosphere over maximum effects, artificial sharpening, gratuitous screen
clutter, and performance-intensive ray tracing. The graphics goal is a
well-balanced **4K output** with appropriate DLSS/internal upscaling and a
realistic performance budget; **do not promise native 4K 60 FPS**. Preserve
display-specific HDR/refresh/VRR choices unless directly evidenced. User's
aesthetic goals include a minimal, context-aware HUD, QuietFolio Gentium
typography, restrained NPC/text shadows, coherent Ink & Iron menu design,
deliberate looting, and Blood and Steel-first combat plus Brawler-only toggle.

### Authoritative source order

1. **Current effective installed environment** (read-only): actual game build,
   active Steam DX12 path, enabled Vortex mod profile, deployed game content,
   winning file owners/load order, Documents configuration, saved mod settings,
   available mod scripts, XML schemas, custom INI/TOML/JSON and current menu
   registration. Record hashes/versions and discover precedence.
2. `general-merge` **implementation records** including
   `brawler-only.md`, `brawler-manifest.json`, `analog-gait.md`,
   `decisions.md`, `handoff.md`, `tools/prepare-settings.py`.
   Historical settings presets are **not** necessarily current or deployed.
3. `ui-overhaul` **read-only** for accepted QuietFolio, NPC colors/shadows,
   SAH/FriendlyHUD visual hierarchy, Ink & Iron 0.8.7 and other active UI work.
   UI branch may contain experimental packages; distinguish built/accepted
   from actually enabled.
4. `main` **read-only** for music controller if its code is installed and
   affects config; do not overwrite audio/music behavior or its mod setup.
5. The user-uploaded originals (if present locally), previous
   `Witcher3_Optimized_4K_Settings_2026-10-21.zip`, and
   `Witcher3_Settings_Coverage_Audit_2026-10-21.md` can serve as **reference
   comparisons only**. They are attachments in a separate ChatGPT environment,
   **not assumed to exist** on the Windows machine. Never use earlier assistant
   output as the sole source of truth.

## Non-negotiable safety

- **No Computer Use or desktop GUI automation.** Code/CLI/read-only file
  inspection only; user performs unavoidable Vortex/game UI actions manually.
- **Do not edit/deploy to** installed game, Vortex staging/hardlinks/profile,
  Documents settings, Windows registry, drivers, saves or live configuration.
  Do not start the game or recompile mods without specific user approval.
  Never run Script Merger, delete stale mods, rebuild working merges, or
  rearrange owner/priority by assumption.
- Back up/source-pin important configuration *for the offline work*, store
  private copies/hashes in ignored local evidence. Outputs go to a
  new ignored directory inside `audit-2026-10-08` (e.g.
  `build/settings-audit-2026-10-21` or `release/settings-review-2026-10-21`).
  Preserve originals and line endings/encoding, comments, key order, duplicate
  section diagnostics and unrelated keys; output **per-file minimal deltas**.
- Commit **original** scanner/validator/patcher source, redacted summaries,
  sanitized schemas/reasoning and tests to `general-merge`; don't commit
  personal paths/usernames, private full settings, third-party assets,
  proprietary source, live profile state, serials or game files.
- If a schema/routing is uncertain, **don't inject settings**; mark
  unverified, report evidence and ask only for a specific missing local input
  or user-operated UI check.
- Never overwrite a live keybinding (F3, F5, F6 Brawler, M1/M2 gamepad
  mappings, keyboard gait/sprint, X whistle, etc.), accessibility settings,
  HDR calibration, difficulty, camera sensitivity or controller response
  without a specific verified reason and explicit review.

## A. Discover all configuration owners and routes

Scan the current effective game and user paths **rather than trusting
filename conventions**:

- Documents/OneDrive-backed Witcher 3 folder(s): `dx12user.settings`,
  `user.settings`, `input.settings`, `profile.settings`,
  `mods.settings`, any `*.ini`, XML, JSON, custom mod text settings and
  separate `user_config_matrix` value caches.
- Installed game's `bin/config/base/*.ini`, input config,
  `bin/config/r4game/user_config_matrix/pc/*.xml`, menu filelists,
  `bin/config` defaults, mod-supplied `bin/` and `Mods/` assets.
- Vortex enabled list, profile metadata, ownership/conflict rules, priority
  winners, locally installed packages (including deployed Core 01,
  replacement Brawler core, package 04 gait, Ink & Iron and compatibility
  configuration), modded DLC pairings, unmanaged files.
  All Vortex data are **read-only**.
- For every configurable mod: parse its actual menu XML groups/Vars/types,
  defaults/ranges/visibility conditions; script config-read calls,
  original INI/TOML/JSON, any mod-specific custom UI/config stores.
  Resolve key name -> section -> storage file -> default -> value -> precedence.
  Some XMLs define menu structure without being the saved-value store.
- Distinguish **native Accessibility AutoLoot** from **Smart AutoLoot mod**.
  Check actual `[AutoLoot]` and `autoloot.ini` if installed. Do **not**
  fabricate `[AutoLoot]` keys from the in-game setting or a newer Nexus
  mod's version.
- Distinguish `[MODS]` duplicated SAHUD values from source `sah*`
  sections: identify actual read/write precedence from installed code
  and menu wiring before changing either. Account for aliases, migration,
  engine regeneration, cloud sync, overrides and first-run values.
- Detect mod features that have **no user-tunable keys** and report those
  explicitly rather than omitting them or inventing an option.
- Read mod authors' documentation or official release notes when installed
  source and menu XML are inadequate. Verify version and separate newer
  documentation from the installed implementation.

### Required output: complete matrix

For each enabled mod, one row with:
mod identity/version, active/winning owner, any configurable feature,
all locations searched, verified file+section+keys, type/range/default,
current value(s), effective precedence, proposed new value (or keep),
reason tied to user intent, confidence/evidence, conflict/dependency,
verification/test, and status (implemented in offline draft /
kept / blocked / no configurable settings).

Provide a machine-readable JSON/CSV manifest and readable concise
Markdown. Cover **every enabled mod** and every in-use settings section,
not only the previously edited DX12 file. Detect existing duplicated and
stale keys, with a warning rather than a speculative cleanup.

## B. Optimization decisions (preserve game design direction)

1. **Smart AutoLoot:** major priority. Aim for passive low-friction herbs/
   ingredients where safe, deliberate efficient containers/corpses,
   avoid accidental theft/quest/diagram consumption, keep notifications
   restrained and useful. Verify author semantics of radius/modes,
   stealing, ownership, diagrams, filters, safeguards and script timers
   in the **installed exact build**. AutoLoot's duplicate scheduler fix
   in Core must remain intact. Avoid making all valuables vacuum up
   without player intent.
2. **Seamless Adaptive HUD / FriendlyHUD / Ink & Iron / optional prompts:**
   preserve intentionally hidden elements and context-aware reveal,
   previously accepted typography/colors/shadow and UI layouts;
   eliminate redundant minimap/markers, unnecessary alerts and
   conflicting visibility controls only where supported. Verify
   current [MODS] mirrors and precedence. Never enable UI simply
   for an experimental font module; keep accessible essential actions.
3. **Blood and Steel / Brawler-only / Arrow Parry:** verify whether the
   B&S-first Brawler-only Core is **actually enabled**, not just built.
   Recommend B&S custom attacks/dodges on, Less Spins
   (`BaS_Aggressiveness=1`) and competing B&S close camera off **only
   if compatible with the current setup**. Preserve custom damage/targeting,
   native and optional parry handling; no leftover Bestg school/CSM
   changes if obsolete. Add F6 only when Brawler Core is actually active
   and F6 free; otherwise report as pending, not force active.
4. **Movement:** preserve accepted package-04 analog walk/jog and held
   sprint plus movement tweaks and horse/boat behavior. Avoid RM speed
   stacking and unnecessary transitions; don't change controller
   mapping or native action wrappers from config without evidence.
5. **Graphics:** inspect current actual DX12 settings *and current GPU/CPU
   profile*, up-to-date Witcher 3 Complete Edition benchmarks and
   engine semantics for each key. Provide a defensible 4K-output,
   latency-conscious baseline: RT/path-tracing disabled unless specifically
   requested, sensible DLSS mode, careful 8GB-ish VRAM budgeting,
   shadows/foliage/crowds/LOD, screen-space reflections, hair,
   textures, sharpen/postprocessing, VSync/VRR/reflex/limiter
   coordination. Report DX12 engine limitations and settings whose
   values can only be selected/read in menu. Do not equate
   `Viewport` resolution with actual Windows desktop or display mode
   blindly. Offer a **secondary** higher-quality variant only if
   technically grounded. Never suggest guaranteed 4K60 on RTX3070Ti/
   Ryzen2600X without measurement.
6. **Other current mods** including Vaxis Blood Physics,
   Enemies of Rivia NG, Enhanced Camera/Living Camera, combat/difficulty,
   FX and animation mods, UI menus, game tuning, Gwent, save mods,
   sound/music: examine actual semantics and preserve deliberate choices.
   Prioritize reduction of repetitive friction and visual clutter;
   don't arbitrarily nerf difficulty or reduce intended consequences.

## C. Produce a minimal, verified review package

- Use the accepted `tools/prepare-settings.py` as a starting point, but
  **do not blindly trust its transform**: test duplicate-section behavior,
  case sensitivity, BOM, CRLF, repeated keys, comments, missing-section
  append, XML/INI type handling, and keybinding collision behavior.
  Extend/refactor with safe parser-backed validators only if needed.
- Only write setting values verified against installed schema and
  semantically justified; never copy a complete historical `dx12user.settings`
  or `input.settings` over current originals.
- For each routing target, generate source-hash-pinned offline
  `*.proposed` copy where practical, targeted unified diff/patch,
  JSON delta, and rationale/rollback. Distinguish game-created writable
  config from packaged **mod default XML**, and do not suggest changing
  a default XML when the effective user override lives elsewhere.
- Provide a single reviewed consolidated package (ZIP) with
  `README-APPLY.md`, `COVERAGE.md`, `CHANGES.md`,
  `UNCERTAIN-KEYS.md`, `ROLLBACK.md`, `manifest.json`,
  per-target offline diffs and, **only when safe**, optional
  drop-in proposed copies. Do **not** place actual files in the
  live game directory. Mark file target paths by role, not embedded
  username. Recheck source hashes immediately before application.
- For values not configurable through files, provide
  **specific user-operated in-game menu steps**, and manual verification
  tests. Avoid a broad list of speculative toggle names.
- Tests: independent round-trip parsers, exact preservation of all
  unselected settings, verified keys/ranges/types, expected owner
  and route, no cross-file conflicting changes, no duplicate/inert
  mod options, no keybinding conflicts, source integrity, independent
  repeatable package output, diff replay and rollback.
- Do not conceal uncertain choices by deleting or resetting them.
  Classify changes: `verified and recommended`, `user-choice dependent`,
  `requires live test`, `unverified/blocked`.
- Report what **was actually optimized** vs only audited,
  with a count of enabled mods and files/keys examined, exact
  changes, outstanding gaps and risks.

## Prior work limitations to correct

The 21 October prior summary covered 71 DX12 sections and 587 values,
but only 31 were changed; that work did not inspect the actual separate
Smart AutoLoot configuration. Its earlier generated archive should be
considered a **reference draft**, not the current machine's canonical
settings. Some historical `general-merge` docs still describe the
previous Bestg/CSM setup, whereas `brawler-only.md` describes a
later, separate (possibly not yet deployed) replacement. Inspect actual
profile and effective current data instead of copying one historical
release proposal.

## Codex execution / stopping rule

Proceed through exhaustive read-only discovery, local schema tracing,
recommendation selection, offline minimal-delta implementation and
test/validation **within the same task**. Don't stop after merely
listing file locations or asking for the 3 missing files: inspect local
installation yourself. Only stop for a specific inaccessible resource,
user-required GUI confirmation, or unsafe ambiguity; explain exactly
which values remain unverified and still deliver all safe audited work.

Return one ready-to-review private package path and hashes, source/proposed
diff summary, current/pending mod-version mismatches, a prioritized list
of genuinely useful changes, and concise manual user next steps.
**No live deployment**, saves/GUI changes, or background execution.
