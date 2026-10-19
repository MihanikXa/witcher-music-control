"""Offline contextual opportunity model. No audio/game/Wwise integration.

Native ownership/outro and playback acceptance are explicit SIMULATED oracle
inputs, not invented WitcherScript APIs. All numbers are experimental profiles.
An integrated exponential hazard clock is independent of callback frequency.
"""
from collections import deque
from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class Profile:
    name: str
    baseline: float
    opportunity: float
    random_rate: float
    window: float=60
    stable: float=8
    quiet_floor: float=30
    ramp: float=120
    excerpt_gap: float=420
    family_gap: float=240
    recovery: float=45

    def __post_init__(self):
        values=[v for k,v in vars(self).items() if k!='name']
        if not all(not isinstance(v,bool) and math.isfinite(v) and v>=0 for v in values) or self.ramp<=0 or self.window<=0:
            raise ValueError('Invalid experimental probability/timing profile')


PROFILES={'restrained':Profile('restrained',1/900,1/180,1/650),
          'contrast':Profile('contrast',1/450,1/100,1/330)}
STATES=('region','location','selector','daypart','weather','activity','game_state',
        'native_owner','threatened','scene','paused','loading','outro_clear')
COMBAT_STATES={'combat','combat_monster_hunt','underwater_combat','underwater_combat_focus'}


def suitability(cue,context):
    """Editorial DEMO hypothesis, no geographic assignments or inferred biome."""
    if context['activity'] not in ('foot','horse'):return 0
    if cue['role']=='atmospheric':
        return 2.0 if context['daypart']=='night' and context['activity']=='foot' else 0
    if cue['role']=='punctuation':return .65 if context['daypart']=='night' else 1.0
    raise ValueError('Unknown illustrative role')


