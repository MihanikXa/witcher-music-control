"""Record state-gate transitions in the validation workspace only."""
import argparse
import json
from pathlib import Path
import time
from white_orchard_prepare import build_path
from white_orchard_wwise import Waapi


def run(project, port):
    project = build_path(project)
    api = Waapi(port)
    if project.parent.name != "validation" or Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project:
        raise RuntimeError("Requires validation project")
    music = r"\Master-Mixer Hierarchy\Default Work Unit\Master Audio Bus\Immerse\Music"
    world = music + r"\WMC_WorldMusic"
    out = project.parent / "transitions"
    out.mkdir(exist_ok=True)
    def recorder(bus, path):
        slot = api.call("ak.wwise.core.object.get", {"from": {"path": [bus]}},
                        {"return": ["@Effects"]})["return"][0]["@Effects"][-1]["id"]
        effect = api.call("ak.wwise.core.object.get", {"from": {"id": [slot]}},
                          {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
        api.call("ak.wwise.core.object.setProperty", {"object": effect,
            "property": "AuthoringFilename", "value": str(path)})
    recorder(world, out / "world-gates.wav")
    recorder(music, out / "music-gates.wav")
    api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
    transport = api.call("ak.wwise.core.transport.create", {
        "object": r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_TestTone"})["transport"]
    api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": "cutscene"})
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    spec = json.loads(Path("src/wwise/white-orchard-mixer.json").read_text())
    for parameter, value in zip(spec["parameters"].values(), [-12, -24, -6]):
        api.call("ak.soundengine.resetRTPCValue", {"rtpc": parameter["name"]})
        api.call("ak.soundengine.setRTPCValue", {"rtpc": parameter["name"],
            "value": 100 * 10 ** (value / 20), "gameObject": 18446744073709551615})
    started = time.monotonic()
    rows = []
    for state in ("cutscene", "exploration", "dialog_scene", "combat", "cutscene"):
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
        rows.append({"state": state, "wall_seconds": time.monotonic() - started})
        time.sleep(3)
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
    time.sleep(.2)
    (out / "transitions.json").write_text(json.dumps(rows, indent=2) + "\n")
    # Restore the matrix's last raw recording after other music simulations.
    recorder(world, project.parent / "probe/case-30-cutscene.wav")
    recorder(music, out / "matrix-restore-master.wav")
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    for parameter in spec["parameters"].values():
        api.call("ak.soundengine.resetRTPCValue", {"rtpc": parameter["name"]})
        api.call("ak.soundengine.setRTPCValue", {"rtpc": parameter["name"], "value": 0,
                                              "gameObject": 18446744073709551615})
    time.sleep(2)
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "stop"})
    print(json.dumps({"states": rows, "output": str(out)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()
    run(args.project, args.port)
