# 57 — Sparse musical-material selection and private auditions

2026-10-16. Implements report56's material-selection task. **No subjective listening by Codex is claimed.** These are structurally supported audition prospects, not approved musical choices. No scheduler, trigger, Wwise session, bank generation, game/Vortex/save change or release integration was performed.

## Start listening

Open this file in Chrome or Edge:

`C:\Dev\witcher-music-control\build\music-material-selection\audition-v3\index.html`

It contains **21 playable full-source previews**, with **S01–S07 first** (about10minutes total); the complete list is about43.7minutes. Audio payloads total54,901,317bytes, approximately52.4MiB. There is no installer, server, network dependency or automatic playback. Start at a comfortable volume: the sources are not loudness-normalized.

Each card provides beginning/middle/ending jumps, additional measured low-energy inspection points, source identification, risks, a Keep/Maybe/Reject choice, provisional musical function and notes. Export the decisions as JSON before closing. Browser local storage is attempted but is not the only way to retain decisions. `auditions.m3u8` is the ordered local-player fallback; `auditions.csv` and `auditions.json` contain detailed mappings. Early native pre-roll can include a few seconds of silence. Full-source clocks can differ from native segment clocks: do not interpret a seek button as a proposed musical edit.

The page and all21 linked media files were structurally checked; every preview decoded using trusted local FFmpeg. **Browser interaction and subjective playback were not tested here.** If the app opens HTML as text, open the same file in the normal browser. The page plays only one audio element at a time.

## A. Library inventory and authority

Exact local input aliases:

