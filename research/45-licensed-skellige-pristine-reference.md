# Licensed Skellige pristine reference — 2026-10-15

**Observed:** the user manually applied the approved entitlement to the isolated untouched baseline. Selected `music_skellige` Windows/SFX generation now exits **2**, produces only that bank and disposable Init, and has **16 warnings, zero errors/fatals**. This resolves report44's baseline prerequisite. No licence fields/key were accessed or transferred. All1,900 regional HIRC records and all non-BKHD chunks are byte-identical to native. All253 streamed media payloads match the installed game's original cache. This is an independently verified untouched reference, not retail Skellige validation.

## Reproduction and evidence

Project `C:\Dev\witcher-music-control\build\skellige-v3\baseline\w3_audio.wproj` retains all1,508 original work units and253 original audio inputs (3,093,678,926 bytes). Installed source is `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`; its corresponding files and all copied inputs rehash exactly. No pruning, leaf exclusions or bank-inclusion edits. Project version `v2023.1.19`, build8928/schema119; the matching console is under `L:\Programs\Wwise_2023.1.19.8928\Authoring\x64\Release\bin`.

Selected command uses `tools/white_orchard_wwise.py --project build/skellige-v3/baseline/w3_audio.wproj --bank music_skellige --output build/skellige-v3/baseline-banks-licensed` with the matching console. `command.json`, `generation.log` and `result.json` preserve full invocation, exit and all diagnostics. Failed `baseline-banks` from report44 remains intact. No other regional bank was regenerated.

Independent read-only verification is reproducible with `tools/regional_baseline_reference.py::verify` and these arguments:

```powershell
python tools/regional_baseline_reference.py --source 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio' --project build/skellige-v3/baseline --banks build/skellige-v3/baseline-banks-licensed --native 'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\soundbanks\Pc' --cache 'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\soundspc.cache' --accepted build/regional-system/nomansgrad/baseline-banks-licensed --region music_skellige --output build/skellige-v3/pristine-baseline-verification.json
```

Output must be fresh. The accepted NML reference is used only for already-reviewed warning membership and unchanged generated globals, never regenerated or treated as Skellige's media baseline. Future Skellige candidates must match **their own** baseline diagnostics exactly. The tool does not read project licence fields, generate banks or deploy anything; cache indexing reads bounded table/payload ranges without loading the multi-gigabyte cache wholesale. Positive/malformed/truncated/unterminated-name tests exercise that reader. Historical strict Init-equivalence gates remain unchanged.

| Resource | SHA-256 |
|---|---|
|Native `music_skellige.bnk`,662,405 bytes|`8bfa09f056045beebe51f59e19b899b370fed999a2212b1ddba7dd26af34476c`|
|Licensed untouched regional bank,662,405 bytes|`a5182fe678d278740831f22cea1c0f7ca079e2d28d373f306f05c364e563db54`|
|Disposable generated Init|`ec6060226583cda325b3175dd990bf7a77c4c49a7a6a57ba0130089b0ea69b01`|

BKHD: version150, bank1324662489, language393239870, alignment16, type0 and native eight-byte zero padding unchanged. Project ID17637 versus native39 is the established licensed-build difference; generated hash `{4581D5F7-5285-43E0-619E-06283348348B}` agrees with SoundbanksInfo. No header was patched. No unexplained non-header difference exists. Prior White Orchard/consolidated user feedback bounds the operational evidence; this does not independently prove Skellige retail loading.

All253 media files selected by current `SoundBank/Media/File` metadata hash-match the bounded native CS3W entries. Native-exact regional HIRC/non-header bytes preserve original stream/source references and embedded data; missing loose native files are not mistaken for media loss. Generated Init non-BKHD chunks equal the accepted complete-context NML baseline, and its18 INIT plugin registrations match native. Historical generated/native Init omissions are not repaired or shipped. Original Init remains unchanged.

All16 warnings are exact members of the19-warning accepted NML reference: nine MediaMultipleUsage, six MediaDuplicated and one Wwise.dat consistency warning. `baseline-warning-review.json` retains the Counter comparison; there are no new Skellige-only messages. Warnings are recorded rather than converted into an exit0 claim. `pristine-baseline-verification.json`, `baseline-native-comparison.json`, `baseline-native-cache-media.json` and source-preservation proofs retain complementary independent evidence under ignored `build/skellige-v3`.

## Ten source-only playlists: bounded conclusion

The ten report29/44 source playlist IDs remain absent in **both** native and licensed untouched HIRC, with no added/removed objects. Their source descendants with ShortIDs are likewise absent. None has an AudioNode selector consumer or direct/descendant event reference across all542 original event work units. This is generation/selection evidence, not permission to delete source definitions.

- Eight transition playlists have no external object references in the inspected music/events/bank source:250487810,822810934,802768195,1003349432,407311040,543725422,954667010,365608565.
- Transition playlist149108804 contains segment GUID `DFFD83C3-FC53-486A-817E-1F4C47617EC4`. Its world-root transition reference is retained, but that rule does not enable `UseTransitionObject`. Matching installed `Authoring\Data\WObjects\WObjects.xml:2615–2617` defines the absent property default as **false**. A stored reference therefore does not establish actual segment playback. Both playlist and descendants remain omitted by the untouched generator.
- Night playlist636008624 is referred to four times as transition-rule **SourceContextObject/DestinationContextObject**, not as an AudioNode or transition segment. Matching definitions at `WObjects.xml:2456–2493` distinguish Object endpoints from actual playback selection. The selected night playlist is a different object,726745057, which exists in native/generated HIRC. Rules referring to the unused endpoint do not independently select it.

Evidence: `source-only-reference-review.json`, `absent-playlist-generated-closure.json`, `absent-transition-owner-review.json`, `source-only-all-events.json`, and original `Interactive Music Hierarchy/music.wwu` declaration lines in report44. Some containing selectors themselves are serialized; do not equate a retained source reference with a serialized playable descendant. **Supported inference:** these ten definitions are unnecessary to reproduce the shipped regional bank's current inclusion closure. Universal runtime unreachability or deletion safety is not claimed. They remain source-identical and ineligible for attenuation; any future changed inclusion must fail independent bank gates.

## Handoff

Proceed with the reviewed static-only manifest and separate complete candidate/validation fixture. Retain this licensed pristine baseline unchanged; never copy its project licence contents into either project. Native Init and verified D/NML banks remain untouched. No custom saves, progression, game launch, Vortex changes or retail test are required. Report46 records subsequent implementation and playback status.
