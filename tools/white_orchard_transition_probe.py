"""Native selector transition recordings. Fixtures only; never generates banks."""
import argparse
import json
from pathlib import Path
import time
import wave
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path
from white_orchard_wwise import Waapi
from white_orchard_state_volume import WORLD, GROUP, MUSIC


GENERIC = {
    "{4A23933D-BE41-4C79-BED2-337D24C605EA}": "village_exploration",
    "{D79C5D2C-22B5-4855-882B-FD18E348605D}": "expl_nml_zone_01_PROLOGUE_NIGHT",
    "{3EA3656B-F8B4-4B72-93D9-535D2ECBBD9E}": "expl_nilfgaard_camp",
    "{C0E409DC-01A4-4C40-9393-51BD4D89A0A0}": "expl_cemetery",
    "{5963D5CD-2EBE-4FFF-AD38-253D18C433B3}": "expl_battlefield",
}


def run(project, name, port, modes, selected, location="village", manifest=None, location_event=None, explicit_threat_zero=False, minimum_duration=19):
    project = build_path(project)
    api = Waapi(port)
    if project.parent.name != "validation" or Path(api.call("ak.wwise.core.getProjectInfo")["path"]).resolve() != project:
        raise ValueError("Only the open isolated validation project is permitted")
    if Path(name).name != name:
        raise ValueError("Simple output name required")
    out = project.parent / name
    out.mkdir(exist_ok=False)
    regional = json.loads(manifest.read_text()) if manifest else None
    regional_modes = {'manifest', 'D-reference', 'native-reference'}
    if set(modes) & regional_modes and (regional is None or not set(modes) <= regional_modes):
        raise ValueError('Regional probes require a manifest and regional modes only')
    world_id = regional['facts']['world']['id'] if regional else WORLD
    group_id = regional['game_state_group'] if regional else GROUP
    if regional is None:
        api.call("ak.wwise.core.object.setStateProperties", {"object": world_id, "stateProperties": ["Volume"]})
        api.call("ak.wwise.core.object.setStateGroups", {"object": world_id, "stateGroups": [group_id]})
    api.call("ak.wwise.core.project.save")
    world = next(x for x in ET.parse(project.parent / "Interactive Music Hierarchy/music.wwu").iter("MusicSwitchContainer") if x.get("ID") == world_id)
    states = {x.find("StateRef").get("Name"): x.find("CustomState").get("ID") for x in world.findall("./StateInfo/CustomStateList/CustomState")}
    if regional is None:
        assert len(states) == 25
    spec = json.loads((Path(__file__).resolve().parents[1] / "src/wwise/white-orchard-state-volume.json").read_text())
    fix = json.loads((Path(__file__).resolve().parents[1] / "src/wwise/white-orchard-transition-fix.json").read_text())
    if GENERIC != {target["id"]: target["name"] for target in fix["targets"]}:
        raise ValueError("Fixture and production target specifications disagree")
    if regional is None and modes != ["D-probe"]:
        for target in fix["targets"]:
            saved = next(n for n in ET.parse(project.parent / "Interactive Music Hierarchy/music.wwu").iter("MusicPlaylistContainer") if n.get("ID") == target["id"])
            from white_orchard_transition_author import volume
            if volume(saved) != target["original_volume_db"]:
                raise ValueError("Baseline/C probe requires untouched generic playlists")
    api.call("ak.wwise.core.object.setProperty", {"object": MUSIC, "property": "BusChannelConfig", "value": 6353158})
    api.call("ak.wwise.core.object.set", {"objects": [{"object": MUSIC, "@Effects": [{"type": "EffectSlot", "name": "", "@Effect": {
        "type": "Effect", "name": "WMC_TransitionRecorder", "classId": 8650755,
        "@DownmixToStereo": False, "@ApplyDownstreamVolume": True, "@AuthoringFilename": str(out / "unused.wav")}}], "listMode": "replaceAll"}]})
    slot = api.call("ak.wwise.core.object.get", {"from": {"path": [MUSIC]}}, {"return": ["@Effects"]})["return"][0]["@Effects"][-1]["id"]
    recorder = api.call("ak.wwise.core.object.get", {"from": {"id": [slot]}}, {"return": ["@Effect"]})["return"][0]["@Effect"]["id"]
    silent = out / "anchor.wav"
    with wave.open(str(silent), "wb") as wav:
        wav.setparams((6, 2, 48000, 0, "NONE", "not compressed"))
        for _ in range(max(60, int(minimum_duration) + 2)):
            wav.writeframesraw(bytes(48000 * 12))
    anchor = r"\Actor-Mixer Hierarchy\Default Work Unit\WMC_TransitionAnchor"
    api.call("ak.wwise.core.audio.import", {"importOperation": "useExisting", "autoAddToSourceControl": False,
        "autoCheckOutToSourceControl": False, "imports": [{"objectPath": anchor, "objectType": "Sound", "audioFile": str(silent),
        "@OverrideOutput": True, "@OutputBus": MUSIC, "@OverrideVirtualVoice": True, "@BelowThresholdBehavior": 0}]})
    anchor_transport = api.call("ak.wwise.core.transport.create", {"object": anchor})["transport"]
    region_name = regional['region'] if regional else 'music_prologue'
    events = {n.get('Name'): n.get('ID') for n in ET.parse(project.parent / 'Events/music.wwu').iter('Event')}
    play_event = 'play_' + region_name
    location_event = location_event or 'mus_loc_prologue_' + location
    if play_event not in events or location_event not in events:
        raise ValueError('Unverified native event')
    event_transport = api.call("ak.wwise.core.transport.create", {"object": events[play_event]})["transport"]
    cases = {
        "e-combat": [(0, "exploration", None), (6, "combat", None), (13, "exploration", None)],
        "e-combat-offset": [(0, "exploration", None), (7.3, "combat", None), (14.3, "exploration", None)],
        "e-dialogue": [(0, "exploration", None), (6, "dialog_scene", None), (10, "exploration", None)],
        "e-cutscene-dialogue": [(0, "exploration", None), (6, "cutscene", None), (6.4, "dialog_scene", None)],
        "e-movie-dialogue": [(0, "exploration", None), (6, "movie", None), (6.4, "dialog_scene", None)],
        "e-music-only-dialogue": [(0, "exploration", None), (6, "music_only", None), (6.4, "dialog_scene", None)],
        "authored": [(0, "exploration", None), (6, "cutscene", "mus_cs001_tavern_intro"), (11, "dialog_scene", "mus_q001_tavern_conversation")],
        "combat-threat": [(0, "exploration", None), (6, "combat", None)],
        "q001-direct": [(0, "dialog_scene", None)],
        "night-combat": [(0, "exploration_night", None), (6, "combat", None), (13, "exploration_night", None)],
        "long-silence-combat": [(0, "exploration", None), (35, "combat", None), (42, "exploration", None)],
        "authored-world": [(0, "exploration", None), (6, "dialog_scene", None), (10, "cutscene", None), (10.4, "dialog_scene", None), (13, "combat", None)],
        "gwent": [(0, "gwent", None)],
    }
    evidence = {"version": api.call("ak.wwise.core.getInfo"), "fixtures_only": True, "location": location,
                "location_event": location_event, "explicit_threat_zero": explicit_threat_zero,
                "preplay_settle_seconds": 1.1 if explicit_threat_zero else 0, "cases": []}
    api.call("ak.wwise.core.profiler.startCapture")
    try:
        for mode in modes:
            if regional:
                # A/B authoring fixture control: D-reference recreates root gain
                # while zeroing descendant gains, never changes production D.
                scope_ids = list(regional['state_scopes'])
                api.call('ak.wwise.core.object.setStateProperties', {'object': world_id, 'stateProperties': ['Volume'] if mode == 'D-reference' else []})
                api.call('ak.wwise.core.object.setStateGroups', {'object': world_id, 'stateGroups': [group_id] if mode == 'D-reference' else []})
                api.call('ak.wwise.core.project.save')
                current = ET.parse(project.parent / 'Interactive Music Hierarchy/music.wwu')
                for node in current.iter('MusicSwitchContainer'):
                    if node.get('ID') not in scope_ids + [world_id]:
                        continue
                    for row_state in node.findall('./StateInfo/CustomStateList/CustomState'):
                        muted = row_state.find('StateRef').get('Name') in regional['muted_states']
                        enabled = (mode == 'D-reference' and node.get('ID') == world_id) or (mode == 'manifest' and node.get('ID') in scope_ids)
                        api.call('ak.wwise.core.object.setProperty', {'object': row_state.find('CustomState').get('ID'), 'property': 'Volume', 'value': -200 if muted and enabled else 0})
                for ident in regional['static_targets']:
                    gain = regional['decisions'][ident]['original_volume'] if mode == 'native-reference' else -200
                    api.call('ak.wwise.core.object.setProperty', {'object': ident, 'property': 'Volume', 'value': gain})
            if mode == "D-probe":
                for ident in GENERIC:
                    api.call("ak.wwise.core.object.setProperty", {"object": ident, "property": "Volume", "value": -200})
            for state, ident in (states.items() if regional is None else []):
                muted = state in spec["active_states"]["exploration"] + spec["active_states"]["dialogue"]
                api.call("ak.wwise.core.object.setProperty", {"object": ident, "property": "Volume", "value": -200 if mode != "baseline" and muted else 0})
            for label, sequence in cases.items():
                if selected and label not in selected:
                    continue
                api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
                api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": sequence[0][1]})
                if explicit_threat_zero:
                    # Fixture control, not a production change. Set global threat
                    # explicitly before any transport, then settle native fades.
                    # Omitting gameObject is the documented transport scope.
                    # Reset global history separately; a transport override can
                    # otherwise mask global scheduled changes.
                    for parameter in ('threat_rating', 'menu_volume_music'):
                        api.call('ak.soundengine.resetRTPCValue', {'rtpc': parameter, 'gameObject': 18446744073709551615})
                        api.call('ak.soundengine.resetRTPCValue', {'rtpc': parameter})
                    api.call("ak.soundengine.setRTPCValue", {"rtpc": "threat_rating", "value": 0})
                    api.call("ak.soundengine.setRTPCValue", {"rtpc": "menu_volume_music", "value": 100})
                    time.sleep(1.1)
                api.call("ak.wwise.core.object.setProperty", {"object": recorder, "property": "AuthoringFilename", "value": str(out / f"{mode}-{label}.wav")})
                api.call("ak.wwise.core.transport.executeAction", {"transport": anchor_transport, "action": "play"})
                started = time.monotonic()
                if not explicit_threat_zero:
                    api.call("ak.soundengine.resetRTPCValue", {"rtpc": "threat_rating"})
                    api.call("ak.soundengine.resetRTPCValue", {"rtpc": "menu_volume_music"})
                if label == "q001-direct":
                    authored = api.call("ak.wwise.core.transport.create", {"object": "{EFA886D9-2BAD-4354-9DC3-BC08E2E75727}"})["transport"]
                    api.call("ak.wwise.core.transport.executeAction", {"transport": authored, "action": "play"})
                else:
                    api.call("ak.wwise.core.transport.executeAction", {"transport": event_transport, "action": "play"})
                    api.call("ak.soundengine.postEvent", {"event": location_event, "gameObject": 18446744073709551614})
                row = {"mode": mode, "case": label, "events": [], "samples": []}
                pending = list(sequence)
                parameters = ([(10, "threat_rating", 35), (14, "threat_rating", 100)] if label == "combat-threat" else
                              [(6, "menu_volume_music", 50), (11, "menu_volume_music", 100)] if label == "q001-direct" else [])
                duration = max(minimum_duration, sequence[-1][0] + 6)
                row['duration_seconds'] = duration
                while time.monotonic() - started < duration:
                    elapsed = time.monotonic() - started
                    while pending and elapsed >= pending[0][0]:
                        scheduled, state, event = pending.pop(0)
                        api.call("ak.soundengine.setState", {"stateGroup": "game_state", "state": state})
                        if event:
                            api.call("ak.soundengine.postEvent", {"event": event, "gameObject": 18446744073709551614})
                        row["events"].append({"scheduled": scheduled, "accepted": time.monotonic() - started, "state": state, "event": event})
                    while parameters and elapsed >= parameters[0][0]:
                        scheduled, parameter, value = parameters.pop(0)
                        args = {"rtpc": parameter, "value": value}
                        if not explicit_threat_zero:
                            args['gameObject'] = 18446744073709551615
                        api.call("ak.soundengine.setRTPCValue", args)
                        row["events"].append({"scheduled": scheduled, "accepted": time.monotonic() - started, "parameter": parameter, "value": value})
                    voices = api.call("ak.wwise.core.profiler.getVoices", {"time": "capture"}, {"return": ["pipelineID", "objectName", "baseVolume", "isVirtual", "isStarted"]})["return"]
                    contributions = {str(v["pipelineID"]): api.call("ak.wwise.core.profiler.getVoiceContributions", {"time": "capture", "voicePipelineID": v["pipelineID"]}) for v in voices if "Anchor" not in v["objectName"]}
                    sample = {"time": time.monotonic() - started, "voices": voices, "contributions": contributions}
                    if explicit_threat_zero:
                        sample['rtpcs'] = [x for x in api.call('ak.wwise.core.profiler.getRTPCs', {'time': 'capture'})['return']
                                           if x['name'] in ('threat_rating', 'menu_volume_music')]
                    row["samples"].append(sample)
                    time.sleep(.08)
                api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
                time.sleep(.25)
                evidence["cases"].append(row)
                (out / "results.json").write_text(json.dumps(evidence, indent=2) + "\n")
                print(json.dumps({"mode": mode, "case": label, "samples": len(row["samples"])}), flush=True)
    finally:
        api.call("ak.wwise.core.transport.executeAction", {"action": "stop"})
        api.call("ak.wwise.core.profiler.stopCapture")
        api.call("ak.soundengine.resetRTPCValue", {"rtpc": "threat_rating"})
        api.call("ak.soundengine.resetRTPCValue", {"rtpc": "menu_volume_music"})
        if explicit_threat_zero:
            for parameter in ('threat_rating', 'menu_volume_music'):
                api.call('ak.soundengine.resetRTPCValue', {'rtpc': parameter, 'gameObject': 18446744073709551615})
    print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--name", default="native-transitions")
    parser.add_argument("--port", default=18090, type=int)
    parser.add_argument("--modes", nargs="+", choices=["baseline", "C", "D-probe", "D-reference", "native-reference", "manifest"], default=["baseline", "C"])
    parser.add_argument("--cases", nargs="+")
    parser.add_argument("--location", choices=["village", "nilfgaard_camp", "cemetery", "battlefield"], default="village")
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--location-event')
    parser.add_argument('--explicit-threat-zero', action='store_true', help='Fixture-only preplay threat=0/Music=100 control with 1.1s settling')
    parser.add_argument('--minimum-duration', type=float, default=19, help='Observe native outro completion; does not alter musical transitions')
    args = parser.parse_args()
    if "D-probe" in args.modes and args.modes != ["D-probe"]:
        parser.error("D-probe mutates fixture playlists: run it separately, after baseline/C")
    run(args.project, args.name, args.port, args.modes, args.cases, args.location, args.manifest, args.location_event, args.explicit_threat_zero, args.minimum_duration)
