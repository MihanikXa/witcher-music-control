"""Rebuild only smooth artwork from a verified private v4 movie checkpoint.
No AS recompilation: ABC bytes, authored placements and exports must stay exact.
Follow with build-ink-hud-v4.py --resume for all native/package gates.
"""
import argparse,json,struct,shutil,subprocess
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();cache=a.cache.resolve();out=a.out.resolve();m.b.font.private_path(cache);m.b.font.private_path(out)
 if out.exists():raise ValueError('Fresh output required')
 contracts=json.loads((cache/'prepared-contracts.json').read_text());parent=json.loads((m.PARENT/'receipt.json').read_text());out.mkdir()
 shutil.copy2(cache/'live-before.json',out/'live-before.json')
 for key,h in parent['resource_hashes'].items():
  source=(cache/'prepared-inputs'/key).read_bytes();stem=Path(key).stem;data=source
  if key in contracts['movie_contracts'] and m.b.audit.sha(source)!=contracts['movie_contracts'][key]['output_sha256']:raise ValueError('Movie checkpoint changed')
  if key in contracts['unchanged_keys'] and m.b.audit.sha(source)!=h:raise ValueError('Unchanged checkpoint differs')
  changes=contracts['changes'].get(key,{})
  details=changes.get('glyphs') or parent.get('movie_contracts',{}).get(key,{}).get('glyphs')
  if details:
   mapping={d['shape_id']:d for d in details if d['shape_id'] and 'dpad' in d['symbol']}
   m.smooth.flat.r.glyph=lambda n,w,h,font:m.smooth.preview(n,w,h,font)
   names={d['bitmap_id']:d['symbol'] for d in details}
   data,blocks=m.smooth.flat.original_atlas_art(source,names,out,m.FONT)
   def change(tags):
    return [(c,m.smooth.shape(struct.unpack_from('<H',p)[0],mapping[struct.unpack_from('<H',p)[0]]['symbol'],64,64,m.FONT) if c==32 and struct.unpack_from('<H',p)[0] in mapping else p) for c,p in tags]
   data=m.replace_tags(data,change)
   for codes in ({82},{76},{48,75,57,71},{39,4,26,70}):
    if [(c,p) for c,p in m.b.audit.swf_tags(source)[2] if c in codes]!=[(c,p) for c,p in m.b.audit.swf_tags(data)[2] if c in codes]:raise ValueError('Non-art contract changed')
  target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  for folder in ('abc','base-export','reexport','exports'):
   directory=cache/folder/stem
   if directory.exists():
    # Copy original private source and receipts; new independent XML below.
    shutil.copytree(directory,out/folder/stem,ignore=shutil.ignore_patterns('*.xml','*.gfx'))
  if details:
   target=out/'reexport'/stem/'final.gfx';target.write_bytes(m.r.p.movie(data)[1])
   cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-swf2xml',str(target),str(target.with_suffix('.xml'))];proc=subprocess.run(cmd,capture_output=True,timeout=90)
   if proc.returncode:raise ValueError('Independent XML parse failed')
  print('Artwork checkpoint',stem,flush=True)
 m.b.write_json(out/'art-rebuild.json',dict(cache=str(cache),tool_sha256=m.b.fallback.sha(Path(__file__)),abc_exports_fonts_placements_unchanged=True))
if __name__=='__main__':main()
