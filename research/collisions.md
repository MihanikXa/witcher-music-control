# Collision and behavior report

Read-only snapshot, 9 October 2026. Live indexes supersede historical reports.
No load order was changed. Same resource paths select a whole winner; different
scripts/movies can still interact through the same Flash contract.

| Proposed/reference unit | Same-path collision | Behavior intersection | Decision |
|---|---|---|---|
| Supplied Alignment Fix | Only its already-deployed identical copy; no competing mod owner | Older complete glossary code overrides newer vanilla input/layout | Disable that one package; no resource priority remedy |
| Gentium EN library | Font of Life EN if both installed; neither font mod is currently deployed | Every EN UI movie using aliases; widths, wrapping, icon positioning, Hoods tooltips, SAH labels, menu rows | One English library at a time. Separate font proof from shadow/color |
| Font of Life | EN overlaps Gentium; RU/UA optional language scope | Global font metrics; bold small-cap and hanging-figure taste | Use upstream Alegreya for our independent design; no reference asset reuse |
| CNC full EnemyFocus WS | FriendlyHUD same path: `game/gui/hud/modules/hudModuleEnemyFocus.ws` | SAH EnemyFocus damage/dodge wrappers, visibility controls; FriendlyHUD name visibility/placement | Do not choose one by priority. Reimplement narrowly on supported current contracts or patch the movie |
| NPC movie proof | No installed owner of `hud_enemyfocus.redswf` | FriendlyHUD WS, SAH visibility/alpha/damage logic; quest icon uses textWidth | Good isolated first candidate; retain exports, names, timelines and visibility code |
| Dialogue/subtitle later modules | No selected subtitle/dialog movie competitor | FriendlyHUD dialogue WS; Monster Hunt and Sharedutils option callbacks; Poster subtitle route | Preserve callbacks, timing and width settings; renderer-level style edits |
| Prompt module | No movie competitor | FriendlyHUD interaction WS, native screen positioning, hold/key inputs | Movie-only style patch first; no script state replacement |
| Quest/notification later modules | No selected movie competitor | FriendlyHUD quest/notification scripts; SAH and Monster Hunt SendObjectives hooks; SAH suppression/pooled label handling | Target presentation only; do not bypass settings or restore deliberately hidden elements |
| Inventory later module | Hoods owns `inventory/panel_inventory.redswf` | Hoods/BIA inventory component wrappers, rarity and tooltip metadata | Combined current compatible movie required, or defer inventory. Priority would lose Hoods features |
| Wolf bars later module | SAH vs Bestg already collide | Existing intentional SAH winner and school stance display trade-off | Defer; do not substitute a vanilla movie to restyle it |
| Settings/menu later module | Selected menu movie has no competitor | Mod Settings Menu Fix, Better IGNI, Sharedutils, SAH, package04 merged scripts | Maintain menu rows and hooks. Avoid menu XML for fixed initial palette |
| Root/common/overlay later modules | Outfit Wheel replacements | Imported/shared renderers and controller flows | Leave out of initial architecture; combined patches only if needed |

Package 04 currently supplies thirteen reviewed merge files including the
analog-gait update. It does not own the Alignment Fix movies or the NPC movie.
The presence of name/HUD references in merged player/hud scripts is a behavior
dependency, not a resource-path collision. Do not regenerate these scripts.

SAH's current `ShowDamageType` and `SetDodgeFeedback` wrappers, its handling of
EnemyFocus visibility, and FriendlyHUD's `SetGeneralVisibility` calls must keep
working after a visual patch. The NPC proof must never force a module visible.
An unshown label can be correct behavior under the selected profile settings.

Limit: compiled script blobs, resource caches and runtime wrapper ordering have
not been exhaustively decoded. No loose/bundled path collision means there is
no detected replacement conflict; it is not a runtime certification. Re-run
the audit after any newly installed UI mod or game update.
