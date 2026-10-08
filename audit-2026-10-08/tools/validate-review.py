# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Read-only audit and review-package validation. Never deploys anything."""
from inventory import *
import xml.etree.ElementTree as ET
import importlib.util,re

def main():
 evidence=ROOT/'evidence'
 read=lambda n:json.loads((evidence/n).read_text(encoding='utf-8'))
 official={x['relative'].replace('\\','/').lower() for x in read('steam-manifest-files.json') if not x['flags']&64}
 ownership={}
 for d in read('deployment-manifests.json'):
  base=Path(d.get('targetPath',str(Path(d['manifest']).parent)))
  for e in d['files']:
   p=base/e.get('target','')/e['relPath'];ownership[str(p).lower()]=e
 extra=[]
 for p in GAME.rglob('*'):
  if p.is_file() and str(p.relative_to(GAME)).replace('\\','/').lower() not in official:
   rel=str(p.relative_to(GAME));extra.append(dict(path=str(p),relative=rel,size=p.stat().st_size,managed=ownership.get(str(p).lower())))
 save('all-extra-game-files.json',extra)
 resources=collections.defaultdict(list)
 for x in read('bundle-entries.json'):
  resources[x['resource']].append(dict(mod=x['mod'],kind='bundle',path=x['bundle']))
 for x in read('installed-files.json'):
  rel=x['relative'].lower()
  if rel.startswith('content/') and Path(rel).suffix in ['.redswf','.w2phase','.w2scene','.w2ent','.xml','.w2mesh','.w2l','.xbm']:
   resources[rel[len('content/'):]].append(dict(mod=x['mod'],kind='loose',path=x['path'],sha256=x['sha256']))
 save('unified-resource-collisions.json',{k:v for k,v in resources.items() if len(set(x['mod'] for x in v))>1})
 changed=[];checked=0
 for x in read('installed-files.json')+read('other-game-files.json'):
  p=Path(x['path']);checked+=1
  if not p.is_file() or sha(p)!=x['sha256']:changed.append(str(p))
 for x in read('control-snapshot.json'):
  checked+=1
  if sha(Path(x['live']))!=x['sha256']:changed.append(x['live'])
 xml=[];groups=collections.defaultdict(list)
 for p in (GAME/'bin/config').rglob('*.xml'):
  try:
   tree=ET.parse(p)
   for g in tree.iter('Group'):
    name=g.attrib.get('id')
    if name:groups[name].append(str(p))
   xml.append(dict(path=str(p),parse=True))
  except Exception as e:xml.append(dict(path=str(p),parse=False,error=str(e)))
 save('config-xml-validation.json',dict(files=xml,shared_group_ids={k:v for k,v in groups.items() if len(set(v))>1}))
 # Compare menu-loader references with the actual menu directory.
 pc=GAME/'bin/config/r4game/user_config_matrix/pc'
 menu_lists=[]
 for p in pc.glob('*filelist*.txt'):
  names=[n.strip() for n in p.read_text(encoding='utf-8-sig').splitlines() if n.strip()]
  menu_lists.append(dict(path=str(p),missing=[n for n in names if not (pc/n).is_file()],duplicates=[n for n,c in collections.Counter(names).items() if c>1]))
 save('menu-filelists.json',menu_lists)
 # Check patch hashes, added resources and explicit enabled/unique priorities.
 patch_changed=[]
 for x in read('patch-manifest.json'):
  if not Path(x['path']).is_file() or sha(Path(x['path']))!=x['sha256']:patch_changed.append(x['path'])
 ini=configparser.ConfigParser();ini.read(ROOT/'patches/load-order/mods.settings.proposed')
 priorities=[int(ini[s]['priority']) for s in ini.sections()]
 projected=[]
 for package in ['arrow-deflection-layout','localization']:
  for p in (ROOT/'patches'/package/'Mods').rglob('*'):
   if p.is_file():
    target=GAME/'Mods'/p.relative_to(ROOT/'patches'/package/'Mods')
    projected.append(dict(package=package,target=str(target),already_exists=target.exists(),sha256=sha(p)))
 result=dict(live_files_rechecked=checked,changed_live_files=changed,patch_hash_failures=patch_changed,
  projected_new_files=projected,priority_sections=len(priorities),priorities_unique=len(set(priorities))==len(priorities),
  compiler_pass=False,runtime_test=False,deploy_performed=False)
 spec=importlib.util.spec_from_file_location('loc_audit',ROOT/'tools/localization-audit.py');loc=importlib.util.module_from_spec(spec);spec.loader.exec_module(loc)
 oldstrings=read('localization-index.json');overlaps=[]
 for p in (ROOT/'patches/arrow-deflection-layout/Mods').rglob('*.w3strings'):
  new=loc.index(p)
  for old in oldstrings:
   if old['language']==p.stem:
    for kind in ['ids','keys']:
     common=set(old[kind])&set(new[kind])
     if common:overlaps.append(dict(language=p.stem,kind=kind,other=old['mod'],shared=sorted(common)))
 result['arrow_localization_new_overlaps']=overlaps
 arrow=(ROOT/'patches/arrow-deflection-layout/Mods/modArrowParryManual/content/scripts/local/arrowParryManual.ws').read_text(encoding='utf-8-sig')
 targets=re.findall(r'@(wrapMethod|replaceMethod|addMethod|addField)\s*\(\s*(\w+)\s*\)\s*(?:\w+\s+)*(?:function|var)\s+(\w+)',arrow)
 ann=read('annotations.json');result['arrow_annotation_existing_targets']=[dict(op=op,target=cls+'.'+name,existing=[a for a in ann if a['cls']==cls and a['member']==name]) for op,cls,name in targets if any(a['cls']==cls and a['member']==name for a in ann)]
 save('review-validation.json',result)
 print(json.dumps(dict(extras=len(extra),live_checked=checked,live_changes=changed,xml_files=len(xml),xml_errors=[x for x in xml if not x['parse']],shared_group_ids={k:v for k,v in groups.items() if len(set(v))>1},menu_lists=menu_lists,patch_hash_failures=patch_changed,projected_files=len(projected),priorities_unique=result['priorities_unique'])))
if __name__=='__main__':main()
