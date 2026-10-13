# 29 вЂ” Regional comparison and scalable full-game implementation

Date: 2026-10-13. Planning plus read-only inventory, not new bank authoring/generation. Working White Orchard D, Vortex and saves unchanged. Reports27вЂ“28 recover actual D and define authored-world risks. Successful White Orchard gameplay resolves the former pilot loading uncertainty; it is not proof of every other bank or authored cue.

## Reproducible structural inventory

W = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`; I = `W\Interactive Music Hierarchy\music.wwu`; E = `W\Events\music.wwu`; B = `W\SoundBanks\music.wwu`; N = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc`. All inputs read-only. Evidence `C:\Dev\witcher-music-control\build\full-game-audit\complete-inventory.json` includes input hashes, GUIDs/ShortIDs, source lines, selection paths, source references, event actions, native bank memberships and empty choices.

New reusable command:

```powershell
python tools/music_region_inventory.py --source 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio' --native-banks 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc' --output build/<fresh-audit>/inventory.json
```

`entries` follows only each selector's own EntryPath/AudioNode mappings; `inventory` resolves GUIDs and refuses unresolved AudioNodes or missing/duplicate regions/banks. Explicit native empty choices are retained as empty, not guessed into playback. `native_banks` inventories bank membership without interpreting opaque reference fields. `run` hashes the four named source WWUs before/after, optional nine native banks before/after, and only writes a fresh ignored build evidence file. It does not inspect the project/licence. Ten synthetic controls test selection scope, empty choices, cross-branch consumers, shared media without policy promotion, native membership and fail-closed missing inputs; total32 repository tests pass.

### Common foundation, not identical compositions

All eight roots select world vs authored through the same existing `music_type`; all world branches select locations and their direct child selectors use `game_state`. Original world roots have **no StateInfo**: the new local table is our edit, not a vanilla table to transplant indiscriminately. Actual current25-State policy comes from `src/wwise/white-orchard-state-volume.json`; original game State definitions/transitions remain in `W\States\global_states.wwu`. Individual selectors map only a subset; omission/default selection must remain native. All regional roots reference existing Music bus GUIDAC8DA8A9-B09E-4E08-BCEC-0FD3D36D101C. Stored descendant Master Audio Bus references are not evidence of active output overrides (reports03/13).

| Regional bank / root source I line | World ShortID / line; quest line | Direct location selectors / world playlists | Distinct E/En/D/Dn targets | Observed special cases / rollout concern |
| --- | --- | ---: | ---: | --- |
| music_prologue /113621 | 1033516231/122301;114180 | 9 /37 | 10 | Known five-static-playlist D correction; winter/tavern winter and village_q505 remain root-muted in E/D. Generic and combat playlists separate. Report28. |
| music_nomansgrad /161929 | 492774600/244033;165531 | 48 /227 | 58 | Includes focus_combat; ghost-forest and dialog_ambient_03 targets cross noncombat/combat use. Quest house silent variants, inquisitor/embassy/burned-village/lovers themes and other report07 cases. Most main-game coverage, largest policy matrix. |
| music_skellige /6 | 655655590/33614;1236 | 23 /121 | 26 | minigames included; expl_skellige_tavern shared noncombat/Gwent/minigames. Yennefer room love theme, q205 burned village, fleet return selects authored; monster-hunting and boat paths. Ten source playlists absent in native regional HIRC. |
| music_kaer_morhen /143761 | 105784741/155258;144197 | 3 /13 | 4 | km_global/caves/silent; caves and silent noncombat use silence, local combat stays distinct. Intro/tutorial authored q001 lives here, distinct from playable White Orchard. Small reusable control once a meaningful existing save is available. |
| music_toussaint /390293 | 680115949/393835;440230 | 19 /94 | 26 | focus_combat,minigames; tournament_general vs tournament_quest; q702 music box, fairy tale, exhibition reused Gwent score. Two mixed noncombat/protected-State playlists. q705_prison source subtree absent from native bank. |
| music_wyzima_castle /380979 | 361704319/383421;381139 | 1 /3 | 1 | mus_loc_wyzima_castle maps exploration to expl_castle, combat cmb_castle, gwent separate. Emperor-conversation source selected as world palace score: author-intent concern dominates otherwise simple structure. |
| music_misty_island /139889 | 1037750256/140132;142936 | 1 /3 | 1 | Authored sibling named **quests_cutscenes** (no вЂњandвЂќ). mus_loc_isle_of_mists selects mi_general/mi_expl; combat mi_cmb, gwent distinct. Entire location story setting; cannot infer its regional theme is disposable. |
| music_spiral /384709 | 577841188/384734;386590 | 2 /3 | 2 | mus_loc_spiral/general vs mus_loc_spiral_castle. **expl_castle is selected in combat and exploration**; no dedicated Gwent mapping in inspected world entries. Shared q101 talk-source is in NML authored branch. Static mute would break required combat behavior. |

