"""Read-only HUD movie/WS contract inventory; no source extracts in Git.

Run after JPEXS module-class exports in build/ink-hud-probe. Names and signatures
are evidence only: a matching name does not prove callback semantics at runtime.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', ROOT/'tools/audit-ui.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def symbols(tags):
    result = {}
    for code, payload in tags:
        if code != 76:
            continue
        count = struct.unpack_from('<H', payload)[0]
        pos = 2
        for _ in range(count):
            ident = struct.unpack_from('<H', payload, pos)[0]
            pos += 2
            end = payload.index(0, pos)
            name = payload[pos:end].decode()
            if name in result:
                raise ValueError('Duplicate SymbolClass name')
            result[name] = ident
            pos = end+1
        if pos != len(payload):
            raise ValueError('SymbolClass bounds differ')
    return result


def signatures(text):
    return {m[0]: {'parameters':m[1], 'returns':m[2]} for m in re.findall(
        r'public function\s+(\w+)\s*\(([^)]*)\)\s*:\s*([\w*]+)', text)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    components = [('bars','wolfstatbars','WolfHead'), ('buffs','buffs','Buffs'),
                  ('quests','quests','Quests'), ('minimap2','minimap2','Minimap2'),
                  ('enemyfocus','enemyfocus','EnemyFocus'), ('interactions','interactions','Interactions')]
    report = {}
    for folder, movie, native in components:
        root = ROOT/'build/ink-hud-probe'/('ink-'+folder)/'scripts'
        resource = ROOT/'build/ink-and-iron-0.8-audit/payloads/modInkAndIronHUD/gameplay/gui_new/swf/hud'/('hud_'+movie+'.redswf')
        data = resource.read_bytes()
        tags = audit.swf_tags(data)[2]
        functions = {}
        sources = []
        for p in root.rglob('*.as'):
            functions.update(signatures(p.read_text()))
            sources.append({'path':str(p.resolve()), 'sha256':audit.sha(p.read_bytes())})
        ws = a.game/'Mods/modFriendlyHUD/content/scripts/game/gui/hud/modules'/('hudModule'+native+'.ws')
        text = ws.read_text(encoding='utf-8-sig')
        required = sorted(set(re.findall(r'GetMemberFlashFunction\(\s*"([^"]+)"', text)))
        imports = []
        for code, payload in tags:
            if code in (57,71):
                imports.append(payload.split(b'\0',1)[0].decode(errors='replace'))
        report[movie] = dict(resource_key='gameplay/gui_new/swf/hud/hud_'+movie+'.redswf',
            resource_sha256=audit.sha(data), symbol_classes=symbols(tags), imports=imports,
            abc_sha256=[audit.sha(p) for c,p in tags if c==82], public_signatures=functions,
            native_provider=str(ws.resolve()), native_provider_sha256=audit.sha(ws.read_bytes()),
            native_bound_functions=required, bindings_not_in_exported_module_classes=sorted(set(required)-set(functions)),
            private_decompiler_inputs=sources,
            limitation='Top-level/public module inventory; nested renderers and data listeners need separate checks')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2))
    print(json.dumps({k:{'bindings':len(v['native_bound_functions']),
                        'unresolved':v['bindings_not_in_exported_module_classes'],
                        'imports':v['imports']} for k,v in report.items()}, indent=2))


if __name__ == '__main__':
    main()
