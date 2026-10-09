# Alignment Fix — no-install recommendation

**Do not install this unchanged package for the current 5.01 runtime.** The
read-only live inspection found it already enabled at priority **38**; its bundle
and metadata exactly match the supplied reference. Recommend disabling only
`Easier to Read for TW3 - Alignment Fix` in Vortex. Nothing was disabled by the agent.

## What it changes

Bundle SHA-256:
`7a8d846ea8238b1cee123923a15b493ec22e43602c87c9f3a33911f7871f73b3`.
Exactly two indexed resource paths:

| Path below `gameplay/gui_new/swf/` | Reference payload SHA-256 | Current installed vanilla SHA-256 |
|---|---|---|
| `glossary/panel_glossary_bestiary.redswf` | `b317f27242e3da1ef0be0b1674db3a3e5362efcdb11d2da8295cea84b6bdebee` | `5504d971e06802cec015e235fe2cef6b0bff69a6680b56e118d8ef65364676cc` |
| `glossary/panel_glossary_encyclopedia.redswf` | `e0c5de8a0864e5d2d58bdb481aa1e4058c91dfb5a30d71226cdcd4168882a7aa` | `b673fec50aca2fd9e3efcc891134125939815b936fef69de3b2151d1006d28bb` |

No script, font library, settings XML, NPC nameplate, subtitle or inventory
movie is included. Both movies still use `$NormalFont`. Font-independent field
geometry changes therefore apply even with vanilla typography, but improvement
is not guaranteed without testing.

Stable comparable text fields: Bestiary DefineEditText IDs 33/36/54/55 and
Encyclopedia IDs 6/7 retain their layout attributes while reducing Ymax. Examples:
Bestiary 55 and Encyclopedia 7: **611 → 564 twips** (2.35 logical px shorter);
Bestiary 54 and Encyclopedia 6: **540 → 498** (2.1 px shorter). These are text-box
bounds changes, not proof of a global baseline correction. Character IDs later
in the export shift; comparing equal numeric IDs globally would misidentify
objects. Shape/sprite, image identifiers and SymbolClass tables also differ.

More serious differences are in the embedded code:

- Current Bestiary `GlossaryBestiaryMenu.configUI` enables touch in the list and
  text area, sets list height 750 and scrollbar height 740. The reference omits
  those statements.
- Current Bestiary `handleInput` calls `CommonUtils.fixupKeyCode(details)`;
  the reference omits it. This is a verified input-path difference, not a
  demonstrated controller crash.
- Current Encyclopedia `configUI` enables list/text-area touch and sets scrollbar
  height 692.75; the reference omits those statements.
- Embedded `W3ScrollingList` lacks current touch-related fields/methods and
  supporting gesture imports. Bestiary's sublist code also differs, including
  current event registration. No claim is made that every removed event has a
  user-visible effect.

Some decompiler differences are variable names/debug metadata; the concrete
missing calls above are behavioral differences. Runtime effects require tests.
Structural parsing is successful and the author tags the mod Remastered
compatible, but that does not override this installed-baseline comparison.

## Collision and priority assessment

No other installed bundle/loose movie owns either path. SAH replaces wolf bars
and buffs; Bestg replaces wolf bars and radial menu; Hoods replaces inventory;
Outfit Wheel replaces common/root HUD/overlay. FriendlyHUD, Menu Fix and package
04's relevant changes are scripts, with different resource paths.

Consequently, this can be packaged independently for Vortex and does not need a
binary compatibility patch with those mods. Its complete movies override
**vanilla**, however. A higher/lower mod priority cannot recover missing vanilla
code. No priority adjustment is recommended. No Script Merger regeneration is
needed or appropriate for this two-movie package.

It may reduce apparent vertical misalignment for some fonts. Narrower field
heights can also clip tall ascenders/descenders, accents or wrapped lines. Its
absence of font assets does not prove its geometry is equally good with every
font. These regression risks have not been tested in-game.

## Exact Vortex procedure for this machine

1. Close the game; select **Witcher Compatibility Test**. Record that Alignment
   Fix alone is enabled at 38; retain the downloaded original archive.
2. In **Mods**, find **Easier to Read for TW3 - Alignment Fix** (internal folder
   `modtw3EasierToRead-UI-Fix`), choose **Disable**, then **Deploy Mods**.
   Leave the package installed for reversal.
3. Verify Vortex reports it disabled, its generated mods.settings entry is
   disabled/removed, and its two deployed payload files are absent from the
   active folder. Do not manually delete managed hardlinks, edit priorities,
   purge all mods, or run automatic Script Merger regeneration.
4. Check Bestiary and Characters with the current font: long names, scrolling,
   description wrapping, item recommendations/tooltips, mouse wheel, keyboard
   navigation and controller focus/back/accept. Use the existing test save and
   avoid overwriting campaign saves during the check.
5. One-package reversal: **Enable** that same Alignment Fix package and
   **Deploy Mods**, retaining its old relative priority. This restores the
   reference version, with the caveats above; it is not the recommended baseline.

For a future corrected build, Vortex procedure is **Install From File** using
the author's original archive or our independently built replacement, verify
`Mods/mod.../content/{blob0.bundle,metadata.store}` deployment (no extra wrapper
directory), enable only one alignment package, preserve all existing priority
relationships, deploy and run the same test matrix. There is **no instruction to
install the current archive now**, and no numeric priority can make it a 5.01
code-preserving patch. A replacement must apply selected geometry adjustments
to current vanilla and preserve current code; author assets cannot be reused
without permission.
