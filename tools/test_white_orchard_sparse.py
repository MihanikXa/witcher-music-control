import copy
import unittest
from unittest.mock import Mock
import xml.etree.ElementTree as E

from white_orchard_sparse import validate, consumer_closure
from white_orchard_sparse_capture import cleanup


def field(node,name,value,typ='Real64'):
    props=node.find('PropertyList')
    if props is None:props=E.Element('PropertyList');node.insert(0,props)
    p=props.find("Property[@Name='%s']"%name)
    if p is None:p=E.SubElement(props,'Property',Name=name,Type=typ)
    p.set('Value',str(value))


def fixture():
    spec=dict(selected='selected',selected_short_id=133462974,parent='parent',phrase='phrase',rest='rest',
              playlist_root='playlist',music_item='music',rest_item='quiet',removed_group='drop',
              rest_loops=3,other_local_state_scopes=['other'])
    d=dict(facts={'world':{'id':'world'}},muted_states=['exploration','dialog_scene','boat'],
           static_targets=['selected','static'],game_state_group='group')
    original=E.Element('Root');world=E.SubElement(original,'MusicSwitchContainer',ID='world',ShortID='1')
    children=E.SubElement(world,'ChildrenList');parent=E.SubElement(children,'MusicSwitchContainer',ID='parent',ShortID='2')
    ch=E.SubElement(parent,'ChildrenList');sel=E.SubElement(ch,'MusicPlaylistContainer',ID='selected',ShortID='133462974')
    field(sel,'Volume',-2)
    refs=E.SubElement(sel,'ReferenceList');ref=E.SubElement(refs,'Reference',Name='PlaylistRoot')
    root=E.SubElement(E.SubElement(ref,'Custom'),'MusicPlaylistItem',ID='playlist',ShortID='3')
    leaves=E.SubElement(root,'ChildrenList')
    for ident in ('music','quiet'):
        leaf=E.SubElement(leaves,'MusicPlaylistItem',ID=ident,ShortID='4' if ident=='music' else '5')
        field(leaf,'PlaylistItemType',1,'int16')
        ref=E.SubElement(E.SubElement(leaf,'ReferenceList'),'Reference',Name='Segment')
        E.SubElement(ref,'ObjectRef',ID='phrase')
    E.SubElement(leaves,'MusicPlaylistItem',ID='drop',ShortID='6')
    E.SubElement(ch,'MusicPlaylistContainer',ID='static',ShortID='7')
    E.SubElement(ch,'MusicPlaylistContainer',ID='other',ShortID='8')
    entries=E.SubElement(E.SubElement(parent,'ObjectLists'),'ObjectList',Name='Entries')
    paths=['exploration','dialog_scene','cutscene','focus_exploration','underwater','boat','underwater_focus']
    for path in paths:
        entry=E.SubElement(E.SubElement(E.SubElement(entries,'Reference'),'Local'),'MultiSwitchEntry')
        target=E.SubElement(E.SubElement(entry,'ReferenceList'),'Reference',Name='AudioNode')
        E.SubElement(target,'ObjectRef',ID='selected',Name='generic')
        pathrefs=E.SubElement(E.SubElement(entry,'ObjectLists'),'ObjectList',Name='EntryPath')
        E.SubElement(E.SubElement(pathrefs,'Reference'),'ObjectRef',ID=path,Name=path)
    states={name:'global-'+name for name in paths+['combat']+['state'+str(i) for i in range(17)]}
    template=E.Element('StateInfo')
    E.SubElement(E.SubElement(template,'StatePropertyList'),'Property',Name='Volume')
    group=E.SubElement(E.SubElement(template,'StateGroupList'),'StateGroupInfo')
    E.SubElement(group,'StateGroupRef',ID='group')
    rows=E.SubElement(template,'CustomStateList')
    for i,(name,ident) in enumerate(states.items()):
        row=E.SubElement(rows,'CustomState');E.SubElement(row,'StateRef',Name=name,ID=ident)
        E.SubElement(row,'CustomState',ID='local'+str(i),ShortID=str(10000+i))
    return original,spec,d,states,template


