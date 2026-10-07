# Reference audit

## Scope and method

This is a read-only inventory of the extracted reference trees. Sizes are byte counts from the files on this machine. SHA-256 is recorded for the principal scripts, configuration, and binary resources; the repeated locale files are grouped when their hashes are identical. No reference file was changed.

## Inventory

### Only Story Music variants

All four variants contain exactly two files. There are no audio banks, Wwise projects, XML configuration files, or bundled resources in these trees.

| Variant | Relative file | Type | Bytes | SHA-256 |
|---|---|---:|---:|---|
| `story-only` | `modOnlyStoryMusic/content/scripts/engine/sound.ws` | WitcherScript | 18,613 | `E42F3AD4FBF20BA0E65861B96DD47FCF7A8E999FF75AF40B37FB1FA08DCCB61F` |
| `story-only` | `README.md` | text | 246 | `2C371FC6FA1235D0237E4102C5A4829C715C89F9C8071DAFA31DD471033A1C11` |
| `story-gwent-tavern` | `modOnlyStoryMusic/content/scripts/engine/sound.ws` | WitcherScript | 18,618 | `4360CA6A0B293190742A9DE519DB775BA7C815E29BD451C6C0B4B779270A2436` |
| `story-gwent-tavern` | `README.md` | text | 328 | `02A7FEA5077DE34FC05CFD97AC2EFAA9D3AED6AA19348A647E014D26E3F9B758` |
| `story-combat` | `modOnlyStoryMusic/content/scripts/engine/sound.ws` | WitcherScript | 18,683 | `C7AEA3C09D897BCC2AF7EFCD819A7CE98733A8290315F0296C80F8A8F7154A76` |
| `story-combat` | `README.md` | text | 291 | `CD38EAC809ACE6E5E7041F08A16DCB0521D5D990BFBDFC585A07488C6F61844F` |
| `story-exploration` | `modOnlyStoryMusic/content/scripts/engine/sound.ws` | WitcherScript | 18,746 | `B55C327888132A2D7C3DEC32696283CA5D2F384E01E8447D93A9C395401229EB` |
| `story-exploration` | `README.md` | text | 316 | `1BD5F71453E2BA37B896DEE46F111A5779A1B5A71AAF37121BDFE8FA44B59E4A` |

**Observed fact:** the only implementation file in every variant is a replacement at `content/scripts/engine/sound.ws`. The variant differences are script text changes, not binary resource changes. See [02-only-story-music-diff.md](02-only-story-music-diff.md).

### Less Is More

| Relative file or group | Type | Bytes | SHA-256 / note |
|---|---:|---:|---|
| `mods/modLessIsMore/content/scripts/engine/sound.ws` | WitcherScript | 30,717 | `BAD44C6293C089F1969676E3C8FBC311DED459DF51420669816D038BA266AE8C` |
| `bin/config/r4game/user_config_matrix/pc/modLessIsMore.xml` | XML config | 2,811 | `79FCF60B4CD7B6211295D54B5433B31B53EE9AC4EE3D2F493ACA06C2D9D65548` |
| `mods/modLessIsMore/content/{ar,br,cn,cz,de,en,es,esmx,fr,hu,it,jp,kr,pl,ru,tr,ua,zh}.w3strings` | localized binary text | 18 files × 180 | all `12890C52233F3F4CB987E99DB951985743EA84AD56F12A677050278153CBB4B7` |
| `README.md` | text | 389 | `A15D4D80A9250EAD994D9A6506DEA8B8E69C55ECF274420098062F022628D9CA` |

**Observed fact:** Less Is More is primarily a full `engine/sound.ws` script replacement plus an XML menu configuration. Its script adds `lim_` fields and methods, including menu reads, elapsed-time handling, an inn/bard exclusion check, and state-string suppression. It has no Wwise bank or cache in the extracted tree.

The added fields and defaults are at `sound.ws:331-384`. `lim_Tick` refreshes menu settings and, during exploration, re-emits the current `game_state` when a random play/mute interval expires (`sound.ws:386-448`). `lim_ReadSettings` reads the XML group `modLessIsMore` (`sound.ws:450-482`; `modLessIsMore.xml:1-42`). `lim_UpdateInnExclusion` looks for an innkeeper and nearby `musician` entities in an interior (`sound.ws:484-567`). `lim_StringToggled` returns either the original state string or `""`, and `lim_OnGameStateChange` extends a mute after combat (`sound.ws:577-642`). Its replacement `GameStateToString` selectively suppresses exploration, dialogue, combat, boat, and underwater mappings while preserving cutscene/movie/music-only/Gwent mappings (`sound.ws:644-693`). The replacement `CollectSoundStates` is otherwise close to vanilla and calls `lim_Tick` (`sound.ws:874-943`).

