# Only Story Music — differential reference set

Download all four current Remastered variants and extract them separately:

```text
only-story-music/
├── story-only/
├── story-gwent-tavern/
├── story-combat/
└── story-exploration/
```

Do not merge the archives.

The point of keeping all four is differential analysis:

- `story-only/` is the baseline.
- Diff `story-gwent-tavern/` against the baseline to isolate Gwent/tavern changes.
- Diff `story-combat/` against the baseline to isolate combat changes.
- Diff `story-exploration/` against the baseline to isolate exploration changes.

Primary research question:

> Which concrete files, settings, resources, events or metadata differ when each music category is restored?

Preserve each archive's internal directory structure. Extracted files are ignored by Git.