Counts concern **106 direct selectors and501 descendant world playlists**, not all authored exception count. Playlist count includes transition material and unselected objects. Same-region authored AudioFile sharing includes silent sources and ordinary arrangements, and is only a review flag. Cross-region same-media cases (prologue q505 / NML q302/q303; Spiral castle / NML q101) remain covered by report07; the tool's `quest_branch_shared_files` is explicitly same-region and is not a complete cross-region intent classifier.

### Transitions and intensity cannot be normalized away

I/world descendants contain201/1508/901/74/632/16/28/21 `MusicTransition` objects respectively in table order, **including folder roots**, not that many executed transitions. Explicit ExitSourceAt values differ: prologue2/3, NML0/1/2/3, Skellige0/2/3, Kaer Morhen2/3, Toussaint0/2/3, Wyzima2, Misty2/3, Spiral2/3; unset values remain unset. Explicit MusicFade times reach6s in NML,8s Skellige and12s Toussaint, compared with2вЂ“4s prologue. Matching installed `L:\Programs\Wwise_2023.1.19.8928\Authoring\Data\WObjects\WObjects.xml:2494` identifies beat/bar selection enums (report25). Preserve complete transition properties/fades, not just the most common value.

World descendant RTPC objects count13/221/154/7/0/0/6/2 respectively; this is recorded structure, not a guarantee of audible intensity layers or absence of other native intensity logic. D's static correction can be generalized only to reviewed generic nodes whose continuing voices should stay muted through intermediate/combat States. A playlist also selected for combat/Gwent/minigames must not receive an unconditional static mute: NML `expl_nml_ghost_forest`, `dialog_ambient_03`; Skellige `expl_skellige_tavern`; Toussaint `explo_toussaint_tavern`, `expl_sq703_photos_exhibition`; Spiral `expl_castle` are concrete conflicts. Their path-based policy requires finer selectors/voice separation or explicit native-preservation exceptions; copying and rerouting nodes introduces IDs and more validation and is not authorized by this audit.

## Banks, inclusion and media

B/each regional SoundBank includes an Events folder, Filter7, rather than a directly named MusicSwitchContainer. Inclusions resolve to prologue, nomansgrad, skellige, kaer_morhen, EP2, wyzima_castle, misty_island and spiral. E/`play_music_*` targets the corresponding actual root and selects world; named location events set a switch, not necessarily branch. The same inclusion closure must be preserved during selected generation. Complete source context remains mandatory; do not prune source to bank size.

| Native bank under N | Bytes / HIRC objects | World playlist IDs absent from its native HIRC |
| --- | ---: | ---: |
| music_prologue.bnk | 174826 /490 | 0 |
| music_nomansgrad.bnk | 1273131 /3831 | 0 |
| music_skellige.bnk | 662405 /1900 | 10 |
| music_kaer_morhen.bnk | 326697 /440 | 0 |
| music_toussaint.bnk | 678428 /1804 | 6 |
| music_wyzima_castle.bnk | 82481 /97 | 0 |
| music_misty_island.bnk | 54244 /70 | 0 |
| music_spiral.bnk | 3904 /33 | 0 |

