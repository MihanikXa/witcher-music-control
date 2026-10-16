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

## Ink & Iron 0.8.6 — next Inventory source (16 October)

**Use 0.8.6 UI as the next Inventory design source**, together with the separate
official **Hoods Compatibility** optional file (first released with 0.8.3).
Place exact original ZIPs and extracted source in a versioned, gitignored
`reference/ink-and-iron-0.8.6/` subtree after checking archive/member hashes.
Do not overwrite the 0.8.0 extraction or treat its audit as a 0.8.6 audit.
If local archives are missing, obtain them manually from the
[official Nexus files page](https://www.nexusmods.com/witcher3/mods/13111?tab=files);
do not invent matching filenames, hashes or dependencies.
See [version-specific Codex handoff](../research/ink-and-iron-0.8.6-inventory-handoff.md).
Do not deploy a new I&I HUD over the accepted v4/RC2 HUD.

## Historical 0.8.0 reference

The **11 October historical integration input was `ink-and-iron-0.8/` (0.8.0)**. Its unmodified module payloads and Fonts (Vanilla) override
are local-only. See the [0.8 audit](../research/ink-and-iron-0.8-integration.md).
The older `ink-and-iron/` extraction is historical comparison evidence.

See [Ink & Iron folder](ink-and-iron/README.md) for v0.7.4 module extraction names and local-only rules.
