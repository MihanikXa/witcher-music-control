"""Read-only PE evidence for this retail build's native LogChannel binding.

Finds registration-pattern candidates, not a general x64 disassembler. Confirm
reported ranges with the installed Microsoft dumpbin. Unknown layouts fail shut.
Never executes, maps into a process, patches, or installs the examined image.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
import struct


class PE:
    def __init__(self,data):
        self.data=data
        if len(data)<64 or data[:2]!=b'MZ':raise ValueError('Not PE')
        p=self.u32(60)
        if self.bytes(p,4)!=b'PE\0\0' or self.u16(p+4)!=0x8664:raise ValueError('Not AMD64 PE')
        o=p+24
        if self.u16(o)!=0x20b:raise ValueError('Not PE32+')
        self.base=self.u64(o+24);self.directories=o+112;self.sections=[]
        h=o+self.u16(p+20)
        for i in range(self.u16(p+6)):
            a=h+40*i
            self.sections.append(dict(name=self.bytes(a,8).rstrip(b'\0').decode('ascii'),
                rva=self.u32(a+12),raw=self.u32(a+20),size=self.u32(a+16),flags=self.u32(a+36)))
        for s in self.sections:self.bytes(s['raw'],s['size'])

    def bytes(self,o,n):
        if o<0 or n<0 or o+n>len(self.data):raise ValueError('PE bounds')
        return self.data[o:o+n]
    def u16(self,o):return struct.unpack('<H',self.bytes(o,2))[0]
    def u32(self,o):return struct.unpack('<I',self.bytes(o,4))[0]
    def u64(self,o):return struct.unpack('<Q',self.bytes(o,8))[0]
    def section(self,rva):
        for s in self.sections:
            if s['rva']<=rva<s['rva']+s['size']:return s
        raise ValueError('Unmapped RVA')
    def off(self,rva):
        s=self.section(rva);return s['raw']+rva-s['rva']
    def rva(self,off):
        for s in self.sections:
            if s['raw']<=off<s['raw']+s['size']:return s['rva']+off-s['raw']
        raise ValueError('Unmapped raw offset')
    def rel(self,rva,length,displacement_offset):
        return rva+length+struct.unpack('<i',self.bytes(self.off(rva)+displacement_offset,4))[0]
    def function(self,rva):
        start=self.u32(self.directories+3*8);size=self.u32(self.directories+3*8+4)
        if size%12:raise ValueError('Malformed exception table')
        raw=self.off(start);ranges=[]
        for a in range(raw,raw+size,12):
            lo,hi,_=struct.unpack('<III',self.bytes(a,12));ranges.append((lo,hi))
        i=bisect.bisect_right([r[0] for r in ranges],rva)-1
        if i<0 or not ranges[i][0]<=rva<ranges[i][1]:raise ValueError('No function boundary')
        return ranges[i]


def audit(path):
    data=path.read_bytes();p=PE(data)
    strings=[m.start()+1 for m in re.finditer(b'\0LogChannel\0',data)]
    text=next(s for s in p.sections if s['name']=='.text');code=p.bytes(text['raw'],text['size'])
    refs=[]
    for off in strings:
        target=p.rva(off)
        for m in re.finditer(b'\x48\x8d\x15',code):
            rva=text['rva']+m.start()
            if p.rel(rva,7,3)!=target:continue
            tail=p.bytes(p.off(rva)+7,32)
            # Registration supplies native handler as r8, after string/name lookup.
            if tail[8:11]!=b'\x4c\x8d\x05':continue
            fn=p.rel(rva+15,7,3);lo,hi=p.function(fn)
            if lo!=fn:raise ValueError('Handler not a function start')
            calls=[]
            for c in re.finditer(b'\xff\x15',p.bytes(p.off(lo),hi-lo)):
                call=lo+c.start();slot=p.rel(call,6,2);dest=p.u64(p.off(slot))-p.base
                if p.section(dest)['flags']&0x20000000==0:raise ValueError('Non-code dispatch target')
                calls.append(dict(call_rva=call,slot_rva=slot,slot_readonly=not bool(p.section(slot)['flags']&0x80000000),
                                  destination_rva=dest,destination_prefix=p.bytes(p.off(dest),3).hex()))
            refs.append(dict(string_rva=target,registration_rva=rva,handler_range=[lo,hi],dispatch=calls))
    if len(refs)!=1 or len(refs[0]['dispatch'])!=1:raise ValueError('Unknown native logging layout')
    call=refs[0]['dispatch'][0]
    if call['destination_prefix']!='c20000':raise ValueError('Not the observed initial fallback')
    # Crucial: default no-op is NOT permanent. Native startup writes the slot.
    writes=[]
    for m in re.finditer(b'[\x48\x4c]\x89[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]',code):
        rva=text['rva']+m.start()
        if p.rel(rva,7,3)==call['slot_rva']:writes.append(rva)
    if not writes:raise ValueError('Runtime logger writer not found')
    return dict(schema=1,sha256=hashlib.sha256(data).hexdigest(),image_base=p.base,
        finding='LogChannel initially dispatches to no-op through writable slot; native startup can rebind it. Initial stub alone does NOT prove logging disabled.',
        runtime_hooking_excluded=True,retail_observed=False,registration=refs[0],native_slot_writes=writes,
        verified_image_layout=file_logger_layout(p,hashlib.sha256(data).hexdigest()))


IMAGE_SHA='2df765398a3d1f165db418271be7200178320a4466817379f2fa0dc0001fb101'


def file_logger_layout(p,sha):
    """Version-pinned observations independently confirmed using dumpbin output.

    Other builds must be traced again; do not transplant offsets or flags.
    """
    if sha!=IMAGE_SHA:raise ValueError('Unreviewed retail image for file-logger layout')
    def string(rva):
        raw=p.bytes(p.off(rva),80);return raw.split(b'\0',1)[0].decode('ascii')
    def binding(node,group,key,value):
        if p.u64(p.off(node+8))!=p.base+group or p.u64(p.off(node+16))!=p.base+key or p.u64(p.off(node+32))!=p.base+value:
            raise ValueError('Config storage layout changed')
        return dict(group=string(group),key=string(key),node_rva=node,value_rva=value)
    fields=[binding(0x5149218,0x35c7940,0x35c7930,0x5149248),
            binding(0x5149250,0x35c7970,0x35c7958,0x5149280),
            dict(group=string(0x35c7928),key=string(0x35c7910),node_rva=0x5c05f80,value_rva=0x5c05fb8,storage='BSS initialized by native constructor 0x1cd3ca..0x1cd42c')]
    for instruction,target in [(0x1cd3ca,0x35c7928),(0x1cd3da,0x5c05f88),(0x1cd3e7,0x35c7910),(0x1cd3f9,0x5c05f90),(0x1cd41c,0x5c05fb8),(0x1cd425,0x5c05fa0)]:
        if p.rel(instruction,7,3)!=target:raise ValueError('String config constructor changed')
    if p.bytes(p.off(0x2287e89),3)!=b'\x48\x8d\x3d' or p.rel(0x2287e89,7,3)!=0x22880f0:
        raise ValueError('Logger initializer changed')
    if p.rel(0x2287e95,7,3)!=0x405baa0:raise ValueError('Logger dispatch assignment changed')
    if string(0x35c78f8)!='scriptslog.txt' or string(0x35c7908)!='w':raise ValueError('File naming/mode changed')
    if p.rel(0x2288669,5,1)!=0x1aa6b20:raise ValueError('CRT file-open path changed')
    return dict(config=fields,initializer_rva=0x2287e60,startup_call_rva=0x2286703,
        callback_rva=0x22880f0,callback_assignment_rva=0x2287e95,filename='scriptslog.txt',open_mode='w',
        append_filename_instructions=[0x2288553,0x2288620],file_open_rva=0x2288669,
        line_format='[channel] text + newline',force_flush_branch_rva=0x2288213,
        native_guard='Initializer skips when byte at engine-global+0x17c is nonzero; meaning/runtime value not established.',
        operating_status='Static complete native file path. Retail execution/config delivery requires user smoke test, not DebugView.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('image',type=Path);ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();root=Path(__file__).resolve().parents[1]/'build'
    if not a.output.resolve().is_relative_to(root.resolve()) or a.output.exists():raise ValueError('Fresh private build output')
    r=audit(a.image);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
