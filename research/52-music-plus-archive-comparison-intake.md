# 52 — Music Plus architecture comparison: intake, not a binary audit — 2026-10-15

## User objective

User requests acquisition and a substantive comparison of Music Plus (Nexus mod 13818) against: (1) their original 0/0/100 generic exploration/dialogue/combat policy; (2) WMC v4's complete eight-region policy / five patched soundbanks; (3) the broader Breath of the Wild / Ghost of Tsushima-inspired vision for spacious, purposeful, sparse/adaptive musical entrances and exits. Evaluate Music Plus strengths, regressions, reusable *ideas* and feasibility of combining behaviors. Do not assume its popularity, track volume, or claimed quest exclusion establishes actual mechanism.

## Public source and version

- Official https://www.nexusmods.com/witcher3/mods/13818 — updated 2026-10-15, **Music Plus 3.3.0**.
- As of 3.3 the author distributes a **main archive** (scripts/settings/tools/playlist editor/playlist data) plus a separate **Music Pack** (music, circa 900 MB). Both are required to run the mod; main archive is the first priority for script/timing and playlist analysis.
- Published claims: 271 new tracks from other Witcher-related sources, 131 playlists; randomized whole-track selection; adjustable probability of a silent pause between tracks (never / 25 / 50 / 75 / 100%) and silence range 10s–1m, 30s–3m, 1–5m or 2–10m; silence starts only at track boundary. The 3.3 update changes location/day-night carryover, short silence-loop handling and user-selectable instant location switches.
- Published combat differences: removal of vanilla 8–20s bridge/intro fragments, randomized combat pieces, roughly 5s combat-piece crossfades, removal of original exploration/combat transition clips and four-second postcombat hold followed by fade. Quest/cutscene music is claimed untouched. Public page also lists separate sliders, keys, playlist weights, source toggles, alternates and local playlist editor.
- Nexus page labels archive downloads behind **login** in the available public interface; no authenticated transfer was performed, no Music Plus archive was retrieved, no binary/Script audit performed. Do NOT claim observed HIRC or file content from the published description.

## Required archive-level audit after authorized local download

1. Inspect main and Music Pack read-only in ignored `reference/music-plus/` or an isolated ignored work directory. Hash archives and list exact contents, sizes and game-version constraints. Never install them over the game, enable via Vortex, execute included bat/PS/editor/servers, change settings, or access account credentials.
2. Audit annotated WitcherScript hooks, changed game events/States/switches, menu settings, keybinding installer side effects, `soundspc.cache`/individual soundbanks, optional Init and extra media. Separate static Wwise modifications from runtime commands and timers; determine precisely how 3.3 schedules tracks, pauses, area/day-night changes, combat returns, and how pause/mode choices persist.
3. Decode native/MP/WMC banks with the existing HIRC/cache readers where supported; extend decoders only with evidence and independent tests. Compare specific native combat intros/outros and long-tail assets, selector/transition changes, Wwise authored branch and authored-world exceptions, Music master, Gwent/minigame/diegetic routes. Do not make an event-closure claim from filenames or author prose.
4. Determine whether random tracks+silence are actually context-triggered short musical punctuation or merely whole-piece rotation with adjustable idle gaps. Compare timing resets, place switching and scene-event priority against report08's richer vision; do not assume these games' actual playback rules without supporting research.
5. Deliver a bounded side-by-side matrix: desirable mechanisms to independently recreate, MP behavior that conflicts with native soundtrack preservation, WMC advantages, unresolved questions, and clear build/buy/hybrid recommendation. Respect Nexus redistribution and modification restrictions: use no third-party files or code/assets in WMC without appropriate permission.

## Interim architectural judgement (page-based only)

MP demonstrates a concrete sparse cadence interface and mature controls that WMC v4 lacks; however its pause selection is stochastic at whole-track boundaries, not demonstrated narrative/context-triggered punctuation. WMC uniquely leaves native combat composition, intro/transition/outro objects unchanged in modified regions, and has verified partial protection of authored-world routing. MP claims quest/cutscene protection but world-origin authored exception coverage is unknown until content inspection. Neither publicly demonstrates an independent discovery-triggered music system of the kind proposed in report08. Avoid recommending dropping WMC or harvesting MP functionality until archive evidence.

## Acquisition boundary

Have the user manually download 3.3 **main archive** and **Music Pack** using their own Nexus session; do not install. For a ChatGPT-file audit, the main archive can be attached; for local Codex, supply actual archive paths. A second download of the Music Pack may be unnecessary for initial scripts/mapping but required for complete embedded-media/bank comparison. Keep third-party source and binaries out of Git.
