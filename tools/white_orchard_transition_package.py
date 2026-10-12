"""Fail-closed D bank audit and regional-only offline cooker/ZIP packaging.

Never edits bank bytes, installs a mod, touches Vortex or accesses licence data.
The original C-only gate remains unchanged. This gate accepts exactly five
measured v150 playlist property bundles; it is not a general HIRC decoder.
"""
import argparse
import copy
import json
from pathlib import Path
import shutil
import struct
import zipfile

from white_orchard_candidate_package import diagnostics
from white_orchard_compare import read_bank, difference
from white_orchard_cooker import prepare, execute
from white_orchard_loading_package import verify, NATIVE_INIT, LICENSED_BANK
from white_orchard_prepare import REPO, build_path, digest
from white_orchard_state_bank_audit import header, state_chunk, WORLD
from white_orchard_state_volume_author import semantic
from white_orchard_transition_author import volume
import xml.etree.ElementTree as ET

C_BANK = "80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698"
D_SOURCE = "cba9ed036e94fe658ca8e506d5539e1f7139f7caea51a21cac3fadbdcebcc259"
ENTRY = "Mods/modWMCBankLoadingTest/content/soundspc.cache"


def playlist_delta(before, after, original_volume):
    """Check the observed five type13 bodies, not arbitrary playlist layouts.

    The pinned C body has a property bundle at offset14: uint8 count,
    uint8 property IDs, float32 values. v150 property0 is Voice Volume.
    Preserve its complete prefix and suffix including routing/RTPCs/transitions.
    No data is rewritten or serialized here.
    """
    def bundle(body):
        if len(body) < 20:
            raise ValueError("Truncated measured playlist")
        count = body[14]
        if count not in (0, 1):
            raise ValueError("Unrecognized measured property bundle")
        end = 15 + count * 5
        props = {} if count == 0 else {body[15]: struct.unpack_from("<f", body, 16)[0]}
        return props, end
    old, old_end = bundle(before)
    new, new_end = bundle(after)
    expected = {} if original_volume == 0 else {0: float(original_volume)}
    if old != expected or new != {0: -200.0}:
        raise ValueError("Unexpected playlist property/value")
    if before[:14] != after[:14] or before[old_end:] != after[new_end:]:
        raise ValueError("Playlist data beyond Voice Volume changed")
    return {"offset": 14, "before": old, "after": new, "prefix_suffix_exact": True}


