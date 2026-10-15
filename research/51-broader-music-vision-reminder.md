# 51 — Broader experience-led music vision reminder — 2026-10-15

## Latest explicit user correction

> I don't think that was the full vision that you are describing, we had more plans to make it work even better, closer to what breath of the wild or tsushima do with their musc

User's correction: implementing reviewed regional attenuation is **not the end of the original goal**. Their broader aspiration includes a soundtrack experience closer to Breath of the Wild and Ghost of Tsushima: breathing space, environmental sound as a first-class layer, and purposeful contextual musical presence. Previous conversation context also supports exploration sparseness, selected intermittent musical punctuation and adaptive transitions/intensity as desired design directions. Preserve the user's original wording, and keep these aspirations distinct from assistant-derived specific implementations.

## Explicit-versus-proposed status

- **Confirmed Stage1 baseline:** Exploration generic score 0%, ordinary dialogue generic score 0%, combat native/unity, deliberate authored gameplay/quest/cinematic score native/unity, original transitions and Music master preserved. This is implemented partially through existing soundbank attenuation, not dynamically inferred from every moment.
- **User's current broader direction:** The finished system should be better than simple mute/keep decisions and aim for the perceptual pacing/spaciousness of Breath of the Wild / Ghost of Tsushima. This is not a request to copy particular scores or replace all Witcher arrangements.
- **Previously documented future hypotheses (report08):** Selected intermittent musical punctuation, a Sparse mode, Minimal mode, Low-background adjustable option and independent sliders. These were design proposals; the user has not specified or approved exact event triggers, delays, probabilities, cue choices, mixing curves or defaults. Do not promote them into certified requirements.

## Actual current architecture and gap

Current v4 is a verified five-bank soundspc.cache containing unchanged retained D/NMLv2/Skelligev1 and new Kaer Morhen/Toussaint; all eight regional policies reviewed, three deliberately unmodified. Main suppression is static -200 dB Voice Volume on selected generic playlists, with White Orchard D additionally retaining context State attenuation. It preserves native Wwise event, location, music_type, selection, intensity, fades and quest branches where structurally separable. Some mixed/ambiguous generic scoring remains; one likely White Orchard authored-world exception remains potentially attenuated. No dynamic exploration scheduler, sparse reintroduction cues, new environmental triggers, runtime mode selector or sliders have been implemented. Offline v4 isn't deployed or retail verified.

## Next investigation — do not launch a bulk implementation without mechanism proof

Study how to achieve intentional sparse exploration presence without arbitrary periodic soundtrack spam or breaking native authored/combat transitions. Separate: (a) environmental/ambience priorities, (b) when an exploration phrase may enter or remain absent, (c) event/location/discovery triggers actually exposed by game/Wwise rather than hypothesized, (d) timing, phrase completion, exit/fade/overlap, (e) authored/noncombat mixed path separation, and (f) prospective Minimal/Sparse/Low-background control and persistence. Compare Wwise-only silence/playlist mechanisms against narrowly scoped WitcherScript/event controls and existing reference mods such as Less Is More, preserving evidence of each technique's tradeoffs. A tiny offline prototype with exact preserved selectors, long transitions and original combat/quest behavior should precede full-game changes. Avoid fake context-awareness based only on a random timer, and avoid claiming precise Ghost of Tsushima/Breath of the Wild algorithms without evidence.

Existing regional baseline/decoder/cache authoring remains useful as foundational engineering. Do not regenerate all regions, disturb the user's current installation, force gameplay progress or introduce spoilers while designing the next layer. Revisit Music Plus on real implementation merits rather than assuming its sliders alone deliver this broader pacing goal.
