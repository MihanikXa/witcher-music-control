"""Read-only Gate 0 receipt for the approved list composition. Never cooks/deploys."""
import configparser, hashlib, importlib.util, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/inventory-approved-gate1'
REFERENCE=ROOT/'reference/inventory-design/approved-inventory-reference.png'
SPEC_SHA='9e7d6bdb0bad0d28b5bacfc02e8433dac177b34690303acee8af6cd03b235ac9'
# Human explicitly authorized this local copy in the current task after mismatch.
AUTHORIZED_SHA='b1443ffafc009a5f123d6c971e3ea1e47572763b229595ab78d76799bde87313'
V4_SHA='a64643afb2bbb5308ecbcfefab14321c530fef978099360f7fc64d8fae57d66a'
EXPORT=ROOT/'build/adaptive-inventory-v2-p1/before'
KEY='gameplay/gui_new/swf/inventory/panel_inventory.redswf'
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def one(name):
    files=list((EXPORT/'scripts').rglob(name+'.as'))
    if len(files)!=1:raise ValueError('Unresolved class '+name)
    return files[0]
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    m=load('build-menus-087');api=m.m.b;game=m.m.v.GAME
    base=ROOT/'build/menus087-v4-final/prepared-inputs'/KEY
    if sha(base)!=V4_SHA or m.m.r.p.movie(base.read_bytes())[1]!=(EXPORT/'source.gfx').read_bytes():raise ValueError('Not exact accepted v4 export')
    import struct
    if not REFERENCE.exists():raise ValueError('Missing approved reference; no substitute')
    refsha=sha(REFERENCE);size=struct.unpack('>II',REFERENCE.read_bytes()[16:24])
    if refsha not in (SPEC_SHA,AUTHORIZED_SHA) or size!=(1672,941):raise ValueError('Unapproved image identity/dimensions')
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(api.settings_text(m.m.v.SETTINGS))
    owners=api.owners(game,cfg,{KEY,'gameplay/gui_new/swf/common/panel_common.redswf'},OUT)
    winners={k:min([r for r in rows if r['enabled']=='1'],key=lambda r:int(r['priority'] or 999999)) for k,rows in owners.items()}
    assembly=json.loads((ROOT/'build/ink-hud-v3-final/scripts/receipt.json').read_text(encoding='utf-8'))
    for row in assembly['current_required_inputs']:
        if sha(Path(row['path']))!=row['sha256']:raise ValueError('Current script provider changed '+row['path'])
    classes={n:dict(path=str(one(n)),sha256=sha(one(n))) for n in ('MenuInventory','InventoryTabbedListModule','SlotsListGrid','SlotInventoryGrid','SlotBase','ItemDataStub','TooltipInventory','ContextInfoManager','ModulePaperdoll','CharacterRendererController','IconItemRenderer')}
    slot=one('SlotBase').read_text(encoding='utf-8-sig');grid=one('SlotInventoryGrid').read_text(encoding='utf-8-sig')
    marker=re.search(r'if\(\(flags & 4\) != 0\)(.*?)\n         }',slot,re.S)
    if not marker or 'g.beginFill(11832388,0.9)' not in marker[1] or 'f |= 4;' not in grid:raise ValueError('Equipped mark changed')
    report=dict(reference=dict(path=str(REFERENCE),sha256=refsha,specification_sha256=SPEC_SHA,dimensions=size,authorization='User: Use the current local image; hash mismatch explicitly approved in this task'),baseline=dict(resource=KEY,sha256=V4_SHA,export_verified_exact=True),owners=owners,winners=winners,classes=classes,marker=dict(owner='SlotBase.iaiDrawLess, flags & 4',state='SlotInventoryGrid.iaiFlags: _data.isEquipped',color=11832388,hex='#'+format(11832388,'06X'),alpha=.9,vertices=[[3,3],[12,3],[3,12],[3,3]],scale='k cancels concatenated X scale; 9 logical-unit legs, 3-unit inset',old_equipedIcon='alpha 0; not the accepted corner mark'),frozen=load('build-inventory-p2').freeze(),runtime_verified=False,native_build_run=False)
    report['current_script_provider_pins_verified']=len(assembly['current_required_inputs'])
    previous=OUT/'source-receipt.json'
    if previous.exists() and json.loads(previous.read_text(encoding='utf-8'))['frozen']!=report['frozen']:raise ValueError('Protected inputs changed since initial Gate 0 snapshot')
    (OUT/'source-receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(reference=refsha,dimensions=size,winners={k:dict(owner=v['owner'],priority=v['priority'],sha256=v['sha256']) for k,v in winners.items()},marker=report['marker']),indent=2))
if __name__=='__main__':main()
