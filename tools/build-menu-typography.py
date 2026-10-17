"""Private Menus v3 typography/item-art candidate; never deploys."""
import argparse,concurrent.futures,configparser,csv,importlib.util,io,json,re,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('complete-menus-087');b=c.b;t=load('refine-menu-typography')
OUT=ROOT/'build/menus087-v3';DEPLOY=ROOT/'deploy/menus087-v3'
TARGETS={
 'panel_alchemy':{'ItemCraftingModule':t.crafting},
 'panel_crafting':{'ItemCraftingModule':t.crafting},
}
# One helper per class; multiple call sites are added without redeclaring state.
def character(s):
 s=t.hook(s,'MenuCharacterDupe','inkRenderInfo')
 return t.append_method(s,'inkInit','this.qfTypeTree(this);')
TARGETS['panel_character_dupe']={'MenuCharacterDupe':character}
def inventory(s):
 s=t.hook(s,'MenuInventory','iaiTick')
 return t.append_method(s,'iaiTick','if(tip) this.qfTypeTree(tip);')
TARGETS['panel_inventory']={'MenuInventory':inventory}
def title(s):
 s=t.add_helper(s,'TextAreaModule');return t.append_method(s,'inkStyleTitle','this.qfCaps(this.tfTitle,30);')
def header(s):
 s=t.add_helper(s,'FeedbackDropdownMenuListItem')
 return t.append_method(s,'inkPaintHeader','this.qfCaps(this.textField,25);')
for stem in ('panel_journal_quests','panel_glossary_books','panel_glossary_bestiary','panel_glossary_encyclopedia'):
 TARGETS[stem]={'TextAreaModule':title,'FeedbackDropdownMenuListItem':header}

def item_cache(source,excluded):
 """Filter the index only. Retain original compressed pages/strings/mips exact.

 Supports only observed HCXT v6, reserved-zero/footer and no mip-table variant.
 No texture conversion, compression, new pixels or native metadata fabrication.
 """
 data=source.read_bytes();reserved,pages,count,names,mips,magic,version=struct.unpack('<QIIII4sI',data[-32:])
 if (reserved,mips,magic,version)!=(0,0,b'HCXT',6):raise ValueError('Unobserved cache variant')
 rows=list(b.m.b.inventory.cache_entries(source));start=len(data)-32-count*52
 selected=[(i,r) for i,r in enumerate(rows) if '/icons/inventory/' in r['resource'] and r['resource'] not in excluded]
 result=data[:start]+b''.join(data[start+i*52:start+(i+1)*52] for i,r in selected)+struct.pack('<QIIII4sI',reserved,pages,len(selected),names,mips,magic,version)
 return result,[r['resource'] for _,r in selected]

def icons():
 source=b.REF/'mods/modInkAndIronIcons/content/texture.cache'
 rows=list(b.m.b.inventory.cache_entries(source));keys={r['resource'] for r in rows};cfg=configparser.ConfigParser();cfg.read_string(b.m.b.settings_text(b.m.v.SETTINGS));collisions=[]
 for mod in (b.m.v.GAME/'Mods').iterdir():
  if mod.name not in cfg or cfg[mod.name].get('Enabled')!='1':continue
  for p in mod.rglob('texture.cache'):
   if not p.stat().st_size:continue
   overlap=keys & {r['resource'] for r in b.m.b.inventory.cache_entries(p)}
   if overlap:collisions.append(dict(owner=mod.name,path=str(p),priority=cfg[mod.name].get('Priority'),keys=sorted(overlap)))
 dlc_caches=0
 for cache in (b.m.v.GAME/'DLC').rglob('texture.cache'):
  if not cache.stat().st_size:continue
  dlc_caches+=1;overlap=keys & {r['resource'] for r in b.m.b.inventory.cache_entries(cache)}
  if overlap:collisions.append(dict(owner='DLC:'+str(cache.relative_to(b.m.v.GAME/'DLC').parts[0]),path=str(cache),priority=None,keys=sorted(overlap)))
 # Preserve all existing item fixes irrespective of the new module's priority.
 exclude={k for row in collisions for k in row['keys']};data,selected=item_cache(source,exclude)
 dest=OUT/'icons/texture.cache';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 observed=list(b.m.b.inventory.cache_entries(dest))
 if {r['resource'] for r in observed}!=set(selected):raise ValueError('Cache index failed roundtrip')
 original={r['resource']:r for r in rows}
 a=source.read_bytes()
 for r in observed:
  old=original[r['resource']]
  if a[old['offset']:old['offset']+old['packed']]!=data[r['offset']:r['offset']+r['packed']]:raise ValueError('Texture payload changed')
 # Verify supplied module against the original, pinned 0.8.7 archive.
 archive=next((b.REF/'archives').glob('*.zip'))
 with zipfile.ZipFile(archive) as z:
  for name in ('texture.cache','metadata.store'):
   path=b.REF/'mods/modInkAndIronIcons/content'/name
   if z.read('mods/modInkAndIronIcons/content/'+name)!=path.read_bytes():raise ValueError('Icon provenance mismatch')
 b.m.b.write_json(OUT/'icons/receipt.json',dict(upstream_archive_sha256=b.m.b.fallback.sha(archive),source_sha256=b.m.b.fallback.sha(source),output_sha256=b.m.b.audit.sha(data),source_entries=len(rows),selected_entries=len(observed),selected_keys=selected,excluded_existing_fixes=sorted(exclude),collisions=collisions,dlc_caches_read=dlc_caches,pixels_recompressed=False,index_reconstructed=True,author_metadata_unchanged=True))

