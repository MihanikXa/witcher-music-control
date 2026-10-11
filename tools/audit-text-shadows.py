"""Read-only installed UI coverage ledger; no winner guesses or global edits."""
import argparse
import collections
import configparser
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'tools/audit-ui.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def index(path):
    """Same observed POTATO layouts, one size query per bundle."""
    limit=path.stat().st_size
    with path.open('rb') as f:
        header=f.read(32)
        if header[:8]!=b'POTATO70':raise ValueError('Unknown bundle')
        size=struct.unpack_from('<I',header,16)[0];f.seek(0x130)
        stride=0x130 if struct.unpack('<I',f.read(4))[0] else 0x140
        if size%stride:raise ValueError('Invalid index')
        f.seek(32)
        for _ in range(size//stride):
            b=f.read(stride);key=b[:256].split(b'\0')[0].decode().lower().replace('\\','/')
            if stride==0x130:offset,raw,packed,_,codec=struct.unpack_from('<QIIII',b,272)
            else:
                raw,packed,offset=struct.unpack_from('<III',b,276);codec=struct.unpack_from('<I',b,316)[0]
            if offset+packed>limit:raise ValueError('Invalid resource bounds')
            yield dict(resource=key,offset=offset,size=raw,packed=packed,codec=codec)


def effects(node):
    return [dict(f.attrib,color=[dict(c.attrib) for c in f]) for f in node.findall('./surfaceFilterList/item')]


def read_resource(entry, game, folder):
    if 'loose' in entry:return Path(entry['loose']).read_bytes()
    with Path(entry['bundle']).open('rb') as f:
        f.seek(entry['offset']);packed=f.read(entry['packed'])
    if entry['codec']==1:data=zlib.decompress(packed)
    elif entry['codec']==0:data=packed
    elif entry['codec']==5:
        # Existing verified game-local QuickBMS decompressor, private output only.
        quick=game/'WitcherScriptMerger/Tools/QuickBMS'
        folder.mkdir(parents=True,exist_ok=True);filt=folder/'filter.txt'
        filt.write_text(entry['resource'].replace('/','\\'))
        dest=folder/'extracted';dest.mkdir(exist_ok=True)
        cmd=[str(quick/'quickbms.exe'),'-Q','-o','-f',str(filt),str(quick/'witcher3.bms'),entry['bundle'],str(dest)]
        p=subprocess.run(cmd,capture_output=True,timeout=60)
        (folder/'decompress.log').write_bytes(p.stdout+p.stderr)
        if p.returncode:raise ValueError('Verified codec-5 extraction failed')
        data=(dest/entry['resource']).read_bytes()
    else:raise ValueError('Unsupported codec '+str(entry['codec']))
    if len(data)!=entry['size']:raise ValueError('Extracted size differs from bundle index')
    return data


def classify(filters):
    if not filters:return 'no_authored_effect'
    black=[f for f in filters if f.get('type') in ('DROPSHADOWFILTER','GLOWFILTER')
           and any(int(c.get('alpha','255'))>0 and all(c.get(k)=='0' for k in ('red','green','blue')) for c in f['color'])]
    if not black:return 'semantic_or_nonblack_effect_review_preserve'
    if any(float(f.get('strength','0'))>1 or max(float(f.get('blurX','0')),float(f.get('blurY','0')))>=4 for f in black):
        return 'strong_black_ordinary_text_candidate_not_visual_verification'
    return 'subtle_black_effect_review_leave'


def inspect_xml(path):
    root=ET.parse(path).getroot();texts={};placements=[];parents=collections.defaultdict(list)
    def walk(tags,sprite=0):
        active={};frame=0
        for ordinal,n in enumerate(tags):
            kind=n.get('type')
            if kind in ('DefineEditTextTag','DefineTextTag','DefineText2Tag'):
                texts[n.get('characterID')]=dict(n.attrib)
            if kind=='DefineSpriteTag':walk(n.find('subTags'),int(n.get('spriteId')))
            if kind=='ShowFrameTag':frame+=1
            if kind in ('RemoveObjectTag','RemoveObject2Tag'):active.pop(n.get('depth'),None)
            if kind in ('PlaceObjectTag','PlaceObject2Tag','PlaceObject3Tag','PlaceObject4Tag'):
                depth=n.get('depth');previous=active.get(depth,{}) if n.get('placeFlagMove')=='true' else {}
                char=n.get('characterId') if n.get('placeFlagHasCharacter')=='true' or kind=='PlaceObjectTag' else previous.get('character')
                if not char:continue
                local=effects(n) if n.get('placeFlagHasFilterList')=='true' else previous.get('filters',[])
                row=dict(sprite=sprite,ordinal=ordinal,frame=frame,depth=depth,character=char,
                    name=n.get('name',previous.get('name')),filters=local,move=n.get('placeFlagMove')=='true')
                active[depth]=row;placements.append(row);parents[char].append(row)
    walk(root.find('tags'))
    def ancestry(sprite,seen=(),level=0):
        if sprite==0:return [[]]
        if sprite in seen or level>=12:return [[dict(unresolved='cycle_or_depth_limit',sprite=sprite)]]
        linked=parents.get(str(sprite),[])
        if not linked:return [[dict(unresolved='exported_or_runtime_instantiated',sprite=sprite)]]
        result=[]
        for row in linked:
            for chain in ancestry(row['sprite'],seen+(sprite,),level+1):
                result.append([row]+chain)
                if len(result)>=64:return result
        return result
    rows=[]
    for character,text in texts.items():
        matched=[p for p in placements if p['character']==character]
        for p in matched or [None]:
            chains=ancestry(p['sprite']) if p else []
            direct=p['filters'] if p else []
            inherited=[q for chain in chains for q in chain if q.get('filters')]
            all_filters=direct+[f for q in inherited for f in q['filters']]
            rows.append(dict(character=character,text_definition=text,placement=p,ancestor_chains=chains,
                            classification=classify(all_filters),runtime_override_verified=False))
    classes=[dict(n.attrib) for n in root.iter() if n.tag=='item' and n.get('className')]
    return dict(text_definition_count=len(texts),text_placement_count=len(rows),fields=rows,
                symbol_classes=classes,all_placements=placements,
                inheritance_note='Authored timeline depth tracking; exported/runtime instantiation, cycles and >64 ancestry paths remain explicit limitations')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True)
    ap.add_argument('--redkit',type=Path,required=True);ap.add_argument('--ffdec',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mods-settings',type=Path)
    a=ap.parse_args();out=a.out.resolve()
    if ROOT/'build' not in out.parents or out.exists():raise ValueError('Fresh ignored output required')
    out.mkdir();inventory=collections.defaultdict(list)
    for folder in ('content','Mods','DLC'):
        for bundle in sorted((a.game/folder).rglob('*.bundle')):
            for e in index(bundle):
                key=e['resource']
                if '/gui_new/swf/' in key and key.endswith('.redswf'):
                    e.update(bundle=str(bundle.resolve()),owner='vanilla' if folder=='content' else bundle.relative_to(a.game).parts[1])
                    inventory[key].append(e)
        if folder!='content':
            for file in sorted((a.game/folder).rglob('*.redswf')):
                parts=file.relative_to(a.game).parts
                if 'content' in parts:
                    key='/'.join(parts[parts.index('content')+1:]).lower()
                    if '/gui_new/swf/' in key:inventory[key].append(dict(resource=key,loose=str(file.resolve()),owner=parts[1]))
    configured={}
    if a.mods_settings:
        config=configparser.RawConfigParser(strict=False)
        config.read(a.mods_settings,encoding='utf-8-sig')
        configured={s.lower():dict(enabled=config.get(s,'Enabled',fallback='unknown'),
                                 priority=config.get(s,'Priority',fallback='unknown')) for s in config.sections()}
    for owners in inventory.values():
        for e in owners:
            if e['owner']!='vanilla':e['configuration']=configured.get(e['owner'].lower(),dict(enabled='unknown',priority='unknown'))
    movies=[];excluded=[]
    for key,owners in sorted(inventory.items()):
        if re.search(r'/fonts_(?!en\.)',key):excluded.append(key);continue
        mods=[e for e in owners if e['owner']!='vanilla' and e['configuration']['enabled']!='0']
        selected=mods if mods else [e for e in owners if e['owner']=='vanilla']
        base_seen={}
        for e in selected:
            row=dict(resource_key=key,owners=owners,selected_owner=e['owner'],
                selection_confidence='multiple_deployed_mod_owners_unresolved' if len(mods)>1 else
                    ('sole_deployed_mod_owner_priority_not_runtime_traced' if mods else
                     'multiple_base_bundle_versions_unresolved' if len(owners)>1 else 'vanilla_no_deployed_mod_owner'),
                runtime_use_verified=False,status='audited_static_deferred')
            try:
                folder=out/'movies'/str(len(movies));folder.mkdir(parents=True,exist_ok=True)
                data=read_resource(e,a.game,folder)
                digest=audit.sha(data)
                if e['owner']=='vanilla':
                    proof=dict(bundle=e['bundle'],sha256=digest)
                    if digest in base_seen:
                        existing=base_seen[digest];existing['base_version_checks'].append(proof)
                        if len(base_seen)==1:existing['selection_confidence']='multiple_base_copies_byte_identical'
                        continue
                    row['base_version_checks']=[proof];base_seen[digest]=row
                    if len(base_seen)>1:
                        for existing in base_seen.values():existing['selection_confidence']='multiple_base_bundle_versions_unresolved'
                offset,_,_=audit.swf_tags(data)
                (folder/'resource.redswf').write_bytes(data);(folder/'movie.gfx').write_bytes(data[offset:])
                row['input_sha256']=digest
                p=subprocess.run(['java','-jar',str(a.ffdec.resolve()),'-swf2xml',str(folder/'movie.gfx'),str(folder/'movie.xml')],capture_output=True,timeout=60)
                (folder/'export.log').write_bytes(p.stdout+p.stderr)
                if p.returncode:raise ValueError('JPEXS export failed')
                row.update(inspect_xml(folder/'movie.xml'));row['local_xml']=str(folder/'movie.xml')
            except (ValueError,subprocess.TimeoutExpired) as ex:row.update(status='blocked',error=str(ex))
            movies.append(row);(out/'coverage.json').write_text(json.dumps(dict(movies=movies,excluded_nonenglish_fonts=excluded),indent=2))
            print(f'{len(movies)} {key} {row["status"]}',flush=True)
    runtime=[];pattern=re.compile(r'\.filters\s*=|new\s+(?:GlowFilter|DropShadowFilter)|setTextFormat\s*\(')
    for base in (a.redkit/'r4data/gameplay/gui_new/actionscript',a.game/'content/content0/scripts',a.game/'Mods'):
        for file in sorted(base.rglob('*')):
            if file.suffix not in ('.as','.ws'):continue
            text=file.read_text(errors='replace');hits=[]
            for i,line in enumerate(text.splitlines(),1):
                if pattern.search(line):hits.append(dict(line=i,operation=pattern.search(line).group()))
            if hits:runtime.append(dict(path=str(file.resolve()),sha256=audit.sha(file.read_bytes()),hits=hits))
    report=dict(movies=movies,excluded_nonenglish_fonts=excluded,runtime_style_setters=runtime,
        mods_settings_sha256=audit.sha(a.mods_settings.read_bytes()) if a.mods_settings else None,
        live_files_modified=False,computer_use=False,
        scope='All installed base/DLC UI movie keys and deployed mod owners; catalogue availability is not proof of runtime visibility',
        dynamic_audit='Native current REDkit and installed WitcherScript scan; not runtime frame tracing or exhaustive embedded ABC analysis')
    (out/'coverage.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(movies=len(movies),blocked=sum(m['status']=='blocked' for m in movies))))


if __name__=='__main__':main()
