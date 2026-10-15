"""Synthetic bundle proof controls; real native two-bank proof is separate."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from regional_music_bundle import verified_inputs, audit_bank_identities, reviewed_diagnostics, completed_native
from unittest.mock import patch
from white_orchard_prepare import REPO


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=REPO/'build');self.root=Path(self.tmp.name)
        self.spec={'banks':[]}
        for name in ('music_prologue.bnk','music_nomansgrad.bnk'):
            path=self.root/name;path.write_bytes(name.encode());sha=hashlib.sha256(path.read_bytes()).hexdigest()
            proof=self.root/(name+'.json');proof.write_text(json.dumps({'passed':True,'original_audio_unchanged':True,
                'decoded_fields':{'passed':True,'candidate_sha256':sha,'global_generated_data_exact':True,'paired_generated_media_exact':1},
                'bank_preflight':{'passed':True,'candidate_sha256':sha}}))
            self.spec['banks'].append({'path':str(path),'proof':str(proof),'sha256':sha})
    def tearDown(self):self.tmp.cleanup()
    def test_two_proven_banks_pass(self):self.assertEqual(len(verified_inputs(self.spec)),2)
    def test_batch_bank_requires_matching_playback_and_transition_proof(self):
        item=self.spec['banks'][0];path=Path(item['proof'])
        data=json.loads(path.read_text());data.update(batch_manifest_sha256s={'music_prologue':'pinned'},manifest_sha256='pinned')
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'playback proof'):verified_inputs(self.spec)
        playback=self.root/'playback.json';item['playback_proof']=str(playback)
        proof={'passed':True,'region':'music_prologue','manifest_sha256':'pinned',
               'static_voice_checks':{'passed':True},'transition_review':{'passed':True}}
        playback.write_text(json.dumps(proof));self.assertEqual(len(verified_inputs(self.spec)),2)
        for key,value in [('region','music_toussaint'),('manifest_sha256','stale'),('transition_review',{'passed':False})]:
            playback.write_text(json.dumps(dict(proof,**{key:value})))
            with self.assertRaisesRegex(ValueError,'playback proof'):verified_inputs(self.spec)
    def test_duplicate_bank_fails(self):
        self.spec['banks'].append(self.spec['banks'][0])
        with self.assertRaises(ValueError):verified_inputs(self.spec)
    def test_stale_payload_fails(self):
        Path(self.spec['banks'][0]['path']).write_bytes(b'changed')
        with self.assertRaises(ValueError):verified_inputs(self.spec)
    def test_missing_expected_region_fails(self):
        self.spec['banks'].pop()
        with self.assertRaises(ValueError):verified_inputs(self.spec)
    def test_init_never_allowed(self):
        self.spec['banks'][0]['path']=str(self.root/'Init.bnk')
        with self.assertRaises(ValueError):verified_inputs(self.spec)

    def test_explicit_three_regions_require_third_independent_proof(self):
        self.spec['regions']=['music_prologue','music_nomansgrad','music_skellige']
        with self.assertRaises(ValueError):verified_inputs(self.spec)
        old=self.spec['banks'][0];path=self.root/'music_skellige.bnk';path.write_bytes(b'skellige')
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        data=json.loads(Path(old['proof']).read_text())
        data['decoded_fields']['candidate_sha256']=sha;data['bank_preflight']['candidate_sha256']=sha
        proof=self.root/'skellige-proof.json';proof.write_text(json.dumps(data))
        self.spec['banks'].append({'path':str(path),'proof':str(proof),'sha256':sha})
        self.assertEqual(len(verified_inputs(self.spec)),3)

    def test_duplicate_definitions_and_bank_ids_rejected(self):
        banks={'a':Path('a'),'b':Path('b')}
        def record(path):return {'records':{1 if str(path)=='a' else 2:None},'sha256':str(path)}
        with patch('regional_music_bundle.read_bank',side_effect=record), patch('regional_music_bundle.header',side_effect=[{'bank_id':1},{'bank_id':2}]):
            self.assertTrue(audit_bank_identities(banks)['passed'])
        with patch('regional_music_bundle.read_bank',side_effect=record), patch('regional_music_bundle.header',return_value={'bank_id':1}):
            with self.assertRaisesRegex(ValueError,'Duplicate bank ID'):audit_bank_identities(banks)
        with patch('regional_music_bundle.read_bank',return_value={'records':{1:None},'sha256':'s'}), patch('regional_music_bundle.header',side_effect=[{'bank_id':1},{'bank_id':2}]):
            with self.assertRaisesRegex(ValueError,'overlapping serialized'):audit_bank_identities(banks)

    def test_unreviewed_three_bank_diagnostics_cannot_inherit_two_bank_approval(self):
        with self.assertRaisesRegex(ValueError,'independent actual native diagnostic review'):
            reviewed_diagnostics(self.root,self.root,'unused',
                ['music_prologue.bnk','music_nomansgrad.bnk','music_skellige.bnk'])

    def test_observed_profile_is_exact_and_bank_scoped(self):
        names=['music_prologue.bnk','music_nomansgrad.bnk','music_skellige.bnk']
        (self.root/'cook.log').write_text('[time][Warning][WCC] reviewed fixture\n')
        (self.root/'bundle-split.log').write_text('[time][Warning][WCC] reviewed split\n')
        profile=self.root/'profile.json'
        data={'schema':1,'bank_names':names,'review_evidence':'Synthetic profile test, not native evidence',
              'cook_rows':['[warning][wcc] reviewed fixture'],'split_rows':['[warning][wcc] reviewed split']}
        profile.write_text(json.dumps(data))
        self.assertTrue(reviewed_diagnostics(self.root,self.root,'cook',names,profile)['passed'])
        (self.root/'cook.log').write_text('[time][Error][WCC] unexpected\n')
        with self.assertRaisesRegex(ValueError,'Unreviewed native'):
            reviewed_diagnostics(self.root,self.root,'cook',names,profile)
        with self.assertRaisesRegex(ValueError,'mismatched'):
            reviewed_diagnostics(self.root,self.root,'cook',names[:2],profile)

    def test_existing_output_requires_exact_native_status_arguments_and_stderr(self):
        arguments=['cooksounds','-platform=pc_dx12']
        result={'exit_code':0,'timeout':False,'args':arguments+['-root',str(self.root)+'\\','-noninteractivecrash']}
        path=self.root/'cook-result.json';path.write_text(json.dumps(result))
        (self.root/'cook.log').write_text('native fixture')
        stderr=self.root/'cook.stderr.log';stderr.write_text('')
        completed_native(self.root,'cook',arguments)
        for key,value in [('exit_code',1),('args',['wrong-root']),('timeout',True)]:
            changed=dict(result);changed[key]=value;path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError,'Completed native command'):
                completed_native(self.root,'cook',arguments)
        path.write_text(json.dumps(result));stderr.write_text('unreviewed stderr')
        with self.assertRaisesRegex(ValueError,'Completed native command'):
            completed_native(self.root,'cook',arguments)