### FMC Audio Remaster

| Relative file | Type | Bytes | SHA-256 |
|---|---:|---:|---|
| `mods/modFMCAudioRemaster/content/scripts/local/FMCAudio.ws` | local WitcherScript | 13,403 | `2B057290FF1CD7488B401B06F9CB633F50A92EE54006A4E7D7350B45BBE825A4` |
| `bin/config/r4game/user_config_matrix/pc/modFMCAudio.xml` | XML config | 5,576 | `0601855C5F4DAF2CBA71F4DA8AFCAAE3D2E198D2CCB130632516B5FB64269CAD` |
| `bin/initialdata/sound/Init.bnk` | Wwise sound bank | 38,007 | `EB79F94D4E7BFA63B1752B821A1B32B606FAAF9A18DDA11227275B41AD6475CD` |
| `mods/modFMCAudioRemaster/content/soundspc.cache` | bundled sound cache | 42,886,567 | `9CDCC9BA66BC4166699B5112967DF74C3060066C3706A6D30090CC0C6F049EED` |
| `mods/modFMCAudioRemaster/content/en.csv` | text localization/source | 1,470 | `D104F7E2596962C9CD355D5A4163DA4B040A03F87BCFDD4A2CD9FF40110D04F5` |
| `mods/modFMCAudioRemaster/content/witcherscript.toml` | mod metadata | 382 | `1CED7B577A55A52E9057A6CCB6FF8A6298984621A40D7B132FB276B72DFC6C79` |
| `mods/modFMCAudioRemaster/content/{ar,br,cn,cz,de,en,es,esmx,fr,hu,it,jp,kr,pl,ru,tr,zh}.w3strings` | localized binary text | 17 files × 1,598 | all `216ED4064A703FC0B358287095A7CC784161BAA9163AB2433D27BDC9171DE88D` |
| `README.md` | text | 429 | `3467A03734A2E195E1236E9C4F966E89B8AA68EFD2CBE57270952A7F24D8DC71` |

**Observed fact:** FMC is a mixed script/config/resource mod. `FMCAudio.ws` wraps `CR4IngameMenu` methods and calls `CScriptSoundSystem.SoundGlobalParameter` for names such as `fmc_explorationMusic`, `fmc_combatMusic`, and `fmc_dialogueMusic` (`reference/fmc-audio-remaster/mods/modFMCAudioRemaster/content/scripts/local/FMCAudio.ws:2-18,140-164,327-338`). The custom `Init.bnk` and `soundspc.cache` are separate resource evidence, not script-only changes.

The FMC `Init.bnk` is 38,007 bytes with SHA-256 `EB79F94D4E7BFA63B1752B821A1B32B606FAAF9A18DDA11227275B41AD6475CD`; the installed vanilla `bin/initialdata/sound/Init.bnk` is 32,840 bytes with SHA-256 `2DCB418B9F96389A57341A49E86CDCB0C18D95552A0E17DCCF10D4DF1D54D277`. This confirms a real bank replacement in FMC, even though the binary contents are not decoded here.

The XML exposes independent 0–100 exploration, combat, and dialogue sliders and presets (`modFMCAudio.xml:5-59`). The script only reacts to menu preset/config callbacks: a search of `FMCAudio.ws` finds no calls to `GetCurrentGameState`, `CollectSoundStates`, `ShouldEnableCombatMusic`, or scene-player state methods. **Inference:** FMC's contextual separation is encoded in its custom Wwise resources, while the script supplies the configured parameter values; the script itself does not classify exploration, combat, dialogue, or cinematics at runtime. Its `witcherscript.toml` records game version `4.04`, so compatibility with the current installed Remastered build remains a question even though the script uses current-looking local-wrapper syntax.

## Preliminary applicability notes

- Less Is More uses the current-looking `ESoundGameState` names and `SoundState` path, but replaces the complete engine sound script. That is useful behavioural evidence and a high conflict risk; it is not evidence that a small local override of `CScriptSoundSystem` is supported.
- FMC is the strongest evidence that contextual music multipliers can be implemented in Wwise with global parameters, but its script does not discover gameplay context. It sets parameters from menu/config callbacks; the resource side must associate those parameters with music content.
- The reference trees do not establish that a `story` runtime state exists. The controlled Only Story Music diff shows a different mechanism.