def process(row):
 key=row['resource'];stem=Path(key).stem;source=(c.OUT/'prepared-inputs'/key).read_bytes();dest=OUT/'prepared-inputs'/key;dest.parent.mkdir(parents=True,exist_ok=True)
 if stem not in TARGETS:dest.write_bytes(source);return dict(row,retained_v2_exact=True)
 folder=OUT/'movies'/stem;folder.mkdir(parents=True,exist_ok=True);before=folder/'before'
 # Export the exact accepted v2 input, including existing compatibility changes.
 if not (before/'scripts').exists():
  before.mkdir(exist_ok=True);gfx=before/'source.gfx';gfx.write_bytes(b.m.r.p.movie(source)[1]);b.m.b.export(gfx,before)
 transforms=TARGETS[stem];checkpoint='abc-header2' if 'FeedbackDropdownMenuListItem' in transforms else ('abc-tip2' if stem=='panel_inventory' else 'abc')
 data,changes=b.batch_compile(source,before,folder/checkpoint,transforms)
 after=folder/'after'
 classes=[str(b.patch.one_file(before/'scripts',n).relative_to(before/'scripts').with_suffix('')).replace('\\','.').replace('/','.') for n in transforms]
 b.selected_export(data,after,classes)
 for n in transforms:
  old=b.patch.one_file(before/'scripts',n).read_text(encoding='utf-8-sig');new=b.patch.one_file(after/'scripts',n).read_text(encoding='utf-8-sig')
  # Exact source bodies are recorded privately; public/protected interface remains.
  import re
  for sig in re.findall(r'(?:public|protected) function [^\n]+',old):
   if sig not in new:raise ValueError('Interface changed '+stem+' '+sig)
 before_tags=b.m.b.audit.swf_tags(source)[2];after_tags=b.m.b.audit.swf_tags(data)[2]
 if [(code,p) for code,p in before_tags if code!=82]!=[(code,p) for code,p in after_tags if code!=82]:raise ValueError('Non-code movie definition changed')
 if b.m.b.contracts.symbols(before_tags)!=b.m.b.contracts.symbols(after_tags):raise ValueError('Symbol exports changed')
 if not all(r['crc_valid'] for r in b.m.b.font.native.chunks(data)):raise ValueError('Resource CRC failed')
 dest.write_bytes(data);print('Typography prepared',stem,flush=True)
 return dict(resource=key,input_sha256=b.m.b.audit.sha(source),output_sha256=b.m.b.audit.sha(data),classes=changes,only_doabc_changed=True)

def prepare():
 OUT.mkdir(exist_ok=True)
 if not (OUT/'installed-v2-check.json').exists():
  import subprocess
  subprocess.run([__import__('sys').executable,str(ROOT/'tools/verify-menu-visual-install.py'),'--release',str(c.OUT/'receipt.json'),'--report',str(OUT/'installed-v2-check.json')],check=True)
 if not (OUT/'frozen.json').exists():b.m.b.write_json(OUT/'frozen.json',b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS))
 icons();rows=json.loads((c.OUT/'prepared.json').read_text())['resources']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(process,rows))
 b.m.b.write_json(OUT/'prepared.json',dict(keys=sorted(r['resource'] for r in results),resources=results,runtime_tested=False))

