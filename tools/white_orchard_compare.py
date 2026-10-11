"""Compare bank chunks and HIRC records without interpreting opaque bodies."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from white_orchard_prepare import build_path


def read_bank(path):
    data = path.read_bytes()
    offset = 0
    chunks = {}
    while offset < len(data):
        tag, length = struct.unpack_from("<4sI", data, offset)
        if offset + 8 + length > len(data):
            raise ValueError("Truncated bank chunk")
        chunks[tag.decode()] = data[offset + 8:offset + 8 + length]
        offset += 8 + length
    hirc = chunks["HIRC"]
    offset = 4
    records = {}
    for _ in range(struct.unpack_from("<I", hirc)[0]):
        kind, length = struct.unpack_from("<BI", hirc, offset)
        ident = struct.unpack_from("<I", hirc, offset + 5)[0]
        records[ident] = (kind, hirc[offset + 9:offset + 5 + length])
        offset += 5 + length
    if offset != len(hirc):
        raise ValueError("HIRC length mismatch")
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "chunks": {k: len(v) for k, v in chunks.items()},
            "records": records, "payload": chunks}


def difference(before, after):
    a, b = before["records"], after["records"]
    return {
        "added": [{"id": i, "type": b[i][0]} for i in sorted(b.keys() - a.keys())],
        "removed": [{"id": i, "type": a[i][0]} for i in sorted(a.keys() - b.keys())],
        "changed": [{"id": i, "type": b[i][0], "before_bytes": len(a[i][1]),
                     "after_bytes": len(b[i][1])} for i in sorted(a.keys() & b.keys()) if a[i] != b[i]],
        "chunk_changed": [k for k in sorted(before["payload"].keys() | after["payload"].keys())
                          if before["payload"].get(k) != after["payload"].get(k)]}


def compare(vanilla, baseline, prototype, output):
    output = build_path(output)
    report = {}
    for bank in ("Init.bnk", "music_prologue.bnk"):
        a, b, c = [read_bank(folder / bank) for folder in (vanilla, baseline, prototype)]
        report[bank] = {
            name: {k: v for k, v in value.items() if k not in ("records", "payload")}
            for name, value in (("vanilla", a), ("baseline", b), ("prototype", c))}
        report[bank].update(baseline_vs_vanilla=difference(a, b), prototype_vs_baseline=difference(b, c))
    controlled = report["music_prologue.bnk"]["prototype_vs_baseline"]
    if controlled["added"] or controlled["removed"] or [x["id"] for x in controlled["changed"]] != [1033516231]:
        raise RuntimeError("Unexpected regional bank changes")
    if any(chunk in controlled["chunk_changed"] for chunk in ("DIDX", "DATA")):
        raise RuntimeError("Embedded media changed")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"regional_change": controlled, "init_baseline_missing":
                      len(report["Init.bnk"]["baseline_vs_vanilla"]["removed"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("vanilla", "baseline", "prototype", "output"):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    compare(args.vanilla, args.baseline, args.prototype, args.output)
