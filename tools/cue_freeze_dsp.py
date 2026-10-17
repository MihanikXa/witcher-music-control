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


def envelope_windows(audio, seconds=.05):
    """Ungated stereo RMS; no peak normalization or assumption about musical dynamics."""
    n=round(seconds*RATE)
    return np.array([np.sqrt(np.mean(audio[a:a+n]**2)) for a in range(0,len(audio),n)])


def release_diagnostics(audio, stop_seconds):
    """Flag *post-source* envelope geometry. Musical evolution before stop is not a failure.

    Modal fluctuations are expected: inspect 250ms RMS, only above -80dBFS,
    sustained rebounds over 3dB and long, nearly flat windows. These are review
    flags, not a musical-quality classifier. Internal energy is checked separately.
    """
    x=audio[round(stop_seconds*RATE):]
    db=20*np.log10(np.maximum(envelope_windows(x,.25),1e-12))
    rebound=0.;plateaus=[]
    for i in range(len(db)-4):
        if db[i]>-80:
            rebound=max(rebound,float(np.mean(db[i+2:i+4])-db[i]))
        if i+8<=len(db) and min(db[i:i+8])>-80:
            slope=float(np.polyfit(np.arange(8)*.25,db[i:i+8],1)[0])
            if np.ptp(db[i:i+8])<1.5 and abs(slope)<.5:plateaus.append(i*.25)
    return dict(max_sustained_rebound_db=rebound,rebound_review=rebound>3,
                plateau_window_starts=plateaus,post_stop_250ms_dbfs=db.tolist())


def validate_wet_control(gain,stop,freeze):
    """Test the processor's gain law, separately from legitimate musical dynamics."""
    if not np.isfinite(gain).all() or len(gain)<=stop+RATE:raise ValueError('Invalid wet control')
    if not np.array_equal(gain[:stop],np.ones(stop)):raise ValueError('Late wet attack/level change before source stop')
    if not freeze:
        if not np.array_equal(gain,np.ones(len(gain))):raise ValueError('Artificial conventional hold/fade')
    else:
        r=gain[stop:]
        if r[0]!=1 or np.any(np.diff(r)>1e-12):raise ValueError('Wet release rebounds')
        # Beyond smooth 150ms entry it must already fall, not wait for a later fade.
        if np.any(np.diff(r[round(.2*RATE)::round(.05*RATE)])>=0):raise ValueError('Freeze release plateau')
    return dict(no_late_wet_attack=True,no_wet_gain_rebound=True,no_post_stop_hold=True,
                independent_secondary_fade=False)


def finish_quiet_tail(raw):
    """Only below -100dBFS peak may finite-file termination be safety-ramped."""
    cleanup=round(.1*RATE)
    if len(raw)<cleanup or not np.isfinite(raw).all():raise ValueError('Invalid cleanup signal')
    peak=float(np.max(np.abs(raw[-cleanup:])))
    if peak>1e-5:raise ValueError('Tail not silent enough for safety cleanup; extend actual render')
    raw[-cleanup:]*=(1-ramp(cleanup))[:,None]
    return peak


