"""Synthetic bundle proof controls; real native two-bank proof is separate."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from regional_music_bundle import verified_inputs
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
