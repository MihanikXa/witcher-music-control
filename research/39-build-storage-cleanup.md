# Build storage cleanup — 2026-10-14

The user requested cleanup before continuing consolidated packaging/NML expansion, then authorized continuation of the proposed conservative cleanup and verified audio deduplication.

## Actual actions

The three suggested deletion targets were **already absent** when execution began: `build/white-orchard-followup/cooker-root/unused-content-probe` and the NML baseline/candidate `.cache` directories. No additional directory or cache was deleted by this run. The previously inventoried 8.2 GiB is not counted as space reclaimed here.

434 original NML audio files were verified against the retained baseline's `input-manifest.json`. Each corresponding candidate and authoring-fixture copy matched its expected SHA-256. All868 duplicates were atomically replaced by NTFS hard links to the baseline originals, followed by hash and shared-file identity verification. Fixture-only imported audio and all profiler/PCM evidence remain independent and untouched.

**Reclaimed duplicate allocation: 13,850,376,020 bytes (12.90 GiB).** C: free space changed from66,308,247,552 bytes at this run's initial snapshot to80,111,517,696 bytes at its final snapshot (other system disk activity can affect the difference). The final reading is approximately74.61 GiB free. Logical folder-size totals still count shared files at every path and need not decrease; storage is actually shared on NTFS.

The verified locations are confined to:

- `build/regional-system/nomansgrad/baseline/Originals` — canonical copies.
- `build/regional-system/nomansgrad/candidate/Originals` — corresponding aliases.
- `build/regional-system/nomansgrad/fixture/validation/Originals` — corresponding aliases only.

No installed game/REDkit/Wwise/depot/reference resources were linked or edited. No project licensing contents were opened, copied or modified. All21 existing `.wproj` files retain their size and modification timestamp. Hashes of retained D, NML pilot and licensed NML baseline banks and the accepted D/NML ZIPs match before/after. No Vortex, save or profile operation occurred. **110 unit tests pass.**

Private detailed preflight/progress/result manifests remain under ignored `build/cleanup-2026-10-14`; they contain the exact source/alias paths, sizes and expected hashes. They are not distributed. The source projects, output-bank Media folders, metadata, accepted archives, settings backups and earlier experimental evidence remain retained.

## Shared-media rule

Treat all deduplicated original audio as **immutable**. Editing an alias in place would edit every linked copy. Contextual Volume/State authoring changes only work units and is compatible with this constraint. Before any future intentional source-audio edit, create and verify a genuinely separate copy; do not change the installed originals or shared baseline material. Conversion caches can be regenerated independently.

The native two-bank packaging and expanded-NML development objective from report38 remains outstanding; this cleanup does not establish cache coexistence or new musical coverage. It restores working space while preserving the existing validated artifacts and project-local entitlement applications.
