"""Incremental selected-gait override from pinned Movement Tweaks; never deploy."""
import argparse,copy,hashlib,importlib.util,json,shutil,subprocess,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];RELEASE=ROOT/'release/witcher-compatibility'
BASE_HASH='6ce762947cfbc02223ac50e635277065df65962f233909acb7a7950398b990d3'
LOCO_HASH='ae5599a6e6eb89b98db3498117c7164e3d95de5a531bb8f2c76dc2699a5d2f75'
REL='content/scripts/game/player/movement/locomotionDirectController.ws'
TARGET='Mods/mod0000_MergedFiles/'+REL
spec=importlib.util.spec_from_file_location('movement',ROOT/'tools/build-movement-fix.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def transform(original):
 a,z=m.bounds(original,'CalculateMoveSpeed');body=original[a:z];edits=[]
 def change(old,new):
  nonlocal body
  assert body.count(old)==1,old[:80];body=body.replace(old,new);edits.append((old,new))
 change('var forceWalkSpeed\t: bool;',"""var forceWalkSpeed	: bool;
        var compatibilityUseSelectedGait : bool;
        var compatibilityRawMagnitude, compatibilityTargetCap : float;
        var compatibilityRestoreWalk, compatibilityWalkBeforeNative : bool;""")
 marker='player.terrainPitch'
 index=body.index(marker)
 setup="""compatibilityRawMagnitude = ClampF(speed, 0.f, 1.f);
        compatibilityUseSelectedGait = _inputLocoEnabled && player == thePlayer
            && player.GetCurrentStateName() == 'Exploration' && player.GetPlayerAction() == PEA_None
            && !player.IsInCombat() && !player.IsCombatMusicEnabled() && !player.IsSwimming()
            && !player.IsUsingVehicle() && !player.IsInAir() && !player.modifyPlayerSpeed
            && !theGame.IsFocusModeActive() && !theGame.IsFading() && !theGame.IsBlackscreen()
            && player.IsActionAllowed(EIAB_RunAndSprint);

        """
 body=body[:index]+setup+body[index:];edits.append(('',setup))
 old='if ( theInput.LastUsedGamepad() )\n\t\t\t{\n\t\t\t\tthePlayer.SetWalkToggle(false);\n\t\t\t\t\n\t\t\t}'
 new="""if (theInput.LastUsedGamepad() && !compatibilityUseSelectedGait)
            {
                // Preserve native combat/special-state calculation without losing selected gait.
                compatibilityWalkBeforeNative = thePlayer.GetIsWalkToggled();
                compatibilityRestoreWalk = true;
                thePlayer.SetWalkToggle(false);
            }"""
 change(old,new)
 mapping="""if (compatibilityUseSelectedGait && speed > 0.f && !player.GetIsSprinting())
        {
            if (player.GetIsWalkToggled())
                compatibilityTargetCap = speedWalkingMax;
            else
                compatibilityTargetCap = speedRunning;
            if (compatibilityGaitCap < 0.f || compatibilityRawMagnitude <= 0.f)
                compatibilityGaitCap = compatibilityTargetCap;
            else if (compatibilityGaitCap < compatibilityTargetCap)
                compatibilityGaitCap = MinF(compatibilityTargetCap, compatibilityGaitCap + 3.f * MaxF(0.f, theTimer.timeDelta));
            else
                compatibilityGaitCap = MaxF(compatibilityTargetCap, compatibilityGaitCap - 3.f * MaxF(0.f, theTimer.timeDelta));
            speed = compatibilityRawMagnitude * compatibilityGaitCap;
            // Keep authored direction-switch slowdown and the native animation graph.
            if (forceWalkSpeed)
                speed = MinF(speed, speedWalkingMax);
            if (speed <= 0.f)
                player.playerMoveType = PMT_Idle;
            else if (player.GetIsWalkToggled() || forceWalkSpeed)
                player.playerMoveType = PMT_Walk;
            else
                player.playerMoveType = PMT_Run;
        }
        else if (compatibilityRawMagnitude <= 0.f || !compatibilityUseSelectedGait)
            compatibilityGaitCap = -1.f;

        """
 marker='tempInt = (int)( player.playerMoveType );';change(marker,mapping+marker)
 marker='return speed;';change(marker,"""if (compatibilityRestoreWalk)
            thePlayer.SetWalkToggle(compatibilityWalkBeforeNative);
        return speed;""")
 # Reverse every controlled insertion and substitution to prove unchanged native body.
 restored=body
 for old,new in reversed(edits):
  assert restored.count(new)==1;restored=restored.replace(new,old)
 assert restored==original[a:z]
 result=original[:a]+body+original[z:]
 marker='function CalculateMoveSpeed() : float';assert result.count(marker)==1
 result=result.replace(marker,'private var compatibilityGaitCap : float; default compatibilityGaitCap = -1.f;\n\t'+marker)
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);ap.add_argument('--compile',action='store_true');args=ap.parse_args()
 base=RELEASE/'movement-fix/04-updated-merges-movement-fix.zip';assert sha(base)==BASE_HASH
 source=args.game/'Mods/modMovementTweaks'/REL;assert sha(source)==LOCO_HASH
 destination=RELEASE/'analog-gait';destination.mkdir(exist_ok=True);patched=transform(source.read_text(encoding='utf-8-sig')).encode('utf-8')
 payload=destination/'payloads'/TARGET;payload.parent.mkdir(parents=True,exist_ok=True);payload.write_bytes(patched)
 archive=destination/'04-updated-merges-analog-gait.zip'
 with zipfile.ZipFile(base) as old:
  for n in old.namelist():assert (args.game/n).read_bytes()==old.read(n),('Working deployment changed',n)
  with zipfile.ZipFile(archive,'w') as new:
   for member in old.infolist():new.writestr(copy.copy(member),old.read(member.filename))
   info=zipfile.ZipInfo(TARGET,date_time=(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;new.writestr(info,patched)
  with zipfile.ZipFile(archive) as new:
   assert new.testzip() is None and len(new.namelist())==13
   assert all(new.read(n)==old.read(n) for n in old.namelist())
 receipt=dict(archive=str(archive),sha256=sha(archive),files=13,unchanged_members=12,added_override=TARGET,base_sha256=BASE_HASH,movement_source_sha256=LOCO_HASH,original_body_reverse_check=True,actual_deployment=False,runtime_test=False)
 previous=destination/'validation.json'
 if previous.exists():
  p=json.loads(previous.read_text(encoding='utf-8'))
  if p.get('sha256')==receipt['sha256'] and 'compiler' in p:receipt['compiler']=p['compiler']
 if args.compile:
  project=Path('C:/REDkitProjects/WitcherCompatibility/compatibility-validation');reference=project/'movement-hotfix';work=project/'analog-gait';assert not work.exists()
  shutil.copytree(reference/'base',work/'base');shutil.copytree(reference/'patch',work/'patch');(work/'output').mkdir()
  target=work/'base/game/player/movement/locomotionDirectController.ws';assert target.read_text(encoding='utf-8-sig')==source.read_text(encoding='utf-8-sig');target.write_bytes(patched)
  runtime=ROOT/'private/redkit-runtime';p=subprocess.run([str(runtime/'wcc_lite.exe'),'compilescripts',str(work/'base'),'-patch='+str(work/'patch'),'-out='+str(work/'output')],cwd=runtime,capture_output=True,timeout=55)
  log=p.stdout+p.stderr;(work/'compiler.log').write_bytes(log);text=log.decode(errors='replace');blob=work/'output/blob.rsblob'
  receipt['compiler']=dict(exit_code=p.returncode,success=p.returncode==0 and 'Success! Patch scripts blob saved' in text and blob.exists(),warnings=text.count('[Warning]'),assertions=text.count('[Error][Assert]'),output_sha256=sha(blob) if blob.exists() else None,scope='Preserved working source assembly plus one locomotion override; opaque blobs not recompiled')
 (destination/'validation.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
 if args.compile:assert receipt['compiler']['success'], 'Official compiler failed; inspect isolated compiler.log before release'
 topology=destination/'topology';topology.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive) as z:(topology/'validation.json').write_text(json.dumps(dict(archives=[dict(name=archive.name,files=[dict(path=n) for n in z.namelist()])]),indent=2),encoding='utf-8')
 print(json.dumps(receipt))
if __name__=='__main__':main()
