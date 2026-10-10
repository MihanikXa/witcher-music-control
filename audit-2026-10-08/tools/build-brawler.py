"""Private incremental Core variant from verified deployed/pinned inputs; no deployment."""
import argparse,copy,difflib,hashlib,importlib.util,json,re,shutil,subprocess,sys,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/'release/witcher-compatibility'
OUT=RELEASE/'brawler-only'
CORE_HASH='0e63fc2f62fc73d3e325e4f698e62735cbaa12bf8977ce136676a48d547950f9'
ANALOG_HASH='fbbe3b2ecfeab77965f13b4e7386c8891167f37f8d770b20a37c7c7fd9539909'
BEST='Mods/modBestGsSchoolStances/'
CSM='Mods/modCombatSpeed/'
PC='bin/config/r4game/user_config_matrix/pc/'
spec=importlib.util.spec_from_file_location('helpers',ROOT/'tools/build-release.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
spec=importlib.util.spec_from_file_location('settings',ROOT/'tools/prepare-settings.py')
settings=importlib.util.module_from_spec(spec);spec.loader.exec_module(settings)

def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2),encoding='utf-8')
def function(text,name,owner=None):
    if owner:
        marker='@wrapMethod('+owner+')'; start=text.index(marker+'\nfunction '+name+'(')
        tail=text[start:]; a,z=h.bounds(tail,name) if tail.count('function '+name+'(')==1 else (None,None)
        if a is None:
            # Disambiguate equal method names belonging to distinct annotation owners.
            following=tail.find('\n@',1);tail=tail if following<0 else tail[:following]
            a,z=h.bounds(tail,name)
        return tail[:z+1].strip()+'\n'
    a,z=h.bounds(text,name);clean=h.masked(text)
    match=next(m for m in re.finditer(r'\bfunction\s+'+re.escape(name)+r'\s*\(',clean) if m.end()<a)
    start=text.rfind('\n',0,match.start())+1
    previous=text.rfind('\n',0,max(0,start-1))+1
    if text[previous:start].lstrip().startswith('@'):start=previous
    return text[start:z+1].strip()+'\n'

