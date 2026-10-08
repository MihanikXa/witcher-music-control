# Mod compatibility audit scope

This directory is a separate mod-compatibility investigation, published on the
general-merge branch at the user's request. Keep the existing music-control
project files unchanged. Do not install its experimental music mod.

Live game/Vortex files are read-only until the user explicitly approves a named
deployment. Game launch requires separate approval. Do not regenerate REDkit's
depot, purge Vortex, or edit saves or game binaries. The user's implementation
request authorizes private replacement builds and documented qualitative feature
trade-offs, including recommended package disables. Do not apply those disables
to the live Vortex profile. The current user instruction takes precedence over
the earlier first-pass feature-preservation gate.

Commit reports and original audit-tool source only. Keep evidence, extracted
resources, private database/control snapshots, third-party tools/source clones,
merged game scripts, localization payloads and installable archives ignored.
Never force-add these assets. Binary quest priority is not a semantic merge.

Machine-specific paths in reports describe the audited installation. Paths in
tool source are example inputs from that installation, not portable defaults;
review and adapt them before reuse.
