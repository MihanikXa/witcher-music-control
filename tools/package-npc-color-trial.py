"""Build one original loose-script ZIP after bounded compiler regression controls.

This is a private runtime experiment, not a claim of complete retail multi-blob
simulation. No resources, compiled blobs, compatibility replacements or settings.
"""
import argparse
import configparser
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fallback', ROOT / 'tools/check-npc-fallback.py')
fallback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback)
MEMBER = 'Mods/modQuietEditorialNPCColors/content/scripts/local/quietEditorialNameColors.ws'


def gate(receipt, candidate, probe=False):
    results = receipt['results']
    labels = ['baseline', 'paired_noop', 'candidate'] if probe else ['baseline', 'npc_noop', 'hud_noop', 'candidate']
    if [r['label'] for r in results] != labels:
        raise ValueError('All ordered compiler controls required')
    if not receipt['source_inputs_unchanged'] or not all(r['success'] and not r['errors'] for r in results):
        raise ValueError('Compiler failure or changed inputs')
    if results[-1]['source_sha256'] != hashlib.sha256(candidate).hexdigest():
        raise ValueError('Candidate differs from compiled source')
    expected = results[1]['assertions_added']
    if len(expected) != 1 or (sum(expected.values()) < 1 if probe else sum(expected.values()) != 1) or not any(
            'scriptCompiledCode.cpp:56' in s and '!m_sourceFile.Empty()' in s for s in expected):
        raise ValueError('Unexpected no-op diagnostic')
    for r in results[1:]:
        if r['assertions_added'] != expected or any(r[k] for k in (
                'assertions_removed', 'warnings_added', 'warnings_removed')):
            raise ValueError('Diagnostic regression beyond no-op controls')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--controls', type=Path, required=True)
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--settings', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--probe', action='store_true', help='Package bounded original diagnostic, requiring v2 disabled')
    ap.add_argument('--v4', action='store_true', help='Package clean UInt color trial, requiring v2 and v3 disabled')
    a = ap.parse_args()
    if a.probe and a.v4:
        raise ValueError('Choose one package mode')
    work = a.out.resolve()
    if ROOT / 'deploy' not in work.parents or work.exists():
        raise ValueError('Fresh private deploy directory required')
    source = ROOT / 'src/npc' / ('quietEditorialNameProbe.ws' if a.probe else 'quietEditorialNameColors.ws')
    member = 'Mods/modQuietEditorialNPCProbe/content/scripts/local/quietEditorialNameProbe.ws' if a.probe else MEMBER
    if a.v4:
        member = 'Mods/modQuietEditorialNPCColorsV4/content/scripts/local/quietEditorialNameColorsV4.ws'
    candidate = fallback.text(source).encode('utf-8')
    receipt = json.loads(a.controls.read_text())
    gate(receipt, candidate, probe=a.probe)
    if fallback.sha(Path(receipt['results'][0]['command'][0])) != receipt['compiler_sha256']:
        raise ValueError('Compiler changed after controls')
    # Recheck every compiler input, not just an old receipt's boolean.
    if any(fallback.sha(Path(s['path'])) != s['sha256'] for s in receipt['sources']):
        raise ValueError('Compiler assembly changed after validation')
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read_string(fallback.text(a.settings))
    mods = [s for s in cfg.sections() if cfg[s].get('Enabled') == '1']
    superseded = []
    must_disable = ['modQuietEditorialNPCColors', 'modQuietEditorialNPCProbe'] if a.v4 else (['modQuietEditorialNPCColors'] if a.probe else [])
    for old in must_disable:
        if old in mods:
            superseded.append(old)
            mods.remove(old)
    assembly_text_hashes = {hashlib.sha256(fallback.text(Path(s['path'])).encode()).hexdigest()
                            for s in receipt['sources']}
    intersection = []
    opaque = []
    providers = []
    for mod in mods:
        content = a.game / 'Mods' / mod / 'content'
        info = content / 'info.json'
        if info.exists() and json.loads(info.read_text(encoding='utf-8-sig')).get('useLooseScripts') is False:
            opaque.append(mod)
        for p in (content / 'scripts').rglob('*.ws'):
            t = fallback.text(p)
            if p.relative_to(content / 'scripts').as_posix().lower() == member.split('/scripts/')[1].lower():
                raise ValueError('Existing package file collision')
            targets = r'(?:CR4HudModuleEnemyFocus|CR4ScriptedHud)' if a.probe else 'CR4HudModuleEnemyFocus'
            methods = r'(?:OnTick|UpdateName)' if a.probe else 'OnTick'
            if re.search(r'@wrapMethod\s*\(\s*' + targets + r'\s*\)\s*(?:function|event)\s+' + methods + r'\b', t):
                covered = hashlib.sha256(t.encode()).hexdigest() in assembly_text_hashes
                intersection.append(dict(mod=mod, path=str(p), sha256=fallback.sha(p), source_assembly_covered=covered))
                if not covered:
                    raise ValueError('Uncompiled known affected wrapper')
            if p.name.lower() in ('sah_hooks.ws', 'hudmoduleenemyfocus.ws'):
                providers.append(dict(mod=mod, path=str(p), sha256=fallback.sha(p),
                                      source_assembly_covered=hashlib.sha256(t.encode()).hexdigest() in assembly_text_hashes))
    required = [p for p in providers if p['mod'] in ('modFriendlyHUD', 'modSeamlessAdaptiveHUD')]
    if not required or not all(p['source_assembly_covered'] for p in required):
        raise ValueError('Current FriendlyHUD/SAH source mismatch')
    work.mkdir(parents=True)
    archive = work / ('QuietEditorial-NPC-NameProbe-private-test.zip' if a.probe else 'QuietEditorial-NPC-Colors-private-test.zip')
    if a.v4:
        archive = work / 'QuietEditorial-NPC-Colors-v4-private-test.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo(member, (2026, 10, 9, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, candidate)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or z.namelist() != [member] or z.read(member) != candidate:
            raise ValueError('ZIP routing or content validation failed')
    manifest = dict(status='private-bounded-name-diagnostic' if a.probe else 'private-color-only-runtime-trial', zip_path=str(archive),
                    zip_sha256=fallback.sha(archive), zip_bytes=archive.stat().st_size,
                    member=member, member_sha256=hashlib.sha256(candidate).hexdigest(),
                    compiler_sha256=receipt['compiler_sha256'], controls_sha256=fallback.sha(a.controls),
                    settings_sha256=fallback.sha(a.settings), on_tick_intersections=intersection,
                    must_disable_mods=must_disable,
                    currently_enabled_superseded_mods=superseded,
                    providers=providers, opaque_mods_not_recompiled=opaque,
                    vortex_route='witcher3tl installer preserves Mods/; witcher3tl deploys at game root',
                    runtime_tested=False, vortex_preview_executed=False, deployed=False,
                    shadow_changes=False, resource_replacements=[], compiled_blobs_packaged=False)
    if a.v4:
        manifest['trial_version'] = 4
        manifest['status'] = 'private-clean-UInt-color-trial; runtime-acceptance-pending'
        manifest['diagnostic_instrumentation'] = False
    (work / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
