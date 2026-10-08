# Audit tools

Implementation tools: refresh-merges.py stages current Steam native changes
using preserved diffs and reviewed override hunks; build-release.py builds four
private deterministic ZIPs from pinned local sources; prepare-settings.py
creates narrow offline settings copies/diffs; validate-release.py validates
the combined overlay, current Steam scripts, archives and retained settings.
All require the preserved private evidence. Public Git deliberately omits
third-party/game payloads. Do not rerun the historical build-reports.py over
phase-two reports without adapting it; it writes first-pass report content.

These are original helper scripts for the private audit. Machine-specific paths
in their source are **example inputs from the audited installation**; adapt them
before reuse. Reports document the tested versions and limitations. No script
deploys fixes or launches the game.

- inventory.py: file hashes, bundle indexes, staging and deployment ownership.
- vanilla-index.py and steam-baseline.py: installed-version resource/depot checks.
- extract-collisions.py and extract-baselines.py: bounded private extraction.
- scripts-audit.py and merge-check.py: annotation overlap and source inclusion.
- localization-audit.py: string-index/key comparisons.
- vortex-state.cjs: inspect a private copy of accessible Vortex database files;
  recovery may omit locked logs and must never be restored to live Vortex.
- stage-safe-fixes.py: generate private review payloads from local sources.
- validate-review.py: live baseline guards and proposed-result checks.
- build-reports.py: render reports from private evidence.

Python tools use the standard library except for staging's installed author
localization helper. Merge checks require Git; extraction requires the locally
installed QuickBMS/tool script; Vortex inspection requires a compatible Node
runtime and Vortex's native LevelDB binding. Third-party tools, source clones,
evidence and game/mod payloads are intentionally not included in Git.

This repository does not contain enough source assets to reproduce a semantic
quest/HUD patch or certify compilation. Do not mistake extraction or a clean
three-way merge for runtime compatibility.
