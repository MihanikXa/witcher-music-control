# 38 — Spoiler-free offline continuation — 2026-10-14

## Explicit user feedback

> I must assume that it works since I am not yet at those zones, and don't want any spoilers by installing some custom saves. White Orchard worked when we did it, I trust it for now, I'll report it something is off when I play the game, let's continue with the mod further for now.

**User decision:** Continue development without imported/custom saves, forced quest states, teleportation, previewing later game content or requiring travel to as-yet-unreached regions. User will report faults as encountered organically. User-visible progress reports must avoid narrative spoilers; refer to technical region or object identifiers. Local source/event inspection and isolated Wwise playback are permitted.

**Evidence boundary:** White Orchard D was user-tested in retail; NML's report37 pilot passes all listed offline source/binary/cook/readback and Wwise authoring gates, but **no retail-game test was performed**. User chooses to proceed despite that risk; this is not new runtime confirmation, not authorization to deploy or alter Vortex, and not evidence that every story cue is preserved.

## Next development priorities

1. Native multi-bank cache/coexistence proof. Working White Orchard D and NML pilot ship separately under their own mod directories with soundspc.cache. This does not establish that the game safely merges multiple caches. Use the established isolated native REDkit cooker with exactly the previously verified prologue and nomansgrad regional banks. Inspect real two-bank cook/split/readback, entries/payload SHA-256/diagnostics, native Init invariance and exact ZIP contents. Preserve original pilot ZIPs; do not manually splice unsupported opaque cache formats. Do not deploy.

2. Broaden main-game NML coverage substantially. Existing four generic day/night playlist edits cover only two zones; 40 targets are mixed or unresolved and currently remain native. Reuse exact GUIDs, physical gain ancestry, complete selector/event/transition consumers, silent evidence, authored routing and Wwise probes. Approve generic-only suppression only where justified; protect authored/world-cue candidates and combat intro/outro, Gwent and mixed-use material. Keep ambiguous decisions native with explicit review status. Batch mechanical inventory/verification instead of repeatedly creating four-playlist prototypes.

3. Scale to remaining regional banks using the shared data-driven manifests and independent source/decoded HIRC/media/stream/RTPC/outro gates. Optimize verified offline generation and packaging across regions, handling per-project licensed Wwise prerequisites via the user when necessary. Never ship generated Init, modify source installs or redo the giant depot.

4. Preserve spoiler-free reporting and honest status: offline acceptance is not retail compatibility; user will give feedback during natural play. No custom saves, forced routing, test quest progression, or unsanctioned live deployment. Keep current D/Vortex setup unchanged.

## Next Codex task

Prefer one bounded proof of native two-bank packaging first, then a substantive source-reviewed NML coverage expansion with a region manifest and offline tests. If the native cooker cannot encode multiple regional entries, document the exact blocker and alternative loader-compatible paths without claiming success. Do not stall all engineering on user gameplay validation.
