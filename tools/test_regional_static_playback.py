import copy
import unittest
import xml.etree.ElementTree as E
from regional_playback_review import static_voice_checks


class MeasuredStaticControls(unittest.TestCase):
    def setUp(self):
        self.tree=E.fromstring('<Music><MusicSwitchContainer ID="r" Name="region"><MusicPlaylistContainer ID="p" Name="generic" /></MusicSwitchContainer></Music>')
        self.spec={'facts':{'root':{'id':'r','name':'region'}},'static_targets':['p']}
        self.node={'name':'generic','parameters':[{'reason':'SoundBankValue','propertyType':'Volume','value':-200}]}
        self.data={'return':{'volume':-214,'objects':[{'name':'region'},self.node]}}
        self.cases=[{'mode':'manifest','samples':[{'contributions':{'1':self.data}}]}]

    def test_measured_ancestry_passes(self):
        self.assertTrue(static_voice_checks(self.cases,self.spec,self.tree)['passed'])

    def test_missing_gain_or_compensating_burst_fails(self):
        for value,gain in ((0,-214),(-200,-14)):
            cases=copy.deepcopy(self.cases);d=cases[0]['samples'][0]['contributions']['1']['return']
            d['objects'][-1]['parameters'][0]['value']=value;d['volume']=gain
            with self.assertRaisesRegex(ValueError,'generic gain missing'):
                static_voice_checks(cases,self.spec,self.tree)

    def test_empty_voices_do_not_prove_suppression(self):
        self.cases[0]['samples'][0]['contributions']={}
        with self.assertRaisesRegex(ValueError,'No measured static'):
            static_voice_checks(self.cases,self.spec,self.tree)
