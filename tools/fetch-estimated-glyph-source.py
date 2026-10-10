"""Fetch pinned OFL sources for U+212E only into a fresh ignored directory."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if ROOT / 'build' not in out.parents or out.exists():
        raise ValueError('Fresh private build directory required')
    pins = json.loads((ROOT / 'src/fonts/noto-estimated-source.json').read_text())
    out.mkdir(parents=True)
    for filename, item in pins['files'].items():
        with urllib.request.urlopen(item['url'], timeout=45) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Pinned independent source hash mismatch: ' + filename)
        (out / filename).write_bytes(data)
    (out / 'provenance.json').write_text(json.dumps(pins, indent=2))


if __name__ == '__main__':
    main()