- **W** = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`.
- **N** = `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc`.
- **A** = `C:\Dev\witcher-music-control\build\music-plus-audit`.
- **J** = `A\main\mods\modMusicPlus\editor\index.json`.
- **P** = `A\pack\mods\modMusicPlus\content\soundspc.cache`.
- **O** = `C:\Dev\witcher-music-control\build\music-material-selection`.

Report53's actual main3.3.0 / pack3.2.0 archives and extraction are reused. No archive reacquisition, full MP architecture reinvestigation or bundled executable is needed. Editor source/title labels are **Music Plus metadata**, not independently authenticated original-game credits or proof of narrative purpose. Native descriptive titles below are working labels, not official soundtrack album titles.

| Pool | Observed inventory | Limit |
| --- | --- | --- |
| Eight native regional banks |1,943 segment records;2,558 unique music-track IDs;857 media IDs mapped to856 original source paths; zero music/track decode failures | These are not1,943 compositions. Segments, sources and stems are extensively reused. Source paths are authoring joins, not proof every file was auditioned. |
| Already reviewed generic native paths |97 segment records, including37 known silent segment records |60 non-silent segment records remain before deduplication/arrangement review; approved attenuation does not prove artistic suitability for Sparse. |
| MP added pack |275 distinct media payloads, no byte-identical payload duplicates; all275 support the inspected stereo/mono Wwise Opus framing | Only the selected10 were fully audio-decoded/measured here; format/framing support is not a claim of listening to275 recordings. |
| MP music joins |271 added recordings joined through1,996 editor assignment rows to actual bank segments/tracks/media; no failed joins | One representative segment per track/assignment is checked, not every scheduler clone. |
| MP remaining4 |Diegetic-only editor entries retained in inventory |Their Sound/Action graphs were not forced into the MusicTrack decoder; none is selected. |

MP metadata source counts: The Witcher2=61, Nyghtfall=61, The Witcher=60, GWENT=56, Thronebreaker=21, GWENT: Rogue Mage=8, The Witcher: Monster Slayer=3, Songs to Play Skyrim to=3, label“Vanilla”=1, The WitcherIV=1. These labels describe the pack, not all material used by Music Plus, and do not establish reuse permission.

Reproducible tools: `tools/music_material_catalog.py`, `native_catalog` and `mp_catalog`. Native joins use `W\Interactive Music Hierarchy\music.wwu`, actual `N\<bank>.bnk` segment children, decoded track clips/source IDs and AudioFileSource/MediaIDList entries. Native eligibility is pinned to existing reviewed static-target ancestry in the D/NML/Skellige/Kaer Morhen/Toussaint manifests. MP joins use **J** `/playlists/<playlist_index>/tracks/<track_index>`, representative `/pools/*/i` segment references and `A\banks\<bank>.bnk`; decoder-derived source IDs must equal the editor WEM IDs. Protected/native dedicated-authored reuse is checked separately, not inferred from names.

Full local inventory: `O\catalog-v3.json`. [Sanitized candidate identities, markers, clip layouts, assignment indices, hashes and measurements](57-music-material-evidence.json) retain the important joins without audio or third-party implementation. [Selection specification](57-music-material-shortlist.json) records provisional functions, risks and listening questions.

## B. Actual audio inspection and decoding

Trusted installed binary: `L:\Programs\Shutter Encoder 20.1 Windows 64bits\Library\ffmpeg.exe`; version/hash and commands are recorded in `O\audition-v3\provenance.json`. No MP-supplied executable, DLL, editor, BAT or server ran. No new decoder software was installed.

Direct FFmpeg probing identifies the pack's Wwise codec0x3041 but cannot directly decode its custom wrapper. `tools/music_material_opus.py` independently validates the complete RIFF, supported mapping, seek-table packet sizes, frame-derived duration and end trim, then writes standard Ogg pages around **unchanged Opus packets**. Independent readback verifies page CRC/sequence/granules and every compressed packet for all10 selected additions. FFmpeg decoding then agrees with the declared Wwise sample count within one8kHz analysis sample. This is a private preview conversion; no original WEM or game header changes.

Format authority: [vgmstream's Wwise OPUSWW implementation](https://github.com/vgmstream/vgmstream/blob/master/src/meta/wwise.c) was read as a format reference, not executed or incorporated. It identifies the packet-size table, sample count and pre-skip fields. The standard container and packet timing are defined by [RFC7845](https://www.rfc-editor.org/rfc/rfc7845) and [RFC6716](https://www.rfc-editor.org/rfc/rfc6716). Retrieved reference text remains ignored, with no MP code copied into WMC.

Native previews are full original sources encoded privately to browser-playable Opus160kbps, with no trims, fades, new mix or normalization. The source originals remain byte-identical. Some are the **unconditional base stem**, not the full layered in-game arrangement. Optional threat-dependent stems are explicitly listed in candidate metadata. Their omission is an audition distinction, not an approved arrangement change.

Measurements use decoded8kHz **stereo** PCM:100ms RMS envelopes, percentile envelope range, first/last-second levels, quiet intervals below−60dBFS for at least0.5s and separated low-energy inspection points. They do not provide LUFS, full-band true peak, perceived restraint, harmony, instrumentation or cadence judgments. Stereo is retained to avoid falsely measuring cancellation from mono downmix. A quiet tail is not proof of a musically complete ending; a low-energy point is not an authorized cut. Full-band private playback previews remain available for listening.

Early catalog controls are preserved: first-pool-only joins missed459 alternate assignments, fixed by selecting representative segments across pools. An overly strict final RIFF pad assumption rejected122 original WEMs; bounded acceptance of the observed unpadded final odd chunk resolves this without ignoring size/packet errors. Final catalog has zero failed music joins and275 supported packet-framing inspections. These corrections do not change production WMC decoders.

## C. Ranked shortlist and proposed musical functions

**Order is provisional structural audition priority, not a claim that Codex has heard the best music.** All proposed ranges below are on the **native segment clock**, whereas preview duration is the complete **source-file clock**. For additions, audition the complete recording unless listening establishes a better independent section. No arbitrary short excerpts were created.

In the ID column, `seg/track/media` identifies the exact native bank path; `wem` identifies the exact pack entry. Native relative filenames, MP representative segment/track IDs and all hashes are in the evidence companion and player details.

| ID | Material / metadata source | Full preview | Exact identity | Structural prospect and proposed boundary | Main uncertainty / adaptation |
| --- | --- | ---: | --- | --- | --- |
| **S01** |Wetland introduction — W3 native base |36.00s|NML654694005/810457805/116649543|Brief punctuation prospect: entry0, exit32, tail to36. Last1s approximately−85dBFS.|Original playlist517264825 proceeds into loop58342400. A fading intro may still lack an independent cadence; listen before retaining it alone.|
| **S02** |City A — W3 native base |49.83s|NML546171631/414481579/187661077|Short native section: entry2, exit48, end49.835. Last1s approximately−83dBFS.|Two optional native layers omitted. Potential unchanged base-source use requires an arrangement decision.|
| **S03** |In Temeria — The Witcher2 |72.52s|wem903823503|One complete source and bounded MP segment; compare regional identity versus brief punctuation.|Prior-game association and perceived dramatic weight unresolved. Full ending falls sharply; judge the actual resolution.|
| **S04** |Island A — W3 native base |60.76s|Skellige263850977/535110851/311392293|Native section entry3.2, exit54.4, segment end57.6. Quiet source tail.|Raw pre-entry/clip trim shifts its clock; two optional layers exist. No speculative marker-to-file trim.|
| **S05** |Dialogue – Neutral — The Witcher |64.16s|wem988417140|Complete source offers a contrasting bounded phrase-scale audition.|Original dialogue assignment does not establish generic safety or a self-contained musical ending.|
| **S06** |Southern night — W3 native full arrangement |124.00s|Toussaint744648631/832016950/811969310|Internal native markers0/32/64/104, exit122, tail to124. Compare entire piece and those existing sections.|Section markers do not prove independently resolving gestures. Whole source may work unchanged; sections require listening.|
| **S07** |Nightfall — Nyghtfall |191.82s|wem948095561|Longer atmospheric-development comparison; measured quiet interval148.8–157.9s within the recording.|Could contain separable episodes, a compositional pause or editing; no subjective determination. Do not automatically remove the gap.|
| S08 |City B — W3 native base |71.68s|NML779346151/305533596/731825264|Distinct B section: entry2.791, exit69.767, segment72.363; compare its ending to A.|Source is shorter than segment; other layers and related sections exist. Base-alone completeness unproven.|
| S09 |Dol Blathanna – Forest — The Witcher2 |92.58s|wem945387783|One bounded regional composition; full source audition.|**Ending hold:** final short RMS window rises to approximately−22dBFS after a roughly−36dBFS tail. Could be a source transient, edit or decoding artifact; listening and, if necessary, a second trusted decoder are required. Thematic association also unresolved.|
| S10 |City neighbourhood B — W3 native base |58.03s|NML715369076/816243834/798158466|Entry2, exit58; another existing short section with a quiet source end.|Loop/cadence and omitted-layer dependency need confirmation; exit nearly coincides with end.|
| S11 |A Quiet Corner — The Witcher2 |194.89s|wem940375184|Long situation-specific comparison, with a measured falling tail.|Name does not establish quietness. Judge whether its development earns3.25minutes; source context unverified.|
| S12 |Island B — W3 native base |73.05s|Skellige175437664/312812702/886014434|Existing exit65.455, segment69.409 and tail; contrasting resolution/section prospect.|Pre-entry trim and base-only arrangement. Leading quiet source portion is about5.4s.|
| S13 |Map Theme3 — The Witcher: Monster Slayer |183.56s|wem986128669|Different original functional pool; complete rendered source with a strongly diminishing endpoint.|Map music is not automatically suitable for traversal. Full recording and rights/context require review.|
| S14 |Reusable ambient01 — W3 native |132.00s|Skellige877863662/165976335/219787535|Single-track native arrangement with exit128 and4s tail; useful restrained-texture **comparison**, not an approved generic choice.|**Restricted:** actual media reuse in8 dedicated-authored segment/track paths. Do not casually repurpose this material.|
| S15 |What Lies Ahead — GWENT: Rogue Mage |189.84s|wem924004613|One complete rendered source with a declining end; longer intentional-presence comparison.|Neither title nor MP assignment proves restraint or original narrative independence.|
| S16 |Southern ambient01 — W3 native |133.33s|Toussaint626459345/374771226/265936293|Entry4.948, exit123.711; substantial native ending region. Single arrangement, no optional intensity tracks in this segment.|Good tail is measurable; satisfactory musical resolution is not. Whole-source audition first.|
| S17 |Untitled #026 — GWENT |104.82s|wem991195799|Separately identified bounded recording, for identity contrast rather than another native stem variation.|Original title, thematic role and context unknown. No inferred emotional classification.|
| S18 |Island alternate pads arrangement — W3 native |157.01s|Skellige421373096/706524924/755958339|Native single-track alternate arrangement, entry0.667 / exit152.667; compare against more layered choices.|“Pads” is an authoring label, not proof of unobtrusiveness. Raw file and155.013s segment differ.|
| S19 |Distant Memories — Nyghtfall |183.81s|wem997260822|Independent second recording to compare temporal/dynamic shape against S07; full source.|Measured10–90% envelope range is only about6.2dB, unlike S07's28.8dB; that does not decide musical quality or intensity.|
| S20 |City night — W3 native |144.00s|NML894778287/1020785585/841561382|Complete native single-track night arrangement, exit140.8 and tail.|May still feel like wallpaper despite a suitable endpoint; needs human judgment of full duration.|
| S21 |Peaceful Moments — The Witcher |306.54s|wem932143796|Deliberately long contrast, with low raw RMS and fading endpoint. Tests whether a complete evolving piece can justify occasional extended presence.|Title/raw mastering level do not establish restraint. Longest candidate is a comparison, not a proposed routine cue.|

The11 native choices use11 distinct original-source hashes;10 additions use10 distinct pack payloads. The list does not pad itself with repeated encodings of one source. Some native sources are **stems** or alternate arrangements; labeling them as21 independent complete compositions would be incorrect.

## D. What the pools offer — and do not yet prove

**Native material is presently the stronger technical starting point for short presentation.** Existing36–73second introductions/A/B sections, native entries/exits, tails, optional layers and at least one sectioned124second arrangement are more useful starting evidence than arbitrarily cutting the140second prototype. Their original traversal consumer policies are already reviewed. This does **not** establish that base stems alone sound complete, or that an intro finishes convincingly without its loop.

**Music Plus broadens the audition vocabulary.** Its additions are actual complete renderings with much better display labels and different source-game identities, including mid-length and longer pieces. They are not necessarily short gestures, dynamically adaptive compositions or emotionally restrained. Most carry simple full-duration MP boundaries rather than native interior cue metadata. Original narrative significance and underlying recording rights are less firmly established here than native Wwise routing. S07's measurable internal quiet interval is worth hearing; it is not a demonstrated musical punctuation system by itself.

**Provisional strategy: audition a mixture, retain native material as the lowest-integration-risk starting pool.** There is enough structurally varied material for a useful listening decision now. There is not yet evidence that it all supports the desired experience, or that MP is artistically better. No conclusion that bespoke rearrangement is necessary follows from duration alone. If only base stems or loop introductions pass, later arrangement work may be needed; do not begin that before hearing which endings and entrances actually work.

The native catalog contains many short authored/transition records too. They were not indiscriminately promoted into exploration candidates to satisfy a duration goal. Existing combat endings and important authored scoring retain their original role. S14's actual authored reuse is specifically quarantined as a comparison, and prior-game titles/context remain unresolved rather than declared safe.

## E. Verification, reproducibility and listening decision

`tools/music_material_audition.py`, `choose`, `metrics`, `build` and `page` produce the private player, original-source/segment joins, packet readback, duration checks and measurements. The builder rejects reference/MP executable paths, unknown layered MP selections, ambiguous native source mappings, missing reviewed native ancestry, selected MP segment/media mismatches and changed catalog input fingerprints. Native source paths stay beneath Originals/SFX. Output must be a fresh ignored build directory; all original inputs are hashed before/after use.

To reproduce, run `music_material_catalog.py --source <W> --banks <N> --audit <A> --output <fresh ignored catalog.json>`, then `music_material_audition.py --catalog <catalog> --selection research/57-music-material-shortlist.json --source <W> --audit <A> --ffmpeg <trusted installed binary> --output <fresh ignored audition folder>`. Both are local inspection/conversion helpers, not WMC gameplay implementation. Existing `music_comparison_decode.py` and cache/bank readers are reused unchanged.

All179 repository tests pass, including prior regional regressions and new positive/negative container, packet/granule/checksum, unknown/truncated format, source eligibility/ambiguity and HTML escaping/control tests. Final preview hashes,10 packet readbacks,11 unchanged originals, exact native source, index links and zero external resources are recorded in `O\audition-v3\verification.json` and the sanitized evidence companion. Browser playback/export ergonomics remain untested, distinct from successful decoder validation. Historical failed padding/join controls remain ignored evidence, not passing output. All11 selected native originals are independently probed as stereo. Ten retained release/native artifact hashes, including native Init and accepted banks/archives, match their prior evidence; see O\preservation.json. No original or converted audio, bank, MP source code or private binary is committed.

**Human decisions needed:** whether each entrance feels justified after silence; whether its ending resolves rather than merely fading; whether the base stem feels incomplete; whether the full duration earns its space; whether a recognizably authored theme should remain reserved; and which provisional role, if any, fits. RMS, markers, titles and source reputation cannot answer those questions.

**Smallest follow-up:** listen to S01–S07, mark Keep/Maybe/Reject and note the best ending/role. Export those decisions. Then narrow to3–5 selections and, only if needed, audition their missing native layers or original-context associations. Do not resume scheduler/re-entry or trigger implementation yet. MP recording incorporation would additionally need a separate underlying-rights/permission review; this private audition authorizes no distribution or playable integration.