def mechanics(source):
    keep=['BG2_GloveEnhancementCount','BG2_IsFightingWithFists',
          'BG2_BrawlerSocketDamageBonus','BG2_BrawlerSocketDefenseBonus']
    chunks=['// Private derivative: Bestg Brawler mechanics, original author attribution retained.\n',
            '@addField(W3DamageAction) var compatBrawlerDamageApplied : bool;\n']
    chunks += [function(source,n) for n in keep]
    out=function(source,'ProcessAction','W3DamageManager')
    body=h.body(out,'ProcessAction');start=body.index('factor = (BG2_Config');end=body.index('act.MultiplyAllDamageBy(factor);',start)+len('act.MultiplyAllDamageBy(factor);')
    retained=body[start:end].replace('bg2_stanceDamageApplied','compatBrawlerDamageApplied')
    out=h.replace_body(out,'ProcessAction','''    var p : CR4Player;
    var hit : W3Action_Attack;
    var factor : float;
    p = GetWitcherPlayer();
    if(act && !act.compatBrawlerDamageApplied && p && p.CompatBrawlerActive()
        && (CActor)act.attacker == p && !act.IsDoTDamage())
    {
        hit = (W3Action_Attack)act;
        if(hit && act.IsActionMelee() && p.BG2_IsFightingWithFists())
        {
'''+retained+'''
        }
    }
    wrappedMethod(act);''');chunks.append(out)
    out=function(source,'ReduceDamage','W3PlayerWitcher');body=h.body(out,'ReduceDamage')
    start=body.index('if(damageData && this == GetWitcherPlayer() && bg2_stance == BG2_Brawler')
    end=body.index('if(!damageData.bg2_guardEligible',start)
    retained=body[start:end].replace('bg2_stance == BG2_Brawler','CompatBrawlerActive()')
    # Require an actual other actor, matching the documented enemy-melee constraint.
    retained=retained.replace('(CActor)damageData.attacker != this','(CActor)damageData.attacker && (CActor)damageData.attacker != this')
    chunks.append(h.replace_body(out,'ReduceDamage','    var factor : float;\n    wrappedMethod(damageData);\n'+retained))
    for name,owner in [('FistFightCheck','CActor'),('PerformParryCheck','CR4Player'),('PerformCounterCheck','CR4Player')]:
        out=function(source,name,owner)
        out=out.replace('p.bg2_stance == BG2_Brawler','p.CompatBrawlerActive()').replace('bg2_stance == BG2_Brawler','CompatBrawlerActive()')
        chunks.append(out)
    return '\n'.join(chunks)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True)
    ap.add_argument('--documents',type=Path,required=True);ap.add_argument('--compile',action='store_true');a=ap.parse_args()
    game=a.game.resolve();docs=a.documents.resolve();OUT.mkdir(parents=True,exist_ok=True)
    core=RELEASE/'01-core-replacements.zip';analog=RELEASE/'analog-gait/04-updated-merges-analog-gait.zip'
    assert sha(core.read_bytes())==CORE_HASH and sha(analog.read_bytes())==ANALOG_HASH
    before={};original={}
    with zipfile.ZipFile(core) as z:
        for n in z.namelist():
            original[n]=z.read(n);assert (game/n).read_bytes()==original[n],('Deployed Core differs',n)
            before[str(game/n)]=sha(original[n])
    with zipfile.ZipFile(analog) as z:
        for n in z.namelist():assert (game/n).read_bytes()==z.read(n),('Deployed analog differs',n);before[str(game/n)]=sha(z.read(n))
    for p in [docs/'input.settings',docs/'dx12user.settings',docs/'mods.settings',game/(PC+'input.xml')]:before[str(p)]=sha(p.read_bytes())
    save(OUT/'protected-live-before.json',before)
    bindings=(docs/'input.settings').read_text(encoding='utf-8-sig')
    assert not re.search(r'^\s*IK_F6\s*=',bindings,re.M),'F6 occupied: choose another vacant key'
    assert 'CompatBrawlerToggle' not in bindings,'Binding baseline already modified'
    # Record every installed Bestg/CSM function and its outgoing named calls.
    graph=[];source_hashes={}
    for n,b in original.items():
        source_hashes[n]=sha(b)
        if not n.endswith('.ws') or not n.startswith((BEST,CSM)):continue
        text=b.decode('utf-8-sig');clean=h.masked(text)
        for m in re.finditer(r'\b(?:function|event)\s+(\w+)\s*\(',clean):
            brace=clean.index('{',m.end());end=brace+1;depth=1
            while depth:
                if clean[end]=='{':depth+=1
                elif clean[end]=='}':depth-=1
                end+=1
            previous=clean.rfind('}',0,m.start())+1
            annotations=list(re.finditer(r'@(?:wrap|replace|add)Method\(([^)]+)\)',clean[previous:m.start()]))
            graph.append(dict(file=n,function=m[1],owner=annotations[-1][1] if annotations else None,line=text[:m.start()].count('\n')+1,
                calls=sorted(set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',clean[brace:end])))))
    save(OUT/'dependency-map.json',dict(source_sha256=source_hashes,functions=graph))
    # Other installed mods must not depend on removed Bestg/CSM APIs.
    outside=[]
    for p in (game/'Mods').rglob('*.ws'):
        if any(x in p.parts for x in ['modBestGsSchoolStances','modCombatSpeed']):continue
        text=p.read_bytes().decode('utf-16' if p.read_bytes().startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        if re.search(r'\b(?:BG2_\w+|bg2_\w+|CombatSpeed|CSM_\w+|SetWhirlSpeed|SetRendSpeed)\b',h.masked(text)):outside.append(str(p))
    assert not outside,('External removed-API dependencies',outside)
    payload={n:b for n,b in original.items() if not n.startswith(CSM) and not (n.startswith(BEST) and not n.endswith('.w3strings'))}
    # Retain locale labels; remove all cooked stance HUD/icons and unrelated scripts.
    payload[PC+'modCombatSpeed.xml']=b'<?xml version="1.0" encoding="utf-8"?>\n<UserConfig />\n'
    menu=ET.fromstring(original[PC+'modBestGsStances.xml'])
    for group in list(menu):
        if group.get('id')!='BG2Brawler':menu.remove(group)
    for parent in menu.iter():
        for child in list(parent):
            if child.get('id')=='ArrowDeflect' or child.get('varId')=='ArrowDeflect':parent.remove(child)
    payload[PC+'modBestGsStances.xml']=ET.tostring(menu,encoding='utf-8',xml_declaration=True)
    bas=ET.fromstring(original[PC+'modBloodAndSteel.xml'])
    for preset in bas.iter('Preset'):
        if preset.get('id')=='1':
            for entry in preset:
                values={'BaS_CustomAttackEnabled':'true','BaS_CustomDodgeEnabled':'true','BaS_CloseCamera':'false','BaS_Aggressiveness':'1'}
                if entry.get('varId') in values:entry.set('value',values[entry.get('varId')])
    payload[PC+'modBloodAndSteel.xml']=ET.tostring(bas,encoding='utf-8',xml_declaration=True)
    prefix=BEST+'content/scripts/local/'
    config=original[prefix+'BestGsStanceConfig.ws'].decode('utf-8-sig')
    config=function(config,'BG2_Config').replace('    BG2_InitializeMenu();\n','').replace('    if(thePlayer) thePlayer.BG2_MigrateAgileProfile();\n','')
    payload[prefix+'CompatBrawlerConfig.ws']=config.encode('utf-8')
    payload[prefix+'CompatBrawlerMechanics.ws']=mechanics(original[prefix+'BestGsStanceDamage.ws'].decode('utf-8-sig')).encode('utf-8')
    payload[prefix+'CompatBrawlerController.ws']=(ROOT/'tools/brawler-controller.ws').read_text(encoding='utf-8-sig').encode('utf-8')
    for n,b in payload.items():
        if n.startswith(BEST) and n.endswith('.ws'):
            text=b.decode('utf-8');assert not re.search(r'BG2_(?:Witcher|Bear|Feline|Griffin|Viper)|SetAnimationSpeedMultiplier|AddAbility|SetStatPointMax',text)
        target=OUT/'payloads'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
    archive=OUT/'01-brawler-only-core.zip'
    with zipfile.ZipFile(archive,'w') as z:
        for n,b in sorted(payload.items()):
            info=zipfile.ZipInfo(n,(2026,10,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==len(payload)
    settings_delta={'BaS_Main':{'BaS_Enabled':'true','BaS_CustomAttackEnabled':'true','BaS_CustomDodgeEnabled':'true','BaS_Aggressiveness':'1','BaS_CloseCamera':'false'}}
    input_delta={context:{'IK_F6':'(Action=CompatBrawlerToggle)'} for context in ['Combat','Exploration']}
    for name,delta in [('dx12user.settings',settings_delta),('input.settings',input_delta)]:
        save(OUT/(name+'.delta.json'),delta);old=(docs/name).read_text(encoding='utf-8-sig');new=settings.transform(old,delta)
        assert old!=new or name=='dx12user.settings'
        (OUT/(name+'.proposed')).write_text(new,encoding='utf-8')
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='current/'+name,tofile='proposed/'+name)),encoding='utf-8')
    changed=[n for n,b in payload.items() if original.get(n)!=b]
    receipt=dict(archive=str(archive),sha256=sha(archive.read_bytes()),files=len(payload),changed=changed,
        removed=sorted(set(original)-set(payload)),unchanged=sorted(n for n,b in payload.items() if original.get(n)==b),
        original_core_sha256=CORE_HASH,package04_sha256=ANALOG_HASH,external_api_dependencies=outside,
        source_inventory_sha256=sha(json.dumps(source_hashes,sort_keys=True).encode()),runtime_test=False,actual_deployment=False)
    old_receipt=OUT/'validation.json'
    if old_receipt.exists():
        prev=json.loads(old_receipt.read_text(encoding='utf-8'))
        if prev.get('sha256')==receipt['sha256'] and 'compiler' in prev:receipt['compiler']=prev['compiler']
    if a.compile:
        reference=Path('C:/REDkitProjects/WitcherCompatibility/compatibility-validation/analog-gait')
        work=reference.parent/'brawler-only';assert not work.exists(),'Preserve previous isolated result before recompilation'
        shutil.copytree(reference/'base',work/'base');shutil.copytree(reference/'patch',work/'patch');(work/'output').mkdir()
        # Alter only the two superseded overlay directories in the isolated copy.
        overlays=work/'base/__overlays'
        for name in ['modBestGsSchoolStances','modCombatSpeed']:
            target=overlays/name;assert target.resolve().is_relative_to(work.resolve());shutil.rmtree(target)
        for n,b in payload.items():
            if n.startswith(BEST) and n.endswith('.ws'):
                target=overlays/'modBestGsSchoolStances'/n.split('content/scripts/',1)[1];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        runtime=ROOT/'private/redkit-runtime'
        proc=subprocess.run([str(runtime/'wcc_lite.exe'),'compilescripts',str(work/'base'),'-patch='+str(work/'patch'),'-out='+str(work/'output')],cwd=runtime,capture_output=True,timeout=55)
        log=proc.stdout+proc.stderr;(work/'compiler.log').write_bytes(log);message=log.decode(errors='replace');blob=work/'output/blob.rsblob'
        receipt['compiler']=dict(exit_code=proc.returncode,success=proc.returncode==0 and 'Success! Patch scripts blob saved' in message and blob.exists(),
            warnings=message.count('[Warning]'),assertions=message.count('[Error][Assert]'),script_errors=[l for l in message.splitlines() if '[Error][WCC]' in l],
            output_sha256=sha(blob.read_bytes()) if blob.exists() else None,opaque_blobs_recompiled=False)
    save(OUT/'validation.json',receipt)
    if a.compile:assert receipt['compiler']['success'],'Inspect compiler.log; do not release failed source'
    for p,digest in before.items():assert sha(Path(p).read_bytes())==digest,('Protected live file changed',p)
    save(OUT/'topology/validation.json',dict(archives=[dict(name=archive.name,files=[dict(path=n) for n in payload])]))
    # Publish original build metadata only: no source bodies, settings or machine paths.
    save(ROOT/'brawler-manifest.json',dict(format=1,archive=archive.name,sha256=receipt['sha256'],
        baseline_core_sha256=CORE_HASH,preserved_package04_sha256=ANALOG_HASH,
        source_inventory_sha256=receipt['source_inventory_sha256'],
        files=[dict(path=n,sha256=sha(b),bytes=len(b),unchanged_from_core=original.get(n)==b) for n,b in sorted(payload.items())],
        removed_core_paths=receipt['removed'],compiler=receipt.get('compiler'),runtime_test=False))
    print(json.dumps({k:receipt[k] for k in ['archive','sha256','files','source_inventory_sha256']}))
    if 'compiler' in receipt:print(json.dumps(receipt['compiler']))
if __name__=='__main__':main()
