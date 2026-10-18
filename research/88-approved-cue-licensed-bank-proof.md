# Accepted-cue Sparse pilot: licensed regional bank proof

Date: 2026-10-18. Follow-up to [report87](87-approved-cue-sparse-playback-proof.md). The user confirmed manual entitlement application to the existing clean isolated generation project. No licence contents were read, copied or logged.

## Result and scope

The clean single-cue project now generates `music_prologue.bnk`. The experiment-specific source and binary gates pass. This extends report87's **authoring playback** proof with a generated regional-bank structure/media proof; it does not establish retail loading, encoded-media listening quality, packaging, rights to distribute the recording, or a finished Sparse scheduling policy.

Private primary output:

`C:\Dev\witcher-music-control\build\sparse-approved-cue-pilot-v1\generated-banks-licensed\music_prologue.bnk`

- SHA-256: `4759b863ac1e2700627811922d3f07b17397635b03a97af212e8657d33fb27bc`
- Size: 2,036,164 bytes; v150, bank ID3228744150, Project ID17637, Windows/SFX.
- Only selected regional bank and a disposable Init were generated. No SoundBank was installed or packaged. Generated Init must not ship.
- The original failed generation directory and all report87 source/playback/PCM evidence remain intact.

## Actual generation and diagnostics

The command is retained privately in `generated-banks-licensed/command.json`. It uses `tools/white_orchard_wwise.py::generate`, Wwise2023.1.19.8928, complete original hierarchy, selected `music_prologue`, Windows/SFX, isolated cache/output, disabled external hooks/source control/Wwise.dat writing, with no source exclusions.

**Exit2, not exit0.** No fatal/error rows. The trial26,219/200 failure and six Mastering Suite errors are resolved. All15 warning rows match the retained licensed pristine baseline exactly, including multiplicity: nine MediaMultipleUsage, five MediaDuplicated and one Wwise.dat consistency-file warning. No new warning was silently approved. `tools/sparse_approved_bank.py::verify` compares the exact diagnostic Counter via the existing `diagnostics` helper.

For encoded-audio inspection, a separate output run requests the official decoded cache by omitting `--no-decode`; the normal wrapper default remains unchanged. This request is not proof that readable decoded PCM exists. The original output remains the primary retained candidate. Commands, logs, failed decoder output and subsequent conversion evidence are private under the same pilot root.

The first decoded-cache request reused the existing conversion. A final bounded control preserved the generated new-cue cache WEM, removed only that isolated cache entry, then requested fresh conversion with decoded-cache enabled. Both controls also exit2 with the exact15 baseline warnings. **All three regional banks and all three Init files are byte-identical**, including the freshly reconverted cue. No readable decoded file appears. There was no source/conversion-setting change and no further generation is justified for this question in this task.

## Source and preservation gates

`sparse_approved_bank.py::verify` reruns both report55 Sparse semantics and `sparse_approved_cue.py::validate_import`, rather than trusting a previous `passed` flag. Removing only the declared new subtree and playlist reference restores the earlier Sparse source; removing the declared local States/static/sequence changes restores pristine music semantics.

All1,508 original WWUs are retained. Every installed original WWU still matches the preparation manifest. Every isolated WWU except `Interactive Music Hierarchy/music.wwu` remains byte-identical; all47 original audio inputs remain exact both in the isolated project and installed source. No instrumentation or new global source definitions are present.

All24 report85 accepted WAV hashes remain exact, as do the ten preserved release/native inputs recorded by report87. The derived PCM remains SHA `5e677a1da33213e55b1ae4540397adee184e9dcbfa9e93eb6aa2ebae10d6cabc`; the approved WAV remains `2fb3282aea3474fada19b823ffb6dc6b9b794efa1f75aa347df00adf3d3cff82`. No new audio edit was made.

## Decoded HIRC proof

The retained licensed pristine baseline remains native-exact in HIRC and all non-BKHD chunks. Against that baseline the candidate has **492 objects: exactly two additions, eight changed existing playlists, zero removals**. Every other record, including event/action, selector, combat, transition and dedicated authored records, remains byte-identical.

| Existing ShortID | Approved fields |
|---|---|
|133462974|Native Volume−2dB retained; local exploration-audible State policy; one physical child added; deterministic cue/rest playlist|
|251819879,531434506,589261176|Local game_state Voice Volume only; nine muted States, other values native0|
|168472101,833483595,883068472,1049502408|Static Voice Volume−200dB only|

`regional_music_bank.py::validate_record` validates the seven ordinary State/static edits with complete byte restoration. `sparse_approved_bank.py::selected_gate` independently decodes the selected playlist and reconstructs its expected body from the pristine baseline with **only** the declared State bytes, physical child list and deterministic playlist replacement. The remaining prefix, properties, RTPCs, native meter, stingers and transition rules must be exact. The selected policy serializes eight nonzero−200dB States; the three other local policies serialize nine each. Source checks still require all25 explicit source State rows per scope. Compiler omission of zero-gain rows is not missing State behavior.

