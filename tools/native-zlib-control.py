"""Standard zlib build adapter; native identity controls remain mandatory.

The local CPython build uses zlib-ng, whose valid Deflate output differs from
WCC's standard zlib stream. Never silently weaken byte-identical controls.
"""
import ctypes,hashlib,json,os
from pathlib import Path
DLL=Path(os.environ.get('INVENTORY_ZLIB_DLL',r'C:\Program Files\Git\mingw64\bin\zlib1.dll'))
_library=None
def library():
    global _library
    if _library is None:
        _library=ctypes.CDLL(str(DLL))
        _library.compressBound.argtypes=[ctypes.c_ulong];_library.compressBound.restype=ctypes.c_ulong
        _library.compress2.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong),ctypes.c_void_p,ctypes.c_ulong,ctypes.c_int];_library.compress2.restype=ctypes.c_int
        _library.zlibVersion.restype=ctypes.c_char_p
    return _library
def compress(data,level=9):
    api=library();size=ctypes.c_ulong(api.compressBound(len(data)));result=ctypes.create_string_buffer(size.value)
    if api.compress2(result,ctypes.byref(size),data,len(data),level)!=0:raise ValueError('zlib compress2 failed')
    return result.raw[:size.value]
def version():return library().zlibVersion().decode()+'; DLL SHA-256 '+hashlib.sha256(DLL.read_bytes()).hexdigest()
if __name__=='__main__':
    import importlib.util
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('build',root/'tools/build-approved-inventory.py');build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
    rows=[]
    for name in ('ink-gear-grid-v1-focus','ink-gear-grid-v1-final'):
        bundle=root/'build'/name/'packed/blob0.bundle';raw=bundle.read_bytes();data=build.b.b.m.b.bars.extract(bundle,build.KEY)
        rows.append(dict(control=name,compressed_identity=compress(data)==raw[336:]))
    print(json.dumps(dict(version=version(),controls=rows),indent=2))
    if not all(row['compressed_identity'] for row in rows):raise ValueError('Native compressor identity control failed')
