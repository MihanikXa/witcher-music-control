# Ink & Iron v0.7.4 — local mod references

Download **separate modules** from https://www.nexusmods.com/witcher3/mods/13111?tab=files and extract each under `reference/ink-and-iron/v0.7.4/<module>/` in the **local** worktree. Keep exact author filenames and folder structure. Suggested directory labels:

```
reference/ink-and-iron/v0.7.4/
├── ui/
├── fonts-vanilla/
├── fonts-im-fell/
├── dialogue/
├── controller-buttons/
├── icon-pack/
├── bestiary-art/
├── animated-main-menu/
├── loading-screens/
├── gwent-board/
├── hud/
└── world-map/       # only if actually downloaded
```

Actual downloaded ZIPs and extracted mod content are ignored by Git. The reference is **read-only**. Inventory-manifest diff and deployment plan: [integration document](../../../research/ink-and-iron-integration-plan.md). Keep user-accepted Vortex Compatibility Test untouched until an evidence-based overlap report. Ink & Iron All-in-One is not the intended source for the first integration test.
