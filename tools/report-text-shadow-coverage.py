"""Produce original coverage findings without publishing XML, strings or code."""
import argparse
import collections
import json
from pathlib import Path


def disposition(movie):
    key=movie['resource_key']
    if movie['status']=='blocked':return 'blocked_static_decode'
    if key.endswith('/hud_enemyfocus.redswf'):return 'accepted_npc_preserve'
    if key.endswith('/fonts_en.redswf'):return 'accepted_font_library_preserve'
    if key.endswith('/hud_interactions.redswf'):return 'wave_a_source_verified_manual_import_required'
    if key=='gameplay/gui_new/swf/hud/hud_subtitles.redswf':return 'wave_a_source_verified_manual_import_required'
    if key=='gameplay/gui_new/swf/witcher3/hud_subtitles.redswf':return 'legacy_route_deferred_not_current_root_module'
    if any(key.endswith('/'+x+'.redswf') for x in ('hud_dialog','hud_quests','hud_oneliners')):return 'wave_b_deferred_until_wave_a_acceptance'
    return 'wave_c_semantics_and_renderer_review_required'


def compact(movie):
    result={k:movie[k] for k in ('resource_key','selected_owner','selection_confidence','input_sha256','error') if k in movie}
    result['owners']=[{k:e[k] for k in ('owner','bundle','loose','codec','size','configuration') if k in e} for e in movie['owners']]
    result['disposition']=disposition(movie);result['runtime_verified']=False
    result['base_version_checks']=movie.get('base_version_checks',[])
    placements={};fields=[]
    def remember(p):
        if 'unresolved' in p:return p
        key=f"{p['sprite']}:{p['ordinal']}"
        placements[key]=p;return key
    for row in movie.get('fields',[]):
        attrs=row['text_definition']
        fields.append(dict(character=row['character'],definition={k:attrs[k] for k in
            ('type','fontHeight','fontId','fontClass','align','leading','multiline','wordWrap','autoSize','useOutlines') if k in attrs},
            placement=remember(row['placement']) if row['placement'] else None,
            ancestor_chains=[[remember(p) for p in chain] for chain in row['ancestor_chains']],
            classification=row['classification'],runtime_override_verified=False))
    result.update(text_definition_count=movie.get('text_definition_count',0),fields=fields,placements=placements,
                  classifications=dict(collections.Counter(r['classification'] for r in fields)))
    return result


def research_json(report):
    """One field/placement per line: compact evidence, reviewable future diffs."""
    lines=['{']
    for key,value in report.items():
        if key!='movies':lines.append('  '+json.dumps(key)+': '+json.dumps(value)+',')
    lines.append('  "movies": [')
    for i,movie in enumerate(report['movies']):
        lines.append('    {')
        for key,value in movie.items():
            if key not in ('fields','placements'):lines.append('      '+json.dumps(key)+': '+json.dumps(value)+',')
        lines.append('      "fields": [')
        for j,row in enumerate(movie['fields']):lines.append('        '+json.dumps(row)+(',' if j+1<len(movie['fields']) else ''))
        lines.append('      ],')
        lines.append('      "placements": {')
        for j,(key,row) in enumerate(movie['placements'].items()):
            lines.append('        '+json.dumps(key)+': '+json.dumps(row)+(',' if j+1<len(movie['placements']) else ''))
        lines.append('      }');lines.append('    }'+(',' if i+1<len(report['movies']) else ''))
    lines.extend(['  ]','}']);text='\n'.join(lines)+'\n'
    if json.loads(text)!=report:raise ValueError('Research serialization changed evidence')
    return text


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audit',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    raw=json.loads(a.audit.read_text(encoding='utf-8'));movies=[compact(m) for m in raw['movies']]
    report=dict(date='2026-10-11',scope=raw['scope'],movies=movies,
        mods_settings_sha256=raw.get('mods_settings_sha256'),
        runtime_style_setters=raw.get('runtime_style_setters',[]),excluded_nonenglish_fonts=raw['excluded_nonenglish_fonts'],
        live_files_modified=False,computer_use=False,
        limitations=['Available installed resources are not proof every movie is currently visible.',
            'Deployed mod candidates are inventoried; unresolved competing owners have no guessed winner.',
            'Authored timeline depth tracking and capped parent chains do not prove native/runtime instantiation.',
            'Filter strength flags candidates for review; it does not certify a semantic highlight should change.',
            'Native AS/installed WS scan is not exhaustive embedded ABC or runtime override tracing.',
            'All non-Wave-A surfaces remain unmodified; no universal shadow-completion claim.'])
    a.out.with_suffix('.json').write_text(research_json(report),encoding='utf-8')
    lines=['# Installed text-shadow coverage ledger — 11 October 2026','',
        'Read-only source catalogue, not a claim of complete runtime coverage. The companion',
        'JSON records every decoded text placement, authored parent chain and filter parameters;',
        'it contains no extracted movie, gameplay prose, glyph outlines or script body.',
        '',f"Audited {len(movies)} owner/movie records; {sum(m['disposition']=='blocked_static_decode' for m in movies)} static decode blockers.",
        '', 'Black-effect classifications are review candidates, not automatic patch permission.',
        'White/color effects, selection, focus and non-text art remain untouched.', '',
        '| Resource under gameplay/gui_new/swf/ | Deployed owner candidate | Text definitions | Strong-black text placements/states | Disposition |',
        '|---|---|---:|---:|---|']
    for m in movies:
        strong=sum(v for k,v in m['classifications'].items() if k.startswith('strong_black'))
        lines.append(f"| `{m['resource_key'].removeprefix('gameplay/gui_new/swf/')}` | {m['selected_owner']} | {m['text_definition_count']} | {strong} | {m['disposition']} |")
    lines+=['','## Blockers and limitations','']+[f'- {x}' for x in report['limitations']]
    for m in movies:
        if 'error' in m:lines.append(f"- `{m['resource_key']}`: {m['error']}")
    lines+=['','No package for these new waves is released before saved Editor output and current',
            'official cook/validation/bundle/re-extraction gates pass. Accepted NPC, color,',
            'Gentium and archived interaction v1 packages remain unchanged.']
    a.out.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':main()
