import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from regional_music_batch_review import collect, master_curves, review
from regional_music_batch_playback import run
from white_orchard_prepare import REPO, digest


class BatchPlaybackTests(unittest.TestCase):
    def test_wrong_source_fingerprint_rejected_before_playback_review(self):
        with tempfile.TemporaryDirectory(dir=REPO/'build') as temp:
            root=Path(temp);manifest=root/'manifest.json';source=root/'music.xml'
            manifest.write_text(json.dumps({'facts':{'original_music_sha256':'wrong'}}));source.write_text('<Music/>')
            with self.assertRaisesRegex(ValueError,'source fingerprint'):
                review(manifest,source,[], 'group','playlist',-17,'named-native-outro')

    def case(self,mode,half=-6.0206003):
        return {'mode':mode,'case':'protected-direct','samples':[{'contributions':{'1':{'return':{'objects':[
            {'name':'Music','parameters':[{'reason':'RTPC','propertyType':'Volume','driverValue':value,'value':gain}]}]}}}}
            for value,gain in ((100.,0.),(50.,half),(100.,0.))]}

    def test_native_master_curve_and_negative_gain(self):
        self.assertEqual(len(master_curves([self.case(m) for m in ('native-reference','manifest')])),2)
        with self.assertRaisesRegex(ValueError,'curve differs'):master_curves([self.case('native-reference',-12)])
        with self.assertRaisesRegex(ValueError,'Paired'):master_curves([self.case('native-reference')])

    def test_incomplete_or_stale_pair_fails(self):
        with tempfile.TemporaryDirectory(dir=REPO/'build') as temp:
            root=Path(temp);manifest=root/'manifest.json';manifest.write_text('{}')
            (root/'results.json').write_text(json.dumps({'cases':[{'mode':'native-reference','case':'one'}]}))
            summary={'folder':str(root),'raw_sha256':'raw','measurement_sha256':'pcm'}
            matrix=root/'matrix.json';matrix.write_text(json.dumps({'manifest_sha256':digest(manifest),'groups':[{'summary':summary}]}))
            with patch('regional_music_batch_review.summarize',return_value=summary):
                with self.assertRaisesRegex(ValueError,'Incomplete'):collect(manifest,[matrix])
            with patch('regional_music_batch_review.summarize',return_value=dict(summary,raw_sha256='changed')):
                with self.assertRaisesRegex(ValueError,'Stale matrix'):collect(manifest,[matrix])
            manifest.write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,'Stale playback'):collect(manifest,[matrix])

    def test_independent_controls_continue_after_one_failure(self):
        with tempfile.TemporaryDirectory(dir=REPO/'build') as temp:
            root=Path(temp);controls=root/'controls.json'
            controls.write_text(json.dumps([{'label':n,'manifest':'source.json','plan':'plan.json'} for n in ('blocked','ready')]))
            with patch('regional_music_batch_playback.matrix',side_effect=[ValueError('blocked fixture'),{'passed':True}]) as mock:
                r=run(root/'validation/w3_audio.wproj',controls,12345,'test',root/'output.json')
            self.assertFalse(r['passed']);self.assertEqual(mock.call_count,2)
            self.assertTrue(r['results'][1]['passed'])
