"""Gate A: authored display ownership + executable P2 geometry, before cooking."""
import hashlib,importlib.util,json,re,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/adaptive-inventory-p2'
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load('build-adaptive-inventory');patch=load('patch-inventory-p2')
def geometry_js():
    text=(ROOT/'src/inventory/p2/Geometry.asinc').read_text();a,z=patch.p.trace.body_span(text,'protected function p2Geometry(')
    body=re.sub(r'var (\w+):\w+',r'var \1',text[a+1:z])
    return 'class Rectangle {constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}get right(){return this.x+this.width;}get bottom(){return this.y+this.height;}}\nfunction geometry(w,h,count){'+body+'}\n'
def fixtures():
    script=geometry_js()+'''const cases=[];for(const count of [6,24,80])for(const [pw,ph] of [[1649,928],[1920,1080],[3840,2160],[2560,1080]])for(const coordinatePolicy of ['authored-fit','viewport-aspect']){
      const h=1080,w=coordinatePolicy==='authored-fit'?1920:pw/ph*1080;const g=geometry(w,h,count);const occupied={};const items=[];
      for(let id=1;id<=count;id++){let size=count===6?2:(id%3===0?1:2),at=0;
        while(occupied[at]||(size===2&&occupied[at+g.cols]))at++;
        occupied[at]=id;if(size===2)occupied[at+g.cols]=id;
        items.push({id,size,index:at,x:g.gallery.x+(at%g.cols)*g.cell,y:g.gallery.y+Math.floor(at/g.cols)*g.cell,width:g.cell,height:size*g.cell});}
      cases.push({capture:[pw,ph],virtual:[w,h],coordinatePolicy,count,geometry:g,items,highestRow:Math.max(...items.map(i=>Math.floor(i.index/g.cols)+i.size)),fixture:'six equipment count observed; conservative two-cell footprints; dense synthetic identities'});
    }console.log(JSON.stringify(cases));'''
    return json.loads(subprocess.check_output(['node','-e',script],text=True))
def authored(path):
    root=ET.parse(path).getroot();tags=root.find('tags');result=[]
    for owner in [tags,*tags.findall('.//subTags')]:
        for x in owner:
            if x.get('type','').startswith('PlaceObject') and x.get('name'):
                matrix=x.find('matrix');result.append(dict(name=x.get('name'),character_id=x.get('characterId'),depth=x.get('depth'),matrix=matrix.attrib if matrix is not None else {}))
    return dict(stage=root.find('displayRect').attrib,placements=result)
def verify_cases(cases):
    for case in cases:
        g=case['geometry'];a=g['gallery'];s=g['summary'];n=g['nav'];p=g['preview']
        assert n['y']>=118 and n['y']+n['height']<=a['y']
        assert a['y']+a['height']<s['y']
        assert s['y']+s['height']<994
        assert a['x']+a['width']<p['x']
        assert s['x']+s['width']<p['x']
        assert len({i['id'] for i in case['items']})==case['count']
        if case['count']==6:assert case['highestRow']<=g['rows']
        # All dense items become reachable with the SAME native scroll page.
        max_offset=max(0,(case['highestRow']-g['rows'])*g['cell'])
        for item in case['items']:assert item['y']+item['height']-max_offset<=a['y']+a['height']+1e-6
def main():
    OUT.mkdir(exist_ok=True)
    source=(b.BASE/'prepared-inputs'/b.KEY).read_bytes();expected=next(r['output_sha256'] for r in json.loads((b.BASE/'receipt.json').read_text())['resources'] if r['resource']==b.KEY)
    assert hashlib.sha256(source).hexdigest()==expected
    assert b.b.m.r.p.movie(source)[1]==(ROOT/'build/adaptive-inventory-v2-p1/before/source.gfx').read_bytes()
    cases=fixtures();verify_cases(cases)
    report=dict(input_sha256=expected,inventory=authored(ROOT/'build/adaptive-inventory-v2-p1/v4.xml'),common=authored(ROOT/'build/adaptive-inventory-v2-p1/common-v4.xml'),geometry_cases=cases,runtime_bounds_observed=False,authored_geometry_only=True)
    b.write(OUT/'gate-a.json',report);print('Gate A: exact v4 export, authored ownership and 24 sparse/dense geometry cases pass (two coordinate policies; runtime UI scale pending).')
if __name__=='__main__':main()
