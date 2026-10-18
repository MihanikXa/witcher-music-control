# 91 — Sparse contextual eligibility and probabilistic entrance: source audit and bounded policy prototype

2026-10-18. User explicitly agreed to the entire contextual/probabilistic approach discussed after report90: **"Agree with you on everything. Let's hand off to codex now."** This replaces the previous focus on exact preservation of timed silence across every location return. **The chief problem is now how/why/which musical passage plays.** Music must have a *contextual reason to be eligible*, but need not have a special event to justify *every entrance*. Build evidence first, then a small falsifiable offline prototype. The user has not approved numerical probabilities, cadence defaults, global context rules, all24 cue placements, or retail deployment.

## 1. Accepted product direction — not a universal timer

The target is a restrained soundtrack with environmental sound as a real layer, inspired by the *design philosophy* of Breath of the Wild and Ghost of Tsushima, without falsely attributing a specific soundtrack algorithm to those games.

The three mechanisms are:

1. **Meaningful contextual opportunity:** a verified change or event (if actually exposed) may temporarily raise the *chance* of a suitable excerpt. It is an opportunity that may expire without a cue, **not** a compulsory stinger on every arrival/discovery.
2. **Low baseline exploratory opportunity:** ordinary stable exploration can occasionally become musical after some quiet time, with bounded randomness and non-repetitive cue choice; neither fixed gaps nor unqualified random soundtrack spam.
3. **Native authored/quest/combat music:** existing game retains absolute priority and its own native intensity, fades, silence and outro. No Sparse choice changes its intent or gain.

**Separate these functions clearly:**
- **Eligibility / hard gates:** may Sparse music play *at all*? Existing authored music, combat, ordinary dialogue when muted, inappropriate game states and other demonstrated ownership states have priority. Require positive evidence that generic exploration is active. A "world" label alone does not prove safe authored-vs-generic classification.
- **Contextual palette:** among the24 approved private cues, which are *plausible here* (region, environmental/time atmosphere, activity, use-case, intensity, duration)? This is a provisional editorial/policy decision, not derived automatically from source filenames or rough audio metrics. 24 selected excerpts include closely related sections of the **same underlying composition**, so avoid-repeat must understand family and not only exact WAV.
- **Opportunity / activation:** a bounded stochastic process can raise/lower entrance chance using time since last music and verified event windows, with a real possibility of no music for a long time. No audio fired simply because a clock elapsed, nor obligatory "vista track."
- **Selection and commitment:** pick one *eligible* passage using suitable weights, anti-repeat, prior composition family, and an evidence-backed event/context match. Allow once-only phrase with approved tail/exit marker; return to ambience. Preserve a native override at any point.
- **Recovery/re-entry:** after native combat and full outro, re-enable opportunities conservatively. Report90's **B rest-first** provides *a provisional Wwise-only foundation*, not a decided30s actual default and not an exact persistent deadline. Redundant same-State/location events already preserve rest. Treat fixed-rest cross-location persistence as secondary; avoid event spam/area-thrashing bias instead of spending another run solving a perfect countdown.

The agreed guiding principle is: **"music should have a contextual reason to be eligible, but it doesn't always need a specific event to justify starting."**

## 2. Source-grounded signal-feasibility audit (do this first)

