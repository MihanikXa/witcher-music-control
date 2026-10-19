"""Stage, never install, a native logger probe; inspect only an explicit log.

No game launch, process attachment, DLL, debugger, Vortex, profile or save access.
Native logging/config activation remains a manual retail experiment.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/'build/sparse-interface-prerequisites-v1'
GENERAL=Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\bin\config\base\general.ini')


def config_bytes(original, directory):
    text=original.decode('utf-8-sig')
    if re.search(r'^\s*\[Scripts\]',text,re.I|re.M):
        raise ValueError('Existing Scripts group: manual merge/review required')
    path=directory.resolve().as_posix()+'/'
    if any(c in path for c in '\r\n[]='):raise ValueError('Unsafe config path')
    block=('\r\n[Scripts]\r\nLogDebugScripts=true\r\nDebugScriptsForceFlush=true\r\n'
           'DebugScriptsLogDir='+path+'\r\n').encode('utf-8')
    return original+block


def prepare():
    root=ROOT/'manual-logger-probe'
    if root.exists():raise FileExistsError('Preserve previous probe; do not overwrite')
    original=GENERAL.read_bytes();logs=ROOT/'retail-logs'
    modified=config_bytes(original,logs)
    root.mkdir(parents=True);logs.mkdir(exist_ok=True)
    (root/'general.ini.original').write_bytes(original)
    (root/'general.ini').write_bytes(modified)
    manifest=dict(schema=1,created_utc=datetime.now(timezone.utc).isoformat(),
        installed_file_modified=False,source=str(GENERAL),
        source_sha256=hashlib.sha256(original).hexdigest(),
        staged_sha256=hashlib.sha256(modified).hexdigest(),
        expected_log=str(logs/'scriptslog.txt'),
        runtime_delivery_verified=False,mode='Native fopen w truncates on each launch; preserve each capture before another launch.')
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


def inspect_log(path, started):
    """Bounded, read-only; never prints unrelated script text or infers no events.

    Input is a user-selected local file. Actual marker formatting is retained;
    normalization deliberately remains the existing fail-closed parser.
    """
    if started.tzinfo is None:raise ValueError('Timezone-aware probe start required')
    stat=path.stat()
    if stat.st_mtime<started.timestamp():raise ValueError('Stale log: not this probe')
    if stat.st_size>16*1024*1024:raise ValueError('Log exceeds bounded reader; retain privately for review')
    raw=path.read_bytes()
    header=b'Debugging scripts for ' in raw[:16384]
    rows=[]
    for line in raw.splitlines():
        if b'WMCCTX1|' not in line:continue
        if len(line)>4096:raise ValueError('Oversize diagnostic line')
        rows.append(line.decode('ascii'))
    result=dict(fresh=True,native_header_seen=header,wmc_rows=len(rows),
        log_sha256=hashlib.sha256(raw).hexdigest(),retail_marker_observed=bool(rows),
        observer_installation_inferred=False)
    if rows:
        from sparse_observer_trace import normalize
        normalized=normalize('\n'.join(rows))
        result.update(normalization_passed=True,records=len(normalized['observations']))
    return result,rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('prepare')
    check=sub.add_parser('check');check.add_argument('--log',type=Path,required=True)
    check.add_argument('--started',required=True,help='UTC ISO time recorded before user launch, e.g. 2026-10-19T12:34:56Z')
    check.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.command=='prepare':print(json.dumps(prepare(),indent=2))
    else:
        output=a.output.resolve()
        if not output.is_relative_to((REPO/'build').resolve()) or output.exists():raise ValueError('Fresh private build output required')
        result,rows=inspect_log(a.log,datetime.fromisoformat(a.started.replace('Z','+00:00')))
        output.mkdir(parents=True)
        (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        (output/'wmc-only.log').write_text('\n'.join(rows)+'\n',encoding='ascii')
        print(json.dumps(result,indent=2))
