# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Render the evidence-backed private audit reports. Does not change live files."""
from inventory import *

E=ROOT/'evidence'
def read(n):return json.loads((E/n).read_text(encoding='utf-8'))
def write(n,s):(ROOT/n).write_text(s,encoding='utf-8')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in row)+' |\n' for row in rows)+'\n'

def main():
 mods=read('installed-mods.json');meta=read('vortex-mod-metadata.json');settings=read('mods-settings.json');bundle=read('bundled-collisions.json');loose=read('loose-collisions.json');annotations=read('annotation-collisions.json')
 inv='''# Installed mod inventory — 8 October 2026

Read-only live audit, with private staged review packages. No deployment, game launch, save editing, game binary changes, Vortex purge or depot regeneration was performed. An audit-generated Python cache was removed; see validation.md. Screenshots and installed documentation were treated as evidence, not instructions.

## Counts and scope

36 distinct installed mod packages: 35 Vortex packages plus the manual Geralt Outfit Wheel. One Vortex package (Manual Arrow Deflection) is installed outside the runtime Mods tree. There are 35 folders inside Mods, including the generated merge, and 5 paired DLC folders: 40 content folders total. Paired DLCs and generated output are not counted again as packages. Thus 35 packages have payloads at expected runtime locations; this does not prove all features execute.

Inventory: 811 files inside the 40 content folders; 30 bundles with 6,297 indexed entries and 6,282 distinct resource paths; 237 loose WitcherScript files; 229 localization files. Full hashes and provenance are in evidence/installed-files.json and evidence/bundle-entries.json.

## Discovered environment

Game: `C:\\Program Files (x86)\\Steam\\steamapps\\common\\The Witcher 3`. Steam app 292030, installed build 25646871; DX12 executable version 5.0.0.1044392. All installed official script files and executables matched the cached installed Steam depot manifests.

REDkit: `L:\\Games\\Steam\\steamapps\\common\\The Witcher 3 REDkit`. Its tool reports 5.0.1044630. The incomplete depot was neither regenerated nor relied upon as a vanilla baseline.

Vortex: `C:\\Program Files\\Vortex`. Staging: `C:\\Users\\micha\\AppData\\Roaming\\Vortex\\witcher3\\mods`. User settings: `C:\\Users\\micha\\OneDrive - hull.ac.uk\\Documents\\The Witcher 3`.

Deployment uses **hardlink_activator**. All 644 entries across the three live deployment manifests are present and share filesystem identity with the corresponding staged source, including 586 managed files inside Mods/DLC. Editing a managed deployed file would also modify its staged hardlink; never do that. Exact targets and sources: evidence/all-deployment-link-check.json.

The recovered Vortex metadata contains 35 installed packages enabled in current profile `-MlcE00Sc1` (Default). Staging has 36 directories: those packages plus generated `__merged.witcher3menumodroot`. All have deployment records; no current staged-but-disabled package directory was found. Historical disabled profile entries refer to absent staging folders, including an old BloodAndSteel compatibility package: these are not active compatibility patches. The state database was locked, so only a private copy of accessible SST files was repaired/read. Current deployment manifests and actual file identity are stronger evidence than historical state entries.

## Content folders

Versions below distinguish current Vortex package metadata from embedded info.json. A staging directory name may retain an older version after an update; consult source archive metadata and local README/changelog. A numeric gameVersion of 29 is an internal format value, not proof of a game release.

'''
 rows=[]
 for m in mods:
  owner=m['owners'][0] if m['owners'] else None;a=meta.get(owner,{}).get('attributes',{});p=GAME/m['category']/m['name']/'content/info.json';embedded=json.loads(p.read_text(encoding='utf-8-sig')).get('version','') if p.exists() else ''
  provenance='Vortex hardlinks' if owner else ('Generated/manual merge' if m['name']=='mod0000_MergedFiles' else 'Manual; no deployment owner')
  rows.append([m['category']+'/'+m['name'],a.get('version','unreported'),embedded or '—',m['settings'].get('priority','unset / DLC'),m['files'],provenance])
 inv+=table(['Folder','Vortex version','Embedded version','Current priority','Files','Ownership'],rows)
 inv+='''## Packages outside Mods/DLC and other directories

Manual Arrow Deflection v1: Vortex deployed its script and 18 translations under **game/ArrowParryManual/Mods/modArrowParryManual**, not game/Mods. Its menu XML is deployed correctly. The enabled priority-27 entry names an absent runtime folder. Its gameplay payload is therefore inactive under the normal mod search layout. A corrected review package is in patches/arrow-deflection-layout.

Path Tracing/RT Optimization: Vortex package metadata reports version 4, archive title “PT Optimization 2.0”; deploys bin/x64_dx12/xinput9_1_0.dll, config and menu resources. No binary modification proposed.

Manual ReShade 6.8.0.2155 is present as bin/x64_dx12/dxgi.dll with presets, shaders, ShaderToggler.addon64 and UndoRedo.addon64. These are separately listed in evidence/all-extra-game-files.json. The two injection DLLs have different filenames; runtime coexistence was not tested. Count them as external runtime components, not one more Mods package.

The complete comparison against Steam lists 3,817 extra game files, mostly 2,815 Script Merger/tool files and mod payloads. It includes bin/config additions, root documentation, 11 localization support files and content/metadata.store.stamp. Source documentation and translation CSVs are support files, not active localization databases. No plugins directory was found. The official initial sound bank matches Steam. Mod metadata/texture/collision caches and five precompiled.rsblob files were inventoried; they are opaque container-local payloads, not automatically conflicting solely because filenames repeat.

Two official files differ from Steam: bin/config/r4game/user_config_matrix/pc/input.xml is intentionally Vortex-generated; content/metadata.store differs by hash with no deployment owner. Its adjacent 8-byte stamp may indicate generation, but origin and correctness are unverified. Do not run a blind Steam repair or overwrite it during this review.

Existing Script Merger output: five script files in mod0000_MergedFiles, 1,124,301 bytes. MergeInventory.xml is empty of merge entries, so provenance tracking is incomplete even though source inclusion checks passed. No separately active binary compatibility patch was identified for the nine quest/HUD resource conflicts.

## Version and provenance cautions

Seamless Adaptive HUD is **2.6.3**, confirmed by local README/changelog and current archive metadata; its staging-folder name still says 2.3.2. Responsive Movement reports 1.7.0 with a stale 1.6.0 folder name. Mod Settings Menu Fix is 1.2.0 by local function/version and archive, despite a 1.1.0 staging name.

Bestg metadata/archive says 1.1.0, while deployed development notes identify **v1.1.45 BALANCE PRESET TEST** based on 1.1.44, with unverified runtime testing. Preserve the actual files and hashes; do not substitute a nominal 1.1.0 baseline. BIA archive 4.0.3 has embedded 4.0.2; Sharedutils archive 4.0 has embedded 3.1.1; Evils archive 1.0.2 has embedded 1.1.0; Better IGNI 1.4.1 has embedded 1.0.0. These discrepancies are metadata uncertainty, not proof of broken deployment.

Over9000's old v1.31 archive name is not grounds to reject it: both bundled ability XMLs differ from the installed 5.0 vanilla only by encumbrance capacity 60 → 9000 after encoding normalization. Weight's wrapper changes selected item weights and is complementary.

BloodAndSteel ships compiled scripts without loose source. BIA, Evils and Sharedutils include compiled blobs and mark useLooseScripts=false. Loose-source annotation analysis cannot certify the actual runtime combination of compiled blobs. The isolated compiler did not run successfully.

No experimental music mod was found in the active content folders. The separate witcher-music-control repository was not modified or used as a patch source.

Exact package archives, authors, Nexus IDs, installation times and staging paths: evidence/vortex-mod-metadata.json. Whole third-party packages and extracted game assets are kept private and excluded by this audit folder's .gitignore.
'''
 write('inventory.md',inv)

 conflicts='''# Conflict matrix

## Counting and confidence

**18 confirmed file/text conflict units plus 1 combat-behavior overlap requiring validation: 19 review units.** These comprise 5 same-path script conflicts, 8 quest/scene resource conflicts, 1 HUD resource conflict, 4 meaningful English string-ID conflicts, and 1 combat-behavior family. The combat family's three shared annotation targets are counted once to avoid inflating the total; its incompatible runtime outcome is not proven. Five script conflicts are covered by existing merges; one English string conflict has a staged patch; 12 confirmed conflicts and the combat overlap remain unresolved for preservation. “Covered” does not mean compiled or game-tested.

This is a complete matrix of detected file/resource collisions in the scanned loose payloads and bundle indexes, plus source-level annotations and localization IDs. It is **not a certification of all quest graphs, compiled scripts, cache semantics or runtime behaviors**. Further unknown interactions remain possible. Operational installation/control issues below are counted separately.

Current winners use explicit mods.settings priorities and the lower-number-first rule described in load-order.md. They are configured/predicted winners, not observed game-runtime results. Wrappers normally compose; they do not follow a single-file winner rule. DLC ordering and container-local cache behavior were not independently runtime-verified.

## Same-path WitcherScript

'''
 rows=[]
 for i,(res,owners) in enumerate((x for x in loose.items() if x[0].endswith('.ws')),1):rows.append(['S'+str(i),res,', '.join(x['mod'] for x in owners if x['mod']!='mod0000_MergedFiles'),'mod0000_MergedFiles (1)','Mergeable; existing merge preserves installed source changes; compile unverified'])
 conflicts+=table(['ID','Path','Source mods','Winner','Classification / result'],rows)
 purposes={
 'skellige_shops_and_craftsmen.w2phase':('Skellige shop/NPC community setup','UPR changes Kaer Muire blacksmith/Gwent timing; exact BIA node modification not mapped in available historical changelog.'),
 'cg_card_minigame_meta.w2phase':('Collect ’Em All / Gwent quest timing','UPR adjusts Gwent availability; historical BIA changelog prevents an automatically awarded Roach card starting the quest prematurely.'),
 'mq3035_wrap_up.w2phase':('Reason of State wrap-up','UPR revises Dijkstra/Philippa aftermath; historical BIA changelog fixes missing warehouse doors after the quest.'),
 'q103_daughter.w2phase':('Family Matters','UPR changes optional Return to Crookback Bog handoff; historical BIA changelog restores fisherman-family action points after quest completion.'),
 'q103_27_baron_final_talk.w2scene':('Baron final conversation','UPR optional quest/dialogue transition; historical BIA changelog fixes optional-choice highlighting after Uma interrupts.'),
 'q107_swamps.w2phase':('Return to Crookback Bog','UPR delays/hides activation while preserving a later join path; historical BIA fixes involve dialogue/action points across this quest, exact phase-node correspondence unverified.'),
 'q206_berserkers.w2phase':('King’s Gambit','UPR changes Crach Gwent timing after massacre; historical BIA optional-content sheet restores Birna/Svanrige gameplay conversation on arrival at Kaer Trolde.'),
 'q206_berserkers_attack.w2phase':('King’s Gambit attack sequence','UPR Gwent/quest state timing inferred from quest and author description; exact BIA change not isolated in available source evidence.')}
 conflicts+='''## Bundled quests/scenes — high preservation risk

All eight pairs have different decompressed SHA-256 hashes, including the equally sized q103 phase. Neither hash equality nor byte size proves semantic compatibility; both versions also differ from the current vanilla baseline. All currently prefer **BIA priority 6 over UPR priority 14**, so UPR's overlapping modifications are shadowed.

The UPR author states BIA compatibility and requires UPR to take priority. That supports a candidate order, but does not establish which BIA 4.0.3 changes are retained in the installed UPR resource. No verified installed merged binary patch was found. The BIA public detailed sheet is v3.0, so its purpose mapping is historical context, not an exact 4.0.3 graph diff. Paths mapped to UPR features below are explicitly inferences where an exact author file-to-node mapping is unavailable. [UPR author page](https://www.nexusmods.com/witcher3/mods/12988), [BIA author page](https://www.nexusmods.com/witcher3/mods/11260), [BIA detailed changelog](https://docs.google.com/spreadsheets/d/1f5MsivPkYdr8_KLTLG2u2E2Jzjc7Mhaaffc1KT0B9LE/edit).

'''
 qrows=[]
 for i,(res,owners) in enumerate((x for x in bundle.items() if Path(x[0]).suffix in ['.w2phase','.w2scene']),1):
  feature,purpose=purposes[Path(res).name];qrows.append(['Q'+str(i),res,feature,purpose,'Requires preservation verification / supported compatibility patch; conditional UPR-first proposal only'])
 conflicts+=table(['ID','Exact resource path','Affected quest/system','Purpose evidence','Status'],qrows)
 conflicts+='## Decompressed bundled hashes and sizes\n\n'
 for res,owners in bundle.items():
  conflicts+='### '+res+'\n\n'+table(['Owner','Bundle','Bytes','SHA-256'],[[x['mod'],str(Path(x['bundle']).relative_to(GAME)),x['extracted_size'],x['sha256']] for x in owners])
 conflicts+='''## H1 — Wolf HUD Flash resource

modBestGsSchoolStances (priority 29) wins over modSeamlessAdaptiveHUD (33) for gameplay/gui_new/swf/hud/hud_wolfstatbars.redswf. Bestg requires mcWolfsHead.BG2_SetStance to display the selected school stance. SAH requires its artwork timelines and clips for custom health/stamina/toxicity/sign/medallion presentation. Its loose wolfstatbars copy is byte-identical to its bundled copy, so it does not supply a combined variant. The independent hud_buffs resource does not resolve the wolfstatbars collision.

Giving SAH priority can lose Bestg's stance display/function; leaving Bestg first can lose SAH artwork/timeline behavior. Source checks establish different resource contracts, not a proven crash. This requires a combined Flash resource or an explicit feature trade-off. No verified compatibility patch was found in the installed payload or author material consulted. A supported Flash source/export pipeline and CR2W packaging are needed; extraction alone is insufficient. [Bestg author page](https://www.nexusmods.com/witcher3/mods/13595), [SAH author page](https://www.nexusmods.com/witcher3/mods/13194).

## English localization IDs

Grammar of the Path (5) currently wins all five repeated IDs over BIA (6) or UPR (14). The .w3strings indexes share the relevant English language key pair. Four differences alter text meaning/content; one is whitespace only.

'''
 lrows=[]
 descriptions={1092187:'BIA: “a sylvan”; Grammar: “Allgod”. Naming/content choice; cannot retain two replacements of one line.',1130095:'BIA: future threat “will be”; Grammar: present “is”. Editorial decision.',391138:'Grammar adds the preceding Fayrlund casualty sentence to BIA’s ambush line. Verify dialogue/audio/subtitle segmentation before choosing.',558403:'Only removes a space before a closing brace; harmless cosmetic overlap.',1063514:'Grammar hides UPR’s expanded Blood Ties letter. One-ID staged patch preserves the expansion and corrects four grammar/spacing issues.'}
 for x in read('english-string-overlaps.json'):lrows.append(['L'+str(x['sid']),', '.join(o['mod'] for o in x['owners']),descriptions[x['sid']],'Staged' if x['sid']==1063514 else ('Harmless' if x['sid']==558403 else 'Unresolved decision')])
 conflicts+=table(['ID','Owners','Difference / feature loss','Status'],lrows)
 conflicts+='''The remaining 18 language-key overlaps are the shared “Mods” menu-root key 0x4d5f8b0c, an intentional common label, not 18 independent functionality losses. No repeated string IDs were found outside the five English IDs among installed Mods/DLC localization indexes. Text decoding was performed for the overlapping English IDs, not every translated string.

strings.list is REDkit-generated JSON bookkeeping (file/string ID lists), not the .w3strings runtime text database. Its seven owners are listed with hashes above; the BloodAndSteel/sharedutils DLC copies are identical. Treat the Script Merger warning as harmless bookkeeping overlap, not a seven-way localization merge request. DLC's single strings.list winner is not established and is immaterial to runtime text. This interpretation is supported by its content and mod-developer guidance; do not delete it merely to hide warnings. [Developer guidance](https://www.nexusmods.com/witcher3/mods/7175?tab=posts).

## C1 — Combat speed / stance / animation behavior

Bestg, Combat Speed and BloodAndSteel modify combat animation/timing behavior. Bestg and Combat Speed share OnCombatActionStart, OnCombatActionEnd and SetIsCurrentlyDodging; Combat Speed replaces the last method while Bestg wraps it. Separate multipliers and resets can compose incorrectly even if compilation succeeds. Bestg's author discourages combining animation-speed overhauls. BloodAndSteel's relevant code is compiled-only here, so the full interaction cannot be patched reliably from available loose sources.

Classification: overlapping behavior requiring supported sources/compatibility patch or an explicit choice of intended behavior. This is one conflict family, not three additional file conflicts. It may cause timing, dodge, targeting or responsiveness defects; a crash was not demonstrated. Do not disable any mod or sacrifice animations automatically.

## Shared annotation targets — full matrix

23 target methods have multiple owners. An annotation collision alone is not a duplicate definition: wrappers generally call the chain and Sharedutils intentionally provides dependency methods. No pair of replaceMethod annotations targets the same method in the scanned loose source. No unrelated-file duplicate class/struct/enum was established; repeated vanilla declarations are covered by same-path winners.

'''
 arows=[]
 for target,owners in annotations.items():
  status='C1 speed/reset interaction' if target in ['CR4Player.OnCombatActionStart','CR4Player.OnCombatActionEnd','CR4Player.SetIsCurrentlyDodging'] else ('Intentional Sharedutils dependency / wrapper composition; runtime unverified' if any(x['op']=='addMethod' for x in owners) else 'Wrapper overlap; no proven source-level incompatibility; runtime chain unverified')
  if target=='CR4IngameMenu.ShowDeveloperMode':status='Better IGNI and Menu Fix both repair menu rows; redundant repair, idempotence needs UI testing'
  arows.append([target,'; '.join(x['mod']+': '+x['op']+' @ '+str(x['line']) for x in owners),status])
 conflicts+=table(['Target','Owners / annotation / source line','Assessment'],arows)
 conflicts+='''## Configuration, dependencies and operational findings (separate from 19)

O1, medium: Arrow Deflection is misdeployed; corrected layout staged, runtime validation pending.

O2, medium: manual Outfit Wheel has no mods.settings entry. Its existing merge is present and F3 OWToggle bindings exist, but relying on implicit order is avoidable. Explicit entry staged as a proposal.

O3, medium: empty Script Merger MergeInventory.xml does not track the five live merges. Rebuild provenance on a copy with current sources; do not regenerate live output blindly.

O4, high uncertainty: unowned vanilla content/metadata.store differs from Steam. Source and semantic correctness unresolved; not classified as a confirmed mod collision or repaired.

O5/O6, functionality: FriendlyHUD's sample input fragment contains 32 actions absent from live input.settings (2 sample actions are present); Hoods' ToggleArdHood action is absent. This means the documented custom shortcuts are not configured, even though scripts/menu resources exist. Sample IK_9 also conflicts between FriendlyHUD's item shortcut and Hoods' toggle; controller bindings may overlap. Defaults are examples, not permission to overwrite the user's controls. A binding plan requires selection of keys/context and checking every existing assignment. Missing saved FriendlyHUD preference keys may simply use script defaults and are not independently a fault. Evidence: input-action-check.json and input-fragment-check.json.

29 installed config XML files parse correctly. Vortex's merged input.xml retains all FriendlyHUD input Var attributes; duplicate Group id Hidden in input.xml/hidden.xml is a shared grouping, not an identified lost variable. Other mod menu groups have no cross-file repeated IDs. No new gameplay XML collision was found between mod bundles; Over9000 replaces vanilla abilities intentionally, and Weight is complementary.

FriendlyHUD and SAH both control HUD visibility/markers; Movement Tweaks and Responsive Movement both influence locomotion. Their source hooks can compose, but desired visual/feel behavior needs game testing. Monster Hunt/Sharedutils hooks are intentional dependency overlap. Existing DLC resources and caches need runtime mounting checks; no extra cross-mod bundled collision beyond the ten indexed paths was detected. Bundled references, precompiled blobs and native injection behavior have not been fully semantically decoded.

4542 distinct mod resource paths override vanilla assets; these are intentional replacements unless another installed mod replaces the same resource. This count is not added to functional conflicts. See evidence/vanilla-mod-overrides.json and vanilla-collision-baselines.json for exact resources/current baselines.
'''
 write('conflicts.md',conflicts)

 resolutions='''# Proposed resolutions — review required

No live installation changes are authorized by this audit's first-pass scope. All payloads are private local review artifacts. Six file/text conflict units are covered: five existing script merges plus one newly staged English localization merge. One additional installation correction is staged. Twelve confirmed conflicts plus one combat overlap remain unresolved; eight have a conditional priority proposal, which is not a merged quest patch.

## Safe/reversible review packages

S1–S5: retain current mod0000_MergedFiles. The 13 installed source contributions were replayed using current Steam-verified vanilla in three-way merges; every result was conflict-free and identical to the current merged text after line-ending normalization. Reference copies are under patches/verified-existing-merges. They are not new replacements and need not be deployed. Function signatures/imports remain as in the current merged files; compiler validation is still required.

L1063514: patches/localization/Mods/mod0000_AuditCompat/content/en.w3strings contains only the Blood Ties letter ID. It preserves UPR's full added paragraph while fixing “born” to “borne”, joining clauses with “but”, removing a double space and correcting “as a I write”. It has no localization key records or other IDs. Author helper write/read roundtrip passed. Preview: patches/localization/letter-before-after.md. Put this small patch ahead of Grammar and UPR, below the existing merge; English only. Readability and runtime string winner must be checked after separately approved deployment.

O1: patches/arrow-deflection-layout contains the existing script, 18 translations and the existing menu XML at the correct archive root. Content is copied without alteration and without Vortex markers. Import/reinstall through Vortex with a corrected installer topology; do not edit the current hardlinks or create two active copies. The existing wrong-root payload is inert and must not be purged during this review. After deployment approval, retain its files until the Vortex-managed replacement and rollback path are verified.

O2: make Outfit Wheel explicitly enabled in the approved Vortex/persistent priority scheme. The complete candidate is patches/load-order/mods.settings.proposed, but it also contains the conditional quest reordering; do not install it wholesale as a “safe-only” change.

## Quest resources Q1–Q8

Minimum candidate: UPR before BIA, as UPR's author instructs. This restores UPR's overlapping behavior but may hide BIA changes if UPR's resource does not incorporate the installed BIA version. It is **not independently verified to preserve all features**. The staged load-order file is clearly labelled conditional and must not be deployed until reviewed.

For a feature-preserving resource patch: obtain compatible original mod source/quest graphs for the installed versions; export both plus current 5.0 vanilla through supported REDkit resource tooling; compare changed nodes/links, facts, conditions, action points and scene choice transitions; combine independent changes; validate reference dependencies and recook a dedicated small patch bundle. Test the exact quest paths on disposable test saves after approval. Where nodes implement contradictory quest design, present the exact mutually exclusive behavior for user choice. Current tooling cannot supply that graph diff; no fabricated binary patch is included.

Known gaps: exact BIA shop and q206 attack changes; exact mapping of q107 phase changes; whether UPR incorporates BIA 4.0.3. Historical author documentation helps identify risk but cannot close these gaps. Priority alone is acceptable only if incorporation or an explicitly accepted loss is proven.

## HUD H1

Use supported Flash source tooling to retain SAH artwork clips/timelines and transplant Bestg's mcWolfsHead.BG2_SetStance contract into a single resource, then export/package it with a compatible REDkit pipeline. Keep both script implementations. Validate all SAH styles, health/stamina/toxicity/sign states, stance updates, Ciri, save/reload and recreated HUDs. No source FLA or verified existing combined resource was available. Giving either original resource priority loses the other's resource-level changes; stop for an explicit decision if source integration is unavailable.

## Remaining localization and combat

L1092187/L1130095/L391138: choose the intended noun, tense and dialogue segmentation using voice/dialogue context, then extend the one-ID patch only for approved text. Do not duplicate both strings under one ID or silently prefer an editorial version. L558403 is cosmetic and can remain Grammar-first.

C1: obtain BloodAndSteel's matching compiled source or author compatibility guidance and unify speed multiplier ownership/reset semantics with Bestg/Combat Speed. Until that is possible, no automatic removal or speed-disabling settings are applied. Current test-build notes increase uncertainty. Any “choose one speed controller” approach requires user acceptance of the precise feature loss.

O4: identify why metadata.store was regenerated/modified (existing logs/stamp/tool history), then use a supported metadata rebuild or verified restore only if justified and separately approved. Steam verification would also affect managed input.xml, so blind repair is inappropriate.

O5/O6: retain current input.settings; propose unused context-specific bindings for the missing FriendlyHUD and Hoods actions, with collision checks. Binding the two defaults to IK_9 would discard one intended action. No mass import of sample controls/preferences is staged.

## Review and deployment sequence

1. Review conflicts.md, the proposed letter, and this file. Approve individual packages and explicitly state whether deployment and subsequent game launch/test are permitted; these are separate approvals.
2. Before live deployment, rerun tools/validate-review.py, inspect Vortex profile/order and make fresh independent backups of the original Arrow package, controls, deployment manifests and affected Vortex metadata. Stop if hashes differ from the audited baseline.
3. Import the approved tiny localization package through Vortex. Correct Arrow's package root using Vortex's installer/reinstall workflow or a separately named corrected local package with the original package disabled only after explicit approval; preserve the original package for rollback. Require Mods/modArrowParryManual to exist and share identity with its corrected managed source.
4. Set only approved priority relationships in Vortex and persist them. Keep the current quest ordering unless the conditional UPR-first change has explicit preservation evidence or an accepted trade-off. Do not blindly copy the whole candidate mods.settings because Vortex rewrites it and it includes unresolved choices.
5. Deploy only approved changes through Vortex. Recheck deployment identity, actual mods.settings, new string IDs/resource winners and compiler result. Do not regenerate the five current merges without reviewing a copy first.
6. Launch only with separate permission. Test combat/dodge, both HUDs, Outfit Wheel F3, Arrow timing, Hoods/FriendlyHUD shortcuts and quest cases listed in validation.md. No save edits; use disposable test saves or independent copies, never overwrite a sole existing save.

Approval of the staged localization/Arrow packages does not approve binary quest/HUD edits, disabling combat mods, control reassignment, Steam repair or a game launch.
'''
 write('resolutions.md',resolutions)

 order='''# Load order and actual overwrite rules

## Evidence

Lower numeric Priority wins for explicitly configured Mods. This was checked against the installed Vortex Witcher plugin (ascending numbers, merged output locked at the top), primary Script Merger source (LoadOrderComparer ascending priority; explicitly configured enabled candidates preferred), and the CDPR-forum-hosted mods.settings guide. Default unset order is case-insensitive alphanumeric according to these tools; the current 5.0 engine was not launched to empirically verify unspecified/default/DLC precedence. [Script Merger source](https://github.com/IDCs/WitcherScriptMerger), [mods.settings guide](https://forums.cdprojektred.com/index.php?attachments/mods_settings-pdf.6711517/).

Priority chooses a complete resource, not a union of its changes. Annotation wrappers generally compose around a target; replacing methods and compiled script integration need semantic checks, not merely sorting folder names. DLC folders are excluded from Vortex's mods.settings generation, so assigning a DLC entry is not a verified DLC conflict solution.

## Current explicit order

All 35 recorded sections are enabled with unique priorities. Outfit Wheel is absent; Arrow's enabled entry names a folder outside the Mods search path. Local mod loading is enabled in dx12user.settings.

'''
 order+=table(['Priority','Section','Effective note'],[[v['priority'],k,'Absent runtime Mods folder' if k=='modArrowParryManual' else 'Enabled'] for k,v in sorted(settings.items(),key=lambda kv:int(kv[1]['priority']))])
 order+='''## Required relationships and review candidate

mod0000_MergedFiles stays ahead of all five same-path script sources. The staged tiny AuditCompat localization patch must precede Grammar/UPR for ID 1063514. Outfit Wheel should have an explicit enabled entry; its same-path script additions already occur in merged output. Correct Arrow's layout before its priority can have an effect.

Current BIA(6) > UPR(14) hides eight UPR resources. Candidate UPR > BIA follows author guidance but has an unresolved BIA preservation gate. The full candidate renumbers all entries uniquely, keeps the existing merge first, inserts AuditCompat second, places UPR directly ahead of BIA and appends explicit Outfit Wheel. It is not approved for deployment.

Current Bestg(29) > SAH(33) selects Bestg's wolfstatbars resource. Reversing these numbers exchanges the feature loss; there is no order that retains two distinct replacements of one resource. A combined supported resource is needed for both.

Current Grammar(5) > BIA(6)/UPR(14) controls five English IDs. The tiny patch changes one winner intentionally; the other four remain unchanged, including one cosmetic overlap. BIA/UPR reordering does not solve their separate Grammar overlaps.

The existing Vortex-generated input.xml is the winner for PC controls and matches its staging hardlink. All FriendlyHUD XML Var records are retained. Other config files have independent paths/groups. Do not overwrite this managed merged file from a mod archive.

No duplicate numeric priorities were found. Existing Sharedutils/BIA dependency hooks must remain available; priority changes must not remove dependency payloads or replace script merges with partial sources. No active compatibility patch was found whose resource winner would become redundant through the safe staged one-ID localization change.

Revalidate actual deployed mods.settings after every Vortex deployment. Vortex rewrites the file from its order; a manual one-time edit is not persistent ownership-safe configuration. The candidate is a review diff, not a standalone deployment mechanism.
'''
 write('load-order.md',order)

 validation='''# Validation results and limits

## Passed static/non-destructive checks

All 30 mod bundles indexed without format/offset errors (both legacy 0x140 and remastered 0x130 entry layouts). Thirty-one vanilla bundles indexed, 365,866 entries, with no parser errors. QuickBMS bounded extraction succeeded for the ten colliding resource paths across nine owners and thirteen relevant baseline/XML extractions. Extracted sizes equal table sizes; actual decompressed SHA-256 is recorded rather than treating compressed bytes/header hashes as content equality.

Installed Steam depot manifests were decoded and 1,926 official files checked: 1,904 hashes match, 20 zero-length tombstone/placeholder files match the expected empty/no-content-hash form, 2 differ. No installed-depot manifest was missing. About 69.76 GB was read; no game file was repaired. All vanilla scripts used in merges and game executables match the installed cached manifest. This verifies local installed-version consistency; it is not a fresh Steam server authenticity check.

Thirteen source-contribution three-way checks across five merged scripts exited 0 and made no change to the normalized current merged output. This establishes source-change inclusion against the current baseline; it is not a full semantic proof or a compiler pass. No new unrelated duplicate type or paired replacement of the same target was identified in scanned loose sources.

All 229 installed .w3strings index structures parse; overlapping English IDs were decoded with the installed author helper. The one-ID English patch roundtrips exactly, contains only ID 1063514 and no keys, and retains UPR's expansion. The Arrow layout adds no string-ID or named script-symbol overlap with scanned installed loose sources. It shares only the intentional “Mods” root localization key in translated languages. New patch paths do not replace existing runtime Mods files: 20 projected files in the Arrow/localization packages, including one intended existing-ID localization override. Arrow's menu XML already exists and is unchanged.

Twenty-nine config XMLs parse. Every FriendlyHUD input Var attribute record survives the Vortex input.xml merge. Missing custom shortcut actions are documented in conflicts.md rather than importing conflicting defaults.

All 644 deployment records are present hardlinks to corresponding staging sources. Final validation rehashed 1,148 installed mod/other/control files and found no content changes; all 29 staged review files match patch-manifest.json and proposed priorities are unique. Exact results: evidence/review-validation.json. Full extra-file inventory is evidence/all-extra-game-files.json.

## Compiler/resource tooling limitation

An isolated copy of REDkit wcc/DLLs was run with private config/tool data. Initial missing-config diagnostics were corrected only in the audit workspace. Initialization then failed with an access violation (0xC0000005) and missing depot/resource/language/sound inputs. An earlier hung audit-owned wcc process was stopped. The installed game and REDkit files were not used as write targets; no depot was generated.

No supported script compilation, quest graph export/recompile or combined redswf generation succeeded. QuickBMS extraction is not semantic merging. Legacy tools are not assumed capable of correctly compiling remastered annotations. Binary caches/precompiled scripts and native DLL combinations remain runtime/semantic uncertainties.

The modern Script Merger UI was not launched for a rescan: it could write state or operate on the live path. The independent bundle, loose-script, annotation, localization, XML, Steam-baseline and staged-path scans supply broader static coverage. A later copied-workspace Script Merger scan can supplement these results but cannot close binary compatibility gaps.

## Audit write boundary

Reports, extracted resources, baseline copies, tool copies, repaired database copy and proposed patches were written only under this audit folder. Loading the installed SAH Python helper initially created one __pycache__/w3s.cpython-314.pyc file beside that helper. Only that audit-generated cache and its empty directory were removed; bytecode writes are disabled in the staging tool now. No mod content or managed payload was changed. No launch/deployment/save edit occurred.

## Required tests after separate approval

1. Compiler/startup: validate current 5.0 scripts and compiled blob integration with supported tooling; verify expected signatures and wrapper chains. Stop on errors, do not work around them by discarding mods.
2. Quest graphs: compare current vanilla/BIA/UPR graph nodes and scene transitions before accepting priority. Test Family Matters/Baron optional quest handoff, delayed Return to Crookback Bog activation and later joining; Reason of State conclusion/warehouse doors/Dijkstra aftermath; King’s Gambit massacre/attack, Crach Gwent timing and Birna/Svanrige conversation; Kaer Muire blacksmith shop/Gwent cooldown; Collect ’Em All/Lambert/Baron/Crach card timing. Test both intended optional paths, save/reload and leaving/returning to the area. Historical purpose mapping is not sufficient to predict all failures.
3. HUD: SAH artwork styles and transitions, health/stamina/toxicity/sign/medallion, Bestg stance display, Ciri, HUD recreation, saving/loading, marker/quest visibility with FriendlyHUD/Monster Hunt.
4. Combat: speed multipliers start/end, dodges, lunge/targeting, heavy attacks, HitLag damage feedback and Evils AI with BloodAndSteel/Bestg/Combat Speed. Require matching compiled sources where needed.
5. Controls: existing F3 Outfit Wheel behavior; Arrow tap/hold/no-block timing; Hoods toggle and approved FriendlyHUD hotkeys in every configured context. Preserve current controls.
6. Localization: expanded Blood Ties letter and remaining BIA/Grammar dialogue IDs aligned with voices and scene segmentation; verify applicable language behavior.
7. Integrity: determine metadata.store origin and supported lifecycle before restoration/rebuild; monitor new compiler/resource errors after any approved deployment.

## Play safety

**The installation cannot be certified mutually compatible or safe for progression from these results.** Eight quest resources currently shadow UPR changes; preservation after reversal is unverified. HUD artwork contracts conflict; combat speed behavior overlaps; metadata.store differs without known provenance. These establish feature-loss and compatibility risks, not proof that a quest is presently broken or that the game will crash. Do not call warning disappearance a successful fix. Until the unresolved gates are closed, continuing important quest progression is not recommended as a validated outcome.
'''
 write('validation.md',validation)

 rollback='''# Rollback and baseline guards

No deployment occurred, so there is currently nothing to roll back. Do not copy backup files into the live installation during review. The following procedures apply only to individually approved later changes.

## Before approved deployment

Run `python tools/validate-review.py` from this audit folder and require changed_live_files and patch_hash_failures to be empty. If the machine/mods were changed since this audit, refresh inventory and decisions rather than using stale rollback material. Preserve fresh independent copies of mods.settings, input.settings, dx12user.settings, MergeInventory.xml, deployment manifests, the original Arrow package/archive and the Vortex profile's order/enabled state. Capture new deployment hashes and ownership. Copies must not be hardlinks.

Existing control backups, live absolute paths and SHA-256 are in evidence/control-snapshot.json; independent copies are in private/control-snapshot. All proposed payload paths/hashes are in evidence/patch-manifest.json. All original deployed/staged source mappings are in evidence/all-deployment-link-check.json. The partial repaired Vortex DB copy is **evidence only, never a restore image**; do not replace Vortex's state.v2 with it.

## Individual change rollback

Localization patch: disable only the newly installed AuditCompat package in Vortex and redeploy. Verify its single en.w3strings no longer mounts and Grammar again wins ID 1063514. Keep the audit patch/source for review. Do not delete a shared managed deployed hardlink manually.

Arrow layout correction: disable only the new corrected package, restore the original package's enabled state/order through Vortex and redeploy. If reinstalling the original package in place was chosen, use the saved original archive and the original installer topology. Verify original managed source/destination hashes and that the earlier game/ArrowParryManual payload is restored. This intentionally restores the prior inactive behavior. No purge or bulk deletion is needed.

Priority/Outfit Wheel entry: restore the exact original Vortex order/profile enablement, redeploy, and compare mods.settings against private/control-snapshot/0-mods.settings (listed hash in control-snapshot.json). If Vortex rewrites priorities, fix its persistent order rather than copying a live file it immediately overwrites. The conditional UPR-first order has no approval now; if later deployed and rolled back, restore BIA 6 before UPR 14 with the rest of the original order.

Existing script references: these were not newly installed. If later merge regeneration is approved, preserve independent copies of all five live files and MergeInventory.xml first. Restore those exact files using the approved ownership method (the current merge folder is unowned/manual), then restore the provenance file only if its baseline still applies. The review copies under patches/verified-existing-merges and their original hashes are in installed-files.json. Do not overwrite Vortex-managed source mods to undo generated merges.

Controls: no control edits are staged. If later approved, back up each control file immediately before editing and record a per-key diff. Restore only the approved changed keys if other user changes occurred; full snapshot restore is safe only when no intervening edits occurred. Do not force-import FriendlyHUD/Hoods example bindings.

Binary quest/HUD/metadata modifications: none exist in patches; no binary rollback is needed. A future supported patch should be a separate managed package with exact bundle hashes and explicit disable/redeploy rollback, not overwritten mod originals. Vanilla metadata repair requires its own pre-change backup and supported restore workflow; no automatic Steam verification/repair is authorized here.

After rollback rerun inventory/conflict checks, verify actual overwrite winners and controls, and compare managed files to their sources. A rollback may restore the known prior conflict state; it does not establish compatibility. Saves and game binaries are never changed by these proposals.
'''
 write('rollback.md',rollback)
 write('patches/README.md','''# Private review packages

- verified-existing-merges: five current merge reference copies; no new deployment needed.
- localization: one English Blood Ties letter ID, preserving expansion and grammar; new staged patch.
- arrow-deflection-layout: unchanged Arrow gameplay payload/menu with corrected install topology.
- load-order: conditional full-order proposal/diff; includes unresolved UPR/BIA choice, do not deploy wholesale.
- installable/localization.zip and installable/arrow-deflection-layout.zip: Vortex-importable review archives; check the installer preview places Mods and bin directly under the game root. CRC checks and SHA-256 are in ../evidence/installable-package-validation.json.

No quest/scene/HUD merged binary is supplied. See ../resolutions.md for supported patch design and deployment gates. All assets are private local material; do not publish this folder or whole third-party mods.
''')
 write('README.md','''# Witcher mod audit — review checkpoint

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
''')
 print('Wrote six reports, review README and patch README')
if __name__=='__main__':main()
