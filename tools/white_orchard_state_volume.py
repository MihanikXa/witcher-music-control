"""Isolated authoring-only State Voice Volume proof. Never generates banks/Init."""
import argparse
import array
import json
import math
from pathlib import Path
import time
import wave
import xml.etree.ElementTree as ET
from white_orchard_prepare import build_path, digest, CONFIG
from white_orchard_wwise import Waapi

WORLD = "{1A59CC64-141A-45A6-8374-EB823D3E9D4F}"
GROUP = "{27711515-3584-4123-9F09-B90831398B80}"
MUSIC = r"\Master-Mixer Hierarchy\Default Work Unit\Master Audio Bus\Immerse\Music"


def run(project, capture_name="state-volume", anchor=False):
    project = build_path(project)
    api = Waapi()
    if project.parent.name != "validation" or Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project:
        raise RuntimeError("Requires the fresh isolated validation project")
    if Path(capture_name).name != capture_name:
        raise ValueError("Capture name must be a simple directory name")
    out = project.parent / capture_name
    if out.exists():
        raise FileExistsError(out)
    out.mkdir()
    info = api.call("ak.wwise.core.getInfo")
    assert info["version"]["build"] == 8928
    spec = json.loads(CONFIG.read_text())
    units = {str(p.relative_to(project.parent)): digest(p) for p in project.parent.rglob("*.wwu")}
    api.call("ak.wwise.core.object.setStateProperties", {"object": WORLD, "stateProperties": ["Volume"]})
    api.call("ak.wwise.core.object.setStateGroups", {"object": WORLD, "stateGroups": [GROUP]})
    api.call("ak.wwise.core.project.save")
    xml = ET.parse(project.parent / "Interactive Music Hierarchy/music.wwu")
    world = next(x for x in xml.iter("MusicSwitchContainer") if x.get("ID") == WORLD)
    overrides = {x.find("StateRef").get("Name"): x.find("CustomState").get("ID")
                 for x in world.findall("./StateInfo/CustomStateList/CustomState")}
    assert len(overrides) == 25

    def levels(e, d, c):
        table = {}
        for state, ident in overrides.items():
            level = next((value for cat, value in zip(("exploration", "dialogue", "combat"), (e, d, c))
                          if state in spec["active_states"][cat]), 0)
            api.call("ak.wwise.core.object.setProperty", {"object": ident, "property": "Volume", "value": level})
            table[state] = level
        return table

    table = levels(-200, -200, 0)
    api.call("ak.wwise.core.project.save")
    changed = [rel for rel, sha in units.items() if digest(project.parent / rel) != sha]
    allowed = {str(Path("Interactive Music Hierarchy/music.wwu")),
               str(Path("Control Surface Sessions/Default Work Unit.wwu"))}
    # Wwise initializes an empty default control-surface session on first save.
    # It is authoring UI metadata, not a runtime mixer or bank definition.
    assert set(changed) <= allowed, changed
    evidence = {"wwise": info, "state_table_db": table, "custom_states": overrides,
                "changed_before_fixtures": changed, "no_bank_generation": True,
                "runs": [], "contexts": []}
    (out / "authoring.json").write_text(json.dumps(evidence, indent=2) + "\n")
    # Preserve the pure local edit before adding any measurement fixtures.
    (out / "world-state-only-music.wwu").write_bytes((project.parent / "Interactive Music Hierarchy/music.wwu").read_bytes())
    worldpath = api.call("ak.wwise.core.object.get", {"from": {"id": [WORLD]}}, {"return": ["path"]})["return"][0]["path"]
    audio = out / "tone.wav"
    frames = array.array("h")
    for i in range(48000):
        frames.extend(round(12000 * math.sin(2*math.pi*f*i/48000)) for f in (300,400,500,60,600,700))
    with wave.open(str(audio), "wb") as wav:
        wav.setparams((6,2,48000,0,"NONE","not compressed"))
        for _ in range(90):
            wav.writeframesraw(frames.tobytes())
    segment = worldpath + r"\WMC_StateTone"
    api.call("ak.wwise.core.audio.import", {"importOperation": "useExisting",
        "autoAddToSourceControl": False, "autoCheckOutToSourceControl": False,
        "imports": [{"objectPath": worldpath + r"\<Music Segment>WMC_StateTone\<Music Track>WMC_StateTrack",
                     "audioFile": str(audio)}]})
    track = segment + r"\WMC_StateTrack"
    api.call("ak.wwise.core.object.set", {"objects": [{"object": track,
        "@OverrideVirtualVoice": True, "@BelowThresholdBehavior": 0}]})
    api.call("ak.wwise.core.object.setProperty", {"object": MUSIC, "property": "BusChannelConfig", "value": 6353158})
    api.call("ak.wwise.core.object.set", {"objects": [{"object": MUSIC, "@Effects": [{
        "type": "EffectSlot", "name": "", "@Effect": {"type": "Effect", "name": "WMC_StateRecorder",
        "classId": 8650755, "@DownmixToStereo": False, "@AuthoringFilename": str(out / "initial.wav")}}],
        "listMode": "replaceAll"}]})
    slots = api.call("ak.wwise.core.object.get", {"from": {"path": [MUSIC]}}, {"return": ["@Effects"]})["return"][0]["@Effects"]
    recorder = api.call("ak.wwise.core.object.get", {"from": {"id": [slots[-1]["id"]]}}, {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
    anchor_transport = None
    if anchor:
        silent = out / "silent-anchor.wav"
        with wave.open(str(silent), "wb") as wav:
            wav.setparams((6,2,48000,0,"NONE","not compressed"))
            for _ in range(90):
                wav.writeframesraw(bytes(48000*6*2))
        anchor_path = r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_StateAnchor"
        api.call("ak.wwise.core.audio.import", {"importOperation": "useExisting",
            "autoAddToSourceControl": False, "autoCheckOutToSourceControl": False,
            "imports": [{"objectPath": anchor_path, "objectType": "Sound", "audioFile": str(silent),
                         "@OverrideOutput": True, "@OutputBus": MUSIC,
                         "@OverrideVirtualVoice": True, "@BelowThresholdBehavior": 0}]})
        anchor_transport = api.call("ak.wwise.core.transport.create", {"object": anchor_path})["transport"]

    def filename(name):
        api.call("ak.wwise.core.object.setProperty", {"object": recorder,
                 "property": "AuthoringFilename", "value": str(out / (name + ".wav"))})

    def snapshot(label):
        voices = api.call("ak.wwise.core.profiler.getVoices", {"time": "capture"},
                         {"return": ["pipelineID","objectName","baseVolume","isVirtual","isStarted"]})
        contributions = [api.call("ak.wwise.core.profiler.getVoiceContributions",
                                 {"time": "capture", "voicePipelineID": v["pipelineID"]})
                         for v in voices["return"][:4]]
        return {"label": label, "voices": voices, "contributions": contributions}

    api.call("ak.wwise.core.profiler.startCapture")
    transport = api.call("ak.wwise.core.transport.create", {"object": segment})["transport"]
    for label, values in (("baseline", (0,0,0)), ("unequal", (-12,-24,-6)), ("defaults", (-200,-200,0))):
        levels(*values)
        filename(label)
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": "cutscene"})
        if anchor_transport is not None:
            api.call("ak.wwise.core.transport.executeAction", {"transport": anchor_transport, "action": "play"})
        api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
        started = time.monotonic()
        rows = []
        for state in ("cutscene", "exploration", "dialog_scene", "combat", "cutscene"):
            api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
            rows.append({"state": state, "wall_seconds": time.monotonic()-started})
            time.sleep(4)
        evidence["runs"].append({"label": label, "states": rows, "levels_db": values, "snapshot": snapshot(label)})
        api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
        time.sleep(.25)
        (out / "results.json").write_text(json.dumps(evidence, indent=2) + "\n")
    # Native selectors / authored playlist are tested without the tone playing.
    levels(-200,-200,0)
    filename("contexts")
    transport = api.call("ak.wwise.core.transport.create", {"object": r"\Events\music\prologue\play_music_prologue"})["transport"]
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    api.call("ak.soundengine.postEvent", {"event": "mus_loc_prologue_village", "gameObject": 18446744073709551614})
    for label, state, cue in (("village", "exploration", None), ("generic-dialogue", "dialog_scene", None),
                              ("combat", "combat", None), ("q001-intro", "cutscene", "mus_cs001_tavern_intro"),
                              ("q001-dialogue", "dialog_scene", "mus_q001_tavern_conversation")):
        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
        if cue:
            api.call("ak.soundengine.postEvent", {"event": cue, "gameObject": 18446744073709551614})
        time.sleep(4)
        evidence["contexts"].append({**snapshot(label), "state": state, "event": cue})
    api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
    # Avoid waiting through the long intro's native exit rules.
    filename("q001-direct")
    api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": "dialog_scene"})
    transport = api.call("ak.wwise.core.transport.create", {"object": "{EFA886D9-2BAD-4354-9DC3-BC08E2E75727}"})["transport"]
    api.call("ak.wwise.core.transport.executeAction", {"transport": transport, "action": "play"})
    time.sleep(4)
    evidence["contexts"].append(snapshot("q001-direct"))
    api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
    api.call("ak.wwise.core.profiler.stopCapture")
    levels(-200,-200,0)
    api.call("ak.wwise.core.project.save")
    (out / "results.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"output": str(out), "states": len(table), "runs": len(evidence["runs"])}))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--capture-name", default="state-volume")
    p.add_argument("--anchor", action="store_true", help="Silent capture fixture outside attenuated branch")
    args = p.parse_args()
    run(args.project, args.capture_name, args.anchor)