def render_continuous(source, settings, rt60, freeze=False, wet_gain=None, lead=2, trail=3):
    """V2: continuous post-fader send; natural decay or immediate single freeze release.

    Kept separate from render_variants so accepted v1 files remain reproducible.
    No late wet normalization, attack, hold, sidechain or perceptual auto-correction.
    Freeze occurs at actual dry stop, not at the beginning of a changing phrase's fade.
    """
    if source.ndim!=2 or source.shape[1]!=2 or not np.isfinite(source).all():raise ValueError('Finite stereo required')
    a,b=round(settings['source_in']*RATE),round(settings['source_out']*RATE)
    if not 0<=a<b<=len(source):raise ValueError('Invalid source cut')
    segment=source[a:b].copy();length=len(segment)/RATE
    fs,fe=[v-settings['source_in'] for v in settings['dry_fade']]
    env=dry_envelope(len(segment),RATE,settings['fade_in'],fs,fe)
    onset=settings.get('onset_mute_seconds',0)
    if onset:
        n=round(onset*RATE);r=round(settings.get('onset_ramp_seconds',.35)*RATE)
        if n+r>=round(fs*RATE):raise ValueError('Onset repair overlaps ending')
        env[:n]=0;env[n:n+r]*=ramp(r)
    dry=segment*env[:,None]
    # Render at least 90dB of decay. Cleanup only below -100dBFS peak.
    extra=max(10,rt60*1.65)
    frames=len(dry)+round(extra*RATE)
    padded=np.zeros((frames,2));padded[:len(dry)]=dry
    hp,lp=settings['highpass_hz'],settings['lowpass_hz']
    if not 80<=hp<lp<=8000:raise ValueError('Unsafe field bandwidth')
    sos=np.concatenate([signal.butter(2,hp,'highpass',fs=RATE,output='sos'),
                        signal.butter(2,lp,'lowpass',fs=RATE,output='sos')])
    filtered=signal.sosfilt(sos,padded,axis=0)
    field=Field(rt60)
    # Both modes have exactly the same audible field before dry stop.
    stop=round(fe*RATE)
    before,_=field.process(filtered[:stop]);initial=field.energy()
    drive=np.zeros_like(filtered[stop:]) if freeze else filtered[stop:]
    after,trace=field.process(drive,freeze=freeze,transition=.15,ledger=True)
    wet=np.concatenate([before,after])
    calibration=slice(max(round((fs-4)*RATE),round((onset+1)*RATE)),round(fs*RATE))
    if len(dry[calibration])<RATE//4:raise ValueError('Insufficient pre-fade calibration')
    if wet_gain is None:
        ref=np.sqrt(np.mean(dry[calibration]**2));wrms=np.sqrt(np.mean(wet[calibration]**2))
        if min(ref,wrms)<1e-9:raise ValueError('Cannot calibrate empty field')
        wet_gain=ref*10**(settings['continuous_wet_db']/20)/wrms
    if not 0<wet_gain<4:raise ValueError('Unsafe send gain')
    release=np.ones(frames)
    if freeze:
        # No plateau. Smooth log-gain release reaches exponential -60dB at RT60.
        t=np.arange(frames-stop)/RATE;tau=.15
        clock=t-tau*(1-np.exp(-t/tau))
        release[stop:]=10**(-3*clock/rt60)
    controls=validate_wet_control(release,stop,freeze)
    wet*=wet_gain*release[:,None]
    raw=padded+wet
    quiet_peak=finish_quiet_tail(raw)
    peak=float(np.max(np.abs(raw)))
    if peak>.96:raise ValueError('Requires explicitly shared headroom reduction; do not normalize variants separately')
    energy=[r['state_energy'] for r in trace if r['seconds']>.2]
    if not energy or initial<1e-20:raise ValueError('Missing established reverb field')
    drift=(max(energy)-min(energy))/max(energy)
    if freeze and drift>1e-10:raise ValueError('Freeze state not stable')
    if not freeze and energy[-1]>=initial*1e-8:raise ValueError('Natural decay insufficient')
    win={k:envelope_windows(v).tolist() for k,v in [('dry',padded),('wet',wet),('combined',raw)]}
    seam=float(np.max(np.abs(np.diff(raw[max(0,stop-128):stop+128],axis=0))))
    proof=dict(source_start_frame=a,source_end_frame=b,dry_seconds=length,dry_stop_relative=fe,
        rt60=rt60,freeze=freeze,freeze_relative=fe if freeze else None,wet_gain=float(wet_gain),
        output_seconds=(frames/RATE+lead+trail),tail_extra=extra,onset_mute_seconds=onset,
        wet_output_policy='constant gain throughout; no late entrance or hold',
        release_policy='single immediate smooth exponential release' if freeze else 'unmodified natural RT60 decay',
        cleanup_peak_dbfs=float(20*np.log10(max(quiet_peak,1e-12))),cleanup_seconds=.1,
        dry_stop_max_sample_delta=seam,energy_trace=trace,initial_energy=initial,
        settled_energy_relative_range=drift,windows_50ms=win,
        wet_control_checks=controls,
        entire_transition_geometry=release_diagnostics(raw,max(0,fs-1)),
        release_diagnostics=release_diagnostics(raw,fe),
        post_stop_first_second_dbfs=float(20*np.log10(max(np.sqrt(np.mean(raw[stop:stop+RATE]**2)),1e-12))))
    components=dict(dry=padded,wet=wet,source_envelope=env)
    return np.pad(raw,((round(lead*RATE),round(trail*RATE)),(0,0))),proof,components
