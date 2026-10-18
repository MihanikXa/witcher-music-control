import copy
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as E

import numpy as np

from sparse_approved_cue import strip_wrapper,validate_import,read,SPEC
from white_orchard_prepare import digest


def fields(node,values):
    p=E.SubElement(node,'PropertyList')
    for name,value in values.items():E.SubElement(p,'Property',Name=name,Value=str(value),Type='Real64')


def fixture(folder):
    spec=read(SPEC);before=E.Element('Root')
    selected=E.SubElement(before,'MusicPlaylistContainer',ID=spec['selected'],ShortID='133462974')
    items=E.SubElement(selected,'Items');item=E.SubElement(items,'MusicPlaylistItem',ID=spec['music_item'])
    ref=E.SubElement(E.SubElement(item,'ReferenceList'),'Reference',Name='Segment');E.SubElement(ref,'ObjectRef',ID='old')
    E.SubElement(selected,'ChildrenList');E.SubElement(before,'MusicSegment',ID='old',ShortID='55')
    after=copy.deepcopy(before);selected=after.find('MusicPlaylistContainer')
    selected.find('.//ObjectRef').set('ID','newseg')
    seg=E.SubElement(selected.find('ChildrenList'),'MusicSegment',ID='newseg',ShortID='99',Name='WMC_S04a_approved')
    fields(seg,{'EndPosition':40850,'OverrideClockSettings':1,'Tempo':60})
    refs=E.SubElement(seg,'ReferenceList')
    for name,target in [('Conversion','{CD5FEB1F-5340-419B-B846-9C660D7A1B24}'),('OutputBus','{1514A4D8-1DA6-412A-A17E-75CA0C2149F3}')]:
        E.SubElement(E.SubElement(refs,'Reference',Name=name),'ObjectRef',ID=target)
    track=E.SubElement(E.SubElement(seg,'ChildrenList'),'MusicTrack',ID='newtrack',ShortID='100')
    refs=E.SubElement(track,'ReferenceList');E.SubElement(E.SubElement(refs,'Reference',Name='OutputBus'),'ObjectRef',ID='{1514A4D8-1DA6-412A-A17E-75CA0C2149F3}')
    root=E.SubElement(E.SubElement(E.SubElement(refs,'Reference',Name='TransitionRoot'),'Custom'),'MusicTransition',ID='transition')
    fields(root,{'IsFolder':1});E.SubElement(root,'TransitionInfo')
    source=E.SubElement(E.SubElement(track,'ChildrenList'),'AudioFileSource',ID='newsource')
    fields(source,{k:-.001 for k in ['LoopBegin','LoopEnd','TrimBegin','TrimEnd']})
    E.SubElement(source,'Language').text='SFX'
    E.SubElement(source,'AudioFile').text='cue.wav';E.SubElement(E.SubElement(source,'MediaIDList'),'MediaID',ID='901')
    ol=E.SubElement(track,'ObjectLists');clips=E.SubElement(ol,'ObjectList',Name='Sequences');clip=E.SubElement(clips,'MusicClip',ID='clip')
    fields(clip,{'EndTrimOffset':40850,'FadeInMode':0,'FadeOutMode':0});E.SubElement(clip,'AudioSourceRef',ID='newsource')
    cues=E.SubElement(E.SubElement(seg,'ObjectLists'),'ObjectList',Name='Cues')
    E.SubElement(cues,'MusicCue',ID='entry');exit=E.SubElement(cues,'MusicCue',ID='exit');fields(exit,{'CueType':1,'TimeMs':30850})
    f=folder/'Originals/SFX/cue.wav';f.parent.mkdir(parents=True);f.write_bytes(b'synthetic source identity, not music')
    return before,after,dict(authoring_sha256=digest(f),duration_ms=40850),folder/'w3_audio.wproj'


class ApprovedCueTests(unittest.TestCase):
    def test_only_wrapper_removed_stereo_samples_exact(self):
        x=np.zeros((100,2),dtype=np.int16);x[10:80]=np.arange(140).reshape(70,2)
        np.testing.assert_array_equal(strip_wrapper(x,10,20),x[10:80])
        x[0,1]=1
        with self.assertRaises(ValueError):strip_wrapper(x,10,20)

    def test_wrapper_bounds_fail_closed(self):
        for lead,trail in [(0,20),(10,0),(80,30),(-1,20)]:
            with self.assertRaises(ValueError):strip_wrapper(np.zeros((100,2)),lead,trail)

    def test_valid_import_restores_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b,m,p=fixture(Path(tmp));self.assertTrue(validate_import(a,b,{},m,p)['exact_restoration'])

    def test_wrong_exit_tail_gain_dependency_and_original_edit_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b,m,p=fixture(Path(tmp))
            changes=[lambda t:t.find('.//MusicCue[@ID="exit"]/PropertyList/Property[@Name="TimeMs"]').set('Value','40850'),
                lambda t:t.find('.//MusicClip/PropertyList/Property[@Name="EndTrimOffset"]').set('Value','30850'),
                lambda t:fields(t.find('.//MusicTrack'),{'Volume':200}),
                lambda t:E.SubElement(t.find('.//MusicTrack'),'RTPCList'),
                lambda t:E.SubElement(t.find('.//MusicClip'),'UnexpectedCurve'),
                lambda t:t.find('.//MusicSegment[@ID="newseg"]/PropertyList/Property[@Name="Tempo"]').set('Value','120'),
                lambda t:t.find('.//MusicSegment[@ID="old"]').set('Name','changed'),
                lambda t:t.find('.//MusicTrack').set('ShortID','55')]
            for change in changes:
                test=copy.deepcopy(b);change(test)
                with self.subTest(change=change),self.assertRaises(ValueError):validate_import(a,test,{},m,p)


if __name__=='__main__':unittest.main()
