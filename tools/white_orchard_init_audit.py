"""Research-only media-filter control. Preserve all objects; never deploy output.

Prepare a fresh complete copy with white_orchard_prepare.py first, then open
that copy in localhost WAAPI. This helper changes only unselected banks' media
inclusion filters through the installed supported API. It does not grant a
licence, remove sources, modify global definitions, or certify resulting Init.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from white_orchard_prepare import build_path, digest, save_xml, GLOBAL_CATEGORIES
from white_orchard_wwise import Waapi


def run(project):
    project = build_path(project)
    evidence = project.parent / "media-filter-audit.json"
    if evidence.exists():
        raise FileExistsError(evidence)
    api = Waapi()
    info = api.call("ak.wwise.core.getInfo")
    opened = api.call("ak.wwise.core.object.get", {"from": {"ofType": ["Project"]}},
                      {"return": ["filePath"]})["return"][0]["filePath"]
    if Path(opened).resolve() != project:
        raise ValueError("Wrong WAAPI project")
    if info["version"]["build"] != 8928:
        raise ValueError("Wrong Wwise build")
    units = {str(p.relative_to(project.parent)): digest(p)
             for p in project.parent.rglob("*.wwu")}
    banks = api.call("ak.wwise.core.object.get", {"from": {"ofType": ["SoundBank"]}},
                     {"return": ["id", "name"]})["return"]
    changes = []
    for bank in banks:
        if bank["name"] == "music_prologue":
            continue
        before = api.call("ak.wwise.core.soundbank.getInclusions",
                          {"soundbank": bank["id"]})["inclusions"]
        after = [{"object": x["object"], "filter": [f for f in x["filter"] if f != "media"]}
                 for x in before]
        if after != before:
            api.call("ak.wwise.core.soundbank.setInclusions",
                     {"soundbank": bank["id"], "operation": "replace", "inclusions": after})
            actual = api.call("ak.wwise.core.soundbank.getInclusions",
                              {"soundbank": bank["id"]})["inclusions"]
            if actual != after:
                raise RuntimeError("Inclusion verification failed")
            changes.append({**bank, "before": before, "after": after})
    api.call("ak.wwise.core.project.save")
    changed_units = [rel for rel, sha in units.items()
                     if digest(project.parent / rel) != sha]
    # Saving can canonicalize bank work units, but all non-bank definitions must
    # remain byte-identical in this experiment, not merely exist by name.
    unrelated = [p for p in changed_units if not p.startswith("SoundBanks\\")
                 and not p.startswith("SoundBanks/")]
    evidence.write_text(json.dumps({"info": info, "project": str(project),
        "banks": len(banks), "changes": changes, "changed_work_units": changed_units,
        "unrelated_work_units_changed": unrelated, "shipping_eligible": False}, indent=2) + "\n")
    if unrelated:
        raise RuntimeError("Unexpected non-bank definition changes; inspect evidence")
    print(json.dumps({"banks": len(banks), "modified_banks": len(changes),
                      "changed_work_units": len(changed_units), "unrelated_changes": unrelated}))


def exclude_leaves(project):
    """Supported node Inclusion experiment, NOT evidence of Init equivalence.

    Keep every node, source, reference, event and bank definition. Only disable
    file-backed Sound/MusicTrack leaves outside the selected regional root.
    This can change compiler dependency usage despite retained global XML.
    """
    project = build_path(project)
    out = project.parent / "leaf-inclusion-audit.json"
    if out.exists():
        raise FileExistsError(out)
    globals_before = {str(p.relative_to(project.parent)): digest(p)
                      for cat in GLOBAL_CATEGORIES for p in (project.parent / cat).rglob("*.wwu")}
    edits = []
    retained_sources = 0
    for cat in ("Actor-Mixer Hierarchy", "Interactive Music Hierarchy"):
        for path in sorted((project.parent / cat).rglob("*.wwu")):
            tree = ET.parse(path)
            protected = set()
            for root in tree.iter("MusicSwitchContainer"):
                if root.get("Name") == "music_prologue":
                    protected.update(root.iter())
            changes = []
            for node in tree.iter():
                if node.tag not in ("Sound", "MusicTrack"):
                    continue
                sources = list(node.iter("AudioFileSource"))
                if not sources:
                    continue
                if node in protected:
                    retained_sources += len(sources)
                    continue
                props = node.find("PropertyList")
                if props is None:
                    props = ET.Element("PropertyList")
                    node.insert(0, props)
                previous = [ET.tostring(p, encoding="unicode") for p in props
                            if p.get("Name") == "Inclusion"]
                for p in list(props):
                    if p.get("Name") == "Inclusion":
                        props.remove(p)
                ET.SubElement(props, "Property", Name="Inclusion", Type="bool", Value="False")
                changes.append({"id": node.get("ID"), "name": node.get("Name"),
                                "type": node.tag, "sources": len(sources), "previous": previous})
            if changes:
                save_xml(tree, path)
                edits.append({"work_unit": str(path.relative_to(project.parent)), "leaves": changes})
    globals_after = {rel: digest(project.parent / rel) for rel in globals_before}
    assert globals_before == globals_after
    result = {"project": str(project), "edits": edits,
              "excluded_file_sources": sum(n["sources"] for e in edits for n in e["leaves"]),
              "retained_prologue_sources": retained_sources,
              "global_work_units_unchanged": globals_before, "shipping_eligible": False}
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("excluded_file_sources", "retained_prologue_sources", "shipping_eligible")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--exclude-file-leaves", action="store_true",
                        help="Offline Inclusion=False control; preserve objects and global XML")
    args = parser.parse_args()
    (exclude_leaves if args.exclude_file_leaves else run)(args.project)
