# Licence approved — paired licensed build gates (2026-10-11)

## Status and decision

**Verification prepared:** [report17](17-read-only-licensed-bank-verification.md) documents the strict read-only baseline/candidate workflow and retained-artifact rejection tests. No licensed generation, approval check or licence change was performed.

**User reports approval** of a Witcher 3 REDkit Wwise modding licence and possession of the key on 2026-10-11. This confirms only user-reported approval, **not effective local application**, validity for matching Windows / Wwise 2023.1.19.8928, HomeCinema/Mastering Suite, Motion, or reproduction of native banks. No key, account identifier or approval timestamp is stored here. Next, prepare an isolated full project, have the user apply the key through Wwise's GUI, then run the untouched baseline first.

Latest technical baseline: [report 15](15-full-context-stage1-results.md). Stage 1 direct world State Voice Volume is proven in Wwise authoring (report 13) and serializes into an experimental `music_prologue.bnk` with exactly one changed HIRC object (117-byte increase, fixed -200/-200/0 State values). Generated bank BKHD dwProjectID=0 versus shipped 39; generation exits 1 due to six HomeCinema licence errors. A new bank with native Init has **not** been loaded. This experiment is not deployable.

**Do not attempt live installation now.** While approval is pending, prepare a reproducible comparison/check script if useful, without altering Wwise outputs, installed files or native Init. No additional project pruning, depot generation, custom buses, sliders or unverified header rewriting.

## Once approval becomes effective

1. User checks Audiokinetic Customer Profile → My Projects for approval of *Witcher 3 - REDKit Modding*. The official [Audiokinetic REDkit setup guide](https://www.audiokinetic.com/en/blog/the-witcher-3-redkit-tutorial/) describes Launcher → Licenses → Get License Key and Wwise Project → License Manager. The older guide's Wwise tool version must **not** replace the actually installed matching 2023.1.19.8928. Apply any licence only to a **fresh isolated project copy**; never paste keys into conversations, Git, scripts or output logs. Do not apply a licence or change installed files automatically.
2. Verify **effective** entitlement from generation outcomes (media gate, HomeCinema/Mastering Suite, AkMotion/Motion if applicable) and version/platform. Approval of a name alone does not establish plug-in coverage. If coverage is insufficient, ask Audiokinetic to clarify the modding project entitlement; do not work around a missing legitimate licence by removing native effects.
3. Prepare two **fresh, complete, isolated** source copies using `white_orchard_prepare.py --preserve-hierarchies` (retain all 1,508 original .wwu files). The untouched copy is the control. Apply Stage 1 local State changes only to the candidate with `white_orchard_state_volume_author.py`, no synthetic fixtures or added global objects. No file-leaf inclusion exclusions in the first licensed control.
4. First generate and inspect **untouched full-hierarchy** banks. Require exit status 0 (or a documented, non-fatal code per verified tool semantics), absence of media-limit/licence errors, and controlled generation into ignored `build/` output. Compare vanilla `Init.bnk` and baseline generated Init for HIRC, INIT plugin registrations, STMG, ENVS, device/effect references, master Music behavior, and every unexplained difference. Check baseline `music_prologue.bnk` version, ID, BKHD dwProjectID (shipped **39**), bank hash semantics, media and all HIRC bodies. **A clean log does not prove native compatibility.**
5. Generate the modified candidate under the same setup and compare to the control. Require exactly the intended `world_music` local State Voice Volume serialization (-200 dB on nine named E/D states), all other regional HIRC objects and DIDX/DATA unchanged, and all State group/references satisfied by **shipped native Init**. Verify the project's BKHD identity and existing stream/media references. Discard any incidental generated Init for deployment; **do not silently replace vanilla Init or transplant header words**.
6. **Go/no-go**: if the licensed baseline still has native Project ID **0** versus **39**, missing unrelated global definitions, unexplained bank header differences, or runtime compatibility remains unsupported, retain evidence and ask Audiokinetic/CDPR for generation/project-provenance guidance. Do not infer compatibility solely from the user's licence approval or a successful Wwise authoring audition.
7. Only after technical acceptance, use the reproducible REDkit `cooksounds -r4remastersounds` workflow documented in reports 11 and 13 to package the **modified regional bank only** as a one-entry `soundspc.cache`, retaining native Init and native WEM. Verify cooker success and byte-identical cache readback. This is still **not** a live-load test.
8. Request **explicit separate authorization** for a test in an isolated mod profile with backed-up White Orchard save. Validate game startup, loader precedence, audible exploration/dialogue baseline, combat transitions, authored scenes, native Music slider, and virtualized/below-threshold/resume behavior across long muted traversal. Do not restart the playthrough or advance quests solely to test earlier q001.

## What counts as done

- **Licence status:** user has confirmed approval/application, matching version/platform/plug-in coverage, and no relevant generation errors.
- **Bank fidelity:** unchanged control has explainable differences vs shipped assets; modified candidate differs only in intended local State volume and is compatible with native Init, including BKHD project identity.
- **Packaging:** native cooker accepts the modified bank and single-entry cache can be read back unchanged.
- **Runtime:** separate user-approved White Orchard test required before claiming a working mod.

If a free REDkit entitlement does not produce matching source/build identity, do **not** widen to all eight regions or substitute a global mixer as a workaround. The first next action is source/identity clarification, not broader output.

Official documentation: [Audiokinetic REDkit setup](https://www.audiokinetic.com/en/blog/the-witcher-3-redkit-tutorial/); [Audiokinetic Launcher project licence status](https://www.audiokinetic.com/en/library/edge/?id=projects&source=InstallGuide); [noncommercial licensing](https://www.audiokinetic.com/en/products/licensing/).