Observed absence is not a licence/Init failure: nine Skellige absent nodes are transition playlists and one `expl_skellige_ard_skellig_night` (I:102380), none referenced by inspected AudioNode entries. Toussaint's six are the q705_prison day/night/combat/intro/outro/Gwent subtree (I:427612 onward), whose local State mappings exist but whose outer world location mapping was unresolved in report07. Actual generation closure, transition references/default resolution and runtime reachability still need separate checks; the audit does not declare these deletable or regenerate unrelated banks to repair them.

No regional world playlist ID appears in any of the **other eight inspected banks** (seven regional peers plus music_shared). This is a bounded membership observation, not complete native dependency decoding. All ordinary media strings and global SoundBank dependencies still require bank/source-reference comparison. Native files and metadata hashes are in ignored inventory; reports cite IDs instead of claiming a universal object-ownership rule.

B/`music_shared` includes shared Events folder GUID5E345BF8-E3C2-4EFC-BFFA-48CF1250F6E1; `music_main_menu_credits` includes main_menu_credits GUIDBD4F4327-51F4-450D-A720-4D81A6E3A96A. I has music_main_menu_credits and music_w2_theme outside the eight world roots. Preserve shared/menu/credits event transport and Init globals. No edit to these banks is justified by current policy; only add a changed shared bank to deployment if an actual changed serialized dependency requires it and is independently audited. Do not interpret unchanged media as permission to omit checking streamed references.

## Data-driven implementation, with strict gates

Use one shared author and one region manifest, not eight scripts. Existing D remains regression input. Manifest fields should include: source hash/version8928; bank/root/world/quest GUIDs and ShortIDs; authored sibling alias; expected location entries and event GUIDs; complete State names/values; **approved generic static targets** with original properties and all consumers; protected/ambiguous targets; intended State scopes; expected changed HIRC IDs/types/property fields; native/license baseline identities and probe recipes. Decisions carry evidence and observed/inferred status; missing decisions must produce a pending plan, never silently become generic. Names help display, GUIDs and expected references authorize edits. Example shape:

```json
{"bank":"music_nomansgrad","world_short_id":492774600,
 "state_policy":"stage1-fixed","static_generic_targets":[],
 "protected_noncombat_targets":[],"unreviewed_targets":"fail-authoring"}
```

The empty example is intentionally not an approved NML patch. Populate finite reviewed policies from this inventory/report07, distinguishing silent/common traversal from likely narrative selectors. No settings sliders or global mixer redesign is required.

1. **Plan all regions cheaply:** inventory/hash originals once, resolve actual gain ancestry and every consumer, compute generic/protected/mixed/unreachable flags. Human review determines score intent; no regex `mus_q` exemption. Freeze versioned manifest/source inputs.
2. **Complete isolated context:** reuse prepare preserve-hierarchies for1,508 work units. Parameterize region selection rather than its historical prologue constants. Keep command/output/Originals isolated. Never copy a key; existing effective project-local licence must be verified by selected generation, manual GUI action if needed.
3. **Author one manifest:** retain world State policy where there are no approved descendant exceptions. For authored-world exceptions, validate report28's relocation of added State gains onto generic physical scopes, so the protected path has no attenuating ancestor. Preserve all events/music_type/locations/transition definitions; keep fixed generic-playlistв€’200 only where every relevant use is approved. No gain on global Music or authored sibling. Do not attempt compensating+200 or assume OutputBus defeats ancestor Volume.
4. **Source gate:** restoration of only approved StateInfo/static fields must yield full original semantic source; unrelated1,507 units exact, no fixture, no global change. Confirm every protected/combat/Gwent voice path retains native gain and every intended generic path is covered. Consumer counts are per manifest, not fixed prologue40 everywhere. Reject surprises instead of ignoring them.
5. **Selected generation:** untouched licensed baseline then same-context candidate, fresh ignored directories. Capture actual exit status and every diagnostic. No premature eight-bank build, leaf exclusion, header patch or unrelated dependency repair. D exit2/15 warnings is historical allowance only for its exact reviewed diagnostics; another region's diagnostics require review.
6. **Bank gate:** compare nativeв†’baseline separately from baselineв†’candidate. Require allowed local State/property fields, explained inline local IDs, preserved unrelated HIRC and all media/stream IDs, unchanged known global references/registrations/State definitions, correct BKHD identity and metadata consistency. Extend the current bounded decoders with measured baseline-backed layouts and negative controls; do not blindly apply prologue type13 offsets to every record. Same shared/global source plus no new external dependencies matters; byte-identical generated Init is not a universal runtime criterion and **generated Init never ships**. Reject unknown differences until classified. Native/source closure omissions above are baseline evidence to explain, not a reason to loosen candidate delta checks.
7. **Playback regression:** native selector events plus realistic Eв†’combat, Cв†’E, Eв†’dialogue, intermediate scenes, location switches, night, threat/layering, Music master and authored exceptions. Profile actual target identities and envelopes; no sustained-tone-only proof. Keep fixtures separate from shipping source. Musical-intent/listening decisions are not replaced by zero-PCM or structural tests.
8. **Package once gates pass:** native cooker using isolated bootstrap/vanilla Init; only changed compatible regional banks. Generalize cache reader from single music_prologue entry to an exact expected bank-name/hash set, reject Init/extra media or duplicates, verify extracted payloads and native split readback. One full-game mod/cache can eventually contain all approved regions; one selected region per early test minimizes risk. Vortex top-level ZIP uses Mods/mod.../content/soundspc.cache with one enabled winner; multiple test variants/caches must not be assumed merged. Retain rollback and native Init hash.
9. **Stage gameplay:** separate approval, existing suitable save and unchanged other mods. Treat each region's audible generic/combat/authored tests as its own coverage, not inherited compatibility from White Orchard.

