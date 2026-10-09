"""Build a private package-04 movement hotfix; live inputs are read-only."""
import argparse,copy,hashlib,importlib.util,json,re,shutil,subprocess,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/'release/witcher-compatibility'
EXPECTED='49220f25110566c6355e19be9464822ef47d0bf12a43b31d209e8d3ef151813a'
TARGET='Mods/mod0000_MergedFiles/content/scripts/game/player/playerInput.ws'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('release_builder',ROOT/'tools/build-release.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def bounds(text,name):
 clean=b.masked(text);hits=list(re.finditer(r'\b(?:event|function)\s+'+name+r'\s*\(',clean));assert len(hits)==1,name
 start=clean.index('{',hits[0].end());end=start+1;depth=1
 while depth:
  if clean[end]=='{':depth+=1
  elif clean[end]=='}':depth-=1
  end+=1
 return start+1,end-1

def transform(text):
 original=text
 a,z=bounds(text,'OnCommSprint');body=text[a:z]
 old='//thePlayer.SetSprintActionPressed(true);'
 new="""if (!movementCompatSprintHeld)
            {
                movementCompatWalkBeforeSprint = thePlayer.GetIsWalkToggled();
                movementCompatSprintHeld = true;
            }
            thePlayer.SetSprintActionPressed(true);"""
 assert body.count(old)==1;body=body.replace(old,new)
 old='thePlayer.SetWalkToggle(true);'
 new="""thePlayer.SetSprintActionPressed(false);
            if (movementCompatSprintHeld)
            {
                thePlayer.SetWalkToggle(movementCompatWalkBeforeSprint);
                movementCompatSprintHeld = false;
            }"""
 assert body.count(old)==1;body=body.replace(old,new);text=text[:a]+body+text[z:]
 a,z=bounds(text,'OnCommSprintToggle');body=text[a:z];old='thePlayer.SetSprintToggle( true );';assert body.count(old)==1
 body=body.replace(old,old+'\n                    thePlayer.getHoldToRun().setSlowWalk(false);');text=text[:a]+body+text[z:]
 a,z=bounds(text,'OnCommWalkToggle');body=text[a:z]
 body+="""
        // Horse handling above returns before the on-foot gait toggle.
        if (IsPressed(action))
        {
            if (movementCompatSprintHeld)
                movementCompatWalkBeforeSprint = !movementCompatWalkBeforeSprint;
            else
                thePlayer.SetWalkToggle(!thePlayer.GetIsWalkToggled());
        }
"""
 text=text[:a]+body+text[z:]
 marker='event OnCommSprint( action : SInputAction )';assert text.count(marker)==1
 text=text.replace(marker,'private var movementCompatSprintHeld : bool;\n    private var movementCompatWalkBeforeSprint : bool;\n\n    '+marker)
 # Unrelated code must be identical after removing these three event regions
 # and the two explicitly introduced fields.
 def unrelated(t):
  for name in ['OnCommSprint','OnCommSprintToggle','OnCommWalkToggle']:
   x,y=bounds(t,name);t=t[:x]+t[y:]
  t=re.sub(r'private var movementCompat(?:SprintHeld|WalkBeforeSprint) : bool;','',t)
  return re.sub(r'\s+','',b.masked(t))
 assert unrelated(original)==unrelated(text)
 # Native sign-casting early return precedes the new sprint flag; horse flow unchanged.
 x,y=bounds(text,'OnCommSprint');assert text[x:y].index('return false;')<text[x:y].index('SetSprintActionPressed(true)')
 x,y=bounds(text,'OnCommWalkToggle');assert text[x:y].index('return false;')<text[x:y].index('movementCompatSprintHeld')
 return text

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',required=True,type=Path);ap.add_argument('--compile',action='store_true');args=ap.parse_args()
 source=RELEASE/'04-updated-merges.zip';assert sha(source)==EXPECTED,'Base package changed: review before rebuilding'
 destination=RELEASE/'movement-fix';destination.mkdir(exist_ok=True)
 with zipfile.ZipFile(source) as archive:
  names=archive.namelist();target=next(n for n in names if n.lower()==TARGET.lower());old=archive.read(target)
  decoded=old.decode('utf-8-sig');patched=transform(decoded).encode('utf-8')
  assert (args.game/target).read_bytes() in [old,patched],'Deployed playerInput differs from both reviewed versions'
  payload=destination/'payloads'/target;payload.parent.mkdir(parents=True,exist_ok=True);payload.write_bytes(patched)
  result=destination/'04-updated-merges-movement-fix.zip'
  with zipfile.ZipFile(result,'w') as hotfix:
   for member in archive.infolist():hotfix.writestr(copy.copy(member),patched if member.filename==target else archive.read(member.filename))
  with zipfile.ZipFile(result) as hotfix:
   assert hotfix.testzip() is None and hotfix.namelist()==names
   unchanged=[n for n in names if n!=target];assert all(hotfix.read(n)==archive.read(n) for n in unchanged)
   assert len(names)==12 and all(n.startswith('Mods/mod0000_MergedFiles/') for n in names)
  shutil.copyfile(source,destination/'04-updated-merges-before-movement-fix.zip')
 receipt=dict(archive=str(result),sha256=sha(result),files=12,changed=[target],unchanged_files=11,previous_sha256=EXPECTED,crc_pass=True,unrelated_source_preserved=True,live_deployment=False,runtime_test=False)
 (destination/'jog-controls.json').write_text(json.dumps({'BASE_CharacterMovementWithSprint':{'IK_CapsLock':'(Action=WalkToggle)'},'Exploration':{'IK_CapsLock':'(Action=WalkToggle)'}},indent=2),encoding='utf-8')
 previous=destination/'validation.json'
 if previous.exists():
  previous_receipt=json.loads(previous.read_text(encoding='utf-8'))
  if previous_receipt.get('sha256')==receipt['sha256'] and 'compiler' in previous_receipt:receipt['compiler']=previous_receipt['compiler']
 if args.compile:
  reference_receipt=json.loads((ROOT/'evidence/compiler-full-split.json').read_text(encoding='utf-8'))
  for input_file in reference_receipt['sources']:
   assert sha(Path(input_file['path']))==input_file['sha256'],('Compiler reference input changed',input_file['path'])
  project=Path('C:/REDkitProjects/WitcherCompatibility/compatibility-validation');reference=project/'full-split';work=project/'movement-hotfix';assert not work.exists(),'Use a fresh isolated compiler directory'
  shutil.copytree(reference/'base',work/'base');shutil.copytree(reference/'patch',work/'patch');(work/'output').mkdir()
  staged=work/'base/game/player/playerInput.ws';assert staged.read_text(encoding='utf-8-sig')==decoded.replace('\r\n','\n'),'Compiler reference differs from current input'
  staged.write_bytes(patched)
  runtime=ROOT/'private/redkit-runtime';command=[str(runtime/'wcc_lite.exe'),'compilescripts',str(work/'base'),'-patch='+str(work/'patch'),'-out='+str(work/'output')]
  p=subprocess.run(command,cwd=runtime,capture_output=True,timeout=55);log=p.stdout+p.stderr;(work/'compiler.log').write_bytes(log);message=log.decode(errors='replace');blob=work/'output/blob.rsblob'
  receipt['compiler']=dict(exit_code=p.returncode,success=p.returncode==0 and 'Success! Patch scripts blob saved' in message and blob.is_file() and blob.stat().st_size>0,compiler_sha256=sha(runtime/'wcc_lite.exe'),output_sha256=sha(blob) if blob.exists() else None,warnings=message.count('[Warning]'),assertions=message.count('[Error][Assert]'),scope='Existing assembled source baseline plus unchanged Gwent patch; not exact opaque-blob deployment order')
 with zipfile.ZipFile(result) as z:
  manifest=dict(archives=[dict(name=result.name,files=[dict(path=n) for n in z.namelist()])])
 routing=destination/'topology';routing.mkdir(exist_ok=True);(routing/'validation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 (destination/'validation.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()