The playlist repeats a sequence of new segment1029261546 once and existing rest4111369 three times. Native physical segment319905093 remains present and unchanged; there is no unexplained inclusion loss.

New segment1029261546 / track499024852 are fully bounded-decoded by `music_comparison_decode.py`, then compared against independently constructed complete v150 records in `new_records_gate`:

- Segment physical parent133462974; only child499024852; inherited bus/no effects/no RTPCs/no local gain; explicit native60BPM,4/4 clock.
- Duration40,850ms; entry0ms; exit30,850ms; baked post-exit allocation10,000ms. No trim, stretch or clip automation.
- Track parent1029261546; one nonstreamed source383927916; existing native Vorbis codec262145; one clip0–40,850ms; no additional processing/routing.
- Local entry/exit marker IDs43573010/1539036744 are pinned observed compiler identities for source GUIDs `{58205DEA-62A7-4731-8A7E-BDB54D776881}` / `{C75E0F5E-0C6C-4A4E-BDAF-FF3423214A4A}`. WWU does not store marker ShortIDs. No GUID-hash algorithm is asserted; the independently repeated output is compared, and native transition rules remain unchanged rather than referencing either new marker ID explicitly.

This is a separate experimental add-node gate. Existing production static-only gates are not weakened or used to waive unknown bytes.

## Encoded media and global dependencies

Seven original embedded payloads and all47 original media metadata/external payloads remain exact. DIDX contains exactly one additional ID,383927916; no duplicate, overlap, out-of-bounds payload or unexplained nonzero padding is accepted. All original stream identities/flags/files remain unchanged.

New embedded WEM: 1,860,773 bytes, SHA-256 `3da5f548a8eb6cf890e2e8c10ce2c30e709a7e9f799975bbcd39cc34a54fbae8`. It is byte-identical to the official converted cache file `generation/.cache/Windows/SFX/WMC_S04a_approved_FFBA5DAD.wem`. The bounded RIFF check establishes Wwise Vorbis, stereo48kHz,1,960,800 declared frames (40.85s). SoundbanksInfo marks it nonstreamed/Memory; it does not require a new loose streamed WEM. **Encoded header/sample count/cache identity are not a decoded PCM comparison.**

Installed trusted FFmpeg returns “no decoder found” for this Wwise Vorbis format. No decoder was installed, no Music Plus executable was run, and no opaque codec repair was attempted. Report87's exact approved PCM/tail playback remains valid for authoring, but is not substituted for a listening/PCM test of this encoded payload.

Generated Init is byte-identical to the retained licensed baseline: SHA `ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01`. Consequently HIRC, INIT registrations, STMG, transitions and all remaining chunks have no new difference. Plugin registrations match native; Vorbis is already used by the native regional bank. The original native Init remains SHA `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`. Historical selective-Init omissions are unchanged, not recreated or deployed.

BKHD version, bank/language/project IDs, alignment flags and type are unchanged. Candidate hash matches its actual SoundbanksInfo GUID. **Padding is an explained difference:** baseline BKHD payload52bytes/DIDX84bytes versus candidate40/96; DATA starts at absolute byte160 in both. The extra12-byte index entry consumes the12zero padding bytes. `header_gate` derives the required zero padding from DIDX length and16-byte DATA alignment; it does not waive arbitrary padding or patch a header. The initial overstrict padding failure is retained privately.

## Tests and remaining boundary

All231 repository Python tests pass. New tests cover exact new records, every single-byte mutation of both new records and the selected sequence body, wrong marker/media identities, malformed/truncated/duplicate/overlapping media indexes, derived padding and incorrect Project ID. The explicit decoded-cache wrapper option is tested while preserving default generation behavior and refusal to overwrite output.

Private gate: `build/sparse-approved-cue-pilot-v1/licensed-bank-gate-final.json`. Sanitized companion evidence accompanies this report. Earlier strict-gate failures (padding assumption, source marker ShortID unavailable) remain private; each was resolved with a bounded explicit rule, not a relaxed opaque comparison.

Reproduce the read-only gate with `python tools/sparse_approved_bank.py --banks build/sparse-approved-cue-pilot-v1/generated-banks-licensed --output build/sparse-approved-cue-pilot-v1/<fresh-evidence-name>.json`. It refuses to overwrite evidence. Full tests: `python -m unittest discover -s tools -p 'test_*.py'`. The final fresh-conversion output is also checked separately in `post-reconversion-bank-gate.json`.

No authoring playback was repeated and no new Wwise audio server was launched. Report87's thirty final captures/67 measured gates remain the actual playback evidence. Native reselection still cancels rests and combat return still uses native overlap; persistent quiet-time/re-entry semantics remain undecided. No full24-cue scheduler or user-installable release is produced.

The next engineering decision remains explicit post-combat/location re-entry behavior before increasing cue count. Readable encoded-media verification remains a separate limited gap; retail loading and subjective encoded quality are not claimed. No manual licence action is currently needed. Stop here: no cooker, deployment, game launch or full-library rollout is authorized.
