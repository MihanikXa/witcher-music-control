"""Strict private WMCCTX1 trace normalization; never invent native ownership.

Only the original diagnostic format is accepted. Observed fields remain separate
from policy inference. Loading-video false is NOT a verified loading=false.
"""
import argparse
import json
import math
from pathlib import Path

STATES=['default','exploration','exploration_night','focus','focus_night','focus_underwater',
        'combat','combat_monster_hunt','dialog_scene','dialog_scene_night','cutscene','minigame',
        'death','movie','boat','music_only','underwater','underwater_combat','paused','gwent','underwater_combat_focus']
ENUMS=['Default','Exploration','ExplorationNight','Focus','FocusNight','FocusUnderwater','Combat',
       'CombatMonsterHunt','Dialog','DialogNight','Cutscene','Minigame','Death','Movie','Boat','MusicOnly',
       'Underwater','UnderwaterCombat','Paused','Gwent','FocusUnderwaterCombat']


def boolean(value):
    if value in ('true','True','1'):return True
    if value in ('false','False','0'):return False
    raise ValueError('Invalid boolean')


def state(value):
    if value.startswith('ESGS_'):
        try:return STATES[ENUMS.index(value[5:])]
        except ValueError:raise ValueError('Unknown native enum')
    try:i=int(value)
    except ValueError:raise ValueError('Unknown native state encoding')
    if not 0<=i<len(STATES):raise ValueError('Out-of-range native enum')
    return STATES[i]


def normalize(text):
    events=[];evidence=[];epoch=None;seq=0;last_raw=0.;offset=0.;last=0.;seen=set();per_epoch=0
    lines=text.splitlines()
    if len(lines)>100000:raise ValueError('Trace too large; split sessions')
    for line in lines:
        if 'WMCCTX1|' not in line:continue
        if len(line)>4096:raise ValueError('Oversize diagnostic line')
        parts=line.split('WMCCTX1|',1)[1].split('|');fields={};kind=None
        for part in parts:
            if '=' not in part:
                if kind is not None:raise ValueError('Ambiguous record kind')
                kind=part;continue
            k,v=part.split('=',1)
            if k in fields:raise ValueError('Duplicate field')
            fields[k]=v
        ep=int(fields['epoch']);n=int(fields['seq']);raw=float(fields['t'])
        if not math.isfinite(raw) or raw<0 or ep<1 or n<1:raise ValueError('Invalid clock/identity')
        if epoch!=ep:
            if kind!='begin' or (epoch is not None and ep<=epoch):raise ValueError('Missing/reversed lifecycle begin; split sessions')
            offset=0. if epoch is None else last+.001
            epoch=ep;seq=0;last_raw=0.;per_epoch=0;seen=set()
            events.append(dict(time=offset,kind='load',source='observed_lifecycle'))
        if n<=seq or raw<last_raw:raise ValueError('Reversed/duplicate record')
        seq=n;last_raw=raw;per_epoch+=1
        if per_epoch>600:raise ValueError('Diagnostic row bound exceeded')
        t=offset+raw;last=t;generation=sum(e['kind']=='load' for e in events)
        record=dict(epoch=ep,sequence=n,source_clock=raw,time=t,origin=fields.get('origin'),kind=kind)
        if kind=='begin':pass
        elif kind=='snapshot':
            values=dict(native_owner='unknown',selector=None,location=None,outro_clear=None,weather=None,loading=None)
            if fields['available']=='1':
                if fields['owner']!='unknown' or fields['outro']!='unknown' or fields['selector']!='unknown' or fields['location']!='unknown':
                    raise ValueError('Diagnostic cannot assert ownership/selector')
                activity=fields['activity']
                if activity not in ('foot','horse','boat'):raise ValueError('Invalid activity')
                region=int(fields['region'])
                values.update(region=str(region),game_state=state(fields['state']),
                    daypart='night' if boolean(fields['night']) else 'day',activity=activity,
                    threatened=boolean(fields['combat']) or boolean(fields['threat']),
                    scene=boolean(fields['scene']),paused=boolean(fields['paused']))
                record['observed']={k:fields[k] for k in ('combat','threat','loading_video','interior')}
                boolean(fields['loading_video']);boolean(fields['interior'])
            elif fields['available']!='0':raise ValueError('Invalid availability')
            else:values.update(region=None,game_state=None,daypart=None,activity=None,threatened=None,scene=None,paused=None)
            events.append(dict(time=t,kind='context',generation=generation,values=values,source='observed_snapshot'))
        elif kind=='discovery':
            if fields.get('origin')!='player_first_trigger' or fields.get('local')!='1' or fields.get('first')!='1':
                raise ValueError('Unfiltered discovery record')
            ident=int(fields['id'])
            if not 1<=ident<=32:raise ValueError('Out-of-bound discovery ordinal')
            if ident in seen:raise ValueError('Duplicate discovery ordinal')
            seen.add(ident)
            events.append(dict(time=t,kind='opportunity',type='first_discovery',generation=generation,
                id=f'epoch{ep}-local{ident}',first=True,local=True,source='observed_trigger'))
        else:raise ValueError('Unknown diagnostic kind')
        evidence.append(record)
    if not evidence:raise ValueError('No diagnostic records; logging delivery not established')
    return dict(schema=1,provenance='observed_diagnostic_format_not_authenticated',duration=last,
        timestamp_semantics='Engine-clock seconds per lifecycle; inter-epoch gap unknown, compacted to1ms. No real wall-gap inference.',
        events=events,observations=evidence,native_owner='unknown',outro_end='unavailable',
        limitations=['Loading video is not complete loading status.','No native music selector/location getter.',
                     'Source-defined snapshots can miss subsecond transitions; timers may pause.',
                     'Raw log authenticity/delivery must be established by user capture.'])


def replay(trace,cues,profile,seed=0):
    """Explicit model replay; trace observations stay observed, no oracle filling."""
    from sparse_context_policy import Model
    if trace.get('provenance')!='observed_diagnostic_format_not_authenticated':raise ValueError('Wrong provenance')
    m=Model(cues,profile,seed)
    for event in trace['events']:
        m.advance(event['time']);m.apply_batch([event])
    m.advance(trace['duration'])
    return m


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]/'build'
    if not a.output.resolve().is_relative_to(root.resolve()):raise ValueError('Private traces belong under ignored build')
    if a.output.exists():raise FileExistsError(a.output)
    result=normalize(a.input.read_text(encoding='utf-8',errors='strict'))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