Read reports08,27–29,50–58,85–90, relevant src/wwise manifests, \`tools/white_orchard_sparse*\`, \`tools/sparse_approved*\`, \`tools/sparse_reentry*\`, existing analyzed Music Plus **metadata** in report53, native Wwise WWUs, and available **original local REDkit and game WitcherScript source**. No need to inspect user profile repos for this engineering task. Work read-only on installed/REDkit sources; this audit should not execute untrusted third-party mod programs.

Investigate a deliberately **broad but bounded signal shortlist**:

| Signal family | Priority questions |
|---|---|
| Regional location, world vs quest branch, combat, \`game_state\`, day/night | Which are confirmed Wwise State/Switch/Event inputs? At what granularity? Which are normal state assignments vs specific event occurrences? Can the signal be read or observed by a game-side controller without weakening native routing? |
| Area arrival / discovery / location markers | Does an actual script callback/event fire for a discovery, point of interest, marked landmark or unique arrival? Is it repeatable, save-dependent or tied to map UI rather than gameplay? No assumed "vista detector." |
| Weather, daylight, time-of-day | Is actual current weather/time readable in suitable script contexts? Does Wwise receive it directly? Update cost/stability and ability to tell ambience from score. |
| Exploration activity, travel mode, horse/boat/underwater, player locomotion | Verified native hooks/properties versus inferred animation state; distinguish activity from narrative importance. |
| Calm/hostility and recent combat | Which actual transitions expose the beginning and end of combat, native outro state and safe resumption? Never use game_state=exploration alone as proof the authored outro already ended. |
| Elevation/vista/biome, world-transition and quest relevance | Only count if **specific** accessible, discriminating signals exist; otherwise mark unavailable/weak/high-cost. Avoid brittle distance polling, world geometry heuristics and false "looks beautiful" proxies. |
| Existing authored and cinematic music ownership | Which native \`music_type\`, events, branches can reliably veto Sparse? State-only heuristics are insufficient, because authored music can play during exploration/dialogue. |

For EACH candidate signal, write an auditable catalog with:
- **exact native source path + symbols/call site + relevant lines or structured Wwise object/event IDs**;
- source type \`native_game_script / native_Wwise / REDkit / reference_mod / hypothesis\`;
- availability: \`verified signal / verified implementation path but unproven delivery / plausible API / absent in inspected sources / not investigated\`;
- precise semantics (edge-triggered event, persistent state, pollable property, derived, location switch, script lifecycle);
- expected update cadence, duplicates/noise, saved/load/travel transitions, quest spoilage risk, false positives;
- integration path: **already reaches Wwise**, accessible to supported WitcherScript, requires localized hook, or unsupported;
- usefulness for **eligibility, palette, probability boost, or hard veto**, separately (one signal can serve more than one);
- proof quality and minimum test required before runtime use.

**Do not promote a source symbol's name to runtime truth.** Prove actual call chains or native event emission if possible. A value the Wwise authoring transport can set manually is not necessarily exposed to WitcherScript at retail runtime; WAAPI getters aren't game APIs. Native WWU fields indicate authoring choices, not necessarily game notifications. Don't invent a generic 'discovery' or 'weather' callback.

Deliver a ranked **feasibility table**: (A) usable with directly demonstrated game/Wwise paths, (B) plausible and needs targeted live validation, (C) missing/fragile or unsafe. Include a "minimum viable input set" even if only region/location/daynight/game-state and explicit native music ownership qualify. Cite files/locations in the report and record unknowns, not broad imagined game design.

## 3. Bounded off-game contextual selection model — only after audit

Implement a small **original, testable deterministic-seed decision engine** and a compact trace/simulator/reviewer, not an in-game/Wwise controller. Pure Python is fine; reuse current repo tests/JSON tooling rather than a large new framework. Give it a *typed chronological event trace* containing **only verified or explicitly simulation-labeled inputs**, an approved cue metadata subset, seeded RNG, and a sequence of state/decision records with reason codes.

Mechanism requirements:

- **Hard priority:** exact native authored/quest/combat ownership inhibits/cancels opportunities; play-state and native outro priority remain. If exact ownership isn't observable from the chosen input, fail closed rather than claim protected routing.
- **Eligibility:** stable generic exploration (with conservative quality gating), correct context palette; normal environment has long periods eligible-but-not-activated.
- **Opportunity process:** low **baseline time-varying entrance hazard** during continuous eligible exploration; optional bounded *event opportunity windows* for confirmed signals; probabilities normalized by elapsed time (so callback/poll rate does not change musical frequency), no forcing one at a timeout. Expiring unconsumed windows are first-class valid outcomes. Avoid permanent music starvation from noisy repeated area events.
- **Meaningful use of triggers:** event windows modify *when a suitable cue can start*, and separately event/context weights modify *what can play*. A trigger is **not a guaranteed cue**.
- **Anti-repeat:** avoid recently played excerpt IDs **and source-family** (S04-a and S04-b etc.); avoid overusing one musical family or harmonic/mood family when tags are actually substantiated. If no plausible cue available, remain silent rather than forcibly pick a bad match. Maintain bounded history without hard universal quotas.
- **Musical integrity:** selected full passage plays once with its exact approved start/fade/tail from report85, except native interruptions. No cutting up the accepted files to meet an arbitrary opportunity window. If trigger expires while another cue plays, don't queue a backlog of stingers.
- **Post-combat:** explicit cooldown/quiet recovery can be represented as a *state gate* anchored to verified native outro completion **when that information is available**; otherwise model uncertainty and fail closed. Do not silently infer actual native outro completion from a 30s Wwise rest.
- **Events/context changes:** repeated identical events are idempotent; real region entry changes palette; context instability dampens/debounces eligibility; semantic handling of discovery repetition and post-load state must be explicit. B rest-first semantics can be used as an illustrative native playback layer but its 30s is not promoted to preference.
- **Seeded variability and robustness:** deterministic replay from input seed+trace; Monte Carlo/sweep comparisons for unintentional long silence, music oversaturation, event spam, exact clip/underlying-family repeats, cue weighting, interrupted events and start-sample fairness. Negative tests for unavailable native-authored ownership, missed combat exit, duplicate signals, rapid A→B→A, repeated POI, pause/loading, save/load (if represented), and state callback timing.
- **Aesthetic numbers are hypotheses:** choose no more than2–3 *clearly marked illustrative policy profiles* solely to visualize the range of consequences; do not choose real probability values as approved defaults. Prefer probability/hazard visualizations in an offline **trace review** (time line: context, eligibility, opportunity window, candidate choice, reason/no-play and native override), plus text/CSV/JSON summary; no need for a user-facing full editor or dashboard.

Use **at most 3 carefully chosen accepted cues** to demonstrate distinct roles/lengths, if their distinctions can be supported by actual user feedback in report58/report85 and source boundaries. The full24 is a **metadata audit catalog only**, not a newly assigned or rendered playlist. Source family must be grounded in report61's source IDs and report85's approved render manifest. S14 tracks remain accepted as *private edits*, but existing authored use and redistribution caveats remain, and don't use them in a general exploration demonstration without contextual justification. S04-a's White Orchard proof was intentionally geographically artificial; do not use that as a region-fit rule. No new audio processing/import required; a visual/synthetic timeline is sufficient for policy proof.

## 4. Evidence and decision gate

Produce:
1. **Context signal audit:** ranked verified/plausible/missing signals with exact game/Wwise citations, reliability and actual access paths; important no-go claims explained.
2. **Cue-role catalog:** all24 accepted cue IDs, exact SHA-linked local file, shared composition family and the user's actual note/role when present; distinguish user-endorsed tonal interpretation from hypotheses. No arbitrary or final regional assignments. Verify all24 file hashes if local files exist; note exact missing paths if not.
3. **Small offline prototype:** reproducible seeded policy trace/engine and hard-negative tests; enough scenarios to show stable traversal, contextual opportunity, triggered-but-expired opportunity, combat/native outro veto, region movement, repeated events, and adjacent cue-family anti-repeat. Explicitly label hypothetical input traces.
4. **Architecture tradeoff:** Wwise-only (location/state palette, native rest, weighted random) vs localized script/event + Wwise playback for richer moment signals, with overhead/compatibility/deployment risks. Determine whether meaningful verified signals demand script; **do not implement script or start a new full Wwise bank**.
5. **Proposed minimal pilot for user review:** 1–3 **grounded** triggers and1–3 distinct cues for one region, with reasons and a suggested order of future in-game validation. If meaningful external triggers are unverified, recommend conservative region/time-based probabilistic opportunities first and propose what targeted runtime probe would unlock stronger event-driven scoring.

Record all **time/probability profiles as experimental**, not decisions by the user. State what's observed, source-inferred, simulated, and untested. Prefer an honest smaller working model over a broad unsupported "smart soundtrack" design.

## 5. Scope, safety, and stop

- New ignored root: \`build/sparse-context-audit-v1/\` for trace and optional local source indexes. New sanitized research result \`research/92-sparse-context-signal-results.md\` (or next free number), machine-readable source signal catalog and model/traces/tests. Commit only original code/sanitized evidence.
- No changes to accepted24 WAVs, source material or WEMs; report85 SHA pins; report88 generated bank; report90 re-entry projects; native Init, v2/v3/v4 bank/cache ZIPs; game install, Vortex, saves, REDkit native source or licences.
- No unverified authored event mutations, no commercial audio redistribution, no untrusted MP execution, no gameplay spoiler walkthroughs, no synthetic webcam/visual scene recognition.
- **Do not** modify retail WitcherScript, scripts under the active game, Wwise project banks, or implement all24 cue-selection production logic. No new Wwise transport/paid licence work is required unless needed for a *narrow read-only clarification*. No full engine/menu, notification or release.
- Run relevant repository tests, add sharply targeted model and signal-parser negative tests, independently sanity-check scenario outcomes, and report limitations candidly.
- **Stop** with an evidence-backed recommendation for the smallest next **real integration pilot**, presenting contextual opportunities vs a pure random fixed-gap baseline, and wait for user authorization.

**Success is not "music starts every N seconds." Success is knowing which real game signals are available, how to map them to bounded opportunities and eligible cues, and having an offline replayable model that explicitly represents when nothing should play.**