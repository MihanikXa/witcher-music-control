"""Publish metadata only from the private audit; never publish source or assets."""
import collections
import csv
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/ink-and-iron-0.8-audit'
DEST=ROOT/'research/ink-and-iron-0.8-audit'
spec=importlib.util.spec_from_file_location('audit',ROOT/'tools/audit-ui.py')
audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)

def disposition(e):
    owner=e['module']; key=e['resource']; mods=sorted(set(o['module'] for o in e['owners'] if o['module']!='vanilla'))
    aliases=[s for s in e.get('movie',{}).get('strings',[]) if s in ('$TitleFont','$BodyFont')]
    dep='modInkAndIronFonts (Vanilla 0.8 aliases)' if aliases else ''
    if owner=='modInkAndIronHUD': return 'DEFER','5/6' if mods else '1/2',dep,'Preserve HUD and trials; whole module disabled'
    if owner=='modInkAndIronFonts' and key.endswith('fonts_en.redswf'): return 'PRESERVE_QUIETFOLIO','6',dep,'Required Body alias is absent from QuietFolio library'
    if owner=='modInkAndIronFonts' and key.endswith('fonts.xml'): return 'ENABLE_WITH_QUIETFOLIO','3','modQuietFolioEnglish supplies accepted English library','0.8 Vanilla package is alias-only; Title/Body point to existing PF Din Text Cond Pro family'
    if owner=='Fonts_IM_Fell_archive': return 'DEFER_ALTERNATIVE','5' if mods else '2',dep,'Alternative only; do not replace accepted Gentium'
    if owner=='modInkAndIronFonts': return 'DEFER','2',dep,'English-only bridge does not need RU/UA replacements'
    if owner=='modInkAndIronUI' and mods: return 'PRESERVE_EXISTING_OWNER','6',dep,'Retain movie; common/map script adapters required before UI test'
    if owner=='modInkAndIronButtons' and mods: return 'PRESERVE_OUTFIT_WHEEL','5',dep,'Buttons HUD lacks Outfit Wheel runtime exports'
    if owner in ('modInkAndIronGlossary','modInkAndIronIcons') and mods: return 'PRESERVE_BIA','4',dep,'Presentation overlap; retain corrected BIA art at these keys'
    if owner=='modInkAndIronMap_Inked': return 'DEFER_OPTIONAL','1/2',dep,'Tile-only pack; no detected Smooth Map resource collision'
    if owner=='configuration': return 'CONFIGURATION_GATE','3','Mods page localization from HUD','Do not enable HUD to obtain two labels; independent labels bridge or leave defaults'
    if owner=='modInkAndIronUI': return 'CANDIDATE_AFTER_ADAPTER','1/2/3',dep,'Retain author design; exact compilation/runtime validation pending'
    return 'CANDIDATE','3' if dep else '1/2',dep,'No detected functionality owner collision; runtime test required'

