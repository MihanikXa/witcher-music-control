"""Add measured generic-playlist attenuation to a fresh complete Stage 1 copy.

Requires white_orchard_state_volume_author.py first. Never generates banks.
"""
import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path, digest
from white_orchard_state_volume_author import semantic, WORK_UNIT, REPO
from white_orchard_wwise import Waapi


def volume(node):
    prop = node.find("./PropertyList/Property[@Name='Volume']")
    if prop is None:
        return 0.0
    return float(prop.get("Value") if prop.get("Value") is not None else prop.findtext("./ValueList/Value"))


def author(project, port):
    project = build_path(project)
    workspace = project.parent
    if workspace.name == "validation" or not project.is_file():
        raise ValueError("Fresh production copy required, never fixture source")
    audit = workspace / "transition-clean-authoring.json"
    if audit.exists():
        raise FileExistsError(audit)
    prior = json.loads((workspace / "state-volume-clean-authoring.json").read_text())
    if not prior["music_changes_only_world_state_info"] or prior["production_audio_fixtures"]:
        raise ValueError("Clean Stage 1 source proof required")
    spec = json.loads((REPO / "src/wwise/white-orchard-transition-fix.json").read_text())
    before = ET.parse(workspace / WORK_UNIT).getroot()
    parents = {c: n for n in before.iter() for c in n}
    originals = {}
    for target in spec["targets"]:
        node = next(n for n in before.iter("MusicPlaylistContainer") if n.get("ID") == target["id"])
        if node.get("Name") != target["name"] or int(node.get("ShortID")) != target["short_id"] or volume(node) != target["original_volume_db"]:
            raise ValueError("Unexpected target identity/property: " + target["name"])
        ancestor = node
        while ancestor in parents and ancestor.get("ID") != spec["world_id"]:
            ancestor = parents[ancestor]
        if ancestor.get("ID") != spec["world_id"]:
            raise ValueError("Target outside world_music")
        originals[target["id"]] = copy.deepcopy(node.find("./PropertyList/Property[@Name='Volume']"))
    target_ids = set(originals)
    consumer_count = 0
    for reference in before.iter("Reference"):
        obj = reference.find("ObjectRef")
        if reference.get("Name") != "AudioNode" or obj is None or obj.get("ID") not in target_ids:
            continue
        ancestor = reference
        while ancestor in parents and ancestor.get("ID") != spec["world_id"]:
            ancestor = parents[ancestor]
        if ancestor.get("ID") != spec["world_id"]:
            raise ValueError("Generic target reused outside world_music")
        consumer_count += 1
    if consumer_count != 40:
        raise ValueError("Unexpected selector consumer count")
    for unit in (workspace / "Events").rglob("*.wwu"):
        if any(obj.get("ID") in target_ids for obj in ET.parse(unit).iter("ObjectRef")):
            raise ValueError("Direct event targets a proposed generic playlist")
    if any((n.get("Name") or "").startswith("WMC_") for n in before.iter()):
        raise ValueError("Measurement fixtures found")
    units = {p: digest(p) for p in workspace.rglob("*.wwu")}
    if len(units) != 1508:
        raise ValueError("Expected complete 1508-work-unit context")
    api = Waapi(port)
    if Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project or api.call("ak.wwise.core.getInfo")["version"]["build"] != spec["wwise_build"]:
        raise ValueError("Wrong open project/version")
    for target in spec["targets"]:
        api.call("ak.wwise.core.object.setProperty", {"object": target["id"], "property": "Volume", "value": spec["volume_db"]})
    api.call("ak.wwise.core.project.save")
    after = ET.parse(workspace / WORK_UNIT).getroot()
    for target in spec["targets"]:
        node = next(n for n in after.iter("MusicPlaylistContainer") if n.get("ID") == target["id"])
        if volume(node) != spec["volume_db"]:
            raise ValueError("Volume edit did not serialize")
        props = node.find("PropertyList")
        props.remove(props.find("Property[@Name='Volume']"))
        original = originals[target["id"]]
        if original is not None:
            props.append(original)
    exact = semantic(before) == semantic(after)
    changed = [str(p.relative_to(workspace)) for p, sha in units.items() if digest(p) != sha]
    unexpected = [p for p in changed if Path(p).as_posix() not in {WORK_UNIT.as_posix(), "Control Surface Sessions/Default Work Unit.wwu"}]
    result = {"targets": spec["targets"], "volume_db": spec["volume_db"], "only_five_static_volumes_changed": exact,
              "unchanged_C_state_table_and_native_transitions": exact, "changed_units": changed,
              "unrelated_changes": unexpected, "source_sha256": digest(workspace / WORK_UNIT),
              "work_units": len(units), "world_only_audio_node_consumers": consumer_count,
              "direct_event_targets": 0, "fixtures": False, "generated_banks": False, "deployable": False}
    audit.write_text(json.dumps(result, indent=2) + "\n")
    if not exact or unexpected or set(units) != set(workspace.rglob("*.wwu")):
        raise RuntimeError("Unexpected source delta; inspect retained evidence")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()
    author(args.project, args.port)