class Model:
    def __init__(self,cues,profile,seed,approach='contextual'):
        if approach not in ('contextual','randomized'):raise ValueError('Unknown approach')
        if not 1<=len(cues)<=3 or len({c['id'] for c in cues})!=len(cues):raise ValueError('One to three unique illustrative cues')
        for c in cues:
            if not c.get('family') or isinstance(c['seconds'],bool) or not math.isfinite(c['seconds']) or c['seconds']<=0:raise ValueError('Invalid cue')
        self.cues=sorted(cues,key=lambda c:c['id']);self.p=profile;self.approach=approach
        self.t=0.;self.context={k:None for k in STATES};self.stable_until=0.;self.quiet_since=0.
        self.recover_until=0.;self.generation=0;self.combat_epoch=0;self.was_combat=False;self.outro_pending=False
        self.time_rng=random.Random(seed);self.pick_rng=random.Random(seed^0x5A17)
        self.budget=None;self.active=None;self.history=deque(maxlen=32)
        self.windows={};self.seen=deque(maxlen=256);self.records=[];self.intervals=[];self.exposure=[]

    def log(self,kind,**data):self.records.append(dict(time=self.t,kind=kind,**data))

    def veto(self):
        c=self.context
        if c['loading'] is not False:return 'loading_or_unknown'
        if c['paused'] is not False:return 'paused_or_unknown'
        if c['native_owner']!='generic':return 'native_'+str(c['native_owner'])
        if c['game_state'] not in ('exploration','exploration_night'):return 'nonexploration'
        if c['scene'] is not False:return 'scene_or_unknown'
        if c['threatened'] is not False:return 'hostility_or_unknown'
        if c['selector']!='reviewed_generic':return 'unreviewed_selector'
        if not all(isinstance(c[k],str) and c[k] for k in ('region','location')):return 'context_unknown'
        if c['outro_clear'] is not True:return 'outro_unconfirmed'
        if c['activity'] not in ('foot','horse'):return 'unsupported_activity'
        if c['weather'] not in ('clear','rain') or c['daypart'] not in ('day','night'):return 'environment_unreviewed'
        return None

    def choices(self):
        result=[]
        for cue in self.cues:
            weight=suitability(cue,self.context) if self.approach=='contextual' else 1.
            if self.approach=='contextual':
                recent=any(self.t-h['end']<self.p.excerpt_gap and h['id']==cue['id'] for h in self.history)
                family=any(self.t-h['end']<self.p.family_gap and h['family']==cue['family'] for h in self.history)
                if recent or family:continue
                if self.history and self.history[-1]['family']==cue['family']:weight*=.25
                if any(w['kind']=='first_discovery' for w in self.windows.values()) and cue['role']=='punctuation':weight*=2
                if any(w['kind']=='weather_change' for w in self.windows.values()) and cue['role']=='atmospheric':weight*=2
            if weight>0:result.append((cue,weight))
        return result

    def reason(self):
        if self.active:return 'playing'
        if self.veto():return self.veto()
        if self.t<self.stable_until-1e-8:return 'context_settling'
        if self.t<self.recover_until-1e-8:return 'recovery'
        if self.t<self.quiet_since+self.p.quiet_floor-1e-8:return 'minimum_quiet'
        if not self.choices():return 'palette_empty_or_recent'
        return 'eligible'

    def primitive(self,t):
        z=max(0.,t-self.quiet_since-self.p.quiet_floor)
        return self.p.baseline*(z*z/(2*self.p.ramp) if z<self.p.ramp else z-self.p.ramp/2)

    def mass(self,a,b):
        if self.approach=='randomized':return self.p.random_rate*(b-a)
        extra=self.p.opportunity*max([w['strength'] for w in self.windows.values()],default=0)
        return self.primitive(b)-self.primitive(a)+extra*(b-a)

    def boundaries(self,end):
        values=[end,self.stable_until,self.recover_until,self.quiet_since+self.p.quiet_floor,
                self.quiet_since+self.p.quiet_floor+self.p.ramp]
        if self.active:values.append(self.active['end'])
        values.extend(w['end'] for w in self.windows.values())
        for h in self.history:values.extend([h['end']+self.p.excerpt_gap,h['end']+self.p.family_gap])
        return min(v for v in values if v>self.t+1e-8)

    def finish(self,reason):
        a=self.active
        if not a:return
        self.history[-1]['end']=self.t;self.intervals.append(dict(start=a['start'],end=self.t,cue=a['cue']['id'],
                                                               family=a['cue']['family'],reason=reason))
        self.log('complete' if reason=='natural' else 'interrupt',cue=a['cue']['id'],reason=reason)
        self.active=None;self.quiet_since=self.t;self.budget=None

    def maintenance(self):
        if self.active and self.t>=self.active['end']-1e-8:self.finish('natural')
        for key,w in list(self.windows.items()):
            if self.t>=w['end']-1e-8:self.log('opportunity_expired',event=key);del self.windows[key]

    def start(self):
        choices=self.choices();total=sum(w for _,w in choices);pick=self.pick_rng.random()*total
        for cue,w in choices:
            pick-=w
            if pick<0:break
        self.active=dict(cue=cue,start=self.t,end=self.t+cue['seconds'])
        self.history.append(dict(id=cue['id'],family=cue['family'],end=self.t))
        self.log('start',cue=cue['id'],family=cue['family'],context=dict(self.context),
                 opportunities=sorted(self.windows),simulated_playback_acceptance=True)
        for key in self.windows:self.log('opportunity_consumed',event=key)
        self.windows.clear();self.budget=None

    def advance(self,end):
        if isinstance(end,bool) or not math.isfinite(end) or end<self.t:raise ValueError('Nonchronological/nonfinite time')
        iterations=0
        while self.t<end-1e-8:
            iterations+=1
            if iterations>100000:raise RuntimeError('Nonconvergent model')
            self.maintenance();boundary=self.boundaries(end);why=self.reason()
            if why=='eligible':
                if self.budget is None:self.budget=self.time_rng.expovariate(1.)
                mass=self.mass(self.t,boundary)
                # External context/native events win ties at their timestamp.
                if self.budget<mass-1e-12:
                    lo,hi=self.t,boundary
                    for _ in range(55):
                        mid=(lo+hi)/2
                        if self.mass(self.t,mid)<self.budget:lo=mid
                        else:hi=mid
                    hit=(lo+hi)/2
                    self.exposure.append(dict(start=self.t,end=hit,reason=why,hazard=self.mass(self.t,hit)))
                    self.t=hit;self.start();continue
                self.budget-=mass
            self.exposure.append(dict(start=self.t,end=boundary,reason=why,
                                      hazard=self.mass(self.t,boundary) if why=='eligible' else 0))
            self.t=boundary
        self.t=end;self.maintenance()

    def change_context(self,values):
        if set(values)-set(STATES):raise ValueError('Unknown context field')
        changed={k:v for k,v in values.items() if self.context[k]!=v}
        if not changed:return
        old_veto=self.veto();old_context=dict(self.context);self.context.update(changed)
        if any(k in changed for k in ('region','location','daypart','weather','activity','selector')):
            self.stable_until=self.t+self.p.stable
        if any(k in changed for k in ('region','location')):
            self.cancel_windows('context_changed')
        combat=self.context['game_state'] in COMBAT_STATES or self.context['native_owner']=='combat'
        if combat and not self.was_combat:
            self.combat_epoch+=1;self.outro_pending=True
        if self.outro_pending:self.context['outro_clear']=False
        self.was_combat=combat
        if 'region' in changed and old_context['region'] is not None:
            self.context['outro_clear']=None  # new bank/lifecycle needs positive re-observation
        new_veto=self.veto()
        if new_veto:
            self.finish(new_veto);self.cancel_windows('native_or_context_veto');self.budget=None
        if old_veto and not new_veto:self.quiet_since=self.t
        self.log('context',changed=changed,veto=new_veto,context=dict(self.context))

    def cancel_windows(self,reason):
        for key in self.windows:self.log('opportunity_cancelled',event=key,reason=reason)
        self.windows.clear()

    def apply_batch(self,events):
        # Aggregate same-time snapshots before any optional opportunity.
        if any(e['kind']=='load' for e in events):
            self.finish('load');self.cancel_windows('load');self.generation+=1;self.budget=None
            self.context={k:None for k in STATES};self.was_combat=False;self.quiet_since=self.t;self.outro_pending=False
            self.log('load',generation=self.generation)
        updates={}
        for event in events:
            if event['kind']=='context':
                if event.get('generation',0)!=self.generation:
                    self.log('stale_context');continue
                for k,v in event['values'].items():
                    if k in updates and updates[k]!=v:raise ValueError('Contradictory simultaneous context')
                    updates[k]=v
        self.change_context(updates)
        for event in events:
            kind=event['kind']
            if kind in ('context','load','poll'):continue
            if kind=='outro_end':
                valid=(event['generation']==self.generation and event['combat_epoch']==self.combat_epoch
                       and self.combat_epoch>0 and self.context['native_owner']=='generic'
                       and self.context['game_state'] in ('exploration','exploration_night') and not self.was_combat
                       and self.context['outro_clear'] is not True)
                if valid:
                    self.context['outro_clear']=True;self.outro_pending=False;self.quiet_since=self.t
                    self.recover_until=self.t+self.p.recovery
                self.log('outro_observation',accepted=valid,simulation_only=True)
            elif kind=='opportunity':
                if event.get('generation',0)!=self.generation:self.log('stale_opportunity');continue
                if event['type'] not in ('first_discovery','location_arrival','weather_change'):raise ValueError('Unsupported contextual opportunity')
                key=event['type']+':'+event['id']
                if not event['id']:raise ValueError('Opportunity needs stable semantic identity')
                if key in self.seen or key in self.windows:self.log('duplicate_opportunity',event=key);continue
                self.seen.append(key)
                if self.veto() or self.active or (event['type']=='first_discovery' and not(event.get('first') is True and event.get('local') is True)):
                    self.log('opportunity_rejected',event=key,reason=self.veto() or 'playing_or_not_first_local');continue
                if self.approach=='contextual':
                    if len(self.windows)>=16:self.log('opportunity_rejected',event=key,reason='bounded_window_capacity');continue
                    strength=.5 if event['type']=='location_arrival' else 1.
                    self.windows[key]=dict(kind=event['type'],end=self.t+self.p.window,strength=strength)
                    self.log('opportunity_open',event=key,expires=self.t+self.p.window)
            else:raise ValueError('Unknown typed trace event')


def run(trace,cues,profile,seed,approach='contextual'):
    if trace.get('provenance')!='simulated':raise ValueError('Only explicitly simulated traces in this prototype')
    model=Model(cues,profile,seed,approach);last=-1.;group=[]
    for event in trace['events']:
        t=event['time']
        if isinstance(t,bool) or not math.isfinite(t) or t<last or t<0:raise ValueError('Unsorted/invalid trace')
        if t!=last and group:
            model.advance(last);model.apply_batch(group);group=[]
        group.append(event);last=t
    if group:model.advance(last);model.apply_batch(group)
    if trace['duration']<last:raise ValueError('Trace ends before events')
    model.advance(trace['duration'])
    if model.active:
        model.intervals.append(dict(start=model.active['start'],end=model.t,cue=model.active['cue']['id'],
                                    family=model.active['cue']['family'],reason='trace_end_not_completion'))
    return model
