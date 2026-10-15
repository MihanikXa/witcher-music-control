# Batch native banks and playback — 2026-10-15

**Result:** Kaer Morhen and Toussaint pass independent pristine/native baseline, exact decoded candidate, source restoration, media and global-dependency checks. Representative Wwise playback passes within the explicit bounds below. Three unchanged regions also receive paired preservation controls. No retail game was launched; authoring playback is not retail compatibility evidence.

Source policy, exact edited identities and intentionally native regions are in report48. Evidence root `P=build/full-game-v4`; original source/native banks are the installed REDkit paths defined in reports45/48. All binaries, licensed projects, audio and raw captures remain ignored.

## Pristine references and candidates

The user manually applied the existing approved entitlement to the fresh baseline and candidate; no key was read, copied or logged. Matching Wwise2023.1.19.8928 generated only each selected regional bank and disposable Init, Windows/SFX, into separate fresh directories. Original complete hierarchies/inclusion rules remain intact; previous accepted banks were not regenerated.

|Region|Native bytes / HIRC|Pristine licensed SHA-256|Candidate bytes / SHA-256|Exact edited records|Warnings, baseline = candidate|
|---|---:|---|---|---:|---:|
|Kaer Morhen|326,697 /440|`ff6d2a41ecb8d4d72de03c84c003616e04c88fa4c84c12c3275e20f9a8ca7a24`|326,702 / `e13353cbd89df3e7d9b19371b39baf12246c43dcb94a2ca6fa756b6da9b07cf9`|2|14|
|Toussaint|678,428 /1,804|`9415f6f10bd47ae54827cec6882e4661e62c143abd637ab550a4791f121ff763`|678,438 / `1332b66ba21a1c973cbf6e09f6979642ae998a3e3c8e132c5194a1d56b6afecb`|9|10|

All four successful generation commands exit**2**, not0, with zero errors/fatals. Each region's baseline warnings are an exact subset of the accepted complete-context NML reference; candidate Counters match their own baseline exactly. Global media-usage/duplication and Wwise.dat warnings remain visible. Command/log/result files are under `P/{baseline-km-licensed,baseline-toussaint-licensed,candidate-km-native-author-licensed,candidate-toussaint-native-author-licensed}`. Failed trial/XML attempts are separate preserved evidence, never package inputs.

`regional_baseline_reference.verify` establishes every pristine HIRC/nonheader byte native-exact, installed native-cache bank identity,62/184 original media payloads, matching metadata, native-exact plugin registrations and accepted generated globals. Proofs: `baseline-{km,toussaint}-full-proof.json`. BKHD v150/language393239870/alignment16/type0 and regional IDs3504965836/864324445 are retained; Project ID17637 versus native39 is the established licensed-authoring difference, not patched or newly inferred from licence correlation. Candidate metadata hashes `{9D1B8731-1A33-3A98-61E9-755B69DCD88D}` and `{8ED6A6CF-EBA6-F4C2-5AF4-6FA03A7847EC}` match BKHD exactly.

`regional_music_batch.verify_banks` invokes the existing `regional_music_gate::{decoded_preflight,bank_preflight}` and `regional_music_bank.record_gate` after the complete batch source gate. Results: `P/{batch-complete-bank-proof,km-full-bank-gate,toussaint-full-bank-gate}.json`. Exactly the approved existing type13 Volume fields differ; no additions/removals, no changed selectors/transitions, RTPCs, parents, immutable record remainders or unrelated objects. Source original values are independently checked, not assumed offsets. No new decoder layout or relaxed comparison is necessary.62 and184 media/reference payloads remain exact. Generated Init non-BKHD definitions/plugins/States/transitions are baseline-exact; generated Init never ships.

Toussaint's six source-only playlists619300091,148396722,353983922,348383165,801727756,428288900 and their descendants remain absent in both native and pristine generated banks. Their parent selector949886373 has no outer AudioNode consumer. Internal State/transition definitions remain unchanged, including the two silent noncombat choices; this is bounded source/generation closure evidence, not a reason to delete them or manufacture runtime inclusion. `P/toussaint-six-omissions.json` binds this conclusion to actual generated membership.

## Accepted capture matrix

**58 completed paired captures:**16 Kaer Morhen,36 Toussaint, and two each for the three native-retained regions. `regional_selector_matrix` and `regional_music_batch_playback` use the same complete isolated `P/fixture/validation/w3_audio.wproj`, never a shipping project. `remaining-control-results.json` preserves independent control status. Matrix files bind exact manifests, plans, raw traces and measurements. An interrupted three-case city folder is retained but excluded; its complete paired replacement uses a fresh label. No previous accepted captures are overwritten.

