"""Independent offline stereo FDN reverb-state freeze for private auditions.

Sixteen unequal delays, orthonormal Hadamard feedback, no dry-sample looping.
Decay has per-line RT60 losses. Freeze closes the input and ramps those losses
to unity; the delay state then conserves energy. Fade is outside the feedback.
General theory: Julius O. Smith, Physical Audio Signal Processing, FDN chapter.
No third-party DSP implementation or proprietary plugin code is used.
"""
import numpy as np
from scipy import signal
from scipy.linalg import hadamard

RATE=48000
DELAYS=np.array([997,1151,1361,1549,1753,1999,2237,2477,
                 2671,2897,3109,3313,3517,3727,3917,4111])
MATRIX=hadamard(16).astype(np.float64)/4


def ramp(count):
    if count<2:raise ValueError('Fade needs at least two samples')
    return .5-.5*np.cos(np.linspace(0,np.pi,count))


def dry_envelope(frames,rate,fade_in,fade_start,fade_stop):
    if not 0<=fade_start<fade_stop<=frames/rate+1/rate:raise ValueError('Invalid dry fade')
    env=np.ones(frames)
    n=min(frames,round(fade_in*rate))
    if n>=2:env[:n]*=ramp(n)
    a,b=round(fade_start*rate),min(frames,round(fade_stop*rate))
    if b-a<2:raise ValueError('Empty ending fade')
    env[a:b]*=1-ramp(b-a);env[b:]=0
    return env