def main():
    a=json.loads((BASE/'audit.json').read_text(encoding='utf-8')); DEST.mkdir(exist_ok=True)
    chosen=[e['resource'] for e in a['resources'] if e['module']=='modInkAndIronFonts']
    en=ET.parse(BASE/'payloads/modInkAndIronFonts/gameplay/gui_new/fonts.xml').getroot().find("lang[@name='EN']")
    if chosen!=['gameplay/gui_new/fonts.xml'] or en is None or any(en.find(k).get('font')!='PF Din Text Cond Pro' for k in ('NormalFont','BoldFont','ItalicFont','TitleFont','BodyFont')):
        raise ValueError('Decisions require the canonical 0.8 alias-only Vanilla Fonts configuration; re-audit changed inputs')
    quiet=BASE/'live/modQuietFolioEnglish-fonts_en.redswf'
    definitions=audit.inspect(quiet)['fonts']
    if not all(any(f['name']=='PF Din Text Cond Pro' and f['flags']&3==flag and f['glyphs'] for f in definitions) for flag in (0,1,2)):
        raise ValueError('Accepted English library does not satisfy the alias-family/weight contract')
    resources=[e for e in a['resources'] if e['module']!='Fonts_Vanilla_archive']
    with (DEST/'resources.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['module','resource','kind','bytes','sha256','stored_sha256','cache_key_hash','existing_mod_owners','existing_owner_hashes','vanilla_present','existing_priority','classification','decision','category','dependencies','reason']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for e in sorted(resources,key=lambda e:(e['module'],e['resource'])):
            d,c,dep,reason=disposition(e); owners={o['module']:o for o in e['owners'] if o['module']!='vanilla'}
            category=c if c not in ('1/2','1/2/3') else ('3+' if dep else '')+('2' if any(o['module']=='vanilla' for o in e['owners']) else '1')
            w.writerow(dict(module=e['module'],resource=e['resource'],kind=e['kind'],bytes=e.get('size',''),sha256=e.get('sha256',''),stored_sha256=e.get('stored_sha256',''),cache_key_hash=e.get('key_hash',''),existing_mod_owners=';'.join(sorted(owners)),existing_owner_hashes=';'.join(n+':'+o.get('sha256',o.get('stored_sha256','')) for n,o in sorted(owners.items())),vanilla_present=any(o['module']=='vanilla' for o in e['owners']),existing_priority=';'.join(n+':'+str(o.get('order',{}).get('priority') if o.get('order') else 'unknown') for n,o in sorted(owners.items())),classification=e['classification'],decision=d,category=category,dependencies=dep,reason=reason))
    files=[e for e in a['files'] if e['module'] not in ('Fonts_Vanilla_archive','Fonts_IM_Fell_archive') and e['path']!='README.md']
    (DEST/'input-files.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8')
    annotations=[]
    for e in a['annotations']:
        annotations.append(dict(module=e['owner'],path=Path(e['path']).relative_to(Path(a['reference_root'])).as_posix(),annotation=e['annotation'],target=e['class_name']+'.'+e['member'],existing=[dict(module=x['owner'],annotation=x['annotation'],path=Path(x['path']).relative_to(Path(a['game'])).as_posix()) for x in e['existing']]))
    (DEST/'annotations.json').write_text(json.dumps(annotations,indent=2)+'\n',encoding='utf-8')
    live=[]
    for p in sorted((BASE/'live').glob('*.redswf')):
        x=audit.inspect(p)
        live.append(dict(input=p.name,sha256=x['sha256'],fonts=[{k:v for k,v in f.items() if k not in ('codes',)} for f in x['fonts']]))
    font_refs=[]
    for e in resources:
        if e.get('movie'):
            aliases=[s for s in e['movie']['strings'] if s in ('$TitleFont','$BodyFont')]
            if aliases: font_refs.append(dict(module=e['module'],resource=e['resource'],aliases=aliases))
    summary=dict(date='2026-10-11',reference_layout='reference/ink-and-iron-0.8/{mods,bin}',source_url='https://www.nexusmods.com/witcher3/mods/13111',extracted_files=len(files),resource_rows=len(resources),counts=dict(collections.Counter(e['module'] for e in resources)),mods_settings_sha256=a['mods_settings_sha256'],retained_order=a['order'],vanilla_fonts_archive=dict(name=Path(a['archive']['path']).name,sha256=a['archive']['sha256']),font_alias_consumers=font_refs,live_inputs=live,limits=[dict(path=Path(x['path']).relative_to(Path(a['game'])).as_posix(),error=x['error']) for x in a['errors']])
    summary['all_in_one_archive']=a.get('all_in_one_archive')
    summary['provenance']=a.get('provenance')
    summary['alternative_font_input_files']=[e for e in a['files'] if e['module']=='Fonts_IM_Fell_archive']
    summary['canonical_resource_rows']=sum(e['module']!='Fonts_IM_Fell_archive' for e in resources)
    summary['retained_merge_inputs']=a.get('controls',[])
    summary['deployment_manifest_hashes']=[dict(file=Path(x['path']).name,sha256=x['sha256'],deploymentTime=x['deploymentTime']) for x in a['deployment_manifests']]
    (DEST/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(files),resources=len(resources),annotations=len(annotations),output=str(DEST)),indent=2))

if __name__=='__main__': main()
