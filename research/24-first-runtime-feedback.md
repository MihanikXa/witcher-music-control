# 24 — First live White Orchard feedback: working Stage 1, transient music bleed

Date: 2026-10-12. **User-reported in-game observation**, not an independently captured trace or a measured Wwise bank-load result. User installed and played the staged music-control variant through the recent Vortex workflow; exact Vortex enabled-state/hash and A→C→A repeat sequence were not supplied in this message.

## Explicit user feedback (preserve wording/meaning)

> "Everything works, the only problem is that sometimes I get a 1 second fade in fade out in dialogues of exploration music and then back to silence, and when entering combat the same thing of fade into exploration first for a second and then combat music transition. But yeah it works, exploration music is gone and dialogue too, can't confirm on curated music though yet."

Separate observed facts from inference:

| Context | User report | Certainty / limits |
| --- | --- | --- |
| Normal White Orchard exploration | Exploration music is gone | Direct reported gameplay observation; not instrumented |
| Ordinary dialogue | Generic dialogue music is gone, **except occasional approximately 1-second exploration-music swell** fading in/out, then silence | Direct reported observation; dialogue entry/exit and specific scene/game_state not yet localized |
| Entering combat | A brief exploration-music swell precedes the transition to combat music | Direct reported observation; combat is audibly reachable; not yet measured whether every combat starts this way |
| Curated/authored quest/cutscene cues | **Not confirmed** | No positive or negative in-game conclusion; Wwise audition protection of q001 (report13) is separate |
| Cross-project bank compatibility | Candidate gives distinctive changed behavior with game Init retained according to staged package design | Strong practical evidence that the modified regional bank works in this tested retail environment. Actual runtime Init hash, deployed mod hash and explicit A→C→A reversibility were not reported afresh; do not overclaim those measurements |

### Exact staged candidate (reports 22–23)

Original native Init SHA-256: `2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277`, ProjectID39. Modified `music_prologue.bnk`: ProjectID17637; SHA-256 `80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698`. Direct cooked C `soundspc.cache` SHA-256 `a2b8cc23285c5b6cd392b0301328d75bd545dde8d9e0c06007b674b68a14aa12`. Package/Vortex ZIP paths and guard code in report23. Stage1 policy: existing world MusicSwitchContainer only, nine exploration/dialogue states at -200dB, combat and other states at unity. All 19 prior offline structural tests passed; this new report does not rerun them.

## Leading technical hypotheses — **not established causes**

1. **Gain change before music selection catches up.** On entering combat the world object's State Voice Volume moves from -200dB toward 0dB while the currently playing exploration segment may still be active, before the underlying game_state-selected combat child actually takes over. The original game_state group has a default 1000ms transition (report19) and native music-switch transitions/sync points (reports03/13). The report of ~1 second is suggestive, **not sufficient to attribute duration** to one setting.
2. **Intermediate dialogue state exposes world music.** Ordinary dialogue start/end can briefly traverse game_state values whose world State Voice Volume is currently 0dB (e.g. movie/cutscene/music_only, depending on actual scene sequence) before reaching dialog_scene/dialog_scene_night -200dB. The game's scene player pushes/pops blocking/cutscene/movie states (report03); **we do not yet know the real sequence for the reported cases**.
3. **Voice continuation / switch scheduling.** Wwise's music switch transitions, fade overlap, transient media activation/virtualization and asynchronous gameplay state changes may expose the previous world segment. Must diagnose before changing the production model.

Avoid assuming the issue is caused by a loader ProjectID mismatch, wrong ZIP deployment, an arbitrary soundtrack track, or deliberate authored music. Also avoid proposing a global Music-bus mute, blanket non-combat state mute, all-cues Stop, general script override, or changing the native StateGroup transition table; such shortcuts can suppress authored cues or damage native fades.

## Next engineering task (scoped)

1. Preserve working C bank/ZIP/source and rollback A untouched. Record a reproduction matrix: dialogue start vs finish; daytime/nighttime; standing in village versus countryside; combat initiation vs end; whether it is genuinely the exploration cue rather than authored score. Ask the user only for a very short clip/context description if the issue cannot be reproduced from authoring probes.
2. Reproduce on a **separate isolated Wwise authoring fixture** using the actual world/quest selector, fixed current -200/0 local States, native game_state transitions and realistic order/timing. Exercise E→combat, E→dialogue, dialogue→E, and intermediate movie/cutscene/music_only sequences. Capture 100ms-or-better output envelopes and selector/state timestamps when possible. Earlier report13 tests measure sustained 4-second steps; they were not designed to catch a 1-second world-music burst during asynchronous playlist switching.
3. Inspect current REDkit scripts/Wwise state and switch transitions in report03/source, especially order of `SoundGameStateChange` versus child Switch selector and any intermediate states. Distinguish a **fade/gain transition** from **music segment switch** timing. Verify any local authoring-only solution against actual supported properties; do not invent APIs.
4. Propose the **smallest local regional change** addressing the demonstrated cause. Preserve normal combat music and intensity, authored branch, Music slider, native fades, original game Init. Do not silently replace policy with global mute or widen to all regions.
5. If a fix is convincingly validated offline, prepare new separately named experimental candidate **D**, with fresh bank/cache/ZIP hashes, existing structural/media checks and no change to working C. Keep all new outputs Git-ignored; do not deploy or launch without the user's separate permission. Record unresolved coverage and in-game test instructions.

## Status and acceptance

- **Milestone achieved:** Real game reportedly exhibits intended exploration and dialogue suppression plus audible combat using the regional-only candidate.
- **Open defect:** Occasional ~1-second exploration music fade in/out during dialogue and on combat entry.
- **Unverified:** Authored/curated score in actual game, transition cause, virtualized-voice recovery after prolonged silence, exact A/C/A reversibility, full save/game profiles and other regions.

For a future D test, a pass means generic music stays inaudible throughout routine dialogue and **until the combat cue itself is selected**, while combat/music intensity and protected authored music remain audible. Avoid 'fixes' that merely silence the first second of combat or prevent any story cue from playing. Record actual user perception and in-game evidence before generalizing.
