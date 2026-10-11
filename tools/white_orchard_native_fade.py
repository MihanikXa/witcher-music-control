"""Validation-only parallel Wwise State-volume experiment; never shipping source.

Four auxiliary paths provide three independently controlled contexts and one
unity path for other states. A separate muted dry bus prevents duplicate audio.
No vanilla state timing, event, playlist or threat control is changed.
"""
import argparse
import json
from pathlib import Path
import time
import wave
import xml.etree.ElementTree as ET
from white_orchard_prepare import build_path, CONFIG
from white_orchard_wwise import Waapi


def run(project, port):
    project = build_path(project)
    api = Waapi(port)
    if project.parent.name != "validation" or Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project:
        raise RuntimeError("Requires isolated validation project")
    api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
    spec = json.loads(CONFIG.read_text())
    out = project.parent / "native-fade"
    if out.exists():
        raise FileExistsError("Preserve earlier measurements; use a fresh validation copy")
    out.mkdir()
    bus = r"\Master-Mixer Hierarchy\Default Work Unit\Master Audio Bus\Immerse\Music\WMC_WorldMusic"
    sound = r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_TestTone"
    api.call("ak.wwise.core.object.setStateGroups", {"object": bus, "stateGroups": []})
    api.call("ak.wwise.core.object.setStateProperties", {"object": bus, "stateProperties": []})
    api.call("ak.wwise.core.object.set", {"objects": [{"object": bus,
        "@Effects": [{"type": "EffectSlot", "name": "", "@Effect": {
            "type": "Effect", "name": "WMC_FadeRecorder", "classId": 8650755,
            "@AuthoringFilename": str(out / "transitions.wav"), "@DownmixToStereo": False}}],
        "listMode": "replaceAll"}]})
    dry = api.call("ak.wwise.core.object.create", {
        "parent": bus, "type": "Bus", "name": "WMC_DryMuted", "onNameConflict": "merge"})["id"]
    api.call("ak.wwise.core.object.setProperty", {"object": dry, "property": "BusVolume", "value": -200})
    paths = {}
    for category in [*spec["parameters"], "other"]:
        obj = api.call("ak.wwise.core.object.create", {
            "parent": bus, "type": "AuxBus", "name": "WMC_Fade_" + category, "onNameConflict": "merge"})
        paths[category] = obj["id"]
        # Numeric State volumes add to the base property. Unity base is required.
        api.call("ak.wwise.core.object.setProperty", {"object": obj["id"], "property": "BusVolume", "value": 0})
        if category != "other":
            parameter = r"\Game Parameters\Default Work Unit" + "\\" + spec["parameters"][category]["name"]
            curve = {"type": "Curve", "points": [
                {"x": 0, "y": spec["minimum_db"], "shape": "Linear"}, {"x": 100, "y": 0, "shape": "Linear"}]}
            api.call("ak.wwise.core.object.set", {"objects": [{"object": obj["id"], "@Effects": [{
                "type": "EffectSlot", "name": "", "@Effect": {"type": "Effect",
                "name": "WMC_Continuous_" + category, "classId": spec["gain_plugin_class_id"],
                "@RTPC": [{"type": "RTPC", "name": "", "@PropertyName": prop,
                           "@ControlInput": parameter, "@Curve": curve} for prop in ("FullBandGain", "LFEGain")]}}],
                "listMode": "replaceAll"}]})
        api.call("ak.wwise.core.object.setStateProperties", {"object": obj["id"], "stateProperties": ["BusVolume"]})
        api.call("ak.wwise.core.object.setStateGroups", {"object": obj["id"], "stateGroups": ["{27711515-3584-4123-9F09-B90831398B80}"]})
    api.call("ak.wwise.core.project.save")
    xml = ET.parse(project.parent / "Master-Mixer Hierarchy/Default Work Unit.wwu")
    tables = {}
    for category, ident in paths.items():
        aux = next(x for x in xml.iter("AuxBus") if x.get("ID") == ident)
        for override in aux.findall("./StateInfo/CustomStateList/CustomState"):
            state = override.find("StateRef").get("Name")
            active = (state in spec["active_states"][category] if category != "other" else
                      not any(state in states for states in spec["active_states"].values()))
            value = 0 if active else -200
            api.call("ak.wwise.core.object.setProperty", {"object": override.find("CustomState").get("ID"),
                "property": "BusVolume", "value": value})
            tables.setdefault(state, {})[category] = value
    # Send overrides belong only to the world root and synthetic fixture.
    routing = {"@OverrideOutput": True, "@OutputBus": dry, "@OverrideUserAuxSends": True}
    routing.update({"@UserAuxSend" + str(i): ident for i, ident in enumerate(paths.values())})
    routing.update({"@UserAuxSendVolume" + str(i): 0 for i in range(4)})
    for obj in (sound, "{1A59CC64-141A-45A6-8374-EB823D3E9D4F}"):
        api.call("ak.wwise.core.object.set", {"objects": [{"object": obj, **routing}]})
    api.call("ak.wwise.core.project.save")
    slot = api.call("ak.wwise.core.object.get", {"from": {"path": [bus]}}, {"return": ["@Effects"]})["return"][0]["@Effects"][-1]["id"]
    recorder = api.call("ak.wwise.core.object.get", {"from": {"id": [slot]}}, {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
    # Keep the recorder's mixing bus alive when all test gains reach zero.
    # This silent fixture has unity authored volume and no shipping equivalent.
    anchor_audio = out / "silent-anchor.wav"
    with wave.open(str(anchor_audio), "wb") as wav:
        wav.setparams((6, 2, 48000, 0, "NONE", "not compressed"))
        for _ in range(150):
            wav.writeframesraw(bytes(48000 * 6 * 2))
    anchor = r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_RecorderAnchor"
    api.call("ak.wwise.core.audio.import", {"importOperation": "useExisting",
        "autoAddToSourceControl": False, "autoCheckOutToSourceControl": False,
        "imports": [{"objectPath": anchor, "objectType": "Sound", "audioFile": str(anchor_audio),
                     "@OverrideOutput": True, "@OutputBus": bus}]})
    api.call("ak.wwise.core.object.set", {"objects": [{"object": anchor,
        "@OverrideVirtualVoice": True, "@BelowThresholdBehavior": 0}]})
    anchor_transport = api.call("ak.wwise.core.transport.create", {"object": anchor})["transport"]
    api.call("ak.wwise.core.profiler.startCapture")
    evidence = {"paths": paths, "dry_bus": dry, "state_table": tables, "runs": [], "shipping": False}
    transport = api.call("ak.wwise.core.transport.create", {"object": sound})["transport"]
    for label, values in [("unequal", [25.118864, 6.309573, 50.118723]),
                          ("all_unity", [100, 100, 100]), ("defaults", [0, 0, 100])]:
        api.call("ak.wwise.core.object.setProperty", {"object": recorder,
            "property": "AuthoringFilename", "value": str(out / (label + ".wav"))})
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": "cutscene"})
        api.call("ak.wwise.core.transport.executeAction", {"transport": anchor_transport, "action": "play"})
        api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
        for parameter, value in zip(spec["parameters"].values(), values):
            api.call("ak.soundengine.resetRTPCValue", {"rtpc": parameter["name"]})
            api.call("ak.soundengine.setRTPCValue", {"rtpc": parameter["name"], "value": value, "gameObject": 18446744073709551615})
        started = time.monotonic()
        rows = []
        for state in ("cutscene", "exploration", "dialog_scene", "combat", "cutscene"):
            api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
            rows.append({"state": state, "wall_seconds": time.monotonic() - started})
            time.sleep(4)
        buses = api.call("ak.wwise.core.profiler.getBusses", {"time": "capture"},
                        {"return": ["objectName", "volume", "effectCount"]})
        api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
        time.sleep(.25)
        evidence["runs"].append({"label": label, "percent": values, "states": rows, "busses": buses})
        (out / "results.json").write_text(json.dumps(evidence, indent=2) + "\n")
    api.call("ak.wwise.core.profiler.stopCapture")
    print(json.dumps({"output": str(out), "runs": len(evidence["runs"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()
    run(args.project, args.port)
