"""Coordinate independent regional fixture controls, retaining partial evidence."""
import argparse
import json
from pathlib import Path
from regional_selector_matrix import matrix
from white_orchard_prepare import build_path, digest


def run(project, controls, port, label, output):
    if Path(label).name!=label or not label:raise ValueError('Simple batch label required')
    rows=json.loads(controls.read_text())
    if (not rows or any(set(r)!={'label','manifest','plan'} for r in rows)
            or len({r['label'] for r in rows})!=len(rows)
            or any(not r['label'] or Path(r['label']).name!=r['label'] for r in rows)):
        raise ValueError('Explicit unique regional controls required')
    output=build_path(output)
    if output.exists():raise FileExistsError(output)
    result={'controls_sha256':digest(controls),'fixtures_only':True,'retail_validated':False,'results':[]}
    for row in rows:
        manifest=controls.parent/row['manifest'];plan=controls.parent/row['plan']
        try:
            evidence=matrix(project,manifest,plan,port,label+'-'+row['label'])
            result['results'].append({'label':row['label'],'passed':True,'evidence':evidence})
        except Exception as error:
            result['results'].append({'label':row['label'],'passed':False,'error':str(error)})
        output.write_text(json.dumps(result,indent=2)+'\n')
    result['passed']=all(r['passed'] for r in result['results'])
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('project','controls','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--port',type=int,required=True);p.add_argument('--label',required=True);a=p.parse_args()
    r=run(a.project,a.controls,a.port,a.label,a.output)
    print(json.dumps({'passed':r['passed'],'controls':len(r['results'])}))
    if not r['passed']:raise SystemExit(1)
