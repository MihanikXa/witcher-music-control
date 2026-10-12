"""Private v2 successor, bounded visual refinements and component rollback.

Requires the validated v1 receipt, canonical assets and current deployed v1.
No deployment, Script Merger regeneration or installed-resource writes.
Run with a Python environment containing Pillow (bundled desktop runtime).
"""
import argparse
import configparser
import json
from pathlib import Path
import re
import shutil
import subprocess
import struct

import importlib.util

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


r=load('refine-ink-hud-movies');b=r.b
PARENT=ROOT/'build/ink-hud-batch-private-v1-final'
GROUPS={'enemy','glyphs','shadows','dialogue','quickslots'}
GAME=Path('C:/Program Files (x86)/Steam/steamapps/common/The Witcher 3')
SETTINGS=Path('C:/Users/micha/OneDrive - hull.ac.uk/Documents/The Witcher 3/mods.settings')
RETAIL_PINS={'hud_oneliners':'410ece977ba843c547676bf76098ee924a6021d1fed416dab4435c35b6bda797',
             'hud_iteminfo':'a83eaafda5dc2f6b33b3d69c34962922bceef6b44f01650aa9afd5475cf77f00'}


def retail(key,out):
    # A full installed bundle lookup on 12 October established these exact 5.01
    # owners. Read the current container on every build; reject any changed key.
    path=GAME/'content/content0/bundles/startup.bundle'
    entry=next(e for e in b.audit.entries(path) if e['resource']==key)
    data=b.read_bundle(path,entry,GAME,out)
    if b.audit.sha(data)!=RETAIL_PINS[Path(key).stem]:raise ValueError('Pinned installed 5.01 retail input changed')
    return data,dict(owner='retail',container=str(path),sha256=b.audit.sha(data))


def contract(source,candidate,before=None,after=None):
    a,btag=b.audit.swf_tags(source)[2],b.audit.swf_tags(candidate)[2]
    if b.contracts.symbols(a)!=b.contracts.symbols(btag):raise ValueError('SymbolClass IDs changed')
    abc_before=[v for c,v in a if c==82];abc_after=[v for c,v in btag if c==82]
    result=dict(symbols=b.contracts.symbols(a),abc_unchanged=abc_before==abc_after)
    if before:
        result.update(b.class_contracts(before/'scripts',after/'scripts'))
        root=next(k.split('.')[-1] for k,v in result['symbols'].items() if v==0)
        original=b.public_chain(before/'scripts',root);modified=b.public_chain(after/'scripts',root)
        if any(modified.get(k)!=v for k,v in original.items()):raise ValueError('Public exports changed')
        pattern=r'[^\n]*(?:addEventListener|removeEventListener|registerDataCallback|registerDataBinding|handleInput|dispatchEvent)[^\n]*'
        def listeners(folder):
            return {p.relative_to(folder).as_posix():sorted(re.sub(r'\s+','',s) for s in re.findall(pattern,p.read_text(encoding='utf-8-sig'))) for p in folder.rglob('*.as') if re.search(pattern,p.read_text(encoding='utf-8-sig'))}
        if listeners(before/'scripts')!=listeners(after/'scripts'):raise ValueError('Event/controller/data sites differ')
        result.update(public_signatures=original,listener_controller_data_sites_unchanged=True)
    elif abc_before!=abc_after:raise ValueError('Unexpected ABC change')
    old,new=b.font.native.chunks(source),b.font.native.chunks(candidate)
    atlas_added=len(new)==len(old)+1
    original_props=[dict(c['properties']) for c in old];new_props=[dict(c['properties']) for c in new[:len(old)]]
    if atlas_added:
        original_props[0].pop('textures');new_props[0].pop('textures')
        if [c['tail'] for c in old[1:]]!=[c['tail'] for c in new[1:-1]]:raise ValueError('Original atlas pixels changed')
    if original_props!=new_props or not all(c['crc_valid'] for c in old+new):raise ValueError('Properties or CRC contract changed')
    if r.p.header_crc(candidate)!=struct.unpack_from('<I',candidate,32)[0]:raise ValueError('Header CRC invalid')
    if [(c,v) for c,v in a if c in (48,75,57,71)]!=[(c,v) for c,v in btag if c in (48,75,57,71)]:raise ValueError('Font definitions/imports changed')
    result.update(input_sha256=b.audit.sha(source),output_sha256=b.audit.sha(candidate),atlas=atlas_contract(candidate),existing_properties_unchanged=True,new_private_atlas=atlas_added,all_original_texture_chunks_unchanged=atlas_added,chunk_header_crcs_valid=True,fonts_imports_unchanged=True)
    return result