The fixture retains native play/location events, verified switch-only location priming before music, transport/global RTPC reset and1.1s settling. Effective transport threat values0/35/100 are measured in both modes; Music100/50/100 is measured separately. Profiler contributions contain full selector/playlist paths and accepted State/event times; available PCM is reduced to50ms RMS envelopes. Profiler wall times and PCM origins differ; no sample-exact alignment or measured mathematical zero is claimed. A silent/virtual bus that emits no Recorder file is not treated as zero-PCM evidence.

`regional_music_batch_review.collect` rejects incomplete/duplicate pairs, stale manifest/raw/measurement bindings and repeated groups. `static_voice_checks` verifies actual−200 dB SoundBankValue and rejects generic contribution above−180 dB, rather than inferring success from a soundtrack gap. Both Kaer Morhen targets and five of nine Toussaint targets are directly observed. All11 targets are independently source/binary checked. City counterparts and other analogous targets receive structural coverage, not a false claim of individual audition.

|Control|Observed result|
|---|---|
|Kaer Morhen generic/day-night/dialogue|Day contributions≤−217 dB; night≤−204 dB. Native combat remains outside gain ancestry.|
|Kaer Morhen sustained combat, two phases|Original combat layer level−18 dB retained; named outro at−17 dB completes after exploration returns. Native/modified ends31.70/31.61s and33.26/33.37s after returns26/27.3s, well before55s capture stop. Four explicit outro gates pass.|
|Toussaint generic/day-night/city/common special-location|Measured generic contributions≤−210 dB, including ordinary dialogue and intermediate cutscene/movie/music-only sequences. No generic overlap burst observed.|
|Toussaint sustained combat, two phases|Combat intro/body−10 dB in both modes; native return tail remains audible after exploration26/27.3s and ends30.46/30.48s and31.46/31.48s (native/modified), before65s stop.|
|Threat/intensity|Effective0→35→100 transport values match. Kaer Morhen's original layered/RTPC structure is unchanged. Toussaint world has no authored RTPC objects in the inventory; do not invent a threat-driven layer response for it. Native part selection/levels remain.|
|Boat|Native boat/return selector paths exercised in the Toussaint general control; no new boat composition or behavior is invented. Approved generic score stays attenuated, combat retains native level/return tail.|
|Gwent/minigames|Kaer Morhen Gwent−17 dB both. Toussaint minigames−10 both; sampled Gwent−9/−10 with different native random choices. Shared playlist/source properties are unchanged, not statically muted.|
|Authored branches / native-preserved world score|Direct original authored playlists801579232/276218467 remain audible at−20/−11 dB in both modes; alternate world score remains−11 dB. This tests hierarchy/master response, not retail quest-event sequencing.|
|Original Music setting|Native and modified Music-bus RTPC curves100→50→100 remain0→−6.0206003→0 dB; active values and both return legs are retained in raw traces.|
|Unchanged small regions|Native/thematic, unresolved island and shared-combat controls retain−21,−17 and−17 dB peaks in both modes. Their policies require no replacement bank.|

### Important bound: Toussaint return behavior

The **separate named** general outro segment696831091 was not observed in either native or modified selector control. Do not claim it was individually auditioned or that combat starting alone proves outro preservation. The accepted comparison verifies the full audible native **combat return tail**, including its completion after exploration returns. The named outro's original HIRC, source, transition references and unattenuated physical ancestry are independently exact; no production change is made to force a cue the untouched control does not play. Why this specific segment is not voiced in these controls remains unconfirmed. This is an audition-coverage limitation, not evidence of a candidate-only attenuation regression. Other native contexts may exercise it.

### Long native fade: stronger control

The first65s location control switched after6s while the native source playlist was still in its authored silence: two3×10s rest entries. It verifies selector/gain envelopes, but **not audible musical continuity**. Preserve it as bounded evidence. A stronger90s paired control leaves native playlist7048184 untouched, waits70s, then switches to ordinary city selector236041814 using the original location event.

Real music begins at62.04/62.08s. Native/modified source voices finish82.89/82.92s, about12.8s after accepted switches70.08/70.09s; the original world transition `{60C4695A-71E7-4E17-B544-9453E7E99B03}` has `SourceFadeOut/FadeTime=12` in I. Different native alternate/main compositions have−16/−19 dB peaks; this is not claimed to be identical random selection. Both remain audible, no−200 SoundBankValue enters their ancestry, and both PCM captures contain music. The destination generic playlist is attenuated. No fade, synchronization, State or playlist rule is shortened. Proof: `toussaint-long-fade-proof.json`, source-bound `toussaint-playback-complete-proof.json` and the `ts-settled-v1` raw/profiler/PCM matrix.

All evidence remains bounded to representative authoring tests and structural comparisons. Native Init compatibility outside prior retail-tested White Orchard/current-play consolidated feedback remains unproved in retail for these new regions. Natural-play feedback is welcome without forced travel or custom saves.
