"""Read-only effective-owner gate; detects installed-but-shadowed menu movies.

Run after manually deploying v2, before starting the game. Does not reorder mods.
"""
import argparse, configparser, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('completion',ROOT/'tools/complete-menus-087.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)

def mismatches(expected, observed):
    return [dict(resource=k,expected=v,actual=observed.get(k)) for k,v in expected.items() if observed.get(k)!=v]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,default=ROOT/'build/menus087-v2/installed-verification.json');ap.add_argument('--release',type=Path,default=c.OUT/'receipt.json');a=ap.parse_args()
    release=json.loads(a.release.read_text());prepared=release.get('prepared') or {'resources':release['resources']};b=c.b
    cfg=configparser.ConfigParser();cfg.read_string(b.m.b.settings_text(b.m.v.SETTINGS))
    expected={r['resource']:r['output_sha256'] for r in prepared['resources']}
    owners=b.m.b.owners(b.m.v.GAME,cfg,set(expected),c.OUT);observed={};winners={}
    for key,rows in owners.items():
        active=[r for r in rows if r['enabled']=='1']
        if not active:continue
        winner=min(active,key=lambda r:int(r['priority'] or 999999));p=Path(winner['container'])
        data=b.m.b.read_bundle(p,next(e for e in b.m.b.audit.entries(p) if e['resource']==key),b.m.v.GAME,c.OUT) if p.suffix=='.bundle' else p.read_bytes()
        observed[key]=b.m.b.audit.sha(data);winners[key]=winner
    errors=mismatches(expected,observed)
    required_mods={name.split('/')[1] for name in release['members'] if name.startswith('Mods/')}
    for mod in sorted(required_mods):
        if mod not in cfg or cfg[mod].get('Enabled')!='1':errors.append(dict(disabled_or_missing=mod))
    if 'modbrothersinarms' in cfg and cfg['modbrothersinarms'].get('Enabled')=='1' and 'modInkAndIronGlossary' in cfg:
        if int(cfg['modbrothersinarms'].get('Priority','999999'))>=int(cfg['modInkAndIronGlossary'].get('Priority','999999')):
            errors.append(dict(texture_owner='Keep Brothers in Arms before Bestiary Art for bestiary_doppler.png'))
    # Check every deployed file, including additive XML and independent caches.
    for name,sha in release['members'].items():
        p=b.m.v.GAME/name;actual=b.m.b.fallback.sha(p) if p.exists() else None
        if actual!=sha:errors.append(dict(file=name,expected=sha,actual=actual))
    report=dict(passed=not errors,errors=errors,effective_winners=winners,runtime_rendering_verified=False)
    a.report.parent.mkdir(parents=True,exist_ok=True);b.m.b.write_json(a.report,report)
    print('PASS: all release files and effective movie hashes match; in-game visual checks still required.' if not errors else 'FAIL: installed files or effective resource winners differ. See '+str(a.report))
    for error in errors:
        if 'resource' in error:print(error['resource'],'winner:',winners.get(error['resource'],{}).get('owner','base game / absent'))
    raise SystemExit(bool(errors))
if __name__=='__main__':main()
