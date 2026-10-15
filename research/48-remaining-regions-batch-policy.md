# Remaining regions: batch policy and source implementation — 2026-10-15

The five remaining regional graphs are reviewed together. Eleven approved static playlist Voice Volume edits cover ordinary score in Kaer Morhen and Toussaint. The other three regions remain native by explicit policy, not by pretending an unchanged bank is a new implementation. This is offline development; the installed consolidated v2 and accepted v3 archive remain untouched. Reports38/43 govern natural-play feedback; no saves or retail travel are required.

## Source authority and classification

`W` denotes the read-only installed `L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio`; `I=W/Interactive Music Hierarchy/music.wwu`, `E=W/Events/music.wwu`, `B=W/SoundBanks/music.wwu`. Exact original I SHA is `f8184d13ea08f6bc161719884e9341bdfd3a3e7666b203c296ffae37d4e08251`. `tools/regional_music_audit.py::audit` resolves all542 event work units, target descendants, selector consumers, transition segment references, physical parents, source reuse and native HIRC membership. Read-only evidence: `build/full-game-v4/source-consumer-audit.json`; independently pinned decisions live in the five `src/wwise/regions/*-v1.json` manifests.

Observed identities/routing/media are separate from musical-intent policy judgments. Ordinary reusable day/night, city, cave and common-background paths have distinct combat and authored consumers; source/event/transition closure authorizes only their local playlist edits. Shared media remains unchanged, including its other authored consumers. Separate alternate/thematic selections remain protected; uncertain location-specific scoring is preserved. No filename, quest-number or genre rule assigns classification.

All26 source location selectors and34 relevant noncombat playlists are classified:

|Region|Generic targets / rows|Silent targets / rows|Protected targets / rows|Mixed targets / rows|Unresolved targets / rows|
|---|---:|---:|---:|---:|---:|
|Kaer Morhen|2 /9|2 /18|0 /0|0 /0|0 /0|
|Toussaint|9 /45|5 /27|5 /36|2 /12|5 /45|
|Wyzima Castle|0 /0|0 /0|1 /6|0 /0|0 /0|
|Isle of Mists|0 /0|0 /0|0 /0|0 /0|1 /9|
|Spiral|0 /0|0 /0|0 /0|2 /18|0 /0|

Totals:54 generic,45 silent,42 protected,30 mixed and54 unresolved source consumer rows,225 overall. **Nine Toussaint silent rows are source-only**, beneath selector949886373 with no outer AudioNode consumer; exclude them from playable-bank coverage. Native-present denominator216:54 generic (25%),36 silent (16.7%),42 protected,30 mixed,54 unresolved. Toussaint alone has156 native-present rows:45 generic (28.8%) plus18 silent (11.5%). These are selection-consumer counts, not geographic coverage or guaranteed event reachability. Dedicated authored siblings are outside this world-playlist denominator.

Both silence originals are RIFF PCM stereo44.1kHz/16-bit,441,000 frames, all sample bytes zero; SHA `086b066a69a1859705f707947bda612cdcf0a003db9ec2c9041b5ee8d1dbc108`. This repeats report07's sample-backed observation, not a name-based silence assumption.

## Exact edits and preserved paths

Only `Volume` becomes−200 dB. GUIDs, original properties and complete selector/State consumer pins are in `kaer-morhen-v1.json` and `toussaint-v1.json`.

|Region|Playlist ShortID|Physical parent ShortID|Original dB|
|---|---:|---:|---:|
|Kaer Morhen|598161056|556828113|−2|
|Kaer Morhen|312446899|556828113|0/default|
|Toussaint|355578338|1047034767|−4|
|Toussaint|534178667|1047034767|−4|
|Toussaint|927971671|236041814|−4|
|Toussaint|598316307|236041814|−3|
|Toussaint|45385052|151201221|0/default|
|Toussaint|707546764|195335809|−4|
|Toussaint|965500254|195335809|−3|
|Toussaint|148058891|397610127|0/default|
|Toussaint|914839555|397610127|−2|

Every edited object is native-present, consumed only within its regional world branch and outside combat/Gwent/minigame and direct-event/transition-segment ancestry. Ordinary and alternate special-location selectors are independently pinned, preserving the alternate's additional score. No transition, playlist ordering, synchronization, RTPC curve, event, source or media is edited. No StateInfo is added to a shared location/root; native Music master remains an additional multiplier.

Wyzima playlist1031426249 reuses an explicitly authored source in another unchanged regional branch (report07's source-reference comparison); conservative protection is intentional. Island playlist833316345 remains unresolved thematic/location scoring. Its sibling is explicitly pinned as `quests_cutscenes`, GUID `{AC3699A8-6056-4769-82D3-0BE7D4688EB8}`, ShortID997293540; identity comes from the original source, not a hardcoded spelling. The existing regional gate already accepts an exact pinned alternate name; a positive/negative alias regression now verifies it.

Spiral926055871 serves underwater combat as well as noncombat;748832630 serves multiple combat and noncombat States. Both remain native. Their existing selection routes reuse the same physical playlists/voices: static muting breaks combat, while State-gating the same continuing voice recreates unproved transition/tail risks (report34). No independently isolated existing generic-only path was established. This batch adds no duplicated voices, script hooks or compensating gains to force coverage.

## Efficient complete-context implementation

`tools/regional_music_batch.py::{prepare_batch,batch_context,batch_semantics,source_gate,author_static}` implements one pristine baseline, one editable batch candidate and one separate Recorder fixture. Each retains all1,508 work units. One268-input immutable audio pool is copied from installed originals; candidate and fixture use verified hard links only to that ignored pool. No installed original is hard-linked or edited in place. Region source gates are not weakened: each regional projection restores every other declared edit, invokes the existing exact semantic validator, then union restoration requires the entire original music source. Every unrelated WWU, all542 events and original audio are checked. Duplicate/overlapping edits, altered Volume layouts, unreviewed consumers and undeclared changes fail closed.

Only the baseline and candidate needed manual entitlement application; the user confirmed it. The initial baseline exit1 trial failure (26,218/200) is retained. No licence data was accessed/transferred. New authoring uses supported WAAPI `object.setProperty` plus project save on the exact matching8928 isolated server. Source SHA after native save is `c4ac43ba4f53f8b5a2560da8bcdb03dabbdd3cfb2d630188e9d89b1d978bad58`; `batch-native-author-source-proof.json` passes complete union restoration.

### Failed XML control retained

The initial experimental XML writer appended new PropertyList nodes after children and, on existing native ValueList properties, incorrectly added a second shorthand Value. Semantic restoration initially passed but native loading rejected it. Reordering alone passed XSD119 yet still failed Wwise load. Pristine source restoration loads successfully with the same project; supported WAAPI authoring resolves both representations without altering unrelated semantics. Failed outputs and both source snapshots remain under `build/full-game-v4`; none is a package input. Production authoring no longer writes modified XML directly. New tests reject duplicate Value/ValueList forms and preserve exact approved native property representations. Passing semantic comparison alone is never a substitute for native load/generation and decoded bank gates.

New native baseline/bank and playback results are recorded separately; source success is not retail validation. Existing D/NML/Skellige banks were not regenerated. All three accepted payloads and v2/v3 archives are rehashed exactly in `retained-three-bank-and-archive-proof.json`.
