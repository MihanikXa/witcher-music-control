"""Read-only complete-source/native-bank/stream proof for a pristine region.

Never opens project licence fields or changes game/cache/authoring inputs.
Generated Init is compared with an accepted complete-context baseline, not shipped.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
from music_region_inventory import REGIONS
from white_orchard_prepare import build_path, digest
from white_orchard_compare import read_bank, difference
from white_orchard_state_bank_audit import header
from white_orchard_build_gate import plugins
from white_orchard_candidate_package import diagnostics


def cache_index(stream):
    stream.seek(0, 2)
    length=stream.tell();stream.seek(0)
    data=stream.read(64)
    if len(data)!=64 or data[:8]!=b'CS3W\x02\0\0\0':
        raise ValueError('Unsupported native cache')
    count=struct.unpack_from('<I',data,24)[0]
    start=struct.unpack_from('<Q',data,32)[0]
    size=struct.unpack_from('<I',data,40)[0]
    if start<64 or start+size+count*24!=length:
        raise ValueError('Native cache index bounds')
    stream.seek(start);names=stream.read(size);table=stream.read(count*24)
    entries={};intervals=[]
    for i in range(count):
        no,off,n=struct.unpack_from('<QQQ',table,i*24)
        end=names.find(b'\0',no)
        if no>=size or end<no or off<64 or off+n>start:
            raise ValueError('Native cache entry bounds')
        name=names[no:end].decode('ascii')
        if name in entries:
            raise ValueError('Duplicate native cache name')
        entries[name]=(off,n);intervals.append((off,off+n))
    intervals.sort()
    if any(a[1]>b[0] for a,b in zip(intervals,intervals[1:])):
        raise ValueError('Overlapping native cache entries')
    return entries


def verify(source, project, banks, native, cache, accepted, region):
    if region not in REGIONS:
        raise ValueError('Unsupported region')
    inputs=json.loads((project/'input-manifest.json').read_text())
    units={x['relative_path'].replace('\\','/'):x['sha256'] for x in inputs['inputs'] if x['relative_path'].endswith('.wwu')}
    actual={p.relative_to(project).as_posix():p for p in project.rglob('*.wwu')}
    if len(units)!=1508 or set(actual)!=set(units):
        raise ValueError('Incomplete pristine authoring context')
    for rel,sha in units.items():
        if digest(source/rel)!=sha or digest(actual[rel])!=sha:
            raise ValueError('Pristine/installed work unit changed: '+rel)
    for item in inputs['originals']:
        rel=item['relative_path']
        if digest(project/rel)!=item['sha256'] or digest(source/rel)!=item['sha256']:
            raise ValueError('Original source audio changed')
    if (inputs['version'].get('WwiseVersion')!='v2023.1.19' or inputs['version'].get('WwiseBuild')!='8928'
            or inputs['version'].get('SchemaVersion')!='119'):
        raise ValueError('Source version mismatch')
    result=json.loads((banks/'result.json').read_text())
    if (result.get('selected_bank')!=region or result.get('exit_code') not in (0,2)
            or sorted(p.name for p in banks.rglob('*.bnk'))!=sorted(['Init.bnk',region+'.bnk'])):
        raise ValueError('Generation scope/status mismatch')
    warnings=diagnostics(banks)
    if warnings-diagnostics(accepted):
        raise ValueError('Unreviewed baseline generation diagnostic')
    a=read_bank(native/(region+'.bnk'));b=read_bank(banks/(region+'.bnk'))
    delta=difference(a,b)
    if delta['added'] or delta['removed'] or delta['changed'] or set(delta['chunk_changed'])-{'BKHD'}:
        raise ValueError('Pristine regional bank differs from native')
    hn,hg=header(a),header(b,banks/'SoundbanksInfo.xml')
    if hn['project_id']!=39 or hg['project_id']!=17637 or not hg['hash_matches_metadata_guid']:
        raise ValueError('Unexplained BKHD project/hash identity')
    excluded={'project_id','hash_hex','metadata_hash','hash_matches_metadata_guid'}
    if {k:v for k,v in hn.items() if k not in excluded}!={k:v for k,v in hg.items() if k not in excluded}:
        raise ValueError('Unexplained BKHD metadata difference')
    init,reference=read_bank(banks/'Init.bnk'),read_bank(accepted/'Init.bnk')
    if set(init['payload'])!=set(reference['payload']) or any(init['payload'][k]!=reference['payload'][k] for k in init['payload'] if k!='BKHD'):
        raise ValueError('Unexpected generated global definitions')
    if plugins(init['payload']['INIT'])!=plugins(read_bank(native/'Init.bnk')['payload']['INIT']):
        raise ValueError('Plugin registration mismatch')
    tree=ET.parse(banks/'SoundbanksInfo.xml')
    selected=next(n for n in tree.iter('SoundBank') if n.findtext('ShortName')==region)
    media={}
    with cache.open('rb') as stream:
        index=cache_index(stream)
        if region+'.bnk' not in index:
            raise ValueError('Missing installed native regional bank')
        off,n=index[region+'.bnk'];stream.seek(off)
        if hashlib.sha256(stream.read(n)).hexdigest()!=a['sha256']:
            raise ValueError('Installed cache/native reference bank mismatch')
        for item in selected.findall('./Media/File'):
            ident=int(item.get('Id'));name=str(ident)+'.wem'
            if ident in media or name not in index:
                raise ValueError('Missing/duplicate native media')
            off,n=index[name];stream.seek(off);sha=hashlib.sha256(stream.read(n)).hexdigest()
            path=(banks/item.findtext('Path')).resolve()
            if not path.is_relative_to(banks.resolve()) or digest(path)!=sha:
                raise ValueError('Native media payload differs')
            media[ident]=sha
    if not media:
        raise ValueError('No media verified')
    return {'passed':True,'region':region,'work_units':1508,'original_audio_inputs':len(inputs['originals']),
            'native_sha256':a['sha256'],'generated_sha256':b['sha256'],'hirc_count':len(b['records']),
            'all_nonheader_chunks_native_exact':True,'native_streamed_payloads_exact':len(media),
            'native_cache_bank_exact':True,
            'warnings_subset_of_accepted_reference':sum(warnings.values()),'generated_header':hg,
            'generated_globals_exact_accepted':True,'native_plugin_registrations_exact':True,
            'native_init_deployed':False,'runtime_compatibility_claimed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','project','banks','native','cache','accepted','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--region',required=True);a=p.parse_args();out=build_path(a.output)
    if out.exists():raise FileExistsError(out)
    result=verify(a.source,build_path(a.project),a.banks,a.native,a.cache,a.accepted,a.region)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
