"""Native multi-bank cache staging from independent verified regional outputs."""
import argparse
import json
from pathlib import Path
import subprocess
import shutil
import zipfile
import re
from collections import Counter

from regional_music_cache import verify_bytes
from white_orchard_cooker import prepare
from white_orchard_loading_package import NATIVE_INIT
from white_orchard_prepare import build_path, digest
from music_region_inventory import REGIONS


def verified_inputs(spec):
    banks = {}
    for item in spec['banks']:
        bank = build_path(item['path'])
        if bank.name not in {r+'.bnk' for r in REGIONS}:raise ValueError('Not an approved regional bank filename')
        proof = json.loads(build_path(item['proof']).read_text(encoding='utf-8'))
        decoded = proof.get('decoded_fields', {})
        gate = proof.get('bank_preflight', {})
        if (not proof.get('passed') or not decoded.get('passed') or not gate.get('passed')
                or decoded.get('candidate_sha256') != digest(bank)
                or gate.get('candidate_sha256') != digest(bank)
                or digest(bank) != item['sha256'] or not decoded.get('global_generated_data_exact')
                or not decoded.get('paired_generated_media_exact') or not proof.get('original_audio_unchanged')):
            raise ValueError('Missing/stale independent regional bank proof')
        if bank.name in banks:
            raise ValueError('Duplicate bank')
        banks[bank.name] = bank
    expected={r+'.bnk' for r in spec.get('regions',['music_prologue','music_nomansgrad'])}
    if len(expected)<2 or set(banks)!=expected:raise ValueError('Bundle differs from explicit region set')
    return banks


def reviewed_diagnostics(root,reference,cook_label,names):
    def rows(folder,label):
        result=[]
        for line in (folder/(label+'.log')).read_text(encoding='utf-8',errors='replace').splitlines():
            if '[Error]' not in line and '[Warning]' not in line:continue
            line=re.sub(r'^\[[^]]+\]','',line).lower().replace(str(folder.resolve()).lower(),'<root>')
            line=line.replace('bundle-input','<input>').replace('regional-input','<input>')
            line=re.sub(r"c:\\users\\[^']*?\\documents\\the witcher 3",'<documents>',line)
            result.append(line)
        return Counter(result)
    expected=rows(reference,'regional-cook-confirmed')
    for name in names:
        if name=='music_nomansgrad.bnk':continue
        base=name.removesuffix('.bnk')
        originals=[r for r in expected if 'music_nomansgrad.bnk' in r or 'music_nomansgrad.txt' in r]
        for row in originals:expected[row.replace('music_nomansgrad',base)]+=expected[row]
    actual=rows(root,cook_label)
    if actual!=expected or rows(root,'bundle-split')!=rows(reference,'regional-split-confirmed'):
        raise ValueError('Unreviewed native cooker/split diagnostics')
    return {'passed':True,'cook_diagnostic_rows':sum(actual.values()),'split_diagnostic_rows':sum(rows(root,'bundle-split').values()),'reviewed_missing_description_and_seed_mapping':True}


def native(exe, root, label, arguments):
    """Capture native exit status with the established PowerShell launcher."""
    def quote(value): return "'" + str(value).replace("'", "''") + "'"
    args = arguments + ['-root', str(root) + '\\', '-noninteractivecrash']
    script = root / (label + '.ps1')
    if script.exists(): raise FileExistsError(script)
    code = "$ErrorActionPreference='Stop'\n"
    code += '$argsNative=@(' + ','.join(quote(a) for a in args) + ')\n'
    code += '$p=Start-Process -FilePath ' + quote(exe) + ' -ArgumentList $argsNative -WorkingDirectory ' + quote(root/'bin/x64')
    code += ' -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput ' + quote(root/(label+'.log'))
    code += ' -RedirectStandardError ' + quote(root/(label+'.stderr.log')) + '\n'
    code += '$p.Id | Set-Content ' + quote(root/(label+'-pid.txt')) + '\n'
    code += '@{exit_code=$p.ExitCode;timeout=$false;args=$argsNative} | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 ' + quote(root/(label+'-result.json')) + '\n'
    script.write_text(code, encoding='utf-8')
    subprocess.run(['powershell.exe','-NoProfile','-File',str(script)],check=True)
    result = json.loads((root/(label+'-result.json')).read_text(encoding='utf-8-sig'))
    if result['exit_code'] != 0 or result['timeout']:
        raise ValueError('Native command failed; preserve output/diagnostics')
    return result


def stage(redkit, spec_path, root, retry_recording=False):
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    banks = verified_inputs(spec)
    root = build_path(root)
    if retry_recording:
        prior=json.loads((root/'bundle-cook-result.json').read_text(encoding='utf-8-sig'))
        if prior['exit_code'] is not None or prior['timeout']:raise ValueError('Not the retained status-recording failure')
    else:prepare(redkit,root)
    inputs=root/'bundle-input';cooked=root/('bundle-cooked-confirmed' if retry_recording else 'bundle-cooked');split=root/'bundle-split'
    if not retry_recording:
        inputs.mkdir()
        for name,bank in banks.items():shutil.copyfile(bank,inputs/name)
    elif any((inputs/n).read_bytes()!=p.read_bytes() for n,p in banks.items()):raise ValueError('Retained inputs changed')
    cooked.mkdir()
    exe=redkit/'bin/x64_RedKit/wcc_lite.exe'
    native(exe,root,'bundle-cook-confirmed' if retry_recording else 'bundle-cook',['cooksounds','-soundbanksdir='+str(inputs)+'\\',
        '-outdir='+str(cooked)+'\\','-platform=pc_dx12','-r4remastersounds',
        '-outsplitfile='+str(cooked/'audio-split.list')])
    cache=cooked/'CookedPC/soundspc.cache';expected={n:p.read_bytes() for n,p in banks.items()}
    first=verify_bytes(cache.read_bytes(),expected)
    native(exe,root,'bundle-split',['splitcache','sounds','-platform=pc_dx12',
        '-split='+str(cooked/'audio-split.list'),'-file='+str(cache),'-outdir='+str(split)+'\\'])
    second=verify_bytes((split/'content0/soundspc.cache').read_bytes(),expected)
    diagnostics=reviewed_diagnostics(root,build_path(spec['reference_cooker']),
                                    'bundle-cook-confirmed' if retry_recording else 'bundle-cook',banks)
    archive=root/'archives'/spec['archive_name'];archive.parent.mkdir()
    if Path(spec['archive_name']).name!=spec['archive_name']:raise ValueError('Unsafe archive name')
    entry='Mods/modWMCConsolidated/content/soundspc.cache'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:z.writestr(entry,cache.read_bytes())
    with zipfile.ZipFile(archive) as z:
        if z.namelist()!=[entry] or z.testzip() or z.read(entry)!=cache.read_bytes():raise ValueError('Archive mismatch')
    if any(digest(p)!=next(x['sha256'] for x in spec['banks'] if build_path(x['path'])==p) for p in banks.values()):raise ValueError('Input changed')
    if any(digest(root/p)!=NATIVE_INIT for p in ('bin/initialdata/sound/Init.bnk','r4data/soundbanks/Pc/Init.bnk')):raise ValueError('Bootstrap Init changed')
    result={'passed':True,'cooked':first,'split':second,'diagnostics':diagnostics,'archive':str(archive),
        'archive_sha256':digest(archive),'zip_entry':entry,'retail_validated':False,'deployed':False}
    (root/'bundle-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--redkit',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--retry-recording',action='store_true')
    a=p.parse_args();stage(a.redkit,a.spec,a.root,a.retry_recording)