Automatable: complete-copy checks, inventory, source authoring after policy approval, hashes, selection generation, bounded comparisons, cache/ZIP exactness and evidence aggregation. Per-region structural review: entry defaults, mixed targets, actual ancestry, serialized layout/closure and native transitions. Human musical judgment: themed location vs explicitly authored dramatic use. In-game listening: transitions, composition/intensity, authored cues and soundtrack gaps. Do not stall mechanical pipeline implementation while waiting for an inaccessible ending save; mark the corresponding exception decision pending and preserve the working pilot.

## Efficient rollout and next task

1. **NML/Velen/Novigrad first**, after shared author/gate reproduces existing D source semantics and bank audit without regeneration. It provides48-selector main-game coverage and reusable complexity; dedicated quest branch remains protected. Review the high-risk noncombat world selections from report07: burned village/q203 reuse, Nilfgaard embassy/emperor theme, lovers spot/love themes, Roche/camp/location themes, and mixed ambient03/ghost-forest targets. Do not uniformly static-mute these. Most quest-labelled HoS houses already select verified silence; that can avoid needless exceptions.
2. **Skellige**, reusing the same pipeline with boat/threat/night plus love-theme/burned-village/fleet/tavern safeguards. Large main-game gain with fewer selectors than NML; unused transition nodes need baseline closure review.
3. **Kaer Morhen** as a small structural regression/catch-up region when an existing suitable save is available; its smaller graph could run before Skellige if gameplay access is better, but it is not a substitute for broad NML coverage.
4. **Toussaint**, with tournament/fairy-tale/music-box/exhibition review and longer crossfade probes. EP2 content and atypical targets justify staged validation rather than first expansion.
5. **Wyzima**, **Isle of Mists**, then **Spiral**, or opportunistically as existing saves permit. Small graph does not imply low semantic risk: emperor score, story-only island context and same-playlist combat/quest castle are the outstanding policies. Do not manufacture new campaign access or reset a playthrough.

**Most efficient next Codex implementation task:** parameterize the existing complete-copy authoring and fail-closed bank/source gate behind a reviewed region manifest, validate it first against preserved White Orchard D, then prepare one NML untouched baseline and one scoped candidate offline. Include explicit protected/pending/mixed-target handling and the narrow State-scope experiment needed for authored-world protection; stop before packaging if that experiment or serialization fails. Do not generate every region yet, add sliders or repeat licence/ProjectID research. Parallel user listening on an available q001/q505 save can settle pilot intent without blocking the shared mechanical tooling. No new experimental banks were required for this audit.
