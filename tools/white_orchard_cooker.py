"""Reproduce isolated REDkit bootstrap and native two-bank cache fixtures.

This is an offline packaging experiment, not deployment. It only packages
byte-identical native Init/music_prologue inputs, never the incomplete pilot
Init. Existing installed executables remain in place and are not copied.
"""
import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess
from white_orchard_prepare import build_path, digest


def prepare(redkit, output):
    output = build_path(output)
    redkit = redkit.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    manifest = {"redkit": str(redkit), "inputs": [], "changes": []}
    def copy(source, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest["inputs"].append({"source": str(source), "sha256": digest(source),
                                   "bytes": source.stat().st_size})
    cfg = redkit / "bin/gameconf.cfg"
    copy(cfg, output / "bin/gameconf.cfg")
    (output / "bin/gameconf.cfg").write_text(cfg.read_text().replace(
        'data "r4data"', 'data "r4data/"').replace('config "bin\\r4config"', 'config "bin/config"'))
    manifest["changes"].append("Isolated gameconf relative data/config paths")
    for source in (redkit / "bin/config").rglob("*"):
        if source.is_file():
            copy(source, output / source.relative_to(redkit))
    for relative in ("r4data/dep.cache", "r4data/staticshaderDx12_0.cache",
                     "r4data/x64.release.redscripts", "r4data/game/dlctable.csv"):
        copy(redkit / relative, output / relative)
    for source in (redkit / "r4data/gameplay/globals").rglob("*"):
        if source.is_file() and source.suffix in (".csv", ".xml"):
            copy(source, output / source.relative_to(redkit))
    csv = output / "r4data/gameplay/globals/soundbanks_always_load.csv"
    shutil.copyfile(csv, output / "startup-banks-original.csv")
    names = csv.read_text().split("\0", 1)[0].splitlines()[1:]
    existing, missing = [], []
    for name in names:
        name = name.strip()
        if not name:
            continue
        if Path(name).name != name or not name.lower().endswith(".bnk"):
            raise ValueError("Unexpected bank filename in installed startup table")
        source = redkit / "r4data/soundbanks/Pc" / name
        if source.is_file():
            copy(source, output / "r4data/soundbanks/Pc" / name)
            existing.append(name)
        else:
            missing.append(name)
    csv.write_text("soundbank\n" + "\n".join(existing) + "\n")
    manifest["changes"].append({"bootstrap_only_startup_csv": "existing files only; discard null padding",
                                "missing_names": missing})
    native_init = redkit / "r4data/soundbanks/Pc/Init.bnk"
    copy(native_init, output / "r4data/soundbanks/Pc/Init.bnk")
    copy(native_init, output / "bin/initialdata/sound/Init.bnk")
    # No rows: the native cooker explicitly assigns unlisted banks to content0.
    # Header labels have no tested mapping semantics and are not a full schema.
    (output / "r4data/soundbanks/soundsplitseed.csv").write_text("bank;chunk\n")
    manifest["changes"].append("Header-only sound split seed; native content0 fallback")
    (output / "bin/x64").mkdir()
    (output / "bootstrap-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"root": str(output), "missing_startup_banks": missing,
                      "input_count": len(manifest["inputs"])}))


def execute(executable, root, label, arguments, timeout_seconds=45):
    args = [str(executable), *arguments, "-root", str(root) + "\\", "-noninteractivecrash"]
    log_path = root / (label + ".log")
    if log_path.exists():
        raise FileExistsError(log_path)
    with log_path.open("w") as log:
        process = subprocess.Popen(args, cwd=root / "bin/x64", stdout=log, stderr=subprocess.STDOUT)
        try:
            code = process.wait(timeout=timeout_seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            process.kill()
            code = process.wait()
            timed_out = True
    result = {"args": args, "cwd": str(root / "bin/x64"), "exit_code": code, "timeout": timed_out,
              "timeout_seconds": timeout_seconds}
    (root / (label + "-result.json")).write_text(json.dumps(result, indent=2) + "\n")
    if code or timed_out:
        raise RuntimeError(f"Cooker failed: {result}; see {log_path}")


def verify_cache(path, inputs):
    data = path.read_bytes()
    if data[:8] != b"CS3W\x02\0\0\0":
        raise ValueError("Unexpected cache format")
    count = struct.unpack_from("<I", data, 24)[0]
    names_offset = struct.unpack_from("<Q", data, 32)[0]
    names_size = struct.unpack_from("<I", data, 40)[0]
    if count != 2:
        raise ValueError("Expected exactly two indexed resources")
    names = data[names_offset:names_offset + names_size]
    entries = []
    for index in range(count):
        name_offset, offset, size = struct.unpack_from("<QQQ", data, names_offset + names_size + index * 24)
        name = names[name_offset:].split(b"\0", 1)[0].decode()
        source = inputs / name
        if not source.exists() and name == "init.bnk":
            source = inputs / "Init.bnk"
        if name not in ("init.bnk", "music_prologue.bnk") or data[offset:offset + size] != source.read_bytes():
            raise ValueError("Cache payload mismatch")
        entries.append({"name": name, "offset": offset, "bytes": size, "sha256": digest(source)})
    return {"path": str(path), "bytes": len(data), "sha256": digest(path), "entries": entries,
            "uninterpreted_header_28": struct.unpack_from("<I", data, 28)[0]}


def fixture(root):
    root = build_path(root)
    manifest = json.loads((root / "bootstrap-manifest.json").read_text())
    redkit = Path(manifest["redkit"])
    executable = redkit / "bin/x64_RedKit/wcc_lite.exe"
    inputs = root / "native-fixture-banks"
    output = root / "native-fixture-cooked"
    if inputs.exists() or output.exists():
        raise FileExistsError("Preserve existing fixtures; prepare a fresh root")
    inputs.mkdir(); output.mkdir()
    for name in ("Init.bnk", "music_prologue.bnk"):
        shutil.copyfile(redkit / "r4data/soundbanks/Pc" / name, inputs / name)
    execute(executable, root, "fixture-cook", ["cooksounds",
        "-soundbanksdir=" + str(inputs) + "\\", "-outdir=" + str(output) + "\\",
        "-platform=pc_dx12", "-r4remastersounds", "-outsplitfile=" + str(output / "audio-split.list")])
    cache = output / "CookedPC/soundspc.cache"
    first = verify_cache(cache, inputs)
    split = root / "native-fixture-split"
    execute(executable, root, "fixture-split", ["splitcache", "sounds", "-platform=pc_dx12",
        "-split=" + str(output / "audio-split.list"), "-file=" + str(cache), "-outdir=" + str(split) + "\\"])
    second = verify_cache(split / "content0/soundspc.cache", inputs)
    (root / "fixture-verified.json").write_text(json.dumps({"cooked": first, "split": second,
        "native_fixture_only": True, "live_mod_loader_test": False}, indent=2) + "\n")
    print(json.dumps({"cache_bytes": first["bytes"], "split_bytes": second["bytes"], "bank_count": 2}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "native-fixture"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--redkit", type=Path)
    args = parser.parse_args()
    if args.operation == "prepare":
        if args.redkit is None:
            parser.error("prepare requires --redkit")
        prepare(args.redkit, args.root)
    else:
        fixture(args.root)
