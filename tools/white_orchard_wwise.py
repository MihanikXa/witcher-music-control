"""Local WAAPI client and guarded selective generator (standard library only)."""
import argparse
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.request
from white_orchard_prepare import build_path


class Waapi:
    def __init__(self, port=18090):
        self.url = f"http://127.0.0.1:{port}/waapi"

    def call(self, uri, args=None, options=None):
        body = json.dumps({"uri": uri, "args": args or {}, "options": options or {}}).encode()
        request = urllib.request.Request(self.url, body, {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode()) from error
        if "error" in result:
            raise RuntimeError(json.dumps(result))
        return result


def generate(console, project, output, bank='music_prologue'):
    project = build_path(project)
    output = build_path(output)
    if project.parent.name == "validation":
        raise ValueError("Never generate banks from the instrumented validation project")
    if not project.is_file():
        raise FileNotFoundError(project)
    if bank not in {'music_prologue', 'music_nomansgrad', 'music_skellige', 'music_kaer_morhen',
                    'music_toussaint', 'music_wyzima_castle', 'music_misty_island', 'music_spiral'}:
        raise ValueError('Unreviewed regional bank name')
    output.mkdir(parents=True, exist_ok=False)
    args = [str(console), "generate-soundbank", str(project),
            "--bank", bank, "--platform", "Windows", "--language", "SFX",
            "--soundbank-path", "Windows", str(output),
            "--cache", str(project.parent / ".cache"),
            "--root-output-path", str(output / "metadata"),
            "--no-source-control", "--no-wwise-dat", "--no-decode",
            "--custom-pre-gen-cmd", "Windows", "",
            "--custom-post-gen-cmd", "Windows", "",
            "--custom-global-opening-cmd", "",
            "--custom-global-closing-cmd", ""]
    (output / "command.json").write_text(json.dumps(args, indent=2) + "\n")
    with (output / "generation.log").open("w", encoding="utf-8") as log:
        process = subprocess.run(args, cwd=project.parent, stdout=log, stderr=subprocess.STDOUT)
    names = sorted(p.name for p in output.rglob("*.bnk"))
    result = {"exit_code": process.returncode, "banks": names,
              "output": str(output), "selected_bank": bank,
              "expected_banks_only": names == sorted(["Init.bnk", bank + '.bnk'])}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    if process.returncode not in (0, 2) or not result["expected_banks_only"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--console", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument('--bank', default='music_prologue')
    args = parser.parse_args()
    generate(args.console, args.project, args.output, args.bank)
