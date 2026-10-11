"""Measure retained continuous tone captures without altering recordings."""
import argparse
import array
import json
import math
from pathlib import Path
import struct
from white_orchard_prepare import build_path


def pcm(path):
    data = path.read_bytes()
    chunks = {}
    offset = 12
    while offset + 8 <= len(data):
        tag, size = struct.unpack_from("<4sI", data, offset)
        chunks[tag] = data[offset + 8:offset + 8 + size]
        offset += 8 + size + size % 2
    fmt = struct.unpack_from("<HHIIHH", chunks[b"fmt "])
    if fmt[5] != 16:
        raise ValueError("Requires PCM16")
    return array.array("h", chunks[b"data"]), fmt[1], fmt[2]


def analyze(path, states, interval):
    samples, channels, rate = pcm(path)
    frames = len(samples) // channels
    def rms(begin, end):
        values = [samples[int(begin * rate) * channels + c:min(frames, int(end * rate)) * channels:channels]
                  for c in range(channels)]
        return [math.sqrt(sum(x*x for x in v)/len(v)) for v in values]
    reference = rms(1, 2)
    result = {"path": str(path), "seconds": frames / rate, "reference_rms": reference,
              "steady_states": [], "transitions": [], "envelope_100ms": []}
    for row in states:
        begin = row["wall_seconds"] + interval - 1.2
        level = rms(begin, begin + .7)
        result["steady_states"].append({"state": row["state"], "rms": level,
            "relative_db": [20 * math.log10(v/r) if v and r else None for v, r in zip(level, reference)]})
    for row in states[1:]:
        # Broad windows include native ramps and wall/audio scheduling uncertainty.
        start = max(1, int((row["wall_seconds"] - .25) * rate))
        end = min(frames - 1, int((row["wall_seconds"] + 1.75) * rate))
        result["transitions"].append({"destination": row["state"],
            "peak_adjacent_pcm_step": [max(abs(samples[(i+1)*channels+c]-samples[i*channels+c])
                                           for i in range(start, end)) for c in range(channels)]})
    for i in range(5, frames // (rate//10) - 5):
        result["envelope_100ms"].append({"time": i/10, "rms": rms(i/10, (i+1)/10)})
    return result


def run(folder, original):
    folder = build_path(folder)
    evidence = json.loads((folder / "results.json").read_text())
    results = {"native": [analyze(folder / (r["label"] + ".wav"), r["states"], 4)
                          for r in evidence["runs"]]}
    expected = {"unequal": [0, -12, -24, -6, 0],
                "all_unity": [0, 0, 0, 0, 0], "defaults": [0, None, None, 0, 0]}
    checks = []
    for run, data in zip(evidence["runs"], results["native"]):
        for row, target in zip(data["steady_states"], expected[run["label"]]):
            values = row["relative_db"]
            checks.append({"check": run["label"] + ":" + row["state"],
                "passed": all(v is None for v in values) if target is None else
                          all(v is not None and abs(v-target) < .15 for v in values)})
        for row in data["transitions"]:
            checks.append({"check": run["label"] + ":smooth-to-" + row["destination"],
                "passed": all(value <= normal + 2 for value, normal in
                              zip(row["peak_adjacent_pcm_step"], [66, 88, 110, 14, 132, 154]))})
        if run["label"] == "all_unity":
            checks.append({"check": "unity-crossfade-envelope", "passed": all(
                abs(20 * math.log10(v/r)) < .05 for point in data["envelope_100ms"]
                for v, r in zip(point["rms"], data["reference_rms"]))})
    results["checks"] = checks
    results["passed"] = all(check["passed"] for check in checks)
    results["limits"] = "PCM16 tone/state proof only; not a live-game or exact float-zero measurement"
    if original:
        original = build_path(original)
        results["boolean_baseline"] = analyze(original / "world-gates.wav",
            json.loads((original / "transitions.json").read_text()), 3)
    (folder / "measured.json").write_text(json.dumps(results, indent=2) + "\n")
    for row in results["native"]:
        print(json.dumps({"file": Path(row["path"]).name,
            "seconds": row["seconds"], "steady_db": [r["relative_db"][0] for r in row["steady_states"]],
            "peak_steps": [r["peak_adjacent_pcm_step"] for r in row["transitions"]]}))
    if original:
        print(json.dumps({"boolean_steps": [r["peak_adjacent_pcm_step"] for r in results["boolean_baseline"]["transitions"]]}))
    if not results["passed"]:
        raise SystemExit("Native fade acceptance checks failed")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--folder", type=Path, required=True)
    p.add_argument("--original", type=Path)
    args = p.parse_args()
    run(args.folder, args.original)
