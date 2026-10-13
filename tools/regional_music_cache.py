"""Read-only exact expected-entry/payload gate for native CS3W caches.

Single-entry native format is demonstrated; synthetic multi-entry controls are
not proof of a new multi-bank cooker build. Never packages Init or loose WEMs.
"""
import hashlib
import struct

from music_region_inventory import REGIONS


def verify_bytes(data, expected):
    if not expected or any(name not in {r+'.bnk' for r in REGIONS} for name in expected):
        raise ValueError('Only explicit regional bank names allowed; no Init/media')
    if len(data) < 64 or data[:8] != b'CS3W\x02\0\0\0':
        raise ValueError('Unexpected native cache header')
    count = struct.unpack_from('<I', data, 24)[0]
    start = struct.unpack_from('<Q', data, 32)[0]
    size = struct.unpack_from('<I', data, 40)[0]
    if count != len(expected) or start < 64 or start+size+count*24 != len(data):
        raise ValueError('Entry count/table bounds differ')
    entries, intervals = {}, []
    for i in range(count):
        name_offset, offset, length = struct.unpack_from('<QQQ', data, start+size+i*24)
        if name_offset >= size or offset < 64 or offset+length > start:
            raise ValueError('Invalid entry bounds')
        tail = data[start+name_offset:start+size]
        if b'\0' not in tail:
            raise ValueError('Unterminated cache name')
        name = tail.split(b'\0',1)[0].decode('ascii')
        if name in entries or name not in expected or data[offset:offset+length] != expected[name]:
            raise ValueError('Unexpected/duplicate entry or changed payload')
        if any(offset < end and begin < offset+length for begin,end in intervals):
            raise ValueError('Overlapping cache payloads')
        intervals.append((offset,offset+length))
        entries[name]={'offset':offset,'bytes':length,
                       'sha256':hashlib.sha256(expected[name]).hexdigest()}
    if set(entries) != set(expected):
        raise ValueError('Missing expected bank')
    return {'passed':True,'entries':entries,'init_present':False,
            'cache_sha256':hashlib.sha256(data).hexdigest()}
