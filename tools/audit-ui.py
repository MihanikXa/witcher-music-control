"""Read-only bundle/SWF audit; proprietary extraction goes only to ignored build/.

Bundle layouts are validated against installed POTATO70 indexes. This is an
inspector, never a resource writer/cooker. Unknown formats fail closed.
"""
from pathlib import Path
import argparse, collections, hashlib, json, re, struct, subprocess, zlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def entries(path):
    with path.open('rb') as f:
        h = f.read(32)
        if h[:8] != b'POTATO70':
            raise ValueError(f'Unknown bundle: {path}')
        table = struct.unpack_from('<I', h, 16)[0]
        f.seek(0x130)
        stride = 0x130 if struct.unpack('<I', f.read(4))[0] else 0x140
        if table % stride:
            raise ValueError('Invalid index length')
        f.seek(32)
        for _ in range(table // stride):
            b = f.read(stride)
            name = b[:256].split(b'\0')[0].decode().lower().replace('\\', '/')
            if stride == 0x130:
                offset, size, packed, _, codec = struct.unpack_from('<QIIII', b, 272)
            else:
                size, packed, offset = struct.unpack_from('<III', b, 276)
                codec = struct.unpack_from('<I', b, 316)[0]
            if offset + packed > path.stat().st_size:
                raise ValueError('Invalid payload bounds')
            yield dict(resource=name, offset=offset, size=size, packed=packed, codec=codec)

def swf_tags(data):
    offsets = [m.start() for m in re.finditer(b'[FC]WS|[CG]FX', data)]
    for offset in offsets:
        raw = data[offset:]
        try:
            length = struct.unpack_from('<I', raw, 4)[0]
            body = zlib.decompress(raw[8:]) if raw[:1] == b'C' else raw[8:length]
            # GFx exporter length can describe the pre-export stream; validate
            # actual tag boundaries instead of assuming standard SWF lengths.
            if raw[:3] in (b'CWS', b'FWS') and len(body) != length - 8:
                continue
            rect_size = (5 + 4 * (body[0] >> 3) + 7) // 8
            pos = rect_size + 4
            tags = []
            while pos < len(body):
                header = struct.unpack_from('<H', body, pos)[0]; pos += 2
                code, size = header >> 6, header & 63
                if size == 63:
                    size = struct.unpack_from('<I', body, pos)[0]; pos += 4
                payload = body[pos:pos+size]
                if len(payload) != size:
                    raise ValueError('Truncated tag')
                tags.append((code, payload)); pos += size
                if code == 0:
                    break
            if not tags or tags[-1][0] != 0:
                raise ValueError('Missing End tag')
            return offset, raw[:3].decode(), tags
        except (ValueError, zlib.error, struct.error, IndexError):
            continue
    raise ValueError('No validated SWF/GFx payload')

def font_info(code, b):
    if code not in (48, 75):
        return None
    fid, flags, language, n = struct.unpack_from('<HBBB', b)
    name = b[5:5+n].decode('utf-8', errors='replace').rstrip('\0')
    count = struct.unpack_from('<H', b, 5+n)[0]
    if count == 0:
        return dict(id=fid, name=name, flags=flags, language=language,
                    glyphs=0, latin=0, cyrillic=0, codes=[], payload_sha256=sha(b))
    base = 7+n; wide = bool(flags & 8); unit = 4 if wide else 2
    fmt = '<I' if wide else '<H'
    codeoff = struct.unpack_from(fmt, b, base + count*unit)[0]
    codesize = 2 if flags & 4 else 1
    start = base + codeoff
    codes = [int.from_bytes(b[start+i*codesize:start+(i+1)*codesize], 'little') for i in range(count)]
    return dict(id=fid, name=name, flags=flags, language=language, glyphs=count,
                latin=sum(0x20 <= c <= 0x24f for c in codes),
                cyrillic=sum(0x400 <= c <= 0x52f for c in codes),
                codes=codes, payload_sha256=sha(b))

def inspect(path):
    data = path.read_bytes(); offset, signature, tags = swf_tags(data)
    fonts = [font_info(c,b) for c,b in tags if c in (48,75)]
    strings = sorted(set(s.decode('utf-8', errors='replace') for c,b in tags
                         for s in re.findall(rb'[\x20-\x7e]{4,}', b)))
    return dict(path=str(path), sha256=sha(data), payload_offset=offset,
                signature=signature, tags=dict(collections.Counter(c for c,b in tags)),
                tag_hashes=[dict(code=c, size=len(b), sha256=sha(b)) for c,b in tags],
                fonts=fonts, strings=strings)

def surface_fields(xml):
    root=ET.parse(xml).getroot()
    texts={x.get('characterID'):x for x in root.iter() if x.get('type')=='DefineEditTextTag'}
    fields=[]
    for x in root.iter():
        if not x.get('name') or x.get('characterId') not in texts:
            continue
        t=texts[x.get('characterId')];filters=x.find('surfaceFilterList')
        fields.append(dict(name=x.get('name'),character=x.get('characterId'),
                           font=t.get('fontClass'),fontHeight=t.get('fontHeight'),
                           align=t.get('align'),leading=t.get('leading'),
                           filters=[dict(f.attrib,color=[c.attrib for c in f]) for f in filters] if filters is not None else []))
    return dict(movie=xml.stem,text_definitions=len(texts),named_fields=fields)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--redkit', type=Path, required=True)
    p.add_argument('--ffdec', type=Path, help='Optional local ffdec.jar; exports read-only XML and selected scripts')
    a=p.parse_args(); out=ROOT/'build/audit'; out.mkdir(parents=True,exist_ok=True)
    refs=[]; files=[]; installed=[]
    quick=a.game/'WitcherScriptMerger/Tools/QuickBMS'
    for path in sorted((ROOT/'reference').rglob('*')):
        if path.is_file():
            files.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size, sha256=sha(path.read_bytes())))
        if path.suffix == '.bundle':
            es=list(entries(path)); dest=out/'references'/path.parent.parent.name
            dest.mkdir(parents=True,exist_ok=True)
            result=subprocess.run([str(quick/'quickbms.exe'), '-Q', '-o', str(quick/'witcher3.bms'), str(path), str(dest)],capture_output=True)
            if result.returncode:
                raise RuntimeError(result.stdout.decode(errors='replace'))
            for e in es:
                f=dest/e['resource']
                e.update(bundle=str(path.relative_to(ROOT)), extracted=str(f), sha256=sha(f.read_bytes()))
                if f.suffix=='.redswf':
                    e['swf']=inspect(f)
            refs.extend(es)
    for kind in ('Mods','DLC'):
        for path in sorted((a.game/kind).rglob('*.bundle')):
            for e in entries(path):
                e.update(bundle=str(path),owner=str(path.relative_to(a.game).parts[1]))
                installed.append(e)
        for path in sorted((a.game/kind).rglob('*.redswf')):
            parts=path.relative_to(a.game).parts
            if 'content' in parts:
                resource='/'.join(parts[parts.index('content')+1:]).lower()
                installed.append(dict(resource=resource,loose=str(path),owner=parts[1]))
    (out/'reference-files.json').write_text(json.dumps(files,indent=2))
    (out/'references.json').write_text(json.dumps(refs,indent=2))
    (out/'installed-bundle-index.json').write_text(json.dumps(installed,indent=2))
    wanted=('enemyfocus','subtitles','interactions','hud_quests','hud_dialog',
            'journalupdate','hud_oneliners','hud_lootfeed','panel_inventory.redswf',
            'panel_ingamemenu','glossary_bestiary','glossary_encyclopedia','fonts_en','fonts_ru','fonts_ua')
    baselines=[]
    for name in ('r4gui.bundle','startup.bundle'):
        bundle=a.game/'content/content0/bundles'/name
        selected=[e for e in entries(bundle) if e['resource'].endswith('.redswf') and any(w in e['resource'] for w in wanted)]
        filt=out/('filter-'+name+'.txt'); filt.write_text('\n'.join(e['resource'].replace('/','\\') for e in selected))
        dest=out/'vanilla';dest.mkdir(exist_ok=True)
        result=subprocess.run([str(quick/'quickbms.exe'),'-Q','-o','-f',str(filt),str(quick/'witcher3.bms'),str(bundle),str(dest)],capture_output=True)
        if result.returncode:
            raise RuntimeError('Baseline extraction failed: '+result.stdout.decode(errors='replace'))
        for e in selected:
            f=dest/e['resource']; info=inspect(f)
            source=a.redkit/'r4data'/e['resource']
            baselines.append(dict(resource=e['resource'],bundle=str(bundle),swf=info,
                                  redkit_sha256=sha(source.read_bytes()) if source.exists() else None))
    (out/'baselines.json').write_text(json.dumps(baselines,indent=2))
    surfaces=[]
    for group in ('references','vanilla'):
        for path in (out/group).rglob('*.redswf'):
            data=path.read_bytes();offset,_,_=swf_tags(data)
            gfx=(out/'gfx'/group/path.relative_to(out/group)).with_suffix('.gfx')
            gfx.parent.mkdir(parents=True,exist_ok=True);gfx.write_bytes(data[offset:])
            if a.ffdec and not path.name.startswith('fonts_'):
                xml=(out/'xml'/group/path.relative_to(out/group)).with_suffix('.xml')
                xml.parent.mkdir(parents=True,exist_ok=True)
                subprocess.run(['java','-jar',str(a.ffdec),'-swf2xml',str(gfx),str(xml)],check=True)
                if group=='vanilla':surfaces.append(surface_fields(xml))
                if any(x in path.name for x in ('enemyfocus','glossary')):
                    dest=out/'decompiled'/group/path.stem
                    subprocess.run(['java','-jar',str(a.ffdec),'-selectclass',
                                    'red.game.witcher3.menus.glossary.*,red.game.witcher3.controls.W3ScrollingList,red.game.witcher3.hud.modules.HudModuleEnemyFocus',
                                    '-export','script',str(dest),str(gfx)],check=True,capture_output=True)
    if a.ffdec:(out/'surface-facts.json').write_text(json.dumps(surfaces,indent=2))
    print(json.dumps([dict(bundle=e['bundle'],resource=e['resource'],bytes=e['size'],codec=e['codec'],fonts=[{k:v for k,v in f.items() if k!='codes'} for f in e.get('swf',{}).get('fonts',[])],collisions=[x.get('owner',x.get('loose')) for x in installed if x['resource']==e['resource']]) for e in refs],indent=2))

if __name__=='__main__':
    main()
