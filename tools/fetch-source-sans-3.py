"""Download independently licensed, pinned Adobe inputs into fresh build only."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    out = parser.parse_args().out.resolve()
    if ROOT/'build' not in out.parents or out.exists():
        raise ValueError('Fresh private build directory required')
    pins = json.loads((ROOT/'src/fonts/source-sans-3-source.json').read_text())
    out.mkdir(parents=True)
    for name,item in pins['files'].items():
        data = urllib.request.urlopen(item['url'],timeout=45).read()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Pinned upstream source differs: '+name)
        (out/name).write_bytes(data)
    (out/'provenance.json').write_text(json.dumps(pins,indent=2))


if __name__=='__main__': main()