def package():
 if DEPLOY.exists():raise ValueError('Fresh deploy directory required')
 commands=json.loads((OUT/'native-commands.json').read_text());prepared=json.loads((OUT/'prepared.json').read_text())
 if {r['label'] for r in commands if r['passed']}!={'cook','validate','pack','metadata'}:raise ValueError('Incomplete native pipeline')
 entries=list(b.m.b.audit.entries(OUT/'packed/blob0.bundle'))
 if {e['resource'] for e in entries}!=set(prepared['keys']):raise ValueError('Unexpected packed resource')
 for e in entries:
  if b.m.b.bars.extract(OUT/'packed/blob0.bundle',e['resource'])!=(OUT/'prepared-inputs'/e['resource']).read_bytes():raise ValueError('Extraction mismatch')
 parent=json.loads((c.OUT/'receipt.json').read_text())
 with zipfile.ZipFile(parent['zip_path']) as z:members={n:z.read(n) for n in z.namelist()}
 for name in ('blob0.bundle','metadata.store'):members['Mods/modInkIronMenus087/content/'+name]=(OUT/'packed'/name).read_bytes()
 members['Mods/modInkIronMenuItemArt/content/texture.cache']=(OUT/'icons/texture.cache').read_bytes()
 members['Mods/modInkIronMenuItemArt/content/metadata.store']=(b.REF/'mods/modInkAndIronIcons/content/metadata.store').read_bytes()
 def zip_bytes():
  stream=io.BytesIO()
  with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
   for name,data in sorted(members.items()):
    info=zipfile.ZipInfo(name,(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
  return stream.getvalue()
 data=zip_bytes()
 if data!=zip_bytes():raise ValueError('Nondeterministic ZIP')
 if b.m.b.bars.snapshot(b.m.v.GAME,b.m.v.SETTINGS)!=json.loads((OUT/'frozen.json').read_text()):raise ValueError('Live inputs changed')
 DEPLOY.mkdir();archive=DEPLOY/'Ink-Iron-0.8.7-Menus-v3-Typography-Icons-private-test.zip';archive.write_bytes(data)
 with zipfile.ZipFile(archive) as z:
  if z.testzip():raise ValueError('ZIP CRC failure')
 b.m.b.write_json(OUT/'receipt.json',dict(zip_path=str(archive),zip_sha256=b.m.b.audit.sha(data),bytes=len(data),parent_sha256=parent['zip_sha256'],resources=prepared['resources'],native=commands,icons=json.loads((OUT/'icons/receipt.json').read_text()),members={k:b.m.b.audit.sha(v) for k,v in members.items()},runtime_tested=False,live_unchanged=True,scripts_unchanged=True))
 print(archive,b.m.b.audit.sha(data),flush=True)

def report():
 receipt=json.loads((OUT/'receipt.json').read_text());proof=json.loads((OUT/'preview-evidence.json').read_text())
 log=(OUT/'tests.log').read_text(encoding='utf-8-sig');match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',log)
 if not match or not re.search(r'\bOK\s*$',log):raise ValueError('Successful targeted test log required')
 icon=receipt['icons'];source=b.REF/'mods/modInkAndIronIcons/content/texture.cache';data=source.read_bytes();chosen=set(icon['selected_keys']);fixed=set(icon['excluded_existing_fixes'])
 ledger=ROOT/'research/menus087-v3-item-textures.csv'
 with ledger.open('w',encoding='utf-8',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=['resource','decision','original_compressed_block_sha256','existing_mod_owner']);writer.writeheader()
  for row in b.m.b.inventory.cache_entries(source):
   key=row['resource'];writer.writerow(dict(resource=key,decision='include unchanged pixels' if key in chosen else ('retain existing fix' if key in fixed else 'exclude non-item artwork'),original_compressed_block_sha256=b.m.b.audit.sha(data[row['offset']:row['offset']+row['packed']]),existing_mod_owner='modbrothersinarms' if key in fixed else 'no active mod/DLC cache override found'))
 concise={k:v for k,v in receipt.items() if k!='icons'};concise['icons']={k:v for k,v in icon.items() if k!='selected_keys'}
 concise['resources']=[dict(resource=r['resource'],input_sha256=r['input_sha256'],output_sha256=r['output_sha256'],retained_v2_exact=r.get('retained_v2_exact',False),classes=[] if r.get('retained_v2_exact') else r.get('classes',[])) for r in receipt['resources']]
 concise.update(date='2026-10-17',release='Menus v3 — Typography and Icon Refinement',
  native_metadata_reconstructed=False,item_cache_index_reconstructed=True,
  texture_ledger=ledger.name,texture_ledger_sha256=b.m.b.fallback.sha(ledger),
  typography=dict(small_cap_ratio=.8,tracking=.65,minimum_fit_ratio=.82,source_strings_changed=False,font_library_replaced=False,modified_movies=8,modified_classes=12,retained_v2_movies_exact=32),
  previews=proof,initial_installed_v2_check=json.loads((OUT/'installed-v2-check.json').read_text()),
  tests=dict(count=int(match[1]),elapsed_seconds=float(match[2]),passed=True,log_sha256=b.m.b.fallback.sha(OUT/'tests.log')),
  native_log_hashes={p.name:b.m.b.fallback.sha(p) for p in (OUT/'native-final').glob('*.log')},
  source_hashes={str(p.relative_to(ROOT)):b.m.b.fallback.sha(p) for p in [ROOT/'tools/refine-menu-typography.py',Path(__file__),ROOT/'tools/preview-menu-refinement.py',ROOT/'tools/verify-menu-visual-install.py',ROOT/'tests/test_menu_typography.py']})
 b.m.b.write_json(ROOT/'research/menus087-v3-typography-icons-manifest.json',concise)

def main():
 import subprocess
 if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('Wrong branch')
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','native','package','report'));a=ap.parse_args()
 if a.stage=='native':b.OUT=OUT;b.native_build()
 else:globals()[a.stage]()
if __name__=='__main__':main()
