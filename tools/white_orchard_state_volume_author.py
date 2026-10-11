"""Author Stage 1 directly on world_music, in a COMPLETE isolated Wwise project.

No sound import, bus/effect/RTPC creation, bank generation or game deployment.
Run from repository root with a matching localhost Wwise WAAPI server.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path, digest
from white_orchard_wwise import Waapi

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "src/wwise/white-orchard-state-volume.json"
WORK_UNIT = Path("Interactive Music Hierarchy/music.wwu")
AUDIT = "state-volume-clean-authoring.json"


def author(project, port=18090):
    project = build_path(project)
    if project.name != "w3_audio.wproj" or not project.is_file():
        raise ValueError("Supply an existing isolated w3_audio.wproj")
    workspace = project.parent
    if workspace.name == "validation":
        raise ValueError("Never author production source inside the validation workspace")
    if (workspace / AUDIT).exists():
        raise FileExistsError("Existing authoring evidence; prepare a fresh workspace")
    if (workspace / "mixer-authoring.json").exists():
        raise ValueError("Do not reuse the previous custom-bus authoring workspace")

    manifest = json.loads((workspace / "input-manifest.json").read_text())
    if "Preserved all work units" not in " ".join(str(x) for x in manifest["changes"]):
        raise ValueError("Stage 1 requires --preserve-hierarchies, not a pruned project")
    all_units = sorted(workspace.rglob("*.wwu"))
    if len(all_units) < 1508:
        raise ValueError("Incomplete work-unit copy: expected at least 1508")
    hashes = {str(p.relative_to(workspace)): digest(p) for p in all_units}

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    target_path = workspace / WORK_UNIT
    tree = ET.parse(target_path)
    world = next((x for x in tree.iter("MusicSwitchContainer")
                  if x.get("ID") == spec["world_id"]), None)
    if world is None or int(world.get("ShortID")) != spec["world_short_id"] or world.get("Name") != "world_music":
        raise ValueError("Unexpected world_music object or ShortID")
    if world.find("StateInfo") is not None:
        raise ValueError("Existing world StateInfo: preserve evidence and inspect before replacing")

    categories = spec["active_states"]
    memberships = {}
    for category, states in categories.items():
        for state in states:
            if state in memberships:
                raise ValueError("Overlapping categories for State " + state)
            memberships[state] = category

    api = Waapi(port)
    info = api.call("ak.wwise.core.getInfo")
    opened = Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve()
    if opened != project.resolve() or info["version"]["build"] != spec["wwise_build"]:
        raise ValueError("Wrong project or Wwise build; refusing edit")
    # The StateGroup already exists. Only its association to the existing
    # world node and locally owned State property overrides are created.
    api.call("ak.wwise.core.object.setStateProperties", {
        "object": spec["world_id"], "stateProperties": [spec["volume_property"]]})
    api.call("ak.wwise.core.object.setStateGroups", {
        "object": spec["world_id"], "stateGroups": [spec["game_state_group_id"]]})
    api.call("ak.wwise.core.project.save")
    updated = ET.parse(target_path)
    updated_world = next(x for x in updated.iter("MusicSwitchContainer")
                         if x.get("ID") == spec["world_id"])
    state_map = {}
    for row in updated_world.findall("./StateInfo/CustomStateList/CustomState"):
        name = row.find("StateRef").get("Name")
        nested = row.find("CustomState")
        if name in state_map:
            raise ValueError("Duplicate State: " + name)
        state_map[name] = nested.get("ID")
    if len(state_map) != spec["expected_states"]:
        raise ValueError(f"Expected {spec['expected_states']} States, found {len(state_map)}")
    if set(memberships) - set(state_map):
        raise ValueError("Some required States are missing")

    state_table = {}
    for name, obj_id in sorted(state_map.items()):
        category = memberships.get(name, "other")
        gain = spec["volume_db"][category]
        api.call("ak.wwise.core.object.setProperty", {
            "object": obj_id, "property": "Volume", "value": gain})
        state_table[name] = {"category": category, "voice_volume_db": gain}
    api.call("ak.wwise.core.project.save")

    changed = [p for p in all_units if digest(p) != hashes[str(p.relative_to(workspace))]]
    allowed = {WORK_UNIT.as_posix(), "Control Surface Sessions/Default Work Unit.wwu"}
    unexpected = [str(p.relative_to(workspace)) for p in changed
                  if p.relative_to(workspace).as_posix() not in allowed]
    evidence = {
        "project": str(project), "wwise_build": info["version"]["build"],
        "world_id": spec["world_id"], "world_short_id": spec["world_short_id"],
        "state_table": state_table,
        "modified_units": [str(p.relative_to(workspace)) for p in changed],
        "unrelated_work_units_changed": unexpected,
        "production_audio_fixtures": False, "generated_banks": False,
        "deployable": False
    }
    (workspace / AUDIT).write_text(json.dumps(evidence, indent=2) + "\n")
    if unexpected:
        raise RuntimeError("Unrelated work units changed; inspect audit before proceeding")
    print(json.dumps({"world": spec["world_id"], "states": len(state_table),
                      "changed_units": evidence["modified_units"],
                      "generated_banks": False}))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--port", default=18090, type=int)
    args = p.parse_args()
    author(args.project, args.port)
