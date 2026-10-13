"""Export actual v4 GFx button shapes at representative parent scales."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--build',type=Path,required=True);a=ap.parse_args();source=a.build.resolve()
 if ROOT/'build' not in source.parents:raise ValueError('Private output required')
 parent=json.loads((ROOT/'build/ink-hud-v3-final/receipt.json').read_text());key='gameplay/gui_new/swf/common/panel_common.redswf';glyphs=parent['movie_contracts'][key]['glyphs']
 ids=[str(g['shape_id']) for g in glyphs if g['shape_id'] and g['symbol'].split('ICO_Xbox_')[-1].split('.')[0] in ('A','B','LT','RT','L_hold','dpad_up','dpad_left_right')]
 output=source/'previews';output.mkdir();receipts=[]
 for zoom in ('0.6875','1.375','4'):
  cmd=['java','-jar',str(ROOT/'build/tools/ffdec/ffdec.jar'),'-selectid',','.join(ids),'-format','shape:png','-zoom',zoom,'-export','shape',str(output/zoom),str(source/'reexport/panel_common/final.gfx')]
  proc=subprocess.run(cmd,capture_output=True,timeout=90);(output/(zoom+'.log')).write_bytes(proc.stdout+proc.stderr)
  if proc.returncode or len(list((output/zoom).glob('*.png')))!=len(ids):raise ValueError('Preview export failed')
  receipts.append(dict(scale=zoom,shape_ids=ids,exit_code=proc.returncode,command=cmd))
 (output/'receipt.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8');print('Independent multi-scale PNG export passed')
if __name__=='__main__':main()
