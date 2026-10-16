"""Private audition: bounded Wwise Opus 0x3041 -> Ogg, unchanged packets.

Independent container writer, not an audio decoder. Only observed stereo/mono
mapping-0 v1 streams; unknown layouts fail. RFC6716/7845/3533 container rules;
format evidence: vgmstream src/meta/wwise.c OPUSWW (read, not executed/copied).
No reference executables or Wwise sessions. Decode using a trusted local FFmpeg.
"""
import struct


def chunks(data):
    data=bytes(data)
    if len(data)<12 or data[:4]!=b'RIFF' or data[8:12]!=b'WAVE' or struct.unpack_from('<I',data,4)[0]+8!=len(data):
        raise ValueError('Complete little-endian RIFF required')
    out={};p=12
    while p<len(data):
        if p+8>len(data):raise ValueError('Truncated chunk')
        tag=data[p:p+4];n=struct.unpack_from('<I',data,p+4)[0];p+=8
        if tag in out or p+n>len(data):raise ValueError('Duplicate/truncated chunk')
        out[tag]=data[p:p+n];p+=n
        # Wwise permits an unpadded final odd data chunk; no bytes are invented.
        if n&1 and p<len(data):p+=1
    if p!=len(data):raise ValueError('Chunk alignment')
    return out


def packet_samples(packet):
    if not packet:raise ValueError('Empty Opus packet')
    config=packet[0]>>3;code=packet[0]&3
    frame=(120<<(config&3)) if config>=16 else ((480<<(config&1)) if config>=12 else (2880 if config&3==3 else 480<<(config&3)))
    if code==3 and len(packet)<2:raise ValueError('Missing frame count')
    count=(packet[1]&63) if code==3 else (1 if code==0 else 2)
    if not count or count*frame>5760:raise ValueError('Invalid Opus duration')
    return count*frame


def inspect(data):
    c=chunks(data);fmt=c[b'fmt ']
    if len(fmt)!=36:raise ValueError('Unsupported Opus fmt size')
    codec,channels,rate=struct.unpack_from('<HHI',fmt)
    samples,count,skip,version,mapping=struct.unpack_from('<IIHBB',fmt,24)
    if codec!=0x3041 or channels not in (1,2) or rate!=48000 or version!=1 or mapping!=0:
        raise ValueError('Unsupported Wwise Opus configuration')
    table=c[b'seek'];audio=c[b'data']
    if len(table)!=count*2 or not samples or not count:raise ValueError('Invalid seek table')
    sizes=struct.unpack('<'+'H'*count,table)
    if not all(sizes) or sum(sizes)!=len(audio):raise ValueError('Packet table/data mismatch')
    packets=[];p=0;total=0
    for size in sizes:
        packet=audio[p:p+size];p+=size;total+=packet_samples(packet);packets.append(packet)
    if not 0<=total-(samples+skip)<packet_samples(packets[-1]):raise ValueError('Inconsistent duration/end trim')
    return dict(channels=channels,rate=rate,samples=samples,skip=skip,packets=count,
                seconds=samples/rate),packets


CRC_TABLE=[]
for i in range(256):
    value=i<<24
    for _ in range(8):value=((value<<1)^0x04c11db7 if value&0x80000000 else value<<1)&0xffffffff
    CRC_TABLE.append(value)


def crc(data):
    value=0
    for byte in data:value=((value<<8)&0xffffffff)^CRC_TABLE[(value>>24)^byte]
    return value


def page(packet,index,granule,flags=0):
    laces=[255]*(len(packet)//255)+[len(packet)%255]
    if len(laces)>255:raise ValueError('Packet too large for bounded page writer')
    header=b'OggS'+bytes((0,flags))+struct.pack('<QIII',granule,1,index,0)+bytes((len(laces),))+bytes(laces)
    data=bytearray(header+packet);struct.pack_into('<I',data,22,crc(data));return bytes(data)


def rewrap(data):
    info,packets=inspect(data)
    head=b'OpusHead'+bytes((1,info['channels']))+struct.pack('<HIhB',info['skip'],48000,0,0)
    vendor=b'WMC private audition'
    tags=b'OpusTags'+struct.pack('<I',len(vendor))+vendor+struct.pack('<I',0)
    pages=[page(head,0,0,2),page(tags,1,0)];granule=0
    for index,packet in enumerate(packets):
        granule+=packet_samples(packet);last=index==len(packets)-1
        pages.append(page(packet,index+2,info['samples']+info['skip'] if last else granule,4 if last else 0))
    return b''.join(pages),info


def verify_rewrap(original,wrapped):
    """Independent readback of this bounded one-packet-per-page Ogg layout."""
    info,expected=inspect(original);packets=[];p=0;granules=[]
    while p<len(wrapped):
        if p+27>len(wrapped) or wrapped[p:p+5]!=b'OggS\0':raise ValueError('Invalid Ogg header')
        n=wrapped[p+26];table=wrapped[p+27:p+27+n]
        end=p+27+n+sum(table)
        if len(table)!=n or end>len(wrapped) or sum(v<255 for v in table)!=1 or table[-1]==255:
            raise ValueError('Unexpected packet/page bounds')
        raw=bytearray(wrapped[p:end]);checksum=struct.unpack_from('<I',raw,22)[0]
        struct.pack_into('<I',raw,22,0)
        if crc(raw)!=checksum:raise ValueError('Ogg checksum mismatch')
        if struct.unpack_from('<II',raw,14)!=(1,len(packets)):raise ValueError('Ogg serial/sequence mismatch')
        flags=2 if not packets else (4 if end==len(wrapped) else 0)
        if raw[5]!=flags:raise ValueError('Unexpected page flags')
        granules.append(struct.unpack_from('<Q',raw,6)[0]);packets.append(bytes(raw[27+n:]));p=end
    if packets[2:]!=expected:raise ValueError('Compressed audio packets changed')
    expected_head=b'OpusHead'+bytes((1,info['channels']))+struct.pack('<HIhB',info['skip'],48000,0,0)
    if packets[0]!=expected_head or not packets[1].startswith(b'OpusTags'):raise ValueError('Invalid Opus headers')
    total=0;wanted=[0,0]
    for i,packet in enumerate(expected):
        total+=packet_samples(packet)
        wanted.append(info['samples']+info['skip'] if i==len(expected)-1 else total)
    if granules!=wanted:raise ValueError('Granule/end-trim mismatch')
    return dict(passed=True,packets_exact=len(expected),samples=info['samples'])
