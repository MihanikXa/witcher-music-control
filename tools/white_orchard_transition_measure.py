"""Read-only native-selector profiler/PCM summary; no runtime certification."""
import argparse
import json
import math
from pathlib import Path
import statistics

from white_orchard_fade_measure import pcm
from white_orchard_prepare import build_path, digest


def measure(folder):
    folder = build_path(folder)
    evidence = json.loads((folder / "results.json").read_text())
    result = {"evidence_sha256": digest(folder / "results.json"), "cases": [],
              "timing_note": "Profiler wall times and PCM capture times have different origins. No sample-exact alignment is claimed."}
    for case in evidence["cases"]:
        row = {"mode": case["mode"], "case": case["case"], "events": case["events"], "voices": {}}
        times = [s["time"] for s in case["samples"]]
        gaps = [b-a for a, b in zip(times, times[1:])]
        row["sample_spacing_seconds"] = {"median": statistics.median(gaps), "maximum": max(gaps)}
        for sample in case["samples"]:
            for voice in sample["voices"]:
                contribution = sample["contributions"].get(str(voice["pipelineID"]))
                if not contribution:
                    continue
                contribution = contribution["return"]
                names = [n["name"] for n in contribution["objects"]]
                key = "/".join(names)
                trace = row["voices"].setdefault(key, {"object": voice["objectName"], "path": names, "envelope": []})
                trace["envelope"].append({"wall_time": sample["time"], "total_db": contribution["volume"],
                                          "virtual": voice["isVirtual"]})
        path = folder / (case["mode"] + "-" + case["case"] + ".wav")
        row["recording_present"] = path.is_file()
        if path.is_file():
            data, channels, rate = pcm(path)
            hop = rate // 20 * channels
            envelope = [math.sqrt(sum(v*v for v in data[i:i+hop]) / len(data[i:i+hop])) for i in range(0, len(data), hop)]
            row["pcm"] = {"sha256": digest(path), "seconds": len(data)/channels/rate,
                          "channels": channels, "rate": rate, "rms50ms": envelope}
        else:
            row["recording_note"] = "Recorder did not emit a file while voices/bus were inaudible or virtual; this is not a measured zero-PCM capture."
        result["cases"].append(row)
    output = folder / "transition-measurements.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "cases": len(result["cases"])}))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    measure(parser.parse_args().folder)
