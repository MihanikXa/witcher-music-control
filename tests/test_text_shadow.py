import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
transform=load('prepare-text-shadow');audit=load('audit-text-shadows')
report=load('report-text-shadow-coverage')


def tag(code,payload):
    return struct.pack('<HI',code<<6|63,len(payload))+payload


class ShadowTests(unittest.TestCase):
    def glow(self):
        return ET.fromstring('<item type="GLOWFILTER" blurX="5" blurY="5" strength="1" passes="3" innerGlow="false" knockout="false" compositeSource="true"><glowColor red="0" green="0" blue="0" alpha="255"/></item>')

    def test_conversion_preserves_passes_and_compositing(self):
        n=transform.shadow(self.glow())
        self.assertEqual(n.get('passes'),'3');self.assertEqual(n.get('compositeSource'),'true')
        self.assertEqual(n.find('dropShadowColor').get('alpha'),'166')
        self.assertAlmostEqual(float(n.get('angle')),51471/65536)

    def test_semantic_color_is_rejected(self):
        n=self.glow();n[0].set('red','255')
        with self.assertRaises(ValueError):transform.shadow(n)

    def test_invisible_effect_is_not_promoted_to_a_visible_shadow(self):
        n=self.glow();n[0].set('alpha','0')
        with self.assertRaises(ValueError):transform.shadow(n)
        self.assertEqual(audit.classify([dict(type='GLOWFILTER',strength='20',color=[dict(red='0',green='0',blue='0',alpha='0')])]),
                         'semantic_or_nonblack_effect_review_preserve')

    def test_existing_angle_is_retained(self):
        n=transform.shadow(self.glow());n.set('angle','1.25')
        for key in ('red','green','blue'):n[0].set(key,'0')
        self.assertEqual(transform.shadow(n).get('angle'),'1.25')

    def test_nested_variable_length_splice_preserves_siblings(self):
        child=tag(70,b'old')+tag(1,b'')+tag(0,b'')
        movie=b'HEAD'+tag(39,struct.pack('<HH',7,1)+child)+tag(82,b'ABC unchanged')+tag(0,b'')
        final=transform.splice(movie,4,{(0,0):b'longer replacement'})
        result=transform.payloads(final,4)
        self.assertEqual(result[(0,0)],(70,b'longer replacement'))
        self.assertEqual(result[(1,)],(82,b'ABC unchanged'))
        self.assertEqual(result[(0,1)],(1,b''))

    def test_malformed_tag_is_rejected(self):
        with self.assertRaises(ValueError):transform.splice(tag(70,b'abc')[:-1],0,{})

    def test_parent_effect_and_move_without_character_are_audited(self):
        xml='''<swf><tags>
        <item type="DefineEditTextTag" characterID="1"/>
        <item type="DefineSpriteTag" spriteId="7"><subTags>
        <item type="PlaceObject3Tag" characterId="1" depth="1" name="tfText" placeFlagHasCharacter="true"/>
        <item type="PlaceObject3Tag" depth="1" placeFlagMove="true" placeFlagHasFilterList="true"><surfaceFilterList>
        <item type="GLOWFILTER" strength="10" blurX="2" blurY="2"><glowColor red="0" green="0" blue="0" alpha="255"/></item>
        </surfaceFilterList></item></subTags></item>
        <item type="PlaceObject3Tag" characterId="7" depth="5" placeFlagHasCharacter="true" placeFlagHasFilterList="true"><surfaceFilterList>
        <item type="DROPSHADOWFILTER" strength="3" blurX="4" blurY="4"><dropShadowColor red="0" green="0" blue="0" alpha="255"/></item>
        </surfaceFilterList></item></tags></swf>'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'movie.xml';p.write_text(xml);r=audit.inspect_xml(p)
        self.assertEqual(len(r['fields']),2)
        self.assertEqual(r['fields'][1]['placement']['name'],'tfText')
        self.assertTrue(r['fields'][1]['ancestor_chains'][0][0]['filters'])
        self.assertIn('strong_black',r['fields'][0]['classification'])

    def test_white_glow_is_not_an_ordinary_black_outline(self):
        self.assertEqual(audit.classify([dict(type='GLOWFILTER',strength='10',color=[dict(red='255',green='255',blue='255')])]),
                         'semantic_or_nonblack_effect_review_preserve')

    def test_research_ledger_excludes_extracted_initial_text(self):
        row=dict(resource_key='gameplay/gui_new/swf/test.redswf',selected_owner='vanilla',
            selection_confidence='unresolved',status='audited_static_deferred',owners=[],fields=[dict(
                character='1',text_definition=dict(type='DefineEditTextTag',fontHeight='520',initialText='proprietary sample'),
                placement=None,ancestor_chains=[],classification='no_authored_effect')])
        result=report.compact(row)
        self.assertNotIn('initialText',result['fields'][0]['definition'])
        self.assertEqual(result['fields'][0]['definition']['fontHeight'],'520')


if __name__=='__main__':unittest.main()
