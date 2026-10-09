# Selected input hashes and provenance

SHA-256, read-only inspection on 9 October 2026. Hashes identify the examined
versions; they do not imply redistribution permission. Full local file/index
receipts are reproducible under ignored build/audit, not committed binaries.

## Reference bundle containers

| Reference / filename | SHA-256 |
|---|---|
| Gentium / content/blob0.bundle | `1b77eceeecf80b18618753485fa049bef8f89674702dc013edafc9b0c075584b` |
| Alignment / content/blob0.bundle | `7a8d846ea8238b1cee123923a15b493ec22e43602c87c9f3a33911f7871f73b3` |
| Font of Life / content/blob0.bundle | `6b0afde675b93c65ea61fa539d2b3c21345d1f4e7b03308f794ce455b68fbf9d` |
| CNC / content/scripts/game/gui/hud/modules/hudModuleEnemyFocus.ws | `89f623727ac01b1f65a82367c094388d8be5dacdf8b17fca2d33350bcf217b73` |
| CNC / content/scripts/local/cnc.ws | `d8ca216d864df2bcdb1a145fb56a6b0e45380871bc129ea712df6dcb97564d95` |
| CNC / bin/config/r4game/user_config_matrix/pc/modConfigurableNameColors.xml | `322ab85572eeed1737235f01eb179059b1a9f5b58c8b60d25c9a25fc559580b3` |

## Extracted reference resources

| Owner / runtime filename | SHA-256 |
|---|---|
| Gentium / fonts_en.redswf | `9a51ed65a56006b505a772657a061b1b7a3b8ae5edbf45dd88bbac803dee1fee` |
| Font of Life / fonts_en.redswf | `3eac1424c2d645416ab218178645eb563f29119187c721c626ed928c1faee58b` |
| Font of Life / fonts_ru.redswf and fonts_ua.redswf | `a0e0f924c6294ce669c34d2220b3d2acf1a6e0cc77db9fe58926150aa3aaeb29` |

Alignment payload hashes and current matching input keys are in
[alignment-fix.md](alignment-fix.md). NPC and font proof inputs/keys are in
[implementation-plan.md](../design/implementation-plan.md).

## Other selected runtime baselines

| Filename | SHA-256 |
|---|---|
| hud_dialog.redswf | `369f02a3ac5b11ff16b04227b7187baa298f2d2040674dfb9c092847821e8e7e` |
| hud_interactions.redswf | `5e1ce7d3be052cea8a0ea9d1d744a3fe059fd367bc4bd7ed951fa76d599780e9` |
| hud_subtitles.redswf | `67795aed77b31053e4383f6e4a23d70d0d5d43cdf1df022a1754ac67a146a044` |
| hud_quests.redswf | `800fabd213227b053fa0572b8cf6c9fcbb2e0f35e0709013908cc721d3b011d8` |
| hud_journalupdate.redswf | `a84762cef295a639ccceff109508031b75ae8b75852222c4ada796b4a85430cc` |
| hud_oneliners.redswf | `410ece977ba843c547676bf76098ee924a6021d1fed416dab4435c35b6bda797` |
| hud_lootfeed.redswf | `50e3716a322cce1574bbe7ef6c069017b4868992c7ac0f34789d4d8b42986262` |
| panel_inventory.redswf | `79d448fcf006c6294eeb3f71a553570a8bee2c01cf53e1a3e6f89f5f2f28ed29` |
| panel_ingamemenu.redswf | `368d253672c4215875f80b3e3f5439b8e7eb849180ef355caaa7abe59b2ea7a6` |

All three styles in each reference EN library contain every current vanilla EN
code point. This confirms code-point-table inclusion, not shaping, glyph quality
or absence of clipping. Exact lists and glyph-tag hashes remain local.
