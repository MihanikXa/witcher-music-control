"""Apply a narrow settings delta to an offline copy; refuses live input overwrite."""
import argparse,difflib,json,re
from pathlib import Path

def transform(text,delta):
 lines=text.splitlines(keepends=True);sections={};section=None
 for i,line in enumerate(lines):
  m=re.match(r'\s*\[([^]]+)\]',line)
  if m:section=m[1];sections.setdefault(section,[])
  elif section:sections[section].append(i)
 added=[]
 for group,items in delta.items():
  if group not in sections:
   added+=['\n['+group+']\n']+[k+'='+v+'\n' for k,v in items.items()];continue
  pending=[]
  for key,value in items.items():
   found=[i for i in sections[group] if re.match(r'^\s*'+re.escape(key)+r'\s*=',lines[i])]
   assert len(found)<=1,('Duplicate setting',group,key)
   if found:
    i=found[0];old=lines[i].split('=',1)[1].strip()
    # Essential binding patch adds only vacant keys, never replaces an assignment.
    if key.startswith('IK_') and old!=value:continue
    lines[i]=key+'='+value+'\n'
   else:pending.append(key+'='+value+'\n')
  if pending:
   m=next(i for i,l in enumerate(lines) if re.match(r'\s*\['+re.escape(group)+r'\]',l));lines[m]+=''.join(pending)
 return ''.join(lines+added)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--delta',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 source=a.input.resolve();target=a.output.resolve();assert source!=target,'Use an offline output path'
 here=Path(__file__).resolve().parent
 # In the release copy, all generated outputs must stay in that release folder.
 assert here in target.parents,'Output must remain beside/below this helper'
 assert not target.is_symlink()
 old=source.read_text(encoding='utf-8-sig');delta=json.loads(a.delta.read_text());new=transform(old,delta)
 target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf-8',newline='\r\n')
 target.with_suffix(target.suffix+'.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(source),tofile=str(target))),encoding='utf-8')
 print('Prepared offline copy:',target,'Review the .diff; occupied IK_ keys were preserved.')
if __name__=='__main__':main()
