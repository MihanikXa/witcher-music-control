"""Author only the isolated White Orchard mixer through installed Wwise WAAPI."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from white_orchard_prepare import build_path
from white_orchard_wwise import Waapi


def author(project, config, port):
    project = build_path(project)
    api = Waapi(port)
    info = api.call("ak.wwise.core.getProjectInfo")
    if Path(info["path"]).resolve() != project.resolve():
        raise RuntimeError("WAAPI has a different project open; refusing mutation")
    spec = json.loads(config.read_text())
    version = api.call("ak.wwise.core.getInfo")
    if version["version"]["build"] != int(spec["wwise_build"]):
        raise RuntimeError("Unexpected Wwise build")
    music = r"\Master-Mixer Hierarchy\Default Work Unit\Master Audio Bus\Immerse\Music"
    bus = music + "\\" + spec["bus_name"]
    api.call("ak.wwise.core.object.create", {
        "parent": music, "type": "Bus", "name": spec["bus_name"], "onNameConflict": "merge"})
    parameters = {}
    existing_parameters = api.call("ak.wwise.core.object.get", {"from": {"ofType": ["GameParameter"]}},
                                   {"return": ["id", "path"]})["return"]
    for category, parameter in spec["parameters"].items():
        legacy = r"\Game Parameters\Default Work Unit\WMC_" + category.title() + "GainDb"
        old = [obj for obj in existing_parameters if obj["path"] == legacy]
        if old:
            api.call("ak.wwise.core.object.setName", {"object": old[0]["id"], "value": parameter["name"]})
        obj = api.call("ak.wwise.core.object.create", {
            "parent": r"\Game Parameters\Default Work Unit", "type": "GameParameter",
            "name": parameter["name"], "onNameConflict": "merge"})
        parameters[category] = obj["id"]
        api.call("ak.wwise.core.object.set", {"objects": [{
            "object": obj["id"], "@Min": 0, "@Max": 100,
            "@InitialValue": parameter["default_percent"]}]})
    slots = []
    for category in spec["parameters"]:
        curve = {"type": "Curve", "points": [
            {"x": 0, "y": spec["minimum_db"], "shape": "Linear"},
            {"x": 100, "y": 0, "shape": "Linear"}]}
        rtpcs = [{"type": "RTPC", "name": "", "@PropertyName": prop,
                  "@ControlInput": parameters[category], "@Curve": curve}
                 for prop in ("FullBandGain", "LFEGain")]
        slots.append({"type": "EffectSlot", "name": "", "@Bypass": True,
                      "@Effect": {"type": "Effect", "name": "WMC_" + category.title() + "Gain",
                                  "classId": spec["gain_plugin_class_id"], "@RTPC": rtpcs}})
    result = api.call("ak.wwise.core.object.set", {"objects": [{
        "object": bus, "@Effects": slots, "listMode": "replaceAll"}]},
        {"return": ["id", "name", "@Effects"]})
    slot_ids = [s["id"] for s in result["objects"][0]["@Effects"]]
    for slot in slot_ids:
        api.call("ak.wwise.core.object.setStateProperties", {
            "object": slot, "stateProperties": ["Bypass"]})
    state_group = "{27711515-3584-4123-9F09-B90831398B80}"
    # State groups belong to the owning bus, not its locally owned EffectSlot.
    api.call("ak.wwise.core.object.setStateGroups", {
        "object": bus, "stateGroups": [state_group]})
    api.call("ak.wwise.core.project.save")
    master = project.parent / "Master-Mixer Hierarchy" / "Default Work Unit.wwu"
    root = ET.parse(master)
    bus_xml = next(b for b in root.iter("Bus") if b.get("Name") == spec["bus_name"])
    truth_table = {}
    for category, slot_id in zip(spec["parameters"], slot_ids):
        slot_xml = next(s for s in bus_xml.iter("EffectSlot") if s.get("ID") == slot_id)
        for override in slot_xml.findall("./StateInfo/CustomStateList/CustomState"):
            state = override.find("StateRef").get("Name")
            custom_id = override.find("CustomState").get("ID")
            bypass = state not in spec["active_states"][category]
            api.call("ak.wwise.core.object.setProperty", {
                "object": custom_id, "property": "Bypass", "value": bypass})
            truth_table.setdefault(state, {})[category] = bypass
    world = "{1A59CC64-141A-45A6-8374-EB823D3E9D4F}"
    api.call("ak.wwise.core.object.set", {"objects": [{
        "object": world, "@OverrideOutput": True, "@OutputBus": bus}]})
    api.call("ak.wwise.core.project.save")
    evidence = {"project": str(project), "wwise": version, "objects": result,
                "parameters": parameters, "bypass_truth_table": truth_table,
                "deployment_authorized": False}
    (project.parent / "mixer-authoring.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"project": str(project), "states": len(truth_table), "slots": len(slot_ids)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("src/wwise/white-orchard-mixer.json"))
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()
    author(args.project, args.config, args.port)
