"""Prepare a self-contained, bank-scoped authoring copy; never write to inputs.

Usage: python tools/white_orchard_prepare.py --audio-project PATH --output PATH
All output must be inside this repository's ignored build directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "src/wwise/white-orchard-mixer.json"
GLOBAL_CATEGORIES = (
    "Master-Mixer Hierarchy", "Effects", "Game Parameters", "States", "Switches",
    "Modulators", "Audio Devices", "Conversion Settings", "Attenuations",
    "Virtual Acoustics", "Metadata", "Triggers",
)


def build_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(REPO / "build") or path == REPO / "build":
        raise ValueError("Output must be a child of the repository build directory")
    return path


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_xml(tree, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve source whitespace inside retained nodes. Wwise will canonicalize
    # its own serialization when saving; compare parsed objects, not line diffs.
    tree.write(path, encoding="utf-8", xml_declaration=True)


def retain(tree, tag, name):
    root = tree.getroot()
    parent = {c: p for p in root.iter() for c in p}
    node = next(x for x in root.iter(tag) if x.get("Name") == name)
    keep = {node}
    cursor = node
    while cursor in parent:
        cursor = parent[cursor]
        keep.add(cursor)
    # Retain the entire selected subtree, pruning sibling hierarchy branches.
    for item in list(keep):
        if item.tag == "ChildrenList":
            for child in list(item):
                if child not in keep:
                    item.remove(child)
    return node


def sanitize_project(tree):
    project = tree.find("./ProjectInfo/Project")
    if project is None:
        raise ValueError("Unexpected project schema")
    # Remove inventory of installation work units. Wwise discovers isolated
    # work units from the local physical folders.
    for child in list(project):
        if child.tag in ("PhysicalFolderList", "SourceControl"):
            project.remove(child)
    for prop in tree.iter("Property"):
        name = prop.get("Name", "")
        if name in ("SoundBankPaths", "SoundBankHeaderFilePath", "ExternalSourcesOutputPath"):
            values = list(prop.iter("Value"))
            if values:
                for value in values:
                    value.text = "GeneratedSoundBanks"
            else:
                prop.set("Value", "GeneratedSoundBanks")
        elif name == "ExternalSourcesInputPath":
            for value in prop.iter("Value"):
                value.text = ""
            if "Value" in prop.attrib:
                prop.set("Value", "")
        elif "CustomCmd" in name:
            for value in prop.iter("Value"):
                value.text = ""
            if "Value" in prop.attrib:
                prop.set("Value", "")
        elif name == "SourceControlGeneratedFiles":
            for value in prop.iter("Value"):
                value.text = "False"
            if "Value" in prop.attrib:
                prop.set("Value", "False")
    for setting in tree.iter("MiscSettingEntry"):
        if setting.get("Name") in ("Cache", "Originals"):
            setting.text = ".cache" if setting.get("Name") == "Cache" else "Originals"


def prepare_defaults(source, output, record=None):
    """Keep required empty default roots without unrelated nested work units."""
    for category in ("Events", "Actor-Mixer Hierarchy", "Presets",
                     "Soundcaster Sessions", "Queries", "Dynamic Dialogue",
                     "Mixing Sessions", "Control Surface Sessions"):
        path = source / category / "Default Work Unit.wwu"
        if not path.exists():
            continue
        if record:
            record(path)
        tree = ET.parse(path)
        workunit = next(tree.iter("WorkUnit"))
        children = workunit.find("ChildrenList")
        if children is not None:
            workunit.remove(children)
        save_xml(tree, output / path.relative_to(source))


def prepare(source, output):
    source = Path(source).resolve()
    output = build_path(output)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing workspace: {output}")
    if source == output or source.is_relative_to(output):
        raise ValueError("Input and output overlap")
    config = json.loads(CONFIG.read_text())
    project = ET.parse(source / "w3_audio.wproj")
    version = project.getroot().attrib
    for field, expected in (("SchemaVersion", str(config["schema_version"])),
                            ("WwiseVersion", config["wwise_version"]),
                            ("WwiseBuild", config["wwise_build"])):
        if version.get(field) != expected:
            raise ValueError(f"Version mismatch: {field}={version.get(field)}")
    output.mkdir(parents=True)
    manifest = {"version": version, "inputs": [], "originals": [], "changes": []}
    recorded = set()

    def record(path):
        if path in recorded:
            return
        recorded.add(path)
        manifest["inputs"].append({"relative_path": str(path.relative_to(source)),
                                   "sha256": digest(path), "bytes": path.stat().st_size})

    record(source / "w3_audio.wproj")
    sanitize_project(project)
    save_xml(project, output / "w3_audio.wproj")
    for category in GLOBAL_CATEGORIES:
        for path in sorted((source / category).glob("*.wwu")):
            record(path)
            target = output / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    for category in ("Interactive Music Hierarchy", "Events", "SoundBanks"):
        default = source / category / "Default Work Unit.wwu"
        if default.exists():
            record(default)
            target = output / category / default.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(default, target)
    path = source / "Interactive Music Hierarchy/music.wwu"
    record(path)
    music = ET.parse(path)
    root = retain(music, "MusicSwitchContainer", config["regional_root"])
    world = next(x for x in root.findall("./ChildrenList/*") if x.get("Name") == "world_music")
    assert int(world.get("ShortID")) == config["world_short_id"]
    save_xml(music, output / path.relative_to(source))
    path = source / "Events/music.wwu"
    record(path)
    events = ET.parse(path)
    retain(events, "Folder", "prologue")
    save_xml(events, output / path.relative_to(source))
    path = source / "SoundBanks/music.wwu"
    record(path)
    banks = ET.parse(path)
    retain(banks, "SoundBank", "music_prologue")
    save_xml(banks, output / path.relative_to(source))
    prepare_defaults(source, output, record)
    for audio in sorted(set(x.text for x in root.iter("AudioFile"))):
        relative = Path("Originals/SFX") / audio.replace("\\", "/")
        path = source / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        manifest["originals"].append({"relative_path": str(relative),
                                      "sha256": digest(path), "bytes": path.stat().st_size})
    (output / "input-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"workspace": str(output), "work_units": len(list(output.rglob("*.wwu"))),
                      "originals": len(manifest["originals"]),
                      "original_bytes": sum(x["bytes"] for x in manifest["originals"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio-project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    prepare(args.audio_project, args.output)
