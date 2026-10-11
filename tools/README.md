# Tools

Project-local helper scripts belong here.

Do not vendor REDkit, Wwise, Script Merger, game binaries, or other third-party executables into this repository.

## Isolated White Orchard pilot

These Python helpers use the standard library and the already installed matching
WwiseConsole. They never install or deploy anything. See
`research/10-white-orchard-prototype-results.md` for commands, measured results
and the current Init/cache blockers.

- `white_orchard_prepare.py`: copy/prune required work units and 47 referenced
  originals, sanitize project output paths/commands, hash read-only inputs.
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

Keep the WAAPI server bound to localhost, verify its project path, and stop it
when finished. Recorders and synthetic source objects stay in the separate
ignored validation workspace. The settings UI, script adapter, live-game tests
and deployment are later work. A rebuild allocates fresh local effect/state
GUIDs; the recipe reproduces the routing and behaviour, not a byte-identical
bank. Preserve the generated workspace/manifest when comparing exact builds.
