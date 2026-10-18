"""Matched single-cue cases using report55's Recorder/profiler and cleanup."""
import argparse
from pathlib import Path

import white_orchard_sparse_capture as capture
from sparse_approved_cue import verify_accepted, read
from white_orchard_prepare import digest
from white_orchard_sparse import MUSIC


def cases():
    return [
        dict(name='two-cycles',duration=130,actions=[(8,'rtpc','menu_volume_music',50),(16,'rtpc','menu_volume_music',100)]),
        dict(name='combat-music',duration=95,actions=[(6,'state','combat',None),(12,'rtpc','threat_rating',35),
            (18,'rtpc','threat_rating',100),(30,'state','exploration',None)]),
        dict(name='combat-rest-early',duration=105,actions=[(44,'state','combat',None),(50,'rtpc','threat_rating',35),
            (56,'rtpc','threat_rating',100),(66,'state','exploration',None)]),
        dict(name='combat-rest-late',duration=115,actions=[(57,'state','combat',None),(64,'rtpc','threat_rating',35),
            (70,'rtpc','threat_rating',100),(82,'state','exploration',None)]),
        dict(name='place-daynight-music',duration=60,actions=[(6,'state','exploration_night',None),(12,'state','exploration',None),
            (20,'event','mus_loc_prologue_nilfgaard_camp',None),(32,'event','mus_loc_prologue_village',None),
            (43,'state','cutscene',None),(44,'state','dialog_scene',None),(49,'state','movie',None),
            (50,'state','music_only',None),(54,'state','exploration',None)]),
        dict(name='place-daynight-rest',duration=95,actions=[(44,'state','exploration_night',None),(48,'state','exploration',None),
            (52,'event','mus_loc_prologue_nilfgaard_camp',None),(62,'event','mus_loc_prologue_village',None),
            (70,'state','cutscene',None),(71,'state','dialog_scene',None),(76,'state','movie',None),
            (77,'state','music_only',None),(81,'state','exploration',None)]),
        dict(name='authored-phrase',duration=35,actions=[(6,'state','dialog_scene',None),(6.1,'event','mus_q001_tavern_conversation',None)]),
        dict(name='authored-rest',duration=80,actions=[(44,'state','dialog_scene',None),(44.1,'event','mus_q001_tavern_conversation',None)]),
        dict(name='protected-world',duration=30,location='mus_loc_prologue_village_q505',technical_isolation=True,
            actions=[(8,'rtpc','menu_volume_music',50),(17,'rtpc','menu_volume_music',100)]),
        dict(name='gwent',duration=20,state='gwent',actions=[]),
    ]


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--port',type=int,required=True);p.add_argument('--label',required=True);p.add_argument('--cases',nargs='+');a=p.parse_args()
    verify_accepted()
    if read(a.project.parent/'sparse-source-gate.json')['mode']=='sparse':
        gate=read(a.project.parent/'approved-cue-source-gate.json')
        if not gate['passed'] or digest(a.project.parent/MUSIC)!=gate['authored_source_sha256']:raise ValueError('Current imported cue source gate required')
    capture.cases=cases
    capture.supplemental_cases=lambda:[]
    capture.run(a.project,a.port,a.label,a.cases)
