"""Validation-only synthetic 5.1 probe; never generate banks from this project."""
import argparse
import array
import json
import math
from pathlib import Path
import time
import wave
from white_orchard_prepare import build_path
from white_orchard_wwise import Waapi


def probe(project, port):
    project = build_path(project)
    if project.parent.name != "validation":
        raise ValueError("Probe requires the separate validation workspace")
    api = Waapi(port)
    if Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project:
        raise RuntimeError("Unexpected open project")
    out = project.parent / "probe"
    out.mkdir(exist_ok=True)
    audio = out / "six-channel-tone.wav"
    # Equal input amplitudes, distinct full-band tones and 60 Hz LFE (channel 4).
    frames = array.array("h")
    frequencies = (300, 400, 500, 60, 600, 700)
    for i in range(48000):
        frames.extend(round(12000 * math.sin(2 * math.pi * f * i / 48000)) for f in frequencies)
    with wave.open(str(audio), "wb") as wav:
        wav.setparams((6, 2, 48000, 0, "NONE", "not compressed"))
        for _ in range(150):
            wav.writeframesraw(frames.tobytes())
    sound = r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_TestTone"
    music = r"\Master-Mixer Hierarchy\Default Work Unit\Master Audio Bus\Immerse\Music"
    bus = music + r"\WMC_WorldMusic"
    result = api.call("ak.wwise.core.audio.import", {
        "importOperation": "useExisting", "autoAddToSourceControl": False,
        "autoCheckOutToSourceControl": False,
        "imports": [{"objectPath": sound, "objectType": "Sound",
                     "audioFile": str(audio), "@OverrideOutput": True, "@OutputBus": bus}]})
    api.call("ak.wwise.core.object.set", {"objects": [{"object": sound,
        "@OverrideVirtualVoice": True, "@BelowThresholdBehavior": 0}]})
    # Explicit 5.1 is restricted to this probe project. Shipping bus inherits.
    api.call("ak.wwise.core.object.setProperty", {
        "object": bus, "property": "BusChannelConfig", "value": 6353158})
    recording = out / "mixer-matrix.wav"
    existing = api.call("ak.wwise.core.object.get", {"from": {"path": [bus]}},
                        {"return": ["@Effects"]})["return"][0]["@Effects"]
    if len(existing) == 3:
        recorder = api.call("ak.wwise.core.object.set", {"objects": [{
            "object": bus, "@Effects": [{"type": "EffectSlot", "name": "",
            "@Effect": {"type": "Effect", "name": "WMC_TestRecorder", "classId": 8650755,
            "@AuthoringFilename": str(recording), "@DownmixToStereo": False}}]}]})
    elif len(existing) == 4:
        recorder = {"existing_slot": existing[-1]["id"]}
    else:
        raise RuntimeError("Unexpected validation effect count")
    existing = api.call("ak.wwise.core.object.get", {"from": {"path": [bus]}},
                        {"return": ["@Effects"]})["return"][0]["@Effects"]
    recorder_id = api.call("ak.wwise.core.object.get", {"from": {"id": [existing[-1]["id"]]}},
                           {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
    transport = api.call("ak.wwise.core.transport.create", {"object": sound})["transport"]
    api.call("ak.wwise.core.profiler.startCapture")
    config = json.loads(Path("src/wwise/white-orchard-mixer.json").read_text())
    evidence = {"import": result, "recorder": recorder, "cases": [], "recording": str(recording)}
    tests = [("cutscene", [0, 0, 0])] + [(s, [-12, -24, -6]) for s in json.loads(
        (project.parent / "mixer-authoring.json").read_text())["bypass_truth_table"]]
    tests += [("exploration", [0, -96.3, -96.3]),
              ("dialog_scene", [-96.3, 0, -96.3]), ("combat", [-96.3, -96.3, 0]),
              ("exploration", [-96.3, 0, 0]), ("cutscene", [-96.3, -96.3, -96.3])]
    for number, (state, values) in enumerate(tests):
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
        recording = out / f"case-{number:02d}-{state}.wav"
        api.call("ak.wwise.core.object.setProperty", {
            "object": recorder_id, "property": "AuthoringFilename", "value": str(recording)})
        time.sleep(.25)
        api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
        # Transport startup restores authoring defaults. Apply test globals
        # afterward, and clear transport-local overrides so scope is verified.
        for parameter, value in zip(config["parameters"].values(), values):
            api.call("ak.soundengine.resetRTPCValue", {"rtpc": parameter["name"]})
            api.call("ak.soundengine.setRTPCValue", {
                "rtpc": parameter["name"], "value": 0 if value == -96.3 else 100 * 10 ** (value / 20),
                "gameObject": 18446744073709551615})
        time.sleep(2)
        row = {"state": state, "values_db": values, "recording": str(recording),
               "busses": api.call("ak.wwise.core.profiler.getBusses", {"time": "capture"},
                                  {"return": ["pipelineID", "objectName", "effectCount", "volume"]}),
               "voices": api.call("ak.wwise.core.profiler.getVoices", {"time": "capture"},
                                   {"return": ["pipelineID", "objectName", "isVirtual", "isStarted"]}),
               "rtpcs": [p for p in api.call("ak.wwise.core.profiler.getRTPCs", {"time": "capture"})["return"]
                         if p["name"].startswith("WMC_")]}
        api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
        time.sleep(.2)
        row["file_exists"] = recording.exists()
        evidence["cases"].append(row)
        (out / "matrix.json").write_text(json.dumps(evidence, indent=2) + "\n")
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
    api.call("ak.wwise.core.profiler.stopCapture")
    print(json.dumps({"cases": len(tests), "recording": str(recording), "bytes": recording.stat().st_size}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()
    probe(args.project, args.port)
