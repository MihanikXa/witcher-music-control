"""Read-only review of the bounded observer/request pilot; no runtime claims."""
import json
from pathlib import Path

from sparse_approved_cue import REPO,verify_accepted,read
from sparse_observer_build import SOURCE,KIT,diagnostics
from sparse_request_probe import source_proof
from white_orchard_prepare import digest

ROOT=REPO/'build/sparse-live-context-pilot-v1'


def review():
    obs=ROOT/'observer';ww=ROOT/'wwise-request/candidate/validation'
    baseline=read(obs/'baseline-v5.result.json');candidate=read(obs/'candidate-v1.result.json')
    control=read(obs/'matched-control.result.json')
    for r in (baseline,candidate,control):
        if not r['compiled'] or r['exit_code'] or r['timeout']:raise ValueError('Failed compiler proof')
    if candidate['source_sha256']!=digest(SOURCE):raise ValueError('Compiled source drift')
    if candidate['blob_sha256']!=digest(obs/'candidate-v1/blob.rsblob'):raise ValueError('Compiled blob drift')
    if candidate['diagnostics']!=control['diagnostics']:raise ValueError('Matched declaration control differs')
    a=baseline['diagnostics'];b=candidate['diagnostics']
    delta={k:b.get(k,0)-a.get(k,0) for k in set(a)|set(b) if b.get(k,0)!=a.get(k,0)}
    if len(delta)!=1 or list(delta.values())!=[8] or 'scriptCompiledCode.cpp:56' not in next(iter(delta)):
        raise ValueError('Unreviewed compiler diagnostics')
    installed=set(p.relative_to(KIT/'r4data/scripts') for p in (KIT/'r4data/scripts').rglob('*.ws'))
    local=set(p.relative_to(obs/'base') for p in (obs/'base').rglob('*.ws'))
    if installed!=local:raise ValueError('Incomplete pristine script context')
    for rel in local:
        if digest(obs/'base'/rel)!=digest(KIT/'r4data/scripts'/rel):raise ValueError('Base script changed')
    runtime=read(obs/'inputs.json')['runtime']
    for item in runtime:
        if (digest(obs/'runtime'/item['file'])!=item['sha256'] or
                digest(KIT/'bin/x64_RedKit'/item['file'])!=item['sha256']):
            raise ValueError('Native compiler runtime input changed')
    verify_accepted();old=read(REPO/'build/sparse-context-audit-v1/preservation.json')
    for name,sha in old['retained_release_inputs'].items():
        p=Path(name) if Path(name).is_absolute() else REPO/name
        if digest(p)!=sha:raise ValueError('Retained release/native input drift')
    banks=list((REPO/'build/sparse-approved-cue-pilot-v1').rglob('music_prologue.bnk'))
    if not any(digest(p)==old['retained_report88_bank'] for p in banks):raise ValueError('Report88 bank missing')
    # All five original report90 snapshots remain pinned by their own prior gate.
    old_gate=read(REPO/'build/sparse-reentry-pilot-v1/source-gate-final-v3.json')
    # Preserve full evidence hash; the individual clone hashes are verified below
    # using only the actual music source records, not licensed project metadata.
    def pins(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if isinstance(v,str) and len(v)==64 and ('music' in k.lower() or 'sha256' in k.lower()):
                    yield k,v
                else:yield from pins(v)
        elif isinstance(value,list):
            for v in value:yield from pins(v)
    retained_music={digest(p) for p in (REPO/'build/sparse-reentry-pilot-v1').glob('*/validation/Interactive Music Hierarchy/music.wwu')}
    prior_hashes={v for _,v in pins(old_gate)}
    if not retained_music or not retained_music<=prior_hashes:raise ValueError('Report90 source proof drift')
    source=source_proof(ww/'w3_audio.wproj')
    measured=read(ww/'measurements.json');captures=[]
    for c in measured:
        path=ww/'request-general-captures'/(c['case']+'.wav')
        if digest(path)!=c['wav_sha256']:raise ValueError('Capture drift')
        captures.append(dict(case=c['case'],rtpcs=c['profiler']['rtpcs'],pcm={k:v for k,v in c['pcm'].items() if k!='rms50ms'},
            pipelines=[{k:p[k] for k in ('role','first','last','peak')} for p in c['profiler']['pipelines']]))
    lifecycle=read(ww/'request-general-lifecycle.json')
    if not lifecycle['source_unchanged'] or lifecycle['cleanup_errors']:raise ValueError('Request cleanup failed')
    return dict(schema=1,date='2026-10-19',observer_source_sha256=digest(SOURCE),
        observer_compiled=True,compiler_sha256=digest(obs/'runtime/wcc_lite.exe'),
        compiler_exit_codes=[baseline['exit_code'],candidate['exit_code'],control['exit_code']],
        pristine_script_files=len(local),candidate_blob_sha256=candidate['blob_sha256'],
        compiler_assert_counts={label:sum(v for k,v in d.items() if '[Error][Assert]' in k)
            for label,d in [('baseline',a),('candidate',b),('matched_declaration_control',control['diagnostics'])]},
        compiler_diagnostic_review='Only native scriptCompiledCode.cpp:56 count+8; exact same diagnostics in matched wrapper/API control.',
        compiled_full_merged_mods=False,retail_log_sink_verified=False,retail_observed=False,
        preservation=dict(approved24_exact=True,ten_release_native_inputs_exact=True,
            report88_bank_exact=True,report90_music_hashes_exact=True,native_compiler_runtime_inputs_exact=len(runtime)),
        wwise=dict(version='2023.1.19.8928',source_proof=source,captures=captures,
            protected_request_gate_proven=False,
            first_candidate='Selected-playlist Seek reference rejected by actual authoring engine.',
            second_candidate='Parent MusicSwitch Seek did not produce request-driven cue acceptance.',
            warnings=['WAMP port bind warning retained; HTTP exact project/version checked.',
                      'WwiseConsole exit1 follows explicit project.close; capture script exited0.'],
            lifecycle={k:lifecycle[k] for k in ['source_before','source_after','source_unchanged','cleanup_errors','process_exit']}),
        artifacts={str(p.relative_to(REPO)):digest(p) for p in [obs/'baseline-v5.full.log',
            obs/'candidate-v1.full.log',obs/'matched-control.full.log',ww/'request-general-captures/results.json',
            ROOT/'tests-final.log']})


if __name__=='__main__':
    out=ROOT/'review.json'
    if out.exists():raise FileExistsError(out)
    result=review();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Observer compiled; request gate NOT proven. Preserved inputs verified.')
