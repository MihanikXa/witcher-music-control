"""Measure the recorded validation probe, including PCM quantization limits."""
import argparse
import array
import json
import math
from pathlib import Path
import struct
from white_orchard_prepare import build_path


def measure(path):
    data = path.read_bytes()
    offset = 12
    chunks = {}
    while offset + 8 <= len(data):
        tag, length = struct.unpack_from("<4sI", data, offset)
        chunks[tag] = data[offset + 8:offset + 8 + length]
        offset += 8 + length + length % 2
    fmt = struct.unpack_from("<HHIIHH", chunks[b"fmt "])
    if fmt[5] != 16:
        raise ValueError("This measurement expects 16-bit PCM")
    samples = array.array("h", chunks[b"data"])
    channels, rate = fmt[1], fmt[2]
    frames = len(samples) // channels
    # Stable middle-quarter window avoids playback-start and stop transients.
    begin, end = frames // 2 * channels, frames * 3 // 4 * channels
    rms = []
    for channel in range(channels):
        values = samples[begin + channel:end:channels]
        if not values:
            raise ValueError("Empty recording window")
        rms.append(math.sqrt(sum(x * x for x in values) / len(values)))
    return {"channels": channels, "bits": fmt[5], "sample_rate": rate,
            "seconds": frames / rate, "rms_pcm": rms,
            "zero_pcm": [x == 0 for x in rms]}


def matrix(folder):
    folder = build_path(folder)
    evidence = json.loads((folder / "matrix.json").read_text())
    config = json.loads(Path("src/wwise/white-orchard-mixer.json").read_text())
    reference = measure(Path(evidence["cases"][0]["recording"]))["rms_pcm"]
    output = {"reference_rms_pcm": reference, "tolerance_db": .15, "cases": []}
    for row in evidence["cases"]:
        result = measure(Path(row["recording"]))
        expected = 0
        for index, states in enumerate(config["active_states"].values()):
            if row["state"] in states:
                expected = row["values_db"][index]
        actual = [20 * math.log10(v / ref) if v else None
                  for v, ref in zip(result["rms_pcm"], reference)]
        passed = (all(result["zero_pcm"]) if expected == -96.3 else
                  all(v is not None and abs(v - expected) < .15 for v in actual))
        output["cases"].append({"state": row["state"], "requested_db": row["values_db"],
                                "expected_extra_db": expected, "measured_extra_db": actual,
                                "passed": passed, **result})
    output["passed"] = all(row["passed"] for row in output["cases"])
    output["zero_limit"] = "Zero PCM at 16 bits does not establish internal floating-point or game digital zero"
    (folder / "measured.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"cases": len(output["cases"]), "passed": output["passed"],
                      "failed_states": [r["state"] for r in output["cases"] if not r["passed"]]}))
    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args()
    matrix(args.folder)