def audit(redkit, baseline, c, d, project, output):
    output = build_path(output)
    if output.exists():
        raise FileExistsError(output)
    spec = json.loads((REPO / "src/wwise/white-orchard-transition-fix.json").read_text())
    targets = {x["short_id"]: x for x in spec["targets"]}
    b, cb, db = [read_bank(p / "music_prologue.bnk") for p in (baseline, c, d)]
    native = read_bank(redkit / "r4data/soundbanks/Pc/music_prologue.bnk")
    diff = difference(cb, db)
    hc, hd = header(cb, c / "SoundbanksInfo.xml"), header(db, d / "SoundbanksInfo.xml")
    checks = {}
    checks["pinned_baseline_and_C"] = b["sha256"] == LICENSED_BANK and cb["sha256"] == C_BANK
    checks["only_five_existing_playlist_records_changed"] = not diff["added"] and not diff["removed"] and {x["id"] for x in diff["changed"]} == set(targets) and all(x["type"] == 13 for x in diff["changed"])
    checks["all_other_records_including_world_exact_C"] = cb["records"].keys() == db["records"].keys() and all(cb["records"][i] == db["records"][i] for i in cb["records"] if i not in targets)
    decoded = {}
    try:
        for ident, target in targets.items():
            if cb["records"][ident][0] != 13 or db["records"][ident][0] != 13:
                raise ValueError("Not the measured playlist type")
            decoded[ident] = playlist_delta(cb["records"][ident][1], db["records"][ident][1], target["original_volume_db"])
        checks["only_static_volume_fields_changed"] = True
    except (ValueError, KeyError, struct.error) as error:
        checks["only_static_volume_fields_changed"] = False
        decoded["error"] = str(error)
    checks["world_state_serialization_exact_C"] = state_chunk(cb["records"][WORLD][1]) == state_chunk(db["records"][WORLD][1])
    checks["only_BKHD_HIRC_chunks_change"] = set(diff["chunk_changed"]) == {"BKHD", "HIRC"}
    checks["unchanged_native_embedded_media"] = all(native["payload"][tag] == b["payload"][tag] == cb["payload"][tag] == db["payload"][tag] for tag in ("DIDX", "DATA"))
    identity = lambda h: {k: v for k, v in h.items() if k not in ("hash_hex", "metadata_hash", "hash_matches_metadata_guid")}
    checks["BKHD_identity_exact_C"] = identity(hc) == identity(hd) and hd["project_id"] == 17637 and hd["version"] == 150
    checks["BKHD_hash_matches_metadata"] = hd["hash_matches_metadata_guid"] and hc["hash_matches_metadata_guid"]
    checks["disposable_Init_all_bytes_exact_C"] = digest(c / "Init.bnk") == digest(d / "Init.bnk") == digest(baseline / "Init.bnk")
    checks["no_new_generation_diagnostics"] = diagnostics(baseline) == diagnostics(c) == diagnostics(d)
    checks["native_Init_unchanged"] = digest(redkit / "r4data/soundbanks/Pc/Init.bnk") == NATIVE_INIT
    manifest = json.loads((project / "input-manifest.json").read_text())
    source = redkit / "assets/w3_audio"
    units = {p.relative_to(project).as_posix(): p for p in project.rglob("*.wwu")}
    inputs = {x["relative_path"].replace("\\", "/"): x for x in manifest["inputs"]}
    checks["all_1508_work_units_retained"] = len(units) == 1508 and set(units) == {p for p in inputs if p.endswith(".wwu")}
    checks["unrelated_source_units_original_exact"] = all(digest(p) == inputs[rel]["sha256"] for rel, p in units.items() if rel != "Interactive Music Hierarchy/music.wwu")
    checks["installed_inputs_and_regional_originals_unchanged"] = all(digest(source / x["relative_path"]) == x["sha256"] for x in manifest["inputs"] + manifest["originals"]) and all(digest(project / x["relative_path"]) == x["sha256"] for x in manifest["originals"])
    checks["pinned_fixture_free_D_source"] = digest(project / "Interactive Music Hierarchy/music.wwu") == D_SOURCE and json.loads((project / "transition-clean-authoring.json").read_text())["only_five_static_volumes_changed"]
    # Restore the five volumes, remove only the known C StateInfo, and compare
    # complete music semantics with original authoring source independently.
    tree = ET.parse(project / "Interactive Music Hierarchy/music.wwu").getroot()
    original_tree = ET.parse(source / "Interactive Music Hierarchy/music.wwu").getroot()
    for target in targets.values():
        node = next(n for n in tree.iter("MusicPlaylistContainer") if n.get("ID") == target["id"])
        old_node = next(n for n in original_tree.iter("MusicPlaylistContainer") if n.get("ID") == target["id"])
        if volume(node) != -200:
            raise ValueError("Unexpected source target value")
        props = node.find("PropertyList")
        props.remove(props.find("Property[@Name='Volume']"))
        old = old_node.find("./PropertyList/Property[@Name='Volume']")
        if old is not None:
            props.append(copy.deepcopy(old))
    world = next(n for n in tree.iter("MusicSwitchContainer") if n.get("ShortID") == str(WORLD))
    world.remove(world.find("StateInfo"))
    checks["source_only_C_states_and_five_static_volumes"] = semantic(tree) == semantic(original_tree)
    media = lambda root: {p.relative_to(root / ".cache").as_posix(): digest(p) for p in (root / ".cache").rglob("*.wem")}
    baseline_project = REPO / "build/licensed-white-orchard/baseline"
    checks["all_converted_media_exact_baseline"] = bool(media(project)) and media(project) == media(baseline_project)
    result = {"checks": checks, "passed": all(checks.values()), "C_vs_D": diff, "playlist_fields": decoded,
              "D_header": hd, "D_bank_sha256": db["sha256"], "D_bank_bytes": db["bytes"],
              "D_source_sha256": D_SOURCE, "generation_exit_code": json.loads((d / "result.json").read_text())["exit_code"],
              "warning_rows": sum(diagnostics(d).values()), "runtime_validated": False, "deployed": False}
    output.write_text(json.dumps(result, indent=2) + "\n")
    if not result["passed"]:
        raise ValueError("D gate failed: " + ", ".join(k for k,v in checks.items() if not v))
    print(json.dumps(result))
    return result


