"""Final metric correction from verified v4 checkpoints; scoped AS edits only."""
import argparse,json,shutil,subprocess,re
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('m',ROOT/'tools/build-ink-hud-v4.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def center(t):
 replacement,count=re.subn(r'getLineMetrics\(0\).ascent - ((?:this\.)?textField.getLineMetrics\(0\).descent)',r'getLineMetrics(0).ascent + \1',t)
 if count!=1:raise ValueError('One centering expression required')
 return replacement

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();cache=a.cache.resolve();out=a.out.resolve();m.b.font.private_path(cache);m.b.font.private_path(out)
 if out.exists():raise ValueError('Fresh output required')
 receipt=json.loads((cache/'prepared-contracts.json').read_text());out.mkdir();shutil.copy2(cache/'live-before.json',out/'live-before.json')
 keys=json.loads((m.PARENT/'receipt.json').read_text())['resource_hashes'];edits={}
 for key in keys:
  source=(cache/'prepared-inputs'/key).read_bytes();data=source;stem=Path(key).stem
  if key in receipt['movie_contracts'] and m.b.audit.sha(source)!=receipt['movie_contracts'][key]['output_sha256']:raise ValueError('Checkpoint hash changed')
  for folder in ('base-export','reexport','exports'):
   origin=cache/folder/stem
   if origin.exists():shutil.copytree(origin,out/folder/stem,ignore=shutil.ignore_patterns('*.xml','*.gfx'))
  before=cache/'reexport'/stem;transforms={}
  for name in ('InputFeedbackButton','HintButton'):
   if list(before.rglob(name+'.as')):transforms[name]=center
  if transforms:
   data,edits[key]=m.r.compile_classes(source,before,out/'abc'/stem,transforms)
   for name in transforms:
    path=next((before/'scripts').rglob(name+'.as'));namespace=path.relative_to(before/'scripts').with_suffix('').as_posix().replace('/','.')
    gfx=out/'reexport'/stem/'final.gfx';gfx.write_bytes(m.r.p.movie(data)[1])
    cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-selectclass',namespace,'-export','script',str(out/'reexport'/stem),str(gfx)]
    proc=subprocess.run(cmd,capture_output=True,timeout=90)
    if proc.returncode:raise ValueError('Targeted compiled class export failed')
    text=next((out/'reexport'/stem/'scripts').rglob(name+'.as')).read_text(encoding='utf-8-sig')
    if 'getLineMetrics(0).ascent + ' not in text:raise ValueError('Compiled baseline correction absent')
   # Unselected cached sources are retained as evidence; selected compiled
   # classes are independently decompiled and checked against all contracts.
   m.v.contract(source,data,before,out/'reexport'/stem)
   cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-swf2xml',str(gfx),str(gfx.with_suffix('.xml'))];proc=subprocess.run(cmd,capture_output=True,timeout=90)
   if proc.returncode:raise ValueError('Final independent XML parse failed')
  target=out/'prepared-inputs'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  print('Centered checkpoint',stem,flush=True)
 m.b.write_json(out/'centering.json',dict(edits=edits,formula='TextField y = glyph center - 2 - (ascent + descent)/2',unmodified_class_sources_reused=True,modified_class_sources_independently_decompiled=True))
if __name__=='__main__':main()
