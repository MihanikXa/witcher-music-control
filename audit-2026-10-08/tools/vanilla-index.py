# Machine-specific paths are example inputs from the audited installation; adapt before reuse.
"""Index vanilla bundles without extracting or altering them; include current game's baseline."""
from inventory import *
def main():
 entries=[];errors=[]
 for p in (GAME/'content').rglob('*.bundle'):
  try:entries.extend(dict(x,owner=str(p.relative_to(GAME/'content'))) for x in bundles(p))
  except Exception as ex:errors.append(str(ex))
 installed=json.loads((ROOT/'evidence/bundle-entries.json').read_text());names=set(x['resource'] for x in installed)
 relevant=[x for x in entries if x['resource'] in names]
 save('vanilla-mod-overrides.json',relevant);save('vanilla-bundle-errors.json',errors)
 save('vanilla-index-summary.json',dict(entries=len(entries),modded_resources=len(names),overridden_vanilla_resources=len(set(x['resource'] for x in relevant)),errors=errors))
 print(json.dumps(dict(entries=len(entries),modded_resources=len(names),overridden_vanilla_resources=len(set(x['resource'] for x in relevant)),errors=errors)))
 # Retain only a private vanilla baseline for actual shared resources and old weight XML.
 c=json.loads((ROOT/'evidence/bundled-collisions.json').read_text());wanted=set(c)|{'gameplay/abilities/geralt_stats.xml','gameplay/abilities_plus/geralt_stats.xml'}
 candidates=[x for x in entries if x['resource'] in wanted];save('vanilla-collision-baselines.json',candidates)
if __name__=='__main__':main()