def stage(redkit, bank, proof_path, root):
    proof = json.loads(proof_path.read_text())
    if not proof["passed"] or not all(proof["checks"].values()) or digest(bank) != proof["D_bank_sha256"]:
        raise ValueError("Passing matching D audit required")
    root = build_path(root)
    prepare(redkit, root)
    inputs, cooked, split = [root / p for p in ("D-input", "D-cooked", "D-split")]
    inputs.mkdir(); cooked.mkdir()
    shutil.copyfile(bank, inputs / bank.name)
    exe = redkit / "bin/x64_RedKit/wcc_lite.exe"
    execute(exe, root, "D-cook", ["cooksounds", "-soundbanksdir=" + str(inputs) + "\\", "-outdir=" + str(cooked) + "\\", "-platform=pc_dx12", "-r4remastersounds", "-outsplitfile=" + str(cooked / "audio-split.list")])
    cache = verify(cooked / "CookedPC/soundspc.cache", bank)
    execute(exe, root, "D-split", ["splitcache", "sounds", "-platform=pc_dx12", "-split=" + str(cooked / "audio-split.list"), "-file=" + cache["path"], "-outdir=" + str(split) + "\\"])
    readback = verify(split / "content0/soundspc.cache", bank)
    package = root / "packages/D/modWMCBankLoadingTest/content/soundspc.cache"
    package.parent.mkdir(parents=True)
    shutil.copyfile(Path(cache["path"]), package)
    archives = root / "archives"
    archives.mkdir()
    archive = archives / "WMC White Orchard — Transition Fix Test.zip"
    entry = zipfile.ZipInfo(ENTRY, date_time=(2026, 10, 12, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(archive, "x") as zipped:
        zipped.writestr(entry, package.read_bytes())
    with zipfile.ZipFile(archive) as zipped:
        if zipped.namelist() != [ENTRY] or zipped.testzip() or zipped.read(ENTRY) != package.read_bytes():
            raise ValueError("Incorrect ZIP layout/payload")
    if any(digest(root / p) != NATIVE_INIT for p in ("bin/initialdata/sound/Init.bnk", "r4data/soundbanks/Pc/Init.bnk")) or digest(bank) != proof["D_bank_sha256"]:
        raise ValueError("Native bootstrap or candidate changed")
    result = {"bank_sha256": digest(bank), "cache": cache, "native_readback": readback,
              "archive": str(archive), "archive_sha256": digest(archive), "zip_entry": ENTRY,
              "init_in_package": False, "runtime_validated": False, "deployed": False}
    (root / "D-package-verified.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("audit", "package"))
    parser.add_argument("--redkit", type=Path, required=True)
    for name in ("baseline", "c", "d", "project", "output", "bank", "proof", "root"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    required = ("baseline", "c", "d", "project", "output") if args.operation == "audit" else ("bank", "proof", "root")
    if any(getattr(args, name) is None for name in required):
        parser.error("Required arguments: " + ", ".join(required))
    if args.operation == "audit":
        audit(args.redkit, args.baseline, args.c, args.d, args.project, args.output)
    else:
        stage(args.redkit, args.bank, args.proof, args.root)
