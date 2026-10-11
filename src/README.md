# Source

Store only project-authored source specifications here; do not commit vanilla Wwise work units, banks, streamed media, REDkit data or downloaded third-party payloads.

- `wwise/white-orchard-state-volume.json` — current **Stage 1** Init-free direct-State Voice Volume policy. The existing game State definitions are reused, with no new global objects.
- `wwise/white-orchard-mixer.json` — earlier optional adjustable-mixer experiment; keep for reproducibility, **not** the first playable build.

The clean Stage 1 authoring helper is in `tools/white_orchard_state_volume_author.py`. No install-shaped source or verified game-compatible audio package exists yet. See research/14-full-context-bank-experiment.md.
