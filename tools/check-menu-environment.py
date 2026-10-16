"""Isolate the unchanged upstream optional environment from movie validation."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('b',ROOT/'tools/build-menus-087.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def main():
 key='environment/definitions/gui_character_display/gui_character_environment.env';data=(b.E/'0.8.7'/key).read_bytes();out=b.OUT/'environment-control';out.mkdir();runner=ROOT/'build/ink-hud-v3-native-runner';commands=[]
 with b.m.b.mount(runner,out,{key:data}) as workspace:
  ok,_=b.native.native(runner,out,'cook',['cook','-platform=pc','-mod='+str(workspace),'-outdir='+str(out/'cooked')],commands)
  if not ok:raise ValueError('Environment control cook did not complete')
  ok,log=b.native.native(runner,out,'validate',['validate','-db='+str(out/'cooked/cook.db'),'-outdir='+str(out/'validation')],commands)
  errors=next((line for line in log.splitlines() if 'Errors found in ' in line),'missing summary')
  commands[-1]['passed']=ok and 'Errors found in 0 resources:' in log;b.m.b.write_json(out/'native-commands.json',commands)
 b.m.b.write_json(out/'receipt.json',dict(input_sha256=b.m.b.audit.sha(data),cooked_sha256=b.m.b.fallback.sha(out/'cooked'/key),validation_summary=errors,native_commands=commands,shipped=False));print(errors,flush=True)
if __name__=='__main__':main()