def atlas_contract(data):
    chunks=b.font.native.chunks(data)
    if len(chunks)==1 and 'textures' not in chunks[0]['properties']:
        if any(c in (1008,1009) for c,v in b.audit.swf_tags(data)[2]):raise ValueError('Images without native texture handles')
        return dict(textures=[],image_links=0,rectangles=0,no_embedded_textures=True)
    return b.atlas_contract(data)


def build(a):
    out,deploy=a.out.resolve(),a.deploy.resolve()
    b.font.private_path(out)
    if ROOT/'deploy' not in deploy.parents or out.exists() or deploy.exists():raise ValueError('Fresh ignored build/deploy directories required')
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul required')
    rollback=set(a.rollback)
    if rollback-GROUPS:raise ValueError('Unknown rollback group')
    parent=json.loads((PARENT/'receipt.json').read_text())
    if not parent['official_cook_validated'] or not parent['exact_reextraction']:raise ValueError('Verified v1 parent required')
    if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('Accepted v1 archive changed')
    for path,digest in parent['reference_pins'].items():
        if b.fallback.sha(Path(path))!=digest:raise ValueError('Canonical reference changed')
    out.mkdir();state=b.bars.snapshot(GAME,SETTINGS);b.write_json(out/'live-before.json',state)
    cfg=configparser.ConfigParser(interpolation=None);cfg.read_string(b.settings_text(SETTINGS))
    keys=set(parent['resource_hashes'])|{b.PREFIX+'hud.redswf',b.PREFIX+'hud_subtitles.redswf',b.PREFIX+'hud_oneliners.redswf',
          'gameplay/gui_new/swf/common/panel_common.redswf','gameplay/gui_new/swf/overlay/panel_overlay.redswf'}
    owners=b.owners(GAME,cfg,keys,out);b.write_json(out/'owners.json',owners)
    sources={};provenance={}
    cached=None
    if a.reuse:
        b.font.private_path(a.reuse.resolve())
        cached=json.loads((a.reuse/'receipt.json').read_text())
        if not cached.get('official_cook_validated') or not cached.get('exact_reextraction') or not cached.get('source_cache_sha256'):raise ValueError('Verified refinement source cache required')
        if b.fallback.sha(Path(cached['zip_path']))!=cached['zip_sha256']:raise ValueError('Verified refinement ZIP changed')
    for key,digest in parent['resource_hashes'].items():
        data=(PARENT/'pack-input'/key).read_bytes()
        if b.audit.sha(data)!=digest:raise ValueError('v1 cooked source changed')
        sources[key]=data;provenance[key]=dict(owner='accepted-v1',sha256=digest)
        # All selected v1 movies must still be the actual deployed winners.
        active=sorted([o for o in owners[key] if o.get('enabled')=='1'],key=lambda o:int(o.get('priority') or 9999))
        if not cached and key.endswith('.redswf') and (not active or active[0]['sha256']!=digest):raise ValueError('Current winner differs from tested v1: '+key)
    for key in keys-set(sources):
        if cached:
            data=(a.reuse/'source-inputs'/key).read_bytes()
            if b.audit.sha(data)!=cached['source_cache_sha256'][key]:raise ValueError('Verified base resource cache changed')
            sources[key]=data;provenance[key]=cached['base_provenance'][key];continue
        active=sorted([o for o in owners[key] if o.get('enabled')=='1'],key=lambda o:int(o.get('priority') or 9999))
        if active:
            owner=active[0];path=Path(owner['container']);entry=next(e for e in b.audit.entries(path) if e['resource']==key)
        else:
            data,owner=retail(key,out);sources[key]=data;provenance[key]=owner;continue
        data=b.read_bundle(path,entry,GAME,out);sources[key]=data;provenance[key]={**owner,'sha256':b.audit.sha(data)}
    base_provenance=dict(provenance)
    for key,data in sources.items():
        target=out/'source-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    cache_hashes={k:b.audit.sha(v) for k,v in sources.items()}
    # Keep the already soft subtitle winner as its independent trial; no duplicate.
    subtitle=sources.pop(b.PREFIX+'hud_subtitles.redswf')
    subtitle_gfx=out/'subtitle.gfx';subtitle_gfx.write_bytes(r.p.movie(subtitle)[1]);b.export(subtitle_gfx,out/'subtitle-audit')
    # Restore actual pre-batch retail iteminfo, not the author's circle cluster.
    itemkey=b.PREFIX+'hud_iteminfo.redswf'
    if 'quickslots' not in rollback:
        sources[itemkey],provenance[itemkey]=retail(itemkey,out)
        provenance[itemkey]['owner']='pre-batch-retail'
    files={};reports={};changes={}
    for key,source in sorted(sources.items()):
        if not key.endswith('.redswf'):files[key]=source;continue
        stem=Path(key).stem;candidate=source;before=None;after=None
        if stem=='hud_enemyfocus' and 'enemy' not in rollback:
            before=out/'exports'/stem;before.mkdir(parents=True);gfx=before/'original.gfx';gfx.write_bytes(r.p.movie(source)[1]);b.export(gfx,before)
            candidate,edits=r.compile_classes(candidate,before,out/'abc'/stem,{'HudModuleEnemyFocus':r.enemy},a.compiled_cache/'abc'/stem if a.compiled_cache else None);changes.setdefault(key,{})['source_edits']=edits
        if stem=='hud_dialog' and ('dialogue' not in rollback or 'shadows' not in rollback):
            before=out/'exports'/stem;before.mkdir(parents=True);gfx=before/'original.gfx';gfx.write_bytes(r.p.movie(source)[1]);b.export(gfx,before)
            transforms={}
            if 'dialogue' not in rollback:transforms={'Option':r.option,'OptionContainer':r.option_container}
            elif 'shadows' not in rollback:
                def soft_option(t):
                    t=r.p.one(t,'new DropShadowFilter(2,90,0,0.95,5,5,1.6,2),new GlowFilter(0,0.55,10,10,1.3,2)',r.SOFT)
                    return r.p.one(t,'new DropShadowFilter(1,90,0,0.95,4,4,1.6,2)',r.SOFT)
                transforms={'Option':soft_option}
            if 'shadows' in rollback and 'dialogue' not in rollback:
                # Size-only rollback retains the tested v1 dynamic filters.
                def size_option(t):
                    result=r.option(t)
                    result=result.replace('this.tfLine.filters = ['+r.SOFT+'];','this.tfLine.filters = [new DropShadowFilter(2,90,0,0.95,5,5,1.6,2),new GlowFilter(0,0.55,10,10,1.3,2)];')
                    return result.replace('this.iaiMark.filters = ['+r.SOFT+'];','this.iaiMark.filters = [new DropShadowFilter(1,90,0,0.95,4,4,1.6,2)];')
                transforms['Option']=size_option
            candidate,edits=r.compile_classes(candidate,before,out/'abc'/stem,transforms,a.compiled_cache/'abc'/stem if a.compiled_cache else None);changes.setdefault(key,{})['source_edits']=edits
        if 'shadows' not in rollback and stem in ('hud_dialog','hud_oneliners'):
            names={'tfLine','tfSubtitles','tfPreviousSubtitles'} if stem=='hud_dialog' else {'textField'}
            candidate,edits=r.soften_authored(candidate,out/'shadow'/stem,names);changes.setdefault(key,{})['authored_shadow_edits']=edits
        if stem=='hud_oneliners' and ('shadows' in rollback or candidate==source):continue
        if 'glyphs' not in rollback and stem!='hud_bossfocus':
            candidate,edits=r.flat_glyphs(candidate,out/'glyphs'/stem,a.glyph_font);changes.setdefault(key,{})['glyphs']=edits
        # Extra shared roots only ship when their bitmap pixels changed.
        if stem in ('hud','panel_common','panel_overlay') and candidate==source:continue
        # Restored iteminfo is omitted if it needs no controller art replacement.
        if stem=='hud_iteminfo' and 'quickslots' not in rollback and candidate==source:continue
        if before:
            after=out/'reexport'/stem;gfx=out/'abc'/stem/'final.gfx';gfx.write_bytes(r.p.movie(candidate)[1]);b.export(gfx,after)
        reports[key]=contract(source,candidate,before,after);files[key]=candidate
        print('Refinement',stem,'passed',flush=True)
    # The selected bars and boss resource stay byte-identical to accepted v1.
    boss=b.PREFIX+'hud_bossfocus.redswf'
    if files[boss]!=sources[boss]:raise ValueError('Boss movie changed')
    for key,data in files.items():
        target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    b.write_json(out/'prepared-contracts.json',dict(resource_hashes={k:b.audit.sha(v) for k,v in files.items()},
        movie_contracts=reports,changes=changes,provenance=provenance,owners=owners,
        source_cache_sha256=cache_hashes,base_provenance=base_provenance,
        refiner_sha256=b.fallback.sha(ROOT/'tools/refine-ink-hud-movies.py'),rollback_groups=sorted(rollback)))
    selected=set(parent['selected'])
    if 'quickslots' not in rollback:selected.remove('iteminfo')
    private_hud=out/'support';(private_hud/'scripts/local').mkdir(parents=True)
    for name in ('texture.cache','en.w3strings'):shutil.copy2(b.HUD/name,private_hud/name)
    for stem in b.selected_scripts(selected):
        text=b.fallback.text(b.HUD/'scripts/local'/(stem+'.ws'))
        if stem=='inkIronNpcPlate' and 'quickslots' not in rollback:
            marker='// ---- Option "Show quick slot key hints"'
            if text.count(marker)!=1:raise ValueError('Nonunique scoped key-hint annotation section')
            text=text.split(marker)[0]
        (private_hud/'scripts/local'/(stem+'.ws')).write_text(text,encoding='utf-8',newline='\n')
    b.HUD=private_hud
    if 'quickslots' not in rollback:b.HUD_OPTIONS.remove('iiShowQuickSlotKeys')
    if a.script_cache:
        cache=a.script_cache.resolve();b.font.private_path(cache)
        script=json.loads((cache/'receipt.json').read_text())
        if len(script['results'])!=3 or not all(s['success'] for s in script['results']):raise ValueError('Completed compiler controls required')
        if script['results'][1]['assertions']!=script['results'][2]['assertions'] or script['results'][1]['warnings']!=script['results'][2]['warnings']:raise ValueError('Compiler cache control diagnostics differ')
        for entry in script['assembly_inputs']+script['current_required_inputs']:
            if b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Cached script provider changed')
        for label in ('baseline','noop','candidate'):
            row=next(s for s in script['results'] if s['label']==label)
            if b.fallback.sha(cache/label/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Cached compiler output changed')
        for stem in b.selected_scripts(selected):
            if b.fallback.text(cache/'patch/local'/(stem+'.ws'))!=b.fallback.text(private_hud/'scripts/local'/(stem+'.ws')):raise ValueError('Candidate annotation differs from compiler cache')
        if b.fallback.text(cache/'patch/local/inkIronHUDStateBridge.ws')!=b.fallback.text(ROOT/'src/hud/inkIronHUDStateBridge.ws'):raise ValueError('Candidate bridge differs from compiler cache')
        shutil.copytree(cache,out/'scripts');script['verified_compile_cache']=str(cache)
    else:script=b.compiler(a.assembly,GAME,cfg,out/'scripts',b.selected_scripts(selected))
    commands=[];runner=ROOT/'build/npc-state-expanded'
    native={k:v for k,v in files.items() if k.endswith('.redswf')}
    with b.mount(runner,out,native) as workspace:
        b.official(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
        log=b.official(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
        if 'Found '+str(len(native))+' files to validate' not in log or 'Errors found in 0 resources:' not in log:raise ValueError('Native validation inventory/error gate failed')
        for key,data in native.items():
            cooked=(out/'cooked'/key).read_bytes()
            if cooked!=data:raise ValueError('Cook changed movie/pixels '+key)
            atlas_contract(cooked)
    if b.bars.snapshot(GAME,SETTINGS)!=state:raise ValueError('Live inputs changed during build')
    manifest=dict(version='Ink & Iron HUD refinement private v2',parent_zip_sha256=parent['zip_sha256'],rollback_groups=sorted(rollback),
        owners=owners,provenance=provenance,changes=changes,movie_contracts=reports,reference_pins=parent['reference_pins'],
        script_regression=script['results'],opaque_mods_not_recompiled=script['opaque_mods_not_recompiled'],
        official_cook_validated=True,live_inputs_unchanged=True,boss_unchanged=True,bars_package_unchanged=True,
        palette={k:dict(before=f'#{v[0]:06X}',after=f'#{v[1]:06X}') for k,v in r.PALETTE.items()},
        dimensions=dict(health_fill=[6,3.8],health_total=[9,4.8],hostile_name=[21,19],name_bar_gap=[10,5],lock_radius=[19.5,13],level_plate=[[27,21],[20,16]],dialogue_option_effective=[26,21],choice_step=[40,36],choice_extra_line=[35,29],hit_minimum=35),
        health_fill_palette=dict(before='#8E1914',after='#AA7565',lag='#C3A18F'),source_cache_sha256=cache_hashes,base_provenance=base_provenance,
        subtitle_retained_sha256=b.audit.sha(subtitle),glyph_font=dict(path=str(a.glyph_font),sha256=b.fallback.sha(a.glyph_font)),
        refined_builder_sha256=b.fallback.sha(Path(__file__)),refiner_sha256=b.fallback.sha(ROOT/'tools/refine-ink-hud-movies.py'))
    b.MOD='modInkIronHUDRefinementV2'
    b.package(out,deploy,selected,files,manifest,runner,commands)
    old=deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip';new=deploy/'Ink-Iron-HUD-Refinement-v2-private-test.zip';old.rename(new)
    manifest['zip_path']=str(new);manifest['refined_builder_sha256']=b.fallback.sha(Path(__file__))
    b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest)
    if b.bars.snapshot(GAME,SETTINGS)!=state:raise ValueError('Live inputs changed during package checks')
    print('V2 ready',new,manifest['zip_sha256'],flush=True)



def finish_package(a):
    """Resume a completed cook/validate/pack after a failed metadata launch.

    Recheck prepared bytes, source/provider pins and successful native evidence;
    this does not manufacture receipts or substitute an unofficial metadata file.
    """
    out,deploy=a.out.resolve(),a.deploy.resolve()
    b.font.private_path(out)
    if ROOT/'deploy' not in deploy.parents or deploy.exists():raise ValueError('Fresh private deploy destination required')
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()!='ui-overhaul':raise ValueError('ui-overhaul required')
    prepared=json.loads((out/'prepared-contracts.json').read_text())
    parent=json.loads((PARENT/'receipt.json').read_text())
    script=json.loads((out/'scripts/receipt.json').read_text())
    state=json.loads((out/'live-before.json').read_text())
    if b.bars.snapshot(GAME,SETTINGS)!=state:raise ValueError('Live inputs changed since preparation')
    for path,digest in parent['reference_pins'].items():
        if b.fallback.sha(Path(path))!=digest:raise ValueError('Canonical input changed')
    if b.fallback.sha(Path(parent['zip_path']))!=parent['zip_sha256']:raise ValueError('V1 archive changed')
    for key,digest in prepared['source_cache_sha256'].items():
        if b.fallback.sha(out/'source-inputs'/key)!=digest:raise ValueError('Prepared base source changed')
    files={key:(out/'prepared-inputs'/key).read_bytes() for key in prepared['resource_hashes']}
    for key,data in files.items():
        if b.audit.sha(data)!=prepared['resource_hashes'][key]:raise ValueError('Prepared movie changed')
        if key.endswith('.redswf'):
            if (out/'cooked'/key).read_bytes()!=data:raise ValueError('Cooked movie differs')
            atlas_contract(data)
    for entry in script['assembly_inputs']+script['current_required_inputs']:
        if b.fallback.sha(Path(entry['path']))!=entry['sha256']:raise ValueError('Script provider changed')
    if len(script['results'])!=3 or not all(row['success'] for row in script['results']):raise ValueError('Completed script controls required')
    if any(script['results'][1][key]!=script['results'][2][key] for key in ('warnings','assertions')):raise ValueError('Script control diagnostics differ')
    for row in script['results']:
        if b.fallback.sha(out/'scripts'/row['label']/'blob.rsblob')!=row['blob_sha256']:raise ValueError('Compiler blob changed')
    rollback=set(prepared['rollback_groups']);selected=set(parent['selected'])
    if 'quickslots' not in rollback:selected.remove('iteminfo');b.HUD_OPTIONS.remove('iiShowQuickSlotKeys')
    b.HUD=out/'support'
    for stem in b.selected_scripts(selected):
        if b.fallback.text(out/'scripts/patch/local'/(stem+'.ws'))!=b.fallback.text(b.HUD/'scripts/local'/(stem+'.ws')):raise ValueError('Prepared annotation differs from script controls')
    if b.fallback.text(out/'scripts/patch/local/inkIronHUDStateBridge.ws')!=b.fallback.text(ROOT/'src/hud/inkIronHUDStateBridge.ws'):raise ValueError('Bridge changed')
    commands=json.loads((out/'commands.json').read_text());runner=ROOT/'build/npc-state-expanded'
    if not all(any(c['label']==label and c['exit_code']==0 for c in commands) for label in ('cook','validate','pack')):raise ValueError('Successful native controls required')
    validation=(out/'validate.full.log').read_text()
    native_count=sum(k.endswith('.redswf') for k in files)
    if 'Found '+str(native_count)+' files to validate' not in validation or 'Errors found in 0 resources:' not in validation:raise ValueError('Native validation gate missing')
    if not any(c['label']=='metadata' and c['exit_code']==0 for c in commands):
        with b.mount(runner,out,{}) as workspace:
            b.official(runner,out,'metadata',['metadatastore','-path='+str(out/'packed')],commands)
    manifest={k:prepared[k] for k in ('owners','provenance','changes','movie_contracts','source_cache_sha256','base_provenance','refiner_sha256','rollback_groups')}
    manifest.update(version='Ink & Iron HUD refinement private v2',parent_zip_sha256=parent['zip_sha256'],reference_pins=parent['reference_pins'],script_regression=script['results'],opaque_mods_not_recompiled=script['opaque_mods_not_recompiled'],official_cook_validated=True,live_inputs_unchanged=True,boss_unchanged=True,bars_package_unchanged=True,palette={k:dict(before=f'#{v[0]:06X}',after=f'#{v[1]:06X}') for k,v in r.PALETTE.items()},dimensions=dict(health_fill=[6,3.8],health_total=[9,4.8],hostile_name=[21,19],name_bar_gap=[10,5],lock_radius=[19.5,13],level_plate=[[27,21],[20,16]],dialogue_option_effective=[26,21],choice_step=[40,36],choice_extra_line=[35,29],hit_minimum=35),health_fill_palette=dict(before='#8E1914',after='#AA7565',lag='#C3A18F'),subtitle_retained_sha256=b.fallback.sha(out/'source-inputs'/(b.PREFIX+'hud_subtitles.redswf')),glyph_font=dict(path=str(a.glyph_font),sha256=b.fallback.sha(a.glyph_font)),refined_builder_sha256=b.fallback.sha(Path(__file__)),native_metadata_bounded_retry=True)
    b.MOD='modInkIronHUDRefinementV2'
    b.package(out,deploy,selected,files,manifest,runner,commands,verified_native_reuse=True)
    new=deploy/'Ink-Iron-HUD-Refinement-v2-private-test.zip';(deploy/'Ink-Iron-HUD-Batch-v1-private-test.zip').rename(new);manifest['zip_path']=str(new)
    b.write_json(out/'receipt.json',manifest);b.write_json(deploy/'manifest.json',manifest)
    if b.bars.snapshot(GAME,SETTINGS)!=state:raise ValueError('Live inputs changed during packaging')
    print('V2 ready',new,manifest['zip_sha256'],flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deploy',type=Path,required=True)
    ap.add_argument('--rollback',nargs='*',default=[],choices=sorted(GROUPS))
    ap.add_argument('--reuse',type=Path,help='Verified v2 base-resource cache; permits component rollback after v2 deployment')
    ap.add_argument('--compiled-cache',type=Path,help='Reuse hash-checked private AS compile intermediates; all native gates still run')
    ap.add_argument('--script-cache',type=Path,help='Reuse completed current-provider and candidate-matched compiler controls')
    ap.add_argument('--assembly',type=Path,default=Path('C:/REDkitProjects/witchercompatibility/compatibility-validation/analog-gait'))
    ap.add_argument('--glyph-font',type=Path,default=Path('C:/Windows/Fonts/segoeui.ttf'))
    ap.add_argument('--finish-package',action='store_true',help='Verify and resume completed native pack; retry metadata only if necessary')
    args=ap.parse_args()
    (finish_package if args.finish_package else build)(args)


if __name__=='__main__':main()
