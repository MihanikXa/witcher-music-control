"""Private I&I 0.8 HUD batch; exact inputs, native gates, no deployment.

Author sources/assets stay in ignored directories. --reuse/--exclude creates a
resource rollback variant from verified cooked inputs, without recooking or
regenerating working merges. Requires the accepted bars-v1 mod separately.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import configparser
import csv
import io
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import zlib
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/(name+'.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


bars = load('build-ink-hud-bars')
patcher = load('patch-ink-hud-movies')
contracts = load('audit-hud-contracts')
inventory = load('audit-ink-and-iron')
audit, font, fallback = bars.audit, bars.font, bars.fallback
REF = ROOT/'reference/ink-and-iron-0.8'
HUD = REF/'mods/modInkAndIronHUD/content'
MOD = 'modInkIronHUDBatchTest'
ALIAS_MOD = 'modInkIronHUDAliasesTest'
PREFIX = 'gameplay/gui_new/swf/hud/'
NATIVE = dict(bossfocus='BossFocus', buffs='Buffs', companion='Companion',
    controlsfeedback='ControlsFeedback', crosshair='Crosshair', damageditems='DamagedItems',
    enemyfocus='EnemyFocus', horsepanicbar='HorsePanicBar', horsestaminabar='HorseStaminaBar',
    interactions='Interactions', iteminfo='ItemInfo', journalupdate='JournalUpdate',
    minimap2='Minimap2', oxygenbar='OxygenBar', quests='Quests', radialmenu='RadialMenu',
    timelapse='TimeLapse', dialog='Dialog')
AUTHOR_SCRIPTS = dict(inkIronGear={'damageditems'}, inkIronHorse={'horsepanicbar','horsestaminabar'},
    inkIronHudScale={'buffs','timelapse'}, inkIronMinimapClock={'minimap2'},
    inkIronNpcPlate={'enemyfocus','interactions','iteminfo'}, inkIronQuest={'journalupdate'},
    inkIronRadialSigns={'radialmenu'})
HUD_OPTIONS = {'iiShowQuickSlotKeys','iiGoldLockRing','iiGearStyle','iiQuestColour',
               'iiQuestXp','iiShowMinimapClock','iiColoredSigns'}
ACCEPTED_BARS_ZIP = ROOT/'deploy/ink-hud-bars-private-v1/Ink-Iron-Adaptive-Bars-v1-private-test.zip'
ACCEPTED_BARS_SHA = '4e138f392d24c7475a7c49249214d1aaa6f3439f650a89a5ff17c4b50170db67'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def settings_text(path):
    data = path.read_bytes()
    if data.startswith((b'\xff\xfe',b'\xfe\xff')):
        return data.decode('utf-16')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        # Vortex may write its VK labels in the current Windows ANSI codepage.
        # We only interpret ASCII Enabled/Priority and retain raw hash pins.
        return data.decode('mbcs')


def selection(exclude):
    unknown = set(exclude)-set(NATIVE)
    if unknown:
        raise ValueError('Unknown components: '+str(unknown))
    exclude = set(exclude)
    # Name|Role protocol and interaction positioning are one native-script unit.
    if exclude & {'enemyfocus','interactions'}:
        exclude |= {'enemyfocus','interactions'}
    # Shared horse overlay is also an atomic pair.
    if exclude & {'horsepanicbar','horsestaminabar'}:
        exclude |= {'horsepanicbar','horsestaminabar'}
    selected = set(NATIVE)-exclude
    if not selected:
        raise ValueError('For full rollback disable the batch; no empty native package')
    return selected


def selected_scripts(selected):
    result = []
    for stem, components in AUTHOR_SCRIPTS.items():
        if stem == 'inkIronNpcPlate':
            if {'enemyfocus','interactions'} <= selected:
                result.append(stem)
        elif components & selected:
            result.append(stem)
    return result


def read_bundle(bundle, e, game, out):
    if e['codec'] in (0,1):
        with bundle.open('rb') as f:
            f.seek(e['offset'])
            data = f.read(e['packed'])
        if e['codec']==1:
            data = zlib.decompress(data)
    elif e['codec']==5:
        dest = out/'owner-extracts'/audit.sha(str(bundle).encode())[:16]
        if not dest.exists():
            dest.mkdir(parents=True)
            quick = game/'WitcherScriptMerger/Tools/QuickBMS'
            p = subprocess.run([str(quick/'quickbms.exe'),'-Q','-o',str(quick/'witcher3.bms'),
                                str(bundle),str(dest)],capture_output=True,timeout=60)
            if p.returncode:
                raise ValueError('Owner extraction failed: '+str(bundle))
        data = (dest/e['resource']).read_bytes()
    else:
        raise ValueError('Unknown current-owner codec')
    if len(data)!=e['size']:
        raise ValueError('Owner resource size differs')
    return data


def owners(game, cfg, keys, out):
    result = {k:[] for k in keys}
    for bundle in (game/'Mods').rglob('*.bundle'):
        owner = bundle.relative_to(game/'Mods').parts[0]
        for e in audit.entries(bundle):
            if e['resource'] in result:
                raw = read_bundle(bundle,e,game,out)
                result[e['resource']].append(dict(owner=owner,container=str(bundle.resolve()),
                    sha256=audit.sha(raw),enabled=cfg[owner].get('Enabled') if owner in cfg else None,
                    priority=cfg[owner].get('Priority') if owner in cfg else None))
    for p in (game/'Mods').rglob('*'):
        if not p.is_file() or p.suffix not in ('.redswf','.xml'):
            continue
        parts = p.relative_to(game/'Mods').parts
        if 'content' not in parts:
            continue
        key = '/'.join(parts[parts.index('content')+1:]).lower()
        if key in result:
            owner = parts[0]
            result[key].append(dict(owner=owner,container=str(p.resolve()),sha256=fallback.sha(p),
                enabled=cfg[owner].get('Enabled') if owner in cfg else None,
                priority=cfg[owner].get('Priority') if owner in cfg else None))
    return result


@contextmanager
def mount(runner, out, files):
    font.private_path(runner)
    font.private_path(out)
    if runner in out.parents or out in runner.parents:
        raise ValueError('Runner/output must be separate directories')
    workspace, backup = runner/'bin/workspace', runner/'bin/workspace-hud-backup'
    if backup.exists() or workspace.is_symlink() or workspace.is_junction():
        raise ValueError('Private workspace busy or linked')
    if workspace.exists() and any(p.is_symlink() or p.is_junction() for p in workspace.rglob('*')):
        raise ValueError('Linked workspace path')
    before = font.workspace_inventory(workspace)
    existed = workspace.exists()
    index = 0
    while (out/('staged-workspace-'+str(index))).exists():
        index += 1
    preserved = out/('staged-workspace-'+str(index))
    if existed:
        workspace.rename(backup)
    try:
        workspace.mkdir(parents=True)
        for key, data in files.items():
            if '..' in Path(key).parts or ':' in key or key.startswith(('/','\\')):
                raise ValueError('Unsafe key')
            dest = workspace/key
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
        yield workspace
    finally:
        if workspace.exists():
            workspace.rename(preserved)
        if existed and backup.exists():
            backup.rename(workspace)
        if font.workspace_inventory(workspace)!=before or workspace.exists()!=existed:
            raise ValueError('Private runner workspace was not restored')


def compiler(assembly, game, cfg, work, author_scripts):
    runtime = ROOT/'build/native-npc-reproduce/runtime'
    if fallback.sha(runtime/'wcc_lite.exe')!=font.COMPILER_SHA:
        raise ValueError('Script compiler changed')
    inputs, required = [], []
    for group in ('base','patch'):
        for p in (assembly/group).rglob('*.ws'):
            q = work/group/p.relative_to(assembly/group)
            q.parent.mkdir(parents=True,exist_ok=True)
            q.write_text(fallback.text(p),encoding='utf-8',newline='\n')
            inputs.append(dict(path=str(p.resolve()),sha256=fallback.sha(p)))
    hashes = {audit.sha(fallback.text(p).encode()) for p in work.rglob('*.ws')}
    for owner, relative in [('mod0000_MergedFiles',''),('modSeamlessAdaptiveHUD','local/SeamlessAdaptiveHUD'),
                            ('modFriendlyHUD','game/gui/hud/modules'),('modFriendlyHUD','fhudscripts')]:
        for p in (game/'Mods'/owner/'content/scripts'/relative).rglob('*.ws'):
            if owner=='modFriendlyHUD' and p.name=='hudModuleRadialMenu.ws':
                continue
            if audit.sha(fallback.text(p).encode()) not in hashes:
                raise ValueError('Current deployed HUD/merge source missing from assembly: '+str(p))
            required.append(dict(path=str(p.resolve()),sha256=fallback.sha(p)))
    for owner, name in [('modQuietEditorialNPCColorsV4','quietEditorialNameColorsV4'),
                        ('modInkIronAdaptiveBarsTest','inkIronBarsBridge')]:
        p = game/'Mods'/owner/'content/scripts/local'/(name+'.ws')
        if not p.exists():
            if owner!='modInkIronAdaptiveBarsTest' or fallback.sha(ACCEPTED_BARS_ZIP)!=ACCEPTED_BARS_SHA:
                raise ValueError('Accepted deployed/archive source missing: '+str(p))
            with zipfile.ZipFile(ACCEPTED_BARS_ZIP) as z:
                text = z.read('Mods/'+owner+'/content/scripts/local/'+name+'.ws').decode('utf-8-sig')
            if text!=fallback.text(ROOT/'src/hud/inkIronBarsBridge.ws'):
                raise ValueError('Accepted bars source differs from original adapter')
            required.append(dict(path=str(ACCEPTED_BARS_ZIP),sha256=ACCEPTED_BARS_SHA,
                                 role='Accepted runtime-tested dependency, currently not deployed'))
        else:
            text = fallback.text(p)
            required.append(dict(path=str(p.resolve()),sha256=fallback.sha(p)))
        if audit.sha(text.encode()) not in hashes:
            q = work/'patch/local'/(name+'.ws')
            q.parent.mkdir(parents=True,exist_ok=True)
            q.write_text(text,encoding='utf-8',newline='\n')
    bridge = work/'patch/local/inkIronHUDStateBridge.ws'
    bridge.parent.mkdir(parents=True,exist_ok=True)
    candidate = fallback.text(ROOT/'src/hud/inkIronHUDStateBridge.ws')
    results = []
    for label in ('baseline','noop','candidate'):
        if label!='baseline':
            for stem in author_scripts:
                p = HUD/'scripts/local'/(stem+'.ws')
                (work/'patch/local'/p.name).write_text(fallback.text(p),encoding='utf-8',newline='\n')
            bridge.write_text(candidate if label=='candidate' else
                '@wrapMethod(SahCore)\nfunction Tick(dt : float) { wrappedMethod(dt); }\n',encoding='utf-8')
        output = work/label
        output.mkdir()
        cmd = [str(runtime/'wcc_lite.exe'),'compilescripts',str(work/'base'),
               '-patch='+str(work/'patch'),'-out='+str(output)]
        p = subprocess.run(cmd,cwd=runtime,capture_output=True,timeout=90)
        log = (runtime.parent/'wcc.log').read_text(errors='replace')
        (work/(label+'.full.log')).write_text(log)
        (work/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
        errors = [s for s in log.splitlines() if '[Error][Script]' in s or '[Error][WCC]' in s]
        blob = output/'blob.rsblob'
        result = dict(label=label,command=cmd,exit_code=p.returncode,errors=errors,
            assertions=dict(bars.diagnostics.diagnostic_counter(log,'[Error][Assert]')),
            warnings=dict(bars.diagnostics.diagnostic_counter(log,'[Warning]')),
            success=p.returncode==0 and not errors and blob.exists() and blob.stat().st_size>0
                and 'Success! Patch scripts blob saved' in log,
            blob_sha256=fallback.sha(blob) if blob.exists() else None)
        results.append(result)
        write_json(work/'commands.json',results)
        print('Script',label,result['success'],flush=True)
        if not result['success']:
            raise ValueError('Script compile failed: '+label)
    if results[1]['warnings']!=results[2]['warnings'] or results[1]['assertions']!=results[2]['assertions']:
        raise ValueError('Bridge regressed matched declaration control diagnostics')
    for r in results[1:]:
        r['assertions_added_vs_baseline'] = dict(Counter(r['assertions'])-Counter(results[0]['assertions']))
        r['warnings_added_vs_baseline'] = dict(Counter(r['warnings'])-Counter(results[0]['warnings']))
    if any(fallback.sha(Path(p['path']))!=p['sha256'] for p in inputs+required):
        raise ValueError('Script input changed')
    opaque = [m for m in cfg.sections() if cfg[m].get('Enabled')=='1'
              and (game/'Mods'/m/'content/info.json').exists()
              and json.loads((game/'Mods'/m/'content/info.json').read_text(encoding='utf-8-sig')).get('useLooseScripts') is False]
    result = dict(results=results,assembly_inputs=inputs,current_required_inputs=required,
                  opaque_mods_not_recompiled=opaque,scope='Source-assembly regression; retail multi-blob test pending')
    write_json(work/'receipt.json',result)
    return result


def export(gfx, dest):
    cmd = ['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-export','script',str(dest),str(gfx)]
    p = subprocess.run(cmd,capture_output=True,timeout=60)
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'export.log').write_bytes(p.stdout+p.stderr)
    if p.returncode or not list(dest.rglob('*.as')):
        raise ValueError('Decompiler export failed')


def public_chain(directory, classname):
    result = {}
    seen = set()
    while classname and classname not in seen:
        seen.add(classname)
        paths = list(directory.rglob(classname+'.as'))
        if len(paths)!=1:
            if classname in ('MovieClip','UIComponent','Sprite','EventDispatcher'):
                break
            raise ValueError('Ambiguous/missing root inheritance: '+classname)
        text = paths[0].read_text(encoding='utf-8-sig')
        # Derived members take precedence over inherited methods.
        for k,v in contracts.signatures(text).items():
            result.setdefault(k,v)
        parent = re.search(r'public (?:dynamic |final )?class\s+\w+\s+extends\s+(\w+)',text)
        classname = parent[1] if parent else None
    return result


def native_input(name, game, assembly):
    relative = Path('game/gui/hud/modules')/('hudModule'+NATIVE[name]+'.ws')
    for folder in (game/'Mods/mod0000_MergedFiles/content/scripts',game/'Mods/modFriendlyHUD/content/scripts',
                   assembly/'patch',assembly/'base'):
        if (folder/relative).exists():
            return folder/relative
    raise ValueError('Native HUD source absent: '+name)


def atlas_contract(data):
    """Validate observed DXT5 mips, handle array, image linkage and rectangles."""
    chunks = font.native.chunks(data)
    textures = {}
    infos = []
    for chunk in chunks[1:]:
        prop = chunk['properties']
        resident,count,width,height,pitch,size,alignment = struct.unpack_from('<7I',chunk['tail'])
        if chunk['class_name']!='CSwfTexture' or prop['compression']['value']!='TCM_DXTAlpha' or resident!=0 or count!=1:
            raise ValueError('Unsupported embedded texture contract')
        if size!=len(chunk['tail'])-28 or size!=((width+3)//4)*((height+3)//4)*16 or width!=prop['width']['value'] or height!=prop['height']['value']:
            raise ValueError('Embedded mip dimensions/length differ')
        name = prop['linkageName']['value']
        if name in textures:
            raise ValueError('Duplicate embedded texture linkage')
        textures[name] = (width,height)
        infos.append(dict(linkage=name,width=width,height=height,bytes=size,
                          compressed_pixels_sha256=audit.sha(chunk['tail'][28:])))
    handles = bytes.fromhex(chunks[0]['properties']['textures']['value'])
    expected = struct.pack('<I',len(textures))+b''.join(struct.pack('<I',i) for i in range(2,len(textures)+2))
    if handles!=expected:
        raise ValueError('Embedded atlas handle array differs')
    tags = audit.swf_tags(data)[2]
    images = {}
    for code,payload in tags:
        if code==1009:
            ident = struct.unpack_from('<H',payload)[0]
            pos = 11+payload[10]
            length = payload[pos]
            name = payload[pos+1:pos+1+length].decode('ascii')
            if name not in textures or ident in images:
                raise ValueError('Missing/duplicate external-image atlas linkage')
            width,height = struct.unpack_from('<HH',payload,6)
            # A standalone image may retain logical height 46 while its native
            # BC3 texture is padded to 48. Accept only this block alignment.
            if (width,height)!=textures[name] and (((width+3)//4)*4,((height+3)//4)*4)!=textures[name]:
                raise ValueError('GFx atlas dimensions differ')
            images[ident] = name
    rectangles = 0
    for code,payload in tags:
        if code==1008:
            character,image,x1,y1,x2,y2 = struct.unpack('<6H',payload)
            if image not in images:
                raise ValueError('Unresolved atlas image ID')
            width,height = textures[images[image]]
            if not(0<=x1<x2<=width and 0<=y1<y2<=height):
                raise ValueError('Image rectangle outside atlas')
            rectangles += 1
    return dict(textures=infos,image_links=len(images),rectangles=rectangles)


def class_contracts(before, after):
    """Retain declared methods/accessors in every class, including GTween."""
    pattern = (r'\b(public|protected|private|internal)\s+(?:override\s+|final\s+|static\s+)*'
               r'function\s+(?:(get|set)\s+)?(\w+)\s*\(([^)]*)\)\s*(?::\s*([\w.*<>]+))?')
    count = 0
    for path in before.rglob('*.as'):
        dest = after/path.relative_to(before)
        if not dest.exists():
            raise ValueError('Original class source missing after compilation')
        def declarations(p):
            return {(scope,accessor,name): (re.sub(r'\s+','',params),result)
                    for scope,accessor,name,params,result in re.findall(pattern,p.read_text(encoding='utf-8-sig'))}
        a,b = declarations(path),declarations(dest)
        if any(b.get(key)!=sig for key,sig in a.items()):
            raise ValueError('Original class method/accessor changed: '+str(path.relative_to(before)))
        count += len(a)
    return dict(original_declarations_retained=count)


def movie_contract(name, source, candidate, before, after, native):
    old_tags, new_tags = audit.swf_tags(source)[2], audit.swf_tags(candidate)[2]
    old_symbols, new_symbols = contracts.symbols(old_tags), contracts.symbols(new_tags)
    if old_symbols!=new_symbols:
        raise ValueError('SymbolClass contract changed: '+name)
    root = next(k.split('.')[-1] for k,v in old_symbols.items() if v==0)
    original = public_chain(before,root)
    modified = public_chain(after,root)
    if any(modified.get(k)!=v for k,v in original.items()):
        raise ValueError('Existing public signature changed: '+name)
    text = fallback.text(native)
    bindings = sorted(set(re.findall(r'GetMemberFlashFunction\(\s*"([^\"]+)"',text)))
    missing = sorted(set(bindings)-set(modified))
    if missing:
        raise ValueError('Missing native function exports for '+name+': '+str(missing))
    # Compare listener calls/controller dispatch sites across original classes.
    # Recompilation may normalize formatting; whitespace is immaterial here.
    listener = r'[^\n]*(?:addEventListener|removeEventListener|registerDataCallback|handleInput|dispatchEvent)[^\n]*'
    old_calls, new_calls = {}, {}
    for directory, target in ((before,old_calls),(after,new_calls)):
        for p in directory.rglob('*.as'):
            calls = [re.sub(r'\s+','',s) for s in re.findall(listener,p.read_text(encoding='utf-8-sig'))]
            if calls:
                target[p.relative_to(directory).as_posix()] = sorted(calls)
    if old_calls!=new_calls:
        raise ValueError('Listener/controller source sites changed: '+name)
    a, b = font.native.chunks(source),font.native.chunks(candidate)
    if not all(c['crc_valid'] for c in a+b) or [c['properties'] for c in a]!=[c['properties'] for c in b]:
        raise ValueError('Chunk/property contract differs')
    if [c['tail'] for c in a[1:]]!=[c['tail'] for c in b[1:]]:
        raise ValueError('Embedded atlas bytes changed')
    def imports(tags):
        return [p.split(b'\0',1)[0].decode(errors='replace') for c,p in tags if c in (57,71)]
    if imports(old_tags)!=imports(new_tags):
        raise ValueError('Font library import changed')
    # Every original non-ABC tag survives byte-for-byte except the two intended
    # interaction field/filter edits; utility font is the only additional tag.
    old_non = [(c,p) for c,p in old_tags if c!=82]
    new_non = [(c,p) for c,p in new_tags if c!=82 and not(c==75 and struct.unpack_from('<H',p)[0]==60000)]
    delta = [(i,c) for i,((c,p),(nc,np)) in enumerate(zip(old_non,new_non)) if (c,p)!=(nc,np)]
    if len(old_non)!=len(new_non) or (name!='interactions' and delta) or (name=='interactions' and [c for i,c in delta]!=[37,39]):
        raise ValueError('Unexpected non-ABC tag edits: '+name+' '+str(delta))
    return dict(resource_key=PREFIX+'hud_'+name+'.redswf',input_sha256=audit.sha(source),
        candidate_sha256=audit.sha(candidate),symbols=old_symbols,imports=imports(new_tags),
        original_public_signatures=original,added_public_signatures={k:v for k,v in modified.items() if k not in original},
        native_source=str(native.resolve()),native_source_sha256=fallback.sha(native),native_bindings=bindings,
        missing_native_bindings=missing,listener_controller_sites_unchanged=True,
        embedded_atlases_unchanged=True,properties_unchanged=True,chunk_crcs_valid=True,
        original_abc_sha256=[audit.sha(p) for c,p in old_tags if c==82],
        candidate_abc_sha256=[audit.sha(p) for c,p in new_tags if c==82],non_abc_changed_tags=delta,
        atlas=atlas_contract(candidate),all_classes=class_contracts(before,after))


def official(runner, out, label, args, commands):
    exe = runner/'bin/x64_RedKit/wcc_lite.exe'
    if fallback.sha(exe)!=font.COMPILER_SHA:
        raise ValueError('Resource compiler changed')
    cmd = [str(exe),*args]
    try:
        p = subprocess.run(cmd,cwd=exe.parent,capture_output=True,timeout=240)
    except subprocess.TimeoutExpired as e:
        (out/(label+'.stdout.log')).write_bytes((e.stdout or b'')+(e.stderr or b''))
        shutil.copy2(runner/'bin/wcc.log',out/(label+'.full.log'))
        raise
    log = (runner/'bin/wcc.log').read_text(errors='replace')
    (out/(label+'.full.log')).write_text(log)
    (out/(label+'.stdout.log')).write_bytes(p.stdout+p.stderr)
    assertions = [s for s in log.splitlines() if '[Error][Assert]' in s]
    commands.append(dict(label=label,command=cmd,exit_code=p.returncode,assertions=assertions))
    write_json(out/'commands.json',commands)
    if p.returncode or any(not any(x in s for x in ('depotDirectory.cpp:11','soundFileLoader.cpp:101')) for s in assertions):
        raise ValueError('Native stage failed or new assertion: '+label)
    print('Native',label,'passed',flush=True)
    return log


def package(out, deploy, selected, files, manifest, runner, commands, verified_native_reuse=False):
    if ((out/'packed').exists() and not verified_native_reuse) or deploy.exists():
        raise ValueError('Fresh pack/deploy destination required; do not overwrite an earlier native run')
    if verified_native_reuse and not all(any(c['label']==label and c['exit_code']==0 for c in commands)
                                        for label in ('cook','validate','pack','metadata')):
        raise ValueError('Completed native evidence required to resume post-build ZIP checks')
    pack = out/'pack-input'
    for key,data in files.items():
        p = pack/key
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
    # The native metadata command is for native resources. Keep the author's
    # already built alias-only bundle/metadata intact instead of passing raw
    # XML through that command. Still cache all logical inputs for rollback.
    native_files = {k:v for k,v in files.items() if k.endswith('.redswf')}
    native_pack = out/'native-pack-input'
    for key,data in native_files.items():
        p = native_pack/key
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
    # Packing operates on explicit cooked input, not a source depot. Isolate an
    # empty depot for these stages rather than retaining the cook mount.
    if not verified_native_reuse:
        with mount(runner,out,{}) as workspace:
            official(runner,out,'pack',['pack','-dir='+str(native_pack),'-outdir='+str(out/'packed'),'-compression=ZLIB'],commands)
            official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
    bundle = out/'packed/blob0.bundle'
    entries = list(audit.entries(bundle))
    if len(entries)!=len(native_files) or {e['resource'] for e in entries}!=set(native_files):
        raise ValueError('Pack resource inventory differs')
    metadata = (out/'packed/metadata.store').read_bytes()
    for key,data in native_files.items():
        if bars.extract(bundle,key)!=data or key.replace('/','\\').encode() not in metadata:
            raise ValueError('Bundle re-extraction/metadata key differs: '+key)
    prefix = 'Mods/'+MOD+'/content/'
    members = {prefix+n:(out/'packed'/n).read_bytes() for n in ('blob0.bundle','metadata.store')}
    alias = REF/'mods/modInkAndIronFonts/content'
    alias_entries = list(audit.entries(alias/'blob0.bundle'))
    if len(alias_entries)!=1 or alias_entries[0]['resource']!='gameplay/gui_new/fonts.xml':
        raise ValueError('Author alias bundle contains unrelated resources')
    game = Path('C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3')
    if read_bundle(alias/'blob0.bundle',alias_entries[0],game,out)!=files['gameplay/gui_new/fonts.xml']:
        raise ValueError('Original alias bundle extraction differs')
    for name in ('blob0.bundle','metadata.store'):
        members['Mods/'+ALIAS_MOD+'/content/'+name] = (alias/name).read_bytes()
    if selected & {'damageditems','journalupdate'}:
        members[prefix+'texture.cache'] = (HUD/'texture.cache').read_bytes()
    members[prefix+'en.w3strings'] = (HUD/'en.w3strings').read_bytes()
    scripts = selected_scripts(selected)
    for stem in scripts:
        members[prefix+'scripts/local/'+stem+'.ws'] = fallback.text(HUD/'scripts/local'/(stem+'.ws')).encode()
    if 'enemyfocus' in selected:
        members[prefix+'scripts/local/inkIronHUDStateBridge.ws'] = fallback.text(ROOT/'src/hud/inkIronHUDStateBridge.ws').encode()
    tree = ET.parse(REF/'bin/config/r4game/user_config_matrix/pc/modInkAndIron.xml')
    visible = tree.find('./Group/VisibleVars')
    for var in list(visible):
        wanted = set(HUD_OPTIONS)
        if 'inkIronNpcPlate' not in scripts:
            wanted -= {'iiShowQuickSlotKeys','iiGoldLockRing'}
        if 'minimap2' not in selected:
            wanted.discard('iiShowMinimapClock')
        if 'damageditems' not in selected:
            wanted.discard('iiGearStyle')
        if 'journalupdate' not in selected:
            wanted -= {'iiQuestColour','iiQuestXp'}
        if 'radialmenu' not in selected:
            wanted.discard('iiColoredSigns')
        if var.get('id') not in wanted:
            visible.remove(var)
    members['bin/config/r4game/user_config_matrix/pc/modInkIronHUDBatch.xml'] = ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)
    # Carry the locally supplied open-font notices with the derivative font.
    utility_zip = ROOT/'deploy/field-folio-interactions-private-v2/Field-and-Folio-Interactions-v2-private-test.zip'
    if 'interactions' in selected:
        with zipfile.ZipFile(utility_zip) as z:
            for name in z.namelist():
                if 'OFL' in name or 'FONT-NOTICES' in name:
                    members[prefix+'font-notices/'+Path(name).name] = z.read(name)
    def zipper():
        buf = io.BytesIO()
        with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in sorted(members.items()):
                info = zipfile.ZipInfo(name,(2026,10,12,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info,data)
        return buf.getvalue()
    data = zipper()
    if data!=zipper():
        raise ValueError('Nondeterministic ZIP')
    deploy.mkdir()
    archive = deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip'
    archive.write_bytes(data)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or {n:z.read(n) for n in z.namelist()}!=members:
            raise ValueError('ZIP validation failed')
    manifest.update(mod=MOD,selected=sorted(selected),author_scripts=scripts,
        build_path=str(out),builder_sha256=fallback.sha(Path(__file__)),
        patcher_sha256=fallback.sha(ROOT/'tools/patch-ink-hud-movies.py'),
        alias_mod=ALIAS_MOD,alias_container_unchanged=True,native_bundle_keys=sorted(native_files),
        commands=commands,resource_hashes={k:audit.sha(v) for k,v in files.items()},
        package_members={n:audit.sha(v) for n,v in members.items()},zip_path=str(archive),
        zip_sha256=audit.sha(data),zip_bytes=len(data),exact_reextraction=True,metadata_keys_verified=True,
        compiler_sha256=font.COMPILER_SHA,ffdec_sha256=fallback.sha(ROOT/'build/tools/ffdec/ffdec.jar'),
        runtime_tested=False,deployed=False)
    write_json(out/'receipt.json',manifest)
    write_json(deploy/'manifest.json',manifest)
    print('Package',archive,manifest['zip_sha256'],flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game',type=Path,default=Path('C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3'))
    ap.add_argument('--settings',type=Path,default=Path('C:/Users/micha/OneDrive - hull.ac.uk/Documents/The Witcher 3/mods.settings'))
    ap.add_argument('--assembly',type=Path,default=Path('C:/REDkitProjects/witchercompatibility/compatibility-validation/analog-gait'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--deploy',type=Path,required=True)
    ap.add_argument('--reuse',type=Path)
    ap.add_argument('--exclude',nargs='*',default=[])
    ap.add_argument('--refresh-movies',nargs='*',default=[],
                    help='Rebuild only bounded edited movies using verified parent contracts/scripts')
    a = ap.parse_args()
    out, deploy = a.out.resolve(),a.deploy.resolve()
    font.private_path(out)
    if ROOT/'deploy' not in deploy.parents or out.exists() or deploy.exists():
        raise ValueError('Fresh ignored build/deploy directories required')
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':
        raise ValueError('ui-overhaul required')
    selected = selection(a.exclude)
    out.mkdir()
    runner = ROOT/'build/npc-state-expanded'
    commands = []
    if a.reuse:
        reuse = font.private_path(a.reuse.resolve())
        parent = json.loads((reuse/'receipt.json').read_text())
        if not parent.get('official_cook_validated') or not parent.get('exact_reextraction') or not selected<=set(parent['selected']):
            raise ValueError('Verified cooked superset required')
        # Support, author sources, and original bridge must still match pins.
        for p,digest in parent['reference_pins'].items():
            if fallback.sha(Path(p))!=digest:
                raise ValueError('Pinned support input changed')
        bridge_key = 'Mods/'+MOD+'/content/scripts/local/inkIronHUDStateBridge.ws'
        if 'enemyfocus' in selected and audit.sha(fallback.text(ROOT/'src/hud/inkIronHUDStateBridge.ws').encode())!=parent['package_members'][bridge_key]:
            raise ValueError('Bridge changed since validated parent')
        files = {}
        for key,digest in parent['resource_hashes'].items():
            if key.endswith('fonts.xml') or Path(key).stem.removeprefix('hud_') in selected:
                data = (reuse/'pack-input'/key).read_bytes()
                if audit.sha(data)!=digest:
                    raise ValueError('Cached cooked resource changed')
                files[key] = data
        if a.refresh_movies:
            if a.exclude or set(a.refresh_movies)-{'buffs','enemyfocus','interactions'}:
                raise ValueError('Refresh is limited to bounded edits in a complete verified batch')
            state = bars.snapshot(a.game,a.settings)
            if state!=json.loads((reuse/'live-before.json').read_text()):
                raise ValueError('Deployed inputs changed since parent compile')
            write_json(out/'live-before.json',state)
            refreshed = {}
            for name in a.refresh_movies:
                key = PREFIX+'hud_'+name+'.redswf'
                source = (ROOT/'build/ink-and-iron-0.8-audit/payloads/modInkAndIronHUD'/key).read_bytes()
                if audit.sha(source)!=parent['movie_contracts'][name]['input_sha256']:
                    raise ValueError('Parent author source changed')
                trial = ROOT/'build/ink-and-iron-0.8-audit/live/modFieldFolioInteractionsV2-hud_interactions.redswf'
                native = Path(parent['movie_contracts'][name]['native_source'])
                if fallback.sha(native)!=parent['movie_contracts'][name]['native_source_sha256']:
                    raise ValueError('Parent native contract source changed')
                # Re-export original source; never trust a stale decompiler tree.
                gfx = out/'exports'/name/'original.gfx'
                gfx.parent.mkdir(parents=True)
                gfx.write_bytes(patcher.movie(source)[1])
                export(gfx,gfx.parent)
                candidate,receipt = patcher.prepare('hud_'+name,source,gfx.parent,out/'modified'/name,
                                                    trial.read_bytes() if name=='interactions' else None)
                after = out/'modified'/name/'reexport'
                export(out/'modified'/name/'candidate.gfx',after)
                parent['movie_contracts'][name] = movie_contract(name,source,candidate,gfx.parent/'scripts',after/'scripts',native)
                parent['modifications'][name] = receipt
                refreshed[key] = candidate
            with mount(runner,out,refreshed) as workspace:
                official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
                log = official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
                if 'Found '+str(len(refreshed))+' files to validate' not in log or 'Errors found in 0 resources:' not in log:
                    raise ValueError('Refreshed native validation inventory differs')
                for key,expected in refreshed.items():
                    cooked = (out/'cooked'/key).read_bytes()
                    if cooked!=expected or not all(c['crc_valid'] for c in font.native.chunks(cooked)):
                        raise ValueError('Refreshed cook changed resource')
                    atlas_contract(cooked)
                    files[key] = cooked
            if bars.snapshot(a.game,a.settings)!=state:
                raise ValueError('Live inputs changed during refreshed build')
            parent['refreshed_movies'] = a.refresh_movies
            parent['reused_script_evidence'] = str(reuse/'scripts/receipt.json')
        # Check all atlases even for immutable reused movies.
        for key,data in files.items():
            if key.endswith('.redswf'):
                parent['movie_contracts'][Path(key).stem.removeprefix('hud_')]['atlas'] = atlas_contract(data)
        parent['reused_native_commands'] = parent['commands']
        parent['movie_contracts'] = {n:r for n,r in parent['movie_contracts'].items() if n in selected}
        parent['modifications'] = {n:r for n,r in parent['modifications'].items() if n in selected}
        parent.update(rollback_parent=str(reuse),rollback_parent_zip_sha256=parent['zip_sha256'],
                      reused_cooked_inputs=True,excluded=sorted(set(NATIVE)-selected))
        package(out,deploy,selected,files,parent,runner,commands)
        return
    if a.exclude:
        raise ValueError('Exclusions only supported for verified --reuse rollback variants')
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read_string(settings_text(a.settings))
    for owner in ('mod0000_MergedFiles','modFriendlyHUD','modSeamlessAdaptiveHUD',
                  'modQuietEditorialNPCColorsV4','modQuietEditorialNPCShadow','modQuietFolioEnglish',
                  'modFieldFolioInteractionsV2'):
        if owner not in cfg or cfg[owner].get('Enabled')!='1':
            raise ValueError('Required deployed provider disabled/absent: '+owner)
    state = bars.snapshot(a.game,a.settings)
    write_json(out/'live-before.json',state)
    pins = json.loads((ROOT/'research/ink-and-iron-0.8-audit/input-files.json').read_text())
    reference_pins = {}
    for row in pins:
        p = REF/row['path']
        if 'modInkAndIronHUD/' in row['path'] or row['path'].endswith('modInkAndIron.xml') or 'modInkAndIronDialogue/' in row['path'] or 'modInkAndIronFonts/' in row['path']:
            if fallback.sha(p)!=row['sha256']:
                raise ValueError('Canonical input changed: '+str(p))
            reference_pins[str(p.resolve())] = row['sha256']
    rows = list(csv.DictReader((ROOT/'research/ink-and-iron-0.8-audit/resources.csv').open()))
    files, reports, modifications = {},{},{}
    owner_keys = {PREFIX+'hud_'+n+'.redswf' for n in selected}|{'gameplay/gui_new/fonts.xml'}
    current = owners(a.game,cfg,owner_keys,out)
    write_json(out/'owners.json',current)
    trial_key = PREFIX+'hud_interactions.redswf'
    trial_owner = next(o for o in current[trial_key] if o['owner']=='modFieldFolioInteractionsV2' and o['enabled']=='1')
    trial = ROOT/'build/ink-and-iron-0.8-audit/live/modFieldFolioInteractionsV2-hud_interactions.redswf'
    if fallback.sha(trial)!=trial_owner['sha256']:
        raise ValueError('Trial font source is not currently deployed resource')
    cache = list(inventory.cache_entries(HUD/'texture.cache'))
    if len(cache)!=59 or any('/inkiron/gear/' not in r['resource'] and '/inkiron/quest/' not in r['resource'] for r in cache):
        raise ValueError('Unexpected HUD texture-cache scope')
    for name in sorted(selected):
        key = PREFIX+'hud_'+name+'.redswf'
        module = 'modInkAndIronDialogue' if name=='dialog' else 'modInkAndIronHUD'
        row = next(r for r in rows if r['resource']==key and r['module']==module)
        path = ROOT/'build/ink-and-iron-0.8-audit/payloads'/module/key
        source = path.read_bytes()
        if audit.sha(source)!=row['sha256']:
            raise ValueError('Audited extraction hash differs')
        gfx = out/'exports'/name/'original.gfx'
        gfx.parent.mkdir(parents=True)
        gfx.write_bytes(patcher.movie(source)[1])
        before = gfx.parent/'scripts'
        export(gfx,gfx.parent)
        candidate = source
        after = before
        if name in ('buffs','enemyfocus','interactions'):
            # prepare expects exports rooted under <probe>/scripts.
            candidate,receipt = patcher.prepare('hud_'+name,source,gfx.parent,out/'modified'/name,
                                                trial.read_bytes() if name=='interactions' else None)
            modifications[name] = receipt
            after = out/'modified'/name/'reexport/scripts'
            export(out/'modified'/name/'candidate.gfx',after.parent)
        reports[name] = movie_contract(name,source,candidate,before,after,native_input(name,a.game,a.assembly))
        files[key] = candidate
        print('Contracts',name,'passed',flush=True)
    write_json(out/'movie-contracts.json',reports)
    script = compiler(a.assembly,a.game,cfg,out/'scripts',selected_scripts(selected))
    with mount(runner,out,files) as workspace:
        official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
        log = official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
        if 'Found '+str(len(files))+' files to validate' not in log or 'Errors found in 0 resources:' not in log:
            raise ValueError('Native resource validation inventory/errors differ')
        for key,expected in files.items():
            cooked = (out/'cooked'/key).read_bytes()
            if font.movie_tags(cooked)!=font.movie_tags(expected) or [c['tail'] for c in font.native.chunks(cooked)[1:]]!=[c['tail'] for c in font.native.chunks(expected)[1:]]:
                raise ValueError('Cooked movie/atlas differs')
            if not all(c['crc_valid'] for c in font.native.chunks(cooked)):
                raise ValueError('Cooked CRC invalid')
            files[key] = cooked
    key = 'gameplay/gui_new/fonts.xml'
    row = next(r for r in rows if r['resource']==key and r['module']=='modInkAndIronFonts')
    alias = (ROOT/'build/ink-and-iron-0.8-audit/payloads/modInkAndIronFonts'/key).read_bytes()
    if audit.sha(alias)!=row['sha256'] or b'PF Din Text Cond Pro' not in alias:
        raise ValueError('Alias-only font support changed')
    ET.fromstring(alias)
    files[key] = alias
    if bars.snapshot(a.game,a.settings)!=state:
        raise ValueError('Live inputs changed during build')
    manifest = dict(version='I&I 0.8 HUD batch private v1',reference_pins=reference_pins,
        owners=current,movie_contracts=reports,modifications=modifications,script_regression=script['results'],
        opaque_mods_not_recompiled=script['opaque_mods_not_recompiled'],texture_entries=cache,
        official_cook_validated=True,live_inputs_unchanged=True,runner_workspace_restored=True,
        accepted_bars_dependency='modInkIronAdaptiveBarsTest; leave v1 enabled unchanged',
        excluded_fullscreen_and_root=True)
    for receipt in modifications.values():
        receipt.update(native_validation_pending=False,native_cook_validated=True)
    package(out,deploy,selected,files,manifest,runner,commands)
    if bars.snapshot(a.game,a.settings)!=state:
        raise ValueError('Live inputs changed during packaging')


if __name__=='__main__':
    main()
