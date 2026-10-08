# Witcher mod audit — review checkpoint

Git publication includes reports and original helper scripts only. Evidence, private machine-state snapshots, extracted game/mod resources, third-party tooling and actual patch payloads remain local and ignored. References to those paths describe the private audit workspace; they are not missing downloads from this repository.

36 mod packages; 35 Mods folders and 5 paired DLC folders (40 content folders including generated output). 18 confirmed file/text conflict units: 5 script, 8 quest/scene, 1 HUD, 4 English text IDs; plus 1 combat-behavior overlap requiring validation. Five existing merges verified for source inclusion; one localization merge staged; one Arrow installation correction staged. Twelve confirmed conflicts and the combat overlap remain unresolved for preservation. Additional control/provenance/integrity issues are listed separately.

The current installation is not certified safe for quest progression. No deployment/game launch took place. The review candidate is not an approved universal fix.

- [Inventory and ownership](inventory.md)
- [Complete detected conflict matrix](conflicts.md)
- [Resolutions and exact approval/deployment steps](resolutions.md)
- [Load-order evidence and candidate](load-order.md)
- [Validation and limitations](validation.md)
- [Rollback procedures](rollback.md)
- [Private patch packages](patches/README.md)

Read the Blood Ties letter preview, then approve only named packages/relationships. Quest/HUD/combat sacrifices require separate explicit decisions. Game launch/testing requires separate approval. Reports and extracted source assets must remain private; .gitignore excludes this audit folder's material.