class Field:
    def __init__(self,rt60=3,rate=RATE):
        if rate!=RATE or not .2<rt60<20:raise ValueError('Unsupported field rate/RT60')
        self.buffers=[np.zeros(int(n)) for n in DELAYS]
        self.positions=np.zeros(16,dtype=int)
        self.decay=10**(-3*DELAYS/(rt60*rate))
        self.injection=MATRIX[[1,5]]
        self.output=np.stack([(MATRIX[2]+.35*MATRIX[9])/np.sqrt(1+.35**2),
                              (MATRIX[9]+.35*MATRIX[2])/np.sqrt(1+.35**2)],axis=1)

    def energy(self):return float(sum(np.dot(x,x) for x in self.buffers))

    def process(self,audio,freeze=False,transition=.1,ledger=False):
        if audio.ndim!=2 or audio.shape[1]!=2 or not np.isfinite(audio).all():raise ValueError('Finite stereo required')
        if freeze and np.any(audio):raise ValueError('A frozen field cannot receive new excitation')
        out=np.empty_like(audio,dtype=np.float64);trace=[]
        for start in range(0,len(audio),256):
            n=min(256,len(audio)-start);indices=[(p+np.arange(n))%len(b) for p,b in zip(self.positions,self.buffers)]
            taps=np.stack([b[i] for b,i in zip(self.buffers,indices)],axis=1)
            out[start:start+n]=taps@self.output
            gain=self.decay
            if freeze:
                t=np.clip(np.arange(start,start+n)/(transition*RATE),0,1)
                gain=self.decay[None,:]+(.5-.5*np.cos(t[:,None]*np.pi))*(1-self.decay)[None,:]
            incoming=(taps@MATRIX.T)*gain+audio[start:start+n]@self.injection
            for k,(b,i) in enumerate(zip(self.buffers,indices)):b[i]=incoming[:,k]
            self.positions=(self.positions+n)%DELAYS
            if ledger and (start//256%10==0 or start+n==len(audio)):
                trace.append(dict(seconds=(start+n)/RATE,state_energy=self.energy()))
        return out,trace


def field_pair(prime,frames,settings,continuation=None):
    """Matched initial states. B keeps normal post-fader send until dry stop;
    C closes excitation at capture, then holds the reverberant field.
    """
    if len(prime)<RATE*.2 or frames<RATE:raise ValueError('Insufficient field context/tail')
    hp,lp=settings['highpass_hz'],settings['lowpass_hz']
    if not 80<=hp<lp<=8000:raise ValueError('Unsafe field bandwidth')
    sos=np.concatenate([signal.butter(2,hp,'highpass',fs=RATE,output='sos'),
                        signal.butter(2,lp,'lowpass',fs=RATE,output='sos')])
    if continuation is None:continuation=np.zeros((0,2))
    if len(continuation)>frames:raise ValueError('Continuation beyond tail')
    filtered=signal.sosfilt(sos,np.concatenate([prime,continuation,np.zeros((frames-len(continuation),2))]),axis=0)
    excitation=filtered[:len(prime)]
    tails={};proof={}
    for name in ('B','C'):
        field=Field(settings['rt60']);field.process(excitation)
        initial=field.energy()
        driving=filtered[len(prime):] if name=='B' else np.zeros((frames,2))
        wet,trace=field.process(driving,freeze=name=='C',
                                transition=settings['freeze_transition'],ledger=True)
        settled=[r['state_energy'] for r in trace if r['seconds']>settings['freeze_transition']+.03]
        if not settled or max(settled)<=1e-16:raise ValueError('No useful reverberant state')
        drift=(max(settled)-min(settled))/max(settled)
        if name=='C' and drift>1e-10:raise ValueError('Freeze energy not conserved')
        if name=='B' and trace[-1]['state_energy']>=initial*.1:raise ValueError('Conventional decay not demonstrated')
        tails[name]=wet
        proof[name]=dict(initial_energy=initial,energy_trace=trace,settled_relative_energy_range=drift,
                        new_excitation_samples_after_capture=int(np.count_nonzero(driving)),
                        input_policy='closed at capture' if name=='C' else 'post-fader dry continuation plus causal input-filter tail',
                        feedback='unity after smooth transition' if name=='C' else 'RT60 losses retained')
    return tails,proof


def render_variants(source,settings,lead=2,trail=3):
    """Pure numerical edit; source is the complete decoded old audition file."""
    if source.ndim!=2 or source.shape[1]!=2 or not np.isfinite(source).all():raise ValueError('Invalid source')
    a=round(settings['source_in']*RATE)
    b=len(source) if settings['source_out'] is None else round(settings['source_out']*RATE)
    if not 0<=a<b<=len(source):raise ValueError('Cut outside original source')
    segment=source[a:b].copy();length=len(segment)/RATE
    fade_start,fade_stop=settings['dry_fade']
    start,stop=fade_start-settings['source_in'],fade_stop-settings['source_in']
    envelope=dry_envelope(len(segment),RATE,settings['fade_in'],start,stop)
    dry=segment*envelope[:,None]
    freeze_source=settings.get('freeze_at',fade_start)
    freeze=round((freeze_source-settings['source_in'])*RATE)
    if not 0<freeze<len(segment):raise ValueError('Freeze outside excerpt')
    if freeze<RATE*.2:raise ValueError('No preceding musical state to freeze')
    prime=segment[max(0,freeze-round(settings['prime_seconds']*RATE)):freeze]
    active_frames=len(segment)+round(settings['tail_extra']*RATE)
    wet_frames=active_frames-freeze
    tails,field_proof=field_pair(prime,wet_frames,settings,dry[freeze:])
    attack=round(settings['wet_attack']*RATE)
    tail_env=np.ones(wet_frames);tail_env[:attack]=ramp(attack)
    end_start=len(segment)+round(settings['hold_after_dry']*RATE)-freeze
    if not attack<=end_start<wet_frames:raise ValueError('Invalid wet hold/fade')
    tail_env[end_start:]=1-ramp(wet_frames-end_start)
    window=min(wet_frames,round(.4*RATE))
    level={k:float(np.sqrt(np.mean(v[:window]**2))) for k,v in tails.items()}
    target=float(np.sqrt(np.mean(prime[-min(len(prime),RATE):]**2)))*10**(settings['wet_db_relative']/20)
    if min(level.values())<1e-9 or target<1e-8:raise ValueError('Weak field: preserve controls, review source before forcing freeze')
    gains={k:target/level[k] for k in tails}
    if max(gains.values())>16:raise ValueError('Unsafe amplification of near-empty state')
    raw={}
    for variant in settings['variants']:
        out=np.zeros((active_frames,2));out[:len(dry)]=dry
        if variant!='A':out[freeze:]+=tails[variant]*gains[variant]*tail_env[:,None]
        raw[variant]=out
    peak=max(float(np.max(np.abs(v))) for v in raw.values())
    headroom=min(1,.96/max(peak,1e-12)) # Attenuate all alternatives equally; never boost or compress dry audio.
    final={k:np.pad(v*headroom,((round(lead*RATE),round(trail*RATE)),(0,0))) for k,v in raw.items()}
    proof=dict(source_start_frame=a,source_end_frame=b,source_frames=len(source),source_seconds=len(source)/RATE,
        dry_seconds=length,dry_fade_relative=[start,stop],freeze_source_seconds=freeze_source,freeze_relative=freeze/RATE,
        field_filter_hz=[settings['highpass_hz'],settings['lowpass_hz']],prime_frames=len(prime),
        tail_extra=settings['tail_extra'],final_sound_source_relative_seconds=settings['source_in']+length+settings['tail_extra'],
        silence_context=[lead,trail],headroom_gain=headroom,headroom_db=20*np.log10(headroom),
        wet_initial_rms_before_envelope=target,wet_calibration_gains=gains,
        output_seconds=next(iter(final.values())).shape[0]/RATE,
        wet_fade_start_source_seconds=settings['source_in']+length+settings['hold_after_dry'],
        field_proof=field_proof,delay_samples=DELAYS.tolist(),matrix_orthogonality_error=float(np.max(np.abs(MATRIX@MATRIX.T-np.eye(16)))))
    return final,proof,dry,envelope