def candidate(original,spec,d,states,template,mode):
    out=copy.deepcopy(original);objects={n.get('ID'):n for n in out.iter() if n.get('ID') and n.tag!='ObjectRef'}
    scopes=[] if mode=='native' else ['world'] if mode=='minimal' else ['selected','other']
    for index,ident in enumerate(scopes):
        info=copy.deepcopy(template)
        for i,row in enumerate(info.findall('./CustomStateList/CustomState')):
            local=row.find('CustomState');local.set('ID','new'+str(index)+'-'+str(i));local.set('ShortID',str(20000+100*index+i))
            muted=row.find('StateRef').get('Name') in d['muted_states']
            if mode=='sparse' and ident=='selected' and row.find('StateRef').get('Name')=='exploration':muted=False
            if muted:field(local,'Volume',-200)
        objects[ident].append(info)
    if mode!='native':
        for ident in d['static_targets']:
            if ident!='selected' or mode=='minimal':field(objects[ident],'Volume',-200)
    if mode=='sparse':
        field(objects['playlist'],'LoopCount',0,'int16')
        objects['playlist'].find('ChildrenList').remove(objects['drop'])
        objects['quiet'].find('./ReferenceList/Reference/ObjectRef').set('ID','rest')
        field(objects['quiet'],'LoopCount',3,'int16')
    return out


class SparseSourceTests(unittest.TestCase):
    def setUp(self):self.o,self.s,self.d,self.states,self.template=fixture()

    def verify(self,c,mode='sparse'):
        return validate(self.o,c,self.s,self.d,mode,self.states,self.template)

    def test_three_positive_controls(self):
        for mode in ('native','minimal','sparse'):
            self.assertTrue(self.verify(candidate(self.o,self.s,self.d,self.states,self.template,mode),mode)['passed'])

    def test_mutations_fail_closed(self):
        c=candidate(self.o,self.s,self.d,self.states,self.template,'sparse')
        def obj(t,ident):return next(n for n in t.iter() if n.get('ID')==ident and not n.tag.endswith('Ref'))
        changes=[lambda t:field(obj(t,'selected'),'Volume',-200),
                 lambda t:field(obj(t,'quiet'),'LoopCount',0,'int16'),
                 lambda t:field(obj(t,'quiet'),'Pitch',20),
                 lambda t:obj(t,'quiet').find('./ReferenceList/Reference/ObjectRef').set('ID','phrase'),
                 lambda t:field(obj(t,'static'),'Volume',-199),
                 lambda t:E.SubElement(obj(t,'phrase') if any(n.get('ID')=='phrase' and n.tag!='ObjectRef' for n in t.iter()) else t,'Extra'),
                 lambda t:obj(t,'selected').set('ShortID','99'),
                 lambda t:obj(t,'other').find('./StateInfo/CustomStateList/CustomState/StateRef').set('ID','wrong'),
                 lambda t:field(obj(t,'other').find('./StateInfo/CustomStateList/CustomState/CustomState'),'Pitch',42)]
        for change in changes:
            x=copy.deepcopy(c);change(x)
            with self.subTest(change=change),self.assertRaises(ValueError):self.verify(x)

    def test_cleanup_continues_after_error(self):
        api=Mock();api.call.side_effect=[RuntimeError('stop failure')]+[{}]*20
        errors=cleanup(api,True,[1,2])
        self.assertEqual(len(errors),1)
        self.assertEqual(api.call.call_count,8)

    def test_consumer_transition_event_closure(self):
        spec=dict(self.s,other_local_state_scopes=[]);d=dict(self.d,static_targets=[])
        event=E.Element('Events')
        self.assertEqual(consumer_closure(self.o,spec,d,[event])['event_work_units'],1)
        E.SubElement(event,'ObjectRef',ID='selected')
        with self.assertRaises(ValueError):consumer_closure(self.o,spec,d,[event])
        changed=copy.deepcopy(self.o);E.SubElement(changed,'TransitionObjectRef',ID='selected')
        with self.assertRaises(ValueError):consumer_closure(changed,spec,d,[])
        changed=copy.deepcopy(self.o)
        changed.find('.//MultiSwitchEntry/ObjectLists/ObjectList/Reference/ObjectRef').set('Name','combat')
        with self.assertRaises(ValueError):consumer_closure(changed,spec,d,[])


if __name__=='__main__':unittest.main()
