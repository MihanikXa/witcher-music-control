"""Prepare offline A/B load-test caches from existing UNMODIFIED banks.

No Wwise generation, licence operation, game installation or save access.
This diagnostic package does not waive the failed licensed compatibility gate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

from white_orchard_compare import read_bank, difference
from white_orchard_cooker import prepare, execute
from white_orchard_prepare import build_path, digest
from white_orchard_state_bank_audit import header

NATIVE_INIT = '2dcb418b9f96389a57341a49e86cdcb0c18d95552a0e17dccf10d4df1d54d277'
NATIVE_BANK = '75984abb6dedb810ddebf076d82cbdd6fe69715279b9248d84d62ea48d079912'
LICENSED_BANK = '5b28f4ee5f286ec46a80120ea632c1d2ca715c0e2b05fb90ddd411f16e9a953a'


def verify(cache, bank):
    data = cache.read_bytes()
    if data[:8] != b'CS3W\x02\0\0\0' or len(data) < 64:
        raise ValueError('Unexpected cache header')
    if struct.unpack_from('<I', data, 24)[0] != 1:
        raise ValueError('Expected one regional entry, no Init or WEM')
    start = struct.unpack_from('<Q', data, 32)[0]
    size = struct.unpack_from('<I', data, 40)[0]
    if start + size + 24 != len(data):
        raise ValueError('Unexpected cache table bounds')
    name_offset, offset, length = struct.unpack_from('<QQQ', data, start + size)
    if name_offset >= size or offset < 64 or offset + length > start:
        raise ValueError('Invalid cache entry bounds')
    name = data[start + name_offset:start + size].split(b'\0', 1)[0].decode('ascii')
    if name != 'music_prologue.bnk' or data[offset:offset + length] != bank.read_bytes():
        raise ValueError('Regional payload differs from exact input')
    return {'path': str(cache), 'bytes': len(data), 'sha256': digest(cache),
            'entry': name, 'payload_offset': offset, 'payload_bytes': length,
            'payload_sha256': hashlib.sha256(data[offset:offset + length]).hexdigest(),
            'init_entry': False, 'byte_identical': True}


def stage(root, label, bank):
    root = build_path(root)
    manifest = json.loads((root / 'bootstrap-manifest.json').read_text())
    redkit = Path(manifest['redkit'])
    native = read_bank(redkit / 'r4data/soundbanks/Pc/music_prologue.bnk')
    selected = read_bank(bank)
    expected = {'control': (NATIVE_BANK, 39), 'licensed': (LICENSED_BANK, 17637)}
    sha, project_id = expected[label]
    diff = difference(native, selected)
    if selected['sha256'] != sha or header(selected)['project_id'] != project_id:
        raise ValueError('Not the recorded unmodified A/B input')
    if diff['added'] or diff['removed'] or diff['changed'] or set(diff['chunk_changed']) - {'BKHD'}:
        raise ValueError('Unexpected content change; never package a candidate here')
    protected = [root / 'bin/initialdata/sound/Init.bnk', root / 'r4data/soundbanks/Pc/Init.bnk']
    if any(digest(p) != NATIVE_INIT for p in protected):
        raise ValueError('Bootstrap must retain vanilla Init')
    inputs, output, split = [root / (label + '-' + suffix) for suffix in ('input', 'cooked', 'split')]
    if any(p.exists() for p in (inputs, output, split, root / (label + '-verified.json'))):
        raise FileExistsError('Use a fresh label/root; preserve evidence')
    inputs.mkdir(); output.mkdir()
    shutil.copyfile(bank, inputs / 'music_prologue.bnk')
    exe = redkit / 'bin/x64_RedKit/wcc_lite.exe'
    execute(exe, root, label + '-cook', ['cooksounds', '-soundbanksdir=' + str(inputs) + '\\',
        '-outdir=' + str(output) + '\\', '-platform=pc_dx12', '-r4remastersounds',
        '-outsplitfile=' + str(output / 'audio-split.list')])
    cooked = verify(output / 'CookedPC/soundspc.cache', bank)
    execute(exe, root, label + '-split', ['splitcache', 'sounds', '-platform=pc_dx12',
        '-split=' + str(output / 'audio-split.list'), '-file=' + cooked['path'],
        '-outdir=' + str(split) + '\\'])
    readback = verify(split / 'content0/soundspc.cache', bank)
    package = root / 'packages' / label / 'modWMCBankLoadingTest/content/soundspc.cache'
    package.parent.mkdir(parents=True)
    shutil.copyfile(Path(cooked['path']), package)
    if digest(package) != cooked['sha256'] or any(digest(p) != NATIVE_INIT for p in protected):
        raise ValueError('Package or native bootstrap changed')
    result = {'label': label, 'input_bank': str(bank), 'project_id': project_id,
              'cooked': cooked, 'native_reader': readback, 'package': str(package),
              'retained_init_sha256': NATIVE_INIT, 'diagnostic_only': True,
              'deployed': False, 'runtime_validated': False}
    (root / (label + '-verified.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'control', 'licensed'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--redkit', type=Path)
    parser.add_argument('--bank', type=Path)
    args = parser.parse_args()
    if args.operation == 'prepare':
        if not args.redkit:
            parser.error('--redkit required')
        prepare(args.redkit, args.root)
    else:
        if not args.bank:
            parser.error('--bank required')
        stage(args.root, args.operation, args.bank.resolve())
