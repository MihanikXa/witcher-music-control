"""Create pinned A/C Vortex ZIPs or verify a future deployment, read-only.

No Vortex/profile mutation, installation, launch, save access or bank generation.
The installed Witcher3 top-level installer was audited in report23.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from white_orchard_prepare import REPO, build_path, digest
from white_orchard_loading_package import NATIVE_INIT

ENTRY = 'Mods/modWMCBankLoadingTest/content/soundspc.cache'
VARIANTS = {
    'A': ('WMC White Orchard — Vanilla Control',
          'build/white-orchard-bank-loading-test/packages/control/modWMCBankLoadingTest/content/soundspc.cache',
          'f7a0c2c20d698d4dbb514e573c64d67df7e9c57ab854012bd0adc6b4afdde40a',
          '75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912'),
    'C': ('WMC White Orchard — Music Control Test',
          'build/licensed-white-orchard-stage1/cooker/packages/candidate/modWMCBankLoadingTest/content/soundspc.cache',
          'a2b8cc23285c5b6cd392b0301328d75bd545dde8d9e0c06007b674b68a14aa12',
          '80c8a5e279c49305c164ff10a6a39cc2fd8d7f28e85479015e1349008e6ae698'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def archives(output):
    output = build_path(output)
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for variant, (title, relative, expected, bank_hash) in VARIANTS.items():
        source = REPO / relative
        data = source.read_bytes()
        if sha(data) != expected:
            raise ValueError('Staged cache does not match the validated evidence')
        # Exact cache hash pins wrapper, sole-entry table and bank bytes already
        # verified by the native cooker. No extraction/rewriting of the bank.
        archive = output / (title + '.zip')
        member = zipfile.ZipInfo(ENTRY, date_time=(2026, 10, 12, 0, 0, 0))
        member.compress_type = zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(archive, 'x') as z:
            z.writestr(member, data)
        with zipfile.ZipFile(archive) as z:
            if z.namelist() != [ENTRY] or z.testzip() is not None or z.read(ENTRY) != data:
                raise ValueError('ZIP payload or path changed')
        records.append(dict(variant=variant, title=title, archive=str(archive),
                            archive_sha256=digest(archive), archive_bytes=archive.stat().st_size,
                            zip_entry=ENTRY, cache_sha256=expected, bank_sha256=bank_hash,
                            installed=False, runtime_validated=False))
    (output / 'archives-verified.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps(records, ensure_ascii=False))


def installed(game, variant):
    """Verify future real deployed bytes; never follow an install command."""
    game = game.resolve()
    init = game / 'bin/initialdata/sound/Init.bnk'
    if digest(init) != NATIVE_INIT:
        raise ValueError('Original Init differs; stop the experiment')
    caches = sorted(p for folder in ('Mods', 'DLC') for p in (game / folder).rglob('*')
                    if p.is_file() and p.name.lower() == 'soundspc.cache')
    target = game / ENTRY
    if caches != [target]:
        raise ValueError('Missing, competing or nested audio caches: ' + str(caches))
    unexpected_banks = [str(p) for folder in ('Mods', 'DLC')
                        for p in (game / folder).rglob('*') if p.is_file() and p.suffix.lower() == '.bnk']
    if unexpected_banks:
        raise ValueError('Loose mod banks require review: ' + str(unexpected_banks))
    if digest(target) != VARIANTS[variant][2]:
        raise ValueError('Deployed cache is not the intended A/C variant')
    print(json.dumps(dict(variant=variant, path=str(target), cache_sha256=digest(target),
                          native_init_unchanged=True, sole_audio_cache=True,
                          runtime_validated=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    create = sub.add_parser('archives')
    create.add_argument('--output', type=Path, required=True)
    check = sub.add_parser('verify-installed')
    check.add_argument('--game', type=Path, required=True)
    check.add_argument('--variant', choices=VARIANTS, required=True)
    args = parser.parse_args()
    if args.operation == 'archives':
        archives(args.output)
    else:
        installed(args.game, args.variant)
