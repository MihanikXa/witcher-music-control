# Three literary directions — English scope

## Recommended: Field & Folio

Use Gentium Book Regular for names, subtitles/dialogue and reading; restrained
Gentium bold for meaningful emphasis/headings. Use Source Sans 3 Regular or
Medium for small controller prompts, settings labels, quantities and compact
utility text. Retain Witcher icons, target behavior and familiar spatial anchors.
Generous spacing and quiet hierarchy should carry the design, with no new
decorative borders or wholesale hiding of information.

The first nameplate proof uses the **current font** to evaluate semantic colors
and shadow independently. Gentium is the primary taste reference and preferred
next font trial, not a prerequisite for the proof.

| Direction | Typography | Strength | Trade-off and feasibility |
|---|---|---|---|
| 01 Quiet Editorial | Gentium Book for reading and auxiliary controls; regular with selective bold | Closest to supplied reference, unified literary tone, simplest global EN library trial | Broad book face is less compact than PF Din; more wrapping, dense small controls and numeric alignment risks. Font library alone changes no sizes/effects |
| 02 Field & Folio | Gentium Book for reading/names; Source Sans 3 for compact auxiliary roles | Preserves personality while separating reading from action; recommended long-term direction | Requires an additional family and selected TextField bindings, beyond three global normal/bold/italic aliases. Exact export/integration pending |
| 03 Humanist Chronicle | Alegreya Regular for reading/names; Source Sans 3 for auxiliary roles | More rhythmic, earthy letterforms; another literary candidate with independently available source | Test figure style, cap texture, width and italics. Do not inherit Font of Life's customized condensation/small caps without independently designing and testing them |

Gentium Book is slightly heavier than Gentium; Regular is the initial weight.
Do not synthesize a Light weight or reduce opacity to fake a fine stroke.
Matching apparent x-height at controller distance is more important than equal
nominal sizes. Maintain EN punctuation/diacritics and test bold/italic use.
Russian/Ukrainian support is no longer a project requirement.

## Provisional palette

RGB values are ordinary sRGB design tokens; `textColor` uses 24-bit RGB, with
alpha/effects handled separately. These are role mappings, not a global filter.

| Role | Hex | RGB | Additional distinguishing signal |
|---|---|---|---|
| Primary / neutral | `#E9E2D2` | 233,226,210 | Stable text hierarchy |
| Secondary / stone | `#C0BBB0` | 192,187,176 | Supporting size/position; not reduced opacity on bright scenery |
| Friendly / sage | `#B4C0A0` | 180,192,160 | Keep game interaction/relationship cues |
| Hostile / muted oxide | `#D6A093` | 214,160,147 | Retain health bar, level danger, hard-lock/targeting behavior |
| Selected / VIP / old brass | `#D5C08E` | 213,192,142 | Existing selection indicator/quest icon; VIP is not automatically friendly |
| Axii / cool slate | `#B4C2D1` | 180,194,209 | Charmed state and associated bars/feedback remain distinct |
| Disabled on fixed dark menu | `#8D8A81` | 141,138,129 | Disabled behavior, low emphasis; not for essential world text |
| Optional contrast surface | `#141718` | 20,23,24 | Small local treatment only when needed |

Oxide is intentionally lighter than a dark brick pigment. Dark red would look
restrained on paper and disappear in caves. Story/chapter/side quests and item
rarity need their own mappings; they must not all become brass or gray. Herbs
can initially retain the neutral state; distinct herb styling requires a later
script/semantic route rather than an invented sixth native attitude.

## Effect strategy

Nameplate baseline has a **black drop shadow**, strength3/blur4/opaque; subtitle
baseline has an **opaque black glow**, blur5/passes3. Test separate field-local
changes. Do not toggle useOutlines or erase all filters.

Initial proposed name shadow trial: same filter type/placement; color
`#141718`, alpha approximately **166/255**, blur2x2, strength1, distance1,
existing angle/passes/composite behavior. These are actual observed filter
property names with proposed new values; perceived output is untested.
Test keeping the current 20 logical px name before trying ~22 or increasing
text-box leading/bounds. Do not shrink an already small name just to make it airy.

Subtitle trial later: reduce the specific glow first, then compare a soft
shadow or local translucent subtitle backing. Runtime 26+SubtitleScale remains
the size authority; changing authored18 alone is ineffective. Do not clear
explicit story/speaker HTML colors indiscriminately.

No automatic scene-luminance detector is established by this research. Offer
an explicit comfort treatment only once supported implementation is verified.
Avoid claiming dynamic adaptation. A local backing at 80% opacity is a **mockup
stress-test option**, not the recommended everyday look and not yet implemented
in game. If the soft-shadow proof fails on snow, increase that field's contrast
treatment before considering unverified adaptive behavior.

## Contrast and legibility findings

Calculated sRGB fill-only contrast, without shadow, on representative **synthetic
flat colors**. These are comparisons, not scene measurements or HDR certification.
Contrast ratio uses relative luminance, `(Llight+.05)/(Ldark+.05)`.

| Text | Foliage `#596D56` | Snow `#E7ECEB` | Cave `#151B1C` | Bright `#F5F3E9` | Fire `#D79D49` |
|---|---:|---:|---:|---:|---:|
| Ivory | 4.34 | 1.08 | 13.50 | 1.16 | 1.85 |
| Sage | 2.93 | 1.60 | 9.12 | 1.72 | 1.25 |
| Oxide | 2.48 | 1.89 | 7.72 | 2.03 | 1.06 |
| Brass | 3.14 | 1.50 | 9.76 | 1.61 | 1.34 |

No-shadow text fails the bright-background stress test. A softer shadow looks
lighter in interiors but still needs a snow/fire comfort option. 70% sRGB
backing over synthetic snow yields only 3.24:1 for oxide; 80% yields **4.53:1**.
This uses sRGB-channel alpha compositing; actual engine blending/HDR differs.
4.5:1 is an internal useful screening target for small essential text, not a
claim that dynamic game rendering is a static webpage.

Browser views were rendered at 1920-wide with all three upstream fonts loaded,
five backgrounds, hostile backing and 1080-wide inspection. No clipped header
or overlapping column was observed in those previews. They do not validate
in-game 1080p/4K or controller viewing distance. Actual tests must include snow,
overcast sky, cave/night, foliage, fire/bloom, bright menus, moving camera and
native1080p/4K UI sizing. Judge hostility using bars/position/targeting alongside
color; color-vision and grayscale tests remain pending.

## View and reproduce

Open [comparison.html](comparison.html). Select background, target and effect
while keeping the three designs side by side. This is an original browser
mockup with synthetic scenery; no third-party screenshot or UI artwork is used.
Body/name font sizes are deliberately comparison sizes, not promised game values.
The title/prose are illustrative, not replacement localization.

Run `tools/get-preview-fonts.ps1` first after cloning. All font binaries and
licenses are local under ignored build/fonts; missing fonts are flagged in the
page. `tools/render-comparison.cjs` produces PNGs under build/comparison.
See [tools guide](../tools/README.md) for runtime paths and commands.
