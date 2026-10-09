# Local reference mods — read-only

Extract the **four reference packages** into these locations beneath the local clone, preserving each archive's own internal folder layout:

```text
reference/
├── easier-to-read/
│   ├── gentium-book/
│   └── alignment-fix/
├── font-of-life/
└── configurable-name-colors/
```

- `easier-to-read/gentium-book/`: the user's preferred literary-font direction. Source: Easier to Read (Nexus 11657).
- `easier-to-read/alignment-fix/`: separate alignment fix from Easier to Read; investigate install impact independently.
- `font-of-life/`: secondary typography/toolchain reference (Nexus 13507).
- `configurable-name-colors/`: source for semantic NPC/name-color control (Nexus 11614).

All extracted binaries, author scripts and files are intentionally ignored by Git. Do not redistribute third-party modified assets or fonts without an appropriate license. These references are **not approved live deployment packages**. Install the standalone alignment fix in Vortex only after checking its actual contents for collisions with Seamless Adaptive HUD/FriendlyHUD.
