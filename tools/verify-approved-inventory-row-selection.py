"""Execute authored row paint with a graphics recorder, not the Flash renderer."""
import hashlib, importlib.util, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def checks():
    spec=importlib.util.spec_from_file_location('verify',ROOT/'tools/verify-approved-inventory.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    source=(ROOT/'src/inventory/unified/Row.asinc').read_text()
    args,body=v.method(source,'aiPaintRow')
    args,body=re.sub(r':\s*(?:Graphics|Rectangle)\b','',v.erase(args+'@@'+body)).split('@@')
    # Exact r5 expression: passive selected rows were identical to unselected.
    old=body.replace('sel ? 0xCAA469 : 0x565650,sel ? (active ? 1 : 0.8) : 0.45',
                     'active ? 0xCAA469 : 0x565650,active ? 1 : 0.45')
    old=old.replace('sel ? 0x30291E : 0x111112,sel ? (active ? 0.32 : 0.24) : 0.12',
                    'active ? 0x30291E : 0x111112,active ? 0.32 : 0.12')
    assert old!=body
    js='const assert=require("node:assert/strict");\n'
    js+='const fixed=function('+args+'){with(this){'+body+'}};\n'
    js+='const prior=function('+args+'){with(this){'+old+'}};\n'
    js+='''
function paint(fn,selected,active,flags=0){let calls=[];let g=new Proxy({},{get:(o,n)=>(...args)=>calls.push([n,...args])});
fn.call({selected,activeSelectionEnabled:active},g,{},1,false,flags);return calls;}
const unselected=paint(fixed,false,false), passive=paint(fixed,true,false), active=paint(fixed,true,true);
assert.deepEqual(paint(prior,true,false),paint(prior,false,false));
assert.notDeepEqual(passive,unselected);assert.notDeepEqual(active,passive);
assert.equal(passive[0][2],0xCAA469);assert.equal(passive[0][3],0.8);
assert.equal(active[0][2],0xCAA469);assert.equal(active[0][3],1);
assert.deepEqual(paint(fixed,false,true),unselected);
// Moving selection has exactly one selected appearance; no retained old highlight.
let rows=[false,true,false].map(s=>paint(fixed,s,false));
assert.equal(rows.filter(x=>JSON.stringify(x)===JSON.stringify(passive)).length,1);
rows=[false,false,true].map(s=>paint(fixed,s,false));
assert.deepEqual(rows[1],unselected);assert.deepEqual(rows[2],passive);
assert.deepEqual(paint(fixed,true,false,4).slice(-7),paint(prior,true,false,4).slice(-7));
console.log(JSON.stringify({r5_negative_control:true,selection_cases:6,native_engine_executed:false}));
'''
    out=ROOT/'build/approved-inventory-row-selection-tests';out.mkdir(exist_ok=True)
    script=out/'authored-row.js';script.write_text(js)
    result=subprocess.run(['node',str(script)],capture_output=True,text=True)
    if result.returncode:raise AssertionError(result.stdout+result.stderr)
    report=json.loads(result.stdout)
    report['row_source_sha256']=hashlib.sha256(source.encode()).hexdigest()
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(checks(),indent=2))
