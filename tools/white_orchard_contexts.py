"""White Orchard authoring simulations and protected-path/master-volume probes."""
import argparse
import json
from pathlib import Path
import time
from white_orchard_prepare import build_path
from white_orchard_wwise import Waapi


def run(project, port, native_fade=False):
    project = build_path(project)
    api = Waapi(port)
    if project.parent.name != "validation" or Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project:
        raise RuntimeError("Requires the separate validation project")
    out = project.parent / ("contexts-native-fade" if native_fade else "contexts")
    out.mkdir(exist_ok=True)
    api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
    music = r"\Master-Mixer Hierarchy\Default Work Unit\Master Audio Bus\Immerse\Music"
    world = music + r"\WMC_WorldMusic"
    sound = r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_TestTone"
    config = json.loads(Path("src/wwise/white-orchard-mixer.json").read_text())
    world_slots = api.call("ak.wwise.core.object.get", {"from": {"path": [world]}},
                           {"return": ["@Effects"]})["return"][0]["@Effects"]
    world_recorder = api.call("ak.wwise.core.object.get", {"from": {"id": [world_slots[-1]["id"]]}},
                             {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
    api.call("ak.wwise.core.object.setProperty", {"object": world_recorder,
        "property": "AuthoringFilename", "value": str(out / "native_world.wav")})
    def rtpc(name, value):
        api.call("ak.soundengine.resetRTPCValue", {"rtpc": name})
        api.call("ak.soundengine.setRTPCValue", {"rtpc": name, "value": value,
                                             "gameObject": 18446744073709551615})
    def gains(values):
        for parameter, value in zip(config["parameters"].values(), values):
            rtpc(parameter["name"], value)
    existing = api.call("ak.wwise.core.object.get", {"from": {"path": [music]}},
                        {"return": ["@Effects"]})["return"][0].get("@Effects", [])
    if not existing:
        api.call("ak.wwise.core.object.set", {"objects": [{"object": music,
            "@Effects": [{"type": "EffectSlot", "name": "", "@Effect": {
                "type": "Effect", "name": "WMC_TestMusicRecorder", "classId": 8650755,
                "@DownmixToStereo": False, "@ApplyDownstreamVolume": True,
                "@AuthoringFilename": str(out / "initial.wav")}}]}]})
    elif len(existing) != 1:
        raise RuntimeError("Unexpected Music validation effect count")
    slot = api.call("ak.wwise.core.object.get", {"from": {"path": [music]}},
                    {"return": ["@Effects"]})["return"][0]["@Effects"][-1]["id"]
    recorder = api.call("ak.wwise.core.object.get", {"from": {"id": [slot]}},
                        {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
    def filename(name):
        api.call("ak.wwise.core.object.setProperty", {
            "object": recorder, "property": "AuthoringFilename", "value": str(out / (name + ".wav"))})
    def snapshot(label):
        voices = api.call("ak.wwise.core.profiler.getVoices", {"time": "capture"},
            {"return": ["pipelineID", "objectGUID", "objectName", "baseVolume", "isVirtual", "isStarted"]})
        buses = api.call("ak.wwise.core.profiler.getBusses", {"time": "capture"},
            {"return": ["pipelineID", "objectGUID", "objectName", "volume", "effectCount"]})
        contributions = [api.call("ak.wwise.core.profiler.getVoiceContributions", {
            "voicePipelineID": v["pipelineID"], "time": "capture"}) for v in voices["return"][:4]]
        return {"label": label, "voices": voices, "busses": buses, "contributions": contributions}
    api.call("ak.wwise.core.profiler.startCapture")
    evidence = {"synthetic": [], "white_orchard": [], "live_game_test": False}
    # A test source routed directly to Music represents the protected routing,
    # without modifying any actual quest container or cue.
    api.call("ak.wwise.core.object.set", {"objects": [{"object": sound, "@OutputBus": music,
        # The parallel experiment adds fixture sends; a protected test source
        # must inherit native sends when routed directly to Music.
        "@OverrideUserAuxSends": False}]})
    if native_fade:
        # This Sound is a root audio node directly in a WorkUnit: disabling the
        # override flag alone does not discard its previously explicit sends.
        for index in range(4):
            api.call("ak.wwise.core.object.setReference", {"object": sound,
                "reference": "UserAuxSend" + str(index),
                "value": "{00000000-0000-0000-0000-000000000000}"})
    transport = api.call("ak.wwise.core.transport.create", {"object": sound})["transport"]
    for name, values, master in [("protected_all_zero", [0, 0, 0], 100),
                                 ("protected_all_unity", [100, 100, 100], 100),
                                 ("protected_music_half", [0, 0, 0], 50)]:
        filename(name)
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": "dialog_scene"})
        api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
        gains(values)
        rtpc("menu_volume_music", master)
        time.sleep(2)
        evidence["synthetic"].append({**snapshot(name), "parameters_percent": values, "music_percent": master,
                                      "recording": str(out / (name + ".wav"))})
        api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
        time.sleep(.2)
    api.call("ak.wwise.core.object.set", {"objects": [{"object": sound, "@OutputBus": world}]})
    filename("native_white_orchard")
    event = r"\Events\music\prologue\play_music_prologue"
    transport = api.call("ak.wwise.core.transport.create", {"object": event})["transport"]
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    gains([100, 100, 100])
    rtpc("menu_volume_music", 100)
    api.call("ak.soundengine.postEvent", {"event": "mus_loc_prologue_village", "gameObject": 18446744073709551614})
    for name, state, cue, values, seconds in [
        ("village_exploration_baseline", "exploration", None, [100, 100, 100], 4),
        ("village_exploration_attenuated", "exploration", None, [0, 0, 100], 3),
        ("village_generic_dialogue", "dialog_scene", None, [0, 0, 100], 3),
        ("village_combat", "combat", None, [0, 0, 100], 6),
        ("q001_tavern_intro", "cutscene", "mus_cs001_tavern_intro", [0, 0, 100], 5),
        ("q001_authored_dialogue", "dialog_scene", "mus_q001_tavern_conversation", [0, 0, 100], 6)]:
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
        gains(values)
        if cue:
            api.call("ak.soundengine.postEvent", {"event": cue, "gameObject": 18446744073709551614})
        time.sleep(seconds)
        evidence["white_orchard"].append({**snapshot(name), "state": state, "event": cue,
                                          "parameters_percent": values})
        (out / "contexts.json").write_text(json.dumps(evidence, indent=2) + "\n")
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
    # The intro segment is 82.667 seconds. A short event sequence may leave
    # its native scheduled transition pending; independently exercise the
    # exact conversation playlist without claiming the cinematic was replayed.
    filename("q001_conversation_direct")
    transport = api.call("ak.wwise.core.transport.create", {
        "object": "{EFA886D9-2BAD-4354-9DC3-BC08E2E75727}"})["transport"]
    api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": "dialog_scene"})
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    gains([0, 0, 100])
    rtpc("menu_volume_music", 100)
    time.sleep(3)
    evidence["white_orchard"].append({**snapshot("q001_conversation_direct"),
        "state": "dialog_scene", "direct_playlist": "{EFA886D9-2BAD-4354-9DC3-BC08E2E75727}",
        "parameters_percent": [0, 0, 100]})
    (out / "contexts.json").write_text(json.dumps(evidence, indent=2) + "\n")
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
    api.call("ak.wwise.core.profiler.stopCapture")
    print(json.dumps({"synthetic_cases": len(evidence["synthetic"]),
                      "white_orchard_cases": len(evidence["white_orchard"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--port", type=int, default=18090)
    parser.add_argument("--native-fade", action="store_true")
    args = parser.parse_args()
    run(args.project, args.port, args.native_fade)
