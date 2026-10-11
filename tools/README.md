# Tools

Project-local helper scripts belong here.

Do not vendor REDkit, Wwise, Script Merger, game binaries, or other third-party executables into this repository.

## Isolated White Orchard pilot

These Python helpers use the standard library and the already installed matching
WwiseConsole. They never install or deploy anything. See
`research/10-white-orchard-prototype-results.md` for commands, measured results
and the current Init/cache blockers.

- `white_orchard_prepare.py`: copy 47 referenced originals, sanitize output
  paths/commands and hash inputs. Use `--preserve-hierarchies` for Init fidelity;
  the legacy pruned mode is retained only to reproduce the failed baseline.
- `white_orchard_author.py`: verify the open isolated project and Wwise build;
  author the mixer described by `src/wwise/white-orchard-mixer.json` through WAAPI.
- `white_orchard_wwise.py`: local HTTP WAAPI client and selective Windows/SFX
  generation. It rejects the instrumented `validation` project and treats the
  present generation error as failure even when bank files exist.
- `white_orchard_compare.py`: compare bank chunks/HIRC by ID; require the regional
  change to be confined to `world_music`, with unchanged embedded media.
- `white_orchard_probe.py` / `white_orchard_measure.py`: validation-only synthetic
  5.1 recordings and measured gain assertions. The probe contains test audio and
  recorders; its project must never supply shipping banks.
- `white_orchard_contexts.py`: authoring simulations of village music, combat,
  authored q001 selectors, protected routing and the native Music parameter.
- `white_orchard_transitions.py`: sustained-tone bypass-switch recordings;
  preserves/restores the probe matrix's final raw recording after other tests.
- `white_orchard_native_fade.py` / `white_orchard_fade_measure.py`: validation-only
  parallel AuxBus/State-volume experiment and six-channel continuous-tone checks.
  Never generate banks from its instrumented workspace. Clear stale State groups
  on the aggregate; the root Sound fixture also needs explicit send clearing for
  protected-path tests (`white_orchard_contexts.py --native-fade`).
- `white_orchard_cooker.py`: prepare an ignored isolated cooker bootstrap and
  reproduce native Init/music_prologue cache fixtures without calling Wwise or
  copying executable tools. It deliberately does not accept the incomplete mixer
  Init or create a deployment candidate. See report 11 for successful commands,
  bootstrap-only CSV changes, nonfatal diagnostics and loader-proof limits.
- `white_orchard_init_audit.py`: research-only complete-project media controls.
  Default mode uses localhost WAAPI to remove only unselected banks' media
  filters; `--exclude-file-leaves` adds supported Inclusion=False to file-backed
  Sound/MusicTrack leaves outside music_prologue. Neither grants a licence or
  certifies Init. Both rejected generation controls are documented in report12;
  preserve native global definitions and never deploy their incomplete output.
- `white_orchard_state_volume.py`: authoring-only direct world Voice Volume
  State proof; no bank/Init generation. The first run preserves the pure local
  StateInfo edit before adding fixtures. `--capture-name <fresh-name> --anchor`
  repeats continuous recordings with a silent capture fixture outside world.
  Later captures reuse instrumented source and must never supply shipping banks.
  See report13 for measurements and the unresolved bank-construction boundary.

Keep the WAAPI server bound to localhost, verify its project path, and stop it
when finished. Recorders and synthetic source objects stay in the separate
ignored validation workspace. The settings UI, script adapter, live-game tests
and deployment are later work. A rebuild allocates fresh local effect/state
GUIDs; the recipe reproduces the routing and behaviour, not a byte-identical
bank. Preserve the generated workspace/manifest when comparing exact builds.

## Active production-source experiment

- `white_orchard_build_gate.py baseline|candidate`: strict read-only future licensed-build acceptance, reusing bank/State comparators. Baseline must preserve native headers/global HIRC/registrations/full STMG/media; candidate requires an unchanged passing baseline proof and only the verified world State edit. Errors, unexplained warnings, stale evidence and ProjectID mismatches fail with JSON and exit1. No generation, licensing or deployment. Commands and limits: report17.
- `test_white_orchard_build_gate.py`: synthetic gate/decoder regression tests under ignored build; run with `python -m unittest discover -s tools -p test_white_orchard_build_gate.py -v`.

- `white_orchard_state_volume_author.py`: clean, author-only Stage 1 helper, exercised on complete isolated Wwise 2023.1.19 copies (report 15). Verifies the existing group, all 25 saved values, work-unit preservation and that removing only world StateInfo restores source semantics. Wwise's equivalent default-property XML forms and PropertyList ordering are normalized; platform-qualified values and signal-order lists are preserved exactly. No test fixtures, globals or generation.
- `white_orchard_state_bank_audit.py`: read-only v150 Stage 1 decoder/comparator. Verifies the measured inline State block, native group/transition evidence, metadata bank hash, unchanged media and all non-world HIRC. This is deliberately limited to the observed world layout; it cannot certify runtime loading or write/repair banks. Current outputs remain nondeployable because generation fails and native/generated project identity compatibility is unresolved.
- `white_orchard_state_volume.py`: historical fixture-based playback proof (report 13), **not** clean shipping authoring source.
- Stage 1 does not use `white_orchard_author.py`'s custom-bus mixer or the WMC RTPCs. The full project remains intact; eventual deployment may still contain a single regional bank. See report 14 for generation and licence limitations.
