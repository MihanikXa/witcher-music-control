"""Executable policy examples for discussion, NOT a runtime ledger/integration.

Inputs are normalized test facts, not invented WitcherScript tags or API names.
No saved-state writes, inferred timestamps or item quality score.
"""
def decision(facts):
    if not facts.get('genuine_acquisition',True):return 'exclude','not-acquired'
    if facts.get('source')=='owned-transfer':return 'exclude','already-owned-transfer'
    if facts.get('auto_consumed_recipe'):return 'defer','needs-valid-target-link'
    if not facts.get('owned',True) or not facts.get('resolvable',True):return 'exclude','no-current-item'
    if not facts.get('inspectable',True):return 'defer','no-safe-action-target'
    if facts.get('routine_material') or facts.get('routine_refill'):return 'exclude','routine-accumulation'
    if facts.get('already_read'):return 'exclude','already-read'
    if facts.get('noteworthy_equipment'):return 'include','nonroutine-equipment'
    if facts.get('first_equippable_type'):return 'include','unfamiliar-equipment-type'
    if facts.get('unique_actionable_document'):return 'include','unread-unique-document'
    if facts.get('indistinct_common_equipment'):return 'exclude','common-equipment-noise'
    return 'defer','classification-not-established'

EXAMPLES=[
 ('hundredth celandine',dict(routine_material=True),('exclude','routine-accumulation')),
 ('rare nonroutine sword',dict(noteworthy_equipment=True),('include','nonroutine-equipment')),
 ('common junk sword',dict(indistinct_common_equipment=True),('exclude','common-equipment-noise')),
 ('first crossbow type',dict(first_equippable_type=True),('include','unfamiliar-equipment-type')),
 ('food refill',dict(routine_refill=True),('exclude','routine-accumulation')),
 ('learned diagram no owned row',dict(auto_consumed_recipe=True,owned=False),('defer','needs-valid-target-link')),
 ('unread unique letter',dict(unique_actionable_document=True),('include','unread-unique-document')),
 ('read book',dict(already_read=True),('exclude','already-read')),
 ('stashed sword returned',dict(source='owned-transfer',noteworthy_equipment=True),('exclude','already-owned-transfer')),
 ('sold pending sword',dict(owned=False,noteworthy_equipment=True),('exclude','no-current-item')),
 ('unresolved ID',dict(resolvable=False),('exclude','no-current-item')),
 ('unknown mod item',dict(),('defer','classification-not-established')),
]
if __name__=='__main__':
    import json
    print(json.dumps([dict(example=n,facts=f,proposed=decision(f)) for n,f,_ in EXAMPLES],indent=2))
