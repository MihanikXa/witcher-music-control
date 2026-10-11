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

## Additional current baseline reference

The **canonical integration input is now `ink-and-iron-0.8/`**, per the user's
11 October update. Its unmodified module payloads and Fonts (Vanilla) override
are local-only. See the [0.8 audit](../research/ink-and-iron-0.8-integration.md).
The older `ink-and-iron/` extraction is historical comparison evidence.

See [Ink & Iron folder](ink-and-iron/README.md) for v0.7.4 module extraction names and local-only rules.
