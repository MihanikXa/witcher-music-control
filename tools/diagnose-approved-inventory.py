"""Read-only evidence and authored-method regression; no game execution/deployment."""
import argparse,configparser,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/approved-inventory-runtime-diagnosis'
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regression():
    v=load('verify-approved-inventory');gate=load('inspect-approved-inventory')
    released=ROOT/'build/approved-inventory-unified-p1/abc-09/after/scripts'
    negative=next(released.rglob('MenuInventory.as')).read_text(encoding='utf-8-sig')
    fixed=(ROOT/'src/inventory/unified/Scene.asinc').read_text()
    tab=next((gate.EXPORT/'scripts').rglob('TabListItem.as')).read_text(encoding='utf-8-sig')
    _,update=v.method(tab,'updateAfterStateChange')
    def erase(t):
        return re.sub(r':\s*(?:Class|MovieClip|Rectangle|SlotPaperdoll|BitmapData|Matrix|Bitmap)\b','',v.erase(t))
    js="""const assert=require('node:assert/strict');
var liveStage={dispatchEvent(e){events.push(e);}},events=[];
function Event(n){this.name=n;} const W3ScrollingList={REPOSITION:'reposition'};
class Tab {
 constructor(){this.stage=null;this.mcIcon={x:0,y:0,gotoAndStop(){}};this.data=null;this.invalid=true;}
 setData(d){this.data=d;} validateNow(){if(this.invalid)this.updateAfterStateChange();}
}
Tab.prototype.updateAfterStateChange=function(){with(this){UPDATE}};
function getDefinitionByName(){return Tab;}
const InventorySlotType={SteelSword:1,Armor:2,Potion1:3,Petard1:4,Quickslot1:5};
const mcPaperDollModule={mcPaperdoll:{getRendererForSlotType(){return null;}}};
var aiRail=Array.from({length:8},()=>({addChild(){}}));
var aiScene={addChild(o){o.stage=liveStage;}};
""".replace('UPDATE',update)
    # Do not emulate Flash rendering: exercise the exact dangerous call using
    # the authored rail method and the authored native state-update method.
    for name,text in [('negative',negative),('fixed',fixed)]:
        args,body=v.method(text,'aiConfigureRailIcons');js+='function '+name+'('+erase(args)+'){'+erase(body)+'}\n'
    js+='''
assert.throws(()=>negative(),e=>e instanceof TypeError && /dispatchEvent/.test(e.message));
assert.equal(events.length,0);
fixed();assert.equal(events.length,7);
console.log(JSON.stringify({negative_control:'released rail throws on null stage',correction:'attached native tabs dispatch successfully',native_dispatches:events.length,game_execution:false}));
'''
    OUT.mkdir(exist_ok=True);path=OUT/'rail-lifecycle-regression.js';path.write_text(js)
    result=subprocess.run(['node',str(path)],capture_output=True,text=True)
    if result.returncode:raise AssertionError(result.stdout+result.stderr)
    report=json.loads(result.stdout);report['native_method_sha256']=sha(next((gate.EXPORT/'scripts').rglob('TabListItem.as')))
    (OUT/'regression.json').write_text(json.dumps(report,indent=2));return report
def inspect():
    b=load('build-approved-inventory');api=b.b.b.m.b;env=b.b.b.m.v
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(api.settings_text(env.SETTINGS))
    OUT.mkdir(exist_ok=True)
    owners=api.owners(env.GAME,cfg,{b.KEY,'gameplay/gui_new/swf/common/panel_common.redswf'},OUT)
    script=env.GAME/'Mods/modApprovedInventoryUnifiedP1/content/scripts/local/approvedInventory.ws'
    manifest=json.loads((ROOT/'research/inventory-approved-unified-p1-manifest.json').read_text())
    duplicates=[]
    for path in (env.GAME/'Mods').rglob('*.ws'):
        # Only candidate namespace collisions; do not publish third-party source.
        text=path.read_text(encoding='utf-8-sig',errors='replace')
        if 'function AiApprovedEnable(' in text or 'function OnApprovedRefresh(' in text:duplicates.append(str(path))
    report=dict(owners=owners,script=dict(path=str(script),sha256=sha(script),release_exact=sha(script)==manifest['annotation_sha256']),candidate_namespace_files=duplicates,game_execution=False,compiled_runtime_annotation_state='not observable from source files or offline compiler receipts')
    (OUT/'installed.json').write_text(json.dumps(report,indent=2));return report
def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['regression','inspect']);a=ap.parse_args();print(json.dumps(globals()[a.stage](),indent=2))
if __name__=='__main__':main()
