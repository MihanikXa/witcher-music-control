# Shared regional authoring — 2026-10-13

Observed: the shared author/source gates represent preserved White Orchard D without regenerating or replacing it. This is implementation, not an expanded release.

## Implementation and reproduction

`src/wwise/regional-manifest.schema.json` and `src/wwise/regions/*.json` separate pinned identities/source facts, classifications/evidence, approved edit decisions and unresolved decisions. `tools/regional_music.py::{plan,author,validate_source}` resolves physical ancestry and selector consumers, checks the existing 25 global States, and uses supported WAAPI State/property operations. Fresh local CustomState identities may differ; their global State references and Voice Volume semantics must match. No new global objects are authored.

`white-orchard-D.json` is a bounded retained-D regression specification: root State policy plus the five original static playlist edits. Its legacy allowance does **not** approve root attenuation for new exception-aware policies. `white-orchard-exception-proof.json` and `nomansgrad-pilot.json` refuse attenuation ancestry for protected, mixed or unresolved targets. Static targets must be approved generic, with no combat/Gwent or unreviewed consumer. Missing decisions, changed identities, global State references, unexpected routing and unrelated edits fail closed.

`tools/regional_music_gate.py::source_gate` checks complete 1,508-unit context, unchanged nonmusic work units, original regional source audio, pinned global inputs and all remaining music semantics after restoring only declared edits. `tools/regional_music_cache.py::verify_bytes` checks bounded CS3W entries, expected regional bank names, no Init/media entries and exact payload bytes. Existing cooker and generation diagnostics gates remain mandatory.

## Actual regression evidence

Local evidence (all ignored): `C:\Dev\witcher-music-control\build\regional-system\D-source-regression.json`, `D-complete-regression.json`, `D-regional-cache-gate.json`. Source regression passes: 25 States, one scope, five static properties; all remaining music semantics exact. Complete gate confirms original context/audio/global objects. Known D bank SHA-256 remains `925e912387fd47aa1e5d9213c9e2cbc8d94eb82e9d66e565f3e9dccb42ca0d6d`; baseline `5b28f4ee5f286ec46a80120ea632c1d2ca715c0e2b05fb90ddd411f16e9a953a`. Six HIRC records differ versus baseline (world plus five playlists), no additions/removals or embedded media change. Cache payload identity passes; working D and A/C artifacts were not edited.

59 tests pass: `python -m unittest discover -s tools -p 'test_*.py'`. New suites cover semantic identity normalization, protected ancestry, mixed consumers, missing approval/coverage, forbidden combat attenuation, unexpected routing/State edits, bank identity/media changes and cache boundaries/payload identity. Negative-test printed failure reports are expected assertions.

## Important unfinished bank gate

`bank_preflight` compares BKHD identity/metadata, record sets, chunks and embedded media, but **only the pinned existing D has a measured regression adapter**. Every new regional/exception bank remains rejected with `measured_record_decoder_required_for_this_manifest`, and packaging authorization is always false. White Orchard byte offsets are deliberately not reused against other objects. New decoded State/static-field allowlists, streamed-reference/dependency checks and generation-warning review are required before candidate approval. This limitation is explicit; source success cannot authorize packaging.

The shared prepare function supports regional media with full hierarchies; the selected-bank generator supports the eight existing regional names and fresh output only. Neither performs bulk generation. Retained D, native Init, installed assets, profiles and saves remain outside authoring targets.
