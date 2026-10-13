# NML scoped implementation — 2026-10-13

Observed: the first manifest-driven NML pilot is authored and source-validated in complete isolated context. Six native-playlist authoring captures completed. No NML bank/package exists: the fresh untouched baseline requires manual project-local licensing. This is a deliberately partial pilot, not full Velen/Novigrad coverage.

## Reviewed scope and conservative decisions

`src/wwise/regions/nomansgrad-pilot.json` pins `music_nomansgrad` root GUID `{B6298CA1-0F86-4AC5-87ED-3D3475BA3DA4}`, ShortID 976763369; world GUID `{FA8A1A46-55DA-4193-B1D2-29F757624C1E}`, ShortID 492774600. State scopes are native `nml_zone_02` (193134718) and `nml_zone_03` (432285193). Four static targets are their day/night exploration playlists: 719937819, 132074504, 946096996, 568231384. Existing combat and Gwent consumers are separate; reviewed targets have no direct event or unreviewed consumer. Intent is a bounded inference from ordinary location/State routing, not playlist naming or quest-number automation.

58 noncombat decision entries: four approved generic, eleven source-verified silent, three conservatively protected narrative candidates, four mixed and 36 unresolved. Nine muted States include focus/underwater/boat as well as ordinary exploration/dialogue; that broader scope exposes mixed consumers omitted by a four-State-only inventory. Burned-village q101, embassy/emperor-associated and lovers' exploration remain native as probable authored candidates. Ghost forest and `dialog_ambient_03` have mixed consumers and are not static targets. Other same-named `expl` objects remain individually identified by GUID/ancestry, not collapsed by name. Roche/camp and other uncertain narrative locations stay unresolved/native. No asset-name heuristic grants or denies protection. Silent selections remain native; their classification comes from source silence evidence in report07.

## Source evidence and commands

Original authoring source is the installed REDkit `assets\w3_audio`; copied context retains all 1,508 work units. Each NML project has 434 copied regional source files, 6,925,188,010 bytes, without hierarchy pruning.

Isolated paths under `C:\Dev\witcher-music-control\build\regional-system\nomansgrad`:

- `baseline\w3_audio.wproj`: untouched complete source project.
- `candidate\w3_audio.wproj`: shared author applied two State scopes and four static properties.
- `candidate\regional-authored-music.xml`: clean source snapshot, no licence/project data.
- `source-gate-retry.json`: passed, unchanged global definitions/nonmusic units/audio and all undeclared music semantics; 40 pending decisions, `shipping_policy_complete: false`.

Candidate music source SHA-256 `9a4d2c408dc3e007819b8e5733ef8b64a2bbd6889ed805aa98fa14aa50d490a7`; manifest SHA-256 `27b55ab0534e1e207c37b11c0c951b3ad1cd3a86f0669dc0b554552052da0bc1`.

Author with `tools/regional_music.py --source <original> --project <isolated-wproj> --manifest src/wwise/regions/nomansgrad-pilot.json --template <retained-D-music.wwu> --port <own-WAAPI-port>`. Prepare through shared `white_orchard_prepare.prepare(..., preserve_hierarchies=True, regional_root='music_nomansgrad')`. Source gate CLI requires the same source, manifest/template and candidate directory; output must be fresh. Do not use a validation fixture for generation.

## Playback evidence

Separate `fixture\validation` starts from original full context plus only the clean candidate music source. `zone02-playback` failed with an HTTP timeout at `ak.wwise.core.getInfo` before capture; no result is claimed. A subsequent bounded connection succeeded, and fresh `zone02-playback-retry` completed native-reference versus manifest: exploration→combat→exploration, cutscene→dialogue after 400 ms, and threat changes. Six captures and measured envelopes are retained there. Timeout cause is unproven.

At 6.5–13 seconds, zone02 exploration intensity-1 voice peaked at −19.23 dB native versus −220.55 dB modified during combat entry; cutscene→dialogue native −19.04 versus modified −233.05. Combat intro intensity-1 remained −13 dB; intensity-2 responded to threat at −15 dB in both threat tests. Native-reference initially also continued cave voices from native selection history; these are outside the pilot and remain native. Pathless profiler entries are excluded. Thus evidence supports suppression on the reviewed zone02 path and retained combat response, not all-region silence or exact phase equivalence. Zone03 source structure passes but has no playback capture yet. No NML authored cue or runtime test is claimed.

## Exact generation blocker

Selected untouched-baseline command used Wwise 2023.1.19.8928 `generate-soundbank`, bank `music_nomansgrad`, Windows/SFX, fresh `baseline-banks`, complete context and no exclusions. `tools/white_orchard_wwise.py` records command/result/log. Exit **1**, **zero banks**, six Mastering Suite licence errors, one fatal media-limit error (**26,218/200**), ten warnings (including media streaming consistency and Wwise.dat). All diagnostics retained; no failed bank is accepted. This means licensing is ineffective for this fresh project, not that the previously licensed D entitlement failed. No licence was accessed/copied; no candidate generation or packaging followed.

Smallest next action: user opens `C:\Dev\witcher-music-control\build\regional-system\nomansgrad\baseline\w3_audio.wproj` and applies the existing approved entitlement through **Project → License Manager**. Do not send the key to Codex. Then run only a fresh selected baseline output. Before candidate approval, implement/measure the new regional State serialization decoder, repeat controlled threat-zero comparison and zone03 playback, and retain the 40 unresolved/mixed decisions as native. Full coverage requires narrow reviewed additions, not automatic bulk attenuation. Native Init, working D, game/Vortex/saves remain untouched.
